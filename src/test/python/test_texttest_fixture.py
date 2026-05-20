"""Unit tests for texttest_fixture helpers (not golden comparison)."""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import AGE_BANDS
from texttest_fixture import capture_cli_stdout, normalize_output


def test_capture_cli_stdout_mini_csv(write_health_csv) -> None:
    path = write_health_csv([("1", 25, 70.0, 170.0)])
    out = capture_cli_stdout(path, use_subprocess=False)
    lines = [line for line in normalize_output(out).splitlines() if line.strip()]
    assert len(lines) == len(AGE_BANDS)
    assert lines[0].startswith("20 - underweight = ")


def test_normalize_output_strips_trailing_blank_lines() -> None:
    assert normalize_output("a\nb\n\n") == "a\nb\n"
