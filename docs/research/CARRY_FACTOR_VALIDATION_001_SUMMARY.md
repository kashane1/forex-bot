# Carry Factor-Validation 001 — Summary (Phase 9)

**Sprint:** `research-carry-factor-validation-001`
**Type:** gross, existence-level carry factor-validation. No campaign, no strategy, no
front gate, no tradability/financing study, no approval. Gross only.
**Date:** 2026-05-31.

---

## Verdict: `FACTOR_REAL_BUT_WEAK`

A genuine gross cross-sectional carry premium exists (+0.74%/quarter, correctly signed,
positive every year/regime, spec-robust, beats identity & unconditional nulls) — but it
is **mechanical accrual with no spot-predictive content**, marginally significant
(t=1.68), **single-name dependent** (drop-JPY → +0.0003), untimed, and crash-untested.
It cannot graduate to a front-gate candidate, and its positive part is precisely the
accrual a broker reclaims as financing.

## Commits by phase

| Phase | Commit | Content |
|---|---|---|
| 0 | `458767f` | baseline audit + plan |
| 1 | `cd25a76` | frozen protocol |
| 2 | `3cbfa35` | factor construction + study engine + tests |
| 3 | `43a67ee` | response study |
| 4 | `3ec133b` | cross-sectional validation |
| 5 | `0899d00` | null comparison |
| 6 | `08ae7aa` | robustness |
| 7 | `f5a240e` | verdict `FACTOR_REAL_BUT_WEAK` |
| 8 | `bc28fde` | implications + next prompt |
| 9 | _(this commit)_ | validation + summary |

## Carry-factor definition (frozen, Phase 1)

Currency cross-section over 8 currencies (USD numeraire; the 7 other currencies' returns
vs USD derived from the 7 real-data majors). At each month-end, rank the 8 by their
**FRED OECD 3-month interbank rate (1-month lag)**; **HML-3** = long top-3 / short
bottom-3, equal-weight, dollar-neutral, gross exposure 2; monthly rebalance. **Primary
metric:** total gross return = spot mid + accrued interbank carry (`yield·h/12`).
**Decisive cell:** currency HML-3, total, 3-month horizon. Secondary: 15-instrument layer
(cross returns reconstructed by no-arbitrage). 61 months (2021-05→2026-05). Seed 20260531.

## Response-study findings

- Currency HML-3 total mean rises with horizon: **+0.26% / +0.74% / +1.41% / +2.44%** at
  1/3/6/12m; NW-HAC t = 1.39 / **1.68** / 1.79 / 2.30 (only 12m clears 2, on ~4
  independent windows).
- **Spot-only (predictive) leg is statistically zero everywhere** (t = 0.12 / 0.10 / 0.01
  / −0.27; negative at 12m). ~94% of the 3m total is mechanical carry accrual. **Carry
  does not forecast spot direction.**
- Near-static signal (rank stability 0.984): a constant short-JPY/CHF/EUR vs
  long-USD/GBP/NZD tilt.

## Cross-sectional findings

- Slope of fwd-3m total on rate **+0.0031** (corr +0.48), correct sign — but driven by the
  **JPY short**: **drop-JPY collapses the premium +0.0075 → +0.0003.** High-yield longs
  did not appreciate (NZD spot −1.0%); the other funder CHF *appreciated* (contradicts
  carry). Positive every year (2022 flat +0.0004) and every regime; **no carry crash
  sampled** (H3 untestable). Instrument layer is concentrated short-JPY, not breadth.

## Null-comparison findings

- Beats randomized-rank (Z=**2.78**), matched-random (Z=**2.68**), and the unconditional
  baseline (+1.57%/qtr) → carry-identity carries information. **Fails shuffled-timestamp**
  (Z=**0.72**) → no timing content (degenerate for a 0.984-persistent signal: a static
  tilt). Holm-Bonferroni survives only vs the weak (accrual-beaten) randomized null at
  3/6/12m. By the frozen all-nulls bar, the primary cell does **not** meet the front-gate
  threshold.

## Robustness findings

- Sign/magnitude stable across k∈{2,3} (+0.0059/+0.0075), equal/rank weighting (+0.0062),
  lag∈{0,1,2}m (+0.0075/+0.0075/+0.0071) — not a single-cell or lookahead artifact. But
  **carry-momentum ranking flips negative (−0.0014)** (no dynamic form works), and the
  stable magnitude is one JPY short re-expressed (drop-JPY → ~0).

## Gate results (Phase 9)

| Gate | Result |
|---|---|
| `pytest tests/ -q` | **2454 passed** (2443 baseline + 11 new carry tests) |
| `ruff check src scripts tests` | new code **clean**; 5 **pre-existing** errors in `run_edge_discovery_vol_managed_tsmom.py` + `build_carry_rate_dataset.py` (untouched this sprint) |
| `check_research_freeze.py` | **ALL CHECKS PASSED** |
| `validate_research_archive.py` | **ALL CHECKS PASSED** |
| `scan_artifacts_for_secrets.py` | **PASSED** (no credential-shaped strings) |
| `git status --short` | clean |

## Compliance

- **No campaign created** (no CAMPAIGN_032 or any campaign).
- **No strategy / entry-exit / trading rules / front gate created.**
- **No strategy approved**; `approved: []`. **Paper/demo/live remain blocked.**
- **No broker API called; no OANDA financing data used.** Carry evaluated **gross only**;
  definitions unchanged after data review.

## Recommended next step

Do **not** open a financing-ingestion sprint for a strategy — the outcome is near-
predetermined `FINANCING_DEFEATED` (the gross premium *is* the accrual financing reclaims;
no spot-predictive residual). Carry was the last genuinely-new in-repo mechanism, so the
recommended next move is a **docs-only programme-direction decision sprint**
(`research-programme-direction-after-carry-001`): archive the in-repo factor search as
exhausted / reposition carry as a risk-context factor / spec a new external thesis /
optionally one cheap financing-defeat confirmation. Full prompt in
[NEXT_PROMPT_AFTER_CARRY_FACTOR_VALIDATION.md](NEXT_PROMPT_AFTER_CARRY_FACTOR_VALIDATION.md).

## Files to review first

1. [CARRY_FACTOR_VERDICT.md](CARRY_FACTOR_VERDICT.md) — the call and why.
2. [CARRY_FACTOR_RESPONSE_STUDY.md](CARRY_FACTOR_RESPONSE_STUDY.md) — the decisive
   accrual-vs-spot decomposition.
3. [CARRY_FACTOR_CROSS_SECTIONAL_VALIDATION.md](CARRY_FACTOR_CROSS_SECTIONAL_VALIDATION.md)
   — the drop-JPY single-name finding.
4. [CARRY_FACTOR_PROTOCOL.md](CARRY_FACTOR_PROTOCOL.md) — the frozen pre-registration.
5. `research/carry/factor_validation/carry_factor_validation.json` — all numbers on disk.
6. [NEXT_PROMPT_AFTER_CARRY_FACTOR_VALIDATION.md](NEXT_PROMPT_AFTER_CARRY_FACTOR_VALIDATION.md)
   — implications + next prompt.
