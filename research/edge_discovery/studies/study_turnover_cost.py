"""Study 2 — turnover and cost-burden sensitivity.

Direct attack on the lesson the sprint brief's CAMPAIGN_012 / 013
narrative carries: turnover amplification of a weak edge makes the
post-cost result worse, not better.

Builds a small matrix of (pre-cost mean per trade in log-return units,
trade count) and computes:

  * cumulative pre-cost return
  * cumulative cost burden
  * cumulative post-cost return
  * cost share of |pre-cost|

The cost-per-trade comes from the same overlay the lab uses for real
studies (spread 1.5 pips + 2 * 0.2 pip slip on EUR_USD-shaped price),
matching CAMPAIGN_005's median spread observations. This is intended
as a *what-would-it-take* table: how big a per-trade edge does a
candidate need at a given trade count, and where does turnover stop
helping?

Produces JSON + Markdown. The Markdown is a simple matrix readable by
a human reviewer; the JSON is the same data for downstream programmatic
use.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from research.edge_discovery.costs import cost_fraction

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs"

# Sweep the pre-cost edge per trade in log-return units. ~0.0001 ≈ ~1
# pip of EUR_USD-ish edge per trade, so the table spans -2 pips to +5
# pips of pre-cost edge per trade.
PRE_COST_EDGES = (-0.00020, -0.00010, 0.0, +0.00010, +0.00025, +0.00050)
TRADE_COUNTS = (50, 100, 250, 500, 1000, 2500)
# Cost basis: EUR_USD-shaped midprice with the lab's default overlay.
INSTRUMENT = "EUR_USD"
ENTRY_PRICE = 1.1000
SPREAD_PIPS = 1.5
SLIP_PIPS = 0.2


@dataclass(frozen=True)
class TurnoverCell:
    pre_cost_edge_per_trade: float
    n_trades: int
    cost_per_trade: float
    cumulative_pre_cost: float
    cumulative_cost: float
    cumulative_post_cost: float
    cost_share_of_pre_cost: float | None  # None when pre-cost = 0


def _build_cells() -> list[TurnoverCell]:
    cost_per_trade = cost_fraction(
        INSTRUMENT,
        entry_price=ENTRY_PRICE,
        spread_pips=SPREAD_PIPS,
        slip_pips=SLIP_PIPS,
    )
    cells: list[TurnoverCell] = []
    for edge in PRE_COST_EDGES:
        for n in TRADE_COUNTS:
            cum_pre = edge * n
            cum_cost = cost_per_trade * n
            cum_post = cum_pre - cum_cost
            if cum_pre == 0:
                share = None
            else:
                share = abs(cum_cost / cum_pre)
            cells.append(
                TurnoverCell(
                    pre_cost_edge_per_trade=edge,
                    n_trades=n,
                    cost_per_trade=cost_per_trade,
                    cumulative_pre_cost=cum_pre,
                    cumulative_cost=cum_cost,
                    cumulative_post_cost=cum_post,
                    cost_share_of_pre_cost=share,
                )
            )
    return cells


def _matrix_lines(cells: list[TurnoverCell], field: str, header: str) -> list[str]:
    lines = [f"### {header}", ""]
    lines.append("| pre-cost edge / trade | " + " | ".join(f"n={n}" for n in TRADE_COUNTS) + " |")
    lines.append("|---" * (1 + len(TRADE_COUNTS)) + "|")
    by_edge: dict[float, dict[int, TurnoverCell]] = {e: {} for e in PRE_COST_EDGES}
    for c in cells:
        by_edge[c.pre_cost_edge_per_trade][c.n_trades] = c
    for e in PRE_COST_EDGES:
        row = [f"{e:+.5f}"]
        for n in TRADE_COUNTS:
            value = getattr(by_edge[e][n], field)
            row.append("—" if value is None else f"{value:+.5f}" if isinstance(value, float) else f"{value}")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    return lines


def run() -> Path:
    cells = _build_cells()
    cost_per_trade = cells[0].cost_per_trade

    md_lines: list[str] = []
    md_lines.append("# Edge-discovery study — turnover_cost_sensitivity")
    md_lines.append("")
    md_lines.append("> Exploratory lab output. Not a strategy verdict; does not approve,")
    md_lines.append("> promote, or change any campaign status. See")
    md_lines.append("> `docs/research/EDGE_DISCOVERY_LAB_001_PLAN.md`.")
    md_lines.append("")
    md_lines.append("## Setup")
    md_lines.append("")
    md_lines.append(f"- Instrument basis: `{INSTRUMENT}` at midprice `{ENTRY_PRICE}`")
    md_lines.append(f"- Cost model: spread `{SPREAD_PIPS}` pip + 2 × slip `{SLIP_PIPS}` pip")
    md_lines.append(f"- Implied cost per trade (round-trip): `{cost_per_trade:+.6f}` log-return units")
    md_lines.append(f"- Pre-cost edge sweep (per trade): `{list(PRE_COST_EDGES)}`")
    md_lines.append(f"- Trade-count sweep: `{list(TRADE_COUNTS)}`")
    md_lines.append("")
    md_lines.extend(_matrix_lines(cells, "cumulative_post_cost", "Cumulative post-cost return (log units)"))
    md_lines.extend(_matrix_lines(cells, "cumulative_cost", "Cumulative cost burden (log units)"))
    md_lines.extend(_matrix_lines(cells, "cost_share_of_pre_cost", "Cost share of pre-cost cumulative"))
    md_lines.append("## Reading")
    md_lines.append("")
    md_lines.append(
        "- Reading down a column shows how a fixed trade count amplifies "
        "an edge in both directions: when the per-trade pre-cost edge is "
        "negative, more trades make the post-cost result strictly worse."
    )
    md_lines.append(
        "- Reading along a row shows how cumulative cost burden grows "
        "linearly in `n`. The cost-per-trade is `0.00015 ≈ 1.5 pips` on "
        "an EUR_USD-shaped midprice; a candidate needs a per-trade "
        "pre-cost edge well above that *plus* a margin over the random-"
        "entry null (CAMPAIGN_005: −0.095 R aggregate) before turnover "
        "helps it."
    )
    md_lines.append(
        "- The cells where `cost_share_of_pre_cost > 1` are cost-dominated: "
        "the strategy loses more in costs than the edge gains pre-cost. "
        "These cells should never graduate to a formal campaign."
    )
    md_lines.append("")

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    md_path = OUTPUTS / "study_turnover_cost.md"
    json_path = OUTPUTS / "study_turnover_cost.json"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {
                "label": "turnover_cost_sensitivity",
                "setup": {
                    "instrument": INSTRUMENT,
                    "entry_price": ENTRY_PRICE,
                    "spread_pips": SPREAD_PIPS,
                    "slip_pips": SLIP_PIPS,
                    "pre_cost_edges": list(PRE_COST_EDGES),
                    "trade_counts": list(TRADE_COUNTS),
                    "cost_per_trade": cost_per_trade,
                },
                "cells": [asdict(c) for c in cells],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return md_path


if __name__ == "__main__":
    p = run()
    print(f"wrote {p}")
