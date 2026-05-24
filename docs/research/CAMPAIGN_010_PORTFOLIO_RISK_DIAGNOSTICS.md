# CAMPAIGN_010 — Portfolio-Risk Diagnostics

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-walk-forward-001`
`strategy_evidence: false`

Phase 6 portfolio-risk diagnostics for the CAMPAIGN_010
walk-forward evidence (`session_breakout 0.1.0-c010`).
**Diagnostic only — these numbers do not gate the verdict.** The
Phase 4 verdict
([`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md))
remains **REJECT** regardless. The diagnostics confirm that the
candidate's failure is not the result of an unconstrained risk
posture: in fact, the RiskEngine is structurally bounded, rejected
14 % of would-be signals as cost-of-trade protections, and never
allowed concurrent positions.

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. The
> risk-engine activations summarized below are evidence that the
> existing safety gates fired correctly during research; they are
> not evidence of an edge.

## 1. Commands

```bash
.venv/bin/python scripts/build_campaign_010_risk_diagnostics.py \
    --campaign-dir backtests/CAMPAIGN_010_session_breakout/
```

Outputs:

- [`backtests/CAMPAIGN_010_session_breakout/risk/diagnostics.json`](../../backtests/CAMPAIGN_010_session_breakout/risk/diagnostics.json)
- [`backtests/CAMPAIGN_010_session_breakout/risk/diagnostics.md`](../../backtests/CAMPAIGN_010_session_breakout/risk/diagnostics.md)

## 2. Concurrency (structurally enforced)

- **Max concurrent open positions per instrument: 1.** The
  bespoke `BacktestEngine` is
  single-instrument-single-position-at-a-time; the candidate's
  R2 rule (block re-entry while an open position exists)
  prevents pyramiding in the strategy module itself.
- **Max open positions (config gate): 1.**
- **Max positions per instrument (config gate): 1.**
- **Max correlated positions (config gate): 1.**
- **Max aggregate notional: bounded by the
  `risk.risk_per_trade_pct = 0.25 %` of the per-pair `$500`
  starting equity** — i.e. the entry size is small relative to
  account equity, gated by the position-sizing formula in
  `forex_bot.risk.sizing`.

No fold produced a concurrency violation, no fold violated the
position-cap rule, and the trade ledger contains no overlapping
trades for any pair × fold combination.

## 3. Per-pair exposure

| pair | trades | total units | total notional (quote ccy approx) | total PnL (USD) | max loss streak | max win streak | largest single loss (USD) | largest single win (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EUR_USD | 310 | 68,083 | 73,732 | −31.07 | 8 | 4 | −1.28 | +3.09 |
| GBP_USD | 565 | 98,223 | 125,162 | −30.57 | 10 | 8 | −1.28 | +4.20 |
| USD_JPY | 492 | 97,166 | 13,913,539 (JPY) | −26.81 | 9 | 9 | −1.29 | +3.49 |
| AUD_USD | 511 | 125,636 | 83,478 | −48.14 | 8 | 11 | −1.29 | +2.96 |
| USD_CAD | 434 | 114,900 | 155,389 | −46.32 | 8 | 6 | −1.28 | +3.33 |
| USD_CHF | 432 | 90,675 | 81,024 | +8.45 | 9 | 8 | −1.30 | +5.35 |
| NZD_USD | 47 | 8,361 | 5,124 | −8.33 | 4 | 4 | −1.27 | +1.35 |

Notes:

- **No single trade exceeded ~$1.30 of equity loss** (out of
  `$500` starting; `0.25 %` risk-per-trade ≈ $1.25). The
  position-sizing gate held.
- **Maximum loss streak across the campaign: 11** (AUD_USD;
  most pairs are 8-10). This is consistent with the trade
  count and the negative expectancy — it is not evidence of
  the engine misbehaving.
- **Largest single win: +$5.35** (USD_CHF); largest single
  loss: −$1.30 (USD_CHF) — wins are bounded above by the time
  stop's catch of profitable moves; losses are bounded below
  by the ATR-based hard stop.
- **USD_JPY notional** is in JPY (the pair's quote currency);
  ~13.9 M JPY ≈ $90 K USD-equivalent at the period's exchange
  rates. Consistent with USD-base notional convention; not a
  position-size anomaly.

## 4. Entry-session clustering

| UTC hour | trades |
|---:|---:|
| 06:00 | 1,030 |
| 09:00 | 1,761 |

| session bucket | trades |
|---|---:|
| London (06–12 UTC) | 2,791 |

**Every entry is in the London window** by design (R3 / R4 enforce
the session windows). The two clusters are exactly the two H4 bar
boundaries that fall inside the London window under each NY DST
posture:

- **06:00 UTC** = London open under NY-standard time alignment
  (Asian H4 bar at 02:00 UTC; eligible from late Oct through
  mid-March).
- **09:00 UTC** = London open under NY-DST (Asian H4 bar at
  05:00 UTC; eligible from mid-March through late Oct).

This pattern was anticipated in
[`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md);
the diagnostic confirms the candidate fires only on the intended
session bars.

## 5. Exit-reason distribution

| reason | trades | share |
|---|---:|---:|
| `time` (max_bars_in_trade hit) | 2,107 | 75.5 % |
| `stop` (ATR hard stop) | 661 | 23.7 % |
| `eod` (end-of-day flat) | 23 | 0.8 % |

The candidate is **time-stop-dominated** — most trades hit the
6-bar holding window without either reaching a profit target or
stopping out. This is a structural feature of the rule set
(no `take_profit`, no `trailing_stop` in v1) and is the most
useful diagnostic for understanding the negative expectancy:
breakout direction is not persistent enough over 24 H4 hours to
turn a positive R-multiple under a 6-bar time-stop with no
trailing logic.

## 6. RiskEngine rejection totals (mode = backtest)

| code | count | meaning |
|---|---:|---|
| `SPREAD_TOO_WIDE` | 414 | rejected because the live spread exceeded the per-pair `spread_filter.max_spread_pips` (a real, protective rejection) |
| `SPREAD_TO_ATR` | 770 | rejected because spread/ATR exceeded `spread_filter.max_spread_to_atr_pct = 8 %` |
| **total** | **1,184** | |

Of the **3,975 raw signals** the strategy emitted (`2,791 trades
+ 1,184 rejected`), the RiskEngine rejected **29.8 %** as
cost-of-trade unsafe — and the trades that *did* go through still
produced a net loss. The spread-filter activation is evidence the
existing risk infrastructure ran correctly, not evidence of a
risk problem; it does not change the verdict.

The committed rejection tables include **per-pair** breakdowns in
[`backtests/CAMPAIGN_010_session_breakout/risk/diagnostics.json`](../../backtests/CAMPAIGN_010_session_breakout/risk/diagnostics.json).

## 7. Drawdown clustering

`backtests/CAMPAIGN_010_session_breakout/risk/diagnostics.json`
records each fold's per-pair `max_drawdown_pct` and the median
per-fold value. Headline numbers:

| fold | median per-pair max DD % | worst per-pair max DD % | worst pair |
|---:|---:|---:|---|
| 0 | −1.04 | −3.45 | USD_CAD |
| 1 | −2.07 | −4.13 | USD_CHF |
| 2 | −1.62 | −3.43 | GBP_USD / AUD_USD |
| 3 | −1.92 | −2.85 | USD_CAD |
| 4 | −1.91 | −4.10 | GBP_USD |
| 5 | −1.50 | −2.99 | AUD_USD |
| 6 | −1.22 | −2.41 | NZD_USD (despite few trades) |
| 7 | −1.02 | −2.06 | GBP_USD |

No single per-pair fold drawdown exceeds the `risk.max_total_drawdown_pct
= 8 %` config gate; no risk-cap activation forced an early
exit. The −8 % aggregate cap would gate at the *account* level
in a live loop; in the per-pair-isolated backtest accounting
used here, each pair runs against its own `$500` starting equity.

## 8. What this tells us about the verdict

- The strategy's failure is **directional**, not a result of
  unsafe risk posture. Every per-trade loss is bounded by the
  ATR stop; every concurrent-position rule held; every
  cost-of-trade rejection fired correctly.
- The signal mix is **biased toward time-stops** (75.5 %),
  consistent with the hypothesis being falsified — the
  breakout direction does not persist long enough to produce
  positive R-multiples on average.
- **NZD_USD is structurally thin** (47 trades vs 310–565 for
  the majors). The pair's session windows are aligned with
  off-peak NZD liquidity; consistent with the candidate's
  spread-filter activations. Even if NZD_USD were excluded
  (`pairs_positive` would still be 1 of 6), the verdict would
  not change.

## 9. Safety state

- `configs/approved_strategies.yaml`: **`approved: []`** (untouched).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **Paper / demo / live remain blocked.**
- **No risk-policy change.** `RiskEngine` ran in `mode='backtest'`
  exactly as configured by the campaign YAML.
- **No broker call; no `.env` read; no credential printed.**
- **No live-loop command exists.**

## 10. Cross-links

- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_010_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_010_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`backtests/CAMPAIGN_010_session_breakout/risk/diagnostics.json`](../../backtests/CAMPAIGN_010_session_breakout/risk/diagnostics.json)
- [`backtests/CAMPAIGN_010_session_breakout/risk/diagnostics.md`](../../backtests/CAMPAIGN_010_session_breakout/risk/diagnostics.md)
- [`scripts/build_campaign_010_risk_diagnostics.py`](../../scripts/build_campaign_010_risk_diagnostics.py)
