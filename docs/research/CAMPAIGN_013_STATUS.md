# CAMPAIGN_013 Status — `cross_pair_currency_strength_rotation 0.1.0-c013`

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-walk-forward-001`
`strategy_evidence: false`

| dimension | value |
|---|---|
| candidate | `cross_pair_currency_strength_rotation 0.1.0-c013` |
| family | cross-pair currency-strength rotation (C6) |
| campaign id | CAMPAIGN_013 |
| status | **REJECTED** (evidence sprint complete) |
| backtest verdict | **REJECT** ([`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md)) |
| walk-forward verdict | **REJECT** (5 of 8 inherited aggregate gates fail; 0 / 8 fold pass) |
| null-baseline comparison | **REJECT** (worse than null on every binding axis, far outside ± band) |
| cross-pair runner contract | **SATISFIED on all 8 folds** (not BLOCKED) |
| financing overlay verdict | **REJECT (informational)** — verdict already REJECT pre-financing; financing adds −$139.99 drag and flips USD_JPY + → − |
| portfolio-risk diagnostics verdict | **diagnostic only; no finding contradicts REJECT** |
| independent verifier status | **not run** (verifier capability-locked to CAMPAIGN_002; not required for REJECT) |
| strategy approval | **NO — REJECTED; cannot be approved by any sprint** |
| paper / demo / live | **blocked** |
| in `configs/approved_strategies.yaml` | **no** (registry remains `approved: []`) |
| enabled in `configs/paper.yaml` | **no** |
| enabled in `configs/practice.yaml` | **no** |

## Headline numbers

| metric | value | gate |
|---|---:|---|
| fold count | 8 | ≥ 6 ✓ |
| fold pass rate | **0 / 8 = 0 %** | = 100 % ✗ |
| total trades | **7,940** | ≥ 200 ✓ |
| aggregate expectancy R | **−0.0564** | ≥ 0.05 ✗ |
| aggregate profit factor | **0.000** | ≥ 1.10 ✗ |
| aggregate return % | **−113.36 %** | informational |
| pairs positive | **1 / 7** (USD_JPY +0.0000 R) | ≥ 4 / 7 ✗ |
| single_fold_dominance % | 22.34 % | ≤ 60 % ✓ |
| single_pair_dominance % | 36.55 % | ≤ 40 % ✓ |

**5 of 8 aggregate gates FAIL → REJECT.**

## What this means

The C6 cross-pair currency-strength rotation hypothesis ("rank the
8 G8 currencies by 24-bar log-return strength; trade only the
largest rank gaps ≥ 4 / 7; long strong-base / short strong-quote
over 6 H4 bars") is **falsified** on the 7-pair OANDA practice H4
universe (2020-01-01 → 2026-05-20) by the Phase 5 walk-forward
verdict:

- Every per-fold expectancy is negative (range −0.1017 R to
  −0.0027 R; no fold reaches break-even).
- 7 of 8 folds have **all** trading pairs producing non-positive
  total returns (profit factor 0.000).
- Aggregate return is **−113.36 %** over 4 years — by far the worst
  of any campaign to date (~214 × CAMPAIGN_011's null floor; ~2.6 ×
  CAMPAIGN_012's regime-switcher).
- USD_JPY sits at the random-walk floor +0.0000 R (same signature
  CAMPAIGN_011 and CAMPAIGN_012 surfaced).
- NZD_USD is catastrophic: −41.76 % over 4 years on 1,863 trades.

The rank-gap rule amplified trade count ~6.7 × vs CAMPAIGN_011's
PRNG-driven null model without improving signal quality — each extra
trade pays the same spread + slippage cost without an offsetting
edge.

The cross-pair runner integration contract (Phase 0 binding
requirement) was **SATISFIED on all 8 folds** — the REJECT is on
inherited gates alone, not on contract failure. Had any fold failed
the contract, the verdict would have been BLOCKED.

## CAMPAIGN_002 / 010 / 011 / 012 relationship

| campaign | status | relation to CAMPAIGN_013 |
|---|---|---|
| CAMPAIGN_002 | REJECT (negative expectancy) | structurally unrelated; different entry family |
| CAMPAIGN_010 | REJECT (session breakout) | inherited gate vector + data + financing infrastructure; NO mechanism reuse |
| CAMPAIGN_011 | REJECT (null-model anchor) | inherited gate vector + data + financing infrastructure; CAMPAIGN_011 is the **null baseline** that CAMPAIGN_013 had to beat by a meaningful margin — and did not (CAMPAIGN_013 is worse on every binding axis) |
| CAMPAIGN_012 | REJECT (regime switcher) | inherited gate vector + data + financing infrastructure; CAMPAIGN_012 was the most recent rejected real-edge candidate; CAMPAIGN_013 is **2.6 × worse on aggregate return** |

All four remain REJECT. Their verdicts are unchanged by this sprint.

CAMPAIGN_013 joins the rejected baseline as the **8th** REJECT
evidence point and the **worst-performing campaign by aggregate
return / profit factor / trade count**.

## Why this REJECT happened (and what it teaches)

CAMPAIGN_013 + CAMPAIGN_012 together establish a clear pattern: on
the 7-pair H4 majors universe under the inherited cost model,
**adding a turnover-amplifying filter to a negative-edge entry
direction makes results materially worse, not better**. The
incremental complexity (regime gate, cross-pair rotation) buys
trade frequency without buying signal quality.

| campaign | filter type | trade count | aggregate return | aggregate expectancy R |
|---|---|---:|---:|---:|
| CAMPAIGN_011 (null) | none — PRNG | 1,177 | −0.53 % | −0.0024 |
| CAMPAIGN_012 (regime) | HIGH-VOL gate amplifies trades | 3,726 | −43.52 % | −0.0521 |
| CAMPAIGN_013 (cross-pair) | rank-gap rule amplifies trades | 7,940 | −113.36 % | −0.0564 |

**The slope is monotonic in trade count.** This is now a binding
anti-pattern that any future discovery sprint should explicitly
disqualify: do not propose turnover-amplifying filters on top of
rejected entry directions on this universe.

## Safety state (verified at sprint close)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | **no** (4 refusal layers; intact) |
| broker / OANDA call this sprint | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| historical campaign verdict change | **none** (CAMPAIGN_002 / 010 / 011 / 012 untouched) |
| parameter "tweak" or "rescue" | **none** (frozen parameters unchanged across all 10 phases) |
| `max_open_positions` relaxation | **none** (rule explicitly maintained) |
| `src/forex_bot/financing.py` edit | **none** |
| RiskEngine / engine / loops edit | **none** |
| pytest baseline | 875 (preserved) |
| ruff baseline | 3 pre-existing in `research/lean_parity/algorithms/` (unchanged) |

## Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md) (sprint Phase 0)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md) (sprint summary)
- [`CAMPAIGN_013_EVIDENCE_SUMMARY.md`](CAMPAIGN_013_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_013_DATA_PROVENANCE.md`](CAMPAIGN_013_DATA_PROVENANCE.md)
- [`CAMPAIGN_013_WALK_FORWARD_PLAN.md`](CAMPAIGN_013_WALK_FORWARD_PLAN.md)
- [`CAMPAIGN_013_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_013_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_013_FINANCING_OVERLAY.md`](CAMPAIGN_013_FINANCING_OVERLAY.md)
- [`CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md)
- [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md) (scaffold-sprint summary)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
- [`EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json)
