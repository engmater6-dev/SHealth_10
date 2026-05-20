from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, Protocol

from models import HealthRecord

logger = logging.getLogger(__name__)

FIELD_ID = "id"
FIELD_AGE = "age"
FIELD_WEIGHT = "weight"
FIELD_HEIGHT = "height"


class BmiCategory(IntEnum):
    UNDERWEIGHT = 100
    NORMALWEIGHT = 200
    OVERWEIGHT = 300
    OBESITY = 400


@dataclass(frozen=True)
class BmiThresholds:
    """BMI 분류 임계값 (README 기준)."""

    underweight_max: float = 18.5
    normal_max: float = 23.0
    overweight_max: float = 25.0


BMI_THRESHOLDS = BmiThresholds()
AGE_BAND_START = 20
AGE_BAND_END = 80
AGE_BAND_STEP = 10
AGE_BANDS: tuple[int, ...] = tuple(
    range(AGE_BAND_START, AGE_BAND_END, AGE_BAND_STEP)
)


def age_bands() -> range:
    """10년 단위 나이대 시작값(20, 30, …, 70)을 반환한다."""
    return range(AGE_BAND_START, AGE_BAND_END, AGE_BAND_STEP)


def in_age_band(age: int, age_band_start: int) -> bool:
    """나이가 age_band_start 이상 age_band_start+STEP 미만이면 True."""
    return age_band_start <= age < age_band_start + AGE_BAND_STEP


class SupportsBmiClassification(Protocol):
    """BMI 분류 전략 인터페이스 (구조적 typing).

    - 상속 없이 ``classify(bmi)`` 만 구현하면 주입 가능 (OCP).
    - ``isinstance`` 검사용 ABC 대신 Protocol: 정적 타입·IDE 지원, 런타임 계층 최소화.
    - 분류 규칙 변경 시 ``SHealth`` 집계 코드는 수정하지 않고 Classifier만 교체.
    """

    def classify(self, bmi: float) -> BmiCategory:
        ...


class WhoAsiaPacificClassifier:
    """WHO 아시아·태평양 기준 BMI 분류 (README 기본 임계값)."""

    def __init__(self, thresholds: Optional[BmiThresholds] = None) -> None:
        self._thresholds = thresholds or BMI_THRESHOLDS

    def classify(self, bmi: float) -> BmiCategory:
        thresholds = self._thresholds
        if bmi <= thresholds.underweight_max:
            return BmiCategory.UNDERWEIGHT
        if bmi < thresholds.normal_max:
            return BmiCategory.NORMALWEIGHT
        if bmi < thresholds.overweight_max:
            return BmiCategory.OVERWEIGHT
        return BmiCategory.OBESITY


def classify_bmi(
    bmi: float, thresholds: BmiThresholds = BMI_THRESHOLDS
) -> BmiCategory:
    """BMI → BmiCategory (100~400). 모듈 수준 하위 호환 thin wrapper."""
    return WhoAsiaPacificClassifier(thresholds).classify(bmi)


def _is_blank_row(row: dict[str, str | None]) -> bool:
    """DictReader 행이 비어 있으면 True."""
    return not any(str(value).strip() for value in row.values() if value is not None)


class SHealth:
    """S-Health BMI 계산 클래스"""

    # BMI 유형 상수 (기존 int API 호환)
    UNDERWEIGHT = int(BmiCategory.UNDERWEIGHT)
    NORMALWEIGHT = int(BmiCategory.NORMALWEIGHT)
    OVERWEIGHT = int(BmiCategory.OVERWEIGHT)
    OBESITY = int(BmiCategory.OBESITY)

    count: int
    _classifier: SupportsBmiClassification
    _records: list[HealthRecord]
    _bmi_ratios: dict[tuple[int, int], float]

    def __init__(
        self, classifier: Optional[SupportsBmiClassification] = None
    ) -> None:
        self._classifier = classifier or WhoAsiaPacificClassifier()
        self.count = 0
        self._records = []
        self._bmi_ratios = {}

    @property
    def ages(self) -> list[int]:
        """하위 호환: 나이 목록 (읽기 전용 복사)."""
        return [record.age for record in self._records]

    @property
    def weights(self) -> list[float]:
        """하위 호환: 체중 목록 (읽기 전용 복사)."""
        return [record.weight for record in self._records]

    @property
    def heights(self) -> list[float]:
        """하위 호환: 키 목록 (읽기 전용 복사)."""
        return [record.height for record in self._records]

    @property
    def bmis(self) -> list[float]:
        """하위 호환: BMI 목록 (읽기 전용 복사)."""
        return [record.bmi for record in self._records]

    def calculate_bmi(self, filename: str) -> int:
        """파일에서 데이터를 읽어 BMI를 계산한다."""
        self._reset_state()
        if self._load_records(filename) == 0 and not self._records:
            return 0
        self._impute_weights()
        self._compute_bmis()
        self._aggregate_ratios()
        return self.count

    def _reset_state(self) -> None:
        """count·레코드·비율 딕셔너리를 초기화한다."""
        self.count = 0
        self._records = []
        self._bmi_ratios = {}

    def _records_in_band(self, age_band_start: int) -> list[HealthRecord]:
        """나이대 구간에 속한 레코드 목록."""
        return [
            record
            for record in self._records
            if in_age_band(record.age, age_band_start)
        ]

    def _load_records(self, filename: str) -> int:
        """CSV 파일을 읽어 내부 리스트를 채우고 레코드 수를 반환한다."""
        try:
            with open(filename, newline="", encoding="utf-8") as file_handle:
                reader = csv.DictReader(file_handle)
                for row in reader:
                    if _is_blank_row(row):
                        continue
                    self._records.append(
                        HealthRecord(
                            id=int(float(row[FIELD_ID])),
                            age=int(row[FIELD_AGE]),
                            weight=float(row[FIELD_WEIGHT]),
                            height=float(row[FIELD_HEIGHT]),
                        )
                    )
                    self.count += 1
        except FileNotFoundError:
            logger.error("Failed to open file: %s", filename)
            return 0
        return self.count

    def _impute_weights(self) -> None:
        """weight=0인 레코드에 나이대별 평균 체중을 적용한다."""
        for age_band_start in AGE_BANDS:
            band_records = self._records_in_band(age_band_start)
            valid_weights = [
                record.weight for record in band_records if record.weight != 0.0
            ]
            if not valid_weights:
                continue
            valid_weight_count = len(valid_weights)
            avg_weight = sum(valid_weights) / valid_weight_count
            for record in band_records:
                if record.weight == 0.0:
                    record.weight = avg_weight

    def _compute_bmis(self) -> None:
        """보정된 체중·키로 각 레코드의 BMI를 계산한다."""
        for record in self._records:
            height_m = record.height / 100.0
            record.bmi = record.weight / (height_m ** 2)

    def _aggregate_ratios(self) -> None:
        """나이대별 BMI 범주 비율을 _bmi_ratios에 저장한다."""
        for age_band_start in AGE_BANDS:
            band_records = self._records_in_band(age_band_start)
            band_size = len(band_records)
            if band_size == 0:
                continue

            counts = {category: 0 for category in BmiCategory}
            for record in band_records:
                category = self._classifier.classify(record.bmi)
                counts[category] += 1

            for category in BmiCategory:
                ratio_key = (age_band_start, category.value)
                self._bmi_ratios[ratio_key] = counts[category] * 100 / band_size

    def get_bmi_ratio(self, age_class: int, bmi_type: int) -> float:
        """나이대와 BMI 유형에 따른 비율을 반환한다."""
        return self._bmi_ratios.get((age_class, bmi_type), 0.0)
