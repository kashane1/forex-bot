# Next Factor-Discovery Direction

**Sprint:** `research-nonusd-cross-factor-discovery-planning-001` · Phase 6
**Type:** single-direction decision. Docs-only. **No factor, no screen, no
campaign, no approval.** This chooses *what to look at next*, nothing more.
**Date:** 2026-05-30.

---

## Decision

# Chosen direction: **S1 — Independent C1 replication on non-USD crosses** (family F24)

The next factor-discovery sprint will run a **fresh, pre-registered, frozen-
threshold replication of the locked C1 factor** (fade simultaneous H4+H1+M15
bullish alignment → reverts down 30–60min) on the 8 populated non-USD crosses, to
answer one question: **is C1 a genuine multi-timeframe-confluence effect, or a
residual-USD-regime artifact?** Replication only — never a re-tune.

> This is a **direction**, not a factor and not a screen. No signal is built, no
> threshold is chosen here, no backtest is run. Phase 7 writes the prompt that
> would open the discovery sprint.

---

## Why S1 over S2–S5

Weighing the shortlist against the programme's actual situation:

1. **It answers the one open scientific question — cheaply.** C1 is the *only*
   GENUINE factor the programme ever produced, and the *only* loose end is whether
   its magnitude is real or a USD-regime artifact. Crosses were named — in the C1
   closeout, the non-time-bar retirement, and the corpus verdict — as the specific
   reopen condition to settle exactly this. Answering it requires **no new data**
   (materialized cross bars exist), **no new infrastructure** (the C1 validation
   runner and the lab's matched-null/cost modules exist), and **no parameter
   search** (the definition is frozen). It is the highest-information, lowest-cost
   move available — Phase-4's top-ranked family (4.31).

2. **It is the sanctioned reuse — and disciplines the whole cross lane.** Every
   other family (S2–S5) is net-new construction whose first risk is *building*
   something. S1 is the one closed lane we are explicitly permitted to revisit,
   and *only* as a replication. Running it first establishes the precedent that the
   cross lane reuses prior work as **replication, not re-tuning** — the exact
   discipline Phase 3 fences. It also produces a clean, citable result either way:
   a confirmed factor *or* a confirmed artifact.

3. **Its result gates the value of S2–S5.** If C1 replicates as a genuine
   non-USD confluence effect, that materially raises confidence that *other*
   multi-TF / breadth structure on crosses is worth mining (S2/S3 become more
   attractive). If C1 evaporates on non-collinear data, that is strong evidence the
   programme's "edges" are USD-regime shadows — a sobering, decision-relevant prior
   that would argue for pausing factor mining and pivoting to the **data
   prerequisites** (financing ingest for carry, or a different venue/history). Either
   outcome sharpens the next decision; S2–S5 do not have this gating property.

4. **It carries the least repeat-risk and the least overfitting surface.** Frozen
   definition + matched-null + cost-first + multiple-comparison over a fixed
   8-pair set = essentially no researcher degrees of freedom. S2–S4 all carry
   live best-of-N / forking-path risk that needs careful pre-registration; S5 is an
   overlay with nothing yet to overlay. Starting with the zero-DOF family is the
   conservative, freeze-respecting choice.

**Why not the others, briefly:**
- **S2 (currency-strength index)** is the most exciting *new* territory and the
  natural *second* sprint — but it requires building a decomposition utility and
  pre-registering a fresh specification, i.e. genuine construction and a larger
  overfitting surface. Better to do it once the C1 replication has established
  whether cross-confluence structure exists at all.
- **S3 (cross-sectional momentum)** depends on S2's foundation; out of order now.
- **S4 (cross RV)** reopens C028 legitimately but is the most cost-exposed
  (two-/three-leg) and should follow, not lead.
- **S5 (regime gate)** is an overlay with no generator to condition yet.
- **Carry (deliberately excluded)** is prerequisite-blocked on financing data.

---

## What this direction explicitly is and is not

**Is:** a scoped intent to *re-screen one frozen factor on independent data* in a
future sprint, to settle the residual-USD question.

**Is not:** a factor (the definition already exists and is locked); a screen (none
is run here); a campaign (forbidden); a strategy (none); an approval (none); a
re-tune (the definition cannot change); a tradability claim (a positive
net-of-cost result is *not* expected — cross spreads are wider; the value is
scientific).

## Pre-stated stop / outcome criteria for the eventual S1 sprint

Defined now so the discovery work cannot drift into open-ended mining:

- **`C1_ARTIFACT`** — if C1's signed reversion is within matched-null on the
  crosses (no sign replication, no significant magnitude) → C1 was a USD-regime
  artifact. The M1/HTF confluence lane stays closed; the cross factor programme
  pivots to data prerequisites or S2 with lowered priors.
- **`C1_GENUINE_BUT_COST_DEFEATED`** — if C1 sign-replicates and beats the
  matched null on crosses but is **net-of-cost negative** (the expected outcome
  given wider cross spreads) → C1 is confirmed a genuine factor and a confirmed
  non-tradable. Lane stays closed for *trading*; confidence in cross multi-TF
  structure rises, making S2/S3 the next target.
- **`C1_GENUINE_AND_COST_SURVIVING`** — if C1 replicates *and* survives
  net-of-cost on ≥2 non-collinear crosses at a cost-stress multiple (not
  expected) → it earns *consideration* for a Stage-4 pre-registered campaign in a
  **separate, later** sprint with human review. Even then, **no campaign is
  created without a fresh pre-commit and approval.**

In all three branches: **no campaign, no strategy, no approval** is produced by
the discovery sprint itself. The discovery sprint produces *evidence and a
verdict*, exactly as the C1, H16, and H03 screens did.
