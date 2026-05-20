"""Age band policy tests (Phase 05)."""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import AGE_BANDS, AGE_BAND_STEP, in_age_band


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
