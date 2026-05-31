# Carry and Financing Readiness Memo

**Date:** 2026-05-27  
**Branch:** `research-financing-modeled-pnl-and-carry-readiness-001`  
**Type:** Infrastructure memo — `strategy_evidence: false`

---

## 1. Why carry cannot be tested yet

Carry-sensitive strategies require **side-specific, date-specific financing rates** reconciled to broker behavior. Today:

| requirement | status |
|---|---|
| Engine PnL includes financing | **No** — UNMODELED |
| Historical OANDA rate series | **Not available** via REST API |
| Observed DAILY_FINANCING capture | **Not executed** — no transaction history |
| MODELED treatment | **Refused** until observed data exists |
| Conservative stress overlay | **Yes** — ESTIMATED, debit-on-both-sides |

Conservative stress **overstates cost** and **flattens long/short asymmetry**. It can falsify strategies (stress test) but cannot identify carry-positive edges.

---

## 2. Data needed for MODELED financing

| data | purpose |
|---|---|
| Observed broker DAILY_FINANCING transactions | Empirical rate reconstruction |
| Daily long/short financing rates by instrument | Per-side accrual in backtest window |
| Account currency (USD) | Notional conversion |
| Rollover cutoff (17:00/21:00 UTC per broker) | Event timing — calculator defaults to 21:00 UTC |
| Weekend triple-rollover behavior | Wednesday ×3 convention |
| Holiday non-rollover calendar | Avoid false accrual on closed markets |

---

## 3. What synthetic/manual schedules can do

- **Descriptive diagnostics** on existing trades (this sprint)
- **Stress gates** — "strategy survives pessimistic carry"
- **Fixture-backed unit tests** for calculator correctness
- **Relative comparison** of hold-duration / exit variants under identical synthetic rates

Synthetic schedules **cannot** approve strategies or claim MODELED treatment.

---

## 4. What requires read-only broker access (future sprint)

- Pull `DAILY_FINANCING` transactions from practice/live account (read-only)
- Snapshot current `longRate`/`shortRate` from instruments endpoint (point-in-time only)
- Reconcile observed events against calculator output
- Build committed observed-rate fixtures with provenance

**No order APIs.** Credentials never committed.

---

## 5. Safety rules for future observed capture sprint

- Read-only endpoints only (`GET /v3/accounts/{id}/transactions`, instruments)
- No order submission
- Redact account IDs in committed artifacts
- `strategy_evidence: false` until separately precommitted campaign
- Observed fixtures require reconciliation pass before MODELED claim
- `configs/approved_strategies.yaml` remains `approved: []`

---

## 6. Integration into future backtests

Recommended path:

1. **Phase A (complete):** Off-engine overlay on trade records (`apply_modeled_financing_overlay.py`)
2. **Phase B (future):** Observed rate table → `TableRateSource` with `source_type=observed_future` after reconciliation
3. **Phase C (future):** Opt-in `BacktestEngine` flag `include_financing=True` research-only, off by default
4. **Phase D (future):** `FutureOandaObservedFinancingModel` implementation → `FinancingTreatment.MODELED`

Engine wiring must remain **opt-in** until observed rates are reconciled.

---

## 7. Why no strategy approval without modeled/observed financing

- Gross R on 40-bar H4 holds misstates net edge by ~0.05–0.09 R/trade (this sprint's diagnostic)
- C018 validation +0.194 R gross → +0.129 R net under stress — still positive but materially lower
- Live promotion requires `FinancingTreatment.MODELED` per `financing_treatment_blocks_approval`
- Passing conservative stress does **not** lift the live blocker

---

## 8. Carry-readiness conclusion

**Not ready.** Infrastructure for deterministic overlay exists; observed rate capture is the binding blocker for MODELED treatment and carry research.
