"""Tumor volume formulas and statistical utilities."""
from math import sqrt, pi

LEGACY_PI = 3.1415

STATUS_MEASURED = "measured"
STATUS_DEAD = "dead"
STATUS_SKIPPED = "skipped"
STATUS_CENSORED = "censored"


def calc_volume(calc_method, length, width):
    """Compute tumor volume based on legacy formulas."""
    if length is None:
        return None
    if calc_method == 10:
        return float(length)
    if width is None:
        return None

    L = float(length)
    W = float(width)
    S = min(L, W)

    if calc_method == 0:
        return L * W
    if calc_method == 1:
        return (LEGACY_PI / 2.0) * L * W
    if calc_method == 2:
        return L * W * S
    if calc_method == 3:
        return 0.4 * L * W * S
    if calc_method == 4:
        return 0.5 * L * W * S
    if calc_method == 5:
        return 0.5236 * L * W * S
    if calc_method == 6:
        return (LEGACY_PI / 6.0) * L * W * S
    if calc_method == 7:
        return (LEGACY_PI / 6.0) * (L * W) ** 1.5
    if calc_method == 8:
        return (LEGACY_PI / 4.0) * L * W * S
    if calc_method == 9:
        return (sqrt(L ** 2 + S ** 2) / 2.0) * 2.0 * LEGACY_PI

    # Default fallback
    return L * W * S


def _measured_values(records):
    """Extract measured volumes from records."""
    return [r["volume"] for r in records if r["status"] == STATUS_MEASURED and r["volume"] is not None]


def mean(records):
    values = _measured_values(records)
    if not values:
        return None
    return sum(values) / len(values)


def geometric_mean(records):
    values = _measured_values(records)
    if not values:
        return None
    product = 1.0
    for v in values:
        if v != 0:
            product *= abs(v)
    return abs(product) ** (1.0 / len(values))


def stddev_sample(records):
    values = _measured_values(records)
    count = len(values)
    if count < 2:
        return None
    sum_sq = sum(v ** 2 for v in values)
    sum_v = sum(values)
    return sqrt(abs(count * sum_sq - sum_v ** 2) / (count * (count - 1)))


def trimmed_mean(records):
    values = _measured_values(records)
    if len(values) < 3:
        return None
    v_min = min(values)
    v_max = max(values)
    return (sum(values) - v_min - v_max) / (len(values) - 2)


def trimmed_geometric_mean(records):
    values = _measured_values(records)
    if len(values) < 3:
        return None
    v_min = min(values)
    v_max = max(values)
    adjusted_min = v_min if v_min != 0 else 1
    product = 1.0
    for v in values:
        if v > 0:
            product *= v
    return abs(product / (v_max * adjusted_min)) ** (1.0 / (len(values) - 2))


def median(records):
    values = sorted(_measured_values(records))
    if not values:
        return None
    n = len(values)
    mid = n // 2
    if n % 2 == 1:
        return values[mid]
    return (values[mid - 1] + values[mid]) / 2.0


def survival_percent(records, limit, previous_percent=None):
    """Legacy-style survival calculation with monotone non-increasing enforcement."""
    if limit is None:
        return None

    count = 0
    above_limit = 0
    censored = 0
    for r in records:
        status = r["status"]
        volume = r["volume"]
        if status == STATUS_SKIPPED:
            continue
        count += 1
        if status == STATUS_CENSORED:
            censored += 1
            above_limit += 1
            continue
        if status == STATUS_DEAD:
            above_limit += 1
            continue
        if volume is not None and volume > limit:
            above_limit += 1

    if count == 0 or (count - censored) == 0:
        return None

    percent = (count - above_limit) / (count - censored) * 100.0
    if previous_percent is not None:
        percent = min(previous_percent, percent)
    return percent


def box_values(records):
    """Return raw values for box plot computation."""
    return _measured_values(records)
