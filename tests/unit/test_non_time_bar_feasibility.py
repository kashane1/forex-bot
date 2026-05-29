"""Unit tests for the non-time-bar feasibility analyzer (diagnostic-only).

Pure-function coverage: cost-to-threshold, cost-to-risk, cadence classification,
the too-noisy / too-sparse / feasible label paths, JPY pip handling, and the
deterministic summary output. No database, no network.
"""

from __future__ import annotations

import pytest

from forex_bot.research.non_time_bar_feasibility import (
    C029_COST_TO_RISK,
    FEASIBLE_COST_TO_RISK,
    bars_per_year,
    build_cell,
    classify_cadence,
    classify_cell,
    compare_pair_vs_others,
    compare_range_vs_volatility,
    cost_floor_row,
    cost_to_risk_ratio,
    cost_to_threshold_ratio,
    is_too_noisy,
    label_counts,
    min_gross_expectancy_to_survive,
    nominal_stop_pips,
    round_trip_cost_pips,
    spread_price_to_pips,
    summarize_feasibility,
)

# --------------------------------------------------------------------------- #
# Cost economics
# --------------------------------------------------------------------------- #


def test_round_trip_cost_is_spread_plus_two_slippage():
    # C029 model: full spread + 0.2 pip slippage per side.
    assert round_trip_cost_pips(1.9, slippage_pips_per_side=0.2) == pytest.approx(2.3)
    assert round_trip_cost_pips(0.0, slippage_pips_per_side=0.0) == 0.0


def test_round_trip_cost_rejects_negative():
    with pytest.raises(ValueError):
        round_trip_cost_pips(-0.1)
    with pytest.raises(ValueError):
        round_trip_cost_pips(1.0, slippage_pips_per_side=-0.1)


def test_cost_to_threshold_ratio():
    assert cost_to_threshold_ratio(2.3, 10.0) == pytest.approx(0.23)
    with pytest.raises(ValueError):
        cost_to_threshold_ratio(2.3, 0.0)


def test_cost_to_risk_reproduces_c029_floor():
    # C029: round-trip ~2.29 pips against a ~24.05-pip stop -> ~0.095 cost-to-risk.
    ctr = cost_to_risk_ratio(2.29, 24.05)
    assert ctr == pytest.approx(0.0952, abs=1e-3)
    assert ctr == pytest.approx(C029_COST_TO_RISK, abs=2e-3)


def test_min_gross_expectancy_is_cost_to_risk():
    assert min_gross_expectancy_to_survive(0.095) == 0.095


def test_nominal_stop_pips_multiple():
    assert nominal_stop_pips(10.0, 2.0) == 20.0
    with pytest.raises(ValueError):
        nominal_stop_pips(0.0, 2.0)
    with pytest.raises(ValueError):
        nominal_stop_pips(10.0, 0.0)


# --------------------------------------------------------------------------- #
# JPY pip handling
# --------------------------------------------------------------------------- #


def test_spread_price_to_pips_jpy_vs_default():
    # USD_JPY pip = 0.01: a 0.019 price spread is 1.9 pips.
    assert spread_price_to_pips(0.019, "USD_JPY") == pytest.approx(1.9)
    # EUR_USD pip = 0.0001: a 0.00008 price spread is 0.8 pips.
    assert spread_price_to_pips(0.00008, "EUR_USD") == pytest.approx(0.8)
    with pytest.raises(ValueError):
        spread_price_to_pips(-0.001, "USD_JPY")


# --------------------------------------------------------------------------- #
# Cadence
# --------------------------------------------------------------------------- #


def test_bars_per_year_normalisation():
    # 2000 bars over ~365.25 days -> ~2000/year.
    assert bars_per_year(2000, 365.25) == pytest.approx(2000.0)
    # 1000 bars over half a year -> ~2000/year.
    assert bars_per_year(1000, 365.25 / 2) == pytest.approx(2000.0)
    with pytest.raises(ValueError):
        bars_per_year(100, 0.0)


def test_classify_cadence_bands():
    assert classify_cadence(100.0) == "too_sparse"
    assert classify_cadence(5000.0) == "sane"
    assert classify_cadence(50_000.0) == "very_high"


def test_is_too_noisy():
    assert is_too_noisy(0.20, 5000.0) is True  # multi-threshold rate high
    assert is_too_noisy(0.01, 50_000.0) is True  # cadence very high
    assert is_too_noisy(0.01, 5000.0) is False


# --------------------------------------------------------------------------- #
# Cell classification — every label path
# --------------------------------------------------------------------------- #


def _classify(**kw):
    base = dict(
        bar_count=5000,
        per_year=3000.0,
        multi_threshold_rate=0.02,
        cost_to_risk_baseline=0.04,
        cost_to_risk_wide=0.02,
    )
    base.update(kw)
    return classify_cell(**base)


def test_label_inconclusive_when_too_few_bars():
    assert _classify(bar_count=10) == "INCONCLUSIVE"


def test_label_too_sparse():
    assert _classify(per_year=100.0) == "TOO_SPARSE"


def test_label_too_noisy_multi_threshold():
    assert _classify(multi_threshold_rate=0.2) == "TOO_NOISY"


def test_label_too_noisy_high_cadence():
    assert _classify(per_year=50_000.0) == "TOO_NOISY"


def test_label_feasible_for_strategy_research():
    assert _classify(cost_to_risk_baseline=0.04) == "FEASIBLE_FOR_STRATEGY_RESEARCH"
    # exactly at the band edge is feasible
    assert _classify(cost_to_risk_baseline=FEASIBLE_COST_TO_RISK) == (
        "FEASIBLE_FOR_STRATEGY_RESEARCH"
    )


def test_label_feasible_only_with_larger_stops():
    assert (
        _classify(cost_to_risk_baseline=0.09, cost_to_risk_wide=0.045)
        == "FEASIBLE_ONLY_WITH_LARGER_STOPS"
    )


def test_label_cost_dominated():
    assert (
        _classify(cost_to_risk_baseline=0.15, cost_to_risk_wide=0.075) == "COST_DOMINATED"
    )


def test_priority_sparse_beats_cost():
    # A sparse cell that would otherwise be cost-dominated is labelled TOO_SPARSE.
    assert _classify(per_year=50.0, cost_to_risk_baseline=0.3) == "TOO_SPARSE"


# --------------------------------------------------------------------------- #
# build_cell — end-to-end derived fields + C029 reproduction
# --------------------------------------------------------------------------- #


def test_build_cell_reproduces_c029_marginal_case():
    # USD_JPY 10-pip range, ~1.9-pip spread, baseline 2x stop = 20-pip nominal.
    cell = build_cell(
        instrument="USD_JPY",
        bar_type="range",
        method=None,
        threshold_pips=10.0,
        bar_count=40_000,
        window_days=949.0,  # ~2.6y C029 train window
        spread_pips=1.9,
        multi_threshold_rate=0.03,
    )
    assert cell.round_trip_cost_pips == pytest.approx(2.3)
    assert cell.baseline_stop_pips == pytest.approx(20.0)
    assert cell.wide_stop_pips == pytest.approx(40.0)
    # 2.3 / 20 = 0.115 baseline -> above feasible (0.05) and above marginal (0.10)
    assert cell.cost_to_risk_baseline == pytest.approx(0.115)
    # 2.3 / 40 = 0.0575 wide -> still above 0.05 feasible band
    assert cell.cost_to_risk_wide == pytest.approx(0.0575)
    # high cadence (40k bars / 2.6y ~ 15k/yr is sane, but verify) -> cost-dominated
    assert cell.label == "COST_DOMINATED"


def test_build_cell_wide_threshold_becomes_feasible():
    # 30-pip range, baseline 2x = 60-pip stop, ~1.9-pip spread -> 2.3/60 = 0.038.
    cell = build_cell(
        instrument="USD_JPY",
        bar_type="range",
        method=None,
        threshold_pips=30.0,
        bar_count=5000,
        window_days=949.0,
        spread_pips=1.9,
        multi_threshold_rate=0.01,
    )
    assert cell.cost_to_risk_baseline == pytest.approx(0.0383, abs=1e-3)
    assert cell.label == "FEASIBLE_FOR_STRATEGY_RESEARCH"


def test_build_cell_volatility_uses_vol_stop_multiples():
    # Volatility baseline stop is 1x threshold, wide is 2x.
    cell = build_cell(
        instrument="EUR_USD",
        bar_type="volatility",
        method="true_range",
        threshold_pips=40.0,
        bar_count=3000,
        window_days=949.0,
        spread_pips=0.8,
        multi_threshold_rate=0.01,
    )
    assert cell.baseline_stop_pips == pytest.approx(40.0)  # 1x
    assert cell.wide_stop_pips == pytest.approx(80.0)  # 2x
    # cost = 0.8 + 0.4 = 1.2; 1.2/40 = 0.03 -> feasible
    assert cell.round_trip_cost_pips == pytest.approx(1.2)
    assert cell.cost_to_risk_baseline == pytest.approx(0.03)
    assert cell.label == "FEASIBLE_FOR_STRATEGY_RESEARCH"


# --------------------------------------------------------------------------- #
# Comparisons + deterministic summary
# --------------------------------------------------------------------------- #


def _sample_cells() -> list:
    return [
        build_cell(
            instrument="USD_JPY",
            bar_type="range",
            method=None,
            threshold_pips=10.0,
            bar_count=40_000,
            window_days=949.0,
            spread_pips=1.9,
            multi_threshold_rate=0.03,
        ),
        build_cell(
            instrument="USD_JPY",
            bar_type="range",
            method=None,
            threshold_pips=30.0,
            bar_count=5000,
            window_days=949.0,
            spread_pips=1.9,
            multi_threshold_rate=0.01,
        ),
        build_cell(
            instrument="EUR_USD",
            bar_type="volatility",
            method="true_range",
            threshold_pips=40.0,
            bar_count=3000,
            window_days=949.0,
            spread_pips=0.8,
            multi_threshold_rate=0.01,
        ),
    ]


def test_label_counts_stable_order():
    counts = label_counts(_sample_cells())
    # all six labels present as keys, in a stable order
    assert next(iter(counts.keys())) == "FEASIBLE_FOR_STRATEGY_RESEARCH"
    assert counts["FEASIBLE_FOR_STRATEGY_RESEARCH"] == 2
    assert counts["COST_DOMINATED"] == 1


def test_compare_range_vs_volatility():
    cmp = compare_range_vs_volatility(_sample_cells())
    assert cmp["range"]["n_cells"] == 2
    assert cmp["volatility"]["n_cells"] == 1
    assert cmp["volatility"]["feasible_share"] == 1.0


def test_compare_pair_vs_others():
    cmp = compare_pair_vs_others(_sample_cells(), focus="USD_JPY")
    assert cmp["USD_JPY"]["n_cells"] == 2
    assert cmp["others_pooled"]["n_cells"] == 1


def test_summarize_feasibility_is_deterministic():
    cells = _sample_cells()
    s1 = summarize_feasibility(cells)
    s2 = summarize_feasibility(list(reversed(cells)))
    # ordering is canonicalised -> identical regardless of input order
    assert s1 == s2
    assert s1["n_cells"] == 3
    assert s1["pairs"] == ["EUR_USD", "USD_JPY"]


def test_cost_floor_row_flags():
    cells = _sample_cells()
    # the 10-pip USD_JPY cell does NOT beat the C029 floor (it ~equals/exceeds it)
    c10 = next(c for c in cells if c.threshold_pips == 10.0)
    row10 = cost_floor_row(c10)
    assert row10.beats_c029_cost_floor is False
    # the 30-pip cell (0.038 cost-to-risk) beats the C029 floor and is lab-survivable
    c30 = next(c for c in cells if c.threshold_pips == 30.0)
    row30 = cost_floor_row(c30)
    assert row30.beats_c029_cost_floor is True
    assert row30.survivable_by_lab_edge is True
