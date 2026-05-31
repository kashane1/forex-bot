# Non-time-bar thesis discovery — sprint 001 SUMMARY

**Branch:** `research-external-non-time-bar-thesis-discovery-001`
**Type:** research & hypothesis-generation only (no code, no campaign, no backtests).
**Date:** 2026-05-29.

---

## 1. Commit hashes by phase

| phase | hash | deliverable |
|---|---|---|
| 0 | `f67d4fa` | truth audit + plan |
| 1 | `a488623` | professional usage survey |
| 2 | `ff0ce91` | literature review |
| 3 | `a0ed374` | public strategy review |
| 4 | `4c150fc` | hypothesis catalog (24) |
| 5 | `b3afba9` | screening & ranking |
| 6 | `7310909` | final shortlist (5) |
| 7 | `58b82bc` | decision + next prompt |
| 8 | this doc | final validation + summary |

Branch stacked on the unmerged feasibility tip `a12f51c` (rebases cleanly onto
`origin/main` once feasibility merges).

## 2. Files changed

10 Markdown docs under `docs/research/`, **no code/config/strategy touched**:
PLAN, PROFESSIONAL_USAGE_SURVEY, LITERATURE_REVIEW, PUBLIC_STRATEGY_REVIEW,
HYPOTHESIS_CATALOG, HYPOTHESIS_RANKING, FINAL_SHORTLIST, NEXT_RESEARCH_DECISION,
NEXT_PROMPT_AFTER_NON_TIME_BAR_THESIS_DISCOVERY, and this SUMMARY (~1.3k lines added).

## 3. Number of hypotheses generated: **24** (H01–H24)
Grouped by external anchor: activity-clock bars, CUSUM events, conditional duration
(ACD), microstructure/flow-proxy, cross-pair RV-commonality, bar-geometry reuse,
sizing/labeling overlays, session structure — plus two deliberately-included
"tempting but should fail" ideas (H23 wider C029 retune, H24 renko) to demonstrate the
screen rejects them.

## 4. Number shortlisted: **5** (H16, H03, H05, H12, H01-deferred)
Classified in Phase 5: 2 `REJECT_IMMEDIATELY`, 8 `LOW_PRIORITY`, 9 `PROMISING`,
5 `FRONT_GATE_CANDIDATE`.

## 5. Top-ranked idea: **H16 · overshoot-exhaustion fade**
When a range/volatility bar completes with unusually large **overshoot** beyond its
threshold (a violent single-candle completion), test whether the next bar(s) **revert**
(exhaustion), on a cost-feasible cell, closing intraday. Cheapest to build (the metric
already exists), financing-free, and not pre-empted by any prior rejection.

> **Re-ranking note:** H16 became #1 after mid-sprint cross-branch evidence — a parallel
> sprint screened vol-managed **time-series momentum** (CAMPAIGN_031) on this corpus and
> found it `COST_FINANCING_DEFEATED + WITHIN_NULL`, also surfacing an **overnight
> financing ≈ 4× spread** cost channel. That **demoted H01 (dollar-bar TSMOM) to
> DEFERRED** (re-tuning a just-rejected effect) and pushed the cheap, intraday,
> non-directional H16 to the top.

## 6. Why H16 differs from C029
- **C029** = a 10-pip USD_JPY range-bar **MTF-trend breakout** (entry on price *travel*
  + HTF confluence), cost-defeated at the tight threshold.
- **H16** = no breakout, no trend confluence, no threshold-direction entry. It conditions
  purely on **completion geometry** (overshoot magnitude) and bets on **short-horizon
  reversion**, on a **cost-feasible** wide bar, with the **H12 spread-state filter** and
  an **intraday exit**. It is orthogonal to C029's signal and is not a threshold tweak of
  it (anti-pattern §3.1 explicitly avoided). It is also distinct from the rejected
  reversion (C027, price-level z-score) and momentum (C031/C025) families.

## 7. Was any campaign created? **No.** (no CAMPAIGN_030; the next step is a *screen*, not a campaign.)
## 8. Was any strategy approved? **No.** `configs/approved_strategies.yaml` = `approved: []`.
## 9. Do paper/demo/live remain blocked? **Yes** — loops still refuse; freeze intact.

## 10. Validation (Phase 8, all green)
- `pytest tests/ -q` → **2340 passed, 3 skipped** (unchanged; docs-only sprint).
- `ruff check src scripts tests` → all checks passed.
- `python scripts/check_research_freeze.py` → ALL CHECKS PASSED.
- `python scripts/validate_research_archive.py` → ALL CHECKS PASSED.
- `python scripts/scan_artifacts_for_secrets.py` → PASSED.
- `git status --short` → clean.

## 11. Recommended next step
Run the drafted **front-gate screening** prompt
([`NEXT_PROMPT_AFTER_NON_TIME_BAR_THESIS_DISCOVERY.md`](NEXT_PROMPT_AFTER_NON_TIME_BAR_THESIS_DISCOVERY.md))
on branch `research-non-time-bar-overshoot-frontgate-001`: screen **H16** (fallback
**H03**, filter **H12**) through the existing edge-discovery lab (matched null,
cost-feasibility, filter-ablation, pair-holdout) to a **pass/block verdict**. It creates
**no campaign** even on PASS. Binding stop: if H16 and H03 both fail matched-null
post-cost on ≥ 2 pairs, directional non-time-bar search on this corpus is exhausted
(reopen only with new data — longer history, non-USD crosses, or true tick data).

## 12. Files to review first
1. [`NON_TIME_BAR_FINAL_SHORTLIST.md`](NON_TIME_BAR_FINAL_SHORTLIST.md) — the 5 ideas + the C031 re-rank.
2. [`NON_TIME_BAR_NEXT_RESEARCH_DECISION.md`](NON_TIME_BAR_NEXT_RESEARCH_DECISION.md) — Option 2 + stop criteria.
3. [`NON_TIME_BAR_HYPOTHESIS_RANKING.md`](NON_TIME_BAR_HYPOTHESIS_RANKING.md) — the full 24-idea screen.
4. [`NON_TIME_BAR_HYPOTHESIS_CATALOG.md`](NON_TIME_BAR_HYPOTHESIS_CATALOG.md) — all 24 candidates.
5. [`NEXT_PROMPT_AFTER_NON_TIME_BAR_THESIS_DISCOVERY.md`](NEXT_PROMPT_AFTER_NON_TIME_BAR_THESIS_DISCOVERY.md) — the front-gate (not campaign) prompt.

## 13. Did this sprint succeed?
By the stated criterion — **yes**. It did **not** find an edge (none was sought). It
produced a small set of **genuinely new, externally-motivated** hypotheses (activity-
clock persistence, CUSUM drift, thin-move fade, overshoot-exhaustion, conditional
duration, spread-state conditioning) that are **materially different** from every
rejected family, honestly screened, with the two obvious traps (C029 retune, renko)
explicitly rejected and the strongest-anchored idea (TSMOM) honestly **deferred** once
fresh evidence showed it within-null on this corpus.
