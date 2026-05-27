# Next Sprint Prompt — After Financing Modeled PnL Readiness

**Date:** 2026-05-27  
**Branch:** `research-financing-modeled-pnl-and-carry-readiness-001`  
**Recommended next sprint:** `infra-observed-financing-capture-readonly-001`

---

## Context

Financing modeled-PnL readiness sprint complete:

- Deterministic overlay utility implemented and tested
- C008/C009/C018 descriptive exposure measured under `SYNTHETIC_FINANCING_DIAGNOSTIC`
- Validation uplift partially carry-inflated (C018 val +0.194 gross → +0.129 net)
- Engine PnL remains UNMODELED
- No observed broker financing used
- All campaigns remain REJECT; `approved: []`

---

## Recommended sprint: `infra-observed-financing-capture-readonly-001`

### Goal

Capture observed OANDA `DAILY_FINANCING` transactions via **read-only** API access, reconcile against the existing calculator, and produce committed observed-rate fixtures — still **without order APIs** and **without strategy approval**.

### Why this sprint (not the alternatives)

| alternative | why deferred |
|---|---|
| `research-exit-hypothesis-financing-refresh-001` | Synthetic stress already applied; refresh adds little until observed rates exist |
| `research-carry-readiness-rate-source-expansion-001` | No external rate source available; OANDA has no historical series |
| `infra-backtrader-exit-parity-diagnostics-001` | Exit parity is secondary to carry-blind PnL for multi-day MR |

Observed capture is the **binding blocker** for MODELED treatment.

### Hard rules

- Read-only broker endpoints only
- No order APIs
- No strategy approval
- No new strategy campaign unless separately precommitted
- No credentials committed
- `configs/approved_strategies.yaml`: `approved: []`
- Paper/demo/live remain blocked
- `strategy_evidence: false` on all artifacts

### Deliverables

1. Execute read-only capture per `FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`
2. Reconcile via `scripts/reconcile_financing_fixtures.py`
3. Commit observed fixtures (redacted) under `research/financing/fixtures/observed/`
4. Update `modeled_pnl_readiness_audit.json` with observed status
5. Document whether MODELED treatment preconditions are met

### Start from

`research-financing-modeled-pnl-and-carry-readiness-001`

---

## Alternative: `research-exit-hypothesis-financing-refresh-001`

Use only if observed capture is blocked (no practice account access). Would re-run C008/C009/C018 financing overlay with manual CSV rate schedules if an external rate table becomes available. **Does not change verdicts.** Diagnostic only.

---

## Alternative: `infra-backtrader-exit-parity-diagnostics-001`

Use if exit-timing parity (Backtrader vs bespoke engine) is prioritized over financing. Does not address carry-blind PnL.
