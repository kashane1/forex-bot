# CAMPAIGN_013 Walk-Forward Readiness

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-001`
`strategy_evidence: false`

Phase 6 readiness doc for the FUTURE walk-forward evidence sprint
**`research-cross-pair-currency-strength-rotation-walk-forward-001`**.
Records what the evidence sprint will do; does not run any of it.
The Phase 5 plan-only dry-run already confirmed the fold structure.

> No backtest fired. No broker call. No strategy approved.
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_011 is the **null baseline only**, not a trading
> candidate.

## 1. Future evidence branch

| field | value |
|---|---|
| branch name | `research-cross-pair-currency-strength-rotation-walk-forward-001` |
| binding spec | [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md) (Phase 7b of discovery-004) |
| sibling reference (CAMPAIGN_010) | `research-asian-london-session-breakout-walk-forward-001` |
| sibling reference (CAMPAIGN_011) | `research-random-entry-diagnostic-anchor-walk-forward-001` |
| sibling reference (CAMPAIGN_012) | `research-regime-switcher-atr-percentile-walk-forward-001` |
| approval allowed by this future sprint? | **NO** — even a clean PASS produces `RESEARCH_PASS_UNAPPROVED` |

## 2. Expected plan parameters (inherited verbatim from CAMPAIGN_010 / 011 / 012)

| field | value |
|---|---|
| `--style` | `rolling` |
| `--parameter-mode` | `frozen` |
| `--train-days` | `540` |
| `--validation-days` | `180` |
| `--test-days` | `180` |
| `--step-days` | `180` |
| `--universe-start` | `2020-01-01` |
| `--universe-end` | `2026-05-20` |
| **expected fold count** | **8** (confirmed by Phase 5 dry-run; identical to CAMPAIGN_010 / 011 / 012) |

## 3. Cross-pair runner integration requirement (binding)

The CAMPAIGN_013 runner is **structurally different** from
CAMPAIGN_010 / 011 / 012 runners because the strategy requires
sibling-pair close series at each invocation. The runner MUST:

1. Load all 7 pairs' completed H4 candles for the test window +
   warm-up margin (≥ 25 H4 bars + slack).
2. Align all 7 pairs to a common H4 timestamp index (intersection
   of completed bars).
3. Build per-pair closes-only `pd.Series` indexed by the common
   index.
4. Inject the dict `{pair: pd.Series}` into
   `strategy_config["cross_pair_closes"]` for each pair's engine
   invocation.

The binding integration contract is documented in
[`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)
§4 R3 and [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md)
§6.

If the runner cannot satisfy these invariants, the evidence sprint
**must classify the verdict as `BLOCKED`** (do not partial-evaluate;
do not approximate; do not silently substitute zero for missing
data).

## 4. Expected artifact paths (the future evidence sprint must commit)

| path | purpose |
|---|---|
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/plan.json` | machine-readable plan |
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/plan.md` | human-readable plan |
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/results.json` | per-fold + aggregate metrics |
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/results.md` | verdict doc |
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/fold_detail.json` | per-fold-per-pair details |
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/folds/fold_NN/fold_NN_<PAIR>_summary.json` | per-fold per-pair summary |
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/folds/fold_NN/fold_NN_<PAIR>_trades.csv` | per-fold per-pair trade log |
| `docs/research/CAMPAIGN_013_DATA_PROVENANCE.md` | data provenance (hashes match CAMPAIGN_010 / 011 / 012 verbatim) |
| `docs/research/CAMPAIGN_013_WALK_FORWARD_PLAN.md` | authoritative plan |
| `docs/research/CAMPAIGN_013_WALK_FORWARD_EXECUTION.md` | per-fold execution details |
| `docs/research/CAMPAIGN_013_WALK_FORWARD_RESULT.md` | formal verdict (must include "Null-baseline comparison" section) |

## 5. Per-fold + aggregate gates (inherited verbatim from CAMPAIGN_010 / 011 / 012)

See [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md)
§11 for the binding gate vector. Same per-fold + aggregate thresholds
as CAMPAIGN_010 / 011 / 012; plus the binding null-baseline
comparison gate (§9 of the precommit).

## 6. Null-baseline comparison gate (binding; CAMPAIGN_011-derived)

| metric | CAMPAIGN_011 floor | CAMPAIGN_013 must beat |
|---|---|---|
| aggregate expectancy R | −0.0024 | by ≥ **+0.0524 R** (→ ≥ 0.05 R) |
| aggregate profit factor | 0.91 | by ≥ **+0.19** (→ ≥ 1.10) |
| aggregate return (4 y) | −0.53 % | meaningfully positive (≥ **+5 %**) |
| `pairs_positive` | 3 / 7 | ≥ **4 / 7** |
| `fold_pass_rate` | 0 / 8 | **100 %** |

"Indistinguishable from null" REJECT band: ± 0.005 R / ± 0.10 PF /
± 2 pp / ± 1 pair.

## 7. Universe / data

| dimension | value |
|---|---|
| pairs | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD (7 pairs) |
| timeframe | H4 |
| data source | `data/campaign_002.sqlite3` (gitignored symlink) |
| data span | 2020-01-01 → 2026-05-19 inclusive |
| source label | `oanda-practice` (runner-enforced) |
| new data fetch needed? | **no** |
| new credentials needed? | **no** |

## 8. What this readiness doc does NOT do

- Does not run the walk-forward.
- Does not load any candle.
- Does not call any broker.
- Does not produce strategy evidence.
- Does not approve any strategy.

The future evidence-sprint *plan* this doc references will, by spec,
produce strategy evidence — but it has not run yet. CAMPAIGN_013
remains scaffold-only.

## 9. Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_013_STATUS.md`](CAMPAIGN_013_STATUS.md)
- [`CAMPAIGN_013_FINANCING_RISK_READINESS.md`](CAMPAIGN_013_FINANCING_RISK_READINESS.md)
- [`CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md)
- [`CAMPAIGN_010_WALK_FORWARD_PLAN.md`](CAMPAIGN_010_WALK_FORWARD_PLAN.md), [`CAMPAIGN_011_WALK_FORWARD_PLAN.md`](CAMPAIGN_011_WALK_FORWARD_PLAN.md), [`CAMPAIGN_012_WALK_FORWARD_PLAN.md`](CAMPAIGN_012_WALK_FORWARD_PLAN.md) (sibling plan references)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
