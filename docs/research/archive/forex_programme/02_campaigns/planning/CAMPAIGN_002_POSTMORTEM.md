# CAMPAIGN_002 Post-Mortem

Status: **CAMPAIGN_002 is accepted as a valid negative result.** This
document is the immutable summary. It does not change, rescue, or
re-tune the frozen baseline.

## One-paragraph summary

The frozen `trend_following 0.1.0-baseline-frozen` strategy (EMA 50/200
filter, Donchian-20 prior-bar breakout, ATR-14, 2.0×ATR initial +
trailing stop, 0.25% risk, one position per instrument) was backtested
on **real OANDA practice candles** for 7 major FX pairs across H4 and
H1, 2020-01-01 → 2026-05-20, with the **production RiskEngine wired into
the backtester**. It lost money on the untouched test split, on the
full window, on every pair, and across all 81 robustness parameter
combinations. The result is **REJECT**.

## What CAMPAIGN_002 established

| Fact | Evidence |
|---|---|
| Real OANDA data was used | 7 pairs × {H4,H1}, ~9.9k H4 + ~39.7k H1 candles/pair, host `api-fxpractice.oanda.com`, raw + normalized SHA256 per fetch in `data_sources`. |
| RiskEngine was wired in | All 665 backtest runs invoked `RiskEngine.evaluate()` (`mode="backtest"`). Parity test: `tests/unit/test_risk_engine_backtest_parity.py`. |
| The frozen baseline was rejected | See untouched-test metrics below. No strategy rule was changed before, during, or after. |
| The result is broad, not a fluke | 0 of 81 robustness parameter combinations produced a positive full-window return. |
| Costs make it worse, monotonically | base → stress_15x → stress_2x worsens expectancy every step. |

### Untouched-test-split metrics (2025-01-01 → 2026-05-20)

| timeframe | trades | return % | profit factor | expectancy R | win rate |
|---|---:|---:|---:|---:|---:|
| H4 | 207 | **−0.88%** | **0.74** | **−0.088** | 34.9% |
| H1 | 247 | **−1.74%** | **0.44** | **−0.206** | 23.7% |

Both timeframes are negative on the data the strategy had never been
evaluated against. Profit factor is far below the 1.05 promotion gate.

### Robustness

The 3×3×3×3 grid (ema_fast × ema_slow × donchian × atr_stop = 81
combinations, 7 pairs each) produced **0 positive combinations**. The
best was the baseline-adjacent 60/200/20/2.5 at −3.55% mean return. The
whole parameter surface is underwater — there is no isolated winner to
chase, and therefore no optimization worth doing.

### Financing

Financing / rollover is **not modeled**. Per
[`docs/financing_decision.md`](../financing_decision.md) it is a
documented blocker. Since the strategy is already net-negative *before*
financing, modeling financing would only deepen the loss — it does not
change the REJECT, but it does mean no positive variant may be trusted
until financing is handled.

## Why this must NOT move to paper / demo / live

1. **Negative untouched-test expectancy after realistic costs.** The
   one split reserved as out-of-sample is negative on both timeframes.
2. **Profit factor 0.44–0.74 on test**, far below the 1.05 gate.
3. **No positive pair, no positive parameter set.** There is nothing to
   promote — paper-trading a known-negative system only spends time and
   (eventually) money confirming what the backtest already proved.
4. **Financing unmodeled** — a hard blocker independent of the above.
5. The CAMPAIGN_002 recommendation engine output **REJECT** under the
   pre-committed Task J gates. Promotion would contradict the gates the
   campaign was designed around.

Paper-loop, demo-loop, and order submission remain disabled. This
branch (`campaign-003-diagnostics`) changes none of that.

## Diagnostic findings (this branch)

Three diagnostic documents accompany this post-mortem. They are
analysis-only; they ran no new campaign and changed no strategy rule.

- [`backtests/campaign_002_real_oanda/DATA_QUALITY_CLASSIFICATION.md`](../../backtests/campaign_002_real_oanda/DATA_QUALITY_CLASSIFICATION.md)
  — the `Clean=False` audit flags are 99.99% expected market closures;
  genuine defects are 46 bars (~0.013% of 347,509 candles): two brief
  mid-week feed outages plus a handful of 1–5 bar gaps. **Data quality
  does not affect the REJECT.**
- [`backtests/campaign_002_real_oanda/RISK_REJECTION_ANALYSIS.md`](../../backtests/campaign_002_real_oanda/RISK_REJECTION_ANALYSIS.md)
  — 85% of rejections are spread-family (`SPREAD_TO_ATR`,
  `SPREAD_TOO_WIDE`). They are protective: they block entries whose edge
  is smaller than the cost to enter. They are not choking profit — the
  signals that *do* pass are themselves net-negative.
- [`backtests/campaign_002_real_oanda/TRADE_DIAGNOSTICS.md`](../../backtests/campaign_002_real_oanda/TRADE_DIAGNOSTICS.md)
  — 2,254 full-window baseline trades: 66% losers, win rate 34% against
  a ~45% break-even requirement. Long and short both lose (≈−0.11R
  each — not a directional bias). The 452 trades that exit on the
  *initial* stop without the trailing stop ever engaging average
  **−0.744R at a 0% win rate** — the false-breakout signature. The
  trailing-stop mechanism itself is mildly positive (+0.044R); the
  entry is the problem.

## Root-cause summary

The Donchian-20 breakout enters as price closes beyond a recent
extreme. On the real 2020-2026 majors, that close is too often the
*exhaustion* of the move, not the start of one: price reverses and hits
the initial stop. The strategy wins ~34% of the time with an average
winner (+0.61R) too small relative to its average loser (−0.50R) to
survive a 34% hit rate. This is the textbook trend-following failure
mode in range-bound / mean-reverting conditions, and the 2020-2026
majors spent much of the period in exactly that regime.

The next research step is **not** to re-tune this entry. It is to test
whether restricting *when* and *where* the breakout is taken (regime,
timeframe, universe) can lift it across break-even — and, if that
fails, to test a different entry family. See
[`HYPOTHESIS_BACKLOG.md`](HYPOTHESIS_BACKLOG.md) and
[`CAMPAIGN_003_PROPOSAL.md`](CAMPAIGN_003_PROPOSAL.md).
