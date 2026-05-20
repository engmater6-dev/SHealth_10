"""BMI formula tests (TC #1~2)."""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import SHealth


@pytest.mark.parametrize(
    "weight,height_cm,expected_bmi",
    [
        pytest.param(70.0, 175.0, 70.0 / (1.75**2), id="standard_70kg_175cm"),
        pytest.param(70.0, 180.0, 70.0 / (1.80**2), id="height_cm_to_m_180cm"),
    ],
)
def test_bmi_formula_via_compute(
    write_health_csv, weight: float, height_cm: float, expected_bmi: float
) -> None:
    """BMI = kg / (height_m)² after load and impute (TC #1~2)."""
    path = write_health_csv([("1", 25, weight, height_cm)])
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    assert shealth.bmis[0] == pytest.approx(expected_bmi, rel=1e-9)
