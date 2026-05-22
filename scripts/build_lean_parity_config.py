#!/usr/bin/env python3
"""Build the authoritative Lean-parity config for the CAMPAIGN_002 H4
trend_following baseline.

Reads the committed campaign config and emits the *exact* parameters a
Lean re-implementation must use, so the parity run never depends on
parameters copied from memory or from a stale table. The CAMPAIGN_002
config — not `configs/paper.yaml` — is authoritative: the two differ
(atr_stop_multiple, max_bars_in_trade, min_atr_pips).

This is verification infrastructure. CAMPAIGN_002 is already REJECT and
nothing here approves a strategy. Runnable now: no broker, no DB, no
network, no paid service.

Usage:
    python scripts/build_lean_parity_config.py [--config PATH] [--out PATH]

See docs/research/LEAN_PARITY_EXECUTION_GUIDE.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.config import Settings, load_settings

DEFAULT_CONFIG = ROOT / "configs" / "campaign_002_real_oanda.yaml"
DEFAULT_OUT = ROOT / "research" / "lean_parity" / "lean_parity_config.json"

# CAMPAIGN_002 walk-forward splits. These live in scripts/run_campaign_002.py
# (SPLITS), not in the YAML config, so they are mirrored here. Keep in sync
# with that runner if it ever changes.
CAMPAIGN_002_SPLITS: dict[str, list[str]] = {
    "train": ["2020-01-01", "2022-12-31"],
    "validation": ["2023-01-01", "2024-12-31"],
    "test_untouched": ["2025-01-01", "2026-05-20"],
    "full": ["2020-01-01", "2026-05-20"],
}


def extract_parity_config(settings: Settings, *, source_path: str) -> dict:
    """Pure extraction of the parity parameters from a loaded campaign
    config. Deterministic — no timestamps — so it is unit-testable."""
    tf = settings.strategy.trend_following
    if tf is None:
        raise ValueError("source config has no strategy.trend_following block")
    return {
        "_meta": {
            "description": (
                "Authoritative Lean-parity parameters for the CAMPAIGN_002 "
                "H4 trend_following baseline, extracted from the committed "
                "campaign config — not hand-copied."
            ),
            "generated_by": "scripts/build_lean_parity_config.py",
            "source_config": source_path,
            "source_config_hash": settings.config_hash,
            "parity_target": "CAMPAIGN_002 H4 trend_following baseline",
            "verdict_on_record": "REJECT",
            "is_an_approval": False,
            "note": (
                "Verification infrastructure only. CAMPAIGN_002 is already "
                "REJECT; a parity run validates the engine, it cannot approve "
                "any strategy."
            ),
        },
        "strategy": {"name": "trend_following", **tf.model_dump()},
        "market": {
            "account_currency": settings.market.account_currency,
            "instruments": list(settings.market.instruments),
            "granularity": settings.market.granularity,
            "daily_alignment": settings.market.daily_alignment,
            "alignment_timezone": settings.market.alignment_timezone,
        },
        "cost_model": {
            "fixed_slippage_pips": settings.backtest.fixed_slippage_pips,
            "spread_slippage_multiplier": settings.backtest.spread_slippage_multiplier,
            "commission_per_unit": settings.backtest.commission_per_unit,
            "fill_timing": settings.backtest.fill_timing,
            "fill_rule": (
                "bid/ask-aware: a long enters at the ask, a short at the bid, "
                "plus the slippage above"
            ),
            "note": (
                "CAMPAIGN_002 ran before the fill-timing model existed, so its "
                "behaviour corresponds to fill_timing=signal_bar_close. A "
                "next_bar_open parity would be a separate, later comparison."
            ),
        },
        "sizing": {
            "starting_equity_usd": settings.backtest.starting_equity_usd,
            "risk_per_trade_pct": settings.risk.risk_per_trade_pct,
            "rule": "fixed fractional — risk_per_trade_pct of equity per trade",
        },
        "splits": CAMPAIGN_002_SPLITS,
        "first_parity_target": {
            "instrument": "EUR_USD",
            "split": "full",
            "note": (
                "Start with EUR_USD over the full window; expand to the other "
                "pairs only if single-pair parity passes."
            ),
        },
        "excluded_from_parity": [
            "financing — unmodeled in both engines",
            "RiskEngine spread / session / correlation / margin filters — "
            "bespoke; compare only the bespoke engine's accepted trades",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the Lean-parity config.")
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    config_path = Path(args.config)
    settings = load_settings(config_path)
    try:
        rel = str(config_path.resolve().relative_to(ROOT))
    except ValueError:
        rel = str(config_path)

    config = extract_parity_config(settings, source_path=rel)
    config["_meta"]["generated_at"] = datetime.now(UTC).isoformat(timespec="seconds")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    strat = config["strategy"]
    print(f"wrote Lean-parity config → {out}")
    print(f"  source: {rel} (config_hash {settings.config_hash[:16]}…)")
    print(
        f"  trend_following {strat['version']}: ema {strat['ema_fast']}/"
        f"{strat['ema_slow']}, donchian {strat['donchian_lookback']}, "
        f"atr_stop ×{strat['atr_stop_multiple']}, "
        f"trail ×{strat['trailing_stop_atr_multiple']}, "
        f"max_bars {strat['max_bars_in_trade']}"
    )
    print(f"  instruments: {', '.join(config['market']['instruments'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
