"""CLI main() integration tests."""

from __future__ import annotations

import argparse
import logging
import sys
import os
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import AGE_BANDS
import shealth_bmi


def test_main_prints_all_age_bands(
    write_health_csv, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write_health_csv([("1", 25, 70.0, 170.0)])

    def _fake_parse_args(argv=None):
        return argparse.Namespace(data_file=path)

    monkeypatch.setattr(shealth_bmi, "parse_args", _fake_parse_args)
    shealth_bmi.main()
    out = capsys.readouterr().out
    lines = [line for line in out.strip().splitlines() if line.strip()]
    assert len(lines) == len(AGE_BANDS)
    assert all(line.startswith(f"{age} - underweight = ") for age, line in zip(AGE_BANDS, lines))


def test_main_logs_info_when_no_records(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    empty = tmp_path / "empty.dat"
    empty.write_text("id,age,weight,height\n", encoding="utf-8")

    def _fake_parse_args(argv=None):
        return argparse.Namespace(data_file=empty)

    monkeypatch.setattr(shealth_bmi, "parse_args", _fake_parse_args)
    caplog.set_level(logging.INFO)
    shealth_bmi.main()
    assert any("No records loaded" in r.message for r in caplog.records)
