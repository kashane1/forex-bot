# Next Sprint Prompt — CAMPAIGN_021 LTF MTF Confluence Execution

**Date:** 2026-05-27  
**Prior sprint:** `research-campaign-021-ltf-mtf-confluence-scaffold-001`  
**Branch:** `research-campaign-021-ltf-mtf-confluence-execution-001`

Copy the block below into a new agent session.

---

## Sprint prompt (copy from here)

```
We are executing CAMPAIGN_021 evidence for lower_timeframe_mtf_confluence_entry 0.1.0-c021.

Branch: research-campaign-021-ltf-mtf-confluence-execution-001

START (mandatory — before any work):
1. Check out latest clean main (fetch origin, fast-forward local main).
2. Create branch research-campaign-021-ltf-mtf-confluence-execution-001 from that main.
3. Merge scaffold commits from research-campaign-021-ltf-mtf-confluence-scaffold-001 if not on main.
4. Run: git status --short
5. Resolve unrelated modified paths before proceeding (revert drift; do not carry financing-overlay
   timestamp noise into this sprint).

Context:
- Precommit: docs/research/CAMPAIGN_021_LTF_MTF_CONFLUENCE_PRECOMMIT.md
- Strategy: src/forex_bot/strategies/lower_timeframe_mtf_confluence_entry.py
- Config: configs/campaign_021_ltf_mtf_confluence.yaml
- Runner: scripts/run_campaign_021_ltf_mtf_confluence.py (enable train-validation; keep test blocked until gates)
- M1 corpus READY_WITH_WARNINGS; hybrid provenance: M1 M15/H1/H4 + native H4→D1AGG only
- CAMPAIGN_020 remains REJECT — do not retune C020 or rerun as rescue
- configs/approved_strategies.yaml remains approved: []
- Paper/demo/live remain blocked

Gate discipline (NON-NEGOTIABLE):
1. Train/validation ONLY first — no test window in Phase 1–2.
2. No retuning — frozen 0.1.0-c021 parameters; no sweeps; no parameter changes after seeing results.
3. No test lockbox unless BOTH train gates AND validation gates pass.
4. Backtrader parity PASS required BEFORE any test lockbox open (parity may run after train+val pass, still before test).
5. No validation rescue if train fails — if train expectancy < 0 or any train gate fails: STOP, REJECT,
   do NOT run test, do NOT cite validation uplift as reason to continue, do NOT retune or soften gates.
6. No approval under any outcome — approved_strategies.yaml stays []; max status RESEARCH_PASS /
   PROMOTION_REVIEW_REQUIRED only; paper/demo/live stay blocked.

Hard rules (data + execution):
- M15 execution; M1-derived M15/H1/H4; D1AGG native_h4_derived_d1agg only (reject m1_derived_d1agg)
- fill_timing: next_bar_open (mandatory for approval-bound metrics)
- execution_realism: conservative; evidence_use: approval_bound
- htf_align / LTF alignment; strict warmups; no incomplete H1/H4/D1AGG at decision time
- No OANDA order/trade/position mutations; no live APIs; no broker/executor changes
- Financing overlay sensitivity if average hold > 1 calendar day (document; do not claim observed financing modeled)

Execution order:
1. Preflight + config validate
2. Train evidence → evaluate train gates
3. If train FAIL → CAMPAIGN_021_GATE_DECISION.md = REJECT; CAMPAIGN_021_TEST_LOCKBOX_NOT_OPENED.md; STOP
4. If train PASS → Validation evidence → evaluate validation gates + 2× cost stress
5. If validation FAIL → REJECT; test lockbox closed; STOP
6. If train+validation PASS → Backtrader parity run
7. If parity FAIL → REJECT; test lockbox closed; STOP
8. Only if train PASS AND validation PASS AND parity PASS → open test lockbox and run test once
9. Final interpretation — still no approval

Frozen gates (see precommit):
- Train expectancy >= 0
- Validation expectancy > 0; PF >= 1.05; trades >= 150 (or justified lower)
- >= 4/7 validation pairs positive (or majority)
- 2× cost stress validation expectancy >= 0
- Beat C011 deduped null by +0.010R margin
- Financing overlay when avg hold > 1 day

Deliverables:
- CAMPAIGN_021_TRAIN_VALIDATION_RESULT.md
- CAMPAIGN_021_GATE_DECISION.md (must state train-first discipline; no validation rescue if train failed)
- CAMPAIGN_021_BACKTRADER_PARITY_RESULT.md
- CAMPAIGN_021_TEST_LOCKBOX_NOT_OPENED.md OR test result doc (only if all pre-test gates + parity pass)
- CAMPAIGN_021_FINAL_INTERPRETATION.md
- Update EVIDENCE_INDEX.md, EVIDENCE_MANIFEST.json, STRATEGY_STATUS.md

Non-goals:
- No M5 default execution in v1
- No M1-derived D1AGG
- No C020 verdict rewrite
- No adding name to approved_strategies.yaml
```

---

## Reference (outside copy block)

| doc | purpose |
|---|---|
| [`CAMPAIGN_021_LTF_MTF_CONFLUENCE_PRECOMMIT.md`](CAMPAIGN_021_LTF_MTF_CONFLUENCE_PRECOMMIT.md) | Frozen parameters and gates |
| [`CAMPAIGN_021_BACKTRADER_PARITY_DESIGN.md`](CAMPAIGN_021_BACKTRADER_PARITY_DESIGN.md) | Parity spec before test |
| [`CAMPAIGN_020_FINAL_INTERPRETATION.md`](CAMPAIGN_020_FINAL_INTERPRETATION.md) | Prior H4 MTF result (REJECT; train failed) |

Scaffold runner still blocks `train-validation` / `test` / `full` until this execution sprint enables them.
