# Financing Model Design

**Date:** 2026-05-22 · **Branch:** `infra-research-foundation-001` · Phase 2
**Module:** `src/forex_bot/financing.py`
**Tests:** `tests/unit/test_financing.py`, `tests/unit/test_financing_model.py`

> Financing is **not solved.** This document describes an explicit
> *architecture* for financing treatment — it does not claim financing
> is modeled. It is not. Financing remains a hard blocker for any live
> promotion.

## 1. What OANDA exposes — and does not

- `GET /v3/accounts/{id}/instruments` returns a `financing` object with
  `longRate` / `shortRate` per instrument. On the **practice** account
  these are **both 0** — practice accounts carry no real financing
  rates. They are also point-in-time values, not a history.
- `DAILY_FINANCING` transactions appear on an account's transaction
  stream after each rollover and reflect the *actual* charge per held
  trade. They exist **only for trades actually held**. This research bot
  has submitted no orders, so there is **no empirical financing
  history** to fit.
- The OANDA v20 REST API publishes **no historical financing-rate time
  series**. There is nothing to backtest 2020–2026 against.

## 2. Why accurate historical financing is not available

A faithful per-day financing model would need one of:

1. **Forward capture** — record OANDA financing rates (or
   `DAILY_FINANCING` transactions from a funded account) daily for an
   extended period. This is forward-looking; it cannot recover
   2020–2026 retroactively.
2. **A market-rate-derived model** — reconstruct financing from interest
   -rate differentials (effective Fed Funds, SONIA, BoJ short rate,
   etc.) plus an OANDA-specific spread, with regression tests against a
   sample of real charges.

The current stack supports neither. Implementing #2 inside a research
campaign would inject untested model assumptions — the opposite of
disciplined research. So financing stays **out of the backtest engine's
PnL**, and is handled as an explicit, conservative stress overlay.

## 3. The conservative stress overlay

`src/forex_bot/financing.py` provides per-pair carry costs in **basis
points of notional per calendar day** a position is open
(`CONSERVATIVE_BP_PER_DAY`). Each value is the worse (more expensive) of
the long and short side, deliberately pessimistic — it overstates the
cost in the average case.

For one closed trade:

```
holding_days  = bars_held * hours_per_bar / 24
notional_usd  = |units| * entry_price        (or |units| for USD-base pairs)
debit_usd     = holding_days * (bp_per_day / 10_000) * notional_usd
debit_r       = debit_usd / risk_usd         (risk = |entry - stop| * units)
```

The debit is **always ≥ 0** — the stress model never assumes a financing
*credit*, even on the favourable carry side. Campaign reports deduct
this debit after the fact in a clearly-labelled "financing-stressed"
column, and gate on the stressed result.

A passing financing-stress test means only "the result is not
*additionally* killed by a pessimistic financing assumption." It does
**not** mean financing is modeled.

## 4. The financing-model interface (Phase 2)

To make the financing posture explicit and gate-able, Phase 2 wraps the
overlay in an interface:

- **`FinancingTreatment`** enum — every backtest / campaign / approval
  declares one of:
  - `modeled` — real per-day financing in the engine's PnL;
  - `estimated` — the conservative stress overlay only (not in PnL);
  - `unmodeled` — financing not accounted for at all.
- **`FinancingModel`** — abstract base. `debit_r` / `debit_usd` return
  one trade's financing cost; `treatment` declares the posture.
  - **`NoFinancingModel`** — `unmodeled`; returns 0. This is the
    backtest engine's *current* behaviour in PnL terms.
  - **`ConservativeStressFinancingModel`** — `estimated`; wraps the
    overlay above. **The default** (`default_financing_model()`).
  - **`FutureOandaObservedFinancingModel`** — a `modeled` placeholder
    that **cannot be instantiated** (its `__init__` raises). It marks
    the seam for future work and guarantees no report can reach a false
    `modeled` state through it.
- **`financing_metadata(model)`** — a report-ready dict
  (`financing_treatment`, `financing_in_engine_pnl`,
  `financing_is_live_blocker`). Every research report should embed it.
- **`financing_treatment_blocks_approval(treatment, mode, ...)`** — the
  approval building block (see §6).

The default is deliberately `estimated`, never silently `unmodeled`:
research must always at least stress financing.

## 5. Why financing remains a live blocker

Live trading pays **real** financing every rollover. A backtest whose
PnL omits financing systematically overstates net return; a conservative
overlay bounds the error but does not remove it. Until financing is
genuinely `modeled` and reconciled against real charges, **no backtest
result can be trusted as a net live result.** Financing is therefore an
unconditional hard blocker for live promotion — independent of any
strategy verdict.

## 6. Financing and strategy approval

`financing_treatment_blocks_approval` ties financing to the approval
workflow (enforced in Phase 5):

| treatment | paper | demo | live |
|---|:--:|:--:|:--:|
| `modeled` | allowed | allowed | allowed (financing-wise) |
| `estimated` | allowed | allowed | **blocked** |
| `unmodeled` | **blocked\*** | **blocked\*** | **blocked** |

\* `unmodeled` may be lifted for paper / demo **only** by an explicit,
documented human override. **Live is never** unblocked by an override —
it unconditionally requires `modeled` financing. (Live additionally has
the existing config-layer live gates on top of this.)

This is why, with the conservative `estimated` overlay, the best
attainable verdict across CAMPAIGN_002–009 was PAPER-TRADE-ONLY — and
why even that was never reached.

## 7. What "solving" financing would require

In priority order:

1. Stand up a funded (or longer-lived practice) account and **capture
   `DAILY_FINANCING` transactions forward** for ≥ 60 rollovers across
   the traded universe.
2. Build `FutureOandaObservedFinancingModel` from that data, with
   regression tests reconciling modeled vs actual charges within a tight
   tolerance.
3. Wire the model into `BacktestEngine` PnL (a new, opt-in code path —
   it must not silently change historical backtest reproducibility).
4. Only then may a report carry `financing_treatment = modeled`, and
   only then is the financing live-blocker lifted.

Until all four are done, financing stays `estimated` at best.

## 8. Validation

```bash
.venv/bin/python -m pytest tests/unit/test_financing.py tests/unit/test_financing_model.py -q
ruff check src/forex_bot/financing.py
```
