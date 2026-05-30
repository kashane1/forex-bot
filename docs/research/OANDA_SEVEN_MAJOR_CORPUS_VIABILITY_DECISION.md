# OANDA Seven-Major Corpus — Viability Decision

**Decision:** `CONTINUE_ONLY_WITH_NEW_EXTERNAL_THESIS`

**Scope:** this decision concerns *strategy search on the current
seven-major OANDA FX corpus*. It does not approve anything, does not
create a campaign, and does not change the freeze. Paper/demo/live
remain blocked; the approved-strategy registry stays empty.

**Date:** 2026-05-29. Grounded in Phases 0–2 of this sprint and the
existing closeout/pause docs.

---

## The four options, and why this one

| Option | Verdict |
|--------|---------|
| `CONTINUE_CURRENT_CORPUS` (resume broad search) | **Rejected.** Broad, undirected mining is exhausted; every family is cost-defeated or no-effect. Resuming would repeat known failures. |
| `CONTINUE_ONLY_WITH_NEW_EXTERNAL_THESIS` | **Chosen.** The corpus stays available, but new strategy work runs *only* behind a genuine new external thesis + the front gate — never a re-tune. |
| `PAUSE_CURRENT_CORPUS` | Close, but understates the finding. "Pause" implies the same search resumes later unchanged; the evidence says undirected search should *not* resume on this corpus as-is. |
| `RETIRE_CURRENT_CORPUS_FOR_STRATEGY_SEARCH` | Too absolute. A genuinely new, cost-aware external thesis still deserves *one* front-gate screen here; retiring outright would forbid even that. |

`CONTINUE_ONLY_WITH_NEW_EXTERNAL_THESIS` is the most precise,
conservative, evidence-consistent label: it forbids the thing that keeps
failing (undirected mining and re-tunes) while leaving a narrow,
gated door open for a genuinely new idea.

### The critical caveat

Phase 2 found the binding constraint is **structural cost**, not idea
quality. Therefore a new thesis is only worth running here if it
**plausibly changes the cost math** — e.g., a much larger gross edge, a
fundamentally different holding pattern, or a regime the cost wall does
not dominate. A new thesis that produces another few-pip edge will hit
the *same* spread/financing squeeze and fail the front gate. **The
higher-expected-value reopen is new data or a lower-cost venue**, which
is the subject of Phases 4–6 (market/data redirect). In short: the
corpus is not where the next *edge* most likely lives, but it remains a
valid place to *screen* a strong new thesis cheaply.

---

## What is still worth doing on the current corpus

1. **Run a single front-gate screen for a genuinely new external
   thesis** (if and only if one appears) — pre-registered, frozen
   thresholds, matched-null + ablation + MCC + cost-feasibility. Never a
   re-tune of a rejected family.
2. **Keep the corpus as the cheap, well-instrumented baseline.** It has
   hardened parity, a working null/front-gate lab, M1 plumbing, and a
   conservative cost model — an excellent *control* environment for
   testing methodology and for null comparison.
3. **Non-strategy hardening** that strengthens any future search:
   cost/execution simulation, the parked observed-financing calibration
   (only when justified), evidence-archive hygiene, and the front-gate
   lab itself.
4. **Catalogue maintenance** of real-but-not-tradable effects (C1) so a
   lower-cost venue can revisit them immediately.

## What is no longer worth doing on the current corpus

1. **Broad, undirected strategy mining.** Exhausted.
2. **Re-tuning any rejected family** (trend, breakout, mean-reversion,
   pullback, MTF/LTF confluence, exits, events, cross-sectional,
   vol-managed TSMOM, relative-value spread, range/vol non-time bars).
   All closed; reopen needs new data or a new thesis, not parameters.
3. **Directional / microstructure non-time-bar search.** Retired
   (stop-criterion met after C029/H16/H03).
4. **Slow macro / carry / regime strategies that need breadth, a real
   rate leg, multi-cycle history, or real financing rates.** These are
   data-blocked on 7 USD majors and ~6.4y.
5. **Anything requiring true tick / order-book data.** Not available.

## Evidence required to reopen *broad* strategy search on this corpus

Broad search reopens **only** when one or more of the following is true
(consistent with every prior closeout):

- **Materially longer history** (≈10–15y) to power slow/regime/macro
  signals across multiple cycles.
- **Non-USD FX crosses** to break USD-leg crowding and enable genuine
  breadth (cross-sectional, carry, relative-value).
- **True tick / order-book data** to make the microstructure lane
  testable at all.
- **A lower-cost execution venue** (institutional/ECN/futures cost
  profile) that changes the two-sided cost squeeze.
- **A genuinely new external thesis** that is cost-aware by construction
  (not a re-tune) — which still must clear the front gate.

Absent all of these, the freeze holds and the corpus stays in
control/baseline mode.

---

## Status guarantees (unchanged by this decision)

- No strategy approved; registry empty; loops refuse.
- No campaign created; no train/validation/test run.
- Freeze intact; `STRATEGY_STATUS.md` still asserts NO-GO.

This decision sets up Phase 4 (alternative markets/data) and Phase 6
(recommended next direction), which address where the next *edge* is
more likely to live.
