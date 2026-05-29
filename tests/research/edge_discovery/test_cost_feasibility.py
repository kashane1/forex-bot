"""Cost-feasibility flagging tests.

Pin the hostile threshold, the C025/C026 timeframe ladder classification,
min-target-R, pair advantaged/disadvantaged, and input guards.
"""

from __future__ import annotations

import pytest
from research.edge_discovery.cost_feasibility import (
    classify_cost_feasibility,
    cost_feasibility_table,
    min_target_r_to_overcome,
    opportunity_score,
    round_trip_cost_pips,
)


def test_round_trip_and_min_target() -> None:
    assert round_trip_cost_pips(1.5, slip_pips=0.2) == pytest.approx(1.9)
    # 1.9 pips of cost against a 19-pip stop = 0.1 R just to break even.
    assert min_target_r_to_overcome(1.9, 19.0) == pytest.approx(0.1)
    with pytest.raises(ValueError, match="stop_pips must be positive"):
        min_target_r_to_overcome(1.9, 0.0)


def test_opportunity_score_bounds() -> None:
    assert opportunity_score(0.0) == 1.0
    assert opportunity_score(0.25, hostile_ratio=0.25) == 0.0
    assert opportunity_score(0.5, hostile_ratio=0.25) == 0.0  # clipped
    assert 0.0 < opportunity_score(0.15, hostile_ratio=0.25) < 1.0


def test_c025_c026_timeframe_ladder_classification() -> None:
    # The committed C025/C026 spread/ATR ladder.
    ladder = {"M3": 0.59, "M5": 0.45, "M15": 0.23, "M30": 0.15}
    df = cost_feasibility_table(ladder, kind="timeframe", hostile_ratio=0.25)
    flags = dict(zip(df["label"], df["flags"], strict=True))
    assert "COST_HOSTILE" in flags["M3"] and "TIMEFRAME_TOO_FAST" in flags["M3"]
    assert "COST_HOSTILE" in flags["M5"] and "TIMEFRAME_TOO_FAST" in flags["M5"]
    assert flags["M15"] == "COST_FEASIBLE"
    assert flags["M30"] == "COST_FEASIBLE"


def test_session_hostile_flag() -> None:
    cell = classify_cost_feasibility("late", 0.4, kind="session", hostile_ratio=0.25)
    assert "COST_HOSTILE" in cell.flags
    assert "SESSION_HOSTILE" in cell.flags


def test_pair_advantaged_and_disadvantaged() -> None:
    cells = {"EUR_USD": 0.10, "USD_JPY": 0.13, "GBP_USD": 0.30}
    df = cost_feasibility_table(cells, kind="pair", flag_pairs_vs_median=True, pair_deviation=0.2)
    flags = dict(zip(df["label"], df["flags"], strict=True))
    # median is 0.13; EUR_USD well below → advantaged; GBP_USD well above → disadvantaged.
    assert "PAIR_COST_ADVANTAGED" in flags["EUR_USD"]
    assert "PAIR_COST_DISADVANTAGED" in flags["GBP_USD"]


def test_min_target_r_populated_when_pips_given() -> None:
    cell = classify_cost_feasibility(
        "EUR_USD_M5", 0.45, spread_pips=1.5, stop_pips=10.0, kind="timeframe"
    )
    assert cell.min_target_r is not None
    assert cell.min_target_r == pytest.approx(0.19)


def test_empty_table_raises() -> None:
    with pytest.raises(ValueError, match="empty"):
        cost_feasibility_table({})
