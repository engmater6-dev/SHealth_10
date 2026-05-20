"""Height imputation tests (TC #23~26)."""

from __future__ import annotations

import sys
import os
from typing import Sequence, Tuple

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import SHealth

HealthRow = Tuple[str, int, float, float]


def test_impute_height_by_age_band(write_health_csv) -> None:
    """20s: h=170 and h=0 → missing height imputed to 170 (TC #23)."""
    path = write_health_csv(
        [
            ("1", 25, 60.0, 170.0),
            ("2", 28, 60.0, 0.0),
        ]
    )
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    assert shealth.heights[1] == 170.0
    assert shealth.bmis[0] == shealth.bmis[1]


def test_impute_weight_and_height_both_zero(write_health_csv) -> None:
    """w=0 and h=0 in same band → both imputed, valid BMI (TC #24)."""
    path = write_health_csv(
        [
            ("1", 25, 70.0, 175.0),
            ("2", 28, 0.0, 0.0),
        ]
    )
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    assert shealth.weights[1] == 70.0
    assert shealth.heights[1] == 175.0
    expected_bmi = 70.0 / ((175.0 / 100.0) ** 2)
    assert shealth.bmis[1] == pytest.approx(expected_bmi, rel=1e-6)


def test_impute_height_all_zero_in_band_stays_zero(write_health_csv) -> None:
    """40s: all h=0 → height remains 0, bmi=0, no ZeroDivision (TC #25)."""
    path = write_health_csv(
        [
            ("1", 45, 70.0, 0.0),
            ("2", 46, 80.0, 0.0),
        ]
    )
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    assert shealth.heights == [0.0, 0.0]
    assert shealth.bmis == [0.0, 0.0]


def test_impute_height_then_bmi(write_health_csv) -> None:
    """w=70, h=0→175 → BMI≈22.86 (TC #26)."""
    path = write_health_csv([("1", 25, 70.0, 0.0), ("2", 28, 70.0, 175.0)])
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    assert shealth.heights[0] == 175.0
    expected = 70.0 / ((175.0 / 100.0) ** 2)
    assert shealth.bmis[0] == pytest.approx(expected, rel=1e-4)


@pytest.mark.parametrize(
    "rows,check_index,expected_height",
    [
        pytest.param(
            [
                ("1", 35, 60.0, 165.0),
                ("2", 36, 60.0, 175.0),
                ("3", 37, 60.0, 0.0),
            ],
            2,
            170.0,
            id="tc23_multiple_valid_heights_average",
        ),
    ],
)
def test_impute_height_parametrize(
    write_health_csv,
    rows: Sequence[HealthRow],
    check_index: int,
    expected_height: float,
) -> None:
    path = write_health_csv(list(rows))
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    assert shealth.heights[check_index] == expected_height
