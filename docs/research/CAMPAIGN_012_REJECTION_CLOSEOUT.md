# CAMPAIGN_012 Rejection Closeout

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-004`
`strategy_evidence: false`

Phase 1 binding closeout for **CAMPAIGN_012 /
`regime_switcher_atr_percentile 0.1.0-c012`**, codifying the REJECT
verdict and the off-limits parameter surface. **No CAMPAIGN_012
verdict artifact is edited by this doc.** This doc binds future
discovery sprints (including the rest of discovery-004) against
disguised retunes of the regime-switcher family.

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
> CAMPAIGN_012 all remain REJECT. `configs/approved_strategies.yaml`
> remains `approved: []`. CAMPAIGN_011 is the **null baseline only**,
> not a trading candidate.

## 1. Why CAMPAIGN_012 was rejected (cited from prior evidence)

Sources of truth (untouched by this doc):

- [`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md) (Phase 5 verdict)
- [`CAMPAIGN_012_EVIDENCE_SUMMARY.md`](CAMPAIGN_012_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_012_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_012_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_012_FINANCING_OVERLAY.md`](CAMPAIGN_012_FINANCING_OVERLAY.md)
- [`CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md)
- [`CAMPAIGN_012_STATUS.md`](CAMPAIGN_012_STATUS.md)

### 1.1 Evidence summary (verbatim from those docs)

| dimension | value |
|---|---|
| folds | 8 (rolling, frozen, 540/180/180/180 days; 2020-01-01 → 2026-05-20) |
| folds passing all per-fold gates | **0 / 8** |
| total trades across folds | **3,726** |
| aggregate expectancy R | **−0.0521** |
| aggregate profit factor | **0.034** |
| aggregate return % (4 y) | **−43.52 %** |
| pairs_positive | **1 / 7** (only USD_JPY at +0.0004 R — random-walk floor) |
| single_fold_dominance % | 28.54 % |
| single_pair_dominance % | 22.39 % |
| financing cashflow (estimated) | **−$65.07** |
| financing cashflow (conservative stress) | **−$65.07** (= estimated; conservative-stress source is the worst-case projection by construction) |
| missing_rate_event_count | 0 |
| risk diagnostics — 8 sanity checks | 8 / 8 PASS |
| risk diagnostics — distribution shape | uniform-noise-like (per-pair ratio 1.60; session distribution diffuse; 79.3 % time-stop exit) — **most resembles CAMPAIGN_011 null model**, not CAMPAIGN_010 |
| verifier | did not run; not required for REJECT |
| pre-financing aggregate trade PnL | −$217.58 |
| post-financing aggregate trade PnL | **−$282.65** |

### 1.2 Inherited-gate vector (5 of 8 FAIL)

| gate | threshold | observed | result |
|---|---|---|:---:|
| `fold_pass_rate_eq_100pct` | = 100 % | 0 % | **FAIL** |
| `fold_count_ge_6` | ≥ 6 | 8 | PASS |
| `expectancy_r_ge_0p05` | ≥ 0.05 R | −0.0521 R | **FAIL** |
| `profit_factor_ge_1p10` | ≥ 1.10 | 0.034 | **FAIL** |
| `trade_count_ge_200` | ≥ 200 | 3,726 | PASS |
| `pairs_positive_ge_4_of_7` | ≥ 4 / 7 | 1 / 7 | **FAIL** |
| `single_fold_dominance_le_60pct` | ≤ 60 % | 28.54 % | PASS |
| `single_pair_dominance_le_40pct` | ≤ 40 % | 22.39 % | PASS |

### 1.3 Null-baseline comparison (binding)

CAMPAIGN_012 is **worse than the CAMPAIGN_011 null baseline on every
binding axis**:

| metric | CAMPAIGN_011 | CAMPAIGN_012 | difference | indistinguishable from null? |
|---|---:|---:|---:|:---:|
| aggregate expectancy R | −0.0024 | **−0.0521** | −0.0497 | NO (21 × ±0.005 half-band) |
| aggregate profit factor | 0.91 | **0.034** | −0.876 | NO (9 × ±0.10 half-band) |
| aggregate return % | −0.53 % | **−43.52 %** | −42.99 pp | NO (22 × ±2 pp half-band) |
| pairs_positive | 3 / 7 | **1 / 7** | −2 pairs | boundary (worse direction) |
| fold_pass_rate | 0 / 8 | **0 / 8** | 0 | YES (same as null) |

Classification: **REJECT** (NOT `REJECT_INDISTINGUISHABLE_FROM_NULL`
— the metrics diverge from null in the WORSE direction, far outside
the symmetric ±band).

## 2. Why CAMPAIGN_012 is rejected (the diagnosis, not just the gates)

| reason | detail |
|---|---|
| **Worse than null baseline** | CAMPAIGN_012's metrics are not merely "below the meaningful-improvement margin" — they are *below the null floor itself* on three of four binding axes (expectancy, PF, return) and equal to it on one (fold pass rate, both 0/8). The regime gate did not produce an edge; it produced anti-edge. |
| **Inherited gates failed** | 5 of 8 aggregate gates fail (`fold_pass_rate`, `expectancy_r`, `profit_factor`, `pairs_positive`, plus per-fold implications). The 3 that pass are structural (fold_count, trade_count, dominance) and would pass for any non-degenerate strategy. |
| **Regime gate amplified cost drag** | CAMPAIGN_012 placed 3,726 trades vs CAMPAIGN_011's 1,177 — ~3.2 × as many. On the same cost model + universe, each additional trade pays the same spread + slippage. The percentile filter widened the trade window without improving signal quality. |
| **H4 close-vs-close trend confirmation did not produce edge** | The trend filter (`close[t] vs close[t-4]` with a 0.25 × ATR-fraction floor) catches noise as readily as signal on these majors. Per-pair expectancy is uniformly negative except USD_JPY (at the random-walk floor +0.0004 R). |
| **HIGH-VOL regimes are not trend-friendly on these majors at H4** | The implicit premise of the C3 hypothesis is falsified. High-vol periods on EUR/GBP/JPY/AUD/CAD/CHF/NZD often coincide with mean-reverting central-bank-event spikes, not persistent multi-day trends. |
| **USD_JPY at +0.0004 R is the random-walk floor** | The same near-exact-zero CAMPAIGN_011 surfaced (literally +0.0000). The regime gate's inability to move USD_JPY off this floor is evidence that the gate is not identifying a real directional edge. |

## 3. Parts of the regime-switcher family now OFF-LIMITS to immediate retune

The following parameter surface is **closed**. Any subsequent
discovery sprint that proposes a new candidate must NOT propose a
variant that differs only by tuning one or more of these:

| parameter | CAMPAIGN_012 value | off-limits scope |
|---|---|---|
| `daily_atr_lookback` | 14 | sweeping ATR window |
| `regime_lookback_days` | 60 | sweeping percentile lookback |
| `regime_percentile_threshold` | 0.70 | sweeping the cutoff (e.g. 0.65, 0.75, 0.80) |
| `min_close_move_atr_fraction` | 0.25 | sweeping the trend floor |
| `trend_lookback_h4_bars` | 4 | sweeping the lookback (e.g. 6, 8) |
| `atr_lookback` (H4 ATR for stop) | 14 | sweeping (8, 20, 28) |
| `atr_stop_multiple` | 2.0 | sweeping (1.5, 2.5, 3.0) |
| `max_bars_in_trade` | 6 | sweeping (4, 10) |
| **adding any pair filter** | `min_atr_pips = {}` (no per-pair floor) | "trade only USD_JPY", "exclude AUD_USD", any per-pair carve-out |
| **adding any session filter on top of the regime gate** | none in v1 | "only HIGH_VOL + London window", "only Asian-close regimes" — would inherit the CAMPAIGN_010 session-breakout family's also-rejected lineage |
| **adding any extra regime label** | binary HIGH/LOW only | "HIGH/MEDIUM/LOW with three thresholds" — same family with more knobs |
| **swapping the regime metric to a near-cousin** | D1AGG ATR-14 percentile | swapping to "D1AGG range percentile", "D1AGG realized-vol percentile", "H4 ATR percentile" — same hypothesis, different lens |
| **inverting the gate** | trade HIGH_VOL | "trade LOW_VOL instead" — would be a result-driven inversion, equally untested |

**Disqualified variants** (illustrative, non-exhaustive):

- "regime_switcher_atr_percentile 0.2.0-c013" with `regime_percentile_threshold = 0.80`
- "regime_switcher_range_percentile 0.1.0" using D1AGG range instead of ATR
- "regime_switcher_atr_percentile_session_filtered" combining C3 + CAMPAIGN_010's London-window
- "regime_switcher_atr_percentile_pair_filtered" restricting to USD_JPY only
- "regime_switcher_atr_percentile_inverted" trading LOW_VOL instead

All of these would be **the same family + a knob**. Each would require
a brand-new discovery cycle with an independent hypothesis (see §5).

## 4. Legitimate future research vs illegitimate "same idea, new knobs"

| illegitimate (forbidden by this closeout) | legitimate (would still need its own discovery cycle) |
|---|---|
| any retune of CAMPAIGN_012's 12 frozen parameters | a different **hypothesis** about *why* a signal should work (e.g. "cross-pair currency-strength rotation outperforms after intraday volatility shocks") |
| restricting the universe to the pairs that produced positive expectancy in CAMPAIGN_012 (USD_JPY only) | a fundamentally different **data-generating mechanism** (e.g. carry / interest-rate-differential overlay with MODELED financing) |
| adding session / day-of-week / pair filters on top of C3 to "rescue" specific folds | a different **signal family** (e.g. paired straddle on event-window vol expansion) |
| using a different ATR-percentile cutoff because 0.70 didn't work | a different **timeframe + universe** combination not yet tested (e.g. M30 cross-pair momentum) |
| inverting the gate to trade LOW-VOL instead of HIGH-VOL | a different **regime concept** not based on a single-pair volatility percentile (e.g. cross-asset correlation regime, term-structure-of-vol regime) — but only with an independently-derived hypothesis |

The line is: **does the new candidate's hypothesis exist independent
of CAMPAIGN_012's result?** If the new hypothesis is "fix CAMPAIGN_012
by X" or "CAMPAIGN_012 would have worked if Y", it is forbidden.

## 5. Cooldown rule for the regime-switcher family

**No `regime_switcher_atr_percentile` variant — or any near-cousin
regime-switcher candidate — should be considered again unless a
future human explicitly authorizes a materially different
regime-switching thesis.**

"Materially different" means:

- A **regime concept** that is not a single-pair volatility-percentile
  binary gate (e.g. cross-asset correlation, options-implied vol
  term structure, term-of-cycle macro regime).
- A **trigger mechanism** that is not "close-vs-close trend within
  the regime" (e.g. session-anchored breakout *only available
  conditional on a separately-defined regime*).
- A **universe / timeframe** combination that the current
  CAMPAIGN_012 evidence cannot speak to (e.g. M30 + cross-pair, D1AGG
  + commodity pairs only, weekly + a different cost model).

Even a "materially different" regime-switcher must:

1. Pass a fresh discovery sprint with its own hypothesis pre-commit
   (no copy-paste from CAMPAIGN_012).
2. Beat the CAMPAIGN_011 null-baseline margins (≥ +0.0524 R aggregate
   expectancy, ≥ +0.19 PF, ≥ +5.5 pp pairs-positive, ≥ +1 pair, 100 %
   fold pass rate).
3. Survive the full six-evidence ladder.

**The discovery-004 sprint must not propose any regime-switcher
variant** (cooldown is binding for at least the next 3 discovery
sprints, or until the explicit human-authorized "materially
different" criteria above are met).

## 6. How CAMPAIGN_012 rejected evidence should (and should not) be used

### 6.1 Legitimate uses

- **Historical rejected evidence:** cite CAMPAIGN_012 as the canonical
  example of "regime gate that amplified cost drag without
  improving signal quality" in future overfit-guardrail docs.
- **Warning against high-volatility regime gate assumptions:** the
  premise "high-vol periods on majors are trend-friendly at H4" is
  falsified; future hypotheses that quietly inherit this premise
  must explicitly justify why CAMPAIGN_012's falsification does not
  apply.
- **Comparison baseline for future hypotheses on the same
  data:** any future candidate that *also* fires on H4 majors with
  the same cost model must demonstrably outperform CAMPAIGN_012's
  −0.0521 R aggregate expectancy (alongside CAMPAIGN_011's null
  floor) to be informative.
- **Verifier-extension justification:** if a *materially different*
  future candidate reaches `RESEARCH_PASS_UNAPPROVED`, the
  CAMPAIGN_012 REJECT becomes part of the rejected-family corroboration
  set (alongside CAMPAIGN_002 / 010 / 011).

### 6.2 Illegitimate uses (binding)

- **Do not retrofit CAMPAIGN_012's per-fold or per-pair winners** to
  motivate a new candidate. Fold 3's EUR_USD +0.25 R / +2.36 % or
  fold 5's PF 1.36 are noise within a rejected aggregate.
- **Do not "fix" CAMPAIGN_012** with any of the disqualified variants
  in §3.
- **Do not present CAMPAIGN_012's regime feature as "almost working"**
  — it is fully tested and falsified.
- **Do not treat USD_JPY's +0.0004 R as a positive signal** — it is
  the random-walk floor (CAMPAIGN_011 had literally +0.0000).

## 7. No campaign verdict changes

This closeout does not edit any of:

- `docs/research/CAMPAIGN_012_WALK_FORWARD_RESULT.md`
- `docs/research/CAMPAIGN_012_EVIDENCE_SUMMARY.md`
- `docs/research/CAMPAIGN_012_STATUS.md`
- `docs/research/EVIDENCE_MANIFEST.json` CAMPAIGN_012 entry
- `docs/research/EVIDENCE_INDEX.md` CAMPAIGN_012 sub-section
- `docs/research/STRATEGY_STATUS.md` `regime_switcher_atr_percentile 0.1.0-c012` row

The Phase 5 verdict (`REJECT`) stands and is the final research
verdict for `regime_switcher_atr_percentile 0.1.0-c012`. CAMPAIGN_002
/ CAMPAIGN_010 / CAMPAIGN_011 verdicts also unchanged.

## 8. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 | all REJECT (untouched) |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| this sprint's broker call | none |
| `.env` read / credential printed | none |
| account / order / trade / position / transaction endpoint queried | none |
| pytest baseline | 818 (preserved) |
| ruff baseline | 3 pre-existing (unchanged) |

## 9. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md) (Phase 0 of this sprint)
- [`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md) (the verdict this closeout codifies)
- [`CAMPAIGN_012_EVIDENCE_SUMMARY.md`](CAMPAIGN_012_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (null baseline; binding)
- [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md) (sibling closeout template)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md) (cross-cutting guardrails)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md) (Phase 2 — to be written)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md) (the binding spec the rejected candidate implemented)
