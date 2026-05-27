# CAMPAIGN_018 — Exit Hypothesis Precommit Scope

**Date:** 2026-05-27  
**Branch:** `research-exit-hypothesis-precommit-001`  
**Status:** **PRECOMMIT ONLY — NOT EXECUTED**

> **Precommit / design only** — `strategy_evidence: false`. **CAMPAIGN_018 was not run in this sprint.**

---

## Explicit statement

This document defines the **future** campaign identity and frozen scope. **No backtest outputs, run folders, config files, or trade artifacts for CAMPAIGN_018 exist as of this commit.** Execution requires a separate sprint after this precommit is merged.

---

## Proposed campaign identity

| field | value |
|---|---|
| **Campaign ID** | `CAMPAIGN_018` |
| **Strategy family** | `mean_reversion_protective_stop` |
| **Version** | `0.1.0-c018` |
| **Hypothesis label** | `delayed_reversion_protective_stop_after_1R` |
| **Research status** | research-only (`paper_only = True`) |
| **Diff vs C008** | one exit rule added (see below) |
| **Diff vs C009** | no midline target; protective stop instead |

---

## Market-structure thesis (exit layer)

On frozen range mean-reversion entries (C008 entry ledger), hard stops at −1R dominate train PnL while time exits capture delayed reversion. Trades reaching +1R favorable excursion before stopping represent a testable sub-mechanism: **break-even protection after objective favorable move** may reduce giveback without capping the time-exit tail.

---

## Entry rules — FROZEN (identical to C008)

All rules: completed bars only, prior bars only, no lookahead.

At the latest completed bar `t`:

1. **Range regime gate** — ADX-14 < 20.0. No trade if trending.
2. **Over-extension** — z-score of close over 20 bars beyond threshold with RSI confirmation:
   - long iff z ≤ −2.0 AND RSI < 35
   - short iff z ≥ +2.0 AND RSI > 65
3. Direction is **counter** to the extension.

### Frozen entry parameters (unchanged from C008)

| parameter | value |
|---|---|
| `adx_lookback` / `adx_max` | 14 / 20.0 |
| `zscore_lookback` | 20 |
| `zscore_long_threshold` / short | −2.0 / +2.0 |
| `rsi_lookback` | 14 (Wilder; <35 / >65) |
| `atr_lookback` | 14 |
| `regime_ema` | 200 (warmup only) |
| `risk_per_trade_pct` | 0.25 |
| Session / spread / rollover filters | per C008 config conventions |
| Confluence | **tag only** — not an entry gate unless separately pre-registered |

**No entry parameter may change in CAMPAIGN_018 execution sprint.**

Source of truth: [`research/deduped_c008_c009_rerun/frozen_config_reconstruction.json`](../../research/deduped_c008_c009_rerun/frozen_config_reconstruction.json) CAMPAIGN_008 block.

---

## Exit rules — SELECTED HYPOTHESIS ONLY

### Baseline elements (unchanged from C008)

| rule | value |
|---|---|
| Initial hard stop | 1.5 × ATR-14 at entry |
| Time stop | 40 H4 bars (`max_bars_in_trade`) |
| Profit target | **none** (`midline_exit: false`) |
| Trailing stop (continuous) | **none** |

### Single pre-registered change (CAMPAIGN_018)

**Protective stop after +1R favorable excursion:**

1. Define **R** at entry as the price distance from entry to the initial hard stop (same R used throughout the repo for expectancy).
2. On each completed bar while in trade, compute **MFE in R** from entry using favorable price extreme (high for long, low for short) **including spread-adjusted exit economics consistent with engine conventions**.
3. When MFE **first reaches ≥ +1.0R**, replace the active stop with a **break-even stop at entry price** (exact fill price at entry, no offset).
4. After transition, the trade exits on: break-even stop, original time stop at 40 bars, or end-of-data — **whichever occurs first**.
5. The protective stop **does not ratchet** beyond break-even in v0.1.0-c018 (no trailing).

**Forbidden in v0.1.0-c018:**

- Midline / band target (C009 path)
- Partial take-profit
- ATR trail after transition
- Stop distance change from 1.5× ATR
- Time-stop length change from 40 bars
- Threshold sweep (0.8R, 1.2R, etc.)

---

## Pair universe

EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF (6 pairs; NZD_USD excluded — same as C008).

---

## Timeframe

H4 (OANDA practice alignment).

---

## Data source

| item | requirement |
|---|---|
| Database | `./data/campaign_002.sqlite3` |
| Source tag | `oanda-practice` |
| Dedupe | **mandatory** — `keep_last` on `(instrument, granularity, utc_time)` via deduped candle load path |
| Preflight | duplicate-row report required before first run |

---

## Cost model

| regime | spread multiplier | slippage (pips) |
|---|---:|---:|
| base | 0.5 | 0.2 |
| stress_15x | 1.5 | 0.3 |
| stress_2x | 2.0 | 0.5 |

Same regimes as C008 forensic replay.

---

## Splits

| split | from | to | authorized in execution |
|---|---|---|---|
| train | 2020-01-01 | 2022-12-31 | yes |
| validation | 2023-01-01 | 2024-12-31 | yes |
| test (lockbox) | 2025-01-01 | 2026-05-20 | **only if screening gate passes** |
| full (cost stress) | 2020-01-01 | 2026-05-20 | stress diagnostics only until lockbox opens |

---

## Diagnostics (explanatory — not gates unless pre-registered)

| diagnostic | role |
|---|---|
| Cost atlas | spread/ATR hostile cells — explanatory |
| FRED normalized features | regime tagging — **explanatory only** in v0.1.0-c018 |
| Confluence grade | tag only |
| MAE/MFE post-run | required descriptive output |
| Exit reason + `stop_transition` event | required |

FRED/confluence **must not** be used to filter entries or exits in v0.1.0-c018 unless a future precommit explicitly adds them as gates.

---

## Test lockbox rule

2025–2026 test window remains **closed** until **all screening gates** pass on deduped train + validation (+ declared stress). This precommit does not open the lockbox.

---

## In scope (future execution sprint)

- Implement `mean_reversion_protective_stop 0.1.0-c018` with frozen entries + one exit change
- Deduped backtest on train / validation
- Gate evaluation vs precommit
- Comparison vs C008/C009 deduped forensic baselines and C011 deduped null
- MAE/MFE and exit anatomy refresh
- Financing overlay (conservative) — **required before interpreting multi-day holds**

---

## Out of scope

- Strategy approval or registry update
- Paper/demo/live enablement
- Entry retuning, pair removal, session cherry-pick
- Parameter sweeps on +1R threshold or stop multiple
- C008/C009 artifact modification
- Backtrader parity campaign (separate infra sprint if needed)
- Broad strategy search reactivation

---

## Comparison baselines (descriptive, not tuning inputs)

| baseline | artifact |
|---|---|
| C008 deduped forensic | `research/deduped_c008_c009_rerun/metrics_summary.json` |
| C009 deduped forensic | same |
| C011 deduped null | `research/null_baselines/campaign_011_deduped_null_baseline.json` |

---

## Verdict ceiling

Even if all gates pass: **REVISE maximum** (research-only). Mean-reversion tail risk requires human review before any promotion sprint.
