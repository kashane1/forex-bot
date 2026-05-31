from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from research.crypto.validation import expected_m1_bars


def test_expected_m1_bars_inclusive():
    start = datetime(2024, 1, 1, 0, 0, tzinfo=UTC)
    end = datetime(2024, 1, 1, 0, 6, tzinfo=UTC)
    assert expected_m1_bars(start, end) == 7


def test_expected_m1_bars_one_minute():
    start = datetime(2024, 1, 1, 0, 0, tzinfo=UTC)
    end = datetime(2024, 1, 1, 0, 0, tzinfo=UTC)
    assert expected_m1_bars(start, end) == 1
