"""Age band policy tests (Phase 05)."""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import AGE_BANDS, AGE_BAND_STEP, SHealth, age_bands, in_age_band


@pytest.mark.parametrize(
    "age,age_band_start,expected",
    [
        (20, 20, True),
        (29, 20, True),
        (30, 20, False),
        (30, 30, True),
        (19, 20, False),
        (80, 70, False),
    ],
)
def test_in_age_band(age: int, age_band_start: int, expected: bool) -> None:
    assert in_age_band(age, age_band_start) is expected


def test_age_bands_matches_impute_and_aggregate() -> None:
    assert AGE_BANDS == (20, 30, 40, 50, 60, 70)
    assert len(AGE_BANDS) == 6
    assert AGE_BANDS[0] + AGE_BAND_STEP == AGE_BANDS[1]
    assert tuple(age_bands()) == AGE_BANDS


def test_age_19_excluded_from_20s_statistics(write_health_csv) -> None:
    """age=19 loaded but not counted in 20s band ratios (TC #40)."""
    path = write_health_csv([("1", 19, 70.0, 170.0)])
    shealth = SHealth()
    assert shealth.calculate_bmi(str(path)) == 1
    for category_value in (100, 200, 300, 400):
        assert shealth.get_bmi_ratio(20, category_value) == 0.0


def test_legacy_list_properties(write_health_csv) -> None:
    path = write_health_csv([("1", 25, 70.0, 170.0)])
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    assert shealth.ages == [25]
    assert shealth.heights == [170.0]
    assert shealth.weights == [70.0]
    assert len(shealth.bmis) == 1
