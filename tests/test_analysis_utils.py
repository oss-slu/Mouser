import math

from shared.analysis_utils import (
    calc_volume,
    mean,
    median,
    trimmed_mean,
    geometric_mean,
    trimmed_geometric_mean,
    stddev_sample,
    survival_percent,
    STATUS_MEASURED,
    STATUS_DEAD,
    STATUS_CENSORED,
)


def _records(vals):
    return [{"volume": v, "status": STATUS_MEASURED} for v in vals]


def test_calc_volume_basic_formulas():
    L = 10.0
    W = 5.0
    S = min(L, W)
    assert calc_volume(0, L, W) == L * W
    assert calc_volume(2, L, W) == L * W * S
    assert calc_volume(10, L, W) == L


def test_calc_volume_legacy_pi():
    L = 8.0
    W = 4.0
    expected = (3.1415 / 2.0) * L * W
    assert math.isclose(calc_volume(1, L, W), expected, rel_tol=1e-6)


def test_statistics_mean_median_trimmed():
    recs = _records([1, 2, 3, 4, 5])
    assert mean(recs) == 3
    assert median(recs) == 3
    assert trimmed_mean(recs) == 3


def test_statistics_geometric_and_trimmed_geo():
    recs = _records([1, 2, 4])
    assert math.isclose(geometric_mean(recs), math.sqrt(8), rel_tol=1e-6)
    # Trimmed geo with 3 values removes min/max -> only middle value
    assert math.isclose(trimmed_geometric_mean(recs), 2, rel_tol=1e-6)


def test_stddev_sample():
    recs = _records([2, 4, 4, 4, 5, 5, 7, 9])
    assert math.isclose(stddev_sample(recs), 2.138089935299395, rel_tol=1e-6)


def test_survival_percent():
    records = [
        {"volume": 900, "status": STATUS_MEASURED},
        {"volume": 1200, "status": STATUS_MEASURED},
        {"volume": None, "status": STATUS_DEAD},
        {"volume": None, "status": STATUS_CENSORED},
    ]
    # count=4, above=3 (1200 + dead + censored), censored=1
    # (4-3)/(4-1)*100 = 33.333...
    val = survival_percent(records, 1000, None)
    assert math.isclose(val, 33.3333333333, rel_tol=1e-6)
