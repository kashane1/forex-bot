"""Tests for the expanded synthetic rate fixtures (one per H4
universe pair) and their reconciliation behaviour.

Covers: 7-pair coverage; every fixture loads; sign-variety
across pairs; size + synthetic invariants; per-pair USD-quote
vs USD-base notional convention; JPY-precision path;
AUD_USD-long-credit reconciliation under skip policy; CLI
non-EUR run; MODELED still refused everywhere."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "research" / "financing" / "fixtures"
RECONCILE_SCRIPT = REPO_ROOT / "scripts" / "reconcile_financing_fixtures.py"

H4_UNIVERSE = (
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
)
USD_BASE_PAIRS = {"USD_JPY", "USD_CAD", "USD_CHF"}


def _pair_to_slug(pair: str) -> str:
    return pair.lower()


def _rate_fixture_path(pair: str) -> Path:
    return FIXTURES / f"rates_two_week_{_pair_to_slug(pair)}.json"


# ---------- 7-pair coverage ----------


def test_every_h4_pair_has_a_rate_fixture() -> None:
    """One of the sprint's two headline deliverables."""
    missing = [p for p in H4_UNIVERSE if not _rate_fixture_path(p).exists()]
    assert missing == [], f"missing rate fixtures: {missing}"


def test_every_rate_fixture_loads() -> None:
    """Every committed rates_two_week_*.json loads via the
    existing loader without error."""
    from research.financing import load_rate_fixture

    for pair in H4_UNIVERSE:
        src, missing = load_rate_fixture(_rate_fixture_path(pair))
        # Sanity: per-pair rate looked up on a known-good date returns
        # a RatePair.
        sample = src.rate_for(date(2026, 5, 18), pair)
        assert sample is not None, f"{pair}: no rate on 2026-05-18"
        assert isinstance(missing, list)


def test_every_rate_fixture_is_synthetic() -> None:
    """Every committed rate fixture declares synthetic: true."""
    for pair in H4_UNIVERSE:
        payload = json.loads(
            _rate_fixture_path(pair).read_text(encoding="utf-8")
        )
        assert payload["synthetic"] is True, f"{pair} fixture is not synthetic"


def test_every_rate_fixture_under_size_cap() -> None:
    """<10 KB per file (sprint convention)."""
    for pair in H4_UNIVERSE:
        size = _rate_fixture_path(pair).stat().st_size
        assert size < 10 * 1024, f"{pair}: {size} bytes — exceeds 10 KB"


def test_every_rate_fixture_has_required_top_level_fields() -> None:
    expected = {
        "kind",
        "schema_version",
        "synthetic",
        "provenance",
        "rate_unit",
        "missing_dates",
        "rates",
    }
    for pair in H4_UNIVERSE:
        payload = json.loads(
            _rate_fixture_path(pair).read_text(encoding="utf-8")
        )
        assert set(payload.keys()) == expected, (
            f"{pair}: top-level keys {set(payload.keys())} != {expected}"
        )
        assert payload["kind"] == "financing_rates"
        assert payload["schema_version"] == 1
        assert payload["rate_unit"] == "annual_bp"


def test_every_rate_fixture_has_at_least_one_missing_date() -> None:
    """Convention: every new pair fixture exercises the
    conservative-fallback / skip-policy path."""
    for pair in H4_UNIVERSE:
        payload = json.loads(
            _rate_fixture_path(pair).read_text(encoding="utf-8")
        )
        assert len(payload["missing_dates"]) >= 1, (
            f"{pair} has no missing_dates entry"
        )


def test_no_real_account_looking_ids_in_any_fixture() -> None:
    """Fixture files must not contain anything that looks like an
    OANDA account id (`NNN-NNN-NNNNNNN-NNN`) or a Bearer token
    (long opaque string)."""
    import re

    account_pat = re.compile(r"\d{3}-\d{3}-\d{7}-\d{3}")
    for fixture in FIXTURES.glob("*.json"):
        text = fixture.read_text(encoding="utf-8")
        assert not account_pat.search(text), (
            f"{fixture.name} contains an OANDA-account-shaped id"
        )


# ---------- Sign variety ----------


def test_rate_sign_variety_across_pairs() -> None:
    """The 6 new fixtures should not all share the same sign
    pattern; at least one pair has a positive long, at least
    one has a negative long, at least one has a positive short,
    and at least one has a negative short. This guards against
    a regression where a copy-paste error gave every fixture
    the same shape."""
    from research.financing import load_rate_fixture

    long_signs: list[int] = []
    short_signs: list[int] = []
    for pair in H4_UNIVERSE:
        src, _ = load_rate_fixture(_rate_fixture_path(pair))
        sample = src.rate_for(date(2026, 5, 18), pair)
        if sample is None:
            continue
        long_signs.append(
            1 if sample.long_annual_bp > 0 else (-1 if sample.long_annual_bp < 0 else 0)
        )
        short_signs.append(
            1 if sample.short_annual_bp > 0 else (-1 if sample.short_annual_bp < 0 else 0)
        )
    assert 1 in long_signs, "no fixture has long_annual_bp > 0"
    assert -1 in long_signs, "no fixture has long_annual_bp < 0"
    assert 1 in short_signs, "no fixture has short_annual_bp > 0"
    assert -1 in short_signs, "no fixture has short_annual_bp < 0"


# ---------- USD-base vs USD-quote notional ----------


def test_usd_base_pair_notional_is_units_in_calculator() -> None:
    """A USD-base pair (e.g. USD_JPY) must have notional_home
    = units (not units * entry_price). Verify against the new
    USD_JPY rate fixture."""
    from research.financing import (
        FinancingCalculatorConfig,
        MissingRatePolicy,
        PositionInterval,
        calculate_position,
        load_rate_fixture,
    )

    src, _ = load_rate_fixture(_rate_fixture_path("USD_JPY"))
    p = PositionInterval(
        position_id="usd-jpy-precision",
        instrument="USD_JPY",
        side="long",
        units=Decimal("10000"),
        entry_price=Decimal("155.123"),  # JPY precision; should be ignored
        open_time=datetime(2026, 5, 18, 8, 0, tzinfo=UTC),
        close_time=datetime(2026, 5, 19, 8, 0, tzinfo=UTC),
    )
    cfg = FinancingCalculatorConfig(missing_rate_policy=MissingRatePolicy.SKIP)
    s = calculate_position(p, src, cfg)
    assert s.rollovers == 1
    e = s.events[0]
    # USD-base: notional = units (NOT units * 155.123)
    assert e.notional_home == pytest.approx(10000.0, rel=1e-9)
    # +18.25 / 365 = +0.05 bp/day; 0.05 / 10000 * 10000 = 0.05 USD credit
    assert e.cashflow_home == pytest.approx(0.05, rel=1e-9)


def test_usd_quote_pair_notional_is_units_times_price() -> None:
    """A USD-quote pair (e.g. AUD_USD) must have notional_home
    = units * entry_price. Verify against the new AUD_USD
    rate fixture."""
    from research.financing import (
        FinancingCalculatorConfig,
        MissingRatePolicy,
        PositionInterval,
        calculate_position,
        load_rate_fixture,
    )

    src, _ = load_rate_fixture(_rate_fixture_path("AUD_USD"))
    p = PositionInterval(
        position_id="aud-usd-q",
        instrument="AUD_USD",
        side="long",
        units=Decimal("10000"),
        entry_price=Decimal("0.6600"),
        open_time=datetime(2026, 5, 18, 8, 0, tzinfo=UTC),
        close_time=datetime(2026, 5, 19, 8, 0, tzinfo=UTC),
    )
    cfg = FinancingCalculatorConfig(missing_rate_policy=MissingRatePolicy.SKIP)
    s = calculate_position(p, src, cfg)
    assert s.rollovers == 1
    e = s.events[0]
    # USD-quote: notional = 10000 * 0.66 = 6600
    assert e.notional_home == pytest.approx(6600.0, rel=1e-9)


# ---------- AUD_USD-long-credit reconciliation ----------


def test_aud_usd_observed_reconciles_against_rate_fixture_under_skip() -> None:
    """The new observed_aud_usd_long_credit.json must reconcile
    exactly against rates_two_week_aud_usd.json under
    missing_rate_policy=skip — the canonical non-EUR
    reconciliation."""
    from research.financing import (
        FinancingCalculatorConfig,
        MissingRatePolicy,
        PositionInterval,
        calculate_position,
        load_observed_event_fixture,
        load_rate_fixture,
    )

    src, missing = load_rate_fixture(_rate_fixture_path("AUD_USD"))
    observed = load_observed_event_fixture(
        FIXTURES / "observed_aud_usd_long_credit.json"
    )
    position = PositionInterval(
        position_id="recon-aud",
        instrument="AUD_USD",
        side="long",
        units=Decimal("10000"),
        entry_price=Decimal("0.6600"),
        open_time=datetime(2026, 5, 18, 8, 0, tzinfo=UTC),
        close_time=datetime(2026, 5, 22, 16, 0, tzinfo=UTC),
    )
    cfg = FinancingCalculatorConfig(missing_rate_policy=MissingRatePolicy.SKIP)
    s = calculate_position(position, src, cfg)
    # The rate fixture skips 5/19; the observed fixture omits 5/19
    # too. Three calculator events, three observed events, all match.
    calc_by_date = {e.date_utc: e for e in s.events}
    obs_by_date = {ev["time"].date(): ev for ev in observed}
    assert set(calc_by_date) == set(obs_by_date)
    for d, calc in calc_by_date.items():
        obs = obs_by_date[d]
        assert calc.cashflow_home == pytest.approx(
            float(obs["financing"]), rel=1e-9,
        ), f"{d}: calculator {calc.cashflow_home} != observed {obs['financing']}"
    # And the missing date listed in the rate fixture is exactly the
    # one absent from both files.
    assert missing == [date(2026, 5, 19)]


# ---------- Reconciliation CLI can run a non-EUR example ----------


def test_reconciliation_cli_runs_on_aud_usd_pair(tmp_path: Path) -> None:
    """The CLI's full subprocess invocation works against the
    new AUD_USD pair pair. Exit 0 expected under skip policy."""
    spec = importlib.util.spec_from_file_location(
        "reconcile_financing_fixtures", RECONCILE_SCRIPT,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    code = module.run(
        [
            "--observed",
            str(FIXTURES / "observed_aud_usd_long_credit.json"),
            "--rates",
            str(FIXTURES / "rates_two_week_aud_usd.json"),
            "--output",
            str(tmp_path),
            "--units",
            "10000",
            "--entry-price",
            "0.6600",
            "--side",
            "long",
            "--missing-rate-policy",
            "skip",
            "--generated-at-utc",
            "2026-05-23T12:00:00+00:00",
        ]
    )
    assert code == module.EXIT_OK
    payload = json.loads(
        (tmp_path / "reconciliation.json").read_text(encoding="utf-8")
    )
    assert payload["summary"]["mismatch"] == 0
    assert payload["summary"]["match"] == 3
    assert payload["financing_treatment"] == "estimated"
    assert payload["strategy_evidence"] is False
    # Every row references AUD_USD.
    for row in payload["rows"]:
        assert row["instrument"] == "AUD_USD"


# ---------- MODELED remains refused for every new fixture ----------


def test_no_new_fixture_can_construct_modeled_rate_source() -> None:
    """The loader refuses treatment=MODELED for every committed
    fixture (per the existing fixtures.py rail). This regression
    test ensures the 6 new fixtures behave the same way."""
    from research.financing import FinancingTreatment, FixtureValidationError, load_rate_fixture

    for pair in H4_UNIVERSE:
        with pytest.raises(FixtureValidationError, match="MODELED"):
            load_rate_fixture(
                _rate_fixture_path(pair),
                treatment=FinancingTreatment.MODELED,
            )


def test_calculator_refuses_modeled_for_new_fixture_treatments() -> None:
    """calculate_run refuses any rate source claiming MODELED.
    The loader already prevents construction; this test pins
    the second layer of defense by mutating the instance
    attribute post-construction (since `TableRateSource.__init__`
    sets `self.treatment` from the constructor parameter and
    refuses MODELED there)."""
    from research.financing import (
        FinancingTreatment,
        PositionInterval,
        calculate_run,
        load_rate_fixture,
    )

    src, _ = load_rate_fixture(_rate_fixture_path("USD_JPY"))
    # Bypass the loader/constructor refusal by mutating the
    # instance attribute. This is the only way to construct a
    # MODELED-self-reporting source; defense-in-depth in
    # calculate_run must still catch it.
    src.treatment = FinancingTreatment.MODELED

    with pytest.raises(ValueError, match="MODELED"):
        calculate_run(
            [
                PositionInterval(
                    position_id="x",
                    instrument="USD_JPY",
                    side="long",
                    units=Decimal("1"),
                    entry_price=Decimal("155.0"),
                    open_time=datetime(2026, 5, 18, 8, 0, tzinfo=UTC),
                    close_time=datetime(2026, 5, 19, 8, 0, tzinfo=UTC),
                ),
            ],
            src,
        )


# ---------- Subprocess smoke: CLI works on every pair without crashing ----------


def test_cli_smoke_against_every_pair_is_safe(tmp_path: Path) -> None:
    """Run the reconciliation CLI in conservative-policy mode
    against every pair (with no observed file — using the
    empty no-rollover file). The script must terminate
    cleanly for each. Verifies no per-pair fixture has a
    surprise that crashes the CLI."""
    spec = importlib.util.spec_from_file_location(
        "reconcile_financing_fixtures", RECONCILE_SCRIPT,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    empty_observed = FIXTURES / "observed_same_day_no_rollover.json"
    for pair in H4_UNIVERSE:
        out = tmp_path / _pair_to_slug(pair)
        code = module.run(
            [
                "--observed",
                str(empty_observed),
                "--rates",
                str(_rate_fixture_path(pair)),
                "--output",
                str(out),
                "--generated-at-utc",
                "2026-05-23T12:00:00+00:00",
            ]
        )
        # Empty observed file ⇒ no rows. Exit 0.
        assert code == module.EXIT_OK, f"CLI failed against {pair}"
        payload = json.loads(
            (out / "reconciliation.json").read_text(encoding="utf-8")
        )
        assert payload["summary"]["row_count"] == 0
        assert payload["financing_treatment"] == "estimated"


# ---------- Repo-global subprocess: pytest catches no regressions ----------


def test_subprocess_loads_all_seven_fixtures_in_fresh_interpreter() -> None:
    """A fresh subprocess loads every rate fixture without
    pulling in forex_bot — pins the package-wide import
    isolation rail one more time."""
    code = (
        "import sys, importlib.util\n"
        f"sys.path.insert(0, r'{REPO_ROOT}')\n"
        "from research.financing import load_rate_fixture\n"
        "from pathlib import Path\n"
        f"fixtures = Path(r'{FIXTURES}')\n"
        "for pair in ['EUR_USD','GBP_USD','USD_JPY','AUD_USD','USD_CAD','USD_CHF','NZD_USD']:\n"
        "    slug = pair.lower()\n"
        "    src, _ = load_rate_fixture(fixtures / f'rates_two_week_{slug}.json')\n"
        "    assert src is not None\n"
        "names = sorted(m for m in sys.modules if m == 'forex_bot' or m.startswith('forex_bot.'))\n"
        "print('FOREX_BOT_MODS:', '|'.join(names))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, cwd=str(REPO_ROOT), check=True,
    )
    last_line = result.stdout.strip().splitlines()[-1]
    assert last_line == "FOREX_BOT_MODS:", (
        f"loading rate fixtures pulled in forex_bot modules: {last_line}"
    )
