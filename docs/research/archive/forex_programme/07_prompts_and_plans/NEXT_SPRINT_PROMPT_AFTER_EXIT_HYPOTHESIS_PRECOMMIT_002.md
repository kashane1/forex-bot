# Next Sprint Prompt — After Exit Hypothesis Precommit 002

**Date:** 2026-05-27  
**Prior sprint:** `research-exit-hypothesis-precommit-002`  
**Recommended execution sprint:** `research-campaign-019-thesis-invalidation-execution-001`  
**Branch suggestion:** `research-campaign-019-thesis-invalidation-execution-001`

Copy the block below into a new agent session.

---

## Sprint prompt (copy from here)

```
We are executing CAMPAIGN_019 — mean-reversion thesis invalidation exit hypothesis.

Branch: research-campaign-019-thesis-invalidation-execution-001
Start from: research-exit-hypothesis-precommit-002

Context:
- Exit hypothesis precommit 002 complete. Exactly ONE hypothesis pre-registered:
  thesis_invalidation_zscore_continuation_exit (exit when z-score reaches ±3.0
  continuation beyond ±2.0 entry band).
- Precommit docs (READ FIRST — do not deviate):
  - docs/research/CAMPAIGN_019_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md
  - docs/research/CAMPAIGN_019_EXIT_HYPOTHESIS_GATE_DESIGN.md
  - docs/research/CAMPAIGN_019_EXIT_HYPOTHESIS_IMPLEMENTATION_DESIGN.md
  - docs/research/EXIT_HYPOTHESIS_PRECOMMIT_002_SELECTION_MEMO.md
  - docs/research/CAMPAIGN_018_FAILURE_ANALYSIS_FOR_NEXT_EXIT_HYPOTHESIS.md
- C008/C009/C018 remain REJECT. C018 +1R break-even protective stop falsified on train.
- Backtrader parity hardened (±1 trade, home_currency_v1, engine_aligned).
- configs/approved_strategies.yaml remains approved: [].
- Paper/demo/live remain blocked.
- Broad strategy search remains PAUSED.
- Test lockbox 2025-2026 is CLOSED until screening gates pass.
- Financing sample path PAUSED — synthetic overlay mandatory for interpretation.

This IS a backtest execution sprint for CAMPAIGN_019 only.
This is NOT an approval sprint.
This is NOT a tuning sprint.

Goal:
Implement mean_reversion_thesis_invalidation 0.1.0-c019 exactly as precommitted,
run deduped backtests on train + validation (+ test ONLY if screening passes),
evaluate gates, run Backtrader parity, produce diagnostic artifacts.
Do not approve anything.

Hard rules:
- Do not approve any strategy.
- Do not edit configs/approved_strategies.yaml except verify approved: [].
- Do not enable paper/demo/live.
- Do not tune parameters (z invalidation stays ±3.0; stop 1.5x ATR; time 40 bars).
- Do not change entry rules from C008 frozen config.
- Do not add midline target, protective stop, or partial exits.
- Do not modify C008/C009/C018 historical artifacts.
- Do not use validation winners to select parameters.
- Do not open test lockbox unless ALL screening gates pass.
- Do not call OANDA order APIs or place trades.
- Use deduped candle loading (keep_last) mandatory.
- Backtrader parity: ±1 trade tolerance, CLOSE_MATCH exits.
- All outputs: strategy_evidence: true for campaign results, not_approved: true.
- Do not commit .env, credentials, SQLite DBs, or bulky trade CSVs.

PHASE 0 — truth audit
1. Verify branch/worktree.
2. Verify precommit docs exist (list above).
3. Verify Backtrader hardened parity artifacts present.
4. Run validation suite (pytest, ruff, freeze, archive, secrets).
5. Create docs/research/CAMPAIGN_019_EXECUTION_001_PLAN.md
Commit.

PHASE 1 — implementation
1. Implement thesis invalidation per IMPLEMENTATION_DESIGN.md.
2. Add configs/campaign_019_mean_reversion_thesis_invalidation.yaml.
3. Unit tests with fixtures.
4. Config guard: entry block must match C008.
Commit.

PHASE 2 — deduped backtest execution
1. Run train + validation on base cost (all 6 pairs).
2. Run validation stress_2x and full stress_15x.
3. Write research/campaign_019/*.json summaries.
Commit.

PHASE 3 — gate evaluation
1. Evaluate all gates from GATE_DESIGN.md.
2. Compare vs C008/C009/C018/C011.
3. Mechanism diagnostics (thesis_invalidation rate, time MFE).
4. Financing overlay report.
5. Open test ONLY if screening passes.
Commit.

PHASE 4 — Backtrader parity
1. Extend parity lane for C019 if needed.
2. Re-run parity; confirm ±1 trade.
Commit.

PHASE 5 — interpretation docs
1. CAMPAIGN_019_TRAIN_VALIDATION_RESULT.md
2. CAMPAIGN_019_FINAL_INTERPRETATION.md
3. CAMPAIGN_019_TEST_LOCKBOX_NOT_OPENED.md (if screening fails)
Commit.

PHASE 6 — archive updates + summary
1. Update EVIDENCE_INDEX, MANIFEST, BACKLOG, STRATEGY_STATUS.
2. CAMPAIGN_019_EXECUTION_001_SUMMARY.md with 20-item close-out.
Commit.

Final response must state: verdict, gate table, mechanism rates, vs C008/C018,
Backtrader parity, test lockbox status, no approval confirmation.
```

---

## If human chooses NOT to execute CAMPAIGN_019

Alternative next sprint: `research-financing-manual-rate-source-expansion-001` if financing
blocker prioritized over exit execution — see FUTURE_RESEARCH_BACKLOG.md.
