from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HealthRecord:
    """단일 사용자 건강 데이터 레코드."""

    id: int
    age: int
    weight: float
    height: float
    bmi: float = 0.0
