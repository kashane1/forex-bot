# Range / volatility-bar feasibility — sprint 001 SUMMARY

**Branch:** `research-range-volatility-bar-feasibility-001`
**Type:** diagnostic feasibility study (NOT a strategy campaign).
**Date:** 2026-05-29.

---

## 1. Commit hashes by phase

| phase | hash | deliverable |
|---|---|---|
| 0 | `dc53f9b` | baseline audit + plan + gitignore/.gitkeep |
| 1 | `cab172b` | feasibility protocol |
| 2 | `51e0ea0` | analyzer module + 26 unit tests |
| 3 | `ef98bf8` | driver script + 18 helper tests |
| 4 | `dd41512` | USD_JPY result + compact artifacts |
| 5 | `6afe965` | seven-pair result + compact artifacts |
| 6 | `d1e4c58` | lane decision |
| 7 | `cbc35c4` | next prompt (drafted, not executed) |
| 8 | this doc | final validation + summary |

(Branched off `origin/main` @ `cc553d8`.)

## 2. Files changed

24 files, +12,476 lines, **0 deletions**:
- Docs (8): PLAN, PROTOCOL, USDJPY_RESULT, SEVEN_PAIR_RESULT, LANE_DECISION,
  NEXT_PROMPT, this SUMMARY.
- Code (2): `src/forex_bot/research/non_time_bar_feasibility.py` (pure analyzer),
  `scripts/analyze_non_time_bar_feasibility.py` (driver).
- Tests (2): `tests/unit/test_non_time_bar_feasibility.py` (26),
  `tests/unit/test_non_time_bar_feasibility_driver.py` (18).
- `.gitignore` (+1 whitelist block) and `research/non_time_bar_feasibility/.gitkeep`.
- Compact diagnostics (12 small JSON/CSV/MD) under
  `research/non_time_bar_feasibility/` (root = 7-pair; `usdjpy/` = USD_JPY focus).

## 3. Was C029 changed? **No.**
`git diff origin/main..HEAD` touches no C029 file (`research/campaign_029/**`,
`range_bar_execution.py`, `usdjpy_range_bar_mtf_breakout.py`, `CAMPAIGN_029*` docs are
all unchanged). C029 was not tuned, revived, or reinterpreted.

## 4. USD_JPY feasibility result
- Reproduces C029: 10-pip range = **cost/risk 0.110** at the baseline 2× (20-pip)
  stop → `COST_DOMINATED` (above the ~0.08R best gross edge this lab has observed;
  C029's own gross edge was +0.084R, net −0.019R).
- Cost falls ~`1/threshold`: 0.110→0.073→0.055→0.044→0.037 across 10/15/20/25/30-pip.
  **25 & 30-pip range are FEASIBLE** at the baseline stop.
- Volatility: **abs_close 50 & true_range 50 feasible**; true_range 20/30/40 +
  abs_close 20 `TOO_NOISY` (cadence > 20k bars/yr; TR-20 ≈ 38k/yr). None too sparse.

## 5. Seven-pair feasibility result (91 cells)
- Labels: 25 FEASIBLE, 41 FEASIBLE_ONLY_WITH_LARGER_STOPS, 10 COST_DOMINATED,
  15 TOO_NOISY, 0 TOO_SPARSE, 0 INCONCLUSIVE.
- 10-pip range is `COST_DOMINATED` on 6/7 majors; only **AUD_USD** (cheapest spread)
  escapes. Min cost-feasible range threshold tracks spread: AUD 20, most 25,
  GBP/CAD 30.
- `true_range 20-pip` is `TOO_NOISY` on all 7 pairs.

## 6. Range-bar threshold findings
Cost is ~fixed (~2.0–2.6 pips round-trip) while risk scales with the threshold, so
cost/risk ≈ `cost / (2 × threshold)`. **10-pip is the problem, not range bars.**
Cost stops dominating at **25–30 pip** on every major; a single shared **30-pip range
bar is cost-feasible across all seven pairs**. Range bars beat volatility bars on
feasible share (0.83 vs 0.66).

## 7. Volatility-bar threshold findings
Volatility bars front-load cadence: small thresholds (esp. `true_range ≤ 40 pip`,
`abs_close 20`) fire 11k–38k bars/yr → `TOO_NOISY`. Only the **50-pip** end is clean
and cost-feasible (cost/risk 0.038–0.051) on all pairs. abs_close and true_range are
near-identical on cost; true_range simply fires more bars. No volatility threshold is
materially *better* than the equivalent-cost range threshold; range is cleaner.

## 8. Cost-floor findings
C029 cost floor: cost 2.29 pips / 24.05-pip risk → cost/risk ≈ 0.095 vs gross +0.084R
→ cost-defeated. The break-even gross edge per cell = cost/risk. It drops below the
**~0.08R lab-achievable benchmark** only at **range ≥ 20–25 pip** (pair-dependent) and
**volatility 50 pip**. Below that, the bar would need an unprecedentedly large gross
edge just to break even.

## 9. Is USD_JPY special? **No.**
Mid-pack on spread (1.80 p), cost/risk (0.110 at 10-pip), and min-feasible threshold
(25). The feasibility ordering is essentially a spread ordering. The C029 failure was
**not** a USD_JPY idiosyncrasy — it would have failed on six of seven majors.

## 10. Lane decision
**Option 3 — keep the non-time-bar infrastructure, PAUSE strategy search**, with a
strict, pre-conditioned door to a future precommit (Option 1) openable only by a
**new external thesis** meeting the re-entry criteria (cost/threshold ≤ 0.10;
cost/risk ≤ 0.05 ⇒ range ≥ 25–30 pip or volatility ≥ 50 pip; 200 ≤ bars/yr ≤ 20,000;
edge-discovery front gate before any campaign number; distinctness memo). Not
retired (cost is not destiny at wide thresholds), not precommitted now (no edge
exists; would be a C029 retune). See
`docs/research/NON_TIME_BAR_LANE_DECISION_AFTER_C029.md`.

## 11. Was CAMPAIGN_030 created? **No.**
## 12. Was any strategy approved? **No.** `configs/approved_strategies.yaml` = `approved: []`.
## 13. Do paper/demo/live remain blocked? **Yes** — loops still refuse; freeze intact.

## 14. Validation commands run (Phase 8, all green)
- `pytest tests/ -q` → **2340 passed, 3 skipped** (local-data skips; was 2296 +44 new).
- `ruff check src scripts tests` → all checks passed.
- `python scripts/check_research_freeze.py` → ALL CHECKS PASSED.
- `python scripts/validate_research_archive.py` → ALL CHECKS PASSED.
- `python scripts/scan_artifacts_for_secrets.py` → PASSED.
- `git status --short` → clean (everything committed).

## 15. Local artifacts NOT committed
- Full generated range/volatility bars and M1 caches (regenerable from local M1;
  gitignored under `research/non_time_bar_feasibility/**`, only compact
  summaries/matrix/report/manifest are whitelisted).
- The discarded smoke run (`research/non_time_bar_feasibility/_smoke/`, deleted).
- No raw M1, trade ledgers, DB dumps, `.env`, or credentials were ever written or
  committed. The analyzer computes no PnL/returns and makes no OANDA/broker calls.

## 16. Recommended next step
Run **Prompt A** from `docs/research/NEXT_PROMPT_AFTER_NON_TIME_BAR_FEASIBILITY.md`:
a docs/archive-only **lane closeout** (`research-non-time-bar-lane-closeout-001`) that
records the PAUSED lane status in the backlog/EVIDENCE_INDEX and confirms
merge-readiness — no campaign, no evidence. Prompt B (external-thesis brief) is the
only path that can later reopen the lane.

## 17. Files to review first
1. `docs/research/NON_TIME_BAR_LANE_DECISION_AFTER_C029.md` — the decision + re-entry criteria.
2. `docs/research/SEVEN_PAIR_NON_TIME_BAR_FEASIBILITY_RESULT.md` — cross-pair findings.
3. `docs/research/USDJPY_NON_TIME_BAR_FEASIBILITY_RESULT.md` — C029-anchored USD_JPY detail.
4. `research/non_time_bar_feasibility/feasibility_matrix.csv` — the 91-cell matrix.
5. `src/forex_bot/research/non_time_bar_feasibility.py` — the economics/classification logic.
