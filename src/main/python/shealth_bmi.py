"""S-Health BMI 통계 CLI 진입점."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from shealth import AGE_BANDS, BmiCategory, SHealth

logger = logging.getLogger(__name__)

_CATEGORIES = (
    BmiCategory.UNDERWEIGHT,
    BmiCategory.NORMALWEIGHT,
    BmiCategory.OVERWEIGHT,
    BmiCategory.OBESITY,
)

_CATEGORY_LABELS = {
    BmiCategory.UNDERWEIGHT: "underweight",
    BmiCategory.NORMALWEIGHT: "normal",
    BmiCategory.OVERWEIGHT: "overweight",
    BmiCategory.OBESITY: "obesity",
}


def format_age_band_report(age: int, shealth: SHealth) -> str:
    """나이대별 BMI 비율 한 줄 리포트 문자열을 반환한다."""
    parts = [
        f"{_CATEGORY_LABELS[cat]} = {shealth.get_bmi_ratio(age, cat.value):.6f}"
        for cat in _CATEGORIES
    ]
    return f"{age} - " + ", ".join(parts)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """CLI 인자를 파싱한다."""
    parser = argparse.ArgumentParser(
        description="Print age-band BMI distribution ratios from a health CSV file."
    )
    parser.add_argument(
        "data_file",
        nargs="?",
        default=Path("shealth.dat"),
        type=Path,
        help="Input CSV file (default: shealth.dat)",
    )
    return parser.parse_args(argv)


def main() -> None:
    """CSV를 읽어 나이대별 BMI 비율을 stdout에 출력한다."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    args = parse_args()
    data_path = args.data_file

    shealth = SHealth()
    count = shealth.calculate_bmi(str(data_path))
    if count == 0:
        logger.info("No records loaded from %s", data_path)

    for age in AGE_BANDS:
        print(format_age_band_report(age, shealth))


if __name__ == "__main__":
    main()
