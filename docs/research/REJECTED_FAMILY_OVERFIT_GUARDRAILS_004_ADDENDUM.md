# Rejected-Family Overfit Guardrails — Discovery-004 Addendum

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-004`
`strategy_evidence: false`

Phase 2 addendum to
[`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md).
Adds CAMPAIGN_012-specific guardrails so the discovery-004 sprint
(and future discovery sprints) cannot disguise a regime-switcher
retune as a new candidate. **Does not edit the base guardrails doc**
— this is an additive, citable addendum.

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
> CAMPAIGN_012 all remain REJECT. `configs/approved_strategies.yaml`
> remains `approved: []`.

## 1. Updated "do not revive" list (now 6 rejected families + 1 null model)

| family | campaign | status | binding closeout |
|---|---|---|---|
| EMA-Donchian trend-following | CAMPAIGN_002 | REJECT | (the family's design + REJECT trail in CAMPAIGN_002 docs) |
| ADX-gated trend-following | CAMPAIGN_003 | REJECT | same family + ADX knob; closeout-by-inclusion |
| volatility-breakout (compressed-ATR) | CAMPAIGN_004 | REJECT | CAMPAIGN_004 verdict |
| pullback-continuation | CAMPAIGN_007 | REJECT | CAMPAIGN_007 verdict |
| mean-reversion (range) | CAMPAIGN_008 / 009 | REJECT (research-only) | CAMPAIGN_008 / 009 verdicts |
| Asian-range London-open session breakout | CAMPAIGN_010 | REJECT | [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md) |
| **daily-ATR-percentile regime switcher + H4 close-vs-close trend** | **CAMPAIGN_012** | **REJECT** | **[`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md)** (new) |
| H4 deterministic-seed random-entry diagnostic anchor (null model) | CAMPAIGN_011 | REJECT (null) | structurally un-approvable by design; null-baseline only |

## 2. New disqualifying overfitting patterns from CAMPAIGN_012

These patterns are additive to the 7 already-codified patterns
(A–G in the base guardrails doc §2). They are specifically motivated
by CAMPAIGN_012's outcome.

### 2.1 Pattern H — "same regime gate, different threshold"

**Disqualified.** Proposing a regime-switcher candidate that uses
the *same* regime metric (D1AGG ATR percentile) and the *same* trend
filter shape (close-vs-close + ATR-fraction floor) but a different
threshold value (e.g. 0.65, 0.75, 0.80, or any other point in [0, 1)).

**Why it's overfitting.** CAMPAIGN_012's threshold (0.70) was
**pre-committed** before any code, exactly because sweeping the
threshold post-result would be the canonical anti-pattern. Re-running
with a different threshold is *seeing* the rejected result and
choosing a value that wouldn't have given it.

**Legitimate alternative.** A *materially different regime concept*
(see CAMPAIGN_012_REJECTION_CLOSEOUT §5 — "materially different"
means a regime metric that is not a single-pair vol percentile).

### 2.2 Pattern I — "same trend filter, different lookback"

**Disqualified.** Proposing a candidate that uses the same H4
close-vs-close trend filter as CAMPAIGN_012 (or CAMPAIGN_002 /
CAMPAIGN_010, which all reduce to a directional H4 trend confirmation
in some form) but with a different lookback (e.g. 2 / 3 / 6 / 8 H4
bars instead of 4).

**Why it's overfitting.** The CAMPAIGN_012 evidence shows that the
**form** of the trend filter (a fixed-lookback close-vs-close with
ATR-fraction floor) is the failing component on this universe + cost
model. Sweeping the lookback is a knob sweep around a falsified
mechanism.

**Legitimate alternative.** A signal that does not reduce to "current
close vs N-bar-prior close + threshold" — e.g. cross-pair relative
strength rotation, options-implied move proxy, calendar-event window.

### 2.3 Pattern J — "same daily-ATR-percentile, different cutoff"

**Disqualified.** Proposing a candidate that swaps the percentile
*direction* (e.g. trade LOW-VOL instead of HIGH-VOL) or the
percentile *shape* (e.g. 2-sided P15/P85 band, or a 3-level
HIGH/MED/LOW classifier with N-1 thresholds) on the same metric.

**Why it's overfitting.** The CAMPAIGN_012 result is that the metric
itself does not separate profitable from unprofitable bars. Inverting
or re-binning a metric that doesn't discriminate just rotates which
bars are filtered — not whether the filter works.

**Legitimate alternative.** A different regime *signal class*
(e.g. cross-asset correlation regime, term-structure-of-vol regime,
macro-state regime) with its own discovery sprint and independent
hypothesis.

### 2.4 Pattern K — "rescue a rejected regime switcher with session/pair/day filters"

**Disqualified.** Proposing a candidate that combines CAMPAIGN_012's
regime gate with a session filter (e.g. CAMPAIGN_010's London window)
or pair filter (e.g. USD_JPY only, or excluding the worst-performing
pairs from CAMPAIGN_012) or day-of-week filter.

**Why it's overfitting.** This stacks rejected families. CAMPAIGN_010's
session-breakout family is already REJECTED (see closeout); adding it
to CAMPAIGN_012's already-REJECTED regime switcher creates a
double-rejected combo, not a new candidate. Pair filters based on
CAMPAIGN_012's per-pair winners (USD_JPY's +0.0004 R) are
result-driven selection (already forbidden by Pattern G in the base
guardrails doc).

**Legitimate alternative.** None at this level of combination — every
combination filter must be independently motivated by its own
hypothesis, and every constituent rejected family must already be
out of cooldown.

### 2.5 Pattern L — "pick the new family because it fixes a CAMPAIGN_012 per-fold artifact"

**Disqualified.** Selecting a new candidate family because the
chosen mechanism "would have rescued fold 0" or "would have made
fold 5 a clean pass" or "would have moved USD_JPY off the random-walk
floor".

**Why it's overfitting.** This is result-driven family selection
(Pattern G). The CAMPAIGN_012 fold-level results are part of a
REJECTED aggregate; per-fold artifacts are noise. Selecting a family
to fit those artifacts is fitting to noise.

**Legitimate alternative.** Select a family because its **prior
hypothesis** (existing in the literature, in protocol docs, or in
documented economic reasoning **independent of CAMPAIGN_012**) is
sound — then test it. The hypothesis must be writable without
reference to CAMPAIGN_012's per-fold or per-pair detail.

## 3. What counts as a "genuinely new" candidate after CAMPAIGN_012

A candidate proposal is **genuinely new** (and may be evaluated)
only if all of the following hold:

| criterion | bar to clear |
|---|---|
| **different primary hypothesis** | the candidate's hypothesis can be written without referencing CAMPAIGN_002 / 010 / 011 / 012 verdict numbers or per-fold detail |
| **different data-generating mechanism** | the candidate's signal does not reduce to "directional H4 close-vs-close trend filter" or "H4 session breakout" or "D1AGG ATR percentile gate" or "random Bernoulli draw" |
| **different signal family** | the candidate is not a re-parameterization of a rejected family (per the off-limits list in §1 + each rejected family's binding closeout) |
| **not merely a different volatility threshold** | no sweep of any of the 12 frozen CAMPAIGN_012 parameters in §3 of [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md) |
| **not a rejected-family stack** | the candidate is not a combination of multiple rejected families' filters (per Pattern K above) |
| **survives the null-baseline-comparison-must-bind test** | the candidate's evaluation plan binds the CAMPAIGN_011 meaningful-improvement margins before any backtest fires |
| **no result-driven pair/session/day carve-outs** | the universe is the same 7-pair H4 OANDA-practice universe (or a *different* universe that the rejected-family evidence does not speak to, e.g. M30 + cross-pair); no carve-outs that mirror CAMPAIGN_012 winners/losers |

Failing any criterion disqualifies the candidate.

## 4. Concrete examples — what passes / fails

### 4.1 Pass examples (illustrative; **not** endorsements — each still needs its own discovery sprint)

- "Cross-pair currency-strength rotation: re-rank the 7 pairs by
  rolling-window relative strength, take a long-short pair against
  the index, no single-pair vol gate" — different signal family; not
  a rejected-family retune; depends on different data shape.
- "Options-event-window long-vol proxy: take a synthetic straddle
  proxy around scheduled NFP / FOMC events; entry triggered by a
  calendar feed; exit at event close + N hours" — different data
  source (calendar feed); not a price-only H4 momentum or regime
  signal.
- "Carry-aware long-only AUD/NZD overlay: explicitly conditional on
  MODELED financing being LIFTED first" — different mechanism
  (carry, not momentum); but blocked until MODELED-financing infra
  unblock is authorized.

### 4.2 Fail examples (illustrative)

- "Daily-ATR-percentile regime switcher with threshold 0.75 instead
  of 0.70" → Pattern H.
- "Daily-ATR-percentile regime switcher with `trend_lookback_h4_bars = 6`
  instead of 4" → Pattern I.
- "Daily-range-percentile regime switcher (range instead of ATR) with
  threshold 0.70" → Pattern J (same regime concept, different metric).
- "C3 + London-session filter" → Pattern K (rejected-family stack).
- "C3 restricted to USD_JPY (the only positive pair)" → Pattern G +
  Pattern L.
- "New family that adds a vol-percentile gate to CAMPAIGN_010's
  session breakout to rescue the rejected folds" → Pattern K (rejected
  + rejected stack).

## 5. How this addendum integrates with the base guardrails doc

| base guardrails item | addendum effect |
|---|---|
| §1 "do not revive" list (5 families) | now **7 entries** (CAMPAIGN_012 added; CAMPAIGN_011 null model retained) |
| §2 patterns A–G | unchanged; supplemented by H–L above |
| §3 universe-level guardrails | unchanged; universe stays 7-pair H4 OANDA practice unless a candidate explicitly tests a *different* universe (in which case it cannot use this 7-pair store's CAMPAIGN_002 / 010 / 011 / 012 evidence as positive support) |
| §4 stop / exit / timeframe guardrails | unchanged |
| §5 data / financing guardrails | unchanged; **MODELED financing remains refused at 4 layers**; any future candidate that depends on MODELED financing must explicitly select the financing-infra unblock path first |
| §6 selection-process guardrails | reinforced by §3 above ("genuinely new" criteria) |
| §7 verifier-coverage guardrails | unchanged; verifier remains capability-locked to CAMPAIGN_002 |
| §8 approval-process guardrails | unchanged; six-evidence ladder + human approval action |

## 6. Discovery-specific guardrails for this sprint

The discovery-004 sprint specifically must:

- **Phase 3 reassessment** must score each candidate against all 6
  rejected families + 1 null model (not just the older 5).
- **Phase 4 proposals** must each pass the §3 "genuinely new"
  criteria above.
- **Phase 5 selection** must explicitly cite which §3 criterion the
  selected candidate satisfies, and must explicitly call out which
  Patterns H–L (if any) the selected candidate could be *mistaken*
  for and why it is not.
- **Phase 6 design** must binding-commit the candidate's null-baseline
  comparison gate before any future backtest fires.

If Phase 5 selects infrastructure instead of a candidate, the
guardrails above apply to the *post-infrastructure candidate*
identified in Phase 7.

## 7. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 | all REJECT (untouched) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| this sprint's broker call | none |
| `.env` read / credential printed | none |
| account / order / trade / position / transaction endpoint queried | none |
| pytest baseline | 818 (preserved) |
| ruff baseline | 3 pre-existing (unchanged) |

## 8. Cross-links

- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md) (base guardrails; binding; this addendum is additive)
- [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md) (sibling closeout for the session-breakout family)
- [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md) (Phase 1 of this sprint; off-limits parameter surface)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md) (sprint plan)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
