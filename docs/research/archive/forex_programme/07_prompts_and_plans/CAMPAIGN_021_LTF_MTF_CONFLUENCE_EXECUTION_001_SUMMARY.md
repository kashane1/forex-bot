# CAMPAIGN_021 — LTF MTF Confluence Execution Sprint Summary

**Date:** 2026-05-28  
**Branch:** `research-campaign-021-ltf-mtf-confluence-execution-001`  
**Verdict:** **REJECT** (train gate fail)

## 1. Branch name

`research-campaign-021-ltf-mtf-confluence-execution-001`

## 2. Base branch / commit

`main` @ `85a8932` (materialization merged via `1c53150`)

## 3. Materialization merge

Yes — M1-derived M5/M15/H1/H4M1 materialized lane merged before re-execution.

## 4. Commit hashes by phase (post-materialization re-run)

| phase | commit | message |
|---|---|---|
| merge | `1c53150` | materialization infra merge |
| 0 | `5d59b2c` | post-materialization execution plan |
| 1 | `dc7fc56` | materialized loader verification |
| 2 | `9bd23b7` | data/feature preflight refresh |
| 3–4 | (this commit) | train evidence + REJECT gate |

## 5. Files changed by phase

| phase | primary files |
|---|---|
| 0 | `CAMPAIGN_021_EXECUTION_AFTER_M1_MATERIALIZATION_PLAN.md` |
| 1 | `CAMPAIGN_021_MATERIALIZED_DATA_LOADER_VERIFICATION.md`, loader tests |
| 2 | `data_feature_preflight.json`, `CAMPAIGN_021_DATA_FEATURE_PREFLIGHT_RESULT.md` |
| 3 | `train_*.json/csv`, `train_runtime_manifest.json` |
| 4 | `CAMPAIGN_021_GATE_DECISION.md`, `TEST_LOCKBOX_NOT_OPENED.md`, `FINAL_INTERPRETATION.md` |

## 6. Baseline validation

| command | result |
|---|---|
| `pytest tests/ -q` | PASS |
| `verify_m1_materialized_coverage.py` | PASS |
| `check_research_freeze.py` | PASS |
| `validate_research_archive.py` | PASS |
| `scan_artifacts_for_secrets.py` | PASS |

## 7. Materialized coverage verification

**PASS** — 7 pairs; 0 OHLC mismatches (pre-run artifact).

## 8. Data/feature preflight

**PASS** — ~21 s; `m1_rows_loaded: 0` all pairs; native D1AGG only.

## 9. Train metrics

| metric | value |
|---|---|
| trade_count | 1,438 |
| expectancy_r | **−0.0174** |
| profit_factor | 0.9642 |
| pairs_positive | 3 / 7 |
| runtime | ~40.4 min |

## 10. Train gate result

**FAIL** — `train_expectancy_gte_zero`

## 11. Validation ran?

**No**

## 12–15. Validation / stress / financing / parity

Not run (train-first discipline). Backtrader parity **NOT_RUN**.

## 16. Test lockbox opened?

**No**

## 17. Test result

N/A

## 18. Final verdict

**REJECT**

## 19. vs C020 train stability

C020 train −0.035 R / 353 trades → C021 −0.0174 R / 1,438 trades. Improved per-trade loss rate but still negative; ~4× turnover on M15.

## 20–23. Turnover / pairs / stop-hold

1,438 trades; 57% stop / 43% time exits; EUR_USD and USD_CHF largest drag; GBP_USD best pair (+0.117 R).

## 24–29. Safety checklist

| item | expected | actual |
|---|---|---|
| CAMPAIGN_021 approved | no | no |
| approved: [] | yes | yes |
| paper/demo/live | blocked | blocked |
| OANDA mutations | no | no |
| live env | no | no |
| secrets committed | no | no |
| materialized coverage | PASS | PASS |
| C020 REJECT | unchanged | unchanged |

## 30. Validation commands

pytest, ruff (pre-existing unrelated warnings), freeze, archive, secrets, materialized coverage.

## 31. WARN / BLOCKED

M1 corpus WARN (calendar gaps); validation BLOCKED by train fail; parity NOT_RUN.

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
| Data load | SQLite H4 | materialized M15/H1/H4M1 (~40 min train) | Infra faster; edge unchanged |
| Validation | +0.053 R (ran) | NOT_RUN | No rescue after train fail |
| Verdict | REJECT | REJECT | LTF did not pass train gate |

## No approval

`configs/approved_strategies.yaml` remains `approved: []`.
