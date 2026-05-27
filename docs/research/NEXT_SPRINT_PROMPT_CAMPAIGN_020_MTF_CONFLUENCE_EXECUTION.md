# Next Sprint Prompt — CAMPAIGN_020 MTF Confluence Execution

**Date:** 2026-05-27  
**Prior sprint:** `research-mtf-confluence-candidate-020-scaffold-001`  
**Branch:** `research-campaign-020-mtf-confluence-execution-001`

Copy the block below into a new agent session.

---

## Sprint prompt (copy from here)

```
We are executing CAMPAIGN_020 evidence for multi_timeframe_confluence_pullback 0.1.0-c020.

Branch: research-campaign-020-mtf-confluence-execution-001

START (mandatory — before any work):
1. Check out latest clean main (fetch origin, fast-forward local main).
2. Create branch research-campaign-020-mtf-confluence-execution-001 from that main.
3. Merge or cherry-pick CAMPAIGN_020 scaffold commits if not yet on main; otherwise
   ensure scaffold files from research-mtf-confluence-candidate-020-scaffold-001 are present.
4. Run: git status --short
5. If research/financing_overlay_local_first/* (or any other unrelated paths) are
   modified, resolve BEFORE proceeding:
   - Revert if only timestamp/git metadata drift from a local overlay re-run.
   - Stash only if the user explicitly asked to keep local experiments.
   - Commit only if the user explicitly asked to keep intentional changes.
   Do NOT start this sprint with unrelated modifications hanging in the worktree.

Context:
- Scaffold + precommit complete: docs/research/CAMPAIGN_020_MTF_CONFLUENCE_PRECOMMIT.md
- Strategy: src/forex_bot/strategies/multi_timeframe_confluence_pullback.py
- Config: configs/campaign_020_mtf_confluence_pullback.yaml
- Runner: scripts/run_campaign_020_mtf_confluence.py (extend with --execute-evidence)
- CAMPAIGN_019 remains REJECT; do not retune C008–C019 families
- configs/approved_strategies.yaml remains approved: []
- Paper/demo/live remain blocked

Hard rules (gate-disciplined):
- next_bar_open is MANDATORY for all approval-bound metrics (no signal_bar_close rescue)
- Use htf_align / d1agg_htf for D1AGG (no incomplete HTF candles)
- RSI warmup_policy="nan" where RSI is used
- Do NOT tune CAMPAIGN_020 parameters after seeing train/validation results
- Run TRAIN then VALIDATION only first — no test window in Phase 1–2
- If TRAIN fails precommitted gates: STOP, classify REJECT, do NOT open test lockbox
- If VALIDATION looks good but TRAIN fails: do NOT rescue, retune, or run test anyway
- Open test lockbox ONLY if train gates pass AND validation gates pass AND Backtrader parity PASS
- Apply financing overlay sensitivity when average hold > 1 calendar day (document, do not claim observed financing is modeled)
- No strategy approval; no paper/demo/live
- No OANDA order/trade/position mutation APIs; no live credentials
- Maximum status: RESEARCH_PASS / PROMOTION_REVIEW_REQUIRED (never approved)

PHASE 0 — audit
1. Confirm clean worktree (git status --short empty)
2. Confirm approved_strategies.yaml is approved: []
3. Run baseline: pytest, ruff, check_research_freeze, validate_research_archive, scan_artifacts_for_secrets
4. Confirm precommit doc matches implementation (frozen parameters unchanged)

PHASE 1 — train ONLY
- Run train split 2020-01-01 → 2022-12-31, base + 2× cost stress
- fill_timing next_bar_open, deduped candles keep_last
- Write research/campaign_020/ train artifacts
- Evaluate train gate: expectancy >= 0 R under next_bar_open
- If train gate FAILS: write CAMPAIGN_020_TRAIN_VALIDATION_RESULT.md,
  CAMPAIGN_020_GATE_DECISION.md (REJECT), CAMPAIGN_020_TEST_LOCKBOX_NOT_OPENED.md,
  CAMPAIGN_020_FINAL_INTERPRETATION.md, update manifest/status — STOP (skip Phase 2–4 test)

PHASE 2 — validation ONLY (only if Phase 1 train gate passes)
- Run validation 2023-01-01 → 2024-12-31, base + 2× stress
- Compute all precommitted validation gates (see CAMPAIGN_020_MTF_CONFLUENCE_PRECOMMIT.md)
- Compare to deduped C011 null (+0.010R margin)
- Financing overlay sensitivity if average hold > 1 day
- If validation fails OR train had failed earlier: REJECT, no test lockbox

PHASE 3 — Backtrader parity (before any test)
- Implement/run lane per CAMPAIGN_020_BACKTRADER_PARITY_DESIGN.md on validation window
- If parity FAILS: REJECT or RESEARCH_INCONCLUSIVE per policy — no test lockbox

PHASE 4 — test lockbox (conditional — all must pass)
- Requires: train gate pass, validation gates pass, parity PASS
- Test window 2025-01-01 → 2026-05-20
- If any prerequisite failed: CAMPAIGN_020_TEST_LOCKBOX_NOT_OPENED.md only

PHASE 5 — evidence docs
- CAMPAIGN_020_TRAIN_VALIDATION_RESULT.md
- CAMPAIGN_020_GATE_DECISION.md
- CAMPAIGN_020_FINAL_INTERPRETATION.md
- CAMPAIGN_020_BACKTRADER_PARITY_RESULT.md
- Update EVIDENCE_INDEX.md, EVIDENCE_MANIFEST.json, STRATEGY_STATUS.md, FUTURE_RESEARCH_BACKLOG.md

PHASE 6 — summary
- CAMPAIGN_020_MTF_CONFLUENCE_EXECUTION_001_SUMMARY.md with honest verdict
- Commits per phase; no approval; no secrets/DB/bulky artifacts committed

Final response must state: verdict, train/validation gates passed/failed, parity, lockbox,
approved: [], no broker mutations, whether worktree was clean at start, no C020 retuning.
```
