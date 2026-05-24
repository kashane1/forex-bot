"""Exporter propagation for the ambiguous-exit + gap-fill fields.

Sprint `infra-exit-fidelity-001` Phase 4. Verifies that the new fields
land correctly in trades CSV, metrics JSON, metrics MD, and summary
JSON, and that:

  * fresh artifacts and the existing campaign `_index.json` files
    interoperate (forward + backward read tolerance)
  * the metrics MD renders counts of 0 as "0" (not "N/A" or missing)
  * `gap_fill_policy` is always present in summary JSON even at default
"""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pandas as pd

from forex_bot.backtesting.engine import BacktestEngine, BacktestResult
from forex_bot.backtesting.exporters import (
    write_all,
    write_metrics_json,
    write_metrics_markdown,
    write_summary_json,
    write_trades_csv,
)
from forex_bot.backtesting.fills import FillModel
from forex_bot.backtesting.metrics import BacktestMetrics, TradeRecord
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_ZERO_FILL = FillModel(
    fixed_slippage_pips=Decimal("0"), spread_slippage_multiplier=Decimal("0")
)


# ---------------------------------------------------------------------------
# Helpers (mirror test_gap_fill.py)
# ---------------------------------------------------------------------------


class _OneShotGapStrategy:
    name = "oneshot_gap"
    version = "test"

    def __init__(self, *, fire_at: int, stop_price: Decimal, tp_price: Decimal) -> None:
        self._fire_at = fire_at
        self._stop = stop_price
        self._tp = tp_price

    def warmup_bars_required(self) -> int:
        return 2

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.completed_only().df
        if len(df) != self._fire_at:
            return None
        last = df.index[-1]
        return Signal(
            signal_id="exporter-test",
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe="H4",
            timestamp=pd.Timestamp(last).tz_convert(UTC).to_pydatetime(),
            side="long",
            stop_model="fixed",
            stop_price=self._stop,
            take_profit_price=self._tp,
            exit_model="target",
        )


def _candle_with_bid_ask(
    k: int,
    *,
    bid_o: Decimal,
    bid_h: Decimal,
    bid_l: Decimal,
    bid_c: Decimal,
    spread: Decimal = Decimal("0.0002"),
) -> Candle:
    return Candle(
        instrument="EUR_USD", granularity="H4",
        time=datetime(2025, 3, 3, tzinfo=UTC) + timedelta(hours=4 * k),
        complete=True, volume=1000,
        bid_o=bid_o, bid_h=bid_h, bid_l=bid_l, bid_c=bid_c,
        ask_o=bid_o + spread, ask_h=bid_h + spread,
        ask_l=bid_l + spread, ask_c=bid_c + spread,
    )


def _ambiguous_gap_frame() -> CandleFrame:
    """Build a frame whose exit bar is BOTH gap-through-stop AND
    ambiguous (tp also in range). Used to populate both new counters."""
    quiet = [
        _candle_with_bid_ask(
            k,
            bid_o=Decimal("1.10000"), bid_h=Decimal("1.10005"),
            bid_l=Decimal("1.09995"), bid_c=Decimal("1.10000"),
        )
        for k in range(6)
    ]
    exit_bar = _candle_with_bid_ask(
        6,
        bid_o=Decimal("1.09300"),  # gaps below stop 1.0950
        bid_h=Decimal("1.10550"),  # also reaches tp 1.1050 (ambiguous)
        bid_l=Decimal("1.09200"),
        bid_c=Decimal("1.09400"),
    )
    return CandleFrame.from_candles("EUR_USD", "H4", quiet + [exit_bar])


def _run_engine_with_gap(eur_usd) -> BacktestResult:
    strat = _OneShotGapStrategy(
        fire_at=6,
        stop_price=Decimal("1.09500"),  # 50 pips below entry
        tp_price=Decimal("1.10500"),    # 50 pips above entry
    )
    engine = BacktestEngine(
        instrument=eur_usd,
        strategy=strat,
        strategy_config={},
        fill_model=_ZERO_FILL,
        starting_equity=Decimal("500"),
        account_currency="USD",
        max_bars_in_trade=999,
        gap_fill_policy="gap_through",
    )
    return engine.run(_ambiguous_gap_frame())


# ---------------------------------------------------------------------------
# CSV round-trip
# ---------------------------------------------------------------------------


def test_csv_carries_ambiguous_and_gap_fill_columns(eur_usd, tmp_path):
    """The trades CSV must include the three new columns
    (`ambiguous_exit`, `gap_fill`, `gap_fill_distance_pips`) and
    round-trip correctly."""
    result = _run_engine_with_gap(eur_usd)
    assert len(result.trades) == 1
    csv_path = tmp_path / "trades.csv"
    write_trades_csv(result, csv_path)
    with csv_path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 1
    row = rows[0]
    # Columns present
    assert "ambiguous_exit" in row
    assert "gap_fill" in row
    assert "gap_fill_distance_pips" in row
    # Values: this trade is both ambiguous AND gap-filled
    assert row["ambiguous_exit"] == "True"
    assert row["gap_fill"] == "True"
    assert float(row["gap_fill_distance_pips"]) > 0


def test_csv_distance_blank_when_no_gap_fill(eur_usd, tmp_path):
    """When `gap_fill_distance_pips` is None, the CSV emits an empty
    string (CSV-idiomatic for absent value) — not 'None'."""
    # Use a quiet exit so no gap-fill fires.
    strat = _OneShotGapStrategy(
        fire_at=6,
        stop_price=Decimal("1.05000"),  # wide stop, never hit
        tp_price=Decimal("1.20000"),    # wide tp, never hit
    )
    quiet_frame = CandleFrame.from_candles(
        "EUR_USD", "H4",
        [
            _candle_with_bid_ask(
                k, bid_o=Decimal("1.10000"), bid_h=Decimal("1.10005"),
                bid_l=Decimal("1.09995"), bid_c=Decimal("1.10000"),
            )
            for k in range(8)
        ],
    )
    engine = BacktestEngine(
        instrument=eur_usd, strategy=strat, strategy_config={},
        fill_model=_ZERO_FILL, starting_equity=Decimal("500"),
        account_currency="USD", max_bars_in_trade=999,
        gap_fill_policy="gap_through",
    )
    result = engine.run(quiet_frame)
    csv_path = tmp_path / "trades.csv"
    write_trades_csv(result, csv_path)
    with csv_path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 1
    assert rows[0]["gap_fill"] == "False"
    assert rows[0]["gap_fill_distance_pips"] == ""


# ---------------------------------------------------------------------------
# Metrics JSON / MD / summary JSON
# ---------------------------------------------------------------------------


def test_metrics_json_carries_new_fields(eur_usd, tmp_path):
    result = _run_engine_with_gap(eur_usd)
    json_path = tmp_path / "metrics.json"
    write_metrics_json(result, json_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["gap_fill_policy"] == "gap_through"
    assert payload["metrics"]["ambiguous_exit_count"] == 1
    assert payload["metrics"]["gap_fill_exit_count"] == 1


def test_metrics_md_renders_new_fields(eur_usd, tmp_path):
    result = _run_engine_with_gap(eur_usd)
    md_path = tmp_path / "metrics.md"
    write_metrics_markdown(result, md_path)
    body = md_path.read_text(encoding="utf-8")
    assert "Gap-fill policy: `gap_through`" in body
    assert "Ambiguous same-bar SL+TP exits: **1**" in body
    assert "Gap-filled exits: **1**" in body


def test_metrics_md_renders_zero_when_no_collisions(eur_usd, tmp_path):
    """With no gap-fills and no ambiguous bars, counts render as **0**
    (not 'N/A' or missing). Numeric is more parseable than missing."""
    strat = _OneShotGapStrategy(
        fire_at=6,
        stop_price=Decimal("1.05000"),
        tp_price=Decimal("1.20000"),
    )
    quiet_frame = CandleFrame.from_candles(
        "EUR_USD", "H4",
        [
            _candle_with_bid_ask(
                k, bid_o=Decimal("1.10000"), bid_h=Decimal("1.10005"),
                bid_l=Decimal("1.09995"), bid_c=Decimal("1.10000"),
            )
            for k in range(8)
        ],
    )
    engine = BacktestEngine(
        instrument=eur_usd, strategy=strat, strategy_config={},
        fill_model=_ZERO_FILL, starting_equity=Decimal("500"),
        account_currency="USD", max_bars_in_trade=999,
    )
    result = engine.run(quiet_frame)
    md_path = tmp_path / "metrics.md"
    write_metrics_markdown(result, md_path)
    body = md_path.read_text(encoding="utf-8")
    assert "Ambiguous same-bar SL+TP exits: **0**" in body
    assert "Gap-filled exits: **0**" in body
    assert "Gap-fill policy: `none`" in body


def test_summary_json_carries_policy_even_when_default(eur_usd, tmp_path):
    """`gap_fill_policy` must be in summary JSON even at default 'none'
    so every artifact records which behavior produced it."""
    strat = _OneShotGapStrategy(
        fire_at=6,
        stop_price=Decimal("1.05000"),
        tp_price=Decimal("1.20000"),
    )
    quiet_frame = CandleFrame.from_candles(
        "EUR_USD", "H4",
        [
            _candle_with_bid_ask(
                k, bid_o=Decimal("1.10000"), bid_h=Decimal("1.10005"),
                bid_l=Decimal("1.09995"), bid_c=Decimal("1.10000"),
            )
            for k in range(8)
        ],
    )
    engine = BacktestEngine(
        instrument=eur_usd, strategy=strat, strategy_config={},
        fill_model=_ZERO_FILL, starting_equity=Decimal("500"),
        account_currency="USD", max_bars_in_trade=999,
        # No gap_fill_policy kwarg — default "none"
    )
    result = engine.run(quiet_frame)
    summary_path = tmp_path / "summary.json"
    write_summary_json(result, summary_path)
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["gap_fill_policy"] == "none"
    assert payload["metrics"]["ambiguous_exit_count"] == 0
    assert payload["metrics"]["gap_fill_exit_count"] == 0


def test_write_all_round_trip(eur_usd, tmp_path):
    """End-to-end: write_all produces all 6 artifacts with the new
    fields present, and they all parse cleanly."""
    result = _run_engine_with_gap(eur_usd)
    paths = write_all(result, tmp_path, "exptest")
    # Sanity check that all expected paths exist
    for name in ("trades_csv", "metrics_json", "metrics_md", "summary_json"):
        assert paths[name].exists()
    # Each new field appears in the respective file
    with paths["trades_csv"].open(encoding="utf-8") as fh:
        csv_rows = list(csv.DictReader(fh))
    assert csv_rows and csv_rows[0]["gap_fill"] == "True"
    md_body = paths["metrics_md"].read_text(encoding="utf-8")
    assert "Gap-fill policy: `gap_through`" in md_body
    summary = json.loads(paths["summary_json"].read_text(encoding="utf-8"))
    assert summary["gap_fill_policy"] == "gap_through"
    metrics = json.loads(paths["metrics_json"].read_text(encoding="utf-8"))
    assert metrics["gap_fill_policy"] == "gap_through"
    assert metrics["metrics"]["gap_fill_exit_count"] == 1


# ---------------------------------------------------------------------------
# `_index.json` forward + backward read tolerance
# ---------------------------------------------------------------------------


def test_committed_index_json_files_load_cleanly():
    """Every committed `backtests/campaign_*/runs/_index.json` predates
    this sprint and does NOT carry the new metric fields. They must
    continue to load cleanly via plain `json.loads` (the only reader
    pattern used by report builders — confirmed by data-integrity
    review)."""
    runs_dirs = list((REPO_ROOT / "backtests").glob("campaign_*/runs"))
    assert runs_dirs, "expected committed campaign runs directories"
    loaded_any = False
    for runs_dir in runs_dirs:
        index_path = runs_dir / "_index.json"
        if not index_path.exists():
            continue
        loaded_any = True
        data = json.loads(index_path.read_text(encoding="utf-8"))
        # Top-level shape must include `runs` (a list)
        assert isinstance(data, dict)
        if "runs" in data:
            assert isinstance(data["runs"], list)
            for run in data["runs"]:
                # Old runs MUST NOT carry the new fields. If they do,
                # someone backfilled and that's a freeze violation.
                assert "ambiguous_exit_count" not in run, (
                    f"unexpected new field in committed artifact "
                    f"{index_path}: ambiguous_exit_count present in a "
                    "pre-sprint run — backfilling is a freeze violation"
                )
                assert "gap_fill_exit_count" not in run
                assert "gap_fill_policy" not in run
    assert loaded_any, "no _index.json files found to test"


def test_fresh_summary_json_parses_with_dict_reader_pattern(eur_usd, tmp_path):
    """Freshly-generated summary.json with the new keys must be readable
    by the `json.loads(...read_text()) + .get(...)` pattern used by all
    existing `scripts/build_campaign_*_report.py` readers — no schema
    validator gets in the way of new fields."""
    result = _run_engine_with_gap(eur_usd)
    summary_path = tmp_path / "summary.json"
    write_summary_json(result, summary_path)
    # Read with the same idiom as build_campaign_*_report.py:
    raw = json.loads(summary_path.read_text(encoding="utf-8"))
    # Access pre-existing fields (these must not have moved or changed type)
    assert raw.get("instrument") == "EUR_USD"
    assert raw.get("config_hash")  # non-empty
    assert raw.get("metrics", {}).get("trade_count") == 1
    # Access new fields via .get() with default — the tolerant pattern
    assert raw.get("gap_fill_policy", "absent") == "gap_through"
    assert raw.get("metrics", {}).get("ambiguous_exit_count", 0) == 1
    assert raw.get("metrics", {}).get("gap_fill_exit_count", 0) == 1


def test_backtestmetrics_and_traderecord_construct_from_dict_without_new_fields():
    """Old code that builds a `BacktestMetrics` or `TradeRecord` from a
    dict (e.g., older test fixtures) without the new keys must continue
    to work via the trailing-default fields. Mirrors the
    `from_dict_tolerant` pattern noted by best-practices-researcher."""
    legacy_metrics_dict = {
        "total_return_pct": 0.0, "final_equity": 500.0,
        "starting_equity": 500.0, "max_drawdown_pct": 0.0,
        "max_drawdown_duration_bars": 0, "sharpe": 0.0, "sortino": 0.0,
        "profit_factor": 0.0, "expectancy_r": 0.0, "average_r": 0.0,
        "median_r": 0.0, "win_rate": 0.0, "average_win": 0.0,
        "average_loss": 0.0, "trade_count": 0,
        "largest_single_loss": 0.0, "average_spread_paid_pips": 0.0,
    }
    m = BacktestMetrics(**legacy_metrics_dict)
    assert m.ambiguous_exit_count == 0  # default
    assert m.gap_fill_exit_count == 0  # default

    legacy_trade_dict = {
        "instrument": "EUR_USD", "side": "long",
        "units": Decimal("100"),
        "entry_time": datetime(2025, 1, 1, tzinfo=UTC),
        "exit_time": datetime(2025, 1, 2, tzinfo=UTC),
        "entry_price": Decimal("1.1000"),
        "exit_price": Decimal("1.1050"),
        "stop_price": Decimal("1.0950"),
        "pnl": Decimal("5"), "r_multiple": Decimal("1.0"),
        "bars_held": 10, "spread_paid_pips": Decimal("1.0"),
        "exit_reason": "target",
    }
    t = TradeRecord(**legacy_trade_dict)
    assert t.ambiguous_exit is False
    assert t.gap_fill is False
    assert t.gap_fill_distance_pips is None
    assert t.fill_timing == "signal_bar_close"  # also a trailing default
