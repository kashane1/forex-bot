# Non-USD Cross Materialization Result (Sprint 001, Phase 4)

**Sprint:** `research-nonusd-cross-data-population-001`
**Tool:** `scripts/materialize_m1_derived_timeframes.py --all-crosses`
(materialize) then `--all-crosses --verify-only` (independent parity).
**Status:** descriptive. No strategy, no campaign, no edge work.

## What was materialized

For all eight ingested crosses, the M1 corpus was aggregated to the
canonical recurring set **M5 / M15 / H1 / H4** (H4-from-M1 stored under the
`H4M1` storage granularity), source label `m1_materialized`,
`aggregation_config_hash = f9b7246b79a0635c` — **identical to the majors'**,
so cross bars share the majors' aggregation provenance. Diagnostic M3/M30
were deliberately **not** materialized (out of scope). Window:
2021-05-25 → 2026-05-26 (matches M1).

## Bar counts (stored)

| Cross | M5 | M15 | H1 | H4M1 |
|-------|----|-----|----|------|
| EUR_GBP | 346,991 | 107,953 | 23,598 | 4,045 |
| EUR_JPY | 360,104 | 116,586 | 27,403 | 5,289 |
| GBP_JPY | 365,917 | 119,806 | 28,446 | 5,609 |
| AUD_JPY | 367,668 | 120,433 | 28,770 | 5,757 |
| NZD_JPY | 362,924 | 117,075 | 26,431 | 4,867 |
| EUR_CHF | 343,763 | 107,931 | 24,120 | 4,249 |
| GBP_CHF | 360,538 | 116,985 | 27,209 | 5,180 |
| EUR_AUD | 363,783 | 118,250 | 27,797 | 5,407 |
| **total** | **2,871,688** | **925,019** | **213,774** | **40,403** |

Counts sit in the majors' range (e.g. major EUR_USD: M5 360,972 / M15
116,628 / H1 27,249 / H4M1 5,234). Combined with M1, the eight crosses add
**~18.77M rows** to the research store.

## Parity verification (independent re-derivation vs stored)

`--verify-only` re-aggregates each timeframe from M1 on the fly and
compares to the stored bars. **Overall status: PASS (8/8 pairs, all 4
timeframes).** Every cell:

- `expected_count == stored_count` (no missing, no extra bars)
- `missing_in_store = 0`, `extra_in_store = 0`
- `ohlc_mismatches = 0`

Total across 8 crosses × 4 timeframes: **0 mismatches, 0 missing, 0 extra.**

### Aggregation correctness, timestamp alignment, provenance

- **Aggregation correctness:** zero OHLC mismatches between stored bars and
  freshly re-derived bars confirms the price-agnostic aggregator produces
  bit-stable bars for crosses (including JPY-quote 0.01-pip pairs).
- **Timestamp alignment:** stored timeframes span the same 2021-05-25 →
  2026-05-26 window as M1; H4M1 uses the 5pm-NY anchor (currency-blind),
  shared with the majors.
- **Provenance:** 100% of materialized rows carry a `fetch_batch_id`;
  source label `m1_materialized`; config hash `f9b7246b79a0635c` matches the
  control universe, so the cross bars are provenance-consistent with the
  majors.

## Note on the materialization run

The first `--all-crosses` materialize run was interrupted (environment
kill) during/after its built-in verification pass, but the bar **writes had
completed for all eight crosses**. A subsequent independent
`--verify-only --all-crosses` run (re-deriving from M1) returned PASS for
every pair and timeframe, confirming the stored bars are correct and
complete — i.e. the result does not depend on the interrupted run's own
verification. The shared majors' materialization manifests were left
untouched (a compact cross-only snapshot is saved under
`research/nonusd_cross_population/`).

## Conclusion

All eight crosses are materialized to M5/M15/H1/H4M1 with exact
re-derivation parity, correct timestamp alignment, and provenance
consistent with the majors. The multi-timeframe cross dataset is ready for
descriptive cost profiling (Phase 5).
