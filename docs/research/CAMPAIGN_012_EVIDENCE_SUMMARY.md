# CAMPAIGN_012 Evidence Summary

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-walk-forward-001`
`strategy_evidence: false`

One-page evidence summary for **CAMPAIGN_012 /
`regime_switcher_atr_percentile 0.1.0-c012`** (the C3 daily-ATR-
percentile regime-switcher candidate).

## Headline

> **`REJECT`** — 5 of 8 inherited aggregate gates fail; metrics
> markedly **worse** than CAMPAIGN_011 null baseline (well outside
> the indistinguishability band, in the worse direction).
>
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_002 / 010 / 011 remain REJECT and untouched. Paper /
> demo / live remain blocked.

## Headline numbers

| metric | CAMPAIGN_012 | CAMPAIGN_011 (null floor) | gate |
|---|---:|---:|---|
| fold count | 8 | 8 | ≥ 6 |
| fold pass rate | **0 / 8 = 0 %** | 0 / 8 | = 100 % required |
| total trades | 3,726 | 1,177 | ≥ 200 |
| aggregate expectancy R | **−0.0521** | −0.0024 | ≥ 0.05 |
| aggregate profit factor | **0.034** | 0.91 | ≥ 1.10 |
| aggregate return % (4 y) | **−43.52 %** | −0.53 % | n/a (informational) |
| pairs positive | **1 / 7** (USD_JPY +0.0004 R) | 3 / 7 | ≥ 4 / 7 |
| single_fold_dominance % | 28.54 % | 40.1 % | ≤ 60 % |
| single_pair_dominance % | 22.39 % | 36.5 % | ≤ 40 % |
| financing cashflow (stress) USD | −65.07 | −24.38 | (no flip) |
| financing missing-rate events | 0 | 0 | = 0 |

5 of 8 aggregate gates FAIL: `fold_pass_rate`, `expectancy_r`,
`profit_factor`, `pairs_positive`, (and trivially `fold_pass_rate`
implies per-fold failures).

## Null-baseline interpretation

CAMPAIGN_012 is **WORSE than the null model on every binding axis**:

| axis | how much worse than null? | inside indistinguishability band? |
|---|---|:---:|
| expectancy R | −0.0497 R lower (~21 × half-band) | NO |
| profit factor | −0.876 lower (~9 × half-band) | NO |
| aggregate return % | −42.99 pp lower (~22 × half-band) | NO |
| pairs positive | −2 pairs lower (= ±1 boundary, worse direction) | boundary |

Classification: **`REJECT`** (NOT `REJECT_INDISTINGUISHABLE_FROM_NULL`
— the metrics diverge from null in the worse direction, far outside
the symmetric ±band).

## Regime-switcher interpretation

The C3 hypothesis was: "filter for HIGH-VOL regimes (top 30 % daily
ATR percentile), then take a 4-bar trend continuation; calm regimes
do not trade." The walk-forward result **falsifies** this hypothesis:

- The regime gate did **not** improve signal quality (every per-fold
  expectancy is negative).
- The regime gate **amplified trade count** (3,726 vs CAMPAIGN_011's
  1,177) without improving signal quality, accumulating cost drag.
- USD_JPY's +0.0004 R is the same near-exact-zero random-walk floor
  CAMPAIGN_011 surfaced — the gate did not move USD_JPY off this
  floor.
- High-vol regimes on these majors are **not** trend-friendly; the
  trend filter goes the wrong way often enough that the gate
  produces more losing trades than it filters out.

## Six-evidence-ladder status

| item | name | status |
|---|---|---|
| 1 | data provenance | **COMPLETE** ([`CAMPAIGN_012_DATA_PROVENANCE.md`](CAMPAIGN_012_DATA_PROVENANCE.md); matches CAMPAIGN_010 / 011 verbatim) |
| 2 | walk-forward verdict | **COMPLETE** ([`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md); REJECT) |
| 3 | financing overlay | **COMPLETE** ([`CAMPAIGN_012_FINANCING_OVERLAY.md`](CAMPAIGN_012_FINANCING_OVERLAY.md); ESTIMATED + stress; MODELED refused) |
| 4 | risk diagnostics | **COMPLETE** ([`CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md); 8 / 8 sanity checks PASS; diagnostic only) |
| 5 | independent verifier | **NOT REQUIRED for REJECT** ([`CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md); deferred indefinitely) |
| 6 | deliberate human approval | **MOOT for REJECT** (no candidate to approve) |

## Comparison to prior REJECT campaigns

| metric | CAMPAIGN_002 (trend_following) | CAMPAIGN_010 (session_breakout) | CAMPAIGN_011 (random null) | **CAMPAIGN_012 (regime sw)** |
|---|---:|---:|---:|---:|
| aggregate expectancy R | −0.085 | −0.085 | −0.0024 | **−0.0521** |
| aggregate return % | −1.02 % | −1.02 % | −0.53 % | **−43.52 %** |
| profit factor | 0.75 | — | 0.91 | **0.034** |
| total trades (8-fold) | — | 2,791 | 1,177 | **3,726** |
| fold pass rate | n/a | 0 / 8 | 0 / 8 | **0 / 8** |
| pairs positive | — | — | 3 / 7 | **1 / 7** |
| verdict | REJECT | REJECT | REJECT (null) | **REJECT** |

**CAMPAIGN_012 has the worst aggregate-return of any campaign to
date.** The regime gate's cost amplification was greater than
session_breakout's session concentration or the null model's
uniform-noise sampling.

## Safety state at evidence-sprint close

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | REJECT (null-model anchor; untouched) |
| **CAMPAIGN_012** | **REJECT (this verdict)** |
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
| `D1AGG` aggregator edit | **none** (read-only use) |

## Cross-links

- [`REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md)
- [`CAMPAIGN_012_DATA_PROVENANCE.md`](CAMPAIGN_012_DATA_PROVENANCE.md)
- [`CAMPAIGN_012_WALK_FORWARD_PLAN.md`](CAMPAIGN_012_WALK_FORWARD_PLAN.md)
- [`CAMPAIGN_012_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_012_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_012_FINANCING_OVERLAY.md`](CAMPAIGN_012_FINANCING_OVERLAY.md)
- [`CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md)
- [`CAMPAIGN_012_STATUS.md`](CAMPAIGN_012_STATUS.md) (updated)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
- [`EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json)
