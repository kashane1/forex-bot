# Next Market-Selection Decision

**Recommended next direction (exactly one):**
**Build a multi-market front-gate discovery lab (Phase-5 Option 6),
seeded with non-USD FX crosses (Option 3) as its first ingested
dataset.**

This is an **infrastructure + data** direction. It creates **no
campaign**, approves **no strategy**, runs **no train/validation/test**,
and changes nothing about the freeze. Paper/demo/live remain blocked;
the approved-strategy registry stays empty.

**Date:** 2026-05-29. Grounded in Phases 0–5 of this sprint.

---

## Why this direction

1. **It attacks the real bottleneck.** The bottleneck is no longer
   code or ideas — it is that the *one* search space we can cheaply
   reach (7 USD majors) is structurally cost-defeated and breadth-poor.
   The highest-leverage move is to make *new* search spaces cheap and
   methodologically uniform to evaluate, rather than to bet on a single
   new market blind.
2. **It is a force-multiplier with the lowest repeat-risk.** A
   multi-market generalization of the existing edge-discovery lab
   (matched-null + ablation + MCC + cost-feasibility) means every future
   instrument/asset class is screened the same disciplined way that
   correctly killed C027/C028 selection noise. It is the single best
   guard against repeating prior failures (Phase 5 repeat-risk 5/5).
3. **It builds on infrastructure that already works.** Parity, the null
   lab, M1 plumbing, and the cost model are sound. This direction
   *extends* proven infra; it does not start from zero.
4. **The seed data is the cheapest genuinely-new data we have.**
   Non-USD FX crosses ingest on the existing pipeline/cost model, break
   USD-leg crowding, and finally give the breadth families
   (cross-sectional, carry, relative-value) enough independent legs to
   be powered — the exact limitation C016/C028/C031 hit. Using crosses
   as the lab's first dataset validates the generalization on familiar
   ground before any expensive lane (futures, crypto, tick/L2).
5. **It is conservative.** It commits no money, no new venue, and no
   strategy. It produces *capability and evidence*, not orders — fully
   consistent with the freeze and with reframing the project as a
   market-research lab (Option 8).

## Why NOT continue current forex strategy search immediately

- Broad, undirected search on the 7 USD majors is **exhausted**; every
  family is cost-defeated or no-effect (Phase 1).
- The constraint is **structural cost** (Phase 2): a new idea on the
  same corpus hits the same two-sided squeeze and will fail the front
  gate, just like its predecessors.
- The Phase 3 decision (`CONTINUE_ONLY_WITH_NEW_EXTERNAL_THESIS`)
  already forbids re-tunes and undirected mining. Immediately launching
  another corpus strategy search would violate that decision and repeat
  known failures.
- The corpus best serves now as a **control/baseline**, not as the
  primary edge search space.

## What must be true for this direction to be worthwhile

- The generalized lab must keep the **full front-gate rigor** (matched
  null, ablation, multiple-comparison correction, cost-feasibility) for
  every instrument — no weakening to "find" something.
- Each new instrument must carry a **realistic, instrument-specific cost
  model** (crosses have wider spreads; do not silently reuse EUR_USD
  costs).
- Ingestion must be **lookahead-free and parity-checked** to the same
  standard as the current corpus (the dedup/contamination lesson holds).
- The lab must **report null/negative results honestly** — its value is
  a trustworthy gate, not a green light.
- It must remain **free/local** (crosses are same-broker free data); no
  paid data or broker calls in this step.

If any of these cannot be met, this direction is not yet worthwhile and
the fallback is Phase-5 Option 1 (pure infra/doc hardening) until they
can be.

## What the next coding-agent sprint should do

A single **infrastructure + data** sprint (no strategy, no campaign, no
screen run):

1. **Generalize the edge-discovery lab** into an instrument/asset-class
   -agnostic *multi-market front gate*: a uniform interface for
   ingesting an instrument, attaching its cost model, and running the
   existing null/ablation/MCC/cost-feasibility checks.
2. **Add a non-USD FX cross ingestion adapter** on the existing pipeline
   and ingest a small set (e.g., EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY)
   with **instrument-specific spreads/financing** and lookahead-free,
   parity-checked candles.
3. **Produce data-quality + cost diagnostics** for the new crosses
   (coverage, spread/financing realism, correlation to existing majors)
   — evidence only, no strategy evaluated.
4. **Do not** run a front-gate *screen* of any strategy, build a
   campaign, approve anything, or touch loops/executor/broker behavior.
   The screen of a specific thesis is a *later*, separately-gated sprint.

The deliverable is **capability + clean new data + diagnostics**, which
makes the *next* decision (which thesis/market to actually screen) cheap
and evidence-based — without prejudging it now.

## Status guarantees (unchanged)

- No campaign created; no strategy approved; no train/validation/test
  run; no broker/credential use; freeze intact; loops refuse.

Phase 7 turns this into the exact next coding-agent prompt.
