# CAMPAIGN_027_VALIDATION_NOT_RUN

**Status:** TRAIN/VALIDATION EXECUTION — Phase 5 / **VALIDATION NOT RUN** (train
gates failed) / REJECT_TRAIN_GATE / TEST_LOCKBOX_CLOSED / NOT_APPROVED. Branch
`research-campaign-027-h4-filtered-zscore-reversion-train-validation-001`.

---

## Why validation was not run

The pre-registered protocol ([plan](CAMPAIGN_027_TRAIN_VALIDATION_001_PLAN.md),
Phase 5; [next-sprint prompt](NEXT_SPRINT_PROMPT_AFTER_CAMPAIGN_027_SCAFFOLD.md))
runs validation **once, only if the train gates pass**. Validation is confirmation,
never selection and never a rescue.

Train **failed 4 of 8 binding gates** (see
[`CAMPAIGN_027_TRAIN_RESULT.md`](CAMPAIGN_027_TRAIN_RESULT.md)):

1. profit factor 1.043 < 1.05;
2. years non-negative 1/3 (2020 and 2021 negative; only 2022 positive);
3. 2× cost stress expectancy −0.00007745 < 0;
4. filter-ablation: `f_strong_extension` only reduces sample (does not add edge).

Therefore the runner did **not** execute the validation window. The validation
artifacts (`trade_ledger_validation.csv`, `pair/year/side_metrics_validation.csv`,
`validation_metrics.json`) are emitted as **empty placeholders** with
`validation_run = false`; `matched_null_result.json` / `cost_stress_2x.json` /
`filter_ablation_confirmation.json` carry `{"validation": {"validation_run":
false}}`.

## No re-tune, no rescue

The frozen rule failed; per the freeze the verdict is **REJECT**, not a re-tune.
No parameters were changed, no gate was weakened after seeing results, no matrix
was added, no long side was enabled, and the validation/test windows were not
mined to recover the result.

## Classification

`REJECT_TRAIN_GATE / TEST_LOCKBOX_CLOSED / NOT_APPROVED` (from
`research/campaign_027/train_validation/gate_result.json`).

Per-the-prompt routing: skip the validation-result phase and proceed to
edge-discovery confirmation (Phase 6, already emitted on train), recency/robustness
interpretation (Phase 7), Backtrader parity readiness (Phase 8 → DEFER), final
interpretation (Phase 9), and status/backlog updates (Phase 10).

## No-approval statement

No strategy is approved. `configs/approved_strategies.yaml` stays `approved: []`.
The test lockbox was not opened. Paper/demo/live remain blocked. No
broker/executor/OANDA endpoint was touched. Backtrader parity is moot (the rule
was rejected before parity).
</content>
