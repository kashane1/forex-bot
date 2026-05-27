#!/usr/bin/env python3
"""CAMPAIGN_020 — MTF confluence pullback runner (scaffold / preflight only).

Full train/validation evidence is **blocked** in this scaffold sprint.
Use a future execution sprint with ``--execute-evidence`` (not enabled here).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.config import Settings, compute_config_hash, load_settings
from forex_bot.research.execution_realism import (
    FillTiming,
    parse_research_metadata,
    validate_campaign_yaml_metadata,
)
from forex_bot.strategies.multi_timeframe_confluence_pullback import (
    MultiTimeframeConfluencePullbackStrategy,
)

CONFIG_PATH = ROOT / "configs/campaign_020_mtf_confluence_pullback.yaml"
OUT_RESEARCH = ROOT / "research/campaign_020"
EXPECTED_STRATEGY = "multi_timeframe_confluence_pullback"


def _load_campaign_yaml() -> dict[str, Any]:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}


def _strip_for_settings(raw: dict[str, Any]) -> dict[str, Any]:
    data = dict(raw)
    for key in ("campaign", "research_metadata", "financing"):
        data.pop(key, None)
    text = CONFIG_PATH.read_text(encoding="utf-8")
    data.setdefault("config_hash", compute_config_hash(text))
    data.setdefault("config_source_path", str(CONFIG_PATH))
    return data


def validate_frozen_config(settings: Settings) -> None:
    sc = settings.strategy
    if sc.enabled != [EXPECTED_STRATEGY]:
        raise SystemExit(
            f"CAMPAIGN_020 config must enable only {EXPECTED_STRATEGY}"
        )
    if sc.multi_timeframe_confluence_pullback is None:
        raise SystemExit("missing multi_timeframe_confluence_pullback config")
    c020 = sc.multi_timeframe_confluence_pullback
    if c020.version != "0.1.0-c020":
        raise SystemExit("version must be 0.1.0-c020")
    if c020.d1_ema_slow != 50 or c020.h4_ema_context != 50:
        raise SystemExit("precommitted EMA parameters diverged")


def preflight(settings: Settings, raw: dict[str, Any]) -> dict[str, Any]:
    db = Path(settings.app.database_path)
    meta = parse_research_metadata(raw.get("research_metadata"))
    financing = raw.get("financing") or {}
    strategy = MultiTimeframeConfluencePullbackStrategy()
    result: dict[str, Any] = {
        "campaign_id": "CAMPAIGN_020",
        "strategy_name": EXPECTED_STRATEGY,
        "version": "0.1.0-c020",
        "not_approved": True,
        "scaffold_only": True,
        "strategy_evidence": False,
        "test_lockbox_opened": False,
        "database_path": str(db),
        "database_exists": db.is_file(),
        "fill_timing": meta.fill_timing.value if meta and meta.fill_timing else None,
        "execution_realism": (
            meta.execution_realism.value if meta and meta.execution_realism else None
        ),
        "financing_mode": financing.get("financing_mode"),
        "financing_overlay_required": financing.get("financing_overlay_required"),
        "warmup_bars_required": strategy.warmup_bars_required(),
        "pairs": list(settings.market.instruments),
        "blocked_reasons": [],
    }
    if meta is None or meta.fill_timing != FillTiming.NEXT_BAR_OPEN:
        result["blocked_reasons"].append("fill_timing must be next_bar_open")
    if not db.is_file():
        result["blocked_reasons"].append(f"missing database: {db}")
    if settings.app.trading_enabled or settings.app.allow_order_submission:
        result["blocked_reasons"].append("order submission must stay disabled")
    if raw.get("campaign", {}).get("not_approved") is not True:
        result["blocked_reasons"].append("campaign.not_approved must be true")
    result["preflight_ok"] = not result["blocked_reasons"]
    return result


def emit_plan(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "campaign_id": "CAMPAIGN_020",
        "strategy": EXPECTED_STRATEGY,
        "version": "0.1.0-c020",
        "status": "PRECOMMITTED_NOT_EXECUTED",
        "splits": {
            "train": ["2020-01-01", "2022-12-31"],
            "validation": ["2023-01-01", "2024-12-31"],
            "test": ["2025-01-01", "2026-05-20"],
        },
        "fill_timing": "next_bar_open",
        "precommit_doc": "docs/research/CAMPAIGN_020_MTF_CONFLUENCE_PRECOMMIT.md",
        "execution_prompt": (
            "docs/research/NEXT_SPRINT_PROMPT_CAMPAIGN_020_MTF_CONFLUENCE_EXECUTION.md"
        ),
        "full_evidence_blocked": True,
        "not_approved": True,
        "research_metadata": raw.get("research_metadata"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="CAMPAIGN_020 scaffold runner")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--validate-config", action="store_true")
    parser.add_argument("--emit-plan", action="store_true")
    parser.add_argument(
        "--execute-evidence",
        action="store_true",
        help="BLOCKED in scaffold sprint — reserved for future execution sprint",
    )
    args = parser.parse_args()

    if args.execute_evidence:
        print(
            "REFUSED: full evidence execution is blocked in the scaffold sprint. "
            "See docs/research/NEXT_SPRINT_PROMPT_CAMPAIGN_020_MTF_CONFLUENCE_EXECUTION.md"
        )
        return 2

    raw = _load_campaign_yaml()
    yaml_errors = validate_campaign_yaml_metadata(raw)
    if yaml_errors:
        print("research_metadata validation failed:", yaml_errors)
        return 1

    settings = Settings.model_validate(_strip_for_settings(raw))
    validate_frozen_config(settings)

    if args.validate_config or args.dry_run or args.preflight_only or args.emit_plan:
        print(f"[CAMPAIGN_020] config OK — {EXPECTED_STRATEGY} 0.1.0-c020")
        print("[CAMPAIGN_020] approved: false · evidence: blocked in scaffold")

    if args.emit_plan:
        plan = emit_plan(raw)
        OUT_RESEARCH.mkdir(parents=True, exist_ok=True)
        out = OUT_RESEARCH / "execution_plan.json"
        out.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        print(f"[CAMPAIGN_020] plan written: {out}")

    if args.preflight_only or args.dry_run:
        pf = preflight(settings, raw)
        OUT_RESEARCH.mkdir(parents=True, exist_ok=True)
        out = OUT_RESEARCH / "preflight.json"
        out.write_text(json.dumps(pf, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(pf, indent=2))
        if not pf["preflight_ok"]:
            print("[CAMPAIGN_020] preflight BLOCKED (expected if DB missing locally)")
        return 0

    if args.validate_config:
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
