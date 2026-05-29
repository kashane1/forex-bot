"""CAMPAIGN_029 train/validation runner — usdjpy_range_bar_mtf_breakout 0.1.0-c029.

Research only. Resolves the FROZEN precommit rule into trades on the M1 tape
(``range_bar_execution``) over the **train** and (conditionally) **validation**
windows, applies the frozen gates, and writes compact artifacts under
``research/campaign_029/execution/``.

HARD REFUSALS — this runner will not:
  * open the **test lockbox** (2025-01-01 → 2026-05-20): ``--test`` / ``--backtest``
    / ``--open-lockbox`` are refused;
  * enable paper/demo/live or submit orders: ``--paper`` / ``--demo`` / ``--live``
    / ``--execute`` are refused;
  * approve anything (``approved_strategies.yaml`` stays empty).

Validation runs only if the train gate is **not catastrophic** (confirmation, not
rescue). No parameter tuning; the rule is frozen in
``docs/research/CAMPAIGN_029_PRECOMMIT_SCOPE.md``.

Usage (worktree: ``PYTHONPATH=$PWD/src:$PWD``)::

    python scripts/run_campaign_029_usdjpy_range_bar_mtf_breakout.py --train-validation
    python scripts/run_campaign_029_usdjpy_range_bar_mtf_breakout.py --train-validation --to 2021-09-01  # smoke
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import get_research_database_config
from forex_bot.project_env import bootstrap_environ
from forex_bot.research.campaign_029_gates import classify
from forex_bot.research.campaign_029_loader import load_campaign_029_inputs
from forex_bot.research.range_bar_execution import (
    precompute_d1agg_regimes,
    precompute_h4_trends,
    run_range_bar_execution,
    summarize_trades,
)
from forex_bot.strategies.usdjpy_range_bar_mtf_breakout import RangeBarMtfBreakoutConfig

TRAIN = (datetime(2021, 5, 27, tzinfo=UTC), datetime(2023, 12, 31, 23, 59, tzinfo=UTC))
VALID = (datetime(2024, 1, 1, tzinfo=UTC), datetime(2024, 12, 31, 23, 59, tzinfo=UTC))
TEST_LOCKBOX = (datetime(2025, 1, 1, tzinfo=UTC), datetime(2026, 5, 20, tzinfo=UTC))

H4_STALE_S = 8 * 3600          # frozen (Phase 2)
D1_STALE_S = 3 * 24 * 3600     # frozen (Phase 2)
FIXED_SLIPPAGE_PIPS = 0.2      # config backtest block
OUT_DIR = ROOT / "research" / "campaign_029" / "execution"

_REFUSED = ("--test", "--backtest", "--open-lockbox", "--paper", "--demo", "--live", "--execute")


def run_window(store: PostgresCandleStore, name: str, frm: datetime, to: datetime, params: RangeBarMtfBreakoutConfig) -> tuple[dict, list]:
    inp = load_campaign_029_inputs(store, from_utc=frm, to_utc=to)
    h4 = precompute_h4_trends(inp.h4_frame, inp.decision_times, params, max_staleness_seconds=H4_STALE_S)
    d1 = precompute_d1agg_regimes(inp.d1agg_frame, inp.decision_times, params, max_staleness_seconds=D1_STALE_S)
    trades = run_range_bar_execution(
        range_bars=inp.range_bars, m1_index=inp.m1_index, h4_trends=h4, d1_regimes=d1,
        params=params, fixed_slippage_pips=FIXED_SLIPPAGE_PIPS,
    )
    summary = summarize_trades(trades, label=name)
    summary["window"] = {"from": frm.isoformat(), "to": to.isoformat()}
    summary["range_bars"] = len(inp.decision_times)
    summary["m1_rows"] = inp.m1_rows_consumed
    summary["staleness_bounds_s"] = {"h4": H4_STALE_S, "d1agg": D1_STALE_S}
    return summary, trades


def _write(name: str, obj: dict) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"wrote {path}")
    return path


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    for bad in _REFUSED:
        if bad in argv:
            print(f"REFUSED: {bad} is not permitted — CAMPAIGN_029 keeps the test lockbox "
                  f"closed and paper/demo/live blocked.", file=sys.stderr)
            return 2

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--train-validation", action="store_true", help="run train, then validation if train gate not catastrophic")
    parser.add_argument("--to", default=None, help="override train/validation END (smoke runs); never enters the lockbox")
    parser.add_argument("--save-ledger", action="store_true", help="write gitignored full trade ledgers locally")
    args = parser.parse_args(argv)

    if not args.train_validation:
        print("nothing to do: pass --train-validation", file=sys.stderr)
        return 1

    bootstrap_environ()
    store = PostgresCandleStore(get_research_database_config())
    params = RangeBarMtfBreakoutConfig()  # FROZEN; no tuning

    train_to = datetime.fromisoformat(args.to).replace(tzinfo=UTC) if args.to else TRAIN[1]
    if train_to >= TEST_LOCKBOX[0]:
        print("REFUSED: --to enters the test lockbox window", file=sys.stderr)
        return 2

    train_summary, train_trades = run_window(store, "train", TRAIN[0], min(train_to, TRAIN[1]), params)
    _write("train_summary.json", train_summary)
    if args.save_ledger:
        _save_ledger("train_ledger.csv", train_trades)

    from forex_bot.research.campaign_029_gates import evaluate_train_gates

    tg = evaluate_train_gates(train_summary)
    val_summary = None
    if tg["run_validation"]:
        val_to = datetime.fromisoformat(args.to).replace(tzinfo=UTC) if args.to else VALID[1]
        if val_to >= TEST_LOCKBOX[0]:
            val_to = VALID[1]
        # only run validation if the override window actually covers validation dates
        if (args.to is None) or (datetime.fromisoformat(args.to).replace(tzinfo=UTC) > VALID[0]):
            val_summary, val_trades = run_window(store, "validation", VALID[0], min(val_to, VALID[1]), params)
            _write("validation_summary.json", val_summary)
            if args.save_ledger:
                _save_ledger("validation_ledger.csv", val_trades)
    else:
        print("validation SKIPPED — train gate catastrophic (confirmation, not rescue)")

    decision = classify(train_summary, val_summary, parity_status="NOT_RUN", engine_ok=True)
    decision["approved"] = False
    decision["test_lockbox_opened"] = False
    decision["paper_demo_live"] = "blocked"
    _write("gate_decision.json", decision)
    print(f"CLASSIFICATION: {decision.get('classification')} | train trades={train_summary['trades']} "
          f"exp_r={train_summary.get('expectancy_r')} | "
          f"validation={'run' if val_summary else 'not run'}")
    return 0


def _save_ledger(name: str, trades: list) -> None:
    # gitignored (research/campaign_029/** whitelists only compact JSON/MD)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    if not trades:
        path.write_text("", encoding="utf-8")
        return
    rows = [t.to_row() for t in trades]
    fields = list(rows[0].keys())
    lines = [",".join(fields)]
    for r in rows:
        lines.append(",".join(str(r[f]) for f in fields))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {path} (gitignored)")


if __name__ == "__main__":
    raise SystemExit(main())
