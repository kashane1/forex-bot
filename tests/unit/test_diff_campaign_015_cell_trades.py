"""Tests for scripts/diff_campaign_015_cell_trades.py."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from scripts.diff_campaign_015_cell_trades import (
    NormalizedTrade,
    TradeClassification,
    classify_cell_trades,
    summarize_cell_diff,
    write_cell_diff_outputs,
)


def _trade(
    source: str,
    entry: str,
    side: str,
    *,
    exit_time: str | None = None,
    entry_price: float = 1.0,
    exit_reason: str = "stop",
) -> NormalizedTrade:
    entry_dt = datetime.fromisoformat(entry.replace("Z", "+00:00"))
    exit_dt = datetime.fromisoformat(
        (exit_time or entry.replace("T09:", "T13:")).replace("Z", "+00:00")
    )
    return NormalizedTrade(
        source=source,
        fold_index=0,
        instrument="EUR_USD",
        entry_time=entry_dt,
        exit_time=exit_dt,
        side=side,
        entry_price=entry_price,
        stop_price=0.99,
        exit_price=0.98,
        exit_reason=exit_reason,
        r_multiple=-1.0,
        pnl=-1.0,
    )


def test_matched_trade_pairing() -> None:
    bt = [_trade("bt", "2022-01-01T09:00:00+00:00", "long")]
    b = [_trade("bespoke", "2022-01-01T09:00:00+00:00", "long")]
    classified = classify_cell_trades(bt, b)
    assert len(classified) == 1
    assert classified[0].classification == TradeClassification.MATCHED


def test_bt_only_and_bespoke_only() -> None:
    bt = [
        _trade("bt", "2022-01-01T09:00:00+00:00", "long"),
        _trade("bt", "2022-01-02T09:00:00+00:00", "short"),
    ]
    b = [_trade("bespoke", "2022-01-03T09:00:00+00:00", "long")]
    classified = classify_cell_trades(bt, b)
    labels = {c.classification for c in classified}
    assert TradeClassification.BT_ONLY in labels
    assert TradeClassification.BESPOKE_ONLY in labels
    diff = summarize_cell_diff(
        fold_index=0,
        pair="EUR_USD",
        classified=classified,
        bt_count=2,
        bespoke_count=1,
    )
    assert diff.first_bt_only is not None
    assert diff.first_bt_only.entry_time == datetime(2022, 1, 1, 9, tzinfo=UTC)
    assert diff.first_bespoke_only is not None


def test_same_time_different_side() -> None:
    bt = [_trade("bt", "2022-01-01T09:00:00+00:00", "long")]
    b = [_trade("bespoke", "2022-01-01T09:00:00+00:00", "short")]
    classified = classify_cell_trades(bt, b)
    assert classified[0].classification == TradeClassification.SAME_TIME_DIFFERENT_SIDE


def test_same_entry_different_exit() -> None:
    bt = _trade("bt", "2022-01-01T09:00:00+00:00", "long", exit_reason="time")
    b = _trade("bespoke", "2022-01-01T09:00:00+00:00", "long", exit_reason="stop")
    classified = classify_cell_trades([bt], [b])
    assert classified[0].classification == TradeClassification.SAME_ENTRY_DIFFERENT_EXIT


def test_same_signal_different_fill() -> None:
    bt = _trade("bt", "2022-01-01T09:00:00+00:00", "long", entry_price=1.01)
    b = _trade("bespoke", "2022-01-01T09:00:00+00:00", "long", entry_price=1.02)
    classified = classify_cell_trades([bt], [b])
    assert classified[0].classification == TradeClassification.SAME_SIGNAL_DIFFERENT_FILL


def test_write_outputs(tmp_path: Path) -> None:
    bt = [_trade("bt", "2022-01-01T09:00:00+00:00", "long")]
    classified = classify_cell_trades(bt, [])
    diff = summarize_cell_diff(
        fold_index=1,
        pair="AUD_USD",
        classified=classified,
        bt_count=1,
        bespoke_count=0,
    )
    json_path, md_path = write_cell_diff_outputs(diff, tmp_path)
    assert json_path.is_file()
    assert md_path.is_file()
    assert "fold_01_AUD_USD" in json_path.name
