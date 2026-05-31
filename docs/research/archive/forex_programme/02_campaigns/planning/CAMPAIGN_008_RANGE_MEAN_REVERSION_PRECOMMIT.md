# CAMPAIGN_008 — Range Mean-Reversion (RESEARCH-ONLY) — Pre-Commit

Written and committed **before** the campaign runs. Research Marathon
001, Phase 4.

## RESEARCH-ONLY status

Mean reversion has fat-tailed loss risk: a range that breaks into a
trend turns a reversion trade into a large loss. **CAMPAIGN_008 cannot
be promoted beyond REVISE without explicit human review**, even if it
clears every numeric gate. The strategy is `paper_only = True` and the
marathon report builder is run with `--research-only`, which caps the
verdict at REVISE.

## Hypothesis

CAMPAIGN_005 found the H4 majors are choppy (efficiency ratio 0.24,
return autocorrelation ≈ 0) — the conditions that *broke* the trend and
breakout campaigns. The symmetric question: in the **low-trend
(range-bound) sub-regime**, does a strictly regime-filtered
mean-reversion entry have a positive cost-adjusted edge? If the majors
spent much of 2020-2024 ranging, buying oversold dips / selling
overbought rips *while no trend is present* is the natural counterpart
hypothesis.

## Strategy — `mean_reversion 0.1.0-c008`

All rules: completed bars only, prior bars only, no lookahead.

At the latest completed bar `t`:

1. **Range regime gate** — ADX-14 < `adx_max`. If a trend is present,
   **no trade** (this is the single most important guard — it is what
   keeps a reversion entry out of the trend that would blow it up).
2. **Over-extension** — z-score of close over `zscore_lookback` bars
   beyond the threshold, with an RSI confirmation:
   - long iff z ≤ `zscore_long_threshold` AND RSI < 35
   - short iff z ≥ `zscore_short_threshold` AND RSI > 65
3. Direction is **counter** to the extension (reversion toward the mean).

**Mandatory hard stop** = `atr_stop_multiple × ATR-14`. Exit is the hard
stop or the `max_bars_in_trade` time stop (the reversion horizon).

**Explicitly forbidden** (and structurally impossible here): averaging
down, grids, martingale, adding to a loser. The strategy emits a single
`Signal`; the RiskEngine enforces one position per instrument; there is
no position-scaling code path.

## Parameters (frozen)

| parameter | value | rationale |
|---|---|---|
| `adx_lookback` / `adx_max` | 14 / 20.0 | ADX < 20 is the textbook "no trend" threshold — the range-regime gate. Pre-committed, not swept. |
| `zscore_lookback` | 20 | ≈ 3 trading days on H4 — the mean a reversion targets. |
| `zscore_long_threshold` / short | −2.0 / +2.0 | Standard 2-sigma over-extension. |
| `rsi_lookback` | 14 | Standard Wilder RSI; <35 / >65 confirmation. |
| `atr_lookback` | 14 | Standard ATR. |
| `atr_stop_multiple` | 1.5 | Tighter than the trend campaigns' 2.0 — a reversion trade should be wrong quickly if the range is breaking. |
| `max_bars_in_trade` | 40 | ≈ 6.6 trading days — a reversion should complete fast or be abandoned. |
| `regime_ema` | 200 | Carried for warmup sizing only. |
| `risk_per_trade_pct` | 0.25 | Risk policy. |
| universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF | 6 pairs; NZD_USD excluded on cost structure. |
| timeframe | H4 | The validated infrastructure timeframe (D1 untestable — CAMPAIGN_006). |

**No parameter is swept.** One pre-committed configuration.

## Data, splits, costs, financing

Real OANDA practice H4 candles reused from `data/campaign_002.sqlite3`
(hashes verified in prior campaigns). Standard marathon splits and cost
regimes. Financing estimated via `forex_bot.financing` conservative
stress; unmodeled in-engine; hard live blocker.

## Test-window discipline

Screen on train + validation + cost stress. Open the 2025-2026 reported
test window **only if** the screening gate passes.

## Pass/fail gates (pre-committed)

**Screening gate** — run the test window only if ALL hold: train
expectancy ≥ 0, validation expectancy ≥ 0, validation PF ≥ 1.05, ≥ 2
pairs positive on validation, validation trade count ≥ 30, stress_15x
expectancy ≥ 0.

**Final gate** (only if the test window opens) — even if every numeric
gate passes, the **best attainable verdict is REVISE** (research-only).
A REVISE verdict means "interesting, but mean-reversion tail risk and
the financing blocker require a human decision before any further
step." Otherwise → **REJECT**.

Live trading is out of scope. PAPER-TRADE-ONLY is **not** attainable
for this campaign without human review.

## Known overfitting risks

1. Mean reversion overfits easily — a backtest that looks good is often
   fitting the specific ranges of the sample. The ADX gate, the
   train→validation screening, and the research-only cap are the
   defences. Treat any positive result with strong suspicion.
2. `adx_max=20`, `zscore=±2`, `atr_stop=1.5`, `max_bars=40` are
   pre-committed conventional values, not tuned. They are the degrees
   of freedom; none is swept.
3. The engine has no midline-target exit; the 40-bar time stop is a
   coarse proxy for "reversion completed." A real mean-reversion system
   would exit at the mean — a known limitation, stated in the report.
4. NZD_USD exclusion is partly returns-correlated (acknowledged since
   CAMPAIGN_003).
