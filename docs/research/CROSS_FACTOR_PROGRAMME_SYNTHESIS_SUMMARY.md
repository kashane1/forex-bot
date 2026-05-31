# Cross-Factor Programme Synthesis — Summary

**Branch:** `research-cross-factor-programme-synthesis-001`
**Type:** project-level synthesis & direction decision. **Docs-only.** No factor,
factor-validation, screen, front gate, campaign, strategy, or train/validation/test.
**Date:** 2026-05-30. **Freeze intact; nothing approved; paper/demo/live blocked.**

This sprint produced a rigorous synthesis of the entire expanded FX research
programme and chose the single highest-value remaining direction.

---

## 1. Branch

`research-cross-factor-programme-synthesis-001` (from clean `origin/main`).

## 2. Commit hashes by phase

| Phase | Hash | Deliverable |
|-------|------|-------------|
| 0 | `63d9cfe` | `CROSS_FACTOR_PROGRAMME_SYNTHESIS_PLAN.md` (truth audit) |
| 1 | `0c013c8` | `COMPLETE_PROGRAMME_EVIDENCE_INVENTORY.md` |
| 2 | `abe7741` | `PROGRAMME_LESSONS_LEARNED.md` |
| 3 | `5695ba5` | `REMAINING_UNTESTED_MECHANISMS.md` |
| 4 | `f0aa68f` | `NEXT_PROGRAMME_OPTIONS.md` |
| 5 | `d3bff16` | `NEXT_MAJOR_DIRECTION_DECISION.md` |
| 6 | `3f33804` | `NEXT_PROMPT_AFTER_PROGRAMME_SYNTHESIS.md` |
| 7 | _this commit_ | this summary + validation |

## 3. Files changed

8 new docs under `docs/research/` (all additions). **Zero code** — `git diff
--name-only origin/main...HEAD -- '*.py'` is empty. No config, registry, or executor
change.

## 4. Evidence inventory summary

Every major effort classified into six buckets:
- **Rejected (no effect / within-null):** C020–023 pullback, C016 cross-sectional
  momentum, C028 RV spread, H16, H03, **S2 currency strength**, **S3** (pre-falsified),
  S5, macro-regime context.
- **Failed replication:** **C1 cross replication (S1)** — the one genuine majors
  factor was a USD-regime artifact.
- **Real but weak:** **S4 cross relative-value** — the programme's **only genuine
  factor** (real no-arb reversion, ~10× inside the cost band).
- **Cost-defeated (gross effect, net-negative):** C015/017/025, C026, C008/C027,
  **C1 validation + front gate**, C029.
- **Financing-blocked:** **C031 vol-managed TSMOM** (financing ≈4× spread).
- **Infrastructure-only:** non-time-bar infra, cross ingestion/population, the
  edge-discovery lab + null/cost gates, parity/risk/financing models, FRED ingest.

**Cross-cutting:** the dominant failure mode is **cost, not idea quality** — where a
gross effect exists it is sub-spread; where cost is not the wall, the effect is
absent or a USD artifact. **Breadth was real but insufficient.** The platform is
**not** the bottleneck.

## 5. Lessons learned

**Wrong assumptions:** breadth would unlock an edge (it unlocked *structure*, still
sub-cost); C1's sign-universality implied generality (it was a USD artifact);
currency strength would predict (it persists, doesn't predict); related crosses
would cointegrate (only the no-arb triangle reverts); a better clock would surface
an edge (alt bars are sampling, not edge). **Correct assumptions:** the venue is
structurally cost-defeated; pre-registration + matched-null + cost gates are
essential; crosses add breadth not cost/history/microstructure; replication on
non-collinear data is decisive; the platform is sound. **Recurring patterns:**
cost-defeat of genuine gross effects; within-null prediction; USD-regime artifacts;
best-of-N selection noise; microstructure mistaken for reversion; a spread wall
(fast) + financing wall (slow); ~5y / tick-proxy / no-real-rate / single-venue data
limits.

## 6. Remaining untested mechanisms

**Carry (interest-rate differential)** — genuinely new return source, **data-blocked
all programme**, now nearly testable in-repo (real carry pairs exist; real rates not
yet ingested). Also untested: financing-as-data (the enabler), lower-cost/
institutional venue, true tick/L2, futures, metals/crypto/equities, longer history,
sentiment data. **Carry is the only one that is both a genuinely new mechanism and
nearly testable in-repo.**

## 7. Strategic options evaluated

A. Financing/carry (composite **~4.4**) · B. Lower-cost venue/tick (~3.0) · C. New
market futures/metals/crypto (~3.1) · D. Stop/archive (~3.0). **A dominates** on
novelty, information gain, and repo compatibility; B/C are higher-ceiling but large
lifts; D is premature.

## 8. Chosen next direction

**Option A — financing/rate-data ingestion enabling carry research.** Carry is the
one genuinely-new, untested mechanism; the immediate next sprint is a
**data-ingestion / research-preparation sprint** (real per-currency rates via the
already-wired FRED pipeline → real carry differential, validated; carry factor
*design* drafted) — **not** a carry screen, **not** a campaign. It resolves the last
in-repo mechanism either way (a real carry factor, or a clean `FINANCING_DEFEATED`
that then justifies archive/venue-pivot), and the financing-data asset is valuable
regardless.

## 9. Was any campaign created?

**No.** No CAMPAIGN_032, no campaign of any number.

## 10. Was any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`; fails closed.

## 11. Do paper/demo/live remain blocked?

**Yes.** Freeze gate confirms paper/demo loops refuse — frozen.

## 12. Validation commands run

| Command | Result |
|---------|--------|
| `pytest tests/ -q` | **2443 passed** — exit 0 |
| `ruff check src scripts tests` | 4 errors — **all pre-existing** in `scripts/run_edge_discovery_vol_managed_tsmom.py` (CAMPAIGN_031). Docs-only sprint changed **zero** Python → not a regression. |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** — exit 0 |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** — exit 0 |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** — exit 0 |
| `git status --short` | clean after this commit |

## 13. Recommended next sprint

`research-financing-rate-data-ingestion-001` — ingest real per-currency interest
rates (FRED, credential-free), build + validate the real carry differential per
cross, and draft the carry factor-validation design. **Data + design only; no carry
screen, no campaign, no approval.** Full prompt in
`NEXT_PROMPT_AFTER_PROGRAMME_SYNTHESIS.md`.

## 14. Files to review first

1. `NEXT_MAJOR_DIRECTION_DECISION.md` — the decision + scope guard.
2. `COMPLETE_PROGRAMME_EVIDENCE_INVENTORY.md` — every effort classified.
3. `REMAINING_UNTESTED_MECHANISMS.md` — why carry is the frontier.
4. `NEXT_PROGRAMME_OPTIONS.md` — the A–D scoring.
5. `PROGRAMME_LESSONS_LEARNED.md` — what the programme taught us.
6. `NEXT_PROMPT_AFTER_PROGRAMME_SYNTHESIS.md` — the exact next (data) sprint.

---

## Bottom line

The expanded FX research programme is **synthesized and the mechanism space is
mapped**: across ten-plus families on majors + crosses, every effect is rejected, a
failed replication, cost-defeated, financing-defeated, or real-but-sub-cost-band —
with **S4 cross relative-value the single genuine factor**, itself ~10× inside the
retail cost band. Breadth was real but not the binding constraint; **cost is**. The
one genuinely-new, untested mechanism is **carry**, and it is nearly testable
in-repo. The chosen direction is a **financing/rate-data ingestion + carry-research-
preparation sprint** — the cheapest, most repo-compatible, highest-information move
that tests genuinely new ground, explicitly **not** a screen or campaign. No factor,
strategy, screen, or campaign was created; freeze intact; paper/demo/live blocked.
