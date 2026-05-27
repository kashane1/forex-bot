# CAMPAIGN_019 Thesis Invalidation Execution 001 — Summary

**Date:** 2026-05-27  
**Sprint:** `research-campaign-019-thesis-invalidation-execution-001`  
**Final verdict:** **REJECT**

---

## 1. Branch name

`research-campaign-019-thesis-invalidation-execution-001`

---

## 2. Commit hashes by phase

| Phase | Commit | Description |
|---|---|---|
| 0 | `b985521` | Execution plan + truth audit |
| 1 | `d0d7ec9` | Thesis-invalidation strategy implementation |
| 2 | `a9ebce4` | Train/validation runner |
| — | `d1f9ef1` | Deduped C008/C009/C018 backtest evidence (comparison inputs) |
| 3 | `25d86d5` | Train/validation execution + artifacts |
| 4 | `87b3784` | Backtrader parity |
| 5–6 | `c08cb08` | Gate decision + interpretation |
| 7 | `c500232` | Archive updates |
| 8 | *(this commit)* | Final summary + test fix |

---

## 3. Files changed by phase

**Phase 0:** `docs/research/CAMPAIGN_019_THESIS_INVALIDATION_EXECUTION_001_PLAN.md`

**Phase 1:** `src/forex_bot/strategies/mean_reversion_thesis_invalidation.py`, `src/forex_bot/config.py`, `src/forex_bot/backtesting/engine.py`, `metrics.py`, `exporters.py`, `research/backtrader_exit_parity/*`, `tests/unit/test_mean_reversion_thesis_invalidation.py`

**Phase 2:** `scripts/run_campaign_019_thesis_invalidation.py`, `configs/campaign_019_mean_reversion_thesis_invalidation.yaml`, `scripts/run_backtrader_exit_parity.py`, `.gitignore`

**Phase 3:** `research/campaign_019/*.json`, `docs/research/CAMPAIGN_019_TRAIN_VALIDATION_RESULT.md`

**Phase 4:** `research/backtrader_exit_parity/c019_*`, `compare.py`, `docs/research/CAMPAIGN_019_BACKTRADER_PARITY_RESULT.md`

**Phases 5–6:** `CAMPAIGN_019_GATE_DECISION.md`, `CAMPAIGN_019_TEST_LOCKBOX_NOT_OPENED.md`, `CAMPAIGN_019_FINAL_INTERPRETATION.md`

**Phase 7:** `EVIDENCE_INDEX.md`, `EVIDENCE_MANIFEST.json`, `FUTURE_RESEARCH_BACKLOG.md`, `STRATEGY_STATUS.md`

**Phase 8:** this summary, `tests/unit/test_validate_research_archive.py`

---

## 4. Implementation summary

Implemented `mean_reversion_thesis_invalidation 0.1.0-c019` with C008-frozen entries and
precommitted z-score continuation invalidation exit (long z ≤ −3.0 / short z ≥ +3.0 at bar
close). Extended bespoke engine, trade metrics, Backtrader parity lane, and a dedicated
runner with all precommitted gates. No executor/broker changes.

---

## 5. Precommit followed exactly?

**Yes.** No parameter tuning, no entry/exit rule changes, no gate changes post-results,
no approval, no paper/demo/live, deduped inputs only, frozen C008 scope.

---

## 6. Train metrics

| Metric | Value |
|---|---|
| Trades | 219 |
| Expectancy | **−0.072 R** |
| Profit factor | 0.927 |
| Pairs positive | 3 / 6 |

---

## 7. Validation metrics

| Metric | Value |
|---|---|
| Trades | 138 |
| Expectancy | **+0.0962 R** |
| Profit factor | 1.1423 |
| Pairs positive | 6 / 6 |

---

## 8. Gate table summary

| Gate | Pass |
|---|---|
| Train exp ≥ 0 | **FAIL** |
| Validation exp > 0 | PASS |
| Validation PF ≥ 1.05 | PASS |
| Validation pairs ≥ 2 | PASS |
| Validation trades ≥ 30 | PASS |
| 2× cost stress val exp ≥ 0 | PASS |
| Beat C011 null + 0.010 R | PASS |
| Thesis invalidation 5–45% | PASS (12.6%) |
| Zero target exits | PASS |
| Zero protective exits | PASS |
| Train ≥ C008 deduped train | **FAIL** |
| Full stress_15x exp ≥ 0 | **FAIL** |
| Backtrader parity ±1 trade | PASS |

**Screening:** FAIL · **Verdict:** REJECT

---

## 9. Thesis-invalidation mechanism diagnostics

- Thesis invalidation exits: **122** (12.6% of runner aggregate trades)
- Median z at invalidation: **3.06**
- Hard stops: 551 · Time exits: 294
- Target exits: **0** · Protective exits: **0**
- Time-exit median R: **1.36 R** (below C008 ~3.29 R)

---

## 10. Backtrader parity result

**PASS / CLOSE_MATCH** — train 219/219 exact; validation 138/137 (±1); exit shares align.

---

## 11. Comparison to C008 deduped

| Split | C008 | C019 | Delta |
|---|---|---|---|
| Train exp | −0.025 R | −0.072 R | **Worse** |
| Val exp | +0.1612 R | +0.0962 R | Lower uplift |

---

## 12. Comparison to C009 deduped

| Split | C009 | C019 |
|---|---|---|
| Train exp | −0.0253 R | −0.072 R |
| Val exp | +0.1859 R | +0.0962 R |

C019 has zero target exits (C009 midline forbidden — satisfied).

---

## 13. Comparison to C018

| Split | C018 | C019 |
|---|---|---|
| Train exp | −0.1188 R | −0.072 R (better but still negative) |
| Val exp | +0.194 R | +0.0962 R |

C019 has zero protective exits (C018 form forbidden — satisfied).

---

## 14. Comparison to C011 deduped null

Validation C019 **+0.0962 R** vs null **−0.0029 R** — beat by **+0.0991 R** (exceeds +0.010 R margin). Not WITHIN_NULL.

---

## 15. 2× cost stress result

Validation stress 2×: **+0.0499 R**, PF 1.063, 138 trades — **PASS**.

---

## 16. Stress_15x result

Full-window stress 15×: **−0.0139 R**, PF 0.970 — **FAIL**.

---

## 17. Test lockbox opened?

**No.** Screening gates failed before lockbox eligibility.

---

## 18. Test metrics

Not applicable — test window not executed.

---

## 19. Final verdict

**REJECT** — thesis-invalidation exit hypothesis **falsified on train**. Validation uplift
and beat-null are insufficient per precommitted binding gates (C018 precedent).

---

## 20. Retuning performed?

**No.**

---

## 21. Strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`.

---

## 22. Paper/demo/live blocked?

**Yes.**

---

## 23. Archive/freeze validation

After Phase 8 fixes: `pytest`, `ruff`, `check_research_freeze.py`, `validate_research_archive.py`, and `scan_artifacts_for_secrets.py` — all **PASS**.

---

## 24. Remaining blockers

- C008-class mean-reversion train edge remains negative under exit-only modifications (C018, C019).
- Financing overlay still synthetic for REVISE interpretation.
- Broad strategy search remains paused.

---

## 25. Recommended next sprint

**`research-exit-hypothesis-precommit-003`** — pre-register a *different* falsifiable exit
mechanism (no C019 retuning), **or** `research-financing-manual-rate-source-expansion-001`
if financing overlay is prioritized before further exit campaigns.

---

## 26. Files to review first

1. [`CAMPAIGN_019_FINAL_INTERPRETATION.md`](CAMPAIGN_019_FINAL_INTERPRETATION.md)
2. [`research/campaign_019/gate_result.json`](../../research/campaign_019/gate_result.json)
3. [`CAMPAIGN_019_TRAIN_VALIDATION_RESULT.md`](CAMPAIGN_019_TRAIN_VALIDATION_RESULT.md)
4. [`CAMPAIGN_019_BACKTRADER_PARITY_RESULT.md`](CAMPAIGN_019_BACKTRADER_PARITY_RESULT.md)
5. [`research/campaign_019/mechanism_diagnostics.json`](../../research/campaign_019/mechanism_diagnostics.json)
