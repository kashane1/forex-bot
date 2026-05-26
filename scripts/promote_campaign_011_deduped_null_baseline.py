#!/usr/bin/env python3
"""Promote the deduped CAMPAIGN_011 walk-forward run to canonical null rollup.

Reads compact walk-forward artifacts from
``backtests/CAMPAIGN_011_random_entry_anchor_deduped/`` and writes:

  * research/null_baselines/campaign_011_deduped_null_baseline.json
  * research/null_baselines/campaign_011_deduped_null_baseline.md
  * docs/research/CAMPAIGN_011_DEDUPED_NULL_BASELINE.md

Does not copy per-fold trade CSVs. Does not call OANDA. Optional
``--probe-dedupe`` reads local SQLite only to populate duplicate-row
counts at the CandleRepo load boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from research.null_baselines.campaign_011_deduped import (
    CANONICAL_CAMPAIGN_011_DEDUPED_JSON,
    CANONICAL_CAMPAIGN_011_DEDUPED_MD,
)

from forex_bot.data.candle_dedupe import DEDUPE_POLICY
from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo, DataSourceRepo, InstrumentRepo

DEFAULT_INPUT = ROOT / "backtests" / "CAMPAIGN_011_random_entry_anchor_deduped"
DOC_OUT = ROOT / "docs" / "research" / "CAMPAIGN_011_DEDUPED_NULL_BASELINE.md"

EXPECTED_PAIRS = (
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
)
SUPERSEDED = {
    "artifact_folder": "backtests/CAMPAIGN_011_random_entry_anchor",
    "integrity_status": "LIKELY_CONTAMINATED",
    "aggregate_expectancy_r": -0.0024,
    "total_trades": 1177,
    "aggregate_return_pct": -0.53,
    "aggregate_profit_factor": 0.91,
    "note": (
        "Pre-fix bespoke SQLite loads before CandleRepo.list dedupe "
        "(commit 30b4654). Verdict REJECT unchanged; headline metrics "
        "must not be used for null-band comparisons."
    ),
}


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _fold_windows(folds: list[dict[str, Any]]) -> list[dict[str, str | int]]:
    return [
        {
            "fold_index": int(f["fold_index"]),
            "test_start": str(f["test_start"]),
            "test_end": str(f["test_end"]),
        }
        for f in folds
    ]


def _per_fold_rows(folds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "fold_index": int(f["fold_index"]),
            "test_start": str(f["test_start"]),
            "test_end": str(f["test_end"]),
            "trade_count": int(f["trade_count"]),
            "expectancy_r": float(f["expectancy_r"]),
            "return_pct": float(f["aggregate_return_pct"]),
            "profit_factor": f.get("profit_factor"),
            "passes_gates": bool(f.get("passes")),
        }
        for f in folds
    ]


def _per_pair_rows(agg: dict[str, Any]) -> list[dict[str, Any]]:
    counts = agg.get("pair_trade_counts") or {}
    exp = agg.get("pair_expectancy_r") or {}
    ret = agg.get("pair_returns_pct") or {}
    rows: list[dict[str, Any]] = []
    for instrument in EXPECTED_PAIRS:
        rows.append(
            {
                "instrument": instrument,
                "trade_count": int(counts.get(instrument, 0)),
                "expectancy_r": float(exp.get(instrument, 0.0)),
                "return_pct": float(ret.get(instrument, 0.0)),
            }
        )
    return rows


def _probe_dedupe_across_folds(
    fold_detail: dict[str, Any],
    *,
    settings_path: Path,
) -> dict[str, Any] | None:
    """Sum CandleRepo.list dedupe stats across all fold windows (local DB)."""
    from forex_bot.config import load_settings

    settings = load_settings(settings_path)
    db_path = Path(settings.app.database_path)
    if not db_path.is_file():
        return {
            "status": "BLOCKED",
            "reason": f"SQLite store missing: {db_path}",
        }

    db = Database(db_path)
    candle_repo = CandleRepo(db)
    instr_repo = InstrumentRepo(db)
    ds_repo = DataSourceRepo(db)

    total_raw = 0
    total_deduped = 0
    total_dropped = 0
    per_pair: dict[str, dict[str, int]] = {}

    for fold in fold_detail["folds"]:
        for instrument in EXPECTED_PAIRS:
            if instr_repo.get(instrument) is None:
                continue
            src = (ds_repo.latest_for(instrument, "H4") or {}).get("source")
            if src != fold_detail.get("data_source"):
                continue
            frm = datetime.fromisoformat(fold["test_start"]).replace(tzinfo=UTC)
            to = datetime.fromisoformat(fold["test_end"]).replace(tzinfo=UTC)
            candle_repo.list(
                instrument,
                "H4",
                completed_only=True,
                from_time=frm,
                to_time=to,
            )
            stats = candle_repo.last_list_dedupe_stats
            if stats is None:
                continue
            total_raw += stats.raw_count
            total_deduped += stats.deduped_count
            total_dropped += stats.duplicates_dropped
            bucket = per_pair.setdefault(
                instrument,
                {"raw_count": 0, "deduped_count": 0, "duplicates_dropped": 0},
            )
            bucket["raw_count"] += stats.raw_count
            bucket["deduped_count"] += stats.deduped_count
            bucket["duplicates_dropped"] += stats.duplicates_dropped

    return {
        "status": "OK",
        "dedupe_policy": DEDUPE_POLICY,
        "duplicates_detected": total_dropped,
        "duplicates_dropped": total_dropped,
        "raw_count_total": total_raw,
        "deduped_count_total": total_deduped,
        "per_pair": per_pair,
    }


def build_rollup(
    *,
    input_dir: Path,
    probe_dedupe: bool,
) -> dict[str, Any]:
    wf = input_dir / "walk_forward"
    fold_detail_path = wf / "fold_detail.json"
    results_path = wf / "results.json"
    if not fold_detail_path.is_file():
        raise SystemExit(f"missing fold_detail.json: {fold_detail_path}")

    fold_detail = json.loads(fold_detail_path.read_text(encoding="utf-8"))
    folds = fold_detail["folds"]
    agg = fold_detail["aggregate"]
    per_fold_exp = [float(f["expectancy_r"]) for f in folds]

    results: dict[str, Any] | None = None
    if results_path.is_file():
        results = json.loads(results_path.read_text(encoding="utf-8"))

    config_path = Path(fold_detail.get("config_path", "configs/campaign_011_random_entry_anchor.yaml"))
    dedupe_probe: dict[str, Any] | None = None
    if probe_dedupe:
        dedupe_probe = _probe_dedupe_across_folds(
            fold_detail,
            settings_path=ROOT / config_path,
        )

    seed_derivation = (
        "Frozen master_seed on strategy config; per-bar entry uses "
        "SHA-256(master_seed, instrument, bar_index) — see "
        "CAMPAIGN_011_PRECOMMIT_CHECKLIST.md §5–§6."
    )

    payload: dict[str, Any] = {
        "schema_version": 1,
        "campaign_id": fold_detail.get("campaign_id", "CAMPAIGN_011"),
        "strategy_name": fold_detail.get("strategy_name", "random_entry_anchor"),
        "strategy_version": fold_detail.get("strategy_version", "0.1.0-c011"),
        "null_model": True,
        "canonical": True,
        "approval_path": "none (null model by design)",
        "overall_verdict": agg.get("overall_verdict", "REJECT"),
        "master_seed": int(fold_detail.get("master_seed", 20260523)),
        "seed_derivation": seed_derivation,
        "data_dedupe_policy": DEDUPE_POLICY,
        "data_source": fold_detail.get("data_source", "oanda-practice"),
        "config_path": str(config_path),
        "config_hash": fold_detail.get("config_hash"),
        "fold_windows": _fold_windows(folds),
        "per_fold": _per_fold_rows(folds),
        "per_pair": _per_pair_rows(agg),
        "aggregate": {
            "fold_count": int(agg.get("fold_count", len(folds))),
            "folds_passing": int(agg.get("folds_passing", 0)),
            "fold_pass_rate": float(agg.get("fold_pass_rate", 0.0)),
            "total_trades": int(agg.get("total_trades", 0)),
            "aggregate_expectancy_r": float(agg.get("aggregate_expectancy_r", 0.0)),
            "aggregate_return_pct": float(agg.get("aggregate_return_pct", 0.0)),
            "profit_factor": agg.get("profit_factor"),
            "pairs_positive_count": int(agg.get("pairs_positive_count", 0)),
            "single_fold_dominance_pct": agg.get("single_fold_dominance_pct"),
            "single_pair_dominance_pct": agg.get("single_pair_dominance_pct"),
        },
        "null_distribution": {
            "per_fold_expectancy_r": per_fold_exp,
            "per_fold_expectancy_r_mean": (
                statistics.mean(per_fold_exp) if per_fold_exp else None
            ),
            "per_fold_expectancy_r_std": (
                statistics.stdev(per_fold_exp) if len(per_fold_exp) >= 2 else None
            ),
        },
        "cost_stress": {
            "note": (
                "Financing overlay not re-run in deduped promotion sprint; "
                "pre-fix CAMPAIGN_011 financing doc remains informational. "
                "Re-run build_campaign_011_financing_overlay.py against "
                "deduped fold trade CSVs locally if stress numbers are needed."
            ),
            "available": False,
        },
        "dedupe_probe": dedupe_probe,
        "supersedes": SUPERSEDED,
        "provenance": {
            "input_dir": str(input_dir.relative_to(ROOT)),
            "fold_detail_sha256": _sha256_file(fold_detail_path),
            "results_sha256": (
                _sha256_file(results_path) if results_path.is_file() else None
            ),
            "generated_at": datetime.now(UTC).isoformat(),
            "dedupe_fix_commit": "30b4654",
        },
        "excluded_local_only": [
            f"{input_dir.name}/folds/**/**_trades.csv",
            f"{input_dir.name}/folds/**/**_summary.json (optional; fold_detail is canonical)",
        ],
        "walk_forward_results": results,
    }
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    agg = payload["aggregate"]
    null_dist = payload["null_distribution"]
    lines = [
        "# CAMPAIGN_011 — Deduped Canonical Null Baseline (rollup)",
        "",
        "> **Canonical** for post-dedupe null comparisons. Supersedes",
        "> pre-fix `backtests/CAMPAIGN_011_random_entry_anchor/` metrics.",
        "> **Not a tradable strategy.** `approved: []`. Paper/demo/live blocked.",
        "",
        "| field | value |",
        "|---|---|",
        f"| strategy | `{payload['strategy_name']}` `{payload['strategy_version']}` |",
        f"| master_seed | `{payload['master_seed']}` |",
        f"| data_source | `{payload['data_source']}` |",
        f"| dedupe_policy | `{payload['data_dedupe_policy']}` |",
        f"| config_hash | `{payload['config_hash']}` |",
        f"| total_trades | **{agg['total_trades']}** |",
        f"| aggregate expectancy R | **{agg['aggregate_expectancy_r']:.4f}** |",
        f"| aggregate return % | **{agg['aggregate_return_pct']:.4f}** |",
        f"| profit_factor | **{agg.get('profit_factor')}** |",
        f"| pairs_positive | **{agg['pairs_positive_count']} / 7** |",
        f"| fold pass rate | **{agg['folds_passing']} / {agg['fold_count']}** |",
        f"| per-fold exp R mean | **{null_dist['per_fold_expectancy_r_mean']}** |",
        f"| per-fold exp R std | **{null_dist['per_fold_expectancy_r_std']}** |",
        "",
        "## Superseded (pre-fix contaminated null)",
        "",
        "| metric | contaminated | deduped canonical |",
        "|---|---:|---:|",
        f"| total_trades | {SUPERSEDED['total_trades']} | {agg['total_trades']} |",
        f"| aggregate expectancy R | {SUPERSEDED['aggregate_expectancy_r']} | "
        f"{agg['aggregate_expectancy_r']:.4f} |",
        "",
        "## Per-fold",
        "",
        "| fold | trades | exp R | return % |",
        "|---:|---:|---:|---:|",
    ]
    for row in payload["per_fold"]:
        lines.append(
            f"| {row['fold_index']} | {row['trade_count']} | "
            f"{row['expectancy_r']:.4f} | {row['return_pct']:.4f} |"
        )
    lines.extend(["", "## Per-pair", "", "| pair | trades | exp R | return % |", "|---|---:|---:|---:|"])
    for row in payload["per_pair"]:
        lines.append(
            f"| {row['instrument']} | {row['trade_count']} | "
            f"{row['expectancy_r']:.4f} | {row['return_pct']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Local-only (not committed)",
            "",
        ]
    )
    for item in payload["excluded_local_only"]:
        lines.append(f"- `{item}`")
    return "\n".join(lines) + "\n"


def render_doc(payload: dict[str, Any]) -> str:
    """Human-facing doc mirroring the rollup with binding comparison note."""
    md = render_markdown(payload)
    header = (
        "# CAMPAIGN_011 — Deduped Null Baseline\n\n"
        "**Sprint:** CAMPAIGN_011_DEDUPED_NULL_BASELINE_001  \n"
        "**Canonical JSON:** [`research/null_baselines/campaign_011_deduped_null_baseline.json`]"
        "(../../research/null_baselines/campaign_011_deduped_null_baseline.json)  \n"
        "**Status:** NULL MODEL — REJECT expected; metrics are the falsifiability floor "
        "for CAMPAIGN_012–014 re-evaluation.\n\n"
        "> Old walk-forward doc "
        "[`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md) "
        "is **SUPERSEDED** for numeric null-band use.\n\n"
    )
    return header + md


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Deduped CAMPAIGN_011 output directory",
    )
    ap.add_argument(
        "--probe-dedupe",
        action="store_true",
        help="Probe local SQLite for duplicate rows dropped at load (no OANDA)",
    )
    ap.add_argument("--json-out", type=Path, default=CANONICAL_CAMPAIGN_011_DEDUPED_JSON)
    ap.add_argument("--md-out", type=Path, default=CANONICAL_CAMPAIGN_011_DEDUPED_MD)
    ap.add_argument("--doc-out", type=Path, default=DOC_OUT)
    args = ap.parse_args()

    payload = build_rollup(input_dir=args.input, probe_dedupe=args.probe_dedupe)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    args.doc_out.write_text(render_doc(payload), encoding="utf-8")
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    print(f"wrote {args.doc_out}")


if __name__ == "__main__":
    main()
