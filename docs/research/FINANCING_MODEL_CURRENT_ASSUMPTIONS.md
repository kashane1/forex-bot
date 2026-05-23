# Financing Model — Current Assumptions Audit

**Date:** 2026-05-23 · **Branch:** `research-financing-model-001` · Phase 1
`strategy_evidence: false`

A code-level audit of how the repo currently handles (and mostly
does **not** handle) financing, carry, rollover, spreads,
slippage, and holding costs. This is the baseline the new
`research/financing/` module is built on top of — it is not a
proposal, not a redesign, and changes nothing.

> No strategy is approved. CAMPAIGN_002 remains REJECT. Paper /
> demo / live remain blocked.

## 1. Summary

| dimension | status today | location |
|---|---|---|
| Backtest-engine PnL financing accrual | **NOT modeled** (zero financing in engine PnL) | [`src/forex_bot/backtesting/engine.py:584-606`](../../src/forex_bot/backtesting/engine.py) |
| Per-trade conservative bp/day overlay | implemented | [`src/forex_bot/financing.py`](../../src/forex_bot/financing.py) |
| `FinancingTreatment` enum + approval gate | implemented | [`src/forex_bot/financing.py`](../../src/forex_bot/financing.py) |
| Observed-event schema + repo (dormant) | implemented; empty | [`src/forex_bot/domain/transactions.py`](../../src/forex_bot/domain/transactions.py), [`src/forex_bot/data/repositories.py`](../../src/forex_bot/data/repositories.py), [`src/forex_bot/data/migrations.py`](../../src/forex_bot/data/migrations.py) |
| `DAILY_FINANCING` broker-transaction parser | implemented; never invoked | [`src/forex_bot/broker/mapping.py:230-313`](../../src/forex_bot/broker/mapping.py) |
| Instrument-metadata financing rates | NOT carried | [`src/forex_bot/domain/instruments.py`](../../src/forex_bot/domain/instruments.py) |
| Historical financing-rate time series | NOT available from OANDA | (none) |
| Practice-account `longRate` / `shortRate` | always 0 | (live OANDA practice; documented) |
| Risk-engine financing gates | none | (only the unrelated session-time `rollover` blackout) |
| CAMPAIGN_002 financing in engine PnL | not included | [`backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md`](../../backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md) |
| CAMPAIGN_002 financing-stressed column | applied; flagged as blocker | same |

**Net:** the backtest engine reports financing-free PnL. The
existing per-trade overlay applies a conservative bp/day debit
*after the fact* as a stress column on top of campaign reports.
No real financing is in any engine PnL stream, and live
promotion is unconditionally blocked until that changes.

## 2. What IS modeled today

### 2.1 The conservative per-trade stress overlay

[`src/forex_bot/financing.py`](../../src/forex_bot/financing.py)
ships a single-number-per-pair `bp/day` stress overlay:

| pair | `bp/day` (worse of long/short) |
|---|---:|
| EUR_USD | 0.6 |
| GBP_USD | 0.7 |
| USD_JPY | 1.2 |
| AUD_USD | 0.7 |
| USD_CAD | 0.5 |
| USD_CHF | 0.9 |
| NZD_USD | 0.7 |
| any other | 1.2 (table max, deliberately pessimistic) |

For one closed trade:

```
holding_days  = bars_held * hours_per_bar / 24
notional_usd  = |units| * entry_price   (USD-quote pairs)
              = |units|                 (USD-base pairs)
debit_usd     = holding_days * (bp_per_day / 10_000) * notional_usd
debit_r       = debit_usd / risk_usd
```

Properties:

- **Always ≥ 0.** The model never assumes a financing credit, even
  on the favourable carry side.
- **Side-agnostic.** Long and short use the same `bp/day`, the
  worse of the two — a deliberate conservative simplification.
- **No calendar.** `holding_days` is a flat `bars × hours / 24`
  number; weekends, holidays, and the Wednesday triple-rollover
  convention do not appear.
- **No rate provenance.** The numbers come from
  [`docs/financing_decision.md`](../financing_decision.md);
  they are not pulled from any data source at runtime.

### 2.2 `FinancingTreatment` and the approval gate

`src/forex_bot/financing.py` also defines:

- `FinancingTreatment` — `MODELED` / `ESTIMATED` / `UNMODELED`.
- `FinancingModel` ABC with `debit_r` and `debit_usd`.
- `NoFinancingModel` → `UNMODELED` — what the backtest engine's
  PnL effectively is.
- `ConservativeStressFinancingModel` → `ESTIMATED` — wraps §2.1.
  `default_financing_model()` returns this; research code must
  always at least stress.
- `FutureOandaObservedFinancingModel` → would be `MODELED` but
  **cannot be instantiated** (its `__init__` raises). No code
  path can reach `MODELED` state through it.
- `financing_treatment_blocks_approval(treatment, mode,
  human_override=False)`:
  | treatment | paper | demo | live |
  |---|:--:|:--:|:--:|
  | `MODELED` | allowed | allowed | allowed |
  | `ESTIMATED` | allowed | allowed | **blocked** |
  | `UNMODELED` | **blocked\*** | **blocked\*** | **blocked** |

  `*` — paper / demo `UNMODELED` may be unblocked only by an
  explicit human override; **live can never be overridden**.

- `financing_metadata(model)` — a report-ready dict that every
  research report should embed.

### 2.3 The observed-event capture layer (dormant)

Built for future paper / demo phases, **shipped empty**:

- `ObservedFinancingEvent` Pydantic model (`account_id_hash` is a
  SHA-256 digest — raw account id never stored).
- `hash_account_id()` redactor at the broker boundary.
- `map_daily_financing()` parses OANDA `DAILY_FINANCING`
  transactions into per-instrument, per-trade events.
- `observed_financing_events()` parses any transaction carrying a
  non-zero `financing` field.
- `ObservedFinancingEventRepo` persists events with idempotent
  `event_key` (deterministic hash of `tx_id + instrument + trade`).
- `observed_financing_events` table (migration v3) holds them.

Nothing writes to that table under the research freeze. The bot
submits no orders, so no `DAILY_FINANCING` transaction is
generated and no event is captured. The schema is a forward
seam, not an active pipeline.

### 2.4 Spreads, slippage, commission (cost components that ARE in engine PnL)

These are accounted for in the backtest engine — separately from
financing, and not affected by this sprint:

- **Spread** at fill is recorded via `spread_pips_at_entry` on
  every trade. Bid/ask-aware fills consume the actual spread of
  the active bar.
- **Slippage** is governed by the fill model
  ([`src/forex_bot/backtesting/fills.py`](../../src/forex_bot/backtesting/fills.py)).
- **Commission** is a per-unit constant
  (`commission_per_unit * units`) subtracted at exit in
  [`engine.py:606`](../../src/forex_bot/backtesting/engine.py).

These are not financing. They appear in PnL today; financing does
not.

### 2.5 The session-time `rollover` blackout (NOT a financing model)

Every YAML config under `configs/` has a `rollover` rule under
`block_new_trades`, e.g.:

```yaml
- name: rollover
  start: "16:45"
  end: "17:15"
```

This is the **risk engine's session-time blackout** around the
17:00 NY rollover window. It prevents the strategy from *opening
new trades* in the spread-blow-out window. It does **not** charge
or credit financing. The name overlap is unfortunate but the rule
is unrelated to carry costs.

[`src/forex_bot/backtesting/d1_aggregation.py:39`](../../src/forex_bot/backtesting/d1_aggregation.py)
similarly carves out a rollover-adjacent H4 bar from synthetic D1
aggregation because of *spread*, not because of financing.

## 3. What IS NOT modeled today

### 3.1 In the backtest engine

The PnL formula in
[`engine.py:584-606`](../../src/forex_bot/backtesting/engine.py)
is:

```
gross_quote = price_diff * units
gross_home  = gross_quote                 (if quote_currency == home)
            | gross_quote / exit_price    (if base_currency == home)
            | ValueError                  (otherwise — cross pair)
return gross_home - commission_per_unit * units
```

There is **no financing accrual** anywhere — no daily debit, no
weekend handling, no Wednesday triple-swap, no long/short
distinction. The engine's behaviour is exactly `NoFinancingModel`
(`UNMODELED`).

### 3.2 Calendar-aware rollover events

There is no daily-rollover event log, no `Wednesday triple swap`
handling, no `weekend skip`, no holiday calendar in any layer.

### 3.3 Long-vs-short carry asymmetry

The per-trade overlay uses one number per pair (the worse side).
There is no per-direction rate, no positive-carry credit, no
direction-aware diagnostics.

### 3.4 Historical financing rates

OANDA's v20 REST API publishes no historical financing-rate time
series for 2020–2026. There is no committed historical-rate file
in the repo. The bot has never traded, so no
`DAILY_FINANCING` transaction has been captured for any window.

### 3.5 Practice-account live rates

`GET /v3/accounts/{id}/instruments` returns `longRate` and
`shortRate` for each instrument. On the practice account, both
are **0**. Real financing on the practice account is zero.

### 3.6 Instrument-metadata financing rates

[`Instrument`](../../src/forex_bot/domain/instruments.py)
carries margin rate, precision, and pip metadata, but no
financing rate fields. Adding rates there would be a deliberate
schema change; this sprint does not propose one.

### 3.7 Cross-pair home-currency conversion for financing

The engine refuses cross pairs (no quote against home) for PnL.
The per-trade overlay USD-base/USD-quote heuristic does not
support an arbitrary home currency. Cross-currency financing
conversion is not modeled.

## 4. Where the current financing logic lives

| concern | file | lines |
|---|---|---|
| Per-trade stress overlay (functions) | `src/forex_bot/financing.py` | 42-128 |
| `FinancingTreatment` enum | `src/forex_bot/financing.py` | 142-156 |
| `FinancingModel` + 3 subclasses | `src/forex_bot/financing.py` | 159-264 |
| `default_financing_model` / `blocks_approval` / `metadata` | `src/forex_bot/financing.py` | 267-316 |
| `ObservedFinancingEvent` domain model | `src/forex_bot/domain/transactions.py` | 48-95 |
| `hash_account_id` redactor | `src/forex_bot/domain/transactions.py` | 34-46 |
| `map_daily_financing` parser | `src/forex_bot/broker/mapping.py` | 230-286 |
| `observed_financing_events` parser | `src/forex_bot/broker/mapping.py` | 289-313 |
| `ObservedFinancingEventRepo` | `src/forex_bot/data/repositories.py` | 697-780 |
| `observed_financing_events` table | `src/forex_bot/data/migrations.py` | 313-340 |
| Backtest engine PnL (no financing here) | `src/forex_bot/backtesting/engine.py` | 584-606 |
| Existing design doc | `docs/research/FINANCING_MODEL_DESIGN.md` | (whole file) |
| Existing decision doc | `docs/financing_decision.md` | (whole file) |
| Observed-capture design doc | `docs/research/OBSERVED_FINANCING_CAPTURE.md` | (whole file) |

The new `research/financing/` module Phase 3 introduces is an
**additional** layer on top of these. It does not modify or
re-implement any of them.

## 5. Did CAMPAIGN_002 include financing?

**No, not in engine PnL — yes, as a stress column.**

- Engine PnL for CAMPAIGN_002 contains zero financing accrual
  (confirmed by audit of `engine._pnl`).
- The report
  [`backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md`](../../backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md)
  computes a financing-stressed column per pair from the per-trade
  overlay (Task F) and gates on it as a blocker:

  > "Financing / rollover (Task F): **NOT modeled** in the PnL
  > stream. … financing/rollover unmodeled — see
  > docs/financing_decision.md"

- CAMPAIGN_002's REJECT verdict is independent of financing: it
  rejects on directional expectancy (negative on every pair, both
  engines agree — see
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §3.1). Adding any financing model can only make the verdict
  more REJECT, never less.

## 6. Why financing remains a promotion blocker

Per [`FINANCING_MODEL_DESIGN.md`](FINANCING_MODEL_DESIGN.md) §5 and
the `financing_treatment_blocks_approval` gate:

- Live trading pays **real** financing every rollover. A backtest
  whose PnL omits financing systematically overstates net return.
- A conservative bp/day overlay bounds the error but does not
  eliminate it. `ESTIMATED` is enough to gate paper / demo
  research; it is **never** enough for live.
- No model in this repo produces `MODELED` financing today. The
  `FutureOandaObservedFinancingModel` placeholder cannot be
  instantiated.
- `live` mode unconditionally requires `MODELED`. No human
  override can unblock it (only paper/demo `UNMODELED` may be
  overridden).

Until a real financing model is wired into engine PnL and
reconciled against observed `DAILY_FINANCING` charges, **no
backtest result can be trusted as a net live result**.

## 7. Risk of overstating returns without financing

Without any financing in PnL:

- **Long positions in high-yield-quote pairs** (e.g. long USD_JPY
  in a high US-rate regime) overstate net return — a real account
  would *pay* financing to short JPY equivalently, and *receive*
  financing on the carry-favorable side. The naive PnL captures
  neither.
- **Short positions in high-yield-quote pairs** undeestate net
  return — a real account would *receive* the same financing.
- **Long-holding-period strategies** (e.g. trend-following with
  240-bar time stops) accumulate more rollovers per trade than
  short-holding strategies, so their PnL is more affected.
- **Wednesday rollovers count triple** under most brokers'
  conventions, so a strategy that systematically holds across
  Wednesdays pays/receives ~50 % more financing per calendar week
  than a flat daily count suggests.

For the CAMPAIGN_002 baseline, the conservative overlay applied
≈0.5–1.2 bp/day on average notional, which on multi-week trend
trades amounts to a non-trivial percent-of-risk debit per trade.
The stress test confirmed the verdict was robust to that overlay;
that is not the same as confirming financing is small in the live
case.

## 8. What evidence future strategies need

Concretely, for any future strategy candidate to clear the
financing gate:

1. **Plug a real financing model into engine PnL.** Either
   `FutureOandaObservedFinancingModel` (currently a placeholder)
   or a documented alternative.
2. **Reconcile model output against observed
   `DAILY_FINANCING` transactions** within a tight tolerance over
   a representative window. The observed-event capture layer
   (§2.3) is the seam that records this.
3. **Document `financing_treatment = modeled`** in the campaign's
   evidence package, with provenance.
4. **Pass `financing_treatment_blocks_approval(modeled, "live")`.**

Until items 1–4 exist, financing is at best `ESTIMATED` and live
remains blocked.

The new `research/financing/` module (Phase 3) is a step
**toward** that, not a completion of it:

- It will provide a calendar-aware calculator that consumes any
  rate source.
- It will support a stress-only mode (so research can run today,
  with no historical rates available).
- It will leave a clean seam for an observed-rate source once
  capture begins.
- It will not, by itself, produce `MODELED` financing for any
  campaign. The `FinancingTreatment` it self-reports for stress
  mode is `ESTIMATED`.

## 9. Cross-links

- Existing financing design:
  [`FINANCING_MODEL_DESIGN.md`](FINANCING_MODEL_DESIGN.md)
- Observed-capture design:
  [`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md)
- Decision memo for CAMPAIGN_002:
  [`../financing_decision.md`](../financing_decision.md)
- This sprint's plan:
  [`FINANCING_MODEL_001_PLAN.md`](FINANCING_MODEL_001_PLAN.md)
- Next-direction motivation:
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §5.4
