# Programme Direction After Carry — PLAN (Phase 0: Truth Audit)

**Sprint:** `research-programme-direction-after-carry-001`
**Type:** Documentation and strategic analysis only. **Zero code. No strategy, no campaign, no factor screen, no front gate.**
**Date:** 2026-05-31
**Freeze:** must remain intact.

---

## Why this sprint exists

The carry factor-validation sprint resolved the **last in-repo-testable mechanism** on the shortlist. Its verdict was **FACTOR_REAL_BUT_WEAK**: a carry premium exists, but it is mechanical accrual rather than spot predictability, single-name (collapses to ≈0 without JPY), untimed, and financing-defeated by construction. Carry does not justify a strategy programme, and financing-aware carry research is not currently justified.

With carry resolved, **every shortlisted factor family has been run to a verdict** and the in-repo factor search is complete. The programme is at a genuine fork: continue, re-arm with new data, pivot markets, or archive. This sprint exists to make that decision **once, on the evidence**, rather than spawning another speculative campaign.

---

## Hard constraints (restated and binding)

- Do NOT create CAMPAIGN_032 or any campaign.
- Do NOT perform factor discovery or factor validation.
- Do NOT build trading logic.
- Do NOT approve any strategy.
- Do NOT enable paper/demo/live.
- Do NOT revive rejected ideas.

This is a **decision sprint**. The only artifacts are documents.

---

## Truth audit — what is actually true about the programme

This is the honest, un-spun state of the programme as of 2026-05-31.

### What has been completed (run to a verdict)

| Area | Outcome |
|------|---------|
| Major-pair strategy research (C001–C031) | No approved strategy |
| MTF confluence research (C1 family) | Factor genuine, cost-defeated |
| Non-time-bar research (range/vol bars) | Infra built; no edge |
| H16 overshoot-exhaustion front gate | FAIL |
| H03 thin-move front gate | FAIL → directional non-time-bar search retired |
| C1 factor validation | Genuine factor, cost-defeated |
| C1 cross replication | REPLICATION_FAILED (→ artifact) |
| S2 currency-strength validation | REJECTED |
| S4 cross relative-value validation | REAL_BUT_WEAK (no-arb band, sub-cost) |
| Cross-universe expansion | Breadth added; cost wall unmoved |
| Carry validation | REAL_BUT_WEAK |

### The bottom line

- **No approved strategy.**
- **No approved campaign.**
- **No front-gate success.**
- **Paper/demo/live remain blocked.**

### The single most important finding of the whole programme

The dominant failure mode is **cost, not idea quality.** Across every family — directional, microstructure, mean-reversion, breakout, momentum, carry, relative-value — the recurring pattern is: a real or plausible effect exists *gross*, but it is smaller than the round-trip cost of crossing the two-sided spread (plus, for held positions, financing ≈4× spread cost). The cost wall is **structural to the corpus**, not specific to any one idea. Widening the universe to non-USD crosses did not move it. The research platform was never the bottleneck.

---

## What this sprint will produce

1. **Phase 0** — this plan (truth audit).
2. **Phase 1** — `FINAL_FOREX_PROGRAMME_EVIDENCE_INVENTORY.md`: every major effort classified (rejected / failed-replication / real-but-weak / cost-defeated / infrastructure-only).
3. **Phase 2** — `REMAINING_UNTESTED_MECHANISMS_AFTER_CARRY.md`: what genuinely remains untested (broker-financing realism, futures FX, institutional-cost venues, alternative datasets, alternative asset classes).
4. **Phase 3** — `POST_CARRY_STRATEGIC_OPTIONS.md`: options A–E scored on information gain, implementation cost, likelihood of repeating prior failures, infra compatibility.
5. **Phase 4** — `FINAL_PROGRAMME_DIRECTION_DECISION.md`: exactly one path, with justification.
6. **Phase 5** — `NEXT_PROMPT_AFTER_PROGRAMME_DIRECTION_DECISION.md`: the actual next coding-agent prompt.
7. **Phase 6** — validation run + `PROGRAMME_DIRECTION_AFTER_CARRY_SUMMARY.md`.

---

## Method

Grounded in the existing evidence corpus (memory index + `docs/research/` synthesis docs: corpus viability, cross-factor synthesis, carry validation, alternative-market comparison, carry remaining-mechanisms). No new data is read; no code is run except the Phase 6 validation gates. Conclusions must follow from evidence already on disk, not from hope.
