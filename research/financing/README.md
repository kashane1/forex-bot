# research/financing — research-grade financing calculator

A reusable, independent calculator for per-day financing /
carry / rollover cashflows on closed positions. Produces
per-event records, per-position summaries, and a position-set
aggregate, all dumpable to JSON and markdown.

> `strategy_evidence: false`. The calculator is diagnostic
> infrastructure. It does **not** approve a strategy.
> CAMPAIGN_002 remains REJECT. `configs/approved_strategies.yaml`
> stays empty. Paper / demo / live remain blocked. This module
> is **never** the source of `MODELED` financing — that path
> is reserved for `src/forex_bot/financing.FutureOandaObservedFinancingModel`.

## Module layout

| module | role |
|---|---|
| `models.py` | Pydantic models — `PositionInterval`, `FinancingCalculatorConfig`, `DailyFinancingEvent`, `PositionFinancingSummary`, `FinancingRunReport`, `RatePair`, `FinancingTreatment`, `MissingRatePolicy` |
| `rates.py` | `FinancingRateSource` interface + `TableRateSource` (per-date table) + `ConservativeStressRateSource` (debit-only pessimistic bp/day, default) |
| `calculator.py` | `calculate_position` and `calculate_run` — pure functions over local inputs |
| `reporting.py` | `render_summary_md` and `dump_events_json` — deterministic formatting |

No file under `research/financing/` imports from `forex_bot`. A
grep-enforced test rail in
`tests/research/test_financing_models.py` guards independence.

## Protocol

See [`docs/research/FINANCING_MODEL_PROTOCOL.md`](../../docs/research/FINANCING_MODEL_PROTOCOL.md)
for the rules the calculator enforces (rollover convention,
Wednesday triple swap, weekend skip, missing-rate fallback,
currency conversion, stress mode, deterministic reproducibility).

## Quick example — stress run

```python
from datetime import UTC, datetime
from decimal import Decimal

from research.financing import (
    FinancingCalculatorConfig,
    PositionInterval,
    calculate_run,
    default_stress_rate_source,
    dump_events_json,
    render_summary_md,
)

positions = [
    PositionInterval(
        position_id="t1",
        instrument="EUR_USD",
        side="long",
        units=Decimal("10000"),
        entry_price=Decimal("1.0800"),
        open_time=datetime(2026, 5, 18, 8, 0, tzinfo=UTC),
        close_time=datetime(2026, 5, 22, 16, 0, tzinfo=UTC),
    ),
]

report = calculate_run(
    positions,
    rate_source=default_stress_rate_source(),
    config=FinancingCalculatorConfig(),  # v1 defaults
)

print(render_summary_md(report))
# Write JSON to disk in calling code:
# Path("financing_report.json").write_text(dump_events_json(report))
```

The stress run uses the bp/day table mirrored from
`src/forex_bot/financing.py`. Both sides debit (never a credit),
Wednesday rollovers count triple, weekends are skipped.

## Quick example — explicit per-date rate table

```python
from datetime import date

from research.financing import RatePair, TableRateSource

table = {
    (date(2026, 5, 19), "EUR_USD"): RatePair(
        long_annual_bp=-12.0,  # long pays
        short_annual_bp=8.0,   # short receives
    ),
    (date(2026, 5, 20), "EUR_USD"): RatePair(
        long_annual_bp=-12.0,
        short_annual_bp=8.0,
    ),
}
source = TableRateSource(table, name="fixture-2026-05")
```

A `TableRateSource` declares `treatment=ESTIMATED` by default
(hand-built tables are not reconciled real data). Passing
`treatment=MODELED` is refused — that path is reserved for the
future observed-rate model in `src/forex_bot/financing.py`.

## What this module does **not** do

- Run a backtest. The bespoke engine is unchanged.
- Fetch broker data. No OANDA call, no network.
- Modify any campaign verdict. CAMPAIGN_002 remains REJECT.
- Modify `src/forex_bot/financing.py`, the `FinancingTreatment`
  enum, the approval gate, or the observed-event schema.
- Reach `MODELED` financing under any rate source.
- Lift the live-promotion blocker.

For the full classification of required / optional / deferred
features see [`docs/research/FINANCING_MODEL_PROTOCOL.md`](../../docs/research/FINANCING_MODEL_PROTOCOL.md)
§9.

## Tests

```bash
.venv/bin/python -m pytest tests/research/test_financing_*.py -q
ruff check research/financing
```
