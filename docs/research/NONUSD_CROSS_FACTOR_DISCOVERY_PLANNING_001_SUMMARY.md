# Non-USD Cross Factor-Discovery PLANNING 001 — Summary

**Branch:** `research-nonusd-cross-factor-discovery-planning-001`
**Type:** factor-discovery **planning & research design only**. Docs-only.
**Date:** 2026-05-30. **Freeze intact; nothing approved; paper/demo/live blocked.**

This sprint produced a roadmap for factor discovery in the expanded 15-instrument
FX universe (7 USD majors + 8 populated non-USD crosses) **without** creating a
factor, strategy, front-gate screen, or campaign. It maps the search space,
enumerates the cross-enabled families, fences the failure-prone ones, ranks and
shortlists the survivors, and names exactly one next direction plus the literal
prompt to open it.

---

## 1. Branch

`research-nonusd-cross-factor-discovery-planning-001` (from clean `origin/main`
at `5324b42`).

## 2. Commit hashes by phase

| Phase | Hash | Deliverable |
|-------|------|-------------|
| 0 | `95a8da4` | `NONUSD_CROSS_FACTOR_DISCOVERY_PLANNING_001_PLAN.md` (baseline audit + plan) |
| 1 | `e0eb26b` | `EXPANDED_FX_SEARCH_SPACE_MAP.md` |
| 2 | `c38d1a2` | `NEW_FACTOR_FAMILIES_ENABLED_BY_CROSSES.md` |
| 3 | `a48e9a4` | `DO_NOT_REPEAT_LIST.md` |
| 4 | `bc9e19d` | `CROSS_UNIVERSE_FACTOR_RANKING.md` |
| 5 | `0b29476` | `CROSS_UNIVERSE_FACTOR_SHORTLIST.md` |
| 6 | `034e540` | `NEXT_FACTOR_DISCOVERY_DIRECTION.md` |
| 7 | `c6a3cd8` | `NEXT_PROMPT_AFTER_CROSS_FACTOR_DISCOVERY_PLANNING.md` |
| 8 | _this commit_ | this summary + validation |

## 3. Files changed

Eight new documents, all additions under `docs/research/`. **Zero code, config,
registry, or executor change** — `git diff --name-only origin/main...HEAD --
'*.py'` is **empty**.

1. `NONUSD_CROSS_FACTOR_DISCOVERY_PLANNING_001_PLAN.md`
2. `EXPANDED_FX_SEARCH_SPACE_MAP.md`
3. `NEW_FACTOR_FAMILIES_ENABLED_BY_CROSSES.md`
4. `DO_NOT_REPEAT_LIST.md`
5. `CROSS_UNIVERSE_FACTOR_RANKING.md`
6. `CROSS_UNIVERSE_FACTOR_SHORTLIST.md`
7. `NEXT_FACTOR_DISCOVERY_DIRECTION.md`
8. `NEXT_PROMPT_AFTER_CROSS_FACTOR_DISCOVERY_PLANNING.md`
9. `NONUSD_CROSS_FACTOR_DISCOVERY_PLANNING_001_SUMMARY.md` (this)

## 4. Search-space map summary

15 instruments across 8 currencies; crosses add **breadth, not new currencies,
history, microstructure, or cheaper cost**. Of 12 research categories:
**4 EXPLORED→closed** (single-instrument directional / mean-reversion / non-time-
bar / macro — *not* reopened by crosses), and **7+ reopened or newly enabled by
breadth**: cross-sectional momentum (D), currency-strength/dispersion (E),
triangular consistency (F), carry (G, financing-data-gated), relative-value (H),
lead-lag/leadership (I), factor replication (J), plus vol/regime baskets
(K-basket). **Exactly one of four "new data" reopen levers (breadth) was pulled;
history, microstructure, and cost walls still stand** — so every admissible
family is one that *breadth* unlocks.

## 5. Number of factor families generated

**24** candidate families (F01–F24), across 8 groups, each with a falsifiable
mechanism, required legs, and the reason majors-only could not test it.

## 6. Top-ranked factor families

By weighted composite (cost ×2, financing/overlap/robustness ×1.5):

1. **F24 — C1 replication (4.31)** — sanctioned reuse, zero-DOF, no new data.
2. **F01 — Cross-implied currency-strength index (4.17)** — breadth-pure foundation.
3. **F23 — Correlation-regime gate (4.17)** — financing-free overlay/enabler.
4. **F02 — Strength-dispersion timing (3.93)**.
5. **F07 / F21 — implied-vs-traded & confirmation filters (3.83)**.

Shortlist (≤5): **S1**=F24 (C1 replication), **S2**=F01 (strength index),
**S3**=F08 (currency cross-sectional momentum), **S4**=F15/F18 (economically-
motivated half-life-matched cross RV), **S5**=F23 (regime gate). Carry (F12–F14)
deliberately excluded — **prerequisite-blocked on financing-rate ingest**.

## 7. Chosen next direction

**S1 — Independent C1 replication on non-USD crosses** (family F24): a fresh,
pre-registered, **frozen-threshold** replication of the locked C1 factor on the 8
crosses to settle whether C1 is a genuine multi-TF-confluence effect or a
residual-USD artifact. Replication, **not** a re-tune. Cheapest, highest-
information, zero-new-data, and its outcome gates the value of S2–S5. Pre-stated
three-branch stop criteria (`C1_ARTIFACT` / `C1_GENUINE_BUT_COST_DEFEATED` /
`C1_GENUINE_AND_COST_SURVIVING`) — none of which creates a campaign.

## 8. Was any campaign created?

**No.** No CAMPAIGN_032, no campaign of any number.

## 9. Was any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`;
`forex_bot.approval` fails closed.

## 10. Do paper/demo/live remain blocked?

**Yes.** Freeze gate confirms `paper-loop refuses ['trend_following'] — frozen`
and `demo-loop refuses ['trend_following'] — frozen`. No executor/loop change.

## 11. Validation commands run

| Command | Result |
|---------|--------|
| `pytest tests/ -q` | **2443 passed** — exit 0 |
| `ruff check src scripts tests` | **4 errors — ALL pre-existing** in `scripts/run_edge_discovery_vol_managed_tsmom.py` (CAMPAIGN_031, on `origin/main`). This sprint changed **zero** Python (`git diff --name-only origin/main...HEAD -- '*.py'` empty), so not a regression. Auto-fixable; out of scope for a docs-only sprint. |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** — exit 0 (registry empty; loops refuse; 747 evidence links resolve) |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** — exit 0 |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** — exit 0 (pattern scan; value scan skipped, no creds in env) |
| `git status --short` | clean after this commit (docs-only) |

## 12. Recommended next sprint

`research-c1-cross-replication-screen-001` — a single, fresh, pre-registered
front-gate **replication** of the locked C1 factor on the 8 crosses (verdict-
producing, **no campaign, no approval**). Full prompt in
`NEXT_PROMPT_AFTER_CROSS_FACTOR_DISCOVERY_PLANNING.md`. If C1 replicates as
genuine, the sprint *after that* is S2 (currency-strength index); if C1 evaporates
as an artifact, pivot instead to the **financing-data prerequisite** (unblocks
carry) or a venue/history expansion — never more mining on this corpus.

## 13. Files to review first

1. `NEXT_FACTOR_DISCOVERY_DIRECTION.md` — the chosen direction + stop criteria.
2. `CROSS_UNIVERSE_FACTOR_SHORTLIST.md` — the 5 families with thesis/failure modes.
3. `DO_NOT_REPEAT_LIST.md` — the fences (especially §1 C1-replication-vs-re-tune).
4. `EXPANDED_FX_SEARCH_SPACE_MAP.md` — what crosses do and do not reopen.
5. `NEXT_PROMPT_AFTER_CROSS_FACTOR_DISCOVERY_PLANNING.md` — the literal next prompt.

---

## Bottom line

The expanded FX universe meaningfully reopens **seven research categories** — but
on **breadth alone**; the cost, financing, history, and microstructure walls that
defeated the seven-major programme are unchanged. The disciplined next move is the
cheapest, highest-information, zero-new-data step: a **frozen-threshold C1
replication on non-collinear crosses** to settle whether the programme's one
genuine factor is real or a USD-regime shadow — then let that answer steer whether
to mine new breadth families (S2+) or pivot to data prerequisites. **No factor,
strategy, screen, or campaign was created; freeze intact; nothing approved;
paper/demo/live blocked.**
