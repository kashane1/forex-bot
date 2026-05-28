#!/usr/bin/env python3
"""Apply local-first financing overlay to prior campaign trade ledgers.

Infrastructure only. No broker. No strategy approval. No campaign reruns.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from glob import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.research.financing_overlay import (
    FinancingOverlayMode,
    TradeLedgerRef,
    inventory_trade_csv,
    overlay_ledger,
)

OUT_DIR = ROOT / "research/financing_overlay_local_first"
LOCAL_ADJUSTED = OUT_DIR / "local_adjusted_trades"

# Selected reference ledgers (compact committed trade CSVs only).
LEDGER_SPECS: list[dict] = [
    {
        "campaign_id": "CAMPAIGN_019",
        "ledger_label": "c019_train_validation_base",
        "strategy": "mean_reversion_thesis_invalidation",
        "version": "0.1.0-c019",
        "timeframe": "H4",
        "globs": [
            "backtests/CAMPAIGN_019_mean_reversion_thesis_invalidation/train/base/*_trades.csv",
            "backtests/CAMPAIGN_019_mean_reversion_thesis_invalidation/validation/base/*_trades.csv",
        ],
    },
    {
        "campaign_id": "CAMPAIGN_016",
        "ledger_label": "c016_weekly_momentum_folds_base",
        "strategy": "weekly_cross_sectional_momentum_low_turnover",
        "version": "0.1.0-c016",
        "timeframe": "H4",
        "globs": [
            "backtests/CAMPAIGN_016_weekly_cross_sectional_momentum/folds/base/fold_*/*_trades.csv",
        ],
    },
    {
        "campaign_id": "CAMPAIGN_017",
        "ledger_label": "c017_weekly_vol_breakout_folds_base",
        "strategy": "weekly_volatility_contraction_breakout",
        "version": "0.1.0-c017",
        "timeframe": "H4",
        "globs": [
            "backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout/folds/base/fold_*/*_trades.csv",
        ],
    },
    {
        "campaign_id": "CAMPAIGN_008",
        "ledger_label": "c008_deduped_forensic_train",
        "strategy": "mean_reversion",
        "version": "0.1.0-c008",
        "timeframe": "H4",
        "globs": [
            "backtests/CAMPAIGN_008_mean_reversion_deduped_forensic/baseline/train/baseline_*_H4_train_trades.csv",
        ],
    },
]

INVENTORY_GLOBS = [
    "backtests/CAMPAIGN_019_mean_reversion_thesis_invalidation/**/base/*_trades.csv",
    "backtests/CAMPAIGN_018_mean_reversion_protective_stop/**/base/*_trades.csv",
    "backtests/CAMPAIGN_016_weekly_cross_sectional_momentum/folds/base/**/*_trades.csv",
    "backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout/folds/base/**/*_trades.csv",
    "backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/folds/base/**/*_trades.csv",
    "backtests/CAMPAIGN_008_mean_reversion_deduped_forensic/baseline/train/baseline_*_H4_train_trades.csv",
]


def _git(*args: str) -> str:
    try:
        r = subprocess.run(
            ["git", "-C", str(ROOT), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return ""
    return r.stdout.strip()


def _expand_glob(pattern: str) -> list[str]:
    paths = sorted(glob(str(ROOT / pattern), recursive="**" in pattern))
    return [str(Path(p).relative_to(ROOT)) for p in paths if Path(p).is_file()]


def build_ledgers() -> list[TradeLedgerRef]:
    out: list[TradeLedgerRef] = []
    for spec in LEDGER_SPECS:
        paths: list[str] = []
        for pattern in spec["globs"]:
            paths.extend(_expand_glob(pattern))
        paths = sorted(set(paths))
        if not paths:
            raise SystemExit(f"no trades for {spec['campaign_id']} globs={spec['globs']}")
        out.append(
            TradeLedgerRef(
                campaign_id=spec["campaign_id"],
                ledger_label=spec["ledger_label"],
                trade_paths=tuple(paths),
                strategy=spec["strategy"],
                version=spec["version"],
                timeframe=spec["timeframe"],
            )
        )
    return out


def build_inventory() -> dict:
    rows: list[dict] = []
    for pattern in INVENTORY_GLOBS:
        for rel in _expand_glob(pattern):
            info = inventory_trade_csv(ROOT / rel)
            if info:
                info["campaign_guess"] = rel.split("/")[1] if "/" in rel else rel
                rows.append(info)
    selected = [s["ledger_label"] for s in LEDGER_SPECS]
    return {
        "strategy_evidence": False,
        "not_approved": True,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "entries": rows,
        "selected_ledger_labels": selected,
    }


def _summary_to_dict(s) -> dict:
    return {
        "campaign_id": s.campaign_id,
        "ledger_label": s.ledger_label,
        "financing_mode": s.financing_mode,
        "rate_source": s.rate_source,
        "synthetic": s.synthetic,
        "trade_count": s.trade_count,
        "gross_expectancy_r": s.gross_expectancy_r,
        "adjusted_expectancy_r": s.adjusted_expectancy_r,
        "financing_drag_r": s.financing_drag_r,
        "avg_hold_days": round(s.avg_hold_days, 3),
        "max_hold_days": round(s.max_hold_days, 3),
        "unavailable_rate_trades": s.unavailable_rate_trades,
        "warnings": s.warnings,
        "by_pair": s.by_pair,
        "by_hold_bucket": s.by_hold_bucket,
    }


def run_overlay(modes: list[FinancingOverlayMode]) -> dict:
    ledgers = build_ledgers()
    by_campaign: dict[str, list[dict]] = {}
    pair_rows: list[dict] = []
    bucket_rows: list[dict] = []
    deltas: dict[str, dict] = {}
    unavailable: list[dict] = []

    for ledger in ledgers:
        mode_results: dict[str, dict] = {}
        for mode in modes:
            summary = overlay_ledger(ledger, mode)
            rec = _summary_to_dict(summary)
            mode_results[mode.value] = rec
            by_campaign.setdefault(ledger.campaign_id, []).append(rec)
            for pair, stats in summary.by_pair.items():
                pair_rows.append(
                    {
                        "campaign_id": ledger.campaign_id,
                        "ledger_label": ledger.ledger_label,
                        "financing_mode": mode.value,
                        "instrument": pair,
                        **stats,
                    }
                )
            for bucket, stats in summary.by_hold_bucket.items():
                bucket_rows.append(
                    {
                        "campaign_id": ledger.campaign_id,
                        "ledger_label": ledger.ledger_label,
                        "financing_mode": mode.value,
                        "hold_bucket": bucket,
                        **stats,
                    }
                )
            if summary.unavailable_rate_trades:
                unavailable.append(
                    {
                        "campaign_id": ledger.campaign_id,
                        "ledger_label": ledger.ledger_label,
                        "financing_mode": mode.value,
                        "unavailable_rate_trades": summary.unavailable_rate_trades,
                    }
                )
        if (
            FinancingOverlayMode.SYNTHETIC_FIXTURE.value in mode_results
            and FinancingOverlayMode.NONE.value in mode_results
        ):
            syn = mode_results[FinancingOverlayMode.SYNTHETIC_FIXTURE.value]
            none = mode_results[FinancingOverlayMode.NONE.value]
            deltas[ledger.ledger_label] = {
                "gross_expectancy_r": none["gross_expectancy_r"],
                "adjusted_expectancy_r": syn["adjusted_expectancy_r"],
                "financing_drag_r": syn["financing_drag_r"],
                "adjusted_minus_gross_r": (
                    (syn["adjusted_expectancy_r"] or 0) - (none["gross_expectancy_r"] or 0)
                    if syn["adjusted_expectancy_r"] is not None
                    and none["gross_expectancy_r"] is not None
                    else None
                ),
            }

    return {
        "manifest": {
            "strategy_evidence": False,
            "not_approved": True,
            "test_lockbox_opened": False,
            "campaign_020_created": False,
            "modes": [m.value for m in modes],
            "git_commit": _git("rev-parse", "HEAD"),
            "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
            "generated_at_utc": datetime.now(UTC).isoformat(),
        },
        "ledger_inventory_used": [s["ledger_label"] for s in LEDGER_SPECS],
        "by_campaign": by_campaign,
        "pair_rows": pair_rows,
        "bucket_rows": bucket_rows,
        "deltas": deltas,
        "unavailable": unavailable,
    }


def write_outputs(payload: dict, out_dir: Path = OUT_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "run_manifest.json").write_text(
        json.dumps(payload["manifest"], indent=2) + "\n",
        encoding="utf-8",
    )
    inv = build_inventory()
    (out_dir / "ledger_inventory_used.json").write_text(
        json.dumps(inv, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "overlay_summary_by_campaign.json").write_text(
        json.dumps(payload["by_campaign"], indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "adjusted_metric_delta.json").write_text(
        json.dumps(payload["deltas"], indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "unavailable_rates_report.json").write_text(
        json.dumps(payload["unavailable"], indent=2) + "\n",
        encoding="utf-8",
    )

    import csv

    pair_path = out_dir / "overlay_summary_by_pair.csv"
    if payload["pair_rows"]:
        fields = list(payload["pair_rows"][0].keys())
        with pair_path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(payload["pair_rows"])

    bucket_path = out_dir / "overlay_summary_by_hold_bucket.csv"
    if payload["bucket_rows"]:
        fields = list(payload["bucket_rows"][0].keys())
        with bucket_path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(payload["bucket_rows"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Financing overlay on trade ledgers")
    parser.add_argument(
        "--modes",
        default="none,synthetic_fixture,manual_observed_fixture",
        help="Comma-separated FinancingOverlayMode values",
    )
    parser.add_argument(
        "--inventory-only",
        action="store_true",
        help="Write ledger inventory JSON only",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory (defaults to research/financing_overlay_local_first). "
        "Use a temp dir to avoid touching committed artifacts.",
    )
    args = parser.parse_args()
    out_dir = Path(args.out_dir) if args.out_dir else OUT_DIR

    if args.inventory_only:
        out_dir.mkdir(parents=True, exist_ok=True)
        inv = build_inventory()
        (out_dir / "ledger_inventory_used.json").write_text(
            json.dumps(inv, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {out_dir / 'ledger_inventory_used.json'}")
        return

    modes = [FinancingOverlayMode(m.strip()) for m in args.modes.split(",")]
    payload = run_overlay(modes)
    write_outputs(payload, out_dir)
    print(f"Wrote compact artifacts to {out_dir}")


if __name__ == "__main__":
    main()
