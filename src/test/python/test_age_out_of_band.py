"""Age outside 20~79 band policy tests (TC #40)."""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import BmiCategory, SHealth


def test_age_19_excluded_from_age_band_ratios_included_in_overall(write_health_csv) -> None:
    """age=19: no 20s ratio, but counts in overall distribution (TC #40)."""
    path = write_health_csv([("1", 19, 60.0, 170.0)])
    shealth = SHealth()
    shealth.calculate_bmi(str(path))

    assert shealth.get_bmi_ratio(20, SHealth.NORMALWEIGHT) == 0.0
    overall = shealth.get_overall_bmi_distribution()
    assert overall[BmiCategory.NORMALWEIGHT] == pytest.approx(100.0, abs=0.01)
    assert shealth.get_normal_weight_user_ids() == [1]
