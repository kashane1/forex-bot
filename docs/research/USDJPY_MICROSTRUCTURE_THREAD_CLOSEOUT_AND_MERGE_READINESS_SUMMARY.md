# USD_JPY Microstructure Thread — Closeout & Merge-Readiness Summary

**Date:** 2026-05-28 · **Type:** closeout + merge-readiness audit + roadmap. Approves
nothing, executes nothing, creates no campaign, changes no verdict, claims no edge.

## 1. Branch

`research-usdjpy-post-entry-trade-management-diagnostic-001`. It is the tip of a chained
sequence (each sprint branched from the previous tip), so it contains the full 33-commit
arc from `main`: post-C022 retirement + USD_JPY scope amendment → USD_JPY microstructure
entry diagnostic → USD_JPY post-entry trade-management diagnostic → this full-thread
closeout.

## 2. Commit hashes for this closeout (Phases A–E)

| Phase | Hash | Title |
|---|---|---|
| A | `d243d5c` | full-thread closeout memo |
| B | `ea90376` | status/backlog/index full-thread closeout |
| C | `cb35876` | next-lane roadmap |
| D | `5820fcc` | next-sprint prompt (external thesis + atlas) |
| E | _this commit_ | final validation + merge-readiness summary |

## 3. Files changed (this closeout)

- **A:** `docs/research/C022_C023_USDJPY_MICROSTRUCTURE_THREAD_CLOSEOUT.md` (new).
- **B:** `docs/research/STRATEGY_STATUS.md`, `docs/research/EVIDENCE_INDEX.md`,
  `docs/research/FUTURE_RESEARCH_BACKLOG.md`, `docs/research/EVIDENCE_MANIFEST.json` (edits).
- **C:** `docs/research/NEXT_RESEARCH_LANE_AFTER_USDJPY_MICROSTRUCTURE_CLOSEOUT.md` (new).
- **D:** `docs/research/NEXT_SPRINT_PROMPT_AFTER_USDJPY_MICROSTRUCTURE_CLOSEOUT.md` (new).
- **E:** this file (new).

Docs + one manifest JSON only — no source/strategy/broker/executor/config-gate code changed.

## 4. Final status of the C022/C023/USD_JPY microstructure thread

**FULLY CLOSED — no actionable edge at either the entry or the management layer.**
- C022/C023 pullback-resolution family: **RETIRED** (`RETIRED_UNLESS_NEW_EXTERNAL_THESIS`).
- USD_JPY microstructure **entry** lane: **CLOSED**; C024 `NOT_READY`.
- USD_JPY post-entry **trade-management** lane: **CLOSED** (`NOT_READY`).

## 5. Why no more mining is recommended

Internally-invented confluence/reclaim/stop/confirmation combinations failed repeatedly
(C010/C015–C017/C020–C022 + USD_JPY entry diagnostic); structural entry features sit at
AUC ≈ 0.50; stop geometry is not the bottleneck; and the post-entry signals that *did*
separate outcomes descriptively are **not actionable** — every predeclared early-exit
counterfactual reduced expectancy on both splits. Further parameter/threshold/overlay
changes on the same family are not warranted; a genuinely new *source* of edge is required.

## 6. Next-lane options compared

Six genuinely-new lanes scored (none a C022-style variant): 1 pause/infra, 2 external
thesis sourcing, 3 macro/calendar/event, 4 session/time-of-day atlas, 5 carry/rates/
financing, 6 regime labeling. See
[`NEXT_RESEARCH_LANE_AFTER_USDJPY_MICROSTRUCTURE_CLOSEOUT.md`](NEXT_RESEARCH_LANE_AFTER_USDJPY_MICROSTRUCTURE_CLOSEOUT.md).

## 7. Selected / recommended next lane

**`external-thesis-sourcing-and-session-atlas-001` (Lane 2 + Lane 4).** Do not code
another entry strategy yet: change the *source* of hypotheses (survey external FX theses)
and *map* USD_JPY behavior (read-only session/vol/spread atlas) to pre-screen any sourced
thesis. Acceptable alternative: Lane 1 (pause strategy research; invest in infra/process).

## 8. Next prompt location

[`NEXT_SPRINT_PROMPT_AFTER_USDJPY_MICROSTRUCTURE_CLOSEOUT.md`](NEXT_SPRINT_PROMPT_AFTER_USDJPY_MICROSTRUCTURE_CLOSEOUT.md)
— branch `research-external-thesis-sourcing-and-session-atlas-001`.

## 9. Merge-readiness status

**READY (clean).** Audited `main...HEAD`:
- 46 files changed, +9081 / −11; all docs, compact JSON, small preview CSVs (15 KB / 19 KB),
  read-only research modules/scripts, and unit tests.
- **No `.env`, credentials, SQLite/DBs, raw candle dumps, or `.parquet` tracked.** Both
  full per-trade parquets are **gitignored** (verified via `git check-ignore`).
- No tracked file added vs main exceeds 200 KB.
- `configs/approved_strategies.yaml` remains `approved: []`.
- No CAMPAIGN_024 created; C023 not executed; no verdict changed; no broker/executor/
  order/live changes; no OANDA mutation/order calls.
- All gates green (pytest 1996 passed/3 skipped, ruff clean, freeze + archive pass,
  secret value-scan active over 2 practice creds and PASSED).

## 10. Whether C023 executed

**No.** Scaffold-only / not executed.

## 11. Whether C024 was created

**No.** No config, no source, no campaign artifact.

## 12. Whether any verdict changed

**No.** All campaign verdicts untouched; no historical metric rewritten.

## 13. Whether any strategy was approved

**No.** `configs/approved_strategies.yaml` remains `approved: []`.

## 14. Whether paper/demo/live remain blocked

**Yes.** No broker/executor/order/live code touched; freeze gate `loops_refuse` passes.

## 15. Tests and validation commands run (Phase E)

| command | result |
|---|---|
| `pytest tests/ -q` | **1996 passed, 3 skipped**. |
| `ruff check src tests scripts research` | **All checks passed.** |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED.** |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED.** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** — value scan active for 2 practice credentials; none leaked. |
| `git status --short` | clean. |
| `git log --graph main..HEAD` / `git diff main...HEAD --stat` | 33 commits; 46 files; audited clean. |

## 16. Pre-existing failures / skips

None as failures. 3 data-dependent pytest skips (two C008 entry-parity cases needing
gitignored CSVs; cost-atlas H4 store path) — unchanged from baseline.

## 17. Exact files to review first

1. [`C022_C023_USDJPY_MICROSTRUCTURE_THREAD_CLOSEOUT.md`](C022_C023_USDJPY_MICROSTRUCTURE_THREAD_CLOSEOUT.md) — full-thread closeout + lessons.
2. [`NEXT_RESEARCH_LANE_AFTER_USDJPY_MICROSTRUCTURE_CLOSEOUT.md`](NEXT_RESEARCH_LANE_AFTER_USDJPY_MICROSTRUCTURE_CLOSEOUT.md) — next-lane comparison + recommendation.
3. [`NEXT_SPRINT_PROMPT_AFTER_USDJPY_MICROSTRUCTURE_CLOSEOUT.md`](NEXT_SPRINT_PROMPT_AFTER_USDJPY_MICROSTRUCTURE_CLOSEOUT.md) — the next-sprint prompt.
4. [`USDJPY_TRADE_MANAGEMENT_READINESS_DECISION.md`](USDJPY_TRADE_MANAGEMENT_READINESS_DECISION.md) + [`USDJPY_POST_ENTRY_MANAGEMENT_COUNTERFACTUALS.md`](USDJPY_POST_ENTRY_MANAGEMENT_COUNTERFACTUALS.md) — the decisive trade-management evidence.

## 18. Recommended push / merge command (branch is clean)

The branch is a docs/research-only, freeze-passing, audited-clean diagnostic arc. Suggested:

```
git push -u origin research-usdjpy-post-entry-trade-management-diagnostic-001
gh pr create --base main \
  --title "research: C022/C023 + USD_JPY microstructure thread closeout (entry + trade-management) — no actionable edge" \
  --body "Full diagnostic arc (33 commits): C022/C023 family retired; USD_JPY microstructure entry lane closed (C024 NOT_READY); USD_JPY post-entry trade-management lane closed (NOT_READY — early-exit counterfactuals all reduce expectancy). Docs + read-only research modules/scripts/tests only; full parquets gitignored; approved_strategies.yaml stays []; no C024/C023/approval/paper-demo-live. Next lane: external-thesis-sourcing-and-session-atlas-001."
```

Merging is a human decision. This arc changes no verdict and approves nothing; it is
safe to merge to preserve the institutional record, or to keep as a branch for review.
