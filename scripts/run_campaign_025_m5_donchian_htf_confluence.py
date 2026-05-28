#!/usr/bin/env python3
"""CAMPAIGN_025 — M5 Donchian + HTF confluence breakout SCAFFOLD runner.

Scaffold/precommit sprint only. This runner implements **preflight** modes only:

    --preflight-only           coverage + safety preflight (no features)
    --data-feature-preflight   per-pair counts/ranges + HTF last-completed probe
    --sample-signals-only      tiny bounded signal-count probe (no evidence)
    --validate-config          frozen-identity check

It deliberately contains **no** train/validation/test evidence machinery: the
test lockbox cannot be opened here. If the materialized store is unavailable, the
runner records ``BLOCKED_DATA_PRECONDITION`` rather than improvising. No OANDA
order/trade/position/live endpoints are touched; approved_strategies stays empty.
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
from forex_bot.data.m1_timeframe_materialization import MATERIALIZED_SOURCE
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import get_research_database_config
from forex_bot.project_env import bootstrap_environ
from forex_bot.research.campaign_025_loader import (
    build_data_feature_preflight,
    check_materialized_coverage,
    instrument_for,
    live_aggregation_enabled,
    load_c025_frames,
)
from forex_bot.research.execution_realism import (
    ExecutionRealism,
    FillTiming,
    parse_research_metadata,
)
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.m5_donchian_htf_confluence_breakout import (
    D1AGG_SOURCE_M1,
    M5DonchianHtfConfluenceBreakoutStrategy,
    validate_c025_data_provenance,
)

CONFIG_PATH = ROOT / "configs/campaign_025_m5_donchian_htf_confluence_breakout.yaml"
APPROVED_PATH = ROOT / "configs/approved_strategies.yaml"
OUT_RESEARCH = ROOT / "research/campaign_025"
OUT_PREFLIGHT = OUT_RESEARCH / "preflight"
EXPECTED_STRATEGY = "m5_donchian_htf_confluence_breakout"

# Frozen splits (used only to scope the preflight window — no evidence here).
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


def assert_registry_empty() -> None:
    approved = yaml.safe_load(APPROVED_PATH.read_text(encoding="utf-8")) or {}
    if approved.get("approved"):
        raise SystemExit("approved_strategies.yaml must remain empty for CAMPAIGN_025")


def assert_execution_metadata(raw: dict[str, Any]) -> None:
    meta = parse_research_metadata(raw.get("research_metadata"))
    if meta is None:
        raise SystemExit("research_metadata required")
    if meta.fill_timing != FillTiming.NEXT_BAR_OPEN:
        raise SystemExit("fill_timing must be next_bar_open")
    if meta.execution_realism != ExecutionRealism.CONSERVATIVE:
        raise SystemExit("execution_realism must be conservative")
    provenance = raw.get("data_provenance") or {}
    validate_c025_data_provenance(provenance)
    if provenance.get("d1agg_context") == D1AGG_SOURCE_M1:
        raise SystemExit("m1_derived_d1agg forbidden")


def validate_frozen_config(settings: Settings, raw: dict[str, Any]) -> dict[str, Any]:
    assert_registry_empty()
    assert_execution_metadata(raw)
    if settings.strategy.enabled != [EXPECTED_STRATEGY]:
        raise SystemExit(f"config must enable only {EXPECTED_STRATEGY}")
    cfg = settings.strategy.m5_donchian_htf_confluence_breakout
    if cfg is None:
        raise SystemExit("missing m5_donchian_htf_confluence_breakout config")
    if cfg.version != "0.1.0-c025" or cfg.timeframe != "M5":
        raise SystemExit("frozen identity diverged")
    if cfg.entry_channel_length != 20 or cfg.atr_stop_multiple != 2.0 or cfg.max_bars_in_trade != 48:
        raise SystemExit("precommitted parameters diverged")
    return cfg.model_dump()


def _write(name: str, payload: Any) -> Path:
    OUT_PREFLIGHT.mkdir(parents=True, exist_ok=True)
    path = OUT_PREFLIGHT / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return path


def _run_manifest(mode: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = {
        "campaign_id": "CAMPAIGN_025",
        "strategy_name": EXPECTED_STRATEGY,
        "version": "0.1.0-c025",
        "mode": mode,
        "scaffold_only": True,
        "not_approved": True,
        "strategy_evidence": False,
        "test_lockbox_opened": False,
        "full_evidence_run": False,
        "fill_timing": "next_bar_open",
        "checked_at_utc": datetime.now(UTC).isoformat(),
    }
    if extra:
        manifest.update(extra)
    return manifest


def _open_store() -> PostgresCandleStore:
    environ = bootstrap_environ(None)
    cfg = get_research_database_config(environ=environ, require=True)
    return PostgresCandleStore(cfg)


def preflight(settings: Settings, raw: dict[str, Any]) -> dict[str, Any]:
    strategy = M5DonchianHtfConfluenceBreakoutStrategy()
    blocked: list[str] = []
    coverage: dict[str, Any] = {}
    result: dict[str, Any] = {
        "campaign_id": "CAMPAIGN_025",
        "strategy_name": EXPECTED_STRATEGY,
        "version": "0.1.0-c025",
        "not_approved": True,
        "strategy_evidence": False,
        "fill_timing": "next_bar_open",
        "data_provenance": raw.get("data_provenance"),
        "warmup_bars_required": strategy.warmup_bars_required(),
        "pairs": list(settings.market.instruments),
        "checked_at_utc": datetime.now(UTC).isoformat(),
    }
    try:
        assert_execution_metadata(raw)
        assert_registry_empty()
    except SystemExit as exc:
        blocked.append(str(exc))
    if live_aggregation_enabled():
        blocked.append(f"{live_aggregation_enabled.__module__}: live aggregation must not be enabled")
    try:
        store = _open_store()
        train_from, train_to = SPLITS["train"]
        from_dt = datetime.fromisoformat(train_from).replace(tzinfo=UTC)
        to_dt = datetime.fromisoformat(train_to).replace(hour=23, minute=59, tzinfo=UTC)
        missing: list[str] = []
        for pair in settings.market.instruments:
            cov = check_materialized_coverage(store, pair, from_dt=from_dt, to_dt=to_dt)
            coverage[pair] = cov
            if cov["status"] != "PASS":
                missing.append(pair)
        if missing:
            blocked.append(
                "BLOCKED_DATA_PRECONDITION: missing materialized M5/M15/H1/H4 for "
                + ", ".join(missing)
                + " — run scripts/materialize_m1_derived_timeframes.py --all-majors"
            )
    except Exception as exc:
        blocked.append(f"BLOCKED_DATA_PRECONDITION: postgres unavailable: {exc}")
    result["materialized_source"] = MATERIALIZED_SOURCE
    result["pair_coverage"] = coverage
    result["blocked_reasons"] = blocked
    result["preflight_ok"] = not blocked
    return result


def sample_signals(
    settings: Settings,
    raw: dict[str, Any],
    *,
    pair: str,
    days: int,
    step: int,
    start: str,
) -> dict[str, Any]:
    """Tiny bounded probe: count signals over a small window. No evidence run."""
    from datetime import timedelta

    from forex_bot.domain.candles import CandleFrame

    assert_execution_metadata(raw)
    assert_registry_empty()
    cfg = settings.strategy.m5_donchian_htf_confluence_breakout
    strat_cfg = cfg.model_dump() if cfg else {}
    strat_cfg["data_provenance"] = raw.get("data_provenance")
    strategy = M5DonchianHtfConfluenceBreakoutStrategy()
    out: dict[str, Any] = {
        "campaign_id": "CAMPAIGN_025",
        "pair": pair,
        "window_start": start,
        "window_days": days,
        "step_bars": step,
        "scaffold_only": True,
        "full_evidence_run": False,
    }
    try:
        store = _open_store()
        from_dt = datetime.fromisoformat(start).replace(tzinfo=UTC)
        to_dt = from_dt + timedelta(days=max(1, days))  # bounded window only
        frames = load_c025_frames(store, pair, from_dt=from_dt, to_dt=to_dt)
    except SystemExit as exc:
        out["status"] = "BLOCKED_DATA_PRECONDITION"
        out["reason"] = str(exc)
        return out
    except Exception as exc:
        out["status"] = "BLOCKED_DATA_PRECONDITION"
        out["reason"] = f"postgres unavailable: {exc}"
        return out

    df = frames.m5.completed_only().df
    instrument = instrument_for(pair)
    context_frames = {"M15": frames.m15, "H1": frames.h1, "H4": frames.h4, "D1AGG": frames.d1agg}
    warmup = strategy.warmup_bars_required()
    signals = long_signals = short_signals = evaluated = 0
    n = len(df)
    for i in range(warmup, n, max(1, step)):
        # Slice the M5 frame to bars [0, i] so Donchian sees prior bars only;
        # HTF frames carry the whole window but the strategy aligns to the last
        # completed HTF bar <= decision, so there is no lookahead.
        ctx_frame = CandleFrame(instrument=pair, granularity="M5", df=df.iloc[: i + 1])
        ctx = StrategyContext(
            instrument=instrument,
            candles=ctx_frame,
            market_state=None,  # not read by this strategy
            open_positions=[],
            config={**strat_cfg, "context_frames": context_frames},
        )
        evaluated += 1
        sig = strategy.generate_signal(ctx)
        if sig is not None:
            signals += 1
            long_signals += int(sig.side == "long")
            short_signals += int(sig.side == "short")
    out.update(
        {
            "status": "OK",
            "m5_bars": n,
            "evaluated_decisions": evaluated,
            "signals": signals,
            "long_signals": long_signals,
            "short_signals": short_signals,
        }
    )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="CAMPAIGN_025 SCAFFOLD runner")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--data-feature-preflight", action="store_true")
    parser.add_argument("--sample-signals-only", action="store_true")
    parser.add_argument("--validate-config", action="store_true")
    parser.add_argument("--sample-pair", default="EUR_USD")
    # Default start sits inside the materialized M5 coverage range (M5 begins
    # ~2021-05-27 in the train split), so the bounded probe is not empty.
    parser.add_argument("--sample-start", default="2021-06-01")
    parser.add_argument("--sample-days", type=int, default=10)
    parser.add_argument("--sample-step", type=int, default=3)
    args = parser.parse_args()
    settings, raw = load_settings()

    if args.validate_config:
        validate_frozen_config(settings, raw)
        print(f"[CAMPAIGN_025] config OK — {EXPECTED_STRATEGY} 0.1.0-c025")
        return 0

    if args.preflight_only:
        pf = preflight(settings, raw)
        _write("preflight_result.json", pf)
        _write(
            "pair_coverage_summary.json",
            {"campaign_id": "CAMPAIGN_025", "pair_coverage": pf.get("pair_coverage", {})},
        )
        _write("run_manifest.json", _run_manifest("preflight-only", {"preflight_ok": pf["preflight_ok"]}))
        print(json.dumps(pf, indent=2, sort_keys=True, default=str))
        return 0 if pf["preflight_ok"] else 1

    if args.data_feature_preflight:
        assert_execution_metadata(raw)
        assert_registry_empty()
        try:
            store = _open_store()
            report = build_data_feature_preflight(
                store, splits=SPLITS, pairs=list(settings.market.instruments)
            )
        except Exception as exc:
            report = {
                "campaign_id": "CAMPAIGN_025",
                "status": "BLOCKED_DATA_PRECONDITION",
                "reason": f"postgres unavailable: {exc}",
                "preflight_ok": False,
                "strategy_evidence": False,
            }
        _write("data_feature_preflight.json", report)
        # split out the HTF / warmup views for quick inspection
        pairs = report.get("pairs", {})
        _write(
            "htf_alignment_sample.json",
            {
                p: {
                    "htf_blocked_samples": r.get("htf_blocked_samples"),
                    "lookahead_violations": r.get("lookahead_violations"),
                }
                for p, r in pairs.items()
            },
        )
        _write(
            "feature_warmup_summary.json",
            {
                p: {
                    "m5_count": r.get("m5_count"),
                    "m15_count": r.get("m15_count"),
                    "h1_count": r.get("h1_count"),
                    "h4_count": r.get("h4_count"),
                    "d1agg_count": r.get("d1agg_count"),
                    "warmup_ok": r.get("warmup_ok"),
                    "status": r.get("status"),
                }
                for p, r in pairs.items()
            },
        )
        _write("run_manifest.json", _run_manifest("data-feature-preflight", {"preflight_ok": report.get("preflight_ok", False)}))
        print(json.dumps(report, indent=2, sort_keys=True, default=str))
        return 0 if report.get("preflight_ok") else 1

    if args.sample_signals_only:
        summary = sample_signals(
            settings,
            raw,
            pair=args.sample_pair,
            days=args.sample_days,
            step=args.sample_step,
            start=args.sample_start,
        )
        _write("sample_signal_summary.json", summary)
        _write("run_manifest.json", _run_manifest("sample-signals-only", {"sample_status": summary.get("status")}))
        print(json.dumps(summary, indent=2, sort_keys=True, default=str))
        return 0 if summary.get("status") in ("OK", "BLOCKED_DATA_PRECONDITION") else 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
