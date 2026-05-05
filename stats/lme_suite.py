"""Linear Mixed-Effects Models suite for longitudinal animal experiment data.

Implements gold-standard statistical analysis for repeated measures using
statsmodels' MixedLM. Handles data extraction, model fitting, and
publication-ready result formatting.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

# Import statsmodels at module level to avoid thread import issues
try:
    from statsmodels.regression.mixed_linear_model import MixedLM
    STATSMODELS_AVAILABLE = True
except ImportError:
    MixedLM = None
    STATSMODELS_AVAILABLE = False


def _parse_timestamp(ts: str) -> datetime:
    """Parse SQLite timestamp string to datetime."""
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue
    return pd.NaT


def extract_lme_data(db) -> pd.DataFrame:
    """Extract and reshape data for LME analysis from Mouser database.

    Returns a DataFrame with columns:
        animal_id (int): Animal identifier
        group (str): Group name (treatment/control)
        group_id (int): Group identifier
        days (float): Days since first measurement (time variable)
        value (float): Measurement value
        measurement_id (int): Measurement type identifier
    """
    # Fetch animals with group info
    db._c.execute("""
        SELECT a.animal_id, a.group_id, g.name
        FROM animals a
        JOIN groups g ON a.group_id = g.group_id
        WHERE a.active = 1
    """)
    animals = db._c.fetchall()
    if not animals:
        return pd.DataFrame()

    animal_groups = {row[0]: (row[2], row[1]) for row in animals}

    # Fetch all measurements
    db._c.execute("""
        SELECT animal_id, timestamp, value, measurement_id
        FROM animal_measurements
        WHERE value IS NOT NULL
        ORDER BY animal_id, timestamp, measurement_id
    """)
    measurements = db._c.fetchall()
    if not measurements:
        return pd.DataFrame()

    # Build DataFrame
    rows = []
    for animal_id, ts, value, mid in measurements:
        if animal_id not in animal_groups:
            continue
        group_name, group_id = animal_groups[animal_id]
        dt = _parse_timestamp(ts)
        rows.append({
            "animal_id": animal_id,
            "group": group_name,
            "group_id": group_id,
            "timestamp": dt,
            "value": value,
            "measurement_id": mid or 1,
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # Compute days since first measurement per animal (time variable)
    df["days"] = df.groupby("animal_id")["timestamp"].transform(
        lambda x: (x - x.min()).dt.total_seconds() / 86400.0
    )

    return df.dropna(subset=["days", "value"])


def fit_lme(df: pd.DataFrame,
            fixed_effects: str = "group",
            random_effects: str = "animal_id",
            include_time: bool = True,
            include_interaction: bool = False) -> Tuple[Optional[object], Optional[Dict[str, Any]]]:
    """Fit a Linear Mixed-Effects Model to longitudinal data.

    Args:
        df: DataFrame from extract_lme_data()
        fixed_effects: Column name(s) for fixed effects (treatment effects)
        random_effects: Column name for random effects (individual variability)
        include_time: Whether to include days as a fixed effect (longitudinal slope)
        include_interaction: Whether to include group:days interaction

    Returns:
        Tuple of (fitted_model, results_dict). Returns (None, None) on failure.
    """
    if not STATSMODELS_AVAILABLE or MixedLM is None:
        print("[LME DEBUG] statsmodels not available")
        return None, None

    print(f"[LME DEBUG] fit_lme: df shape={df.shape}, columns={df.columns.tolist()}")
    if df.empty or "value" not in df.columns:
        print(f"[LME DEBUG] Empty or missing value column, returning None")
        return None, None

    # Prepare model matrix - use pandas DataFrames to preserve column names
    endog = df["value"].astype(float)  # Keep as Series to preserve index
    exog_df = pd.DataFrame(index=df.index)

    # Always add intercept first (required for proper AIC/BIC calculation)
    exog_df["intercept"] = 1.0

    # Add time variable
    if include_time and "days" in df.columns:
        exog_df["days"] = df["days"].astype(float)

    # Add fixed effects (categorical variables as dummies)
    if fixed_effects in df.columns:
        dummies = pd.get_dummies(df[fixed_effects], prefix=fixed_effects, drop_first=True)
        # Ensure all columns are float (not bool)
        for col in dummies.columns:
            dummies[col] = dummies[col].astype(float)
        exog_df = pd.concat([exog_df, dummies], axis=1)

    # Add interaction terms
    if include_interaction and include_time and fixed_effects in df.columns:
        for grp in df[fixed_effects].unique()[1:]:  # Skip reference group
            col_name = f"{fixed_effects}_{grp}:days"
            is_grp = (df[fixed_effects] == grp).astype(float)
            exog_df[col_name] = is_grp * df["days"]

    # Convert to appropriate types for statsmodels
    # Note: MixedLM can accept DataFrames directly (preserves column names for summary)
    exog = exog_df.astype(float)

    # Random effects variance (animal-level random intercept)
    groups = df[random_effects].values if random_effects in df.columns else None
    if groups is None:
        return None, None

    try:
        model = MixedLM(endog, exog, groups=groups)
        result = model.fit()
        return result, _format_results(result, fixed_effects, include_time, groups_array=groups)
    except Exception as e:
        import traceback
        print(f"LME fitting error: {e}")
        traceback.print_exc()
        return None, None


def _format_results(result, fixed_effects: str, include_time: bool, groups_array=None) -> Dict[str, Any]:
    """Format LME results into publication-ready dictionary."""
    # Extract model info from summary table 0 (which is a DataFrame)
    summary = result.summary()
    model_info = {}
    try:
        table0 = summary.tables[0]
        for idx in range(len(table0)):
            if len(table0.iloc[idx]) >= 2:
                key = str(table0.iloc[idx, 0]) if hasattr(table0, 'iloc') else str(table0[idx][0])
                val = str(table0.iloc[idx, 1]) if hasattr(table0, 'iloc') else str(table0[idx][1])
                model_info[key.strip()] = val.strip()
    except Exception:
        pass

    # Extract fixed effects with p-values from table 1
    fixed_effects_dict = {}
    try:
        fe_table = summary.tables[1]
        # fe_table is a DataFrame with 6 columns: [0]Coef., [1]Std.Err., [2]z, [3]P>|z|, [4][0.025, [5]0.975]
        # The row index contains the coefficient name (e.g., 'group_Treatment', 'days')
        # Skip the header row (idx=0) and Group Var row (last row)
        for idx in range(1, len(fe_table) - 1):  # -1 to skip Group Var row
            row = fe_table.iloc[idx]
            # Get coefficient name from the row index (not from row values)
            coef_name = str(fe_table.index[idx])
            # Only include rows with valid coefficient names (not Group Var)
            if coef_name and coef_name != "Group Var":
                fixed_effects_dict[coef_name] = {
                    "coef": float(row.iloc[0]) if pd.notna(row.iloc[0]) else None,  # Column 0 = Coef.
                    "std_err": float(row.iloc[1]) if pd.notna(row.iloc[1]) else None,  # Column 1 = Std.Err.
                    "z_value": float(row.iloc[2]) if pd.notna(row.iloc[2]) else None,  # Column 2 = z
                    "p_value": float(row.iloc[3]) if pd.notna(row.iloc[3]) else None,  # Column 3 = P>|z|
                    "ci_lower": float(row.iloc[4]) if pd.notna(row.iloc[4]) else None,  # Column 4 = [0.025
                    "ci_upper": float(row.iloc[5]) if pd.notna(row.iloc[5]) else None,  # Column 5 = 0.975]
                }
    except Exception as e:
        print(f"Error extracting fixed effects: {e}")
        import traceback
        traceback.print_exc()
        pass

    # Random effects variance - handle both DataFrame and numpy array
    re_var = np.nan
    try:
        if hasattr(result.cov_re, 'iloc'):
            re_var = float(result.cov_re.iloc[0, 0])
        elif hasattr(result.cov_re, 'shape'):
            re_var = float(result.cov_re[0, 0]) if result.cov_re.size > 0 else np.nan
    except Exception:
        pass

    # Compute AIC/BIC, handling NaN values
    aic = float(result.aic)
    bic = float(result.bic)
    if np.isnan(aic):
        # Fallback: AIC = -2*log_likelihood + 2*k
        k = result.k_fe + result.k_re2
        aic = -2 * float(result.llf) + 2 * k
    if np.isnan(bic):
        # Fallback: BIC = -2*log_likelihood + k*log(n)
        k = result.k_fe + result.k_re2
        bic = -2 * float(result.llf) + k * np.log(float(result.nobs))

    # Compute actual number of groups (animals), not parameters
    n_groups = int(result.k_re2 + result.k_fe)  # fallback
    if groups_array is not None:
        try:
            n_groups = len(np.unique(groups_array))
        except Exception:
            pass

    return {
        "model_info": {
            "method": model_info.get("Method", "REML"),
            "dependent_var": model_info.get("Dependent Variable", "value"),
            "nobs": int(result.nobs),
            "groups": n_groups,
            "log_likelihood": float(result.llf),
            "aic": aic,
            "bic": bic,
        },
        "fixed_effects": fixed_effects_dict,
        "random_effects_variance": float(re_var) if not np.isnan(re_var) else None,
        "converged": bool(result.converged),
        "pvalues_significant": {
            k: v for k, v in fixed_effects_dict.items()
            if v["p_value"] < 0.05
        },
    }


def compare_groups_lme(db, group1_name: str, group2_name: str,
                       include_time: bool = True, exclude_outliers: bool = False) -> Optional[Dict[str, Any]]:
    """Compare two specific groups using LME.

    Args:
        db: Database connection
        group1_name: Reference group name
        group2_name: Treatment group name
        include_time: Whether to include time (days) as fixed effect
        exclude_outliers: If True, exclude values beyond 3 standard deviations from group mean

    Returns:
        Dictionary with comparison results or None if insufficient data.
    """
    df = extract_lme_data(db)
    if df.empty:
        return None

    # Filter to the two groups
    df_filtered = df[df["group"].isin([group1_name, group2_name])].copy()
    if len(df_filtered["group"].unique()) < 2:
        return None

    # Optionally exclude outliers (3 sigma rule)
    if exclude_outliers:
        rows_to_drop = []
        for grp in df_filtered["group"].unique():
            grp_data = df_filtered[df_filtered["group"] == grp]
            values = [float(v) for v in grp_data["value"].tolist()]
            if len(values) < 2:
                continue
            mean = float(np.mean(values))
            std = float(np.std(values))
            if std <= 0:
                continue
            lower = mean - 3 * std
            upper = mean + 3 * std
            for idx in grp_data.index:
                val = float(grp_data.loc[idx, "value"])
                if val < lower or val > upper:
                    rows_to_drop.append(idx)
                    print(f"[LME DEBUG] Group '{grp}': excluded outlier {val} (3-sigma rule)")

        if rows_to_drop:
            df_filtered = df_filtered.drop(index=rows_to_drop)

        if len(df_filtered) < 4:
            print("[LME DEBUG] Too few observations after outlier exclusion")
            return None

    # Compute per-animal statistics
    per_animal_stats = []
    for animal_id, group_name in df_filtered[["animal_id", "group"]].drop_duplicates().itertuples(index=False):
        animal_data = df_filtered[df_filtered["animal_id"] == animal_id]["value"]
        if len(animal_data) > 0:
            per_animal_stats.append({
                "animal_id": int(animal_id),
                "group": group_name,
                "n_obs": len(animal_data),
                "mean": float(animal_data.mean()),
                "median": float(animal_data.median()),
                "std_dev": float(animal_data.std()) if len(animal_data) > 1 else 0.0,
                "min_val": float(animal_data.min()),
                "max_val": float(animal_data.max()),
            })
    per_animal_stats.sort(key=lambda x: (x["group"], x["animal_id"]))

    result, formatted = fit_lme(df_filtered, fixed_effects="group",
                                 include_time=include_time)
    if result is None:
        return None

    print(f"[LME DEBUG] Model fitted. Fixed effects keys: {list(formatted.get('fixed_effects', {}).keys())}")

    # Extract the treatment effect (coefficient for group2 vs reference group1)
    group_col = f"group_{group2_name}"
    effect = formatted["fixed_effects"].get(group_col, {})
    print(f"[LME DEBUG] Effect for {group_col}: {effect}")

    return {
        "comparison": f"{group2_name} vs {group1_name}",
        "coefficient": effect.get("coef"),
        "p_value": effect.get("p_value"),
        "ci_lower": effect.get("ci_lower"),
        "ci_upper": effect.get("ci_upper"),
        "significant": effect.get("p_value", 1.0) < 0.05,
        "n_observations": int(result.nobs),
        "n_groups": formatted["model_info"]["groups"],
        "model_aic": formatted["model_info"]["aic"],
        "model_bic": formatted["model_info"]["bic"],
        "log_likelihood": formatted["model_info"]["log_likelihood"],
        "method": formatted["model_info"]["method"],
        "converged": formatted["converged"],
        "random_effects_variance": formatted["random_effects_variance"],
        "all_fixed_effects": formatted["fixed_effects"],
        "model_info": formatted["model_info"],
        "per_animal_stats": per_animal_stats,
    }
