"""research/backtrader_lane — local-only Backtrader secondary verification lane.

`strategy_evidence: false`. This package is verification infrastructure for the
bespoke backtest engine in `src/forex_bot/backtesting/`. It does not, cannot,
and must not approve any strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011,
CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only exactly as
documented; CAMPAIGN_014 remains scaffold-only.

Safety invariants (enforced by tests and the freeze gate):

- No imports from any `backtrader.brokers.oandabroker`,
  `backtrader.feeds.oanda`, or `backtrader.stores.oandastore` module.
- No imports from `lean` / `quantconnect`.
- No network calls. No OANDA API. No credentials read/printed.
- `Cerebro` is run locally over pre-exported CSV / pandas H4 candles only.

See:

- `docs/research/INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md`
- `docs/research/BACKTRADER_INSTALL_AND_SMOKE_RESULT.md`
"""

from __future__ import annotations

__all__: list[str] = []
