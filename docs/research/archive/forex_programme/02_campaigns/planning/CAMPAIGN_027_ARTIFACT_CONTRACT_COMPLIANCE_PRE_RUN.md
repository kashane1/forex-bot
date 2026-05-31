# CAMPAIGN_027_ARTIFACT_CONTRACT_COMPLIANCE_PRE_RUN

**Status:** TRAIN/VALIDATION EXECUTION — Phase 3 / NOT_APPROVED / TEST_LOCKBOX_CLOSED.
Branch `research-campaign-027-h4-filtered-zscore-reversion-train-validation-001`.

Before any evidence is interpreted, this phase verifies the runner can emit **all**
artifact schemas required by
[`research/campaign_027/artifact_contract.json`](../../research/campaign_027/artifact_contract.json)
/ [the contract doc](CAMPAIGN_027_EDGE_DISCOVERY_ARTIFACT_CONTRACT.md). Run via the
bounded, lockbox-safe schema check:

```
PYTHONPATH=$PWD/src python scripts/run_campaign_027_h4_filtered_zscore_reversion.py \
    --artifact-schema-check
```

`--artifact-schema-check` runs the full pipeline on a **bounded** sub-window
(train 2020 / validation 2021) writing to
`research/campaign_027/train_validation/schema_check/`. It never reads the test
window. The check is reproducible; the bounded output directory is **not
committed** (it is regenerated on demand).

---

## Result

**`all_required_present = true`; `blocked = null`. Train/validation may proceed.**

- 22/22 required artifacts emitted.
- 0 missing files.
- 0 missing fields on the three contract-critical ledgers.
- Exit code 0.

## Required artifacts (all emitted)

`run_manifest.json`, `candidate_registry.json`, `signal_ledger.csv`,
`trade_ledger_train.csv`, `trade_ledger_validation.csv`, `filter_stage_ledger.csv`,
`signal_funnel_ledger.csv`, `train_metrics.json`, `validation_metrics.json`,
`gate_result.json`, `pair_metrics_train.csv`, `pair_metrics_validation.csv`,
`year_metrics_train.csv`, `year_metrics_validation.csv`, `side_metrics_train.csv`,
`side_metrics_validation.csv`, `cost_stress_2x.json`, `matched_null_result.json`,
`filter_ablation_confirmation.json`, `recency_risk_report.json`,
`artifact_contract_compliance.json`, `blocked_or_warning_conditions.json`.

## Ledger field verification (against the contract)

| ledger | contract-required fields | emitted header | match |
|---|---|---|---|
| `signal_ledger.csv` | instrument, signal_time_utc, side, timeframe, zscore, atr14, atr_percentile, session_bucket, f_low_vol, f_strong_extension, f_quiet_session, entered | identical (+ diagnostic long rows, `entered=false`) | ✅ |
| `trade_ledger_*.csv` | instrument, side, units, entry_time, exit_time, entry_price, exit_price, stop_price, pnl, r_multiple, bars_held, spread_paid_pips, exit_reason, fill_timing | identical (short_only entered) | ✅ |
| `signal_funnel_ledger.csv` | trigger, f_low_vol_pass, f_strong_extension_pass, f_quiet_session_pass, log_return, log_return_post_cost_conservative, r_multiple | identical (+ instrument, signal_time_utc, log_return_post_cost) | ✅ |

`filter_stage_ledger.csv` carries the ablation stage table
(`split, kind, stage, filters_applied, n, reduction_ratio, expectancy,
post_cost_expectancy, hit_rate`) — the `filter_ablation` decomposition input.

## Metadata items 4–12 (contract)

- **4 pair/side/session** — on signal + trade ledgers (session derivable from UTC
  timestamp; `session_bucket` also carried explicitly).
- **5 hold duration** — `bars_held` per trade.
- **6 spread/cost** — `spread_paid_pips` per trade; both optimistic and
  conservative post-cost figures (`pnl` = conservative binding; `pnl_optimistic`,
  `cost_optimistic`, `cost_conservative` carried).
- **7 split-window tag** — `split` column on every ledger row.
- **8 candidate registry + matrix** — `candidate_registry.json` (single frozen
  candidate; `single_candidate=true`).
- **9 timeframe column** — `timeframe = H4` explicit on signal + trade ledgers.
- **10 null-benchmark fields** — `instrument, side, entry_time, bars_held` +
  derivable session/weekday feed the matched-null reconstruction; C011 deduped
  null referenced in the artifact contract.
- **11 reproducibility manifest** — `run_manifest.json` carries `commit_hash`,
  `input_data_path`, `dedupe_policy`, train/validation windows, `precommitted_rule`,
  `lab_modules`, and `strategy_evidence` (true for the campaign's own evidence;
  `approved`/`promotion_eligible`/`paper_demo_live_enabled` all false).
- **12 random-seed metadata** — `random_seed_metadata.matched_null_seeds` =
  `range(0,50)` in the manifest and in `matched_null_result.json`.

## Blocked conditions

None. `BLOCKED_ARTIFACT_CONTRACT` is **not** raised. Train/validation execution is
cleared to proceed (Phases 4–5).

## No-approval statement

This phase emits schemas only (bounded sub-window). It approves nothing, opens no
test lockbox, and keeps `configs/approved_strategies.yaml` = `approved: []` with
paper/demo/live blocked.
</content>
