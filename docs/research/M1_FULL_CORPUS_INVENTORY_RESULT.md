# M1 Full Corpus Inventory Result

**Status:** PASS
**Generated:** 2026-05-27 (UTC inventory query)

## Summary

All seven major pairs are present in `forex_bot.market_data.candles` with `granularity = 'M1'`. Actual row counts match the sprint expected counts exactly (delta 0). Date coverage is 2021-05-27 through 2026-05-26 UTC for every pair. Duplicates are zero; `data_hash` coverage is 100%; all rows are `complete`.

## Inventory Table

| Pair | Actual | Expected | Δ | First (UTC) | Last (UTC) | Dupes | data_hash |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| EUR_USD | 1,843,476 | 1,843,476 | 0 | 2021-05-27 | 2026-05-26 | 0 | 100% |
| GBP_USD | 1,836,170 | 1,836,170 | 0 | 2021-05-27 | 2026-05-26 | 0 | 100% |
| USD_JPY | 1,844,454 | 1,844,454 | 0 | 2021-05-27 | 2026-05-26 | 0 | 100% |
| AUD_USD | 1,822,196 | 1,822,196 | 0 | 2021-05-27 | 2026-05-26 | 0 | 100% |
| USD_CAD | 1,836,013 | 1,836,013 | 0 | 2021-05-27 | 2026-05-26 | 0 | 100% |
| USD_CHF | 1,786,535 | 1,786,535 | 0 | 2021-05-27 | 2026-05-26 | 0 | 100% |
| NZD_USD | 1,824,352 | 1,824,352 | 0 | 2021-05-27 | 2026-05-26 | 0 | 100% |

**Total M1 rows:** 12,793,196

## Provenance

Each pair has one distinct `fetch_batch_id` (full-corpus ingestion batches). No missing or extra instruments.

## Classification

| Check | Result |
| --- | --- |
| All pairs present | PASS |
| Expected vs actual counts | PASS |
| Date coverage | PASS |
| Duplicate timestamps | PASS |
| Provenance hashes | PASS |

**Overall:** PASS — candidate canonical M1 corpus inventory is consistent with reported ingestion totals.
