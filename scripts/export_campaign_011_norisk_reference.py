#!/usr/bin/env python3
"""Export the canonical no-RiskEngine bespoke reference for CAMPAIGN_011.

Produces a hash-pinned full-window reference plus an informational
per-fold rollup for `random_entry_anchor 0.1.0-c011` (CAMPAIGN_011)
using the **already-frozen** strategy module and config. Runs the
bespoke `BacktestEngine` with `risk_engine=None` (the spread / session
/ loss-limit gates are silenced; the strategy's own R1-R8 logic and
the 6-bar time stop remain in force).

**This script does not approve a strategy and does not change any
verdict.** CAMPAIGN_011 remains REJECT / null diagnostic anchor by
design. `configs/approved_strategies.yaml` is not touched. The
master_seed is frozen at 20260523 and verified pre-run; mismatch
aborts before any backtest fires.

Read-only data: it reads `data/campaign_002.sqlite3` only, makes no
OANDA call, and writes only compact reference JSONs plus an optional
Markdown summary. Large trade-level outputs are NOT written by default
and must opt in via ``--trades-out``; the destination should be under
``backtests/diagnostics/campaign_011_norisk/`` which is gitignored.

See:
- ``docs/research/CAMPAIGN_011_NORISK_REFERENCE_001_PLAN.md``
- ``docs/research/CAMPAIGN_011_NORISK_REFERENCE_CONTRACT.md``
- ``docs/research/CAMPAIGN_011_NORISK_REFERENCE_RUNNER.md``
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from forex_bot.backtesting.engine import BacktestEngine, compute_data_request_hash
from forex_bot.backtesting.fills import FillModel
from forex_bot.backtesting.metrics import TradeRecord
from forex_bot.config import load_settings
from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo, DataSourceRepo, InstrumentRepo
from forex_bot.domain.candles import CandleFrame
from forex_bot.strategies.random_entry_anchor import RandomEntryAnchorStrategy

# isort: off
from research.walk_forward import Fold, WalkForwardPlan
# isort: on

CANONICAL_PAIRS: tuple[str, ...] = (
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
)
REQUIRED_DATA_SOURCE = "oanda-practice"
EXPECTED_STRATEGY = "random_entry_anchor"
EXPECTED_VERSION = "0.1.0-c011"
EXPECTED_MASTER_SEED = 20260523

# Window matches CAMPAIGN_002 no-RiskEngine reference (sprint
# infra-lean-parity-001 + sprint 003). Inclusive UTC.
WINDOW_FROM = "2020-01-01"
WINDOW_TO = "2026-05-20"

# Frozen parameters (verbatim from CAMPAIGN_011_PRECOMMIT_CHECKLIST.md
# §5). Any mismatch aborts the run.
FROZEN_PARAMETERS: dict[str, Any] = {
    "version": EXPECTED_VERSION,
    "timeframe": "H4",
    "master_seed": EXPECTED_MASTER_SEED,
    "entry_probability_per_bar": 0.05,
    "atr_lookback": 14,
    "atr_stop_multiple": 2.0,
    "trailing_stop_atr_multiple": None,
    "max_bars_in_trade": 6,
    "min_atr_pips": {},
}

DEFAULT_CONFIG = ROOT / "configs" / "campaign_011_random_entry_anchor.yaml"
DEFAULT_DB = ROOT / "data" / "campaign_002.sqlite3"
DEFAULT_OUT = ROOT / "research" / "lean_parity" / "campaign_011_h4_bespoke_reference.json"
DEFAULT_PER_FOLD_OUT = (
    ROOT
    / "research"
    / "lean_parity"
    / "campaign_011_h4_bespoke_reference_per_fold.json"
)
DEFAULT_DIAG_OUT = (
    ROOT / "backtests" / "diagnostics" / "custom_campaign_011_h4_parity_norisk.md"
)
DEFAULT_PLAN_PATH = (
    ROOT
    / "backtests"
    / "CAMPAIGN_011_random_entry_anchor"
    / "walk_forward"
    / "plan.json"
)


# ---------------------------------------------------------------------------
# Frozen-parameter enforcement (mirrors scripts/run_campaign_011.py)


def _assert_frozen(strategy_cfg: dict[str, Any]) -> None:
    """Fail-closed if the loaded YAML deviates from the pre-commit."""
    mismatched: list[str] = []
    for key, expected in FROZEN_PARAMETERS.items():
        got = strategy_cfg.get(key)
        if isinstance(expected, dict) and isinstance(got, dict):
            if got != expected:
                mismatched.append(f"  {key}: got {got!r}, expected {expected!r}")
        elif got != expected:
            mismatched.append(f"  {key}: got {got!r}, expected {expected!r}")
    if mismatched:
        raise SystemExit(
            "CAMPAIGN_011 frozen-parameter mismatch — see "
            "CAMPAIGN_011_PRECOMMIT_CHECKLIST.md §5:\n" + "\n".join(mismatched)
        )
    if int(strategy_cfg.get("master_seed", -1)) != EXPECTED_MASTER_SEED:
        raise SystemExit(
            f"CAMPAIGN_011 master_seed must be {EXPECTED_MASTER_SEED}; "
            f"got {strategy_cfg.get('master_seed')!r}. Seed tuning is "
            "forbidden — this is a null model anchor."
        )


# ---------------------------------------------------------------------------
# Per-window engine invocation


@dataclass
class PairWindowResult:
    instrument: str
    candle_count: int
    first_ts: str | None
    last_ts: str | None
    data_request_hash: str
    trade_count: int
    expectancy_r: float
    return_pct: float
    profit_factor: float | None
    win_rate: float
    max_drawdown_pct: float
    config_hash: str
    long_trades: int
    short_trades: int
    starting_equity: float
    final_equity: float
    trades: list[TradeRecord]


def _build_engine(
    *,
    settings: Any,
    instrument_meta: Any,
    strategy_cfg: dict[str, Any],
) -> BacktestEngine:
    return BacktestEngine(
        instrument=instrument_meta,
        strategy=RandomEntryAnchorStrategy(version=strategy_cfg["version"]),
        strategy_config=strategy_cfg,
        fill_model=FillModel(
            fixed_slippage_pips=Decimal(str(settings.backtest.fixed_slippage_pips)),
            spread_slippage_multiplier=Decimal(
                str(settings.backtest.spread_slippage_multiplier)
            ),
        ),
        fill_timing="signal_bar_close",
        starting_equity=Decimal(str(settings.backtest.starting_equity_usd)),
        account_currency=settings.market.account_currency,
        risk_per_trade_pct=Decimal(str(settings.risk.risk_per_trade_pct)),
        max_bars_in_trade=int(strategy_cfg["max_bars_in_trade"]),
        commission_per_unit=Decimal(str(settings.backtest.commission_per_unit)),
        trailing_stop_atr_multiple=strategy_cfg.get("trailing_stop_atr_multiple"),
        atr_lookback=int(strategy_cfg["atr_lookback"]),
        risk_engine=None,
        settings=settings,
    )


def _run_window(
    *,
    settings: Any,
    instrument: str,
    from_dt: datetime,
    to_dt: datetime,
    candle_repo: CandleRepo,
    instrument_repo: InstrumentRepo,
    ds_repo: DataSourceRepo,
    strategy_cfg: dict[str, Any],
) -> PairWindowResult | None:
    """Run the strategy in no-RiskEngine mode for one (pair, window)."""
    meta = instrument_repo.get(instrument)
    if meta is None:
        raise SystemExit(
            f"missing instrument metadata for {instrument} in the DB"
        )
    latest = ds_repo.latest_for(instrument, "H4") or {}
    src = latest.get("source", "unknown")
    if src != REQUIRED_DATA_SOURCE:
        raise SystemExit(
            f"data source for {instrument} H4 is {src!r}, expected "
            f"{REQUIRED_DATA_SOURCE!r}. CAMPAIGN_011 reference aborts."
        )
    rows = candle_repo.list(
        instrument,
        "H4",
        completed_only=True,
        from_time=from_dt,
        to_time=to_dt,
    )
    if not rows:
        return None
    frame = CandleFrame.from_candles(instrument, "H4", rows)
    data_hash = compute_data_request_hash(
        instrument=instrument,
        granularity="H4",
        from_time=from_dt.isoformat(),
        to_time=to_dt.isoformat(),
        source=src,
        candle_count=len(rows),
    )
    engine = _build_engine(
        settings=settings, instrument_meta=meta, strategy_cfg=strategy_cfg
    )
    result = engine.run(frame, data_request_hash=data_hash)
    m = result.metrics
    long_trades = sum(1 for t in result.trades if t.side == "long")
    short_trades = sum(1 for t in result.trades if t.side == "short")
    return PairWindowResult(
        instrument=instrument,
        candle_count=len(rows),
        first_ts=rows[0].time.isoformat(),
        last_ts=rows[-1].time.isoformat(),
        data_request_hash=data_hash,
        trade_count=m.trade_count,
        expectancy_r=float(m.expectancy_r),
        return_pct=float(m.total_return_pct),
        profit_factor=(
            None if m.profit_factor == float("inf") else float(m.profit_factor)
        ),
        win_rate=float(m.win_rate),
        max_drawdown_pct=float(m.max_drawdown_pct),
        config_hash=result.config_hash,
        long_trades=long_trades,
        short_trades=short_trades,
        starting_equity=float(m.starting_equity),
        final_equity=float(m.final_equity),
        trades=list(result.trades),
    )


# ---------------------------------------------------------------------------
# JSON serialization


def _round_or_none(value: float | None, places: int) -> float | None:
    if value is None:
        return None
    return round(value, places)


def _pair_json(p: PairWindowResult) -> dict[str, Any]:
    return {
        "instrument": p.instrument,
        "candle_count": p.candle_count,
        "trades": p.trade_count,
        "expectancy_r": round(p.expectancy_r, 4),
        "return_pct": round(p.return_pct, 4),
        "profit_factor": _round_or_none(p.profit_factor, 4),
        "win_rate": round(p.win_rate, 4),
        "max_drawdown_pct": round(p.max_drawdown_pct, 4),
    }


def _fold_pair_json(p: PairWindowResult) -> dict[str, Any]:
    # Per-fold per-pair has fewer fields — drops candle_count + drawdown
    # because the per-fold rollup is informational; the full-window
    # numbers are the canonical comparison target.
    return {
        "instrument": p.instrument,
        "trades": p.trade_count,
        "expectancy_r": round(p.expectancy_r, 4),
        "return_pct": round(p.return_pct, 4),
        "profit_factor": _round_or_none(p.profit_factor, 4),
        "win_rate": round(p.win_rate, 4),
    }


def _aggregate_fold(
    pair_runs: list[PairWindowResult],
) -> tuple[int, float, float, float | None]:
    total = sum(p.trade_count for p in pair_runs)
    if total == 0:
        return 0, 0.0, 0.0, None
    expectancy = (
        sum(p.expectancy_r * p.trade_count for p in pair_runs) / total
    )
    ret = sum(p.return_pct for p in pair_runs)
    gains = sum(p.return_pct for p in pair_runs if p.return_pct > 0)
    losses = -sum(p.return_pct for p in pair_runs if p.return_pct < 0)
    pf: float | None
    if losses == 0:
        pf = None if gains > 0 else 0.0
    else:
        pf = gains / losses
    return total, expectancy, ret, pf


# ---------------------------------------------------------------------------
# Diagnostics MD


def _render_diagnostics_md(
    *,
    pair_results: list[PairWindowResult],
    config_hash: str,
    db_display: str,
    generated_at: datetime,
) -> str:
    total_trades = sum(p.trade_count for p in pair_results)
    lines: list[str] = [
        "# Custom-engine CAMPAIGN_011 H4 parity reproduction (no-RiskEngine)",
        "",
        f"**Generated:** {generated_at.isoformat()} · "
        f"**Branch:** `infra-bespoke-campaign-011-norisk-reference-001`",
        "",
        "> **DIAGNOSTIC / PARITY REPRODUCTION — NOT A NEW VERDICT.** This "
        "runs `random_entry_anchor 0.1.0-c011` (CAMPAIGN_011) on the "
        "bespoke engine with `risk_engine=None` so the future Backtrader "
        "CAMPAIGN_011 comparison sprint has a canonical, no-gates "
        "reference to compare against. CAMPAIGN_011 is a null model by "
        "construction; it remains **REJECT / null diagnostic anchor by "
        "design**. `configs/approved_strategies.yaml` is not touched. "
        "`strategy_evidence: false`.",
        "",
        "## Run parameters",
        "",
        "| field | value |",
        "|---|---|",
        "| strategy | `random_entry_anchor 0.1.0-c011` |",
        "| master_seed | `20260523` (frozen, no seed sweep) |",
        f"| config hash | `{config_hash[:16]}…` |",
        "| fill timing | `signal_bar_close` |",
        "| risk engine | **not wired** (`risk_engine=None`) — "
        "strategy + engine mechanics only |",
        "| cost model | 0.2 pip fixed slippage + 0.5× spread, "
        "0.0 commission/unit |",
        f"| window | {WINDOW_FROM} → {WINDOW_TO} (full split) |",
        f"| data store | `{db_display}` (gitignored) |",
        "",
        "## Full-window results (bespoke engine, no RiskEngine)",
        "",
        "| instrument | candles | trades | expectancy R | return % "
        "| profit factor | win % | max DD % |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for p in pair_results:
        pf_str = (
            "inf" if p.profit_factor is None else f"{p.profit_factor:.2f}"
        )
        lines.append(
            f"| {p.instrument} | {p.candle_count} | {p.trade_count} | "
            f"{p.expectancy_r:.4f} | {p.return_pct:.2f} | "
            f"{pf_str} | {p.win_rate * 100:.1f} | "
            f"{p.max_drawdown_pct:.2f} |"
        )
    lines += [
        "",
        f"**Total trades across the seven pairs (no RiskEngine): "
        f"{total_trades}.**",
        "",
        "## What this establishes",
        "",
        "- A reproducible, hash-pinned no-RiskEngine bespoke reference "
        "for CAMPAIGN_011 / `random_entry_anchor`, suitable for the "
        "future Backtrader CAMPAIGN_011 comparison sprint.",
        "- It does **not** establish, measure, or imply any strategy "
        "edge. CAMPAIGN_011 is a null model by construction; the "
        "no-RiskEngine path silences spread / session / loss-limit "
        "gates, which by itself produces more trades but no edge.",
        "- `configs/approved_strategies.yaml` is not touched. "
        "CAMPAIGN_011 cannot be approved by design.",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Optional trade dump


def _serialize_trade(t: TradeRecord) -> dict[str, Any]:
    """Serialize a TradeRecord to a JSONL-friendly dict."""
    data: dict[str, Any] = {}
    for field_name in (
        "signal_id",
        "instrument",
        "side",
        "entry_time",
        "exit_time",
        "entry_price",
        "exit_price",
        "stop_price",
        "units",
        "pnl_home",
        "r_multiple",
        "bars_held",
        "exit_reason",
    ):
        if hasattr(t, field_name):
            value = getattr(t, field_name)
            if isinstance(value, Decimal):
                data[field_name] = str(value)
            elif isinstance(value, datetime):
                data[field_name] = value.isoformat()
            else:
                data[field_name] = value
    return data


def _write_trade_dump(
    *,
    full_window_results: list[PairWindowResult],
    per_fold_results: list[tuple[Fold, list[PairWindowResult]]],
    trades_out: Path,
) -> None:
    trades_out.mkdir(parents=True, exist_ok=True)
    # Full-window
    fw_path = trades_out / "full_window_trades.jsonl"
    with fw_path.open("w", encoding="utf-8") as f:
        for p in full_window_results:
            for t in sorted(
                p.trades,
                key=lambda x: (
                    getattr(x, "entry_time", datetime(1970, 1, 1, tzinfo=UTC)),
                    getattr(x, "signal_id", ""),
                ),
            ):
                row = _serialize_trade(t)
                row["instrument"] = p.instrument
                f.write(json.dumps(row, default=str, sort_keys=True))
                f.write("\n")
    # Per-fold per-pair
    folds_dir = trades_out / "folds"
    folds_dir.mkdir(parents=True, exist_ok=True)
    for fold, pair_runs in per_fold_results:
        fp = folds_dir / f"fold_{fold.fold_index:02d}_trades.jsonl"
        with fp.open("w", encoding="utf-8") as f:
            for p in pair_runs:
                for t in sorted(
                    p.trades,
                    key=lambda x: (
                        getattr(x, "entry_time", datetime(1970, 1, 1, tzinfo=UTC)),
                        getattr(x, "signal_id", ""),
                    ),
                ):
                    row = _serialize_trade(t)
                    row["instrument"] = p.instrument
                    row["fold_index"] = fold.fold_index
                    f.write(json.dumps(row, default=str, sort_keys=True))
                    f.write("\n")


# ---------------------------------------------------------------------------
# CLI


def _fold_to_utc_window(fold: Fold) -> tuple[datetime, datetime]:
    """Match scripts/run_campaign_011.py:_fold_dates_to_dts inclusive
    semantics so the per-fold rollup is comparable to the published
    walk-forward fold detail."""
    start = datetime.combine(fold.test_start, datetime.min.time(), tzinfo=UTC)
    end = datetime.combine(
        fold.test_end, datetime.max.time().replace(microsecond=0), tzinfo=UTC
    )
    return start, end


def _build_full_window_reference(
    *,
    pair_results: list[PairWindowResult],
    config_hash: str,
) -> dict[str, Any]:
    total = sum(p.trade_count for p in pair_results)
    return {
        "parity_target": (
            "CAMPAIGN_011 H4 random_entry_anchor null-model baseline"
        ),
        "risk_engine_used": False,
        "fill_timing": "signal_bar_close",
        "window": [WINDOW_FROM, WINDOW_TO],
        "master_seed": EXPECTED_MASTER_SEED,
        "config_hash": config_hash,
        "data_request_hashes": {
            p.instrument: p.data_request_hash for p in pair_results
        },
        "strategy_evidence": False,
        "approval_path": "none (null model by design)",
        "total_trades": total,
        "pairs": [_pair_json(p) for p in pair_results],
    }


def _build_per_fold_reference(
    *,
    per_fold_results: list[tuple[Fold, list[PairWindowResult]]],
    plan: WalkForwardPlan,
    plan_source: str,
    config_hash: str,
) -> dict[str, Any]:
    folds_payload: list[dict[str, Any]] = []
    for fold, pair_runs in per_fold_results:
        total, expectancy, ret, pf = _aggregate_fold(pair_runs)
        folds_payload.append(
            {
                "fold_index": fold.fold_index,
                "test_start": str(fold.test_start),
                "test_end": str(fold.test_end),
                "total_trades": total,
                "expectancy_r": round(expectancy, 4),
                "return_pct": round(ret, 4),
                "profit_factor": _round_or_none(pf, 4),
                "pairs": [_fold_pair_json(p) for p in pair_runs],
            }
        )
    return {
        "parity_target": (
            "CAMPAIGN_011 H4 random_entry_anchor null-model baseline (per-fold)"
        ),
        "risk_engine_used": False,
        "fill_timing": "signal_bar_close",
        "master_seed": EXPECTED_MASTER_SEED,
        "config_hash": config_hash,
        "strategy_evidence": False,
        "approval_path": "none (null model by design)",
        "plan_source": plan_source,
        "fold_count": len(plan.folds),
        "folds": folds_payload,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Export the canonical no-RiskEngine bespoke reference for "
            "CAMPAIGN_011. Reads local SQLite only; no OANDA call. "
            "Does not approve any strategy. CAMPAIGN_011 remains REJECT."
        )
    )
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--per-fold-out", default=str(DEFAULT_PER_FOLD_OUT))
    ap.add_argument("--diagnostics-md", default=str(DEFAULT_DIAG_OUT))
    ap.add_argument("--plan", default=str(DEFAULT_PLAN_PATH))
    ap.add_argument(
        "--trades-out",
        default=None,
        help=(
            "Optional output dir for full trade dumps (JSONL). Large. "
            "Should be under backtests/diagnostics/campaign_011_norisk/ "
            "which must be gitignored. Omit to skip."
        ),
    )
    ap.add_argument(
        "--full-window-only",
        action="store_true",
        help=(
            "Skip the per-fold rollup. Used by the determinism check "
            "to keep both runs fast."
        ),
    )
    args = ap.parse_args(argv)

    config_path = Path(args.config)
    db_path = Path(args.db)
    out_path = Path(args.out)
    per_fold_out_path = Path(args.per_fold_out)
    diag_md_path = Path(args.diagnostics_md)
    plan_path = Path(args.plan)

    if not db_path.exists():
        print(
            f"BLOCKER: no H4 SQLite store at {db_path}. "
            "Restore data/campaign_002.sqlite3 or pass a different --db.",
            file=sys.stderr,
        )
        return 1

    settings = load_settings(config_path)
    sc = settings.strategy
    if sc.enabled != [EXPECTED_STRATEGY] or sc.random_entry_anchor is None:
        raise SystemExit(
            f"CAMPAIGN_011 config must enable only {EXPECTED_STRATEGY!r}; "
            f"got {sc.enabled}"
        )
    strategy_cfg = sc.random_entry_anchor.model_dump()
    _assert_frozen(strategy_cfg)
    if tuple(settings.market.instruments) != CANONICAL_PAIRS:
        raise SystemExit(
            f"CAMPAIGN_011 universe mismatch — got "
            f"{tuple(settings.market.instruments)}, expected {CANONICAL_PAIRS}"
        )

    db = Database(db_path)
    candle_repo = CandleRepo(db)
    instr_repo = InstrumentRepo(db)
    ds_repo = DataSourceRepo(db)

    # --- Full-window pass -------------------------------------------------
    from_dt = datetime.fromisoformat(WINDOW_FROM).replace(tzinfo=UTC)
    to_dt = datetime.fromisoformat(WINDOW_TO).replace(tzinfo=UTC)
    full_results: list[PairWindowResult] = []
    print(
        f"=== CAMPAIGN_011 no-RiskEngine reference "
        f"started {datetime.now(UTC).isoformat()} ==="
    )
    print(f"full-window: {WINDOW_FROM} .. {WINDOW_TO}")
    print(f"master_seed: {strategy_cfg['master_seed']}")
    for pair in CANONICAL_PAIRS:
        res = _run_window(
            settings=settings,
            instrument=pair,
            from_dt=from_dt,
            to_dt=to_dt,
            candle_repo=candle_repo,
            instrument_repo=instr_repo,
            ds_repo=ds_repo,
            strategy_cfg=strategy_cfg,
        )
        if res is None:
            print(
                f"BLOCKER: no H4 candles for {pair} in the store "
                f"between {WINDOW_FROM} and {WINDOW_TO}.",
                file=sys.stderr,
            )
            return 1
        full_results.append(res)
        print(
            f"  full-window {pair}: trades={res.trade_count} "
            f"expectancy_r={res.expectancy_r:+.4f} "
            f"return_pct={res.return_pct:+.2f}%"
        )

    config_hash = full_results[0].config_hash

    # --- Per-fold pass ----------------------------------------------------
    per_fold_results: list[tuple[Fold, list[PairWindowResult]]] = []
    plan: WalkForwardPlan | None = None
    if not args.full_window_only:
        if not plan_path.exists():
            raise SystemExit(
                f"plan file not found: {plan_path}. Pass --plan or "
                "--full-window-only."
            )
        plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
        plan = WalkForwardPlan(**plan_payload)
        for fold in plan.folds:
            f_from, f_to = _fold_to_utc_window(fold)
            pair_runs: list[PairWindowResult] = []
            for pair in CANONICAL_PAIRS:
                res = _run_window(
                    settings=settings,
                    instrument=pair,
                    from_dt=f_from,
                    to_dt=f_to,
                    candle_repo=candle_repo,
                    instrument_repo=instr_repo,
                    ds_repo=ds_repo,
                    strategy_cfg=strategy_cfg,
                )
                if res is None:
                    raise SystemExit(
                        f"no candles for {pair} fold={fold.fold_index} "
                        f"test_window {fold.test_start}..{fold.test_end}"
                    )
                pair_runs.append(res)
            per_fold_results.append((fold, pair_runs))
            total, expectancy, ret, _pf = _aggregate_fold(pair_runs)
            print(
                f"  fold {fold.fold_index:>2d} "
                f"[{fold.test_start}..{fold.test_end}]: "
                f"trades={total} expectancy_r={expectancy:+.4f} "
                f"return_pct={ret:+.2f}%"
            )

    # --- Write outputs ----------------------------------------------------
    fw_payload = _build_full_window_reference(
        pair_results=full_results, config_hash=config_hash
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(fw_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote full-window reference → {out_path}")

    if per_fold_results and plan is not None:
        pf_payload = _build_per_fold_reference(
            per_fold_results=per_fold_results,
            plan=plan,
            plan_source=str(
                plan_path.resolve().relative_to(ROOT)
                if plan_path.resolve().is_relative_to(ROOT)
                else plan_path
            ),
            config_hash=config_hash,
        )
        per_fold_out_path.parent.mkdir(parents=True, exist_ok=True)
        per_fold_out_path.write_text(
            json.dumps(pf_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote per-fold rollup → {per_fold_out_path}")

    try:
        db_display = str(db_path.resolve().relative_to(ROOT))
    except ValueError:
        db_display = str(db_path)
    diag_md = _render_diagnostics_md(
        pair_results=full_results,
        config_hash=config_hash,
        db_display=db_display,
        generated_at=datetime.now(UTC),
    )
    diag_md_path.parent.mkdir(parents=True, exist_ok=True)
    diag_md_path.write_text(diag_md, encoding="utf-8")
    print(f"wrote diagnostics markdown → {diag_md_path}")

    if args.trades_out:
        trades_out = Path(args.trades_out)
        _write_trade_dump(
            full_window_results=full_results,
            per_fold_results=per_fold_results,
            trades_out=trades_out,
        )
        print(f"wrote optional trade dump → {trades_out}")

    total_trades = fw_payload["total_trades"]
    print(
        f"\nCAMPAIGN_011 no-RiskEngine reference: "
        f"7 pairs, {total_trades} full-window trades. "
        f"Verdict unchanged — REJECT / null diagnostic anchor."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
