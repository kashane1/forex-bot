# CAMPAIGN_002 Financing Retrospective (diagnostic only)

**Date:** 2026-05-23 · **Branch:** `research-financing-model-001` · Phase 5
`strategy_evidence: false`

A diagnostic retrospective showing how the new `research/financing/`
module would attach to CAMPAIGN_002 H4 — using CAMPAIGN_002 only
as a rejected-historical example. **No CAMPAIGN_002 metadata,
verdict, or artifact is modified.** No strategy is approved.

> CAMPAIGN_002 H4 `trend_following 0.1.0` remains **REJECT**. This
> retrospective cannot, and does not, change that verdict.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked. This document does not load, fit,
> or revisit CAMPAIGN_002's rules.

## 1. Why a metadata-only retrospective

Actual historical financing rates for 2020–2026 are **not
available** to this repo:

- OANDA's v20 REST API publishes no historical financing-rate
  time series.
- The bot has submitted no orders, so no real
  `DAILY_FINANCING` transactions have been captured.
- The practice account exposes `longRate = shortRate = 0`.

A true retrospective requiring real per-day rates therefore
cannot be performed. What we *can* do — and what this document
shows — is run the new `research/financing/` calculator in
**stress mode** against a small set of CAMPAIGN_002-shaped
positions, to illustrate the calculator's wiring and the
*upper bound* on financing impact under a conservative
assumption.

This is a **demonstration of attachment**, not a financial
restatement.

## 2. Method

- **Source.** `default_stress_rate_source()` — the same
  per-pair bp/day table the existing per-trade overlay uses,
  re-stated in the new module to preserve import isolation.
  Debit-only on both sides (the stress view never assumes a
  credit).
- **Config.** Protocol defaults: `rollover_hour_utc=21`,
  `triple_swap_weekday=2` (Wednesday), `skip_weekends=True`,
  `missing_rate_policy=conservative`, `home_currency=USD`,
  `conservative_fallback_bp_per_day=1.2`.
- **Positions.** Seven synthetic positions across the seven
  CAMPAIGN_002 H4 pairs, each `units=10,000` at a realistic
  entry price, with holding intervals between 4 and 18
  calendar days. These intervals are **representative** of
  trend-following holds in CAMPAIGN_002's universe (which had
  240-bar ≈ 40-calendar-day time stops), not extracted from
  CAMPAIGN_002's actual trade log. The position-id strings are
  opaque labels.
- **`generated_at_utc`** pinned to `2026-05-23T12:00:00+00:00`
  for reproducibility.

This retrospective does not load, deserialize, or parse the
CAMPAIGN_002 trade artifacts under `backtests/campaign_002_real_oanda/`.
That is a deliberate choice: the existing per-trade overlay
already gates CAMPAIGN_002 reports, and re-running anything
against the real trade log risks suggesting a verdict change.
The new calculator is *demonstrated* here, not *applied* to the
campaign.

## 3. Inputs

| position_id | pair | side | units | entry_price | open (UTC) | close (UTC) | cal days |
|---|---|---|---:|---:|---|---|---:|
| `eu-long-1` | EUR_USD | long | 10,000 | 1.0800 | 2026-04-06 08:00 | 2026-04-17 16:00 | 11 |
| `uj-long-1` | USD_JPY | long | 10,000 | 155.00 | 2026-04-06 08:00 | 2026-04-24 16:00 | 18 |
| `gu-short-1` | GBP_USD | short | 10,000 | 1.2600 | 2026-04-13 08:00 | 2026-04-20 16:00 | 7 |
| `au-long-1` | AUD_USD | long | 10,000 | 0.6600 | 2026-04-06 08:00 | 2026-04-10 16:00 | 4 |
| `uc-short-1` | USD_CAD | short | 10,000 | 1.3700 | 2026-04-13 08:00 | 2026-04-23 16:00 | 10 |
| `us-long-1` | USD_CHF | long | 10,000 | 0.9000 | 2026-04-06 08:00 | 2026-04-13 16:00 | 7 |
| `nz-long-1` | NZD_USD | long | 10,000 | 0.6000 | 2026-04-06 08:00 | 2026-04-17 16:00 | 11 |

## 4. Result (stress mode)

Headline aggregate, USD home currency:

| metric | value |
|---|---:|
| positions | 7 |
| `event_count` | 54 |
| `missing_rate_event_count` | 0 |
| `cashflow_home_total` | **-59.13** |
| `cashflow_home_stress_total` | **-59.13** |
| `financing_treatment` | `estimated` |
| `financing_in_engine_pnl` | `false` |
| `financing_is_live_blocker` | `true` |
| `strategy_evidence` | `false` |

Per-position stress totals:

| position_id | pair | side | rollovers | stress (USD) |
|---|---|---|---:|---:|
| `eu-long-1` | EUR_USD | long | 9 | -8.424000 |
| `uj-long-1` | USD_JPY | long | 14 | -24.000000 |
| `gu-short-1` | GBP_USD | short | 5 | -6.174000 |
| `au-long-1` | AUD_USD | long | 4 | -2.772000 |
| `uc-short-1` | USD_CAD | short | 8 | -6.000000 |
| `us-long-1` | USD_CHF | long | 5 | -6.300000 |
| `nz-long-1` | NZD_USD | long | 9 | -5.460000 |
| **total** | | | **54** | **-59.130000** |

The numbers are tiny in dollar terms because each position is
`10,000 units` at the bp-per-day stress rates. The structural
points the run shows:

- The Wednesday triple-rollover multiplier fires correctly
  inside each holding window where Wednesday occurs.
- Weekend skip suppresses Saturday and Sunday rollovers.
- USD_JPY uses the USD-base notional convention (notional =
  units, not units × price).
- GBP_USD short and USD_CAD short are charged at the per-pair
  stress bp/day, same as long would be — the stress source is
  side-symmetric.

## 5. What this would imply at CAMPAIGN_002 scale (rough bound)

CAMPAIGN_002 H4 with-RiskEngine had **1,032 trades**. The
stress-debit per trade scales linearly with notional and holding
days; using the same bp/day table and a charitable mean holding
of ~5 calendar days at ~$10,800 average notional (EUR_USD at
1.08):

```
mean stress debit per trade ≈ 5 days × (0.7 bp/day) / 10000 × 10800
                            ≈ $3.78
total stress drag over 1,032 trades ≈ $3,900
```

On a starting equity of $10,000 — the per-pair convention
CAMPAIGN_002 reports use — that is a **~3–5 % additional drag
relative to starting equity**. The existing per-trade overlay
applies the same magnitude as the financing-stressed column in
[`backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md`](../../backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md).
The result here matches the existing overlay's order of
magnitude — as it should, since the new module mirrors the
bp/day table.

**This is not a tighter or looser claim about historical
financing. It is the same stress bound, expressed in a richer
event log.**

## 6. Why CAMPAIGN_002 remains REJECT regardless

CAMPAIGN_002's H4 rejection reasons (from
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§3):

- Negative expectancy R on **every** pair under both engines
  (bespoke `-0.0001` to `-0.2645`; free verifier corroborates).
- Pair-level `return_pct` negative on every pair on both engines.
- 1,647-trade no-RiskEngine path also REJECT — the strategy
  itself fails, not the risk filters.
- 1,032-trade with-RiskEngine path is the committed REJECT.

Adding any financing model — stress or modeled — can only make
the verdict **more REJECT**, never less:

- Both `cashflow_home` and `cashflow_home_stress` from this
  retrospective are `<= 0`. The stress view caps any potential
  positive carry at 0.
- A real per-day financing model would for some pairs (e.g.
  USD_JPY long) reduce the modeled debit (positive long carry),
  and for others (e.g. AUD_USD long in low-AUD-rate regimes)
  *increase* it. On a campaign that is already loss-making on
  every pair, that has no realistic chance of flipping the
  aggregate verdict.

**The CAMPAIGN_002 verdict is independent of financing.** This
retrospective changes nothing.

## 7. What would be required for production-grade financing

To replace the stress overlay with a real model that genuinely
removes the live-promotion blocker, the existing financing
design doc and approval gate set the bar:

1. **Forward-capture observed financing.** Stand up a funded or
   longer-lived practice account, let the existing
   `ObservedFinancingEventRepo` accumulate `DAILY_FINANCING`
   transactions for ≥ 60 rollovers across the traded universe.
2. **Build a real model.** Implement (a successor to)
   `FutureOandaObservedFinancingModel` from observed events,
   with regression tests reconciling modeled vs actual charges
   within a tight tolerance.
3. **Wire into engine PnL.** A new, opt-in code path in
   `BacktestEngine` so historical backtest reproducibility is
   preserved by default.
4. **Document and approve.** Campaign reports declare
   `financing_treatment = modeled`; a documented human approval
   per the strategy approval process; the financing-live-blocker
   lifts.

Steps 1–4 are **not** done by this sprint. The new
`research/financing/` module **does not** advance any of them on
its own — it provides a calculator that *could* consume a real
rate source once one exists.

## 8. Cross-links

- This sprint's plan:
  [`FINANCING_MODEL_001_PLAN.md`](FINANCING_MODEL_001_PLAN.md)
- Protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Current assumptions audit:
  [`FINANCING_MODEL_CURRENT_ASSUMPTIONS.md`](FINANCING_MODEL_CURRENT_ASSUMPTIONS.md)
- Existing per-trade overlay:
  [`FINANCING_MODEL_DESIGN.md`](FINANCING_MODEL_DESIGN.md)
- CAMPAIGN_002 directional postmortem:
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
- CAMPAIGN_002 report (unchanged):
  [`../../backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md`](../../backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md)
- CAMPAIGN_002 walk-forward retrospective (previous sister
  sprint):
  [`CAMPAIGN_002_WALK_FORWARD_RETROSPECTIVE.md`](CAMPAIGN_002_WALK_FORWARD_RETROSPECTIVE.md)
