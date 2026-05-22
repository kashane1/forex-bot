"""Tests for the financing-model interface (Phase 2, infra-foundation-001).

Proves the conservative stress overlay is applied deterministically, the
financing treatment is exposed as report metadata, the default stays
conservative, the future-observed model is a non-functional placeholder,
and that an unmodeled financing treatment blocks strategy approval unless
a human override is explicitly given.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from forex_bot.financing import (
    ConservativeStressFinancingModel,
    FinancingModel,
    FinancingTreatment,
    FutureOandaObservedFinancingModel,
    NoFinancingModel,
    default_financing_model,
    financing_debit_r,
    financing_metadata,
    financing_treatment_blocks_approval,
)

# A representative closed trade.
_TRADE = dict(
    instrument="EUR_USD",
    units=Decimal("1000"),
    entry_price=Decimal("1.1000"),
    stop_price=Decimal("1.0950"),
    bars_held=24,
)


def test_treatment_enum_has_exactly_three_values():
    assert {t.value for t in FinancingTreatment} == {
        "modeled", "estimated", "unmodeled",
    }


def test_default_model_is_conservative_and_estimated():
    model = default_financing_model()
    assert isinstance(model, ConservativeStressFinancingModel)
    assert isinstance(model, FinancingModel)
    assert model.treatment is FinancingTreatment.ESTIMATED


def test_no_financing_model_is_unmodeled_and_zero():
    model = NoFinancingModel()
    assert model.treatment is FinancingTreatment.UNMODELED
    assert model.debit_r(**_TRADE) == 0.0
    assert model.debit_usd(
        instrument="EUR_USD", units=Decimal("1000"),
        entry_price=Decimal("1.1000"), bars_held=24,
    ) == 0.0


def test_conservative_model_matches_pure_function_deterministically():
    model = ConservativeStressFinancingModel()
    first = model.debit_r(**_TRADE)
    second = model.debit_r(**_TRADE)
    assert first == second  # deterministic
    assert first == financing_debit_r(**_TRADE)  # wraps the tested function
    assert first > 0.0  # a real holding period costs a real (positive) debit


def test_conservative_debit_is_never_a_credit():
    """A stress model only ever charges a cost — never assumes a benefit."""
    model = ConservativeStressFinancingModel()
    for bars in (0, 1, 6, 24, 240):
        assert model.debit_r(
            instrument="USD_JPY", units=Decimal("1000"),
            entry_price=Decimal("150.00"), stop_price=Decimal("149.00"),
            bars_held=bars,
        ) >= 0.0


def test_future_oanda_model_is_a_nonfunctional_placeholder():
    with pytest.raises(NotImplementedError, match="placeholder"):
        FutureOandaObservedFinancingModel()


def test_financing_metadata_states_the_treatment():
    meta = financing_metadata(default_financing_model())
    assert meta["financing_treatment"] == "estimated"
    assert meta["financing_in_engine_pnl"] is False
    assert meta["financing_is_live_blocker"] is True

    unmodeled_meta = financing_metadata(NoFinancingModel())
    assert unmodeled_meta["financing_treatment"] == "unmodeled"
    assert unmodeled_meta["financing_is_live_blocker"] is True


def test_unmodeled_financing_blocks_all_approval():
    for mode in ("paper", "demo", "live"):
        assert financing_treatment_blocks_approval(
            FinancingTreatment.UNMODELED, mode,
        ) is True


def test_human_override_lifts_unmodeled_for_paper_demo_only():
    # An explicit human override unblocks paper / demo ...
    for mode in ("paper", "demo"):
        assert financing_treatment_blocks_approval(
            FinancingTreatment.UNMODELED, mode, human_override=True,
        ) is False
    # ... but never live — live unconditionally requires modeled financing.
    assert financing_treatment_blocks_approval(
        FinancingTreatment.UNMODELED, "live", human_override=True,
    ) is True


def test_estimated_financing_blocks_live_only():
    assert financing_treatment_blocks_approval(
        FinancingTreatment.ESTIMATED, "paper",
    ) is False
    assert financing_treatment_blocks_approval(
        FinancingTreatment.ESTIMATED, "demo",
    ) is False
    assert financing_treatment_blocks_approval(
        FinancingTreatment.ESTIMATED, "live",
    ) is True


def test_modeled_financing_blocks_nothing():
    for mode in ("paper", "demo", "live"):
        assert financing_treatment_blocks_approval(
            FinancingTreatment.MODELED, mode,
        ) is False
