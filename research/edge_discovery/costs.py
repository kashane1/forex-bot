"""Cost overlay for forward-return studies.

A deliberately simple model: a fixed spread (in pips) plus a fixed
slippage (in pips), applied once on entry and once on exit. The pip
value per price unit is inferred from the instrument code:

  * JPY-quote pairs (e.g. ``USD_JPY``): pip = 0.01
  * everything else: pip = 0.0001

The cost is expressed as a fractional return so it composes with the
log-returns from ``compute_forward_returns``:

  cost_fraction ≈ (spread_pips + 2 * slip_pips) * pip / mid_entry_price

A financing-stress overlay is also exposed, sourced from
``forex_bot.financing.CONSERVATIVE_BP_PER_DAY``. Both overlays are
*stresses* (always subtractive, never crediting), which matches the
existing campaign reporting convention.
"""

from __future__ import annotations

import sys
from collections.abc import Mapping
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from forex_bot.financing import CONSERVATIVE_BP_PER_DAY  # noqa: E402

_JPY_QUOTE_SUFFIX = "_JPY"


def pip_value_for(instrument: str) -> float:
    """Fractional price move per pip."""
    return 0.01 if instrument.endswith(_JPY_QUOTE_SUFFIX) else 0.0001


def cost_fraction(
    instrument: str,
    entry_price: float,
    *,
    spread_pips: float,
    slip_pips: float,
) -> float:
    """Round-trip cost as a fraction of entry price.

    Entry pays half-spread + slip; exit pays half-spread + slip; the
    quoted spread/slip are the values from CAMPAIGN_005 ranges (median
    1.4–1.9 pips spread on the six majors).
    """
    pip = pip_value_for(instrument)
    pips_paid = spread_pips + 2.0 * slip_pips
    if entry_price <= 0:
        raise ValueError(f"entry_price must be positive, got {entry_price}")
    return pips_paid * pip / entry_price


def financing_stress_fraction(
    instrument: str,
    *,
    bars_held: int,
    hours_per_bar: float = 4.0,
) -> float:
    """Conservative financing stress as a fractional return.

    Uses the worst-of-long/short bp/day from
    ``forex_bot.financing.CONSERVATIVE_BP_PER_DAY``. This is a *stress*,
    not a real financing accrual — financing remains unmodeled in the
    engine PnL, per ``docs/research/FINANCING_MODEL_CURRENT_ASSUMPTIONS.md``.
    """
    bp_per_day = CONSERVATIVE_BP_PER_DAY.get(instrument, max(CONSERVATIVE_BP_PER_DAY.values()))
    days = bars_held * hours_per_bar / 24.0
    return (bp_per_day / 10000.0) * days


def apply_cost_overlay(
    returns_df: pd.DataFrame,
    instrument: str,
    *,
    spread_pips: float = 1.5,
    slip_pips: float = 0.2,
    apply_financing: bool = True,
    hours_per_bar: float = 4.0,
) -> pd.DataFrame:
    """Return a copy of ``returns_df`` with three added columns:

      - ``cost_fraction`` — round-trip transaction cost as a fraction
      - ``financing_fraction`` — financing stress as a fraction
      - ``log_return_post_cost`` — ``log_return - cost_fraction
        - (financing_fraction if apply_financing else 0)``

    The cost and financing overlays are *subtractive* (they always
    reduce the post-cost return), consistent with the campaign
    convention.
    """
    if "log_return" not in returns_df.columns:
        raise ValueError("returns_df must come from compute_forward_returns()")
    if returns_df.empty:
        out = returns_df.copy()
        for c in ("cost_fraction", "financing_fraction", "log_return_post_cost"):
            out[c] = pd.Series(dtype=float)
        return out
    out = returns_df.copy()
    out["cost_fraction"] = out["entry_price"].astype(float).apply(
        lambda p: cost_fraction(instrument, float(p), spread_pips=spread_pips, slip_pips=slip_pips)
    )
    out["financing_fraction"] = out["bars_held"].astype(int).apply(
        lambda b: financing_stress_fraction(instrument, bars_held=int(b), hours_per_bar=hours_per_bar)
    )
    fin = out["financing_fraction"] if apply_financing else 0.0
    out["log_return_post_cost"] = out["log_return"] - out["cost_fraction"] - fin
    return out


def turnover_cost_burden(
    pre_cost_mean: float,
    n_trades: int,
    cost_per_trade_fraction: float,
) -> Mapping[str, float]:
    """How much of a pre-cost mean a given trade count consumes.

    Returns a dict with:
      - ``cost_per_trade`` — input echo
      - ``n_trades`` — input echo
      - ``cost_total`` — n_trades * cost_per_trade
      - ``cost_share_of_mean`` — cost_total / abs(pre_cost_mean * n_trades),
        which is the fraction of the cumulative pre-cost return that
        costs eat (clipped to >= 0; returns +inf when pre_cost_mean is
        zero, because that's exactly what cost-dominance looks like)
    """
    cost_total = n_trades * cost_per_trade_fraction
    if pre_cost_mean == 0:
        share = float("inf") if cost_total > 0 else 0.0
    else:
        share = abs(cost_total / (pre_cost_mean * n_trades))
    return {
        "cost_per_trade": cost_per_trade_fraction,
        "n_trades": float(n_trades),
        "cost_total": cost_total,
        "cost_share_of_mean": share,
    }
