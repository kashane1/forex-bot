# Next Real Candidate — Evidence Branch Spec (Sprint 003)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-003`
`strategy_evidence: false`

Phase 6b future-branch prompt specification for the **evidence
sprint** that will run CAMPAIGN_012 /
`regime_switcher_atr_percentile 0.1.0-c012` through the full
walk-forward + financing + risk + verifier-readiness pipeline.
**This document does not run a backtest.** It is the prompt a
future Claude Code instance can use after the scaffold sprint
([`NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md))
completes.

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
> remain REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. **Even a clean PASS from the evidence sprint
> produces `RESEARCH_PASS_UNAPPROVED` — it does NOT approve the
> candidate.** Approval requires items 5 (verifier extension) +
> 6 (human approval) of the six-evidence ladder.

## 1. Branch identity

| field | value |
|---|---|
| branch name | `research-regime-switcher-atr-percentile-walk-forward-001` |
| sprint type | **evidence** (full walk-forward + financing + risk + verifier-readiness) |
| base commit | the tip of `research-regime-switcher-atr-percentile-001` (the scaffold sprint) |
| campaign label | `CAMPAIGN_012` |
| strategy id | `regime_switcher_atr_percentile` |
| strategy version | `0.1.0-c012` |
| target deliverables | walk-forward plan + per-fold execution + verdict + financing overlay + risk diagnostics + verifier-status + evidence summary + sprint summary + status registry update |
| expected commits | 9 (Phase 0 → Phase 8 — mirrors CAMPAIGN_010 / CAMPAIGN_011 evidence sprints structurally) |

## 2. Standing safety rules (verbatim, binding)

All the standing rules from the scaffold sprint's spec §2 apply,
**plus**:

- **The frozen parameters from the scaffold pre-commit are
  immutable.** The runner asserts them; deviation aborts the
  backtest before any fold fires.
- **The walk-forward plan uses CAMPAIGN_010 / CAMPAIGN_011's
  window settings verbatim.** No tuning.
- **The gate vector is the one inherited from
  `CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` §11 (which inherits
  CAMPAIGN_010 §10).** No gate is relaxed, tightened, or
  removed.
- **The null-baseline comparison gate is binding** per
  [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
  §3 + §8. The verdict doc must include a
  **"Null-baseline comparison"** section with the binary
  "meaningful improvement over null?" verdict per metric and an
  explicit "indistinguishable from null?" classification.
- **Expected outcomes:**
  - **REJECT** (most likely; CAMPAIGN_010 already failed
    unconditional H4 momentum; the regime gate may or may not
    rescue it).
  - **RESEARCH_PASS_UNAPPROVED** (unlikely; would be the first
    evidence-passing candidate in the project's history; requires
    follow-up verifier-extension sprint + human approval before
    any paper-promotion consideration).
  - **REJECT (indistinguishable from null)** (possible; if
    CAMPAIGN_012's metrics cluster within
    ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair of CAMPAIGN_011's,
    the regime gate adds no measurable edge).
  - **BLOCKED** (only if a pipeline / data bug aborts the run).
- **If RESEARCH_PASS_UNAPPROVED, DO NOT add the candidate to
  `configs/approved_strategies.yaml`.** Trigger the
  paper-promotion-prep playbook: write verdict doc; recommend
  `infra-free-local-parity-verifier-regime-switcher-001`; do not
  enable any loop.

## 3. Pre-existing context the evidence sprint must read

Before running anything, read:

- [`docs/research/REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md)
  (the scaffold sprint's exit handoff — once written)
- [`docs/research/CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)
  (binding gate vector + frozen parameters + null-baseline
  reference)
- [`docs/research/CAMPAIGN_012_STATUS.md`](CAMPAIGN_012_STATUS.md)
- [`docs/research/CAMPAIGN_012_SMOKE_RESULT.md`](CAMPAIGN_012_SMOKE_RESULT.md)
- [`docs/research/CAMPAIGN_012_WALK_FORWARD_READINESS.md`](CAMPAIGN_012_WALK_FORWARD_READINESS.md)
- [`docs/research/CAMPAIGN_012_FINANCING_RISK_READINESS.md`](CAMPAIGN_012_FINANCING_RISK_READINESS.md)
- [`docs/research/CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md)
- [`docs/research/REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md)
- [`docs/research/NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md)
  (the binding design from this discovery sprint)
- [`docs/research/CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
  (the null-baseline comparison rules the verdict doc must
  apply)
- [`docs/research/CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md)
  (the null-baseline numbers verbatim)
- [`docs/research/CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
  (the directional-comparison-reject baseline)
- [`docs/research/REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`docs/research/STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`scripts/run_campaign_011.py`](../../scripts/run_campaign_011.py)
  (the model runner — copy structure, swap strategy class +
  `FROZEN_PARAMETERS`)
- [`scripts/build_campaign_011_financing_overlay.py`](../../scripts/build_campaign_011_financing_overlay.py)
- [`scripts/build_campaign_011_risk_diagnostics.py`](../../scripts/build_campaign_011_risk_diagnostics.py)

## 4. Phase plan (9 commits, mirroring CAMPAIGN_011's evidence sprint)

### Phase 0 — repo truth audit + sprint plan

Verify scaffold sprint's tip:

- `regime_switcher_atr_percentile.py` exists
- `RegimeSwitcherAtrPercentileStrategyConfig` in `config.py`
- ≥ 25 unit tests pass
- `configs/campaign_012_regime_switcher_atr_percentile.yaml`
  loads
- CAMPAIGN_012 pre-commit + status + smoke + 3 readiness docs
  exist
- 796 pytests pass (771 + 25 new)
- safety state unchanged

Commit `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md`.

### Phase 1 — data availability + provenance

Re-audit; commit `docs/research/CAMPAIGN_012_DATA_PROVENANCE.md`
(same hashes as CAMPAIGN_010 / 011 verbatim; no refetch).

### Phase 2 — authoritative walk-forward plan

Generate:

```bash
.venv/bin/python scripts/run_walk_forward_dry_run.py \
    --campaign-name CAMPAIGN_012 \
    --universe-start 2020-01-01 --universe-end 2026-05-20 \
    --style rolling --parameter-mode frozen \
    --train-days 540 --validation-days 180 --test-days 180 \
    --step-days 180 \
    --output backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/
```

Commit `walk_forward/plan.{json,md}` +
`docs/research/CAMPAIGN_012_WALK_FORWARD_PLAN.md`. 8 folds
expected (identical to CAMPAIGN_010 / 011).

### Phase 3 — per-fold backtest execution

Add `scripts/run_campaign_012.py` — copy of
`scripts/run_campaign_011.py` with:

- `EXPECTED_VERSION = "0.1.0-c012"`
- `EXPECTED_STRATEGY = "regime_switcher_atr_percentile"`
- `FROZEN_PARAMETERS` from `CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`
- Strategy import:
  `from forex_bot.strategies.regime_switcher_atr_percentile import RegimeSwitcherAtrPercentileStrategy`
- Gate thresholds: inherited verbatim from CAMPAIGN_010 / 011
  (`TEST_FOLD_GATES`, `AGGREGATE_GATES`)

Run:

```bash
.venv/bin/python scripts/run_campaign_012.py \
    --config configs/campaign_012_regime_switcher_atr_percentile.yaml \
    --plan backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/plan.json \
    --out backtests/CAMPAIGN_012_regime_switcher_atr_percentile/
```

Commit per-fold artifacts +
`docs/research/CAMPAIGN_012_WALK_FORWARD_EXECUTION.md`.

### Phase 4 — walk-forward report and verdict classification

Apply the inherited gate vector + the null-baseline comparison.
Classification options:

- **REJECT** (any per-fold or aggregate gate fails on a
  PnL-direction dimension)
- **REJECT (indistinguishable from null)** (metrics cluster
  within the null tolerance band)
- **RESEARCH_PASS_UNAPPROVED** (every gate passes AND meaningful
  improvement over null)
- **BLOCKED** (pipeline failure)

Commit `docs/research/CAMPAIGN_012_WALK_FORWARD_RESULT.md` with
the full gate table + per-fold metrics + per-pair aggregate +
**"Null-baseline comparison"** section.

### Phase 5 — financing overlay

Add `scripts/build_campaign_012_financing_overlay.py` (clone of
CAMPAIGN_011's). Run; commit
`backtests/.../financing/financing_run.{json,md}` +
`financing_summary.json` + `docs/research/CAMPAIGN_012_FINANCING_OVERLAY.md`.

### Phase 6 — portfolio-risk diagnostics

Add `scripts/build_campaign_012_risk_diagnostics.py` (clone of
CAMPAIGN_011's; add **regime-period clustering** reporting —
see §15 of `NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`).
Run; commit `risk/diagnostics.{json,md}` +
`docs/research/CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md`.

### Phase 7 — independent verifier status

Document the verifier capability assessment. **Verifier
extension is conditional on the verdict:**

- If REJECT (any flavour): verifier NOT extended; document gap;
  recommend `infra-free-local-parity-verifier-regime-switcher-001`
  as optional future follow-up.
- If RESEARCH_PASS_UNAPPROVED: verifier extension is **required**
  before any paper-promotion consideration; recommend the same
  follow-up sprint as mandatory next step; do NOT add the
  candidate to `configs/approved_strategies.yaml`.

Commit `docs/research/CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md`.

### Phase 8 — campaign status, evidence manifest, and final validation

Update:

- `docs/research/CAMPAIGN_012_STATUS.md` →
  `rejected` / `rejected (indistinguishable from null)` /
  `research_pass_unapproved`
- `docs/research/EVIDENCE_INDEX.md` — add CAMPAIGN_012
  walk-forward evidence sub-section
- `docs/research/EVIDENCE_MANIFEST.json` — add CAMPAIGN_012
  entry (verdict=REJECT or RESEARCH_PASS_UNAPPROVED,
  strategy_family=regime_switcher_atr_percentile,
  data_source=oanda-practice, ...)
- `docs/research/STRATEGY_STATUS.md` — add per-strategy row +
  detail subsection
- `tests/unit/test_validate_research_archive.py` if needed —
  update campaign count guard from 11 → 12

Commit `docs/research/CAMPAIGN_012_EVIDENCE_SUMMARY.md` (one-page
summary; includes null-baseline comparison verbatim) and
`docs/research/REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md`.

Run final validation suite (same as CAMPAIGN_011's Phase 8).

## 5. Non-goals (binding)

- **No paper / demo / live enablement**, ever.
- **No approval** action on `configs/approved_strategies.yaml`.
- **No parameter tuning** — runner asserts frozen values.
- **No gate relaxation.**
- **No verifier extension** in this sprint (recommended as a
  separate sprint, conditional on PASS verdict).
- **No engine / financing / risk-policy code edits.**
- **No edits to CAMPAIGN_002 / 010 / 011 artifacts.**
- **No edits to the D1AGG aggregator.**

## 6. Expected files (committed by the evidence sprint)

```
backtests/CAMPAIGN_012_regime_switcher_atr_percentile/
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
├── REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md
├── CAMPAIGN_012_DATA_PROVENANCE.md
├── CAMPAIGN_012_WALK_FORWARD_PLAN.md
├── CAMPAIGN_012_WALK_FORWARD_EXECUTION.md
├── CAMPAIGN_012_WALK_FORWARD_RESULT.md (with null-baseline comparison)
├── CAMPAIGN_012_FINANCING_OVERLAY.md
├── CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md
├── CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md
├── CAMPAIGN_012_EVIDENCE_SUMMARY.md
├── CAMPAIGN_012_STATUS.md (updated)
├── REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md
├── EVIDENCE_INDEX.md (updated)
├── EVIDENCE_MANIFEST.json (updated — new CAMPAIGN_012 entry)
└── STRATEGY_STATUS.md (updated — new row + subsection)

scripts/
├── run_campaign_012.py
├── build_campaign_012_financing_overlay.py
└── build_campaign_012_risk_diagnostics.py
```

## 7. Validation commands (run at every phase boundary)

Same as the scaffold sprint's spec §7.

## 8. Final report requirements (Phase 8's structured response)

Mirror CAMPAIGN_010 / CAMPAIGN_011's evidence sprint final-report
format exactly. Adapt campaign id and include the
**null-baseline comparison** table verbatim per
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
§8.

## 9. UNEXPECTED PASS — what to do (binding)

If the verdict is `RESEARCH_PASS_UNAPPROVED`:

1. **DO NOT** add `regime_switcher_atr_percentile` to
   `configs/approved_strategies.yaml`.
2. **DO NOT** enable any loop. Paper / demo / live remain
   blocked.
3. **DO** write the verdict doc honestly:
   - All gate-pass statements.
   - All null-baseline-comparison entries (meaningful
     improvement on every metric).
   - An explicit "next steps" section:
     `infra-free-local-parity-verifier-regime-switcher-001`
     (verifier extension; item 5 of six-evidence ladder) +
     human-approval action (item 6).
4. **DO** flag the unexpectedness — every prior candidate
   REJECTED. The verdict doc must include an audit summary
   confirming no parameter tuning, no gate relaxation, no
   seed manipulation, no leakage.
5. **DO** recommend a second independent walk-forward run
   (with the same frozen parameters) before any human approval
   review, as additional defense against pipeline bugs.

## 10. Safety state (unchanged across the evidence sprint)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (unchanged) |
| CAMPAIGN_002 / 010 / 011 | REJECT (untouched) |
| CAMPAIGN_012 | scaffold-only at sprint start; verdict at sprint end (one of REJECT / REJECT (indistinguishable from null) / RESEARCH_PASS_UNAPPROVED / BLOCKED) |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| broker / OANDA call | none |
| `.env` read | none |
| credentials printed | none |
| engine-PnL change | none |
| `src/forex_bot/financing.py` change | none |
| `src/forex_bot/backtesting/d1_aggregation.py` change | none |
| `MODELED` financing reachable | no |
| pytest baseline at start | ≥ 796 (scaffold's contribution) |
| pytest baseline at end | ≥ 796 (evidence sprint may add small validator-test count guard update) |

## 11. Cross-links

- [`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md)
- [`NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md)
- [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md)
  (the null-baseline numbers verbatim)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md)
  (the model evidence sprint to mirror exactly)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`D1_AGGREGATION_DESIGN.md`](D1_AGGREGATION_DESIGN.md)
