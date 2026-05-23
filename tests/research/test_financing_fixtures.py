"""Tests for the fixture loader and reconciliation against the
calculator. Covers: determinism, validation, naive timestamp
rejection, sign preservation, Wednesday triple-swap, missing
rate fallback, calculator reconciliation, strategy_evidence
rail, and import isolation."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from research.financing import (
    FinancingCalculatorConfig,
    FinancingTreatment,
    FixtureValidationError,
    MissingRatePolicy,
    PositionInterval,
    calculate_position,
    calculate_run,
    canonical_event_key,
    load_observed_event_fixture,
    load_rate_fixture,
    utc_date_of,
)

FIXTURES = Path(__file__).resolve().parents[2] / "research" / "financing" / "fixtures"


def _utc(y: int, m: int, d: int, h: int = 12) -> datetime:
    return datetime(y, m, d, h, 0, tzinfo=UTC)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(tmp_path: Path, payload: dict, name: str = "fixture.json") -> Path:
    p = tmp_path / name
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return p


# ---------- Committed fixtures load deterministically ----------


def test_every_committed_event_fixture_loads() -> None:
    """Every committed observed-events fixture loads without error
    and obeys the deterministic-sort invariant."""
    for path in sorted(FIXTURES.glob("observed_*.json")):
        events = load_observed_event_fixture(path)
        # Sort invariant: re-loaded list equals itself when re-sorted.
        keyed = [(e["time"], e["instrument"] or "", e["trade_id"] or "") for e in events]
        assert keyed == sorted(keyed), f"{path}: not sorted by (time, instrument, trade_id)"


def test_rates_fixture_loads_with_missing_dates() -> None:
    src, missing = load_rate_fixture(FIXTURES / "rates_two_week_eur_usd.json")
    assert src.treatment == FinancingTreatment.ESTIMATED
    assert missing == [date(2026, 5, 19)]
    # Spot-check one row.
    pair = src.rate_for(date(2026, 5, 18), "EUR_USD")
    assert pair is not None
    assert pair.long_annual_bp == pytest.approx(-18.25)
    assert pair.short_annual_bp == pytest.approx(9.125)


def test_event_fixture_load_is_deterministic() -> None:
    a = load_observed_event_fixture(FIXTURES / "observed_multi_day_with_triple.json")
    b = load_observed_event_fixture(FIXTURES / "observed_multi_day_with_triple.json")
    assert a == b


def test_rate_fixture_load_is_deterministic() -> None:
    src_a, miss_a = load_rate_fixture(FIXTURES / "rates_two_week_eur_usd.json")
    src_b, miss_b = load_rate_fixture(FIXTURES / "rates_two_week_eur_usd.json")
    # TableRateSource doesn't define __eq__; compare rate lookups across the table.
    for d in (date(2026, 5, 18), date(2026, 5, 20), date(2026, 5, 29)):
        assert src_a.rate_for(d, "EUR_USD") == src_b.rate_for(d, "EUR_USD")
    assert miss_a == miss_b


def test_same_day_no_rollover_fixture_is_empty() -> None:
    events = load_observed_event_fixture(FIXTURES / "observed_same_day_no_rollover.json")
    assert events == []


# ---------- Schema and validation rails ----------


def _baseline_event_payload() -> dict:
    return {
        "kind": "observed_financing_events",
        "schema_version": 1,
        "synthetic": True,
        "provenance": "test",
        "account_currency": "USD",
        "account_id_hash": "c4e91d9f7c03827938cbb2c82608bba023e98f23d52b2f84784cbcf9652df69f",
        "events": [],
    }


def _baseline_rate_payload() -> dict:
    return {
        "kind": "financing_rates",
        "schema_version": 1,
        "synthetic": True,
        "provenance": "test",
        "rate_unit": "annual_bp",
        "missing_dates": [],
        "rates": [],
    }


def _event_row() -> dict:
    return {
        "transaction_id": "fix-txn-x-001",
        "instrument": "EUR_USD",
        "trade_id": "fix-trade-x-001",
        "units": "10000",
        "financing": "-0.054",
        "time": "2026-05-19T21:00:00+00:00",
    }


def test_rejects_unknown_top_level_key(tmp_path: Path) -> None:
    payload = _baseline_event_payload()
    payload["wat"] = 1
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="unknown top-level keys"):
        load_observed_event_fixture(p)


def test_rejects_missing_top_level_key(tmp_path: Path) -> None:
    payload = _baseline_event_payload()
    del payload["account_currency"]
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="missing required top-level keys"):
        load_observed_event_fixture(p)


def test_rejects_wrong_kind(tmp_path: Path) -> None:
    payload = _baseline_event_payload()
    payload["kind"] = "financing_rates"
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="kind must be"):
        load_observed_event_fixture(p)


def test_rejects_wrong_schema_version(tmp_path: Path) -> None:
    payload = _baseline_event_payload()
    payload["schema_version"] = 99
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="schema_version must be"):
        load_observed_event_fixture(p)


def test_rejects_non_boolean_synthetic(tmp_path: Path) -> None:
    payload = _baseline_event_payload()
    payload["synthetic"] = "yes"
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="synthetic must be a boolean"):
        load_observed_event_fixture(p)


def test_rejects_bad_account_id_hash(tmp_path: Path) -> None:
    payload = _baseline_event_payload()
    payload["account_id_hash"] = "TOO_SHORT"
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="64-character lowercase"):
        load_observed_event_fixture(p)


def test_rejects_bad_account_currency(tmp_path: Path) -> None:
    payload = _baseline_event_payload()
    payload["account_currency"] = "usd"
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="account_currency must match"):
        load_observed_event_fixture(p)


def test_rejects_missing_required_event_row_field(tmp_path: Path) -> None:
    payload = _baseline_event_payload()
    row = _event_row()
    del row["financing"]
    payload["events"] = [row]
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="missing required event-row keys"):
        load_observed_event_fixture(p)


def test_rejects_unknown_event_row_field(tmp_path: Path) -> None:
    payload = _baseline_event_payload()
    row = _event_row()
    row["mystery"] = 1
    payload["events"] = [row]
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="unknown event-row keys"):
        load_observed_event_fixture(p)


def test_rejects_naive_time(tmp_path: Path) -> None:
    payload = _baseline_event_payload()
    row = _event_row()
    row["time"] = "2026-05-19T21:00:00"  # no offset
    payload["events"] = [row]
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="timezone-aware"):
        load_observed_event_fixture(p)


def test_accepts_explicit_utc_offset(tmp_path: Path) -> None:
    payload = _baseline_event_payload()
    payload["events"] = [_event_row()]
    p = _write(tmp_path, payload)
    events = load_observed_event_fixture(p)
    assert events[0]["time"].tzinfo is not None
    assert events[0]["time"] == datetime(2026, 5, 19, 21, 0, tzinfo=UTC)


def test_rejects_numeric_financing_literal(tmp_path: Path) -> None:
    payload = _baseline_event_payload()
    row = _event_row()
    row["financing"] = -0.054  # numeric, not string
    payload["events"] = [row]
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="stringified Decimal"):
        load_observed_event_fixture(p)


def test_rejects_unparseable_decimal(tmp_path: Path) -> None:
    payload = _baseline_event_payload()
    row = _event_row()
    row["financing"] = "not-a-number"
    payload["events"] = [row]
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="not parseable as Decimal"):
        load_observed_event_fixture(p)


def test_rejects_bad_instrument(tmp_path: Path) -> None:
    payload = _baseline_event_payload()
    row = _event_row()
    row["instrument"] = "EURUSD"  # no underscore
    payload["events"] = [row]
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="instrument"):
        load_observed_event_fixture(p)


def test_rejects_invalid_json(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(FixtureValidationError, match="invalid JSON"):
        load_observed_event_fixture(p)


def test_rejects_top_level_array(tmp_path: Path) -> None:
    p = tmp_path / "arr.json"
    p.write_text("[]", encoding="utf-8")
    with pytest.raises(FixtureValidationError, match="top-level must be a JSON object"):
        load_observed_event_fixture(p)


def test_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FixtureValidationError, match="could not read file"):
        load_observed_event_fixture(tmp_path / "does-not-exist.json")


# ---------- Rate-fixture-specific rails ----------


def test_rate_fixture_rejects_bad_rate_unit(tmp_path: Path) -> None:
    payload = _baseline_rate_payload()
    payload["rate_unit"] = "bp_per_day"
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="annual_bp"):
        load_rate_fixture(p)


def test_rate_fixture_rejects_duplicate_date_instrument(tmp_path: Path) -> None:
    payload = _baseline_rate_payload()
    row = {
        "date_utc": "2026-05-18",
        "instrument": "EUR_USD",
        "long_annual_bp": -1.0,
        "short_annual_bp": 1.0,
    }
    payload["rates"] = [row, dict(row)]
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="duplicate"):
        load_rate_fixture(p)


def test_rate_fixture_rejects_missing_dates_overlap(tmp_path: Path) -> None:
    payload = _baseline_rate_payload()
    payload["missing_dates"] = ["2026-05-18"]
    payload["rates"] = [
        {
            "date_utc": "2026-05-18",
            "instrument": "EUR_USD",
            "long_annual_bp": -1.0,
            "short_annual_bp": 1.0,
        }
    ]
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="missing_dates entries also present"):
        load_rate_fixture(p)


def test_rate_fixture_rejects_modeled_treatment() -> None:
    with pytest.raises(FixtureValidationError, match="MODELED"):
        load_rate_fixture(
            FIXTURES / "rates_two_week_eur_usd.json",
            treatment=FinancingTreatment.MODELED,
        )


def test_rate_fixture_rejects_bad_date(tmp_path: Path) -> None:
    payload = _baseline_rate_payload()
    payload["rates"] = [
        {
            "date_utc": "2026/05/18",
            "instrument": "EUR_USD",
            "long_annual_bp": -1.0,
            "short_annual_bp": 1.0,
        }
    ]
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="YYYY-MM-DD"):
        load_rate_fixture(p)


def test_rate_fixture_rejects_non_numeric_rate(tmp_path: Path) -> None:
    payload = _baseline_rate_payload()
    payload["rates"] = [
        {
            "date_utc": "2026-05-18",
            "instrument": "EUR_USD",
            "long_annual_bp": "not-a-number",
            "short_annual_bp": 1.0,
        }
    ]
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="numeric"):
        load_rate_fixture(p)


def test_rate_fixture_rejects_bool_as_numeric(tmp_path: Path) -> None:
    """JSON true/false would otherwise satisfy ``isinstance(value, (int, float))``
    via Python's int subclass — the loader must reject it explicitly."""
    payload = _baseline_rate_payload()
    payload["rates"] = [
        {
            "date_utc": "2026-05-18",
            "instrument": "EUR_USD",
            "long_annual_bp": True,
            "short_annual_bp": 1.0,
        }
    ]
    p = _write(tmp_path, payload)
    with pytest.raises(FixtureValidationError, match="numeric"):
        load_rate_fixture(p)


# ---------- Sign convention preserved ----------


def test_sign_convention_preserved_long_debit() -> None:
    events = load_observed_event_fixture(FIXTURES / "observed_eur_usd_long_debit.json")
    assert all(e["financing"] < 0 for e in events)


def test_sign_convention_preserved_short_credit() -> None:
    events = load_observed_event_fixture(FIXTURES / "observed_eur_usd_short_credit.json")
    assert all(e["financing"] > 0 for e in events)


# ---------- Wednesday triple-swap representation ----------


def test_wednesday_triple_swap_row_is_three_times_neighbours() -> None:
    """Wednesday's debit in the multi-day fixture is 3x the
    surrounding non-Wednesday rows."""
    events = load_observed_event_fixture(FIXTURES / "observed_multi_day_with_triple.json")
    by_date = {e["time"].date(): e for e in events}
    mon = by_date[date(2026, 5, 18)]["financing"]
    wed = by_date[date(2026, 5, 20)]["financing"]
    thu = by_date[date(2026, 5, 21)]["financing"]
    assert wed == 3 * mon
    assert wed == 3 * thu
    assert events[2]["time"].weekday() == 2  # Wednesday


# ---------- canonical event_key matches ----------


def test_canonical_event_key_helper_matches_load() -> None:
    events = load_observed_event_fixture(FIXTURES / "observed_eur_usd_long_debit.json")
    for ev in events:
        expected = canonical_event_key(
            ev["transaction_id"], ev["instrument"], ev["trade_id"]
        )
        assert ev["event_key"] == expected


def test_loaded_event_field_set_matches_canonical_schema() -> None:
    """The loader's ObservedEventDict shape must match the canonical
    ObservedFinancingEvent field set field-for-field, plus the
    event_key. This protects the future capture-pipeline path that
    will write through the canonical model.

    The canonical model is imported here (this test file is NOT
    inside research/financing/, so it may cross the boundary)."""
    from forex_bot.domain.transactions import ObservedFinancingEvent

    canonical_fields = set(ObservedFinancingEvent.model_fields.keys())
    loaded_fields = {
        "transaction_id",
        "account_id_hash",
        "instrument",
        "trade_id",
        "units",
        "financing",
        "currency",
        "time",
        "source",
    }
    assert canonical_fields == loaded_fields

    # Spot-check that a loaded event's event_key matches the canonical
    # property's derivation for the same inputs.
    events = load_observed_event_fixture(FIXTURES / "observed_eur_usd_long_debit.json")
    for ev in events:
        canonical = ObservedFinancingEvent(
            transaction_id=ev["transaction_id"],
            account_id_hash=ev["account_id_hash"],
            instrument=ev["instrument"],
            trade_id=ev["trade_id"],
            units=ev["units"],
            financing=ev["financing"],
            currency=ev["currency"],
            time=ev["time"],
            source=ev["source"],
        )
        assert ev["event_key"] == canonical.event_key


# ---------- Reconciliation against the calculator ----------


def test_reconciliation_skips_missing_date_matches_observed_per_row() -> None:
    """With the rate fixture + missing_rate_policy=SKIP, the
    calculator's per-event cashflow_home matches the observed
    fixture's financing field for the same dates exactly."""
    src, missing = load_rate_fixture(FIXTURES / "rates_two_week_eur_usd.json")
    observed = load_observed_event_fixture(
        FIXTURES / "observed_multi_day_with_triple.json"
    )

    cfg = FinancingCalculatorConfig(missing_rate_policy=MissingRatePolicy.SKIP)
    position = PositionInterval(
        position_id="recon-multi-day",
        instrument="EUR_USD",
        side="long",
        units=Decimal("10000"),
        entry_price=Decimal("1.0800"),
        open_time=_utc(2026, 5, 18, 8),
        close_time=_utc(2026, 5, 22, 16),
    )
    s = calculate_position(position, src, cfg)
    # Calculator skipped the missing 5/19 → 3 events. Observed has 4.
    assert s.rollovers == 3

    calc_by_date = {e.date_utc: e for e in s.events}
    obs_by_date = {ev["time"].date(): ev for ev in observed}
    # All three calculator dates have matching observed rows.
    for d, calc in calc_by_date.items():
        obs = obs_by_date[d]
        assert calc.cashflow_home == pytest.approx(float(obs["financing"]), rel=1e-9)

    # The missing date is exactly the one in the fixture's missing_dates list.
    missing_calc = set(obs_by_date) - set(calc_by_date)
    assert missing_calc == {date(2026, 5, 19)}
    assert date(2026, 5, 19) in missing


def test_reconciliation_conservative_policy_fires_fallback_on_missing() -> None:
    """With the rate fixture + missing_rate_policy=CONSERVATIVE
    (default), the missing 5/19 date produces a flagged event with
    the conservative fallback bp/day rather than skipping."""
    src, missing = load_rate_fixture(FIXTURES / "rates_two_week_eur_usd.json")
    position = PositionInterval(
        position_id="recon-fallback",
        instrument="EUR_USD",
        side="long",
        units=Decimal("10000"),
        entry_price=Decimal("1.0800"),
        open_time=_utc(2026, 5, 18, 8),
        close_time=_utc(2026, 5, 22, 16),
    )
    s = calculate_position(position, src)  # default CONSERVATIVE
    assert s.rollovers == 4
    fallbacks = [e for e in s.events if e.rate_was_missing]
    assert [e.date_utc for e in fallbacks] == [date(2026, 5, 19)]
    assert date(2026, 5, 19) in missing
    # Conservative fallback debit: -1.2 bp/day * 10800 / 10000 = -1.296
    assert fallbacks[0].cashflow_home == pytest.approx(-1.296, rel=1e-9)


def test_weekend_skip_fixture_dates_are_friday_and_monday() -> None:
    events = load_observed_event_fixture(FIXTURES / "observed_weekend_skip.json")
    weekdays = [e["time"].weekday() for e in events]
    assert weekdays == [4, 0]  # Fri, Mon


def test_utc_date_of_helper() -> None:
    events = load_observed_event_fixture(FIXTURES / "observed_eur_usd_long_debit.json")
    assert utc_date_of(events[0]) == events[0]["time"].date()


# ---------- strategy_evidence rail through calculate_run with fixture inputs ----------


def test_loaded_rate_source_run_report_is_diagnostic_only() -> None:
    """A calculate_run report driven from a fixture-loaded
    TableRateSource carries strategy_evidence: false,
    financing_in_engine_pnl: false, financing_is_live_blocker: true
    just like the stress-source path."""
    src, _missing = load_rate_fixture(FIXTURES / "rates_two_week_eur_usd.json")
    position = PositionInterval(
        position_id="rail",
        instrument="EUR_USD",
        side="long",
        units=Decimal("10000"),
        entry_price=Decimal("1.0800"),
        open_time=_utc(2026, 5, 18, 8),
        close_time=_utc(2026, 5, 20, 16),
    )
    report = calculate_run([position], src, now=_utc(2026, 5, 23))
    assert report.strategy_evidence is False
    assert report.financing_in_engine_pnl is False
    assert report.financing_is_live_blocker is True
    assert report.financing_treatment == FinancingTreatment.ESTIMATED


# ---------- Import isolation rail (loader file too) ----------


def test_fixtures_module_does_not_import_forex_bot() -> None:
    """The grep-enforced rail in test_financing_models.py globs the
    whole package; this explicit check pins the loader file by
    name as well, so a future refactor that moves the loader
    cannot accidentally weaken the rail."""
    loader = Path(__file__).resolve().parents[2] / "research" / "financing" / "fixtures.py"
    text = loader.read_text(encoding="utf-8")
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "forex_bot" in stripped and (
            stripped.startswith("import ") or stripped.startswith("from ")
        ):
            raise AssertionError(
                f"research/financing/fixtures.py:{line_no} imports forex_bot: {stripped}"
            )


# ---------- Fixture files themselves are safe ----------


def test_every_committed_fixture_carries_synthetic_true() -> None:
    for path in sorted(FIXTURES.glob("*.json")):
        payload = _read_json(path)
        assert payload.get("synthetic") is True, f"{path} must carry synthetic: true"


def test_every_committed_fixture_is_under_10kb() -> None:
    for path in sorted(FIXTURES.glob("*.json")):
        size = path.stat().st_size
        assert size < 10 * 1024, f"{path} is {size} bytes — exceeds 10 KB cap"


def test_every_committed_event_fixture_uses_documented_hash() -> None:
    """The fixture README documents one synthetic account_id_hash;
    every committed event fixture must use it."""
    expected_hash = (
        "c4e91d9f7c03827938cbb2c82608bba023e98f23d52b2f84784cbcf9652df69f"
    )
    for path in sorted(FIXTURES.glob("observed_*.json")):
        payload = _read_json(path)
        assert payload["account_id_hash"] == expected_hash
