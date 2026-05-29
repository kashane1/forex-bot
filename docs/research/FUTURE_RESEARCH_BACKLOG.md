# Future Research Backlog

**Date:** 2026-05-27 · **Branch:** `research-mtf-confluence-candidate-020-scaffold-001`

> **Nothing in this document is authorized.** This is a menu of *possible*
> future directions, recorded so the research freeze does not lose
> institutional memory. Each item requires an explicit human decision
> before any work begins. The research is currently **frozen** — see
> `docs/research/FINAL_RESEARCH_DECISION_MEMO.md`. No strategy is
> approved; no campaign may be run on the strength of this list.
>
> **Broad seven-pair pattern strategy search is paused** (2026-05-26).
> Re-entry gates: [`BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md`](BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md).
> Trade-quality infrastructure sprints **complete**:
> [`INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_SUMMARY.md`](INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_SUMMARY.md),
> [`INFRA_EXTERNAL_DATA_INGEST_BLOCKER_RESOLUTION_001_SUMMARY.md`](INFRA_EXTERNAL_DATA_INGEST_BLOCKER_RESOLUTION_001_SUMMARY.md),
> [`C008_MEAN_REVERSION_POST_MORTEM_001_SUMMARY.md`](C008_MEAN_REVERSION_POST_MORTEM_001_SUMMARY.md),
> [`STOP_AND_EXIT_DIAGNOSTICS_001_SUMMARY.md`](STOP_AND_EXIT_DIAGNOSTICS_001_SUMMARY.md),
> [`DEDUPED_C008_C009_RERUN_FORENSIC_ONLY_001_SUMMARY.md`](DEDUPED_C008_C009_RERUN_FORENSIC_ONLY_001_SUMMARY.md),
> [`EXIT_HYPOTHESIS_PRECOMMIT_001_SUMMARY.md`](EXIT_HYPOTHESIS_PRECOMMIT_001_SUMMARY.md),
> [`CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001_SUMMARY.md`](CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001_SUMMARY.md),
> [`FINANCING_MODELED_PNL_AND_CARRY_READINESS_001_SUMMARY.md`](FINANCING_MODELED_PNL_AND_CARRY_READINESS_001_SUMMARY.md),
> [`OBSERVED_FINANCING_CAPTURE_READONLY_001_SUMMARY.md`](OBSERVED_FINANCING_CAPTURE_READONLY_001_SUMMARY.md),
> [`PRACTICE_OVERNIGHT_FINANCING_SAMPLE_PLAN_001_SUMMARY.md`](PRACTICE_OVERNIGHT_FINANCING_SAMPLE_PLAN_001_SUMMARY.md),
> [`BACKTRADER_EXIT_PARITY_DIAGNOSTICS_001_SUMMARY.md`](BACKTRADER_EXIT_PARITY_DIAGNOSTICS_001_SUMMARY.md),
> [`ENTRY_ORCHESTRATION_PARITY_DIAGNOSTICS_001_SUMMARY.md`](ENTRY_ORCHESTRATION_PARITY_DIAGNOSTICS_001_SUMMARY.md),
> [`BACKTRADER_ENTRY_PARITY_HARDENING_001_SUMMARY.md`](BACKTRADER_ENTRY_PARITY_HARDENING_001_SUMMARY.md),
> [`EXIT_HYPOTHESIS_PRECOMMIT_002_SUMMARY.md`](EXIT_HYPOTHESIS_PRECOMMIT_002_SUMMARY.md).

Ordering is rough priority. **Item 0** is the recommended next action.
Items 1–2 are infrastructure; items 3–4 are validation / diagnostics;
items 5–8 are genuinely new strategy research — **blocked until
broad-search re-entry gates are met.**

---

## 0-rejected-c026. CAMPAIGN_026 Donchian + HTF confluence timeframe ladder (REJECT — 2026-05-28)

- **Candidate.** `donchian_htf_confluence_timeframe_ladder 0.1.0-c026`. The C025 M5
  family tested across execution timeframes **M3 / M15 / M30** (11 pre-committed
  candidates) to ask whether M5 was *uniquely* cost-defeated. Materialized M3/M30 from
  canonical M1 (~4.18M / ~380K bars; hash-stable, opt-in). Same signal, cost model, and
  evidence discipline as C025; split identical (train 2021-07-01→2023-06-30).
- **Status.** **REJECT — `REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE /
  TEST_LOCKBOX_CLOSED / NOT_APPROVED`.** **0/11 eligible.** No champion → validation not
  run; no single-pair review; lockbox closed; paper/demo/live blocked. See
  [`CAMPAIGN_026_TRAIN_TIMEFRAME_LADDER_RESULT.md`](CAMPAIGN_026_TRAIN_TIMEFRAME_LADDER_RESULT.md)
  and [`CAMPAIGN_026_TIMEFRAME_LADDER_INTERPRETATION.md`](CAMPAIGN_026_TIMEFRAME_LADDER_INTERPRETATION.md).
- **Reusable lesson (decisive).** Cost **and** expectancy improve monotonically as the
  timeframe slows — M3 −0.16R (spread/ATR 0.59) → M5 −0.12 (0.44) → M15 −0.06 (0.23) →
  M30 −0.008 (0.15). **M5 was *not* uniquely cost-defeated**; it sits on a smooth
  cost/timeframe curve and M15/M30 are genuinely much cheaper. But the best candidate
  anywhere (M30 trend-runner) is still net-negative, below the C011 null, failing 2×
  stress. **Removing cost reveals a coin-flip, not a hidden edge** — the Donchian + HTF
  construct has no intrinsic directional edge on the majors. Cheaper execution is
  *necessary but not sufficient*: do not assume a slower timeframe rescues a null signal.
- **USD_JPY.** Again the lone consistently-positive leg (M30 +0.19R) — best explained
  by its cheapest spread, fails 2× stress, aggregate negative → **not** a single-pair
  trigger; overlaps the already-exhausted USD_JPY microstructure/price-structure thread.
- **Next sprint.** **None for this family** — close the lower-timeframe Donchian + HTF
  family across M3–M30; do not re-tune. Backtrader parity = `DEFER_PARITY_REJECTED`.
  Any revival needs a **new external thesis or signal**, not another timeframe/param
  sweep (consistent with the standing `PAUSE_STRATEGY_RESEARCH` posture). The M3/M30
  materialization + timeframe cost-diagnostic infrastructure is reusable.

---

## 0-rejected-c025. CAMPAIGN_025 M5 Donchian + HTF confluence breakout (REJECT — 2026-05-28)

- **Candidate.** `m5_donchian_htf_confluence_breakout 0.1.0-c025`. M5 Donchian(20)
  breakout trigger gated by M15 pullback/compression + H1/H4M1 trend + D1AGG
  (native-H4-derived) permissive regime; `next_bar_open` fills; single frozen stop
  (farther of 2.0×ATR and the opposite prior-20-bar channel side) + 48-bar time
  stop; no TP/trailing/protective.
- **Status.** **REJECT — `REJECT_MATRIX_NO_TRAIN_CANDIDATE / TEST_LOCKBOX_CLOSED /
  NOT_APPROVED`.** Train-matrix sprint ran 16 archetypes on train 2021-07-01→
  2023-06-30; **0/16 eligible** (all net-negative, spread/ATR ≈ 0.45 on M5, none
  beats the C011 null). No champion → validation not run; no single-pair review;
  lockbox closed; paper/demo/live blocked. See
  [`CAMPAIGN_025_TRAIN_MATRIX_RESULT.md`](CAMPAIGN_025_TRAIN_MATRIX_RESULT.md) and
  [`CAMPAIGN_025_INTERPRETATION_AND_PRIOR_COMPARISON.md`](CAMPAIGN_025_INTERPRETATION_AND_PRIOR_COMPARISON.md).
- **Reusable lesson.** M5 execution for spread-paying majors is defeated by a
  spread/ATR ratio ≈ 0.5; future M5 ideas must clear a **cost-stress gate before
  signal design** and target a much larger per-trade move or a lower-spread regime.
- **Precommit / plan.**
  [`CAMPAIGN_025_PRECOMMIT_M5_DONCHIAN_HTF_CONFLUENCE_SCOPE.md`](CAMPAIGN_025_PRECOMMIT_M5_DONCHIAN_HTF_CONFLUENCE_SCOPE.md),
  [`CAMPAIGN_025_M5_DONCHIAN_HTF_CONFLUENCE_SCAFFOLD_001_PLAN.md`](CAMPAIGN_025_M5_DONCHIAN_HTF_CONFLUENCE_SCAFFOLD_001_PLAN.md).
- **Why C025 (not C024).** The retired C022/C023 family closeout already used
  **"C024"** for a *pullback-resolution continuation* idea (recorded as
  `C024 NOT_READY` in `C024_READINESS_FROM_C022_FEATURE_SEPARATION.md`) that was
  never built. To avoid reusing a number already in the record, this M5 Donchian
  campaign takes the next free number, **C025**. It is also **not** a same-shaped
  pullback-resolution campaign (the trigger is a Donchian channel break on M5, not
  an M15 EMA20 reclaim), so it does **not** reopen the retired family and does not
  depend on its reopening bar.
- **Next sprint.** None for this family — the train-matrix sprint
  (`research-campaign-025-m5-donchian-htf-confluence-train-matrix-validation-001`)
  is **complete and REJECT**. Do not re-gate or re-tune C025; any revival needs a
  materially different idea that clears a cost-stress gate first (see lesson above).
  Backtrader parity = `DEFER_PARITY_REJECTED`.

---

## 0-retired-c022-c023. H4/H1 pullback resolution family (RETIRED — 2026-05-28)

- **Candidates.** `h4_h1_pullback_resolution_entry` — CAMPAIGN_022 (`0.1.0-c022`,
  H4 ADX gate **20**, **REJECT**) and its pre-registered sibling CAMPAIGN_023
  (`0.1.0-c023`, H4 ADX gate **22**, scaffold-only/not executed). Identical in every
  other respect; one shared strategy class.
- **Precommit.** [`CAMPAIGN_023_H4_H1_PULLBACK_RESOLUTION_ADX22_PRECOMMIT.md`](CAMPAIGN_023_H4_H1_PULLBACK_RESOLUTION_ADX22_PRECOMMIT.md)
- **Status.** **RETIRED — `RETIRED_UNLESS_NEW_EXTERNAL_THESIS`** (2026-05-28).
  Post-execution diagnostics localized C022's failure to the **entry signal**: all
  ATR/time stop variants and a cost-free baseline stay negative, and every structural
  entry feature (H4 regime, H1 pullback, M15 reclaim) sits at AUC ≈ 0.50. C023 ADX22
  is **not authorized** — H4 ADX does not separate winners from losers (flat quintile
  win-rates). C024 is **NOT_READY**; **no CAMPAIGN_024 is created**. See
  [`C022_C023_PULLBACK_RESOLUTION_FAMILY_CLOSEOUT.md`](C022_C023_PULLBACK_RESOLUTION_FAMILY_CLOSEOUT.md).
- **Reopening bar (all four required).** A new external market-structure thesis; a
  materially different trigger (not a threshold change on the M15 EMA reclaim);
  independent out-of-sample evidence; and not merely re-gated parameters. Absent all
  four, do not open any same-shaped C02x pullback-resolution campaign.

---

## 0-closed-usdjpy-microstructure. USD_JPY M15 microstructure — ENTRY + POST-ENTRY LANES CLOSED (2026-05-28)

- **What it was.** The selected Lane D (market-microstructure-style confirmation),
  scoped to **USD_JPY only**, run read-only over the 306 USD_JPY C022 base trades
  (train 133 / val 173): an **entry** diagnostic (live detectors: impulse,
  micro-swing-break, sweep+displacement, range-expansion) and a follow-up **post-entry
  trade-management** diagnostic (retest-hold, trap, early MFE/MAE at horizons 2/4/8/16).
- **Entry lane: CLOSED.** No live primitive showed material, stable winner/loser
  separation (best stable live effect |AUC−0.5| = 0.016, below the 0.05 floor) and none
  beat the inert EMA20-reclaim baseline. **C024 `NOT_READY`; no CAMPAIGN_024 created.**
- **Post-entry trade-management lane: CLOSED (`NOT_READY`).** Post-entry events separate
  outcomes only **descriptively**; **all five predeclared early-exit counterfactuals
  reduced expectancy on both splits** (−0.065 to −0.134R) — flagged trades often recover
  before the stop and the rules cut winners. Not actionable.
- **Final status.** The full C022/C023/USD_JPY microstructure thread is **CLOSED at both
  the entry and management layers — no actionable edge.** See
  [`C022_C023_USDJPY_MICROSTRUCTURE_THREAD_CLOSEOUT.md`](C022_C023_USDJPY_MICROSTRUCTURE_THREAD_CLOSEOUT.md).
- **No more mining of this family is recommended.** The next genuinely-new lane is
  compared in
  [`NEXT_RESEARCH_LANE_AFTER_USDJPY_MICROSTRUCTURE_CLOSEOUT.md`](NEXT_RESEARCH_LANE_AFTER_USDJPY_MICROSTRUCTURE_CLOSEOUT.md);
  default = source/map a genuinely different edge (external thesis + session atlas), not
  another C022-style entry variant.
- **Forbidden.** No entry-alpha or management campaign on USD_JPY microstructure; no
  C024; no C023 execution; no approval; no paper/demo/live; no further mining of these
  signals (the counterfactual already shows acting on them is net-negative).

---

## 0-paused-strategy-search. STRATEGY SEARCH PAUSED after macro-context (2026-05-28)

- **What happened.** After the microstructure thread, three further genuinely-new
  read-only lanes were run and all returned null: (a) external-thesis sourcing + USD_JPY
  session/vol/spread atlas; (b) volatility-compression→expansion (broad thesis falsified;
  one post-hoc London-continuation lead); (c) the London-continuation overfit-hardened
  confirmation (**FAILED** — dies under any intrabar stop, conservative cost, Bonferroni
  ×12, and is a 2022/2024 trend-regime artifact); (d) slow macro/rates/calendar
  tradeability context (lookahead-safe + latency-independent but **no actionable
  conditioning**; rate-regime non-identifiable on current history, JP leg absent).
- **Standing decision.** **`PAUSE_STRATEGY_RESEARCH`** on the current data/thesis set.
  Both the price-structure and macro-context families are exhausted. See
  [`STRATEGY_SEARCH_PAUSE_AFTER_USDJPY_MACRO_CONTEXT.md`](STRATEGY_SEARCH_PAUSE_AFTER_USDJPY_MACRO_CONTEXT.md),
  [`STRATEGY_RESEARCH_RESTART_CRITERIA.md`](STRATEGY_RESEARCH_RESTART_CRITERIA.md),
  [`NEXT_ACTION_OPTIONS_AFTER_STRATEGY_SEARCH_PAUSE.md`](NEXT_ACTION_OPTIONS_AFTER_STRATEGY_SEARCH_PAUSE.md).
- **C024 status.** **Not created; blocked by the pause** until the restart criteria are
  met. C023 not executed. Verdicts unchanged; `approved: []`; paper/demo/live blocked.
- **Forbidden.** No more indicator/threshold/stop tweaks as a "rescue"; no C022/C023 or
  microstructure re-mining; no macro-context re-mining without new data; no C024; no new
  campaign number until a restart criterion is met.
- **Data-acquisition infra items that would UNBLOCK future work (not authorized):**
  verified JP rate leg + multi-cycle history (to make a rate-differential regime
  *identifiable*); verified BOJ/CPI economic-event calendar; options/vol or order-flow
  proxy data; any non-price external source. These are infrastructure, not strategy.

---

## 0-complete-c020. CAMPAIGN_020 MTF confluence execution (COMPLETE — REJECT)

- **Sprint name.** `research-campaign-020-mtf-confluence-execution-001`
- **Result.** Train **−0.035 R**, validation **+0.053 R** under `next_bar_open`; train gate **FAIL**; test lockbox **closed**.
- **Summary.** [`CAMPAIGN_020_MTF_CONFLUENCE_EXECUTION_001_SUMMARY.md`](CAMPAIGN_020_MTF_CONFLUENCE_EXECUTION_001_SUMMARY.md)
- **Status.** **COMPLETE — REJECT**

---

## 0. CAMPAIGN_019 thesis-invalidation execution (COMPLETE — REJECT)

- **Sprint name.** `research-campaign-019-thesis-invalidation-execution-001`
- **Result.** CAMPAIGN_019 executed under frozen precommit; train **−0.072 R**, validation **+0.0962 R**; screening **FAIL**; test lockbox closed; Backtrader parity **PASS**.
- **Summary.** [`CAMPAIGN_019_THESIS_INVALIDATION_EXECUTION_001_SUMMARY.md`](CAMPAIGN_019_THESIS_INVALIDATION_EXECUTION_001_SUMMARY.md)
- **Status.** **COMPLETE — REJECT**

---

## 0-recommended. Practice overnight sample + observed capture execute (NEXT)

- **Why.** Sprint 002 built capture tooling; execute blocked without local practice credentials; prior window returned **OBSERVED_FINANCING_EMPTY**.
- **Actions.** Human overnight hold per [`PRACTICE_OVERNIGHT_FINANCING_SAMPLE_COLLECTION_RUNBOOK.md`](PRACTICE_OVERNIGHT_FINANCING_SAMPLE_COLLECTION_RUNBOOK.md); then `scripts/capture_oanda_observed_financing_readonly.py --execute-readonly-capture`.
- **Status.** **BLOCKED_AWAITING_LOCAL_CREDENTIALS_AND_SAMPLE**

## 0-complete-capture-002. Observed financing capture read-only 002 (COMPLETE)

- **Sprint name.** `infra-observed-financing-capture-readonly-002`
- **Result.** Endpoint allowlist, capture script, fixture schema, reconciliation; execute blocked in runner; empty placeholder fixture.
- **Summary.** [`OBSERVED_FINANCING_CAPTURE_READONLY_002_SUMMARY.md`](OBSERVED_FINANCING_CAPTURE_READONLY_002_SUMMARY.md)
- **Status.** **COMPLETE** — infrastructure only; no strategy approval.

## 0-complete-financing-overlay. Observed financing overlay local-first (COMPLETE)

- **Sprint name.** `infra-observed-cost-financing-overlay-local-first-001`
- **Result.** Ledger overlay contract, runner, synthetic_fixture runs on C008/C016/C017/C019 reference ledgers.
- **Summary.** [`OBSERVED_COST_FINANCING_OVERLAY_LOCAL_FIRST_001_SUMMARY.md`](OBSERVED_COST_FINANCING_OVERLAY_LOCAL_FIRST_001_SUMMARY.md)
- **Status.** **COMPLETE** — infrastructure only; no strategy approval.

## 0-fill-timing-rule. Approval-bound fill timing + HTF align (POLICY — COMPLETE)

- **Sprint:** `infra-next-bar-open-policy-and-htf-align-migration-001`
- Future approval-bound precommits must **declare `fill_timing`**; default **`next_bar_open`**; `signal_bar_close` = diagnostic/upper-bound (`promotion_eligible: false`).
- Future HTF strategies must use **`htf_align.align_last_completed()`** or **`d1agg_htf`** (weekly completed-period = documented exception).
- Multi-day strategies must declare **financing mode**; observed financing still **BLOCKED** until practice sample.
- Docs: [`FILL_TIMING_APPROVAL_BOUND_POLICY.md`](FILL_TIMING_APPROVAL_BOUND_POLICY.md), [`HTF_ALIGNMENT_POLICY_FOR_FUTURE_STRATEGIES.md`](HTF_ALIGNMENT_POLICY_FOR_FUTURE_STRATEGIES.md), [`NEXT_BAR_OPEN_POLICY_AND_HTF_ALIGN_MIGRATION_001_SUMMARY.md`](NEXT_BAR_OPEN_POLICY_AND_HTF_ALIGN_MIGRATION_001_SUMMARY.md)
- Evidence: [`NEXT_BAR_OPEN_REFERENCE_COMPARISON_RESULT.md`](NEXT_BAR_OPEN_REFERENCE_COMPARISON_RESULT.md) (C019 validation −0.079 R delta).

## 0-complete. Shared audit WARN remediation (COMPLETE)

- **Sprint name.** `infra-shared-audit-warn-remediation-and-next-bar-open-001`
- **Result.** C019 fill-timing comparison; `htf_align`; RSI `warmup_policy`; optional signal provenance fields.
- **Summary.** [`SHARED_AUDIT_WARN_REMEDIATION_AND_NEXT_BAR_OPEN_001_SUMMARY.md`](SHARED_AUDIT_WARN_REMEDIATION_AND_NEXT_BAR_OPEN_001_SUMMARY.md)

## 0-previous. Exit hypothesis precommit 003 OR financing overlay

- **Why it matters.** C018 (+1R protective) and C019 (z±3 thesis invalidation) both show validation uplift with **train failure** — exit-only tweaks on C008 entries are not rescuing in-sample edge.
- **Options.**
  1. `research-exit-hypothesis-precommit-003` — pre-register a **different** falsifiable exit mechanism (no C019 retuning).
  2. `research-financing-manual-rate-source-expansion-001` — financing overlay before further REVISE interpretation.
- **Status.** **RECOMMENDED** — human choice; no execution authorized from this backlog alone.

---

## 0-complete. Exit hypothesis precommit 002 (COMPLETE)

- **Sprint name.** `research-exit-hypothesis-precommit-002`
- **Result.** CAMPAIGN_019 pre-registered (thesis invalidation z ≤ −3 / z ≥ +3); PRECOMMITTED_NOT_RUN.
- **Summary.** [`EXIT_HYPOTHESIS_PRECOMMIT_002_SUMMARY.md`](EXIT_HYPOTHESIS_PRECOMMIT_002_SUMMARY.md)
- **Status.** **COMPLETE — PRECOMMIT_DESIGN**

---

## 0-complete-prior. Backtrader entry parity hardening (COMPLETE)

- **Sprint name.** `infra-backtrader-entry-parity-hardening-001`
- **Result.** PnL fix landed; C008/C009/C018 within ±1 trade; exit shares CLOSE_MATCH.
- **Summary.** [`BACKTRADER_ENTRY_PARITY_HARDENING_001_SUMMARY.md`](BACKTRADER_ENTRY_PARITY_HARDENING_001_SUMMARY.md)
- **Status.** **COMPLETE — PARITY_DIAGNOSTIC**

---

## 0-next-blocked. Backtrader general parity framework (IF NEEDED LATER)

- **Sprint name.** `infra-backtrader-general-parity-framework-001`
- **Why it matters.** Reusable framework for future campaigns beyond C008/C009/C018.
- **Status.** **NOT RECOMMENDED NOW** — C008/C009/C018 lane sufficient for next exit sprint.

---

## 0-paused. Human practice overnight sample (PAUSED — NOT A SPRINT)

- **Why it matters.** Read-only capture returned **zero DAILY_FINANCING**; parser/capture ready but no observed data.
- **Action.** Human follows [`PRACTICE_OVERNIGHT_FINANCING_SAMPLE_COLLECTION_RUNBOOK.md`](PRACTICE_OVERNIGHT_FINANCING_SAMPLE_COLLECTION_RUNBOOK.md) — manual practice UI trades only.
- **Status.** **PAUSED** by operator directive — no Cursor/bot order submission; do not resume until explicitly authorized.

---

## 0-complete. Entry orchestration parity diagnostics (COMPLETE)

- **Sprint name.** `infra-entry-orchestration-parity-diagnostics-001`
- **Result.** BACKTRADER_IMPLEMENTATION_GAP — missing quote→USD PnL; fix narrows gap to ±1 trade.
- **Summary.** [`ENTRY_ORCHESTRATION_PARITY_DIAGNOSTICS_001_SUMMARY.md`](ENTRY_ORCHESTRATION_PARITY_DIAGNOSTICS_001_SUMMARY.md)
- **Status.** **COMPLETE — PARITY_DIAGNOSTIC**

---

## 0-complete-prior. Backtrader exit parity diagnostics (COMPLETE)
- **Result.** Backtrader 1.9.78 exit shares CLOSE_MATCH bespoke; trade counts MATERIAL_DIVERGENCE (entry-side).
- **Summary.** [`BACKTRADER_EXIT_PARITY_DIAGNOSTICS_001_SUMMARY.md`](BACKTRADER_EXIT_PARITY_DIAGNOSTICS_001_SUMMARY.md)
- **Status.** **COMPLETE — PARITY_DIAGNOSTIC**

---

## 0-complete-prior. Practice overnight financing sample plan (COMPLETE — PLANNING ONLY)

- **Sprint name.** `infra-practice-overnight-financing-sample-plan-001`
- **Result.** Human-only runbooks; manual sample path created then **paused** by operator.
- **Summary.** [`PRACTICE_OVERNIGHT_FINANCING_SAMPLE_PLAN_001_SUMMARY.md`](PRACTICE_OVERNIGHT_FINANCING_SAMPLE_PLAN_001_SUMMARY.md)
- **Status.** **COMPLETE — PAUSED**

---

## 0-next. Post-sample observed financing capture (CONDITIONAL SPRINT)

- **Sprint name.** `infra-observed-financing-post-sample-capture-001`
- **Trigger.** Human sample exists; OANDA history shows DAILY_FINANCING > 0.
- **Action.** Run capture per [`POST_SAMPLE_OBSERVED_FINANCING_CAPTURE_CHECKLIST.md`](POST_SAMPLE_OBSERVED_FINANCING_CAPTURE_CHECKLIST.md); commit sanitized artifacts.
- **Status.** **BLOCKED** — manual sample paused; no bot trades.

---

## 0-next-bridge. Observed-to-modeled financing bridge (CONDITIONAL SPRINT)

- **Sprint name.** `infra-financing-observed-to-modeled-bridge-001`
- **Trigger.** Post-sample capture succeeds with sanitized JSON.
- **Design.** [`OBSERVED_TO_MODELED_FINANCING_BRIDGE_DESIGN.md`](OBSERVED_TO_MODELED_FINANCING_BRIDGE_DESIGN.md)
- **Status.** **BLOCKED** — waiting on non-empty observed capture.

---

## 0-complete-prior. Observed financing capture read-only (COMPLETE — EMPTY)

- **Sprint name.** `infra-observed-financing-capture-readonly-001`
- **Result.** Read-only GET capture; 0 DAILY_FINANCING in 180 days; parser + sanitizer ready.
- **Summary.** [`OBSERVED_FINANCING_CAPTURE_READONLY_001_SUMMARY.md`](OBSERVED_FINANCING_CAPTURE_READONLY_001_SUMMARY.md)
- **Status.** **COMPLETE — OBSERVED_FINANCING_EMPTY**

---

## 0-complete-prior. Financing modeled PnL and carry readiness (COMPLETE)

- **Sprint name.** `research-financing-modeled-pnl-and-carry-readiness-001`
- **Delivered.** Capability audit, overlay utility, C008/C009/C018 synthetic exposure.
- **Summary.** [`FINANCING_MODELED_PNL_AND_CARRY_READINESS_001_SUMMARY.md`](FINANCING_MODELED_PNL_AND_CARRY_READINESS_001_SUMMARY.md)
- **Status.** **COMPLETE** — carry not ready; observed capture is next blocker.

---

## 0-complete-prior. CAMPAIGN_018 protective-stop execution (COMPLETE — REJECT)

- **Sprint name.** `research-campaign-018-protective-stop-execution-001`
- **Result.** Train −0.119 R / val +0.194 R; screening FAIL; test lockbox not opened.
- **Summary.** [`CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001_SUMMARY.md`](CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001_SUMMARY.md)
- **Status.** **COMPLETE — REJECT**

---

## 0-complete-prior. Exit hypothesis precommit (COMPLETE)

- **Sprint name.** `research-exit-hypothesis-precommit-001`
- **Delivered.** One hypothesis selected, CAMPAIGN_018 scope/gates/implementation design,
  execution sprint prompt. **No backtest run.**
- **Summary.** [`EXIT_HYPOTHESIS_PRECOMMIT_001_SUMMARY.md`](EXIT_HYPOTHESIS_PRECOMMIT_001_SUMMARY.md)
- **Status.** **COMPLETE** — CAMPAIGN_018 pre-registered, not executed.

---

## 0-complete-prior. Deduped C008/C009 forensic replay (COMPLETE)

- **Sprint name.** `infra-deduped-c008-c009-rerun-forensic-only-001`
- **Delivered.** Frozen config reconstruction, deduped replay, old vs deduped comparison,
  exit anatomy/MAE/MFE refresh, evidence integrity decision.
- **Summary.** [`DEDUPED_C008_C009_RERUN_FORENSIC_ONLY_001_SUMMARY.md`](DEDUPED_C008_C009_RERUN_FORENSIC_ONLY_001_SUMMARY.md)
- **Status.** **COMPLETE** — C008/C009 remain REJECT; descriptive claims confirmed.

---

## 0-complete-prior. Stop and exit diagnostics (COMPLETE)

- **Why it mattered.** C008 post-mortem showed validation edge entirely time-stop
  driven; train failure stop-dominated. Needed cross-campaign context.
- **Sprint name.** `research-stop-and-exit-diagnostics-001`
- **Delivered.** Exit artifact inventory, cross-campaign matrix, C008/C009 forensics,
  MAE/MFE diagnostics, future exit hypotheses + gate.
- **Summary.** [`STOP_AND_EXIT_DIAGNOSTICS_001_SUMMARY.md`](STOP_AND_EXIT_DIAGNOSTICS_001_SUMMARY.md)
- **Status.** **COMPLETE** — diagnostic only; no strategy approved.

---

## 0-deferred. Gold manual CSV or COT design advance (OPTIONAL — NOT BLOCKING)

- **Why it matters.** Gold (`MANUAL_CSV_REQUIRED`) and COT (`DESIGN_ONLY`) remain
  optional enhancements. FRED ingest complete; C008 post-mortem did not identify
  positioning as the primary failure mode.
- **Sprint name.** `infra-gold-manual-csv-or-cot-design-001` or
  `infra-cot-positioning-feature-ingest-001`
- **Status.** **DEFERRED** — not blocking mean-reversion understanding.

---

## 0-complete. C008 mean-reversion post-mortem (COMPLETE)

- **Sprint.** `research-c008-mean-reversion-post-mortem-001`
- **Delivered.** Evidence reconstruction, trade anatomy, cross-asset regime overlay,
  confluence overlay, human review post-mortem, future research gate.
- **Summary.** [`C008_MEAN_REVERSION_POST_MORTEM_001_SUMMARY.md`](C008_MEAN_REVERSION_POST_MORTEM_001_SUMMARY.md)
- **Status.** **COMPLETE** — diagnostic only; C008/C009 remain REJECT.

---

## 0-complete-prior. External data credentials setup (COMPLETE)

- **Sprint.** operator action — `FRED_API_KEY` configured locally
- **Delivered.** Full-window FRED fetch (7 series, 2,148 daily rows), H4 alignment
  100% coverage, `cross_asset_missing` eliminated.
- **Summary.** [`INFRA_EXTERNAL_DATA_INGEST_BLOCKER_RESOLUTION_001_SUMMARY.md`](INFRA_EXTERNAL_DATA_INGEST_BLOCKER_RESOLUTION_001_SUMMARY.md)
- **Status.** **COMPLETE** — FRED auth resolved; data ingested.

---

## 0-complete-prior. External data ingest blocker resolution (COMPLETE)

- **Sprint.** `infra-external-data-ingest-blocker-resolution-001`
- **Delivered.** H4-aware observation window, full-window pipeline, fetch status
  reporting, local CSV template/validation, enhanced manifest, alignment audit,
  diagnostic re-run.
- **Summary.** [`INFRA_EXTERNAL_DATA_INGEST_BLOCKER_RESOLUTION_001_SUMMARY.md`](INFRA_EXTERNAL_DATA_INGEST_BLOCKER_RESOLUTION_001_SUMMARY.md)
- **Status.** **COMPLETE** — FRED ingest succeeded after operator auth.

---

## 0-superseded. External data credentials or manual CSV setup (SUPERSEDED)

- **Sprint name.** `infra-external-data-credentials-or-manual-csv-setup-001`
- **Status.** **SUPERSEDED** — FRED auth configured; full-window ingest complete.

---

---

## 0-complete-prior. Cross-asset real-data ingest (COMPLETE)

- **Sprint.** `infra-cross-asset-real-data-ingest-001`
- **Delivered.** Source registry, FRED fetcher, local CSV loader, normalization,
  derived features, H4 availability alignment, COT design, diagnostic re-run.
- **Summary.** [`INFRA_CROSS_ASSET_REAL_DATA_INGEST_001_SUMMARY.md`](INFRA_CROSS_ASSET_REAL_DATA_INGEST_001_SUMMARY.md)
- **Status.** **COMPLETE** — superseded by full-window FRED ingest.

---

## 0-complete-prior. Cross-asset real-data ingest planning (SUPERSEDED)

- **Sprint name.** `infra-cross-asset-real-data-ingest-001` (planning entry — now complete)
- **Status.** **COMPLETE** — see above.

---

## 0-complete-mtf. Multi-timeframe confluence + cost atlas (COMPLETE)

- **Sprint.** `infra-multi-timeframe-confluence-and-cost-atlas-001`
- **Delivered.** Cost atlas (69,648 H4 bars), confluence prototype,
  cross-asset scaffolding, diagnostic runner, validation protocol.
- **Summary.** [`INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_SUMMARY.md`](INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_SUMMARY.md)
- **Status.** **COMPLETE** — diagnostic only; no strategy approved.

---

## 1. Improve the financing / swap model

- **Why it might matter.** Financing (overnight swap) is currently
  unmodeled in the backtest engine — only a conservative stress overlay
  exists. It is an unconditional hard blocker for *any* live promotion.
  Until it is modelled, no backtest figure can be trusted as a net
  result.
- **Required data / code.** A reliable historical swap-rate source per
  instrument (broker financing tables or a data vendor); a financing
  accrual in `BacktestEngine` keyed on position carry and rollover
  timestamps; reconciliation against real OANDA financing transactions.
- **Risk of overfitting.** Low — this is a cost model, not a signal.
  The danger is *under*-modelling (optimism), not overfitting.
- **What would count as success.** Engine PnL includes financing;
  backtested financing reconciles within a small tolerance against real
  practice-account financing transactions; the conservative stress
  overlay can be retired.

## 2. Valid D1 (daily) backtest support

- **Why it might matter.** CAMPAIGN_006 could not test a daily-trend
  hypothesis at all: D1 candles close at the 17:00 NY rollover and the
  engine's intraday fill / session / spread machinery is invalid for
  them. A whole timeframe is currently untestable.
- **Required data / code.** Either (a) next-bar-open fills plus a
  non-rollover spread reference for true D1 candles, or (b) synthetic
  daily bars aggregated from already-validated H4 candles, with a
  documented, tested aggregation that avoids the rollover contamination.
  A non-rollover spread snapshot is required either way.
- **Risk of overfitting.** Low for the infrastructure itself; normal
  for any strategy later tested on D1.
- **What would count as success.** A D1 backtest of a known strategy
  produces results consistent with its H4 behaviour and with no
  session/spread artifacts; the CAMPAIGN_006 blocker is lifted.

## 3. Lean parity for one historical rejected campaign

- **Why it might matter.** The backtest engine is bespoke. Reproducing
  one rejected campaign (e.g. CAMPAIGN_002 trend baseline) in an
  independent engine (QuantConnect Lean) would validate the engine
  itself — that the REJECT verdicts are real, not an engine artifact.
- **Required data / code.** The `src/forex_bot/lean/` parity notes; a
  Lean project replicating one strategy + the same OANDA candles; a
  comparison of trade-by-trade output.
- **Risk of overfitting.** None — this is verification, not search.
- **What would count as success.** Lean and the bespoke engine agree on
  trade entries/exits and aggregate metrics for the chosen campaign
  within a small, explained tolerance.

## 4. Richer market-regime diagnostics

- **Why it might matter.** CAMPAIGN_005 measured one regime statistic
  (efficiency ratio 0.24 — choppy). A richer, time-resolved regime map
  (trend vs range vs volatile, per pair, per period) would let a future
  human judge *whether any tradable regime exists at all* before
  committing to a strategy campaign.
- **Required data / code.** A diagnostics script over the existing
  OANDA candle store; regime metrics (efficiency ratio, ADX
  distribution, autocorrelation, realised vol regimes); no strategy, no
  pass/fail gate.
- **Risk of overfitting.** Low if it stays descriptive. The danger is
  using the diagnostics to *reverse-engineer* a strategy to the sample —
  which must be explicitly avoided.
- **What would count as success.** A descriptive regime atlas that a
  human can read to decide whether further strategy research is even
  worthwhile — purely informational.

## 5. Non-FX or multi-asset research

- **Why it might matter.** The project tested six FX majors and found no
  edge. Other asset classes (index CFDs, commodities, crypto) have
  different regime and cost structures; an edge absent in FX majors may
  exist elsewhere — or the same null result may recur, which is itself
  informative.
- **Required data / code.** A data source and a verified candle store
  for the new asset class; instrument metadata; cost (spread / commission
  / financing) models appropriate to that class.
- **Risk of overfitting.** High — a new universe multiplies the search
  space. Strict pre-commit discipline and held-out test windows are
  mandatory.
- **What would count as success.** A strategy that passes a pre-committed
  screening **and** test window on real data for the new class, earning
  at most PAPER-TRADE-ONLY.

## 6. Carry / swap-aware research — only after item 1

- **Why it might matter.** Carry (holding positive-swap positions) is a
  recognised FX return source. But researching it *before* the financing
  model exists would be meaningless — carry research is entirely a
  financing-PnL question.
- **Required data / code.** A completed, reconciled financing model
  (item 1) is a hard prerequisite; historical swap rates; a
  carry-oriented signal.
- **Risk of overfitting.** Moderate — carry is a small, slow signal
  easily swamped by curve-fitting on a short sample.
- **What would count as success.** Net-of-financing positive expectancy
  on a pre-committed test window, with the edge attributable to carry
  rather than to price direction.

## 7. Mean-reversion revisit — only with a fresh human-approved thesis

- **Why it might matter.** Regime-filtered mean reversion was the only
  family with a real validation-era signal (CAMPAIGN_008/009). It is the
  most plausible place an edge could exist.
- **Required data / code.** A **genuinely new thesis** — not a tweak of
  c008/c009, not a relaxed gate. Possible angles: a different regime
  definition, a different universe, an explicit volatility filter. A
  fresh pre-commit and explicit human authorization.
- **Risk of overfitting.** High — mean reversion overfits easily, and
  the project has already looked at this data twice. A third look at the
  same data is especially dangerous; any revisit should prefer new data
  or a new universe.
- **What would count as success.** An **independent** train split that
  is non-negative (both prior campaigns failed exactly here), plus a
  passed test window — the bar c008/c009 could not clear.

## 8. News / economic-calendar filter research — only with reliable data

- **Why it might matter.** Large scheduled events (rate decisions, NFP)
  drive spread spikes and gaps. A filter that avoids trading around them
  could improve any future strategy's cost profile.
- **Required data / code.** A *reliable* historical economic-calendar
  data source with accurate timestamps — without it, this research is
  not worth starting. A calendar-aware filter in the risk engine.
- **Risk of overfitting.** Moderate — event windows are a tempting place
  to fit noise; the filter must be specified before seeing results.
- **What would count as success.** A calendar filter that measurably
  reduces adverse-cost trades on a pre-committed window without being
  tuned to specific historical events.

---

## Cross-cutting discipline (applies to every item above)

- No item is authorized; each needs an explicit human decision.
- Every strategy campaign needs a pre-commit written and committed
  *before* the run, with gates fixed in advance.
- The 2025–2026 reported test window stays a sealed lockbox until a
  screening gate passes.
- Best attainable verdict remains **PAPER-TRADE-ONLY** until financing
  is modelled; live trading is out of scope.
- A strategy is only ever runnable in a loop after a human adds it to
  `configs/approved_strategies.yaml`.
- See `docs/research/HYPOTHESIS_BACKLOG.md` for the earlier,
  campaign-era hypothesis list.

## 9. CAMPAIGN_021 LTF MTF confluence — REJECT (2026-05-28)

- **Verdict:** REJECT — train expectancy **−0.0174 R** (1,438 trades); train gate fail.
- **Re-run:** post-materialization; metrics bit-identical (bars verified); train runtime ~40 min vs multi-hour pre-infra.
- **Not run:** validation, 2× cost stress, Backtrader parity, test lockbox (no validation rescue).
- **vs C020:** train improved from −0.035 R but remained negative; ~4× trade count on M15.
- **Data.** Materialized M1-derived M15/H1/H4M1 + native H4→D1AGG; `next_bar_open`.
- **Next.** New structural hypothesis only via new precommit — not C021 retune.
- See [`CAMPAIGN_021_FINAL_INTERPRETATION.md`](CAMPAIGN_021_FINAL_INTERPRETATION.md).

## 10. M1 derived timeframe materialization — INFRA_PASS (2026-05-28)

- **Sprint.** `infra-m1-derived-timeframe-materialization-001`
- **What.** Postgres materialization of M1→M5/M15/H1/H4M1 (`source=m1_materialized`).
- **Why.** Removes per-campaign M1 re-aggregation; `--data-feature-preflight` ~21s vs multi-hour M1 scans.
- **Note.** Does not fix M15 backtest O(n²) indicator cost; speeds data loading only.
- See [`M1_DERIVED_TIMEFRAME_MATERIALIZATION_001_SUMMARY.md`](M1_DERIVED_TIMEFRAME_MATERIALIZATION_001_SUMMARY.md).
