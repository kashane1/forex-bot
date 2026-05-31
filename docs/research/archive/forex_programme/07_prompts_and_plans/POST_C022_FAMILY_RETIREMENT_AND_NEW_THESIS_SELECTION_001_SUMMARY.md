# Post-C022 Family Retirement & New-Thesis Selection — Sprint 001 Summary

**Date:** 2026-05-28 · **Type:** research closeout + thesis selection. Approves
nothing, executes nothing, creates no campaign, changes no verdict.

## 1. Branch

`research-post-c022-family-retirement-and-new-thesis-selection-001` (off `main` @ `f693920`).

## 2. Commit hashes by phase

| Phase | Hash | Title |
|---|---|---|
| 0 | `0002185` | branch, audit, plan |
| 1 | `865dfac` | family closeout memo |
| 2 | `b4ab443` | backlog/status updates |
| 3 | `027a83c` | next-thesis lane comparison |
| 4 | `cca37c2` | next-thesis selection decision |
| 5 | `6edfea8` | next-sprint prompt draft |
| 6 | _this commit_ | final validation + summary |

## 3. Files changed by phase

- **0:** `docs/research/POST_C022_FAMILY_RETIREMENT_AND_NEW_THESIS_SELECTION_001_PLAN.md` (new).
- **1:** `docs/research/C022_C023_PULLBACK_RESOLUTION_FAMILY_CLOSEOUT.md` (new).
- **2:** `docs/research/STRATEGY_STATUS.md`, `docs/research/EVIDENCE_INDEX.md`,
  `docs/research/FUTURE_RESEARCH_BACKLOG.md`, `docs/research/EVIDENCE_MANIFEST.json` (edits only).
- **3:** `docs/research/NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md` (new).
- **4:** `docs/research/NEXT_THESIS_SELECTION_DECISION.md` (new).
- **5:** `docs/research/NEXT_SPRINT_PROMPT_AFTER_C022_FAMILY_CLOSEOUT.md` (new).
- **6:** this file (new).

Total vs `main`: 9 files, +830 / −11 lines. **Docs + one manifest JSON only — no
source/strategy/broker/executor/config-gate code changed.**

## 4. C022/C023 family status

**RETIRED**, classification `RETIRED_UNLESS_NEW_EXTERNAL_THESIS`. The
H4-regime → H1-pullback → M15-EMA-reclaim signal is closed out: four independent
diagnostics (MFE/MAE, executed stop-model comparison, lifecycle conclusions,
winner/loser feature separation) localized the failure to the **entry signal**.
Stop multiple, time-invalidation, ADX re-gating, and a cost-free mid-price baseline
all stay negative; every structural entry feature is at AUC ≈ 0.50.

## 5. Why C023 was deferred / retired

C023's only change is the H4 directional-bias ADX gate 20 → 22, but `h4_adx_at_entry`
does not separate winners from losers (AUC 0.515 train / 0.501 validation; flat
quintile win-rates ~0.30–0.35). A stricter ADX gate would only shrink the sample with
no evidence of improvement, and is not a structurally new thesis. **C023 remains
scaffold-only and is not executed.**

## 6. Why C024 was not created

C024 readiness is **`NOT_READY`**: no entry-time structural feature separated winners
from losers, so there is no justified filter hypothesis to refine the
pullback-resolution signal. Creating C024 would require choosing thresholds the data
does not support — i.e. threshold-mining. **No CAMPAIGN_024 was created.**

## 7. Candidate thesis lanes compared

Seven lanes, scored on distinctness, current-evidence support, complexity, overfit
resistance, M1/M15 data fit, sample size, and precommit cleanliness
(see [`NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md`](NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md)):
A session/time-of-day, B volatility expansion/compression, C cost/tradeability filter,
**D microstructure-style confirmation**, E single-pair specialization, F news/calendar,
G pause/infra deepening.

## 8. Selected next thesis lane

**Lane D — market-microstructure-style confirmation**, pursued first as a **read-only
diagnostic** (not a campaign, not C024).

## 9. Why selected

It targets the actual diagnosed defect — the inert M15 EMA-reclaim trigger
(AUC 0.494/0.485) — by testing structurally different confirmation primitives
(sweep+displacement, break/retest, range expansion, trap avoidance); it is the most
structurally distinct lane; it starts falsifiable and threshold-free (a read-only
winner/loser separation test on the existing C022 trade set); and it needs no new
data. Lanes A/B rest on weak, partly mechanical context effects (and B carries strong
negative priors); C/G are process/guardrail value, not alpha; E has weak support and
high overfit risk; F is gated on calendar-data quality.

## 10. Next-sprint prompt location

[`NEXT_SPRINT_PROMPT_AFTER_C022_FAMILY_CLOSEOUT.md`](NEXT_SPRINT_PROMPT_AFTER_C022_FAMILY_CLOSEOUT.md)
— a copy-paste prompt for `research-m15-microstructure-confirmation-diagnostic-001`
that ends at a C024 readiness decision and creates no C024.

## 11. Did any verdict change?

**No.** C020/C021/C022 remain REJECT; C023 remains scaffold-only/not executed; no
historical metric was rewritten.

## 12. Was any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`.

## 13. Do paper/demo/live remain blocked?

**Yes.** No broker/executor/order/live code touched; no OANDA mutation/order calls;
freeze gate `loops_refuse` still passes.

## 14. Tests and validation commands run (Phase 6)

| command | result |
|---|---|
| `pytest tests/ -q` | **1967 passed, 3 skipped** (data-dependent skips). |
| `ruff check src tests scripts research` | **All checks passed.** |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED.** |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED.** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** (value scan active over 5654 files; pattern scan over 5317; none found). |
| `git status --short` | clean (all work committed). |

## 15. Pre-existing failures

None as failures. The 3 pytest skips are data-dependent and unrelated to this sprint:
`tests/research/test_cost_atlas.py` (local H4 store absent) and two
`tests/unit/entry_parity/test_compare_entries.py` cases (local C008 bespoke trade CSVs
gitignored/absent in a fresh worktree).

## 16. Remaining blockers

None for this closeout. The next sprint (Lane D diagnostic) requires the same
read-only local data access (materialized M15/H1/H4 + C022 base trade CSVs via the
authorized gitignored `.env` symlinks) the C022 feature-separation sprint used.

## 17. Exact files to review first

1. [`C022_C023_PULLBACK_RESOLUTION_FAMILY_CLOSEOUT.md`](C022_C023_PULLBACK_RESOLUTION_FAMILY_CLOSEOUT.md) — the retirement decision + reopening bar.
2. [`NEXT_THESIS_SELECTION_DECISION.md`](NEXT_THESIS_SELECTION_DECISION.md) — the selected lane + five-part C024 readiness bar.
3. [`NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md`](NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md) — how the lanes were scored.
4. [`NEXT_SPRINT_PROMPT_AFTER_C022_FAMILY_CLOSEOUT.md`](NEXT_SPRINT_PROMPT_AFTER_C022_FAMILY_CLOSEOUT.md) — the next-sprint prompt.

## 18. Recommended next sprint

`research-m15-microstructure-confirmation-diagnostic-001` (read-only) — inventory M15
confirmation primitives, build causal read-only detectors, compare their presence on
C022 winners vs losers, and output a `READY_FOR_PRECOMMIT` / `NOT_READY` decision for a
*possible future* C024. Carry **Lane C (cost/tradeability guardrail)** as a companion
overlay only. Create no C024; execute no C023; approve nothing; touch no
paper/demo/live or broker code.
