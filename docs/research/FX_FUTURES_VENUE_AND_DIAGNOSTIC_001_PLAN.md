# FX Futures Venue & Diagnostic — PLAN (Phase 0: Baseline Audit)

**Sprint:** `research-fx-futures-venue-and-diagnostic-001`
**Type:** Infrastructure, data, and diagnostic *research design* only. **Zero code. No strategy, no campaign, no front gate, no train/validation/test.**
**Date:** 2026-05-31
**Freeze:** must remain intact. Paper/demo/live remain blocked.

---

## Why this sprint exists

The Programme-Direction-After-Carry sprint selected **Option C: pivot from retail spot FX research to FX futures venue evaluation.** The reasoning, established across the whole programme, is that the dominant failure mode is **transaction economics, not absence of market structure.** Genuine structures were repeatedly found and then erased by cost.

This sprint asks one narrow, decision-forcing question: **is FX futures a credible venue in which to re-test the programme's already-frozen real-but-weak structures — and is such a diagnostic realistically executable from free/local data and defensible cost assumptions?**

It produces a **viability verdict and a design**, not a diagnostic run. The diagnostic itself (if it happens) is the *next* sprint.

---

## Baseline audit — what the prior evidence actually says

### Programme Direction After Carry / Final Decision
- In-repo spot-FX factor search is **exhausted**; every shortlisted family has a verdict; none produced a tradable edge.
- Dominant terminal cause is **cost**, not idea quality.
- Decision: build the FX-futures venue and run a read-only survival diagnostic on frozen C1 / S4 / TSMOM effects; **archive (Option E) is the pre-committed fallback** if the cost wall holds in futures.
- Futures is the *only* remaining mechanism that **changes the cost structure** (no nightly financing leg, tighter spreads, decades of history) rather than relabeling it.

### Evidence Inventory
- **rejected** (9): C001–C023, C025, C027, C028, S2, S3, H16, H03.
- **failed replication** (1): C1 on non-USD crosses → C1_ARTIFACT.
- **real but weak** (3): C1, S4, carry.
- **cost-defeated** (4): C026, C029, C031 (+ C1 secondary).
- No approved strategy or campaign, ever.

### S4 — cross triangular relative-value (the programme's only genuine factor)
- Verdict **FACTOR_REAL_BUT_WEAK**: stretched triangular no-arbitrage residuals revert hard (P 0.94–0.96, ~80% closed, all 8 relationships, stable across years/sessions); 20/20 null cells clear → a genuine no-arb property.
- **But confined to the no-arb band:** ~0.5 bp reversion vs ~5 bp retail cost band ≈ **10× inside cost**. ~78% reverts within 5 min; several relationships have half-life ≤ 1 bar (staleness-bound).
- Shared-leg cointegration spreads do **not** revert (half-life 7k–27k bars).
- **Relevance to futures:** a tighter cost band is the *only* thing that could move S4 from "real" to "marginally tradable." This is the single most futures-sensitive structure in the programme — but note the staleness/latency constraint (sub-5-min, ≤1-bar half-lives) is **independent of venue** and will not improve with futures.

### Carry — gross cross-sectional carry premium
- Verdict **FACTOR_REAL_BUT_WEAK**: premium exists (+0.74%/qtr) but is **mechanical accrual** (spot-predictive leg statistically zero), **single-name** (drop-JPY → ≈0), untimed (fails shuffled-timestamp null), and **financing-defeated by construction** (the gross premium *is* the accrual a broker reclaims as financing).
- **Relevance to futures:** futures carry is expressed in the **basis/roll**, not a nightly financing debit. This is the structurally cleanest reason to re-examine carry — but the spot-predictive leg being *zero* means futures cannot create predictability that the factor never had. Futures changes *how carry is paid/earned*, not whether carry *forecasts spot*.

### C1 — MTF confluence fade
- Genuine on USD majors, **cost-defeated** net of cost; **failed to replicate** on non-USD crosses (→ artifact).
- **Relevance to futures:** the genuine USD-major effect could get a fairer cost test; but the cross-replication failure means breadth claims do not carry over.

---

## The honest prior on this sprint's outcome

Futures plausibly **narrows** the cost wall (tighter spreads, no nightly financing) and **deepens history** (decades vs ~6.4 y). But three constraints are **venue-independent** and already known:
1. S4's edge is sub-5-min and staleness/latency-bound — a tighter spread helps the *size* comparison but not the *speed* problem, and CME FX futures are not where sub-bp triangular arbitrage lives (that is an HFT/colocation game).
2. Carry's spot-predictive content is *zero* — futures cannot manufacture it.
3. C1 did not replicate out-of-universe.

So the realistic best case is **VIABLE_WITH_LIMITATIONS**: a meaningful *gross-vs-net survival* diagnostic is constructible and worth running as the programme's final falsification, but it is unlikely to resurrect a tradable edge, and it must be framed as a *closeout-quality test*, not a revival attempt.

---

## What this sprint will produce (documents only)

| Phase | Doc | Question answered |
|-------|-----|-------------------|
| 0 | `FX_FUTURES_VENUE_AND_DIAGNOSTIC_001_PLAN.md` | What are we doing and why (this doc) |
| 1 | `FX_FUTURES_UNIVERSE_DESIGN.md` | Which CME contracts, mappings, tick/point values, roll/continuous methodology |
| 2 | `FX_FUTURES_DATA_SOURCE_FEASIBILITY.md` | Can we get the data free/local, with what coverage/licensing |
| 3 | `FX_FUTURES_COST_MODEL.md` | Research-only cost assumptions (spread, commission, roll, financing, slippage) |
| 4 | `FX_FUTURES_DIAGNOSTIC_FRAMEWORK.md` | How frozen C1/S4/carry would be evaluated **without altering definitions** |
| 5 | `FX_FUTURES_VIABILITY_DECISION.md` | NOT_VIABLE / VIABLE_WITH_LIMITATIONS / READY_FOR_DIAGNOSTIC |
| 6 | `NEXT_PROMPT_AFTER_FX_FUTURES_VENUE_AND_DIAGNOSTIC.md` | The exact next prompt (diagnostic OR archive) |
| 7 | `FX_FUTURES_VENUE_AND_DIAGNOSTIC_001_SUMMARY.md` | Validation + summary |

---

## Hard constraints (binding, restated)

- Do NOT create CAMPAIGN_032 or any campaign.
- Do NOT create trading logic, entry/exit rules, or a strategy.
- Do NOT approve any strategy; paper/demo/live stay blocked.
- Do NOT alter prior factor definitions; do NOT retune C1, S4, carry, or any rejected factor.
- Keep the research freeze intact. This sprint writes **docs only** — no code, no data ingestion (data feasibility is *assessed*, not executed).

## Method

Grounded in the existing evidence corpus (decision doc, evidence inventory, S4 validation, carry verdict, alternative-market comparison) plus general, well-established CME contract specifications and public-data availability. No broker API is called; no futures data is ingested in this sprint. Where a claim depends on a vendor detail that should be re-confirmed at ingestion time, it is flagged as an assumption.
