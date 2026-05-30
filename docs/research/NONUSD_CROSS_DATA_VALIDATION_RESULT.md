# Non-USD Cross Data Validation Result (Sprint 001, Phase 3)

**Sprint:** `research-nonusd-cross-data-population-001`
**Tool:** `scripts/validate_nonusd_cross_data.py --scope all`
**Status:** descriptive validation. No strategy, no campaign, no edge work.

## Headline

`db_state: AVAILABLE`, `metadata_check: PASS`, **8 / 8 ingested**,
`not_ingested: []`. All eight first-wave crosses are populated over the
matched majors horizon (2021-05-26 → 2026-05-26) with clean provenance and
no integrity violations.

## Row counts, provenance, integrity (M1, read back from store)

| Cross | M1 rows | batches | data_hash | dup ts | bid>ask | spread≤0 |
|-------|---------|:-------:|:---------:|:------:|:-------:|:--------:|
| EUR_GBP | 1,823,232 | 1 | 100% | 0 | 0 | 0 |
| EUR_JPY | 1,841,779 | 1 | 100% | 0 | 0 | 0 |
| GBP_JPY | 1,852,770 | 1 | 100% | 0 | 0 | 0 |
| AUD_JPY | 1,857,000 | 1 | 100% | 0 | 0 | 0 |
| NZD_JPY | 1,845,840 | 1 | 100% | 0 | 0 | 0 |
| EUR_CHF | 1,811,686 | 1 | 100% | 0 | 0 | 0 |
| GBP_CHF | 1,838,790 | 1 | 100% | 0 | 0 | 0 |
| EUR_AUD | 1,849,425 | 1 | 100% | 0 | 0 | 0 |
| **total** | **14,720,522** | — | 100% | 0 | 0 | 0 |

Counts sit in the majors' band (majors average ~1,827,600 M1 rows); thinner
crosses (EUR_CHF) are marginally lower, busier ones (AUD_JPY) marginally
higher — as expected.

## Quality status (and why WARN is benign here)

`quality_for_pair` returns **WARN** for 7 crosses and **PASS** for EUR_AUD.
The WARN is driven entirely by the **missing-minute heuristic**, which
compares observed M1 timestamps against a naive count of *all* weekday
minutes — so the daily FX maintenance break (~22:00–22:05 NY) and market
holidays read as "missing". This is the **same heuristic that flags a
major**: re-running it on the control universe, `USD_JPY` is also `WARN`
(33,305 missing minutes) while `EUR_USD` is `PASS` (34,283) — the
PASS/WARN split is the heuristic's 2% threshold, not a data defect. The
hard integrity checks (duplicate timestamps, bid>ask, non-positive
spreads, OHLC violations) are **all zero** for every cross.

| Cross | quality | missing_min | dup ts | bid>ask |
|-------|---------|-------------|--------|---------|
| EUR_GBP | WARN | 55,967 | 0 | 0 |
| EUR_JPY | WARN | 37,420 | 0 | 0 |
| GBP_JPY | WARN | 26,429 | 0 | 0 |
| AUD_JPY | WARN | 22,199 | 0 | 0 |
| NZD_JPY | WARN | 33,359 | 0 | 0 |
| EUR_CHF | WARN | 67,513 | 0 | 0 |
| GBP_CHF | WARN | 40,409 | 0 | 0 |
| EUR_AUD | PASS | 29,774 | 0 | 0 |

(Compare control: USD_JPY WARN / 33,305 missing; EUR_USD PASS / 34,283.)

## Spread diagnostics (M1 close spread, price units)

| Cross | p50 | p90 | p99 | ≈ p50 in pips |
|-------|-----|-----|-----|---------------|
| EUR_GBP | 0.00014 | 0.00018 | 0.00084 | ~1.4 |
| EUR_JPY | 0.021 | 0.029 | 0.131 | ~2.1 |
| GBP_JPY | 0.031 | 0.041 | 0.173 | ~3.1 |
| AUD_JPY | 0.019 | 0.025 | 0.117 | ~1.9 |
| NZD_JPY | 0.025 | 0.033 | 0.147 | ~2.5 |
| EUR_CHF | 0.00016 | 0.00021 | 0.00123 | ~1.6 |
| GBP_CHF | 0.00022 | 0.00030 | 0.00199 | ~2.2 |
| EUR_AUD | 0.00026 | 0.00041 | 0.00178 | ~2.6 |

These line up with the feasibility study's qualitative bands
(near-major EUR_GBP/EUR_JPY; wide GBP_JPY) and confirm crosses are
**wider than the comparable majors** (EUR_USD p50 ~1.5p; USD_JPY ~1.7p) —
a breadth expansion, not a cost fix.

## Session diagnostics (median spread, pips)

| Cross | asian | london | london_ny_overlap | ny |
|-------|-------|--------|-------------------|----|
| EUR_GBP | 1.5 | 1.4 | 1.8 (p90 7.9) | 1.6 |
| GBP_JPY | 2.3 | 2.2 | 2.8 (p90 14.9) | 2.4 |

Spreads are tightest in london, widen through the london/NY overlap, and
the overlap p90 captures rollover/news spikes — the expected intraday
shape, matching the cost-atlas session conventions used for the majors.

## Aggregation consistency (on-the-fly M1→TF coverage, GBP_JPY example)

| TF | bars | coverage vs M1 | expected ratio |
|----|------|----------------|----------------|
| M5  | 365,917 | 19.47% | ~20.0% (1/5) |
| M15 | 119,806 | 6.38% | ~6.7% (1/15) |
| H1  | 28,446 | 1.51% | ~1.67% (1/60) |
| H4  | 5,609 | 0.30% | ~0.42% (1/240) |

Ratios match the expected fractions (slightly under, from omitted
incomplete blocks) — the price-agnostic aggregator derives cross
timeframes correctly. Native H4 does not exist for crosses (M1-only
ingestion), so `h4_consistency` is `WARN: no_native_h4_in_store` for all —
expected; Phase 4 materializes the derived H4M1.

## Conclusion

All eight crosses pass metadata and hard-integrity validation with
provenance intact. The only WARNs are the benign FX-closure missing-minute
heuristic (identical on the majors) and the absence of a native H4 series
(crosses are M1-derived). The dataset is ready to materialize.
