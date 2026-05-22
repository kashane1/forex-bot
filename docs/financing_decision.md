# Financing / rollover decision for CAMPAIGN_002

## Decision

**Option 2 — financing remains UNMODELED for CAMPAIGN_002. We add a
conservative stress estimate and mark this as a BLOCKER for any
paper-to-live promotion.**

## Why not Option 1 (full historical model)

OANDA exposes financing primarily as account-state events:

- `DAILY_FINANCING` and `RESETTABLE_PL` are transaction types emitted on
  the live account's transaction stream after rollover; they reflect
  the *actual* financing charge applied per trade.
- `GET /v3/accounts/{accountID}/instruments` exposes the current
  `financing.longRate` / `shortRate` per instrument, but these are
  point-in-time values; OANDA does not publish a historical financing
  curve through the v20 REST API that we can backtest against.

Building a faithful per-day financing model would require:

1. Either capturing OANDA financing rates daily for an extended period
   (a forward-looking effort, not retroactive), OR
2. Modelling financing from market interest-rate differentials
   (effective Fed Funds, SONIA, BoJ short-rate, etc.) plus an
   OANDA-specific spread on top — a research project in its own right.

The v0 broker stack does not support either. Implementing #2 inside
this campaign would mean introducing untested model assumptions, which
is the opposite of the campaign's purpose.

## Conservative stress estimate

For the v0 trend-following baseline we apply a conservative annualized
financing assumption ONLY in the report's stress sections, not in the
backtester's PnL stream.

Worst-case carrying cost assumption per pair, per side, expressed in
basis points per *calendar day* the position is open:

| pair    | long bp/day | short bp/day | source / rationale |
|---------|------------:|-------------:|---|
| EUR_USD |  0.6 |  0.6 | tight EUR-USD rate differential 2020-2026 average |
| GBP_USD |  0.4 |  0.7 | GBP higher rates intermittently; punish short |
| USD_JPY |  1.2 |  0.1 | wide rate differential, BoJ near zero |
| AUD_USD |  0.7 |  0.5 | varies with RBA / Fed |
| USD_CAD |  0.4 |  0.5 | small spread |
| USD_CHF |  0.9 |  0.1 | SNB negative rates → expensive to be long USD when not |
| NZD_USD |  0.7 |  0.5 | similar to AUD |

These are intentionally pessimistic and overstate the cost in the
average case. The CAMPAIGN_002 report computes a "financing-stressed"
return per pair by deducting (avg_trade_days × bp_per_day × notional)
from each trade's PnL after the fact, in a clearly-labelled section.

## Blocker for live promotion

A strategy cannot move from paper to live based on this campaign alone.
A subsequent campaign must either:

- (a) accumulate at least 30 days of practice `DAILY_FINANCING`
  transactions and rerun with that empirical model, or
- (b) implement a market-interest-rate-derived model with regression
  tests against a sample of historical rate data.

Documented as a blocking limitation in
[`backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md`](../backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md).
