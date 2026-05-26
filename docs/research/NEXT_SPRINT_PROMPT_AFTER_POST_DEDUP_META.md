# Next Sprint Prompt — After Post-Dedup Meta-Analysis

**Date:** 2026-05-26  
**Prior sprint:** `research-post-dedup-failure-meta-analysis-001`  
**Selected lane:** `pause broad strategy search`  
**Branch suggestion:** `research-pause-broad-search-deduped-001`

Copy the block below into a new agent session to execute the pause sprint.

---

## Sprint prompt (copy from here)

```
We are executing a research pause sprint after post-dedup failure meta-analysis.

Branch: research-pause-broad-search-deduped-001
Start from: research-post-dedup-failure-meta-analysis-001

Context:
- CAMPAIGN_015, CAMPAIGN_016, CAMPAIGN_017 are all REJECT on deduped canonical data.
- All three are WITHIN_NULL vs CAMPAIGN_011 deduped null baseline (exp_r = -0.002915).
- configs/approved_strategies.yaml remains approved: [].
- Paper/demo/live remain blocked.
- Post-dedup meta-analysis selected lane: PAUSE BROAD STRATEGY SEARCH.

This is NOT a strategy implementation sprint.
This is NOT a tuning sprint.
This is NOT paper/demo/live enablement.
This is NOT CAMPAIGN_018 creation.

Goal:
Document the pause, consolidate dedup-safe learnings, and define explicit re-entry
criteria before any new broad pattern-family campaign is scaffolded.

Hard rules:
- Do not approve any strategy.
- Do not add anything to configs/approved_strategies.yaml.
- Do not enable paper/demo/live.
- Do not call OANDA or broker APIs.
- Do not tune C015, C016, or C017.
- Do not create CAMPAIGN_018 or any new backtest campaign.
- Do not present exploratory findings as tradable edge.
- Do not use contaminated historical metrics as positive evidence.
- Do not commit .env, credentials, SQLite DBs, or bulky trade dumps.

PHASE 0 — truth audit
1. Verify branch/worktree.
2. Verify dedup-safe evidence paths still present:
   - research/null_baselines/campaign_011_deduped_null_baseline.json
   - backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/walk_forward/gate_result.json
   - backtests/CAMPAIGN_016_weekly_cross_sectional_momentum/walk_forward/gate_result.json
   - backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout/walk_forward/gate_result.json
   - research/post_dedup_meta/campaign_metric_matrix.json
   - research/post_dedup_meta/archetype_analysis.json
3. Run: pytest tests/ -q, ruff check, check_research_freeze.py,
   validate_research_archive.py, scan_artifacts_for_secrets.py
4. Create docs/research/PAUSE_BROAD_SEARCH_DEDUPED_001_PLAN.md
Commit.

PHASE 1 — pause charter
Create docs/research/BROAD_STRATEGY_SEARCH_PAUSE_CHARTER.md covering:
- Why broad search is paused (C015–C017 WITHIN_NULL cluster).
- What exploratory archetypes were considered and rejected (USD_JPY micro-positive,
  USD_CAD consistent negative, C016 concentration artifacts, fold cells that do
  not replicate across families).
- Explicit re-entry gates (from POST_DEDUP_NEXT_RESEARCH_LANE_DECISION.md).
- What work IS allowed during pause (infra, dedupe audits, financing observation
  capture, Backtrader parity for existing families — no new campaigns).
Commit.

PHASE 2 — update status registries (descriptive only)
Update docs/research/STRATEGY_STATUS.md and docs/research/EVIDENCE_INDEX.md to
reference:
- Post-dedup meta-analysis summary
- Pause charter
- Re-entry criteria
Do NOT change any campaign verdict. Do NOT approve strategies.
Commit.

PHASE 3 — optional infra backlog (documentation only)
Create docs/research/PAUSE_PERIOD_INFRA_BACKLOG.md listing deferred but valuable
work that does not require new campaigns:
- Backtrader fold-window parity for C016/C017 weekly state machines
- Observed financing capture pilot (already scripted; no live promotion)
- CAMPAIGN_011 deduped financing overlay re-run (local only)
No implementation required unless trivial doc cross-links.
Commit.

PHASE 4 — final validation and summary
Run all validation scripts. Create docs/research/PAUSE_BROAD_SEARCH_DEDUPED_001_SUMMARY.md.
Verify approved: [], paper/demo/live blocked, no CAMPAIGN_018.
Commit.

Final response must include:
1. Branch
2. Commits by phase
3. Pause rationale (1 paragraph)
4. Re-entry gates
5. Whether any strategy approved (expected: no)
6. Whether paper/demo/live blocked (expected: yes)
7. Files to review first
```

---

## Anti-overfit warnings for any future lab (if pause is lifted)

If a future sprint overrides this pause with a pair-specific or regime lab:

1. **Pre-register** the pair or regime *before* seeing fold results — no cherry-picking USD_JPY after the fact without a written hypothesis.
2. **Minimum trade count:** ≥ 120 trades per lab arm on deduped data; ≥ 30 per fold for fold-level claims.
3. **Beat-null threshold:** aggregate exp_r must exceed null centre + 0.05R, not merely “positive in 3/3 campaigns at 0.003R”.
4. **Compare against deduped null** — never pre-fix CAMPAIGN_005/011 contaminated metrics.
5. **Lab output only** — no `approved_strategies.yaml` edit, no paper/demo/live, no campaign number assignment until a separate pre-committed campaign sprint.
6. **Concentration guard:** reject pair-level claims where a single fold or ≤5 trades drives >50% of cumulative R.
7. **No retuning** of C015/C016/C017 parameters — lab must use frozen configs or explicitly new archetype stubs.

---

## If pause is later overridden for financing work instead

Use branch `research-financing-observed-capture-deduped-001` and scope to:

- Observed financing capture via existing pilot scripts (read-only OANDA if credentials present — optional).
- Cost-model documentation updates only.
- No MODELED financing promotion.
- No strategy approval.

Do not use this path unless the pause charter re-entry review explicitly authorizes it.
