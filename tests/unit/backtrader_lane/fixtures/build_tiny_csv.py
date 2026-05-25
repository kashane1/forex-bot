"""Generate the tiny deterministic CSV + provenance fixtures used by the
adapter tests.

This is a build helper, not a test. It writes:

  tests/unit/backtrader_lane/fixtures/TEST_PAIR_H4_lean.csv
  tests/unit/backtrader_lane/fixtures/TEST_PAIR_H4_lean.provenance.json

The sha256 in the provenance JSON is recomputed *from* the CSV the
script writes, so the fixture is self-consistent. The CSV is small
enough (12 rows) to commit.

Run with:
    python tests/unit/backtrader_lane/fixtures/build_tiny_csv.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parent
HEADER = [
    "time",
    "bid_open",
    "bid_high",
    "bid_low",
    "bid_close",
    "ask_open",
    "ask_high",
    "ask_low",
    "ask_close",
    "volume",
]
PAIR = "TEST_PAIR"
START = datetime(2024, 1, 1, 22, 0, 0, tzinfo=UTC)
N_BARS = 12
BASE_BID = 1.10000
STEP = 0.00010
SPREAD = 0.00020


def _build_rows() -> list[list[str]]:
    rows: list[list[str]] = []
    for i in range(N_BARS):
        t = START + timedelta(hours=4 * i)
        bid_o = BASE_BID + i * STEP
        bid_h = bid_o + 0.5 * STEP
        bid_l = bid_o - 0.5 * STEP
        bid_c = bid_o + 0.2 * STEP
        ask_o = bid_o + SPREAD
        ask_h = bid_h + SPREAD
        ask_l = bid_l + SPREAD
        ask_c = bid_c + SPREAD
        rows.append(
            [
                t.isoformat(),
                f"{bid_o:.5f}",
                f"{bid_h:.5f}",
                f"{bid_l:.5f}",
                f"{bid_c:.5f}",
                f"{ask_o:.5f}",
                f"{ask_h:.5f}",
                f"{ask_l:.5f}",
                f"{ask_c:.5f}",
                "100",
            ]
        )
    return rows


def _compute_sha(rows: list[list[str]]) -> str:
    h = hashlib.sha256()
    for row in sorted(rows, key=lambda r: r[0]):
        h.update(("|".join(row)).encode("utf-8"))
    return h.hexdigest()


def main(out_dir: Path = FIXTURE_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = _build_rows()
    csv_path = out_dir / f"{PAIR}_H4_lean.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(HEADER)
        writer.writerows(rows)
    sha = _compute_sha(rows)
    prov_path = out_dir / f"{PAIR}_H4_lean.provenance.json"
    provenance = {
        "instrument": PAIR,
        "granularity": "H4",
        "source": "oanda-test-fixture",
        "requested_from": rows[0][0],
        "requested_to": rows[-1][0],
        "candle_count": len(rows),
        "first_ts": rows[0][0],
        "last_ts": rows[-1][0],
        "data_sha256": sha,
        "campaign_002_data_request_hash": "deadbeefcafef00d",
        "lean_csv": csv_path.name,
        "exported_by": "tests/unit/backtrader_lane/fixtures/build_tiny_csv.py",
        "exported_at": "2026-05-24T00:00:00+00:00",
        "note": (
            "Synthetic deterministic H4 fixture for the Backtrader-lane data-adapter "
            "tests. NOT real OANDA data. NOT campaign evidence. strategy_evidence: false."
        ),
    }
    prov_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {csv_path}")
    print(f"wrote {prov_path}")


if __name__ == "__main__":
    main()
    sys.exit(0)
