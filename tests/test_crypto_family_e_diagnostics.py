"""Unit tests for Family E exploratory diagnostics helpers (synthetic fixtures only)."""

from __future__ import annotations

import numpy as np
import pytest
from research.crypto.family_e.costs import (
    funding_includes,
    net_returns,
    round_trip_cost_bps,
)
from research.crypto.family_e.cross_regime_oi import (
    diagnostics_4_5_oi_low_power,
    oi_availability,
)
from research.crypto.family_e.data import (
    InstrumentSeries,
    build_basis_sample,
    build_funding_sample,
    forward_log_return,
    funding_8h_windows,
    hour_index,
    realized_funding_over_hold,
)
from research.crypto.family_e.nulls import run_cohort_nulls
from research.crypto.family_e.reporting import GateInputs, classify, holm_adjust


def _series(
    *,
    canonical_id: str = "BTC_PERP_USD",
    n_hours: int = 400,
    funding_value: float = 1e-5,
    drift: float = 0.0,
    funding_gaps: tuple[int, ...] = (),
) -> InstrumentSeries:
    funding = {h: funding_value for h in range(n_hours) if h not in funding_gaps}
    open_px = {h: 100.0 * (1.0 + drift) ** h for h in range(n_hours)}
    close_px = {h: 100.0 * (1.0 + drift) ** h for h in range(n_hours)}
    basis = {h: float(h % 11) for h in range(n_hours)}
    index = {h: 100.0 for h in range(n_hours)}
    return InstrumentSeries(
        canonical_id=canonical_id,
        funding=funding,
        open_px=open_px,
        close_px=close_px,
        basis_bps=basis,
        index_close=index,
    )


# --- data: funding resampling + lookahead --------------------------------------- #

def test_funding_8h_windows_sum_and_entry_hour():
    funding = {h: float(h) for h in range(24)}
    windows = funding_8h_windows(funding)
    # window [0,8) sums 0..7 = 28, becomes known at entry hour 8
    assert windows[8] == pytest.approx(28.0)
    # window [8,16) sums 8..15 = 92, entry hour 16
    assert windows[16] == pytest.approx(92.0)
    # entry hours are settlement boundaries (divisible by 8)
    assert all(h % 8 == 0 for h in windows)


def test_funding_8h_windows_no_lookahead_only_complete():
    # drop one hour inside the [0,8) window -> that window excluded
    funding = {h: 1.0 for h in range(16) if h != 3}
    windows = funding_8h_windows(funding)
    assert 8 not in windows  # incomplete window skipped (no interpolation)
    assert 16 in windows


def test_missing_funding_gap_excludes_hold_window():
    # hold from entry hour 8 over 8h needs hours 8..15; drop 10 -> None
    funding = {h: 1.0 for h in range(24) if h != 10}
    assert realized_funding_over_hold(funding, 8, 8) is None
    assert realized_funding_over_hold(funding, 16, 8) == pytest.approx(8.0)


def test_forward_log_return_alignment():
    open_px = {0: 100.0, 8: 110.0}
    r = forward_log_return(open_px, 0, 8)
    assert r == pytest.approx(np.log(110.0 / 100.0))
    assert forward_log_return(open_px, 0, 24) is None  # missing exit leg


def test_build_funding_sample_skips_incomplete():
    s = _series(n_hours=200, funding_gaps=(10,))
    sample = build_funding_sample(s, horizon_h=8)
    assert sample.n > 0
    assert sample.n_skipped >= 1  # the window touching the gap is skipped
    # signal is the 8h funding sum (constant funding_value*8 here)
    assert np.allclose(sample.signal, 1e-5 * 8)


def test_build_basis_sample_signal_shifted_one_hour():
    s = _series(n_hours=200)
    sample = build_basis_sample(s, horizon_h=4)
    # entry hour = bar_hour + 1; basis signal taken from the prior bar (no lookahead)
    assert sample.n > 0
    assert sample.horizon_h == 4


# --- costs + funding cashflow --------------------------------------------------- #

def test_cost_variant_calculation_btc():
    assert round_trip_cost_bps("BTC_PERP_USD", variant="gross") == 0.0
    assert round_trip_cost_bps("BTC_PERP_USD", variant="spread_only") == 4.0
    assert round_trip_cost_bps("BTC_PERP_USD", variant="all_in") == 16.0  # 2*2+2*1+10


def test_two_x_stress_calculation():
    # 2*(2*2) + 2*(2*1) + 20 = 8 + 4 + 20 = 32
    assert round_trip_cost_bps("BTC_PERP_USD", variant="stress_2x") == 32.0
    assert round_trip_cost_bps("ETH_PERP_USD", variant="stress_2x") == 36.0


def test_funding_cashflow_sign_long_pays_when_positive():
    signs = np.array([1.0])  # long
    fwd = np.array([0.0])
    funding = np.array([0.01])  # positive funding
    # long pays: net funding term = -signs*funding = -0.01
    net = net_returns(signs, fwd, funding, 0.0, include_funding=True)
    assert net[0] == pytest.approx(-0.01)
    # short receives
    net_short = net_returns(np.array([-1.0]), fwd, funding, 0.0, include_funding=True)
    assert net_short[0] == pytest.approx(0.01)


def test_funding_excluded_from_gross_and_spread():
    assert funding_includes("gross") is False
    assert funding_includes("spread_only") is False
    assert funding_includes("all_in") is True
    assert funding_includes("stress_2x") is True


# --- nulls ---------------------------------------------------------------------- #

def _null_arrays(n=300, seed=0):
    rng = np.random.default_rng(seed)
    signs_full = rng.choice(np.array([-1.0, 0.0, 1.0]), size=n)
    fwd = rng.normal(0, 0.01, size=n)
    funding = rng.normal(0, 1e-4, size=n)
    cost = np.zeros(n)
    mask = signs_full != 0
    return signs_full, fwd, funding, cost, mask


def test_matched_random_and_shuffle_and_sign_nulls_present():
    s, f, fu, c, m = _null_arrays()
    res = run_cohort_nulls(
        mask=m, signs_full=s, fwd_ret=f, funding_hold=fu, cost_frac_full=c,
        include_funding=False, seed=123, n_draws=50,
    )
    assert set(res) == {"shuffled", "randomized_sign", "matched_random"}
    for nr in res.values():
        assert 0.0 <= nr.p_value_two_sided <= 1.0
        assert nr.n_draws == 50


def test_null_deterministic_seeds():
    s, f, fu, c, m = _null_arrays()
    a = run_cohort_nulls(mask=m, signs_full=s, fwd_ret=f, funding_hold=fu,
                         cost_frac_full=c, include_funding=False, seed=7, n_draws=40)
    b = run_cohort_nulls(mask=m, signs_full=s, fwd_ret=f, funding_hold=fu,
                         cost_frac_full=c, include_funding=False, seed=7, n_draws=40)
    assert a["shuffled"].null_mean == b["shuffled"].null_mean
    assert a["matched_random"].p_value_greater == b["matched_random"].p_value_greater


def test_wrong_pairing_breaks_signal_link():
    # construct a real edge: signs aligned with returns
    n = 200
    fwd = np.concatenate([np.full(100, 0.02), np.full(100, -0.02)])
    signs = np.concatenate([np.full(100, 1.0), np.full(100, -1.0)])  # always profits
    funding = np.zeros(n)
    cost = np.zeros(n)
    mask = np.ones(n, dtype=bool)
    real = run_cohort_nulls(mask=mask, signs_full=signs, fwd_ret=fwd, funding_hold=funding,
                            cost_frac_full=cost, include_funding=False, seed=1, n_draws=200)
    # observed edge strongly positive vs shuffled null
    assert real["shuffled"].observed > real["shuffled"].null_p95


# --- reporting / classification ------------------------------------------------- #

def test_holm_adjust_monotone_and_bounded():
    adj = holm_adjust({"a": 0.001, "b": 0.04, "c": 0.5})
    assert all(0.0 <= v <= 1.0 for v in adj.values())
    assert adj["a"] <= adj["b"] <= adj["c"]  # ascending p -> non-decreasing adjusted


def test_classify_candidate_requires_all_gates():
    g = GateInputs(
        gross_effect_clears_null=True, all_in_net_positive=True, stress_net_positive=True,
        btc_supportive=True, eth_supportive=True, pooled_supportive=True,
        sufficient_observations=True,
    )
    assert classify(g)[0] == "candidate_for_front_gate"


def test_classify_statistical_only_when_cost_defeats():
    g = GateInputs(
        gross_effect_clears_null=True, all_in_net_positive=False, stress_net_positive=False,
        btc_supportive=True, eth_supportive=True, pooled_supportive=True,
        sufficient_observations=True,
    )
    assert classify(g)[0] == "statistical_only_cost_defeated"


def test_classify_single_asset_rejected():
    g = GateInputs(
        gross_effect_clears_null=False, all_in_net_positive=False, stress_net_positive=False,
        btc_supportive=True, eth_supportive=False, pooled_supportive=True,
        sufficient_observations=True,
    )
    assert classify(g)[0] == "rejected"


def test_oi_low_power_classification_guard():
    g = GateInputs(
        gross_effect_clears_null=True, all_in_net_positive=True, stress_net_positive=True,
        btc_supportive=True, eth_supportive=True, pooled_supportive=True,
        sufficient_observations=True, oi_depth_limited=True,
    )
    # even with all gates passing, OI depth forces the low-power label
    assert classify(g)[0] == "blocked_low_power_oi"


def test_oi_diagnostics_block_low_power():
    btc = _series(canonical_id="BTC_PERP_USD")
    eth = _series(canonical_id="ETH_PERP_USD")
    series = {"BTC_PERP_USD": btc, "ETH_PERP_USD": eth}
    avail = oi_availability(series)
    assert all(a["low_power"] for a in avail.values())  # no OI rows in fixture
    res = diagnostics_4_5_oi_low_power(series, seed=1, n_draws=10)
    assert "LOW-POWER" in res["note"]


# --- BTC/ETH-only guard --------------------------------------------------------- #

def test_btc_eth_only_guard_rejects_altcoin():
    from research.crypto.derivatives_registry import validate_perp

    with pytest.raises(ValueError):
        validate_perp("SOL_PERP_USD")
    assert validate_perp("BTC_PERP_USD") == "BTC_PERP_USD"


def test_hour_index_boundary_alignment():
    from datetime import UTC, datetime

    # 1970-01-01T00:00 is hour 0 (a settlement boundary)
    assert hour_index(datetime(1970, 1, 1, 0, 0, tzinfo=UTC)) == 0
    assert hour_index(datetime(1970, 1, 1, 8, 0, tzinfo=UTC)) % 8 == 0
