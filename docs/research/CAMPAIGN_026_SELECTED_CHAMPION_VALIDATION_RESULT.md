# CAMPAIGN_026 — selected-champion validation result

**Validation did NOT run — no champion was selected on train.**

Per the evidence protocol, validation runs **once on the train-selected champion only**,
and **only if** a champion exists. The Phase 7 train matrix produced
`REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE` (0/11 eligible, no champion, no single-pair
review), so promotion-style validation is **not run**.

Command (confirms the refusal path):
```
PYTHONPATH=$PWD/src python scripts/run_campaign_026_donchian_htf_timeframe_ladder.py \
  --validate-champion --validation-start 2023-07-01 --validation-end 2024-12-31
```
Output:
```json
{"validation_run": false, "reason": "no champion selected on train",
 "classification": "REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE"}
```
(written to `research/campaign_026/timeframe_ladder/validation_result.json`)

## Champion candidate / timeframe / parameters

**None** — n/a.

## Train selection metrics

n/a — no candidate passed the train filters (see
[`CAMPAIGN_026_TRAIN_TIMEFRAME_LADDER_RESULT.md`](CAMPAIGN_026_TRAIN_TIMEFRAME_LADDER_RESULT.md)).

## Validation metrics / gate table

n/a — validation not run. The validation gate definitions (for the record) would have
been: expectancy > 0; PF ≥ 1.05; trades ≥ 80 (M15/M30) or ≥ 150 (M3); ≥ 4/7 pairs
non-negative; 2× cost-stress expectancy ≥ 0; beat the C011 null by +0.010R; Backtrader
parity required before any promotion-review classification. None was evaluated.

## Protocol attestations

- **Validation ran once only?** It did **not** run at all (no champion).
- **Validation influenced selection?** **No** — selection is train-only by
  construction (`selection_uses_validation: false`); validation never executed.
- **Test lockbox opened?** **No** — the validation window 2023-07-01…2024-12-31 does
  not intersect the locked test window, and no test-window run occurred.
- **Any approval granted?** **No** — `approved_strategies.yaml` remains `approved: []`;
  paper/demo/live blocked.
