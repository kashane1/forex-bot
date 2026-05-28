"""Diagnostic labels + entry-feature separation for the C022 winner/loser study.

Labels here intentionally use the trade's **future outcome** (result_r, MFE/MAE,
exit_reason). That is correct for a *diagnostic* separation study — we ask "did
any entry-time feature distinguish trades that later won from those that lost?".
These labels MUST NOT be used as live/trading features; they are post-hoc by
construction. The build step keeps outcome columns strictly separate from the
entry-time feature columns so no outcome ever leaks into separation scoring.

Approves nothing, changes no verdict, tunes nothing.
"""

from __future__ import annotations

from collections.abc import Mapping

__all__ = [
    "FEATURE_DENYLIST",
    "LABEL_NAMES",
    "build_labels",
    "entry_feature_columns",
]

# Outcome / post-entry columns — never valid as entry-time separation features.
FEATURE_DENYLIST: frozenset[str] = frozenset({
    "result_r", "exit_reason", "bars_held", "pnl", "mfe_r", "mae_r", "mfe_status",
    "reached_plus_0_25r", "reached_plus_0_5r", "reached_plus_1_0r",
    "touched_minus_0_5r", "touched_minus_0_9r",
    # identifiers / provenance / derived labels (not features)
    "campaign_id", "split", "entry_time", "exit_time", "decision_time",
    "recon_h4_bias", "h4_feature_time", "h1_feature_time",
})

LABEL_NAMES: tuple[str, ...] = (
    "profitable_trade",
    "survived_to_time_exit",
    "hard_stop_loss",
    "reached_plus_0_5r",
    "clean_winner",
    "straight_to_stop",
)


def _num(v: object) -> float | None:
    if v is None:
        return None
    try:
        f = float(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return f if f == f else None  # drop NaN


def _truthy(v: object) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    s = str(v).strip().lower()
    return s in {"true", "1", "yes"}


def build_labels(row: Mapping[str, object]) -> dict[str, bool | None]:
    """Build the six diagnostic labels for one per-trade record.

    Returns ``None`` for a label when its inputs are missing (never fabricated).
    Labels are derived from outcome fields only — they are not features.
    """
    result_r = _num(row.get("result_r"))
    exit_reason = row.get("exit_reason")
    exit_s = str(exit_reason).strip().lower() if exit_reason is not None else None
    mae_r = _num(row.get("mae_r"))
    reached_025 = _truthy(row.get("reached_plus_0_25r"))
    reached_05 = _truthy(row.get("reached_plus_0_5r"))

    is_time = exit_s == "time_stop" if exit_s is not None else None
    is_stop = exit_s == "hard_stop" if exit_s is not None else None

    profitable = (result_r > 0) if result_r is not None else None

    # clean_winner: profitable AND adverse excursion never got deep (MAE > -0.5R).
    if profitable is None or mae_r is None:
        clean_winner = None
    else:
        clean_winner = bool(profitable and mae_r > -0.5)

    # straight_to_stop: stopped out AND never reached +0.25R before the stop.
    if is_stop is None:
        straight_to_stop = None
    else:
        straight_to_stop = bool(is_stop and not reached_025)

    return {
        "profitable_trade": profitable,
        "survived_to_time_exit": is_time,
        "hard_stop_loss": is_stop,
        "reached_plus_0_5r": bool(reached_05),
        "clean_winner": clean_winner,
        "straight_to_stop": straight_to_stop,
    }


def entry_feature_columns(columns: list[str]) -> list[str]:
    """Entry-time feature columns: every column except outcomes/ids/provenance.

    ``instrument``, ``side``, ``session_bucket``, ``weekday``,
    ``volatility_regime``, ``hour`` are kept (categorical/time entry features).
    """
    return [c for c in columns if c not in FEATURE_DENYLIST]
