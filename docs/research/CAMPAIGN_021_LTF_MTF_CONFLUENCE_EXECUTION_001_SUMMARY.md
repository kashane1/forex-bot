# CAMPAIGN_021 — LTF MTF Confluence Execution Sprint Summary

**Date:** 2026-05-28  
**Branch:** `research-campaign-021-ltf-mtf-confluence-execution-001`  
**Verdict:** **REJECT** (train gate fail)

## 1. Branch name

`research-campaign-021-ltf-mtf-confluence-execution-001`

## 2. Base branch / commit

`main` @ `dc8e0cb`

## 3. Commit hashes by phase

| phase | commit | message |
|---|---|---|
| 0 | `43e3908` | execution sprint plan |
| 1 | `4a2d59b` | runner hardening |
| 2 | `a34be3f` | data feature preflight |
| perf | `376ec37` | HTF frame cache for backtests |
| 3–4 | `684e94b` | train evidence + gate REJECT |
| 9–10 | `TBD` | archive + this summary |

## 4. Files changed by phase

| phase | primary files |
|---|---|
| 0 | `CAMPAIGN_021_LTF_MTF_CONFLUENCE_EXECUTION_001_PLAN.md` |
| 1 | `run_campaign_021_ltf_mtf_confluence.py`, `campaign_021_gates.py`, `campaign_021_loader.py` |
| 2 | `data_feature_preflight.json`, `CAMPAIGN_021_DATA_FEATURE_PREFLIGHT_RESULT.md` |
| 3 | `train_*.json/csv`, `backtests/CAMPAIGN_021_ltf_mtf_confluence/train/` |
| 4 | `CAMPAIGN_021_GATE_DECISION.md`, `TEST_LOCKBOX_NOT_OPENED.md`, `FINAL_INTERPRETATION.md` |
| 7 | `CAMPAIGN_021_BACKTRADER_PARITY_RESULT.md` (NOT_RUN) |
| 9–10 | `EVIDENCE_*`, `STRATEGY_STATUS.md`, this summary |

## 5. Baseline validation

| command | result |
|---|---|
| `pytest tests/ -q` | PASS (after summary commit) |
| `ruff check` | WARN pre-existing fill-timing scripts |
| `check_research_freeze.py` | PASS |
| `validate_research_archive.py` | PASS (after manifest commit_hash) |
| `scan_artifacts_for_secrets.py` | PASS |

## 6. Data/feature preflight

**PASS** — all 7 pairs; 0 lookahead violations; native D1AGG only.

## 7. Train metrics

| metric | value |
|---|---|
| trade_count | 1,438 |
| expectancy_r | **−0.0174** |
| profit_factor | 0.9642 |
| pairs_positive | 3 / 7 |

## 8. Train gate result

**FAIL** — `train_expectancy_gte_zero`

## 9. Validation ran?

**No**

## 10–13. Validation / stress / financing

Not run (train-first discipline).

## 14. Backtrader parity

**NOT_RUN**

## 15. Test lockbox opened?

**No**

## 16. Test result

N/A

## 17. Final verdict

**REJECT**

## 18. vs C020 train stability

C020 train −0.035 R / 353 trades → C021 −0.0174 R / 1,438 trades. Improved but still negative.

## 19–21. Turnover / pairs / stop-hold

Higher M15 turnover; EUR/CHF worst pairs; 2×ATR / 32-bar time stop precommitted.

## 22–29. Safety checklist

| item | expected | actual |
|---|---|---|
| CAMPAIGN_021 approved | no | no |
| approved: [] | yes | yes |
| paper/demo/live | blocked | blocked |
| executor changed | no | no |
| OANDA mutations | no | no |
| live env | no | no |
| secrets committed | no | no |
| raw M1/DB staged | no | no (raw trades gitignored) |
| C020 REJECT | unchanged | unchanged |

## 30. Validation commands

Listed in §5.

## 31. WARN / BLOCKED

M1 corpus WARN (calendar gaps); Backtrader parity NOT_RUN; validation BLOCKED by train fail.

## 32. Recommended next sprint

New structural hypothesis via new precommit — not C021 retune.

## 33. Review first

1. `CAMPAIGN_021_GATE_DECISION.md`
2. `CAMPAIGN_021_TRAIN_RESULT.md`
3. `CAMPAIGN_021_FINAL_INTERPRETATION.md`
4. `research/campaign_021/train_metrics.json`

## Gate table

| Gate | Status | Metric | Threshold | Action taken |
|---|---|---|---|---|
| Train expectancy ≥ 0 | FAIL | −0.0174 R | ≥ 0 | REJECT; STOP |
| Validation | NOT_RUN | — | — | Skipped |
| 2× cost stress | NOT_RUN | — | ≥ 0 | Skipped |
| Backtrader parity | NOT_RUN | — | PASS | Skipped |
| Test lockbox | CLOSED | — | all gates | Not opened |

## C020 vs C021

| Area | C020 H4 | C021 M15 | Interpretation |
|---|---|---|---|
| Train exp R | −0.035 | −0.0174 | Better but still negative |
| Train trades | 353 | 1,438 | Much higher LTF turnover |
| Validation | +0.053 R (ran) | NOT_RUN | No rescue after train fail |
| Verdict | REJECT | REJECT | LTF did not pass train gate |

## No approval

`configs/approved_strategies.yaml` remains `approved: []`.
