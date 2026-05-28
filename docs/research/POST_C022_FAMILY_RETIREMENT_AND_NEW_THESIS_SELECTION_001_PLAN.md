# Post-C022 Family Retirement & New-Thesis Selection — Sprint 001 Plan

**Date:** 2026-05-28 · **Branch:** `research-post-c022-family-retirement-and-new-thesis-selection-001` (off `main` @ `f693920`)
**Type:** research closeout + thesis-selection. Approves nothing, executes no campaign, implements no strategy, tunes nothing, changes no verdict.

> This sprint produces **documented decisions and a next-sprint prompt**, not code
> and not a new strategy. Its only deliverables are markdown decision docs plus
> freeze-safe updates to existing backlog/status indexes.

## 1. Purpose

The C022/C023 pullback-resolution family has now been diagnosed to exhaustion. The
remaining question is no longer "can we fix the stop / gate / ADX threshold" — it is
"is there any entry-time edge in this signal at all," and the winner/loser
feature-separation analysis answered **no**. This sprint formally:

1. **Retires or pauses** the C022/C023 pullback-resolution family with a written
   closeout memo and reopening criteria.
2. Updates the research backlog/status indexes to reflect that status (without
   altering any verdict).
3. Compares the next **structurally different** research theses.
4. **Selects exactly one** next lane.
5. Drafts the **exact next-sprint prompt** for that lane.

## 2. Evidence being closed out

| Evidence | Finding |
|---|---|
| `CAMPAIGN_022` verdict | **REJECT** (entry-edge failure). |
| [`CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md`](CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md) | Time-exit winners rarely approach the stop (4.7% touch −0.9R); 45.9% of stop-outs never reach +0.25R. Stop geometry is **not** the primary problem. |
| [`DIAGNOSTIC_STOP_MODEL_COMPARISON_EXECUTED.md`](DIAGNOSTIC_STOP_MODEL_COMPARISON_EXECUTED.md) | All ATR-multiple stops (1.5×–3.0×) and time-invalidation variants stay negative (≈ −0.05 to −0.08R). Cost-free mid-price baseline still negative. Entry edge, not stop distance. |
| [`LIFECYCLE_FEATURE_CAPTURE_AND_MFE_MAE_EXECUTION_001_CONCLUSIONS.md`](LIFECYCLE_FEATURE_CAPTURE_AND_MFE_MAE_EXECUTION_001_CONCLUSIONS.md) | Bigger issue is entry timing, not stop placement. Structure stop / early-invalidation exit not worth a campaign on current evidence. |
| [`C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md`](C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md) | H4 regime, H1 pullback, M15 reclaim/trigger features all at AUC ≈ 0.50. Strongest stable signal-quality effect below the 0.05 floor. Only weak **context** separators: cost, volatility, time-of-day. |
| [`C024_READINESS_FROM_C022_FEATURE_SEPARATION.md`](C024_READINESS_FROM_C022_FEATURE_SEPARATION.md) | **NOT_READY.** No structural entry feature separates winners; C023 ADX22 unsupported (H4 ADX flat across quintiles). |
| [`C022_WINNER_LOSER_FEATURE_SEPARATION_001_SUMMARY.md`](C022_WINNER_LOSER_FEATURE_SEPARATION_001_SUMMARY.md) | Recommends retiring/pausing the family; any new entry idea must be structurally different and pre-committed. |

## 3. Non-goals

- **Not** a new-strategy implementation sprint.
- **Not** C024 (no CAMPAIGN_024 is created).
- **Not** C023 execution.
- **Not** a tuning/threshold-mining sprint.
- **Not** paper/demo/live enablement.

## 4. Safety rules (hard)

- Do not create CAMPAIGN_024.
- Do not execute C023.
- Do not implement a new strategy.
- Do not retune C022.
- Do not alter existing campaign verdicts.
- Do not rewrite historical metrics.
- Do not modify `configs/approved_strategies.yaml` except to verify it stays `approved: []`.
- Do not enable paper/demo/live; do not modify broker/executor/order/live behavior.
- Do not call OANDA mutation/order APIs; do not use live credentials.
- Do not commit `.env`, credentials, SQLite DBs, raw candle dumps, huge CSVs, or bulky generated artifacts.
- Do not present exploratory findings as tradable edge.
- Any selected next thesis must be pre-committed in a later sprint before execution.

## 5. Candidate thesis lanes (to be scored in Phase 3)

A. Session / time-of-day behavior.
B. Volatility expansion / compression.
C. Cost / spread-aware tradeability filter.
D. Market-microstructure-style confirmation (sweep+displacement, break/retest, expansion, trap).
E. Single-pair specialization diagnostic (e.g. USD_JPY).
F. News / calendar / event lane revisit.
G. Pause strategy campaigns; deepen execution/cost/parity infrastructure.

## 6. Expected docs (deliverables)

- `POST_C022_FAMILY_RETIREMENT_AND_NEW_THESIS_SELECTION_001_PLAN.md` (this file, Phase 0).
- `C022_C023_PULLBACK_RESOLUTION_FAMILY_CLOSEOUT.md` (Phase 1).
- Updates to `STRATEGY_STATUS.md`, `EVIDENCE_INDEX.md`, `FUTURE_RESEARCH_BACKLOG.md`, and `EVIDENCE_MANIFEST.json` if freeze-safe (Phase 2).
- `NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md` (Phase 3).
- `NEXT_THESIS_SELECTION_DECISION.md` (Phase 4).
- `NEXT_SPRINT_PROMPT_AFTER_C022_FAMILY_CLOSEOUT.md` (Phase 5).
- `POST_C022_FAMILY_RETIREMENT_AND_NEW_THESIS_SELECTION_001_SUMMARY.md` (Phase 6).

## 7. Validation commands

- `pytest tests/ -q`
- `ruff check src tests scripts research`
- `python scripts/check_research_freeze.py`
- `python scripts/validate_research_archive.py`
- `python scripts/scan_artifacts_for_secrets.py`
- `git status --short`

## 8. Phase-0 baseline (executed on this branch off `main` @ `f693920`)

| Check | Result |
|---|---|
| Required diagnostic artifacts | All 6 present. |
| C020 / C021 / C022 verdicts | **REJECT** (unchanged). |
| C023 | scaffold-only, **not executed** (unchanged). |
| C024 | **does not exist** (no config, no source, no campaign artifact). |
| `configs/approved_strategies.yaml` | `approved: []` (verified, unchanged). |
| `pytest tests/ -q` | 1967 passed, 3 skipped (data-dependent skips; see §9). |
| `ruff check src tests scripts research` | All checks passed. |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED (incl. `loops_refuse`). |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED. |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED (value scan skipped — no real OANDA creds in env; pattern scan ran clean). |

## 9. Known pre-existing / environmental notes

- The 3 pytest skips are data-dependent and unrelated to this sprint:
  `tests/research/test_cost_atlas.py` (local H4 store absent) and two
  `tests/unit/entry_parity/test_compare_entries.py` cases (local C008 bespoke
  trade CSVs gitignored/absent in a fresh worktree). On clean `main` these are
  skips, not failures, in this worktree.
- The secret value-scan is skipped because no real OANDA credentials are sourced
  in this environment; this is the expected safe state for a docs-only sprint.

## 10. Explicit closeout statement

This sprint **approves no strategy, creates no CAMPAIGN_024, does not execute
C023, implements no strategy, and changes no verdict.** `approved_strategies.yaml`
remains `approved: []` and paper/demo/live remain blocked. Any next thesis chosen
here is a **research lane only** and must be independently pre-committed in a future
sprint before any execution.
