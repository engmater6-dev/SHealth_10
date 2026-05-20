"""CSV load tests (Phase 04 — DictReader, blank row continue)."""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import SHealth


def test_load_records_skips_blank_row_in_middle(write_health_csv):
    """중간 빈 행 이후 레코드도 로드한다 (break 대비 count 증가, TC #37)."""
    path = write_health_csv(
        [
            ("1", 25, 70.0, 170.0),
            ("2", 28, 80.0, 175.0),
        ],
        filename="with_blank.dat",
    )
    # 헤더 + row1 + blank + row2 형태로 수동 삽입
    content = path.read_text(encoding="utf-8")
    lines = content.strip().splitlines()
    lines.insert(2, ",,,")  # 빈 데이터 행
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    shealth = SHealth()
    count = shealth.calculate_bmi(str(path))
    assert count == 2
    assert shealth.weights == [70.0, 80.0]


def test_header_only_csv_returns_zero(write_health_csv) -> None:
    """헤더만 → count 0, ratios empty (TC #37)."""
    path = write_health_csv([])
    shealth = SHealth()
    count = shealth.calculate_bmi(str(path))
    assert count == 0
    assert shealth.get_bmi_ratio(20, SHealth.UNDERWEIGHT) == 0.0


def test_calculate_bmi_returns_row_count(write_health_csv) -> None:
    """N data rows → return N (TC #43)."""
    path = write_health_csv(
        [
            ("1", 25, 70.0, 170.0),
            ("2", 35, 80.0, 175.0),
            ("3", 45, 90.0, 180.0),
        ]
    )
    shealth = SHealth()
    assert shealth.calculate_bmi(str(path)) == 3
