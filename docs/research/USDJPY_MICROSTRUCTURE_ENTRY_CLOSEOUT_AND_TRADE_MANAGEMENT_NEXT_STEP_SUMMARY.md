# USD_JPY Microstructure Entry Closeout & Trade-Management Next Step — Summary

**Date:** 2026-05-28 · **Type:** follow-up closeout + next-step plan. Approves nothing,
executes nothing, creates no campaign, changes no verdict, claims no edge.

## 1. Branch

`research-usdjpy-m15-microstructure-confirmation-diagnostic-001` (same branch as the
USD_JPY microstructure diagnostic; no new branch created, per instruction).

## 2. Commit hashes for this follow-up

| Phase | Hash | Title |
|---|---|---|
| A | `00e8c54` | close USD_JPY entry lane |
| B | `feb5fac` | status/backlog updates |
| C | `d6768df` | next-sprint prompt (trade-management) |
| D | _this commit_ | final validation + summary |

(Prior diagnostic phases 0–6 ended at `31e1389`.)

## 3. Files changed

- **A:** `docs/research/USDJPY_MICROSTRUCTURE_ENTRY_LANE_CLOSEOUT.md` (new).
- **B:** `docs/research/STRATEGY_STATUS.md`, `docs/research/EVIDENCE_INDEX.md`,
  `docs/research/FUTURE_RESEARCH_BACKLOG.md`, `docs/research/EVIDENCE_MANIFEST.json` (edits only).
- **C:** `docs/research/NEXT_SPRINT_PROMPT_AFTER_USDJPY_MICROSTRUCTURE_ENTRY_CLOSEOUT.md` (new).
- **D:** this file (new).

Docs + one manifest JSON only — no source/strategy/broker/executor/config-gate code changed.

## 4. USD_JPY microstructure entry lane status

**CLOSED as an entry-alpha lane.** The read-only USD_JPY diagnostic (306 C022 base
trades; 299 MFE/MAE OK / 7 NO_BARS; 172 hard stops / 134 time exits; near-flat mean R)
found **no live M15 entry primitive with material, stable winner/loser separation**
(best stable live effect |AUC−0.5| = 0.016, below the 0.05 floor), and none beat the
inert EMA20-reclaim baseline (AUC 0.539/0.486). The only above-floor separation was
**post-entry** (retest-hold AUC 0.611/0.552; trap), which cannot gate a live entry.

## 5. Why C024 remains NOT_READY

A C024 entry campaign requires a **live**, stable, plausible, non-overfit entry signal
that beats the existing trigger and preserves sample. On USD_JPY: every live primitive
is negligible or direction-unstable; the only above-floor signal is post-entry
(unavailable at the entry decision and partly tautological); the sample is small and the
one stable boolean lift (sweep+displacement) is fragile with no straight-to-stop
reduction. No live entry edge exists to precommit, so C024 stays `NOT_READY` and no
CAMPAIGN_024 is created.

## 6. Why the next lane is trade management, not entry

The separation that *does* exist is **post-entry** — it describes how trades behave
after they are open (winners hold their reclaim; losers trap). That is useless for
deciding *whether to enter*, but it is the natural input to deciding *what to do with a
trade already open*: early invalidation, hold/exit, stop-avoidance, time-stop
refinement. The next sprint therefore reframes these post-entry signals honestly as
**trade-management diagnostics**, explicitly not entry alpha, and explicitly not a
reopening of the closed entry lane. It remains read-only, pre-committed, out-of-sample,
no-threshold-mining, and ends at a readiness classification — not a rule, campaign, or
C024.

## 7. Next sprint prompt location

[`docs/research/NEXT_SPRINT_PROMPT_AFTER_USDJPY_MICROSTRUCTURE_ENTRY_CLOSEOUT.md`](NEXT_SPRINT_PROMPT_AFTER_USDJPY_MICROSTRUCTURE_ENTRY_CLOSEOUT.md)
— branch `research-usdjpy-post-entry-trade-management-diagnostic-001`.

## 8. Whether C023 executed

**No.** C023 remains scaffold-only / not executed.

## 9. Whether C024 was created

**No.** No CAMPAIGN_024 exists (verified: no config, no source).

## 10. Whether any verdict changed

**No.** C022 remains REJECT; C023 scaffold-only; all prior verdicts untouched; no
historical metric rewritten.

## 11. Whether any strategy was approved

**No.** `configs/approved_strategies.yaml` remains `approved: []`.

## 12. Whether paper/demo/live remain blocked

**Yes.** No broker/executor/order/live code touched; no OANDA mutation/order calls;
freeze gate `loops_refuse` still passes.

## 13. Tests and validation commands run (Phase D)

| command | result |
|---|---|
| `pytest tests/ -q` | **1984 passed, 3 skipped** (data-dependent skips). |
| `ruff check src tests scripts research` | **All checks passed.** |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED.** |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED.** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** — with `.env` sourced the **value scan was active** for 2 practice credentials; none leaked. |
| `git status --short` | clean (all work committed). |

## 14. Pre-existing failures / skips

None as failures. 3 data-dependent pytest skips (cost-atlas H4 store path; two C008
entry-parity cases needing gitignored CSVs) — unchanged from baseline.

## 15. Exact files to review first

1. [`USDJPY_MICROSTRUCTURE_ENTRY_LANE_CLOSEOUT.md`](USDJPY_MICROSTRUCTURE_ENTRY_LANE_CLOSEOUT.md) — the entry-lane closeout decision.
2. [`NEXT_SPRINT_PROMPT_AFTER_USDJPY_MICROSTRUCTURE_ENTRY_CLOSEOUT.md`](NEXT_SPRINT_PROMPT_AFTER_USDJPY_MICROSTRUCTURE_ENTRY_CLOSEOUT.md) — the trade-management diagnostic prompt.
3. [`USDJPY_C024_READINESS_DECISION.md`](USDJPY_C024_READINESS_DECISION.md) — why C024 stays NOT_READY.
4. [`USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_001_SUMMARY.md`](USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_001_SUMMARY.md) — the underlying diagnostic.
