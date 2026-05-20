"""Golden Master helpers: capture CLI stdout and approve against golden files.

Usage (Phase 03)::

    actual = capture_cli_stdout(project_root() / "shealth.dat")
    approve_output(actual, golden_dir() / "shealth_dat_stdout.txt")
"""

from __future__ import annotations

import difflib
import os
import subprocess
import sys
from pathlib import Path

import pytest

# In-process imports (tests add src/main/python to sys.path)
_MAIN_PYTHON = Path(__file__).resolve().parents[2] / "main" / "python"
if str(_MAIN_PYTHON) not in sys.path:
    sys.path.insert(0, str(_MAIN_PYTHON))


def project_root() -> Path:
    """Repository root (parent of ``src/``)."""
    return Path(__file__).resolve().parents[3]


def golden_dir() -> Path:
    """Directory for golden master expected output files."""
    return Path(__file__).resolve().parents[1] / "golden"


def normalize_output(text: str) -> str:
    """Normalize line endings and trailing whitespace for stable comparison."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in normalized.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + ("\n" if lines else "")


def read_golden(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_golden(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalize_output(content), encoding="utf-8", newline="\n")


def capture_cli_stdout_inprocess(data_file: Path) -> str:
    """Capture ``shealth_bmi.main()`` stdout (logging goes to stderr)."""
    import argparse
    from io import StringIO

    import shealth_bmi

    argv_backup = sys.argv
    try:
        captured = StringIO()
        sys.stdout = captured

        def _parse_args(argv=None):
            return argparse.Namespace(data_file=data_file)

        original_parse = shealth_bmi.parse_args
        shealth_bmi.parse_args = _parse_args
        try:
            shealth_bmi.main()
        finally:
            shealth_bmi.parse_args = original_parse
        return captured.getvalue()
    finally:
        sys.stdout = sys.__stdout__
        sys.argv = argv_backup


def capture_cli_stdout_subprocess(data_file: Path) -> str:
    """Run CLI as subprocess from project root (integration-style)."""
    script = project_root() / "src" / "main" / "python" / "shealth_bmi.py"
    data_path = data_file.resolve()
    result = subprocess.run(
        [sys.executable, str(script), str(data_path)],
        cwd=str(project_root()),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return result.stdout


def capture_cli_stdout(data_file: Path, *, use_subprocess: bool = False) -> str:
    """Capture age-band report lines printed by ``shealth_bmi.main()``."""
    if use_subprocess:
        return capture_cli_stdout_subprocess(data_file)
    return capture_cli_stdout_inprocess(data_file)


def approve_output(actual: str, golden_path: Path) -> None:
    """Compare *actual* to golden file; update when ``UPDATE_GOLDEN=1``."""
    actual_norm = normalize_output(actual)
    if os.environ.get("UPDATE_GOLDEN") == "1":
        write_golden(golden_path, actual_norm)
        return

    if not golden_path.is_file():
        write_golden(golden_path, actual_norm)
        pytest.fail(
            f"Golden master created at {golden_path}. "
            "Commit the file or set UPDATE_GOLDEN=1 to refresh intentionally."
        )

    expected_norm = normalize_output(read_golden(golden_path))
    if actual_norm == expected_norm:
        return

    diff = "\n".join(
        difflib.unified_diff(
            expected_norm.splitlines(keepends=True),
            actual_norm.splitlines(keepends=True),
            fromfile=str(golden_path),
            tofile="actual",
        )
    )
    pytest.fail(f"Golden master mismatch for {golden_path}:\n{diff}")
