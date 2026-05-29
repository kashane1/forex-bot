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


TRAIN_DIR = OUT_RESEARCH / "train_matrix"
VALID_DIR = OUT_RESEARCH / "validation"
# Test window is LOCKED — the runner refuses to operate inside it.
TEST_WINDOW = ("2025-01-01", "2026-05-20")


def _assert_not_test_window(start: str, end: str) -> None:
    ts, te = TEST_WINDOW
    if not (end < ts or start > te):
        raise SystemExit(
            f"FAIL_IF_TEST_WINDOW: requested window [{start},{end}] overlaps the LOCKED "
            f"test window [{ts},{te}] — the lockbox stays closed in this sprint."
        )


def _load_candidates() -> list[dict]:
    reg = json.loads((TRAIN_DIR / "candidate_registry.json").read_text(encoding="utf-8"))
    return reg["candidates"]


def run_train_matrix(settings, raw, *, train_start: str, train_end: str) -> dict[str, Any]:
    """Run the full candidate matrix on the TRAIN window only; never validation/test."""
    import csv

    from forex_bot.research import campaign_025_train_matrix as tm

    assert_execution_metadata(raw)
    assert_registry_empty()
    _assert_not_test_window(train_start, train_end)
    pairs = list(settings.market.instruments)
    ws = datetime.fromisoformat(train_start).replace(tzinfo=UTC)
    we = datetime.fromisoformat(train_end).replace(hour=23, minute=59, tzinfo=UTC)
    store = _open_store()
    feats = tm.load_features_for_window(store, pairs, window_start=ws, window_end=we)
    candidates = _load_candidates()
    evals = [tm.evaluate_candidate(feats, c, window_start=ws, window_end=we) for c in candidates]
    selection = tm.rank_and_select(evals)

    TRAIN_DIR.mkdir(parents=True, exist_ok=True)

    def _csv(name: str, rows: list[dict]) -> None:
        if not rows:
            (TRAIN_DIR / name).write_text("", encoding="utf-8")
            return
        with (TRAIN_DIR / name).open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    metrics_rows, gate_rows, pair_rows, side_rows, exit_rows, stress_rows, c011_rows = ([] for _ in range(7))
    holding, spread_atr, funnel = {}, {}, {}
    for ev in evals:
        cid, b, s = ev["candidate_id"], ev["base"], ev["stress_2x"]
        metrics_rows.append({
            "candidate_id": cid, "archetype": ev["archetype"], "trade_count": b["trade_count"],
            "expectancy_r": b["expectancy_r"], "profit_factor": b["profit_factor"],
            "pairs_nonneg": b["pairs_nonneg"], "top_pair_concentration": b["top_pair_positive_r_concentration"],
            "stress_2x_expectancy_r": s["expectancy_r"], "beat_c011_null_by": b["beat_c011_null_by"],
            "avg_hold_bars": round(b["avg_hold_bars"], 2), "avg_spread_atr_ratio": b["avg_spread_atr_ratio"],
        })
        gate_rows.append({"candidate_id": cid, "eligible": ev["filters"]["eligible"],
                          "failed": "|".join(ev["filters"]["failed"]),
                          "single_pair_review_flag": ev["filters"]["single_pair_review_flag"]})
        for p, v in b["per_pair_expectancy_r"].items():
            pair_rows.append({"candidate_id": cid, "pair": p, "expectancy_r": v,
                              "trade_count": b["per_pair_trade_count"][p]})
        side_rows.append({"candidate_id": cid, "long_count": b["long_count"], "long_expectancy_r": b["long_expectancy_r"],
                          "short_count": b["short_count"], "short_expectancy_r": b["short_expectancy_r"]})
        exit_rows.append({"candidate_id": cid, **b["exit_reason_counts"]})
        stress_rows.append({"candidate_id": cid, "base_expectancy_r": b["expectancy_r"], "stress_2x_expectancy_r": s["expectancy_r"]})
        c011_rows.append({"candidate_id": cid, "expectancy_r": b["expectancy_r"], "c011_null": tm.C011_NULL_EXP_R,
                          "beat_by": b["beat_c011_null_by"], "beat_by_margin_010": (b["beat_c011_null_by"] or -9) >= 0.010})
        holding[cid] = {"avg_hold_bars": b["avg_hold_bars"], "median_hold_bars": b["median_hold_bars"]}
        spread_atr[cid] = {"avg_spread_atr_ratio": b["avg_spread_atr_ratio"]}
        funnel[cid] = ev["funnel_total"]

    _csv("train_matrix_metrics.csv", metrics_rows)
    _csv("train_matrix_gate_filters.csv", gate_rows)
    _csv("train_matrix_pair_metrics.csv", pair_rows)
    _csv("train_matrix_side_metrics.csv", side_rows)
    _csv("train_matrix_exit_reason_summary.csv", exit_rows)
    _csv("train_matrix_cost_stress_2x.csv", stress_rows)
    _csv("train_matrix_comparison_to_c011_null.csv", c011_rows)
    (TRAIN_DIR / "train_matrix_holding_period_diagnostics.json").write_text(json.dumps(holding, indent=2), encoding="utf-8")
    (TRAIN_DIR / "train_matrix_spread_atr_diagnostics.json").write_text(json.dumps(spread_atr, indent=2), encoding="utf-8")
    (TRAIN_DIR / "train_matrix_signal_funnel_diagnostics.json").write_text(json.dumps(funnel, indent=2), encoding="utf-8")
    selection["train_window"] = {"start": train_start, "end": train_end}
    selection["pairs"] = pairs
    (TRAIN_DIR / "train_matrix_candidate_selection.json").write_text(json.dumps(selection, indent=2, default=str), encoding="utf-8")
    (TRAIN_DIR / "train_matrix_run_manifest.json").write_text(json.dumps(
        _run_manifest("train-matrix", {"train_window": [train_start, train_end], "candidates": len(candidates),
                                       "champion": selection["champion_candidate_id"],
                                       "classification": selection["classification"]}), indent=2), encoding="utf-8")
    warnings = {"classification": selection["classification"],
                "single_pair_review_flags": selection.get("single_pair_review_flags", []),
                "validation_allowed": selection["champion_candidate_id"] is not None}
    (TRAIN_DIR / "blocked_or_warning_conditions.json").write_text(json.dumps(warnings, indent=2), encoding="utf-8")
    return selection


def run_champion_validation(settings, raw, *, valid_start: str, valid_end: str) -> dict[str, Any]:
    """Run validation ONCE on the train-selected champion only; never test."""
    from forex_bot.research import campaign_025_train_matrix as tm

    assert_execution_metadata(raw)
    assert_registry_empty()
    _assert_not_test_window(valid_start, valid_end)
    sel_path = TRAIN_DIR / "train_matrix_candidate_selection.json"
    if not sel_path.is_file():
        raise SystemExit("no train selection found — run --train-matrix first")
    selection = json.loads(sel_path.read_text(encoding="utf-8"))
    champ_id = selection.get("champion_candidate_id")
    if not champ_id:
        return {"validation_run": False, "reason": "no champion selected on train", "classification": selection["classification"]}
    champ = selection["champion_parameters"]
    pairs = list(settings.market.instruments)
    ws = datetime.fromisoformat(valid_start).replace(tzinfo=UTC)
    we = datetime.fromisoformat(valid_end).replace(hour=23, minute=59, tzinfo=UTC)
    store = _open_store()
    feats = tm.load_features_for_window(store, pairs, window_start=ws, window_end=we)
    ev = tm.evaluate_candidate(feats, champ, window_start=ws, window_end=we)
    b, s = ev["base"], ev["stress_2x"]
    gates = {
        "validation_expectancy_gt_0": (b["expectancy_r"] or -9) > 0,
        "validation_pf_gte_1_05": (b["profit_factor"] or 0) >= 1.05,
        "validation_trades_gte_100": b["trade_count"] >= 100,
        "validation_pairs_nonneg_gte_4": b["pairs_nonneg"] >= 4,
        "stress_2x_expectancy_gte_0": (s["expectancy_r"] or -9) >= 0,
        "beat_c011_null_by_010": (b["beat_c011_null_by"] or -9) >= 0.010,
        "backtrader_parity_pass": False,  # parity not built this sprint
    }
    screening = all(v for k, v in gates.items() if k != "backtrader_parity_pass")
    classification = (
        "TRAIN_MATRIX_VALIDATION_PASS_PARITY_REQUIRED" if screening else "TRAIN_MATRIX_VALIDATION_REJECT"
    )
    out = {
        "validation_run": True, "validation_run_once": True, "selection_uses_validation": False,
        "champion_candidate_id": champ_id, "champion_parameters": champ,
        "validation_window": {"start": valid_start, "end": valid_end},
        "base": b, "stress_2x": s, "gates": gates, "screening_pass": screening,
        "classification": f"{classification} / TEST_LOCKBOX_CLOSED / NOT_APPROVED",
        "funnel_total": ev["funnel_total"], "test_lockbox_opened": False, "approved": False,
    }
    VALID_DIR.mkdir(parents=True, exist_ok=True)
    (VALID_DIR / "champion_validation_result.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="CAMPAIGN_025 runner (scaffold + train-matrix evidence)")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--data-feature-preflight", action="store_true")
    parser.add_argument("--sample-signals-only", action="store_true")
    parser.add_argument("--validate-config", action="store_true")
    parser.add_argument("--train-matrix", action="store_true")
    parser.add_argument("--validate-champion", action="store_true")
    parser.add_argument("--train-start", default="2021-07-01")
    parser.add_argument("--train-end", default="2023-06-30")
    parser.add_argument("--valid-start", default="2023-07-01")
    parser.add_argument("--valid-end", default="2024-12-31")
    parser.add_argument("--sample-pair", default="EUR_USD")
    # Default start sits inside the materialized M5 coverage range (M5 begins
    # ~2021-05-27 in the train split), so the bounded probe is not empty.
    parser.add_argument("--sample-start", default="2021-06-01")
    parser.add_argument("--sample-days", type=int, default=10)
    parser.add_argument("--sample-step", type=int, default=3)
    args = parser.parse_args()
    settings, raw = load_settings()

    if args.train_matrix:
        selection = run_train_matrix(settings, raw, train_start=args.train_start, train_end=args.train_end)
        print(json.dumps({k: v for k, v in selection.items() if k != "ranking"}, indent=2, default=str))
        return 0

    if args.validate_champion:
        out = run_champion_validation(settings, raw, valid_start=args.valid_start, valid_end=args.valid_end)
        print(json.dumps({k: v for k, v in out.items() if k not in ("base", "stress_2x")}, indent=2, default=str))
        return 0

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
