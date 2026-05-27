#!/usr/bin/env python3
"""Generate C008/C009/C018 financing exposure diagnostics (one-off).

Reads local gitignored trade CSVs; writes committed aggregate JSON only.
Diagnostic only — strategy_evidence: false.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from research.financing.overlay import (  # noqa: E402
    apply_financing_overlay,
    load_trades_from_glob,
)

CAMPAIGNS = {
    "C008": {
        "train": "backtests/CAMPAIGN_008_mean_reversion_deduped_forensic/baseline/train/*_train_trades.csv",
        "validation": "backtests/CAMPAIGN_008_mean_reversion_deduped_forensic/baseline/validation/*_validation_trades.csv",
    },
    "C009": {
        "train": "backtests/CAMPAIGN_009_mean_reversion_midline_deduped_forensic/train/base/*_train_trades.csv",
        "validation": "backtests/CAMPAIGN_009_mean_reversion_midline_deduped_forensic/validation/base/*_validation_trades.csv",
    },
    "C018": {
        "train": "backtests/CAMPAIGN_018_mean_reversion_protective_stop/train/base/*_train_base_trades.csv",
        "validation": "backtests/CAMPAIGN_018_mean_reversion_protective_stop/validation/base/*_validation_base_trades.csv",
    },
}


def _strip_per_trade(result: dict) -> dict:
    """Keep aggregate diagnostics only — omit bulky per-trade rows."""
    out = dict(result)
    out.pop("per_trade", None)
    return out


def main() -> None:
    output: dict = {
        "strategy_evidence": False,
        "not_approved": True,
        "diagnostic_label": "SYNTHETIC_FINANCING_DIAGNOSTIC",
        "observed_financing_used": False,
        "rate_source": "conservative_stress (default_stress_rate_source)",
        "campaigns": {},
    }

    for cid, splits in CAMPAIGNS.items():
        output["campaigns"][cid] = {}
        for split, pattern in splits.items():
            trades = load_trades_from_glob(str(ROOT / pattern))
            if not trades:
                print(f"WARN: no trades for {cid} {split} — skip (run forensic replay locally)")
                output["campaigns"][cid][split] = {"trade_count": 0, "skipped": True}
                continue
            result = apply_financing_overlay(trades)
            output["campaigns"][cid][split] = _strip_per_trade(result)
            agg = result["aggregate"]
            print(
                f"{cid} {split}: n={result['trade_count']} "
                f"gross={agg['gross_expectancy_r']:.4f}R "
                f"net={agg['net_expectancy_r']:.4f}R "
                f"drag={agg['financing_drag_r']:.4f}R"
            )

    out_path = ROOT / "research/financing/c008_c009_c018_financing_exposure.json"
    out_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
