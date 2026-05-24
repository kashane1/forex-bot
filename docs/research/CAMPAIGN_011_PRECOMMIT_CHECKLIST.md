# CAMPAIGN_011 — Pre-Commit Checklist

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-001`
`strategy_evidence: false`

Pre-commit / evaluation checklist for **CAMPAIGN_011** /
`random_entry_anchor 0.1.0-c011` — the **C5 diagnostic anchor /
null model**. This document is the gate any future evaluation
sprint must satisfy before treating its outputs as evidence.
**Loading this checklist, the config YAML, or running the
strategy in unit / smoke mode does not approve the candidate.
The candidate cannot be approved by design.**

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked. **CAMPAIGN_011
> is a null model — cannot be added to `configs/approved_strategies.yaml`
> under any circumstance.**

## 1. Candidate identity

| field | value |
|---|---|
| campaign label | `CAMPAIGN_011` |
| strategy name | `random_entry_anchor` |
| version | `0.1.0-c011` |
| role | **diagnostic anchor / null model** (NOT a paper candidate) |
| sprint that scaffolded | `research-random-entry-diagnostic-anchor-001` |
| design source | [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md) |
| implementation spec | [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md) |
| selection rationale | [`NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md) |
| approval path | **none — null model by design** |

## 2. Null-model hypothesis (verbatim, frozen)

> A deterministic-seed coin-flip H4 entry on the 7-pair OANDA
> practice universe, executed under the same RiskEngine gates
> and the same ATR-stop / time-stop exit logic as CAMPAIGN_010,
> has *no edge by construction*. Its per-fold and aggregate
> expectancy under rolling walk-forward will set the
> falsifiability bar that every subsequent candidate must beat
> by a meaningful margin to count as evidence of an edge. The
> headline gate vector is inherited verbatim from
> [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
> §10 so the comparison is on the entry signal alone, not on a
> shifted goalpost.

## 3. Implementation files (committed by this sprint)

| file | role |
|---|---|
| [`src/forex_bot/strategies/random_entry_anchor.py`](../../src/forex_bot/strategies/random_entry_anchor.py) | strategy module implementing the `Strategy` protocol; emits `Signal | None` per H4 bar; no broker / execution / loops imports; no `random` / `numpy` / built-in `hash()` |
| [`src/forex_bot/strategies/__init__.py`](../../src/forex_bot/strategies/__init__.py) | re-exports `RandomEntryAnchorStrategy` |
| [`src/forex_bot/config.py`](../../src/forex_bot/config.py) | new `RandomEntryAnchorStrategyConfig` sub-model + `StrategyConfig.random_entry_anchor` slot + `@model_validator` enforcing the frozen-parameter validity ranges |
| [`tests/unit/test_random_entry_anchor.py`](../../tests/unit/test_random_entry_anchor.py) | 36 unit + structural-audit cases (Phase 3) |

## 4. Config files (committed by this sprint)

| file | role |
|---|---|
| [`configs/campaign_011_random_entry_anchor.yaml`](../../configs/campaign_011_random_entry_anchor.yaml) | research candidate config; loads via `load_settings(...)`; `app.trading_enabled=false`, `app.allow_order_submission=false`, `app.allow_live_trading=false`; 7-pair H4 universe; data reused from `data/campaign_002.sqlite3` (gitignored symlink, same as CAMPAIGN_010) |
| **NOT TOUCHED** [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml) | remains `approved: []`; CAMPAIGN_011 is **deliberately absent** and **structurally ineligible** for this registry |

## 5. Frozen parameters (verbatim from the spec)

| parameter | value |
|---|---|
| `version` | `0.1.0-c011` |
| `timeframe` | `H4` |
| `master_seed` | `20260523` |
| `entry_probability_per_bar` | `0.05` |
| `atr_lookback` | `14` |
| `atr_stop_multiple` | `2.0` |
| `trailing_stop_atr_multiple` | `null` |
| `max_bars_in_trade` | `6` |
| `min_atr_pips` | `{}` |
| `risk.risk_per_trade_pct` | `0.25` |
| `risk.max_positions_per_instrument` | `1` |

**Any change to any of these parameters constitutes a NEW
candidate** that requires its own discovery + design cycle.

## 6. No seed optimization rule (binding)

The `master_seed = 20260523` is **fixed in this pre-commit**
before any unit test runs and before any backtest fires. Future
sprints **must not**:

- Change `master_seed` based on observed backtest output.
- Run a "seed sweep" to find a "lucky" seed.
- Apply a "fold-best-seed" or "pair-best-seed" rule.
- Justify a `master_seed` change with prior CAMPAIGN_011 results.

If a future sprint wants to use a different seed, that constitutes
a NEW candidate (e.g. `random_entry_anchor 0.2.0-c011-seed-N`)
requiring its own pre-commit. The original seed value is the
canonical CAMPAIGN_011.

## 7. Required local-only evaluation commands (Phase 5 smoke + future evidence sprints)

### 7.1 Phase 5 (this sprint) smoke commands — credential-free, no broker call

```bash
# Pytest the candidate's full unit suite.
.venv/bin/python -m pytest tests/unit/test_random_entry_anchor.py -q

# Config-load smoke (instantiate Settings from the YAML; no broker call).
.venv/bin/python -c "from forex_bot.config import load_settings; \
    s = load_settings('configs/campaign_011_random_entry_anchor.yaml'); \
    print('loaded:', s.strategy.enabled, 'random_entry_anchor?', \
          s.strategy.random_entry_anchor is not None)"

# Walk-forward dry-run plan (writes to /tmp; not committed).
.venv/bin/python scripts/run_walk_forward_dry_run.py \
    --campaign-name CAMPAIGN_011 \
    --universe-start 2020-01-01 --universe-end 2026-05-20 \
    --style rolling --parameter-mode frozen \
    --train-days 540 --validation-days 180 --test-days 180 \
    --step-days 180 \
    --output /tmp/campaign_011_smoke/
```

The full smoke result is recorded in
[`CAMPAIGN_011_SMOKE_RESULT.md`](CAMPAIGN_011_SMOKE_RESULT.md).

### 7.2 Future evidence sprint commands (NOT run by this sprint)

A separate future
`research-random-entry-diagnostic-anchor-walk-forward-001`
sprint must run:

```bash
# 1. Regenerate the authoritative walk-forward plan (committed).
.venv/bin/python scripts/run_walk_forward_dry_run.py \
    --campaign-name CAMPAIGN_011 \
    --universe-start 2020-01-01 --universe-end 2026-05-20 \
    --style rolling --parameter-mode frozen \
    --train-days 540 --validation-days 180 --test-days 180 \
    --step-days 180 \
    --output backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/

# 2. Run the per-fold backtests (new scripts/run_campaign_011.py,
#    structurally cloned from scripts/run_campaign_010.py with
#    the random_entry_anchor strategy class + frozen-parameter
#    assertion).
.venv/bin/python scripts/run_campaign_011.py \
    --config configs/campaign_011_random_entry_anchor.yaml \
    --plan backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json \
    --out backtests/CAMPAIGN_011_random_entry_anchor/

# 3. Financing overlay (ESTIMATED + conservative stress).
.venv/bin/python scripts/build_campaign_011_financing_overlay.py \
    --campaign-dir backtests/CAMPAIGN_011_random_entry_anchor/

# 4. Risk diagnostics.
.venv/bin/python scripts/build_campaign_011_risk_diagnostics.py \
    --campaign-dir backtests/CAMPAIGN_011_random_entry_anchor/
```

The above commands are listed for future-sprint reference; **this
sprint does not run any of them**.

## 8. Required walk-forward artifacts (future evidence sprint)

Per
[`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
§10 + §15:

- `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json`
- `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.md`
- `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json`
- `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.md`
- `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/fold_detail.json`

Constraints:

- `parameter_mode = "frozen"` (only authorised mode).
- `SplitStyle = "rolling"`.
- 540 / 180 / 180 / 180-day windows; ≥ 6 folds; **8 expected**
  (identical to CAMPAIGN_010).
- `validate_plan(plan)` must pass.
- `WalkForwardResults.overall_verdict ∈ {"PASS", "REJECT"}`.

## 9. Required financing artifacts (future evidence sprint)

Per
[`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
§11:

- `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.json`
- `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.md`
- `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_summary.json`

Required-embed fields verbatim:

- `financing_treatment = "estimated"` (MODELED refused at four layers)
- `financing_in_engine_pnl = false`
- `financing_is_live_blocker = true`
- `cashflow_home_total`
- `cashflow_home_stress_total`
- `missing_rate_event_count`

## 10. Required risk diagnostics (future evidence sprint)

Per
[`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
§12 (informational; do not gate the verdict):

- per-pair exposure trace at fold boundaries
- max concurrent open positions (expected 1 — engine-enforced)
- max aggregate notional
- per-pair distribution (expected ~uniform across 7 pairs;
  contrast with CAMPAIGN_010's pair-skewed distribution)
- **session-of-day distribution** (expected ~uniform across UTC
  hours — key diagnostic contrast with CAMPAIGN_010's 100 %
  London-window concentration)
- loss-streak distribution
- drawdown clustering
- RiskEngine rejection-code table

## 11. Required rejection gates (verbatim from the CAMPAIGN_010 pre-commit, inherited for clean comparability)

A REJECT verdict is **mandatory** if any of these hold (no
parameter tweaks, no gate relaxation, no per-pair save):

| level | gate | threshold |
|---|---|---|
| train fold | `expectancy_R_net_of_stress_financing` | ≥ 0.00 R |
| train fold | `trade_count` | ≥ 30 |
| train fold | `no_lookahead_audit` | PASS |
| validation fold | `expectancy_R_net_of_stress_financing` | ≥ 0.05 R |
| validation fold | `profit_factor_net_of_stress_financing` | ≥ 1.05 |
| validation fold | `pairs_positive_net_of_stress_financing` | ≥ 3 of 7 |
| validation fold | `trade_count` | ≥ 30 |
| test fold | `expectancy_R_net_of_stress_financing` | ≥ 0.05 R |
| test fold | `profit_factor_net_of_stress_financing` | ≥ 1.10 |
| test fold | `pairs_positive_net_of_stress_financing` | ≥ 4 of 7 |
| test fold | `trade_count` | ≥ 30 |
| test fold | `single_pair_dominance` | ≤ 60 % |
| aggregate | `fold_pass_rate` | 100 % (strict) |
| aggregate | `fold_count` | ≥ 6 |
| aggregate | `expectancy_R_net_of_stress_financing` | ≥ 0.05 R |
| aggregate | `profit_factor_net_of_stress_financing` | ≥ 1.10 |
| aggregate | `pairs_positive` | ≥ 4 of 7 |
| aggregate | `trade_count` | ≥ 200 |
| aggregate | `single_fold_dominance` | ≤ 60 % |
| aggregate | `single_pair_dominance` | ≤ 40 % |
| financing | `conservative_stress_run_does_not_flip_verdict` | PASS |
| financing | `modeled_refused` | PASS |
| financing | `missing_rate_event_count` | `0` |

**Expected outcome under random entry: REJECT on every
PnL-direction gate; PASS on every structural / financing /
dominance gate.** Expected aggregate expectancy R near
CAMPAIGN_005's −0.095 R random baseline (deepened by the longer
6-bar time stop and per-fold financing overlay).

## 12. Unexpected-PASS investigation playbook (binding)

If the future evidence sprint records `WalkForwardResults.overall_verdict == "PASS"`,
the documented response is:

1. **Do NOT** add `random_entry_anchor` to
   `configs/approved_strategies.yaml`.
2. **Do NOT** treat the result as evidence of an edge.
3. **Do** trigger the investigation playbook per
   [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
   §14:
   - Confirm `seed_input` does not include any bar-`t` data
     (re-grep `_derive_random_pair`'s signature + source).
   - Confirm fold-boundary leakage rules pass (`validate_plan()`).
   - Confirm the strategy module's structural audits pass
     (no `forex_bot.broker` import; no CAMPAIGN_002 / 010 keys).
   - Confirm the entry-probability rate matches the expected
     ~5 % per bar within statistical bounds.
   - Confirm the long-short distribution matches 50 / 50 within
     statistical bounds.
4. **Do** escalate to a separate investigation sprint
   (`infra-pipeline-validation-investigation-001`).
5. **Do** commit the verdict as REJECT pending investigation —
   an unexpected PASS that turns out to be a pipeline bug is
   *not* a research-pass; it is a bug report against the
   pipeline.

## 13. Explicit no-approval statement

This checklist, the candidate config, the implementation
spec, and the unit tests **do not approve the strategy**.
**`random_entry_anchor 0.1.0-c011` cannot be approved by
design — it is a null model.**

The candidate cannot be added to
[`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
under any circumstance. The protocol's §4 whitelist explicitly
lists "Baseline / null model" as "Allowed only as a diagnostic
comparison anchor for the preferred candidate; cannot itself be
the 'preferred candidate' for paper promotion."

## 14. Independent-verifier optional-follow-up status

Per
[`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
§13:

- Item 5 of the six-evidence ladder (independent corroboration)
  is a paper-promotion gate, not a research-pass gate.
- C5 cannot be paper-promoted (null model), so item 5 is
  structurally not binding for CAMPAIGN_011.
- The verifier extension is **uniquely valuable for C5 as a
  follow-up** because random has zero tunable parameters —
  same seed → same trades → same metrics → deterministic
  exact-equivalence corroboration is possible.
- **Recommended follow-up sprint:**
  `infra-free-local-parity-verifier-random-entry-001`.
- Neither the scaffold sprint nor the future evidence sprint
  is blocked on the verifier extension.

## 15. Safety state (unchanged from sprint Phase 0)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT.**
- **CAMPAIGN_010 remains REJECT.**
- **Paper / demo / live remain blocked.** `paper-loop` and
  `demo-loop` refuse; no `live-loop` command exists.
- No broker / OANDA call this sprint.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.
- `MODELED` financing remains refused at four layers.
- live-promotion financing blocker stands.

## 16. Cross-links

- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md)
- [`NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
  (the gate vector this checklist inherits)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
- [`CAMPAIGN_011_SMOKE_RESULT.md`](CAMPAIGN_011_SMOKE_RESULT.md)
- [`CAMPAIGN_011_WALK_FORWARD_READINESS.md`](CAMPAIGN_011_WALK_FORWARD_READINESS.md)
- [`CAMPAIGN_011_FINANCING_RISK_READINESS.md`](CAMPAIGN_011_FINANCING_RISK_READINESS.md)
- [`CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
