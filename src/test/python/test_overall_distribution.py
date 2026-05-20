"""Overall BMI distribution tests (TC #29~30)."""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import BmiCategory, SHealth


def test_overall_distribution_ten_users(write_health_csv) -> None:
    """10 users: 2/3/3/2 per category → 20/30/30/20% (TC #29)."""
    rows = [
        ("1", 25, 50.0, 170.0),
        ("2", 26, 50.0, 170.0),
        ("3", 27, 60.0, 170.0),
        ("4", 28, 60.0, 170.0),
        ("5", 29, 60.0, 170.0),
        ("6", 30, 68.0, 170.0),
        ("7", 31, 68.0, 170.0),
        ("8", 32, 68.0, 170.0),
        ("9", 33, 75.0, 170.0),
        ("10", 34, 75.0, 170.0),
    ]
    path = write_health_csv(rows)
    shealth = SHealth()
    shealth.calculate_bmi(str(path))

    dist = shealth.get_overall_bmi_distribution()
    assert dist[BmiCategory.UNDERWEIGHT] == pytest.approx(20.0, abs=0.01)
    assert dist[BmiCategory.NORMALWEIGHT] == pytest.approx(30.0, abs=0.01)
    assert dist[BmiCategory.OVERWEIGHT] == pytest.approx(30.0, abs=0.01)
    assert dist[BmiCategory.OBESITY] == pytest.approx(20.0, abs=0.01)
    assert sum(dist.values()) == pytest.approx(100.0, abs=0.01)


def test_overall_distribution_single_normal_user(write_health_csv) -> None:
    """1 normal user → 100% normal, others 0% (TC #30)."""
    path = write_health_csv([("1", 25, 60.0, 170.0)])
    shealth = SHealth()
    shealth.calculate_bmi(str(path))

    dist = shealth.get_overall_bmi_distribution()
    assert dist[BmiCategory.NORMALWEIGHT] == pytest.approx(100.0, abs=0.01)
    assert dist[BmiCategory.UNDERWEIGHT] == 0.0
    assert dist[BmiCategory.OVERWEIGHT] == 0.0
    assert dist[BmiCategory.OBESITY] == 0.0


def test_overall_distribution_empty_after_load(write_health_csv) -> None:
    """No valid height → all zeros."""
    path = write_health_csv([])
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    dist = shealth.get_overall_bmi_distribution()
    assert all(value == 0.0 for value in dist.values())
