# CAMPAIGN_015 — No-Follow-Up-Candidate Decision (At This Time)

**Sprint:** [CAMPAIGN_015 Post-Run Diagnostics 001](CAMPAIGN_015_POST_RUN_DIAGNOSTICS_001_PLAN.md)
**Branch:** `research-campaign-015-post-run-diagnostics-001`
**Date:** 2026-05-26
**Decision:** **No new strategy candidate is designed in this sprint.**

> Decision document only. Does **NOT** approve any strategy, does
> **NOT** modify CAMPAIGN_015, does **NOT** revise the runner verdict.
> `configs/approved_strategies.yaml` remains `approved: []`.

---

## 1 · What this document is

The Phase 6 step in the sprint plan permits — but does not require —
a docs-only design for a future candidate that builds on the
diagnostics. The user's brief states:

> "Only do this phase if diagnostics support a follow-up."
> "If diagnostics do not justify a future candidate, write:
> `docs/research/CAMPAIGN_015_NO_FOLLOWUP_DECISION.md`."

This is that document. It says: **no follow-up *strategy* candidate
is justified at this time.** It does NOT say "stop CAMPAIGN_015
research forever"; it says "the next move is not a new strategy".

---

## 2 · Why no new strategy candidate is designed in this sprint

The Phase 5 [interpretation memo](CAMPAIGN_015_POST_RUN_INTERPRETATION.md)
labels the result `SPARSE_BUT_PROMISING` and recommends
**`COLLECT_MORE_DATA_FIRST`**, with `RUN_BACKTRADER_OR_NULL_FIRST` as
a hard precondition. Designing a new strategy candidate now would be
premature for three concrete reasons:

1. **The Backtrader secondary lane is BLOCKED on `DATA_MISMATCH`.**
   See [BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON.md](BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON.md).
   All 7 CAMPAIGN_002 H4 CSVs have sha-drifted from their committed
   provenance JSONs. Until that is fixed and BT corroborates the
   bespoke +0.230 R aggregate expectancy, every CAMPAIGN_015 number
   is a single-engine claim. Building a new candidate on a
   single-engine claim is the kind of thing the secondary lane
   exists to prevent.

2. **Sparsity is the dominant failure mode** ([Phase 1](CAMPAIGN_015_GATE_FAILURE_AUTOPSY.md)).
   The fix for sparsity is more data, not a new strategy. Designing
   a new strategy candidate to "be less sparse" is a strategy-design
   shortcut that side-steps the data question — and once a redesigned
   strategy trades more often, the original CAMPAIGN_015 hypothesis
   ("failed range-extreme sweeps fade") becomes mixed with whatever
   the new gate adds, making it impossible to isolate the original
   edge.

3. **Per-pair concentration in USD_CHF is real on the net-R view**
   ([Phase 2](CAMPAIGN_015_CONCENTRATION_DIAGNOSTICS.md)). Until an
   extended-universe re-run shows whether USD_CHF's outsized share
   (54.5% of total R) is structural (a property of CHF crosses being
   more prone to failed sweeps) or sample-specific (this particular
   4-year window), a candidate design that either embraces or
   discounts USD_CHF would be designed on noise.

---

## 3 · What this is NOT

- **Not a STOP_C015 decision.** The diagnostics affirmatively
  preserve CAMPAIGN_015 as research-only with a real-looking per-trade
  edge above the matched null (Phase 3 t=+3.19, label `ROBUST_ABOVE_NULL`).
- **Not an approval-track signal.** Approval requires a fresh
  pre-committed campaign on a clean candidate AND a human registry
  edit. Neither exists here.
- **Not a constraint on future sprints.** A future infra sprint that
  unblocks BT and extends the data universe is free to make a
  different decision based on the new evidence.

---

## 4 · What the next sprint(s) should look like (sketch only)

These are *not* commitments and *not* candidate designs; they are
notes for whoever picks up this thread:

1. **Infra sprint A — restore Lean-parity CSV provenance lock-step.**
   Re-export the 7 CAMPAIGN_002 H4 CSVs via
   `scripts/export_lean_parity_data.py` and re-commit the matching
   `*.provenance.json` sidecars in lock-step. Verify
   `python scripts/run_backtrader_parity.py --campaign CAMPAIGN_015 --dry-run`
   completes cleanly. Run the BT lane and compare to the rehydrate
   artifact under `research/campaign_015/diagnostics/walk_forward_rehydrate/`.
2. **Infra sprint B — extend the H4 universe.** Add as many years
   back of OANDA-practice H4 data as the data store supports. Re-run
   the existing CAMPAIGN_015 walk-forward (no parameter changes; the
   `config_hash` must match `17ddfd7e…`) on the extended universe.
   Per-fold trade counts ought to roughly double if the per-trade
   firing-rate is stable.
3. **Decision sprint.** If sprints A + B both succeed and the
   extended-universe expectancy R remains positive and the per-pair
   distribution becomes less USD_CHF-concentrated, **then** Phase 6
   of a *new* diagnostic sprint can write a real, justified follow-up
   candidate design. Until then, none.

---

## 5 · Safety invariants

- `configs/approved_strategies.yaml` is `approved: []`.
- Paper / demo / live loops refuse to start.
- No CAMPAIGN_015 parameter was changed in this sprint.
- No new strategy module was added in this sprint.
- No prior campaign evidence was modified.
- No broker call, no `.env`, no live OANDA.
