"""Tests for trade-record financing overlay utility."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from research.financing.models import PositionInterval
from research.financing.overlay import (
    apply_financing_overlay,
    load_trades_from_csv,
    write_overlay_result,
)
from research.financing.rates import default_stress_rate_source


def _sample_trade_row() -> dict[str, str]:
    return {
        "instrument": "EUR_USD",
        "side": "short",
        "units": "292",
        "entry_time": "2020-07-06T09:00:00+00:00",
        "exit_time": "2020-07-13T13:00:00+00:00",
        "entry_price": "1.132830",
        "exit_price": "1.13718",
        "stop_price": "1.13718",
        "pnl": "-1.270200",
        "r_multiple": "-1",
        "bars_held": "31",
    }


def test_apply_financing_overlay_preserves_gross_and_adds_financing() -> None:
    row = _sample_trade_row()
    interval = PositionInterval(
        position_id="t0001",
        instrument=row["instrument"],
        side=row["side"],
        units=Decimal(row["units"]),
        entry_price=Decimal(row["entry_price"]),
        open_time=datetime.fromisoformat(row["entry_time"]),
        close_time=datetime.fromisoformat(row["exit_time"]),
        home_currency="USD",
    )
    result = apply_financing_overlay(
        [(interval, row)],
        rate_source=default_stress_rate_source(),
    )
    assert result["strategy_evidence"] is False
    assert result["diagnostic_label"] == "SYNTHETIC_FINANCING_DIAGNOSTIC"
    assert result["trade_count"] == 1
    pt = result["per_trade"][0]
    assert pt["gross_r"] == -1.0
    assert pt["rollovers"] >= 1
    assert pt["financing_usd"] <= 0.0
    assert pt["net_r"] <= pt["gross_r"]


def test_apply_financing_overlay_aggregate_drag() -> None:
    row = _sample_trade_row()
    interval = PositionInterval(
        position_id="t0001",
        instrument=row["instrument"],
        side=row["side"],
        units=Decimal(row["units"]),
        entry_price=Decimal(row["entry_price"]),
        open_time=datetime.fromisoformat(row["entry_time"]),
        close_time=datetime.fromisoformat(row["exit_time"]),
    )
    result = apply_financing_overlay([(interval, row)])
    agg = result["aggregate"]
    assert agg["financing_drag_r"] < 0
    assert agg["net_expectancy_r"] < agg["gross_expectancy_r"]


def test_load_trades_from_csv_roundtrip(tmp_path: Path) -> None:
    csv_path = tmp_path / "trades.csv"
    csv_path.write_text(
        "instrument,side,units,entry_time,exit_time,entry_price,exit_price,"
        "stop_price,pnl,r_multiple,bars_held\n"
        + ",".join(_sample_trade_row().values())
        + "\n",
        encoding="utf-8",
    )
    loaded = load_trades_from_csv(csv_path)
    assert len(loaded) == 1
    interval, row = loaded[0]
    assert interval.instrument == "EUR_USD"
    assert row["r_multiple"] == "-1"


def test_write_overlay_result(tmp_path: Path) -> None:
    out = tmp_path / "out.json"
    payload = {"strategy_evidence": False, "trade_count": 0}
    write_overlay_result(payload, out)
    assert out.read_text(encoding="utf-8").startswith("{")
