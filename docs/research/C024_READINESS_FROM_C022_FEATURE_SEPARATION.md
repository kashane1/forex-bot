# C024 Readiness — from C022 Winner/Loser Feature Separation

**Status:** diagnostic decision memo. Approves nothing, changes no verdict,
tunes nothing, creates no campaign. No CAMPAIGN_024 is created here; any future
C024 must be **pre-committed in a separate sprint** before execution.

Inputs:
[`C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md`](C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md),
`research/c022_feature_separation/feature_separation_summary.json`.

## Decision

### `NOT_READY`

No structural entry-signal feature separates C022 winners from losers, so there
is **no evidential basis for a C024 entry-filter campaign that refines the
pullback-resolution signal**.

## Why

The readiness bar (from the sprint precommit) is `READY_FOR_PRECOMMIT` only if at
least one feature family:

1. separates winners/losers in **both** train and validation,
2. has plausible market logic,
3. is **not** just pair/session overfit,
4. does **not** rely on outcome leakage,
5. would materially reduce stop-outs **without** destroying sample size.

Against the evidence:

- **Structural entry-signal features fail (1).** Every feature the C022 thesis is
  actually built on is at AUC ≈ 0.50 (P[winner value > loser value]):
  - H4 regime: `h4_adx_at_entry` 0.515/0.501, `h4_bias_score` 0.515/0.484
    (direction not even stable), `h4_ema_slope_atr` 0.500/0.497,
    `h4_close_dist_ema50_atr` 0.544/0.555.
  - H1 pullback: `h1_pullback_depth_atr` 0.545/0.537, `h1_rsi_at_entry`
    0.509/0.501, `h1_close_dist_ema50_atr` 0.503/0.524.
  - M15 trigger: `m15_reclaim_distance_atr` 0.494/0.485, `m15_adx_at_entry`
    0.504/0.521, `m15_body_atr` 0.497/0.478.

  The strongest **stable signal-quality** effect is `h4_close_dist_ema50_atr` at
  |AUC−0.5| = 0.044 — below the 0.05 negligibility floor. There is essentially no
  univariate winner/loser signal in the entry features.

- **The only separators above the floor are context, and they fail (2)/(3)/(5):**
  - `spread_to_atr_pct` (cost), |AUC−0.5| = 0.077 — the largest effect, but it is
    **mechanical**: cost is subtracted directly from net R, so low-cost trades win
    more by construction. This is cost management, not an entry edge, and filtering
    on it does not fix the signal.
  - `atr_at_entry` (volatility), 0.068, and `hour` (time-of-day), 0.074 — both
    weak (AUC ≲ 0.58), plausible but generic context effects. Selecting a
    volatility or hour cut from this same dataset would be picking a post-hoc
    threshold on a weak effect — overfitting, not edge (violates (3)). Neither is a
    structural improvement to the pullback-resolution signal, and a volatility/hour
    filter that moved win-rate by ~5–6 AUC points would not plausibly turn a
    REJECT expectancy positive while keeping a usable sample (violates (5)).

- The diagnostic labels are post-hoc by construction and were kept strictly
  separate from features (no leakage — (4) is satisfied), but that does not rescue
  the decision because (1) already fails for signal-quality features.

## C023 (ADX22 sibling) — execute / defer recommendation

**Defer, and consider retiring.** C023's *only* change vs C022 is raising the H4
directional-bias ADX gate from 20.0 → 22.0. But `h4_adx_at_entry` does **not**
separate winners from losers (AUC 0.515 train / 0.501 validation), and the
quintile win-rates by H4 ADX are flat (~0.30–0.35 across all quintiles). There is
therefore **no evidence** that a stricter H4 ADX gate would improve outcomes; it
would only shrink the sample. Executing C023 is not justified by this analysis.

## Family-level recommendation

**Pause / retire the C022–C023 pullback-resolution family.** The family's entry
features carry no winner/loser information at the univariate level, which is
consistent with — and sharpens — the prior conclusion that C022's failure is an
entry-edge / signal-quality failure, not a stop-placement problem. Continuing to
tweak gates on the same signal (C023 and any C024 of the same shape) is unlikely
to be productive.

## What is NOT being done (hard rules upheld)

- No CAMPAIGN_024 created; no C024 prompt, thesis numbers, or thresholds drafted.
- No C023 execution.
- No C022 retune; no verdict changed; no historical metric rewritten.
- No threshold from this data is proposed as a parameter.

## If a future entry-feature idea is ever pursued

Only as a **fresh, pre-committed** hypothesis in a separate sprint, and it should
look *structurally different* from "filter the existing pullback signal" — the
evidence here says that lever is empty. The weak volatility/time context effects
are at best low-priority, low-confidence leads and must not be threshold-mined
from this dataset; they would need an independent, out-of-sample pre-registration
to mean anything. Absent such an idea, the recommended next step is to retire the
pullback-resolution family rather than open C024.
