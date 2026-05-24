# Rejected-Family Overfit Guardrails — Discovery-005 Addendum

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-005`
`strategy_evidence: false`

Phase 3 addendum to
[`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
+ [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md).
Adds CAMPAIGN_013-specific guardrails so the discovery-005 sprint (and
future discovery sprints) cannot disguise a cross-pair-rotation retune
or a turnover-amplified variant as a new candidate. **Does not edit
the base guardrails doc or the discovery-004 addendum** — this is an
additive, citable addendum.

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 / 013 all
> remain REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`.

## 1. Updated "do not revive" list (now 7 rejected families + 1 null model)

| family | campaign | status | binding closeout |
|---|---|---|---|
| EMA-Donchian trend-following | CAMPAIGN_002 | REJECT | (CAMPAIGN_002 verdict + base guardrails §1) |
| ADX-gated trend-following | CAMPAIGN_003 | REJECT | same family + ADX knob; closeout-by-inclusion |
| volatility-breakout (compressed-ATR) | CAMPAIGN_004 | REJECT | CAMPAIGN_004 verdict |
| pullback-continuation | CAMPAIGN_007 | REJECT | CAMPAIGN_007 verdict |
| mean-reversion (range) | CAMPAIGN_008 / 009 | REJECT (research-only) | CAMPAIGN_008 / 009 verdicts |
| Asian-range London-open session breakout | CAMPAIGN_010 | REJECT | [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md) |
| daily-ATR-percentile regime switcher + H4 close-vs-close trend | CAMPAIGN_012 | REJECT | [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md) |
| **8-currency strength rank-gap cross-pair rotation** | **CAMPAIGN_013** | **REJECT** | **[`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md)** (new; Phase 1 of this sprint) |
| H4 deterministic-seed random-entry diagnostic anchor (null model) | CAMPAIGN_011 | REJECT (null) | structurally un-approvable by design; null-baseline only |

## 2. New disqualifying overfitting patterns from CAMPAIGN_013

These patterns are additive to the 7 codified in the base guardrails
doc (A–G), the 5 codified in the discovery-004 addendum (H–L), and
the 5 codified in this sprint's Phase 2 anti-pattern doc (M–Q). They
are specifically motivated by CAMPAIGN_013's outcome and the cross-
pair-rotation family's structural shape.

### 2.1 Pattern R — "same cross-pair rank gate, different threshold"

**Disqualified.** Proposing a cross-pair-rotation candidate that
uses the *same* rank metric (8-currency strength via USD-base / USD-
quote log-return aggregation) and the *same* signal-direction
mapping (long strong-base / short strong-quote) but a different
threshold value (e.g. rank_gap_threshold = 3, 5, 6, or any other
integer in [1, 7]).

**Why it's overfitting.** CAMPAIGN_013's `rank_gap_threshold = 4`
was **pre-committed** before any code precisely because sweeping the
threshold post-result would be the canonical anti-pattern. Re-running
with a different threshold is *seeing* the rejected result and
choosing a value that wouldn't have given it.

**Legitimate alternative.** A *materially different cross-sectional
concept* (per `CAMPAIGN_013_REJECTION_CLOSEOUT.md` §5 — "materially
different" means a cross-sectional concept that is not USD-relative
log-return rank).

### 2.2 Pattern S — "same cross-pair ranking metric, different lookback"

**Disqualified.** Proposing a candidate that uses the same 8-currency
strength rank shape (USD-base aggregation / USD-quote aggregation /
sign convention) but with a different lookback (e.g. 12 / 16 / 32 /
48 H4 bars instead of 24).

**Why it's overfitting.** CAMPAIGN_013's `currency_strength_lookback_
bars = 24` was pre-committed for the same reason. The **form** of the
ranking metric is the failing component on this universe; sweeping
the lookback is a knob sweep around a falsified mechanism.

**Legitimate alternative.** A cross-sectional signal that does not
reduce to "USD-relative N-bar log-return rank" — e.g. realized-vol-
parity-based position sizing on a *separately-justified entry
signal*; correlation-regime classification as a *filter*; carry-
ranked basket exposure (after MODELED financing unblock).

### 2.3 Pattern T — "same cross-pair rotator, pair-filtered after rejection"

**Disqualified.** Proposing a candidate that combines CAMPAIGN_013's
rotator with a pair filter (e.g. "trade only USD_JPY because it was
+0.0000 R", or "exclude NZD_USD because it lost 41.76 %", or "trade
only the 3 USD-quote pairs").

**Why it's overfitting.** This is result-driven pair selection
(Pattern G in base guardrails) + per-pair tuning (Pattern D in base
guardrails) + fitting to noise within a REJECT aggregate (Pattern L
in discovery-004 addendum) + pair-only survivor selection (Pattern P
in this sprint's Phase 2). It is also a universe change disguised as
a filter (per `REJECTED_FAMILY_OVERFIT_GUARDRAILS.md` §3, "universe
is part of family identity").

**Legitimate alternative.** None at this layer. Any sub-universe
candidate must have an independent hypothesis that *implies* the
sub-universe before any backtest fires; CAMPAIGN_013's per-pair
output cannot motivate the choice.

### 2.4 Pattern U — "same cross-pair rotator with session/regime rescue filter"

**Disqualified.** Proposing a candidate that combines CAMPAIGN_013's
rotator with a session filter (e.g. CAMPAIGN_010's London window) or
a regime filter (e.g. CAMPAIGN_012's HIGH-VOL gate) or a day-of-week
filter.

**Why it's overfitting.** This stacks rejected families. CAMPAIGN_010's
session-breakout family is REJECTED; CAMPAIGN_012's regime-switcher
family is REJECTED; CAMPAIGN_013's cross-pair rotator family is
REJECTED. Any combination is a triple-rejected stack, not a new
candidate. This is also a special case of Pattern K (rejected-family
stack) from the discovery-004 addendum, now extended to include
CAMPAIGN_013 as one of the rejected components.

**Legitimate alternative.** None at this combination level. Every
combination filter must be independently motivated by its own
hypothesis, and **every constituent rejected family must already be
out of cooldown** — which for CAMPAIGN_013 means at least 3 discovery
sprints from now (per Phase 1 cooldown rule).

### 2.5 Pattern V — "high-turnover variant of any rejected family"

**Disqualified.** Proposing any variant of any of the 7 rejected
families that **increases** the expected trade count materially
(e.g. ≥ 2 ×) without bringing an explicit per-trade expectancy
argument that survives the inherited cost model.

**Why it's overfitting.** This is a generalization of the turnover-
amplification anti-pattern (Phase 2 of this sprint, Pattern O). It
covers all rejected families, not just the cross-pair rotator, because
the empirical slope (CAMPAIGN_011 → 012 → 013) is mechanism-agnostic:
the cost-per-trade is roughly fixed regardless of which falsified
direction the strategy uses.

**Legitimate alternative.** A **lower-turnover** variant (≤ ~1,000
trades over 4 years on the 7-pair universe) is also disqualified
without a fresh hypothesis (per Patterns G + L) — but a lower-turnover
*genuinely new* candidate with a pre-declared expectancy budget that
survives costs is allowed (subject to all other guardrails).

### 2.6 Pattern W — "select new family because it fixes a CAMPAIGN_013 per-pair / per-fold artifact"

**Disqualified.** Selecting a new candidate family because the chosen
mechanism "would have rescued fold 6" (the least-bad CAMPAIGN_013
fold) or "would have moved USD_JPY off the random-walk floor" or
"would have prevented NZD_USD's 41.76 % loss".

**Why it's overfitting.** This is the CAMPAIGN_013-specialization of
Pattern L (discovery-004 addendum). The CAMPAIGN_013 fold-level and
pair-level results are part of a REJECTED aggregate; per-fold /
per-pair artifacts are noise. Selecting a family to fit those
artifacts is fitting to noise.

**Legitimate alternative.** Select a family because its **prior
hypothesis** (existing in the literature, in protocol docs, or in
documented economic reasoning **independent of CAMPAIGN_013**) is
sound — then test it. The hypothesis must be writable without
reference to CAMPAIGN_013's per-fold or per-pair detail.

## 3. What counts as a "genuinely new" candidate after CAMPAIGN_013

A candidate proposal is **genuinely new** (and may be evaluated)
only if **all** of the following hold:

| criterion | bar to clear |
|---|---|
| **different primary hypothesis** | the candidate's hypothesis can be written without referencing CAMPAIGN_002 / 010 / 011 / 012 / 013 verdict numbers or per-fold / per-pair detail |
| **different data-generating mechanism** | the candidate's signal does not reduce to "directional H4 close-vs-close trend filter" or "H4 session breakout" or "D1AGG ATR percentile gate" or "8-currency strength rank gate" or "random Bernoulli draw" |
| **different signal family** | the candidate is not a re-parameterization of a rejected family (per the off-limits list in §1 + each rejected family's binding closeout) |
| **not merely a different cross-pair rank threshold or lookback** | no sweep of any of the CAMPAIGN_013 frozen parameters in §3 of [`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md) |
| **not a rejected-family stack** | the candidate is not a combination of multiple rejected families' filters (per Patterns K + U) |
| **survives the null-baseline-comparison-must-bind test** | the candidate's evaluation plan binds the CAMPAIGN_011 meaningful-improvement margins before any backtest fires |
| **no result-driven pair / currency / session / day carve-outs** | the universe is the same 7-pair H4 OANDA-practice universe (or a *different* universe that the rejected-family evidence does not speak to, e.g. M30, D1, weekly); no carve-outs that mirror CAMPAIGN_013 winners / losers |
| **explicit turnover budget** | the candidate's pre-commit binds a turnover-budget range, a derivation, and a rejection rule per [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) §4 |
| **explicit cost section** | the candidate's proposal includes the per-trade cost section required by Pattern Q |
| **not a high-frequency H4 firehose** | the candidate's expected trade count is below the Pattern M ceiling (≤ ~16,000 over 4 years on the 7-pair universe) |
| **not a broad simultaneous multi-pair entry without portfolio-level edge proof** | per Pattern N — either single-pair, or with an explicit portfolio-level expectancy hypothesis |

Failing any criterion disqualifies the candidate.

## 4. Concrete examples — what passes / fails

### 4.1 Pass examples (illustrative; **not** endorsements — each still needs its own discovery sprint)

- **"Calendar-event window anomaly with pre-declared low turnover"** —
  trades only during a small, pre-committed set of high-impact event
  windows (e.g. NFP, FOMC, ECB, BoJ, BoE), expected ~150 – 400 trades
  over 4 years (well below CAMPAIGN_011 null), single-pair single-
  position, with an event-window calendar fixture. Different signal
  family (calendar-conditional, not price-only); explicit low turnover;
  not a rejected-family retune. (Requires a small new committed
  calendar fixture; no broker call.)
- **"Weekly-bias H4-execution candidate"** — derives a weekly bias
  signal from completed weekly closes and executes one entry per pair
  per week at the start of the trading week, expected ~50 – 350 trades
  over 4 years (well below null). Different timeframe basis (weekly);
  explicit low turnover; not a rejected-family retune.
- **"Carry-aware long-only AUD/NZD overlay"** — explicitly conditional
  on MODELED financing being LIFTED first (infra-A); different
  mechanism (carry, not momentum); explicit low turnover; blocked
  until MODELED-financing infra unblock.

### 4.2 Fail examples (illustrative)

- "Cross-pair currency-strength rotation with `rank_gap_threshold = 3`
  instead of 4" → Pattern R.
- "Cross-pair currency-strength rotation with `currency_strength_
  lookback_bars = 48` instead of 24" → Pattern S.
- "Cross-pair currency-strength rotation restricted to USD_JPY (the
  least-bad pair)" → Pattern T + G + P.
- "Cross-pair currency-strength rotation excluding NZD_USD (the
  worst pair)" → Pattern T + G + P.
- "Cross-pair currency-strength rotation + London session filter" →
  Pattern U (rejected-family stack: C6 + CAMPAIGN_010).
- "Cross-pair currency-strength rotation + HIGH-VOL regime filter" →
  Pattern U (rejected-family stack: C6 + CAMPAIGN_012).
- "Trend-following 0.3.0 with H4 trigger every bar (much higher
  trade count than 0.1.0)" → Pattern V (high-turnover variant of
  rejected family).
- "New family that adds a cross-pair rank filter to CAMPAIGN_012's
  regime switcher" → Pattern U + Pattern O (rejected + rejected stack
  + turnover amplification).
- "New family selected because it would have made USD_JPY positive
  in CAMPAIGN_013 fold 6" → Pattern W.
- "Random entry with `entry_probability = 0.10` (double CAMPAIGN_011's
  0.05)" → Pattern V (CAMPAIGN_011 retune; null model is permanently
  un-approvable per its design).

## 5. How this addendum integrates with prior guardrails

| guardrail | addendum effect |
|---|---|
| Base guardrails §1 "do not revive" list (5 families) | **now 8 entries** (CAMPAIGN_013 added, plus CAMPAIGN_012 from discovery-004, plus CAMPAIGN_011 null model retained) |
| Base guardrails §2 patterns A–G | unchanged; supplemented by H–L (discovery-004), M–Q (this sprint Phase 2), R–W (this addendum) |
| Base guardrails §3 universe-level | reinforced — CAMPAIGN_013's NZD_USD catastrophe specifically forbids "drop NZD_USD" universe carve-outs |
| Base guardrails §4 stop / exit / timeframe | unchanged; CAMPAIGN_013 used ATR-2 stops / 6-bar max hold (within the standing range) |
| Base guardrails §5 data / financing | unchanged; CAMPAIGN_013 used the same authorized data + financing source; MODELED remains refused at 4 layers |
| Base guardrails §6 selection-process | reinforced by §3 above ("genuinely new" criteria; now including turnover budget + cost section) |
| Base guardrails §7 verifier-coverage | unchanged; verifier remains capability-locked to CAMPAIGN_002; CAMPAIGN_013's `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001` is deferred indefinitely |
| Base guardrails §8 approval-process | unchanged; six-evidence ladder + human approval action |
| Discovery-004 addendum §1 do-not-revive list | now extended to include CAMPAIGN_013 |
| Discovery-004 addendum §2 patterns H–L | unchanged |
| Discovery-005 Phase 2 patterns M–Q | active and binding |
| **Discovery-005 Phase 3 patterns R–W (this addendum)** | active and binding |

## 6. Discovery-005-specific guardrails for this sprint

The discovery-005 sprint specifically must:

- **Phase 4 reassessment** must score each candidate against all 8
  rejected families + 1 null model (5 prior + CAMPAIGN_011 null +
  CAMPAIGN_012 + CAMPAIGN_013).
- **Phase 5 proposals** must each pass the §3 "genuinely new" criteria
  above (including the new turnover-budget and cost-section
  requirements).
- **Phase 6 selection** must explicitly cite which §3 criterion the
  selected candidate satisfies, and must explicitly call out which
  Patterns H–W (if any) the selected candidate could be *mistaken*
  for and why it is not.
- **Phase 7 design** must binding-commit the candidate's turnover-
  budget range, derivation, rejection rule, and per-trade cost
  section before any future backtest fires.

If Phase 6 selects infrastructure instead of a candidate, the
guardrails above apply to the *post-infrastructure candidate*
identified in Phase 8.

## 7. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| this sprint's broker call | none |
| `.env` read / credential printed | none |
| account / order / trade / position / transaction endpoint queried | none |
| pytest baseline | 875 (preserved) |
| ruff baseline | 3 pre-existing (unchanged) |

## 8. Cross-links

- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md) (base guardrails — Patterns A–G)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md) (CAMPAIGN_012 addendum — Patterns H–L)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) (Phase 2 of this sprint — Patterns M–Q)
- [`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md) (Phase 1 of this sprint; off-limits parameter surface)
- [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md) (earlier closeout)
- [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md) (earlier closeout)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md) (sprint plan)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
