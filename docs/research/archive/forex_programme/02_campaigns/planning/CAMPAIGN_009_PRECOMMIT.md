# CAMPAIGN_009 — Mean-Reversion + Midline Exit — Pre-Commit

Written and committed **before** the campaign runs. This is a
human-authorized, focused follow-up to CAMPAIGN_008, **not** a marathon
campaign and **not** a re-grade of CAMPAIGN_008.

- **Date written:** 2026-05-22 (before any CAMPAIGN_009 run)
- **Branch:** `campaign-009-mean-reversion-human-review`
- **Authority:** human review — see `docs/research/CAMPAIGN_008_HUMAN_REVIEW.md`
- **Strategy:** `mean_reversion 0.2.0-c009`
- **Config:** `configs/campaign_009_mean_reversion.yaml`

## Status — research, paper-ceiling

Mean reversion has fat-tailed loss risk: a range that breaks into a
trend turns a reversion trade into a large loss. CAMPAIGN_009's **best
attainable verdict is PAPER-TRADE-ONLY.** It can never recommend demo
or live trading. The strategy is `paper_only = True`. A REJECT outcome
is an equally valid, acceptable result.

This campaign does **not** authorize paper-loop, demo-loop, or order
submission. It produces a backtest report and a recommendation only.

## Hypothesis

CAMPAIGN_008 (regime-filtered H4 mean reversion) was REJECT solely
because its train split came in at −0.017 R against a pre-committed
"train ≥ 0" gate. On validation (2023–2024, never used for design) it
was clearly positive: +0.172 R, PF 1.29, 6/6 pairs positive, and it
survived 2× cost stress. Its known structural weakness: the backtest
engine had **no midline-target exit** — reversion trades could only
leave via the hard ATR stop or a 40-bar time stop.

**CAMPAIGN_009 hypothesis:** giving the strategy a midline-target exit
— exit a reversion trade when price reverts to the mean it was measured
against — produces a cost-adjusted, financing-aware, out-of-sample edge
that clears a fresh, stricter screening gate, with the train split
**independently** non-negative.

This is an honest open question, not a foregone conclusion: CAMPAIGN_008
full-window time-stop exits averaged +1.89 R, so cutting trades at the
mean could just as plausibly *cap* winners. The campaign tests it.

## The single predeclared rule change

Exactly **one** change versus `mean_reversion 0.1.0-c008`; everything
else is frozen identical.

**Add a midline-target exit.** At entry the strategy computes the
midline = rolling mean of close over `zscore_lookback` bars (the exact
mean the z-score is measured against). It emits this level as the
signal's `take_profit_price`. The backtest engine then exits the trade
at the midline when price reaches it:

- **Long:** exit at the midline when the bar's favourable extreme
  reaches it (price reverts *up* to the mean).
- **Short:** exit at the midline when price reverts *down* to the mean.
- The **hard ATR stop is retained** and keeps **same-bar precedence** —
  if a bar touches both the stop and the target, the adverse stop wins
  (conservative).
- The **40-bar time stop is retained** as a backstop for trades that
  neither hit the stop nor revert to the mean.
- The **regime filter (ADX-14 < 20) and every entry rule and parameter
  are unchanged.**

The change is opt-in behind a `midline_exit` config flag. With the flag
off, the emitted signal is byte-identical to CAMPAIGN_008, so
CAMPAIGN_008 remains exactly reproducible. CAMPAIGN_009 sets
`midline_exit: true`.

No parameter is tuned. No parameter will be tuned after results are
seen.

## Strategy — `mean_reversion 0.2.0-c009`

All rules: completed bars only, prior bars only, no lookahead.

At the latest completed bar `t`:

1. **Range regime gate** — ADX-14 < `adx_max`. If a trend is present,
   no trade. (The single most important guard.)
2. **Over-extension** — z-score of close over `zscore_lookback` bars
   beyond threshold, with RSI confirmation:
   - long iff z ≤ `zscore_long_threshold` AND RSI < 35
   - short iff z ≥ `zscore_short_threshold` AND RSI > 65
3. Direction is **counter** to the extension (reversion toward the mean).

**Mandatory hard stop** = `atr_stop_multiple × ATR-14`.
**Midline target** = rolling mean of close over `zscore_lookback` bars.
**Exit** = hard stop, midline target, or `max_bars_in_trade` time stop
— whichever comes first; the adverse stop wins a same-bar tie.

**Explicitly forbidden** (and structurally impossible here): averaging
down, grids, martingale, adding to a loser. The strategy emits a single
`Signal`; the RiskEngine enforces one position per instrument; there is
no position-scaling code path.

## Parameters (frozen — identical to CAMPAIGN_008)

| parameter | value | note |
|---|---|---|
| `adx_lookback` / `adx_max` | 14 / 20.0 | range-regime gate — unchanged from c008 |
| `zscore_lookback` | 20 | z-score window; also the midline window |
| `zscore_long_threshold` / short | −2.0 / +2.0 | unchanged from c008 |
| `rsi_lookback` | 14 | unchanged from c008 |
| `atr_lookback` | 14 | unchanged from c008 |
| `atr_stop_multiple` | 1.5 | unchanged from c008 |
| `max_bars_in_trade` | 40 | time-stop backstop — unchanged from c008 |
| `regime_ema` | 200 | warmup sizing only — unchanged from c008 |
| `midline_exit` | **true** | **the one change** (c008: absent → false) |
| `risk_per_trade_pct` | 0.25 | risk policy — unchanged |
| universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF | 6 pairs; NZD_USD excluded |
| timeframe | H4 | D1 untestable (CAMPAIGN_006 infra blocker) |

**No parameter is swept.** One pre-committed configuration.

## Data, splits, costs, financing

- **Data:** real OANDA practice H4 candles, reused from
  `data/campaign_002.sqlite3` — the identical store CAMPAIGN_002–008
  used. Reuse is valid only if per-request data hashes reproduce the
  CAMPAIGN_002 provenance (same instrument/granularity/window/source/
  candle-count). No synthetic fallback — if the data is absent or its
  provenance does not reproduce, the campaign stops.
- **Splits:** train 2020-01-01→2022-12-31; validation
  2023-01-01→2024-12-31; reported test 2025-01-01→2026-05-20; full
  descriptive 2020-01-01→2026-05-20.
- **Cost regimes:** base (0.5× spread, 0.2 pip slippage), stress_15x
  (1.5×, 0.3 pip), stress_2x (2.0×, 0.5 pip).
- **RiskEngine:** wired in for every run, `mode="backtest"`. Per-signal
  rejection CSVs exported for every run.
- **Financing:** estimated via the conservative `forex_bot.financing`
  stress overlay; **UNMODELED in-engine**; applied in the report as a
  stress; an unconditional hard blocker for any live consideration.

## Test-window discipline

- **Screening (Step A)** runs **only** train + validation, under all
  three cost regimes. The 2025–2026 test window and the 2020–2026 full
  window are **not run** during screening.
- The reported test window **and** the full descriptive window are run
  **only if every screening gate below passes.**
- If any screening gate fails: stop, do not open the test window, write
  the REJECT report, do not tune.

## Pass/fail gates (pre-committed)

### Screening gate — open the test window only if ALL hold

1. Train expectancy **≥ 0** R.
2. Validation expectancy **> 0** R (strictly positive).
3. Validation profit factor **≥ 1.05**.
4. Stress_2× validation expectancy **≥ 0** R.
5. Financing-stressed validation expectancy **≥ 0** R (validation
   expectancy minus the conservative financing debit).
6. **≥ 2 of 6** pairs with positive validation return.
7. Validation trade count **≥ 30** (meaningful sample).
8. Worst per-pair validation max drawdown **within −8 %** policy.
9. RiskEngine invoked on every screening run (parity complete).
10. Data provenance clean — every run sourced `oanda-practice`, data
    hashes reproduce.

### Final gate — only evaluated if the test window was opened

Verdict is **PAPER-TRADE-ONLY** only if ALL hold:

1. Test expectancy **> 0** R.
2. Test profit factor **≥ 1.05**.
3. Stress_2× test expectancy **≥ 0** R.
4. Financing-stressed test expectancy **≥ 0** R.
5. **≥ 2 of 6** pairs with positive test return.
6. Worst per-pair test max drawdown **within −8 %** policy.
7. Limitations stated explicitly in the report.

Otherwise → **REJECT**. If the screening gate did not pass, the test
window is never opened and the verdict is **REJECT** (screening-only).

**PAPER-TRADE-ONLY is the ceiling.** Live trading is out of scope and
will not be recommended under any result.

## Known overfitting risks

1. Mean reversion overfits easily — a good-looking backtest often fits
   the sample's specific ranges. The ADX gate, the train→validation
   screening, the stricter c009 gates, and the sealed test lockbox are
   the defences. Treat any positive result with suspicion.
2. The entry/regime parameters are pre-committed conventional values
   carried verbatim from c008; none is swept. The midline exit is a
   structural rule, not a tuned number — it has no free parameter (the
   window equals `zscore_lookback`).
3. The midline exit could *cap* winning trades rather than improve
   them (c008 time-stop exits averaged +1.89 R). The test is designed
   to detect that, not hide it.
4. NZD_USD exclusion is partly returns-correlated (acknowledged since
   CAMPAIGN_003).
5. Financing is unmodeled in-engine — a hard live blocker regardless of
   any backtest figure.
