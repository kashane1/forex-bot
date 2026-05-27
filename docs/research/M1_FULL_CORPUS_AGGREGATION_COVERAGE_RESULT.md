# M1 Full Corpus Aggregation Coverage Result

**Status:** PASS for M5/M15/H1/H4 execution/context timeframes; D1AGG counted after full-span H4 merge.

## Method

Streaming 14-day M1 chunks per pair through `aggregate_m1_candles` with `missing_policy=omit`. D1AGG is built once per pair from deduplicated M1-derived H4 (not per-chunk), matching research convention.

## Representative Coverage (EUR_USD)

| Timeframe | Bars | First (UTC) | Last (UTC) | Avg M1 / bar |
| --- | ---: | --- | --- | ---: |
| M5 | 360,972 | 2021-05-27 | 2026-05-26 | 4.94 |
| M15 | 116,628 | 2021-05-27 | 2026-05-26 | 14.80 |
| H1 | 27,249 | 2021-05-27 | 2026-05-26 | 59.00 |
| H4 | 5,234 | 2021-05-27 | 2026-05-26 | 233.01 |
| D1AGG | see `aggregate_coverage_summary.json` | — | — | — |

All seven pairs produced similar M15 bar counts (~115k–117k) and M5 (~357k–361k), indicating viable lower-timeframe lanes.

## Viability

| Use | Verdict |
| --- | --- |
| M15 default execution | **Viable** — complete bars across span; omitted blocks documented in JSON |
| M5 optional execution | **Viable** — higher bar count, same span |
| H1/H4/D1AGG context | **Viable** — aggregation omits incomplete M1 blocks; aligns with research policy |

## Warnings

- `coverage_pct_vs_m1` in CSV is informational (bar count / weekday-minute model), not a strict data-quality score.
- Incomplete M1 windows (FX close/holidays) increase `omitted_incomplete_blocks`; expected.

**Artifact:** `research/m1_full_corpus_validation/aggregate_coverage_summary.json`
