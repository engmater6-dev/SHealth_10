"""Weight imputation tests (TC #10~14)."""

from __future__ import annotations

import sys
import os
from typing import Sequence, Tuple

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import SHealth

HealthRow = Tuple[str, int, float, float]


def test_impute_weight_by_age_band(write_health_csv) -> None:
    """20s: w=60 and w=0 → missing weight imputed to age-band average 60 (TC #10)."""
    path = write_health_csv(
        [
            ("1", 25, 60.0, 170.0),
            ("2", 28, 0.0, 175.0),
        ]
    )
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    assert shealth.weights[1] == 60.0
    expected_bmi = 60.0 / ((175.0 / 100.0) ** 2)
    assert shealth.bmis[1] == expected_bmi


@pytest.mark.parametrize(
    "rows,check_index,expected_weight",
    [
        pytest.param(
            [
                ("1", 35, 50.0, 170.0),
                ("2", 36, 80.0, 170.0),
                ("3", 37, 0.0, 170.0),
                ("4", 38, 0.0, 170.0),
            ],
            2,
            65.0,
            id="tc11_multiple_zeros_same_average",
        ),
        pytest.param(
            [
                ("1", 25, 0.0, 170.0),
                ("2", 28, 60.0, 170.0),
                ("3", 35, 90.0, 170.0),
            ],
            0,
            60.0,
            id="tc12_age_band_isolation",
        ),
    ],
)
def test_impute_weight_parametrize(
    write_health_csv,
    rows: Sequence[HealthRow],
    check_index: int,
    expected_weight: float,
) -> None:
    path = write_health_csv(list(rows))
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    assert shealth.weights[check_index] == expected_weight


def test_impute_weight_all_zero_in_band_stays_zero(write_health_csv) -> None:
    """40s: all w=0 → no valid sample; weight remains 0 (current policy, TC #13)."""
    path = write_health_csv(
        [
            ("1", 45, 0.0, 170.0),
            ("2", 46, 0.0, 175.0),
        ]
    )
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    assert shealth.weights == [0.0, 0.0]
    assert shealth.bmis == [0.0, 0.0]
