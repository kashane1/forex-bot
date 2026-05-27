# Entry Orchestration Parity Decision

**Branch:** `infra-entry-orchestration-parity-diagnostics-001`  
**Date:** 2026-05-27

---

## Classification

**BACKTRADER_IMPLEMENTATION_GAP** (resolved in diagnostic lane)

Prior classification of ~20% trade-count divergence was **not** an expected orchestration difference and **not** a bespoke engine bug.

---

## Primary questions answered

1. **Why fewer BT trades?** Missing JPY/CAD quote→USD PnL conversion inflated drawdown → RiskEngine `DRAWDOWN_LIMIT` blocked USD_JPY entries (59 of 75 C008 gaps).

2. **Filter vs orchestration?** Orchestration bug in BT PnL accounting; spread/session filters behave consistently on matched pairs.

3. **Can BT match without rule changes?** **Yes** — PnL fix alone; ±1 trade residual.

4. **Is bespoke entry orchestration trustworthy?** **Yes** — BT entries were exact subset with identical entry/exit timestamps.

5. **Acceptable for exit-only corroboration?** **Yes**, and after PnL fix **full entry parity is essentially achieved** (±1).

---

## Exit parity validity

**Remains valid.** Exit-reason shares matched before entry fix; matched trades had identical exit timestamps. Exit findings were never contaminated by the PnL bug (matched subset was self-consistent).

---

## Full campaign parity

**Limited prior to fix; now viable** after landing PnL conversion in the Backtrader lane and refreshing exit-parity artifacts.

---

## Engine bug suspected?

| Engine | Suspected? |
|---|---|
| Bespoke | **No** |
| Backtrader lane | **Yes (fixed in branch)** — PnL conversion |

---

## Precommit-002 allowed?

**Yes** — entry gap explained and fixable; exit pathology corroborated; no bespoke bug.

---

## Financing

**Remains blocked.** Manual sample paused.

---

## Recommended next sprint

**`infra-backtrader-entry-parity-hardening-001`**

Land PnL fix + engine-aligned risk windows in the Backtrader lane, refresh `research/backtrader_exit_parity/*` artifacts, re-run exit comparison at ±1 trade tolerance, then proceed to `research-exit-hypothesis-precommit-002`.

---

## Approval statement

No strategy approved. `approved: []`. All campaigns REJECT. No CAMPAIGN_019.
