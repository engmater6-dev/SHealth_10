"""Weight imputation tests (TC #10)."""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from shealth import SHealth


def test_impute_weight_by_age_band(write_health_csv):
    """20s: w=60 and w=0 → missing weight imputed to age-band average 60 (TC #10)."""
    path = write_health_csv(
        [
            ("1", 25, 60.0, 170.0),
            ("2", 28, 0.0, 175.0),
        ]
    )
    shealth = SHealth()
    shealth.calculate_bmi(str(path))
    assert shealth.weights[1] == 60.0
    expected_bmi = 60.0 / ((175.0 / 100.0) ** 2)
    assert shealth.bmis[1] == expected_bmi
