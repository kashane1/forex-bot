from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from research.crypto.coinbase import iter_coinbase_chunks, parse_coinbase_candles


def test_parse_coinbase_candles_mid_and_spread_proxy():
    ts = int(datetime(2024, 1, 1, 0, 0, tzinfo=UTC).timestamp())
    payload = [[ts, 990.0, 1010.0, 1000.0, 1005.0, 12.5]]
    rows = parse_coinbase_candles(payload, instrument="BTC_USD", granularity="M1")
    assert len(rows) == 1
    row = rows[0]
    assert row.mid_c == 1005.0
    assert row.bid_c < row.mid_c < row.ask_c
    assert row.volume == 12


def test_incomplete_rows_skipped():
    rows = parse_coinbase_candles([], instrument="ETH_USD", granularity="M1")
    assert rows == []


def test_iter_coinbase_chunks_seven_days():
    start = datetime(2024, 1, 1, tzinfo=UTC)
    end = datetime(2024, 1, 7, 23, 59, tzinfo=UTC)
    chunks = iter_coinbase_chunks(start, end, granularity="M1")
    assert len(chunks) >= 34
    assert chunks[0][0] == start
