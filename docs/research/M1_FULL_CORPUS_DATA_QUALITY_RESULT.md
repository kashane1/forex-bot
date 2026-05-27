# M1 Full Corpus Data Quality Result

**Overall status:** WARN (acceptable for infrastructure; no repair ingestion required)
**Policy:** Weekday calendar minute model; weekends excluded from missing count. Extreme spread threshold 0.0001 for non-JPY, 0.05 for JPY pairs.

## Pair Summary

| Pair | Status | Rows | Missing* | Dupes | bid>ask | OHLC bad | Extreme spread |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| EUR_USD | PASS | 1,843,476 | 34,283 (1.8%) | 0 | 0 | 0 | 0 |
| GBP_USD | WARN | 1,836,170 | 41,589 (2.2%) | 0 | 0 | 0 | 0 |
| USD_JPY | WARN | 1,844,454 | 33,305 (1.8%) | 0 | 0 | 0 | 0 |
| AUD_USD | WARN | 1,822,196 | 55,563 (3.0%) | 0 | 0 | 0 | 0 |
| USD_CAD | WARN | 1,836,013 | 41,746 (2.2%) | 0 | 0 | 0 | 0 |
| USD_CHF | WARN | 1,786,535 | 91,224 (4.9%) | 0 | 0 | 0 | 0 |
| NZD_USD | WARN | 1,824,352 | 53,407 (2.8%) | 0 | 0 | 0 | 0 |

\*Missing = weekday calendar minutes minus distinct timestamps. Includes daily FX close and holiday windows, not only data defects.

## Spread Sanity

Bid ≤ ask holds for all pairs. Median spreads are plausible (EUR ~1.5 pips, JPY ~1.5–2.0 yen pips after JPY-specific threshold). No negative or zero spreads.

## Largest Gaps

Dominant gap per pair is ~4,326 minutes (~3 days) starting near 2023-12-22 21:57 UTC — consistent with Christmas/holiday market closure, not random corruption.

## Exclusions / Repair

- No pair excluded.
- No repair ingestion recommended: duplicates zero, OHLC/bid-ask clean, holiday gaps expected.

## Classification Rationale

WARN reflects calendar-model missing-minute rate above 2% for six pairs and USD_CHF near 5% (still below 5% FAIL gate). This does not block aggregation or LTF lane scaffold when combined with drift/alignment results.
