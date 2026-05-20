"""BMI classifier protocol and strategy tests (Phase 07)."""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import BmiCategory, SHealth, WhoAsiaPacificClassifier, classify_bmi


class AllObesityClassifier:
    """Fake: 모든 BMI를 비만으로 분류 (Protocol duck typing)."""

    def classify(self, bmi: float) -> BmiCategory:
        return BmiCategory.OBESITY


def test_who_classifier_matches_classify_bmi() -> None:
    clf = WhoAsiaPacificClassifier()
    assert clf.classify(25.0) == classify_bmi(25.0)
    assert clf.classify(18.5) == BmiCategory.UNDERWEIGHT


def test_fake_classifier_injection(write_health_csv) -> None:
    """분류 정책 교체 시 SHealth 집계 코드 수정 없이 결과만 변경."""
    path = write_health_csv([("1", 25, 70.0, 170.0)])
    shealth = SHealth(classifier=AllObesityClassifier())
    shealth.calculate_bmi(str(path))
    assert shealth.get_bmi_ratio(20, BmiCategory.OBESITY) == pytest.approx(100.0)
    assert shealth.get_bmi_ratio(20, BmiCategory.NORMALWEIGHT) == pytest.approx(0.0)


def test_shealth_default_classifier_same_as_before(write_health_csv) -> None:
    path = write_health_csv([("1", 25, 70.0, 170.0)])
    default = SHealth()
    explicit = SHealth(classifier=WhoAsiaPacificClassifier())
    default.calculate_bmi(str(path))
    explicit.calculate_bmi(str(path))
    for cat in BmiCategory:
        assert default.get_bmi_ratio(20, cat) == explicit.get_bmi_ratio(20, cat)
