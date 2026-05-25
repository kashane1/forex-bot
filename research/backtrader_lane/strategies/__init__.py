"""Backtrader strategy adapters that mirror frozen forex-bot campaigns.

Importing this package registers every adapter on the runner's
campaign registry. The runner CLI does ``from research.backtrader_lane
import strategies`` for that side effect.

Each adapter is a one-way port of an already-committed, frozen
campaign's rules into Backtrader. Adapters do not tune parameters, do
not invent rules, and cannot approve strategies.
"""

from __future__ import annotations

# Side-effect imports — each module calls `register_campaign(...)` on import.
from research.backtrader_lane.strategies import (
    campaign_002_trend_following,  # noqa: F401
    campaign_011_random_entry_anchor,  # noqa: F401
)

__all__: list[str] = []
