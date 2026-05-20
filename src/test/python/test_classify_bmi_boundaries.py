"""BMI classification boundary tests (integration via age-group ratios)."""

from __future__ import annotations

import math
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import SHealth

HEIGHT_CM = 170.0


def _weight_for_bmi(bmi: float, height_cm: float = HEIGHT_CM) -> float:
    weight = bmi * (height_cm / 100.0) ** 2
    # BMI 25.0 등: weight 역산 후 재계산 시 24.999…가 되는 float 드리프트 방지
    if bmi >= 25.0:
        weight = math.nextafter(weight, float("inf"))
    return weight


# (target_bmi, expected_bmi_type) — weight derived to avoid float drift
BOUNDARY_CASES = [
    pytest.param(18.5, SHealth.UNDERWEIGHT, id="bmi_18.5_underweight"),
    pytest.param(18.500001, SHealth.NORMALWEIGHT, id="bmi_18.500001_normal"),
    pytest.param(23.0, SHealth.OVERWEIGHT, id="bmi_23.0_overweight"),
    pytest.param(25.0, SHealth.OBESITY, id="bmi_25.0_obesity"),
]


@pytest.mark.parametrize("target_bmi,expected_type", BOUNDARY_CASES)
def test_classify_bmi_boundaries(write_health_csv, target_bmi, expected_type):
    """Single 20s record; expect 100% in one BMI category (TC #15-21)."""
    weight = _weight_for_bmi(target_bmi)
    path = write_health_csv([("1", 25, weight, HEIGHT_CM)])
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    assert shealth.get_bmi_ratio(20, expected_type) == pytest.approx(100.0)
    for other in (
        SHealth.UNDERWEIGHT,
        SHealth.NORMALWEIGHT,
        SHealth.OVERWEIGHT,
        SHealth.OBESITY,
    ):
        if other != expected_type:
            assert shealth.get_bmi_ratio(20, other) == pytest.approx(0.0)
