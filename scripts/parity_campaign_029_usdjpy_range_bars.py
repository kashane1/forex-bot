"""CAMPAIGN_029 Phase 4 — parity harness (primary engine vs independent verifier).

Runs the FROZEN rule over the **train** window with both the primary M1-resolved
engine (``range_bar_execution``) and the independent verifier
(``campaign_029_parity``, no shared execution code), then compares entries / exit
reasons / per-trade R against the frozen acceptance bar
(``CAMPAIGN_029_BACKTRADER_PARITY_DESIGN.md`` §6). No lockbox; no evidence verdict.
Output: research/campaign_029/parity/parity_summary.json.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import get_research_database_config
from forex_bot.project_env import bootstrap_environ
from forex_bot.research.campaign_029_loader import load_campaign_029_inputs
from forex_bot.research.campaign_029_parity import compare, independent_verify
from forex_bot.research.range_bar_execution import (
    precompute_d1agg_regimes,
    precompute_h4_trends,
    run_range_bar_execution,
)
from forex_bot.strategies.usdjpy_range_bar_mtf_breakout import RangeBarMtfBreakoutConfig

TRAIN = (datetime(2021, 5, 27, tzinfo=UTC), datetime(2023, 12, 31, 23, 59, tzinfo=UTC))
H4_STALE_S = 8 * 3600
D1_STALE_S = 3 * 24 * 3600


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--to", default=None, help="override END (smoke); never enters the lockbox")
    args = p.parse_args()

    bootstrap_environ()
    store = PostgresCandleStore(get_research_database_config())
    params = RangeBarMtfBreakoutConfig()
    to = datetime.fromisoformat(args.to).replace(tzinfo=UTC) if args.to else TRAIN[1]
    if to >= datetime(2025, 1, 1, tzinfo=UTC):
        print("REFUSED: parity window cannot enter the test lockbox")
        return 2

    inp = load_campaign_029_inputs(store, from_utc=TRAIN[0], to_utc=to)
    h4 = precompute_h4_trends(inp.h4_frame, inp.decision_times, params, max_staleness_seconds=H4_STALE_S)
    d1 = precompute_d1agg_regimes(inp.d1agg_frame, inp.decision_times, params, max_staleness_seconds=D1_STALE_S)

    primary = run_range_bar_execution(
        range_bars=inp.range_bars, m1_index=inp.m1_index, h4_trends=h4, d1_regimes=d1, params=params, fixed_slippage_pips=0.2
    )
    verifier = independent_verify(
        range_bars=inp.range_bars, m1_index=inp.m1_index, h4_trends=h4, d1_regimes=d1, params=params, fixed_slippage_pips=0.2
    )
    report = compare(primary, verifier)
    report["window"] = {"from": TRAIN[0].isoformat(), "to": to.isoformat()}
    report["range_bars"] = len(inp.decision_times)
    report["campaign"] = "CAMPAIGN_029"
    report["test_lockbox_opened"] = False
    report["approved"] = False

    out_dir = ROOT / "research" / "campaign_029" / "parity"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "parity_summary.json"
    path.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"wrote {path}")
    print(f"PARITY {report['status']}: primary={report['primary_trades']} verifier={report['verifier_trades']} "
          f"exit_share={report['exit_reason_aligned_share']} mean_r_diff={report['mean_net_r_diff']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
