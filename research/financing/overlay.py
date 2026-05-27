"""Trade-record financing overlay utilities.

Applies deterministic financing to existing trade CSV rows without
rerunning strategy campaigns. Diagnostic only — ``strategy_evidence:
false``.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from research.financing.calculator import calculate_run
from research.financing.models import FinancingCalculatorConfig, PositionInterval
from research.financing.rates import FinancingRateSource, default_stress_rate_source

_USD_BASE = frozenset({"USD_JPY", "USD_CAD", "USD_CHF"})


def _risk_usd(
    instrument: str,
    units: Decimal,
    entry_price: Decimal,
    stop_price: Decimal,
) -> float:
    risk_quote = abs(entry_price - stop_price) * abs(units)
    if instrument in _USD_BASE:
        return float(risk_quote / entry_price) if entry_price else 0.0
    return float(risk_quote)


def load_trades_from_csv(
    path: str | Path,
    *,
    home_currency: str = "USD",
    id_prefix: str | None = None,
) -> list[tuple[PositionInterval, dict[str, str]]]:
    """Load trade rows from a campaign-style trades CSV."""
    p = Path(path)
    prefix = id_prefix or p.stem
    out: list[tuple[PositionInterval, dict[str, str]]] = []
    with p.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for i, row in enumerate(reader):
            pid = f"{prefix}_{i:04d}"
            interval = PositionInterval(
                position_id=pid,
                instrument=row["instrument"],
                side=row["side"],
                units=Decimal(row["units"]),
                entry_price=Decimal(row["entry_price"]),
                open_time=datetime.fromisoformat(row["entry_time"]),
                close_time=datetime.fromisoformat(row["exit_time"]),
                home_currency=home_currency,
            )
            out.append((interval, dict(row)))
    return out


def load_trades_from_glob(
    pattern: str,
    *,
    home_currency: str = "USD",
) -> list[tuple[PositionInterval, dict[str, str]]]:
    """Load and concatenate trades matching a glob pattern."""
    from glob import glob

    all_trades: list[tuple[PositionInterval, dict[str, str]]] = []
    for path in sorted(glob(pattern)):
        all_trades.extend(
            load_trades_from_csv(path, home_currency=home_currency)
        )
    return all_trades


def apply_financing_overlay(
    trades: list[tuple[PositionInterval, dict[str, str]]],
    rate_source: FinancingRateSource | None = None,
    config: FinancingCalculatorConfig | None = None,
    *,
    diagnostic_label: str = "SYNTHETIC_FINANCING_DIAGNOSTIC",
) -> dict[str, Any]:
    """Apply financing to trade records and return aggregate diagnostics."""
    source = rate_source or default_stress_rate_source()
    cfg = config or FinancingCalculatorConfig()
    intervals = [t[0] for t in trades]
    report = calculate_run(intervals, source, cfg)

    per_trade: list[dict[str, Any]] = []
    missing_rates: list[dict[str, str]] = []
    by_pair: dict[str, dict[str, float]] = defaultdict(
        lambda: {
            "trades": 0,
            "rollovers": 0,
            "financing_usd": 0.0,
            "gross_pnl_usd": 0.0,
            "gross_r": 0.0,
            "net_r": 0.0,
            "hold_bars": 0,
        }
    )
    by_side: dict[str, dict[str, float]] = defaultdict(
        lambda: {
            "trades": 0,
            "financing_usd": 0.0,
            "gross_r": 0.0,
            "net_r": 0.0,
        }
    )

    gross_r_sum = 0.0
    net_r_sum = 0.0
    financing_r_sum = 0.0

    for (interval, row), summary in zip(trades, report.positions, strict=True):
        fin_usd = summary.cashflow_home_stress_total
        gross_pnl = float(row["pnl"])
        gross_r = float(row["r_multiple"])
        bars = int(row.get("bars_held", "0") or 0)
        stop = Decimal(row["stop_price"]) if row.get("stop_price") else Decimal(0)
        risk = _risk_usd(interval.instrument, interval.units, interval.entry_price, stop)
        fin_r = fin_usd / risk if risk > 0 else 0.0
        net_r = gross_r + fin_r

        if summary.rate_was_missing_any:
            missing_rates.append(
                {
                    "position_id": interval.position_id,
                    "instrument": interval.instrument,
                }
            )

        rec = {
            "position_id": interval.position_id,
            "instrument": interval.instrument,
            "side": interval.side,
            "bars_held": bars,
            "rollovers": summary.rollovers,
            "gross_pnl_usd": gross_pnl,
            "gross_r": gross_r,
            "financing_usd": fin_usd,
            "financing_r": fin_r,
            "net_r": net_r,
            "rate_was_missing": summary.rate_was_missing_any,
        }
        per_trade.append(rec)

        gross_r_sum += gross_r
        net_r_sum += net_r
        financing_r_sum += fin_r

        bp = by_pair[interval.instrument]
        bp["trades"] += 1
        bp["rollovers"] += summary.rollovers
        bp["financing_usd"] += fin_usd
        bp["gross_pnl_usd"] += gross_pnl
        bp["gross_r"] += gross_r
        bp["net_r"] += net_r
        bp["hold_bars"] += bars

        bs = by_side[interval.side]
        bs["trades"] += 1
        bs["financing_usd"] += fin_usd
        bs["gross_r"] += gross_r
        bs["net_r"] += net_r

    n = len(trades) or 1
    total_rollovers = sum(s.rollovers for s in report.positions)
    return {
        "strategy_evidence": False,
        "not_approved": True,
        "diagnostic_label": diagnostic_label,
        "financing_source_type": source.source_type.value,
        "financing_treatment": source.treatment.value,
        "rate_source_name": source.name,
        "trade_count": len(trades),
        "aggregate": {
            "gross_expectancy_r": gross_r_sum / n,
            "net_expectancy_r": net_r_sum / n,
            "financing_drag_r": financing_r_sum / n,
            "total_financing_usd": report.cashflow_home_stress_total,
            "total_rollovers": total_rollovers,
            "missing_rate_event_count": report.missing_rate_event_count,
            "avg_bars_held": sum(int(r["bars_held"]) for r in per_trade) / n,
            "avg_rollovers_per_trade": total_rollovers / n,
        },
        "by_pair": dict(by_pair),
        "by_side": dict(by_side),
        "missing_rates": missing_rates,
        "per_trade": per_trade,
    }


def write_overlay_result(result: dict[str, Any], output_path: str | Path) -> None:
    """Write overlay diagnostics to JSON."""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
