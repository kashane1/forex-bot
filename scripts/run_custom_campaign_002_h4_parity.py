#!/usr/bin/env python3
"""Custom-engine CAMPAIGN_002 H4 parity reproduction.

Re-runs the **already-REJECTED** CAMPAIGN_002 H4 `trend_following`
baseline on the local seven-pair real-OANDA H4 store, using the bespoke
backtest engine, the committed campaign config, and the same fill timing
CAMPAIGN_002 used (`signal_bar_close`). It exists so the custom engine's
side of the Lean parity comparison is reproducible and hash-pinned.

**This is not a new strategy campaign.** It is a parity reproduction of
a rejected baseline — `strategy_evidence: false`. It runs no new
hypothesis, sweeps no parameter, and produces no verdict: CAMPAIGN_002
stays REJECT regardless of the numbers here.

Read-only: it reads the local H4 store, makes no OANDA call, and writes
only a compact Markdown summary — no bulky trade/equity CSVs.

Usage:
    python scripts/run_custom_campaign_002_h4_parity.py
        [--db data/oanda_h4_research.sqlite3]
        [--config configs/campaign_002_real_oanda.yaml]
        [--out backtests/diagnostics/custom_campaign_002_h4_parity.md]

See docs/research/INFRA_LEAN_PARITY_001_PLAN.md.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.backtesting.engine import BacktestEngine, compute_data_request_hash
from forex_bot.backtesting.fills import FillModel
from forex_bot.config import load_settings
from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo
from forex_bot.domain.candles import CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.risk.policy import RiskEngine
from forex_bot.strategies.trend_following import TrendFollowingStrategy

PAIRS = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD"]
WINDOW_FROM = "2020-01-01"
WINDOW_TO = "2026-05-20"
DEFAULT_DB = ROOT / "data" / "oanda_h4_research.sqlite3"
DEFAULT_CONFIG = ROOT / "configs" / "campaign_002_real_oanda.yaml"
DEFAULT_OUT = ROOT / "backtests" / "diagnostics" / "custom_campaign_002_h4_parity.md"

# Verified instrument metadata — OANDA_INSTRUMENT_METADATA_AUDIT.md
# (oanda-practice-readonly-001 Phase 3). (pip_location, display_precision,
# margin_rate). margin_rate is broker/account-specific and informational.
_META: dict[str, tuple[int, int, str]] = {
    "EUR_USD": (-4, 5, "0.02"),
    "GBP_USD": (-4, 5, "0.05"),
    "USD_JPY": (-2, 3, "0.05"),
    "AUD_USD": (-4, 5, "0.03"),
    "USD_CAD": (-4, 5, "0.02"),
    "USD_CHF": (-4, 5, "0.03"),
    "NZD_USD": (-4, 5, "0.03"),
}

# Committed CAMPAIGN_002 H4 full-split, base-cost per-pair numbers, read
# from backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md. The reference the
# reproduction is compared against — NOT a target to hit.
CAMPAIGN_002_H4_REFERENCE: dict[str, dict[str, float]] = {
    "EUR_USD": {"trades": 132, "expectancy_r": -0.218, "return_pct": -7.04, "profit_factor": 0.55},
    "GBP_USD": {"trades": 198, "expectancy_r": -0.089, "return_pct": -4.40, "profit_factor": 0.79},
    "USD_JPY": {"trades": 217, "expectancy_r": -0.000, "return_pct": -0.54, "profit_factor": 0.98},
    "AUD_USD": {"trades": 144, "expectancy_r": -0.218, "return_pct": -7.64, "profit_factor": 0.56},
    "USD_CAD": {"trades": 122, "expectancy_r": -0.185, "return_pct": -7.19, "profit_factor": 0.51},
    "USD_CHF": {"trades": 181, "expectancy_r": -0.171, "return_pct": -6.91, "profit_factor": 0.65},
    "NZD_USD": {"trades": 38, "expectancy_r": -0.203, "return_pct": -1.95, "profit_factor": 0.53},
}
REFERENCE_TOTAL_TRADES = 1032


def make_instrument(name: str) -> Instrument:
    pip_location, display_precision, margin_rate = _META[name]
    return Instrument(
        name=name,
        type="CURRENCY",
        display_precision=display_precision,
        pip_location=pip_location,
        trade_units_precision=0,
        minimum_trade_size=Decimal("1"),
        maximum_order_units=Decimal("100000000"),
        margin_rate=Decimal(margin_rate),
    )


@dataclass
class PairResult:
    instrument: str
    candle_count: int
    first_ts: str | None
    last_ts: str | None
    data_request_hash: str
    trade_count: int
    expectancy_r: float
    total_return_pct: float
    profit_factor: float | None
    win_rate: float
    max_drawdown_pct: float
    rejected_signal_count: int


def baseline_params(settings: object) -> dict:
    """The CAMPAIGN_002 trend_following baseline parameters, from the
    committed campaign config."""
    cfg = settings.strategy.trend_following.model_dump()  # type: ignore[attr-defined]
    cfg["version"] = "0.1.0-baseline-frozen"
    return cfg


def run_pair(
    settings: object,
    risk_engine: RiskEngine,
    candle_repo: CandleRepo,
    *,
    instrument: str,
    from_dt: datetime,
    to_dt: datetime,
    source: str,
) -> PairResult | None:
    """Reproduce the CAMPAIGN_002 H4 baseline for one pair. Returns None
    if the store has no candles for it."""
    rows = candle_repo.list(
        instrument, "H4", completed_only=True, from_time=from_dt, to_time=to_dt
    )
    if not rows:
        return None
    frame = CandleFrame.from_candles(instrument, "H4", rows)
    data_hash = compute_data_request_hash(
        instrument=instrument,
        granularity="H4",
        from_time=from_dt.isoformat(),
        to_time=to_dt.isoformat(),
        source=source,
        candle_count=len(rows),
    )
    cfg = baseline_params(settings)
    fill_model = FillModel(
        fixed_slippage_pips=Decimal(str(settings.backtest.fixed_slippage_pips)),  # type: ignore[attr-defined]
        spread_slippage_multiplier=Decimal(
            str(settings.backtest.spread_slippage_multiplier)  # type: ignore[attr-defined]
        ),
    )
    engine = BacktestEngine(
        instrument=make_instrument(instrument),
        strategy=TrendFollowingStrategy(version=cfg["version"]),
        strategy_config=cfg,
        fill_model=fill_model,
        # CAMPAIGN_002 predates the fill-timing model — signal_bar_close.
        fill_timing="signal_bar_close",
        starting_equity=Decimal(str(settings.backtest.starting_equity_usd)),  # type: ignore[attr-defined]
        account_currency=settings.market.account_currency,  # type: ignore[attr-defined]
        risk_per_trade_pct=Decimal(str(settings.risk.risk_per_trade_pct)),  # type: ignore[attr-defined]
        max_bars_in_trade=int(cfg.get("max_bars_in_trade", 240)),
        commission_per_unit=Decimal(str(settings.backtest.commission_per_unit)),  # type: ignore[attr-defined]
        trailing_stop_atr_multiple=cfg.get("trailing_stop_atr_multiple"),
        atr_lookback=int(cfg.get("atr_lookback", 14)),
        risk_engine=risk_engine,
        settings=settings,  # type: ignore[arg-type]
    )
    result = engine.run(frame, data_request_hash=data_hash)
    m = result.metrics
    return PairResult(
        instrument=instrument,
        candle_count=len(rows),
        first_ts=rows[0].time.isoformat(),
        last_ts=rows[-1].time.isoformat(),
        data_request_hash=data_hash,
        trade_count=m.trade_count,
        expectancy_r=float(m.expectancy_r),
        total_return_pct=float(m.total_return_pct),
        profit_factor=(
            None if m.profit_factor == float("inf") else float(m.profit_factor)
        ),
        win_rate=float(m.win_rate),
        max_drawdown_pct=float(m.max_drawdown_pct),
        rejected_signal_count=len(result.rejected_signals),
    )


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------


def _delta(actual: float, reference: float) -> str:
    return f"{actual - reference:+.3f}"


def render_doc(
    results: list[PairResult],
    *,
    config_hash: str,
    generated_at: datetime,
    db_display: str,
) -> str:
    total_trades = sum(r.trade_count for r in results)
    lines: list[str] = [
        "# Custom-engine CAMPAIGN_002 H4 parity reproduction",
        "",
        f"**Generated:** {generated_at.isoformat()} · "
        f"**Branch:** `infra-lean-parity-001`",
        "",
        "> **DIAGNOSTIC / PARITY REPRODUCTION — NOT A NEW VERDICT.** This "
        "re-runs the **already-REJECTED** CAMPAIGN_002 H4 `trend_following` "
        "baseline on the bespoke engine for parity verification. "
        "`strategy_evidence: false`. It runs no new hypothesis, sweeps no "
        "parameter, and approves nothing. CAMPAIGN_002 stays **REJECT** "
        "regardless of the figures below.",
        "",
        "## Run parameters",
        "",
        "| field | value |",
        "|---|---|",
        "| strategy | `trend_following 0.1.0-baseline-frozen` |",
        "| config | `configs/campaign_002_real_oanda.yaml` |",
        f"| config hash | `{config_hash[:16]}…` |",
        "| fill timing | `signal_bar_close` (CAMPAIGN_002's timing) |",
        "| cost model | base regime — 0.2 pip slippage, 0.5× spread |",
        "| risk engine | wired in (`mode=backtest`) — as CAMPAIGN_002 ran |",
        f"| window | {WINDOW_FROM} → {WINDOW_TO} (full split) |",
        f"| data store | `{db_display}` (gitignored) |",
        "",
        "## Data provenance",
        "",
        "| instrument | candles | first ts | last ts | data_request_hash |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r.instrument} | {r.candle_count} | {r.first_ts} | "
            f"{r.last_ts} | `{r.data_request_hash}` |"
        )

    lines += [
        "",
        "## Reproduction results (bespoke engine)",
        "",
        "| instrument | trades | expectancy R | return % | profit factor "
        "| win % | max DD % | rejected |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        pf = f"{r.profit_factor:.2f}" if r.profit_factor is not None else "inf"
        lines.append(
            f"| {r.instrument} | {r.trade_count} | {r.expectancy_r:.3f} | "
            f"{r.total_return_pct:.2f} | {pf} | {r.win_rate * 100:.1f} | "
            f"{r.max_drawdown_pct:.2f} | {r.rejected_signal_count} |"
        )
    lines.append("")
    lines.append(f"**Total trades across the seven pairs: {total_trades}.**")

    lines += [
        "",
        "## Comparison to the committed CAMPAIGN_002 report",
        "",
        "Reference numbers are the CAMPAIGN_002 H4 full-split, base-cost "
        "per-pair figures from `backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md`. "
        "A small delta is expected (the store was independently "
        "re-fetched); a large delta would itself be a finding to "
        "investigate — never tuned away.",
        "",
        "| instrument | trades (repro / ref / Δ) | expectancy R (repro / ref / Δ) |",
        "|---|---|---|",
    ]
    for r in results:
        ref = CAMPAIGN_002_H4_REFERENCE.get(r.instrument)
        if ref is None:
            lines.append(
                f"| {r.instrument} | {r.trade_count} / — / — | "
                f"{r.expectancy_r:.3f} / — / — |"
            )
            continue
        lines.append(
            f"| {r.instrument} | {r.trade_count} / {int(ref['trades'])} / "
            f"{r.trade_count - int(ref['trades']):+d} | "
            f"{r.expectancy_r:.3f} / {ref['expectancy_r']:.3f} / "
            f"{_delta(r.expectancy_r, ref['expectancy_r'])} |"
        )
    lines += [
        "",
        f"Reproduction total trades **{total_trades}** vs committed "
        f"**{REFERENCE_TOTAL_TRADES}** "
        f"(Δ {total_trades - REFERENCE_TOTAL_TRADES:+d}).",
        "",
        "## What this establishes",
        "",
        "- The bespoke engine's CAMPAIGN_002 H4 baseline is **reproducible** "
        "from the committed config and the local real-OANDA H4 store — the "
        "custom-engine side of the Lean parity comparison is hash-pinned "
        "and re-runnable.",
        "- It does **not** establish, measure, or imply any strategy edge. "
        "CAMPAIGN_002 was REJECT and stays REJECT. This is parity "
        "reproduction infrastructure, not strategy evidence, and approves "
        "nothing.",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Custom-engine CAMPAIGN_002 H4 parity reproduction."
    )
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args(argv)

    db_path = Path(args.db)
    try:
        db_display = str(db_path.resolve().relative_to(ROOT))
    except ValueError:
        db_display = str(db_path)
    if not db_path.exists():
        print(
            f"BLOCKER: no H4 store at {db_display}. Run "
            "scripts/rehydrate_oanda_h4_store.py first.",
            file=sys.stderr,
        )
        return 1

    settings = load_settings(Path(args.config))
    risk_engine = RiskEngine(settings, mode="backtest")
    candle_repo = CandleRepo(Database(db_path))
    from_dt = datetime.fromisoformat(WINDOW_FROM).replace(tzinfo=UTC)
    to_dt = datetime.fromisoformat(WINDOW_TO).replace(tzinfo=UTC)

    results: list[PairResult] = []
    for pair in PAIRS:
        result = run_pair(
            settings, risk_engine, candle_repo,
            instrument=pair, from_dt=from_dt, to_dt=to_dt,
            source="oanda-practice",
        )
        if result is None:
            print(f"BLOCKER: no H4 candles for {pair} in the store.", file=sys.stderr)
            return 1
        results.append(result)
        print(
            f"  {pair}: {result.trade_count} trades, "
            f"expectancy_r={result.expectancy_r:.3f}"
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        render_doc(
            results,
            config_hash=settings.config_hash,  # type: ignore[attr-defined]
            generated_at=datetime.now(UTC),
            db_display=db_display,
        ),
        encoding="utf-8",
    )
    try:
        out_display = str(out_path.resolve().relative_to(ROOT))
    except ValueError:
        out_display = str(out_path)
    print(
        f"custom-engine CAMPAIGN_002 H4 parity reproduction: "
        f"{len(results)} pairs, {sum(r.trade_count for r in results)} trades "
        f"— report written to {out_display}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
