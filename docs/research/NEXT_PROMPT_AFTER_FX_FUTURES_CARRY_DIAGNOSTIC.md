# Next Prompt After FX Futures Carry Diagnostic (Phase 7)

**Sprint:** `research-fx-futures-carry-diagnostic-001` · Phase 7
**Type:** Documentation only.
**Date:** 2026-05-31
**Verdict carried in:** `CARRY_DOES_NOT_SURVIVE_IN_FUTURES` → carry fails → draft the **archive / closeout sprint**.

---

## Why this is the archive prompt

The diagnostic resolved the programme's final open question: carry is **genuinely non-predictive**, not merely financing-defeated. Futures — the one venue that removes the financing wall — was the pre-committed last experiment, and the strongest candidate failed it (futures carry price return statistically zero, t = 0.09, indistinguishable from every null; 24-year ex-JPY run negative and below every null). Per the programme-direction decision, the triggered path is **Option E: archive the strategy search.** The next sprint is a docs-only closeout, not another factor study.

## Operator notes

- Documentation-only sprint: post-mortem + restart criteria + platform freeze. No code, no data, no factor work.
- Must not reopen any closed family or soften the freeze.
- Grep that any identifier is unused before assigning.

---

## The prompt

> We are starting the forex strategy-search archive / closeout sprint from clean, updated origin/main.
>
> **Branch:**
>
> `research-forex-strategy-search-archive-001`
>
> **Context:**
>
> The FX-futures carry diagnostic returned `CARRY_DOES_NOT_SURVIVE_IN_FUTURES`: the frozen carry factor on real CME FX-futures price returns is statistically zero (primary 3-month +0.04 %/qtr, t = 0.09) and indistinguishable from every null in the matched 5-year window, and negative/below-every-null over 24 years ex-JPY. Carry was the last remaining high-information experiment, and futures was the pre-committed venue that removes the financing wall. The result converts the programme's root cause from "cost-defeated (maybe fixable)" to "idea-quality / market-efficiency is the binding limit." Per the programme-direction decision, this triggers Option E: archive the strategy search.
>
> **Goal:**
>
> Produce the definitive, evidence-based closeout of the forex strategy-search programme: a post-mortem, strict restart criteria, and a platform freeze — preserving everything as a reusable research asset.
>
> **This sprint is documentation only.**
>
> Do not create a strategy. Do not create a campaign. Do not create a factor screen or front gate. Do not perform factor discovery or validation. Do not build trading logic. Do not approve any strategy. Do not enable paper/demo/live. Do not reopen or re-tune any closed/rejected factor.
>
> **Hard rules:**
>
> - Do not create CAMPAIGN_032 or any campaign.
> - Keep the research freeze intact; paper/demo/live stay blocked.
> - No code, no data ingestion — docs only.
>
> **PHASE 0 — baseline audit.** Review the full evidence chain: `FINAL_FOREX_PROGRAMME_EVIDENCE_INVENTORY.md`, `FINAL_PROGRAMME_DIRECTION_DECISION.md`, the FX-futures venue + carry-diagnostic docs (`FX_FUTURES_CARRY_VERDICT.md`, `FX_FUTURES_CARRY_PROGRAMME_IMPLICATION.md`). Create `docs/research/FOREX_STRATEGY_SEARCH_ARCHIVE_001_PLAN.md`. Commit.
>
> **PHASE 1 — programme post-mortem.** Create `docs/research/FOREX_PROGRAMME_POST_MORTEM.md`: the complete narrative (families attempted → verdicts → root cause), the decisive finding (idea-quality/efficiency, not just retail cost, is the binding limit, proven by the financing-free futures carry null), and the lessons (what the platform did well; where time was spent; the cost-wall taxonomy). Commit.
>
> **PHASE 2 — restart criteria.** Create `docs/research/FOREX_RESEARCH_RESTART_CRITERIA.md`: the *only* conditions that justify reopening — a new market, a new data class (true tick/L2, multi-decade fundamentals, positioning/flow, options-implied), or a new external thesis with an a-priori economic mechanism. Explicitly exclude re-tunes of closed families. Define the gate any restart must pass before any campaign. Commit.
>
> **PHASE 3 — platform freeze + asset inventory.** Create `docs/research/FOREX_PLATFORM_FROZEN_ASSET_INVENTORY.md`: catalogue the reusable assets (edge-discovery lab + gates, cross/futures ingestion, carry/rate data, non-time-bar builders, cost models) with pointers, so a future effort can reuse rather than rebuild. Confirm the freeze and blocked execution. Commit.
>
> **PHASE 4 — validation.** Run: pytest tests/ -q; ruff check src scripts tests; python scripts/check_research_freeze.py; python scripts/validate_research_archive.py; python scripts/scan_artifacts_for_secrets.py; git status --short. Create `docs/research/FOREX_STRATEGY_SEARCH_ARCHIVE_001_SUMMARY.md`.
>
> **Final response must include:** branch; commit hashes by phase; the post-mortem's root-cause conclusion; restart criteria; frozen-asset inventory; whether any campaign was created (expected: no); whether any strategy was approved (expected: no); whether paper/demo/live remain blocked (expected: yes); files to review first.
>
> **Success criteria:** conclude the forex strategy search with a complete, honest, evidence-based archive that preserves the platform and sets a high bar for any restart. Do not create a strategy. Do not create a campaign. Do not attempt to trade.

---

## If, instead, the operator wants to keep going (not recommended on this evidence)

The only defensible non-archive move is to acquire a **genuinely new input** before any further factor work — e.g. a true tick/L2 FX dataset (unlocks the microstructure lane that S4/H16/H03 could only proxy), multi-decade fundamentals (enables FX value, a different mechanism from carry/momentum), or positioning/flow data. That would be a **data-acquisition** sprint, not a campaign, and it must still pass the restart gate. Absent such a new input, archiving is the evidence-based choice.
