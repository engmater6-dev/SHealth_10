"""Invalid CSV row handling tests (TC #38~39, #41)."""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import SHealth


def test_skip_non_numeric_row_with_warning(write_health_csv, caplog) -> None:
    """Non-numeric field → skip row, WARNING logged (TC #38)."""
    path = write_health_csv([("1", 25, 70.0, 170.0)], filename="mixed.dat")
    content = path.read_text(encoding="utf-8")
    lines = content.strip().splitlines()
    lines.insert(2, "abc,25,70,170")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with caplog.at_level("WARNING"):
        shealth = SHealth()
        count = shealth.calculate_bmi(str(path))

    assert count == 1
    assert shealth.weights == [70.0]
    assert any("Skipping invalid CSV row" in record.message for record in caplog.records)


def test_skip_short_row_with_warning(tmp_path, caplog) -> None:
    """Too few columns → skip + WARNING (TC #39)."""
    path = tmp_path / "short.dat"
    path.write_text("id,age,weight,height\n1,20,70\n", encoding="utf-8")

    with caplog.at_level("WARNING"):
        shealth = SHealth()
        count = shealth.calculate_bmi(str(path))

    assert count == 0
    assert any("Skipping invalid CSV row" in record.message for record in caplog.records)


@pytest.mark.parametrize(
    "bad_row",
    [
        "2,25,-1,170",
        "2,25,70,-1",
    ],
    ids=["negative_weight", "negative_height"],
)
def test_skip_negative_weight_or_height_with_warning(
    write_health_csv, caplog, bad_row: str
) -> None:
    """Negative weight or height → skip row, WARNING logged (TC #41)."""
    path = write_health_csv([("1", 25, 70.0, 170.0)], filename="neg.dat")
    content = path.read_text(encoding="utf-8")
    lines = content.strip().splitlines()
    lines.insert(2, bad_row)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with caplog.at_level("WARNING"):
        shealth = SHealth()
        count = shealth.calculate_bmi(str(path))

    assert count == 1
    assert shealth.weights == [70.0]
    assert shealth.heights == [170.0]
    assert any("Skipping invalid CSV row" in record.message for record in caplog.records)
