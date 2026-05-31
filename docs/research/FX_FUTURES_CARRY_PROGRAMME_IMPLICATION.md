# FX Futures Carry — Programme Implication (Phase 6)

**Sprint:** `research-fx-futures-carry-diagnostic-001` · Phase 6
**Type:** Programme-level interpretation of a decision-forcing verdict. Docs only.
**Date:** 2026-05-31
**Verdict carried in:** `CARRY_DOES_NOT_SURVIVE_IN_FUTURES`.

---

## 1. What just happened

Carry was the **last remaining high-information experiment** in the forex research programme. The programme-direction decision selected the FX-futures pivot precisely because futures is the one venue that **removes the nightly financing wall** — the cost that defeated C031 and made spot carry untradable. The hypothesis under test was binary:

- **(a) carry was merely financing-defeated** → it might survive a fair, financing-free venue; or
- **(b) carry is genuinely non-predictive** → it stays null even with the financing wall gone.

The diagnostic answers **(b)**. On real CME FX-futures price returns: the matched 5-year (incl-JPY) carry factor is **statistically zero** (h3 +0.04 %/qtr, t = +0.09, all null Z ≤ 0.21), and the 24-year ex-JPY run is **negative and below every null**. Removing the financing penalty also removed the accrual benefit (they are the same rate differential), and nothing predictive remained — the futures total matched the spot study's predictive leg (≈0) almost exactly.

## 2. Why this is the end of the in-repo strategy search

This was not "one more rejected idea." It was the **designated tie-breaker** for the programme's root-cause question: *is our recurring failure cost, or idea quality?* The evidence inventory showed every family failing with cost as the proximate killer. The natural hope was that a better cost structure (futures) would let a real-but-cost-defeated effect through.

The futures carry diagnostic tested that hope on the single most futures-favourable factor and found: **even in a fair venue, the predictive effect is simply not there.** That converts the programme's conclusion from the hopeful "cost-defeated (maybe fixable with a better venue)" to the decisive **"idea quality / market efficiency is the binding limit, not just retail cost."**

Combined with the prior verdicts:
- C1 — genuine on USD majors, **failed cross replication** (artifact).
- S2 — **rejected** (no predictive content).
- S4 — real but **economically insignificant** (sub-cost no-arb band; staleness-bound, venue-independent).
- Carry — real-but-weak in spot, now **non-predictive in futures**.

…there is **no remaining untested mechanism** that (a) is reachable with available data and (b) attacks the binding constraint. Futures was that mechanism; it has now been run.

## 3. Should the strategy search be archived?

**Yes.** This is the pre-committed Option E from the programme-direction decision, and the trigger condition (carry non-predictive in futures) has been met. The honest, evidence-based position:

> The in-repo forex strategy search is **exhausted**. Every shortlisted mechanism has a verdict; the one venue change that could have rescued a real-but-cost-defeated effect (futures, removing the financing wall) was executed and the strongest candidate (carry) is non-predictive even there. Continuing to mine the same corpus/mechanisms would repeat known failures.

Archiving is **not** a claim that no FX edge exists anywhere — it is a statement that *this programme, on this data and these mechanisms, has reached the end of its information*, and that further work requires a genuinely new input (new market, new data class, or new external thesis), not another pass over the same ground.

## 4. What archiving means concretely

- **Freeze the platform as a reusable research asset.** The lab (null benchmarks, multiple-comparison, cost-feasibility), the cross/futures ingestion, the carry/rate data, and the non-time-bar builders all remain — mature and documented.
- **Record strict restart criteria** (Phase 7 next prompt): only a *new market*, a *new data class* (true tick/L2, multi-decade fundamentals, positioning), or a *new external thesis* justifies reopening — **never** a re-tune of a closed family.
- **No strategy, campaign, approval, or live enablement.** Paper/demo/live stay blocked.

## 5. What is explicitly NOT concluded

- Not "futures are untradeable" in general — only that *this carry construction* shows no predictive price content.
- Not "the infrastructure was wasted" — it produced clean, decision-forcing verdicts; that is the point of a research platform.
- Not "carry is not a risk premium" — it is; it is simply realized through the rate differential (basis), which is not a predictable, tradable price edge net of how the venue pays it.

## 6. Recommendation

Proceed to the **archive / closeout sprint** (drafted in `NEXT_PROMPT_AFTER_FX_FUTURES_CARRY_DIAGNOSTIC.md`): write the programme post-mortem, codify restart criteria, and freeze the platform. The forex strategy search concludes here, on evidence, with integrity.
