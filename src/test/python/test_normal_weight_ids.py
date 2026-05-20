"""Normal-weight user ID list tests (TC #32~35)."""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import SHealth


def test_normal_weight_ids_only_normal(write_health_csv) -> None:
    """id=1 underweight, id=2 normal → [2] (TC #32)."""
    path = write_health_csv(
        [
            ("1", 25, 50.0, 170.0),
            ("2", 26, 60.0, 170.0),
        ]
    )
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    assert shealth.get_normal_weight_user_ids() == [2]


def test_normal_weight_ids_boundary_excluded(write_health_csv) -> None:
    """BMI=18.5 and 23.0 excluded from normal list (TC #33)."""
    path = write_health_csv(
        [
            ("1", 25, 49.0, 170.0),
            ("2", 26, 66.47, 170.0),
            ("3", 27, 60.0, 170.0),
        ]
    )
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    assert shealth.bmis[0] < 18.5
    assert shealth.bmis[1] == pytest.approx(23.0, abs=0.01)
    assert shealth.get_normal_weight_user_ids() == [3]


def test_normal_weight_ids_empty_when_none(write_health_csv) -> None:
    """All obesity → [] (TC #34)."""
    path = write_health_csv(
        [
            ("1", 25, 90.0, 170.0),
            ("2", 26, 95.0, 170.0),
        ]
    )
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    assert shealth.get_normal_weight_user_ids() == []


def test_normal_weight_ids_preserves_input_order(write_health_csv) -> None:
    """Return IDs in CSV order (TC #35)."""
    path = write_health_csv(
        [
            ("10", 25, 60.0, 170.0),
            ("5", 26, 50.0, 170.0),
            ("20", 27, 62.0, 170.0),
        ]
    )
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    assert shealth.get_normal_weight_user_ids() == [10, 20]
