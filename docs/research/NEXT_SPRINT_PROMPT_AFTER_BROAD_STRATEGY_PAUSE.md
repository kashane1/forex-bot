# Next Sprint Prompt — After Broad Strategy Pause

**Date:** 2026-05-26  
**Prior sprint:** `research-broad-strategy-pause-and-roadmap-001`  
**Selected workstream:** `infra-observed-cost-and-spread-regime-diagnostics-001`  
**Branch suggestion:** `infra-observed-cost-and-spread-regime-diagnostics-001`

Copy the block below into a new agent session.

---

## Sprint prompt (copy from here)

```
We are executing a non-strategy infrastructure sprint: observed transaction-cost
and spread-regime diagnostics.

Branch: infra-observed-cost-and-spread-regime-diagnostics-001
Start from: research-broad-strategy-pause-and-roadmap-001

Context:
- Broad seven-pair pattern strategy search is PAUSED (BROAD_STRATEGY_SEARCH_PAUSE_MEMO).
- CAMPAIGN_011 deduped null: exp_r = -0.002915, 1180 trades.
- CAMPAIGN_015/016/017 are REJECT, WITHIN_NULL, all worsen under 2x cost.
- configs/approved_strategies.yaml remains approved: [].
- Paper/demo/live remain blocked.
- CAMPAIGN_018 must NOT be created.

This is NOT a strategy sprint.
This is NOT a tuning sprint.
This is NOT paper/demo/live enablement.

Goal:
Characterize transaction-cost drag from existing local deduped H4 bid/ask data.
Produce compact diagnostics and gating recommendations for FUTURE strategy
research only (no campaign, no approval).

Hard rules:
- Do not approve any strategy.
- Do not add anything to configs/approved_strategies.yaml.
- Do not enable paper/demo/live.
- Do not create CAMPAIGN_018 or any backtest campaign.
- Do not tune CAMPAIGN_015, CAMPAIGN_016, or CAMPAIGN_017.
- Do not call OANDA order APIs or place trades.
- Do not present diagnostics as tradable edge.
- Do not commit .env, credentials, SQLite DBs, or bulky artifacts.
- Use deduped candle loads (keep_last) consistent with C011–C017.

PHASE 0 — truth audit
1. Verify branch/worktree.
2. Confirm pause docs present:
   - docs/research/BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md
   - docs/research/NEXT_NON_STRATEGY_WORKSTREAM_DECISION.md
3. Run: pytest tests/ -q, ruff check src tests scripts research,
   python scripts/check_research_freeze.py,
   python scripts/validate_research_archive.py,
   python scripts/scan_artifacts_for_secrets.py
4. Create docs/research/OBSERVED_COST_SPREAD_DIAGNOSTICS_001_PLAN.md
Commit.

PHASE 1 — diagnostics implementation
1. Add script(s) under scripts/ or research/cost_diagnostics/ that:
   - Load deduped H4 bid/ask from existing campaign candle stores
   - Compute per-bar spread = ask - bid (and spread in pips where applicable)
   - Compute spread/ATR ratio using same ATR window as walk-forward campaigns
   - Aggregate distributions by:
     * instrument (7 pairs)
     * walk-forward fold test windows (8 folds, dates from CAMPAIGN_011 plan)
     * UTC session bucket (Asia / London / NY / overlap — define in plan)
     * weekday (Mon–Fri)
     * volatility regime (e.g. ATR percentile terciles)
   - Flag cost-hostile windows: e.g. top-decile spread/ATR cells per pair
2. Write outputs to research/cost_diagnostics/ (JSON summaries, small CSV ok)
3. Add unit tests with fixture candles (no full SQLite in git)
Commit.

PHASE 2 — human report
Create docs/research/OBSERVED_COST_SPREAD_DIAGNOSTICS_001.md with:
- Executive summary (descriptive only)
- Tables: median/p90 spread and spread/ATR by pair and session
- Fold-level cost comparison vs CAMPAIGN_011 null fold windows
- List of cost-hostile windows (pair × session × regime)
- Recommendations for FUTURE strategy gating (pre-registration required)
- Explicit disclaimer: not strategy evidence, not approval
Commit.

PHASE 3 — optional 2x cost linkage
Compare diagnostic spread/ATR cells to observed 2x cost stress deltas from
CAMPAIGN_015/016/017 gate_result.json (descriptive correlation only).
Commit.

PHASE 4 — archive touch-up
Update docs/research/EVIDENCE_INDEX.md and EVIDENCE_MANIFEST.json with
diagnostic artifact entries (strategy_evidence: false).
Do NOT change any campaign verdict.
Commit.

PHASE 5 — summary and validation
Re-run all validation commands from Phase 0.
Create docs/research/OBSERVED_COST_SPREAD_DIAGNOSTICS_001_SUMMARY.md
Confirm: no strategy approved, CAMPAIGN_018 not created, loops still blocked.
Commit.

Deliverables checklist:
- [ ] research/cost_diagnostics/*.json (compact)
- [ ] scripts or research module with tests
- [ ] OBSERVED_COST_SPREAD_DIAGNOSTICS_001.md
- [ ] No broker order API calls
- [ ] approved_strategies.yaml unchanged (approved: [])
```

---

## Expected outputs

| artifact | purpose |
|---|---|
| `docs/research/OBSERVED_COST_SPREAD_DIAGNOSTICS_001_PLAN.md` | Sprint plan |
| `docs/research/OBSERVED_COST_SPREAD_DIAGNOSTICS_001.md` | Human report |
| `research/cost_diagnostics/*.json` | Machine-readable summaries |
| `docs/research/OBSERVED_COST_SPREAD_DIAGNOSTICS_001_SUMMARY.md` | Close-out |

---

## Data references

- Fold windows: `research/null_baselines/campaign_011_deduped_null_baseline.json` → `fold_windows`
- Candle store: same SQLite paths as CAMPAIGN_011–017 (deduped `CandleRepo.list`)
- Cost stress reference: `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/walk_forward/gate_result.json` (and C016/C017)
