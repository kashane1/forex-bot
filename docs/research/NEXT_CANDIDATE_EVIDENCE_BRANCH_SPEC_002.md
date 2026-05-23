# Next Candidate — Evidence Branch Spec (Sprint 002)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-002`
`strategy_evidence: false`

Phase 5b future-branch prompt specification for the **evidence
sprint** that will run CAMPAIGN_011 / `random_entry_anchor
0.1.0-c011` through the full walk-forward + financing + risk +
verifier pipeline. **This document does not run a backtest.**
It is the prompt a future Claude Code instance can use after the
scaffold sprint
([`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md))
completes.

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. **CAMPAIGN_011 is a diagnostic anchor / null
> model; even the evidence sprint cannot approve it. Even an
> unexpected PASS is to be treated as a bug report against the
> pipeline, not as evidence of an edge.**

## 1. Branch identity

| field | value |
|---|---|
| branch name | `research-random-entry-diagnostic-anchor-walk-forward-001` |
| sprint type | **evidence** (full walk-forward + financing + risk + verifier-readiness) |
| base commit | the tip of `research-random-entry-diagnostic-anchor-001` (the scaffold sprint) |
| campaign label | `CAMPAIGN_011` |
| strategy id | `random_entry_anchor` |
| strategy version | `0.1.0-c011` |
| target deliverables | walk-forward plan + per-fold execution + verdict + financing overlay + risk diagnostics + verifier-status + evidence summary + sprint summary + status registry update |
| expected commits | 9 (Phase 0 → Phase 8 — mirrors CAMPAIGN_010's evidence sprint structure exactly) |

## 2. Standing safety rules (verbatim, binding)

All the standing rules from the scaffold sprint's spec §2 apply,
**plus**:

- **The seed sequence is the one committed in the scaffold
  sprint's pre-commit checklist.** No deviation, no
  re-seeding, no "pilot with different seed".
- **The walk-forward plan uses CAMPAIGN_010's window settings
  verbatim.** Any deviation would invalidate the entry-signal
  comparison.
- **The gate vector is the one inherited from
  `CAMPAIGN_010_PRECOMMIT_CHECKLIST.md` §10.** No gate is
  relaxed, no gate is tightened, no gate is removed.
- **Expected outcome: REJECT.** The evidence sprint is
  *successful* if it produces a clean REJECT verdict with
  fold_pass_rate = 0 / 8 and aggregate expectancy R near
  CAMPAIGN_005's −0.095 R baseline (deepened by the longer
  6-bar hold and per-fold financing overlay). A REJECT is the
  expected diagnostic output; the sprint *records* it cleanly.
- **If CAMPAIGN_011 unexpectedly PASSES, do not promote it.**
  Trigger the unexpected-PASS investigation playbook in
  [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
  §14 — confirm no seed-input leakage, confirm fold-boundary
  rules pass, confirm structural audits pass, confirm
  long-short and entry-rate distributions are sound. Treat as
  a bug report against the pipeline; escalate to a separate
  investigation sprint; do not add to
  `configs/approved_strategies.yaml` under any circumstance.

## 3. Pre-existing context the evidence sprint must read

Before running anything, read:

- [`docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md)
  (the scaffold sprint's exit handoff — once written)
- [`docs/research/CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
  (binding gate vector + frozen parameters)
- [`docs/research/CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
- [`docs/research/CAMPAIGN_011_SMOKE_RESULT.md`](CAMPAIGN_011_SMOKE_RESULT.md)
- [`docs/research/CAMPAIGN_011_WALK_FORWARD_READINESS.md`](CAMPAIGN_011_WALK_FORWARD_READINESS.md)
- [`docs/research/CAMPAIGN_011_FINANCING_RISK_READINESS.md`](CAMPAIGN_011_FINANCING_RISK_READINESS.md)
- [`docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md)
- [`docs/research/NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
  (the binding design from this discovery sprint)
- [`docs/research/CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
  (the comparison baseline — CAMPAIGN_011's gate vector and
  fold structure are identical)
- [`docs/research/CAMPAIGN_010_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_010_WALK_FORWARD_EXECUTION.md)
- [`docs/research/CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md)
- [`docs/research/CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`docs/research/REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`docs/research/STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`scripts/run_campaign_010.py`](../../scripts/run_campaign_010.py)
  (the model runner — copy structure, swap strategy class)
- [`scripts/build_campaign_010_financing_overlay.py`](../../scripts/build_campaign_010_financing_overlay.py)
  (the model financing-overlay script)
- [`scripts/build_campaign_010_risk_diagnostics.py`](../../scripts/build_campaign_010_risk_diagnostics.py)
  (the model risk-diagnostics script)

## 4. Phase plan (9 commits, mirroring CAMPAIGN_010's evidence sprint)

### Phase 0 — repo truth audit + sprint plan

Verify scaffold sprint's tip:
- `random_entry_anchor.py` exists
- `RandomEntryAnchorStrategyConfig` in config.py
- ≥ 20 unit tests pass
- `configs/campaign_011_random_entry_anchor.yaml` loads
- Pre-commit checklist exists
- Walk-forward + financing + risk readiness docs exist
- Smoke result exists
- 735 + 20 = 755 tests pass

Verify safety:
- `configs/approved_strategies.yaml` reads `approved: []`
- CAMPAIGN_002 / CAMPAIGN_010 unchanged
- paper-loop / demo-loop refuse; no live-loop

Verify data:
- `data/campaign_002.sqlite3` symlink present and readable
- (Or recreate the symlink if absent — pointing at
  `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3`)
- 7 pairs, ~9,931 candles each, source `oanda-practice`

Commit `docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md`
with audit + 9-phase pipeline plan.

### Phase 1 — data availability + provenance

Re-audit and commit
`docs/research/CAMPAIGN_011_DATA_PROVENANCE.md` — same 7-pair
counts, first/last timestamps, recorded hash prefixes, source
label. Do not refetch.

### Phase 2 — authoritative walk-forward plan

Generate:
```bash
.venv/bin/python scripts/run_walk_forward_dry_run.py \
    --campaign-name CAMPAIGN_011 \
    --universe-start 2020-01-01 --universe-end 2026-05-20 \
    --style rolling --parameter-mode frozen \
    --train-days 540 --validation-days 180 --test-days 180 \
    --step-days 180 \
    --output backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/
```

Commit `walk_forward/plan.{json,md}` +
`docs/research/CAMPAIGN_011_WALK_FORWARD_PLAN.md`. 8 folds
expected (identical to CAMPAIGN_010).

### Phase 3 — per-fold backtest execution

Add `scripts/run_campaign_011.py` — copy of
`scripts/run_campaign_010.py` with:
- `EXPECTED_VERSION = "0.1.0-c011"`
- `EXPECTED_STRATEGY = "random_entry_anchor"`
- `FROZEN_PARAMETERS` from
  `CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` §5
- Strategy import: `from
  forex_bot.strategies.random_entry_anchor import
  RandomEntryAnchorStrategy`
- Gate thresholds: inherited verbatim from CAMPAIGN_010 (`TEST_FOLD_GATES`,
  `AGGREGATE_GATES`)

Run:
```bash
.venv/bin/python scripts/run_campaign_011.py \
    --config configs/campaign_011_random_entry_anchor.yaml \
    --plan backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json \
    --out backtests/CAMPAIGN_011_random_entry_anchor/
```

Commit per-fold artifacts (mirrors CAMPAIGN_010's commit
layout):
- `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_NN/fold_NN_<PAIR>_summary.json`
- `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_NN/fold_NN_<PAIR>_trades.csv`
- `walk_forward/results.json`, `walk_forward/results.md`,
  `walk_forward/fold_detail.json`
- `docs/research/CAMPAIGN_011_WALK_FORWARD_EXECUTION.md`

### Phase 4 — walk-forward report and verdict classification

Apply the inherited gate vector. Expected verdict: **REJECT**.

Commit `docs/research/CAMPAIGN_011_WALK_FORWARD_RESULT.md` with
the full gate table + per-fold metrics + per-pair aggregate.

### Phase 5 — financing overlay

Add `scripts/build_campaign_011_financing_overlay.py` — copy of
`scripts/build_campaign_010_financing_overlay.py` with the
output directory updated.

Run:
```bash
.venv/bin/python scripts/build_campaign_011_financing_overlay.py \
    --campaign-dir backtests/CAMPAIGN_011_random_entry_anchor/
```

Commit
`backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.{json,md}`,
`financing_summary.json`, and
`docs/research/CAMPAIGN_011_FINANCING_OVERLAY.md`.

### Phase 6 — portfolio-risk diagnostics

Add `scripts/build_campaign_011_risk_diagnostics.py` — copy of
`scripts/build_campaign_010_risk_diagnostics.py` with the
output directory + the diagnostic's "expected uniform session
distribution" comparison (random entry should produce a uniform
hour-of-day distribution, contrasting with CAMPAIGN_010's
100 % London-window concentration).

Run + commit
`backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.{json,md}`
and `docs/research/CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`.

### Phase 7 — independent verifier readiness

Document the verifier capability assessment. **Verifier was not
extended for CAMPAIGN_011 in this sprint** — extension is a
recommended follow-up (`infra-free-local-parity-verifier-random-entry-001`).

Commit
`docs/research/CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`
noting that item 5 of the six-evidence ladder is not binding
for a null model that cannot be paper-promoted.

### Phase 8 — campaign status, evidence manifest, and final validation

Update:
- `docs/research/CAMPAIGN_011_STATUS.md` →
  `rejected (null model — diagnostic anchor)`
- `docs/research/EVIDENCE_INDEX.md` — add CAMPAIGN_011
  walk-forward evidence sub-section
- `docs/research/EVIDENCE_MANIFEST.json` — add CAMPAIGN_011
  entry (verdict=REJECT, strategy_family=random_entry_anchor,
  data_source=oanda-practice, ...)
- `docs/research/STRATEGY_STATUS.md` — add per-strategy row +
  detail subsection for `random_entry_anchor 0.1.0-c011` as
  `rejected (null model anchor)`
- `tests/unit/test_validate_research_archive.py` if needed —
  update campaign count guard from 10 → 11

Commit
`docs/research/CAMPAIGN_011_EVIDENCE_SUMMARY.md` (one-page
summary) and
`docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md`.

Run final validation suite (same as CAMPAIGN_010's Phase 8).

## 5. Non-goals (binding)

- **No paper / demo / live enablement**, ever.
- **No approval** action on
  `configs/approved_strategies.yaml`.
- **No parameter tuning** — the runner asserts the loaded YAML
  matches the pre-commit verbatim.
- **No seed change** between pilot runs and the committed
  evidence run.
- **No gate relaxation** — the gates are CAMPAIGN_010's,
  verbatim.
- **No verifier extension** in this sprint (recommended as a
  separate sprint after this one).
- **No engine / financing / risk-policy code edits.**
- **No edits to CAMPAIGN_002 / CAMPAIGN_010 artifacts.**

## 6. Expected files (committed by the evidence sprint)

```
backtests/CAMPAIGN_011_random_entry_anchor/
├── walk_forward/
│   ├── plan.json
│   ├── plan.md
│   ├── results.json
│   ├── results.md
│   └── fold_detail.json
├── folds/
│   └── fold_NN/                    (8 folds × 7 pairs × 2 files)
│       ├── fold_NN_<PAIR>_summary.json
│       └── fold_NN_<PAIR>_trades.csv
├── financing/
│   ├── financing_run.json
│   ├── financing_run.md
│   └── financing_summary.json
└── risk/
    ├── diagnostics.json
    └── diagnostics.md

docs/research/
├── RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md
├── CAMPAIGN_011_DATA_PROVENANCE.md
├── CAMPAIGN_011_WALK_FORWARD_PLAN.md
├── CAMPAIGN_011_WALK_FORWARD_EXECUTION.md
├── CAMPAIGN_011_WALK_FORWARD_RESULT.md
├── CAMPAIGN_011_FINANCING_OVERLAY.md
├── CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md
├── CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md
├── CAMPAIGN_011_EVIDENCE_SUMMARY.md
├── CAMPAIGN_011_STATUS.md (updated)
├── RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md
├── EVIDENCE_INDEX.md (updated)
├── EVIDENCE_MANIFEST.json (updated — new CAMPAIGN_011 entry)
└── STRATEGY_STATUS.md (updated — new row + subsection)

scripts/
├── run_campaign_011.py
├── build_campaign_011_financing_overlay.py
└── build_campaign_011_risk_diagnostics.py
```

## 7. Validation commands (run at every phase boundary)

Same as the scaffold sprint's spec §7.

## 8. Final report requirements (Phase 8's 35-item structured response)

Mirror CAMPAIGN_010's evidence sprint final-report format
exactly. Required items include:

1. Branch name.
2. Commit hashes by phase.
3. Files changed by phase.
4. Tests + validation commands.
5. Latest full test count (≥ 755 → ≥ 755; may include 0 new
   tests since this is an evidence sprint).
6. Ruff status.
7. Data provenance status.
8. Whether candle data was existing or regenerated.
9. Whether credentials were used.
10. Whether credentials were printed.
11. Whether broker account/order/trade/position/transaction
    endpoint was queried.
12. Walk-forward plan status (8 folds expected).
13. Fold count + date ranges.
14. Per-fold execution status.
15. Aggregate walk-forward metrics.
16. Gate verdict table.
17. Final CAMPAIGN_011 research status (expected REJECT).
18. Financing overlay status (ESTIMATED + conservative stress;
    MODELED refused).
19. Portfolio-risk diagnostics status.
20. Independent verifier status (NOT RUN — capability gap).
21. Implementation bugs fixed (expected none).
22. Data issues found (expected none).
23. Confirmation no parameter tuning.
24. Confirmation no strategy approved.
25. Confirmation configs/approved_strategies.yaml remains approved: [].
26. Confirmation CAMPAIGN_002 / CAMPAIGN_010 remain REJECT.
27. Confirmation CAMPAIGN_011 not approved.
28. Confirmation paper/demo/live remain blocked.
29. Confirmation no orders submitted/queried.
30. Confirmation no QuantConnect/LEAN.
31. Research freeze/archive status.
32. Local files created but not committed.
33. Remaining blockers (verifier extension; future C3 / C2 / C4
    candidate ordering).
34. Recommended next branch
    (`research-new-candidate-strategy-discovery-003` to pick
    C3 next).
35. Exact files to review first.

## 9. Expected outcome — REJECT (and what to do)

The expected verdict under the inherited CAMPAIGN_010 gate
vector is **REJECT**. Specifically:

| metric | expected value (random) | gate threshold | expected gate result |
|---|---|---|---|
| `fold_pass_rate` | 0 / 8 (no fold passes ≥ 0.05 R expectancy) | 100 % | **FAIL** |
| `aggregate_expectancy_R` | ≈ −0.05 to −0.15 R (random baseline) | ≥ 0.05 R | **FAIL** |
| `aggregate_profit_factor` | ≈ 0.6 to 0.9 | ≥ 1.10 | **FAIL** |
| `aggregate_return_pct` | ≈ −30 % to −50 % over 4 years | (no gate) | informational |
| `pairs_positive` | 0–2 / 7 | ≥ 4 / 7 | **FAIL** |
| `single_pair_dominance` | ≤ 25 % (uniform target ≈ 14 %) | ≤ 40 % | PASS |
| `single_fold_dominance` | ≤ 25 % (uniform target ≈ 13 %) | ≤ 60 % | PASS |
| `financing.modeled_refused` | PASS | PASS | PASS |
| `financing.missing_rate_event_count` | 0 | 0 | PASS |
| `financing.conservative_stress_run_does_not_flip_verdict` | vacuously PASS (pre-financing already REJECT) | PASS | PASS |

The expected REJECT is the **success outcome of the sprint** —
the falsifiability anchor is now established, and any future
candidate's per-fold + aggregate metrics can be compared to
CAMPAIGN_011's.

## 10. Expected outcome — UNEXPECTED PASS (and what NOT to do)

If the gates unexpectedly pass:

- **DO NOT** add `random_entry_anchor` to
  `configs/approved_strategies.yaml`.
- **DO NOT** treat the result as evidence of an edge.
- **DO** trigger the unexpected-PASS investigation playbook
  (§14 of
  [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)):
  1. Confirm `seed_input` does not include any bar-`t` data.
  2. Confirm fold-boundary leakage rules pass.
  3. Confirm structural audits pass.
  4. Confirm the entry-probability rate matches expectation.
  5. Confirm the long-short distribution matches 50/50.
- **DO** escalate to a separate investigation sprint
  (`infra-pipeline-validation-investigation-001`).
- **DO** commit the result as REJECT in the campaign status
  pending investigation (an unexpected PASS that turns out to
  be a pipeline bug is *not* a research-pass; it is a bug
  report).

## 11. Safety state (unchanged across the evidence sprint)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (unchanged) |
| CAMPAIGN_002 / CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | scaffold-only at sprint start; **REJECT (expected)** at sprint end |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| broker / OANDA call | none (existing symlinked data store) |
| `.env` read | none |
| credentials printed | none |
| engine-PnL change | none |
| `src/forex_bot/financing.py` change | none |
| `MODELED` financing reachable | no |
| pytest baseline at start | ≥ 755 (scaffold's contribution) |
| pytest baseline at end | ≥ 755 (evidence sprint may add small validator-test count guard update) |

## 12. Cross-links

- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
  (the structural template + comparison baseline)
- [`CAMPAIGN_010_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_010_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md)
- [`CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md)
  (the model evidence sprint to mirror exactly)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md`](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md)
  (the prior random-entry single-window benchmark that
  CAMPAIGN_011 strictly improves on)
