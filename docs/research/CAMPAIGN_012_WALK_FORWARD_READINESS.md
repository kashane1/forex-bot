# CAMPAIGN_012 Walk-Forward Readiness

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-001`
`strategy_evidence: false`

Phase 6 readiness doc for the FUTURE walk-forward evidence sprint
**`research-regime-switcher-atr-percentile-walk-forward-001`**. This
doc records what the evidence sprint will do; it does not run any of
it. The Phase 5 plan-only dry-run already confirmed the fold structure.

> No backtest fired. No broker call. No strategy approved.
> `configs/approved_strategies.yaml` remains `approved: []`. CAMPAIGN_011
> is the **null baseline only**, not a trading candidate.

## 1. Future evidence branch

| field | value |
|---|---|
| branch name | `research-regime-switcher-atr-percentile-walk-forward-001` |
| binding spec | [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md) (Phase 6b of discovery-003) |
| sibling reference (CAMPAIGN_010) | `research-asian-london-session-breakout-walk-forward-001` |
| sibling reference (CAMPAIGN_011) | `research-random-entry-diagnostic-anchor-walk-forward-001` |
| approval allowed by this future sprint? | **NO** — even a clean PASS produces `RESEARCH_PASS_UNAPPROVED`; human approval action is separate |

## 2. Expected plan parameters (inherited verbatim from CAMPAIGN_010 / CAMPAIGN_011)

| `--style` | `rolling` |
|---|---|
| `--parameter-mode` | `frozen` |
| `--train-days` | `540` |
| `--validation-days` | `180` |
| `--test-days` | `180` |
| `--step-days` | `180` |
| `--universe-start` | `2020-01-01` |
| `--universe-end` | `2026-05-20` |
| **expected fold count** | **8** (confirmed by the Phase 5 dry-run; identical to CAMPAIGN_010 / 011 plans) |

The Phase 5 dry-run produced the following fold boundaries (also
identical to CAMPAIGN_010 / CAMPAIGN_011 plans):

| fold | train | validation | test |
|---|---|---|---|
| 0 | 2020-01-01 → 2021-06-23 | 2021-06-24 → 2021-12-20 | 2021-12-21 → 2022-06-18 |
| 1 | 2020-06-29 → 2021-12-20 | 2021-12-21 → 2022-06-18 | 2022-06-19 → 2022-12-15 |
| 2 | 2020-12-26 → 2022-06-18 | 2022-06-19 → 2022-12-15 | 2022-12-16 → 2023-06-13 |
| 3 | 2021-06-24 → 2022-12-15 | 2022-12-16 → 2023-06-13 | 2023-06-14 → 2023-12-10 |
| 4 | 2021-12-21 → 2023-06-13 | 2023-06-14 → 2023-12-10 | 2023-12-11 → 2024-06-07 |
| 5 | 2022-06-19 → 2023-12-10 | 2023-12-11 → 2024-06-07 | 2024-06-08 → 2024-12-04 |
| 6 | 2022-12-16 → 2024-06-07 | 2024-06-08 → 2024-12-04 | 2024-12-05 → 2025-06-02 |
| 7 | 2023-06-14 → 2024-12-04 | 2024-12-05 → 2025-06-02 | 2025-06-03 → 2025-11-29 |

(Plan-only output; written to `/tmp` during Phase 5 and not committed.)

## 3. Expected artifact paths (the future evidence sprint must commit)

| path | purpose |
|---|---|
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/plan.json` | machine-readable plan |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/plan.md` | human-readable plan |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/results.json` | per-fold + aggregate metrics |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/results.md` | verdict doc |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/fold_detail.json` | per-fold-per-pair details |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/folds/fold_NN/fold_NN_<PAIR>_summary.json` | per-fold per-pair summary |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/folds/fold_NN/fold_NN_<PAIR>_trades.csv` | per-fold per-pair trade log |
| `docs/research/CAMPAIGN_012_DATA_PROVENANCE.md` | data provenance (SHA-256 hashes; should match CAMPAIGN_010 / 011 verbatim — same physical store) |
| `docs/research/CAMPAIGN_012_WALK_FORWARD_PLAN.md` | authoritative plan |
| `docs/research/CAMPAIGN_012_WALK_FORWARD_EXECUTION.md` | per-fold execution details |
| `docs/research/CAMPAIGN_012_WALK_FORWARD_RESULT.md` | formal verdict (must include "Null-baseline comparison" section per §5) |
| `docs/research/CAMPAIGN_012_FINANCING_OVERLAY.md` | financing overlay (ESTIMATED + conservative stress) |
| `docs/research/CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md` | risk diagnostics |
| `docs/research/CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md` | verifier capability assessment |
| `docs/research/CAMPAIGN_012_EVIDENCE_SUMMARY.md` | one-page evidence summary |
| `docs/research/CAMPAIGN_012_STATUS.md` (updated) | reclassified `scaffold-only → rejected` OR `scaffold-only → research_pass_unapproved` |
| `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md` | sprint summary |

## 4. Per-fold gates (inherited verbatim from CAMPAIGN_010 §10 / CAMPAIGN_011 §11)

| level | gate | threshold |
|---|---|---|
| test fold | `expectancy_R_net_of_stress_financing` | ≥ 0.05 R |
| test fold | `profit_factor_net_of_stress_financing` | ≥ 1.10 |
| test fold | `pairs_positive_net_of_stress_financing` | ≥ 4 of 7 |
| test fold | `trade_count` | ≥ 30 |
| test fold | `single_pair_dominance` | ≤ 60 % |

## 5. Aggregate gates (inherited) + null-baseline comparison gate

| level | gate | threshold |
|---|---|---|
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
| financing | `missing_rate_event_count` | 0 |
| **null-baseline** | **meaningful improvement vs CAMPAIGN_011 (§7)** | **PASS** |

### Null-baseline comparison gate (binding; CAMPAIGN_011-derived)

Per
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
§3, the CAMPAIGN_012 verdict doc **must** include a "Null-baseline
comparison" section with explicit "meaningful improvement over null?"
verdicts:

| metric | CAMPAIGN_011 floor | CAMPAIGN_012 must beat |
|---|---|---|
| aggregate expectancy R | −0.0024 | by ≥ **+0.0524 R** (→ ≥ 0.05 R) |
| aggregate profit factor | 0.91 | by ≥ **+0.19** (→ ≥ 1.10) |
| aggregate return (4 y) | −0.53 % | meaningfully positive (≥ **+5 %**) |
| `pairs_positive` | 3 / 7 | ≥ **4 / 7** |
| `fold_pass_rate` | 0 / 8 | **100 %** |
| `single_fold_dominance` | 40.1 % | ≤ **60 %** (CAMPAIGN_010 gate) |

If CAMPAIGN_012's aggregate metrics cluster within
**±0.005 R / ±0.10 PF / ±2 pp / ±1 pair** of CAMPAIGN_011's, the
verdict doc must classify it as **REJECT (indistinguishable from null)**,
regardless of which inherited gates technically pass.

## 6. Universe / data

| dimension | value |
|---|---|
| pairs | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD (7 pairs) |
| timeframe | H4 |
| data source | `data/campaign_002.sqlite3` (gitignored symlink) |
| data span | 2020-01-01 → 2026-05-19 inclusive |
| source label | `oanda-practice` (runner-enforced) |
| new data fetch needed? | **no** |
| new credentials needed? | **no** |

## 7. What this readiness doc does NOT do

- Does not run the walk-forward.
- Does not load any candle.
- Does not call any broker.
- Does not produce strategy evidence.
- Does not approve any strategy.

The future evidence-sprint *plan* this doc references will, by spec,
produce strategy evidence — but it has not run yet. CAMPAIGN_012
remains scaffold-only.

## 8. Cross-links

- [`REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md)
- [`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_012_STATUS.md`](CAMPAIGN_012_STATUS.md)
- [`CAMPAIGN_012_FINANCING_RISK_READINESS.md`](CAMPAIGN_012_FINANCING_RISK_READINESS.md)
- [`CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md)
- [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md)
- [`CAMPAIGN_010_WALK_FORWARD_PLAN.md`](CAMPAIGN_010_WALK_FORWARD_PLAN.md) (sibling plan reference)
- [`CAMPAIGN_011_WALK_FORWARD_PLAN.md`](CAMPAIGN_011_WALK_FORWARD_PLAN.md) (sibling plan reference)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
