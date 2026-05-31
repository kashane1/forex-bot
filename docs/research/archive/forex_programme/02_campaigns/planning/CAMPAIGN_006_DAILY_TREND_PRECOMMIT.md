# CAMPAIGN_006 — Daily (D1) Trend — Pre-Commit

Written and committed **before** the campaign runs. Research Marathon
001, Phase 2.

## Hypothesis

The H1/H4 breakout/trend campaigns (002-004) and the CAMPAIGN_005
benchmark all failed for cost/turnover reasons: at H4 the spread is
~5% of ATR and price paths retrace ~76% of their movement (efficiency
ratio 0.24). **A daily (D1) timeframe trades far less often and each
move is larger relative to the fixed spread, so spread drag per unit of
signal is much lower.** If a trend edge exists anywhere in this
universe, D1 is where it has the best chance to clear costs.

## Strategy

`trend_following 0.1.0-baseline-frozen` — the **frozen baseline rules,
unchanged**, run on D1 candles. The *only* difference from CAMPAIGN_002
is the timeframe. This is deliberate: it isolates the single variable
"does a daily timeframe rescue the trend entry?" No ADX gate (the
CAMPAIGN_003 ADX experiment is concluded). One predeclared variant.

Rules (frozen):
- EMA 50 / 200 direction filter (on D1 = the classic golden/death cross).
- Donchian-20 breakout using prior bars only.
- ATR-14, 2.0×ATR initial stop, 2.0×ATR trailing stop.
- Max one open position per instrument, 0.25% risk per trade.
- Production `RiskEngine.evaluate()` wired into the backtest.
- `max_bars_in_trade`: 60 D1 bars (≈ 3 trading months) — a D1-appropriate
  time stop (CAMPAIGN_002 used 240 H4 bars ≈ 40 days; 60 D1 ≈ 84
  calendar days is the closest sensible analogue and is fixed here).

## Universe & data

- D1, 6 pairs: EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF.
  NZD_USD excluded on the cost-structure basis used since CAMPAIGN_003.
- Real OANDA practice D1 bid/ask candles, complete only, 2020-01-01 →
  2026-05-20. D1 was **not** fetched by CAMPAIGN_002, so it is fetched
  fresh from OANDA practice; provenance hashes recorded. No synthetic
  fallback — stop if the fetch fails.

## Splits, costs, financing

- Standard splits: train 2020-2022, validation 2023-2024, reported test
  2025-01-01 → 2026-05-20, full descriptive.
- Cost regimes: base, stress_15x, stress_2x.
- Financing: estimated via `forex_bot.financing` conservative stress;
  unmodeled in-engine; hard live blocker.

## Test-window discipline

Screen on train + validation + cost stress first. The reported test
window is opened **only if** the screening gate passes.

## Pass/fail gates (pre-committed)

**Screening gate** — the 2025-2026 test window is run only if ALL hold:
- train expectancy ≥ 0 after base costs
- validation expectancy ≥ 0 after base costs
- validation profit factor ≥ 1.05
- ≥ 2 pairs positive on validation
- validation trade count ≥ 30 (meaningful)
- stress_15x expectancy ≥ 0

**Final gate** (only if the test window is opened) — PAPER-TRADE-ONLY
only if ALL hold: test expectancy > 0, test PF ≥ 1.05, ≥ 2 pairs
positive on test, stress_2x expectancy > 0, financing-stressed test
expectancy > 0, worst test drawdown within the 8% policy.

Otherwise → **REJECT**. Live trading is out of scope.

## POST-RUN DISCOVERY (amendment, added after the screening run)

The screening run produced **0 trades across all 36 runs**. Root cause
is an infrastructure incompatibility, not a strategy result:

- OANDA D1 candles are timestamped at their **close = 17:00 America/
  New_York = the daily rollover** (`daily_alignment: 17`).
- Therefore every D1 signal's timestamp lands inside the session
  filter's rollover blackout (16:45–17:15 NY): **SESSION_BLOCKED fired
  on 100/100 raw signals.**
- Independently, the D1 candle's close bid/ask **is** the thin-liquidity
  rollover spread. Measured: EUR_USD D1 close-spread median 2.0 pips
  (H4 1.5), GBP_USD 3.7 (H4 1.9), p95 up to 15 pips. The engine's fill
  model and spread filter both read the signal bar's close spread — for
  D1 that is rollover-contaminated and unrepresentative of where a D1
  system would actually transact (the next day's open, normal hours).

The current backtester was designed and validated for intraday (H1/H4)
candles, whose close carries a representative tradeable price. It
**cannot validly backtest a D1 strategy** without methodology changes
(next-bar-open fills, a non-rollover spread reference). Making those
changes mid-marathon and trusting the result would violate the
marathon rule against relying on an unreliable backtester path.

**CAMPAIGN_006 is therefore recorded as a methodological NO-VALID-RESULT
(verdict REJECT).** The D1 hypothesis is neither confirmed nor refuted
— it was not testable with the available infrastructure. The marathon
continues to CAMPAIGN_007 (H4, where the infrastructure is sound). See
`backtests/CAMPAIGN_006_DAILY_TREND_REPORT.md`.

## Known overfitting risks

1. **Low trade count.** D1 over 6 years ≈ 1565 bars per pair; after the
   EMA-200 warmup and one-position-at-a-time, each split yields few
   trades. The screening gate's ≥30-validation-trades rule guards
   against concluding from noise. If trade counts are too thin the
   honest verdict is REJECT (insufficient evidence), not a marginal
   pass.
2. No parameters are swept; the strategy is the frozen baseline. The
   only D1-specific choice is `max_bars_in_trade=60`, fixed above.
3. NZD_USD exclusion is partly returns-correlated (acknowledged since
   CAMPAIGN_003).
