"""Step 0 (CAMPAIGN_003): permanent per-signal RiskEngine rejection export.

Proves the risk_rejections CSV is always written, carries the
analysis-ready columns, and never contains credentials.
"""

from __future__ import annotations

import csv
import re
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from forex_bot.backtesting.engine import BacktestEngine, RejectedSignalRecord
from forex_bot.backtesting.exporters import write_all, write_risk_rejections_csv
from forex_bot.backtesting.fills import FillModel
from forex_bot.backtesting.metrics import compute_metrics
from forex_bot.config import load_settings
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.risk.policy import RiskEngine
from forex_bot.strategies.trend_following import TrendFollowingStrategy

REQUIRED_COLUMNS = {
    "timestamp",
    "instrument",
    "granularity",
    "split",
    "strategy_version",
    "side",
    "rejection_code",
    "rejection_reason",
    "spread_pips",
    "atr_pips",
    "stop_distance_pips",
    "hour_utc",
    "day_of_week",
    "session",
}

# Patterns that would indicate a credential leak.
_SECRET_PATTERNS = [
    re.compile(r"\b[a-f0-9]{32}-[a-f0-9]{32}\b", re.IGNORECASE),  # OANDA token
    re.compile(r"\b\d{3}-\d{3}-\d{4,10}-\d{3}\b"),  # OANDA account id
    re.compile(r"Bearer\s+\S+", re.IGNORECASE),
]


def _wide_spread_frame(n: int = 260) -> CandleFrame:
    """Uptrend with a 5-pip spread on every bar — the RiskEngine spread
    filter rejects every entry the strategy proposes."""
    candles = []
    base = Decimal("1.0500")
    spread = Decimal("0.0005")
    for i in range(n):
        m = base + Decimal("0.0002") * i
        bid_c = m - spread / 2
        ask_c = m + spread / 2
        prev = base + Decimal("0.0002") * (i - 1) if i > 0 else m
        bid_o = prev - spread / 2
        ask_o = prev + spread / 2
        candles.append(
            Candle(
                instrument="EUR_USD",
                granularity="H4",
                time=datetime(2025, 1, 1, tzinfo=UTC) + timedelta(hours=4 * i),
                complete=True,
                volume=1000,
                bid_o=bid_o, bid_h=bid_c, bid_l=bid_o, bid_c=bid_c,
                ask_o=ask_o, ask_h=ask_c, ask_l=ask_o, ask_c=ask_c,
            )
        )
    return CandleFrame.from_candles("EUR_USD", "H4", candles)


def _practice_settings(practice_config_path: Path, monkeypatch, tmp_path):
    monkeypatch.setenv("OANDA_ACCOUNT_ID_PRACTICE", "x")
    monkeypatch.setenv("OANDA_ACCESS_TOKEN_PRACTICE", "y")
    text = practice_config_path.read_text(encoding="utf-8")
    text = text.replace("./KILL_SWITCH", str(tmp_path / "KILL_SWITCH"))
    text = text.replace("./data/bot.sqlite3", str(tmp_path / "bot.sqlite3"))
    text = text.replace("./logs/bot.jsonl", str(tmp_path / "bot.jsonl"))
    out = tmp_path / "practice.yaml"
    out.write_text(text, encoding="utf-8")
    return load_settings(out)


def _engine(settings, eur_usd) -> BacktestEngine:
    return BacktestEngine(
        instrument=eur_usd,
        strategy=TrendFollowingStrategy(version="0.1.0-baseline-frozen"),
        strategy_config={
            "ema_fast": 20,
            "ema_slow": 60,
            "donchian_lookback": 10,
            "atr_lookback": 14,
            "atr_stop_multiple": 2.0,
            "min_atr_pips": {},
            "max_bars_in_trade": 60,
            "timeframe": "H4",
        },
        fill_model=FillModel(
            fixed_slippage_pips=Decimal("0"),
            spread_slippage_multiplier=Decimal("0"),
        ),
        starting_equity=Decimal("500"),
        account_currency="USD",
        risk_engine=RiskEngine(settings, mode="backtest"),
        settings=settings,
    )


def test_write_all_emits_risk_rejections_csv(practice_config_path, monkeypatch, tmp_path, eur_usd):
    settings = _practice_settings(practice_config_path, monkeypatch, tmp_path)
    result = _engine(settings, eur_usd).run(_wide_spread_frame())
    assert len(result.rejected_signals) > 0, "fixture should produce rejections"

    paths = write_all(result, tmp_path / "exp", "test_run", split="full")
    rej_path = paths["risk_rejections_csv"]
    assert rej_path.exists(), "risk_rejections.csv must be written by write_all"

    rows = list(csv.DictReader(rej_path.open(encoding="utf-8")))
    assert len(rows) > 0
    assert REQUIRED_COLUMNS.issubset(set(rows[0].keys()))


def test_rejection_csv_columns_populated(practice_config_path, monkeypatch, tmp_path, eur_usd):
    settings = _practice_settings(practice_config_path, monkeypatch, tmp_path)
    result = _engine(settings, eur_usd).run(_wide_spread_frame())
    path = tmp_path / "rej.csv"
    write_risk_rejections_csv(result, path, split="test_untouched")
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    sample = rows[0]
    assert sample["instrument"] == "EUR_USD"
    assert sample["granularity"] == "H4"
    assert sample["split"] == "test_untouched"
    assert sample["rejection_code"]  # non-empty
    assert sample["session"] in {"Asia/late", "London", "London/NY overlap", "NY"}
    assert 0 <= int(sample["hour_utc"]) <= 23
    assert sample["day_of_week"] in {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}


def test_rejection_csv_contains_no_credentials(
    practice_config_path, monkeypatch, tmp_path, eur_usd
):
    settings = _practice_settings(practice_config_path, monkeypatch, tmp_path)
    result = _engine(settings, eur_usd).run(_wide_spread_frame())
    path = tmp_path / "rej.csv"
    write_risk_rejections_csv(result, path, split="full")
    content = path.read_text(encoding="utf-8")
    for pattern in _SECRET_PATTERNS:
        assert not pattern.search(content), f"credential-like text matched {pattern.pattern}"
    # Belt and braces: the literal practice creds set in the fixture.
    assert "OANDA_ACCESS_TOKEN" not in content


def test_rejection_csv_written_empty_when_no_risk_engine(tmp_path, eur_usd):
    """A run without a RiskEngine still gets a header-only file so downstream
    tooling can rely on the path existing."""
    engine = BacktestEngine(
        instrument=eur_usd,
        strategy=TrendFollowingStrategy(version="0.1.0-baseline-frozen"),
        strategy_config={"ema_fast": 20, "ema_slow": 60, "donchian_lookback": 10},
        fill_model=FillModel(
            fixed_slippage_pips=Decimal("0"),
            spread_slippage_multiplier=Decimal("0"),
        ),
        starting_equity=Decimal("500"),
        risk_engine=None,
    )
    result = engine.run(_wide_spread_frame())
    paths = write_all(result, tmp_path / "exp", "no_re")
    rej = paths["risk_rejections_csv"]
    assert rej.exists()
    rows = list(csv.DictReader(rej.open(encoding="utf-8")))
    assert rows == []  # header only, no data rows


def test_one_row_per_rejection_code(tmp_path):
    """A rejected signal with two codes must produce two rows."""
    result = compute_metrics([], [], 500.0)
    from forex_bot.backtesting.engine import BacktestResult

    bt = BacktestResult(
        metrics=result,
        strategy_version="0.2.0-c003",
        granularity="H4",
        rejected_signals=[
            RejectedSignalRecord(
                timestamp=datetime(2025, 6, 2, 13, 0, tzinfo=UTC),
                instrument="EUR_USD",
                granularity="H4",
                side="long",
                rejection_codes=["SPREAD_TOO_WIDE", "SPREAD_TO_ATR"],
                rejection_messages=["spread 5 > cap 1.5", "spread/atr 40%"],
                spread_pips=Decimal("5.0"),
                atr_pips=Decimal("12.5"),
            )
        ],
    )
    path = tmp_path / "rej.csv"
    write_risk_rejections_csv(bt, path, split="full")
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert len(rows) == 2
    assert {r["rejection_code"] for r in rows} == {"SPREAD_TOO_WIDE", "SPREAD_TO_ATR"}
    assert rows[0]["day_of_week"] == "Mon"  # 2025-06-02 is a Monday
    assert rows[0]["session"] == "London/NY overlap"  # 13:00 UTC
