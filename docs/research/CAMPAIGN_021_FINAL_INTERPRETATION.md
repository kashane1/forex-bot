# CAMPAIGN_021 — Final Interpretation

**Date:** 2026-05-28  
**Verdict:** **REJECT**  
**Branch:** `research-campaign-021-ltf-mtf-confluence-execution-001`

## Summary

CAMPAIGN_021 tested whether M15 MTF confluence entries with H1/H4/D1AGG context improve on CAMPAIGN_020’s H4-only MTF pullback under `next_bar_open`. Train evidence failed the binding train expectancy gate (−0.0174 R on 1,438 trades). Validation, Backtrader parity, and test lockbox were **not** run per gate discipline.

**Post-materialization re-run (2026-05-28):** Train re-executed on materialized M15/H1/H4M1 bars after infra merge. Metrics are **bit-identical** to the pre-materialization train — expected, since materialization verification showed 0 OHLC mismatches. Runtime dropped from multi-hour (M1 re-aggregation) to ~40 min (7 pairs).

## Did M15 improve train stability vs C020?

**Partially on expectancy, not enough to pass.** C020 train was −0.035 R (353 trades); C021 train is −0.0174 R (1,438 trades). Lower-timeframe execution reduced train loss rate per trade but remained negative with ~4× trade count.

## Train-negative / validation-positive pattern?

**Unknown — validation not run.** Deliberately not tested after train failure (same discipline applied to C020 REJECT). Do not infer validation uplift.

## Trade count / turnover

1,438 train trades vs C020’s 353 — M15 pullback/reclaim fires far more often. Turnover and cost footprint are materially higher.

## Pair behavior

Positive train expectancy: GBP_USD (+0.117), USD_JPY (~0), NZD_USD (+0.047).  
Largest drag: EUR_USD (−0.184), USD_CHF (−0.173).

## Stop / hold-time

Precommitted 2× M15 ATR stop, 32-bar time stop. Hold diagnostics in `train_trades_summary.json` (avg hold available from raw trades).

## Backtrader parity

**NOT_RUN** — train gate failed first.

## Test lockbox

**Not opened.**

## Why no approval

Train gate failed. Even a hypothetical validation pass cannot rescue per precommit. `approved_strategies.yaml` stays empty.

## Recommendation

Do not promote `lower_timeframe_mtf_confluence_entry 0.1.0-c021`. Next work should treat this as a **failed hypothesis** unless a **new precommit campaign** proposes a different structural entry family (not a parameter retune of C021).

## No approval

Paper / demo / live blocked. C020 remains REJECT. Prior verdicts unchanged.
