# Next Sprint Prompt — After Exit Hypothesis Precommit

**Date:** 2026-05-27  
**Prior sprint:** `research-exit-hypothesis-precommit-001`  
**Recommended execution sprint:** `research-campaign-018-protective-stop-execution-001`  
**Branch suggestion:** `research-campaign-018-protective-stop-execution-001`

Copy the block below into a new agent session.

---

## Sprint prompt (copy from here)

```
We are executing CAMPAIGN_018 — mean-reversion protective stop exit hypothesis.

Branch: research-campaign-018-protective-stop-execution-001
Start from: research-exit-hypothesis-precommit-001

Context:
- Exit hypothesis precommit complete. Exactly ONE hypothesis pre-registered:
  delayed_reversion_protective_stop_after_1R (break-even stop after +1R MFE).
- Precommit docs (READ FIRST — do not deviate):
  - docs/research/CAMPAIGN_018_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md
  - docs/research/CAMPAIGN_018_EXIT_HYPOTHESIS_GATE_DESIGN.md
  - docs/research/CAMPAIGN_018_EXIT_HYPOTHESIS_IMPLEMENTATION_DESIGN.md
  - docs/research/EXIT_HYPOTHESIS_SELECTION_MEMO.md
- C008/C009 remain REJECT / research-only. Deduped forensic replay confirmed.
- configs/approved_strategies.yaml remains approved: [].
- Paper/demo/live remain blocked.
- Broad strategy search remains PAUSED.
- Test lockbox 2025-2026 is CLOSED until screening gates pass.

This IS a backtest execution sprint for CAMPAIGN_018 only.
This is NOT an approval sprint.
This is NOT a tuning sprint.
This is NOT paper/demo/live enablement.

Goal:
Implement mean_reversion_protective_stop 0.1.0-c018 exactly as precommitted,
run deduped backtests on train + validation (+ test ONLY if screening passes),
evaluate gates, produce diagnostic artifacts. Do not approve anything.

Hard rules:
- Do not approve any strategy.
- Do not edit configs/approved_strategies.yaml except verify approved: [].
- Do not enable paper/demo/live.
- Do not tune parameters (threshold stays 1.0R; stop 1.5x ATR; time 40 bars).
- Do not change entry rules from C008 frozen config.
- Do not add midline target or partial exits.
- Do not modify C008/C009 historical artifacts.
- Do not use validation winners to select parameters.
- Do not open test lockbox unless ALL screening gates pass.
- Do not call OANDA order APIs or place trades.
- Do not modify executor/broker live order behavior.
- Use deduped candle loading (keep_last) mandatory.
- All outputs: strategy_evidence: false until separate promotion review.
- Do not commit .env, credentials, SQLite DBs, or bulky trade CSVs.

PHASE 0 — truth audit
1. Verify branch/worktree.
2. Verify precommit docs exist (list above).
3. Verify deduped C008/C009 forensic artifacts present.
4. Run: pytest tests/ -q, ruff check src tests scripts research,
   python scripts/check_research_freeze.py,
   python scripts/validate_research_archive.py,
   python scripts/scan_artifacts_for_secrets.py
5. Create docs/research/CAMPAIGN_018_EXECUTION_001_PLAN.md
Commit.

PHASE 1 — implementation
1. Implement protective stop per IMPLEMENTATION_DESIGN.md.
2. Add configs/campaign_018_mean_reversion_protective_stop.yaml (frozen params).
3. Add unit tests with fixtures (no full SQLite in git).
4. Config guard: entry block must match C008.
Commit.

PHASE 2 — deduped backtest execution
1. Run train + validation on base cost (all 6 pairs).
2. Run validation stress_2x and full stress_15x per gate design.
3. Do NOT run test window unless screening passes.
4. Write compact JSON to research/campaign_018/ (see design doc).
5. Gitignore bulky trade CSVs under backtests/CAMPAIGN_018_mean_reversion_protective_stop/
Commit JSON + report doc only.

PHASE 3 — gate evaluation and baselines
1. Evaluate gates from CAMPAIGN_018_EXIT_HYPOTHESIS_GATE_DESIGN.md.
2. Compare vs C008/C009 deduped forensic + C011 null.
3. Run financing overlay on multi-day holds.
4. Create docs/research/CAMPAIGN_018_PROTECTIVE_STOP_RESULT.md
Commit.

PHASE 4 — conditional test lockbox
ONLY if screening gate PASS:
1. Run test window 2025-2026.
2. Evaluate T1-T4 gates.
If screening FAIL: document REJECT, lockbox stays closed.
Commit.

PHASE 5 — exit anatomy + MAE/MFE
1. Recompute exit anatomy and MAE/MFE on C018 outputs.
2. Compare stop/time/protective buckets vs C008 deduped.
3. Create docs/research/CAMPAIGN_018_EXIT_ANATOMY.md
Commit.

PHASE 6 — archive updates
Update EVIDENCE_INDEX, EVIDENCE_MANIFEST (precommit staged → executed label),
FUTURE_RESEARCH_BACKLOG. Do NOT add CAMPAIGN_018 to approved registry.
Do NOT mark strategy_evidence: true.
Commit.

PHASE 7 — final validation and summary
Run full validation suite + git status --short.
Create docs/research/CAMPAIGN_018_EXECUTION_001_SUMMARY.md with:
- branch, commits by phase, selected hypothesis recap
- train/val metrics, gates passed/failed
- test lockbox status
- vs C008/C009/null comparison
- whether approval changed (expected: no)
- recommended next sprint
Commit.

Final response must state explicitly: no approval, no paper/demo/live,
lockbox status, and verdict (REJECT or REVISE ceiling only).
```

---

## Notes for operator

- If financing overlay flips validation negative, run `research-financing-modeled-pnl-and-carry-readiness-001` before interpreting results.
- If engine exit-fill semantics differ from C008 on protective transition, run `infra-backtrader-exit-parity-diagnostics-001` before lockbox.
- Do not iterate exit rules within CAMPAIGN_018 after seeing validation — new hypothesis requires new campaign ID.
