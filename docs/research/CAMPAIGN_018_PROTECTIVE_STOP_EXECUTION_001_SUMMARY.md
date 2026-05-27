# CAMPAIGN_018 Protective Stop Execution — Summary

**Date:** 2026-05-27  
**Branch:** `research-campaign-018-protective-stop-execution-001`  
**Sprint ID:** `CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001`

> **Research execution complete** — `strategy_evidence: true`, `not_approved: true`. **REJECT.**

---

## 1. Branch name

`research-campaign-018-protective-stop-execution-001`

---

## 2. Commit hashes by phase

| phase | commit |
|---|---|
| 0 | `a48a8ca` |
| 1 | `adae664` |
| 2 | `2ec55d3` |
| 3–5 | `0e6896c` |
| 6 | *(this commit)* archive updates |
| 7 | *(final summary commit)* |

---

## 3. Files changed by phase

| phase | files |
|---|---|
| 0 | `CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001_PLAN.md` |
| 1 | engine, metrics, exporters, strategy, config, unit tests |
| 2 | `run_campaign_018_protective_stop.py`, runner tests, `.gitignore` |
| 3–5 | `research/campaign_018/*.json`, result/gate/interpretation docs |
| 6 | EVIDENCE_INDEX, MANIFEST, BACKLOG, STRATEGY_STATUS |
| 7 | this summary |

---

## 4. Implementation summary

- `MeanReversionProtectiveStopStrategy` — C008-identical entries, no target
- `BacktestEngine.protective_stop_after_r` — break-even at +1R MFE (backtest-only)
- Trade records capture protective_stop_armed/exit fields
- Runner with precommitted gate evaluation on deduped candles

---

## 5. Precommit followed exactly?

**Yes.** Frozen C008 entries, +1.0R threshold, no ratchet, no target, no gate changes, no test without screening pass.

---

## 6. Train metrics

236 trades · expectancy **−0.119 R** · PF **0.92** · 2/6 pairs positive

---

## 7. Validation metrics

142 trades · expectancy **+0.194 R** · PF **1.58** · 6/6 pairs positive

---

## 8. Gate table summary

| gate | result |
|---|---|
| train exp ≥ 0 | **FAIL** |
| validation exp > 0 | PASS |
| validation PF ≥ 1.05 | PASS |
| pairs ≥ 2 | PASS |
| trades ≥ 30 | PASS |
| 2× stress val exp ≥ 0 | PASS (+0.178) |
| beat C011 null | PASS |
| mechanism active | PASS (53.3%) |
| zero targets | PASS |
| full stress_15x | **FAIL** |

**Screening FAIL → REJECT**

---

## 9. Protective-stop mechanism diagnostics

53.3% armed · 37.0% protective_stop exits · 47.4% hard stops · 16.4% time · **0 targets**

---

## 10. Comparison to C008 deduped

| split | C008 exp R | C018 exp R |
|---|---:|---:|
| train | −0.025 | **−0.119** |
| validation | +0.161 | **+0.194** |

---

## 11. Comparison to C009 deduped

| split | C009 exp R | C018 exp R |
|---|---:|---:|
| train | −0.025 | −0.119 |
| validation | +0.186 | +0.194 |

C018 avoids target exits (C009 had ~41% targets).

---

## 12. Comparison to C011 deduped null

Validation +0.194 R vs null −0.003 R — **ABOVE_NULL** (not WITHIN_NULL).

---

## 13. 2× cost stress result

Validation expectancy **+0.178 R**, PF **1.49**, 5/6 pairs positive — **PASS**.

---

## 14. Test lockbox opened?

**No** — screening failed.

---

## 15. Test metrics

Not run.

---

## 16. Final verdict

**REJECT** — protective-stop-after-+1R hypothesis falsified on train gate.

---

## 17. Retuning performed?

**No.**

---

## 18. Any strategy approved?

**No** (`approved: []`).

---

## 19. Paper/demo/live blocked?

**Yes.**

---

## 20. Archive/freeze validation

pytest **1660+ passed**, ruff **PASS**, freeze/archive **PASS** (after summary doc).

---

## 21. Remaining blockers

- Train-negative MR family persists
- Financing unmodeled on 40-bar holds
- Broad strategy search paused
- No approved strategies

---

## 22. Recommended next sprint

**`research-financing-modeled-pnl-and-carry-readiness-001`** — C018 validation uplift cannot be interpreted fairly without financing on multi-day holds; also needed before any future exit variant comparison.

---

## 23. Files to review first

1. [`CAMPAIGN_018_FINAL_INTERPRETATION.md`](CAMPAIGN_018_FINAL_INTERPRETATION.md)
2. [`CAMPAIGN_018_TRAIN_VALIDATION_RESULT.md`](CAMPAIGN_018_TRAIN_VALIDATION_RESULT.md)
3. [`CAMPAIGN_018_GATE_DECISION.md`](CAMPAIGN_018_GATE_DECISION.md)
4. [`research/campaign_018/gate_result.json`](../../research/campaign_018/gate_result.json)
5. [`research/campaign_018/mechanism_diagnostics.json`](../../research/campaign_018/mechanism_diagnostics.json)
6. [`research/campaign_018/metrics_summary.json`](../../research/campaign_018/metrics_summary.json)
