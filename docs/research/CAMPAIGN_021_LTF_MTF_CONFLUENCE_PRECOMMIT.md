# CAMPAIGN_021 — LTF MTF Confluence Entry Precommit

**Date:** 2026-05-27  
**Status:** PRECOMMITTED_NOT_EXECUTED — parameters frozen; scaffold sprint only

## Identity

| field | value |
|---|---|
| `campaign_id` | CAMPAIGN_021 |
| `strategy_name` | `lower_timeframe_mtf_confluence_entry` |
| `version` | `0.1.0-c021` |
| `working_name` | LTF MTF Confluence Entry |
| `promotion_eligible` | false |

## Universe and timeframes

- **Pairs:** EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD (seven majors)
- **Execution:** M15 (completed bars only)
- **Context:** H1, H4, D1AGG (all joined with `htf_align.align_last_completed` / LTF lane policy)
- **Future optional:** M5 execution — not in v1 evidence plan

## Data provenance (hybrid — mandatory)

| layer | source | notes |
|---|---|---|
| M15 execution | `m1_derived` | aggregated from Postgres M1 corpus |
| H1 context | `m1_derived` | same |
| H4 context | `m1_derived` | same |
| D1AGG context | `native_h4_derived_d1agg` | H4 in store → `aggregate_h4_to_d1` |
| M1-derived D1AGG | **forbidden** | `m1_derived_d1agg_allowed: false` |

Config block: `configs/campaign_021_ltf_mtf_confluence.yaml` → `data_provenance`.

## D1AGG structure (native H4-derived)

- Mid close per D1AGG bar; EMA20 and EMA50 on D1AGG closes (full series, then aligned).
- **Bullish:** `close > ema50` AND `ema20 > ema50`
- **Bearish:** `close < ema50` AND `ema20 < ema50`
- Else: no signal

## H4 context

- **Bullish:** `h4_close > h4_ema50`
- **Bearish:** `h4_close < h4_ema50`

## H1 tactical trend

- **Bullish:** `h1_close > h1_ema20` AND EMA20 slope ≥ 0 over **3** completed H1 bars
- **Bearish:** `h1_close < h1_ema20` AND EMA20 slope ≤ 0 over **3** completed H1 bars

## M15 entry trigger

Lookback: **8** completed M15 bars before decision bar (exclusive of decision).

**Long (all required):**

- D1AGG bullish, H4 bullish, H1 bullish
- In lookback window: `low` touched `ema20` or `ema50`
- Reclaim: `close[t] > ema20[t]` AND `close[t-1] <= ema20[t-1]`

**Short:** mirror on highs / bearish stack.

**ADX gate:** ADX(14) ≥ **18** on M15 (warmup-safe; skip if NaN).

## Side rules

- Long only on full bullish stack + M15 pullback + reclaim
- Short only on full bearish stack + M15 pullback + reclaim

## Cost / session

- Spread filter: enabled (`max_spread_to_atr_pct: 8.0`, per-pair caps)
- Session filter: rollover / Friday / Sunday blocks per campaign YAML
- Strategy `min_atr_pips`: empty default (optional per-pair floor)

## Stop / exit

| rule | value |
|---|---|
| initial stop | **2.0 × M15 ATR(14)** (prior-bar ATR at index −2) |
| time stop | **32** M15 bars (~8 hours) |
| take-profit | none |
| trailing | none |
| exit_model | `hard_stop_or_time` |
| exit priority | stop → time → session/EOD (engine) |

## Position sizing

- `risk_per_trade_pct: 0.25`, `max_risk_per_trade_pct: 0.50`
- `max_open_positions: 1`, `max_positions_per_instrument: 1`

## Execution realism metadata

```yaml
research_metadata:
  fill_timing: next_bar_open
  execution_realism: conservative
  evidence_use: approval_bound
  promotion_eligible: false
```

## Financing

| field | value |
|---|---|
| `financing_mode` | `none` (scaffold) |
| `financing_overlay_required` | true if future avg hold > 1 day |

## Warmup / alignment

- Strict indicator warmup (`nan` until ready)
- No signal if any HTF align returns `HTF_UNAVAILABLE` or blocked reason
- Incomplete H1/H4/D1AGG must not affect M15 decision

## Future execution gates (not run in scaffold)

- Train expectancy ≥ 0 (`next_bar_open`)
- Validation expectancy > 0; PF ≥ 1.05; trades ≥ 150 (or documented lower)
- ≥ 4/7 validation pairs positive (or majority if fewer pairs)
- 2× cost stress validation expectancy ≥ 0
- Beat C011 deduped null by +0.010R
- Financing overlay if avg hold > 1 day
- Backtrader parity **before** test lockbox
- Test lockbox only if train/val + parity pass
- Max status: RESEARCH_PASS / PROMOTION_REVIEW_REQUIRED — **not approval**

## No tuning rule

One frozen parameter set in YAML. No sweeps. No parameter choice from historical results in this or future execution without a new precommit campaign.

## No approval

`configs/approved_strategies.yaml` remains `approved: []`. Paper/demo/live blocked.
