"""Golden Master approval tests for CLI stdout (TC #44)."""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import AGE_BANDS
from texttest_fixture import (
    approve_output,
    capture_cli_stdout,
    golden_dir,
    normalize_output,
    project_root,
)

GOLDEN_SHEALTH_DAT = golden_dir() / "shealth_dat_stdout.txt"
SHEALTH_DAT = project_root() / "shealth.dat"


@pytest.mark.golden_master
def test_golden_master_shealth_dat_stdout() -> None:
    """Full CLI output for shealth.dat matches committed golden file."""
    assert SHEALTH_DAT.is_file(), f"Missing fixture data: {SHEALTH_DAT}"
    actual = capture_cli_stdout(SHEALTH_DAT, use_subprocess=False)
    lines = [line for line in normalize_output(actual).splitlines() if line.strip()]
    assert len(lines) == len(AGE_BANDS)
    approve_output(actual, GOLDEN_SHEALTH_DAT)


@pytest.mark.golden_master
def test_golden_master_subprocess_matches_inprocess() -> None:
    """Subprocess and in-process capture produce the same stdout."""
    assert SHEALTH_DAT.is_file()
    in_proc = normalize_output(capture_cli_stdout(SHEALTH_DAT, use_subprocess=False))
    sub_proc = normalize_output(capture_cli_stdout(SHEALTH_DAT, use_subprocess=True))
    assert in_proc == sub_proc
