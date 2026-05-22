# CAMPAIGN 006 — Daily (D1) Trend — Report

> **Result: REJECT — no valid result (infrastructure incompatibility).**
> The D1 trend hypothesis could not be tested: the backtester's
> intraday-designed fill / session / spread machinery is invalid for D1
> candles, which close at the daily rollover. This is a documented
> infrastructure blocker scoped to D1 only; H4 campaigns are unaffected.
> Research Marathon 001, Phase 2.

## Provenance

- **Campaign:** CAMPAIGN_006_DAILY_TREND
- **Branch:** `research-marathon-001`
- **Git commit:** `e5c0fa659cec070ee644ab93cd9871d256c7132a`
- **Working tree dirty at report time:** yes (report + ledger pending commit)
- **Config:** [`configs/campaign_006_daily_trend.yaml`](../configs/campaign_006_daily_trend.yaml)
- **Strategy:** `trend_following 0.1.0-baseline-frozen` on D1 (frozen rules, timeframe = D)
- **Pre-commit:** [`docs/research/CAMPAIGN_006_DAILY_TREND_PRECOMMIT.md`](../docs/research/CAMPAIGN_006_DAILY_TREND_PRECOMMIT.md) (with a post-run discovery amendment)
- **RiskEngine invoked:** YES — all 36 runs, `mode="backtest"`
- **Financing:** estimated stress model (`forex_bot.financing`); not reached — no trades.

## Data

Real OANDA practice **D1** bid/ask candles, fetched fresh from the
practice host into `data/campaign_002.sqlite3` (D1 was not part of
CAMPAIGN_002). Complete candles only, 2020-01-01 → 2026-05-20.

| pair | D1 candles | raw_sha256 (12) |
|---|---:|---|
| EUR_USD | 1656 | `a8cf1ca1718d` |
| GBP_USD | 1656 | `a3d31216ed83` |
| USD_JPY | 1657 | `3b26474d51eb` |
| AUD_USD | 1656 | `8dc3a22bbcc8` |
| USD_CAD | 1656 | `d3ff144136c8` |
| USD_CHF | 1656 | `08b02db45239` |

Data is real, complete, and provenance-hashed. The data is **not** the
problem.

## What happened

The screening run executed all 36 runs (6 pairs × {train, validation,
full} + 18 cost-stress) and produced **0 trades in every run**.

The strategy itself is not silent. A direct probe of
`trend_following 0.1.0-baseline-frozen` over the full EUR_USD D1 series
generated **100 raw breakout signals**. Every one was then rejected by
the production RiskEngine:

| rejection code | count (EUR_USD full) | of 100 raw signals |
|---|---:|---|
| `SESSION_BLOCKED` | 100 | **100%** |
| `SPREAD_TOO_WIDE` | 89 | 89% |
| `SPREAD_TO_ATR` | 5 | 5% |

(A signal can carry several codes; `SESSION_BLOCKED` alone is fatal.)

## Root cause — infrastructure, not strategy

OANDA D1 candles are timestamped at their **close = 17:00
America/New_York**, which is the **daily rollover** (`daily_alignment:
17`). Two independent consequences:

1. **Session filter.** The RiskEngine's `session_filter` blocks new
   trades in the rollover window 16:45–17:15 NY. Every D1 signal's
   timestamp is 17:00 NY — squarely inside that window. Result:
   `SESSION_BLOCKED` on 100% of D1 signals. The rollover blackout is an
   *intraday-entry-timing* safeguard; for a once-per-day D1 decision it
   is structurally inapplicable, yet it vetoes everything.

2. **Spread basis.** The engine reads the *signal bar's close* bid/ask
   for the fill model and the spread filter. A D1 bar's close bid/ask
   **is** the thin-liquidity rollover spread:

   | pair | D1 close-spread median | H4 close-spread median |
   |---|---:|---:|
   | EUR_USD | 2.0 pips | 1.5 |
   | USD_JPY | 2.7 pips | 1.6 |
   | GBP_USD | 3.7 pips | 1.9 (p95 15.0) |

   A D1 system would not transact at the rollover — it would act on the
   next day's open in normal hours. Backtesting it against
   rollover-inflated spreads would overstate costs and is not a
   trustworthy basis for a result.

The backtester (fill model, spread-at-signal, session filter) was
designed and validated for **intraday H1/H4 candles**, whose close
carries a representative tradeable price. It does **not** support a
next-bar-open fill or a non-rollover spread reference, which a correct
D1 backtest requires.

## Decision

Per the marathon's hard-stop discipline — *do not rely on an unreliable
backtester/reporting path* — CAMPAIGN_006 is recorded as a
**methodological NO-VALID-RESULT**. The D1 trend hypothesis is neither
confirmed nor refuted; it was **not testable** with the available
infrastructure.

This blocker is **scoped to D1**. The H1/H4 path has been validated
across CAMPAIGN_001–005 and is unaffected, so this does **not** trigger
a full-marathon stop. The ladder continues to CAMPAIGN_007 (H4
pullback-continuation).

No config or strategy was hacked to force trades: doing so would have
produced a number built on rollover spreads — exactly the kind of
unreliable evidence the marathon forbids.

## Pass/fail

- Screening gate: **FAIL** (0 trades — not a strategy signal; an
  infrastructure incompatibility).
- Reported test window (2025-2026): **NOT opened** (lockbox intact).
- Verdict: **REJECT — no valid result.**

## Recommendation

- Do not paper-trade, demo-trade, or live-trade anything from this
  campaign — there is no result to act on.
- A genuine D1 test would first require a backtester methodology
  upgrade: next-bar-open entry fills and a normal-hours (non-rollover)
  spread reference for D1. That upgrade is **out of scope** for this
  marathon and would itself need validation before any D1 result could
  be trusted. Logged as a follow-up infrastructure item.

_Live trading is not recommended and not in scope._
