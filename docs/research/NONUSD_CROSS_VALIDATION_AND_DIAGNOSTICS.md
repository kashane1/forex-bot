# Non-USD Cross Validation & Diagnostics

**Sprint:** `research-nonusd-cross-ingestion-and-cost-models-001` (Phase 5)
**Status:** infrastructure only — read-only validation/diagnostics. No
strategy, no campaign, no approval.

## Script

`scripts/validate_nonusd_cross_data.py` — emits a single compact JSON
summary (no verbose dumps) and is `strategy_evidence: false`,
`diagnostic_only: true`. It degrades gracefully:

- **No research DB configured** → `db_state: UNAVAILABLE:<reason>`,
  metadata still validated, coverage/diagnostics skipped.
- **Cross has no rows** → `state: NOT_INGESTED`, per-pair quality /
  aggregation / spread / session diagnostics skipped (this is the expected
  state until a credentialed M1 fetch is run).

### Usage

```
python scripts/validate_nonusd_cross_data.py                 # all 8 crosses
python scripts/validate_nonusd_cross_data.py --scope primary # wave-1 four
python scripts/validate_nonusd_cross_data.py --no-diagnostics
python scripts/validate_nonusd_cross_data.py --out report.json
```

## Capabilities

| Capability | Source | Notes |
|------------|--------|-------|
| Instrument-metadata checks | `metadata_check()` | pip_location / display_precision vs JPY-quote convention, no USD leg, bp/day set; no DB needed |
| Row counts + provenance | `cross_ingestion.cross_coverage` | INGESTED/NOT_INGESTED, row_count, last_timestamp |
| Missing-bar analysis | `m1_corpus_validation.quality_for_pair` | missing minutes, duplicate timestamps |
| Spread diagnostics | `quality_for_pair` percentiles + `session_spread_summary` | p50/p90/p99 spread; per-session median/p90 |
| Aggregation consistency | `aggregation_coverage_for_pair` | per-timeframe bar counts + coverage% vs M1 |
| H4 consistency | `h4_drift_for_pair` | derived-vs-native H4 OHLC mismatch count |
| Session diagnostics | `session_spread_summary` + cost-atlas `session_bucket` | asian / london / london_ny_overlap / ny |
| Cost profile | `cost_models.cross_cost_profile` | spread band + two-legged carry, always included |

The diagnostics reuse the **same** corpus validators the majors use
(`quality_for_pair`, `aggregation_coverage_for_pair`, `h4_drift_for_pair`)
and the **same** session buckets as the cost atlas — so crosses are held to
the identical research standard, not a bespoke shortcut.

## Verified behaviour

Run against the live research DB in this sprint:

```
db_state: AVAILABLE
metadata_check: PASS
target_count: 8
ingested_count: 0
not_ingested: [EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY, NZD_JPY, EUR_CHF, GBP_CHF, EUR_AUD]
```

i.e. metadata for all eight crosses validates, and every cross correctly
reports `NOT_INGESTED` (no cross data has been fetched). `tests/unit/
test_validate_nonusd_cross_data.py` (6 tests) covers metadata PASS, the
all-NOT_INGESTED report with cost profiles intact, primary scope, session
bucketing (incl. ignoring incomplete rows), and the ingested-without-
diagnostics path.
