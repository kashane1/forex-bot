# FX Futures Viability Decision (Phase 5)

**Sprint:** `research-fx-futures-venue-and-diagnostic-001`
**Type:** Documentation only.
**Date:** 2026-05-31
**Question:** Can the next sprint realistically perform a *meaningful* futures diagnostic on the frozen factors?

---

## Verdict: **VIABLE_WITH_LIMITATIONS**

A meaningful, decision-forcing futures diagnostic **is** executable — but only for **carry**, only on **free/local EOD data**, and with an honest prior that it most likely **confirms the null** rather than reviving an edge. C1 is gated behind paid/account intraday data; S4 is infeasible and venue-inappropriate. The diagnostic is therefore worth running as the programme's **final, closeout-quality falsification**, not as a revival attempt.

---

## Why not `READY_FOR_DIAGNOSTIC`

`READY` would mean the next sprint can run the diagnostic immediately with infrastructure and data in hand. It cannot yet:
- the futures **ingestion + continuous-contract roll adapter does not exist** (designed in Phase 1, not built — this sprint is docs-only);
- free-source **coverage must be confirmed** at ingestion (Stooq/Yahoo EOD depth per contract; 6J ×100 scaling);
- tick/commission specs need `[CONFIRM]`.

These are one focused build sprint away, not in place now.

## Why not `NOT_VIABLE`

`NOT_VIABLE` would mean no informative futures test is possible at all. That is false:
- **Carry is fully fundable from free/local EOD data with decades of history** — more than the spot corpus's ~6.4 y, directly fixing the carry power limit;
- futures **structurally removes the nightly financing wall** (the exact constraint that defeated C031/carry), giving carry its first *fair* venue test;
- the basis/roll (futures carry) is directly observable in the same free feed.
That test is genuinely decision-forcing, so the situation is not non-viable.

## Why `VIABLE_WITH_LIMITATIONS` is the honest call

| Factor | Feasible next sprint? | Limitation |
|--------|----------------------|------------|
| **Carry** | **Yes** (free/local EOD) | Honest prior: gross collapses toward the spot-predictive leg (~0); fair test, likely null |
| **C1** | Only if a paid/account **intraday** feed is secured | Free intraday too shallow; USD-major-only (cross form is an artifact) |
| **S4** | **No** | Needs synced tick + latency model; binding constraint (≤1-bar staleness) is venue-independent |

So 1 of 3 frozen factors is free-feasible now, 1 is data-gated, 1 is excluded with reasons. That is the definition of *viable with limitations*.

---

## The limitations, stated plainly

1. **Scope shrinks to carry** for a free/local run. C1 is a stretch goal contingent on intraday data; S4 is out.
2. **The likely result is a null, not a revival.** The cost model shows futures removes both the financing *penalty* and the accrual *benefit* (same rate differential, two sides), so carry-in-futures gross ≈ its spot-predictive content, which was statistically zero. Futures gives a *fair* test; it cannot manufacture predictability.
3. **Build cost before any result:** an ingestion + roll adapter and coverage confirmation are required first.
4. **Even a "survives" outcome for carry would be modest** and would still need a future pre-registered front-gate screen (a separate sprint) before meaning anything tradable — and nothing here approves trading.

---

## What this implies for the programme

The futures pivot is **worth completing as a closeout-grade test**, primarily because it lets the programme retire its two strongest open questions honestly:
- *Was carry only financing-defeated, or genuinely non-predictive?* → futures (no financing) answers this cleanly.
- *Is the programme's failure truly cost, or idea quality?* → a fair-cost venue that *still* yields null carry would confirm **idea quality / efficiency**, not just cost, as the ceiling — strengthening the eventual archive decision.

This sets up Phase 6's next prompt: a **scoped, carry-first futures diagnostic** (free/local EOD), with C1 as a conditional stretch and S4 excluded — explicitly framed as decision-forcing toward either a narrow continue or the pre-committed archive.
