"""Tests for the OANDA instrument metadata audit script
(Phase 3, oanda-practice-readonly-001).

Cover the pure audit logic: JPY-aware expectations, field comparison,
missing-instrument handling, JPY pip math, and report redaction. No
OANDA call is made.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from forex_bot.domain.instruments import Instrument

_REPO = Path(__file__).resolve().parents[2]


def _load_script(name: str):
    path = _REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


audit = _load_script("audit_oanda_instruments")


def _instr(name: str, **overrides) -> Instrument:
    """Build an Instrument with the metadata the repo expects for `name`,
    allowing field overrides to construct mismatch fixtures."""
    jpy = "JPY" in name.split("_")
    base: dict = {
        "name": name,
        "type": "CURRENCY",
        "display_precision": 3 if jpy else 5,
        "pip_location": -2 if jpy else -4,
        "trade_units_precision": 0,
        "minimum_trade_size": Decimal("1"),
        "margin_rate": Decimal("0.0333"),
    }
    base.update(overrides)
    return Instrument(**base)


# --------------------------------------------------------------------------
# Expectations
# --------------------------------------------------------------------------


def test_is_jpy_pair():
    assert audit.is_jpy_pair("USD_JPY")
    assert not audit.is_jpy_pair("EUR_USD")
    assert not audit.is_jpy_pair("NZD_USD")


def test_expected_metadata_jpy_vs_non_jpy():
    eur = audit.expected_metadata("EUR_USD")
    assert eur["pip_location"] == -4
    assert eur["display_precision"] == 5
    jpy = audit.expected_metadata("USD_JPY")
    assert jpy["pip_location"] == -2
    assert jpy["display_precision"] == 3
    assert jpy["trade_units_precision"] == 0
    assert jpy["minimum_trade_size"] == Decimal("1")


def test_redact_account_id():
    assert audit.redact_account_id("101-002-7654321-003") == "101…003"
    assert audit.redact_account_id("") == "<short-or-empty>"
    assert audit.redact_account_id(None) == "<short-or-empty>"


# --------------------------------------------------------------------------
# Single-instrument audit
# --------------------------------------------------------------------------


def test_audit_one_passes_a_correct_instrument():
    a = audit.audit_one("EUR_USD", _instr("EUR_USD"), in_universe=True)
    assert a.found is True
    assert a.ok is True
    assert a.mismatches == []


def test_audit_one_flags_a_pip_location_mismatch():
    # A non-JPY pair wrongly carrying JPY precision is a real metadata bug.
    bad = _instr("EUR_USD", pip_location=-2, display_precision=3)
    a = audit.audit_one("EUR_USD", bad, in_universe=True)
    assert a.found is True
    assert a.ok is False
    mismatched_fields = {c.field for c in a.mismatches}
    assert "pip_location" in mismatched_fields
    assert "display_precision" in mismatched_fields


def test_audit_one_handles_a_missing_instrument():
    a = audit.audit_one("USD_CHF", None, in_universe=True)
    assert a.found is False
    assert a.ok is False
    assert a.checks == []


def test_audit_one_does_not_fail_on_a_differing_margin_rate():
    # Margin rate is informational only — never a stable-field failure.
    a = audit.audit_one("EUR_USD", _instr("EUR_USD", margin_rate=Decimal("0.05")), in_universe=True)
    assert a.ok is True
    assert a.margin_rate == Decimal("0.05")


# --------------------------------------------------------------------------
# JPY pip handling
# --------------------------------------------------------------------------


def test_jpy_pip_size_resolves_to_one_hundredth():
    a = audit.audit_one("USD_JPY", _instr("USD_JPY"), in_universe=True)
    assert a.ok is True
    assert a.pip_size == Decimal("0.01")


def test_non_jpy_pip_size_resolves_to_one_ten_thousandth():
    a = audit.audit_one("EUR_USD", _instr("EUR_USD"), in_universe=True)
    assert a.pip_size == Decimal("0.0001")


# --------------------------------------------------------------------------
# Full audit
# --------------------------------------------------------------------------


def test_audit_splits_universe_and_historical_and_detects_missing():
    # USD_CHF intentionally absent from the fetched list.
    present = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "NZD_USD"]
    report = audit.audit_instruments([_instr(n) for n in present])
    assert "USD_CHF" in report.missing
    assert report.ok is False
    universe = {a.name for a in report.audits if a.in_research_universe}
    assert universe == set(audit.RESEARCH_UNIVERSE)
    historical = {a.name for a in report.audits if not a.in_research_universe}
    assert historical == {"NZD_USD"}


def test_audit_all_present_and_correct_is_ok():
    names = audit.RESEARCH_UNIVERSE + audit.HISTORICAL_EXTRA
    report = audit.audit_instruments([_instr(n) for n in names])
    assert report.ok is True
    assert report.missing == []
    assert report.mismatched == []


def test_audit_reports_a_mismatched_instrument():
    names = audit.RESEARCH_UNIVERSE + audit.HISTORICAL_EXTRA
    instruments = [_instr(n) for n in names if n != "GBP_USD"]
    instruments.append(_instr("GBP_USD", trade_units_precision=2))
    report = audit.audit_instruments(instruments)
    assert "GBP_USD" in report.mismatched
    assert report.ok is False


# --------------------------------------------------------------------------
# Report rendering
# --------------------------------------------------------------------------


def test_render_report_redacts_and_states_read_only():
    names = audit.RESEARCH_UNIVERSE + audit.HISTORICAL_EXTRA
    report = audit.audit_instruments([_instr(n) for n in names])
    text = audit.render_report(
        report,
        account_id_redacted="101…001",
        host="https://api-fxpractice.oanda.com",
        config_path="configs/paper.yaml",
        generated_at=datetime(2026, 5, 22, tzinfo=UTC),
    )
    assert "101…001" in text
    assert "No order was submitted" in text
    assert "strategy_evidence: false" in text
    # NZD_USD appears, but in the historical section, not the universe.
    assert "NZD_USD" in text
    assert "Historical extra" in text
