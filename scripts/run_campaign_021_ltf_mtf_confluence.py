#!/usr/bin/env python3
"""CAMPAIGN_021 — LTF MTF confluence entry scaffold runner (preflight only)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.config import Settings, compute_config_hash
from forex_bot.data.m1_corpus_validation import MAJOR_PAIRS, inventory_sql
from forex_bot.data.m1_timeframe_materialization import MATERIALIZED_SOURCE
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import get_research_database_config
from forex_bot.project_env import bootstrap_environ
from forex_bot.research.campaign_021_loader import (
    build_data_feature_preflight,
    check_materialized_coverage,
)
from forex_bot.research.execution_realism import FillTiming, parse_research_metadata
from forex_bot.strategies.lower_timeframe_mtf_confluence_entry import (
    D1AGG_SOURCE_M1,
    D1AGG_SOURCE_NATIVE,
    LowerTimeframeMtfConfluenceEntryStrategy,
    validate_c021_data_provenance,
)

CONFIG_PATH = ROOT / "configs/campaign_021_ltf_mtf_confluence.yaml"
OUT_RESEARCH = ROOT / "research/campaign_021"
EXPECTED_STRATEGY = "lower_timeframe_mtf_confluence_entry"
EVIDENCE_BLOCKED = (
    "BLOCKED: train/validation/test evidence requires "
    "research-campaign-021-ltf-mtf-confluence-execution-001"
)
SPLITS: dict[str, tuple[str, str]] = {
    "train": ("2020-01-01", "2022-12-31"),
    "validation": ("2023-01-01", "2024-12-31"),
    "test": ("2025-01-01", "2026-05-20"),
}


def _load_raw() -> dict[str, Any]:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}


def _strip_for_settings(raw: dict[str, Any]) -> dict[str, Any]:
    data = dict(raw)
    for key in ("campaign", "research_metadata", "financing", "data_provenance"):
        data.pop(key, None)
    text = CONFIG_PATH.read_text(encoding="utf-8")
    data.setdefault("config_hash", compute_config_hash(text))
    data.setdefault("config_source_path", str(CONFIG_PATH))
    return data


def load_settings() -> tuple[Settings, dict[str, Any]]:
    raw = _load_raw()
    return Settings.model_validate(_strip_for_settings(raw)), raw


def validate_frozen_config(settings: Settings, raw: dict[str, Any]) -> dict[str, Any]:
    if settings.strategy.enabled != [EXPECTED_STRATEGY]:
        raise SystemExit(f"config must enable only {EXPECTED_STRATEGY}")
    cfg = settings.strategy.lower_timeframe_mtf_confluence_entry
    if cfg is None:
        raise SystemExit("missing lower_timeframe_mtf_confluence_entry config")
    if cfg.version != "0.1.0-c021":
        raise SystemExit("version must be 0.1.0-c021")
    if cfg.timeframe != "M15":
        raise SystemExit("execution timeframe must be M15")
    if cfg.max_bars_in_trade != 32 or cfg.atr_stop_multiple != 2.0:
        raise SystemExit("precommitted risk parameters diverged")
    provenance = raw.get("data_provenance") or {}
    validate_c021_data_provenance(provenance)
    if provenance.get("m1_derived_d1agg_allowed"):
        raise SystemExit("m1_derived_d1agg_allowed must be false")
    return cfg.model_dump()


def preflight(settings: Settings, raw: dict[str, Any]) -> dict[str, Any]:
    meta = parse_research_metadata(raw.get("research_metadata"))
    provenance = raw.get("data_provenance") or {}
    strategy = LowerTimeframeMtfConfluenceEntryStrategy()
    blocked: list[str] = []
    result: dict[str, Any] = {
        "campaign_id": "CAMPAIGN_021",
        "strategy_name": EXPECTED_STRATEGY,
        "version": "0.1.0-c021",
        "status": "SCAFFOLD_ONLY",
        "not_approved": True,
        "strategy_evidence": False,
        "test_lockbox_opened": False,
        "fill_timing": meta.fill_timing.value if meta and meta.fill_timing else None,
        "data_provenance": provenance,
        "warmup_bars_required": strategy.warmup_bars_required(),
        "pairs": list(settings.market.instruments),
        "checked_at_utc": datetime.now(UTC).isoformat(),
        "blocked_reasons": blocked,
    }
    try:
        validate_c021_data_provenance(provenance)
    except ValueError as exc:
        blocked.append(str(exc))
    if provenance.get("d1agg_context") == D1AGG_SOURCE_M1:
        blocked.append("m1_derived_d1agg forbidden for CAMPAIGN_021")
    if provenance.get("d1agg_context") != D1AGG_SOURCE_NATIVE:
        blocked.append("d1agg_context must be native_h4_derived_d1agg")
    if meta is None or meta.fill_timing != FillTiming.NEXT_BAR_OPEN:
        blocked.append("fill_timing must be next_bar_open")
    if settings.app.trading_enabled or settings.app.allow_order_submission:
        blocked.append("order submission must stay disabled")
    try:
        environ = bootstrap_environ(None)
        cfg = get_research_database_config(environ=environ, require=True)
        store = PostgresCandleStore(cfg)
        inv = inventory_sql(store)
        result["m1_corpus"] = {
            "overall_status": inv["overall_status"],
            "pair_count": len(inv["pairs"]),
            "expected_pairs": list(MAJOR_PAIRS),
        }
        if inv.get("missing_pairs"):
            blocked.append(f"missing M1 pairs: {inv['missing_pairs']}")
        with store.connection() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT COUNT(*) FROM {cfg.schema}.candles
                WHERE granularity = 'H4'
                """
            )
            h4_total = int(cur.fetchone()[0])
            cur.execute(
                f"""
                SELECT COUNT(DISTINCT instrument) FROM {cfg.schema}.candles
                WHERE granularity = 'D1AGG'
                """
            )
            d1agg_pairs = int(cur.fetchone()[0])
        result["native_h4_rows"] = h4_total
        result["d1agg_pairs_in_store"] = d1agg_pairs
        if h4_total < 1000:
            blocked.append("insufficient native H4 rows for D1AGG derivation")
        materialized: dict[str, Any] = {"source": MATERIALIZED_SOURCE, "pairs": {}}
        train_from, train_to = SPLITS["train"]
        from_dt = datetime.fromisoformat(train_from).replace(tzinfo=UTC)
        to_dt = datetime.fromisoformat(train_to).replace(hour=23, minute=59, tzinfo=UTC)
        missing_materialized: list[str] = []
        for pair in settings.market.instruments:
            cov = check_materialized_coverage(
                store, pair, from_dt=from_dt, to_dt=to_dt
            )
            materialized["pairs"][pair] = cov
            if cov["status"] != "PASS":
                missing_materialized.append(pair)
        result["materialized_coverage"] = materialized
        if missing_materialized:
            blocked.append(
                "missing materialized M5/M15/H1/H4 for: "
                + ", ".join(missing_materialized)
                + " — run scripts/materialize_m1_derived_timeframes.py --all-majors"
            )
    except Exception as exc:
        blocked.append(f"postgres preflight: {exc}")
    result["blocked_reasons"] = blocked
    result["preflight_ok"] = not blocked
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="CAMPAIGN_021 scaffold runner")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--data-feature-preflight", action="store_true")
    parser.add_argument("--validate-config", action="store_true")
    parser.add_argument("--emit-plan", action="store_true")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["train-validation", "test", "full"],
        help="Blocked in scaffold sprint",
    )
    args = parser.parse_args()
    settings, raw = load_settings()

    if args.command:
        print(EVIDENCE_BLOCKED, file=sys.stderr)
        return 2

    if args.preflight_only:
        pf = preflight(settings, raw)
        OUT_RESEARCH.mkdir(parents=True, exist_ok=True)
        (OUT_RESEARCH / "preflight_result.json").write_text(
            json.dumps(pf, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(pf, indent=2, sort_keys=True))
        return 0 if pf["preflight_ok"] else 1

    if args.data_feature_preflight:
        environ = bootstrap_environ(None)
        cfg = get_research_database_config(environ=environ, require=True)
        store = PostgresCandleStore(cfg)
        report = build_data_feature_preflight(
            store,
            splits=SPLITS,
            pairs=list(settings.market.instruments),
        )
        OUT_RESEARCH.mkdir(parents=True, exist_ok=True)
        (OUT_RESEARCH / "data_feature_preflight.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["preflight_ok"] else 1

    if args.validate_config or args.emit_plan:
        validate_frozen_config(settings, raw)
        print(f"[CAMPAIGN_021] config OK — {EXPECTED_STRATEGY} 0.1.0-c021")
        if args.emit_plan:
            OUT_RESEARCH.mkdir(parents=True, exist_ok=True)
            (OUT_RESEARCH / "execution_plan.json").write_text(
                json.dumps(
                    {
                        "campaign_id": "CAMPAIGN_021",
                        "status": "SCAFFOLD_ONLY",
                        "fill_timing": "next_bar_open",
                        "execution_timeframe": "M15",
                        "data_provenance": raw.get("data_provenance"),
                        "evidence_blocked_in_scaffold": True,
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
