"""Free / local independent parity verifier.

This package re-implements the CAMPAIGN_002 H4 ``trend_following 0.1.0``
strategy + engine mechanics from the committed mapping spec, with no
imports from ``src/forex_bot/`` and no external services. It exists
to provide an independent corroboration check against the bespoke
backtest engine — verification only, never a strategy approval.

Safety constraints (enforced by code structure, tests, and CI gates):

- imports nothing from ``forex_bot`` (the bespoke engine);
- makes no network calls, no broker calls, no QuantConnect / LEAN
  calls;
- reads only local files;
- writes no strategy approval, no campaign verdict, no broker order;
- the verifier's outputs are diagnostic only — ``strategy_evidence: false``.

See ``docs/research/FREE_LOCAL_PARITY_VERIFIER_PLAN.md`` for the
design and ``docs/research/INFRA_FREE_LOCAL_PARITY_VERIFIER_001_PLAN.md``
for the implementation-sprint plan.
"""

from research.parity_verifier.models import (
    Bar,
    CandleSeries,
    ComparisonReport,
    ComparisonStatus,
    DivergenceClassification,
    InstrumentSpec,
    PairResult,
    Side,
    Signal,
    StopState,
    Trade,
    TradeExitReason,
    VerifierConfig,
    VerifierResult,
)

__all__ = [
    "Bar",
    "CandleSeries",
    "ComparisonReport",
    "ComparisonStatus",
    "DivergenceClassification",
    "InstrumentSpec",
    "PairResult",
    "Side",
    "Signal",
    "StopState",
    "Trade",
    "TradeExitReason",
    "VerifierConfig",
    "VerifierResult",
]
