"""Research-grade financing / carry / rollover cost calculator.

A reusable, independent, deterministic calculator for per-day
financing events on closed positions. Consumes a pluggable
``FinancingRateSource`` (table-backed or conservative stress)
and produces per-event records, per-position summaries, and a
position-set aggregate, all dumpable to JSON and markdown.

Strategy execution and the bespoke backtest engine's PnL stream
are **not** modified. This module sits beside them and produces
diagnostic artifacts only.

Safety constraints (mirrored from the walk-forward harness):

- imports nothing from ``forex_bot`` — independence is enforced
  by a grep test in ``tests/research/test_financing_models.py``;
- makes no network calls, no broker calls, no QuantConnect / LEAN
  calls;
- reads no files at import time;
- writes no strategy approval, no campaign verdict, no broker
  order;
- every report carries ``strategy_evidence: false`` (Pydantic
  rail);
- ``financing_treatment`` from this module's sources is at most
  ``ESTIMATED`` — ``MODELED`` remains reserved for the future
  observed-rate path in ``src/forex_bot/financing.py``.

See ``docs/research/FINANCING_MODEL_PROTOCOL.md`` for the
protocol the calculator enforces.
"""

from research.financing.calculator import (
    MissingFinancingRateError,
    calculate_position,
    calculate_run,
)
from research.financing.models import (
    DailyFinancingEvent,
    FinancingCalculatorConfig,
    FinancingRunReport,
    FinancingTreatment,
    MissingRatePolicy,
    PositionFinancingSummary,
    PositionInterval,
    RatePair,
)
from research.financing.rates import (
    CONSERVATIVE_BP_PER_DAY,
    ConservativeStressRateSource,
    FinancingRateSource,
    TableRateSource,
    default_stress_rate_source,
)
from research.financing.reporting import (
    dump_events_json,
    render_summary_md,
)

__all__ = [
    "CONSERVATIVE_BP_PER_DAY",
    "ConservativeStressRateSource",
    "DailyFinancingEvent",
    "FinancingCalculatorConfig",
    "FinancingRateSource",
    "FinancingRunReport",
    "FinancingTreatment",
    "MissingFinancingRateError",
    "MissingRatePolicy",
    "PositionFinancingSummary",
    "PositionInterval",
    "RatePair",
    "TableRateSource",
    "calculate_position",
    "calculate_run",
    "default_stress_rate_source",
    "dump_events_json",
    "render_summary_md",
]
