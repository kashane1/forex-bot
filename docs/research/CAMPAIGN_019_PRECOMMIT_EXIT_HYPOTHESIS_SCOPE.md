# CAMPAIGN_019 — Exit Hypothesis Precommit Scope

**Date:** 2026-05-27  
**Branch:** `research-exit-hypothesis-precommit-002`  
**Status:** **PRECOMMIT ONLY — NOT EXECUTED**

> **Precommit / design only** — `strategy_evidence: false`. **CAMPAIGN_019 was not run in this sprint.**

---

## Explicit statement

This document defines the **future** campaign identity and frozen scope. **No backtest
outputs, run folders, config files, or trade artifacts for CAMPAIGN_019 exist as of this
commit.** Execution requires a separate sprint after this precommit is merged.

---

## Proposed campaign identity

| field | value |
|---|---|
| **Campaign ID** | `CAMPAIGN_019` |
| **Strategy family** | `mean_reversion_thesis_invalidation` |
| **Version** | `0.1.0-c019` |
| **Hypothesis label** | `thesis_invalidation_zscore_continuation_exit` |
| **Research status** | research-only (`paper_only = True`) |
| **Diff vs C008** | one exit rule added (thesis invalidation) |
| **Diff vs C018** | invalidation on adverse z-score, not +1R break-even |

---

## Market-structure thesis (exit layer)

On frozen range mean-reversion entries (C008 entry ledger), **41–47%** of hard stops never
reached +1R favorable excursion — trades where the reversion thesis failed to engage or
price continued extending against the position. C018 tested profit-triggered break-even
after +1R and **failed train**. CAMPAIGN_019 tests whether **early exit on z-score
continuation failure** (beyond entry band) improves train expectancy without capping the
time-exit tail or reintroducing fixed targets.

---

## Entry rules — FROZEN (identical to C008)

All rules: completed bars only, prior bars only, no lookahead.

At the latest completed bar `t`:

1. **Range regime gate** — ADX-14 < 20.0.
2. **Over-extension** — z-score of close over 20 bars with RSI confirmation:
   - long iff z ≤ −2.0 AND RSI < 35
   - short iff z ≥ +2.0 AND RSI > 65
3. Direction is **counter** to the extension.

### Frozen entry parameters (unchanged from C008)

| parameter | value |
|---|---|
| `adx_lookback` / `adx_max` | 14 / 20.0 |
| `zscore_lookback` | 20 |
| `zscore_long_threshold` / short | −2.0 / +2.0 |
| `rsi_lookback` | 14 (<35 / >65) |
| `atr_lookback` | 14 |
| `regime_ema` | 200 (warmup only) |
| `risk_per_trade_pct` | 0.25 |
| Session / spread / rollover filters | per C008 config conventions |
| Confluence | tag only — not an entry gate |

**No entry parameter may change in CAMPAIGN_019 execution sprint.**

Source: [`research/deduped_c008_c009_rerun/frozen_config_reconstruction.json`](../../research/deduped_c008_c009_rerun/frozen_config_reconstruction.json) CAMPAIGN_008 block.

---

## Exit rules — SELECTED HYPOTHESIS ONLY

### Baseline elements (unchanged from C008)

| rule | value |
|---|---|
| Initial hard stop | 1.5 × ATR-14 at entry |
| Time stop | 40 H4 bars (`max_bars_in_trade`) |
| Profit target | **none** (`midline_exit: false`) |
| Protective stop | **none** (C018 form closed) |
| Trailing stop | **none** |

### Single pre-registered change (CAMPAIGN_019)

**Thesis invalidation via z-score continuation** — evaluated each completed bar while in trade:

| side | invalidation condition | exit_reason |
|---|---|---|
| long | z-score ≤ **−3.0** | `thesis_invalidation` |
| short | z-score ≥ **+3.0** | `thesis_invalidation` |

- z-score computed over **20 bars** (same as entry).
- Exit at **signal bar close** (same fill timing as C008 deduped forensic).
- Threshold ±3.0 is **structural** (one z-unit beyond ±2.0 entry band) — not tuned from validation.

**Bar processing priority:** thesis_invalidation → hard stop → time stop → EOD.

---

## Pair universe — FROZEN

Same six pairs as C008/C009/C018 deduped forensic replay:

`EUR_USD`, `GBP_USD`, `USD_JPY`, `AUD_USD`, `USD_CAD`, `USD_CHF`

No additions. No removals.

---

## Timeframe and data

| item | value |
|---|---|
| Granularity | H4 |
| Data source | `data/campaign_002.sqlite3` |
| Deduped input | **mandatory** (`keep_last` policy) |
| Splits | train 2020–2022, validation 2023–2024, test 2025–2026 (lockbox) |

---

## Cost model

| item | value |
|---|---|
| Spread | bid/ask from deduped candles |
| Slippage | per C008 campaign config |
| Stress | 2× spread/slippage on validation; full-window stress_15x per gate design |
| Financing in-engine | **unmodeled** (same as C008/C018) |
| Financing overlay | **mandatory** conservative stress before any REVISE interpretation |

---

## Backtrader parity requirement

After execution, run Backtrader exit-parity lane with:

- `pnl_conversion_mode: home_currency_v1`
- `risk_window_mode: engine_aligned`
- Tolerance: **±1 trade** vs bespoke per campaign slice
- Exit shares: **CLOSE_MATCH** or documented divergence

Parity artifacts committed under `research/backtrader_exit_parity/` or campaign-specific folder.

---

## Test lockbox rule

Test window (2025-01-01 → 2026-05-20) opens **only if ALL screening gates pass** on
train + validation. Test FAIL → REJECT even if validation strong.

---

## In scope

- One new strategy variant implementing thesis invalidation exit
- Deduped train + validation backtests
- Gate evaluation vs C008/C009/C018/C011 baselines
- Mechanism diagnostics (thesis_invalidation rate, time-exit MFE)
- Financing overlay report
- Backtrader parity replay
- Compact JSON summaries under `research/campaign_019/`

---

## Out of scope

- Strategy approval; paper/demo/live enablement
- Entry retune; stop/time retune; protective threshold retune
- Midline target; partial exits; trailing stops
- Pair universe expansion; confluence gating
- OANDA order/trade/position mutation
- Test lockbox without screening pass
- CAMPAIGN_019 execution **in this precommit sprint**

---

## Explicit no-execution statement

**CAMPAIGN_019 is NOT executed in `research-exit-hypothesis-precommit-002`.** This document
is pre-registration only. Status: **PRECOMMITTED_NOT_RUN**.
