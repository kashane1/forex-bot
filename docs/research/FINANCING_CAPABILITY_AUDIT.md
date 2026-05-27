# Financing Capability Audit

**Date:** 2026-05-27  
**Branch:** `research-financing-modeled-pnl-and-carry-readiness-001`  
**Sprint:** `FINANCING_MODELED_PNL_AND_CARRY_READINESS_001`  
**Machine-readable audit:** [`research/financing/modeled_pnl_readiness_audit.json`](../../research/financing/modeled_pnl_readiness_audit.json)

> **Diagnostic only** — `strategy_evidence: false`. No strategy approved. CAMPAIGN_018 remains REJECT.

---

## 1. Current architecture

```
BacktestEngine PnL          → UNMODELED (no financing accrual)
        │
        ▼
Trade CSV / JSON artifacts  → gross pnl, r_multiple, bars_held
        │
        ├── src/forex_bot/financing.py
        │     ConservativeStressFinancingModel (per-trade bp/day debit)
        │     Treatment: ESTIMATED
        │
        └── research/financing/
              calculate_run(PositionInterval[], rate_source)
              Per-day rollover events, long/short asymmetric
              Treatment: ESTIMATED (MODELED refused)
```

The two layers are **complementary**: the src overlay is the authoritative approval-gate path for per-trade stress; the research calculator provides richer per-event diagnostics (rollovers, triple-swap, weekend skip, side asymmetry).

---

## 2. What has been implemented

| component | location | status |
|---|---|---|
| Conservative bp/day overlay | `src/forex_bot/financing.py` | Production research path; ESTIMATED |
| FinancingModel interface | `src/forex_bot/financing.py` | NoFinancingModel, ConservativeStressFinancingModel, FutureOandaObserved placeholder |
| Per-day rollover calculator | `research/financing/calculator.py` | Complete, 70+ tests |
| Rate sources | `research/financing/rates.py` | TableRateSource, ConservativeStressRateSource |
| Fixture loaders | `research/financing/fixtures.py` | JSON rate tables + observed-event shape |
| Campaign overlay scripts | `scripts/build_campaign_0{10..14}_financing_overlay.py` | C010–C014 only |
| Reconciliation tooling | `scripts/reconcile_financing_fixtures.py` | Synthetic fixture validation |
| Observed capture design | docs + `scripts/capture_oanda_observed_financing_pilot.py` | Designed, not executed under freeze |

---

## 3. What has not been implemented

| gap | impact |
|---|---|
| Financing in engine PnL | Gross backtest R is carry-blind; multi-day holds misstate net edge |
| Historical OANDA rate series | Cannot backtest with broker-accurate daily rates for 2020–2026 |
| Observed DAILY_FINANCING capture | No empirical rate table to reconcile against |
| MODELED treatment | Refused at four layers until observed data exists |
| C008/C009/C018 financing overlays | No descriptive exposure report until this sprint |
| Trade-record → overlay utility | Campaign scripts are per-campaign; no generic utility until this sprint |
| Cross-pair home-currency conversion | Calculator uses conservative fallback for non-USD-home pairs |
| Holiday calendar | Missing holidays fall through to missing-rate policy |

---

## 4. Why financing matters for 40-bar H4 holds

C008/C009/C018 mean-reversion uses a **40-bar (≈6.7-day) time stop** on H4 bars. Typical holds span multiple rollover events (17:00 UTC). At conservative 0.5–1.2 bp/day on notional:

- A 7-day EUR_USD short at ~$33k notional → ~$1.4–$2.8 financing drag
- Expressed in R (ATR-based stop ~1.5×): often **0.05–0.15 R per trade**
- C018 validation +0.194 R over 142 trades → **~0.001 R/trade gross uplift**; financing drag on multi-day winners could materially reduce net edge

CAMPAIGN_018 validation improved vs C008 (+0.194 vs +0.161 R) while train worsened (−0.119 vs −0.025 R). Without financing adjustment, we cannot distinguish carry tail from exit improvement.

---

## 5. Why carry research cannot proceed without modeled financing

Carry-sensitive strategies (positive roll on one side, negative on another) require:

1. **Side-specific rates** — conservative stress debits both sides; cannot identify carry-positive setups
2. **Daily rate history** — constant bp/day misses rate-regime changes across 2020–2026
3. **Net PnL in engine or overlay** — gross R alone cannot gate carry hypotheses
4. **Observed reconciliation** — synthetic schedules cannot approve strategies

Until MODELED financing exists (observed rates reconciled to broker), carry campaigns are **blocked**.

---

## 6. What this sprint will change

- Add `FinancingSourceType` and manual CSV rate loader
- Add generic `apply_modeled_financing_overlay.py` utility
- Produce C008/C009/C018 descriptive financing exposure (SYNTHETIC_FINANCING_DIAGNOSTIC)
- Document carry-readiness gaps and next-sprint options

## 7. What this sprint will not change

- Engine PnL (remains UNMODELED unless opt-in research flag added — not planned)
- C008/C009/C018 verdicts
- `configs/approved_strategies.yaml`
- Executor/broker behavior
- Any strategy parameters
