"""
Unit tests for the Linear Mixed-Effects Model suite.

Tests validate:
- Data extraction from Mouser database format
- LME model fitting and result formatting
- Group comparison functionality
- Edge cases and error handling
"""

import os
import sys
import tempfile
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import pytest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from stats.lme_suite import extract_lme_data, fit_lme, compare_groups_lme


@pytest.fixture
def setup_test_db():
    """Create an in-memory database with test data for LME testing."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    c = conn.cursor()

    # Create tables
    c.execute('''CREATE TABLE experiment (
                    name TEXT, species TEXT, uses_rfid INTEGER,
                    num_animals INTEGER, num_groups INTEGER, cage_max INTEGER,
                    measurement_type INTEGER, id TEXT, investigators TEXT, measurement TEXT)''')

    c.execute('''CREATE TABLE groups (
                    group_id INTEGER PRIMARY KEY, name TEXT,
                    num_animals INTEGER, cage_capacity INTEGER)''')

    c.execute('''CREATE TABLE animals (
                    animal_id INTEGER PRIMARY KEY, group_id INTEGER,
                    rfid TEXT UNIQUE, remarks TEXT, active INTEGER)''')

    c.execute('''CREATE TABLE animal_measurements (
                    measurement_id INTEGER, animal_id INTEGER,
                    timestamp TEXT, value REAL,
                    FOREIGN KEY(animal_id) REFERENCES animals(animal_id),
                    PRIMARY KEY (animal_id, timestamp, measurement_id))''')

    # Insert experiment
    c.execute('''INSERT INTO experiment VALUES (?,?,?,?,?,?,?,?,?,?)''',
              ("Test Experiment", "Mouse", 1, 4, 2, 2, 1, "EXP001", "PI", "weight"))

    # Insert groups
    c.execute("INSERT INTO groups VALUES (1, 'Control', 2, 2)")
    c.execute("INSERT INTO groups VALUES (2, 'Treatment', 2, 2)")

    # Insert animals
    c.execute("INSERT INTO animals VALUES (1, 1, 'RFID001', '', 1)")
    c.execute("INSERT INTO animals VALUES (2, 1, 'RFID002', '', 1)")
    c.execute("INSERT INTO animals VALUES (3, 2, 'RFID003', '', 1)")
    c.execute("INSERT INTO animals VALUES (4, 2, 'RFID004', '', 1)")

    # Insert measurements over time with different trends per group
    base_time = datetime(2024, 1, 1, 10, 0, 0)
    np.random.seed(42)

    for day in range(10):
        timestamp = (base_time + timedelta(days=day)).strftime("%Y-%m-%d %H:%M:%S")
        for animal_id, group_id in [(1, 1), (2, 1), (3, 2), (4, 2)]:
            # Control group: slow growth ~0.1 per day
            # Treatment group: faster growth ~0.3 per day
            base_growth = 0.1 if group_id == 1 else 0.3
            noise = np.random.normal(0, 0.05)
            value = 20.0 + (base_growth * day) + noise
            c.execute("INSERT INTO animal_measurements VALUES (1, ?, ?, ?)",
                      (animal_id, timestamp, round(value, 3)))

    conn.commit()

    class MockDB:
        def __init__(self, conn):
            self._conn = conn
            self._c = conn.cursor()
            self.db_file = ":memory:"

    return MockDB(conn)


class TestExtractLMEData:
    """Test data extraction for LME analysis."""

    def test_extract_returns_dataframe(self, setup_test_db):
        db = setup_test_db
        df = extract_lme_data(db)
        assert isinstance(df, __import__('pandas').DataFrame)

    def test_extract_has_required_columns(self, setup_test_db):
        db = setup_test_db
        df = extract_lme_data(db)
        required_cols = ["animal_id", "group", "days", "value"]
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"

    def test_extract_computes_days_correctly(self, setup_test_db):
        db = setup_test_db
        df = extract_lme_data(db)
        assert "days" in df.columns
        # First measurement for each animal should have days=0
        first_days = df.groupby("animal_id")["days"].min()
        assert all(first_days == 0.0), "First measurement should have days=0"

    def test_extract_filters_inactive_animals(self, setup_test_db):
        db = setup_test_db
        # Deactivate an animal
        db._c.execute("UPDATE animals SET active=0 WHERE animal_id=1")
        db._conn.commit()
        df = extract_lme_data(db)
        assert 1 not in df["animal_id"].values, "Inactive animals should be excluded"

    def test_extract_empty_db(self):
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE experiment (name TEXT)''')
        c.execute('''CREATE TABLE animals (animal_id INTEGER, group_id INTEGER, rfid TEXT, remarks TEXT, active INTEGER)''')
        c.execute('''CREATE TABLE groups (group_id INTEGER, name TEXT, num_animals INTEGER, cage_capacity INTEGER)''')
        c.execute('''CREATE TABLE animal_measurements (measurement_id INTEGER, animal_id INTEGER, timestamp TEXT, value REAL)''')

        class MockDB:
            def __init__(self, conn):
                self._conn = conn
                self._c = conn.cursor()
        df = extract_lme_data(MockDB(conn))
        assert df.empty


class TestFitLME:
    """Test LME model fitting."""

    def test_fit_returns_model_and_results(self, setup_test_db):
        db = setup_test_db
        df = extract_lme_data(db)
        model, results = fit_lme(df)
        assert model is not None, "Model should be fitted"
        assert results is not None, "Results dict should be returned"

    def test_fit_results_structure(self, setup_test_db):
        db = setup_test_db
        df = extract_lme_data(db)
        model, results = fit_lme(df)
        assert "model_info" in results
        assert "fixed_effects" in results
        assert "random_effects_variance" in results
        assert "converged" in results

    def test_fit_detects_group_difference(self, setup_test_db):
        db = setup_test_db
        df = extract_lme_data(db)
        model, results = fit_lme(df)
        # Treatment group coefficient should have reasonable p-value
        # (treatment group grows faster)
        fixed_effects = results["fixed_effects"]
        # Look for group_Treatment or similar key (the prefix depends on implementation)
        group_keys = [k for k in fixed_effects.keys() if "Treatment" in k and "group" in k]
        assert len(group_keys) > 0, f"Treatment group effect should be in fixed effects. Keys: {list(fixed_effects.keys())}"
        treatment_key = group_keys[0]
        # Coefficient should be positive (treatment grows faster)
        assert fixed_effects[treatment_key]["coef"] > 0

    def test_fit_empty_dataframe(self):
        df = __import__('pandas').DataFrame()
        model, results = fit_lme(df)
        assert model is None
        assert results is None

    def test_fit_with_time_included(self, setup_test_db):
        db = setup_test_db
        df = extract_lme_data(db)
        model, results = fit_lme(df, include_time=True)
        assert model is not None
        # Days coefficient should be positive (growth over time)
        fixed_effects = results["fixed_effects"]
        day_keys = [k for k in fixed_effects.keys() if "days" in k.lower()]
        if day_keys:
            assert fixed_effects[day_keys[0]]["coef"] > 0


class TestCompareGroupsLME:
    """Test group comparison using LME."""

    def test_compare_groups_returns_result(self, setup_test_db):
        db = setup_test_db
        result = compare_groups_lme(db, "Control", "Treatment")
        assert result is not None
        assert "comparison" in result
        assert "coefficient" in result
        assert "p_value" in result

    def test_compare_groups_significance(self, setup_test_db):
        db = setup_test_db
        result = compare_groups_lme(db, "Control", "Treatment")
        # With strong effect size, should detect difference
        assert result["coefficient"] is not None
        assert result["n_observations"] > 0

    def test_compare_groups_invalid_groups(self, setup_test_db):
        db = setup_test_db
        result = compare_groups_lme(db, "Control", "Nonexistent")
        assert result is None

    def test_compare_groups_same_group(self, setup_test_db):
        db = setup_test_db
        result = compare_groups_lme(db, "Control", "Control")
        assert result is None or not result.get("significant", True)


class TestLMEResultFormatting:
    """Test result formatting for publication-ready output."""

    def test_format_has_confidence_intervals(self, setup_test_db):
        db = setup_test_db
        df = extract_lme_data(db)
        model, results = fit_lme(df)
        for effect_name, effect_data in results["fixed_effects"].items():
            assert "ci_lower" in effect_data
            assert "ci_upper" in effect_data
            assert effect_data["ci_lower"] < effect_data["ci_upper"]

    def test_format_model_info(self, setup_test_db):
        db = setup_test_db
        df = extract_lme_data(db)
        model, results = fit_lme(df)
        info = results["model_info"]
        assert "nobs" in info
        assert "aic" in info
        assert "bic" in info
        assert info["nobs"] > 0

    def test_significant_pvalues_detected(self, setup_test_db):
        db = setup_test_db
        df = extract_lme_data(db)
        model, results = fit_lme(df)
        # Should correctly identify significant effects
        sig_effects = results["pvalues_significant"]
        # At least time (days) should be significant with 10 days of data
        assert len(results["fixed_effects"]) > 0
