# CAMPAIGN_011 — Status

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-walk-forward-001`
`strategy_evidence: false`

Status of the **CAMPAIGN_011 research candidate**
(`random_entry_anchor 0.1.0-c011`) at the close of the
walk-forward evidence sprint.

> ## Verdict: REJECT (null model anchor). No approval. No paper / demo / live.
>
> - **CAMPAIGN_011 is a null model by design.** It cannot be
>   added to
>   [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
>   under any circumstance. The protocol's §4 whitelist
>   explicitly lists "Baseline / null model" as "Allowed only
>   as a diagnostic comparison anchor for the preferred
>   candidate; cannot itself be the 'preferred candidate' for
>   paper promotion."
> - The walk-forward evidence sprint
>   (`research-random-entry-diagnostic-anchor-walk-forward-001`)
>   produced a clean, decisive REJECT verdict consistent with
>   no-edge expectations — see
>   [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md).
> - The REJECT verdict **validates the evidence pipeline** —
>   the gates correctly REJECT a known-zero-edge strategy with
>   metrics consistent with random expectations.
> - **CAMPAIGN_002 remains REJECT and is unrelated.** Only the
>   candle store is reused as data input.
> - **CAMPAIGN_010 remains REJECT and is unrelated.** The
>   exit logic + walk-forward fold structure + gate vector are
>   deliberately inherited so the comparison isolates the entry
>   signal; no CAMPAIGN_010 frozen parameter is "tuned" or
>   tweaked.

## 1. Headline result

| dimension | value |
|---|---|
| `WalkForwardResults.overall_verdict` | **`REJECT`** |
| classification | **REJECT** (not BLOCKED — pipeline ran cleanly; not INCONCLUSIVE — sample is rich; not INVESTIGATE_PIPELINE — no anomalous over-performance; not RESEARCH_PASS — gates fail) |
| pre-committed gates evaluated verbatim? | yes (4 PnL-direction gates fail; 6 structural / dominance / financing gates pass) |
| any gate relaxed? | no |
| any parameter tuned? | no (frozen-parameter + master-seed assertion in the runner aborts on any drift) |
| any seed optimized? | no (`master_seed = 20260523` was the only seed used) |
| `fold_pass_rate` | 0 / 8 = 0 % (gate 100 %) |
| `aggregate.expectancy_R` | **−0.0024 R** (gate ≥ 0.05) — within 0.0024 R of zero, exactly the null-model signature |
| `aggregate.profit_factor` | **0.91** (gate ≥ 1.10) — within 0.09 of one |
| `aggregate.return_pct` | −0.53 % over 4 years (essentially zero) |
| `aggregate.pairs_positive` | 3 / 7 (GBP_USD, USD_JPY ≈ 0, USD_CHF; gate ≥ 4 / 7) — close to uniform-noise expectation of ~3.5 |
| financing overlay impact | strictly worsens (USD_JPY flips +→− under conservative stress; `pairs_positive` → 2 / 7) |
| independent verifier ran? | no (capability-locked to CAMPAIGN_002; not required for REJECT verdict on a null model) |
| human approval action? | n/a — structurally impossible for a null model |

## 2. Pipeline validation outcome — **GREEN**

The REJECT verdict is the **expected and desired outcome of the
diagnostic anchor**. It confirms:

1. **The pipeline correctly REJECTs a known-zero-edge strategy.**
   No false positive.
2. **Metrics are statistically consistent with random
   expectations**: expectancy ≈ 0 (−0.0024 R), profit factor
   ≈ 1 (0.91), return ≈ 0 over 4 years (−0.53 %),
   pairs_positive ≈ uniform (3 / 7 vs 3.5 expected).
3. **USD_JPY expectancy is literally +0.0000** to 4 decimal
   places — textbook random-walk signature.
4. **Per-pair trade distribution is near-uniform** (ratio
   max/min = 1.65 vs CAMPAIGN_010's 12.0) — random sampling
   working correctly.
5. **Session-of-day distribution is diffuse** across all 4
   UTC buckets (no concentration > 50 %) — random has no
   session bias, as designed.
6. **8 / 8 pipeline sanity checks passed** in the risk
   diagnostics (per-pair uniformity, session diffuseness,
   long-share binomial bounds, concurrency, per-trade loss
   bounds, drawdown bounds, rejection codes firing correctly,
   events:trades ratio).

## 3. Evidence artifacts (this sprint's output)

| artifact | path |
|---|---|
| Sprint plan | [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md) |
| Data provenance | [`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md) |
| Walk-forward plan | [`CAMPAIGN_011_WALK_FORWARD_PLAN.md`](CAMPAIGN_011_WALK_FORWARD_PLAN.md) + `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.{json,md}` |
| Per-fold execution | [`CAMPAIGN_011_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_011_WALK_FORWARD_EXECUTION.md) + `backtests/CAMPAIGN_011_random_entry_anchor/folds/...` |
| Walk-forward verdict | [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md) + `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/{results.json,results.md,fold_detail.json}` |
| Financing overlay | [`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md) + `backtests/CAMPAIGN_011_random_entry_anchor/financing/{financing_run.json,financing_run.md,financing_summary.json}` |
| Portfolio-risk diagnostics | [`CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md) + `backtests/CAMPAIGN_011_random_entry_anchor/risk/{diagnostics.json,diagnostics.md}` |
| Independent verifier status | [`CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md) |
| Evidence summary | [`CAMPAIGN_011_EVIDENCE_SUMMARY.md`](CAMPAIGN_011_EVIDENCE_SUMMARY.md) (this sprint's Phase 9) |
| Sprint summary | [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md) |

## 4. Prior scaffold-sprint artifacts (still authoritative)

| artifact | path |
|---|---|
| Pre-commit checklist | [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md) (gates referenced verbatim) |
| Implementation spec | [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md) |
| Scaffold-sprint plan | [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md) |
| Scaffold-sprint summary | [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md) |
| Strategy module | [`src/forex_bot/strategies/random_entry_anchor.py`](../../src/forex_bot/strategies/random_entry_anchor.py) |
| Strategy unit tests | [`tests/unit/test_random_entry_anchor.py`](../../tests/unit/test_random_entry_anchor.py) |
| Strategy config sub-model | [`src/forex_bot/config.py`](../../src/forex_bot/config.py) (`RandomEntryAnchorStrategyConfig`) |
| Research config | [`configs/campaign_011_random_entry_anchor.yaml`](../../configs/campaign_011_random_entry_anchor.yaml) |
| Walk-forward readiness (preceding) | [`CAMPAIGN_011_WALK_FORWARD_READINESS.md`](CAMPAIGN_011_WALK_FORWARD_READINESS.md) |
| Financing + risk readiness (preceding) | [`CAMPAIGN_011_FINANCING_RISK_READINESS.md`](CAMPAIGN_011_FINANCING_RISK_READINESS.md) |
| Independent-verifier readiness (preceding) | [`CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md) |
| Smoke result (preceding) | [`CAMPAIGN_011_SMOKE_RESULT.md`](CAMPAIGN_011_SMOKE_RESULT.md) |

## 5. Safety state (unchanged)

| dimension | status |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| CAMPAIGN_002 verdict | **REJECT** (untouched) |
| CAMPAIGN_010 verdict | **REJECT** (untouched) |
| CAMPAIGN_011 verdict | **REJECT (null model anchor)** (this sprint) |
| `random_entry_anchor` in approved registry | **no, and structurally cannot be (null model)** |
| `random_entry_anchor` in any active loop | **no** |
| `random_entry_anchor` in `configs/paper.yaml` | **no** (verified by unit test) |
| `random_entry_anchor` in `configs/practice.yaml` | **no** (verified by unit test) |
| paper-loop / demo-loop refuse | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired; not used |
| broker / OANDA call this sprint | **none** |
| `.env` read this sprint | **none** |
| credential printed this sprint | **none** |
| account / order / trade / position / transaction endpoint queried this sprint | **none** |
| engine-PnL change | none |
| `src/forex_bot/financing.py` change | none |
| `MODELED` financing reachable | no (four refusal layers) |
| live-promotion financing blocker | stands (structurally moot for null model) |
| parameter tuning | none |
| seed optimization | none (only `master_seed = 20260523` was used) |
| pytest baseline | **771 passes** (unchanged) |

## 6. Strategy registry impact (Phase 9 update)

Per the verdict and
[`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)'s status conventions,
`random_entry_anchor 0.1.0-c011` is reclassified from
`scaffold-only` to **`rejected (null model anchor)`**. The
candidate joins the existing rejected list with
CAMPAIGN_002/003/004/007/008/009/010 — but with the
distinguishing label "null model anchor": it is the
reference floor, not just another failed candidate. Approval
is impossible for a null model; the registry row exists to
document the falsifiability bar.

## 7. Why this is REJECT, not INCONCLUSIVE, not BLOCKED, not INVESTIGATE_PIPELINE

| classification | criterion | this campaign |
|---|---|---|
| **BLOCKED** | pipeline cannot execute (data / tooling gap) | **not blocked** — 56 backtests ran cleanly in 5.6 s, 1,177 trades produced |
| **INCONCLUSIVE** | gates miss because of sample-size / coverage thinness | **not inconclusive** — aggregate 1,177 trades (≥ 200 gate); 8 folds (≥ 6 gate); the issue is the strategy has no edge, not statistical noise |
| **REJECT** | gates fail; metrics consistent with no-edge | **yes** — 4 / 8 PnL-direction gates fail; metrics within null-model tolerance |
| **INVESTIGATE_PIPELINE** | gates unexpectedly pass on a known-zero-edge strategy → information leakage / gate miscalibration / pipeline bug | **not triggered** — the null model REJECTed cleanly; no anomalous over-performance |

## 8. Recommended next sprints

- **`research-new-candidate-strategy-discovery-003`** —
  the next *real* candidate selection sprint (recommended
  ordering: C3 → C2 → C4 per
  [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md)).
  With the CAMPAIGN_011 falsifiability floor established
  (aggregate expectancy −0.0024 R, profit factor 0.91, 3/7
  pairs positive, 0/8 folds passing), any future real
  candidate has a clear bar to beat by a meaningful margin.
- (Optional) **`infra-free-local-parity-verifier-random-entry-001`** —
  extend the free / local verifier with a `random_entry_anchor`
  rule path; produces deterministic exact-equivalence
  corroboration; useful follow-up but not blocking.
- (Eventual) **`infra-ruff-up042-stress-enum-001`** —
  small cleanup sprint for the 11 pre-existing UP042 findings
  in untouched files.

## 9. Cross-links

- [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_011_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_011_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_011_WALK_FORWARD_PLAN.md`](CAMPAIGN_011_WALK_FORWARD_PLAN.md)
- [`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md)
- [`CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md)
- [`CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
