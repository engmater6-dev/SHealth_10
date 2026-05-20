"""Age-band BMI ratio sum tests (TC #27~28)."""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import BmiCategory, SHealth


def test_age_band_four_categories_sum_to_100(write_health_csv) -> None:
    """20s: one record per BMI category → each 25%, sum ≈ 100% (TC #27)."""
    # BMI targets: under / normal / overweight / obesity
    rows = [
        ("1", 25, 50.0, 170.0),   # ~17.3 under
        ("2", 26, 60.0, 170.0),   # ~20.8 normal
        ("3", 27, 68.0, 170.0),   # ~23.5 overweight
        ("4", 28, 75.0, 170.0),   # ~26.0 obesity
    ]
    path = write_health_csv(rows)
    shealth = SHealth()
    shealth.calculate_bmi(str(path))

    for category in BmiCategory:
        ratio = shealth.get_bmi_ratio(20, category.value)
        assert ratio == pytest.approx(25.0, abs=0.01)

    total = sum(shealth.get_bmi_ratio(20, c.value) for c in BmiCategory)
    assert total == pytest.approx(100.0, abs=0.01)


def test_empty_age_band_returns_zero_ratios(write_health_csv) -> None:
    """No 20s records → all 20s ratios 0.0 (TC #28)."""
    path = write_health_csv([("1", 35, 70.0, 170.0)])
    shealth = SHealth()
    shealth.calculate_bmi(str(path))

    for category in BmiCategory:
        assert shealth.get_bmi_ratio(20, category.value) == 0.0
