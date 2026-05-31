# CAMPAIGN_020 — MTF Confluence Pullback Precommit

**Date:** 2026-05-27  
**Status:** PRECOMMITTED_NOT_EXECUTED — parameters frozen; no evidence run in scaffold sprint

## Identity

| field | value |
|---|---|
| `campaign_id` | CAMPAIGN_020 |
| `strategy_name` | `multi_timeframe_confluence_pullback` |
| `version` | `0.1.0-c020` |
| `working_name` | MTF Confluence Pullback |

## Universe and timeframe

- **Pairs:** EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF (same seven majors as recent campaigns)
- **Execution timeframe:** H4 (completed bars only)
- **HTF:** D1AGG from H4 via `aggregate_h4_to_d1` + `d1agg_htf` / `htf_align`

## D1AGG feature construction

1. Aggregate completed H4 candles to D1AGG (NY alignment 17, same as campaign configs).
2. Mid OHLC close per D1AGG bar.
3. Wilder-style EMA(20) and EMA(50) on D1AGG closes (computed on full D1 series, then aligned).
4. Align to H4 decision time with `htf_align.align_last_completed` — only `complete=True` D1 rows.

**D1 bullish:** `d1_close > d1_ema50` AND `d1_ema20 > d1_ema50`  
**D1 bearish:** `d1_close < d1_ema50` AND `d1_ema20 < d1_ema50`  
Otherwise: no signal (`HTF trend neutral`).

## H4 context rules

- **Long context:** `h4_close > h4_ema50`
- **Short context:** `h4_close < h4_ema50`
- **ADX gate (optional, simple):** ADX(14) ≥ 18 on completed H4 bars (skip dead markets)

## Pullback trigger rules

Lookback: **6** completed H4 bars before decision bar `t` (exclusive of `t`).

**Long pullback (any one):**

- Minimum low in window ≤ `h4_ema20 + 0.5 × ATR14` (touched/near fast EMA), OR
- RSI(14) with `warmup_policy="nan"` had a value ≤ 40 in the window

**Long trigger (re-acceptance at bar `t`):**

- `h4_close[t] > h4_ema20[t]` AND `h4_close[t-1] <= h4_ema20[t-1]` (reclaim cross)

**Short pullback:** mirror (high ≥ ema20 − 0.5×ATR or RSI ≥ 60 in window)  
**Short trigger:** `close[t] < ema20[t]` AND `close[t-1] >= ema20[t-1]`

No same-bar entry at signal close — engine uses **`next_bar_open`**.

## Side rules

- Long only when D1 bullish + H4 long context + long pullback + long trigger
- Short only when D1 bearish + H4 short context + short pullback + short trigger

## Cost / session filters

- **Spread filter:** enabled in YAML (`max_spread_to_atr_pct: 8.0`, per-pair pip caps) — enforced by `RiskEngine`
- **Session filter:** rollover / Friday / Sunday blocks per standard campaign YAML
- **Strategy-layer:** `min_atr_pips` per pair (empty dict default = no extra floor)

## Stop model

- **Initial stop:** `2.0 × ATR(14)` from H4 OHLC at bar `t` (prior-bar ATR index `-2` for stop distance consistency with other campaigns)
- **No take-profit** in v1 — avoids C009-style midline overfit

## Exit model

**Priority (engine):**

1. Hard stop (adverse same-bar wins tie)
2. Time stop: `max_bars_in_trade = 24` H4 bars (~4 trading days)
3. No trailing stop in v1 (`trailing_stop_atr_multiple: null`)

`exit_model`: `hard_stop_or_time`

## Position sizing

- `risk_per_trade_pct: 0.25`, `max_risk_per_trade_pct: 0.50` — consistent with C008–C019 research configs
- `max_open_positions: 1`, `max_positions_per_instrument: 1`

## Execution realism metadata (YAML `research_metadata`)

```yaml
research_metadata:
  fill_timing: next_bar_open
  execution_realism: conservative
  evidence_use: approval_bound
  promotion_eligible: false
  fill_timing_justification: null
```

## Financing

| field | value |
|---|---|
| `financing_mode` (campaign) | `none` for base backtest |
| `financing_overlay_required` | `true` when hold spans > 1 calendar day |
| `observed_financing_status` | blocked pending practice sample (infrastructure sprint) |

Base metrics are **without** financing; execution sprint must document overlay sensitivity.

## Warmup

- `warmup_bars_required`: **520** H4 bars (D1AGG EMA50 + alignment buffer)
- Fail-closed if HTF align returns `HTF_UNAVAILABLE` / stale

## Frozen parameter set (single set — no sweeps)

| parameter | value | qualitative rationale |
|---|---|---|
| `d1_ema_fast` | 20 | responsive HTF trend |
| `d1_ema_slow` | 50 | standard slow trend filter |
| `h4_ema_context` | 50 | intermediate trend agreement |
| `h4_ema_pullback` | 20 | local pullback rail |
| `pullback_lookback` | 6 | ~1 trading week H4 |
| `pullback_band_atr` | 0.5 | near-EMA touch without tight optimization |
| `rsi_lookback` | 14 | standard |
| `rsi_pullback_long` | 40 | oversold-in-uptrend zone |
| `rsi_pullback_short` | 60 | overbought-in-downtrend zone |
| `adx_lookback` | 14 | standard |
| `adx_min` | 18 | skip very dead markets |
| `atr_lookback` | 14 | standard |
| `atr_stop_multiple` | 2.0 | conservative stop, matches many campaigns |
| `max_bars_in_trade` | 24 | limits carry / turnover |

## Evidence gates (execution sprint only)

| gate | threshold |
|---|---|
| Train expectancy | ≥ 0 R (`next_bar_open`) |
| Validation expectancy | > 0 R |
| Validation profit factor | ≥ 1.05 |
| Validation trades | ≥ 80 aggregate (avoid tiny sample) |
| Validation pair breadth | ≥ 2 pairs with positive expectancy |
| 2× cost stress validation | expectancy ≥ 0 |
| Beat deduped C011 null | validation exp > −0.0029 + 0.010 |
| Backtrader parity | PASS before test lockbox |
| Test lockbox | only if train/validation + parity pass |
| Maximum status | RESEARCH_PASS / PROMOTION_REVIEW_REQUIRED — **not approved** |

## Train / validation / test handling

| split | window (UTC) |
|---|---|
| train | 2020-01-01 → 2022-12-31 |
| validation | 2023-01-01 → 2024-12-31 |
| test | 2025-01-01 → 2026-05-20 (lockbox — not opened in scaffold) |

## Backtrader parity

Required before test lockbox in execution sprint. Design doc: `CAMPAIGN_020_BACKTRADER_PARITY_DESIGN.md`.

## Non-goals

- No approval, paper, demo, live
- No broker mutations
- No tuning after seeing results
- No broad pair search beyond frozen seven

## No-tuning rule

Parameters were chosen from infrastructure defaults and common-sense levels **before** any CAMPAIGN_020 backtest. Any change after evidence requires a **new** campaign id.
