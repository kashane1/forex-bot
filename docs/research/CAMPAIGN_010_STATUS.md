# CAMPAIGN_010 — Status

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-walk-forward-001`
`strategy_evidence: false`

Status of the **CAMPAIGN_010 research candidate**
(`session_breakout 0.1.0-c010`) at the close of the
walk-forward evidence sprint.

> ## Verdict: REJECT. No approval. No paper / demo / live.
>
> - The walk-forward evidence sprint
>   (`research-asian-london-session-breakout-walk-forward-001`)
>   produced a clean, decisive REJECT verdict — see
>   [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md).
> - The candidate is **not** in
>   [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
>   and never will be — the rejected verdict is binding.
> - **CAMPAIGN_002 remains REJECT and is unrelated** to this
>   candidate. Only the candle store was reused; no rule, no
>   parameter, no setting overlap.

## 1. Headline result

| dimension | value |
|---|---|
| `WalkForwardResults.overall_verdict` | **`REJECT`** |
| pre-committed gates evaluated verbatim? | yes (5 fail, 4 pass; see [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md) §2) |
| any gate relaxed? | no |
| any parameter tuned? | no (frozen-parameter assertion in the runner aborts on any drift) |
| `fold_pass_rate` | 0 / 8 = 0 % (gate 100 %) |
| `aggregate.expectancy_R` | −0.0408 R (gate ≥ 0.05) |
| `aggregate.profit_factor` | 0.04 (gate ≥ 1.10) |
| `aggregate.pairs_positive` | 1 / 7 (USD_CHF only; gate ≥ 4 / 7) |
| financing overlay impact | strictly worsens (USD_CHF flips +→− under conservative stress; `pairs_positive` → 0 / 7) |
| independent verifier ran? | no (capability-locked to CAMPAIGN_002; would have only mattered for a hypothetical PASS) |
| human approval action? | n/a — REJECT cannot be approved |

## 2. Evidence artifacts (this sprint's output)

| artifact | path |
|---|---|
| Sprint plan | [`ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_PLAN.md) |
| Data provenance | [`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md) |
| Walk-forward plan | [`CAMPAIGN_010_WALK_FORWARD_PLAN.md`](CAMPAIGN_010_WALK_FORWARD_PLAN.md) + `backtests/CAMPAIGN_010_session_breakout/walk_forward/plan.{json,md}` |
| Per-fold execution | [`CAMPAIGN_010_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_010_WALK_FORWARD_EXECUTION.md) + `backtests/CAMPAIGN_010_session_breakout/folds/...` |
| Walk-forward verdict | [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md) + `backtests/CAMPAIGN_010_session_breakout/walk_forward/{results.json,results.md,fold_detail.json}` |
| Financing overlay | [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md) + `backtests/CAMPAIGN_010_session_breakout/financing/{financing_run.json,financing_run.md,financing_summary.json}` |
| Portfolio-risk diagnostics | [`CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md) + `backtests/CAMPAIGN_010_session_breakout/risk/{diagnostics.json,diagnostics.md}` |
| Independent verifier status | [`CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md) |
| Evidence summary | [`CAMPAIGN_010_EVIDENCE_SUMMARY.md`](CAMPAIGN_010_EVIDENCE_SUMMARY.md) (this sprint's Phase 8) |
| Sprint summary | [`ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md) |

## 3. Prior scaffold artifacts (still authoritative)

| artifact | path |
|---|---|
| Pre-commit checklist | [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md) (gates referenced verbatim) |
| Implementation spec | [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md) |
| Scaffold-sprint plan | [`ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md) |
| Scaffold-sprint summary | [`ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md) |
| Strategy module | [`src/forex_bot/strategies/session_breakout.py`](../../src/forex_bot/strategies/session_breakout.py) |
| Strategy unit tests | [`tests/unit/test_session_breakout.py`](../../tests/unit/test_session_breakout.py) |
| Strategy config sub-model | [`src/forex_bot/config.py`](../../src/forex_bot/config.py) (`SessionBreakoutStrategyConfig`) |
| Research config | [`configs/campaign_010_session_breakout.yaml`](../../configs/campaign_010_session_breakout.yaml) |
| Walk-forward readiness (preceding) | [`CAMPAIGN_010_WALK_FORWARD_READINESS.md`](CAMPAIGN_010_WALK_FORWARD_READINESS.md) |
| Financing + risk readiness (preceding) | [`CAMPAIGN_010_FINANCING_RISK_READINESS.md`](CAMPAIGN_010_FINANCING_RISK_READINESS.md) |
| Smoke result (preceding) | [`CAMPAIGN_010_SMOKE_RESULT.md`](CAMPAIGN_010_SMOKE_RESULT.md) |

## 4. Safety state (unchanged)

| dimension | status |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| CAMPAIGN_002 verdict | **REJECT** (untouched) |
| `session_breakout` in approved registry | **no** |
| `session_breakout` in any active loop | **no** |
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
| live-promotion financing blocker | stands |
| pytest baseline | **735 passes** (unchanged) |

## 5. Strategy registry impact (Phase 8 update)

Per the verdict and
[`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)'s status conventions,
`session_breakout 0.1.0-c010` is reclassified from
`candidate-scaffold (no verdict)` to **`rejected`**. The candidate
joins the existing rejected list with
CAMPAIGN_002/003/004/007/008/009. Approval is impossible for a
rejected candidate; any future variant would require a new
candidate identity (different name + version) with a fresh
discovery + design + pre-commit cycle.

## 6. Why the candidate failed

The hypothesis — that the London-session H4 close penetrating the
prior Asian-session H4 bar's range tends to *continue* through the
London/NY-overlap H4 bar — is **falsified by the data** on the
7-pair × 6-year universe under frozen parameters:

- The breakout direction does not persist on average; 75.5 % of
  trades hit the 6-bar time stop, and the realized R-distribution
  is negative.
- The only marginally positive pair (USD_CHF) flips to net
  negative under conservative-stress financing.
- The only marginally positive fold (fold 6) is below the per-fold
  expectancy R gate.

The candidate's failure is **directional**, not the result of
unsafe risk posture, lookahead bug, or sample-size thinness.

## 7. Recommended next sprints

- **No re-attempt of this family.** Per
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
  §12, parameter-tweaking a rejected candidate is a curve-fitting
  anti-pattern.
- **Resume the candidate-discovery process at C2–C5** from
  [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
  via a new candidate discovery sprint with its own pre-commit
  and the same evidence discipline this sprint demonstrated.
- **`infra-ruff-up042-stress-enum-001`** — clean up the 11
  pre-existing UP042 findings in untouched files (carried forward
  from the prior sprint; documented in Phase 0 here).

## 8. Cross-links

- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_010_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_010_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_010_WALK_FORWARD_PLAN.md`](CAMPAIGN_010_WALK_FORWARD_PLAN.md)
- [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md)
- [`CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md)
- [`CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_PLAN.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
