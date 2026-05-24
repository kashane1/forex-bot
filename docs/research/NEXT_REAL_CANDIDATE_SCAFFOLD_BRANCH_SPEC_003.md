# Next Real Candidate — Scaffold Branch Spec (Sprint 003)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-003`
`strategy_evidence: false`

Phase 6a future-branch prompt specification for the **scaffold
sprint** that will implement CAMPAIGN_012 /
`regime_switcher_atr_percentile 0.1.0-c012` (the C3 real
candidate selected in
[`NEXT_PREFERRED_REAL_CANDIDATE_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_003.md)).
**This document does not implement the candidate.** It is the
prompt a future Claude Code instance can use to run the
scaffold sprint cleanly.

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
> remain REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. **CAMPAIGN_012 cannot be approved by the
> scaffold sprint** — that requires items 5 + 6 of the
> six-evidence ladder via a future evidence sprint + verifier
> extension + human approval.

## 1. Branch identity

| field | value |
|---|---|
| branch name | `research-regime-switcher-atr-percentile-001` |
| sprint type | **scaffold** (strategy module + config + tests + smoke; no walk-forward evidence run) |
| base commit | the tip of `research-new-candidate-strategy-discovery-003` (this discovery sprint) |
| campaign label | `CAMPAIGN_012` |
| strategy id | `regime_switcher_atr_percentile` |
| strategy version | `0.1.0-c012` |
| target deliverables | strategy module + config sub-model + ≥ 25 unit tests + research config + pre-commit checklist + status doc + smoke result + readiness docs (walk-forward + financing + risk + verifier) + sprint summary |
| expected commits | 8 (Phase 0 → Phase 7) |

## 2. Standing safety rules (verbatim, binding for the scaffold sprint)

The scaffold sprint must reproduce every standing safety rule
this discovery sprint's prompt enumerated, plus:

- **Do not approve any strategy.**
- **Do not run paper-loop or demo-loop except refusal checks.**
- **Do not create or run live-loop.**
- **Do not submit, create, modify, cancel, close, or query
  broker orders.**
- **Do not use live broker credentials.**
- **Do not print credentials.**
- **Do not read `.env`.**
- **Do not fetch new data.**
- **Do not commit `.env`, SQLite stores, candle CSVs, bulky
  raw outputs, tokens, credentials, cache files, or local-only
  generated data.**
- **Do not use QuantConnect / LEAN.**
- **Do not revive or tune CAMPAIGN_002, CAMPAIGN_010, or
  CAMPAIGN_011.**
- **Do not change historical campaign verdicts.**
- **Do not present a trading recommendation.**
- **Do not claim readiness for paper / demo / live.**
- **Be explicit when something is research-only, scaffold-only,
  or blocked.**
- **Commit after each meaningful phase.**

Plus C3-specific binding rules:

- **All frozen parameters from
  [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
  §2 are fixed.** No `regime_lookback_days` sweep, no
  `regime_percentile_threshold` sweep, no
  `min_close_move_atr_fraction` sweep, no
  `trend_lookback_h4_bars` sweep. The scaffold sprint asserts
  these verbatim in the unit tests.
- **`CAMPAIGN_012` cannot enter any active loop.** Even after
  the future evidence sprint records a verdict, the scaffold
  config keeps `app.trading_enabled = false`,
  `allow_order_submission = false`, `allow_live_trading = false`.
- **The D1AGG aggregator is consumed read-only.** No edits to
  `src/forex_bot/backtesting/d1_aggregation.py`.
- **No new pip-install dependency.** The aggregator + walk-forward
  + financing + risk infrastructure is all in place.

## 3. Pre-existing context the scaffold sprint must read

Before any code, read:

- [`docs/research/NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md)
  (Phase 8 of this discovery sprint — the entry point)
- [`docs/research/NEXT_PREFERRED_REAL_CANDIDATE_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_003.md)
  (Phase 4 selection)
- [`docs/research/NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md)
  (Phase 5 binding design — R1–R8 rules + frozen parameters +
  walk-forward + financing + risk + verifier expectations)
- [`docs/research/C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
  (Phase 3 feasibility deep dive — frozen parameters; no-lookahead
  invariants; D1AGG integration pattern)
- [`docs/research/CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
  (binding null-baseline rules — the future evidence sprint
  inherits these)
- [`docs/research/CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
  (gate vector inherited verbatim by CAMPAIGN_012)
- [`docs/research/CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md)
- [`docs/research/REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md)
  (the model scaffold sprint to mirror in structure)
- [`docs/research/D1_AGGREGATION_DESIGN.md`](D1_AGGREGATION_DESIGN.md)
- [`docs/research/STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`docs/research/STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`docs/research/WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`docs/research/FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`src/forex_bot/strategies/random_entry_anchor.py`](../../src/forex_bot/strategies/random_entry_anchor.py)
  (closest existing strategy to mirror in shape)
- [`src/forex_bot/strategies/session_breakout.py`](../../src/forex_bot/strategies/session_breakout.py)
  (alternative shape reference)
- [`tests/unit/test_random_entry_anchor.py`](../../tests/unit/test_random_entry_anchor.py)
  (test pattern to mirror; ≥ 36 cases)
- [`configs/campaign_011_random_entry_anchor.yaml`](../../configs/campaign_011_random_entry_anchor.yaml)
  (config pattern to mirror)
- [`src/forex_bot/backtesting/d1_aggregation.py`](../../src/forex_bot/backtesting/d1_aggregation.py)
  (the D1AGG aggregator the strategy will consume)
- [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
  (verify `approved: []`)

## 4. Phase plan (8 commits)

### Phase 0 — repo truth audit + sprint plan

Verify:
- git branch / status / recent commits
- baseline tests pass (≥ 771)
- ruff finds only the 11 pre-existing UP042 in untouched files
- archive validator / freeze checker / secret scanner all PASS
- paper-loop / demo-loop refuse; no live-loop
- `configs/approved_strategies.yaml` reads `approved: []`
- CAMPAIGN_002 / 010 / 011 verdicts unchanged
- `src/forex_bot/backtesting/d1_aggregation.py` exists; public
  API matches §3 of Phase 3 feasibility doc

Read the binding context per §3 above.

Commit `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md`
with audit + 8-phase plan.

### Phase 1 — implementation spec

Commit `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`
elaborating
[`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md)
§§3–9 into a machine-facing rule table (R1–R8), candidate
identity, frozen parameters, no-lookahead invariants, expected
test cases. Mirrors the structure of
[`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md).

### Phase 2 — strategy scaffold

Add code:

- `src/forex_bot/strategies/regime_switcher_atr_percentile.py`
  (~250 LOC) implementing the `Strategy` protocol with R1–R8.
  Includes:
  - `_df_to_candle_list(df, instrument_name)` helper to convert
    the pandas DataFrame back to `list[Candle]` for the
    aggregator.
  - `_wilder_atr_over_d1agg(d1_candles, lookback)` helper for
    Wilder ATR-14 over the D1AGG-typed candle list.
  - `_compute_regime(...)` per
    [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
    §6 pseudocode.
- Update `src/forex_bot/strategies/__init__.py` to re-export
  `RegimeSwitcherAtrPercentileStrategy`.
- Update `src/forex_bot/config.py` to add
  `RegimeSwitcherAtrPercentileStrategyConfig` and
  `StrategyConfig.regime_switcher_atr_percentile`.

Run `python -m pytest -q` after the edits — expect 771 → still
771 (no new tests yet, no regression).

Commit the code edits.

### Phase 3 — unit tests (≥ 25 cases)

Add `tests/unit/test_regime_switcher_atr_percentile.py` per the
per-group breakdown in
[`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md)
§9:

- config / validation (≥ 6)
- regime feature happy-path (≥ 3)
- regime feature no-lookahead structural audit (≥ 4)
- D1AGG aggregator integration (≥ 2)
- strategy core (≥ 5)
- R5 minimum-move filter (≥ 2)
- no forbidden imports / usages (≥ 2)
- rejected-family contamination audit (≥ 3)
- approval / safety regression (≥ 2)

All cases pass; full repo suite goes 771 → ≥ 796.

Commit.

### Phase 4 — research config + CAMPAIGN_012 docs

Add `configs/campaign_012_regime_switcher_atr_percentile.yaml`:

- `strategy.enabled = ["regime_switcher_atr_percentile"]`
- frozen parameters per
  [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
  §2 verbatim
- `app.trading_enabled = false`, `app.allow_order_submission =
  false`, `app.allow_live_trading = false`
- 7-pair H4 universe
- `risk.max_open_positions = 1`
- `app.database_path = ./data/campaign_002.sqlite3`

Commit docs:

- `docs/research/CAMPAIGN_012_PRECOMMIT_CHECKLIST.md` with the
  hypothesis verbatim, implementation files, config files,
  frozen parameters, required local-only evaluation commands,
  required walk-forward / financing / risk artifacts, verbatim
  gate vector inherited from CAMPAIGN_010 §10, **binding
  null-baseline reference section** citing CAMPAIGN_011's eight
  aggregate metrics + the six meaningful-improvement margins
  from
  [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
  §3, and an explicit no-approval statement.
- `docs/research/CAMPAIGN_012_STATUS.md` — candidate-scaffold-only.

### Phase 5 — smoke result

Run non-evidence smokes:

- `python -m pytest tests/unit/test_regime_switcher_atr_percentile.py -q`
- config-load smoke
- walk-forward dry-run plan to `/tmp/campaign_012_smoke/`
  (8 folds expected; matches CAMPAIGN_010 / CAMPAIGN_011)

Commit `docs/research/CAMPAIGN_012_SMOKE_RESULT.md`.

### Phase 6 — walk-forward + financing + risk + verifier readiness docs

Commit (no backtest run):

- `docs/research/CAMPAIGN_012_WALK_FORWARD_READINESS.md`
- `docs/research/CAMPAIGN_012_FINANCING_RISK_READINESS.md`
- `docs/research/CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md`

### Phase 7 — sprint summary + EVIDENCE_INDEX update + final validation

Commit:

- `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md`
- Update `docs/research/EVIDENCE_INDEX.md` with a CAMPAIGN_012
  scaffold sub-section.
- (No edit to `EVIDENCE_MANIFEST.json` until the evidence sprint
  produces a verdict; the scaffold sprint defers per
  CAMPAIGN_010 / 011 convention.)
- (No edit to `STRATEGY_STATUS.md` until the evidence sprint
  records a verdict; the scaffold sprint may add a small
  annotation noting the candidate is selected and scaffolded.)

Run final validation suite (same as CAMPAIGN_011's scaffold
Phase 7).

## 5. Non-goals (binding)

- **No walk-forward backtest run.** That is the evidence
  sprint's job.
- **No financing overlay computation.** Same — evidence sprint.
- **No risk-diagnostics generation.** Same — evidence sprint.
- **No verifier extension.** Recommended only if the future
  evidence sprint produces an unexpected PASS.
- **No approval action.**
- **No paper / demo / live enablement.**
- **No engine / financing / risk-policy code edits.**
- **No edits to CAMPAIGN_002 / 010 / 011 artifacts.**
- **No edits to the D1AGG aggregator.**
- **No `regime_lookback_days` / `regime_percentile_threshold`
  / `min_close_move_atr_fraction` / `trend_lookback_h4_bars` /
  any other frozen-parameter sweeps.**

## 6. Expected files (committed by the scaffold sprint)

| file | purpose |
|---|---|
| `src/forex_bot/strategies/regime_switcher_atr_percentile.py` | new strategy module (~250 LOC) |
| `src/forex_bot/strategies/__init__.py` | re-export |
| `src/forex_bot/config.py` | new sub-model + slot + enabled-list check |
| `tests/unit/test_regime_switcher_atr_percentile.py` | ≥ 25 unit cases |
| `configs/campaign_012_regime_switcher_atr_percentile.yaml` | research candidate config |
| `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md` | Phase 0 plan |
| `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md` | Phase 1 spec |
| `docs/research/CAMPAIGN_012_PRECOMMIT_CHECKLIST.md` | Phase 4 pre-commit (includes null-baseline reference) |
| `docs/research/CAMPAIGN_012_STATUS.md` | Phase 4 status (scaffold-only) |
| `docs/research/CAMPAIGN_012_SMOKE_RESULT.md` | Phase 5 smokes |
| `docs/research/CAMPAIGN_012_WALK_FORWARD_READINESS.md` | Phase 6 readiness |
| `docs/research/CAMPAIGN_012_FINANCING_RISK_READINESS.md` | Phase 6 readiness |
| `docs/research/CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md` | Phase 6 readiness |
| `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md` | Phase 7 sprint summary |
| `docs/research/EVIDENCE_INDEX.md` | Phase 7 update — add CAMPAIGN_012 scaffold sub-section |

## 7. Validation commands (run at every phase boundary)

```bash
python -m pytest -q
ruff check src tests scripts research
python scripts/validate_research_archive.py
python scripts/check_research_freeze.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

Plus at Phase 0 and Phase 7:

```bash
python -m forex_bot.cli paper-loop -c configs/paper.yaml
python -m forex_bot.cli demo-loop -c configs/practice.yaml
python -m forex_bot.cli --help
```

## 8. Final report requirements (Phase 7's structured response)

The scaffold sprint's final response should provide the same
30-item structured report shape that CAMPAIGN_010 / 011
scaffolds used. Adapt the campaign id and recommended next
branch.

## 9. Safety state (unchanged at sprint start and end)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (unchanged) |
| CAMPAIGN_002 / 010 / 011 | REJECT (untouched) |
| CAMPAIGN_012 | scaffold-only at the close of the scaffold sprint; verdict comes from the future evidence sprint |
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
| pytest baseline at start | 771 |
| pytest baseline at end | ≥ 796 (≥ 25 new tests) |

## 10. Cross-links

- [`NEXT_PREFERRED_REAL_CANDIDATE_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_003.md)
- [`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md)
- [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md)
  (the model scaffold sprint to mirror)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`D1_AGGREGATION_DESIGN.md`](D1_AGGREGATION_DESIGN.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
