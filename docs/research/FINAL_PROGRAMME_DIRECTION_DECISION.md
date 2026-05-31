# Final Programme Direction Decision (Phase 4)

**Sprint:** `research-programme-direction-after-carry-001`
**Type:** Documentation only. No strategy, no campaign, no approval.
**Date:** 2026-05-31
**Freeze:** intact. Paper/demo/live remain blocked.

---

## Decision

**Option C — Pivot to FX futures (CME), as a data + infrastructure + diagnostic sprint, NOT a campaign.**

The next sprint re-platforms the research lab onto exchange-traded FX futures: ingest continuous futures data, build a futures cost/roll model, and run a **read-only diagnostic** that re-tests the programme's already-identified genuine effects (C1-style MTF confluence fade, S4 triangular relative-value reversion, and time-series momentum) under the futures cost structure. It is decision-forcing and produces no strategy, campaign, or approval.

**Pre-committed fallback:** if the futures diagnostic shows the same cost wall holds (genuine effects remain net-negative after the futures cost/roll model), the programme moves to **Option E — Archive strategy search**, with a clean, evidence-based conclusion that this style of edge does not survive cost in liquid FX, spot or futures.

---

## Why C, and why now

### 1. It is the only remaining move that attacks the binding constraint

The entire programme's terminal cause is **cost**, established across C026, C029, C031, C1, S4, and carry. Every other option either relabels the same cost wall (A: same corpus; B: same crowded spot market) or starts a new project before exhausting the cheap experiment (D). Futures is the **single mechanism** (per Phase 2) that structurally changes the cost equation:

- **No nightly financing leg** — the ≈4× spread-cost financing squeeze that defeated C031 and made carry untradable is *absent*; futures carry is in the basis/roll, paid at roll, not bled nightly.
- **Tighter effective spreads** — centralized order book vs OTC two-sided retail spread.
- **Deep history (decades)** — fixes the ~6.4y slow-signal power limit that weakened momentum/carry tests.
- **Real exchange volume** — not the tick-count proxy the spot corpus relied on.

### 2. It is decision-forcing either way

This is the decisive test of the programme's open question: *were the edges real but the cost structure wrong, or were the edges never big enough?*

- If genuine effects (C1, S4, TSMOM) **survive** the futures cost/roll model → a real, fair lane finally opens, and the programme has a justified reason to continue.
- If they **do not survive** → the effects were simply too small, full stop, and the programme archives with a complete, honest conclusion (spot *and* futures both cost-defeated).

There is no ambiguous outcome. That is exactly what a terminal decision sprint should set up.

### 3. It reuses the mature platform

The factor lab, matched-null/multiple-comparison/cost-feasibility gates, the cost-model framework, and the non-time-bar builders all transfer. Only an additive instrument registry, ingestion, and a futures cost/roll model are new — the **same additive pattern the cross-expansion sprint already proved works** (majors untouched, new market bolted on). High infra leverage, moderate cost.

### 4. It does not repeat prior failures or revive rejected ideas

Re-testing C1/S4/TSMOM **in a structurally different cost regime is not a re-tune** — it is the same falsification discipline applied to a new venue. No closed family is reopened on the spot corpus; no rejected idea is revived; no parameters are re-fit to chase a result. The thresholds and effects are taken as-found from the existing verdicts.

### 5. Scoring backs it

Phase 3 scored C at 17/20 — tied with Archive (E) but winning on the criterion that matters most for a research programme: **expected information gain (5/5).** The decision rule is explicit: *do not archive while a cheap, high-information, never-run experiment that attacks the binding constraint remains.* Futures is that experiment.

---

## Why not the others

- **A (continue same corpus):** the in-repo search is exhausted; the corpus-viability gate already says continue only with a new external thesis. Near-zero information.
- **B (new spot-FX datasets):** expensive (paid tick/L2 feeds, latency modeling) and still the same crowded spot market with the same financing leg. Value strategies would be maximally financing-exposed — the exact wall that killed carry.
- **D (another market):** premature. It throws away FX domain knowledge and is effectively a new project. It becomes the live question *only if* futures also fails.
- **E (archive):** correct *eventually*, but archiving now would conclude the programme with a cheap, decisive, never-run experiment still on the table. Archive is the pre-committed fallback, not the present step.

---

## Scope guardrails for the next sprint (binding)

The futures sprint is **data + infrastructure + read-only diagnostic only**. It must:

- NOT create a campaign (no CAMPAIGN_032 or any number).
- NOT build trading logic or an executable strategy.
- NOT approve anything; paper/demo/live stay blocked.
- NOT re-tune or revive any closed spot-FX family.
- Treat existing C1/S4/TSMOM effect definitions as **frozen and as-found** — the diagnostic measures whether they survive futures cost, it does not search for new ones.
- Keep the research freeze intact; majors/crosses code untouched (additive only).
- Honestly document data limitations (continuous-contract roll method, basis assumptions, vendor) and present **no futures result as an edge** — only as a gross/net survival diagnostic.

The decision: **build the futures venue and run the survival diagnostic. Let that one experiment decide whether the programme continues or archives.**
