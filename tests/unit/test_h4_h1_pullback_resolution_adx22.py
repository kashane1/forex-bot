"""CAMPAIGN_023 ADX22 sibling tests.

Proves C023 is identical to C022 except the H4 directional-bias strength gate
(`h4_adx_min` 22.0 vs C022's 20.0). Helpers are reused from the C022 test module
to guarantee the two campaigns are exercised through one shared logic path.
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pandas as pd
import pytest
import yaml

from forex_bot.config import Settings, compute_config_hash
from forex_bot.domain.candles import CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.strategies.h4_h1_pullback_resolution_entry import (
    H4H1PullbackResolutionEntryStrategy,
    aligned_h4_bias,
    validate_c022_data_provenance,
)
from tests.unit.test_h4_h1_pullback_resolution_entry import (
    _PROVENANCE,
    _ctx_from_m15,
    _make_candle,
    _trending_candles,
)

_MOD = "forex_bot.strategies.h4_h1_pullback_resolution_entry"
_REPO_ROOT = Path(__file__).resolve().parents[2]
_C023_YAML = _REPO_ROOT / "configs/campaign_023_h4_h1_pullback_resolution_adx22.yaml"
_C022_YAML = _REPO_ROOT / "configs/campaign_022_h4_h1_pullback_resolution.yaml"
_STRATEGY_SOURCE = (
    _REPO_ROOT / "src" / "forex_bot" / "strategies"
    / "h4_h1_pullback_resolution_entry.py"
).read_text(encoding="utf-8")


def _load_settings(path: Path) -> Settings:
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    for key in ("campaign", "research_metadata", "financing", "data_provenance"):
        data.pop(key, None)
    data.setdefault("config_hash", compute_config_hash(raw))
    data.setdefault("config_source_path", str(path))
    return Settings.model_validate(data)


def _force_adx(monkeypatch: pytest.MonkeyPatch, value: float) -> None:
    """Pin the ADX indicator to a constant so the H4 strength gate is testable."""

    def fake_adx(high, low, close, n):
        return pd.Series(value, index=close.index, dtype=float)

    monkeypatch.setattr(f"{_MOD}.adx", fake_adx)


@pytest.fixture
def bullish_h4() -> CandleFrame:
    return CandleFrame.from_candles(
        "EUR_USD", "H4", _trending_candles(200, granularity="H4", minutes_step=240)
    )


# --- config identity (tests 1-3, 9) ------------------------------------------


def test_c023_frozen_config_loads() -> None:
    settings = _load_settings(_C023_YAML)
    assert settings.strategy.enabled == ["h4_h1_pullback_resolution_entry"]
    sc = settings.strategy.h4_h1_pullback_resolution_entry
    assert sc is not None
    assert sc.timeframe == "M15"
    assert sc.h4_adx_min == 22.0
    assert sc.adx_min == 18.0
    assert sc.atr_stop_multiple == 2.0


def test_c023_version_is_c023() -> None:
    sc = _load_settings(_C023_YAML).strategy.h4_h1_pullback_resolution_entry
    assert sc is not None
    assert sc.version == "0.1.0-c023"


def test_c023_trading_disabled() -> None:
    app = _load_settings(_C023_YAML).app
    assert app.trading_enabled is False
    assert app.allow_order_submission is False
    assert app.allow_live_trading is False


def test_approved_registry_empty() -> None:
    approved = yaml.safe_load(
        (_REPO_ROOT / "configs/approved_strategies.yaml").read_text(encoding="utf-8")
    )
    assert approved["approved"] == []


# --- provenance (tests 4-5) --------------------------------------------------


def test_c023_provenance_m1_derived_only() -> None:
    raw = yaml.safe_load(_C023_YAML.read_text(encoding="utf-8"))
    assert raw["data_provenance"] == _PROVENANCE
    validate_c022_data_provenance(raw["data_provenance"])  # must not raise


def test_c023_rejects_daily_keys() -> None:
    raw = yaml.safe_load(_C023_YAML.read_text(encoding="utf-8"))
    for forbidden in ("d1agg_context", "d1_context", "d1_source", "d1agg_source"):
        assert forbidden not in raw["data_provenance"]
    bad = dict(_PROVENANCE)
    bad["d1agg_context"] = "native_h4_derived_d1agg"
    with pytest.raises(ValueError, match="no daily layer"):
        validate_c022_data_provenance(bad)


# --- the only intentional delta: H4 ADX gate (tests 6-7) ----------------------


def test_c023_h4_bias_blocks_at_adx_21_9(
    monkeypatch: pytest.MonkeyPatch, bullish_h4: CandleFrame
) -> None:
    _force_adx(monkeypatch, 21.9)
    decision = bullish_h4.df.index[-1].to_pydatetime()
    bias, _ts, block = aligned_h4_bias(
        bullish_h4, decision, ema_fast_len=20, ema_slow_len=50, slope_bars=3,
        adx_len=14, adx_min=22.0,
    )
    assert block is None
    assert bias == "neutral"  # below the C023 gate -> no directional bias


def test_c023_h4_bias_passes_at_adx_22_0(
    monkeypatch: pytest.MonkeyPatch, bullish_h4: CandleFrame
) -> None:
    _force_adx(monkeypatch, 22.0)
    decision = bullish_h4.df.index[-1].to_pydatetime()
    bias, _ts, block = aligned_h4_bias(
        bullish_h4, decision, ema_fast_len=20, ema_slow_len=50, slope_bars=3,
        adx_len=14, adx_min=22.0,
    )
    assert block is None
    assert bias == "bullish"  # votes pass and ADX meets the C023 gate


def test_c022_h4_bias_passes_at_adx_20_0(
    monkeypatch: pytest.MonkeyPatch, bullish_h4: CandleFrame
) -> None:
    # The C022 gate (20.0) still admits a trend that the C023 gate would reject.
    _force_adx(monkeypatch, 21.0)
    decision = bullish_h4.df.index[-1].to_pydatetime()
    bias_c022, _, _ = aligned_h4_bias(
        bullish_h4, decision, ema_fast_len=20, ema_slow_len=50, slope_bars=3,
        adx_len=14, adx_min=20.0,
    )
    bias_c023, _, _ = aligned_h4_bias(
        bullish_h4, decision, ema_fast_len=20, ema_slow_len=50, slope_bars=3,
        adx_len=14, adx_min=22.0,
    )
    assert bias_c022 == "bullish"
    assert bias_c023 == "neutral"


# --- full-strategy parity: same data, only the threshold differs (test 8) -----


def _full_signal(
    monkeypatch: pytest.MonkeyPatch,
    eur_usd: Instrument,
    *,
    h4_adx_min: float,
    adx_value: float,
    version: str,
    campaign_id: str,
):
    _force_adx(monkeypatch, adx_value)
    m15 = _trending_candles(200)
    decision = m15[-1].time
    # H4 context warmed up at the decision time: 200 rising H4 bars ending at
    # the decision so the aligned H4 bar has valid EMAs and bullish votes.
    h4: list = []
    price = 1.0
    start = decision - timedelta(minutes=240 * 200)
    for i in range(201):
        o = price
        price += 0.0010
        h4.append(
            _make_candle(
                start + timedelta(minutes=240 * i),
                open_=o, high=price + 0.0002, low=price - 0.0002, close=price,
                granularity="H4",
            )
        )
    monkeypatch.setattr(
        f"{_MOD}.aligned_h1_pullback_holds",
        lambda *a, **k: (True, decision - timedelta(hours=1), None),
    )
    monkeypatch.setattr(
        f"{_MOD}.m15_pullback_and_reclaim", lambda **kw: (True, True, "test")
    )
    strat = H4H1PullbackResolutionEntryStrategy(
        version=version, campaign_id=campaign_id
    )
    cfg = {"adx_min": 0.0, "h4_adx_min": h4_adx_min}
    return strat.generate_signal(_ctx_from_m15(m15, cfg, eur_usd, h4=h4))


def test_threshold_is_sole_discriminator(
    monkeypatch: pytest.MonkeyPatch, eur_usd: Instrument
) -> None:
    # ADX 21.0 on identical data: C022 (gate 20) trades, C023 (gate 22) does not.
    c022 = _full_signal(
        monkeypatch, eur_usd, h4_adx_min=20.0, adx_value=21.0,
        version="0.1.0-c022", campaign_id="CAMPAIGN_022",
    )
    monkeypatch.undo()
    c023 = _full_signal(
        monkeypatch, eur_usd, h4_adx_min=22.0, adx_value=21.0,
        version="0.1.0-c023", campaign_id="CAMPAIGN_023",
    )
    assert c022 is not None and c022.campaign_id == "CAMPAIGN_022"
    assert c023 is None


def test_above_gate_signals_identical_except_identity(
    monkeypatch: pytest.MonkeyPatch, eur_usd: Instrument
) -> None:
    # ADX 30.0 clears both gates: signals must match except campaign_id/version.
    c022 = _full_signal(
        monkeypatch, eur_usd, h4_adx_min=20.0, adx_value=30.0,
        version="0.1.0-c022", campaign_id="CAMPAIGN_022",
    )
    monkeypatch.undo()
    c023 = _full_signal(
        monkeypatch, eur_usd, h4_adx_min=22.0, adx_value=30.0,
        version="0.1.0-c023", campaign_id="CAMPAIGN_023",
    )
    assert c022 is not None and c023 is not None
    assert c023.campaign_id == "CAMPAIGN_023"
    assert c023.strategy_version == "0.1.0-c023"
    # Everything that is strategy logic (not identity) is byte-for-byte equal.
    assert c023.side == c022.side
    assert c023.timeframe == c022.timeframe
    assert c023.entry_intent == c022.entry_intent
    assert c023.stop_model == c022.stop_model
    assert c023.stop_price == c022.stop_price
    assert c023.exit_model == c022.exit_model
    assert c023.features == c022.features
    # Identity fields are the intended difference.
    assert c022.campaign_id == "CAMPAIGN_022"
    assert c023.campaign_id != c022.campaign_id


# --- structural identity + freeze hygiene (tests 8, 10) -----------------------


def test_yaml_strategy_block_identical_except_threshold() -> None:
    c022 = yaml.safe_load(_C022_YAML.read_text(encoding="utf-8"))["strategy"][
        "h4_h1_pullback_resolution_entry"
    ]
    c023 = yaml.safe_load(_C023_YAML.read_text(encoding="utf-8"))["strategy"][
        "h4_h1_pullback_resolution_entry"
    ]
    diffs = {k for k in set(c022) | set(c023) if c022.get(k) != c023.get(k)}
    assert diffs == {"h4_adx_min", "version"}
    assert c022["h4_adx_min"] == 20.0
    assert c023["h4_adx_min"] == 22.0


def test_strategy_no_broker_imports() -> None:
    assert "forex_bot.broker" not in _STRATEGY_SOURCE
    assert "forex_bot.execution" not in _STRATEGY_SOURCE
    assert "forex_bot.loops" not in _STRATEGY_SOURCE
    assert "oanda" not in _STRATEGY_SOURCE.lower()
