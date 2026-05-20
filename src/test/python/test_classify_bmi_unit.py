"""Unit tests for module-level classify_bmi (Phase 03)."""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import BmiCategory, SHealth, classify_bmi

CLASSIFY_CASES = [
    pytest.param(17.0, SHealth.UNDERWEIGHT, id="bmi_17.0"),
    pytest.param(18.5, SHealth.UNDERWEIGHT, id="bmi_18.5"),
    pytest.param(18.500001, SHealth.NORMALWEIGHT, id="bmi_18.500001"),
    pytest.param(21.0, SHealth.NORMALWEIGHT, id="bmi_21.0"),
    pytest.param(22.999, SHealth.NORMALWEIGHT, id="bmi_22.999"),
    pytest.param(23.0, SHealth.OVERWEIGHT, id="bmi_23.0"),
    pytest.param(24.999, SHealth.OVERWEIGHT, id="bmi_24.999"),
    pytest.param(25.0, SHealth.OBESITY, id="bmi_25.0"),
    pytest.param(30.0, SHealth.OBESITY, id="bmi_30.0"),
    pytest.param(46.875, SHealth.OBESITY, id="bmi_46.875_extreme"),
]


@pytest.mark.parametrize("bmi,expected", CLASSIFY_CASES)
def test_classify_bmi_unit(bmi: float, expected: int) -> None:
    assert classify_bmi(bmi) == expected
    assert classify_bmi(bmi).value == expected
    assert isinstance(classify_bmi(bmi), BmiCategory)
