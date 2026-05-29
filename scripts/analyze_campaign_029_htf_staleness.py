"""CAMPAIGN_029 Phase 2 — quantify H4M1 / D1AGG availability & staleness.

Builds 10-pip USD_JPY range bars over train+validation, aligns H4M1 and
native-H4-derived D1AGG to each range-bar decision, and reports missing / stale
counts + max staleness against candidate bounds. NO signals, trades, or P&L; the
test window is never loaded. Output: research/campaign_029/execution/htf_staleness_summary.json.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import get_research_database_config
from forex_bot.project_env import bootstrap_environ
from forex_bot.research.campaign_029_loader import load_campaign_029_inputs, staleness_stats
from forex_bot.research.range_bar_execution import precompute_d1agg_regimes, precompute_h4_trends
from forex_bot.strategies.usdjpy_range_bar_mtf_breakout import RangeBarMtfBreakoutConfig

TRAIN = (datetime(2021, 5, 27, tzinfo=UTC), datetime(2023, 12, 31, 23, 59, tzinfo=UTC))
VALID = (datetime(2024, 1, 1, tzinfo=UTC), datetime(2024, 12, 31, 23, 59, tzinfo=UTC))
H4_BOUND_S = 8 * 3600        # candidate: 2 x H4
D1_BOUND_S = 3 * 24 * 3600   # candidate: 3 calendar days (covers weekend gaps)


def main() -> int:
    bootstrap_environ()
    store = PostgresCandleStore(get_research_database_config())
    params = RangeBarMtfBreakoutConfig()

    out: dict = {
        "campaign": "CAMPAIGN_029",
        "purpose": "HTF/D1AGG availability + staleness (no signals/trades/PnL)",
        "candidate_bounds": {"h4_seconds": H4_BOUND_S, "d1agg_seconds": D1_BOUND_S},
        "splits": {},
        "test_window_loaded": False,
    }
    for name, (f, t) in (("train", TRAIN), ("validation", VALID)):
        inp = load_campaign_029_inputs(store, from_utc=f, to_utc=t)
        h4 = precompute_h4_trends(inp.h4_frame, inp.decision_times, params)
        d1 = precompute_d1agg_regimes(inp.d1agg_frame, inp.decision_times, params)
        out["splits"][name] = {
            "from": f.isoformat(),
            "to": t.isoformat(),
            "range_bars": len(inp.decision_times),
            "m1_rows": inp.m1_rows_consumed,
            "h4_frame_bars": len(inp.h4_frame.completed_only().df),
            "d1agg_frame_bars": (len(inp.d1agg_frame.completed_only().df) if inp.d1agg_frame else 0),
            "h4": staleness_stats(inp.decision_times, h4, max_staleness_seconds=H4_BOUND_S),
            "d1agg": staleness_stats(inp.decision_times, d1, max_staleness_seconds=D1_BOUND_S),
        }
        print(f"[{name}] bars={len(inp.decision_times)} "
              f"h4_missing={out['splits'][name]['h4']['missing']} "
              f"h4_stale={out['splits'][name]['h4']['stale_over_bound']} "
              f"h4_max={out['splits'][name]['h4']['max_staleness_seconds']}s | "
              f"d1_missing={out['splits'][name]['d1agg']['missing']} "
              f"d1_stale={out['splits'][name]['d1agg']['stale_over_bound']} "
              f"d1_max={out['splits'][name]['d1agg']['max_staleness_seconds']}s")

    out_dir = ROOT / "research" / "campaign_029" / "execution"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "htf_staleness_summary.json"
    path.write_text(json.dumps(out, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
