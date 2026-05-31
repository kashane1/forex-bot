# Programme Direction After Carry — SUMMARY (Phase 6)

**Sprint:** `research-programme-direction-after-carry-001`
**Type:** Documentation and strategic analysis only. Zero code (other than running validation gates).
**Status:** COMPLETE.
**Date:** 2026-05-31
**Freeze:** intact. Paper/demo/live remain blocked.

---

## What this sprint did

Made the **final, evidence-based programme-direction decision** after the carry factor validation (FACTOR_REAL_BUT_WEAK) resolved the last in-repo-testable mechanism. No strategy, campaign, factor screen, or front gate was created.

---

## Commit hashes by phase

| Phase | Hash | Artifact |
|-------|------|----------|
| 0 — truth audit plan | `16888ef` | `PROGRAMME_DIRECTION_AFTER_CARRY_PLAN.md` |
| 1 — evidence inventory | `504f82f` | `FINAL_FOREX_PROGRAMME_EVIDENCE_INVENTORY.md` |
| 2 — remaining mechanisms | `37e947e` | `REMAINING_UNTESTED_MECHANISMS_AFTER_CARRY.md` |
| 3 — strategic options | `c374656` | `POST_CARRY_STRATEGIC_OPTIONS.md` |
| 4 — decision | `068fcb6` | `FINAL_PROGRAMME_DIRECTION_DECISION.md` |
| 5 — next prompt | `05a336d` | `NEXT_PROMPT_AFTER_PROGRAMME_DIRECTION_DECISION.md` |
| 6 — summary | *(this commit)* | `PROGRAMME_DIRECTION_AFTER_CARRY_SUMMARY.md` |

---

## Evidence inventory summary

Every major effort classified. No effort ever reached "approved strategy."

- **rejected (9):** C001–C023 families, C025, C027, C028, S2, S3, H16, H03.
- **failed replication (1):** C1 on non-USD crosses (→ C1_ARTIFACT).
- **real but weak (3):** C1 (MTF confluence), S4 (triangular relative-value), carry.
- **cost-defeated (4):** C026 (timeframe ladder), C029 (range bars), C031 (vol-managed TSMOM); C1 secondary.
- **infrastructure-only (12+):** non-time bars, cross ingestion/population/planning, rate-data ingestion, cost models, lab, and all docs-only reviews.

**Central finding:** the dominant failure mode is **cost, not idea quality.** When an effect was real, cost killed it; when cost was survivable, the effect wasn't real. The cost wall is structural to the corpus and was not moved by widening the universe.

---

## Remaining untested mechanisms

Evaluated five (broker-financing realism, futures FX, institutional venues, alternative datasets, alternative asset classes). Only **one** is genuinely remaining, cost-relevant, and near-term testable:

- **FX futures (CME)** — the only mechanism that *changes the cost structure* (no nightly financing leg, tighter spreads, decades of history) rather than relabeling it.
- Broker-financing realism: **foreclosed by inference** (confirms a loss).
- Institutional ECN/L2 and alternative datasets: **gated behind unavailable data/access.**
- Alternative asset classes: **effectively a new project.**

---

## Strategic options evaluated (scored /20)

| Option | Total |
|--------|------:|
| A. Continue forex (same corpus) | 11 |
| B. New external datasets (still FX) | 12 |
| **C. Pivot to futures (CME)** | **17** |
| D. Pivot to another market | 11 |
| E. Archive strategy search | 17 |

C and E tied; C wins on the criterion that matters for a research programme — **expected information gain (5/5)** — and the decision rule: *do not archive while a cheap, high-information, never-run experiment that attacks the binding constraint remains.*

---

## Chosen direction

**Option C — Pivot to FX futures (CME)**, as a **data + infrastructure + read-only diagnostic** sprint (NOT a campaign). Re-test the frozen, as-found C1 / S4 / TSMOM effects under a futures cost/roll model. Decision-forcing:

- survive → a real lane opens; or
- fail → trigger the **pre-committed fallback, Option E (Archive)**, concluding spot *and* futures are both cost-defeated.

---

## Validation results (Phase 6)

| Check | Result |
|-------|--------|
| `pytest tests/ -q` | **2454 passed** in 39.32s |
| `ruff check src scripts tests` | 5 errors — **all pre-existing** (UP017 `datetime.UTC`) in `scripts/run_edge_discovery_vol_managed_tsmom.py` + `scripts/build_carry_rate_dataset.py`, both **untouched this sprint** (this sprint changed zero code). No new lint debt introduced. |
| `python scripts/check_research_freeze.py` | freeze intact (exit 0) |
| `python scripts/validate_research_archive.py` | archive valid (exit 0) |
| `python scripts/scan_artifacts_for_secrets.py` | no secrets (exit 0) |
| `git status --short` | clean |

---

## Compliance ledger

- **Campaign created?** No. (No CAMPAIGN_032; no campaign of any kind.)
- **Strategy approved?** No.
- **Factor discovery/validation performed?** No.
- **Trading logic built?** No.
- **Rejected ideas revived?** No.
- **Paper/demo/live?** Still blocked.
- **Freeze?** Intact.

---

## Recommended next sprint

`research-fx-futures-venue-and-diagnostic-001` — build the FX-futures instrument registry + cost/roll model, ingest deep continuous-contract history, and run the read-only survival diagnostic on the frozen C1/S4/TSMOM effects. Full drafted prompt in `NEXT_PROMPT_AFTER_PROGRAMME_DIRECTION_DECISION.md`.

---

## Files to review first

1. `FINAL_PROGRAMME_DIRECTION_DECISION.md` — the decision + justification.
2. `POST_CARRY_STRATEGIC_OPTIONS.md` — the scored options.
3. `REMAINING_UNTESTED_MECHANISMS_AFTER_CARRY.md` — why futures is the one live mechanism.
4. `FINAL_FOREX_PROGRAMME_EVIDENCE_INVENTORY.md` — the complete ledger.
5. `NEXT_PROMPT_AFTER_PROGRAMME_DIRECTION_DECISION.md` — the exact next prompt.
