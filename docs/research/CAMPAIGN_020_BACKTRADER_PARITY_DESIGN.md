# CAMPAIGN_020 — Backtrader Parity Design

**Date:** 2026-05-27  
**Status:** Design only — no historical parity run in scaffold sprint

## Objective

Before any CAMPAIGN_020 test lockbox open, an independent Backtrader lane must reproduce bespoke signal counts and trade economics within established WARN-band tolerances, using **`next_bar_open`** fills.

## What must match

| layer | bespoke | Backtrader lane |
|---|---|---|
| Candle input | Deduped H4 bid/ask, `keep_last` | Same DB + dedupe policy |
| D1AGG | `aggregate_h4_to_d1` + `htf_align` | Re-implement or import shared `d1agg_htf` only |
| H4 indicators | EMA20/50, RSI(nan), ADX, ATR | Same periods, same completed-bar indexing |
| Entry rules | D1 trend + H4 context + pullback + EMA20 reclaim | Independent copy of precommit §3–5 |
| Fill timing | `next_bar_open` | `next_bar_open` (mandatory) |
| Stop | ATR×2 from signal bar | Same |
| Exit priority | hard stop > time stop (24 bars) | Same ordering |
| Spread/session | RiskEngine filters | Equivalent filters in lane |

## Signal provenance

Parity compare must check:

- `campaign_id == CAMPAIGN_020`
- `htf_feature_times.d1agg_trend <= decision_time`
- `fill_timing` column on trades = `next_bar_open`

## Expected tolerance

Follow CAMPAIGN_011/C015 lane precedent:

- Per-pair trade count within ±2% or documented structural reason
- Aggregate expectancy direction agreement on validation window
- No systematic side bias mismatch

## Blocked conditions

- Any run using `signal_bar_close` for approval-bound comparison
- Incomplete D1AGG bar included in HTF features
- Parity attempted before train/validation gates pass

## Placeholder adapter

Future file: `research/backtrader_lane/strategies/campaign_020_mtf_confluence_pullback.py` (not required for scaffold sprint).

## Scaffold sprint scope

No historical parity execution. Tiny synthetic fixture optional in unit tests only.
