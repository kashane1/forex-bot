# CAMPAIGN_013 Evidence Summary

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-walk-forward-001`
`strategy_evidence: false`

One-page evidence summary for **CAMPAIGN_013 /
`cross_pair_currency_strength_rotation 0.1.0-c013`** (the C6
cross-pair currency-strength rotation candidate).

## Headline

> **`REJECT`** — 5 of 8 inherited aggregate gates fail; the
> worst-performing campaign to date by aggregate return, profit
> factor, and trade count. Catastrophically worse than CAMPAIGN_011
> null baseline (well outside the indistinguishability band, in the
> worse direction). The cross-pair runner integration contract was
> SATISFIED on all 8 folds — the REJECT is on inherited gates alone,
> not BLOCKED.
>
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_002 / 010 / 011 / 012 remain REJECT and untouched. Paper /
> demo / live remain blocked.

## Headline numbers

| metric | CAMPAIGN_013 | CAMPAIGN_011 (null floor) | gate |
|---|---:|---:|---|
| fold count | 8 | 8 | ≥ 6 |
| fold pass rate | **0 / 8 = 0 %** | 0 / 8 | = 100 % required |
| total trades | **7,940** | 1,177 | ≥ 200 |
| aggregate expectancy R | **−0.0564** | −0.0024 | ≥ 0.05 |
| aggregate profit factor | **0.000** | 0.91 | ≥ 1.10 |
| aggregate return % (4 y) | **−113.36 %** | −0.53 % | n/a (informational) |
| pairs positive | **1 / 7** (USD_JPY +0.0000 R) | 3 / 7 | ≥ 4 / 7 |
| single_fold_dominance % | 22.34 % | 40.1 % | ≤ 60 % |
| single_pair_dominance % | 36.55 % | 36.5 % | ≤ 40 % |
| financing cashflow (stress) USD | **−139.99** | −24.38 | (USD_JPY flips + → −) |
| financing missing-rate events | 0 | 0 | = 0 |
| cross-pair contract satisfied | **8 / 8** | n/a | all folds required |
| `MAX_OPEN_POSITIONS_EXCEEDED` | **0** | 0 | n/a (per-pair runner) |

5 of 8 aggregate gates FAIL: `fold_pass_rate_eq_100pct`,
`expectancy_r_ge_0p05`, `profit_factor_ge_1p10`,
`pairs_positive_ge_4_of_7`, (and trivially `fold_pass_rate`
implies per-fold failures). 3 gates PASS: `fold_count_ge_6`,
`trade_count_ge_200`, `single_fold_dominance_le_60pct`,
`single_pair_dominance_le_40pct` (4 — `pairs_positive` already
counted in the failures column).

## Null-baseline interpretation

CAMPAIGN_013 is **WORSE than the null model on every binding axis**:

| axis | how much worse than null? | inside indistinguishability band? |
|---|---|:---:|
| expectancy R | −0.0540 R lower (~11 × half-band) | NO |
| profit factor | −0.910 lower (~9 × half-band) | NO |
| aggregate return % | −112.83 pp lower (~56 × half-band) | NO |
| pairs positive | −2 pairs lower (= ±1 boundary, worse direction) | boundary |

Classification: **`REJECT`** (NOT `REJECT_INDISTINGUISHABLE_FROM_NULL`
— the metrics diverge from null in the worse direction, far outside
the symmetric ±band). NOT `BLOCKED` (the cross-pair runner
integration contract was satisfied on all 8 folds; the REJECT is on
inherited gates alone).

## Cross-pair rotator interpretation

The C6 hypothesis was: "rank the 8 G8 currencies by 24-bar log-
return strength, take only the largest rank gaps (≥ 4 / 7), long
the strong-base / short the strong-quote pair." The walk-forward
result **falsifies** this hypothesis:

- The rank-gap filter did **not** improve signal quality (every
  per-fold expectancy is negative; range −0.1017 R to −0.0027 R).
- The rank-gap filter **amplified trade count** dramatically (7,940
  vs CAMPAIGN_011's 1,177 — ~6.7 × as many), without improving
  signal quality, accumulating cost drag.
- USD_JPY's +0.0000 R is the same near-exact-zero random-walk floor
  CAMPAIGN_011 and CAMPAIGN_012 surfaced — the rank-gap rule did not
  move USD_JPY off this floor.
- NZD_USD lost **41.76 %** over 4 years (1,863 trades, −0.0897 R) —
  by far the worst pair; the cross-pair rotator's USD-relative
  ranking pushed it into NZD_USD positions during trending periods
  that subsequently reversed, with the 6-bar holding period
  magnifying whipsaw losses.
- The rank gap is **not a directional edge** for the pair-level
  distribution on the 6-bar holding horizon; by the time the
  strategy enters, the rank-gap-implied move has often already played
  out.

## Cross-pair runner integration contract

**SATISFIED on all 8 folds.** The runner emitted
`cross_pair_diagnostics` for each fold showing
`contract_satisfied = true` and `common_index_length = 1,825-1,848`
H4 bars. The REJECT comes from inherited gates alone, not from
contract failure. Had any fold failed the contract, the verdict
would have been BLOCKED regardless of fold metrics.

## Architectural diagnostic: `MAX_OPEN_POSITIONS_EXCEEDED = 0`

The `BacktestEngine` is single-instrument; the runner invokes one
engine per pair per fold. The `max_open_positions = 1` cap is
within-pair only, not portfolio-wide. A portfolio-aware runner with
`max_open_positions = 1` enforced *across* pairs would reduce trade
count by ~40 % (simultaneous-signal rate; see
`CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md` §7.4) but cannot
rescue per-pair negative expectancy (6 of 7 pairs are negative).
The standing rule "do not relax `max_open_positions` to rescue
trade count" is unaffected; no rule change is motivated.

## Six-evidence-ladder status

| item | name | status |
|---|---|---|
| 1 | data provenance | **COMPLETE** ([`CAMPAIGN_013_DATA_PROVENANCE.md`](CAMPAIGN_013_DATA_PROVENANCE.md); matches CAMPAIGN_010 / 011 / 012 verbatim) |
| 2 | walk-forward verdict | **COMPLETE** ([`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md); REJECT) |
| 3 | financing overlay | **COMPLETE** ([`CAMPAIGN_013_FINANCING_OVERLAY.md`](CAMPAIGN_013_FINANCING_OVERLAY.md); ESTIMATED + stress; MODELED refused; USD_JPY flips + → −) |
| 4 | risk diagnostics | **COMPLETE** ([`CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md); diagnostic only; no diagnostic contradicts REJECT) |
| 5 | independent verifier | **NOT REQUIRED for REJECT** ([`CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md); deferred indefinitely) |
| 6 | deliberate human approval | **MOOT for REJECT** (no candidate to approve) |

## Comparison to prior REJECT campaigns

| metric | CAMPAIGN_002 (trend_following) | CAMPAIGN_010 (session_breakout) | CAMPAIGN_011 (random null) | CAMPAIGN_012 (regime sw) | **CAMPAIGN_013 (cross-pair)** |
|---|---:|---:|---:|---:|---:|
| aggregate expectancy R | −0.085 | −0.085 | −0.0024 | −0.0521 | **−0.0564** |
| aggregate return % | −1.02 % | −1.02 % | −0.53 % | −43.52 % | **−113.36 %** |
| profit factor | 0.75 | — | 0.91 | 0.034 | **0.000** |
| total trades (8-fold) | — | 2,791 | 1,177 | 3,726 | **7,940** |
| fold pass rate | n/a | 0 / 8 | 0 / 8 | 0 / 8 | **0 / 8** |
| pairs positive | — | — | 3 / 7 | 1 / 7 | **1 / 7** |
| verdict | REJECT | REJECT | REJECT (null) | REJECT | **REJECT** |

**CAMPAIGN_013 has by far the worst aggregate-return of any campaign
to date** (~214 × worse than CAMPAIGN_011's null floor and ~2.6 ×
worse than CAMPAIGN_012). The pattern is consistent: adding
turnover-amplifying filters to a negative-edge entry direction on H4
majors makes results materially worse, not better. The incremental
complexity costs (regime gate, cross-pair rotation) buy extra trade
frequency without buying signal quality.

## Safety state at evidence-sprint close

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | REJECT (null-model anchor; untouched) |
| CAMPAIGN_012 | REJECT (untouched) |
| **CAMPAIGN_013** | **REJECT (this verdict)** |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| live-promotion financing blocker | stands |
| broker call this sprint | **none** |
| `.env` read / credential printed | **none** |
| account/order/trade/position/transaction endpoint queried | **none** |
| historical campaign verdict change | **none** |
| parameter "tweak" or "rescue" | **none** (frozen parameters intact) |
| `max_open_positions` relaxation | **none** (rule explicitly maintained) |

## Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md)
- [`CAMPAIGN_013_DATA_PROVENANCE.md`](CAMPAIGN_013_DATA_PROVENANCE.md)
- [`CAMPAIGN_013_WALK_FORWARD_PLAN.md`](CAMPAIGN_013_WALK_FORWARD_PLAN.md)
- [`CAMPAIGN_013_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_013_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_013_FINANCING_OVERLAY.md`](CAMPAIGN_013_FINANCING_OVERLAY.md)
- [`CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md)
- [`CAMPAIGN_013_STATUS.md`](CAMPAIGN_013_STATUS.md) (updated)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
- [`EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json)
