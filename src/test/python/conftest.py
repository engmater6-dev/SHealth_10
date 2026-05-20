"""pytest fixtures for SHealth tests."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Sequence, Tuple

import pytest

from texttest_fixture import golden_dir as _golden_dir


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--golden",
        action="store_true",
        default=False,
        help="Run golden_master tests (same as -m golden_master).",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "golden_master: Golden Master stdout approval tests (TC #44)",
    )


@pytest.fixture
def golden_dir() -> Path:
    """Path to ``src/test/golden``."""
    return _golden_dir()

# CSV row: (id, age, weight, height)
HealthRow = Tuple[str, int, float, float]


@pytest.fixture
def write_health_csv(tmp_path: Path):
    """Write a minimal shealth-format CSV and return its path."""

    def _write(rows: Sequence[HealthRow], filename: str = "test.dat") -> Path:
        path = tmp_path / filename
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "age", "weight", "height"])
            for row in rows:
                writer.writerow(row)
        return path

    return _write
