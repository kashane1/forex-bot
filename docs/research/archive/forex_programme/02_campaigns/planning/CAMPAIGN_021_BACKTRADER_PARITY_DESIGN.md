# CAMPAIGN_021 — Backtrader Parity Design

**Date:** 2026-05-27  
**Status:** DESIGN ONLY — no historical parity run in scaffold sprint

## Scope

Independent Backtrader reproduction of `lower_timeframe_mtf_confluence_entry 0.1.0-c021` before any test lockbox open in a future execution sprint.

## Data feeds

| feed | provenance | notes |
|---|---|---|
| M15 execution | M1-derived aggregation | same bar timestamps as research engine |
| H1 / H4 context | M1-derived | joined with last-completed policy |
| D1AGG | native H4→D1AGG | **not** M1-derived D1AGG |

Parity preflight must fail if D1AGG source is `m1_derived_d1agg`.

## Signal timing

- Decision on completed M15 bar close
- Fill at **next M15 bar open** (`next_bar_open`)
- Conservative spread/slippage from campaign YAML

## Risk / exit parity

- Entry stop distance: **2.0 × M15 ATR(14)** from prior bar
- Time stop: **32** M15 bars from entry bar
- No take-profit, no trailing
- Exit priority: stop → time → session/EOD filters

## Provenance fields to compare

- `campaign_id`, `decision_time`, `source_candle_timestamp`
- `htf_feature_times` (d1agg, h4, h1) each ≤ `decision_time`
- `features.data_provenance` / `d1agg_source`

## Tolerance (draft)

- Signal timestamps: exact match on bar open UTC
- Stop price: within 1 pip after instrument rounding
- Side: exact match
- Allow documented skips when spread/session filter blocks in both engines

## Divergence classes

| class | action |
|---|---|
| HTF align mismatch | BLOCK parity — fix alignment |
| D1AGG source mismatch | BLOCK — provenance error |
| Fill timing drift | BLOCK — policy violation |
| Rounding / pip size | document tolerance |
| Warmup length | align `warmup_bars_required()` = 120 |

## Blocked conditions

- M1-derived D1AGG in either engine
- `signal_bar_close` fill timing
- Incomplete HTF bar used in decision
- Test lockbox requested before parity PASS

## Fixture plan (future)

- Tiny synthetic M15 + H1/H4/D1AGG frames (10–20 bars) with known bullish reclaim
- One long + one short expected signal JSON golden file
- No full-corpus Backtrader run in scaffold sprint

## No approval

Parity design does not approve CAMPAIGN_021 or open lockbox.
