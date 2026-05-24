# CAMPAIGN_012 Status — `regime_switcher_atr_percentile 0.1.0-c012`

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-walk-forward-001`
`strategy_evidence: false`

| dimension | value |
|---|---|
| candidate | `regime_switcher_atr_percentile 0.1.0-c012` |
| family | volatility-regime switching (C3) |
| campaign id | CAMPAIGN_012 |
| status | **REJECTED** |
| backtest verdict | **REJECT** (5 of 8 inherited aggregate gates fail; markedly worse than CAMPAIGN_011 null baseline) |
| walk-forward verdict | REJECT (`CAMPAIGN_012_WALK_FORWARD_RESULT.md`) |
| financing overlay verdict | confirms REJECT (worsens net PnL by −$65.07; no pair flip) |
| portfolio-risk diagnostics verdict | diagnostic only (8 / 8 sanity checks pass; uniform-noise distribution shape, like CAMPAIGN_011 null) |
| independent verifier status | not run; **not required for REJECT** (capability-locked to CAMPAIGN_002) |
| strategy approval | **NO — REJECTED; cannot be approved** |
| paper / demo / live | **blocked** |
| in `configs/approved_strategies.yaml` | **no** (registry remains `approved: []`) |
| enabled in `configs/paper.yaml` | **no** |
| enabled in `configs/practice.yaml` | **no** |

## Verdict reasoning

Per the Phase 5 verdict
([`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md)):

- **5 of 8 inherited aggregate gates FAIL** (`fold_pass_rate`,
  `expectancy_r`, `profit_factor`, `pairs_positive`, and the
  `fold_pass_rate` failure implies all per-fold pass-rate gates fail).
- **Aggregate expectancy −0.0521 R** vs gate ≥ 0.05 R; vs CAMPAIGN_011
  null floor of −0.0024 R. CAMPAIGN_012 is **WORSE than null by
  0.0497 R** — ~21 × the indistinguishability half-band.
- **Aggregate return −43.52 % over 4 years** vs CAMPAIGN_011's
  −0.53 % — ~82 × worse in absolute terms.
- **Profit factor 0.034** vs gate ≥ 1.10; vs CAMPAIGN_011's 0.91.
- **Only 1 of 7 pairs positive** (USD_JPY at +0.0004 R, essentially
  random-walk floor) vs gate ≥ 4 / 7; vs CAMPAIGN_011's 3 / 7.
- **0 of 8 folds pass** — same as CAMPAIGN_011.

The classification is **`REJECT`** (NOT
`REJECT_INDISTINGUISHABLE_FROM_NULL`) because CAMPAIGN_012's metrics
diverge from CAMPAIGN_011's *in the worse direction*, far outside the
symmetric ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair indistinguishability
band on three of four binding axes (and exactly at the boundary on
`pairs_positive`, in the worse direction).

The regime gate did not rescue trend-following on H4 majors — it
**amplified cost drag** by allowing more bars to qualify for trading
(3,726 trades vs CAMPAIGN_011's 1,177) without improving signal
quality enough to overcome those costs.

## What this means

CAMPAIGN_012 is **REJECTED** and cannot be paper-promoted,
demo-deployed, or live-traded under any circumstance under the
current frozen-parameter pre-commit.

A different regime hypothesis (different threshold, different
lookback, different trend definition) would require a **new**
discovery + design + pre-commit cycle as a NEW candidate; it cannot
reuse CAMPAIGN_012's name, version, or pre-commit (binding per
[`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)).

The verifier-extension sprint
`infra-free-local-parity-verifier-regime-switcher-001` is **not
needed** for this REJECT and is **deferred indefinitely**.

## CAMPAIGN_002 / 010 / 011 relationship

| campaign | status | relation to CAMPAIGN_012 |
|---|---|---|
| CAMPAIGN_002 | REJECT (negative expectancy) | structurally unrelated; different entry family |
| CAMPAIGN_010 | REJECT (session breakout) | inherited gate vector + data + financing infrastructure; CAMPAIGN_012 result is materially worse |
| CAMPAIGN_011 | REJECT (null-model anchor) | inherited gate vector + data + financing infrastructure; **CAMPAIGN_011 is the null baseline that CAMPAIGN_012 failed to beat — by a wide margin in the WORSE direction**; CAMPAIGN_011 remains a null model and is NOT a trading candidate |

All four campaigns (002, 010, 011, 012) remain REJECT. Their verdicts
are unchanged by this sprint — except CAMPAIGN_012, which transitions
from `scaffold only` (set during the scaffold sprint
`research-regime-switcher-atr-percentile-001`) to `REJECTED` (this
evidence-sprint outcome).

## Why this is no longer a viable real candidate

Unlike CAMPAIGN_011's null model, CAMPAIGN_012 had a directional
hypothesis. But the walk-forward result falsifies the hypothesis on
the 7-pair × 6-year H4 OANDA-practice universe:

- The regime feature does not predict trade profitability for the
  candidate's entry direction.
- The trend filter on H4 close-vs-close drift catches noise as
  readily as signal on these pairs.
- HIGH-VOL regimes on majors are not trend-friendly at this
  timeframe; they often coincide with mean-reverting central-bank-event
  spikes.

Future candidate families should consider an entirely different
gate concept (e.g. cross-instrument momentum, carry-overlay long-only,
volatility-expansion paired straddle — see
[`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md)
for the deferred C2 / C4 menu) rather than another regime variant on
this universe.

## Safety state (verified)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | **no** (4 refusal layers; intact) |
| broker / OANDA call this sprint | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| historical campaign verdict change | **none** (CAMPAIGN_002 / 010 / 011 untouched) |
| CAMPAIGN_012 parameter "tweak" or "rescue" | **none** (frozen parameters unchanged across all 10 phases) |
| `D1AGG` aggregator edit | **none** (read-only use) |
| pytest baseline | 818 → 818 (preserved) |
| ruff baseline | 3 pre-existing (unchanged) |

## Cross-links

- [`REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md)
- [`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md) (verdict)
- [`CAMPAIGN_012_EVIDENCE_SUMMARY.md`](CAMPAIGN_012_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_012_DATA_PROVENANCE.md`](CAMPAIGN_012_DATA_PROVENANCE.md)
- [`CAMPAIGN_012_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_012_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_012_FINANCING_OVERLAY.md`](CAMPAIGN_012_FINANCING_OVERLAY.md)
- [`CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
- [`EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json)
