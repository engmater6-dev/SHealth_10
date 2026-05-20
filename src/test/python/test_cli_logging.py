"""CLI and logging tests (Phase 06 — TC #42)."""

from __future__ import annotations

import logging
import sys
import os
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import SHealth
from shealth_bmi import format_age_band_report, parse_args


def test_file_not_found_logs_error(caplog: pytest.LogCaptureFixture) -> None:
    """존재하지 않는 파일: ERROR 로그, count=0 (TC #42)."""
    caplog.set_level(logging.ERROR, logger="shealth")
    shealth = SHealth()
    count = shealth.calculate_bmi("nonexistent.dat")
    assert count == 0
    assert any(
        r.levelname == "ERROR" and "Failed to open file" in r.message
        for r in caplog.records
    )


def test_format_age_band_report_six_decimal_places(write_health_csv) -> None:
    """리포트 형식: 라벨·소수 6자리 유지 (TC #44)."""
    path = write_health_csv([("1", 25, 70.0, 170.0)])
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    line = format_age_band_report(20, shealth)
    assert line.startswith("20 - underweight = ")
    assert ", normal = " in line
    assert ", overweight = " in line
    assert ", obesity = " in line
    # 소수 6자리 패턴 (예: 12.345678)
    import re

    assert re.search(r"=\s\d+\.\d{6}", line)


def test_parse_args_default_and_custom(tmp_path) -> None:
    custom = tmp_path / "custom.dat"
    custom.write_text("id,age,weight,height\n", encoding="utf-8")
    default_args = parse_args([])
    assert default_args.data_file == Path("shealth.dat")
    custom_args = parse_args([str(custom)])
    assert custom_args.data_file == custom
