# Next Sprint Prompt — CAMPAIGN_020 MTF Confluence Execution

**Date:** 2026-05-27  
**Prior sprint:** `research-mtf-confluence-candidate-020-scaffold-001`  
**Branch suggestion:** `research-campaign-020-mtf-confluence-execution-001`

Copy the block below into a new agent session.

---

## Sprint prompt (copy from here)

```
We are executing CAMPAIGN_020 evidence for multi_timeframe_confluence_pullback 0.1.0-c020.

Branch: research-campaign-020-mtf-confluence-execution-001
Start from: research-mtf-confluence-candidate-020-scaffold-001 (or main after merge)

Context:
- Scaffold + precommit complete: docs/research/CAMPAIGN_020_MTF_CONFLUENCE_PRECOMMIT.md
- Strategy: src/forex_bot/strategies/multi_timeframe_confluence_pullback.py
- Config: configs/campaign_020_mtf_confluence_pullback.yaml
- Runner: scripts/run_campaign_020_mtf_confluence.py (extend with --execute-evidence)
- CAMPAIGN_019 remains REJECT; do not retune C008–C019 families
- configs/approved_strategies.yaml remains approved: []
- Paper/demo/live remain blocked

Hard rules:
- Use next_bar_open for all approval-bound metrics
- Use htf_align / d1agg_htf for D1AGG (no incomplete HTF candles)
- RSI warmup_policy="nan" where RSI is used
- No strategy approval; no paper/demo/live
- No OANDA order/trade/position mutation APIs
- No live credentials
- No parameter tuning after seeing results
- Open test lockbox ONLY if train/validation gates AND Backtrader parity pass
- Maximum status: RESEARCH_PASS / PROMOTION_REVIEW_REQUIRED

PHASE 0 — audit
1. Verify branch, clean tree, approved: []
2. Run baseline: pytest, ruff, check_research_freeze, validate_research_archive, scan_artifacts_for_secrets
3. Confirm precommit doc unchanged vs implementation

PHASE 1 — train
- Run train split 2020-01-01 → 2022-12-31, base + 2× cost stress
- fill_timing next_bar_open, deduped candles keep_last
- Write research/campaign_020/ train artifacts

PHASE 2 — validation
- Run validation 2023-01-01 → 2024-12-31, base + 2× stress
- Compute all precommitted gates (see precommit doc)
- Compare to deduped C011 null (+0.010R margin)
- Document financing overlay sensitivity if holds > 1 day

PHASE 3 — Backtrader parity
- Implement lane adapter per CAMPAIGN_020_BACKTRADER_PARITY_DESIGN.md
- Run validation-window parity before any test lockbox

PHASE 4 — test lockbox (conditional)
- Only if train gate (exp >= 0), validation gates, and parity PASS
- Test window 2025-01-01 → 2026-05-20
- If gates fail: CAMPAIGN_020_TEST_LOCKBOX_NOT_OPENED.md

PHASE 5 — evidence docs
- CAMPAIGN_020_TRAIN_VALIDATION_RESULT.md
- CAMPAIGN_020_GATE_DECISION.md
- CAMPAIGN_020_FINAL_INTERPRETATION.md
- CAMPAIGN_020_BACKTRADER_PARITY_RESULT.md
- Update EVIDENCE_INDEX.md, EVIDENCE_MANIFEST.json, STRATEGY_STATUS.md, FUTURE_RESEARCH_BACKLOG.md

PHASE 6 — summary
- CAMPAIGN_020_MTF_CONFLUENCE_EXECUTION_001_SUMMARY.md with honest verdict
- Commits per phase; no approval; no secrets/DB/bulky artifacts committed

Final response must state: verdict, gates passed/failed, parity, lockbox, approved: [], no broker mutations.
```
