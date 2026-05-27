"""Trade-ledger financing overlay contract (local-first, no broker I/O).

Wraps ``research.financing`` calculator/overlay with explicit overlay modes.
Does not modify backtest engine PnL or approve strategies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any

from research.financing.calculator import calculate_run
from research.financing.fixtures import FixtureValidationError, load_rate_fixture
from research.financing.models import FinancingCalculatorConfig, PositionInterval
from research.financing.rates import (
    FinancingRateSource,
    TableRateSource,
    default_stress_rate_source,
)

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "research" / "financing" / "fixtures"


class FinancingOverlayMode(StrEnum):
    NONE = "none"
    SYNTHETIC_FIXTURE = "synthetic_fixture"
    MANUAL_OBSERVED_FIXTURE = "manual_observed_fixture"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class TradeLedgerRef:
    campaign_id: str
    ledger_label: str
    trade_paths: tuple[str, ...]
    strategy: str = ""
    version: str = ""
    timeframe: str = "H4"
    hours_per_bar: int = 4


@dataclass
class TradeOverlayResult:
    position_id: str
    instrument: str
    side: str
    entry_time: str
    exit_time: str
    days_held: float
    rollover_events: int
    triple_rollover_events: int
    gross_pnl_home: float
    gross_r: float | None
    financing_home: float
    financing_r: float | None
    adjusted_pnl_home: float | None
    adjusted_r: float | None
    financing_mode: str
    rate_source: str
    synthetic: bool
    warnings: list[str] = field(default_factory=list)


@dataclass
class LedgerOverlaySummary:
    campaign_id: str
    ledger_label: str
    financing_mode: str
    rate_source: str
    synthetic: bool
    trade_count: int
    gross_expectancy_r: float | None
    adjusted_expectancy_r: float | None
    financing_drag_r: float | None
    avg_hold_days: float
    max_hold_days: float
    unavailable_rate_trades: int
    warnings: list[str] = field(default_factory=list)
    by_pair: dict[str, Any] = field(default_factory=dict)
    by_hold_bucket: dict[str, Any] = field(default_factory=dict)


def _risk_usd(
    instrument: str,
    units: Any,
    entry_price: Any,
    stop_price: Any,
) -> float:
    from decimal import Decimal

    from forex_bot.financing import risk_usd

    return risk_usd(
        instrument,
        Decimal(str(units)),
        Decimal(str(entry_price)),
        Decimal(str(stop_price)),
    )


def _hold_bucket(days: float) -> str:
    if days <= 1.0:
        return "0-1d"
    if days <= 3.0:
        return "1-3d"
    if days <= 7.0:
        return "3-7d"
    return "7d+"


def merge_rate_fixtures(paths: list[Path], *, name: str = "merged_manual_fixture") -> TableRateSource:
    """Merge committed ``financing_rates`` JSON fixtures into one table."""
    table: dict[tuple[date, str], Any] = {}
    for path in paths:
        source, _ = load_rate_fixture(path)
        for key, pair in source._table.items():
            table[key] = pair
    return TableRateSource(table, name=name)


def resolve_rate_source(
    mode: FinancingOverlayMode,
    *,
    fixture_paths: list[Path] | None = None,
) -> tuple[FinancingRateSource | None, str, bool, list[str]]:
    """Return (source, rate_source_label, is_synthetic, warnings)."""
    warnings: list[str] = []
    if mode == FinancingOverlayMode.NONE:
        return None, "none", False, warnings
    if mode == FinancingOverlayMode.UNAVAILABLE:
        warnings.append("financing rates unavailable — overlay skipped")
        return None, "unavailable", False, warnings
    if mode == FinancingOverlayMode.SYNTHETIC_FIXTURE:
        src = default_stress_rate_source()
        return src, src.name, True, warnings
    if mode == FinancingOverlayMode.MANUAL_OBSERVED_FIXTURE:
        paths = fixture_paths or sorted(FIXTURES_DIR.glob("rates_two_week_*.json"))
        if not paths:
            warnings.append("no manual rate fixtures found")
            return None, "unavailable", False, warnings
        try:
            merged = merge_rate_fixtures(paths, name="manual_fixture_table")
        except FixtureValidationError as exc:
            warnings.append(str(exc))
            return None, "unavailable", False, warnings
        warnings.append(
            "fixtures are committed synthetic schedules labeled for diagnostic use; "
            "not broker-observed history"
        )
        return merged, merged.name, True, warnings
    raise ValueError(f"unknown financing mode: {mode!r}")


def load_trades_for_overlay(
    path: str | Path,
    *,
    home_currency: str = "USD",
    hours_per_bar: int = 4,
) -> tuple[list[tuple[PositionInterval, dict[str, str]]], list[str]]:
    """Load trades; repair ledger rows where exit_time <= entry_time using bars_held."""
    import csv
    from datetime import datetime
    from decimal import Decimal

    from research.financing.models import PositionInterval

    warnings: list[str] = []
    out: list[tuple[PositionInterval, dict[str, str]]] = []
    p = Path(path)
    prefix = p.stem
    with p.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for i, row in enumerate(reader):
            pid = f"{prefix}_{i:04d}"
            entry = datetime.fromisoformat(row["entry_time"])
            exit_t = datetime.fromisoformat(row["exit_time"])
            row_copy = dict(row)
            if exit_t <= entry:
                bars = max(int(row.get("bars_held") or 0), 1)
                exit_t = entry + timedelta(hours=bars * hours_per_bar)
                row_copy["exit_time"] = exit_t.isoformat()
                warnings.append(
                    f"{p.name}: row {i} repaired close_time from bars_held={bars}"
                )
            interval = PositionInterval(
                position_id=pid,
                instrument=row["instrument"],
                side=row["side"],
                units=Decimal(row["units"]),
                entry_price=Decimal(row["entry_price"]),
                open_time=entry,
                close_time=exit_t,
                home_currency=home_currency,
            )
            out.append((interval, row_copy))
    return out, warnings


def overlay_ledger(
    ledger: TradeLedgerRef,
    mode: FinancingOverlayMode,
    *,
    home_currency: str = "USD",
    fixture_paths: list[Path] | None = None,
) -> LedgerOverlaySummary:
    """Apply financing overlay to all trade CSVs in a ledger reference."""
    trades: list[tuple[PositionInterval, dict[str, str]]] = []
    load_warnings: list[str] = []
    for path in ledger.trade_paths:
        batch, warns = load_trades_for_overlay(
            path, home_currency=home_currency, hours_per_bar=ledger.hours_per_bar
        )
        trades.extend(batch)
        load_warnings.extend(warns)

    source, rate_label, is_synthetic, mode_warnings = resolve_rate_source(
        mode, fixture_paths=fixture_paths
    )
    cfg = FinancingCalculatorConfig()

    per_trade_results: list[TradeOverlayResult] = []
    by_pair: dict[str, dict[str, float]] = {}
    by_bucket: dict[str, dict[str, float]] = {}
    unavailable_trades = 0
    gross_r_sum = 0.0
    fin_r_sum = 0.0
    net_r_sum = 0.0
    hold_days_list: list[float] = []

    if mode == FinancingOverlayMode.NONE or source is None:
        for interval, row in trades:
            bars = int(row.get("bars_held") or 0)
            days = bars * ledger.hours_per_bar / 24.0
            hold_days_list.append(days)
            gross_r = float(row["r_multiple"])
            gross_r_sum += gross_r
            net_r_sum += gross_r
            bucket = _hold_bucket(days)
            _accum(by_pair, interval.instrument, gross_r, 0.0, gross_r, days)
            _accum(by_bucket, bucket, gross_r, 0.0, gross_r, days)
        n = len(trades) or 1
        return LedgerOverlaySummary(
            campaign_id=ledger.campaign_id,
            ledger_label=ledger.ledger_label,
            financing_mode=mode.value,
            rate_source=rate_label,
            synthetic=is_synthetic,
            trade_count=len(trades),
            gross_expectancy_r=gross_r_sum / n if trades else None,
            adjusted_expectancy_r=gross_r_sum / n if trades else None,
            financing_drag_r=0.0 if trades else None,
            avg_hold_days=sum(hold_days_list) / n if hold_days_list else 0.0,
            max_hold_days=max(hold_days_list) if hold_days_list else 0.0,
            unavailable_rate_trades=0,
            warnings=list(mode_warnings) + load_warnings,
            by_pair=by_pair,
            by_hold_bucket=by_bucket,
        )

    intervals = [t[0] for t in trades]
    report = calculate_run(intervals, source, cfg)

    for (interval, row), summary in zip(trades, report.positions, strict=True):
        bars = int(row.get("bars_held") or 0)
        days = bars * ledger.hours_per_bar / 24.0
        hold_days_list.append(days)
        gross_pnl = float(row["pnl"])
        gross_r = float(row["r_multiple"])
        stop = row.get("stop_price") or row["entry_price"]
        risk = _risk_usd(interval.instrument, interval.units, interval.entry_price, stop)
        fin_home = summary.cashflow_home_stress_total
        fin_r = fin_home / risk if risk > 0 else None
        adj_pnl = gross_pnl + fin_home
        adj_r = (gross_r + fin_r) if fin_r is not None else None
        triple = sum(1 for e in summary.events if e.rollover_multiplier >= 3)
        trade_warnings: list[str] = []
        if summary.rate_was_missing_any:
            unavailable_trades += 1
            trade_warnings.append("HTF_UNAVAILABLE_RATE")
        per_trade_results.append(
            TradeOverlayResult(
                position_id=interval.position_id,
                instrument=interval.instrument,
                side=interval.side,
                entry_time=row["entry_time"],
                exit_time=row["exit_time"],
                days_held=days,
                rollover_events=summary.rollovers,
                triple_rollover_events=triple,
                gross_pnl_home=gross_pnl,
                gross_r=gross_r,
                financing_home=fin_home,
                financing_r=fin_r,
                adjusted_pnl_home=adj_pnl,
                adjusted_r=adj_r,
                financing_mode=mode.value,
                rate_source=rate_label,
                synthetic=is_synthetic,
                warnings=trade_warnings,
            )
        )
        gross_r_sum += gross_r
        fin_r_sum += fin_r or 0.0
        net_r_sum += adj_r if adj_r is not None else gross_r
        bucket = _hold_bucket(days)
        _accum(by_pair, interval.instrument, gross_r, fin_r or 0.0, adj_r or gross_r, days)
        _accum(by_bucket, bucket, gross_r, fin_r or 0.0, adj_r or gross_r, days)

    n = len(trades) or 1
    return LedgerOverlaySummary(
        campaign_id=ledger.campaign_id,
        ledger_label=ledger.ledger_label,
        financing_mode=mode.value,
        rate_source=rate_label,
        synthetic=is_synthetic,
        trade_count=len(trades),
        gross_expectancy_r=gross_r_sum / n if trades else None,
        adjusted_expectancy_r=net_r_sum / n if trades else None,
        financing_drag_r=fin_r_sum / n if trades else None,
        avg_hold_days=sum(hold_days_list) / n if hold_days_list else 0.0,
        max_hold_days=max(hold_days_list) if hold_days_list else 0.0,
        unavailable_rate_trades=unavailable_trades,
        warnings=list(mode_warnings) + load_warnings,
        by_pair=by_pair,
        by_hold_bucket=by_bucket,
    )


def _accum(
    bucket: dict[str, dict[str, float]],
    key: str,
    gross_r: float,
    fin_r: float,
    net_r: float,
    days: float,
) -> None:
    if key not in bucket:
        bucket[key] = {
            "trades": 0,
            "gross_r": 0.0,
            "financing_r": 0.0,
            "adjusted_r": 0.0,
            "hold_days": 0.0,
        }
    b = bucket[key]
    b["trades"] += 1
    b["gross_r"] += gross_r
    b["financing_r"] += fin_r
    b["adjusted_r"] += net_r
    b["hold_days"] += days


def inventory_trade_csv(path: Path, *, hours_per_bar: int = 4) -> dict[str, Any] | None:
    """Summarize one trades CSV for inventory."""
    if not path.is_file():
        return None
    import csv

    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return {"path": str(path), "trade_count": 0, "available": False}
    bars = [int(r.get("bars_held") or 0) for r in rows]
    days = [b * hours_per_bar / 24.0 for b in bars]
    cols = set(rows[0].keys())
    return {
        "path": str(path),
        "trade_count": len(rows),
        "avg_hold_bars": sum(bars) / len(bars),
        "max_hold_bars": max(bars),
        "avg_hold_days": sum(days) / len(days),
        "max_hold_days": max(days),
        "has_timestamps": "entry_time" in cols and "exit_time" in cols,
        "has_side": "side" in cols,
        "has_units": "units" in cols,
        "has_r_multiple": "r_multiple" in cols,
        "has_pnl": "pnl" in cols,
        "has_stop": "stop_price" in cols,
        "financing_in_engine": False,
        "available": True,
    }
