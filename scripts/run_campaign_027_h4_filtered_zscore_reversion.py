#!/usr/bin/env python3
"""CAMPAIGN_027 — Filtered H4 z-score reversion SCAFFOLD runner.

Scaffold/precommit sprint only. **Preflight modes only** — no train/validation/
test/backtest/execute evidence machinery, and the test lockbox cannot be opened
here:

    --validate-config          frozen-identity check
    --preflight-only           H4 coverage + safety preflight
    --data-feature-preflight   per-pair feature computability (train window)
    --sample-signals-only      tiny bounded signal-count probe (diagnostic only)

Forbidden flags (``--train`` / ``--validation`` / ``--test`` / ``--backtest`` /
``--execute``) are explicitly refused. No OANDA order/trade/position/live
endpoint is touched; no live creds; ``approved_strategies.yaml`` must stay empty.
If the H4 store is unavailable the runner records ``BLOCKED_DATA_PRECONDITION``
rather than improvising. No bulky raw candle data is emitted.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.config import Settings, compute_config_hash
from forex_bot.strategies.h4_filtered_zscore_reversion import (
    H4FilteredZscoreReversionStrategy,
    compute_decision,
)

CONFIG_PATH = ROOT / "configs/campaign_027_h4_filtered_zscore_reversion.yaml"
APPROVED_PATH = ROOT / "configs/approved_strategies.yaml"
OUT_RESEARCH = ROOT / "research/campaign_027"
OUT_PREFLIGHT = OUT_RESEARCH / "preflight"
EXPECTED_STRATEGY = "h4_filtered_zscore_reversion"

# Frozen splits — used only to SCOPE the preflight window. No evidence here.
SPLITS: dict[str, tuple[str, str]] = {
    "train": ("2020-01-01", "2022-12-31"),
    "validation": ("2023-01-01", "2024-12-31"),
    "test": ("2025-01-01", "2026-05-20"),
}
TEST_WINDOW = SPLITS["test"]
_BIDASK = ("bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c")


# --------------------------------------------------------------------------
# Safety helpers
# --------------------------------------------------------------------------

def _load_raw() -> dict[str, Any]:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}


def _strip_for_settings(raw: dict[str, Any]) -> dict[str, Any]:
    data = dict(raw)
    for key in ("campaign", "research_metadata", "financing", "data_provenance", "cost_model"):
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
        raise SystemExit("approved_strategies.yaml must remain empty for CAMPAIGN_027")


def assert_execution_metadata(raw: dict[str, Any]) -> None:
    meta = raw.get("research_metadata") or {}
    if meta.get("fill_timing") != "next_bar_open":
        raise SystemExit("fill_timing must be next_bar_open")
    if meta.get("execution_realism") != "conservative":
        raise SystemExit("execution_realism must be conservative")
    if meta.get("promotion_eligible") is True:
        raise SystemExit("promotion_eligible must be false in scaffold")


def assert_not_test_window(start: str, end: str) -> None:
    ts, te = TEST_WINDOW
    if not (end < ts or start > te):
        raise SystemExit(
            f"FAIL_IF_TEST_WINDOW: requested window [{start},{end}] overlaps the LOCKED "
            f"test window [{ts},{te}] — the lockbox stays closed in this sprint."
        )


def validate_frozen_config(settings: Settings, raw: dict[str, Any]) -> dict[str, Any]:
    assert_registry_empty()
    assert_execution_metadata(raw)
    if settings.strategy.enabled != [EXPECTED_STRATEGY]:
        raise SystemExit(f"config must enable only {EXPECTED_STRATEGY}")
    cfg = settings.strategy.h4_filtered_zscore_reversion
    if cfg is None:
        raise SystemExit("missing h4_filtered_zscore_reversion config")
    if cfg.version != "0.1.0-c027" or cfg.timeframe != "H4":
        raise SystemExit("frozen identity diverged")
    if (
        cfg.zscore_lookback != 20
        or cfg.strong_extension_abs_z != 2.5
        or cfg.atr_percentile_window != 250
        or cfg.atr_percentile_max != 0.33
        or cfg.side_mode != "short_only"
        or cfg.max_bars_in_trade != 12
        or cfg.atr_stop_multiple != 3.0
    ):
        raise SystemExit("precommitted parameters diverged")
    return cfg.model_dump()


# --------------------------------------------------------------------------
# Data (raw read-only sqlite; worktree-aware store resolution)
# --------------------------------------------------------------------------

def resolve_store() -> Path | None:
    """Resolve the H4 store, worktree-aware. Env override > worktree > primary."""
    candidates: list[Path] = []
    env = os.environ.get("CAMPAIGN_027_STORE") or os.environ.get("CAMPAIGN_STORE")
    if env:
        candidates.append(Path(env))
    candidates.append(ROOT / "data/campaign_002.sqlite3")
    # primary checkout (worktrees live under <primary>/.claude/worktrees/<name>)
    candidates.append(ROOT.parents[2] / "data/campaign_002.sqlite3")
    for c in candidates:
        if c.is_file():
            return c
    return None


def display_store(store: Path) -> str:
    """A portable, repo-relative store label (avoids committing absolute home
    paths). Falls back to the basename if the store is not under a repo root."""
    for base in (ROOT, ROOT.parents[2]):
        try:
            return str(store.relative_to(base))
        except ValueError:
            continue
    return store.name


def load_h4_frame(db_path: Path, instrument: str) -> pd.DataFrame:
    """Completed H4 candles for one instrument; UTC-indexed mid OHLC."""
    query = (
        "SELECT time, bid_o, bid_h, bid_l, bid_c, ask_o, ask_h, ask_l, ask_c, volume "
        "FROM candles WHERE instrument = ? AND granularity = 'H4' AND complete = 1 "
        "ORDER BY time ASC"
    )
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
        df = pd.read_sql_query(query, conn, params=[instrument])
    if df.empty:
        return df
    df["time"] = pd.to_datetime(df["time"], utc=True)
    for col in _BIDASK:
        df[col] = df[col].astype(float)
    df = df.sort_values("time").drop_duplicates("time", keep="last").set_index("time")
    df["open"] = (df["bid_o"] + df["ask_o"]) / 2.0
    df["high"] = (df["bid_h"] + df["ask_h"]) / 2.0
    df["low"] = (df["bid_l"] + df["ask_l"]) / 2.0
    df["close"] = (df["bid_c"] + df["ask_c"]) / 2.0
    return df[["open", "high", "low", "close", "volume"]]


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def _write(name: str, payload: Any) -> Path:
    OUT_PREFLIGHT.mkdir(parents=True, exist_ok=True)
    path = OUT_PREFLIGHT / name
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    return path


def _run_manifest(mode: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = {
        "campaign_id": "CAMPAIGN_027",
        "strategy_name": EXPECTED_STRATEGY,
        "version": "0.1.0-c027",
        "mode": mode,
        "scaffold_only": True,
        "not_approved": True,
        "strategy_evidence": False,
        "diagnostic_only": True,
        "test_lockbox_opened": False,
        "full_evidence_run": False,
        "fill_timing": "next_bar_open",
        "checked_at_utc": datetime.now(UTC).isoformat(),
    }
    if extra:
        manifest.update(extra)
    return manifest


# --------------------------------------------------------------------------
# Modes
# --------------------------------------------------------------------------

def preflight(settings: Settings, raw: dict[str, Any]) -> dict[str, Any]:
    strategy = H4FilteredZscoreReversionStrategy()
    blocked: list[str] = []
    try:
        assert_execution_metadata(raw)
        assert_registry_empty()
    except SystemExit as exc:
        blocked.append(str(exc))

    result: dict[str, Any] = {
        "campaign_id": "CAMPAIGN_027",
        "strategy_name": EXPECTED_STRATEGY,
        "version": "0.1.0-c027",
        "not_approved": True,
        "strategy_evidence": False,
        "fill_timing": "next_bar_open",
        "warmup_bars_required": strategy.warmup_bars_required(),
        "pairs": list(settings.market.instruments),
        "checked_at_utc": datetime.now(UTC).isoformat(),
    }
    store = resolve_store()
    coverage: dict[str, Any] = {}
    if store is None:
        blocked.append("BLOCKED_DATA_PRECONDITION: H4 store campaign_002.sqlite3 not found")
    else:
        result["store"] = display_store(store)
        warmup = strategy.warmup_bars_required()
        for pair in settings.market.instruments:
            try:
                df = load_h4_frame(store, pair)
            except Exception as exc:  # pragma: no cover - defensive
                coverage[pair] = {"status": "ERROR", "reason": str(exc)}
                blocked.append(f"BLOCKED_DATA_PRECONDITION: {pair}: {exc}")
                continue
            n = len(df)
            cov = {
                "bars": n,
                "min_time": str(df.index.min()) if n else None,
                "max_time": str(df.index.max()) if n else None,
                "warmup_ok": n >= warmup,
                "status": "PASS" if n >= warmup else "INSUFFICIENT_WARMUP",
            }
            coverage[pair] = cov
            if cov["status"] != "PASS":
                blocked.append(f"BLOCKED_DATA_PRECONDITION: {pair} {cov['status']}")
    result["pair_coverage"] = coverage
    result["blocked_reasons"] = blocked
    result["preflight_ok"] = not blocked
    return result


def data_feature_preflight(settings: Settings, raw: dict[str, Any]) -> dict[str, Any]:
    assert_execution_metadata(raw)
    assert_registry_empty()
    train_start, train_end = SPLITS["train"]
    assert_not_test_window(train_start, train_end)
    cfg = settings.strategy.h4_filtered_zscore_reversion.model_dump()
    store = resolve_store()
    report: dict[str, Any] = {
        "campaign_id": "CAMPAIGN_027",
        "strategy_evidence": False,
        "diagnostic_only": True,
        "window": [train_start, train_end],
        "no_lookahead": "zscore mean/std and atr percentile are .shift(1)",
        "pairs": {},
        "checked_at_utc": datetime.now(UTC).isoformat(),
    }
    if store is None:
        report["status"] = "BLOCKED_DATA_PRECONDITION"
        report["reason"] = "H4 store not found"
        report["preflight_ok"] = False
        return report
    report["store"] = display_store(store)
    ts = pd.Timestamp(train_start, tz="UTC")
    te = pd.Timestamp(train_end, tz="UTC") + pd.Timedelta(hours=23, minutes=59)
    ok = True
    for pair in settings.market.instruments:
        df = load_h4_frame(store, pair)
        win = df[(df.index >= ts) & (df.index <= te)]
        # features computable if the decision computes (needs warmup); evaluate on
        # the LAST bar of the train window using the full pre-window history.
        upto = df[df.index <= te]
        decision = compute_decision(upto, cfg) if len(upto) else None
        feat_ok = decision is not None
        report["pairs"][pair] = {
            "train_window_bars": len(win),
            "history_bars_through_window": len(upto),
            "features_computable": feat_ok,
            "last_window_zscore": round(decision.zscore, 4) if decision else None,
            "last_window_atr_percentile": round(decision.atr_percentile, 4) if decision else None,
            "last_window_session": decision.session_bucket if decision else None,
            "status": "PASS" if feat_ok else "INSUFFICIENT_WARMUP",
        }
        ok = ok and feat_ok
    report["preflight_ok"] = ok
    return report


def sample_signals(
    settings: Settings, raw: dict[str, Any], *, pair: str, start: str, sample_bars: int
) -> dict[str, Any]:
    """Tiny bounded probe: count signals over a small bounded window. No evidence."""
    assert_execution_metadata(raw)
    assert_registry_empty()
    out: dict[str, Any] = {
        "campaign_id": "CAMPAIGN_027",
        "pair": pair,
        "window_start": start,
        "sample_bars": sample_bars,
        "scaffold_only": True,
        "diagnostic_only": True,
        "full_evidence_run": False,
        "note": "signal counts only — NOT trades, NOT evidence; long counts are diagnostic-only and never entered",
    }
    store = resolve_store()
    if store is None:
        out["status"] = "BLOCKED_DATA_PRECONDITION"
        out["reason"] = "H4 store not found"
        return out
    cfg = settings.strategy.h4_filtered_zscore_reversion.model_dump()
    strategy = H4FilteredZscoreReversionStrategy()
    df = load_h4_frame(store, pair)
    start_ts = pd.Timestamp(start, tz="UTC")
    # bound: a small window starting at `start`, capped at `sample_bars` bars,
    # never crossing into the test lockbox.
    win = df[df.index >= start_ts].head(max(1, sample_bars))
    if win.empty:
        out["status"] = "BLOCKED_DATA_PRECONDITION"
        out["reason"] = f"no H4 bars at/after {start}"
        return out
    win_end = str(win.index.max().date())
    assert_not_test_window(str(win.index.min().date()), win_end)

    warmup = strategy.warmup_bars_required()
    evaluated = short_entries = long_diag = strong = low_vol = quiet = 0
    for end_ts in win.index:
        slice_df = df[df.index <= end_ts]
        if len(slice_df) < warmup:
            continue
        decision = compute_decision(slice_df, cfg)
        if decision is None:
            continue
        evaluated += 1
        strong += int(decision.f_strong_extension)
        low_vol += int(decision.f_low_vol)
        quiet += int(decision.f_quiet_session)
        if decision.entered_short:
            short_entries += 1
        elif decision.raw_side == "long" and decision.f_strong_extension and decision.f_low_vol and decision.f_quiet_session:
            long_diag += 1  # would-be long under the same filters — DIAGNOSTIC ONLY
    out.update({
        "status": "OK",
        "window_end": win_end,
        "evaluated_decisions": evaluated,
        "short_entries": short_entries,
        "long_diagnostic_only_not_entered": long_diag,
        "f_strong_extension_pass": strong,
        "f_low_vol_pass": low_vol,
        "f_quiet_session_pass": quiet,
    })
    return out


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

_FORBIDDEN = ("--train", "--validation", "--test", "--backtest", "--execute")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    for bad in _FORBIDDEN:
        if bad in argv:
            raise SystemExit(
                f"REFUSED: {bad} is not available in the CAMPAIGN_027 scaffold sprint "
                "— no train/validation/test/backtest/execute evidence; lockbox stays closed."
            )
    parser = argparse.ArgumentParser(description="CAMPAIGN_027 scaffold runner (preflight only)")
    parser.add_argument("--validate-config", action="store_true")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--data-feature-preflight", action="store_true")
    parser.add_argument("--sample-signals-only", action="store_true")
    parser.add_argument("--sample-pair", default="EUR_USD")
    parser.add_argument("--sample-start", default="2021-01-01")
    parser.add_argument("--sample-bars", type=int, default=300)
    args = parser.parse_args(argv)
    settings, raw = load_settings()

    if args.validate_config:
        validate_frozen_config(settings, raw)
        print(f"[CAMPAIGN_027] config OK — {EXPECTED_STRATEGY} 0.1.0-c027")
        return 0

    if args.preflight_only:
        pf = preflight(settings, raw)
        _write("preflight_result.json", pf)
        _write("pair_coverage_summary.json",
               {"campaign_id": "CAMPAIGN_027", "pair_coverage": pf.get("pair_coverage", {})})
        _write("run_manifest.json", _run_manifest("preflight-only", {"preflight_ok": pf["preflight_ok"]}))
        print(json.dumps(pf, indent=2, sort_keys=True, default=str))
        return 0 if pf["preflight_ok"] else 1

    if args.data_feature_preflight:
        report = data_feature_preflight(settings, raw)
        _write("data_feature_preflight.json", report)
        _write("run_manifest.json", _run_manifest("data-feature-preflight",
                                                   {"preflight_ok": report.get("preflight_ok", False)}))
        print(json.dumps(report, indent=2, sort_keys=True, default=str))
        return 0 if report.get("preflight_ok") else 1

    if args.sample_signals_only:
        summary = sample_signals(settings, raw, pair=args.sample_pair,
                                 start=args.sample_start, sample_bars=args.sample_bars)
        _write("sample_signal_summary.json", summary)
        _write("run_manifest.json", _run_manifest("sample-signals-only",
                                                   {"sample_status": summary.get("status")}))
        print(json.dumps(summary, indent=2, sort_keys=True, default=str))
        return 0 if summary.get("status") in ("OK", "BLOCKED_DATA_PRECONDITION") else 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
