# OANDA H4 Data Quality Audit — `oanda-practice-readonly-001` Phase 5

**Generated:** 2026-05-22T20:34:48.553813+00:00 · **Branch:** `oanda-practice-readonly-001`
**Store:** `data/oanda_h4_research.sqlite3` · **Overall:** **PASS**

> Read-only audit of the local H4 research store. **No OANDA call, no credentials.** Diagnostic only — `strategy_evidence: false`; approves no strategy and produces no trading verdict.

## Summary

| instrument | candles | incomplete | dups | weekend | holiday | outage | suspicious | median spr | p95 spr | abnormal | acceptable |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EUR_USD | 9931 | 0 | 0 | 333 | 4 | 0 | 0 | 1.50 | 2.50 | 107 | yes |
| GBP_USD | 9931 | 0 | 0 | 333 | 4 | 0 | 0 | 1.90 | 6.00 | 174 | yes |
| USD_JPY | 9932 | 0 | 0 | 333 | 4 | 0 | 0 | 1.60 | 4.10 | 304 | yes |
| AUD_USD | 9931 | 0 | 0 | 333 | 4 | 0 | 0 | 1.40 | 2.90 | 184 | yes |
| USD_CAD | 9931 | 0 | 0 | 333 | 4 | 0 | 0 | 1.90 | 4.50 | 141 | yes |
| USD_CHF | 9931 | 0 | 0 | 333 | 4 | 0 | 0 | 1.70 | 4.10 | 165 | yes |

## Gap & anomaly classification

Every gap and spread anomaly is sorted into one of five categories — the first two are expected market behaviour, the last three warrant a look:

1. **Expected weekend gaps** — the Friday-close → Sunday-open closure (a gap spanning Saturday, ≥ 24h). Normal; not a defect.
2. **Expected holiday closures** — gaps overlapping the Dec 24 – Jan 2 thin-liquidity window. Normal for FX.
3. **Broker / data outage-like gaps** — a multi-bar (> 2 H4 bars) non-weekend, non-holiday gap. Concerning — review.
4. **Suspicious short missing bars** — a 1-2 bar non-weekend, non-holiday gap. Usually thin mid-week liquidity; noted.
5. **Spread spikes / rollover events** — abnormal spreads (> 5× median close spread). FX spreads widen at the daily rollover, the Sunday open, and around news; the per-pair breakdown buckets them by whether they fall on the H4 bar that closes at the 17:00 NY rollover (start hour [17, 18] UTC). These are expected microstructure, not data corruption.

## EUR_USD

- First / last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-19 21:00:00+00:00`
- Candle count: **9931** (complete 9931, incomplete 0)
- Duplicate timestamps: **0**
- Bid / ask availability: **9931 / 9931** of 9931
- Missing intervals (non-weekend, raw): **4**
- Gap classification:
    - expected weekend gaps: **333**
    - expected holiday closures: **4**
    - broker/data outage-like gaps: **0**
    - suspicious short missing bars: **0**
- Median spread: **1.50** pips · p95 spread: **2.50** pips
- Abnormal spreads (> 5× median): **107** (106 on the rollover-close H4 bar, 1 elsewhere)
- **Acceptable for diagnostics / parity:** acceptable for diagnostics / parity

## GBP_USD

- First / last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-19 21:00:00+00:00`
- Candle count: **9931** (complete 9931, incomplete 0)
- Duplicate timestamps: **0**
- Bid / ask availability: **9931 / 9931** of 9931
- Missing intervals (non-weekend, raw): **4**
- Gap classification:
    - expected weekend gaps: **333**
    - expected holiday closures: **4**
    - broker/data outage-like gaps: **0**
    - suspicious short missing bars: **0**
- Median spread: **1.90** pips · p95 spread: **6.00** pips
- Abnormal spreads (> 5× median): **174** (165 on the rollover-close H4 bar, 9 elsewhere)
- **Acceptable for diagnostics / parity:** acceptable for diagnostics / parity

## USD_JPY

- First / last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-19 21:00:00+00:00`
- Candle count: **9932** (complete 9932, incomplete 0)
- Duplicate timestamps: **0**
- Bid / ask availability: **9932 / 9932** of 9932
- Missing intervals (non-weekend, raw): **4**
- Gap classification:
    - expected weekend gaps: **333**
    - expected holiday closures: **4**
    - broker/data outage-like gaps: **0**
    - suspicious short missing bars: **0**
- Median spread: **1.60** pips · p95 spread: **4.10** pips
- Abnormal spreads (> 5× median): **304** (298 on the rollover-close H4 bar, 6 elsewhere)
- **Acceptable for diagnostics / parity:** acceptable for diagnostics / parity

## AUD_USD

- First / last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-19 21:00:00+00:00`
- Candle count: **9931** (complete 9931, incomplete 0)
- Duplicate timestamps: **0**
- Bid / ask availability: **9931 / 9931** of 9931
- Missing intervals (non-weekend, raw): **4**
- Gap classification:
    - expected weekend gaps: **333**
    - expected holiday closures: **4**
    - broker/data outage-like gaps: **0**
    - suspicious short missing bars: **0**
- Median spread: **1.40** pips · p95 spread: **2.90** pips
- Abnormal spreads (> 5× median): **184** (182 on the rollover-close H4 bar, 2 elsewhere)
- **Acceptable for diagnostics / parity:** acceptable for diagnostics / parity

## USD_CAD

- First / last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-19 21:00:00+00:00`
- Candle count: **9931** (complete 9931, incomplete 0)
- Duplicate timestamps: **0**
- Bid / ask availability: **9931 / 9931** of 9931
- Missing intervals (non-weekend, raw): **4**
- Gap classification:
    - expected weekend gaps: **333**
    - expected holiday closures: **4**
    - broker/data outage-like gaps: **0**
    - suspicious short missing bars: **0**
- Median spread: **1.90** pips · p95 spread: **4.50** pips
- Abnormal spreads (> 5× median): **141** (136 on the rollover-close H4 bar, 5 elsewhere)
- **Acceptable for diagnostics / parity:** acceptable for diagnostics / parity

## USD_CHF

- First / last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-19 21:00:00+00:00`
- Candle count: **9931** (complete 9931, incomplete 0)
- Duplicate timestamps: **0**
- Bid / ask availability: **9931 / 9931** of 9931
- Missing intervals (non-weekend, raw): **4**
- Gap classification:
    - expected weekend gaps: **333**
    - expected holiday closures: **4**
    - broker/data outage-like gaps: **0**
    - suspicious short missing bars: **0**
- Median spread: **1.70** pips · p95 spread: **4.10** pips
- Abnormal spreads (> 5× median): **165** (155 on the rollover-close H4 bar, 10 elsewhere)
- **Acceptable for diagnostics / parity:** acceptable for diagnostics / parity

## Verdict

- All 6 pairs are structurally acceptable for diagnostics / parity: completed candles only, full bid/ask coverage, no duplicate timestamps, and a full ~6-year H4 history.
- 0 concerning gap(s) (outage-like + suspicious-short) across all pairs are classified above. For a **diagnostic**, classified gaps are handled by D1 aggregation and do not block the run; they would warrant scrutiny before any strategy verdict (which this sprint does not produce).
- Weekend and year-end-holiday gaps are expected market closures and are not defects.

## Safety statement

- Read-only audit of the local store; no OANDA call, no credentials read or written.
- Diagnostic only — `strategy_evidence: false`. Approves no strategy and produces no trading recommendation.
