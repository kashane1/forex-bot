# USD_JPY Post-Entry Trade-Management Diagnostic — Sprint 001 Summary

**Date:** 2026-05-28 · **Type:** read-only diagnostic. Approves nothing, executes
nothing, creates no campaign, changes no verdict, claims no edge.

## 1. Branch

`research-usdjpy-post-entry-trade-management-diagnostic-001` (off the USD_JPY
microstructure entry-closeout tip `110181e`).

## 2. Commit hashes by phase

| Phase | Hash | Title |
|---|---|---|
| 0 | `48043b9` | branch, audit, plan |
| 1 | `e983d49` | post-entry event taxonomy |
| 2 | `63e9efd` | build post-entry diagnostic dataset |
| 3 | `cf7c8a0` | trade-management separation analysis |
| 4 | `07d9572` | counterfactual early-exit simulation |
| 5 | `beb3fbb` | trade-management readiness = NOT_READY |
| 6 | _this commit_ | final validation + summary |

## 3. Files changed by phase

- **0:** `docs/research/USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_001_PLAN.md`.
- **1:** `src/forex_bot/research/post_entry_trade_management.py`,
  `tests/unit/test_post_entry_trade_management.py`.
- **2:** `scripts/build_usdjpy_post_entry_trade_management_dataset.py`, `.gitignore`,
  `research/usdjpy_trade_management_diagnostic/{post_entry_dataset_manifest.json,usdjpy_post_entry_preview.csv}`.
- **3:** `scripts/analyze_usdjpy_post_entry_trade_management.py`,
  `research/usdjpy_trade_management_diagnostic/post_entry_analysis_summary.json`,
  `docs/research/USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_RESULT.md`.
- **4:** `scripts/simulate_usdjpy_post_entry_management_counterfactuals.py`,
  `research/usdjpy_trade_management_diagnostic/post_entry_counterfactuals.json`,
  `docs/research/USDJPY_POST_ENTRY_MANAGEMENT_COUNTERFACTUALS.md`.
- **5:** `docs/research/USDJPY_TRADE_MANAGEMENT_READINESS_DECISION.md`.
- **6:** this file.

Full per-trade parquet is **gitignored**; only manifests + small preview + summary/analysis
JSON committed. Docs + research artifacts + read-only research modules/scripts; no
strategy/broker/executor/config-gate code changed.

## 4. Dataset size and path coverage

306 USD_JPY C022 base trades — train 133, validation 173. Post-entry M15 path joined for
**299** (7 NO_BARS data-edge trades carry `None` events). All events evaluated only on
trades **still open at each horizon** (2/4/8/16 M15 bars). Realized mean R near-flat
(train −0.0017, validation +0.0004); overall hard-stop rate 0.562.

## 5. Post-entry event families implemented

`early_retest_hold`, `early_reclaim_failure`, `no_continuation`,
`early_adverse_expansion`, `early_favorable_displacement`, `trap_or_failed_breakout`,
`range_compression_after_entry`, `reached_plus_025/05`, `mae_by` (per-horizon
live-manageable); `time_to_first_{plus,minus}_*` (hindsight-only); `open_at`,
`bars_to_exit` (descriptive). Each labelled `live_manageable` / `hindsight_only` /
`descriptive`. 12 unit tests incl. long/short, trap, retest-hold, and a
no-lookahead-beyond-horizon test.

## 6. Strongest separation findings

EXIT-type events stably separate (among still-open trades): `early_reclaim_failure`
(hard-stop lift +0.19/+0.43 @ h2, win-rate lift −0.14/−0.31), `early_adverse_expansion`
@ h2/h4, `no_continuation` @ h4, and `trap_or_failed_breakout` (hard-stop lift
+0.13/+0.46). HOLD-type `reached_plus_05` raises win-rate (+0.04→+0.29, tautological).
But all EXIT-type signals also flag a meaningful minority of eventual **winners**
(winner-damage win-rate ~20–33% present-group).

## 7. Live-manageable vs hindsight-only distinction

37 live-manageable feature columns vs 6 hindsight-only. The strongest separators
(realized MAE-at-exit, full time-to-threshold) are **hindsight-only** and excluded from
the usefulness verdict by construction — they cannot drive a live decision.

## 8. Counterfactual simulation result

**Run** (Phase 3 found stable candidates). Five predeclared exit rules (next-bar-open
exit if flagged and still open). **Every rule reduced expectancy on both splits:**
early_reclaim_failure@h2 −0.134/−0.112R, @h4 −0.098/−0.090R; early_adverse_expansion@h2
−0.091/−0.077R; no_continuation@h4 −0.106/−0.065R; trap@h2 −0.124/−0.106R. The signals
flag trades that often recover before the stop, so early-exiting locks in avoidable
losses and cuts winners — even under optimistic, cost-free mid marks.

## 9. Winner damage analysis

Each exit rule cut 9–20 eventual winners per split, forfeiting ~0.7–4.5R of winner
excursion. This winner damage exceeds the stop-loss reduction in every case, which is
why all expectancy deltas are negative.

## 10. Hard-stop / straight-to-stop reduction

Descriptively, EXIT-type signals do flag higher hard-stop and straight-to-stop rates
among still-open trades. But translating that into an early exit **does not** net-reduce
losses once winner damage and trade recovery are accounted for (Phase 4) — the realized
stop/time exit already captures the information.

## 11. Trade-management readiness decision

**`NOT_READY`.** No live-manageable post-entry signal yields a net-useful management
rule; all counterfactual early-exit rules reduce expectancy. Recommendation: **close the
USD_JPY post-entry trade-management lane** — USD_JPY microstructure shows no actionable
edge at either the entry or the management layer. See
[`USDJPY_TRADE_MANAGEMENT_READINESS_DECISION.md`](USDJPY_TRADE_MANAGEMENT_READINESS_DECISION.md).

## 12. Whether C023 executed

**No.** C023 remains scaffold-only / not executed.

## 13. Whether C024 was created

**No.** No CAMPAIGN_024 exists (verified: no config, no source).

## 14. Whether any verdict changed

**No.** C022 REJECT; C023 scaffold-only; all prior verdicts untouched; no historical
metric rewritten.

## 15. Whether any strategy was approved

**No.** `configs/approved_strategies.yaml` remains `approved: []`.

## 16. Whether paper/demo/live remain blocked

**Yes.** No broker/executor/order/live code touched; no OANDA mutation/order calls;
freeze gate `loops_refuse` still passes.

## 17. Tests and validation commands run (Phase 6)

| command | result |
|---|---|
| `pytest tests/ -q` | **1996 passed, 3 skipped** (12 new post-entry tests; 3 data-dependent skips). |
| `ruff check src tests scripts research` | **All checks passed.** |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED.** |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED.** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** — value scan active for 2 practice credentials; none leaked. |
| `git status --short` | clean (all work committed). |

## 18. Pre-existing skips / failures

None as failures. 3 data-dependent pytest skips (two C008 entry-parity cases needing
gitignored CSVs; cost-atlas H4 store path) — unchanged from baseline.

## 19. Remaining blockers

None for this diagnostic. The full per-trade parquet is local-only (gitignored);
rebuild via the Phase 2/4 scripts with `.env` sourced.

## 20. Exact files to review first

1. [`USDJPY_TRADE_MANAGEMENT_READINESS_DECISION.md`](USDJPY_TRADE_MANAGEMENT_READINESS_DECISION.md) — the decision (NOT_READY) + recommendation.
2. [`USDJPY_POST_ENTRY_MANAGEMENT_COUNTERFACTUALS.md`](USDJPY_POST_ENTRY_MANAGEMENT_COUNTERFACTUALS.md) — the decisive result (early-exit hurts).
3. [`USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_RESULT.md`](USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_RESULT.md) — descriptive separation + winner damage.
4. `src/forex_bot/research/post_entry_trade_management.py` — the events (scrutinize liveness + no-lookahead).

## 21. Recommended next sprint

**Default: stop / hold the freeze.** Record USD_JPY microstructure (entry **and**
post-entry management) as closed — no actionable edge found at either layer. Pursue a
genuinely new external thesis only when one appears; otherwise pick a structurally
different lane from
[`NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md`](NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md)
(a thesis that changes *what is detected*, not another overlay on the C022 entry). No
further mining of these post-entry signals is sanctioned — the counterfactual already
shows acting on them is net-negative.
