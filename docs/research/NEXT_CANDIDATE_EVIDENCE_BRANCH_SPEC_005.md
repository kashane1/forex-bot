# Next Candidate Evidence Branch Spec (Phase 8b)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-005`
`strategy_evidence: false`

Phase 8b binding spec for the **future evidence sprint** that runs
the full 6-evidence-ladder evaluation of C7 /
`calendar_event_window_anomaly 0.1.0-c014` (CAMPAIGN_014). This doc
is a binding *prompt template* for the next Claude Code instance to
begin from, after the scaffold sprint completes.

> No strategy approved. `configs/approved_strategies.yaml` remains
> `approved: []`. **The future evidence sprint cannot approve any
> strategy.** Even a verdict of `RESEARCH_PASS_UNAPPROVED` is not
> approval — only a deliberate human edit per
> `STRATEGY_APPROVAL_PROCESS.md` can promote a strategy.

## 1. Future branch identity

| field | value |
|---|---|
| **branch name** | **`research-calendar-event-window-anomaly-walk-forward-001`** |
| base commit | (latest of `research-calendar-event-window-anomaly-001` scaffold sprint) |
| type | evidence sprint (walk-forward + financing + risk + verifier-readiness) |
| binding design | [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md) |
| sibling reference | `research-cross-pair-currency-strength-rotation-walk-forward-001` (CAMPAIGN_013 evidence) + `research-regime-switcher-atr-percentile-walk-forward-001` (CAMPAIGN_012 evidence) |
| binding pre-commit | `docs/research/CAMPAIGN_014_PRECOMMIT_CHECKLIST.md` (from scaffold sprint Phase 4) — **immutable** for this sprint |

## 2. Phase outline (10 phases; mirrors CAMPAIGN_013 evidence sprint)

| phase | output | scope |
|---|---|---|
| 0 | `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md` | repo truth audit + 10-phase evidence-sprint plan |
| 1 | `docs/research/CAMPAIGN_014_DATA_PROVENANCE.md` | data availability + provenance (matches CAMPAIGN_010 / 011 / 012 / 013 verbatim for the 7-pair H4 store; adds an event-calendar fixture provenance subsection referencing the scaffold sprint's `EVENT_CALENDAR_FIXTURE_PROVENANCE.md`) |
| 2 | `docs/research/CAMPAIGN_014_WALK_FORWARD_PLAN.md` | authoritative walk-forward plan: 8 folds rolling/frozen 540/180/180/180 days; inherited per-fold + aggregate gates; new turnover-budget gate (REJECT if > 800 trades over 4y); new signal-density gate (REJECT if > 1,500 signals); event-fixture coverage contract |
| 3 | `scripts/run_campaign_014.py` + `docs/research/CAMPAIGN_014_WALK_FORWARD_EXECUTION.md` | per-fold runner: loads per-pair strategy config; injects event-fixture; asserts no-lookahead invariants; emits per-fold metrics + signal density + event-fixture coverage diagnostics |
| 4 | `backtests/CAMPAIGN_014_calendar_event_window_anomaly/` (gitignored bulky outputs; **only the per-fold summary JSONs and the aggregate report are committed**) | execute per-fold backtests; output CSV trades, JSON summaries, aggregate report |
| 5 | `docs/research/CAMPAIGN_014_WALK_FORWARD_RESULT.md` | formal verdict: aggregate gate table; null-baseline comparison (CAMPAIGN_011 binding); turnover-budget verification; event-fixture coverage report; classification (REJECT / REJECT_INDISTINGUISHABLE_FROM_NULL / RESEARCH_PASS_UNAPPROVED / BLOCKED) |
| 6 | `scripts/build_campaign_014_financing_overlay.py` + `docs/research/CAMPAIGN_014_FINANCING_OVERLAY.md` | ESTIMATED + conservative-stress financing overlay; MODELED refused; aggregate financing impact; per-pair sensitivity; flip events |
| 7 | `scripts/build_campaign_014_risk_diagnostics.py` + `docs/research/CAMPAIGN_014_PORTFOLIO_RISK_DIAGNOSTICS.md` | standard risk diagnostics + C7-specific (event-class clustering; per-event-class per-pair sensitivity; pre-event vs post-event direction breakdown; entry-window concentration) |
| 8 | `docs/research/CAMPAIGN_014_INDEPENDENT_VERIFIER_STATUS.md` | verifier status: capability-locked to CAMPAIGN_002; not required for REJECT; deferred for PASS unless a deliberate authorization runs `infra-free-local-parity-verifier-calendar-event-window-anomaly-001` |
| 9 | `docs/research/CAMPAIGN_014_EVIDENCE_SUMMARY.md` + `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_SUMMARY.md` + EDIT `docs/research/CAMPAIGN_014_STATUS.md` (scaffold-only → final verdict) + EDIT `docs/research/EVIDENCE_INDEX.md` + EDIT `docs/research/EVIDENCE_MANIFEST.json` (CAMPAIGN_014 entry; 13 → 14 campaigns) + EDIT `docs/research/STRATEGY_STATUS.md` (annotate CAMPAIGN_014 outcome) + EDIT `tests/unit/test_validate_research_archive.py` (campaign-count assertion 13 → 14) | one-page evidence summary + sprint summary + status update + manifest update + final validation |

## 3. Expected files

**NEW source files:**

- `scripts/run_campaign_014.py` (~400 LOC; per-pair runner with event-fixture injection; mirrors `run_campaign_013.py` minus the cross-pair runner contract)
- `scripts/build_campaign_014_financing_overlay.py` (~250 LOC; mirrors `build_campaign_013_financing_overlay.py` verbatim with campaign-id swap)
- `scripts/build_campaign_014_risk_diagnostics.py` (~400 LOC; mirrors `build_campaign_013_risk_diagnostics.py` minus cross-pair sections, adds C7-specific event-class clustering + per-event-class per-pair sensitivity + pre-event vs post-event direction breakdown + entry-window concentration)

**NEW docs:**

- `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md` (Phase 0)
- `docs/research/CAMPAIGN_014_DATA_PROVENANCE.md` (Phase 1)
- `docs/research/CAMPAIGN_014_WALK_FORWARD_PLAN.md` (Phase 2)
- `docs/research/CAMPAIGN_014_WALK_FORWARD_EXECUTION.md` (Phase 3)
- `docs/research/CAMPAIGN_014_WALK_FORWARD_RESULT.md` (Phase 5)
- `docs/research/CAMPAIGN_014_FINANCING_OVERLAY.md` (Phase 6)
- `docs/research/CAMPAIGN_014_PORTFOLIO_RISK_DIAGNOSTICS.md` (Phase 7)
- `docs/research/CAMPAIGN_014_INDEPENDENT_VERIFIER_STATUS.md` (Phase 8)
- `docs/research/CAMPAIGN_014_EVIDENCE_SUMMARY.md` (Phase 9)
- `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_SUMMARY.md` (Phase 9)

**EDIT docs:**

- `docs/research/CAMPAIGN_014_STATUS.md` (scaffold-only → final verdict)
- `docs/research/EVIDENCE_INDEX.md` (add CAMPAIGN_014 evidence sub-section)
- `docs/research/EVIDENCE_MANIFEST.json` (add CAMPAIGN_014 entry; 13 → 14 campaigns)
- `docs/research/STRATEGY_STATUS.md` (annotate CAMPAIGN_014 outcome)
- `tests/unit/test_validate_research_archive.py` (campaign-count assertion 13 → 14; `_CAMPAIGN_IDS` set)

## 4. Validation commands (per-phase + at sprint close)

```bash
python -m pytest -q
ruff check src tests scripts research
python scripts/validate_research_archive.py
python scripts/check_research_freeze.py
python scripts/scan_artifacts_for_secrets.py
python -m forex_bot.cli paper-loop -c configs/paper.yaml      # expect refusal
python -m forex_bot.cli demo-loop -c configs/practice.yaml    # expect refusal
python -m forex_bot.cli --help                                 # expect no live-loop
git status --short
```

Test-count target: **(scaffold-sprint baseline) → +1** for the
`test_validate_research_archive.py` campaign-count assertion bump
(13 → 14). The campaign-count assertion is a single test rename +
constant update; no new test cases. Total pytest count after evidence
sprint should be the scaffold-sprint count (e.g. 905 from scaffold)
exactly preserved if the test rename is the only change.

Ruff target: **3 pre-existing in `research/lean_parity/algorithms/`
maintained** (untouched LEAN-parity archive); the new runner +
financing-overlay + risk-diagnostics scripts must clear ruff with
zero new findings.

## 5. Safety rules (binding for the evidence sprint)

- **NO broker / account / order / trade / position / transaction
  endpoint queries.** All data is local (the H4 SQLite store + the
  committed event-calendar fixture).
- **NO `.env` read.** No credential print.
- **NO `live-loop` command creation.**
- **NO `configs/approved_strategies.yaml` mutation** (must remain
  `approved: []`).
- **NO enabling** `calendar_event_window_anomaly` in
  `configs/paper.yaml` or `configs/practice.yaml`.
- **NO QuantConnect / LEAN.**
- **NO parameter tuning.** The scaffold sprint's pre-commit checklist
  is **immutable** for this sprint; the runner's `_assert_frozen()`
  pattern (from CAMPAIGN_010 / 011 / 012 / 013 runners) blocks
  any parameter drift.
- **NO `max_open_positions` relaxation** (per Phase 7 design §10).
- **NO MODELED financing** (per Phase 7 design §19; MODELED refused
  at 4 layers; the overlay script aborts if treatment is MODELED).
- **NO modifying any rejected-family strategy module** or any
  CAMPAIGN_002 / 010 / 011 / 012 / 013 doc.
- **NO modifying the cross-pair runner integration contract** added
  in CAMPAIGN_013's evidence sprint (CAMPAIGN_014 does not use it).
- **NO modifying the event-fixture** committed in the scaffold
  sprint. If the fixture has a bug, fix it in a separate sprint with
  human authorization; do not modify mid-evidence.

## 6. Non-goals (binding)

- No new strategy module (only the scaffold sprint added the
  strategy; evidence sprint may not edit it).
- No new strategy config schema (scaffold sprint set this).
- No new unit tests beyond the campaign-count assertion bump.
- No new fixture (scaffold sprint set this).
- No verifier extension run (deferred unless RESEARCH_PASS_UNAPPROVED
  is the verdict, and even then it's a separate sprint).
- No MODELED financing capture (separate sprint; requires human
  authorization).

## 7. Final report requirements (Phase 9 of evidence sprint)

The evidence sprint's Phase 9 summary doc must report:

1. Branch name (`research-calendar-event-window-anomaly-walk-forward-001`).
2. Commit hashes by phase (10 hashes).
3. Files changed by phase.
4. Tests / validation commands run.
5. Latest full test count.
6. Ruff status.
7. **Per-fold metrics table** (8 folds; trades, expectancy R, return %, PF, pairs+ count, single-pair dominance).
8. **Aggregate metrics table** (8 inherited gates + 1 turnover budget + 1 signal density + 1 event-fixture coverage = 11 gates).
9. **Null-baseline comparison table** (vs CAMPAIGN_011).
10. **Per-event-class metrics table** (NFP / FOMC / ECB / BoJ / BoE).
11. **Per-pair metrics table** (7 pairs).
12. **Financing overlay summary** (cashflow_home_total + stress; per-pair sensitivity; flip events).
13. **Risk diagnostics summary** (event-class clustering; per-event-class per-pair; pre-event vs post-event direction; entry-window concentration).
14. **Verifier status** (capability-locked; deferred or required).
15. **Verdict classification** (REJECT / REJECT_INDISTINGUISHABLE_FROM_NULL / RESEARCH_PASS_UNAPPROVED / BLOCKED).
16. Confirmation CAMPAIGN_002 / 010 / 011 / 012 / 013 remain REJECT.
17. Confirmation no broker / account / order endpoint was queried.
18. Confirmation `configs/approved_strategies.yaml` remains `approved: []`.
19. Confirmation paper / demo / live remain blocked.
20. Confirmation no QuantConnect / LEAN was used.
21. Confirmation no parameter tuning, no `max_open_positions` relaxation, no risk-limit relaxation.
22. Recommended next sprint (one of: `research-new-candidate-strategy-discovery-006` if REJECT; `infra-free-local-parity-verifier-calendar-event-window-anomaly-001` if RESEARCH_PASS_UNAPPROVED; `research-financing-modeled-capture-credentialed-001` if BLOCKED-by-financing; etc.).

## 8. Approval boundary (binding)

The evidence sprint **cannot** approve `calendar_event_window_anomaly`
for paper / demo / live trading. The verdict classifications mean:

- **REJECT / REJECT_INDISTINGUISHABLE_FROM_NULL / BLOCKED**: the
  strategy is **not** evaluable for paper-promotion; binding cooldown
  applies per the rejection-closeout pattern established by
  CAMPAIGN_010 / 012 / 013.
- **RESEARCH_PASS_UNAPPROVED**: the strategy has cleared the
  walk-forward + financing + risk evidence ladders but still requires
  (a) independent-verifier-extension corroboration via a separate
  `infra-free-local-parity-verifier-calendar-event-window-anomaly-001`
  sprint AND (b) a deliberate human approval action per
  `STRATEGY_APPROVAL_PROCESS.md`. The evidence sprint's verdict
  alone does not authorize either.

**paper / demo / live remain blocked throughout the evidence sprint
and after it completes.**

## 9. Turnover / cost guardrails (binding evaluation rules)

The evidence sprint's Phase 5 verdict doc MUST evaluate and report:

- **Turnover budget gate**: REJECT if `total_trades > 800` over 4-year walk-forward.
- **Signal density gate**: REJECT if `total_signals > 1,500` over 8 folds.
- **Cost section reconciliation**: report `actual_avg_spread_bp_per_trade`, `actual_avg_slippage_bp_per_trade`, `actual_avg_financing_bp_per_trade`, `actual_avg_gross_expectancy_R_per_trade`, `actual_avg_net_expectancy_R_per_trade`, and compare to the pre-commit's 7 bp gross / 5 bp net hypothesis.
- **Event-fixture coverage contract**: report per-fold `fixture_covers_test_window` boolean; if any fold is FALSE → verdict is BLOCKED regardless of metrics.

## 10. Null-baseline comparison (binding)

Per `CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md` §8 + §9 + Phase 7
design §17, the Phase 5 verdict doc MUST include a "Null-baseline
comparison" section with:

- Side-by-side aggregate table: CAMPAIGN_014 vs CAMPAIGN_011.
- Side-by-side per-pair expectancy table.
- Binary "meaningful improvement over null?" per metric.
- Explicit indistinguishability-band check.

## 11. Cross-campaign comparison (binding)

The Phase 5 verdict doc MUST include a "Comparison to prior REJECT
campaigns" section mirroring CAMPAIGN_013's `WALK_FORWARD_RESULT.md`
§ "Comparison to prior REJECT campaigns" — a row per CAMPAIGN_002 /
010 / 011 / 012 / 013 / 014.

## 12. Safety state (must remain) after evidence sprint

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| CAMPAIGN_014 | final verdict per evidence sprint (REJECT or RESEARCH_PASS_UNAPPROVED or BLOCKED; never APPROVED) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| pytest baseline | (scaffold baseline) — preserved |
| ruff baseline | 3 pre-existing (unchanged) |
| broker call this sprint | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| parameter "tweak" or "rescue" | **none** (frozen parameters intact) |
| `max_open_positions` relaxation | **none** |

## 13. Cross-links

- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md) (binding design)
- [`NEXT_PREFERRED_DIRECTION_005.md`](NEXT_PREFERRED_DIRECTION_005.md) (C7 selection)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md) (paired scaffold-branch spec)
- [`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) (binding turnover budget + REJECT triggers)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) (binding patterns)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md) (sibling template; CAMPAIGN_013 evidence)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
