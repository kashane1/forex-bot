# Evidence Index

**Date:** 2026-05-27 · **Branch:** `research-campaign-019-thesis-invalidation-execution-001`

A single index of every campaign report, pre-commit, post-mortem, and
research-freeze document. All paths are repo-relative. This index is the
map; the linked documents are the authoritative evidence.

> **Before numbering new work**, confirm the campaign number / version code is
> unused (even by abandoned ideas) per
> [`CAMPAIGN_NUMBERING_CONVENTION.md`](CAMPAIGN_NUMBERING_CONVENTION.md).

> **Bottom line:** eighteen campaigns (CAMPAIGN_001–017 plus **CAMPAIGN_018** and
> **CAMPAIGN_019** exit-hypothesis executions), **no approved trading strategy.**
> Broad seven-pair pattern strategy search is **paused** (2026-05-26).
> Trade-quality infrastructure sprint **complete** (cost atlas, MTF
> confluence prototype, cross-asset scaffolding — diagnostic only).
> Cross-asset **blocker-resolution sprint** complete (full-window FRED ingest
> succeeded; `cross_asset_missing` eliminated). **C008 post-mortem sprint**
> complete. **Stop/exit diagnostics sprint** complete. **Deduped C008/C009 forensic
> replay** complete. **CAMPAIGN_018 executed** — **REJECT** (protective stop;
> train gate fail). **CAMPAIGN_019 executed** — **REJECT** (thesis invalidation;
> train gate fail). See respective summaries.
> See `docs/research/FINAL_RESEARCH_DECISION_MEMO.md`.

## Broad strategy pause and roadmap (BROAD_STRATEGY_PAUSE_001)

| document | purpose |
|---|---|
| [`BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md`](BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md) | Formal pause, C015–C017 vs null table, re-entry gates |
| [`BROAD_STRATEGY_PAUSE_AND_ROADMAP_001_PLAN.md`](BROAD_STRATEGY_PAUSE_AND_ROADMAP_001_PLAN.md) | Sprint plan and truth audit |
| [`BROAD_STRATEGY_PAUSE_AND_ROADMAP_001_SUMMARY.md`](BROAD_STRATEGY_PAUSE_AND_ROADMAP_001_SUMMARY.md) | Sprint close-out |
| [`POST_DEDUP_FAILURE_META_ANALYSIS_001_SUMMARY.md`](POST_DEDUP_FAILURE_META_ANALYSIS_001_SUMMARY.md) | Inputs: NO_RELIABLE_ARCHETYPE |
| [`NON_STRATEGY_WORKSTREAM_OPTIONS_AFTER_PAUSE.md`](NON_STRATEGY_WORKSTREAM_OPTIONS_AFTER_PAUSE.md) | Eight non-strategy options compared |
| [`NEXT_NON_STRATEGY_WORKSTREAM_DECISION.md`](NEXT_NON_STRATEGY_WORKSTREAM_DECISION.md) | Selected next sprint |
| [`NEXT_SPRINT_PROMPT_AFTER_BROAD_STRATEGY_PAUSE.md`](NEXT_SPRINT_PROMPT_AFTER_BROAD_STRATEGY_PAUSE.md) | Copy-paste agent prompt |

## Pro-alpha confluence and asset expansion (PRO_ALPHA_CONFLUENCE_001)

> **Roadmap / design only** — `strategy_evidence: false`. No strategy
> approved. No CAMPAIGN_018. Broad strategy search **still paused**.
> Recommended next **implementation** sprint:
> `infra-multi-timeframe-confluence-and-cost-atlas-001` (cost atlas +
> MTF confluence prototype + read-only Phase 1 cross-asset ingest).
> Prior sprint `infra-observed-cost-and-spread-regime-diagnostics-001`
> remains valid as the cost-atlas slice of that combined sprint.

| document | purpose |
|---|---|
| [`PRO_ALPHA_CONFLUENCE_AND_ASSET_EXPANSION_PLAN.md`](PRO_ALPHA_CONFLUENCE_AND_ASSET_EXPANSION_PLAN.md) | Master plan, truth audit, five-layer trade-quality model |
| [`MULTI_TIMEFRAME_CONFLUENCE_DESIGN.md`](MULTI_TIMEFRAME_CONFLUENCE_DESIGN.md) | `ConfluenceScore`, MTF states, divergence rules |
| [`CROSS_ASSET_FEATURE_ROADMAP.md`](CROSS_ASSET_FEATURE_ROADMAP.md) | Phase 1 features, cost atlas, financing/carry, COT |
| [`EXIT_AND_SIZING_OVERLAY_ROADMAP.md`](EXIT_AND_SIZING_OVERLAY_ROADMAP.md) | Exit catalog, C008 post-mortem lane, Kelly deferral |
| [`ASSET_EXPANSION_SHORTLIST.md`](ASSET_EXPANSION_SHORTLIST.md) | Phased instrument shortlist + avoid list |
| [`PRO_ALPHA_CONFLUENCE_AND_ASSET_EXPANSION_SUMMARY.md`](PRO_ALPHA_CONFLUENCE_AND_ASSET_EXPANSION_SUMMARY.md) | Sprint close-out |

## Infra external data blocker resolution (INFRA_EXTERNAL_DATA_INGEST_BLOCKER_RESOLUTION_001)

> **Implementation infrastructure / data only** — `strategy_evidence: false`. No
> strategy approved. No CAMPAIGN_018. FRED full-window ingest **succeeded**;
> `cross_asset_missing` eliminated (2,142 → 0). Remaining: gold CSV, COT design.

| document | purpose |
|---|---|
| [`INFRA_EXTERNAL_DATA_INGEST_BLOCKER_RESOLUTION_001_PLAN.md`](INFRA_EXTERNAL_DATA_INGEST_BLOCKER_RESOLUTION_001_PLAN.md) | Sprint plan and truth audit |
| [`INFRA_EXTERNAL_DATA_INGEST_BLOCKER_RESOLUTION_001_SUMMARY.md`](INFRA_EXTERNAL_DATA_INGEST_BLOCKER_RESOLUTION_001_SUMMARY.md) | Sprint close-out |

## C008 mean-reversion post-mortem (C008_MEAN_REVERSION_POST_MORTEM_001)

> **Diagnostic post-mortem only** — `strategy_evidence: false`. No strategy
> approved. C008/C009 verdicts unchanged (**REJECT**). No CAMPAIGN_018.
> Recommended next sprint: `infra-deduped-c008-c009-rerun-forensic-only-001`.

| document | purpose |
|---|---|
| [`C008_MEAN_REVERSION_POST_MORTEM_001_PLAN.md`](C008_MEAN_REVERSION_POST_MORTEM_001_PLAN.md) | Sprint plan |
| [`C008_MEAN_REVERSION_POST_MORTEM_001_SUMMARY.md`](C008_MEAN_REVERSION_POST_MORTEM_001_SUMMARY.md) | Sprint close-out |
| [`C008_C009_EVIDENCE_RECONSTRUCTION.md`](C008_C009_EVIDENCE_RECONSTRUCTION.md) | Evidence table |
| [`C008_TRADE_ANATOMY_DIAGNOSTICS.md`](C008_TRADE_ANATOMY_DIAGNOSTICS.md) | Trade shape diagnostics |
| [`C008_CROSS_ASSET_REGIME_OVERLAY.md`](C008_CROSS_ASSET_REGIME_OVERLAY.md) | FRED regime overlay |
| [`C008_CONFLUENCE_OVERLAY_DIAGNOSTIC.md`](C008_CONFLUENCE_OVERLAY_DIAGNOSTIC.md) | Confluence overlay |
| [`C008_HUMAN_REVIEW_POST_MORTEM.md`](C008_HUMAN_REVIEW_POST_MORTEM.md) | Why clue, not approval |
| [`FUTURE_MEAN_REVERSION_RESEARCH_GATE.md`](FUTURE_MEAN_REVERSION_RESEARCH_GATE.md) | Future campaign requirements |
| [`research/c008_post_mortem/c008_trade_anatomy.json`](../../research/c008_post_mortem/c008_trade_anatomy.json) | Machine-readable anatomy |
| [`EXTERNAL_DATA_INGEST_STILL_BLOCKED.md`](EXTERNAL_DATA_INGEST_STILL_BLOCKED.md) | Operator setup guide (superseded for FRED; gold/COT still apply) |
| [`FRED_REAL_WINDOW_FETCH_RESULT.md`](FRED_REAL_WINDOW_FETCH_RESULT.md) | Full-window fetch result |
| [`EXTERNAL_FEATURE_LOCAL_CSV_TEMPLATE.md`](EXTERNAL_FEATURE_LOCAL_CSV_TEMPLATE.md) | Manual CSV drop template |
| [`CROSS_ASSET_H4_ALIGNMENT_AUDIT_FULL_WINDOW.md`](CROSS_ASSET_H4_ALIGNMENT_AUDIT_FULL_WINDOW.md) | Full-window alignment audit |
| [`EXTERNAL_DATA_BLOCKER_RESOLUTION_DIAGNOSTIC_IMPACT.md`](EXTERNAL_DATA_BLOCKER_RESOLUTION_DIAGNOSTIC_IMPACT.md) | Diagnostic impact (no edge claims) |
| [`research/cross_asset_features/fred_fetch_status_real_window.json`](../../research/cross_asset_features/fred_fetch_status_real_window.json) | FRED fetch status JSON |
| [`research/cross_asset_features/local_csv_fallback_status.json`](../../research/cross_asset_features/local_csv_fallback_status.json) | Local CSV scan status |

## Stop and exit diagnostics (STOP_AND_EXIT_DIAGNOSTICS_001)

> **Diagnostic only** — `strategy_evidence: false`. No strategy approved. C008/C009
> remain **REJECT**. No CAMPAIGN_018. Stop/time pathology is **framework-wide**, not
> C008-only. Recommended next sprint: `infra-deduped-c008-c009-rerun-forensic-only-001`.

| document | purpose |
|---|---|
| [`STOP_AND_EXIT_DIAGNOSTICS_001_PLAN.md`](STOP_AND_EXIT_DIAGNOSTICS_001_PLAN.md) | Sprint plan |
| [`STOP_AND_EXIT_DIAGNOSTICS_001_SUMMARY.md`](STOP_AND_EXIT_DIAGNOSTICS_001_SUMMARY.md) | Sprint close-out |
| [`EXIT_ARTIFACT_INVENTORY.md`](EXIT_ARTIFACT_INVENTORY.md) | Trade artifact field inventory |
| [`CROSS_CAMPAIGN_EXIT_PATHOLOGY_MATRIX.md`](CROSS_CAMPAIGN_EXIT_PATHOLOGY_MATRIX.md) | Cross-campaign exit breakdown |
| [`C008_C009_EXIT_FORENSICS.md`](C008_C009_EXIT_FORENSICS.md) | C008/C009 train/validation forensics |
| [`STOP_DISTANCE_AND_ADVERSE_EXCURSION_DIAGNOSTICS.md`](STOP_DISTANCE_AND_ADVERSE_EXCURSION_DIAGNOSTICS.md) | MAE/MFE and stop distance |
| [`FUTURE_EXIT_RESEARCH_HYPOTHESES.md`](FUTURE_EXIT_RESEARCH_HYPOTHESES.md) | Pre-registerable exit hypotheses |
| [`FUTURE_EXIT_RESEARCH_GATE.md`](FUTURE_EXIT_RESEARCH_GATE.md) | Future exit campaign gate |
| [`research/exit_diagnostics/exit_artifact_inventory.json`](../../research/exit_diagnostics/exit_artifact_inventory.json) | Machine-readable inventory |
| [`research/exit_diagnostics/cross_campaign_exit_matrix.json`](../../research/exit_diagnostics/cross_campaign_exit_matrix.json) | Machine-readable exit matrix |
| [`research/exit_diagnostics/c008_c009_exit_forensics.json`](../../research/exit_diagnostics/c008_c009_exit_forensics.json) | C008/C009 forensics JSON |
| [`research/exit_diagnostics/stop_distance_adverse_excursion.json`](../../research/exit_diagnostics/stop_distance_adverse_excursion.json) | MAE/MFE JSON |

## Deduped C008/C009 forensic replay (DEDUPED_C008_C009_RERUN_FORENSIC_ONLY_001)

> **Forensic replay only** — `strategy_evidence: false`. C008/C009 remain **REJECT**.
> Deduped replay confirmed train-fail/validation-positive shape and exit pathology.
> Recommended next sprint: `research-campaign-018-protective-stop-execution-001`.

| document | purpose |
|---|---|
| [`DEDUPED_C008_C009_RERUN_FORENSIC_ONLY_001_PLAN.md`](DEDUPED_C008_C009_RERUN_FORENSIC_ONLY_001_PLAN.md) | Sprint plan |
| [`DEDUPED_C008_C009_RERUN_FORENSIC_ONLY_001_SUMMARY.md`](DEDUPED_C008_C009_RERUN_FORENSIC_ONLY_001_SUMMARY.md) | Sprint close-out |
| [`C008_C009_FROZEN_CONFIG_RECONSTRUCTION.md`](C008_C009_FROZEN_CONFIG_RECONSTRUCTION.md) | Frozen rule reconstruction |
| [`C008_C009_DEDUPED_FORENSIC_REPLAY_RESULTS.md`](C008_C009_DEDUPED_FORENSIC_REPLAY_RESULTS.md) | Replay results |
| [`C008_C009_OLD_VS_DEDUPED_COMPARISON.md`](C008_C009_OLD_VS_DEDUPED_COMPARISON.md) | Old vs deduped comparison |
| [`C008_C009_DEDUPED_EXIT_ANATOMY.md`](C008_C009_DEDUPED_EXIT_ANATOMY.md) | Deduped exit anatomy |
| [`C008_C009_DEDUPED_MAE_MFE_DIAGNOSTICS.md`](C008_C009_DEDUPED_MAE_MFE_DIAGNOSTICS.md) | Deduped MAE/MFE |
| [`C008_C009_EVIDENCE_INTEGRITY_DECISION.md`](C008_C009_EVIDENCE_INTEGRITY_DECISION.md) | Integrity decision |
| [`research/deduped_c008_c009_rerun/metrics_summary.json`](../../research/deduped_c008_c009_rerun/metrics_summary.json) | Deduped metrics JSON |
| [`research/deduped_c008_c009_rerun/gate_result.json`](../../research/deduped_c008_c009_rerun/gate_result.json) | Gate JSON |
| [`research/deduped_c008_c009_rerun/old_vs_deduped_metric_comparison.json`](../../research/deduped_c008_c009_rerun/old_vs_deduped_metric_comparison.json) | Comparison JSON |

## Exit hypothesis precommit (EXIT_HYPOTHESIS_PRECOMMIT_001)

> **Precommit / design only** — `strategy_evidence: false`. CAMPAIGN_018 identity
> and gates pre-registered; **no backtest executed**. C008/C009 remain **REJECT**.
> Recommended next sprint: `research-campaign-018-protective-stop-execution-001`.

| document | purpose |
|---|---|
| [`EXIT_HYPOTHESIS_PRECOMMIT_001_PLAN.md`](EXIT_HYPOTHESIS_PRECOMMIT_001_PLAN.md) | Sprint plan |
| [`EXIT_HYPOTHESIS_PRECOMMIT_001_SUMMARY.md`](EXIT_HYPOTHESIS_PRECOMMIT_001_SUMMARY.md) | Sprint close-out |
| [`EXIT_HYPOTHESIS_SELECTION_MEMO.md`](EXIT_HYPOTHESIS_SELECTION_MEMO.md) | Selected hypothesis |
| [`CAMPAIGN_018_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md`](CAMPAIGN_018_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md) | Frozen scope (not executed) |
| [`CAMPAIGN_018_EXIT_HYPOTHESIS_GATE_DESIGN.md`](CAMPAIGN_018_EXIT_HYPOTHESIS_GATE_DESIGN.md) | Gate design |
| [`CAMPAIGN_018_EXIT_HYPOTHESIS_IMPLEMENTATION_DESIGN.md`](CAMPAIGN_018_EXIT_HYPOTHESIS_IMPLEMENTATION_DESIGN.md) | Future implementation design |
| [`NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT.md`](NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT.md) | Execution sprint prompt |

## CAMPAIGN_018 protective stop execution (CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001)

> **CAMPAIGN_018 executed** — `strategy_evidence: true`, `not_approved: true`.
> Verdict **REJECT** (train −0.119 R; validation +0.194 R). Test lockbox **not opened**.
> Recommended next sprint: `research-financing-modeled-pnl-and-carry-readiness-001`.

| document | purpose |
|---|---|
| [`CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001_PLAN.md`](CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001_PLAN.md) | Execution sprint plan |
| [`CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001_SUMMARY.md`](CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001_SUMMARY.md) | Sprint close-out |
| [`CAMPAIGN_018_TRAIN_VALIDATION_RESULT.md`](CAMPAIGN_018_TRAIN_VALIDATION_RESULT.md) | Train/validation results |
| [`CAMPAIGN_018_GATE_DECISION.md`](CAMPAIGN_018_GATE_DECISION.md) | Gate decision |
| [`CAMPAIGN_018_TEST_LOCKBOX_NOT_OPENED.md`](CAMPAIGN_018_TEST_LOCKBOX_NOT_OPENED.md) | Lockbox closed |
| [`CAMPAIGN_018_FINAL_INTERPRETATION.md`](CAMPAIGN_018_FINAL_INTERPRETATION.md) | Final interpretation |
| [`research/campaign_018/gate_result.json`](../../research/campaign_018/gate_result.json) | Gate JSON |
| [`research/campaign_018/mechanism_diagnostics.json`](../../research/campaign_018/mechanism_diagnostics.json) | Mechanism JSON |
| [`research/campaign_018/metrics_summary.json`](../../research/campaign_018/metrics_summary.json) | Metrics JSON |

## Financing modeled PnL and carry readiness (FINANCING_MODELED_PNL_AND_CARRY_READINESS_001)

> **Infrastructure / diagnostic only** — `strategy_evidence: false`. Engine PnL
> remains UNMODELED. C008/C009/C018 verdicts unchanged (**REJECT**). Observed
> financing **not used** — `SYNTHETIC_FINANCING_DIAGNOSTIC` only.
> Recommended next sprint: `infra-observed-financing-capture-readonly-001`.

| document | purpose |
|---|---|
| [`FINANCING_MODELED_PNL_AND_CARRY_READINESS_001_PLAN.md`](FINANCING_MODELED_PNL_AND_CARRY_READINESS_001_PLAN.md) | Sprint plan |
| [`FINANCING_CAPABILITY_AUDIT.md`](FINANCING_CAPABILITY_AUDIT.md) | Capability audit |
| [`C008_C009_C018_FINANCING_EXPOSURE_DIAGNOSTIC.md`](C008_C009_C018_FINANCING_EXPOSURE_DIAGNOSTIC.md) | MR financing exposure |
| [`CARRY_AND_FINANCING_READINESS_MEMO.md`](CARRY_AND_FINANCING_READINESS_MEMO.md) | Carry readiness gaps |
| [`NEXT_SPRINT_PROMPT_AFTER_FINANCING_MODELED_PNL.md`](NEXT_SPRINT_PROMPT_AFTER_FINANCING_MODELED_PNL.md) | Next sprint prompt |
| [`research/financing/modeled_pnl_readiness_audit.json`](../../research/financing/modeled_pnl_readiness_audit.json) | Machine-readable audit |
| [`research/financing/c008_c009_c018_financing_exposure.json`](../../research/financing/c008_c009_c018_financing_exposure.json) | Exposure JSON |

## Observed financing capture read-only (OBSERVED_FINANCING_CAPTURE_READONLY_001)

> **Infrastructure / read-only capture** — `strategy_evidence: false`. Practice GET
> transactions only. Capture result: **OBSERVED_FINANCING_EMPTY** (zero DAILY_FINANCING
> in 180-day window). MODELED not ready. Recommended next:
> `infra-practice-overnight-financing-sample-collection-001`.

| document | purpose |
|---|---|
| [`OBSERVED_FINANCING_CAPTURE_READONLY_001_PLAN.md`](OBSERVED_FINANCING_CAPTURE_READONLY_001_PLAN.md) | Sprint plan |
| [`OBSERVED_FINANCING_CAPTURE_READONLY_RUNBOOK.md`](OBSERVED_FINANCING_CAPTURE_READONLY_RUNBOOK.md) | Runbook |
| [`OBSERVED_FINANCING_CAPTURE_PREFLIGHT.md`](OBSERVED_FINANCING_CAPTURE_PREFLIGHT.md) | Preflight checks |
| [`OBSERVED_FINANCING_CAPTURE_RESULT.md`](OBSERVED_FINANCING_CAPTURE_RESULT.md) | Capture result (empty) |
| [`OBSERVED_FINANCING_SCHEMA_RECONCILIATION.md`](OBSERVED_FINANCING_SCHEMA_RECONCILIATION.md) | Schema vs overlay |
| [`OBSERVED_FINANCING_READINESS_DECISION.md`](OBSERVED_FINANCING_READINESS_DECISION.md) | Readiness decision |
| [`research/financing/observed/observed_financing_capture_status.json`](../../research/financing/observed/observed_financing_capture_status.json) | Capture status |
| [`research/financing/observed/observed_financing_manifest.json`](../../research/financing/observed/observed_financing_manifest.json) | Endpoint manifest |

## Practice overnight financing sample plan (PRACTICE_OVERNIGHT_FINANCING_SAMPLE_PLAN_001)

> **Planning / runbook only** — `strategy_evidence: false`. Human manually places
> practice trades; Cursor/bot must **not** submit orders. DAILY_FINANCING capture
> remains empty until human sample exists. Next after sample:
> `infra-observed-financing-post-sample-capture-001`.

| document | purpose |
|---|---|
| [`PRACTICE_OVERNIGHT_FINANCING_SAMPLE_PLAN_001.md`](PRACTICE_OVERNIGHT_FINANCING_SAMPLE_PLAN_001.md) | Sprint plan |
| [`PRACTICE_OVERNIGHT_FINANCING_SAMPLE_COLLECTION_RUNBOOK.md`](PRACTICE_OVERNIGHT_FINANCING_SAMPLE_COLLECTION_RUNBOOK.md) | Human collection runbook |
| [`POST_SAMPLE_OBSERVED_FINANCING_CAPTURE_CHECKLIST.md`](POST_SAMPLE_OBSERVED_FINANCING_CAPTURE_CHECKLIST.md) | Post-sample capture checklist |
| [`OBSERVED_TO_MODELED_FINANCING_BRIDGE_DESIGN.md`](OBSERVED_TO_MODELED_FINANCING_BRIDGE_DESIGN.md) | Bridge design (not implemented) |

## Backtrader exit parity diagnostics (BACKTRADER_EXIT_PARITY_DIAGNOSTICS_001)

> **Parity diagnostic only** — `strategy_evidence: false`. Independent Backtrader
> lane for C008/C009/C018 exit behavior. Manual financing sample **paused**. No
> strategy approved. Recommended next: `research-exit-hypothesis-precommit-002`.

| document | purpose |
|---|---|
| [`BACKTRADER_EXIT_PARITY_DIAGNOSTICS_001_PLAN.md`](BACKTRADER_EXIT_PARITY_DIAGNOSTICS_001_PLAN.md) | Sprint plan and truth audit |
| [`BACKTRADER_EXIT_PARITY_DIVERGENCE_ANALYSIS.md`](BACKTRADER_EXIT_PARITY_DIVERGENCE_ANALYSIS.md) | Divergence taxonomy |
| [`BACKTRADER_EXIT_PARITY_STATUS.md`](BACKTRADER_EXIT_PARITY_STATUS.md) | Status and next-sprint decision |
| [`BACKTRADER_EXIT_PARITY_DIAGNOSTICS_001_SUMMARY.md`](BACKTRADER_EXIT_PARITY_DIAGNOSTICS_001_SUMMARY.md) | Sprint close-out |
| [`research/backtrader_exit_parity/c008_parity_summary.json`](../../research/backtrader_exit_parity/c008_parity_summary.json) | C008 BT aggregates |
| [`research/backtrader_exit_parity/c009_parity_summary.json`](../../research/backtrader_exit_parity/c009_parity_summary.json) | C009 BT aggregates |
| [`research/backtrader_exit_parity/c018_parity_summary.json`](../../research/backtrader_exit_parity/c018_parity_summary.json) | C018 BT aggregates |
| [`research/backtrader_exit_parity/exit_reason_comparison.csv`](../../research/backtrader_exit_parity/exit_reason_comparison.csv) | Exit-reason side-by-side |

## Entry orchestration parity diagnostics (ENTRY_ORCHESTRATION_PARITY_DIAGNOSTICS_001)

> **Parity diagnostic only** — `strategy_evidence: false`. Root cause of ~20% trade-count
> gap: Backtrader lane missing quote→USD PnL conversion (USD_JPY/USD_CAD). Fixed in branch;
> gap narrows to ±1 trade. Bespoke engine entry orchestration **trustworthy**.

| document | purpose |
|---|---|
| [`ENTRY_ORCHESTRATION_PARITY_DIAGNOSTICS_001_PLAN.md`](ENTRY_ORCHESTRATION_PARITY_DIAGNOSTICS_001_PLAN.md) | Sprint plan |
| [`ENTRY_TIMESTAMP_PARITY_COMPARISON.md`](ENTRY_TIMESTAMP_PARITY_COMPARISON.md) | Entry timestamp analysis |
| [`RISK_FILTER_ENTRY_PARITY_ATTRIBUTION.md`](RISK_FILTER_ENTRY_PARITY_ATTRIBUTION.md) | Root-cause attribution |
| [`BACKTRADER_ENTRY_PARITY_ADJUSTMENT_EXPERIMENT.md`](BACKTRADER_ENTRY_PARITY_ADJUSTMENT_EXPERIMENT.md) | PnL-fix experiment |
| [`ENTRY_ORCHESTRATION_PARITY_DECISION.md`](ENTRY_ORCHESTRATION_PARITY_DECISION.md) | Classification + next sprint |
| [`ENTRY_ORCHESTRATION_PARITY_DIAGNOSTICS_001_SUMMARY.md`](ENTRY_ORCHESTRATION_PARITY_DIAGNOSTICS_001_SUMMARY.md) | Sprint close-out |
| [`research/entry_parity/entry_timestamp_comparison.json`](../../research/entry_parity/entry_timestamp_comparison.json) | Entry comparison JSON |
| [`research/entry_parity/backtrader_adjustment_experiment.json`](../../research/entry_parity/backtrader_adjustment_experiment.json) | Adjustment profiles |

## Backtrader entry parity hardening (BACKTRADER_ENTRY_PARITY_HARDENING_001)

> **Parity diagnostic only** — `strategy_evidence: false`. Formalizes quote→USD PnL
> fix and engine-aligned risk windows; C008/C009/C018 within ±1 trade tolerance.
> Independent Backtrader lane **hardened for these campaigns only**. Manual financing
> sample **paused**. No strategy approved. Recommended next:
> `research-exit-hypothesis-precommit-002`.

| document | purpose |
|---|---|
| [`BACKTRADER_ENTRY_PARITY_HARDENING_001_PLAN.md`](BACKTRADER_ENTRY_PARITY_HARDENING_001_PLAN.md) | Sprint plan and truth audit |
| [`BACKTRADER_ENTRY_PARITY_HARDENING_RESULT.md`](BACKTRADER_ENTRY_PARITY_HARDENING_RESULT.md) | Post-hardening entry comparison |
| [`BACKTRADER_PARITY_HARDENED_STATUS.md`](BACKTRADER_PARITY_HARDENED_STATUS.md) | Final parity decision |
| [`BACKTRADER_ENTRY_PARITY_HARDENING_001_SUMMARY.md`](BACKTRADER_ENTRY_PARITY_HARDENING_001_SUMMARY.md) | Sprint close-out |
| [`research/backtrader_exit_parity/parity_run_manifest.json`](../../research/backtrader_exit_parity/parity_run_manifest.json) | Run metadata (BT version, PnL mode) |
| [`research/backtrader_exit_parity/pnl.py`](../../research/backtrader_exit_parity/pnl.py) | Home-currency PnL conversion module |

## Exit hypothesis precommit 002 (EXIT_HYPOTHESIS_PRECOMMIT_002)

> **Precommit / design only** — `strategy_evidence: false`. CAMPAIGN_019 thesis-invalidation
> exit pre-registered; **executed** on branch `research-campaign-019-thesis-invalidation-execution-001`
> — **REJECT** (train gate fail). See CAMPAIGN_019 execution section below.

| document | purpose |
|---|---|
| [`EXIT_HYPOTHESIS_PRECOMMIT_002_PLAN.md`](EXIT_HYPOTHESIS_PRECOMMIT_002_PLAN.md) | Sprint plan and truth audit |
| [`CAMPAIGN_018_FAILURE_ANALYSIS_FOR_NEXT_EXIT_HYPOTHESIS.md`](CAMPAIGN_018_FAILURE_ANALYSIS_FOR_NEXT_EXIT_HYPOTHESIS.md) | C018 failure → next hypothesis |
| [`EXIT_HYPOTHESIS_PRECOMMIT_002_SELECTION_MEMO.md`](EXIT_HYPOTHESIS_PRECOMMIT_002_SELECTION_MEMO.md) | Hypothesis selection |
| [`CAMPAIGN_019_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md`](CAMPAIGN_019_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md) | CAMPAIGN_019 frozen scope |
| [`CAMPAIGN_019_EXIT_HYPOTHESIS_GATE_DESIGN.md`](CAMPAIGN_019_EXIT_HYPOTHESIS_GATE_DESIGN.md) | Gate design and falsification |
| [`CAMPAIGN_019_EXIT_HYPOTHESIS_IMPLEMENTATION_DESIGN.md`](CAMPAIGN_019_EXIT_HYPOTHESIS_IMPLEMENTATION_DESIGN.md) | Implementation design |
| [`NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT_002.md`](NEXT_SPRINT_PROMPT_AFTER_EXIT_HYPOTHESIS_PRECOMMIT_002.md) | Execution sprint prompt |
| [`EXIT_HYPOTHESIS_PRECOMMIT_002_SUMMARY.md`](EXIT_HYPOTHESIS_PRECOMMIT_002_SUMMARY.md) | Sprint close-out |

## CAMPAIGN_019 thesis invalidation execution (CAMPAIGN_019_THESIS_INVALIDATION_EXECUTION_001)

> **CAMPAIGN_019 executed** — `strategy_evidence: true`, `not_approved: true`.
> Verdict **REJECT** — train exp_r **−0.072 R**; validation **+0.0962 R**; test lockbox **closed**.

| document | purpose |
|---|---|
| [`CAMPAIGN_019_THESIS_INVALIDATION_EXECUTION_001_PLAN.md`](CAMPAIGN_019_THESIS_INVALIDATION_EXECUTION_001_PLAN.md) | Execution sprint plan |
| [`CAMPAIGN_019_TRAIN_VALIDATION_RESULT.md`](CAMPAIGN_019_TRAIN_VALIDATION_RESULT.md) | Train/validation results |
| [`CAMPAIGN_019_BACKTRADER_PARITY_RESULT.md`](CAMPAIGN_019_BACKTRADER_PARITY_RESULT.md) | Backtrader parity |
| [`CAMPAIGN_019_GATE_DECISION.md`](CAMPAIGN_019_GATE_DECISION.md) | Gate decision |
| [`CAMPAIGN_019_TEST_LOCKBOX_NOT_OPENED.md`](CAMPAIGN_019_TEST_LOCKBOX_NOT_OPENED.md) | Lockbox closed |
| [`CAMPAIGN_019_FINAL_INTERPRETATION.md`](CAMPAIGN_019_FINAL_INTERPRETATION.md) | Final interpretation |
| [`CAMPAIGN_019_THESIS_INVALIDATION_EXECUTION_001_SUMMARY.md`](CAMPAIGN_019_THESIS_INVALIDATION_EXECUTION_001_SUMMARY.md) | Sprint close-out |
| [`research/campaign_019/gate_result.json`](../../research/campaign_019/gate_result.json) | Machine-readable gates |
| [`research/backtrader_exit_parity/c019_parity_summary.json`](../../research/backtrader_exit_parity/c019_parity_summary.json) | BT parity summary |

## CAMPAIGN_020 MTF confluence pullback (research-campaign-020-mtf-confluence-execution-001)

> **CAMPAIGN_020 executed** — `strategy_evidence: true`, `not_approved: true`.
> Verdict **REJECT** — train **−0.035 R** under `next_bar_open`; validation **+0.053 R**;
> test lockbox **closed** (train gate fail).

| document | purpose |
|---|---|
| [`CAMPAIGN_020_MTF_CONFLUENCE_PRECOMMIT.md`](CAMPAIGN_020_MTF_CONFLUENCE_PRECOMMIT.md) | Frozen parameters and gates |
| [`CAMPAIGN_020_TRAIN_VALIDATION_RESULT.md`](CAMPAIGN_020_TRAIN_VALIDATION_RESULT.md) | Train/validation results |
| [`CAMPAIGN_020_GATE_DECISION.md`](CAMPAIGN_020_GATE_DECISION.md) | Gate decision |
| [`CAMPAIGN_020_TEST_LOCKBOX_NOT_OPENED.md`](CAMPAIGN_020_TEST_LOCKBOX_NOT_OPENED.md) | Lockbox closed |
| [`CAMPAIGN_020_BACKTRADER_PARITY_RESULT.md`](CAMPAIGN_020_BACKTRADER_PARITY_RESULT.md) | Parity NOT_RUN |
| [`CAMPAIGN_020_FINAL_INTERPRETATION.md`](CAMPAIGN_020_FINAL_INTERPRETATION.md) | Final interpretation |
| [`CAMPAIGN_020_MTF_CONFLUENCE_EXECUTION_001_SUMMARY.md`](CAMPAIGN_020_MTF_CONFLUENCE_EXECUTION_001_SUMMARY.md) | Execution sprint close-out |
| [`research/campaign_020/gate_result.json`](../../research/campaign_020/gate_result.json) | Machine-readable gates |
| [`CAMPAIGN_020_MTF_CONFLUENCE_SCAFFOLD_001_SUMMARY.md`](CAMPAIGN_020_MTF_CONFLUENCE_SCAFFOLD_001_SUMMARY.md) | Scaffold sprint close-out |

## CAMPAIGN_023 H4/H1 pullback resolution — ADX22 sibling (scaffold only)

> **SCAFFOLD_ONLY / PRECOMMITTED_NOT_EXECUTED** — `strategy_evidence: false`,
> `not_approved: true`. Pre-registered ADX-sensitivity **sibling of CAMPAIGN_022**:
> identical except the H4 directional-bias strength gate (`h4_adx_min` **22.0** vs
> C022's **20.0**). No train/validation/test evidence; no verdict; paper/demo/live
> blocked. (CAMPAIGN_022 is a parallel scaffold on the same branch.)

| document | purpose |
|---|---|
| [`CAMPAIGN_023_ADX22_SIBLING_PLAN.md`](CAMPAIGN_023_ADX22_SIBLING_PLAN.md) | Plan + C022 baseline audit |
| [`CAMPAIGN_023_H4_H1_PULLBACK_RESOLUTION_ADX22_PRECOMMIT.md`](CAMPAIGN_023_H4_H1_PULLBACK_RESOLUTION_ADX22_PRECOMMIT.md) | Frozen parameters; ADX22 delta; contamination guard |
| [`../../configs/campaign_023_h4_h1_pullback_resolution_adx22.yaml`](../../configs/campaign_023_h4_h1_pullback_resolution_adx22.yaml) | Frozen config (`h4_adx_min: 22.0`) |
| [`../../scripts/run_campaign_023_h4_h1_pullback_resolution_adx22.py`](../../scripts/run_campaign_023_h4_h1_pullback_resolution_adx22.py) | Preflight-only runner (evidence blocked) |
| [`../../tests/unit/test_h4_h1_pullback_resolution_adx22.py`](../../tests/unit/test_h4_h1_pullback_resolution_adx22.py) | Proves C023 == C022 except ADX gate |
| [`CAMPAIGN_023_ADX22_SIBLING_SCAFFOLD_SUMMARY.md`](CAMPAIGN_023_ADX22_SIBLING_SCAFFOLD_SUMMARY.md) | Scaffold sprint close-out |

## CAMPAIGN_025 M5 Donchian + HTF confluence breakout (REJECT — train-matrix)

> **REJECT** — `REJECT_MATRIX_NO_TRAIN_CANDIDATE / TEST_LOCKBOX_CLOSED /
> NOT_APPROVED`. Train-matrix sprint (2026-05-28) ran 16 archetypes on train
> 2021-07-01→2023-06-30; **0/16 eligible** (all net-negative; spread/ATR ≈ 0.45 on
> M5). No champion → validation not run; no single-pair review; lockbox closed;
> `not_approved: true`; paper/demo/live blocked. Scaffold (below) preceded this.

| document | purpose |
|---|---|
| [`CAMPAIGN_025_M5_DONCHIAN_HTF_CONFLUENCE_SCAFFOLD_001_PLAN.md`](CAMPAIGN_025_M5_DONCHIAN_HTF_CONFLUENCE_SCAFFOLD_001_PLAN.md) | Plan + baseline audit |
| [`CAMPAIGN_025_PRECOMMIT_M5_DONCHIAN_HTF_CONFLUENCE_SCOPE.md`](CAMPAIGN_025_PRECOMMIT_M5_DONCHIAN_HTF_CONFLUENCE_SCOPE.md) | Frozen rules, stop, and gates |
| [`../../configs/campaign_025_m5_donchian_htf_confluence_breakout.yaml`](../../configs/campaign_025_m5_donchian_htf_confluence_breakout.yaml) | Frozen config (M5; `not_approved: true`) |
| [`../../src/forex_bot/strategies/m5_donchian_htf_confluence_breakout.py`](../../src/forex_bot/strategies/m5_donchian_htf_confluence_breakout.py) | Pure research strategy module |
| [`../../tests/unit/test_m5_donchian_htf_confluence_breakout.py`](../../tests/unit/test_m5_donchian_htf_confluence_breakout.py) | Strategy unit tests |
| [`../../src/forex_bot/research/campaign_025_loader.py`](../../src/forex_bot/research/campaign_025_loader.py) | Materialized M5/M15/H1/H4 + native-H4 D1AGG loader |
| [`../../src/forex_bot/research/campaign_025_gates.py`](../../src/forex_bot/research/campaign_025_gates.py) | Frozen precommit gates |
| [`../../scripts/run_campaign_025_m5_donchian_htf_confluence.py`](../../scripts/run_campaign_025_m5_donchian_htf_confluence.py) | Scaffold preflight runner (no evidence machinery) |
| [`CAMPAIGN_025_BACKTRADER_PARITY_DESIGN.md`](CAMPAIGN_025_BACKTRADER_PARITY_DESIGN.md) | Parity design stub (precommitted gate) |
| [`CAMPAIGN_025_DISTINCTNESS_AND_PRIOR_LESSONS_MEMO.md`](CAMPAIGN_025_DISTINCTNESS_AND_PRIOR_LESSONS_MEMO.md) | Distinctness + prior lessons |
| [`CAMPAIGN_025_M5_DONCHIAN_HTF_CONFLUENCE_SCAFFOLD_001_SUMMARY.md`](CAMPAIGN_025_M5_DONCHIAN_HTF_CONFLUENCE_SCAFFOLD_001_SUMMARY.md) | Scaffold sprint close-out |
| [`CAMPAIGN_025_TRAIN_MATRIX_VALIDATION_001_PLAN.md`](CAMPAIGN_025_TRAIN_MATRIX_VALIDATION_001_PLAN.md) | Train-matrix sprint plan |
| [`CAMPAIGN_025_DATA_COVERAGE_AND_SPLIT_DECISION.md`](CAMPAIGN_025_DATA_COVERAGE_AND_SPLIT_DECISION.md) | Frozen narrowed split from M5 coverage |
| [`CAMPAIGN_025_TRAIN_MATRIX_SPEC.md`](CAMPAIGN_025_TRAIN_MATRIX_SPEC.md) | Frozen 16-candidate matrix + exit math + selection rules |
| [`CAMPAIGN_025_TRAIN_MATRIX_RESULT.md`](CAMPAIGN_025_TRAIN_MATRIX_RESULT.md) | **Train-matrix result — REJECT_MATRIX_NO_TRAIN_CANDIDATE** |
| [`CAMPAIGN_025_SELECTED_CHAMPION_VALIDATION_RESULT.md`](CAMPAIGN_025_SELECTED_CHAMPION_VALIDATION_RESULT.md) | Validation NOT run (no champion) |
| [`CAMPAIGN_025_INTERPRETATION_AND_PRIOR_COMPARISON.md`](CAMPAIGN_025_INTERPRETATION_AND_PRIOR_COMPARISON.md) | Interpretation + prior-campaign comparison |
| [`CAMPAIGN_025_BACKTRADER_PARITY_READINESS.md`](CAMPAIGN_025_BACKTRADER_PARITY_READINESS.md) | Parity readiness = DEFER_PARITY_REJECTED |
| [`../../src/forex_bot/research/campaign_025_train_matrix.py`](../../src/forex_bot/research/campaign_025_train_matrix.py) | Vectorized M5 train-matrix simulator |
| [`CAMPAIGN_025_TRAIN_MATRIX_VALIDATION_001_SUMMARY.md`](CAMPAIGN_025_TRAIN_MATRIX_VALIDATION_001_SUMMARY.md) | **Train-matrix sprint close-out (43-item summary)** |

## CAMPAIGN_026 Donchian + HTF confluence timeframe ladder (REJECT — M3/M15/M30)

> **REJECT** — `REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE / TEST_LOCKBOX_CLOSED /
> NOT_APPROVED`. Diagnostic sprint (2026-05-28) testing whether the C025 M5 family is
> salvageable on a different execution timeframe. Materialized M3/M30 from M1; ran 11
> pre-committed candidates on train 2021-07-01→2023-06-30 across M3/M15/M30. **0/11
> eligible.** Cost and expectancy improve monotonically as the timeframe slows
> (M3 −0.16R/0.59 spread-ATR → M15 −0.06/0.23 → M30 −0.008/0.15) — the cost hypothesis
> is confirmed and M5 was not uniquely cost-defeated — but even the best M30 candidate
> is net-negative, below the C011 null, failing 2× stress. No champion → validation not
> run; no single-pair review; lockbox closed; `not_approved: true`; paper/demo/live
> blocked. Family rejected across all lower timeframes.

| document | purpose |
|---|---|
| [`CAMPAIGN_026_TIMEFRAME_LADDER_001_PLAN.md`](CAMPAIGN_026_TIMEFRAME_LADDER_001_PLAN.md) | Plan + truth audit |
| [`CAMPAIGN_026_M3_M30_MATERIALIZATION_DESIGN.md`](CAMPAIGN_026_M3_M30_MATERIALIZATION_DESIGN.md) | M3/M30 materialization design (hash-stable, opt-in) |
| [`CAMPAIGN_026_M3_M30_MATERIALIZATION_RESULT.md`](CAMPAIGN_026_M3_M30_MATERIALIZATION_RESULT.md) | Materialization result (PASS; ~4.18M M3 / ~380K M30) |
| [`../../scripts/materialize_campaign_026_m3_m30.py`](../../scripts/materialize_campaign_026_m3_m30.py) | M3/M30 materialization + verification driver |
| [`CAMPAIGN_026_TIMEFRAME_COST_ATR_DIAGNOSTIC.md`](CAMPAIGN_026_TIMEFRAME_COST_ATR_DIAGNOSTIC.md) | Pre-evidence spread/ATR diagnostic (PROCEED) |
| [`CAMPAIGN_026_TIMEFRAME_LADDER_SPEC.md`](CAMPAIGN_026_TIMEFRAME_LADDER_SPEC.md) | Frozen 11-candidate matrix + selection rules |
| [`../../research/campaign_026/timeframe_ladder/candidate_registry.json`](../../research/campaign_026/timeframe_ladder/candidate_registry.json) | Machine-readable frozen registry (`not_approved: true`) |
| [`CAMPAIGN_026_DATA_COVERAGE_AND_SPLIT_DECISION.md`](CAMPAIGN_026_DATA_COVERAGE_AND_SPLIT_DECISION.md) | Frozen split (= C025, comparable) |
| [`../../src/forex_bot/research/campaign_026_loader.py`](../../src/forex_bot/research/campaign_026_loader.py) | Variable execution-tf frame loader + context ladder |
| [`../../src/forex_bot/research/campaign_026_timeframe_ladder.py`](../../src/forex_bot/research/campaign_026_timeframe_ladder.py) | Vectorized timeframe-ladder simulator |
| [`../../scripts/run_campaign_026_donchian_htf_timeframe_ladder.py`](../../scripts/run_campaign_026_donchian_htf_timeframe_ladder.py) | Preflight / cost-diagnostic / train-matrix / validate runner |
| [`CAMPAIGN_026_TRAIN_TIMEFRAME_LADDER_RESULT.md`](CAMPAIGN_026_TRAIN_TIMEFRAME_LADDER_RESULT.md) | **Train result — REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE** |
| [`CAMPAIGN_026_SELECTED_CHAMPION_VALIDATION_RESULT.md`](CAMPAIGN_026_SELECTED_CHAMPION_VALIDATION_RESULT.md) | Validation NOT run (no champion) |
| [`CAMPAIGN_026_TIMEFRAME_LADDER_INTERPRETATION.md`](CAMPAIGN_026_TIMEFRAME_LADDER_INTERPRETATION.md) | Interpretation + family-close decision |
| [`CAMPAIGN_026_BACKTRADER_PARITY_READINESS.md`](CAMPAIGN_026_BACKTRADER_PARITY_READINESS.md) | Parity readiness = DEFER_PARITY_REJECTED |
| [`CAMPAIGN_026_TIMEFRAME_LADDER_001_SUMMARY.md`](CAMPAIGN_026_TIMEFRAME_LADDER_001_SUMMARY.md) | **Sprint close-out (41-item summary)** |

## CAMPAIGN_027 Filtered H4 z-score reversion (SCAFFOLD_ONLY / PRECOMMITTED)

> **SCAFFOLD_ONLY / PRECOMMITTED / NOT_RUN / NOT_APPROVED** (2026-05-28). Scaffold
> for the single idea that survived the edge-discovery front gate: **short-only
> filtered H4 z-score mean reversion** (20-bar z, mean/σ shifted 1, ddof=1; enter
> short at |z|>=2.5; low-vol ATR-14 simple-mean trailing-250 percentile <=0.33;
> quiet-session asia/london UTC; `next_bar_open` fill; exit = 12-bar time stop +
> wide 3xATR protective stop; conservative financing-inclusive cost binding; 7
> majors). **No train/validation/test evidence run; test lockbox closed;
> `approved_strategies.yaml` stays empty; paper/demo/live blocked; C011 stays the
> null benchmark; C025/C026 stay REJECT.** Borderline (wafer-thin; 2024/2026
> negative) — the nine precommitted kill conditions bind a future sprint.

| document | purpose |
|---|---|
| [`CAMPAIGN_027_H4_FILTERED_ZSCORE_REVERSION_SCAFFOLD_001_PLAN.md`](CAMPAIGN_027_H4_FILTERED_ZSCORE_REVERSION_SCAFFOLD_001_PLAN.md) | Plan + truth audit (CAMPAIGN_027 verified free) |
| [`CAMPAIGN_027_EDGE_DISCOVERY_TO_PRECOMMIT_RECONCILIATION.md`](CAMPAIGN_027_EDGE_DISCOVERY_TO_PRECOMMIT_RECONCILIATION.md) | Front-gate evidence → precommit decision |
| [`CAMPAIGN_027_PRECOMMIT_H4_FILTERED_ZSCORE_REVERSION_SCOPE.md`](CAMPAIGN_027_PRECOMMIT_H4_FILTERED_ZSCORE_REVERSION_SCOPE.md) | **Frozen rule (binding precommit)** |
| [`CAMPAIGN_027_EDGE_DISCOVERY_ARTIFACT_CONTRACT.md`](CAMPAIGN_027_EDGE_DISCOVERY_ARTIFACT_CONTRACT.md) | Edge-discovery-compatible artifact contract |
| [`../../research/campaign_027/artifact_contract.json`](../../research/campaign_027/artifact_contract.json) | Machine-readable artifact contract (scaffold-safe) |
| [`CAMPAIGN_027_BACKTRADER_PARITY_DESIGN.md`](CAMPAIGN_027_BACKTRADER_PARITY_DESIGN.md) | Backtrader parity design (design only) |
| [`NEXT_SPRINT_PROMPT_AFTER_CAMPAIGN_027_SCAFFOLD.md`](NEXT_SPRINT_PROMPT_AFTER_CAMPAIGN_027_SCAFFOLD.md) | Future train/validation prompt (NOT executed) |
| [`../../configs/campaign_027_h4_filtered_zscore_reversion.yaml`](../../configs/campaign_027_h4_filtered_zscore_reversion.yaml) | Campaign config (`not_approved`, scaffold_only) |
| [`../../src/forex_bot/strategies/h4_filtered_zscore_reversion.py`](../../src/forex_bot/strategies/h4_filtered_zscore_reversion.py) | Short-only pure-signal strategy module |
| [`../../scripts/run_campaign_027_h4_filtered_zscore_reversion.py`](../../scripts/run_campaign_027_h4_filtered_zscore_reversion.py) | Preflight-only runner (refuses evidence modes) |
| [`CAMPAIGN_027_H4_FILTERED_ZSCORE_REVERSION_SCAFFOLD_001_SUMMARY.md`](CAMPAIGN_027_H4_FILTERED_ZSCORE_REVERSION_SCAFFOLD_001_SUMMARY.md) | **Sprint close-out (25-item summary)** |

## Infra cross-asset real data ingest (INFRA_CROSS_ASSET_REAL_DATA_INGEST_001)

> **Implementation infrastructure / data only** — `strategy_evidence: false`. No
> strategy approved. No CAMPAIGN_018. FRED fetch blocked without API key;
> normalized pipeline operational on fixture window. Recommended next sprint:
> `infra-external-data-ingest-blocker-resolution-001`.

| document | purpose |
|---|---|
| [`INFRA_CROSS_ASSET_REAL_DATA_INGEST_001_PLAN.md`](INFRA_CROSS_ASSET_REAL_DATA_INGEST_001_PLAN.md) | Sprint plan and truth audit |
| [`INFRA_CROSS_ASSET_REAL_DATA_INGEST_001_SUMMARY.md`](INFRA_CROSS_ASSET_REAL_DATA_INGEST_001_SUMMARY.md) | Sprint close-out |
| [`CROSS_ASSET_REAL_DATA_SOURCE_REGISTRY.md`](CROSS_ASSET_REAL_DATA_SOURCE_REGISTRY.md) | Human-readable source registry |
| [`CROSS_ASSET_FRED_INGEST_RUNBOOK.md`](CROSS_ASSET_FRED_INGEST_RUNBOOK.md) | FRED fetch + local CSV runbook |
| [`CROSS_ASSET_H4_ALIGNMENT_AUDIT.md`](CROSS_ASSET_H4_ALIGNMENT_AUDIT.md) | No-lookahead alignment audit |
| [`COT_FEATURE_INGEST_DESIGN.md`](COT_FEATURE_INGEST_DESIGN.md) | COT design (DESIGN_ONLY) |
| [`CROSS_ASSET_REAL_DATA_DIAGNOSTIC_IMPACT.md`](CROSS_ASSET_REAL_DATA_DIAGNOSTIC_IMPACT.md) | Diagnostic impact (no edge claims) |
| [`research/cross_asset_features/source_registry.json`](../../research/cross_asset_features/source_registry.json) | Machine-readable registry |
| [`research/cross_asset_features/normalized_features_manifest.json`](../../research/cross_asset_features/normalized_features_manifest.json) | Normalized feature manifest |
| [`research/cross_asset_features/fred_fetch_blocked_report.json`](../../research/cross_asset_features/fred_fetch_blocked_report.json) | FRED auth blocked report |

## Infra MTF confluence and cost atlas (INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001)

> **Implementation infrastructure only** — `strategy_evidence: false`. No
> strategy approved. No CAMPAIGN_018. Executor unchanged. Superseded for
> cross-asset data by `infra-cross-asset-real-data-ingest-001`.

| document | purpose |
|---|---|
| [`INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_PLAN.md`](INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_PLAN.md) | Sprint plan and truth audit |
| [`INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_SUMMARY.md`](INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_SUMMARY.md) | Sprint close-out |
| [`MTF_CONFLUENCE_PROTOTYPE_DESIGN_NOTES.md`](MTF_CONFLUENCE_PROTOTYPE_DESIGN_NOTES.md) | Confluence prototype design |
| [`CROSS_ASSET_FEATURE_INGEST_001.md`](CROSS_ASSET_FEATURE_INGEST_001.md) | Cross-asset CSV scaffolding |
| [`MTF_CONFLUENCE_AND_COST_ATLAS_DIAGNOSTICS_001.md`](MTF_CONFLUENCE_AND_COST_ATLAS_DIAGNOSTICS_001.md) | Diagnostic runner output |
| [`HIGH_PROBABILITY_TRADE_VALIDATION_PROTOCOL.md`](HIGH_PROBABILITY_TRADE_VALIDATION_PROTOCOL.md) | Future validation pre-registration template |
| [`research/cost_atlas/README.md`](../../research/cost_atlas/README.md) | Cost atlas outputs |
| [`research/cross_asset_features/feature_schema.md`](../../research/cross_asset_features/feature_schema.md) | Feature CSV schema |

## Post-dedup failure meta-analysis (POST_DEDUP_FAILURE_META_ANALYSIS_001)

| document | purpose |
|---|---|
| [`POST_DEDUP_FAILURE_META_ANALYSIS_001_PLAN.md`](POST_DEDUP_FAILURE_META_ANALYSIS_001_PLAN.md) | Sprint plan |
| [`POST_DEDUP_CAMPAIGN_METRIC_MATRIX.md`](POST_DEDUP_CAMPAIGN_METRIC_MATRIX.md) | Headline metric matrix |
| [`POST_DEDUP_ARCHETYPE_ANALYSIS.md`](POST_DEDUP_ARCHETYPE_ANALYSIS.md) | Pair/fold/side/exit synthesis |
| [`POST_DEDUP_NEXT_RESEARCH_LANE_DECISION.md`](POST_DEDUP_NEXT_RESEARCH_LANE_DECISION.md) | Lane: pause broad search |

Machine-readable: [`research/post_dedup_meta/campaign_metric_matrix.json`](../../research/post_dedup_meta/campaign_metric_matrix.json), [`research/post_dedup_meta/archetype_analysis.json`](../../research/post_dedup_meta/archetype_analysis.json).

## Evidence integrity after dedupe fix (CAMPAIGN_CONTAMINATION_AUDIT_001)

Duplicate UTC H4 bars in `data/campaign_002.sqlite3` contaminated
pre-fix bespoke loads via `CandleRepo.list` (fixed commit `30b4654`,
`keep_last`). Authoritative classification:

| doc | purpose |
|---|---|
| [`CAMPAIGN_EVIDENCE_INTEGRITY_AFTER_DEDUP_FIX.md`](CAMPAIGN_EVIDENCE_INTEGRITY_AFTER_DEDUP_FIX.md) | per-campaign integrity status CAMPAIGN_001–015 |
| [`CAMPAIGN_DATA_SOURCE_INVENTORY.md`](CAMPAIGN_DATA_SOURCE_INVENTORY.md) | artifact/data-source scan summary |
| [`POST_DEDUP_RERUN_BACKLOG.md`](POST_DEDUP_RERUN_BACKLOG.md) | ranked rerun priorities |
| [`POST_DEDUP_NULL_REFERENCE_REFRESH_001_SUMMARY.md`](POST_DEDUP_NULL_REFERENCE_REFRESH_001_SUMMARY.md) | CAMPAIGN_012–014 null-reference refresh close-out |
| [`POST_DEDUP_NULL_REFERENCE_INVENTORY.md`](POST_DEDUP_NULL_REFERENCE_INVENTORY.md) | scanned null-reference inventory |
| [`CAMPAIGN_CONTAMINATION_AUDIT_001_SUMMARY.md`](CAMPAIGN_CONTAMINATION_AUDIT_001_SUMMARY.md) | sprint close-out |

**Integrity legend:** `DEDUP-SAFE` · `SUPERSEDED BY DEDUP AUDIT` ·
`EVIDENCE INTEGRITY UNKNOWN — RERUN REQUIRED BEFORE USE` (likely
contaminated, verdict unchanged until rerun).

## Campaign reports

| campaign | report | verdict | key metrics |
|---|---|---|---|
| 001 | [`backtests/CAMPAIGN_001_REPORT.md`](../../backtests/CAMPAIGN_001_REPORT.md) | not evidence | **Synthetic** candles (no OANDA creds at the time) — harness validation only; superseded by 002 |
| 002 | [`backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md`](../../backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md) | **REJECT** | trend_following baseline, real OANDA H4/H1: −0.085 R, PF 0.75, −1.02 % · **EVIDENCE INTEGRITY UNKNOWN — RERUN REQUIRED BEFORE USE** (pre-fix SQLite) |
| 003 | [`backtests/CAMPAIGN_003_CONTROLLED_ADX_REPORT.md`](../../backtests/CAMPAIGN_003_CONTROLLED_ADX_REPORT.md) | **REJECT** | trend_following + ADX-14 > 25 gate, real OANDA H4: −0.071 R, PF 0.77, −0.63 % · **EVIDENCE INTEGRITY UNKNOWN — RERUN REQUIRED BEFORE USE** |
| 004 | [`backtests/CAMPAIGN_004_VOLATILITY_BREAKOUT_REPORT.md`](../../backtests/CAMPAIGN_004_VOLATILITY_BREAKOUT_REPORT.md) | **REJECT** | volatility_breakout (ATR compression), real OANDA H4: −0.163 R, PF 0.63, −1.40 % · **EVIDENCE INTEGRITY UNKNOWN — RERUN REQUIRED BEFORE USE** |
| 005 | [`backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md`](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md) | diagnostic | benchmarks: random entry −0.095 R; efficiency ratio 0.24 · **EVIDENCE INTEGRITY UNKNOWN — RERUN REQUIRED BEFORE USE** |
| 006 | [`backtests/CAMPAIGN_006_DAILY_TREND_REPORT.md`](../../backtests/CAMPAIGN_006_DAILY_TREND_REPORT.md) | **REJECT** — no valid result | D1 trend untestable: rollover / session / spread contamination (infrastructure blocker) · **DEDUP-SAFE** (blocked; no H4 duplicate exposure) |
| 007 | [`backtests/CAMPAIGN_007_H4_PULLBACK_REPORT.md`](../../backtests/CAMPAIGN_007_H4_PULLBACK_REPORT.md) | **REJECT** | H4 pullback-continuation: screening fail, train −0.164 R, validation −0.166 R · **EVIDENCE INTEGRITY UNKNOWN — RERUN REQUIRED BEFORE USE** |
| 008 | [`backtests/CAMPAIGN_008_RANGE_MEAN_REVERSION_REPORT.md`](../../backtests/CAMPAIGN_008_RANGE_MEAN_REVERSION_REPORT.md) | **REJECT** (narrow) | range mean-reversion: train −0.017 R (failing gate); validation +0.172 R, PF 1.29, 6/6 pairs positive · **EVIDENCE INTEGRITY UNKNOWN — RERUN REQUIRED BEFORE USE** |
| 009 | [`backtests/CAMPAIGN_009_MEAN_REVERSION_REPORT.md`](../../backtests/CAMPAIGN_009_MEAN_REVERSION_REPORT.md) | **REJECT** | mean-reversion + midline-target exit: train −0.062 R (failing gate); validation +0.170 R, PF 1.37 · **EVIDENCE INTEGRITY UNKNOWN — RERUN REQUIRED BEFORE USE** |
| 010 | [`docs/research/CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md) | **REJECT** | session_breakout walk-forward: exp_r −0.0408, 2791 trades · **EVIDENCE INTEGRITY UNKNOWN — RERUN REQUIRED BEFORE USE** |
| 011 | [`docs/research/CAMPAIGN_011_DEDUPED_NULL_BASELINE.md`](CAMPAIGN_011_DEDUPED_NULL_BASELINE.md) | **REJECT** (null anchor) | random_entry_anchor deduped canonical: exp_r −0.0029, 1180 trades · [`campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json) · pre-fix WALK_FORWARD_RESULT **SUPERSEDED** |
| 012 | [`docs/research/CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md) | **REJECT** | regime_switcher: exp_r −0.0521 · **LIKELY_CONTAMINATED** metrics; null gap refreshed vs deduped null (−0.0029 R) — verdict unchanged |
| 013 | [`docs/research/CAMPAIGN_013_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_013_POST_DEDUP_NULL_REFERENCE.md) | **REJECT** | cross_pair rotation: exp_r −0.0564 · **LIKELY_CONTAMINATED** metrics; null gap refreshed — verdict unchanged |
| 014 | [`docs/research/CAMPAIGN_014_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_014_POST_DEDUP_NULL_REFERENCE.md) | **REJECT** | calendar event window: exp_r −0.148 · **LIKELY_CONTAMINATED** metrics; null gap refreshed — verdict unchanged |
| 015 | [`docs/research/CAMPAIGN_015_DEDUPED_RERUN_RESULT.md`](CAMPAIGN_015_DEDUPED_RERUN_RESULT.md) | **REJECT** | failed_breakout_reversal deduped rerun: exp_r **−0.0101**, 375 trades, **DEDUP-SAFE**; prior bespoke **SUPERSEDED BY DEDUP AUDIT** |
| 016 | [`docs/research/CAMPAIGN_016_WEEKLY_CROSS_SECTIONAL_MOMENTUM_RESULT.md`](CAMPAIGN_016_WEEKLY_CROSS_SECTIONAL_MOMENTUM_RESULT.md) | **REJECT** | weekly_cross_sectional_momentum deduped: exp_r **−0.0633**, 137 trades, 3/8 folds, **DEDUP-SAFE**; anti-overfit **WITHIN_NULL** |
| 017 | [`docs/research/CAMPAIGN_017_WEEKLY_VOLATILITY_CONTRACTION_BREAKOUT_RESULT.md`](CAMPAIGN_017_WEEKLY_VOLATILITY_CONTRACTION_BREAKOUT_RESULT.md) | **REJECT** | weekly_volatility_contraction_breakout deduped: exp_r **−0.0227**, 230 trades, 3/8 folds, **DEDUP-SAFE**; anti-overfit **WITHIN_NULL** |

## Research Marathon 001

A disciplined four-campaign ladder (005–008) under one supervisor spec.

| document | what it is |
|---|---|
| [`docs/research/RESEARCH_MARATHON_001_PLAN.md`](RESEARCH_MARATHON_001_PLAN.md) | marathon plan / supervisor spec |
| [`docs/research/RESEARCH_MARATHON_001_LEDGER.md`](RESEARCH_MARATHON_001_LEDGER.md) | campaign-by-campaign running ledger |
| [`docs/research/RESEARCH_MARATHON_001_NO_GO.md`](RESEARCH_MARATHON_001_NO_GO.md) | **close-out: NO-GO** — no hypothesis earned PAPER-TRADE-ONLY |
| [`docs/research/RESUME_RESEARCH_MARATHON_001.md`](RESUME_RESEARCH_MARATHON_001.md) | marathon resume / handover notes |

## Pre-commit specs (the discipline trail)

Each campaign's pass/fail gates, fixed and committed *before* the run.

| campaign | pre-commit |
|---|---|
| 004 | [`docs/research/CAMPAIGN_004_PRECOMMIT.md`](CAMPAIGN_004_PRECOMMIT.md) |
| 005 | [`docs/research/CAMPAIGN_005_BENCHMARKS_PRECOMMIT.md`](CAMPAIGN_005_BENCHMARKS_PRECOMMIT.md) |
| 006 | [`docs/research/CAMPAIGN_006_DAILY_TREND_PRECOMMIT.md`](CAMPAIGN_006_DAILY_TREND_PRECOMMIT.md) |
| 007 | [`docs/research/CAMPAIGN_007_H4_PULLBACK_PRECOMMIT.md`](CAMPAIGN_007_H4_PULLBACK_PRECOMMIT.md) |
| 008 | [`docs/research/CAMPAIGN_008_RANGE_MEAN_REVERSION_PRECOMMIT.md`](CAMPAIGN_008_RANGE_MEAN_REVERSION_PRECOMMIT.md) |
| 009 | [`docs/research/CAMPAIGN_009_PRECOMMIT.md`](CAMPAIGN_009_PRECOMMIT.md) |
| 015 | [`docs/research/CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_PRECOMMIT.md`](CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_PRECOMMIT.md) |
| 016 | [`docs/research/CAMPAIGN_016_WEEKLY_CROSS_SECTIONAL_MOMENTUM_PRECOMMIT.md`](CAMPAIGN_016_WEEKLY_CROSS_SECTIONAL_MOMENTUM_PRECOMMIT.md) |
| 017 | [`docs/research/CAMPAIGN_017_WEEKLY_VOLATILITY_CONTRACTION_BREAKOUT_PRECOMMIT.md`](CAMPAIGN_017_WEEKLY_VOLATILITY_CONTRACTION_BREAKOUT_PRECOMMIT.md) |

## Post-mortems, proposals & diagnostics

| document | what it is |
|---|---|
| [`docs/research/CAMPAIGN_002_POSTMORTEM.md`](CAMPAIGN_002_POSTMORTEM.md) | post-mortem of the trend baseline rejection |
| [`docs/research/CAMPAIGN_003_POSTMORTEM.md`](CAMPAIGN_003_POSTMORTEM.md) | post-mortem of the ADX-trend rejection |
| [`docs/research/CAMPAIGN_003_PROPOSAL.md`](CAMPAIGN_003_PROPOSAL.md) | proposal that led to the ADX campaign |
| [`docs/research/HYPOTHESIS_BACKLOG.md`](HYPOTHESIS_BACKLOG.md) | campaign-era hypothesis backlog |
| [`docs/research/CAMPAIGN_008_HUMAN_REVIEW.md`](CAMPAIGN_008_HUMAN_REVIEW.md) | human review authorizing the CAMPAIGN_009 follow-up |
| [`docs/strategy_research.md`](../strategy_research.md) | strategy-research overview / methodology |
| [`docs/financing_decision.md`](../financing_decision.md) | financing investigation & decision |

Diagnostics scripts live under `scripts/` (e.g. `diagnostics_campaign_002.py`),
and per-run risk-rejection CSVs are committed under each campaign's
`backtests/campaign_00X*/runs/` tree.

## Diagnostic & parity artifacts (NOT strategy evidence)

Infrastructure outputs from the `infra-execution-fidelity-001`,
`infra-data-parity-001`, `oanda-practice-readonly-001`,
`infra-lean-parity-001`, `infra-lean-parity-run-001`,
`infra-lean-parity-execute-001`, and `infra-retire-quantconnect-lean-001`
sprints. **These are not campaign evidence.**
They are mechanical plumbing checks and independent-verification
inputs — none measures, implies, or can establish a strategy edge, and
none can approve anything. The machine-readable manifest lists them
under `diagnostic_artifacts` with `strategy_evidence: false`, enforced
by `scripts/validate_research_archive.py`.

| artifact | what it is |
|---|---|
| [`backtests/diagnostics/d1agg_next_open_smoke.md`](../../backtests/diagnostics/d1agg_next_open_smoke.md) | D1AGG + next-bar-open fill-path smoke (single-pair) |
| [`backtests/diagnostics/d1agg_next_open_six_pair_smoke.md`](../../backtests/diagnostics/d1agg_next_open_six_pair_smoke.md) | D1AGG + next-bar-open smoke across the six majors |
| [`research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.md`](../../research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.md) | Lean-parity export bundle for the CAMPAIGN_002 H4 baseline (seven pairs) |
| [`backtests/diagnostics/custom_campaign_002_h4_parity.md`](../../backtests/diagnostics/custom_campaign_002_h4_parity.md) | custom-engine reproduction of the rejected CAMPAIGN_002 H4 baseline |
| [`NEXT_BAR_OPEN_REFERENCE_COMPARISON_RESULT.md`](NEXT_BAR_OPEN_REFERENCE_COMPARISON_RESULT.md) | CAMPAIGN_019 `signal_bar_close` vs `next_bar_open` (WARN remediation 001) |
| [`research/fill_timing_reference_comparison/run_manifest.json`](../../research/fill_timing_reference_comparison/run_manifest.json) | Fill-timing comparison manifest (`strategy_evidence: false`) |
| [`research/financing_overlay_local_first/run_manifest.json`](../../research/financing_overlay_local_first/run_manifest.json) | Financing overlay manifest (`strategy_evidence: false`) |

### Shared audit WARN remediation (`infra-shared-audit-warn-remediation-and-next-bar-open-001`)

> **Infrastructure only** — addresses audit WARNs (fill timing, HTF align, RSI policy, signal provenance). **No strategy approval.**

| document | purpose |
|---|---|
| [`SHARED_AUDIT_WARN_REMEDIATION_AND_NEXT_BAR_OPEN_001_PLAN.md`](SHARED_AUDIT_WARN_REMEDIATION_AND_NEXT_BAR_OPEN_001_PLAN.md) | Sprint plan |
| [`SHARED_AUDIT_WARN_REMEDIATION_AND_NEXT_BAR_OPEN_001_SUMMARY.md`](SHARED_AUDIT_WARN_REMEDIATION_AND_NEXT_BAR_OPEN_001_SUMMARY.md) | Close-out |
| [`NEXT_BAR_OPEN_REFERENCE_COMPARISON_DESIGN.md`](NEXT_BAR_OPEN_REFERENCE_COMPARISON_DESIGN.md) | Comparison design |
| [`NEXT_BAR_OPEN_REFERENCE_COMPARISON_RESULT.md`](NEXT_BAR_OPEN_REFERENCE_COMPARISON_RESULT.md) | Comparison results |
| [`SHARED_HTF_ALIGN_MODULE_RESULT.md`](SHARED_HTF_ALIGN_MODULE_RESULT.md) | `htf_align` module |
| [`CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_WARN_REMEDIATION.md`](CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_WARN_REMEDIATION.md) | Validity impact |

### next_bar_open policy + HTF align migration (`infra-next-bar-open-policy-and-htf-align-migration-001`)

> **Infrastructure only** — mechanical `fill_timing` policy for approval-bound evidence; regime-switcher D1AGG path migrated to `d1agg_htf` / `htf_align`. **No strategy approval. CAMPAIGN_020 not created.**

| document | purpose |
|---|---|
| [`NEXT_BAR_OPEN_POLICY_AND_HTF_ALIGN_MIGRATION_001_PLAN.md`](NEXT_BAR_OPEN_POLICY_AND_HTF_ALIGN_MIGRATION_001_PLAN.md) | Sprint plan |
| [`FILL_TIMING_APPROVAL_BOUND_POLICY.md`](FILL_TIMING_APPROVAL_BOUND_POLICY.md) | Canonical fill-timing policy |
| [`FILL_TIMING_POLICY_VALIDATION_RESULT.md`](FILL_TIMING_POLICY_VALIDATION_RESULT.md) | Schema / validation |
| [`FILL_TIMING_EVIDENCE_MANIFEST_INTEGRATION_RESULT.md`](FILL_TIMING_EVIDENCE_MANIFEST_INTEGRATION_RESULT.md) | Manifest integration |
| [`NEXT_BAR_OPEN_APPROVAL_GATE_RESULT.md`](NEXT_BAR_OPEN_APPROVAL_GATE_RESULT.md) | Promotion gate |
| [`HTF_ALIGN_MIGRATION_DESIGN.md`](HTF_ALIGN_MIGRATION_DESIGN.md) | HTF migration design |
| [`HTF_ALIGN_MIGRATION_RESULT.md`](HTF_ALIGN_MIGRATION_RESULT.md) | HTF migration result |
| [`HTF_ALIGNMENT_POLICY_FOR_FUTURE_STRATEGIES.md`](HTF_ALIGNMENT_POLICY_FOR_FUTURE_STRATEGIES.md) | Future HTF policy |
| [`CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_NEXT_BAR_OPEN_POLICY_AND_HTF_MIGRATION.md`](CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_NEXT_BAR_OPEN_POLICY_AND_HTF_MIGRATION.md) | Validity impact |
| [`NEXT_BAR_OPEN_POLICY_AND_HTF_ALIGN_MIGRATION_001_SUMMARY.md`](NEXT_BAR_OPEN_POLICY_AND_HTF_ALIGN_MIGRATION_001_SUMMARY.md) | Close-out |

### Observed financing capture read-only 002 (`infra-observed-financing-capture-readonly-002`)

> **Read-only infrastructure** — practice transaction inspection only; capture **blocked** in CI runner (`BLOCKED_READONLY_CREDENTIALS`); prior practice history **empty**. **No strategy approval.**

| document | purpose |
|---|---|
| [`OBSERVED_FINANCING_CAPTURE_READONLY_002_PLAN.md`](OBSERVED_FINANCING_CAPTURE_READONLY_002_PLAN.md) | Sprint plan |
| [`OANDA_READONLY_ENDPOINT_SAFETY_REVIEW.md`](OANDA_READONLY_ENDPOINT_SAFETY_REVIEW.md) | Allowlist / denylist |
| [`OBSERVED_FINANCING_FIXTURE_SCHEMA.md`](OBSERVED_FINANCING_FIXTURE_SCHEMA.md) | Sanitized fixture schema |
| [`OBSERVED_FINANCING_CAPTURE_SCRIPT_RESULT.md`](OBSERVED_FINANCING_CAPTURE_SCRIPT_RESULT.md) | Capture script |
| [`OBSERVED_FINANCING_CAPTURE_BLOCKED.md`](OBSERVED_FINANCING_CAPTURE_BLOCKED.md) | Blocker classification |
| [`OBSERVED_FINANCING_CAPTURE_READONLY_RESULT.md`](OBSERVED_FINANCING_CAPTURE_READONLY_RESULT.md) | Capture result |
| [`OBSERVED_VS_SYNTHETIC_FINANCING_RECONCILIATION.md`](OBSERVED_VS_SYNTHETIC_FINANCING_RECONCILIATION.md) | Reconciliation |
| [`OBSERVED_FINANCING_OVERLAY_REFERENCE_RESULT.md`](OBSERVED_FINANCING_OVERLAY_REFERENCE_RESULT.md) | Reference overlay |
| [`CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_OBSERVED_FINANCING_CAPTURE.md`](CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_OBSERVED_FINANCING_CAPTURE.md) | Validity impact |
| [`OBSERVED_FINANCING_CAPTURE_READONLY_002_SUMMARY.md`](OBSERVED_FINANCING_CAPTURE_READONLY_002_SUMMARY.md) | Close-out |
| [`research/observed_financing_capture_readonly/run_manifest.json`](../../research/observed_financing_capture_readonly/run_manifest.json) | Run manifest |

### Financing overlay local-first (`infra-observed-cost-financing-overlay-local-first-001`)

> **Infrastructure only** — trade-ledger financing overlay; synthetic/manual fixtures; no broker I/O; **no strategy approval.**

| document | purpose |
|---|---|
| [`OBSERVED_COST_FINANCING_OVERLAY_LOCAL_FIRST_001_PLAN.md`](OBSERVED_COST_FINANCING_OVERLAY_LOCAL_FIRST_001_PLAN.md) | Sprint plan |
| [`FINANCING_OVERLAY_LEDGER_INVENTORY.md`](FINANCING_OVERLAY_LEDGER_INVENTORY.md) | Ledger inventory + selection |
| [`FINANCING_OVERLAY_CONTRACT.md`](FINANCING_OVERLAY_CONTRACT.md) | Overlay contract |
| [`FINANCING_FIXTURE_SUPPORT_LOCAL_FIRST_RESULT.md`](FINANCING_FIXTURE_SUPPORT_LOCAL_FIRST_RESULT.md) | Fixture support |
| [`FINANCING_OVERLAY_LOCAL_FIRST_RESULT.md`](FINANCING_OVERLAY_LOCAL_FIRST_RESULT.md) | Overlay run results |
| [`SPREAD_COST_AND_FINANCING_SENSITIVITY_LINKAGE.md`](SPREAD_COST_AND_FINANCING_SENSITIVITY_LINKAGE.md) | Cost atlas linkage |
| [`CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_FINANCING_OVERLAY_LOCAL_FIRST.md`](CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_FINANCING_OVERLAY_LOCAL_FIRST.md) | Validity impact |
| [`OBSERVED_FINANCING_CAPTURE_READ_ONLY_NEXT_PROMPT.md`](OBSERVED_FINANCING_CAPTURE_READ_ONLY_NEXT_PROMPT.md) | Future read-only capture prompt |
| [`OBSERVED_COST_FINANCING_OVERLAY_LOCAL_FIRST_001_SUMMARY.md`](OBSERVED_COST_FINANCING_OVERLAY_LOCAL_FIRST_001_SUMMARY.md) | Close-out |
| [`research/financing_overlay_local_first/run_manifest.json`](../../research/financing_overlay_local_first/run_manifest.json) | Overlay manifest (`strategy_evidence: false`) |

Supporting infrastructure docs:
[fill-timing model](FILL_TIMING_MODEL.md) ·
[Lean parity execution](LEAN_PARITY_EXECUTION_GUIDE.md) (LEAN path retired — historical) ·
[Lean parity local status](LEAN_PARITY_LOCAL_STATUS.md) (LEAN path retired — historical) ·
[OANDA H4 rehydration](OANDA_H4_DATA_REHYDRATION.md) ·
[data rehydration runbook](DATA_REHYDRATION_RUNBOOK.md) ·
[data/parity sprint plan](INFRA_DATA_PARITY_001_PLAN.md).

### OANDA practice read-only integration (`oanda-practice-readonly-001`)

Read-only OANDA practice integration and data-foundation reports. All
diagnostic / infrastructure outputs — none is strategy evidence, none
approves anything, and the research freeze is unaffected.

| document | what it is |
|---|---|
| [`OANDA_PRACTICE_READONLY_001_PLAN.md`](OANDA_PRACTICE_READONLY_001_PLAN.md) | the read-only sprint plan |
| [`OANDA_PRACTICE_CREDENTIAL_CHECK.md`](OANDA_PRACTICE_CREDENTIAL_CHECK.md) | practice credential & environment gate (redacted) |
| [`OANDA_READONLY_HEALTHCHECK_RESULT.md`](OANDA_READONLY_HEALTHCHECK_RESULT.md) | read-only OANDA API healthcheck result |
| [`OANDA_INSTRUMENT_METADATA_AUDIT.md`](OANDA_INSTRUMENT_METADATA_AUDIT.md) | instrument metadata audit |
| [`OANDA_H4_REHYDRATION_RESULT.md`](OANDA_H4_REHYDRATION_RESULT.md) | real OANDA H4 store rehydration result |
| [`OANDA_H4_DATA_QUALITY_AUDIT.md`](OANDA_H4_DATA_QUALITY_AUDIT.md) | H4 data quality audit |
| [`OANDA_PRACTICE_READONLY_001_SUMMARY.md`](OANDA_PRACTICE_READONLY_001_SUMMARY.md) | sprint summary & handoff |

### Lean parity completeness (`infra-lean-parity-001`)

Independent-engine parity readiness for the CAMPAIGN_002 H4 baseline.
All diagnostic / infrastructure outputs — none is strategy evidence,
none approves anything; CAMPAIGN_002 stays REJECT.

| document | what it is |
|---|---|
| [`INFRA_LEAN_PARITY_001_PLAN.md`](INFRA_LEAN_PARITY_001_PLAN.md) | the Lean-parity sprint plan |
| [`OANDA_H4_NZDUSD_REHYDRATION_RESULT.md`](OANDA_H4_NZDUSD_REHYDRATION_RESULT.md) | NZD_USD H4 rehydration result |
| [`OANDA_H4_DATA_QUALITY_AUDIT_7PAIR.md`](OANDA_H4_DATA_QUALITY_AUDIT_7PAIR.md) | seven-pair H4 data quality audit |
| [`LEAN_PARITY_CAMPAIGN_002_BLOCKED.md`](LEAN_PARITY_CAMPAIGN_002_BLOCKED.md) | Lean dry-run blocker (`lean init` needs a QuantConnect account) |
| [`CAMPAIGN_002_H4_PARITY_STATUS.md`](CAMPAIGN_002_H4_PARITY_STATUS.md) | independent-engine parity status |
| [`INFRA_LEAN_PARITY_001_SUMMARY.md`](INFRA_LEAN_PARITY_001_SUMMARY.md) | sprint summary & handoff |

### Lean parity run (`infra-lean-parity-run-001`)

The faithful Lean parity algorithm and comparison harness for the
CAMPAIGN_002 H4 baseline. All verification infrastructure — none is
strategy evidence; CAMPAIGN_002 stays REJECT.

| document | what it is |
|---|---|
| [`INFRA_LEAN_PARITY_RUN_001_PLAN.md`](INFRA_LEAN_PARITY_RUN_001_PLAN.md) | the Lean-parity-run sprint plan |
| [`CAMPAIGN_002_LEAN_MAPPING_SPEC.md`](CAMPAIGN_002_LEAN_MAPPING_SPEC.md) | bespoke→Lean behavior mapping spec |
| [`LEAN_ALGORITHM_IMPLEMENTATION_NOTES.md`](LEAN_ALGORITHM_IMPLEMENTATION_NOTES.md) | Lean algorithm — faithful vs approximated |
| [`LEAN_PARITY_COMPARISON_METHOD.md`](LEAN_PARITY_COMPARISON_METHOD.md) | comparison metrics, tolerances, pass/fail |
| [`INFRA_LEAN_PARITY_RUN_001_SUMMARY.md`](INFRA_LEAN_PARITY_RUN_001_SUMMARY.md) | sprint summary & handoff |

### Lean parity execute attempt (`infra-lean-parity-execute-001`)

A second attempt at running the local Lean parity backtest, gated on
locally-present QuantConnect/Lean CLI credentials. Auth was absent;
execution did not proceed and no Lean result was fabricated.

| document | what it is |
|---|---|
| [`INFRA_LEAN_PARITY_EXECUTE_001_PLAN.md`](INFRA_LEAN_PARITY_EXECUTE_001_PLAN.md) | the execute-sprint plan + auth-handling rules |
| [`LEAN_LOCAL_WORKSPACE_STATUS.md`](LEAN_LOCAL_WORKSPACE_STATUS.md) | local Lean tooling / auth / workspace state |
| [`LEAN_PARITY_EXECUTE_BLOCKED.md`](LEAN_PARITY_EXECUTE_BLOCKED.md) | precise execution blocker + exact next human steps |
| [`INFRA_LEAN_PARITY_EXECUTE_001_SUMMARY.md`](INFRA_LEAN_PARITY_EXECUTE_001_SUMMARY.md) | sprint summary & handoff |

### QuantConnect/LEAN retirement (`infra-retire-quantconnect-lean-001`)

QuantConnect/LEAN CLI execution is **retired** for this project
(decision date 2026-05-22). The free-tier QuantConnect account does
not provide the API access required for the intended local LEAN CLI
workflow, and a paid QuantConnect upgrade is declined. The LEAN
algorithm / mapping spec / harness artifacts are preserved as
**historical infrastructure evidence only**; no LEAN result exists; no
LEAN comparison exists; no strategy is approved; CAMPAIGN_002 remains
**REJECT**; paper / demo / live remain blocked. The replacement
direction is a free / local independent verifier.

| document | what it is |
|---|---|
| [`QUANTCONNECT_LEAN_RETIREMENT_DECISION.md`](QUANTCONNECT_LEAN_RETIREMENT_DECISION.md) | decision record retiring the QuantConnect/LEAN path |
| [`FREE_LOCAL_PARITY_VERIFIER_PLAN.md`](FREE_LOCAL_PARITY_VERIFIER_PLAN.md) | plan for the free / local independent verifier |
| [`INFRA_RETIRE_QUANTCONNECT_LEAN_001_SUMMARY.md`](INFRA_RETIRE_QUANTCONNECT_LEAN_001_SUMMARY.md) | retirement-sprint summary & handoff |

### Free / local parity verifier implementation (`infra-free-local-parity-verifier-001`)

Implementation of the free / local independent parity verifier
designed in `FREE_LOCAL_PARITY_VERIFIER_PLAN.md`. All
diagnostic / infrastructure outputs — none is strategy evidence; none
approves anything; CAMPAIGN_002 remains REJECT.

| document | what it is |
|---|---|
| [`INFRA_FREE_LOCAL_PARITY_VERIFIER_001_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_001_PLAN.md) | the implementation-sprint plan |
| [`FREE_LOCAL_PARITY_VERIFIER_INDICATOR_FIXTURES.md`](FREE_LOCAL_PARITY_VERIFIER_INDICATOR_FIXTURES.md) | indicator fixture-test status (EMA / ATR / Donchian — 16 cases pass) |
| [`FREE_LOCAL_PARITY_VERIFIER_RULE_FIXTURES.md`](FREE_LOCAL_PARITY_VERIFIER_RULE_FIXTURES.md) | rule fixture-test status (entry / stop / trailing / fill / sizing / PnL — 31 cases pass) |
| [`FREE_LOCAL_PARITY_VERIFIER_EVENT_LOOP_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_EVENT_LOOP_STATUS.md) | event-loop status (8 integration tests pass; full-data run BLOCKED — CSVs absent) |
| [`FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md`](FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md) | comparison-harness status (11 fixture tests pass; full-data comparison BLOCKED) |
| [`FREE_LOCAL_PARITY_VERIFIER_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_STATUS.md) | headline verifier status (85 verifier-side fixture tests pass; full-data run BLOCKED locally) |
| [`INFRA_FREE_LOCAL_PARITY_VERIFIER_001_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_001_SUMMARY.md) | sprint summary & handoff |
| [`INFRA_FREE_LOCAL_PARITY_VERIFIER_002_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_002_PLAN.md) | sprint-002 plan — full-data unblock & first-run |
| [`FREE_LOCAL_PARITY_VERIFIER_DATA_UNBLOCK_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_DATA_UNBLOCK_STATUS.md) | sprint-002 data unblock status (BLOCKED — no SQLite, no creds) |
| [`FREE_LOCAL_PARITY_VERIFIER_FULL_DATA_RUN.md`](FREE_LOCAL_PARITY_VERIFIER_FULL_DATA_RUN.md) | sprint-002 first full-data run (BLOCKED — 7/7 pairs missing CSVs, exit code 2) |
| [`INFRA_FREE_LOCAL_PARITY_VERIFIER_002_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_002_SUMMARY.md) | sprint-002 summary & handoff |
| [`INFRA_FREE_LOCAL_PARITY_VERIFIER_003_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_003_PLAN.md) | sprint-003 plan — guarded OANDA-practice historical rehydrate + export + run |
| [`FREE_LOCAL_PARITY_VERIFIER_003_REHYDRATE_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_003_REHYDRATE_STATUS.md) | sprint-003 rehydrate status (BLOCKED — no creds, only `--verify` ran) |
| [`FREE_LOCAL_PARITY_VERIFIER_003_EXPORT_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_003_EXPORT_STATUS.md) | sprint-003 export status (BLOCKED — no SQLite source) |
| [`FREE_LOCAL_PARITY_VERIFIER_003_FULL_DATA_RUN.md`](FREE_LOCAL_PARITY_VERIFIER_003_FULL_DATA_RUN.md) | sprint-003 full-data run (BLOCKED — exit code 2, valid empty summary) |
| [`INFRA_FREE_LOCAL_PARITY_VERIFIER_003_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_003_SUMMARY.md) | sprint-003 summary & handoff |
| [`FREE_LOCAL_PARITY_VERIFIER_003_UNBLOCKED_RESULT.md`](FREE_LOCAL_PARITY_VERIFIER_003_UNBLOCKED_RESULT.md) | sprint-003 mid-sprint unblock — verifier ran end-to-end (post-Phase-5: 1,655 vs 1,647 trades, overall WARN; 2 verifier-side bugs fixed) |
| [`FREE_LOCAL_PARITY_VERIFIER_003_DEBUG_NOTES.md`](FREE_LOCAL_PARITY_VERIFIER_003_DEBUG_NOTES.md) | sprint-003 Phase 5 verifier-side debug notes (Bug #1 initial-stop base; Bug #2 same-bar re-entry) |
| [`INFRA_FREE_LOCAL_PARITY_VERIFIER_004_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_004_PLAN.md) | sprint-004 plan — precision / rounding closure |
| [`FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_AUDIT.md`](FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_AUDIT.md) | sprint-004 rounding audit (bespoke metadata, round_price, mismatch table) |
| [`FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_FIXES.md`](FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_FIXES.md) | sprint-004 verifier-side rounding fixes (round_price wired into initial stop; observed comparison impact negligible) |
| [`FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md`](FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md) | sprint-004 remaining-drift classification (localized to float-vs-Decimal precision; USD_CAD is the cleanest evidence) |
| [`INFRA_FREE_LOCAL_PARITY_VERIFIER_004_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_004_SUMMARY.md) | sprint-004 summary & handoff |
| [`FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md) | **single closeout reference** — verifier accepted as WARN-band corroboration; no further sprints planned unless deferral conditions are met |
| [`FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md`](FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md) | explicit deferral of the Decimal end-to-end rewrite; conditions for reopening |
| [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md) | post-verifier next-research-direction plan; recommended next branch + success criteria for any future candidate |
| [`RESEARCH_CLOSE_FREE_LOCAL_VERIFIER_AND_NEXT_DIRECTION_001_SUMMARY.md`](RESEARCH_CLOSE_FREE_LOCAL_VERIFIER_AND_NEXT_DIRECTION_001_SUMMARY.md) | closeout-sprint summary & handoff |

### Backtrader secondary lane (`infra-backtrader-secondary-lane-001`)

A second independent local verification lane built on top of the
canonical `backtrader 1.9.78.123` Python package. Adds a third-party
event-driven engine to the comparison set so the bespoke engine has
two independent re-implementations voting on its mechanics
(`research/parity_verifier/` is the first; this is the second). All
diagnostic / verification infrastructure — none is strategy evidence,
none approves anything; CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011,
CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only and
CAMPAIGN_014 remains scaffold-only. Paper / demo / live remain
blocked.

| document | what it is |
|---|---|
| [`INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md`](INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md) | the secondary-lane sprint plan |
| [`BACKTRADER_INSTALL_AND_SMOKE_RESULT.md`](BACKTRADER_INSTALL_AND_SMOKE_RESULT.md) | Phase 1 install + smoke test (`backtrader 1.9.78.123`; 7 smoke tests PASS; no broker/LEAN/credential touched) |
| [`BACKTRADER_DATA_ADAPTER_SPEC.md`](BACKTRADER_DATA_ADAPTER_SPEC.md) | Phase 2 data-adapter spec over the existing Lean parity export CSVs (sha-validated, mid OHLC derived, bid/ask + half-spread carried; 15 tests PASS) |
| [`BACKTRADER_RUNNER_CONTRACT.md`](BACKTRADER_RUNNER_CONTRACT.md) | Phase 3 campaign-agnostic runner contract + `scripts/run_backtrader_parity.py` (17 tests PASS; refuses to leak OANDA env vars) |
| [`BACKTRADER_FIRST_CAMPAIGN_ADAPTER.md`](BACKTRADER_FIRST_CAMPAIGN_ADAPTER.md) | Phase 4 CAMPAIGN_002 H4 `trend_following 0.1.0-baseline-frozen` Backtrader adapter (20 tests PASS; selection rationale vs CAMPAIGN_011) |
| [`BACKTRADER_PARITY_COMPARISON_SPEC.md`](BACKTRADER_PARITY_COMPARISON_SPEC.md) | Phase 5 comparison harness spec + `scripts/compare_backtrader_parity.py` (16 tests PASS; emits one of the 12 documented divergence labels) |
| [`BACKTRADER_PARITY_FIRST_RESULT.md`](BACKTRADER_PARITY_FIRST_RESULT.md) | Phase 6 first end-to-end CAMPAIGN_002 attempt — overall `BLOCKED` (no local CSVs / no local rehydrated SQLite store; no bug found in either engine; no verdict change) |
| [`BACKTRADER_SECOND_CAMPAIGN_BLOCKED.md`](BACKTRADER_SECOND_CAMPAIGN_BLOCKED.md) | Phase 7 second-campaign decision — `BLOCKED`, same root cause; recommends CAMPAIGN_011 (deterministic null model, ATR-only) for a future unblock sprint with the scoped 6-step next-sprint prompt |
| [`INFRA_BACKTRADER_SECONDARY_LANE_001_SUMMARY.md`](INFRA_BACKTRADER_SECONDARY_LANE_001_SUMMARY.md) | sprint summary & handoff |

### Backtrader secondary lane — real-data run (`infra-backtrader-secondary-lane-002-real-data-run`)

Follow-up sprint that attempted the real local-data CAMPAIGN_002
comparison the previous sprint scaffolded. Outcome: BLOCKED at Phase 1
on the same single artefact (`data/oanda_h4_research.sqlite3`) — the
lane itself was not changed and remains tested + ready. No campaign
verdict changed.

| document | what it is |
|---|---|
| [`BACKTRADER_REAL_DATA_RUN_002_PLAN.md`](BACKTRADER_REAL_DATA_RUN_002_PLAN.md) | Phase 0 plan + verified data-availability snapshot + the four BLOCKED criteria |
| [`BACKTRADER_REAL_DATA_PREFLIGHT_002.md`](BACKTRADER_REAL_DATA_PREFLIGHT_002.md) | Phase 1 BLOCKED preflight + the single load-bearing restore recipe (Path A — backup copy; Path B — read-only OANDA practice rehydration) |
| [`BACKTRADER_CAMPAIGN_011_BLOCKED_002.md`](BACKTRADER_CAMPAIGN_011_BLOCKED_002.md) | Phase 5 cascade-BLOCKED decision + carry-forward CAMPAIGN_011 implementation prompt (frozen parameters, R1–R8, approximation flags, test plan, reference paths) |
| [`INFRA_BACKTRADER_SECONDARY_LANE_002_SUMMARY.md`](INFRA_BACKTRADER_SECONDARY_LANE_002_SUMMARY.md) | sprint summary & handoff |

### Backtrader secondary lane — real-data run, sprint 003 (`infra-backtrader-secondary-lane-003-real-data-run`)

Successor sprint that **unblocked** Sprint 002 by locating the source
SQLite (`data/campaign_002.sqlite3`) in the main repo working
directory, regenerated the seven CAMPAIGN_002 H4 CSVs from it
(sha256-validated against committed provenance sidecars), ran the
Backtrader lane end-to-end on real data (1 647 trades — exact match
to bespoke), found and fixed one fidelity bug (R formula divided
denominator by `exit_price` for USD-base pairs — bespoke doesn't),
and produced an overall **PASS** comparison versus the bespoke
no-RiskEngine reference at sub-pip precision. CAMPAIGN_002 remains
**REJECT** — the lane corroborates that REJECT.

| document | what it is |
|---|---|
| [`BACKTRADER_REAL_DATA_RUN_003_PLAN.md`](BACKTRADER_REAL_DATA_RUN_003_PLAN.md) | Phase 0 plan; data found in main repo; Path B (regenerate from local SQLite) selected |
| [`BACKTRADER_REAL_DATA_PREFLIGHT_003.md`](BACKTRADER_REAL_DATA_PREFLIGHT_003.md) | Phase 1 — seven CSVs regenerated; sha256 matches committed provenance bit-for-bit; 69 522 H4 bars total; no OANDA call |
| [`BACKTRADER_CAMPAIGN_002_REAL_RUN_003.md`](BACKTRADER_CAMPAIGN_002_REAL_RUN_003.md) | Phase 2 — real CAMPAIGN_002 run (1 647 trades, ~10 s, no warnings, no env-var leak) |
| [`BACKTRADER_CAMPAIGN_002_REAL_COMPARISON_003.md`](BACKTRADER_CAMPAIGN_002_REAL_COMPARISON_003.md) | Phase 3 + 4 — pre-fix `SIZING_OR_PNL_MISMATCH` on USD-base pairs; root cause + Backtrader-lane R-formula fix; **post-fix overall classification: PASS** (all 7 pairs Δ expR ≤ 0.0014) |
| [`BACKTRADER_CAMPAIGN_011_BLOCKED_003.md`](BACKTRADER_CAMPAIGN_011_BLOCKED_003.md) | Phase 5 — CAMPAIGN_011 BLOCKED-by-design (no no-RiskEngine reference; per-fold artefacts vs full-window BT runner); scoped follow-up named |
| [`INFRA_BACKTRADER_SECONDARY_LANE_003_SUMMARY.md`](INFRA_BACKTRADER_SECONDARY_LANE_003_SUMMARY.md) | sprint summary & handoff; recommends `infra-bespoke-campaign-011-norisk-reference-001` as the next branch |

### Bespoke-engine CAMPAIGN_011 no-RiskEngine reference, sprint 001 (`infra-bespoke-campaign-011-norisk-reference-001`)

Produces the canonical no-RiskEngine bespoke-engine reference for
CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011` so the Backtrader
secondary lane has a clean apples-to-apples comparison target. Runs
the bespoke `BacktestEngine` with `risk_engine=None` on the
already-frozen strategy + config (no rule change, no parameter tuning,
no seed sweep). Full-window + per-fold rollup, both deterministic.
2 800 full-window trades across 7 pairs over 2020-01-01 → 2026-05-20;
1 661 per-fold trades across the 8-fold rolling plan. CAMPAIGN_011
remains **REJECT / null diagnostic anchor by design**; the reference
is hand-off infrastructure for the next Backtrader sprint.

| document | what it is |
|---|---|
| [`CAMPAIGN_011_NORISK_REFERENCE_001_PLAN.md`](CAMPAIGN_011_NORISK_REFERENCE_001_PLAN.md) | Phase 0 plan + artefact inventory + non-goals + why this cannot approve CAMPAIGN_011 |
| [`CAMPAIGN_011_NORISK_REFERENCE_CONTRACT.md`](CAMPAIGN_011_NORISK_REFERENCE_CONTRACT.md) | Phase 1 schema contract + deterministic-seed rules + full-window/per-fold scope + tolerance bands inherited from sprint 003 |
| [`CAMPAIGN_011_NORISK_REFERENCE_RUNNER.md`](CAMPAIGN_011_NORISK_REFERENCE_RUNNER.md) | Phase 2 runner doc — exact command, inputs, outputs, fail-loud modes, gitignore behaviour, safety notes |
| [`CAMPAIGN_011_NORISK_REFERENCE_RESULT.md`](CAMPAIGN_011_NORISK_REFERENCE_RESULT.md) | Phase 3 result doc — full-window per-pair metrics + per-fold rollup vs published with-RiskEngine + determinism check (`sha256 fba55057…` matched on two runs) |
| [`BACKTRADER_CAMPAIGN_011_HANDOFF_FROM_NORISK_REFERENCE.md`](BACKTRADER_CAMPAIGN_011_HANDOFF_FROM_NORISK_REFERENCE.md) | Phase 4 hand-off doc for the next Backtrader sprint (frozen rules, seed derivation requirements, tolerance bands, approximation flags, R-formula note from sprint 003); recommends `infra-backtrader-secondary-lane-004-campaign-011` as the next branch |
| [`INFRA_BESPOKE_CAMPAIGN_011_NORISK_REFERENCE_001_SUMMARY.md`](INFRA_BESPOKE_CAMPAIGN_011_NORISK_REFERENCE_001_SUMMARY.md) | sprint summary & validation |

### Backtrader secondary lane — CAMPAIGN_011 port, sprint 004 (`infra-backtrader-secondary-lane-004-campaign-011`)

Ports CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011` into the
Backtrader secondary lane and compares against the new no-RiskEngine
bespoke reference. The full-window comparison reaches **trade-for-trade
PASS** after two BT-lane fidelity fixes: (a) warmup off-by-N (the BT
adapter now respects `strategy.warmup_bars_required() = 32`, not just
the in-strategy R1 check) and (b) a same-bar EOD re-entry artefact on
the final bar (the BT adapter now closes any open trade only via
`stop()`, matching the bespoke engine's post-loop EOD close). 2 800 /
2 800 trades match by `(instrument, entry_time, side)` on all 7 pairs;
deterministic; harness verdict PASS under tight CAMPAIGN_011
tolerances. CAMPAIGN_011 remains **REJECT / null diagnostic anchor by
design** — the BT lane corroborates the REJECT verdict at sub-pip
precision; no bespoke-engine bug found.

| document | what it is |
|---|---|
| [`BACKTRADER_CAMPAIGN_011_004_PLAN.md`](BACKTRADER_CAMPAIGN_011_004_PLAN.md) | Phase 0 plan + non-goals + reference artefacts + frozen rule source + seed reproducibility requirements + safety invariants |
| [`BACKTRADER_CAMPAIGN_011_FULL_WINDOW_RUN_004.md`](BACKTRADER_CAMPAIGN_011_FULL_WINDOW_RUN_004.md) | Phase 3 — initial (pre-fix) run; 2 808 trades vs bespoke 2 800 (+8); preserved as the load-bearing finding; deterministic |
| [`BACKTRADER_CAMPAIGN_011_FULL_WINDOW_COMPARISON_004.md`](BACKTRADER_CAMPAIGN_011_FULL_WINDOW_COMPARISON_004.md) | Phase 4 — pre-fix comparison; harness verdict TOLERABLE_DRIFT, sprint-plan binding label SIGNAL_RULE_MISMATCH; per-pair Δ + ruled-out alternatives + load-bearing warmup-window root cause |
| [`BACKTRADER_CAMPAIGN_011_FIDELITY_FIX_004.md`](BACKTRADER_CAMPAIGN_011_FIDELITY_FIX_004.md) | Phase 5 — two BT-lane bugs fixed: warmup_bars_required threshold (-7 trades) + in-loop EOD close (-1 trade); post-fix 2 800 / 2 800 trade-for-trade PASS; new regression test pins the warmup constant equal to the bespoke `warmup_bars_required()` |
| [`BACKTRADER_CAMPAIGN_011_PER_FOLD_DEFERRED_004.md`](BACKTRADER_CAMPAIGN_011_PER_FOLD_DEFERRED_004.md) | Phase 6 — per-fold comparison deferred; why post-hoc slicing of the full-window BT JSONL cannot replicate the bespoke per-fold rollup; recommended `infra-backtrader-secondary-lane-005-fold-plan-support` next branch if needed |
| [`INFRA_BACKTRADER_SECONDARY_LANE_004_CAMPAIGN_011_SUMMARY.md`](INFRA_BACKTRADER_SECONDARY_LANE_004_CAMPAIGN_011_SUMMARY.md) | sprint summary & handoff |

### Walk-forward research harness (`research-walk-forward-harness-001`)

Reusable fold-generation library that future strategy campaigns
must use. Infrastructure, not a strategy. Diagnostic only — every
emitted artifact carries `strategy_evidence: false`. Sprint
adds no campaign and does not change any verdict.

| document | what it is |
|---|---|
| [`WALK_FORWARD_HARNESS_001_PLAN.md`](WALK_FORWARD_HARNESS_001_PLAN.md) | sprint plan |
| [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md) | protocol future campaigns must follow (splits, no-leakage, parameter freeze, metrics, rejection criteria, required artifacts) |
| [`CAMPAIGN_002_WALK_FORWARD_RETROSPECTIVE.md`](CAMPAIGN_002_WALK_FORWARD_RETROSPECTIVE.md) | metadata-only retrospective showing how the harness would frame CAMPAIGN_002; no re-run, no verdict change |
| [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md) | headline status — implemented pieces, tests (42 cases pass), limitations, usage |
| [`RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md`](RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md) | sprint summary & handoff |

### Research-grade financing calculator (`research-financing-model-001`)

Reusable per-day rollover-event calculator that future strategy
campaigns can attach to their trade lists for a richer, calendar-
and side-aware financing diagnostic than the existing per-trade
overlay. Infrastructure, not a strategy. Diagnostic only — every
emitted artifact carries `strategy_evidence: false` and is at
most `financing_treatment: estimated`. Sprint adds no campaign,
does not change any verdict, and does not lift the live-promotion
financing blocker.

| document | what it is |
|---|---|
| [`FINANCING_MODEL_001_PLAN.md`](FINANCING_MODEL_001_PLAN.md) | sprint plan |
| [`FINANCING_MODEL_CURRENT_ASSUMPTIONS.md`](FINANCING_MODEL_CURRENT_ASSUMPTIONS.md) | audit of how the repo currently handles (and mostly does not handle) financing in engine PnL, overlays, observed-event capture, instrument metadata, and risk |
| [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md) | protocol the new `research/financing/` calculator follows (inputs, outputs, rollover convention, triple swap, weekend skip, missing-rate fallback, currency conversion, stress mode, required/optional/deferred classification, approval-gate non-interaction) |
| [`CAMPAIGN_002_FINANCING_RETROSPECTIVE.md`](CAMPAIGN_002_FINANCING_RETROSPECTIVE.md) | diagnostic-only retrospective showing how the calculator attaches to CAMPAIGN_002-shaped positions; no real CAMPAIGN_002 artifact loaded; verdict unchanged |
| [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md) | headline status — implemented pieces, tests (71 cases pass), limitations, usage |
| [`RESEARCH_FINANCING_MODEL_001_SUMMARY.md`](RESEARCH_FINANCING_MODEL_001_SUMMARY.md) | sprint summary & handoff |

### Financing rate-source fixtures & pilot spec (`research-financing-rate-source-fixtures-001`)

The fixture format, loader/adapter, and pilot specification a
future observed-financing capture sprint will land into.
Synthetic fixtures only; **no broker data fetched**.
Infrastructure, not a strategy. Diagnostic only — every
emitted artifact carries `strategy_evidence: false`. Sprint
adds no campaign, does not change any verdict, and does not
lift the live-promotion financing blocker.

| document | what it is |
|---|---|
| [`FINANCING_RATE_SOURCE_FIXTURES_001_PLAN.md`](FINANCING_RATE_SOURCE_FIXTURES_001_PLAN.md) | sprint plan |
| [`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md) | on-disk fixture schema (observed-events + financing-rates shapes; mirrors the canonical `ObservedFinancingEvent` field-for-field) |
| [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md) | future-facing specification for the read-only `DAILY_FINANCING` capture pilot (authorization, endpoint allow-list, redaction, reconciliation, `MODELED` acceptance criteria, why `MODELED` remains blocked) |
| [`FINANCING_RATE_SOURCE_FIXTURES_STATUS.md`](FINANCING_RATE_SOURCE_FIXTURES_STATUS.md) | headline status — schema, fixtures (9 files ~9 KB), loader/adapter, tests (43 cases pass), no broker data fetched, MODELED unavailable, live blocker remains |
| [`RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md`](RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md) | sprint summary & handoff |

### Financing reconciliation tooling (`research-financing-reconciliation-tooling-001`)

Local-only CLI that reconciles an observed-financing
fixture against the calculator's prediction for the same
window. Diagnostic only — every output carries
`strategy_evidence: false` and at most
`financing_treatment: estimated`. No broker call, no
credential read. Sprint adds no campaign, does not change
any verdict, and does not lift the live-promotion blocker.

| document | what it is |
|---|---|
| [`FINANCING_RECONCILIATION_TOOLING_001_PLAN.md`](FINANCING_RECONCILIATION_TOOLING_001_PLAN.md) | sprint plan |
| [`FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md`](FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md) | CLI protocol — inputs, JSON + markdown output shapes, classification rules, exit codes, defense-in-depth MODELED guard |
| [`FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md`](FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md) | records of five synthetic runs (commands, inputs, exit codes, per-run summaries); confirms no broker / OANDA data fetched |
| [`FINANCING_RECONCILIATION_TOOLING_STATUS.md`](FINANCING_RECONCILIATION_TOOLING_STATUS.md) | headline status — script (`scripts/reconcile_financing_fixtures.py`), tests (22 cases pass), no broker data fetched, MODELED unavailable, live blocker remains |
| [`RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md`](RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md) | sprint summary & handoff |

### Observed-financing capture pilot (`research-financing-observed-capture-pilot-001`)

Read-only OANDA practice DAILY_FINANCING capture pilot.
Authorized for **practice transaction history only** —
no orders, trades, positions, pricing, mutation, or live
access. The pilot run did **not** execute (practice
credentials absent in the worktree); the script, tests,
allowlist + denylist, and dry-run path are all in place
for a future credentialed sprint. **No OANDA data
fetched. No MODELED financing. Live blocker remains.**

| document | what it is |
|---|---|
| [`FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md) | sprint plan + endpoint allow/denylist + credential / redaction rules |
| [`FINANCING_OBSERVED_CAPTURE_EXISTING_PATH_AUDIT.md`](FINANCING_OBSERVED_CAPTURE_EXISTING_PATH_AUDIT.md) | code-level audit of the existing parser / schema / repo / read-only endpoint; confirms minimal pilot wiring |
| [`FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md) | record of the attempted dry-run (no credentials → exit 2; valid pilot result) |
| [`FINANCING_OBSERVED_CAPTURE_RECONCILIATION.md`](FINANCING_OBSERVED_CAPTURE_RECONCILIATION.md) | reconciliation blocker (no captured events to reconcile); records the would-be command and the rate-fixture coverage gap |
| [`FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`](FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md) | headline status — script (`scripts/capture_oanda_observed_financing_pilot.py`), tests (27 cases pass), no broker data fetched, no MODELED, live blocker remains |
| [`RESEARCH_FINANCING_OBSERVED_CAPTURE_PILOT_001_SUMMARY.md`](RESEARCH_FINANCING_OBSERVED_CAPTURE_PILOT_001_SUMMARY.md) | sprint summary & handoff |

### Financing bp/day fixture expansion (`research-financing-bp-day-fixture-expansion-001`)

Synthetic-data sprint. Expands the rate-fixture coverage so
all seven CAMPAIGN_002 H4 universe pairs (EUR_USD,
GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD)
have committed synthetic rate fixtures + a non-EUR
observed companion. Infrastructure only — no broker call,
no code change in `research/financing/` Python, no
production-path change. Every fixture continues to feed
`TableRateSource(treatment=ESTIMATED)`; **MODELED is
refused at all four pipeline layers**. The live blocker
remains.

| document | what it is |
|---|---|
| [`FINANCING_BP_DAY_FIXTURE_EXPANSION_001_PLAN.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_001_PLAN.md) | sprint plan |
| [`FINANCING_BP_DAY_FIXTURE_EXPANSION_CONVENTIONS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_CONVENTIONS.md) | per-pair sign / precision / missing-rate / triple-swap / weekend conventions; contributor checklist for adding more pair fixtures |
| [`FINANCING_BP_DAY_FIXTURE_EXPANSION_SYNTHETIC_RUNS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_SYNTHETIC_RUNS.md) | 7 synthetic reconciliation runs (commands, exit codes, summaries); confirms no broker data fetched |
| [`FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md) | headline status — 7-pair coverage, fixture files added, tests (16 cases pass), synthetic run status, MODELED unavailable, live blocker remains |
| [`RESEARCH_FINANCING_BP_DAY_FIXTURE_EXPANSION_001_SUMMARY.md`](RESEARCH_FINANCING_BP_DAY_FIXTURE_EXPANSION_001_SUMMARY.md) | sprint summary & handoff |

### New candidate strategy discovery (`research-new-candidate-strategy-discovery-001`)

Docs-only design sprint. Produces the protocol, framework
inventory, candidate shortlist, and preferred-candidate
evaluation design for a future strategy candidate
meaningfully distinct from CAMPAIGN_002 and the other four
already-rejected families (trend_following, volatility_breakout,
pullback_continuation, mean_reversion). **No code is added**;
no strategy is implemented; no campaign is run; no approval is
granted; paper / demo / live remain blocked. The preferred
candidate (Asian-range / London-open session breakout) is
designed for a *separate, future, human-authorized* sprint
named `research-asian-london-session-breakout-001`. The
702-test baseline is preserved.

| document | what it is |
|---|---|
| [`NEXT_BRANCH_DECISION_AUDIT.md`](NEXT_BRANCH_DECISION_AUDIT.md) | Phase 0 repo-truth audit & branch decision (records the completed financing + walk-forward state, the 702-test baseline, the safety gates, and the PATH B selection) |
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md) | sprint plan — scope, non-goals, phase deliverables, safety rails, success criteria |
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md) | binding protocol — "meaningfully distinct from CAMPAIGN_002"; allowed / disallowed family categories; frozen-parameter / walk-forward / financing / risk-diagnostic requirements; six-item evidence ladder; §12 overfitting-pattern disqualifiers |
| [`STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md) | read-only inventory of every surface a new candidate plugs into (Strategy Protocol, existing 4 families, indicator primitives, bespoke BacktestEngine, RiskEngine gates, StrategyConfig, walk-forward harness API, financing calculator API, reporting, data sources) |
| [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md) | five candidates (C1 session breakout — PREFERRED; C2 carry overlay — blocked on MODELED; C3 daily-ATR regime switcher; C4 volatility-expansion straddle; C5 random-entry anchor) with 6-dimension distinctness scoring and §12 overfitting audit |
| [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md) | finalised evidence-pipeline design for C1 (frozen params, universe, timeframe, walk-forward fold design ~9 folds, per-fold + aggregate + financing + risk-diagnostic gates, no-lookahead checks, rejection criteria, required artifacts, future implementation branch name) |
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_HELPER_SCAFFOLDING_NOTE.md) | Phase B5 decision note — five helper-code options considered, all rejected with documented rationale; zero code added |
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md) | sprint summary & handoff |

### CAMPAIGN_010 candidate scaffold (`research-asian-london-session-breakout-001`)

Candidate-scaffold sprint for **C1 — Asian-range / London-open
session breakout** (strategy `session_breakout 0.1.0-c010`,
campaign label `CAMPAIGN_010`). Adds the strategy module, the
`StrategyConfig.session_breakout` schema slot, the candidate
config YAML, 33 unit + structural-audit tests, and the
candidate's pre-commit / status / smoke / readiness docs.
**CANDIDATE SCAFFOLD ONLY — not approved for paper / demo / live.**
`configs/approved_strategies.yaml` remains `approved: []`;
CAMPAIGN_002 remains REJECT; the candidate is structurally
ready for a future evidence sprint to generate walk-forward
results + financing overlay + risk diagnostics. The 735-test
baseline (702 prior + 33 new) is preserved.

| document | what it is |
|---|---|
| [`ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md) | Phase 0 sprint plan + repo truth audit (verified preconditions, 702 baseline, all safety gates) |
| [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md) | machine-facing implementation spec: candidate identity, R1–R11 rule table, session window definitions with half-open intervals + midnight wrap, frozen parameter table (12 strategy params + 2 RiskConfig params), no-lookahead rules, H4/intraday limitation risks (DST, holidays), data + risk + financing + walk-forward interface assumptions, expected test cases (≥ 24 floor), explicit non-evidence warning |
| [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md) | candidate-pre-commit citing hypothesis verbatim, implementation + config files, frozen parameters, required local-only evaluation commands, required walk-forward / financing / risk artifacts, verbatim pass/fail gates from design §8–§15, explicit no-approval statement |
| [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md) | candidate-scaffold-only status (no verdict; no campaign report; no approval; safety state confirmed) |
| [`CAMPAIGN_010_SMOKE_RESULT.md`](CAMPAIGN_010_SMOKE_RESULT.md) | Phase 5 NON-EVIDENCE smokes: config-load PASS; signal-generation unit suite PASS (33 cases); walk-forward dry-run PASS (8-fold validated plan, ≥ 6 floor satisfied); local historical backtest BLOCKED (no SQLite store) |
| [`CAMPAIGN_010_WALK_FORWARD_READINESS.md`](CAMPAIGN_010_WALK_FORWARD_READINESS.md) | walk-forward integration readiness: harness plug-in READY; fold-by-fold sketch; missing adapters (only the per-fold backtest driver); data soft-blocker (data/ empty); strict gates restated |
| [`CAMPAIGN_010_FINANCING_RISK_READINESS.md`](CAMPAIGN_010_FINANCING_RISK_READINESS.md) | financing + portfolio-risk readiness: ESTIMATED-only via default_stress_rate_source(); per-pair TableRateSource diagnostic sample; MODELED refused at four layers; expected 0–1 rollover events per trade; risk-engine diagnostic checklist with note on conservative max_open_positions=1 |
| [`ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md) | sprint summary & handoff |

### CAMPAIGN_010 walk-forward evidence (`research-asian-london-session-breakout-walk-forward-001`)

Walk-forward evidence sprint that ran the full
`PREFERRED_CANDIDATE_EVALUATION_DESIGN` pipeline against the
`session_breakout 0.1.0-c010` candidate on the 7-pair × 6-year
real OANDA practice H4 universe. Verdict: **REJECT** —
`fold_pass_rate = 0/8`, `aggregate_expectancy_r = -0.0408`,
`profit_factor = 0.04`, `pairs_positive = 1/7` (USD_CHF only,
which flips to net negative under conservative-stress financing).
CAMPAIGN_010 reclassifies from `candidate-scaffold (no verdict)`
to `rejected`. `configs/approved_strategies.yaml` remains
`approved: []`; CAMPAIGN_002 remains REJECT and untouched.
Paper / demo / live remain blocked. No broker call, no credential
read, no engine edit.

| document | what it is |
|---|---|
| [`ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_PLAN.md) | Phase 0 repo truth audit + 8-phase sprint plan; baseline 735 pytests pass; data status (existing 7-pair × 6-year H4 store reused via gitignored symlink) |
| [`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md) | Phase 1 data provenance — per-pair counts, first/last bar timestamps, recorded raw/normalized SHA-256 prefixes; reconfirms `source=oanda-practice`; no rehydration this sprint |
| [`CAMPAIGN_010_WALK_FORWARD_PLAN.md`](CAMPAIGN_010_WALK_FORWARD_PLAN.md) | Phase 2 authoritative walk-forward plan — 8 folds rolling/frozen, 540/180/180/180 days, universe 2020-01-01 → 2026-05-20, `validate_plan()` PASS, `strategy_evidence=false` Pydantic-pinned |
| [`CAMPAIGN_010_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_010_WALK_FORWARD_EXECUTION.md) | Phase 3 per-fold execution — 56 backtests (8 folds × 7 pairs) in 7.9 s, 2,791 trades, frozen-parameter assertion in runner, no implementation bug fixes required |
| [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md) | Phase 4 formal verdict — REJECT against verbatim gates from `CAMPAIGN_010_PRECOMMIT_CHECKLIST.md` §10 (5 gates fail, 4 pass) |
| [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md) | Phase 5 financing overlay — ESTIMATED + `default_stress_rate_source()` (MODELED refused at four layers); 2,483 rollover events; cashflow_home_stress_total = -$55.69; USD_CHF flips +→- under stress |
| [`CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md) | Phase 6 risk diagnostics — concurrency structurally bounded; per-pair exposure under risk cap; 75.5 % time-stop exit; RiskEngine rejected 29.8 % of raw signals as cost-unsafe |
| [`CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md) | Phase 7 verifier capability assessment — verifier capability-locked to CAMPAIGN_002 trend_following; did NOT run for CAMPAIGN_010; would only matter for a hypothetical PASS (not for this REJECT) |
| [`CAMPAIGN_010_EVIDENCE_SUMMARY.md`](CAMPAIGN_010_EVIDENCE_SUMMARY.md) | Phase 8 one-page evidence summary — headline numbers, six-evidence-ladder status, committed artifact tree, safety state |
| [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md) (updated) | now reclassified `candidate-scaffold → rejected`; verdict, gates, evidence artifacts, safety state |
| [`ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md) | sprint summary & handoff |

### New candidate strategy discovery — Sprint 002 (`research-new-candidate-strategy-discovery-002`)

Second candidate-discovery sprint, opened after CAMPAIGN_010
(`session_breakout 0.1.0-c010`) was REJECTED. Re-scores the
prior shortlist (C2-C5) against the now-5 rejected baseline,
codifies rejected-family anti-overfit guardrails, and selects
**C5 — H4 random-entry diagnostic anchor (future CAMPAIGN_011)**
as the next preferred candidate. **Selection is not approval.**
The selected candidate is a null model by design and cannot be
paper-promoted; its purpose is to validate the full evidence
pipeline and establish a per-fold + aggregate falsifiability
floor that every subsequent C2 / C3 / C4 / new-family candidate
must beat by a meaningful margin. No strategy code, no backtest,
no broker call, no approval. The 735-test baseline is preserved.

| document | what it is |
|---|---|
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_002_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_PLAN.md) | Phase 0 audit + 8-phase sprint plan; verifies safety state at the close of CAMPAIGN_010's REJECT; baseline 735 pytests pass |
| [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md) | Phase 1 — formal closeout for `session_breakout 0.1.0-c010`; codifies which session-breakout parameters are off-limits to retune; binding cooldown rule against re-attempts |
| [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md) | Phase 1 — cross-cutting anti-overfit guardrails for every future candidate; concrete illegitimate-vs-legitimate examples for each of the 7 disqualifier patterns; universe/stop/exit/data/financing/selection/verifier/approval guardrails |
| [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md) | Phase 2 — full scoring of C2 / C3 / C4 / C5 against the now-5 rejected families plus implementation complexity, engine compatibility, data availability, walk-forward compatibility, financing dependency, portfolio-risk implications, verifier feasibility, overfit risk, diagnostic value, paper-candidate suitability; blockers per candidate; recommendation = C5 |
| [`NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md) | Phase 3 — C5 selected as CAMPAIGN_011 (`random_entry_anchor 0.1.0-c011`); distinctness vs CAMPAIGN_002 + CAMPAIGN_010; why not parameter tuning; compatibility checks; success/rejection criteria; cooldown/re-attempt rule; C2 / C3 / C4 deferred (not abandoned) |
| [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md) | Phase 4 binding design — hypothesis, R1-R8 signal rules, frozen parameters (master_seed=20260523, entry_probability=0.05, atr_lookback=14, atr_multiple=2.0, max_bars=6), no-lookahead rules, config schema, walk-forward (inherits CAMPAIGN_010's 8-fold rolling/frozen 540/180/180/180), financing (ESTIMATED + conservative stress; MODELED refused), risk diagnostics (uniform-distribution expectations), verifier (extension recommended but not required for REJECT), rejection criteria + UNEXPECTED-PASS investigation playbook |
| [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md) | Phase 5a — future scaffold-branch prompt (`research-random-entry-diagnostic-anchor-001`); 8 phases; strategy module + config + ≥ 20 unit tests + research config + CAMPAIGN_011 docs + smoke; baseline 735 → ≥ 755 pytests; no backtest run |
| [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md) | Phase 5b — future evidence-branch prompt (`research-random-entry-diagnostic-anchor-walk-forward-001`); 9 phases mirroring CAMPAIGN_010 exactly; full walk-forward + financing + risk + verifier; expected verdict REJECT; UNEXPECTED-PASS playbook |
| [`NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md) | Phase 6 — five helper-code options considered, all rejected with documented rationale; zero code added; matches prior discovery sprint's identical no-helper decision |
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md) | Phase 7 — sprint summary & handoff; final validation; recommended next branch is the scaffold sprint |

### CAMPAIGN_011 candidate scaffold (`research-random-entry-diagnostic-anchor-001`)

Scaffold sprint for **CAMPAIGN_011** / `random_entry_anchor
0.1.0-c011` — the C5 diagnostic-anchor null model. Adds the
strategy module, the `StrategyConfig.random_entry_anchor`
schema slot, the candidate config YAML, 36 unit + structural-audit
tests, and the CAMPAIGN_011 pre-commit / status / smoke /
readiness docs. **CANDIDATE SCAFFOLD ONLY; NULL MODEL BY DESIGN
— cannot be approved under any circumstance.** `configs/approved_strategies.yaml`
remains `approved: []`; CAMPAIGN_002 / CAMPAIGN_010 remain
REJECT; the candidate is structurally ready for the future
evidence sprint to generate `WalkForwardResults`. The 771-test
baseline (735 prior + 36 new) is preserved.

| document | what it is |
|---|---|
| [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md) | Phase 0 sprint plan + repo truth audit (verified preconditions, 735 baseline, all safety gates) |
| [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md) | Phase 1 binding spec — R1-R8 rule table; frozen parameters (master_seed=20260523, entry_probability=0.05, atr_lookback=14, atr_multiple=2.0, max_bars=6, trailing=None); no-lookahead invariants (seed input never contains close[t]/ATR); distribution/determinism expectations; null-model restrictions |
| [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md) | candidate pre-commit; null-model hypothesis verbatim; implementation + config files; frozen parameters; binding no-seed-optimization rule; required local-only evaluation commands; required walk-forward / financing / risk artifacts; verbatim gate vector inherited from CAMPAIGN_010 §10; unexpected-PASS investigation playbook |
| [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md) | candidate-scaffold-only status; null model / diagnostic anchor; no backtest verdict yet; no evidence campaign run; no strategy approval possible (by design) |
| [`CAMPAIGN_011_SMOKE_RESULT.md`](CAMPAIGN_011_SMOKE_RESULT.md) | Phase 5 NON-EVIDENCE smokes: config-load PASS; unit-test suite PASS (36 cases); walk-forward dry-run plan PASS (8 folds; matches CAMPAIGN_010); full repo regression 771 passes. Explicit "this is not evidence" framing |
| [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_READINESS.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_READINESS.md) | scaffold readiness GREEN across all 11 dimensions; future evidence branch identity (`research-random-entry-diagnostic-anchor-walk-forward-001`); comparison vs CAMPAIGN_005 (strictly stronger anchor); pre-flight checklist |
| [`CAMPAIGN_011_WALK_FORWARD_READINESS.md`](CAMPAIGN_011_WALK_FORWARD_READINESS.md) | walk-forward integration readiness; harness plug-in READY; fold table identical to CAMPAIGN_010 (8 folds); inherited gate vector; per-fold backtest invocation deferred to future evidence sprint |
| [`CAMPAIGN_011_FINANCING_RISK_READINESS.md`](CAMPAIGN_011_FINANCING_RISK_READINESS.md) | financing + portfolio-risk readiness; ESTIMATED + conservative-stress; MODELED refused at 4 layers; expected uniform per-pair distribution and uniform session-of-day distribution (KEY contrast with CAMPAIGN_010); expected ~$30-60 cashflow_home_stress |
| [`CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md) | verifier capability-locked to CAMPAIGN_002; extension NOT required for the REJECT verdict (null model cannot be paper-promoted); recommended follow-up `infra-free-local-parity-verifier-random-entry-001` because deterministic seed allows EXACT (not WARN-band) corroboration |
| [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md) | sprint summary & handoff; recommended next branch is the evidence sprint |

### CAMPAIGN_011 walk-forward evidence (`research-random-entry-diagnostic-anchor-walk-forward-001`)

Walk-forward evidence sprint that ran the full
`PREFERRED_CANDIDATE_EVALUATION_DESIGN` pipeline against the
`random_entry_anchor 0.1.0-c011` null-model candidate on the
7-pair × 6-year real OANDA practice H4 universe. Verdict:
**REJECT (null model anchor)** — `fold_pass_rate = 0/8`,
`aggregate_expectancy_r = -0.0024` (≈ 0; null-model
signature), `profit_factor = 0.91` (≈ 1), `aggregate_return =
-0.53%` over 4 years, `pairs_positive = 3/7` (≈ uniform-noise
expectation of 3.5). USD_JPY expectancy literally **+0.0000**
to 4 dp (textbook random-walk signature). The REJECT is the
**expected and desired outcome** — it validates the evidence
pipeline by demonstrating the gates correctly REJECT a
known-zero-edge strategy with metrics consistent with random
expectations. CAMPAIGN_011 reclassifies from `scaffold-only`
to `rejected (null model anchor)`.
`configs/approved_strategies.yaml` remains `approved: []`;
CAMPAIGN_002 / CAMPAIGN_010 remain REJECT and untouched.
Paper / demo / live remain blocked. **CAMPAIGN_011 cannot be
approved by design** (null model). No broker call, no
credential read, no parameter tuning, no seed optimization.

| document | what it is |
|---|---|
| [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md) | Phase 0 repo truth audit + 10-phase sprint plan; baseline 771 pytests pass; data status (existing 7-pair × 6-year H4 store reused via gitignored symlink) |
| [`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md) | Phase 1 data provenance — per-pair counts, first/last bar timestamps, recorded raw/normalized SHA-256 prefixes; ALL HASHES MATCH CAMPAIGN_010 verbatim (same physical store; identical data; the entry-signal comparison is on byte-for-byte identical candles) |
| [`CAMPAIGN_011_WALK_FORWARD_PLAN.md`](CAMPAIGN_011_WALK_FORWARD_PLAN.md) | Phase 2 authoritative walk-forward plan — 8 folds rolling/frozen, 540/180/180/180 days, universe 2020-01-01 → 2026-05-20, IDENTICAL to CAMPAIGN_010's plan |
| [`CAMPAIGN_011_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_011_WALK_FORWARD_EXECUTION.md) | Phase 4 per-fold execution — 56 backtests (8 folds × 7 pairs) in 5.6s, 1,177 trades, frozen-parameter + master-seed (20260523) assertion held, no implementation bug fixes required |
| [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md) | Phase 5 formal verdict — REJECT (null model anchor); 4 PnL-direction gates fail, 6 structural / dominance / financing gates pass; metrics statistically consistent with random/no-edge expectations |
| [`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md) | Phase 6 financing overlay — ESTIMATED + `default_stress_rate_source()` (MODELED refused at four layers); 1,080 rollover events; cashflow_home_stress_total = -$24.38; USD_JPY flips +→- under stress; per-trade cost (-$0.023/event) consistent with CAMPAIGN_010 (-$0.022/event) |
| [`CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md) | Phase 7 risk diagnostics — per-pair ratio max/min = 1.65 (random-uniform vs CAMPAIGN_010's 12.0); session diffuse across all 4 UTC buckets (no concentration > 50%; KEY contrast vs CAMPAIGN_010's 100% London); 79% time-stop exit (matches CAMPAIGN_010); 8/8 pipeline sanity checks pass |
| [`CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md) | Phase 8 verifier capability assessment — verifier capability-locked to CAMPAIGN_002; did NOT run for CAMPAIGN_011; not required for null-model REJECT; recommended follow-up `infra-free-local-parity-verifier-random-entry-001` (uniquely valuable because deterministic-seed → EXACT, not WARN-band, corroboration is possible) |
| [`CAMPAIGN_011_EVIDENCE_SUMMARY.md`](CAMPAIGN_011_EVIDENCE_SUMMARY.md) | Phase 9 one-page evidence summary — headline numbers, null-model interpretation, falsifiability floor for future candidates, six-evidence-ladder status, comparison to CAMPAIGN_010 |
| [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md) (updated) | now reclassified `scaffold-only → rejected (null model anchor)`; verdict, gates, evidence artifacts, safety state |
| [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md) | sprint summary & handoff |

### New candidate strategy discovery — Sprint 003 (`research-new-candidate-strategy-discovery-003`)

Third candidate-discovery sprint, opened after CAMPAIGN_011
(`random_entry_anchor 0.1.0-c011`) was REJECTED as the
expected/desired null-model anchor. Codifies CAMPAIGN_011 as a
**quantitative falsifiability floor** (aggregate expectancy
−0.0024 R, profit factor 0.91, fold pass rate 0/8, pairs
positive 3/7, return −0.53 % over 4 years; USD_JPY expectancy
literally +0.0000) and defines an "indistinguishable from null"
band + "meaningful improvement over null" margins that every
future real-edge candidate must beat. Re-scores the remaining
shortlist (C2 / C3 / C4 / new-family) against the now-6 rejected
baseline (5 prior + CAMPAIGN_011 null anchor), confirms C3 has
NONE HARD blockers because the H4→D1AGG aggregator already
exists (`src/forex_bot/backtesting/d1_aggregation.py`), and
selects **C3 — Daily-ATR-percentile regime switcher (future
CAMPAIGN_012)** as the next preferred real candidate.
**Selection is not approval.** The selected candidate is
designed but not yet implemented; the discovery output is two
binding future-branch specs (scaffold + evidence). No strategy
code, no backtest, no broker call, no approval. The 771-test
baseline is preserved.

| document | what it is |
|---|---|
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_PLAN.md) | Phase 0 audit + 9-phase sprint plan; verifies safety state at the close of CAMPAIGN_011's REJECT; confirms D1AGG infrastructure already exists; baseline 771 pytests pass |
| [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) | Phase 1 — codifies CAMPAIGN_011's verbatim metrics as a quantitative falsifiability floor; defines "indistinguishable from null" band (±0.005 R / ±0.10 PF / ±2 pp / ±1 pair) and "meaningful improvement over null" margins (≥+0.0524 R / ≥+0.19 PF / ≥+5.5 pp / ≥+1 pair / 100% fold pass); 7 anti-overfit rules; binds future scaffold pre-commit + evidence verdict docs to include null-baseline reference / comparison sections |
| [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md) | Phase 2 — full scoring of C2 / C3 / C4 against the now-6 rejected baseline (incl. CAMPAIGN_011 null anchor); C2 blocked (MODELED financing); C3 NONE HARD (D1AGG infra already exists); C4 blocked (engine paired-entry); recommendation = C3 |
| [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md) | Phase 3 — C3 feasibility deep dive; frozen parameters pre-committed BEFORE any code (`daily_atr_lookback=14`, `regime_lookback_days=60`, `regime_percentile_threshold=0.70`, `min_close_move_atr_fraction=0.25`, `trend_lookback_h4_bars=4`); 6 leakage risks with concrete mitigations; safe implementation pattern in pseudocode using `aggregate_h4_to_d1`; distinctness vs every rejected family ≥5/6; feasibility GREEN |
| [`NEXT_PREFERRED_REAL_CANDIDATE_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_003.md) | Phase 4 — C3 selected as `regime_switcher_atr_percentile 0.1.0-c012` (CAMPAIGN_012); future branches `research-regime-switcher-atr-percentile-001` (scaffold) + `research-regime-switcher-atr-percentile-walk-forward-001` (evidence); distinctness tables vs CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 all 5/6; compatibility checks all GREEN; C2 / C4 deferred (not abandoned) |
| [`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md) | Phase 5 binding design — R1-R8 signal rules (warm-up 500 bars; regime via `aggregate_h4_to_d1` + Wilder ATR-14 + trailing-60 P70; H4 ATR fail-closed; close[t] vs close[t-4] trend + ATR-fraction filter; ATR-stop placement; spread delegated; emit deterministic Signal); 11 no-lookahead invariants; `RegimeSwitcherAtrPercentileStrategyConfig` Pydantic schema; ≥25 unit tests planned; walk-forward inherits CAMPAIGN_010 §10 + adds null-baseline comparison gate; `RESEARCH_PASS_UNAPPROVED` classification rule |
| [`NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md) | Phase 6a — future scaffold-branch prompt (`research-regime-switcher-atr-percentile-001`); 8 phases; strategy module + config + ≥ 25 unit tests + research config + CAMPAIGN_012 docs + smoke; baseline 771 → ≥ 796 pytests; no backtest run |
| [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md) | Phase 6b — future evidence-branch prompt (`research-regime-switcher-atr-percentile-walk-forward-001`); 9 phases mirroring CAMPAIGN_011 exactly; full walk-forward + financing + risk + verifier; verdict options REJECT / REJECT (indistinguishable from null) / RESEARCH_PASS_UNAPPROVED / BLOCKED; UNEXPECTED-PASS 5-step protocol |
| [`NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md) | Phase 7 — six helper-code options considered, all rejected with documented rationale; zero code added; matches both prior discovery sprints' identical no-helper decision |
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md) | Phase 8 — sprint summary & handoff; final validation; recommended next branch is the scaffold sprint `research-regime-switcher-atr-percentile-001` |

### CAMPAIGN_012 candidate scaffold (`research-regime-switcher-atr-percentile-001`)

Scaffold sprint for **CAMPAIGN_012** /
`regime_switcher_atr_percentile 0.1.0-c012` — the C3 daily-ATR-percentile
regime switcher selected by the
`research-new-candidate-strategy-discovery-003` sprint. Adds the strategy
module (R1-R8 per binding spec), the
`StrategyConfig.regime_switcher_atr_percentile` schema slot, 47 unit +
structural-audit tests, the candidate config YAML, and the CAMPAIGN_012
pre-commit / status / readiness / smoke docs. **CANDIDATE SCAFFOLD
ONLY — NOT APPROVED.** `configs/approved_strategies.yaml` remains
`approved: []`; CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 all remain
REJECT; the candidate is structurally ready for the future evidence
sprint to generate `WalkForwardResults`. The 818-test baseline
(771 prior + 47 new) is preserved. The future evidence sprint must
beat the CAMPAIGN_011 null-baseline floor (≥ +0.0524 R aggregate
expectancy, ≥ +0.19 PF, ≥ +5.5 pp pairs-positive, ≥ +1 pair, 100 %
fold pass rate) to count as evidence of an edge; "indistinguishable
from null" (within ± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair) is
REJECTED.

| document | what it is |
|---|---|
| [`REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md) | Phase 0 sprint plan + repo truth audit (verified 771 baseline + base commit `384314a` + D1AGG infra present + clean slate for CAMPAIGN_012) |
| [`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md) | Phase 1 binding spec — R1-R8 rule table; 12 frozen parameters (`atr_lookback=14`, `atr_stop_multiple=2.0`, `max_bars_in_trade=6`, `trailing_stop_atr_multiple=None`, `daily_atr_lookback=14`, `regime_lookback_days=60`, `regime_percentile_threshold=0.70`, `min_close_move_atr_fraction=0.25`, `trend_lookback_h4_bars=4`); 15 no-lookahead invariants; 11 fail-closed conditions; 40 expected tests |
| [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md) | candidate pre-commit; hypothesis verbatim; implementation files + frozen parameters + no-lookahead checklist; D1AGG completed-day rule; rolling percentile rule; binding null-baseline comparison gate vs CAMPAIGN_011; required walk-forward / financing / risk artifacts; verbatim gate vector inherited from CAMPAIGN_010 §10 + CAMPAIGN_011 §11; unexpected-PASS 5-step escalation protocol |
| [`CAMPAIGN_012_STATUS.md`](CAMPAIGN_012_STATUS.md) | candidate-scaffold-only status; no backtest verdict yet; no evidence campaign run; no strategy approval (cannot be approved by any research sprint); CAMPAIGN_002 / 010 / 011 all REJECT relationship; why this is a real candidate (deterministic, directional, distinct) but not approved |
| [`REGIME_SWITCHER_ATR_PERCENTILE_READINESS.md`](REGIME_SWITCHER_ATR_PERCENTILE_READINESS.md) | scaffold readiness GREEN across all 21 dimensions; future evidence branch identity `research-regime-switcher-atr-percentile-walk-forward-001`; data expectations; known limitations (verifier lock; MODELED financing); D1AGG usage; null-baseline comparison; why this is a real candidate but not approved |
| [`CAMPAIGN_012_SMOKE_RESULT.md`](CAMPAIGN_012_SMOKE_RESULT.md) | Phase 5 NON-EVIDENCE smokes: config-load PASS; unit-test suite PASS (47 cases); walk-forward dry-run plan PASS (8 folds; matches CAMPAIGN_010 / 011 verbatim); full repo regression 818 passes. Explicit "this is not evidence" framing; dry-run output written to /tmp and NOT committed |
| [`CAMPAIGN_012_WALK_FORWARD_READINESS.md`](CAMPAIGN_012_WALK_FORWARD_READINESS.md) | future-evidence walk-forward plan (inherited verbatim from CAMPAIGN_010 / 011: rolling, frozen, 540/180/180/180 days, 2020-01-01 → 2026-05-20, expected 8 folds); per-fold + aggregate gate vector; binding null-baseline comparison gate; expected artifact paths |
| [`CAMPAIGN_012_FINANCING_RISK_READINESS.md`](CAMPAIGN_012_FINANCING_RISK_READINESS.md) | future-evidence financing overlay (ESTIMATED + conservative stress; MODELED refused at 4 layers; not lifted) + portfolio-risk diagnostics (regime-period clustering as the signature; expected session-of-day diffuse across 4 UTC buckets like CAMPAIGN_011); per-instrument concurrency = 1 |
| [`CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md) | future-evidence verifier coverage; current capability lock to CAMPAIGN_002 / `trend_following`; not required for REJECT; required only on RESEARCH_PASS_UNAPPROVED via the suggested follow-up sprint `infra-free-local-parity-verifier-regime-switcher-001` |
| [`REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md) | sprint summary & handoff; final validation; recommended next branch is the evidence sprint `research-regime-switcher-atr-percentile-walk-forward-001` |

### CAMPAIGN_012 walk-forward evidence (`research-regime-switcher-atr-percentile-walk-forward-001`)

Walk-forward evidence sprint that ran the full
`PREFERRED_CANDIDATE_EVALUATION_DESIGN` pipeline against the
`regime_switcher_atr_percentile 0.1.0-c012` C3 daily-ATR-percentile
regime-switcher candidate on the 7-pair × 6-year real OANDA practice
H4 universe. Verdict: **REJECT** — 5 of 8 inherited aggregate gates
fail (`fold_pass_rate = 0/8`; `aggregate_expectancy_r = −0.0521 R`;
`profit_factor = 0.034`; `pairs_positive = 1/7`); aggregate return
`−43.52 %` over 4 years. **Markedly worse than CAMPAIGN_011 null
baseline** on every binding axis (expectancy −0.0497 R lower, PF
−0.876 lower, return −42.99 pp lower, pairs −2 lower) — well outside
the symmetric ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair
indistinguishability band; classification is **REJECT** (not
`REJECT_INDISTINGUISHABLE_FROM_NULL`, because the divergence is in
the WORSE direction). The regime gate amplified trade count (3,726 vs
1,177) without improving signal quality, accumulating cost drag.
USD_JPY's +0.0004 R is the same near-exact-zero random-walk floor
CAMPAIGN_011 surfaced. CAMPAIGN_012 reclassifies from `scaffold-only`
to `rejected`. `configs/approved_strategies.yaml` remains
`approved: []`; CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 remain
REJECT and untouched. Paper / demo / live remain blocked.
**CAMPAIGN_012 cannot be approved.** No broker call, no credential
read, no parameter tuning.

| document | what it is |
|---|---|
| [`REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md) | Phase 0 repo truth audit + 10-phase evidence-sprint plan; baseline 818 pytests pass; data status (existing 7-pair × 6-year H4 store reused via gitignored symlink) |
| [`CAMPAIGN_012_DATA_PROVENANCE.md`](CAMPAIGN_012_DATA_PROVENANCE.md) | Phase 1 data provenance — per-pair counts, first/last bar timestamps, recorded raw/normalized SHA-256 prefixes; ALL HASHES MATCH CAMPAIGN_010 / CAMPAIGN_011 verbatim (same physical store; identical data; the entry-signal comparison is on byte-for-byte identical candles) |
| [`CAMPAIGN_012_WALK_FORWARD_PLAN.md`](CAMPAIGN_012_WALK_FORWARD_PLAN.md) | Phase 2 authoritative walk-forward plan — 8 folds rolling/frozen, 540/180/180/180 days, universe 2020-01-01 → 2026-05-20, IDENTICAL to CAMPAIGN_010 / 011 plans |
| [`CAMPAIGN_012_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_012_WALK_FORWARD_EXECUTION.md) | Phase 4 per-fold execution — 56 backtests (8 folds × 7 pairs) in ~2,022 s, 3,726 trades, frozen-parameter assertion in runner, no implementation bug fixes required |
| [`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md) | Phase 5 formal verdict — REJECT; 5 of 8 inherited aggregate gates fail; CAMPAIGN_011 null-baseline comparison classifies REJECT (not REJECT_INDISTINGUISHABLE_FROM_NULL because metrics diverge from null in WORSE direction) |
| [`CAMPAIGN_012_FINANCING_OVERLAY.md`](CAMPAIGN_012_FINANCING_OVERLAY.md) | Phase 6 financing overlay — ESTIMATED + `default_stress_rate_source()` (MODELED refused at four layers); 3,404 rollover events; cashflow_home_stress_total = −$65.07; no pair flip; `conservative_stress_run_does_not_flip_verdict` PASSES (verdict already REJECT pre-financing) |
| [`CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md) | Phase 7 risk diagnostics — per-pair ratio max/min = 1.60 (uniform; close to CAMPAIGN_011's 1.65 vs CAMPAIGN_010's 12.0); session distribution diffuse across all 4 UTC buckets (no concentration > 50 %; like CAMPAIGN_011); 79.3 % time-stop exit; 8 / 8 pipeline sanity checks PASS; RiskEngine rejected 42.7 % of raw signals (SPREAD_TOO_WIDE 2013, SESSION_BLOCKED 758) |
| [`CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md) | Phase 8 verifier capability assessment — verifier capability-locked to CAMPAIGN_002 / `trend_following`; did NOT run for CAMPAIGN_012; not required for REJECT; recommended follow-up `infra-free-local-parity-verifier-regime-switcher-001` **deferred indefinitely** (no paper-promotion candidate to corroborate) |
| [`CAMPAIGN_012_EVIDENCE_SUMMARY.md`](CAMPAIGN_012_EVIDENCE_SUMMARY.md) | Phase 9 one-page evidence summary — headline numbers, null-baseline interpretation, regime-switcher interpretation (hypothesis falsified), comparison to prior REJECT campaigns (CAMPAIGN_012 has the worst aggregate return of any campaign to date) |
| [`CAMPAIGN_012_STATUS.md`](CAMPAIGN_012_STATUS.md) (updated) | now reclassified `scaffold-only → rejected`; verdict, gates, evidence artifacts, safety state |
| [`REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md`](REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md) | sprint summary & handoff |

### New candidate strategy discovery — Sprint 004 (`research-new-candidate-strategy-discovery-004`)

Fourth candidate-discovery sprint, opened after CAMPAIGN_012
(`regime_switcher_atr_percentile 0.1.0-c012`) was REJECTED.
Codifies CAMPAIGN_012's rejection closeout (off-limits parameter
surface + indefinite cooldown for the regime-switcher family);
adds 5 new disqualifying overfitting patterns (H–L) to the base
rejected-family guardrails (forbidding same-regime-different-
threshold retunes, trend-filter lookback sweeps, rank-inversion
"different cutoff" variants, rejected-family stacks, and per-fold-
artifact-driven family selection); re-scores the now-7 rejected
baseline (5 prior + CAMPAIGN_011 null + CAMPAIGN_012 real) against
4 deferred candidates (C2 / C4) + 4 infrastructure paths
(financing-MODELED-capture, paired-entry-engine-support, verifier-
extension, ruff-cleanup); proposes 4 genuinely-new candidate
families (C6 / C7 / C8 / C9); selects **C6 — Cross-Pair Currency
Strength Rotation** for future **CAMPAIGN_013 /
`cross_pair_currency_strength_rotation 0.1.0-c013`** as the next
preferred real candidate. **Selection is not approval.** The
selected candidate is designed but not yet implemented; the
discovery output is two binding future-branch specs (scaffold +
evidence). No strategy code, no backtest, no broker call, no
approval. The 818-test baseline is preserved.

| document | what it is |
|---|---|
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md) | Phase 0 audit + 10-phase sprint plan; verifies safety state at the close of CAMPAIGN_012's REJECT; baseline 818 pytests pass |
| [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md) | Phase 1 — formal closeout for `regime_switcher_atr_percentile 0.1.0-c012`; codifies which regime-switcher parameters are off-limits to retune (12 frozen parameters + 5 illegitimate extension patterns); binding cooldown rule against the regime-switcher family until a future human explicitly authorizes a "materially different" thesis |
| [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md) | Phase 2 — additive addendum to the base guardrails doc; adds Patterns H (same regime gate, different threshold), I (same trend filter, different lookback), J (same percentile, different cutoff), K (rejected-family stack), L (per-fold-artifact-driven family selection); "genuinely new" criteria (7 axes) any candidate must satisfy after the now-7 rejected baseline |
| [`NEXT_DIRECTION_REASSESSMENT_004.md`](NEXT_DIRECTION_REASSESSMENT_004.md) | Phase 3 — 15-axis scoring of 7 paths (C2 / C4 / C6+ + infra-A/B/C/D); recommends discovery-driven C6+ family selection (zero blockers; evaluable honestly today); fallback to infra-A if Phase 4 fails |
| [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md) | Phase 4 — shortlist of 4 genuinely-new families (C6 cross-pair currency strength rotation; C7 calendar-event window anomaly; C8 multi-window vol-compression breakout; C9 time-of-day cost-adjusted MR on spreads); 13 disqualified variants documented |
| [`NEXT_PREFERRED_DIRECTION_004.md`](NEXT_PREFERRED_DIRECTION_004.md) | Phase 5 — C6 selected as `cross_pair_currency_strength_rotation 0.1.0-c013` (CAMPAIGN_013); future branches `research-cross-pair-currency-strength-rotation-001` (scaffold) + `research-cross-pair-currency-strength-rotation-walk-forward-001` (evidence); distinctness vs every rejected family 6/6; Patterns H–L explicitly cleared; C7/C8/C9 and all 4 infra paths deferred (not abandoned) |
| [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md) | Phase 6 binding design — currency-strength feature definition (8 currencies; USD-base / USD-quote sign convention; USD strength = `−mean(non-USD)`); R1-R8 signal rules; 9 frozen parameters (`currency_strength_lookback_bars=24`, `rank_gap_threshold=4`, etc.); 12 no-lookahead invariants; `CrossPairCurrencyStrengthRotationStrategyConfig` schema; ≥ 30 unit tests planned; walk-forward inherits CAMPAIGN_010 §10 + adds null-baseline comparison gate; critical multi-pair-runner integration contract for the evidence sprint; cross-pair concurrent-rejection rate as CAMPAIGN_013-specific risk diagnostic |
| [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md) | Phase 7a — future scaffold-branch prompt (`research-cross-pair-currency-strength-rotation-001`); 8 phases; strategy module + config + ≥ 30 unit tests + research config + CAMPAIGN_013 docs + smoke; baseline 818 → ≥ 848 pytests; no backtest run |
| [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md) | Phase 7b — future evidence-branch prompt (`research-cross-pair-currency-strength-rotation-walk-forward-001`); 10 phases mirroring CAMPAIGN_012 evidence sprint; full walk-forward + financing + risk + verifier; verdict options REJECT / REJECT_INDISTINGUISHABLE_FROM_NULL / RESEARCH_PASS_UNAPPROVED / BLOCKED; binding cross-pair-runner integration contract |
| [`NEW_CANDIDATE_DISCOVERY_004_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_004_HELPER_DECISION.md) | Phase 8 — seven helper-code options considered, all rejected with documented rationale; zero code added; matches all three prior discovery sprints' identical no-helper decision |
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md) | Phase 9 — sprint summary & handoff; final validation; recommended next branch is the scaffold sprint `research-cross-pair-currency-strength-rotation-001` |

### CAMPAIGN_013 candidate scaffold (`research-cross-pair-currency-strength-rotation-001`)

Scaffold sprint for **CAMPAIGN_013** /
`cross_pair_currency_strength_rotation 0.1.0-c013` — the C6
cross-pair currency-strength rotation candidate selected by the
`research-new-candidate-strategy-discovery-004` sprint. Adds the
strategy module (R1-R8 per binding spec), the
`StrategyConfig.cross_pair_currency_strength_rotation` schema slot,
57 unit + structural-audit tests, the candidate config YAML, and
the CAMPAIGN_013 pre-commit / status / readiness / smoke docs.
**CANDIDATE SCAFFOLD ONLY — NOT APPROVED.**
`configs/approved_strategies.yaml` remains `approved: []`;
CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 / CAMPAIGN_012 all remain
REJECT; the candidate is structurally ready for the future evidence
sprint to generate `WalkForwardResults`. The 875-test baseline
(818 prior + 57 new) is preserved. The future evidence sprint must
beat the CAMPAIGN_011 null-baseline floor (≥ +0.0524 R aggregate
expectancy, ≥ +0.19 PF, ≥ +5.5 pp pairs-positive, ≥ +1 pair, 100 %
fold pass rate) to count as evidence of an edge; "indistinguishable
from null" (within ± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair) is
REJECTED. **Critical CAMPAIGN_013-specific evidence-runner
requirement:** must implement the cross-pair runner integration
contract (align all 7 pairs' completed H4 closes to a common index;
inject as `cross_pair_closes` into each pair's `strategy_config`).

| document | what it is |
|---|---|
| [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md) | Phase 0 sprint plan + repo truth audit (verified 818 baseline + base commit `ff34e96` + clean slate for CAMPAIGN_013) |
| [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md) | Phase 1 binding spec — R1-R8 rule table; 9 frozen parameters (`currency_strength_lookback_bars=24`, `rank_gap_threshold=4`, `atr_lookback=14`, `atr_stop_multiple=2.0`, `max_bars_in_trade=6`, `trailing_stop_atr_multiple=None`); 7-pair universe + 8-currency sign convention (USD-base = +log_return; USD-quote = −log_return; USD = −mean(non-USD)); 14 no-lookahead invariants; 10 fail-closed conditions; 51 expected tests |
| [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md) | candidate pre-commit; hypothesis verbatim; implementation files + frozen parameters + no-lookahead checklist; cross-pair-closes contract; currency-strength sign convention; rank-gap rule (inclusive at threshold); binding null-baseline comparison gate vs CAMPAIGN_011; required walk-forward / financing / risk artifacts; verbatim gate vector inherited from CAMPAIGN_010 / 011 / 012; unexpected-PASS 5-step escalation protocol |
| [`CAMPAIGN_013_STATUS.md`](CAMPAIGN_013_STATUS.md) | candidate-scaffold-only status; no backtest verdict yet; no evidence campaign run; no strategy approval (cannot be approved by any research sprint); CAMPAIGN_002 / 010 / 011 / 012 all REJECT relationship; why this is a real candidate (deterministic, directional, cross-pair structure never tested before) but not approved |
| [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_READINESS.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_READINESS.md) | scaffold readiness GREEN across 18 dimensions; future evidence branch identity `research-cross-pair-currency-strength-rotation-walk-forward-001`; data expectations; known limitations (verifier lock; MODELED financing; MAX_OPEN_POSITIONS_EXCEEDED rejection from cross-pair concurrent signals — KNOWN behavior, NOT a bug); binding cross-pair runner integration requirement; null-baseline comparison; why this is a real candidate but not approved |
| [`CAMPAIGN_013_SMOKE_RESULT.md`](CAMPAIGN_013_SMOKE_RESULT.md) | Phase 5 NON-EVIDENCE smokes: config-load PASS; unit-test suite PASS (57 cases); walk-forward dry-run plan PASS (8 folds; matches CAMPAIGN_010 / 011 / 012 verbatim); full repo regression 875 passes. Explicit "this is not evidence" framing; dry-run output written to `/tmp` and NOT committed |
| [`CAMPAIGN_013_WALK_FORWARD_READINESS.md`](CAMPAIGN_013_WALK_FORWARD_READINESS.md) | future-evidence walk-forward plan (inherited verbatim from CAMPAIGN_010 / 011 / 012: rolling, frozen, 540/180/180/180 days, 2020-01-01 → 2026-05-20, expected 8 folds); per-fold + aggregate gate vector; binding null-baseline comparison gate; **binding cross-pair runner integration contract**; expected artifact paths |
| [`CAMPAIGN_013_FINANCING_RISK_READINESS.md`](CAMPAIGN_013_FINANCING_RISK_READINESS.md) | future-evidence financing overlay (ESTIMATED + conservative stress; MODELED refused at 4 layers; not lifted) + portfolio-risk diagnostics (standard battery PLUS CAMPAIGN_013-specific: rank-gap distribution, simultaneous-signal frequency, MAX_OPEN_POSITIONS_EXCEEDED rejection rate, currency-rank flip rate, pair-direction conflict rate); per-instrument concurrency = 1 |
| [`CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md) | future-evidence verifier coverage; current capability lock to CAMPAIGN_002 / `trend_following`; not required for REJECT; required only on RESEARCH_PASS_UNAPPROVED via the suggested follow-up sprint `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001` |
| [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md) | sprint summary & handoff; final validation; recommended next branch is the evidence sprint `research-cross-pair-currency-strength-rotation-walk-forward-001` |

### CAMPAIGN_013 walk-forward evidence (`research-cross-pair-currency-strength-rotation-walk-forward-001`)

Walk-forward evidence sprint that ran the full evaluation pipeline
against the `cross_pair_currency_strength_rotation 0.1.0-c013` C6
cross-pair currency-strength rotation candidate on the 7-pair ×
6-year real OANDA practice H4 universe. Verdict: **REJECT** — 5 of
8 inherited aggregate gates fail (`fold_pass_rate = 0/8`;
`aggregate_expectancy_r = −0.0564 R`; `profit_factor = 0.000`;
`pairs_positive = 1/7`); aggregate return **−113.36 %** over 4 years
on **7,940 trades**. **Catastrophically worse than CAMPAIGN_011 null
baseline** on every binding axis (expectancy −0.0540 R lower, PF
−0.910 lower, return −112.83 pp lower, pairs −2 lower) — well
outside the symmetric ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair
indistinguishability band; classification is **REJECT** (not
`REJECT_INDISTINGUISHABLE_FROM_NULL` because the divergence is in
the WORSE direction). The rank-gap rule amplified trade count (7,940
vs CAMPAIGN_011's 1,177 — 6.7 × as many) without improving signal
quality, accumulating cost drag. USD_JPY's +0.0000 R is the same
near-exact-zero random-walk floor CAMPAIGN_011 and CAMPAIGN_012
surfaced; NZD_USD catastrophic at −41.76 % over 4 years on 1,863
trades. The **cross-pair runner integration contract was SATISFIED
on all 8 folds** (common_index 1,825-1,848 H4 bars) — the REJECT is
on inherited gates alone, not BLOCKED. Financing overlay
(ESTIMATED + conservative stress; MODELED refused at 4 layers) adds
−$139.99 drag (7,154 rollover events); USD_JPY flips + → − under
financing (+$2.27 → −$5.89), taking `pairs_positive` from 1/7 to 0/7
post-financing. Architectural diagnostic:
`MAX_OPEN_POSITIONS_EXCEEDED = 0` (per-pair runner; engine is
single-instrument); ~40 % simultaneous-signal rate (a portfolio-aware
runner would cut trade count by ~40 % but cannot rescue per-pair
negative expectancy on 6 of 7 pairs). **CAMPAIGN_013 is the
worst-performing campaign to date by aggregate return / profit
factor / trade count.** CAMPAIGN_013 reclassifies from
`scaffold-only` to `rejected`. `configs/approved_strategies.yaml`
remains `approved: []`; CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
CAMPAIGN_012 remain REJECT and untouched. Paper / demo / live remain
blocked. **CAMPAIGN_013 cannot be approved.** No broker call, no
credential read, no parameter tuning.

| document | what it is |
|---|---|
| [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md) | Phase 0 repo truth audit + 10-phase evidence-sprint plan; baseline 875 pytests pass; data status (existing 7-pair × 6-year H4 store reused via gitignored symlink) |
| [`CAMPAIGN_013_DATA_PROVENANCE.md`](CAMPAIGN_013_DATA_PROVENANCE.md) | Phase 1 data provenance — per-pair counts, first/last bar timestamps, recorded raw/normalized SHA-256 prefixes; ALL HASHES MATCH CAMPAIGN_010 / CAMPAIGN_011 / CAMPAIGN_012 verbatim (same physical store; identical data) |
| [`CAMPAIGN_013_WALK_FORWARD_PLAN.md`](CAMPAIGN_013_WALK_FORWARD_PLAN.md) | Phase 2 authoritative walk-forward plan — 8 folds rolling/frozen, 540/180/180/180 days, universe 2020-01-01 → 2026-05-20, IDENTICAL to CAMPAIGN_010 / 011 / 012 plans |
| [`CAMPAIGN_013_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_013_WALK_FORWARD_EXECUTION.md) | Phase 4 per-fold execution — 56 backtests (8 folds × 7 pairs) in ~20.2 s, 7,940 trades, frozen-parameter assertion in runner, no implementation bug fixes required, **cross-pair runner contract SATISFIED on all 8 folds** |
| [`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md) | Phase 5 formal verdict — REJECT; 5 of 8 inherited aggregate gates fail; CAMPAIGN_011 null-baseline comparison classifies REJECT (not REJECT_INDISTINGUISHABLE_FROM_NULL because metrics diverge from null in WORSE direction); NOT BLOCKED (contract satisfied) |
| [`CAMPAIGN_013_FINANCING_OVERLAY.md`](CAMPAIGN_013_FINANCING_OVERLAY.md) | Phase 6 financing overlay — ESTIMATED + `default_stress_rate_source()` (MODELED refused at four layers); 7,154 rollover events; cashflow_home_stress_total = −$139.99; USD_JPY flips + → − under financing (pairs_positive 1/7 → 0/7 post-financing); `conservative_stress_run_does_not_flip_verdict` PASSES (verdict already REJECT pre-financing) |
| [`CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md) | Phase 7 risk diagnostics — standard battery (per-pair exposure, session clustering, exit reasons, rejection codes) PLUS CAMPAIGN_013-specific (cross-pair runner contract status per fold, zero-trade pair-fold cells 29/56, per-fold long/short imbalance, simultaneous-signal frequency ~40 %, per-pair firing rate ~16-18 %); architectural finding `MAX_OPEN_POSITIONS_EXCEEDED = 0` (per-pair runner); RiskEngine rejected 41 % of raw signals (SPREAD_TOO_WIDE 3024, DRAWDOWN_LIMIT 1507, SESSION_BLOCKED 992); 76.7 % time-stop exit |
| [`CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md) | Phase 8 verifier capability assessment — verifier capability-locked to CAMPAIGN_002 / `trend_following`; did NOT run for CAMPAIGN_013; not required for REJECT; recommended follow-up `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001` **deferred indefinitely** (no paper-promotion candidate to corroborate; extension would be structurally larger than CAMPAIGN_012's would have been because of the cross-pair runner integration contract re-implementation requirement) |
| [`CAMPAIGN_013_EVIDENCE_SUMMARY.md`](CAMPAIGN_013_EVIDENCE_SUMMARY.md) | Phase 9 one-page evidence summary — headline numbers, null-baseline interpretation, cross-pair rotator interpretation (hypothesis falsified), comparison to prior REJECT campaigns (CAMPAIGN_013 is worst-performing campaign to date) |
| [`CAMPAIGN_013_STATUS.md`](CAMPAIGN_013_STATUS.md) (updated) | now reclassified `scaffold-only → rejected`; verdict, gates, evidence artifacts, safety state |
| [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md) | sprint summary & handoff |

### New candidate strategy discovery — Sprint 005 (`research-new-candidate-strategy-discovery-005`)

Fifth candidate-discovery sprint, opened after CAMPAIGN_013
(`cross_pair_currency_strength_rotation 0.1.0-c013`) was REJECTED.
Codifies CAMPAIGN_013's rejection closeout (14+ off-limits parameter
shapes + cooldown for the cross-pair-rotation family until a future
human authorizes a materially different cross-sectional FX thesis);
**establishes the turnover-amplification anti-pattern as a first-
class binding guardrail** (the monotonic CAMPAIGN_011 → 012 → 013
slope: 1,177 → 3,726 → 7,940 trades; −0.53 % → −43.52 % → −113.36 %
return), adding 5 new disqualifying patterns (M–Q: high-frequency
firehose, broad simultaneous multi-pair, turnover-amplifying filter
on rejected core, pair-only survivor selection, cost-insensitive
signal design); adds 6 further CAMPAIGN_013-specific patterns (R–W:
cross-pair rank threshold sweep, ranking-metric lookback sweep,
pair-filtered rotator rescue, session/regime rescue stack, high-
turnover variant of any rejected family, per-fold artifact-driven
family selection); re-scores the now-8 rejected baseline (5 prior +
CAMPAIGN_011 null + CAMPAIGN_012 real + CAMPAIGN_013 real) against
the deferred candidates (C2 / C4 / C7 / C8 / C9) + 4 infrastructure
paths on 18 axes (added: distinctness from CAMPAIGN_013; turnover
profile vs null; explicit cost-awareness per Pattern Q); proposes 4
genuinely-new candidate families plus 1 sizing modifier (C7 CEWA
reaffirmed; C10 WBH4E; C11 LHRVPS sizing; C12 MFSR) and 1
disqualified (C13 QESCF Pattern U + K + G); selects **C7 — Calendar-
Event Window Anomaly (CEWA)** for future **CAMPAIGN_014 /
`calendar_event_window_anomaly 0.1.0-c014`** as the next preferred
real candidate. **Selection is not approval.** The selected
candidate is designed but not yet implemented; the discovery output
is two binding future-branch specs (scaffold + evidence) plus a
small new committed event-calendar fixture (Phase 1b of the scaffold
sprint). No strategy code, no backtest, no broker call, no approval.
The 875-test baseline is preserved.

| document | what it is |
|---|---|
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md) | Phase 0 audit + 11-phase sprint plan; verifies safety state at the close of CAMPAIGN_013's REJECT; baseline 875 pytests pass |
| [`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md) | Phase 1 — formal closeout for `cross_pair_currency_strength_rotation 0.1.0-c013`; codifies which cross-pair-rotation parameters / variant shapes are off-limits (14+ entries: lookback / threshold / ATR / stop / pair-filter / currency-filter / session/regime filter / ranking-metric swap / inversion / `max_open_positions` relax / universe change); 9 disqualified variant examples; binding cooldown rule against the cross-pair-rotation family ≥ 3 discovery sprints unless a future human explicitly authorizes a "materially different" cross-sectional FX thesis |
| [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) | Phase 2 — first-class binding turnover-amplification guardrail; empirical slope (CAMPAIGN_011 / 012 / 013 trade count × aggregate return); causality analysis (shared universe + cost model; entry direction independently falsified; independent pre-commits; monotonic across multiple axes); binding turnover-budget requirement for future candidates (pre-declared expected count + derivation + comparison to CAMPAIGN_011 / 012 / 013 + rejection rule + no max-positions relaxation); 5 new disqualifying patterns (M high-frequency H4 firehose; N broad simultaneous multi-pair; O turnover-amplifying filter on rejected core; P pair-only survivor selection; Q cost-insensitive signal design); discovery-005-specific application to Phases 4 / 5 / 6 / 7 |
| [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) | Phase 3 — additive addendum to the base guardrails doc + discovery-004 addendum; updates do-not-revive list to 8 rejected families + 1 null model (adds CAMPAIGN_013); adds Patterns R (same cross-pair rank gate, different threshold), S (same cross-pair ranking metric, different lookback), T (same cross-pair rotator, pair-filtered after rejection), U (same cross-pair rotator with session/regime rescue filter), V (high-turnover variant of any rejected family), W (per-fold artifact-driven family selection from CAMPAIGN_013); "genuinely new" criteria (11 axes; expanded from discovery-004's 7) any candidate must satisfy after the now-8 rejected baseline (including explicit turnover budget + explicit cost section + Pattern M ceiling + Pattern N portfolio-edge proof) |
| [`NEXT_DIRECTION_REASSESSMENT_005.md`](NEXT_DIRECTION_REASSESSMENT_005.md) | Phase 4 — 18-axis scoring (15 inherited from discovery-004 + 3 new: distinctness from CAMPAIGN_013 + turnover profile vs null + explicit cost-awareness per Pattern Q) of 10 paths (C2 / C4 / C6 cooled-down / C7 / C8 / C9 / C10+ + infra-A/B/C/D); recommends a new candidate sprint with C7 as lead + C10+ shortlist exploration in Phase 5; fallback to infra-A if Phase 5 fails |
| [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md) | Phase 5 — shortlist of 4 active families (C7 calendar-event window anomaly reaffirmed; C10 weekly-bias H4-execution; C11 long-horizon realized-vol-parity sizing — modifier not standalone; C12 monthly fundamentals-spread rebalance) + 1 disqualified (C13 QESCF Pattern U + K + G) + 1 infra fallback (infra-A); 15 disqualified family variants documented (cross-pair-rotation retunes, regime-switcher retunes, trend / breakout / MR / session / pullback retunes, weighted-pair-vote ensemble, high-frequency M30 firehose, all-pair simultaneous entry, C13) |
| [`NEXT_PREFERRED_DIRECTION_005.md`](NEXT_PREFERRED_DIRECTION_005.md) | Phase 6 — C7 selected as `calendar_event_window_anomaly 0.1.0-c014` (CAMPAIGN_014); future branches `research-calendar-event-window-anomaly-001` (scaffold) + `research-calendar-event-window-anomaly-walk-forward-001` (evidence); distinctness vs every rejected family 8/8; Patterns H–W explicitly cleared; C10 / C12 / C11 / C13 and all 4 infra paths deferred (not abandoned); CAMPAIGN_008/009 mean-reversion adjacency addressed (C7's trigger is event-time-conditional vs statistic-conditional; ~25–60 × lower turnover) |
| [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md) | Phase 7 binding design — R1–R8 signal rules (warmup, event-proximity trigger, counter-direction signal, overlap precedence FOMC > NFP > ECB > BoJ > BoE, ATR-2 stop, 6-bar time stop, 3-bar re-entry block, fail-closed); 10 frozen parameters (`event_set`, `impact_ordering`, `post_event_window_bars=6`, `atr_lookback=14`, `atr_stop_multiple=2.0`, `max_post_event_bars=6`, `re_entry_block_bars=3`, `risk_per_trade_pct=0.005`, `initial_equity_per_pair=500`, `event_warmup_bars=1`); 5 new no-lookahead invariants for calendar access; `CalendarEventWindowAnomalyStrategyConfig` schema; ≥ 30 unit tests planned; walk-forward inherits CAMPAIGN_010/011/012/013 §10 + adds null-baseline comparison gate + turnover-budget REJECT trigger (> 800 trades) + signal-density REJECT trigger (> 1,500 signals) + event-fixture coverage BLOCKED contract; cost section binding pre-commit (~1.5–4 bp per trade total, gross ≥ 7 bp hypothesized); event-class clustering + per-event-class per-pair sensitivity + pre/post direction + entry-window concentration as CAMPAIGN_014-specific risk diagnostics |
| [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md) | Phase 8a — future scaffold-branch prompt (`research-calendar-event-window-anomaly-001`); 9 phases (mirrors CAMPAIGN_013 scaffold + adds Phase 1b event-fixture compilation from public BLS / FOMC / ECB / BoJ / BoE URLs; deterministic; broker-free; ~10–50 KB committed JSON); strategy module + event-calendar loader + config + ≥ 30 unit tests + research config + CAMPAIGN_014 docs + smoke; baseline 875 → ≥ 905 pytests; no backtest run |
| [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) | Phase 8b — future evidence-branch prompt (`research-calendar-event-window-anomaly-walk-forward-001`); 10 phases mirroring CAMPAIGN_013 evidence sprint; full walk-forward + financing + risk + verifier; verdict options REJECT / REJECT_INDISTINGUISHABLE_FROM_NULL / RESEARCH_PASS_UNAPPROVED / BLOCKED; binding turnover-budget + signal-density + event-fixture coverage gates; cross-campaign comparison binding (002/010/011/012/013/014) |
| [`NEW_CANDIDATE_DISCOVERY_005_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_005_HELPER_DECISION.md) | Phase 9 — ten helper-code options considered, all rejected with documented rationale; zero code added; matches all four prior discovery sprints' identical no-helper decision |
| [`NEW_CANDIDATE_STRATEGY_DISCOVERY_005_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_005_SUMMARY.md) | Phase 10 — sprint summary & handoff; final validation; recommended next branch is the scaffold sprint `research-calendar-event-window-anomaly-001` |

### CAMPAIGN_014 candidate scaffold (`research-calendar-event-window-anomaly-001`)

Scaffold sprint for **CAMPAIGN_014** /
`calendar_event_window_anomaly 0.1.0-c014` — the C7 Calendar-Event
Window Anomaly candidate selected by the
`research-new-candidate-strategy-discovery-005` sprint. Adds the
strategy module (R1-R8 per binding spec); a new event-calendar
fixture loader (`src/forex_bot/calendar_events.py`) with binding
deny-list at load time (rejects any `actual` / `forecast` /
`consensus` / `surprise` / `revision` / `revised_value` /
`market_reaction` / `post_event_move` / `commentary` field); the
`StrategyConfig.calendar_event_window_anomaly` schema slot; 93 unit +
structural-audit tests; the candidate config YAML; the **first
committed event-calendar fixture in the repo**
(`research/calendar/fixtures/campaign_014_events.json`; 281
scheduled events; NFP 77 / FOMC 51 / ECB 51 / BoJ 51 / BoE 51;
coverage 2020-01-01 → 2026-05-20; compiled offline from public
official URLs — BLS / FOMC.gov / ECB.europa.eu / BoJ.or.jp /
BoE.co.uk — with no network fetch, no `.env` read, no credentials,
no broker SDK); the CAMPAIGN_014 pre-commit / status / readiness /
smoke / future-evidence-readiness docs; and a deterministic
fixture-compilation script. **CANDIDATE SCAFFOLD ONLY — NOT
APPROVED.** `configs/approved_strategies.yaml` remains
`approved: []`; CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
CAMPAIGN_012 / CAMPAIGN_013 all remain REJECT; the candidate is
structurally ready for the future evidence sprint to generate
`WalkForwardResults` after a **date-verification audit** against
the 5 source URLs. The 968-test baseline (875 prior + 93 new) is
preserved. The future evidence sprint must beat the CAMPAIGN_011
null-baseline floor (≥ +0.0524 R aggregate expectancy, ≥ +0.19 PF,
≥ +5 pp pairs-positive, ≥ +1 pair, 100 % fold pass rate) to count
as evidence of an edge; "indistinguishable from null" (within
± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair) is REJECTED. **Critical
CAMPAIGN_014-specific evidence-sprint requirements:** (a) binding
turnover-budget gate (REJECT > 800 trades over 4y per the
turnover-amplification anti-pattern); (b) binding signal-density
gate (REJECT > 1,500 signals over 8 folds); (c) binding event-
fixture coverage contract (BLOCKED if any fold's test-window-end
exceeds `fixture.coverage_end_utc`).

| document | what it is |
|---|---|
| [`CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md) | Phase 0 sprint plan + repo truth audit (verified 875 baseline + base commit `ed20604` + clean slate for CAMPAIGN_014; confirmed no existing event-calendar infrastructure) |
| [`CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`](CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md) | Phase 1 binding spec — R1-R8 rule table (event-fixture availability, post-event proximity trigger, FOMC > NFP > ECB > BoJ > BoE overlap precedence, counter-direction signal, H4 ATR-14 fail-closed, ATR×2 stop, time stop, deterministic Signal); 14 frozen parameters (`event_set=[NFP,FOMC,ECB,BoJ,BoE]`, `impact_ordering=[FOMC,NFP,ECB,BoJ,BoE]`, `post_event_window_bars=6`, `atr_lookback=14`, `atr_stop_multiple=2.0`, `max_post_event_bars=6`, `re_entry_block_bars=3`, `event_warmup_bars=1`, `trailing_stop_atr_multiple=null`, `min_atr_pips={}`); 7-pair universe + per-event-class impacted-pairs mapping (NFP/FOMC = all 7; ECB = EUR_USD; BoJ = USD_JPY; BoE = GBP_USD); 8 no-lookahead invariants; 14 fail-closed conditions; event-fixture JSON schema (`schema_version=campaign_014.event_fixture.v1`); per-event allowed-fields allow-list (`event_id`, `event_class`, `event_time_utc`) + binding deny-list of 10 post-event-result substrings |
| [`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md) | Phase 1B fixture provenance — fixture path; per-class event counts (NFP 77 · FOMC 51 · ECB 51 · BoJ 51 · BoE 51 = 281 total); first/last event timestamp; coverage range matches walk-forward universe verbatim; 5 source URLs (BLS / FOMC.gov / ECB.europa.eu / BoJ.or.jp / BoE.co.uk); **no credentials used; no broker / account endpoint touched; no `.env` read; no network fetch at compile time**; per-event allowed/excluded fields; schema version v1; limitations (scaffold-grade date accuracy; future evidence sprint must run date-verification audit before walk-forward Phase 2 launches); reviewability via deterministic compilation script |
| [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md) | candidate pre-commit; hypothesis verbatim; implementation files + fixture files + config files + 14 frozen parameters + 8 no-lookahead invariants; turnover budget (~320-520 expected trades over 4y; REJECT if > 800; signal-density REJECT if > 1,500; fixture-coverage BLOCKED if fold-end > fixture-end); cost section (~1.5-4 bp/trade total; gross ≥ 7 bp hypothesized; net ≥ 5 bp expected); binding null-baseline comparison gate vs CAMPAIGN_011; required walk-forward / financing / risk artifacts; **unexpected-PASS 5-step escalation protocol**; verbatim gate vector inherited from CAMPAIGN_010 / 011 / 012 / 013 + 3 new gates (turnover budget + signal density + event-fixture coverage) |
| [`CAMPAIGN_014_STATUS.md`](CAMPAIGN_014_STATUS.md) | candidate-scaffold-only status; no backtest verdict yet; no evidence campaign run; no strategy approval (cannot be approved by any research sprint); CAMPAIGN_002 / 010 / 011 / 012 / 013 all REJECT relationship; why this is a real candidate (new gating modality: scheduled-event-timestamp matching; distinctness 8/8 vs every rejected family; structurally low-turnover by event-set finiteness) but not approved |
| [`CALENDAR_EVENT_WINDOW_ANOMALY_READINESS.md`](CALENDAR_EVENT_WINDOW_ANOMALY_READINESS.md) | scaffold readiness GREEN across 17 dimensions; future evidence branch identity `research-calendar-event-window-anomaly-walk-forward-001`; event-fixture readiness (deterministic; broker-free; scaffold-grade dates pending audit); data expectations; known limitations (date-verification audit; first-published-only timestamps; approximate announcement times; implicit re-entry block; no surprise data; verifier capability lock; MODELED refused); turnover budget + REJECT triggers; null-baseline comparison binding; why real-candidate-not-approved |
| [`CAMPAIGN_014_SMOKE_RESULT.md`](CAMPAIGN_014_SMOKE_RESULT.md) | Phase 6 NON-EVIDENCE smokes: config-load PASS; fixture-load PASS (281 events); import smoke PASS (warmup=32); unit-test suite 93/93 PASS; full repo regression 968/968 PASS; validate_research_archive ALL PASS; check_research_freeze ALL PASS; scan_artifacts_for_secrets PASSED; paper-loop/demo-loop REFUSED; live-loop does not exist; ruff 3 pre-existing in lean_parity. Explicit "this is not evidence" framing; explicit "what was NOT run" enumeration |
| [`CAMPAIGN_014_WALK_FORWARD_READINESS.md`](CAMPAIGN_014_WALK_FORWARD_READINESS.md) | future-evidence walk-forward plan (inherited verbatim from CAMPAIGN_010 / 011 / 012 / 013: rolling, frozen, 540/180/180/180 days, 2020-01-01 → 2026-05-20, expected 8 folds); per-fold + aggregate gate vector; **binding event-fixture coverage contract**; **binding date-verification audit prerequisite**; **binding turnover-budget gate (REJECT > 800)**; **binding signal-density gate (REJECT > 1,500)**; **binding null-baseline comparison** (CAMPAIGN_011 margins); expected artifact paths |
| [`CAMPAIGN_014_FINANCING_RISK_READINESS.md`](CAMPAIGN_014_FINANCING_RISK_READINESS.md) | future-evidence financing overlay (ESTIMATED + conservative stress; MODELED refused at 4 layers; not lifted; expected aggregate drag ~$5-15 USD given short hold + low turnover) + portfolio-risk diagnostics (standard battery PLUS CAMPAIGN_014-specific: event-class clustering, per-event-class per-pair sensitivity heatmap, pre/post direction balance, entry-window concentration, event-fixture coverage per fold, concurrent-rejection diagnostic for NFP/FOMC); simultaneous-pair NFP/FOMC entries explicitly justified by hypothesis (event-driven mechanism per pair = portfolio-level edge proof against Pattern N); per-instrument concurrency = 1 |
| [`CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md) | future-evidence verifier coverage; current capability lock to CAMPAIGN_002 / `trend_following`; not required for REJECT; required only on RESEARCH_PASS_UNAPPROVED via the suggested follow-up sprint `infra-free-local-parity-verifier-calendar-event-window-anomaly-001`; six-evidence-ladder item 5 deferred for REJECT; item 6 (deliberate human approval) permanent and never automatic |
| [`CALENDAR_EVENT_WINDOW_ANOMALY_001_SUMMARY.md`](CALENDAR_EVENT_WINDOW_ANOMALY_001_SUMMARY.md) | sprint summary & handoff; final validation; recommended next branch is the evidence sprint `research-calendar-event-window-anomaly-walk-forward-001` |

### CAMPAIGN_014 evidence sprint (`research-calendar-event-window-anomaly-walk-forward-001`)

Evidence-grade walk-forward sprint for **CAMPAIGN_014** /
`calendar_event_window_anomaly 0.1.0-c014`. Adds the binding
fixture date-verification audit (Phase 0 — NFP 100 % verified
procedurally + FOMC 100 % verified against official Fed.gov
calendar + BoJ 91 % for 2025-2026 + ECB/BoE structurally
consistent but not WebFetch-verifiable + 1 BoJ post-coverage
drift logged; classification PARTIAL — PROCEED WITH EXPLICIT
CAVEAT); the per-fold runner `scripts/run_campaign_014.py` (with
binding `_assert_frozen()` check + event-fixture coverage gate);
the 56 per-pair per-fold trade summaries + trades CSVs (~448 KB
total compact text); the 8-fold walk-forward verdict; the
financing-overlay script + ESTIMATED + conservative-stress
report (cashflow_home_stress_total = −$10.64, lowest of any
real candidate); the risk-diagnostics script with CAMPAIGN_014-
specific event-class clustering + per-event-class per-pair
heatmap + concurrent-firing diagnostic; the independent verifier
status (NOT REQUIRED for REJECT, matching CAMPAIGN_010 / 011 /
012 / 013 precedent); the campaign status / evidence summary /
sprint summary; updates to `EVIDENCE_MANIFEST.json` (13 → 14
campaigns) + `STRATEGY_STATUS.md` (scaffold-only → REJECT). The
verdict is **REJECT (direction-of-trade falsification)** — 6/8
inherited aggregate gates fail; materially WORSE than CAMPAIGN_011
null baseline on all 4 PnL-direction axes (OUTSIDE the
indistinguishability band on the WORSE side). Turnover budget
PASS (720 trades ≤ 800; 1,240 raw signals ≤ 1,500); fixture-
coverage gate PASS on all 8 folds. Phase 7 surfaced two findings
of independent research value: (1) FOMC = 0 trades (all 51 FOMC
events SESSION_BLOCKED because the 19:00-UTC FOMC time → 22:00-UTC
trigger bar overlaps the rollover window; the C7 hypothesis's
claim about FOMC is structurally untestable on this universe +
session filter); (2) NFP dominates and loses — 571/720 trades (79 %)
NFP-triggered generating −$151.17 (98 % of total losses); near-50/50
long/short balance → losses on BOTH sides → post-event H4 bar
CONTINUES the NFP event-bar's direction, does not REVERT. The
independent verifier was not run (capability-locked to CAMPAIGN_002;
not required for REJECT; matches CAMPAIGN_010 / 011 / 012 / 013
precedent verbatim — 5 successive REJECT-with-no-verifier-extension
outcomes). `configs/approved_strategies.yaml` remains `approved: []`;
CAMPAIGN_002 / 010 / 011 / 012 / 013 / 014 all REJECT; paper /
demo / live remain blocked; no broker call this sprint; no `.env`
read; no credential printed; no MODELED financing; no parameter
tuning post-result; no pair carve-out (ECB / BoE positive cells
flagged but NOT used per Pattern P binding); no fixture
modification mid-sprint (BoJ 2026-03 drift logged for future
fixture-revision sprint). Pytest 968/968 PASS; ruff 3 pre-existing
in `lean_parity` unchanged.

| document | what it is |
|---|---|
| [`CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md) | Phase 0 sprint plan — repo truth audit, 10-phase pipeline, expected commands per phase, non-goals, safety invariants, verdict options |
| [`CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md`](CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md) | Phase 0 binding fixture date-verification audit (PARTIAL — PROCEED WITH EXPLICIT CAVEAT; NFP + FOMC 100 % verified; BoJ partially via WebFetch; ECB / BoE not WebFetch-reachable; 1 post-coverage BoJ drift logged) |
| [`CAMPAIGN_014_DATA_PROVENANCE.md`](CAMPAIGN_014_DATA_PROVENANCE.md) | Phase 1 candle + event-fixture provenance (candle store byte-identical to CAMPAIGN_010 / 011 / 012 / 013 stores; fixture sha256 + coverage; no fetch; no broker call) |
| [`CAMPAIGN_014_WALK_FORWARD_PLAN.md`](CAMPAIGN_014_WALK_FORWARD_PLAN.md) | Phase 2 authoritative 8-fold rolling/frozen walk-forward plan (inherits CAMPAIGN_010 / 011 / 012 / 013 verbatim; per-fold event coverage table 171 events total: NFP 47 + FOMC 31 + ECB 31 + BoJ 31 + BoE 31) |
| [`CAMPAIGN_014_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_014_WALK_FORWARD_EXECUTION.md) | Phase 4 execution log — 56 backtests completed in 50.9 s; per-pair per-fold metrics; aggregate metrics; per-fold gate table; cost-section reconciliation (Pattern Q falsified on gross-expectancy side, not costs) |
| [`CAMPAIGN_014_WALK_FORWARD_RESULT.md`](CAMPAIGN_014_WALK_FORWARD_RESULT.md) | Phase 5 walk-forward verdict — REJECT (direction-of-trade falsification); inherited gate table; turnover/cost gate table; CAMPAIGN_011 null-baseline comparison (OUTSIDE band on all 4 dimensions, WORSE side); calendar-event-window interpretation; explicit no-approval |
| [`CAMPAIGN_014_FINANCING_OVERLAY.md`](CAMPAIGN_014_FINANCING_OVERLAY.md) | Phase 6 financing overlay (ESTIMATED + conservative stress; −$10.64 total, lowest of any real candidate; MODELED refused at 4 layers; zero pair-flips since every pair already negative; verdict unchanged) |
| [`CAMPAIGN_014_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_014_PORTFOLIO_RISK_DIAGNOSTICS.md) | Phase 7 standard + CAMPAIGN_014-specific diagnostics (per-event-class PnL: NFP 571 / FOMC 0 / ECB 41 / BoJ 47 / BoE 61; per-event-class per-pair heatmap; entry-window concentration 100 % at offset 1; NFP concurrent-firing histogram median 6/7 pairs; per-fold fixture coverage PASS on all 8; 409 SESSION_BLOCKED + 196 SPREAD_TOO_WIDE rejections; FOMC = 0 trades + NFP-dominated losses surfaced) |
| [`CAMPAIGN_014_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_014_INDEPENDENT_VERIFIER_STATUS.md) | Phase 8 verifier status — NOT REQUIRED for REJECT (matches CAMPAIGN_010 / 011 / 012 / 013 precedent; 5 successive REJECT-with-no-verifier-extension outcomes); capability lock unchanged |
| [`CAMPAIGN_014_EVIDENCE_SUMMARY.md`](CAMPAIGN_014_EVIDENCE_SUMMARY.md) | one-page evidence summary; headline numbers; null-baseline interpretation; per-pair vs CAMPAIGN_011; per-event-class breakdown; comparison across 5 real candidates + null; financing impact; risk diagnostics; verifier status; six-evidence-ladder status |
| [`CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_SUMMARY.md`](CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_SUMMARY.md) | sprint summary & handoff; final validation; recommended next branch is the next discovery sprint (NOT a C7 retry; revival forbidden by Pattern O / P / Q) |

## Research-freeze documents (this branch)

| document | what it is |
|---|---|
| [`docs/research/FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md) | the freeze decision — **NO APPROVED TRADING STRATEGY** |
| [`docs/research/STRATEGY_STATUS.md`](STRATEGY_STATUS.md) | per-strategy status registry (all paper/demo/live = NO) |
| [`docs/research/FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md) | unauthorized menu of possible future directions |
| [`docs/research/EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) | this index |
| [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml) | machine-enforced approved-strategy registry (empty) |

## M1 canonical data and LTF execution lane 001

Infrastructure-only sprint on branch
`infra-m1-canonical-data-and-ltf-execution-lane-001`. It builds the
canonical M1 data-store design, local M1 aggregation into
M5/M15/H1/H4/D1AGG, a practice-only read-only M1 ingestion scaffold, an
M1 data-quality validator, LTF-to-HTF alignment helpers, and an LTF
backtest preflight scaffold. It creates **no CAMPAIGN_021 evidence**,
does not rerun C020, does not approve any strategy, and does not enable
paper/demo/live. C020 remains REJECT.

| document | what it is |
|---|---|
| [`M1_CANONICAL_DATA_AND_LTF_EXECUTION_LANE_001_PLAN.md`](M1_CANONICAL_DATA_AND_LTF_EXECUTION_LANE_001_PLAN.md) | Phase 0 plan and baseline audit |
| [`M1_CANONICAL_DATA_STORE_DESIGN.md`](M1_CANONICAL_DATA_STORE_DESIGN.md) | Phase 1 Postgres M1 store design |
| [`M1_TO_MULTI_TIMEFRAME_AGGREGATION_RESULT.md`](M1_TO_MULTI_TIMEFRAME_AGGREGATION_RESULT.md) | Phase 2 aggregation result |
| [`M1_READONLY_INGESTION_CLIENT_RESULT.md`](M1_READONLY_INGESTION_CLIENT_RESULT.md) | Phase 3 read-only ingestion scaffold |
| [`M1_DATA_QUALITY_VALIDATOR_RESULT.md`](M1_DATA_QUALITY_VALIDATOR_RESULT.md) | Phase 4 validator result |
| [`LTF_TO_HTF_ALIGNMENT_LANE_RESULT.md`](LTF_TO_HTF_ALIGNMENT_LANE_RESULT.md) | Phase 5 alignment helper result |
| [`LTF_BACKTEST_LANE_SCAFFOLD_RESULT.md`](LTF_BACKTEST_LANE_SCAFFOLD_RESULT.md) | Phase 6 preflight scaffold result |
| [`M1_INGESTION_AGGREGATION_SMOKE_RESULT.md`](M1_INGESTION_AGGREGATION_SMOKE_RESULT.md) | Phase 7 blocked smoke result |
| [`LOWER_TIMEFRAME_STRATEGY_TRANSLATION_ROADMAP.md`](LOWER_TIMEFRAME_STRATEGY_TRANSLATION_ROADMAP.md) | Phase 8 future roadmap |
| [`NEXT_SPRINT_PROMPT_CAMPAIGN_021_LTF_MTF_CONFLUENCE_SCAFFOLD.md`](NEXT_SPRINT_PROMPT_CAMPAIGN_021_LTF_MTF_CONFLUENCE_SCAFFOLD.md) | Phase 8 scaffold-only next prompt |

## M1 full corpus validation and aggregation 001

Branch `infra-m1-full-corpus-validation-and-aggregation-001`. Validates
~12.8M ingested M1 rows (2021-05-27→2026-05-26) for seven majors;
compact JSON/CSV under `research/m1_full_corpus_validation/`. **No
CAMPAIGN_021 evidence.** Readiness: `READY_WITH_WARNINGS` (hybrid D1AGG
from native H4 until M1→D1AGG day completeness improves).

| document | what it is |
|---|---|
| [`M1_FULL_CORPUS_VALIDATION_AND_AGGREGATION_001_PLAN.md`](M1_FULL_CORPUS_VALIDATION_AND_AGGREGATION_001_PLAN.md) | Phase 0 plan |
| [`M1_FULL_CORPUS_INVENTORY_RESULT.md`](M1_FULL_CORPUS_INVENTORY_RESULT.md) | Phase 1 inventory |
| [`M1_FULL_CORPUS_DATA_QUALITY_RESULT.md`](M1_FULL_CORPUS_DATA_QUALITY_RESULT.md) | Phase 2 quality |
| [`M1_FULL_CORPUS_AGGREGATION_COVERAGE_RESULT.md`](M1_FULL_CORPUS_AGGREGATION_COVERAGE_RESULT.md) | Phase 3 aggregation |
| [`M1_DERIVED_H4_DRIFT_COMPARISON_RESULT.md`](M1_DERIVED_H4_DRIFT_COMPARISON_RESULT.md) | Phase 4 H4 drift |
| [`M1_DERIVED_D1AGG_CONVENTION_RESULT.md`](M1_DERIVED_D1AGG_CONVENTION_RESULT.md) | Phase 5 D1AGG |
| [`M1_FULL_CORPUS_LTF_HTF_ALIGNMENT_RESULT.md`](M1_FULL_CORPUS_LTF_HTF_ALIGNMENT_RESULT.md) | Phase 6 alignment |
| [`M1_FULL_CORPUS_LTF_BACKTEST_PREFLIGHT_RESULT.md`](M1_FULL_CORPUS_LTF_BACKTEST_PREFLIGHT_RESULT.md) | Phase 7 preflight |
| [`M1_FULL_CORPUS_LTF_LANE_READINESS_DECISION.md`](M1_FULL_CORPUS_LTF_LANE_READINESS_DECISION.md) | Phase 8 readiness |
| [`M1_FULL_CORPUS_VALIDATION_AND_AGGREGATION_001_SUMMARY.md`](M1_FULL_CORPUS_VALIDATION_AND_AGGREGATION_001_SUMMARY.md) | Phase 9 close-out |

## M1 derived timeframe materialization 001

Branch `infra-m1-derived-timeframe-materialization-001`. Persists M1-derived
M5/M15/H1/H4M1 under `source=m1_materialized` in Postgres. **No campaign
evidence.** Unblocks faster CAMPAIGN_021 loader paths.

| document | what it is |
|---|---|
| [`M1_DERIVED_TIMEFRAME_MATERIALIZATION_001_PLAN.md`](M1_DERIVED_TIMEFRAME_MATERIALIZATION_001_PLAN.md) | Phase 0 plan |
| [`M1_DERIVED_TIMEFRAME_MATERIALIZATION_RESULT.md`](M1_DERIVED_TIMEFRAME_MATERIALIZATION_RESULT.md) | Verification + row counts |
| [`M1_DERIVED_TIMEFRAME_MATERIALIZATION_001_SUMMARY.md`](M1_DERIVED_TIMEFRAME_MATERIALIZATION_001_SUMMARY.md) | Sprint close-out |

Compact JSON: `research/m1_timeframe_materialization/`.

## CAMPAIGN_021 LTF MTF confluence (execution — post-materialization)

> **CAMPAIGN_021 REJECT** — train expectancy **−0.0174 R** (1,438 trades).
> Re-run on materialized bars; metrics bit-identical; runtime ~40 min.
> Validation/test not run after train gate fail. C020 remains REJECT.

| document | what it is |
|---|---|
| [`CAMPAIGN_021_EXECUTION_AFTER_M1_MATERIALIZATION_PLAN.md`](CAMPAIGN_021_EXECUTION_AFTER_M1_MATERIALIZATION_PLAN.md) | Post-materialization execution plan |
| [`CAMPAIGN_021_TRAIN_RESULT.md`](CAMPAIGN_021_TRAIN_RESULT.md) | Train metrics |
| [`CAMPAIGN_021_GATE_DECISION.md`](CAMPAIGN_021_GATE_DECISION.md) | Gate decision |
| [`CAMPAIGN_021_TEST_LOCKBOX_NOT_OPENED.md`](CAMPAIGN_021_TEST_LOCKBOX_NOT_OPENED.md) | Lockbox closed |
| [`CAMPAIGN_021_BACKTRADER_PARITY_RESULT.md`](CAMPAIGN_021_BACKTRADER_PARITY_RESULT.md) | Parity NOT_RUN |
| [`CAMPAIGN_021_FINAL_INTERPRETATION.md`](CAMPAIGN_021_FINAL_INTERPRETATION.md) | Final interpretation |
| [`CAMPAIGN_021_LTF_MTF_CONFLUENCE_EXECUTION_001_SUMMARY.md`](CAMPAIGN_021_LTF_MTF_CONFLUENCE_EXECUTION_001_SUMMARY.md) | Execution sprint close-out |

## CAMPAIGN_021 LTF MTF confluence scaffold (research-campaign-021-ltf-mtf-confluence-scaffold-001)

> **Scaffold phase** — precommit and runner; superseded by execution verdict above.

| document | what it is |
|---|---|
| [`CAMPAIGN_021_LTF_MTF_CONFLUENCE_SCAFFOLD_001_PLAN.md`](CAMPAIGN_021_LTF_MTF_CONFLUENCE_SCAFFOLD_001_PLAN.md) | Phase 0 plan |
| [`CAMPAIGN_021_STRUCTURAL_DISTINCTNESS_MEMO.md`](CAMPAIGN_021_STRUCTURAL_DISTINCTNESS_MEMO.md) | Distinctness vs rejected families |
| [`CAMPAIGN_021_LTF_MTF_CONFLUENCE_PRECOMMIT.md`](CAMPAIGN_021_LTF_MTF_CONFLUENCE_PRECOMMIT.md) | Frozen parameters and gates |
| [`CAMPAIGN_021_PREFLIGHT_SCAFFOLD_RESULT.md`](CAMPAIGN_021_PREFLIGHT_SCAFFOLD_RESULT.md) | Preflight PASS (compact) |
| [`CAMPAIGN_021_BACKTRADER_PARITY_DESIGN.md`](CAMPAIGN_021_BACKTRADER_PARITY_DESIGN.md) | Parity design (not run) |
| [`NEXT_SPRINT_PROMPT_CAMPAIGN_021_LTF_MTF_CONFLUENCE_EXECUTION.md`](NEXT_SPRINT_PROMPT_CAMPAIGN_021_LTF_MTF_CONFLUENCE_EXECUTION.md) | Future execution prompt |
| [`CAMPAIGN_021_LTF_MTF_CONFLUENCE_SCAFFOLD_001_SUMMARY.md`](CAMPAIGN_021_LTF_MTF_CONFLUENCE_SCAFFOLD_001_SUMMARY.md) | Scaffold sprint close-out |

## Machine-readable manifest & validation

- [`docs/research/EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json) — a
  machine-readable index of all nine campaigns: report path, strategy
  family, data source, verdict, key metrics, commit hash, artifact
  folder, whether the test window was opened, whether the RiskEngine was
  used, the financing treatment, and `strategy_approved` (false for
  every campaign). Manifest version 2 adds a `diagnostic_artifacts`
  array — the diagnostic / parity outputs above, each carrying
  `strategy_evidence: false`.
- [`scripts/validate_research_archive.py`](../../scripts/validate_research_archive.py)
  audits the archive's integrity. Run it any time — before trusting a
  report, after editing docs, or in CI:

  ```bash
  .venv/bin/python scripts/validate_research_archive.py
  ```

  It checks that the approved-strategy registry is empty, that every
  report and artifact folder named in the manifest exists, that no
  campaign is marked approved, that every verdict is a non-approval
  verdict, that each report corroborates its manifest verdict, that
  every declared diagnostic artifact exists and is not marked strategy
  evidence, that every link in this index resolves, and that no
  committed artifact contains a credential-shaped string. The check
  logic lives in
  `forex_bot.research_archive` and is unit-tested by
  `tests/unit/test_validate_research_archive.py`.

## CAMPAIGN_022 H4/H1 pullback-resolution execution (research-campaign-022-h4-h1-pullback-resolution-execution-001)

First **executed** evidence for the pullback-resolution thesis (H4 bias + H1 holding-pullback
+ M15 reclaim; H4 top timeframe, no D1). Verdict: **REJECT** — train expectancy −0.1042R
(0/7 pairs positive), validation −0.1663R, 2× cost-stress −0.2468R; underperforms C020 all-green
and loses to the C011 null. Train-gate failure terminal; test lockbox never opened; `approved: []`.

| document | role |
|---|---|
| [`CAMPAIGN_022_H4_H1_PULLBACK_RESOLUTION_PRECOMMIT.md`](CAMPAIGN_022_H4_H1_PULLBACK_RESOLUTION_PRECOMMIT.md) | frozen precommit |
| [`CAMPAIGN_022_STRUCTURAL_DISTINCTNESS_MEMO.md`](CAMPAIGN_022_STRUCTURAL_DISTINCTNESS_MEMO.md) | distinctness vs C020/C021 |
| [`CAMPAIGN_022_EXECUTION_001_PLAN.md`](CAMPAIGN_022_EXECUTION_001_PLAN.md) | execution plan, splits, gates |
| [`CAMPAIGN_022_TRAIN_VALIDATION_RESULT.md`](CAMPAIGN_022_TRAIN_VALIDATION_RESULT.md) | train/validation metrics + gate table |
| [`CAMPAIGN_022_BEHAVIOR_DIAGNOSTICS.md`](CAMPAIGN_022_BEHAVIOR_DIAGNOSTICS.md) | mechanism diagnostics |
| [`CAMPAIGN_022_BACKTRADER_PARITY_RESULT.md`](CAMPAIGN_022_BACKTRADER_PARITY_RESULT.md) | parity NOT run (moot — train REJECT) |
| [`CAMPAIGN_022_GATE_DECISION.md`](CAMPAIGN_022_GATE_DECISION.md) | gate decision (REJECT) |
| [`CAMPAIGN_022_FINAL_INTERPRETATION.md`](CAMPAIGN_022_FINAL_INTERPRETATION.md) | final interpretation |
| [`CAMPAIGN_022_H4_H1_PULLBACK_RESOLUTION_SCAFFOLD_001_SUMMARY.md`](CAMPAIGN_022_H4_H1_PULLBACK_RESOLUTION_SCAFFOLD_001_SUMMARY.md) | scaffold sprint summary |
| [`CAMPAIGN_022_EXECUTION_001_SUMMARY.md`](CAMPAIGN_022_EXECUTION_001_SUMMARY.md) | execution sprint summary |

### C022 post-execution diagnostics & family closeout

Diagnostic-only follow-ups that localized C022's failure to the **entry signal**
(not stop geometry or cost) and **retired** the C022/C023 family. No verdict
changed; no CAMPAIGN_024 created; C023 not executed; `approved: []`.

| document | role |
|---|---|
| [`CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md`](CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md) | MFE/MAE: winners rarely near stop; many stop-outs never get going |
| [`DIAGNOSTIC_STOP_MODEL_COMPARISON_EXECUTED.md`](DIAGNOSTIC_STOP_MODEL_COMPARISON_EXECUTED.md) | all ATR/time stop variants + cost-free baseline stay negative |
| [`LIFECYCLE_FEATURE_CAPTURE_AND_MFE_MAE_EXECUTION_001_CONCLUSIONS.md`](LIFECYCLE_FEATURE_CAPTURE_AND_MFE_MAE_EXECUTION_001_CONCLUSIONS.md) | entry-timing problem, not stop placement |
| [`C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md`](C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md) | structural entry features all at AUC ≈ 0.50 |
| [`C022_WINNER_LOSER_FEATURE_SEPARATION_001_SUMMARY.md`](C022_WINNER_LOSER_FEATURE_SEPARATION_001_SUMMARY.md) | feature-separation sprint close-out |
| [`C024_READINESS_FROM_C022_FEATURE_SEPARATION.md`](C024_READINESS_FROM_C022_FEATURE_SEPARATION.md) | C024 readiness = NOT_READY |
| [`C022_C023_PULLBACK_RESOLUTION_FAMILY_CLOSEOUT.md`](C022_C023_PULLBACK_RESOLUTION_FAMILY_CLOSEOUT.md) | family closeout: RETIRED_UNLESS_NEW_EXTERNAL_THESIS |
| [`POST_C022_FAMILY_RETIREMENT_AND_NEW_THESIS_SELECTION_001_PLAN.md`](POST_C022_FAMILY_RETIREMENT_AND_NEW_THESIS_SELECTION_001_PLAN.md) | retirement + next-thesis-selection sprint plan |

Next-thesis comparison, selection decision, and scope amendment (USD_JPY-only):

| document | role |
|---|---|
| [`NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md`](NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md) | seven candidate lanes scored; Lane E reframed as USD_JPY scope |
| [`NEXT_THESIS_SELECTION_DECISION.md`](NEXT_THESIS_SELECTION_DECISION.md) | Lane D selected; §1a USD_JPY-only scope; §5 C024 bar |
| [`POST_C022_USDJPY_SCOPE_AMENDMENT_SUMMARY.md`](POST_C022_USDJPY_SCOPE_AMENDMENT_SUMMARY.md) | USD_JPY scope-amendment summary |

### USD_JPY M15 microstructure-confirmation diagnostic + entry-lane closeout

USD_JPY-only, read-only diagnostic over the 306 USD_JPY C022 base trades. No live M15
entry primitive separated winners from losers materially/stably or beat the inert
EMA20-reclaim baseline; the only above-floor separation was **post-entry** (retest-hold
/ trap), not a live entry filter. USD_JPY microstructure confirmation is **closed as an
entry-alpha lane**; C024 stays `NOT_READY`; C023 not executed; `approved: []`.

| document | role |
|---|---|
| [`USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_001_PLAN.md`](USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_001_PLAN.md) | diagnostic sprint plan (USD_JPY-only) |
| [`USDJPY_MICROSTRUCTURE_DATASET_INVENTORY.md`](USDJPY_MICROSTRUCTURE_DATASET_INVENTORY.md) | dataset inventory (306 trades; 299 MFE/MAE OK) |
| [`USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_RESULT.md`](USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_RESULT.md) | separation results vs the EMA-reclaim baseline |
| [`USDJPY_C024_READINESS_DECISION.md`](USDJPY_C024_READINESS_DECISION.md) | USD_JPY C024 readiness = NOT_READY |
| [`USDJPY_MICROSTRUCTURE_ENTRY_LANE_CLOSEOUT.md`](USDJPY_MICROSTRUCTURE_ENTRY_LANE_CLOSEOUT.md) | entry-lane closed; post-entry signals → trade-management only |
| [`USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_001_SUMMARY.md`](USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_001_SUMMARY.md) | diagnostic sprint summary |

### USD_JPY post-entry trade-management diagnostic + full-thread closeout

USD_JPY-only, read-only. Tested whether post-entry retest-hold/trap + early MFE/MAE
behavior could inform early-invalidation / hold decisions. Post-entry events separate
outcomes **descriptively**, but **all five predeclared early-exit counterfactuals
reduced expectancy on both splits** (−0.065 to −0.134R) — not actionable. The
post-entry trade-management lane is **CLOSED** (`NOT_READY`). With this, the full
C022/C023/USD_JPY microstructure thread is closed at both the entry and management
layers; no further mining recommended. No verdict changed; no C024; `approved: []`.

| document | role |
|---|---|
| [`USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_001_PLAN.md`](USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_001_PLAN.md) | trade-management sprint plan |
| [`USDJPY_MICROSTRUCTURE_DATASET_INVENTORY.md`](USDJPY_MICROSTRUCTURE_DATASET_INVENTORY.md) | (shared) USD_JPY trade-set inventory |
| [`USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_RESULT.md`](USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_RESULT.md) | descriptive separation + winner damage |
| [`USDJPY_POST_ENTRY_MANAGEMENT_COUNTERFACTUALS.md`](USDJPY_POST_ENTRY_MANAGEMENT_COUNTERFACTUALS.md) | early-exit counterfactuals (all reduce expectancy) |
| [`USDJPY_TRADE_MANAGEMENT_READINESS_DECISION.md`](USDJPY_TRADE_MANAGEMENT_READINESS_DECISION.md) | trade-management readiness = NOT_READY |
| [`USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_001_SUMMARY.md`](USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_001_SUMMARY.md) | trade-management sprint summary |
| [`C022_C023_USDJPY_MICROSTRUCTURE_THREAD_CLOSEOUT.md`](C022_C023_USDJPY_MICROSTRUCTURE_THREAD_CLOSEOUT.md) | **full-thread closeout + lessons** |

## Strategy-search pause: external-thesis → compression-expansion → macro-context (2026-05-28)

Three genuinely-new read-only lanes after the microstructure closeout — all null/not-ready.
No verdict changed; no C024; C023 not executed; `approved: []`; paper/demo/live blocked.
**Standing decision: `PAUSE_STRATEGY_RESEARCH`.**

| document | role |
|---|---|
| [`STRATEGY_SEARCH_PAUSE_AFTER_USDJPY_MACRO_CONTEXT.md`](STRATEGY_SEARCH_PAUSE_AFTER_USDJPY_MACRO_CONTEXT.md) | **final pause memo (read first)** |
| [`STRATEGY_SEARCH_PAUSE_AFTER_USDJPY_MACRO_CONTEXT_001_PLAN.md`](STRATEGY_SEARCH_PAUSE_AFTER_USDJPY_MACRO_CONTEXT_001_PLAN.md) | pause sprint plan |
| [`EXTERNAL_FX_THESIS_SOURCING_FRAMEWORK.md`](EXTERNAL_FX_THESIS_SOURCING_FRAMEWORK.md) | external-thesis sourcing framework |
| [`USDJPY_SESSION_VOLATILITY_SPREAD_ATLAS.md`](USDJPY_SESSION_VOLATILITY_SPREAD_ATLAS.md) | session/vol/spread atlas (direction null) |
| [`USDJPY_EXTERNAL_THESIS_CANDIDATE_SCORECARD.md`](USDJPY_EXTERNAL_THESIS_CANDIDATE_SCORECARD.md) | candidate-thesis scorecard |
| [`USDJPY_VOLATILITY_COMPRESSION_EXPANSION_DIAGNOSTIC_RESULT.md`](USDJPY_VOLATILITY_COMPRESSION_EXPANSION_DIAGNOSTIC_RESULT.md) | compression→expansion result (falsified) |
| [`USDJPY_COMPRESSION_EXPANSION_MONETIZATION_DIAGNOSTIC.md`](USDJPY_COMPRESSION_EXPANSION_MONETIZATION_DIAGNOSTIC.md) | monetization diagnostic + London lead |
| [`USDJPY_VOLATILITY_COMPRESSION_EXPANSION_READINESS_DECISION.md`](USDJPY_VOLATILITY_COMPRESSION_EXPANSION_READINESS_DECISION.md) | compression→expansion readiness |
| [`USDJPY_LONDON_COMPRESSION_CONTINUATION_CONFIRMATION_RESULT.md`](USDJPY_LONDON_COMPRESSION_CONTINUATION_CONFIRMATION_RESULT.md) | London confirmation (FAILED) |
| [`USDJPY_LONDON_COMPRESSION_CONTINUATION_ROBUSTNESS.md`](USDJPY_LONDON_COMPRESSION_CONTINUATION_ROBUSTNESS.md) | London robustness/falsification |
| [`USDJPY_LONDON_COMPRESSION_CONTINUATION_READINESS_DECISION.md`](USDJPY_LONDON_COMPRESSION_CONTINUATION_READINESS_DECISION.md) | London readiness = PAUSE |
| [`MACRO_REGIME_CONTEXT_TRADEABILITY_THESIS_FRAMING.md`](MACRO_REGIME_CONTEXT_TRADEABILITY_THESIS_FRAMING.md) | slow-context framing (not fast-news) |
| [`USDJPY_MACRO_REGIME_CONTEXT_RESULT.md`](USDJPY_MACRO_REGIME_CONTEXT_RESULT.md) | macro-context result (no conditioning) |
| [`USDJPY_MACRO_REGIME_CONTEXT_ROBUSTNESS.md`](USDJPY_MACRO_REGIME_CONTEXT_ROBUSTNESS.md) | macro-context robustness + latency-independence |
| [`USDJPY_MACRO_REGIME_CONTEXT_READINESS_DECISION.md`](USDJPY_MACRO_REGIME_CONTEXT_READINESS_DECISION.md) | macro-context readiness = PAUSE |

| [`FOREX_BOT_RESEARCH_LESSONS_LEARNED_001.md`](FOREX_BOT_RESEARCH_LESSONS_LEARNED_001.md) | lessons learned + failure taxonomy |
| [`STRATEGY_RESEARCH_RESTART_CRITERIA.md`](STRATEGY_RESEARCH_RESTART_CRITERIA.md) | strict restart criteria (sufficient vs insufficient) |
| [`NEXT_ACTION_OPTIONS_AFTER_STRATEGY_SEARCH_PAUSE.md`](NEXT_ACTION_OPTIONS_AFTER_STRATEGY_SEARCH_PAUSE.md) | next-action options + recommendation |
| [`NEXT_SPRINT_PROMPT_AFTER_STRATEGY_SEARCH_PAUSE.md`](NEXT_SPRINT_PROMPT_AFTER_STRATEGY_SEARCH_PAUSE.md) | non-strategy next-sprint prompt (3 tracks) |
| [`STRATEGY_SEARCH_PAUSE_AFTER_USDJPY_MACRO_CONTEXT_001_SUMMARY.md`](STRATEGY_SEARCH_PAUSE_AFTER_USDJPY_MACRO_CONTEXT_001_SUMMARY.md) | pause-sprint summary |

## Edge-discovery null-benchmark lab (EDGE_DISCOVERY_NULL_BENCHMARK_LAB_001)

Infrastructure/diagnostic sprint — **extended** the existing import-isolated
`research/edge_discovery/` lab (it was NOT rebuilt). Added matched-null,
filter-ablation, multiple-comparison, and cost-feasibility-flag modules + CLI
diagnostics, the pre-campaign process docs, and an artifact-first C025/C026
retrospective. Approves nothing; opens no test lockbox; C011 stays the null
benchmark; C025/C026 stay REJECT.

| document | purpose |
|---|---|
| [`EDGE_DISCOVERY_NULL_BENCHMARK_LAB_001_PLAN.md`](EDGE_DISCOVERY_NULL_BENCHMARK_LAB_001_PLAN.md) | sprint plan (extend-not-rebuild pivot) |
| [`EDGE_DISCOVERY_EXISTING_LAB_AUDIT_001.md`](EDGE_DISCOVERY_EXISTING_LAB_AUDIT_001.md) | capability→gap map of the existing lab |
| [`EDGE_DISCOVERY_PROTOCOL.md`](EDGE_DISCOVERY_PROTOCOL.md) | screen-before-campaign protocol |
| [`FUTURE_CAMPAIGN_REENTRY_GATES.md`](FUTURE_CAMPAIGN_REENTRY_GATES.md) | strict G1–G9 pre-campaign gates |
| [`FUTURE_STRATEGY_SEARCH_WORKFLOW.md`](FUTURE_STRATEGY_SEARCH_WORKFLOW.md) | 11-step search workflow |
| [`PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md`](PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md) | copy-per-idea checklist |
| [`FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md`](FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md) | ledgers future campaigns must emit |
| [`EDGE_DISCOVERY_RETROSPECTIVE_C025_C026.md`](EDGE_DISCOVERY_RETROSPECTIVE_C025_C026.md) | C025/C026 retrospective (no verdict change) |
| [`EDGE_DISCOVERY_NULL_BENCHMARK_LAB_001_SUMMARY.md`](EDGE_DISCOVERY_NULL_BENCHMARK_LAB_001_SUMMARY.md) | sprint summary |
| [`../../research/edge_discovery/matched_nulls.py`](../../research/edge_discovery/matched_nulls.py) | matched-null module |
| [`../../research/edge_discovery/filter_ablation.py`](../../research/edge_discovery/filter_ablation.py) | filter-ablation module |
| [`../../research/edge_discovery/multiple_comparison.py`](../../research/edge_discovery/multiple_comparison.py) | multiple-comparison module |
| [`../../research/edge_discovery/cost_feasibility.py`](../../research/edge_discovery/cost_feasibility.py) | cost-feasibility flagging module |
| [`../../research/edge_discovery/retrospectives/c025_matrix_sanity.json`](../../research/edge_discovery/retrospectives/c025_matrix_sanity.json) | C025 matrix-sanity retrospective |
| [`../../research/edge_discovery/retrospectives/c026_matrix_sanity.json`](../../research/edge_discovery/retrospectives/c026_matrix_sanity.json) | C026 matrix-sanity retrospective |
| [`../../research/edge_discovery/retrospectives/c025_cost_feasibility_retrospective.json`](../../research/edge_discovery/retrospectives/c025_cost_feasibility_retrospective.json) | C025 cost-feasibility retrospective |
| [`../../research/edge_discovery/retrospectives/c026_cost_feasibility_retrospective.json`](../../research/edge_discovery/retrospectives/c026_cost_feasibility_retrospective.json) | C026 cost-feasibility retrospective |
| [`../../research/edge_discovery/retrospectives/retrospective_compatibility_gaps.json`](../../research/edge_discovery/retrospectives/retrospective_compatibility_gaps.json) | which retro diagnostics ran vs skipped |

## Edge-discovery front-gate idea selection (EDGE_DISCOVERY_FRONT_GATE_IDEA_SELECTION_001)

Infrastructure / diagnostic / **idea-selection** sprint — *consumed* the merged
edge-discovery lab as a front gate to screen 12 candidate idea families cheaply
before any campaign. **Not** a campaign, **not** CAMPAIGN_027, approves nothing,
opens no test lockbox; `approved_strategies.yaml` stays `approved: []`. Local
data only (H4/H1 on 7 majors; M1/M5/M15/M30 absent → sub-H1 ideas
compatibility-blocked). Outcome: **one idea CAMPAIGN_ELIGIBLE (borderline)** —
H4 low-vol quiet-session strong-extension short-biased z-score reversion — for
which a *draft* precommit prompt was written (not executed). All others
REJECT_CHEAPLY / INCONCLUSIVE / COMPATIBILITY_BLOCKED. C011 stays null; C025/C026
stay REJECT. This sprint is **idea-selection evidence, not strategy evidence.**

| document | purpose |
|---|---|
| [`EDGE_DISCOVERY_FRONT_GATE_IDEA_SELECTION_001_PLAN.md`](EDGE_DISCOVERY_FRONT_GATE_IDEA_SELECTION_001_PLAN.md) | sprint plan + Phase-0 truth audit |
| [`EDGE_DISCOVERY_IDEA_INVENTORY.md`](EDGE_DISCOVERY_IDEA_INVENTORY.md) | 12-family feasibility inventory |
| [`EDGE_DISCOVERY_OPPORTUNITY_MAP_REFRESH.md`](EDGE_DISCOVERY_OPPORTUNITY_MAP_REFRESH.md) | H4/H1 cost/vol opportunity map |
| [`EDGE_DISCOVERY_SIGNAL_PROBE_RESULTS.md`](EDGE_DISCOVERY_SIGNAL_PROBE_RESULTS.md) | 6 forward-return signal probes |
| [`EDGE_DISCOVERY_MATCHED_NULL_SCREENING_RESULTS.md`](EDGE_DISCOVERY_MATCHED_NULL_SCREENING_RESULTS.md) | matched-null + matrix sanity |
| [`EDGE_DISCOVERY_FILTER_ABLATION_RESULTS.md`](EDGE_DISCOVERY_FILTER_ABLATION_RESULTS.md) | filter ablation on the strongest probe |
| [`EDGE_DISCOVERY_IDEA_RANKING_AND_DECISION.md`](EDGE_DISCOVERY_IDEA_RANKING_AND_DECISION.md) | ranked idea selection + decision |
| [`NEXT_CAMPAIGN_PROMPT_FROM_EDGE_DISCOVERY_FRONT_GATE.md`](NEXT_CAMPAIGN_PROMPT_FROM_EDGE_DISCOVERY_FRONT_GATE.md) | draft precommit prompt (NOT executed) |
| [`EDGE_DISCOVERY_COMPATIBILITY_CHECKLIST.md`](EDGE_DISCOVERY_COMPATIBILITY_CHECKLIST.md) | campaign edge-discovery compatibility gate |
| [`EDGE_DISCOVERY_FRONT_GATE_IDEA_SELECTION_001_SUMMARY.md`](EDGE_DISCOVERY_FRONT_GATE_IDEA_SELECTION_001_SUMMARY.md) | sprint summary (27-item) |
| [`../../research/edge_discovery/front_gate_idea_selection/build_opportunity_map.py`](../../research/edge_discovery/front_gate_idea_selection/build_opportunity_map.py) | opportunity-map builder |
| [`../../research/edge_discovery/front_gate_idea_selection/run_signal_probes.py`](../../research/edge_discovery/front_gate_idea_selection/run_signal_probes.py) | signal-probe engine |
| [`../../research/edge_discovery/front_gate_idea_selection/run_matched_null_screening.py`](../../research/edge_discovery/front_gate_idea_selection/run_matched_null_screening.py) | matched-null/matrix-sanity screen |
| [`../../research/edge_discovery/front_gate_idea_selection/run_filter_ablation.py`](../../research/edge_discovery/front_gate_idea_selection/run_filter_ablation.py) | filter-ablation + cost/stationarity check |
| [`../../research/edge_discovery/front_gate_idea_selection/signal_probe_summary.csv`](../../research/edge_discovery/front_gate_idea_selection/signal_probe_summary.csv) | per-prototype probe summary |
| [`../../research/edge_discovery/front_gate_idea_selection/matched_null_probe_summary.csv`](../../research/edge_discovery/front_gate_idea_selection/matched_null_probe_summary.csv) | matched-null per-mode results |

## How to read the evidence

- **Verdicts are bright lines.** Every campaign fixed its gates in a
  pre-commit *before* running. A REJECT means a pre-committed gate
  failed; gates were never relaxed afterward.
- **Test-window discipline.** The 2025–2026 window was a sealed
  lockbox, opened only if a screening gate passed. For 007/008/009 it
  was never opened.
- **R is per-trade expectancy** in units of initial risk. Negative R
  means the strategy lost money per trade after real costs.
- **CAMPAIGN_001 is not evidence** about edge — it ran on synthetic
  candles before OANDA credentials were configured, and exists only as
  harness validation.
