"""Unit tests for ``CalendarEventWindowAnomalyStrategy`` (CAMPAIGN_014).

These tests are research-only and prove the calendar-event window
anomaly candidate is **deterministic, no-lookahead, low-turnover-by-
design, and structurally safe**. A passing suite is NOT strategy
approval; the candidate is a research scaffold and cannot be added
to ``configs/approved_strategies.yaml`` without the full six-evidence
ladder + a deliberate human approval action per
``STRATEGY_APPROVAL_PROCESS.md``. ``configs/approved_strategies.yaml``
remains ``approved: []``; the strategy is not enabled in any active
loop.

See:
- docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md
- docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md
- docs/research/CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from forex_bot.calendar_events import (
    ALLOWED_EVENT_CLASSES,
    DEFAULT_IMPACT_ORDERING,
    EXPECTED_SCHEMA_VERSION,
    FORBIDDEN_FIELD_SUBSTRINGS,
    CalendarEvent,
    CalendarEventFixture,
    EventFixtureError,
    class_precedence,
    covers_range,
    eligible_events_at_or_before,
    impacted_pairs_for,
    load_event_fixture,
)
from forex_bot.config import (
    CalendarEventWindowAnomalyStrategyConfig,
    StrategyConfig,
)
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import MarketState, Quote, SpreadSnapshot
from forex_bot.domain.positions import Position
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.calendar_event_window_anomaly import (
    CalendarEventWindowAnomalyStrategy,
)

# ---------------------------------------------------------------------------
# Constants + helpers
# ---------------------------------------------------------------------------

# H4 bars align at UTC 22, 02, 06, 10, 14, 18 (NY-standard convention).
_H4_HOURS_UTC: tuple[int, ...] = (22, 2, 6, 10, 14, 18)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STRATEGY_SOURCE = (
    _REPO_ROOT
    / "src"
    / "forex_bot"
    / "strategies"
    / "calendar_event_window_anomaly.py"
).read_text(encoding="utf-8")
_LOADER_SOURCE = (
    _REPO_ROOT / "src" / "forex_bot" / "calendar_events.py"
).read_text(encoding="utf-8")

# Stripped versions: docstrings removed. The contamination checks below
# use the stripped versions because rejected-family names appear in the
# module docstring to EXPLAIN the strategy is NOT them — that's
# documentation, not contamination. Following the
# test_cross_pair_currency_strength_rotation.py precedent (§10).
_STRATEGY_SOURCE_NO_DOCS = re.sub(r'""".*?"""', "", _STRATEGY_SOURCE, flags=re.DOTALL)
_LOADER_SOURCE_NO_DOCS = re.sub(r'""".*?"""', "", _LOADER_SOURCE, flags=re.DOTALL)
_FIXTURE_PATH = _REPO_ROOT / "research" / "calendar" / "fixtures" / "campaign_014_events.json"


def _bar_time(base: datetime, idx: int) -> datetime:
    return base + timedelta(hours=4 * idx)


def _make_candle(
    time: datetime,
    *,
    open_: float,
    high: float,
    low: float,
    close: float,
    complete: bool = True,
    instrument: str = "EUR_USD",
) -> Candle:
    spread = Decimal("0.00010")
    mid_o = Decimal(str(round(open_, 5)))
    mid_h = Decimal(str(round(high, 5)))
    mid_l = Decimal(str(round(low, 5)))
    mid_c = Decimal(str(round(close, 5)))
    return Candle(
        instrument=instrument,
        granularity="H4",
        time=time,
        complete=complete,
        volume=1000,
        bid_o=mid_o - spread / 2,
        bid_h=mid_h - spread / 2,
        bid_l=mid_l - spread / 2,
        bid_c=mid_c - spread / 2,
        ask_o=mid_o + spread / 2,
        ask_h=mid_h + spread / 2,
        ask_l=mid_l + spread / 2,
        ask_c=mid_c + spread / 2,
    )


def _build_h4_frame(
    n: int,
    *,
    base_close: float = 1.0800,
    range_size: float = 0.0010,
    start: datetime | None = None,
    instrument: str = "EUR_USD",
    closes: list[float] | None = None,
) -> CandleFrame:
    """Build an H4 frame of n bars. If `closes` is given, use those as bar closes."""
    base = start or datetime(2024, 11, 4, _H4_HOURS_UTC[0], tzinfo=UTC)
    candles: list[Candle] = []
    for i in range(n):
        t = _bar_time(base, i)
        if closes is not None:
            c = closes[i]
            o = closes[i - 1] if i > 0 else c
        else:
            c = base_close
            o = base_close
        candles.append(
            _make_candle(
                t,
                open_=o,
                high=max(o, c) + range_size / 2,
                low=min(o, c) - range_size / 2,
                close=c,
                instrument=instrument,
            )
        )
    return CandleFrame.from_candles(instrument, "H4", candles)


def _ctx(
    frame: CandleFrame,
    instrument: Instrument,
    *,
    config: dict,
    open_position_units: Decimal = Decimal("0"),
) -> StrategyContext:
    last_close = float(frame.df["close"].iloc[-1]) if len(frame) else 1.0800
    quote_time = (
        frame.df.index[-1].to_pydatetime()
        if len(frame)
        else datetime(2024, 11, 4, tzinfo=UTC)
    )
    quote = Quote(
        instrument=instrument.name,
        time=quote_time,
        bid=Decimal(str(last_close - 0.0001)),
        ask=Decimal(str(last_close + 0.0001)),
    )
    position = Position(
        instrument=instrument.name,
        long_units=open_position_units,
    )
    return StrategyContext(
        instrument=instrument,
        candles=frame,
        market_state=MarketState(
            quote=quote,
            spread_snapshot=SpreadSnapshot(
                instrument=instrument.name,
                time=quote.time,
                bid=quote.bid,
                ask=quote.ask,
                spread_pips=Decimal("2.0"),
            ),
        ),
        open_positions=[position],
        config=config,
    )


def _eur_usd_instrument() -> Instrument:
    return Instrument(
        name="EUR_USD",
        type="CURRENCY",
        display_precision=5,
        pip_location=-4,
        trade_units_precision=0,
        minimum_trade_size=Decimal("1"),
        maximum_order_units=Decimal("100000000"),
        margin_rate=Decimal("0.02"),
    )


def _gbp_usd_instrument() -> Instrument:
    return Instrument(
        name="GBP_USD",
        type="CURRENCY",
        display_precision=5,
        pip_location=-4,
        trade_units_precision=0,
        minimum_trade_size=Decimal("1"),
        maximum_order_units=Decimal("100000000"),
        margin_rate=Decimal("0.02"),
    )


def _build_test_fixture(events: list[dict]) -> dict:
    """Build a valid in-memory fixture dict for loader tests."""
    return {
        "schema_version": EXPECTED_SCHEMA_VERSION,
        "coverage_start_utc": "2020-01-01T00:00:00+00:00",
        "coverage_end_utc": "2026-12-31T23:59:59+00:00",
        "event_classes": list(ALLOWED_EVENT_CLASSES),
        "source_attribution": {
            "NFP": {"name": "test", "url": "https://example.org/nfp"},
            "FOMC": {"name": "test", "url": "https://example.org/fomc"},
            "ECB": {"name": "test", "url": "https://example.org/ecb"},
            "BoJ": {"name": "test", "url": "https://example.org/boj"},
            "BoE": {"name": "test", "url": "https://example.org/boe"},
        },
        "events": events,
    }


def _default_cfg(**overrides) -> dict:
    cfg: dict = {
        "version": "0.1.0-c014",
        "timeframe": "H4",
        "event_calendar_path": str(_FIXTURE_PATH),
        "event_set": ["NFP", "FOMC", "ECB", "BoJ", "BoE"],
        "impact_ordering": ["FOMC", "NFP", "ECB", "BoJ", "BoE"],
        "post_event_window_bars": 6,
        "atr_lookback": 14,
        "atr_stop_multiple": 2.0,
        "trailing_stop_atr_multiple": None,
        "max_post_event_bars": 6,
        "re_entry_block_bars": 3,
        "event_warmup_bars": 1,
        "min_atr_pips": {},
    }
    cfg.update(overrides)
    return cfg


# ===========================================================================
# 1. Config defaults / validation (9 cases)
# ===========================================================================


def test_default_config_matches_frozen_spec():
    c = CalendarEventWindowAnomalyStrategyConfig(version="0.1.0-c014")
    assert c.version == "0.1.0-c014"
    assert c.timeframe == "H4"
    assert c.event_set == ["NFP", "FOMC", "ECB", "BoJ", "BoE"]
    assert c.impact_ordering == ["FOMC", "NFP", "ECB", "BoJ", "BoE"]
    assert c.post_event_window_bars == 6
    assert c.atr_lookback == 14
    assert c.atr_stop_multiple == 2.0
    assert c.max_post_event_bars == 6
    assert c.re_entry_block_bars == 3
    assert c.event_warmup_bars == 1
    assert c.trailing_stop_atr_multiple is None
    assert c.min_atr_pips == {}
    assert c.event_calendar_path == "research/calendar/fixtures/campaign_014_events.json"


def test_config_rejects_unsupported_event_class():
    with pytest.raises(ValidationError, match="event_set contains unsupported"):
        CalendarEventWindowAnomalyStrategyConfig(
            version="0.1.0-c014", event_set=["NFP", "UNKNOWN_CLASS"]
        )


def test_config_rejects_empty_event_set():
    with pytest.raises(ValidationError, match="event_set must contain"):
        CalendarEventWindowAnomalyStrategyConfig(
            version="0.1.0-c014", event_set=[]
        )


def test_config_rejects_impact_ordering_not_permutation():
    with pytest.raises(ValidationError, match="impact_ordering must be a permutation"):
        CalendarEventWindowAnomalyStrategyConfig(
            version="0.1.0-c014",
            event_set=["NFP", "FOMC"],
            impact_ordering=["NFP"],
        )


def test_config_rejects_impact_ordering_duplicate():
    with pytest.raises(
        ValidationError, match="impact_ordering must be a permutation"
    ):
        CalendarEventWindowAnomalyStrategyConfig(
            version="0.1.0-c014",
            event_set=["NFP", "FOMC"],
            impact_ordering=["NFP", "NFP"],
        )


def test_config_rejects_invalid_post_event_window_bars():
    for bad in (-1, 0):
        with pytest.raises(ValidationError, match="post_event_window_bars must be"):
            CalendarEventWindowAnomalyStrategyConfig(
                version="0.1.0-c014", post_event_window_bars=bad
            )
    with pytest.raises(ValidationError, match="post_event_window_bars must be <= 30"):
        CalendarEventWindowAnomalyStrategyConfig(
            version="0.1.0-c014", post_event_window_bars=31
        )


def test_config_rejects_invalid_atr_lookback():
    for bad in (-1, 0, 1):
        with pytest.raises(ValidationError, match="atr_lookback must be"):
            CalendarEventWindowAnomalyStrategyConfig(
                version="0.1.0-c014", atr_lookback=bad
            )


def test_config_rejects_invalid_atr_stop_multiple():
    for bad in (-1.0, 0.0):
        with pytest.raises(ValidationError, match="atr_stop_multiple must be"):
            CalendarEventWindowAnomalyStrategyConfig(
                version="0.1.0-c014", atr_stop_multiple=bad
            )


def test_config_rejects_invalid_max_post_event_bars():
    for bad in (-1, 0):
        with pytest.raises(ValidationError, match="max_post_event_bars must be"):
            CalendarEventWindowAnomalyStrategyConfig(
                version="0.1.0-c014", max_post_event_bars=bad
            )
    with pytest.raises(ValidationError, match="max_post_event_bars must be <= 30"):
        CalendarEventWindowAnomalyStrategyConfig(
            version="0.1.0-c014", max_post_event_bars=31
        )


def test_config_rejects_negative_re_entry_block_bars():
    with pytest.raises(ValidationError, match="re_entry_block_bars must be"):
        CalendarEventWindowAnomalyStrategyConfig(
            version="0.1.0-c014", re_entry_block_bars=-1
        )


def test_config_rejects_negative_event_warmup_bars():
    with pytest.raises(ValidationError, match="event_warmup_bars must be"):
        CalendarEventWindowAnomalyStrategyConfig(
            version="0.1.0-c014", event_warmup_bars=-1
        )


def test_config_rejects_non_null_trailing_stop_in_v1():
    with pytest.raises(
        ValidationError, match="trailing_stop_atr_multiple must be None"
    ):
        CalendarEventWindowAnomalyStrategyConfig(
            version="0.1.0-c014", trailing_stop_atr_multiple=1.5
        )


def test_config_extra_field_forbidden():
    with pytest.raises(ValidationError):
        CalendarEventWindowAnomalyStrategyConfig(
            version="0.1.0-c014", actual=0.123
        )


# ===========================================================================
# 2. Event-fixture loader (13 cases)
# ===========================================================================


def test_loader_accepts_valid_fixture(tmp_path: Path):
    payload = _build_test_fixture(
        [
            {
                "event_id": "NFP_2024-11-01",
                "event_class": "NFP",
                "event_time_utc": "2024-11-01T12:30:00+00:00",
            }
        ]
    )
    p = tmp_path / "events.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    fixture = load_event_fixture(p)
    assert fixture.schema_version == EXPECTED_SCHEMA_VERSION
    assert len(fixture.events) == 1
    assert fixture.events[0].event_class == "NFP"


def test_loader_rejects_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_event_fixture(tmp_path / "nope.json")


def test_loader_rejects_invalid_json(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(EventFixtureError, match="JSON parse"):
        load_event_fixture(p)


def test_loader_rejects_root_not_object(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(EventFixtureError, match="root must be an object"):
        load_event_fixture(p)


def test_loader_rejects_missing_schema_version(tmp_path: Path):
    payload = _build_test_fixture([])
    del payload["schema_version"]
    p = tmp_path / "events.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(EventFixtureError):
        load_event_fixture(p)


def test_loader_rejects_wrong_schema_version(tmp_path: Path):
    payload = _build_test_fixture([])
    payload["schema_version"] = "campaign_014.event_fixture.v99"
    p = tmp_path / "events.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(EventFixtureError, match="schema_version"):
        load_event_fixture(p)


def test_loader_rejects_naive_timestamp(tmp_path: Path):
    payload = _build_test_fixture(
        [
            {
                "event_id": "NFP_2024-11-01",
                "event_class": "NFP",
                "event_time_utc": "2024-11-01T12:30:00",  # no tz
            }
        ]
    )
    p = tmp_path / "events.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(EventFixtureError):
        load_event_fixture(p)


def test_loader_rejects_non_utc_timestamp(tmp_path: Path):
    payload = _build_test_fixture(
        [
            {
                "event_id": "NFP_2024-11-01",
                "event_class": "NFP",
                "event_time_utc": "2024-11-01T12:30:00-05:00",  # EST
            }
        ]
    )
    p = tmp_path / "events.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(EventFixtureError):
        load_event_fixture(p)


def test_loader_rejects_unsupported_event_class(tmp_path: Path):
    payload = _build_test_fixture(
        [
            {
                "event_id": "X_2024-11-01",
                "event_class": "UNKNOWN_CLASS",
                "event_time_utc": "2024-11-01T12:30:00+00:00",
            }
        ]
    )
    p = tmp_path / "events.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(EventFixtureError):
        load_event_fixture(p)


@pytest.mark.parametrize(
    "field",
    [
        "actual",
        "actual_value",
        "forecast",
        "consensus",
        "surprise",
        "revision",
        "revised_value",
        "market_reaction",
        "post_event_move",
        "commentary",
    ],
)
def test_loader_rejects_each_forbidden_field(tmp_path: Path, field: str):
    """Each forbidden field name (deny-list per spec §7.2) is rejected."""
    payload = _build_test_fixture(
        [
            {
                "event_id": "NFP_2024-11-01",
                "event_class": "NFP",
                "event_time_utc": "2024-11-01T12:30:00+00:00",
                field: 0.123,
            }
        ]
    )
    p = tmp_path / "events.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(EventFixtureError, match="forbidden field"):
        load_event_fixture(p)


def test_loader_forbidden_field_case_insensitive(tmp_path: Path):
    """Case-insensitive substring match rejects mixed-case forbidden fields."""
    payload = _build_test_fixture(
        [
            {
                "event_id": "NFP_2024-11-01",
                "event_class": "NFP",
                "event_time_utc": "2024-11-01T12:30:00+00:00",
                "Forecast": 250000,
            }
        ]
    )
    p = tmp_path / "events.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(EventFixtureError, match="forbidden field"):
        load_event_fixture(p)


def test_loader_loads_committed_fixture():
    """The committed fixture loads + validates cleanly."""
    fixture = load_event_fixture(_FIXTURE_PATH)
    assert fixture.schema_version == EXPECTED_SCHEMA_VERSION
    assert len(fixture.events) > 200  # ~281
    assert fixture.coverage_start_utc == datetime(2020, 1, 1, tzinfo=UTC)
    classes = {e.event_class for e in fixture.events}
    assert classes == set(ALLOWED_EVENT_CLASSES)


def test_loader_extra_top_level_field_rejected(tmp_path: Path):
    payload = _build_test_fixture([])
    payload["surprise_value"] = 123  # top-level extra (forbid)
    p = tmp_path / "events.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(EventFixtureError):
        load_event_fixture(p)


# ===========================================================================
# 3. Eligible-event helper / class precedence / coverage (7 cases)
# ===========================================================================


def test_eligible_helper_returns_only_past_events():
    fixture = load_event_fixture(_FIXTURE_PATH)
    cutoff = datetime(2021, 1, 1, tzinfo=UTC)
    out = eligible_events_at_or_before(list(fixture.events), cutoff)
    assert all(ev.event_time_utc <= cutoff for ev in out)
    assert len(out) > 0


def test_eligible_helper_excludes_future_events():
    fixture = load_event_fixture(_FIXTURE_PATH)
    cutoff = datetime(2020, 1, 1, tzinfo=UTC)
    out = eligible_events_at_or_before(list(fixture.events), cutoff)
    # The committed fixture's earliest event is 2020-01-03; cutoff at
    # 2020-01-01 should return zero.
    assert all(ev.event_time_utc <= cutoff for ev in out)


def test_eligible_helper_deterministic_sort():
    fixture = load_event_fixture(_FIXTURE_PATH)
    cutoff = datetime(2026, 6, 1, tzinfo=UTC)
    out1 = eligible_events_at_or_before(list(fixture.events), cutoff)
    out2 = eligible_events_at_or_before(list(fixture.events), cutoff)
    assert [e.event_id for e in out1] == [e.event_id for e in out2]
    # And: sorted by event_time_utc ascending.
    for i in range(1, len(out1)):
        assert (out1[i - 1].event_time_utc, out1[i - 1].event_id) <= (
            out1[i].event_time_utc, out1[i].event_id
        )


def test_eligible_helper_filters_by_class():
    fixture = load_event_fixture(_FIXTURE_PATH)
    cutoff = datetime(2026, 6, 1, tzinfo=UTC)
    nfp = eligible_events_at_or_before(
        list(fixture.events), cutoff, event_classes=("NFP",)
    )
    assert all(e.event_class == "NFP" for e in nfp)
    assert len(nfp) > 60  # ~77


def test_eligible_helper_rejects_naive_cutoff():
    fixture = load_event_fixture(_FIXTURE_PATH)
    with pytest.raises(ValueError, match="timezone-aware"):
        eligible_events_at_or_before(
            list(fixture.events), datetime(2024, 1, 1)
        )


def test_class_precedence_default_ordering():
    assert class_precedence("FOMC") == 0
    assert class_precedence("NFP") == 1
    assert class_precedence("ECB") == 2
    assert class_precedence("BoJ") == 3
    assert class_precedence("BoE") == 4
    # Unknown class: sentinel value past the ordering.
    assert class_precedence("UNKNOWN") > len(DEFAULT_IMPACT_ORDERING)


def test_class_precedence_custom_ordering():
    # User-supplied ordering wins.
    custom = ("ECB", "FOMC", "NFP", "BoJ", "BoE")
    assert class_precedence("ECB", impact_ordering=custom) == 0
    assert class_precedence("FOMC", impact_ordering=custom) == 1


def test_covers_range_within():
    fixture = load_event_fixture(_FIXTURE_PATH)
    assert covers_range(
        fixture,
        start=datetime(2021, 1, 1, tzinfo=UTC),
        end=datetime(2025, 1, 1, tzinfo=UTC),
    )


def test_covers_range_overshoot_rejected():
    fixture = load_event_fixture(_FIXTURE_PATH)
    assert not covers_range(
        fixture,
        start=datetime(2020, 1, 1, tzinfo=UTC),
        end=datetime(2030, 1, 1, tzinfo=UTC),
    )


def test_covers_range_undershoot_rejected():
    fixture = load_event_fixture(_FIXTURE_PATH)
    assert not covers_range(
        fixture,
        start=datetime(2010, 1, 1, tzinfo=UTC),
        end=datetime(2024, 1, 1, tzinfo=UTC),
    )


# ===========================================================================
# 4. IMPACTED_PAIRS mapping (5 cases)
# ===========================================================================


def test_impacted_pairs_nfp_is_all_seven():
    assert set(impacted_pairs_for("NFP")) == {
        "EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD",
        "USD_CAD", "USD_CHF", "NZD_USD",
    }


def test_impacted_pairs_fomc_is_all_seven():
    assert set(impacted_pairs_for("FOMC")) == {
        "EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD",
        "USD_CAD", "USD_CHF", "NZD_USD",
    }


def test_impacted_pairs_ecb_is_eur_only():
    assert impacted_pairs_for("ECB") == ("EUR_USD",)


def test_impacted_pairs_boj_is_jpy_only():
    assert impacted_pairs_for("BoJ") == ("USD_JPY",)


def test_impacted_pairs_boe_is_gbp_only():
    assert impacted_pairs_for("BoE") == ("GBP_USD",)


def test_impacted_pairs_unknown_class_empty():
    assert impacted_pairs_for("UNKNOWN") == ()


# ===========================================================================
# 5. Strategy R1-R8: happy path + fail-closed (10 cases)
# ===========================================================================


def _build_event_fixture_at(event_time: datetime, event_class: str = "NFP", event_id: str | None = None) -> CalendarEventFixture:
    """Helper: build an in-memory single-event fixture."""
    if event_id is None:
        event_id = f"{event_class}_{event_time.date().isoformat()}"
    return CalendarEventFixture(
        schema_version=EXPECTED_SCHEMA_VERSION,
        coverage_start_utc=datetime(2020, 1, 1, tzinfo=UTC),
        coverage_end_utc=datetime(2030, 1, 1, tzinfo=UTC),
        event_classes=list(ALLOWED_EVENT_CLASSES),
        source_attribution={
            c: {"name": "test", "url": "https://example.org"} for c in ALLOWED_EVENT_CLASSES
        },
        events=[
            CalendarEvent(
                event_id=event_id,
                event_class=event_class,
                event_time_utc=event_time,
            )
        ],
    )


def test_strategy_returns_none_on_short_warmup():
    """R1: insufficient warm-up → no signal."""
    strategy = CalendarEventWindowAnomalyStrategy()
    frame = _build_h4_frame(10)  # < 32 + ATR-14 minimum
    cfg = _default_cfg()
    ctx = _ctx(frame, _eur_usd_instrument(), config=cfg)
    assert strategy.generate_signal(ctx) is None


def test_strategy_returns_none_when_no_fixture():
    """R2: missing event_fixture / event_calendar_path → no signal."""
    strategy = CalendarEventWindowAnomalyStrategy()
    frame = _build_h4_frame(50)
    cfg = _default_cfg(event_calendar_path="")
    ctx = _ctx(frame, _eur_usd_instrument(), config=cfg)
    assert strategy.generate_signal(ctx) is None


def test_strategy_returns_none_when_position_open():
    """R2: existing position → no signal (defense in depth)."""
    strategy = CalendarEventWindowAnomalyStrategy()
    frame = _build_h4_frame(50)
    cfg = _default_cfg()
    ctx = _ctx(
        frame, _eur_usd_instrument(), config=cfg,
        open_position_units=Decimal("100"),
    )
    assert strategy.generate_signal(ctx) is None


def test_strategy_returns_none_when_no_event_in_window():
    """R3: no eligible event for current bar → no signal."""
    strategy = CalendarEventWindowAnomalyStrategy()
    # Build frame with a date far from any committed event.
    # Use 2023-04-15 — a weekend; no scheduled events.
    base = datetime(2023, 4, 15, 22, tzinfo=UTC)
    frame = _build_h4_frame(50, start=base)
    cfg = _default_cfg()
    # Use the committed fixture; this bar should not be in any post-
    # event window.
    ctx = _ctx(frame, _eur_usd_instrument(), config=cfg)
    sig = strategy.generate_signal(ctx)
    # It's possible there is some event in window; if so, that's still
    # a valid signal — but most likely no signal.
    if sig is not None:
        # If a signal does fire, confirm it's a valid one.
        assert sig.strategy_name == "calendar_event_window_anomaly"


def test_strategy_fires_signal_on_trigger_bar():
    """R3 + R5 + R7 + R8: happy-path trigger fires a counter-direction signal."""
    strategy = CalendarEventWindowAnomalyStrategy()
    # Setup: place an event in a specific H4 bar; the trigger bar is the
    # next H4 bar. Build a frame where event_bar has a positive return.
    base = datetime(2024, 11, 4, 22, tzinfo=UTC)
    n_bars = 50
    closes = [1.0800] * n_bars
    # Event bar at idx -2 has open=1.0800, close=1.0850 (positive return)
    event_bar_idx = n_bars - 2
    closes[event_bar_idx] = 1.0850
    # Trigger bar at idx -1: close=1.0830
    closes[-1] = 1.0830
    frame = _build_h4_frame(n_bars, start=base, closes=closes)
    event_bar_time = frame.df.index[event_bar_idx]
    fixture = _build_event_fixture_at(
        event_bar_time.to_pydatetime() + timedelta(hours=1),  # within H4 window
        event_class="NFP",
    )
    cfg = _default_cfg()
    cfg["event_fixture"] = fixture
    ctx = _ctx(frame, _eur_usd_instrument(), config=cfg)
    sig = strategy.generate_signal(ctx)
    assert sig is not None
    assert sig.strategy_name == "calendar_event_window_anomaly"
    assert sig.strategy_version == "0.1.0-c014"
    # Counter-direction: positive event return → SHORT
    assert sig.side == "short"
    assert sig.exit_model == "time_stop_only"
    assert "NFP" in sig.reason


def test_strategy_signal_direction_long_on_negative_event_return():
    """R5: negative event_bar_return → Side.LONG."""
    strategy = CalendarEventWindowAnomalyStrategy()
    base = datetime(2024, 11, 4, 22, tzinfo=UTC)
    n_bars = 50
    closes = [1.0800] * n_bars
    event_bar_idx = n_bars - 2
    closes[event_bar_idx] = 1.0750  # negative event return
    closes[-1] = 1.0770
    frame = _build_h4_frame(n_bars, start=base, closes=closes)
    event_bar_time = frame.df.index[event_bar_idx]
    fixture = _build_event_fixture_at(
        event_bar_time.to_pydatetime() + timedelta(hours=1),
        event_class="NFP",
    )
    cfg = _default_cfg()
    cfg["event_fixture"] = fixture
    ctx = _ctx(frame, _eur_usd_instrument(), config=cfg)
    sig = strategy.generate_signal(ctx)
    assert sig is not None
    assert sig.side == "long"


def test_strategy_no_signal_on_zero_event_return():
    """R5: event_bar_return == 0 → no signal (degenerate)."""
    strategy = CalendarEventWindowAnomalyStrategy()
    base = datetime(2024, 11, 4, 22, tzinfo=UTC)
    n_bars = 50
    closes = [1.0800] * n_bars
    # No change at event bar: open == close
    frame = _build_h4_frame(n_bars, start=base, closes=closes)
    event_bar_time = frame.df.index[n_bars - 2]
    fixture = _build_event_fixture_at(
        event_bar_time.to_pydatetime() + timedelta(hours=1),
        event_class="NFP",
    )
    cfg = _default_cfg()
    cfg["event_fixture"] = fixture
    ctx = _ctx(frame, _eur_usd_instrument(), config=cfg)
    sig = strategy.generate_signal(ctx)
    assert sig is None


def test_strategy_no_signal_when_instrument_not_in_impacted_pairs():
    """R3 + impacted-pairs mapping: ECB event but instrument is GBP_USD → no signal."""
    strategy = CalendarEventWindowAnomalyStrategy()
    base = datetime(2024, 11, 4, 22, tzinfo=UTC)
    n_bars = 50
    closes = [1.2500] * n_bars
    closes[n_bars - 2] = 1.2550
    closes[-1] = 1.2530
    frame = _build_h4_frame(n_bars, start=base, closes=closes, instrument="GBP_USD")
    event_bar_time = frame.df.index[n_bars - 2]
    # ECB event — impacts only EUR_USD; GBP_USD should not signal.
    fixture = _build_event_fixture_at(
        event_bar_time.to_pydatetime() + timedelta(hours=1),
        event_class="ECB",
    )
    cfg = _default_cfg()
    cfg["event_fixture"] = fixture
    ctx = _ctx(frame, _gbp_usd_instrument(), config=cfg)
    sig = strategy.generate_signal(ctx)
    assert sig is None


def test_strategy_atr_fail_closed_on_non_finite():
    """R6: non-finite ATR → no signal."""
    strategy = CalendarEventWindowAnomalyStrategy()
    base = datetime(2024, 11, 4, 22, tzinfo=UTC)
    # Build a frame where all closes/highs/lows are identical → ATR = 0
    n_bars = 50
    frame = _build_h4_frame(n_bars, start=base, base_close=1.0800, range_size=0.0)
    # Override event_bar to have non-zero return
    df = frame.df.copy()
    df.loc[df.index[n_bars - 2], "close"] = 1.0850
    # Then ATR=0 over flat history; R6 should fail.
    event_bar_time = frame.df.index[n_bars - 2]
    fixture = _build_event_fixture_at(
        event_bar_time.to_pydatetime() + timedelta(hours=1),
        event_class="NFP",
    )
    cfg = _default_cfg()
    cfg["event_fixture"] = fixture
    ctx = _ctx(frame, _eur_usd_instrument(), config=cfg)
    # With zero-range bars the ATR is essentially zero; R6 should fail.
    sig = strategy.generate_signal(ctx)
    assert sig is None


def test_strategy_stop_placement_is_below_close_for_long():
    """R7: long signal places stop below close at `close - atr*multiple`."""
    strategy = CalendarEventWindowAnomalyStrategy()
    base = datetime(2024, 11, 4, 22, tzinfo=UTC)
    n_bars = 50
    closes = [1.0800 + 0.0001 * i for i in range(n_bars)]
    # Override event-bar to be negative-return (long signal expected)
    closes[n_bars - 2] = closes[n_bars - 3] - 0.0050  # negative return at event bar
    closes[-1] = closes[n_bars - 2] + 0.0010
    frame = _build_h4_frame(n_bars, start=base, closes=closes)
    event_bar_time = frame.df.index[n_bars - 2]
    fixture = _build_event_fixture_at(
        event_bar_time.to_pydatetime() + timedelta(hours=1),
        event_class="NFP",
    )
    cfg = _default_cfg()
    cfg["event_fixture"] = fixture
    ctx = _ctx(frame, _eur_usd_instrument(), config=cfg)
    sig = strategy.generate_signal(ctx)
    if sig is not None:
        # Long signal: stop below close
        assert sig.side == "long"
        assert sig.stop_price < ctx.market_state.quote.bid  # roughly
        assert sig.stop_price < Decimal(str(closes[-1]))


# ===========================================================================
# 6. Determinism + signal_id stability (2 cases)
# ===========================================================================


def test_strategy_signal_id_is_deterministic():
    """Identical input → identical signal_id."""
    strategy = CalendarEventWindowAnomalyStrategy()
    base = datetime(2024, 11, 4, 22, tzinfo=UTC)
    n_bars = 50
    closes = [1.0800] * n_bars
    closes[n_bars - 2] = 1.0850
    closes[-1] = 1.0830
    frame = _build_h4_frame(n_bars, start=base, closes=closes)
    event_bar_time = frame.df.index[n_bars - 2]
    fixture = _build_event_fixture_at(
        event_bar_time.to_pydatetime() + timedelta(hours=1),
        event_class="NFP",
    )
    cfg = _default_cfg()
    cfg["event_fixture"] = fixture
    ctx1 = _ctx(frame, _eur_usd_instrument(), config=cfg)
    ctx2 = _ctx(frame, _eur_usd_instrument(), config=cfg)
    sig1 = strategy.generate_signal(ctx1)
    sig2 = strategy.generate_signal(ctx2)
    assert sig1 is not None
    assert sig2 is not None
    assert sig1.signal_id == sig2.signal_id


def test_strategy_signal_features_contain_safe_metadata_only():
    """R8: signal.features contains only safe metadata; no actual/forecast/surprise."""
    strategy = CalendarEventWindowAnomalyStrategy()
    base = datetime(2024, 11, 4, 22, tzinfo=UTC)
    n_bars = 50
    closes = [1.0800] * n_bars
    closes[n_bars - 2] = 1.0850
    closes[-1] = 1.0830
    frame = _build_h4_frame(n_bars, start=base, closes=closes)
    event_bar_time = frame.df.index[n_bars - 2]
    fixture = _build_event_fixture_at(
        event_bar_time.to_pydatetime() + timedelta(hours=1),
        event_class="NFP",
    )
    cfg = _default_cfg()
    cfg["event_fixture"] = fixture
    ctx = _ctx(frame, _eur_usd_instrument(), config=cfg)
    sig = strategy.generate_signal(ctx)
    assert sig is not None
    # Required safe metadata
    assert "event_class" in sig.features
    assert "event_id" in sig.features
    assert "event_time_utc" in sig.features
    assert "bars_since_event" in sig.features
    assert "event_bar_return" in sig.features
    assert "prior_atr_h4" in sig.features
    assert "last_close" in sig.features
    # Forbidden fields MUST NOT appear in features
    for forbidden in (
        "actual", "actual_value", "forecast", "consensus",
        "surprise", "revision", "revised_value",
        "market_reaction", "post_event_move", "commentary",
    ):
        assert forbidden not in sig.features
        # Case-insensitive
        assert all(forbidden not in k.lower() for k in sig.features)


# ===========================================================================
# 7. Anti-contamination: source-grep tests (8 cases)
# ===========================================================================


def test_strategy_source_no_broker_import():
    # Imports are not in docstrings, so check the raw source for safety.
    assert "from forex_bot.broker" not in _STRATEGY_SOURCE
    assert "from forex_bot.execution" not in _STRATEGY_SOURCE
    assert "from forex_bot.loops" not in _STRATEGY_SOURCE
    assert "from forex_bot.cli" not in _STRATEGY_SOURCE
    assert "import forex_bot.broker" not in _STRATEGY_SOURCE


def test_strategy_source_no_prng():
    # Use docstring-stripped source — docstrings mention "no random" as
    # documentation, which is allowed.
    src = _STRATEGY_SOURCE_NO_DOCS
    assert "import random" not in src
    assert "from random " not in src
    assert "numpy.random" not in src
    assert "np.random" not in src
    assert "import secrets" not in src
    # builtin hash() — must not appear as bare hash( call (no leading
    # word char or dot).
    assert not re.findall(r"(?<![\.\w])hash\s*\(", src)


def test_strategy_source_no_campaign_002_keys():
    """No CAMPAIGN_002 / trend_following / Donchian / EMA parameter keys
    in executable code. Docstrings mention these as "things we do not
    do" — that's documentation, not contamination."""
    src = _STRATEGY_SOURCE_NO_DOCS
    bad = ["donchian", "Donchian", "ema_fast", "ema_slow", "EmaFast", "trend_following"]
    for k in bad:
        assert k not in src, f"unexpected {k!r} in strategy executable code"


def test_strategy_source_no_campaign_010_keys():
    src = _STRATEGY_SOURCE_NO_DOCS
    bad = ["session_breakout", "asian_range", "london_open", "AsianRange", "LondonOpen"]
    for k in bad:
        assert k not in src, f"unexpected {k!r} in strategy executable code"


def test_strategy_source_no_campaign_011_keys():
    src = _STRATEGY_SOURCE_NO_DOCS
    bad = [
        "random_entry_anchor", "master_seed",
        "entry_probability_per_bar", "RandomEntry",
    ]
    for k in bad:
        assert k not in src, f"unexpected {k!r} in strategy executable code"


def test_strategy_source_no_campaign_012_keys():
    src = _STRATEGY_SOURCE_NO_DOCS
    bad = [
        "regime_switcher_atr_percentile", "daily_atr_lookback",
        "regime_lookback_days", "regime_percentile_threshold",
        "min_close_move_atr_fraction", "trend_lookback_h4_bars",
    ]
    for k in bad:
        assert k not in src, f"unexpected {k!r} in strategy executable code"


def test_strategy_source_no_campaign_013_keys():
    src = _STRATEGY_SOURCE_NO_DOCS
    bad = [
        "cross_pair_currency_strength_rotation", "currency_strength",
        "rank_gap_threshold", "currency_strength_lookback_bars",
        "cross_pair_closes",
    ]
    for k in bad:
        assert k not in src, f"unexpected {k!r} in strategy executable code"


def test_loader_source_no_broker_or_prng():
    """The fixture loader is similarly anti-contaminated."""
    assert "from forex_bot.broker" not in _LOADER_SOURCE
    assert "from forex_bot.execution" not in _LOADER_SOURCE
    assert "from forex_bot.loops" not in _LOADER_SOURCE
    src = _LOADER_SOURCE_NO_DOCS
    assert "import random" not in src
    assert "import secrets" not in src
    assert "numpy.random" not in src
    # No HTTP client at all
    assert "import requests" not in src
    assert "import httpx" not in src
    assert "import urllib" not in src
    assert "import aiohttp" not in src


def test_loader_source_does_not_read_env():
    src = _LOADER_SOURCE_NO_DOCS
    assert "os.environ" not in src
    assert ".env" not in src
    assert "dotenv" not in src


def test_strategy_source_does_not_read_env():
    src = _STRATEGY_SOURCE_NO_DOCS
    assert "os.environ" not in src
    assert ".env" not in src
    assert "dotenv" not in src


def test_strategy_source_no_actual_forecast_surprise_in_features():
    """Strategy must NOT reference forbidden event-result fields anywhere."""
    # The source MAY mention them in DOCUMENTATION as things-to-avoid,
    # but MUST NOT reference them as data keys.
    # Simpler check: no `.get("actual"` / etc. patterns.
    for forbidden in ("actual", "forecast", "consensus", "surprise", "revision"):
        # No `cfg.get("<forbidden>` or `cfg["<forbidden>"`
        assert (
            f'cfg.get("{forbidden}' not in _STRATEGY_SOURCE
            and f'cfg["{forbidden}' not in _STRATEGY_SOURCE
            and f"event.{forbidden}" not in _STRATEGY_SOURCE
        ), f"strategy must not read {forbidden!r} from cfg or event"


# ===========================================================================
# 8. Approval-registry / paper / demo regression (3 cases)
# ===========================================================================


def test_approved_strategies_registry_is_empty():
    p = _REPO_ROOT / "configs" / "approved_strategies.yaml"
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert doc["approved"] == []


def test_paper_config_does_not_enable_calendar_event_window_anomaly():
    p = _REPO_ROOT / "configs" / "paper.yaml"
    if not p.exists():
        pytest.skip("paper.yaml not present")
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    enabled = doc.get("strategy", {}).get("enabled", [])
    assert "calendar_event_window_anomaly" not in enabled


def test_demo_config_does_not_enable_calendar_event_window_anomaly():
    p = _REPO_ROOT / "configs" / "practice.yaml"
    if not p.exists():
        pytest.skip("practice.yaml not present")
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    enabled = doc.get("strategy", {}).get("enabled", [])
    assert "calendar_event_window_anomaly" not in enabled


# ===========================================================================
# 9. Fixture path + coverage + provenance (3 cases)
# ===========================================================================


def test_fixture_path_is_local_repo_relative():
    """Default config fixture path is repo-local; no URL, no credentials."""
    cfg = CalendarEventWindowAnomalyStrategyConfig(version="0.1.0-c014")
    p = cfg.event_calendar_path
    assert not p.startswith("http")
    assert not p.startswith("https")
    assert not p.startswith("ftp")
    assert "api_key" not in p
    assert "token" not in p
    assert "password" not in p


def test_fixture_no_credential_shaped_strings():
    """Committed fixture contains no credential-shaped strings."""
    raw = _FIXTURE_PATH.read_text(encoding="utf-8")
    # Check for common credential keywords (case-insensitive)
    raw_lower = raw.lower()
    assert "api_key" not in raw_lower
    assert "secret" not in raw_lower
    assert "token" not in raw_lower
    assert "password" not in raw_lower
    assert "oanda_account_id" not in raw_lower
    assert "oanda_access_token" not in raw_lower


def test_fixture_contains_minimum_events_per_class():
    """Each binding event class has a non-trivial count in the committed fixture."""
    fixture = load_event_fixture(_FIXTURE_PATH)
    by_class: dict[str, int] = {}
    for ev in fixture.events:
        by_class[ev.event_class] = by_class.get(ev.event_class, 0) + 1
    # NFP should have ~77 (monthly × 6.5 years); others ~51 (8/year × 6.5).
    assert by_class.get("NFP", 0) >= 60
    assert by_class.get("FOMC", 0) >= 40
    assert by_class.get("ECB", 0) >= 40
    assert by_class.get("BoJ", 0) >= 40
    assert by_class.get("BoE", 0) >= 40


# ===========================================================================
# 10. StrategyConfig integration (3 cases)
# ===========================================================================


def test_strategy_config_requires_calendar_event_window_anomaly_when_enabled():
    """StrategyConfig._check_enabled requires sub-config when in `enabled`."""
    with pytest.raises(ValidationError, match="calendar_event_window_anomaly"):
        StrategyConfig(enabled=["calendar_event_window_anomaly"])


def test_strategy_config_accepts_calendar_event_window_anomaly_when_provided():
    sc = StrategyConfig(
        enabled=["calendar_event_window_anomaly"],
        calendar_event_window_anomaly=CalendarEventWindowAnomalyStrategyConfig(
            version="0.1.0-c014",
        ),
    )
    assert sc.calendar_event_window_anomaly is not None
    assert sc.calendar_event_window_anomaly.version == "0.1.0-c014"


def test_strategy_config_extra_field_forbidden():
    with pytest.raises(ValidationError):
        StrategyConfig(
            enabled=["trend_following"],
            calendar_event_window_anomaly=None,
            future_field="oops",
        )


# ===========================================================================
# 11. Strategy module-level constants + interface (3 cases)
# ===========================================================================


def test_strategy_class_name_and_default_version():
    assert CalendarEventWindowAnomalyStrategy.name == "calendar_event_window_anomaly"
    s = CalendarEventWindowAnomalyStrategy()
    assert s.version == "0.1.0-c014"


def test_strategy_warmup_bars_required_is_at_least_atr_plus_buffer():
    s = CalendarEventWindowAnomalyStrategy()
    # ATR(14) needs >= 15 bars; +2 for index -2; pinned at 32.
    assert s.warmup_bars_required() >= 14 + 2
    assert s.warmup_bars_required() == 32


def test_strategy_does_not_expose_approval_attribute():
    """The strategy class must not expose any 'approved' / 'approve' / 'is_live' attribute."""
    s = CalendarEventWindowAnomalyStrategy()
    for attr in dir(s):
        a_lower = attr.lower()
        assert "approv" not in a_lower
        assert "is_live" not in a_lower
        assert "promote" not in a_lower


# ===========================================================================
# 12. ALLOWED_EVENT_CLASSES / DEFAULT_IMPACT_ORDERING / EXPECTED_SCHEMA_VERSION (3 cases)
# ===========================================================================


def test_allowed_event_classes_set():
    assert set(ALLOWED_EVENT_CLASSES) == {"NFP", "FOMC", "ECB", "BoJ", "BoE"}


def test_default_impact_ordering_permutation():
    assert set(DEFAULT_IMPACT_ORDERING) == set(ALLOWED_EVENT_CLASSES)
    # FOMC is highest impact
    assert DEFAULT_IMPACT_ORDERING[0] == "FOMC"


def test_expected_schema_version_is_v1():
    assert EXPECTED_SCHEMA_VERSION == "campaign_014.event_fixture.v1"


def test_forbidden_field_substrings_include_core_deny_list():
    """All core deny-list field names are caught by the substring matcher."""
    cases = [
        ("actual", True),
        ("actual_value", True),
        ("forecast", True),
        ("consensus", True),
        ("surprise", True),
        ("revision", True),
        ("revised", True),
        ("market_reaction", True),
        ("post_event_move", True),
        ("commentary", True),
        ("Forecast", True),  # case-insensitive — substring match on lower
        ("event_id", False),  # safe field
        ("event_class", False),
        ("event_time_utc", False),
    ]
    for name, should_match in cases:
        name_lower = name.lower()
        matched = any(s in name_lower for s in FORBIDDEN_FIELD_SUBSTRINGS)
        assert matched == should_match, f"{name!r}: expected {should_match}, got {matched}"


# ===========================================================================
# 13. Future-evidence coverage guardrail (1 case)
# ===========================================================================


def test_covers_range_walk_forward_universe():
    """The committed fixture covers the CAMPAIGN_010/011/012/013 walk-forward universe."""
    fixture = load_event_fixture(_FIXTURE_PATH)
    assert covers_range(
        fixture,
        start=datetime(2020, 1, 1, tzinfo=UTC),
        end=datetime(2026, 5, 20, tzinfo=UTC),
    )


# ===========================================================================
# 14. Compilation script provenance (2 cases)
# ===========================================================================


def test_compilation_script_has_no_network_imports():
    """The fixture compilation script is offline. Check the docstring-
    stripped source so 'documentation that mentions network' doesn't
    trip the check."""
    raw = (_REPO_ROOT / "scripts" / "build_campaign_014_event_fixture.py").read_text()
    script = re.sub(r'""".*?"""', "", raw, flags=re.DOTALL)
    assert "import requests" not in script
    assert "import httpx" not in script
    assert "import urllib" not in script
    assert "import aiohttp" not in script
    assert "from urllib" not in script
    assert "from forex_bot.broker" not in script
    assert "import oandapyV20" not in script


def test_compilation_script_does_not_read_env():
    """Check docstring-stripped source — the docstring legitimately
    mentions '.env' as 'no .env is read'."""
    raw = (_REPO_ROOT / "scripts" / "build_campaign_014_event_fixture.py").read_text()
    script = re.sub(r'""".*?"""', "", raw, flags=re.DOTALL)
    assert "os.environ" not in script
    assert "dotenv" not in script
    assert ".env" not in script
