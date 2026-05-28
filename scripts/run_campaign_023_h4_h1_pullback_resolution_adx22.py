#!/usr/bin/env python3
"""CAMPAIGN_023 — H4/H1 pullback resolution entry, ADX22 sibling (preflight only).

Defaults to preflight-only. Train/validation/test/approval are BLOCKED in this
scaffold sprint; any execution subcommand exits non-zero without running evidence.

CAMPAIGN_023 is identical to CAMPAIGN_022 except the H4 directional-bias strength
gate (h4_adx_min 22.0 vs 20.0). See
docs/research/CAMPAIGN_023_H4_H1_PULLBACK_RESOLUTION_ADX22_PRECOMMIT.md.
"""

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
from forex_bot.research.execution_realism import FillTiming, parse_research_metadata
from forex_bot.strategies.h4_h1_pullback_resolution_entry import (
    H4H1PullbackResolutionEntryStrategy,
    validate_c022_data_provenance,
)

CONFIG_PATH = ROOT / "configs/campaign_023_h4_h1_pullback_resolution_adx22.yaml"
OUT_RESEARCH = ROOT / "research/campaign_023"
EXPECTED_STRATEGY = "h4_h1_pullback_resolution_entry"
EXPECTED_VERSION = "0.1.0-c023"
CAMPAIGN_ID = "CAMPAIGN_023"
EXPECTED_H4_ADX_MIN = 22.0
EVIDENCE_BLOCKED = (
    "BLOCKED: CAMPAIGN_023 train/validation/test evidence requires a separate "
    "execution sprint. This scaffold runner is preflight-only."
)


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
    cfg = settings.strategy.h4_h1_pullback_resolution_entry
    if cfg is None:
        raise SystemExit("missing h4_h1_pullback_resolution_entry config")
    if cfg.version != EXPECTED_VERSION:
        raise SystemExit(f"version must be {EXPECTED_VERSION}")
    if cfg.timeframe != "M15":
        raise SystemExit("execution timeframe must be M15")
    if cfg.h4_adx_min != EXPECTED_H4_ADX_MIN:
        raise SystemExit("CAMPAIGN_023 requires h4_adx_min == 22.0 (ADX22 sibling)")
    if cfg.max_bars_in_trade != 32 or cfg.atr_stop_multiple != 2.0:
        raise SystemExit("precommitted risk parameters diverged")
    if settings.app.trading_enabled or settings.app.allow_order_submission:
        raise SystemExit("order submission / trading must stay disabled")
    validate_c022_data_provenance(raw.get("data_provenance") or {})
    return cfg.model_dump()


def preflight(settings: Settings, raw: dict[str, Any]) -> dict[str, Any]:
    meta = parse_research_metadata(raw.get("research_metadata"))
    provenance = raw.get("data_provenance") or {}
    strategy = H4H1PullbackResolutionEntryStrategy(
        version=EXPECTED_VERSION, campaign_id=CAMPAIGN_ID
    )
    blocked: list[str] = []
    cfg = settings.strategy.h4_h1_pullback_resolution_entry
    result: dict[str, Any] = {
        "campaign_id": CAMPAIGN_ID,
        "strategy_name": EXPECTED_STRATEGY,
        "version": EXPECTED_VERSION,
        "sibling_of": "CAMPAIGN_022",
        "h4_adx_min": cfg.h4_adx_min if cfg else None,
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

    # --- config / provenance / no-lookahead validation (no DB needed) ---------
    try:
        validate_c022_data_provenance(provenance)
    except ValueError as exc:
        blocked.append(str(exc))
    for forbidden in ("d1agg_context", "d1agg_source", "d1_context", "d1_source"):
        if provenance.get(forbidden) is not None:
            blocked.append(f"CAMPAIGN_023 has no daily layer; unexpected {forbidden}")
    if cfg is None or cfg.h4_adx_min != EXPECTED_H4_ADX_MIN:
        blocked.append("h4_adx_min must be 22.0 (ADX22 sibling delta)")
    if meta is None or meta.fill_timing != FillTiming.NEXT_BAR_OPEN:
        blocked.append("fill_timing must be next_bar_open")
    if meta is not None and meta.promotion_eligible:
        blocked.append("promotion_eligible must be false")
    if settings.app.trading_enabled or settings.app.allow_order_submission:
        blocked.append("order submission must stay disabled")
    if settings.app.allow_live_trading:
        blocked.append("live trading must stay disabled")
    approved = yaml.safe_load(
        (ROOT / "configs/approved_strategies.yaml").read_text(encoding="utf-8")
    )
    if approved.get("approved"):
        blocked.append("approved_strategies.yaml must remain empty")

    # --- data + feature availability (best-effort; DB optional) ---------------
    data_check: dict[str, Any] = {"db_reachable": False}
    try:
        from forex_bot.data.m1_corpus_validation import MAJOR_PAIRS, inventory_sql
        from forex_bot.data.m1_timeframe_materialization import MATERIALIZED_SOURCE
        from forex_bot.data.postgres_candle_store import PostgresCandleStore
        from forex_bot.data.research_db import get_research_database_config
        from forex_bot.project_env import bootstrap_environ

        environ = bootstrap_environ(None)
        db_cfg = get_research_database_config(environ=environ, require=True)
        store = PostgresCandleStore(db_cfg)
        inv = inventory_sql(store)
        data_check["db_reachable"] = True
        data_check["materialized_source"] = MATERIALIZED_SOURCE
        data_check["m1_overall_status"] = inv["overall_status"]
        data_check["m1_pair_count"] = len(inv["pairs"])
        data_check["expected_pairs"] = list(MAJOR_PAIRS)
        if inv.get("missing_pairs"):
            blocked.append(f"missing M1 pairs: {inv['missing_pairs']}")
        feature_rows: dict[str, int] = {}
        with store.connection() as conn, conn.cursor() as cur:
            for gran in ("M15", "H1", "H4"):
                cur.execute(
                    f"SELECT COUNT(*) FROM {db_cfg.schema}.candles "
                    f"WHERE granularity = %s",
                    (gran,),
                )
                feature_rows[gran] = int(cur.fetchone()[0])
        data_check["feature_rows"] = feature_rows
        for gran, n in feature_rows.items():
            if n < 1000:
                blocked.append(f"insufficient materialized {gran} rows ({n})")
    except Exception as exc:
        data_check["note"] = (
            f"data/feature availability not verified (DB unavailable): {exc}"
        )
    result["data_feature_availability"] = data_check

    result["blocked_reasons"] = blocked
    # preflight_ok reflects config/provenance/freeze; DB availability is advisory.
    config_blockers = [b for b in blocked if not b.startswith(("missing M1", "insufficient"))]
    result["config_preflight_ok"] = not config_blockers
    result["preflight_ok"] = not blocked
    return result


def _write(out_name: str, payload: dict[str, Any]) -> None:
    OUT_RESEARCH.mkdir(parents=True, exist_ok=True)
    (OUT_RESEARCH / out_name).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CAMPAIGN_023 ADX22 scaffold runner (preflight only)"
    )
    parser.add_argument("--validate-config", action="store_true")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["train-validation", "test", "full"],
        help="BLOCKED in scaffold sprint (no evidence is produced)",
    )
    args = parser.parse_args()
    settings, raw = load_settings()

    if args.command:
        print(EVIDENCE_BLOCKED, file=sys.stderr)
        return 2

    if args.validate_config:
        validate_frozen_config(settings, raw)
        print(f"[{CAMPAIGN_ID}] config OK — {EXPECTED_STRATEGY} {EXPECTED_VERSION} "
              f"(h4_adx_min=22.0, ADX22 sibling of CAMPAIGN_022)")
        return 0

    # Default: preflight-only.
    pf = preflight(settings, raw)
    _write("preflight_result.json", pf)
    print(json.dumps(pf, indent=2, sort_keys=True))
    return 0 if pf["config_preflight_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
