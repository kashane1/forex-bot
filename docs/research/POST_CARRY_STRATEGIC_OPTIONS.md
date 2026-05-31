# Post-Carry Strategic Options (Phase 3)

**Sprint:** `research-programme-direction-after-carry-001`
**Type:** Documentation only.
**Date:** 2026-05-31
**Purpose:** Score the five strategic options against four criteria, as input to the single direction decision in Phase 4.

---

## The five options

- **A. Continue forex research** — keep searching the existing spot-FX corpus (majors + crosses) for new factors/strategies.
- **B. Continue only with new external datasets** — stay in spot FX but re-arm with data the corpus lacks (tick/L2, multi-decade history, positioning, options-implied).
- **C. Pivot to futures** — re-platform onto FX futures (CME), reusing infrastructure and known effects under a better cost structure.
- **D. Pivot to another market** — leave FX for crypto / equities-ETFs / metals.
- **E. Archive strategy search** — formally conclude the strategy hunt; keep the platform as a frozen research asset.

---

## Scoring criteria (1 = poor, 5 = excellent)

1. **Expected information gain** — how much genuinely new, decision-relevant knowledge does this produce?
2. **Implementation cost** — *inverted so higher = cheaper*: how cheap/fast is it to run the next meaningful step?
3. **Avoids repeating prior failures** — *higher = less likely to re-hit the same cost wall / re-tune a closed family.*
4. **Infra compatibility** — how much of the existing platform (lab, null benchmarks, cost models, non-time bars, ingestion) carries over?

---

## Scores

| Option | Info gain | Cheapness | Avoids repeat-failure | Infra compat | **Total /20** |
|--------|:--------:|:---------:|:---------------------:|:------------:|:-------------:|
| A. Continue forex (same corpus) | 1 | 4 | 1 | 5 | **11** |
| B. New external datasets (still FX) | 3 | 2 | 3 | 4 | **12** |
| **C. Pivot to futures (CME)** | **5** | **3** | **5** | **4** | **17** |
| D. Pivot to another market | 4 | 1 | 4 | 2 | **11** |
| E. Archive strategy search | 2 | 5 | 5 | 5 | **17** |

---

## Per-option reasoning

### A. Continue forex research — 11
- **Info gain (1):** the in-repo factor search is *exhausted*. Every shortlisted family has a verdict. Continuing means either re-tuning closed families (forbidden, low-information) or inventing speculative variants with no external thesis — which the corpus-viability review already ruled out (CONTINUE_ONLY_WITH_NEW_EXTERNAL_THESIS).
- **Cheapness (4):** cheap to attempt, but cheapness of a near-zero-information action is not a virtue.
- **Avoids repeat-failure (1):** it *is* the prior failure. Same corpus, same cost wall.
- **Infra (5):** fully compatible.
- **Verdict:** low-value. Rejected by the existing viability gate.

### B. New external datasets (still FX) — 12
- **Info gain (3):** tick/L2 or multi-decade history could open genuinely new mechanisms (microstructure, value). Real but uncertain.
- **Cheapness (2):** requires paid data feeds/subscriptions, new ingestion, and (for L2) latency-aware backtesting the platform doesn't model. Expensive and slow.
- **Avoids repeat-failure (3):** lower spreads/new info *might* clear the cost wall, but it's still the same crowded spot market; value strategies are slow → maximally financing-exposed (the wall that killed carry).
- **Infra (4):** mostly compatible; needs new data adapters and possibly a latency model.
- **Verdict:** plausible but costly and partly redundant with the cost wall.

### C. Pivot to futures (CME) — 17  ← top
- **Info gain (5):** highest. It is the only near-term step that tests the programme's central hypothesis — *is the edge real but the cost structure wrong?* Futures remove the nightly financing leg and tighten effective spreads, so any known-real-but-cost-defeated effect (C1 confluence, S4 relative-value, momentum) gets its first fair test. Deep history also fixes the slow-signal power limit. Either result is decisive: edges survive (→ a real lane opens) or they don't (→ the effects were never big enough, full stop).
- **Cheapness (3):** moderate. Needs new ingestion + a futures cost/roll model, but **no live account, no paid retail-vs-institutional gap, no latency model** — continuous futures data is broadly available and the existing lab/null/cost-model scaffolding ports directly.
- **Avoids repeat-failure (5):** highest. It deliberately attacks the *binding constraint* (cost) instead of relabeling it. It does not re-tune any closed family; it re-tests them in a structurally different cost regime.
- **Infra (4):** high. The factor lab, null benchmarks, multiple-comparison gates, cost-model framework, and non-time-bar builders all transfer; only the instrument registry, ingestion, and cost model need futures-specific additions (the cross-expansion sprint already proved this additive pattern works).
- **Verdict:** best information-per-dollar, and the only option that could actually change the programme's conclusion.

### D. Pivot to another market — 11
- **Info gain (4):** high in principle (crypto/equities are different regimes), but undirected — no specific thesis yet.
- **Cheapness (1):** lowest. New market = new everything (data, cost model, microstructure understanding, edge thesis). Effectively a new project.
- **Avoids repeat-failure (4):** different wall, but also throws away FX domain knowledge.
- **Infra (2):** low; only the generic lab scaffolding ports.
- **Verdict:** premature. If futures also fail, *this* becomes the live question.

### E. Archive strategy search — 17  ← tie on score, different role
- **Info gain (2):** archiving produces no new market knowledge, but it produces decisive *programme* knowledge: a clean, honest "we searched this corpus to exhaustion and it is cost-defeated."
- **Cheapness (5):** highest — docs only, no further compute.
- **Avoids repeat-failure (5):** by definition stops the repeat.
- **Infra (5):** preserves the platform frozen, fully reusable later.
- **Verdict:** the correct option **if and only if** there is no remaining cost-relevant mechanism. But Phase 2 found exactly one — futures — that has never been tested and that attacks the binding constraint. Archiving *before* testing futures would archive with a known, cheap, high-information experiment still on the table. Archiving is therefore the right *fallback*, not the right *now*.

---

## How to read the A=11 / C=17 / E=17 result

C and E tie on raw score, but they answer different questions:
- **E scores high because it is cheap and safe** — it wins on three "avoidance" criteria.
- **C scores high because it is the one move that could still change the answer** — it wins on the criterion that actually matters for a *research* programme: information gain.

The decision rule for a research programme is: **do not archive while a cheap, high-information, never-run experiment remains that attacks the binding constraint.** Futures is exactly that experiment. So the ordering is **C now → E if C fails.**

This is carried into the Phase 4 decision.
