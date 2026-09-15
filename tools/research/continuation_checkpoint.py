"""Compare manifest jobs across Python/Rust JSON number round trips."""
import math


def same_job(actual, expected):
    """Require identical structure/values, allowing one binary64 ULP for floats.

    serde_json's default decimal parsing can round an effective stack one ULP
    away from Python. This is far below the solver's f32 storage precision;
    it is not a tolerance for altered configurations or range strings.
    """
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(
            same_job(actual[k], expected[k]) for k in expected)
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            same_job(a, b) for a, b in zip(actual, expected))
    if isinstance(expected, float):
        return math.isfinite(actual) and math.isfinite(expected) and abs(
            actual - expected) <= max(math.ulp(actual), math.ulp(expected))
    return actual == expected
