# CAMPAIGN_007 — H4 Pullback-Continuation — Pre-Commit

Written and committed **before** the campaign runs. Research Marathon
001, Phase 3.

## Hypothesis

CAMPAIGN_002-004 and the CAMPAIGN_005 benchmark showed the failure mode
is **breakout exhaustion**: a Donchian breakout enters at a fresh
extreme, which is too often the end of the move (the diagnostic trade
analysis found 452 trades exiting on the initial stop at −0.744 R / 0%
win — immediate reversals). **A pullback-continuation entry never buys
the extreme.** It waits for price, inside an established trend, to
retrace toward the trend EMA and then *resume*. If the trend has any
real persistence, entering on the resumption (not the extreme) should
have a better cost-adjusted edge.

## Strategy — `pullback_continuation 0.1.0-c007`

A genuinely different entry family. **No Donchian breakout anywhere.**
All rules use completed, prior bars only — no lookahead.

At the latest completed bar `t`:

1. **Trend regime** — EMA-50 > EMA-200 ⇒ uptrend; EMA-50 < EMA-200 ⇒
   downtrend; otherwise no trade.
2. **Pullback** — within the `pullback_lookback` bars *before* `t`,
   price retraced to the trend EMA: for a long, some bar's low came
   within `pullback_band × ATR-14` of EMA-50 (mirror for a short).
3. **Continuation** — bar `t` resumes the trend: for a long,
   `close[t] > high[t-1]` AND `close[t] > EMA-50[t]` (mirror for short).

Entry on the continuation bar. Stop = `2.0 × ATR-14`. Exit = `2.0 ×
ATR-14` trailing stop + a `max_bars_in_trade` time stop. Max one
position per instrument, 0.25% risk. Production RiskEngine wired in.

## Parameters (frozen)

| parameter | value | rationale |
|---|---|---|
| `ema_fast` / `ema_slow` | 50 / 200 | Same trend-regime definition as every prior campaign — keeps "is there a trend" comparable; the change under test is the *entry*, not the regime filter. |
| `atr_lookback` | 14 | Standard Wilder ATR, as everywhere. |
| `pullback_lookback` | 6 | 6 H4 bars ≈ 1 trading day — a pullback must be recent to still be actionable. |
| `pullback_band` | 0.5 | The retrace must come within 0.5 ATR of EMA-50 to count as "pulled back to the average" — a normal-depth pullback, not a deep reversal. |
| `atr_stop_multiple` | 2.0 | Same as CAMPAIGN_002-004 — stop is not a hidden variable. |
| `trailing_stop_atr_multiple` | 2.0 | Same trailing machinery as prior campaigns. |
| `max_bars_in_trade` | 120 | Same H4 time stop as CAMPAIGN_002/004. |
| `risk_per_trade_pct` | 0.25 | Risk policy. |
| universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF | 6 pairs; NZD_USD excluded on cost structure. |
| timeframe | H4 | The validated infrastructure timeframe (D1 is not testable — see CAMPAIGN_006). |

**No parameter is swept.** One pre-committed configuration. No
robustness grid in the decision path.

## Data

Real OANDA practice H4 candles, reused from `data/campaign_002.sqlite3`;
provenance hashes already verified in CAMPAIGN_002-005. No re-fetch, no
synthetic data.

## Splits, costs, financing

Standard marathon splits (train 2020-2022, validation 2023-2024,
reported test 2025-01-01 → 2026-05-20, full). Cost regimes base /
stress_15x / stress_2x. Financing estimated via `forex_bot.financing`
conservative stress; unmodeled in-engine; hard live blocker.

## Test-window discipline

Screen on train + validation + cost stress. Open the 2025-2026 reported
test window **only if** the screening gate passes.

## Pass/fail gates (pre-committed)

**Screening gate** — run the test window only if ALL hold:
- train expectancy ≥ 0 after base costs
- validation expectancy ≥ 0 after base costs
- validation profit factor ≥ 1.05
- ≥ 2 pairs positive on validation
- validation trade count ≥ 30
- stress_15x expectancy ≥ 0

**Final gate** (only if the test window opens) — PAPER-TRADE-ONLY only
if ALL hold: test expectancy > 0, test PF ≥ 1.05, ≥ 2 pairs positive on
test, stress_2x expectancy > 0, financing-stressed test expectancy > 0,
worst test drawdown within the 8% policy. Otherwise **REJECT**.

Live trading is out of scope.

## Known overfitting risks

1. `pullback_lookback=6` and `pullback_band=0.5` are two new
   parameters. Both are pre-committed to conventional values (≈1 day;
   half an ATR) and are **not swept**. They are the only degrees of
   freedom beyond the shared EMA/ATR/stop settings.
2. Pullback-continuation is a well-known pattern; the risk is not
   exoticism but that 2020-2026 H4 trends may lack the persistence for
   a resumption to follow through — which the screening gate will catch.
3. NZD_USD exclusion is partly returns-correlated (acknowledged since
   CAMPAIGN_003).
