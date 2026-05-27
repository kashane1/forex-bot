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
from research.financing.fixtures import (
    FixtureValidationError,
    ObservedEventDict,
    canonical_event_key,
    load_observed_event_fixture,
    load_rate_fixture,
    utc_date_of,
)
from research.financing.manual_csv import (
    ManualCsvValidationError,
    load_manual_csv_rate_schedule,
)
from research.financing.models import (
    DailyFinancingEvent,
    FinancingCalculatorConfig,
    FinancingRunReport,
    FinancingSourceType,
    FinancingTreatment,
    MissingRatePolicy,
    PositionFinancingSummary,
    PositionInterval,
    RatePair,
)
from research.financing.overlay import (
    apply_financing_overlay,
    load_trades_from_csv,
    load_trades_from_glob,
    write_overlay_result,
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
    "FinancingSourceType",
    "FinancingTreatment",
    "FixtureValidationError",
    "ManualCsvValidationError",
    "MissingFinancingRateError",
    "MissingRatePolicy",
    "ObservedEventDict",
    "PositionFinancingSummary",
    "PositionInterval",
    "RatePair",
    "TableRateSource",
    "apply_financing_overlay",
    "calculate_position",
    "calculate_run",
    "canonical_event_key",
    "default_stress_rate_source",
    "dump_events_json",
    "load_manual_csv_rate_schedule",
    "load_observed_event_fixture",
    "load_rate_fixture",
    "load_trades_from_csv",
    "load_trades_from_glob",
    "render_summary_md",
    "utc_date_of",
    "write_overlay_result",
]
