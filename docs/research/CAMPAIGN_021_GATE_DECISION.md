# CAMPAIGN_021 — Gate Decision

**Date:** 2026-05-28  
**Final verdict:** **REJECT**  
**Campaign:** `lower_timeframe_mtf_confluence_entry 0.1.0-c021`

## Gate table

| Gate | Status | Metric | Threshold | Action taken |
|---|---|---|---|---|
| Train expectancy ≥ 0 | **FAIL** | −0.0174 R | ≥ 0 | Classified REJECT |
| Train trade count sanity | PASS | 1,438 | ≥ 30 | — |
| Train provenance | PASS | hybrid M1 + native D1AGG | enforced | — |
| Validation expectancy > 0 | **NOT_RUN** | — | > 0 | Skipped (train fail) |
| Validation PF ≥ 1.05 | **NOT_RUN** | — | ≥ 1.05 | Skipped |
| Validation trades ≥ 150 | **NOT_RUN** | — | ≥ 150 | Skipped |
| Validation pairs ≥ 4/7 | **NOT_RUN** | — | ≥ 4 | Skipped |
| 2× cost stress val ≥ 0 | **NOT_RUN** | — | ≥ 0 | Skipped |
| Beat C011 null +0.010R | **NOT_RUN** | — | > −0.0129 R | Skipped |
| Backtrader parity | **NOT_RUN** | — | PASS | Skipped (train fail) |
| Test lockbox | **CLOSED** | — | all pre-test gates | Not opened |

## Train-first discipline

Train expectancy failed. Per precommit and execution prompt:

- No validation rescue
- No parameter retuning
- No Backtrader parity run
- No test lockbox

## Comparison to CAMPAIGN_020 (H4 execution, REJECT)

| metric | C020 H4 train | C021 M15 train |
|---|---|---|
| expectancy_r | −0.035 | −0.0174 |
| trade_count | 353 | 1,438 |
| pairs_positive | (see C020) | 3/7 |

M15 execution improved train expectancy versus C020 but **did not** achieve a non-negative train gate. Higher trade count indicates materially higher turnover on the shorter execution bar.

## Maximum status

REJECT — not RESEARCH_PASS. No entry in `approved_strategies.yaml`.

## No approval

Paper / demo / live remain blocked.
