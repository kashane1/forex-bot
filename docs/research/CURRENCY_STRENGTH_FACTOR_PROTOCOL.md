# Currency-Strength Factor — Pre-Registration Protocol

**Sprint:** `research-currency-strength-factor-validation-001` · Phase 1
**Status:** **PRE-REGISTERED AND FROZEN as of this commit.** Every element below
is locked *before* any datum is read. No element may change after data review
(hard rule). Any deviation forced during execution must be recorded as a
deviation in the result docs, never silently applied.
**Date:** 2026-05-30.

This is a **factor-existence/robustness** protocol. Tradability, cost, signals,
and entry/exit are out of scope and are not computed.

---

## 1. Universe (frozen)

**15 instruments** (materialized M5 mid closes, source `m1_materialized`, window
2021-05-26 → 2026-05-26):

- **USD majors (7):** EUR_USD, GBP_USD, USD_JPY, AUD_USD, NZD_USD, USD_CAD, USD_CHF
- **Crosses (8):** EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY, NZD_JPY, EUR_CHF, GBP_CHF,
  EUR_AUD

**8 currencies:** USD, EUR, GBP, JPY, AUD, NZD, CHF, CAD.

Leg multiplicity (instruments containing each currency, of 15): USD 7, EUR 6,
JPY 5, GBP 4, AUD 4, CHF 3, NZD 3, **CAD 1** (USD_CAD only — pre-registered weak
link; CAD strength ≡ −USD_CAD return; reported but flagged).

## 2. Base grid (frozen)

- Common **M5** timestamp index across all 15 instruments: keep only timestamps
  where **all 15** have a complete bar (inner join) → a single aligned panel of
  mid-close log returns. This removes weekend/holiday gaps uniformly.
- Per-instrument per-bar return `r_i(t) = ln(mid_close_i(t) / mid_close_i(t-1))`.

## 3. Strength calculation method (frozen — PRIMARY = average-of-pairs)

For currency `c` at bar `t` over **lookback L bars**:
- For each instrument `i` containing `c`, take the cumulative log return over the
  last L bars, **signed** so positive = `c` appreciated:
  `s = (+1 if c is base of i else −1) * Σ_{k=0..L−1} r_i(t−k)`.
- **`strength_c(t) = mean over the instruments containing c of s`** (equal-weight,
  average-of-pairs).

This yields an 8-vector of currency strengths per bar, in cumulative-log-return
units. **Equal-weight, no volatility scaling, no winsorization** (frozen — kept
deliberately simple/transparent; a vol-normalized variant is a Phase-6
*robustness* check, not the primary).

**Secondary method (for the Phase-6 collinearity/robustness contrast only):**
a least-squares decomposition of the return matrix onto currency dummies
(`r_i = strength_base(i) − strength_quote(i) + ε`, solved per bar over the L-bar
window with a USD-numéraire constraint). This is **not** the primary and is used
only to test whether the two aggregations agree.

## 4. Derived measures (frozen)

- **Ranking:** sort the 8 currencies by `strength_c(t)` each evaluated bar;
  rank 1 = strongest, rank 8 = weakest.
- **Change-in-strength (momentum of strength):** `Δstrength_c(t) = strength_c(t)
  − strength_c(t − D)` with **D = 12 M5 bars (1 hour)**. Top-1 by Δ = "rapidly
  strengthening"; bottom-1 = "rapidly weakening".
- **Dispersion:** cross-sectional **std** of the 8 strengths each bar.
- **Spread:** **max − min** strength (strongest − weakest gap) each bar.

## 5. Lookback windows (frozen)

- **Primary lookback L = 48 M5 bars (4 hours).**
- Robustness lookbacks (Phase 6, nearby — NOT optimization): **24 (2h)** and
  **96 (8h)**. The verdict is decided on the **primary L=48**; the others only
  test stability.

## 6. Update / sampling frequency (frozen)

- Evaluate the factor on a **decimated hourly grid**: one event every **12 M5
  bars**. This limits overlap/autocorrelation between consecutive events (events
  60 min apart while horizons reach 240 min still overlap, handled by the
  block/independent-resample nulls in §9; the decimation reduces but does not
  eliminate overlap, which is acknowledged).

## 7. Response windows (frozen)

Forward horizons: **5, 15, 30, 60, 240 minutes** = **1, 3, 6, 12, 48 M5 bars**.

**Forward currency return** for currency `c` over horizon `h`:
`fwd_c(t,h) = mean over instruments i containing c of [ (+1 if c base else −1) *
Σ_{k=1..h_bars} r_i(t+k) ]` — i.e. the same signed average-of-pairs aggregation,
measured strictly **after** `t`.

## 8. Response metrics (frozen)

Per condition × horizon: **mean forward return**, **P(positive)**, **P(negative)**,
**MFE** (max favourable excursion of the cumulative signed currency-return path
over the horizon), **MAE** (max adverse excursion), and **rank persistence**
(fraction of events where the conditioned currency holds its rank bucket — e.g.
rank-1 still rank-1 — at the horizon). Units: cumulative log return (reported in
basis points; 1 bp = 1e-4).

## 9. Conditions studied (frozen)

For each evaluated bar, the conditioned currency sets are:
1. **Strongest** (rank 1) → forward currency return (momentum if +, reversion if −).
2. **Weakest** (rank 8) → forward currency return.
3. **Rapidly strengthening** (top-1 by Δstrength) → forward return.
4. **Rapidly weakening** (bottom-1 by Δstrength) → forward return.

Direction is an **empirical output**, not assumed. A coherent factor shows a
consistent, null-separated pattern (e.g. continuation or reversion) across
horizons and conditions.

## 10. Null methodology (frozen)

Four nulls, each resampled over **200 seeds** (with a fixed integer seed sequence
0..199 for reproducibility — no `Math.random`):
- **Unconditional baseline:** mean `fwd_c(t,h)` over **all** currency-bars
  (ignoring rank) — the "is there just drift?" reference (expected ≈ 0).
- **Randomized ranks:** shuffle the rank→currency assignment within each bar
  (break strength→rank link), recompute the conditional means.
- **Shuffled currencies:** permute currency identity across the strength vector
  (break currency→its-own-forward-return link).
- **Matched timestamps:** draw random bars (same count, **session-matched** by
  the lab's UTC session bucket) and random currencies → conditional means.

**Decisive statistic:** `matched_z = (observed_cond_mean − null_mean) /
null_std` per condition × horizon × null. Reuse the lab's
`research/edge_discovery/matched_nulls.py` session bucketing where applicable.

## 11. Significance / multiple-comparison (frozen)

- Bar: **|matched-Z| ≥ 2** to "clear" a cell.
- 4 conditions × 5 horizons = **20 cells per null**. Isolated |Z|≈2 hits are the
  multiple-comparison **noise expectation** (~1 per null); a real factor clears
  **multiple coherent cells** under **all four** nulls.

## 12. Breadth / collinearity diagnostic (frozen)

- Pairwise correlation matrix of the 8 strength series; **variance explained per
  currency** via PCA of the strength panel (how many independent axes; does PC1 =
  USD?). H2 (breadth) holds only if **>1 currency** contributes materially
  independent variance and the effect is not reducible to the USD axis.

## 13. Robustness axes (frozen — Phase 6, stability not optimization)

- **Nearby lookbacks:** L ∈ {24, 96} vs primary 48.
- **Nearby ranking definitions:** rank-1 vs **top-2** bucket; weakest vs bottom-2.
- **Nearby aggregation definitions:** average-of-pairs (primary) vs **least-squares
  decomposition** (§3 secondary) vs **vol-normalized** average-of-pairs.
- **Slices:** per-currency, per-pair, per-year, per-session (already in Phase 4).
The verdict uses the **primary** spec; robustness only tests whether the
conclusion survives these neighbours.

## 14. What is NOT allowed post-data (frozen)

No change to L, D, grid, aggregation, ranking, horizons, nulls, seeds, or the
|Z|≥2 / multiple-cell rules after seeing a number. No dropping a currency/pair/
year to improve a statistic. No new condition invented to rescue a weak result.
No cost/tradability gate. **Definitions frozen; only the instrument data feeds in.**

## 15. Frozen verdict map (applied mechanically in Phase 7)

| Verdict | Condition |
|---|---|
| **FACTOR_FRONT_GATE_CANDIDATE** | coherent existence effect **and** |Z|≥2 on multiple cells under **all four** nulls **and** robust across currencies/pairs/years/sessions/neighbours **and** breadth holds (not the USD axis) |
| **FACTOR_REAL_BUT_WEAK** | a coherent, null-separated effect exists **somewhere** stable, but is narrow (few cells / modest Z / partial robustness) — insufficient for a front gate |
| **FACTOR_REJECTED** | effect within null, or sign-incoherent across horizons/years/sessions, or single-currency/period-driven, or reducible to the USD axis |

This map is frozen. Phases 2–6 produce evidence; Phase 7 applies the table
without further latitude.
