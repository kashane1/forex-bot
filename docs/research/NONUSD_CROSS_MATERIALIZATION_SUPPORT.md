# Non-USD Cross Materialization Support

**Sprint:** `research-nonusd-cross-ingestion-and-cost-models-001` (Phase 3)
**Status:** infrastructure only — no strategy, no campaign, no approval.

## What was added

The M1→derived-timeframe materialization pipeline now accepts registered
non-USD crosses. The pipeline is **price-agnostic** — the M1→M5/M15/H1/H4
aggregation is pure OHLCV math on `Decimal` prices with a 5pm-NY H4 anchor
that is currency-blind — so crosses (including JPY-quote, 0.01-pip pairs)
flow through the *same* code path the majors use, with no parallel logic.

### Changes (additive)

- `m1_timeframe_materialization.materialize_pair` instrument gate widened
  from `MAJOR_PAIRS` to `SUPPORTED_PAIRS` (= majors ∪ registered crosses).
  Unknown instruments are still rejected.
- `scripts/materialize_m1_derived_timeframes.py`:
  - `--pair` now accepts any supported pair (major or registered cross).
  - new `--all-crosses` materializes every registered cross.
  - `--all-majors` unchanged (control universe).

### Materialization targets (unchanged, per cross)

| Logical | Storage granularity | Notes |
|---------|--------------------|-------|
| M5  | `M5`  | fixed 5-min UTC buckets |
| M15 | `M15` | fixed 15-min UTC buckets |
| H1  | `H1`  | fixed 60-min UTC buckets |
| H4  | `H4M1`| 4-hour buckets anchored to 5pm New York; stored as `H4M1` to distinguish M1-derived from native broker H4 |

Diagnostic `M3`/`M30` remain opt-in via `--targets` for crosses too. The
`aggregation_config_hash()` provenance fingerprint is **unchanged** — the
shared M1-derivation ruleset is identical for crosses, so already-
materialized major bars keep their provenance.

## Correctness, alignment, provenance

`tests/unit/test_cross_materialization.py` verifies:

- **Aggregation correctness** — five M1 GBP_JPY bars at ~190 (0.01-pip
  scale) aggregate to one M5 bar with open=first, high=max, low=min,
  close=last, volume=sum, all exact `Decimal` values (no precision loss on
  JPY-scale prices).
- **Timestamp alignment** — the M5 bucket aligns to the first M1 minute.
- **Provenance retention** — `candle_to_record` for a cross retains
  `fetch_batch_id` and maps logical H4 to the `H4M1` storage granularity;
  JPY-scale prices survive the `Decimal→float` store conversion unchanged.
- **Gate** — `materialize_pair` accepts a registered cross (empty window →
  zero rows, no rejection) and rejects an unknown instrument
  (`XAU_USD` → "supported universe" error).

## What is NOT done here

No cross M1 data is ingested yet, so no cross bars are actually
materialized into the store in this sprint. This phase adds the
*capability*; a credentialed M1 fetch (later, explicitly scoped) is the
prerequisite for a real materialization run, after which
`verify_materialized_pair` will check live-vs-stored parity for crosses
exactly as it does for majors.
