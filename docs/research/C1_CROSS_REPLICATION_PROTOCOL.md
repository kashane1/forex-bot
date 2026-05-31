# C1 Cross-Replication — Pre-Registration Protocol

**Sprint:** `research-c1-cross-replication-screen-001` · Phase 1
**Status:** **PRE-REGISTERED AND FROZEN as of this commit.** Every element below
is locked *before* any cross datum is read. No element may change after data
review (hard rule). Any deviation discovered during execution must be recorded as
a deviation in the result doc, not silently applied.
**Date:** 2026-05-30.

This is a **replication** protocol: the only thing that differs from the original
C1 majors run is the **instrument list**. All analysis parameters are copied
verbatim from the locked `forex_bot.research.c1_factor_validation.BASELINE` spec
and `m1_response_matrix` constants (audited in Phase 0).

---

## 1. Instrument universe (frozen)

The 8 first-wave populated non-USD crosses, partitioned exactly as the prompt
specifies. **All 8 are analyzed**; the required/optional split governs how the
verdict is weighted (the verdict's sign/null criteria are evaluated primarily on
the 4 required, with the optional 4 as corroboration).

**Required (4):**
- EUR_GBP
- EUR_JPY
- GBP_JPY
- AUD_JPY

**Optional (4):**
- NZD_JPY
- EUR_CHF
- GBP_CHF
- EUR_AUD

Control/reference: the existing **7-major** C1 artifacts (already committed under
`docs/research/c1_validation/`) are the comparison baseline — **not** re-run, not
re-tuned.

## 2. Factor definition (frozen — verbatim from `C1Spec` BASELINE)

| Element | Frozen value |
|---|---|
| EMA fast / slow | **20 / 50** |
| EMA50 slope lookback | **3** completed bars |
| `trend` leg rule | close vs EMA50 **AND** EMA50 slope in trend direction |
| `aligned` leg rule | close vs EMA50 only |
| Confluence legs (slowest→fastest) | **H4 = trend, H1 = trend, M15 = aligned** |
| Both sides | C1_trend_cont_**long** (bullish confluence) and `_short` (mirror) |
| Trigger | **rising-edge** of the full confluence (not persistence) |
| Cooldown | **60 min** minimum between accepted events |

No EMA, slope, leg, side, or trigger parameter changes for any cross.

## 3. Thresholds (frozen)

C1 is a **confluence-state** factor, not a parameter-thresholded one — there is no
tunable entry threshold to freeze beyond the spec above. The only numeric
decision boundaries are the **verdict criteria**, frozen here:
- **Sign criterion:** C1_long 60-min signed mean **< 0** (reverts) counts as
  sign-replicating per pair.
- **Null-separation criterion:** **|matched-Z| ≥ 2.0** at 30 or 60 min counts as
  clearing the null per pair.
- **Strong-significance reference:** |matched-Z| ≥ 3.0 (the bar EUR_USD/USD_JPY
  cleared on majors).
These boundaries are fixed now and applied mechanically in Phase 5.

## 4. Look-ahead rules (frozen)

Inherited unchanged from the locked M1/HTF alignment framework:
- HTF (H4/H1/M15) state is assigned to an M1 timestamp using only **completed**
  HTF bars (the framework's lookahead-safe HTF→M1 alignment).
- Confluence is evaluated on the **rising edge** using bars available at event
  time; the **signed forward return** is measured strictly **after** the event
  timestamp.
- H4 is the **H4M1** materialized series (M1-derived, parity-verified) — the same
  source the majors used — never a peeked native H4.
- No future bar enters any indicator, trigger, or response computation.

## 5. Response windows (frozen)

- Horizons: **5, 10, 15, 30, 60 minutes** (primary reporting at **30 and 60**).
- Response = **signed forward mid return in pips**; negative = price moves
  *against* the confluence direction (the C1 reversion).
- Spread (`spread_close`) is captured per event for descriptive cost context
  **only** — it is **not** used to gate replication (tradability is out of scope).

## 6. Significance methodology (frozen)

- Per-event parametric **t-stat** and **P(neg)** at each horizon (as on majors).
- The **decisive** statistic is the **session-matched null Z** (`matched_z`,
  §7), not the parametric t — identical to the original C1 validation.
- **Multiple-comparison awareness:** with 8 crosses, a single pair clearing
  |mZ| ≥ 2 is treated as **selection noise**, not replication. Replication
  requires multiple pairs and a coherent sign pattern (codified in Phase 5).

## 7. Null methodology (frozen — identical to original C1 run)

- **Unconditional baseline:** the full signed-return distribution (mean/SD)
  ignoring confluence — the "is the pair just drifting?" reference.
- **Random null:** randomly placed pseudo-events (same count) → random-null mean
  per horizon.
- **Session-matched null:** pseudo-events drawn to **match the session/time-of-day
  distribution** of the real C1 events, removing session structure as a confound;
  yields `matched_null_mean`, `matched_null_std`, and **`matched_z` =
  (observed − matched_null_mean) / matched_null_std**.
- **Seeds: 60** (random + session-matched), the same count the original run used
  after confirming null-mean dispersion is stable to the 200-seed result within
  rounding.
- Driver: the **existing** `c1v.c1_nulls(...)` — reused unchanged.

## 8. Execution method (frozen)

- Reuse the **existing** `scripts/run_c1_factor_validation.py` with the pair set
  widened to the 8 crosses (the only change). It calls the locked `c1v`
  functions; it does **not** redefine the factor.
- Outputs land in `docs/research/c1_validation/{cross}_c1_events.csv`,
  `{cross}_c1_nulls.csv`, and a cross meta JSON — the same artifact schema as the
  majors, so every reported number is read **directly from committed CSVs**
  (artifact-first; verify CSV-on-disk before quoting any figure — the standing
  integrity rule).
- Robustness (Phase 4) uses the same one-knob-perturbation specs the majors used
  (`ROBUSTNESS_SPECS`), **as a stability check, never as optimisation.**

## 9. What is explicitly NOT allowed (post-data)

- No change to EMAs, slope, legs, horizons, cooldown, seeds, null design, or
  verdict boundaries after seeing a cross number.
- No dropping/adding a cross to improve a statistic (all 8 reported).
- No new threshold, filter, vol-cut, or pair-weighting invented to rescue a
  weak result — that would convert replication into a **C1 re-tune** (forbidden,
  `DO_NOT_REPEAT_LIST` §1).
- No tradability/net-of-cost gate decides the verdict (out of scope).

## 10. Frozen verdict map (applied mechanically in Phase 5)

| Verdict | Condition (on the 4 required, corroborated by optional 4) |
|---|---|
| **REPLICATION_SUCCESS** | majority-negative C1_long 60-min sign **and** |mZ|≥2 on multiple pairs **and** magnitude in the majors' band, not single-pair-driven |
| **PARTIAL_REPLICATION** | sign mostly stable **but** null-separation on only some pairs, or magnitude materially weaker — mixed |
| **REPLICATION_FAILED** | mixed/positive sign, or no pair clears |mZ|≥2, or effect is single-pair/regime-artifact |

This map is frozen. Phases 2–4 produce the evidence; Phase 5 applies this table
without further interpretation latitude.
