# CAMPAIGN_013 Rejection Closeout

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-005`
`strategy_evidence: false`

Phase 1 binding closeout for **CAMPAIGN_013 /
`cross_pair_currency_strength_rotation 0.1.0-c013`** (the C6 cross-pair
currency-strength rotation candidate), codifying the REJECT verdict and
the off-limits parameter surface. **No CAMPAIGN_013 verdict artifact is
edited by this doc.** This doc binds future discovery sprints
(including the rest of discovery-005) against disguised retunes of the
cross-pair-rotation family.

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
> CAMPAIGN_012 / CAMPAIGN_013 all remain REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_011 is the **null baseline only**, not a trading candidate.

## 1. Why CAMPAIGN_013 was rejected (cited from prior evidence)

Sources of truth (untouched by this doc):

- [`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md) (Phase 5 verdict)
- [`CAMPAIGN_013_EVIDENCE_SUMMARY.md`](CAMPAIGN_013_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_013_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_013_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_013_FINANCING_OVERLAY.md`](CAMPAIGN_013_FINANCING_OVERLAY.md)
- [`CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md)
- [`CAMPAIGN_013_STATUS.md`](CAMPAIGN_013_STATUS.md)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md)

### 1.1 Evidence summary (verbatim from those docs)

| dimension | value |
|---|---|
| folds | 8 (rolling, frozen, 540/180/180/180 days; 2020-01-01 → 2026-05-20) |
| folds passing all per-fold gates | **0 / 8** |
| total trades across folds | **7,940** |
| aggregate expectancy R | **−0.0564** |
| aggregate profit factor | **0.000** (literally zero — 7 of 8 folds have PF 0.000) |
| aggregate return % (4 y) | **−113.36 %** |
| pairs_positive | **1 / 7** (USD_JPY at +0.0000 R — random-walk floor) |
| single_fold_dominance % | 22.34 % |
| single_pair_dominance % | 36.55 % (NZD_USD; ~36.8 % of portfolio loss) |
| financing cashflow (ESTIMATED baseline) | **−$139.99** |
| financing cashflow (conservative stress) | **−$139.99** (= baseline by source construction; debits-on-both-sides) |
| financing flip events | USD_JPY flips + → − under stress (`pairs_positive` 1/7 → 0/7) |
| rollover events | 7,154 |
| missing_rate_event_count | 0 |
| pre-financing aggregate trade PnL | **−$566.79** |
| post-financing aggregate trade PnL | **−$706.78** |
| cross-pair runner integration contract | **SATISFIED on all 8 folds** (common_index 1,825–1,848 H4 bars per fold) |
| `MAX_OPEN_POSITIONS_EXCEEDED` | **0** across all 56 pair-fold cells (per-pair runner architecture; portfolio-wide cap is not currently enforced) |
| risk diagnostics — 8 sanity checks | all PASS (diagnostic only; no diagnostic contradicts REJECT) |
| risk diagnostics — zero-trade cells | 29 / 56 pair-fold cells produced zero trades (cross-pair rotator did not pick certain pairs in certain folds) |
| verifier | did not run; not required for REJECT |
| `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001` | **deferred indefinitely** (would be larger than CAMPAIGN_012's extension due to cross-pair runner contract re-implementation) |

### 1.2 Inherited-gate vector (5 of 8 FAIL)

| gate | threshold | observed | result |
|---|---|---|:---:|
| `fold_pass_rate_eq_100pct` | = 100 % | 0 % | **FAIL** |
| `fold_count_ge_6` | ≥ 6 | 8 | PASS |
| `expectancy_r_ge_0p05` | ≥ 0.05 R | −0.0564 R | **FAIL** |
| `profit_factor_ge_1p10` | ≥ 1.10 | 0.000 | **FAIL** |
| `trade_count_ge_200` | ≥ 200 | 7,940 | PASS |
| `pairs_positive_ge_4_of_7` | ≥ 4 / 7 | 1 / 7 | **FAIL** |
| `single_fold_dominance_le_60pct` | ≤ 60 % | 22.34 % | PASS |
| `single_pair_dominance_le_40pct` | ≤ 40 % | 36.55 % | PASS |

### 1.3 Null-baseline comparison (binding)

CAMPAIGN_013 is **catastrophically worse than the CAMPAIGN_011 null
baseline on every binding axis**:

| metric | CAMPAIGN_011 | CAMPAIGN_013 | difference | indistinguishable from null? |
|---|---:|---:|---:|:---:|
| aggregate expectancy R | −0.0024 | **−0.0564** | −0.0540 | NO (~11 × ±0.005 half-band) |
| aggregate profit factor | 0.91 | **0.000** | −0.910 | NO (~9 × ±0.10 half-band) |
| aggregate return % | −0.53 % | **−113.36 %** | −112.83 pp | NO (~56 × ±2 pp half-band) |
| pairs_positive | 3 / 7 | **1 / 7** | −2 pairs | boundary (worse direction) |
| fold_pass_rate | 0 / 8 | **0 / 8** | 0 | YES (same as null) |

Classification: **REJECT** (NOT `REJECT_INDISTINGUISHABLE_FROM_NULL`
— the metrics diverge from null in the WORSE direction, far outside
the symmetric ±band). NOT `BLOCKED` (the cross-pair runner
integration contract was satisfied on all 8 folds; the REJECT is on
inherited gates alone).

### 1.4 Cross-pair runner integration contract (binding context)

The cross-pair runner integration contract was the **binding Phase 0
requirement** for CAMPAIGN_013's evidence sprint:

- Align all 7 pairs' completed H4 closes to a common timestamp index.
- Inject `cross_pair_closes` into each pair's strategy config / context.
- Ensure strategy sees completed-only close series for all required pairs.
- Fail closed if any pair missing / misaligned / non-finite / insufficient.
- If runner cannot satisfy this contract → classify as BLOCKED.

The runner **SATISFIED** the contract on **all 8 folds** (per
`CAMPAIGN_013_WALK_FORWARD_EXECUTION.md` §`cross_pair_diagnostics`,
`contract_satisfied = true`, `common_index_length = 1,825-1,848`).
Therefore the REJECT is on inherited gates alone, **not** on contract
failure.

## 2. Why CAMPAIGN_013 is rejected (the diagnosis, not just the gates)

| reason | detail |
|---|---|
| **Worse than null baseline** | CAMPAIGN_013's metrics are not merely "below the meaningful-improvement margin" — they are *far below the null floor* on three of four binding axes (expectancy 23 × worse than the half-band, PF 9 × worse, return 56 × worse) and equal-or-worse on the fourth (pairs_positive on the worse-direction boundary). The cross-pair rank-gap rule did not produce an edge; it produced anti-edge. |
| **Inherited gates failed** | 5 of 8 aggregate gates fail. The 3 that pass are structural (fold_count, trade_count, dominance) and would pass for any non-degenerate strategy that fires enough trades. |
| **Turnover amplified cost drag dramatically** | CAMPAIGN_013 placed 7,940 trades — ~6.7 × CAMPAIGN_011 (1,177) and ~2.1 × CAMPAIGN_012 (3,726). Each additional trade pays the same spread + slippage cost without an offsetting edge. The slope from CAMPAIGN_011 → CAMPAIGN_012 → CAMPAIGN_013 (trade count vs aggregate return) is monotonic and steep. |
| **Rank-gap rule produced too many trades** | The `\|rank(quote) − rank(base)\| ≥ 4` (inclusive) gate fires on a much wider H4-bar slice than the rotator hypothesis assumed; this is structural to the 8-currency rank metric, not a tunable threshold problem. |
| **Cross-pair ranking did not identify persistent edge** | Every per-fold expectancy is negative (range −0.1017 R to −0.0027 R). 7 of 8 folds have all trading pairs producing non-positive aggregate returns. The cross-sectional FX rank signal does not survive the 6-bar H4 holding horizon under the inherited cost model. |
| **USD_JPY at +0.0000 R is the random-walk floor** | The same near-exact-zero CAMPAIGN_011 surfaced (literally +0.0000) and CAMPAIGN_012 echoed (+0.0004). The cross-pair rotator's USD-relative ranking did not move USD_JPY off this floor — strong evidence the gate is not identifying a real directional edge for USD_JPY. |
| **NZD_USD catastrophe** | NZD_USD lost **41.76 %** over 4 years on 1,863 trades (−0.0897 R). The cross-pair rotator's USD-relative ranking pushed NZD_USD into trending periods that subsequently reversed; the 6-bar holding period magnified whipsaw losses. |
| **Per-pair direction implied by rotation is not edge-bearing** | By the time the rotator enters, the rank-gap-implied move has typically already played out on the H4 horizon; the holding period sits in mean-reversion / noise territory. |
| **`MAX_OPEN_POSITIONS_EXCEEDED = 0` is architectural, not a rescue lever** | The per-pair runner architecture means `max_open_positions = 1` is within-pair only; a portfolio-aware runner cap would cut trade count by ~40 % (via simultaneous-signal filtering) but cannot rescue per-pair negative expectancy (6 of 7 pairs negative). The standing rule "do not relax `max_open_positions` to rescue trade count" remains intact and was not violated. |
| **Financing strictly worsens** | Conservative-stress overlay adds −$139.99 drag (vs CAMPAIGN_011's −$24.38), flips USD_JPY + → − and `pairs_positive` 1/7 → 0/7. No pair flips − → + under financing. |

## 3. Parts of the cross-pair-rotation family now OFF-LIMITS to immediate retune

The following parameter surface is **closed**. Any subsequent
discovery sprint that proposes a new candidate must NOT propose a
variant that differs only by tuning one or more of these:

| parameter | CAMPAIGN_013 value | off-limits scope |
|---|---|---|
| `currency_strength_lookback_bars` | 24 | sweeping the lookback (e.g. 12, 16, 32, 48) |
| `rank_gap_threshold` | 4 (inclusive; on a 0–7 rank space) | sweeping the threshold (e.g. 3, 5, 6); inverting the inequality |
| `atr_lookback` (H4 ATR for stop) | 14 | sweeping (8, 20, 28) |
| `atr_stop_multiple` | (per the implementation spec) | sweeping (1.5, 2.5, 3.0) |
| `max_bars_in_trade` | 6 | sweeping (4, 8, 10, 12) |
| `re_entry_block_bars` | (per the implementation spec) | sweeping |
| **adding any pair filter** | (no per-pair carve-out) | "trade only USD_JPY", "exclude NZD_USD", any per-pair carve-out motivated by CAMPAIGN_013's per-pair output |
| **adding any currency filter** | (8-currency strength uses all G8) | "exclude AUD / NZD because they were worst" |
| **adding any session filter on top of the rotator** | none in v1 | "only HIGH-VOL hours", "only London window" — would inherit the CAMPAIGN_010 session-breakout family's also-rejected lineage |
| **adding any regime filter on top of the rotator** | none in v1 | "only HIGH-VOL regime + cross-pair rotation" — would inherit CAMPAIGN_012's also-rejected regime-switcher lineage |
| **swapping the ranking metric to a near-cousin** | 24-bar log-return strength | swapping to "24-bar realized-vol strength", "24-bar Sharpe", "24-bar Z-score of return" — same hypothesis, different lens |
| **inverting the rotation direction** | long strong-base / short strong-quote | "long weak-base / short weak-quote (mean-revert the rank)" — result-driven inversion |
| **`max_open_positions` relaxation** | within-pair = 1 | relaxing within-pair, OR relaxing the *currently-unenforced* portfolio-wide cap to "rescue" trade count (forbidden; standing rule) |
| **changing the universe** | 7-pair OANDA practice H4 majors | switching to a 6-pair / 4-pair / 10-pair subset to "exclude NZD_USD-style catastrophes" — universe is part of family identity per `REJECTED_FAMILY_OVERFIT_GUARDRAILS.md` §3 |

**Disqualified variants** (illustrative, non-exhaustive):

- `cross_pair_currency_strength_rotation 0.2.0-c014` with `rank_gap_threshold = 3` (looser) or `5` (tighter)
- `cross_pair_currency_strength_rotation` with `currency_strength_lookback_bars = 12` or `48`
- `cross_pair_currency_strength_rotation_pair_filtered` restricting to USD_JPY only
- `cross_pair_currency_strength_rotation_excl_nzd` dropping NZD_USD because of its 41.76 % loss
- `cross_pair_currency_strength_rotation_session_filtered` combining C6 + CAMPAIGN_010's London window
- `cross_pair_currency_strength_rotation_regime_filtered` combining C6 + CAMPAIGN_012's HIGH-VOL gate
- `cross_pair_currency_strength_rotation_inverted` trading mean-reversion of the rank
- `cross_pair_currency_strength_rotation_realized_vol_rank` swapping the ranking metric
- `cross_pair_currency_strength_rotation_portfolio_capped` adding a portfolio-wide `max_open_positions = 1` to cut trade count

All of these would be **the same family + a knob** (or a rejected-
family stack). Each would require a brand-new discovery cycle with
an independent hypothesis (see §5).

## 4. Legitimate future research vs illegitimate "same idea, new knobs"

| illegitimate (forbidden by this closeout) | legitimate (would still need its own discovery cycle) |
|---|---|
| any retune of CAMPAIGN_013's frozen parameters | a different **hypothesis** about *why* a signal should work (e.g. "low-frequency carry / event-window structural anomaly with pre-declared low turnover budget") |
| restricting the universe to the pairs that produced positive expectancy in CAMPAIGN_013 (USD_JPY only) | a fundamentally different **data-generating mechanism** (e.g. interest-rate-differential overlay with MODELED financing, or scheduled-event window mean reversion with calendar data) |
| adding session / day-of-week / regime filters on top of C6 to "rescue" specific folds | a different **signal family** (e.g. paired straddle on event-window vol expansion; structural cost-aware mean reversion) |
| using a different rank-gap threshold because 4 didn't work | a different **timeframe + universe** combination not yet tested under the same null-baseline framework (e.g. D1 + cross-pair, M30 + majors with proven low-turnover) |
| inverting the rotation to trade rank-mean-reversion instead of rank-momentum | a different **cross-sectional concept** not based on USD-relative log-return ranks (e.g. realized-vol parity across pairs as a *position-sizing* feature, never as an entry trigger) — but only with an independently-derived hypothesis |
| swapping the ranking metric (vol-rank, Sharpe-rank, Z-rank) | None — these are all the same C6 hypothesis with a different ranking projection; the underlying "cross-sectional rank signal on H4 majors" was falsified |
| selecting a new family because its mechanism "would have rescued fold 6" or "would have made USD_JPY positive" | family selection from the **distinctness rubric** (per `REJECTED_FAMILY_OVERFIT_GUARDRAILS.md` §6 + `REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md` §3 + this sprint's Phase 3 addendum), with no reference to CAMPAIGN_013's per-day, per-fold, or per-pair output beyond "this family is REJECTED" |

The line is: **does the new candidate's hypothesis exist independent
of CAMPAIGN_013's result?** If the new hypothesis is "fix CAMPAIGN_013
by X" or "CAMPAIGN_013 would have worked if Y", it is forbidden.

## 5. Cooldown rule for the cross-pair-rotation family

**No `cross_pair_currency_strength_rotation` variant — or any near-
cousin cross-sectional FX-rank candidate — should be considered again
unless a future human explicitly authorizes a materially different
cross-sectional FX thesis.**

"Materially different" means:

- A **cross-sectional concept** that is not USD-relative log-return
  rank (e.g. realized-vol-parity sizing across pairs as a
  *position-sizing* feature on top of a separately-justified entry
  signal; correlation-regime classification across pairs as a *filter*
  conditional on a separately-justified entry).
- A **trigger mechanism** that is not "long-strong-base / short-
  strong-quote on rank-gap ≥ N" (e.g. event-window calendar trigger
  *conditional on* a separately-defined cross-sectional state; weekly
  re-balance toward parity weights with H4 execution and pre-declared
  low turnover).
- A **universe / timeframe** combination that the current CAMPAIGN_013
  evidence cannot speak to (e.g. D1 + cross-pair rotation with a
  weekly hold; M30 with a much higher signal threshold).

Even a "materially different" cross-sectional variant must:

1. Pass a fresh discovery sprint with its own hypothesis pre-commit
   (no copy-paste from CAMPAIGN_013).
2. **Pre-declare an expected trade-count budget** and explicitly explain
   why the resulting turnover survives the inherited cost model (the
   binding turnover-amplification anti-pattern; Phase 2 of this sprint).
3. Beat the CAMPAIGN_011 null-baseline margins (≥ +0.0524 R aggregate
   expectancy, ≥ +0.19 PF, ≥ +5 pp aggregate return, ≥ +1 pair, 100 %
   fold pass rate).
4. Survive the full six-evidence ladder.

**The discovery-005 sprint must not propose any cross-pair-rotation
variant** (cooldown is binding for at least the next 3 discovery
sprints, or until the explicit human-authorized "materially
different" criteria above are met).

## 6. How CAMPAIGN_013 rejected evidence should (and should not) be used

### 6.1 Legitimate uses

- **Historical rejected evidence:** cite CAMPAIGN_013 as the
  canonical example of "turnover-amplifying filter on top of a
  negative-edge entry direction that produced anti-edge" in future
  overfit-guardrail docs.
- **Warning against cross-sectional FX-rank assumptions:** the
  premise "cross-pair rank-gap rotation is a positive-edge signal on
  H4 majors after costs" is falsified; future hypotheses that quietly
  inherit this premise must explicitly justify why CAMPAIGN_013's
  falsification does not apply.
- **Comparison baseline for future hypotheses on the same data:**
  any future candidate that *also* fires on H4 majors with the same
  cost model must demonstrably outperform CAMPAIGN_013's −0.0564 R
  aggregate expectancy AND CAMPAIGN_012's −0.0521 R AND CAMPAIGN_011's
  −0.0024 R null floor.
- **Turnover-amplification reference point:** CAMPAIGN_013's 7,940-
  trade / −113.36 % data point anchors the upper end of the turnover-
  amplification slope (Phase 2 of this sprint codifies the slope).
- **Cross-pair runner contract reference:** the runner's `cross_pair_
  diagnostics` and `common_index` semantics are reusable for any
  *future* cross-sectional candidate that survives §5's "materially
  different" gate — the contract pattern is good, only the C6 signal
  is bad.
- **Verifier-extension justification:** if a *materially different*
  future candidate reaches `RESEARCH_PASS_UNAPPROVED`, the CAMPAIGN_013
  REJECT becomes part of the rejected-family corroboration set
  (alongside CAMPAIGN_002 / 010 / 011 / 012).

### 6.2 Illegitimate uses (binding)

- **Do not retrofit CAMPAIGN_013's per-fold or per-pair winners** to
  motivate a new candidate. Fold 6's USD_JPY +0.0000 R or fold 6's
  PF 0.126 are noise within a rejected aggregate.
- **Do not "fix" CAMPAIGN_013** with any of the disqualified variants
  in §3.
- **Do not present CAMPAIGN_013's cross-pair rank feature as "almost
  working"** — it is fully tested and falsified.
- **Do not treat USD_JPY's +0.0000 R as a positive signal** — it is
  the random-walk floor (CAMPAIGN_011 had literally +0.0000;
  CAMPAIGN_012 had +0.0004; CAMPAIGN_013 also +0.0000).
- **Do not select a pair-only rescue candidate** from CAMPAIGN_013's
  per-pair table. NZD_USD's −41.76 % means "drop NZD_USD" is exactly
  Pattern G (result-driven family selection).
- **Do not relax `max_open_positions`** to rescue trade count, even
  though the per-pair runner currently does not enforce a portfolio-
  wide cap. The standing rule applies regardless of where the cap
  sits in the architecture.
- **Do not modify the cross-pair runner integration contract** based
  on CAMPAIGN_013's result. The contract is sound; the C6 signal it
  fed is the rejected component.

## 7. No campaign verdict changes

This closeout does not edit any of:

- `docs/research/CAMPAIGN_013_WALK_FORWARD_RESULT.md`
- `docs/research/CAMPAIGN_013_EVIDENCE_SUMMARY.md`
- `docs/research/CAMPAIGN_013_STATUS.md`
- `docs/research/CAMPAIGN_013_FINANCING_OVERLAY.md`
- `docs/research/CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md`
- `docs/research/CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md`
- `docs/research/EVIDENCE_MANIFEST.json` CAMPAIGN_013 entry
- `docs/research/EVIDENCE_INDEX.md` CAMPAIGN_013 sub-section
- `docs/research/STRATEGY_STATUS.md` `cross_pair_currency_strength_rotation 0.1.0-c013` row

The Phase 5 verdict (`REJECT`) stands and is the final research
verdict for `cross_pair_currency_strength_rotation 0.1.0-c013`.
CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 / CAMPAIGN_012 verdicts
also unchanged.

## 8. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| this sprint's broker call | none |
| `.env` read / credential printed | none |
| account / order / trade / position / transaction endpoint queried | none |
| pytest baseline | 875 (preserved) |
| ruff baseline | 3 pre-existing (unchanged) |

## 9. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md) (Phase 0 of this sprint)
- [`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md) (the verdict this closeout codifies)
- [`CAMPAIGN_013_EVIDENCE_SUMMARY.md`](CAMPAIGN_013_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_013_FINANCING_OVERLAY.md`](CAMPAIGN_013_FINANCING_OVERLAY.md)
- [`CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (null baseline; binding)
- [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md) (sibling closeout template)
- [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md) (earlier closeout template)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md) (cross-cutting guardrails)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md) (Patterns H–L from discovery-004)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) (Phase 2 of this sprint — to be written)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) (Phase 3 of this sprint — to be written)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md) (the binding spec the rejected candidate implemented)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
