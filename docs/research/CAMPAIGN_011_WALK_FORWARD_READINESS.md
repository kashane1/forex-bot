# CAMPAIGN_011 — Walk-Forward Readiness

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-001`
`strategy_evidence: false`

Phase 6 walk-forward integration-readiness assessment for the
**CAMPAIGN_011 research candidate** (`random_entry_anchor
0.1.0-c011`). **Reading this document does not approve the
strategy and does not constitute a campaign verdict.** It
records whether the scaffold is *structurally ready* for a
future evidence sprint to generate `WalkForwardResults`.

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked. **CAMPAIGN_011
> is a null model — cannot be approved by design.**

## 1. Headline status

| dimension | status | note |
|---|---|---|
| Harness plug-in (plan generation, `validate_plan`) | **READY** | proven by Phase 5 dry-run: 8-fold plan generated and validated; ≥ 6 floor satisfied; matches CAMPAIGN_010 exactly |
| Strategy module conforms to the `Strategy` protocol | **READY** | Phase 3 unit tests assert `name`, `version`, `warmup_bars_required()`, `generate_signal(ctx) -> Signal \| None` |
| `parameter_mode = "frozen"` compatibility | **READY** | design + spec mandate frozen mode (only authorised); confirmed in `configs/campaign_011_random_entry_anchor.yaml` |
| Deterministic-seed reproducibility | **READY** | `master_seed = 20260523` frozen in pre-commit; same `(seed, pair, ts)` → same `bar_random` / `gate_random` — verified by Phase 3 unit tests over 10,000 bars |
| Inherited gate-vector compatibility | **READY** | gates inherited verbatim from `CAMPAIGN_010_PRECOMMIT_CHECKLIST.md` §10; the comparison is on the entry signal alone |
| Per-fold backtest invocation | **NOT EXECUTED** in this sprint | requires the future evidence sprint to drive `BacktestEngine` per fold via a new `scripts/run_campaign_011.py` (clone of `scripts/run_campaign_010.py` with the random_entry_anchor strategy class + frozen-parameter assertion); this sprint deliberately does not run any backtest |
| `WalkForwardResults` emission | **NOT EXECUTED** in this sprint | future evidence sprint |

**Net: harness-plumbing readiness is GREEN; backtest evidence
remains the future evidence sprint's job.**

## 2. Walk-forward fold plan (Phase 5 smoke; identical to CAMPAIGN_010)

Phase 5 produced and validated the fold plan with the inherited
parameters (rolling, frozen, 540 / 180 / 180 / 180 days,
`2020-01-01 → 2026-05-20`). Output committed to `/tmp` (not
committed to the repo per the prior sprints' convention; the
*evidence-grade* plan must commit to
`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/`).

### 2.1 Smoke plan summary (reproducible)

| field | value |
|---|---|
| `--campaign-name` | `CAMPAIGN_011` |
| `--style` | `rolling` |
| `--parameter-mode` | `frozen` |
| `--train-days` | `540` |
| `--validation-days` | `180` |
| `--test-days` | `180` |
| `--step-days` | `180` |
| `--universe-start` | `2020-01-01` |
| `--universe-end` | `2026-05-20` |
| **fold count emitted by harness** | **8** (identical to CAMPAIGN_010) |
| ≥ 6 minimum gate satisfied | **yes** |

### 2.2 Fold-by-fold (inherited from CAMPAIGN_010's authoritative plan)

| fold | test_start | test_end |
|---:|---|---|
| 0 | 2021-12-21 | 2022-06-18 |
| 1 | 2022-06-19 | 2022-12-15 |
| 2 | 2022-12-16 | 2023-06-13 |
| 3 | 2023-06-14 | 2023-12-10 |
| 4 | 2023-12-11 | 2024-06-07 |
| 5 | 2024-06-08 | 2024-12-04 |
| 6 | 2024-12-05 | 2025-06-02 |
| 7 | 2025-06-03 | 2025-11-29 |

(The future evidence sprint will regenerate via its own
`run_walk_forward_dry_run.py` invocation and commit the
authoritative `plan.json` / `plan.md` under
`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/`.)

## 3. Missing adapters (none required for plumbing; runner is required for backtest)

| adapter | required for | status |
|---|---|---|
| `Strategy` protocol implementation | bespoke `BacktestEngine` to drive per-fold | **DONE** — `src/forex_bot/strategies/random_entry_anchor.py` |
| `StrategyConfig.random_entry_anchor` slot | `forex_bot.config.load_settings` to recognise the candidate | **DONE** — `src/forex_bot/config.py` |
| YAML config that the bespoke engine can drive | the per-fold backtest invocation | **DONE** — `configs/campaign_011_random_entry_anchor.yaml` |
| Per-fold backtest driver (`scripts/run_campaign_011.py`) | iterating folds, slicing date windows, invoking `BacktestEngine`, accumulating `FoldMetrics` | **NOT DONE** — this is the future evidence sprint's task; clone `scripts/run_campaign_010.py` and swap the strategy class + `FROZEN_PARAMETERS` constant |
| Local historical candle data | per-fold backtest execution | **READY** — `data/campaign_002.sqlite3` symlink already in place (created by the prior `research-asian-london-session-breakout-walk-forward-001` Phase 1); 7 pairs × ~9,931 H4 candles each |

## 4. Future evidence-sprint commands (recorded; not run here)

The future
`research-random-entry-diagnostic-anchor-walk-forward-001` sprint
must run:

```bash
# 1. Regenerate the authoritative walk-forward plan (committed).
.venv/bin/python scripts/run_walk_forward_dry_run.py \
    --campaign-name CAMPAIGN_011 \
    --universe-start 2020-01-01 --universe-end 2026-05-20 \
    --style rolling --parameter-mode frozen \
    --train-days 540 --validation-days 180 --test-days 180 \
    --step-days 180 \
    --output backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/

# 2. Drive per-fold backtests via the new scripts/run_campaign_011.py
#    (clone of scripts/run_campaign_010.py with:
#    - EXPECTED_STRATEGY = "random_entry_anchor"
#    - EXPECTED_VERSION = "0.1.0-c011"
#    - FROZEN_PARAMETERS from CAMPAIGN_011_PRECOMMIT_CHECKLIST §5
#    - import RandomEntryAnchorStrategy
#    - gate constants inherited verbatim from CAMPAIGN_010).
.venv/bin/python scripts/run_campaign_011.py \
    --config configs/campaign_011_random_entry_anchor.yaml \
    --plan backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json \
    --out backtests/CAMPAIGN_011_random_entry_anchor/

# 3. Emit WalkForwardResults JSON + Markdown via
#    research.walk_forward.render_results_md inside the runner.
```

This sprint **does not** run any of these.

## 5. Strict gates (verbatim from CAMPAIGN_010 §10; inherited for clean comparability)

Every per-fold and aggregate gate from
[`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
§11 is binding on the future evidence sprint. The summary:

- **Strict pass:** `aggregate.fold_pass_rate == 100 %`. Any
  failed test fold = REJECT.
- **Min trade count:** 30 / fold, 200 / aggregate.
- **Dominance:** ≤ 60 % per pair per test fold; ≤ 40 % per pair
  on aggregate; ≤ 60 % per fold on aggregate.
- **Net of financing:** every PnL number must be reported
  **after** the conservative-stress overlay.

**No gate is relaxed after seeing results.** This is the same
rule the protocol applied to CAMPAIGN_010 — the null-model
candidate gets exactly the same treatment.

## 6. Expected outcome under random entry (informational; do not gate verdict)

Per
[`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
§9:

| metric | expected value (random) | gate threshold | expected result |
|---|---|---|---|
| `fold_pass_rate` | 0 / 8 | 100 % | **FAIL** |
| `aggregate_expectancy_R` | ≈ −0.05 to −0.15 R (random baseline; CAMPAIGN_005 reported −0.095 R on 6 majors with a different exit) | ≥ 0.05 R | **FAIL** |
| `aggregate_profit_factor` | ≈ 0.6 to 0.9 | ≥ 1.10 | **FAIL** |
| `aggregate_return_pct` | ≈ −30 % to −50 % over 4 years out-of-sample | (no gate) | informational |
| `pairs_positive` | 0–2 / 7 | ≥ 4 / 7 | **FAIL** |
| `single_pair_dominance` | ≤ 25 % (uniform target ≈ 14 %) | ≤ 40 % | PASS |
| `single_fold_dominance` | ≤ 25 % (uniform target ≈ 13 %) | ≤ 60 % | PASS |

The expected REJECT is the **success outcome of the evidence
sprint** — the falsifiability anchor is now established, and
any future candidate's per-fold + aggregate metrics can be
compared directly to CAMPAIGN_011's.

## 7. Why the scaffold sprint cannot grant a verdict

- It produced no `FoldMetrics`.
- It produced no `AggregateMetrics`.
- It produced no `WalkForwardResults`.
- It produced no per-pair expectancy R.
- It produced no per-pair profit factor.
- It produced no per-pair / per-fold dominance number.
- It executed no `BacktestEngine` invocation.
- It did not load any candle data into a strategy run.

A non-evidence smoke (Phase 5) cannot promote to evidence.
Only the future evidence sprint can.

## 8. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT.**
- **CAMPAIGN_010 remains REJECT.**
- **Paper / demo / live remain blocked.**
- No broker / OANDA call made by this readiness check.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.

## 9. Cross-links

- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
- [`CAMPAIGN_011_SMOKE_RESULT.md`](CAMPAIGN_011_SMOKE_RESULT.md)
- [`CAMPAIGN_011_FINANCING_RISK_READINESS.md`](CAMPAIGN_011_FINANCING_RISK_READINESS.md)
- [`CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
