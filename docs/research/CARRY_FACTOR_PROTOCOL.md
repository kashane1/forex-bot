# Carry Factor — Frozen Protocol (Phase 1)

**Sprint:** `research-carry-factor-validation-001` · Phase 1
**Status:** **FROZEN.** Pre-registered before any forward return is computed. No
definition, ranking, window, null, or statistic below may be modified after data
review. Any deviation discovered necessary mid-study is recorded as a *failed
pre-registration* (the study is reported as exploratory), not silently changed.
**Date:** 2026-05-31.

This protocol operationalizes the design in
[CARRY_FACTOR_VALIDATION_DESIGN.md](CARRY_FACTOR_VALIDATION_DESIGN.md) and the plan in
[CARRY_FACTOR_VALIDATION_001_PLAN.md](CARRY_FACTOR_VALIDATION_001_PLAN.md). Gross-only.
No trades, no costs, no approval.

---

## §1. Universe (frozen)

**Currencies (8):** USD, EUR, GBP, JPY, AUD, NZD, CHF, CAD.

**Instruments (15):** EUR_USD, GBP_USD, USD_JPY, AUD_USD, NZD_USD, USD_CAD, USD_CHF
(7 majors) + EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY, NZD_JPY, EUR_CHF, GBP_CHF, EUR_AUD
(8 crosses).

**Two analysis layers:**

- **Primary — currency cross-section (8 currencies).** USD is the numeraire; the 7
  other currencies' returns vs USD come directly from the 7 major pairs. This is the
  breadth-respecting construction (the S2 lesson: a true factor must not collapse to a
  USD-axis bet).
- **Secondary — instrument cross-section (15 pairs).** Each cross's gross mid
  log-return is reconstructed by no-arbitrage from its two USD-leg majors
  (`r(B_Q) = r(B_USD) + r(USD_Q)`, signs per §3). Used only as an instrument-level
  consistency check; it carries **no** independent cost information.

## §2. Spot data & monthly sampling (frozen)

- **Source:** `data/campaign_002.sqlite3`, table `candles`, granularity **H1**, the 7
  majors. Read-only. The runner records each query and the row counts in the artifact.
- **Mid price:** `mid = (bid_c + ask_c) / 2` per H1 bar (the `mid_c` column is
  unpopulated in this store; bid/ask are authoritative).
- **Month-end close:** for each calendar month, the **last available H1 mid** with
  timestamp `≤ month-end` is the month's spot close. Months are labelled by
  month-start (`MS`) to align with the carry matrix.
- **Study window:** **2021-06-01 → 2026-05-01** month-starts for the *signal*; spot
  closes from 2021-05 (the base month) onward. This yields **≤ 60** monthly spot
  observations; the realised count is reported, not assumed.
- **Currency return vs USD** for month *t* (log): with `P` the major's month-end mid,
  - ccy is **base** (EUR_USD, GBP_USD, AUD_USD, NZD_USD): `r_ccy(t) = ln P(t) − ln P(t−1)`.
  - ccy is **quote** (USD_JPY→JPY, USD_CAD→CAD, USD_CHF→CHF): `r_ccy(t) = −(ln P(t) − ln P(t−1))`.
  - `r_USD(t) ≡ 0` (numeraire).

## §3. Carry signal (frozen — reuses the committed asset, unchanged)

- **Per-currency rate** `rate_ccy(t)`: the monthly rate matrix built by the **existing,
  unmodified** `research/carry/carry_rates.py::monthly_rate_matrix` from
  `docs/research/carry_rates/rate_series.csv` (FRED OECD 3M interbank, annualized %).
- **Instrument carry** `carry(B_Q,t) = rate_B(t) − rate_Q(t)` (the committed
  `carry_differentials.csv`; identical by construction).
- **Implementation lag (lookahead safety):** the carry used to rank at month *t* is
  the rate **known at the end of month *t*** — and, to respect the documented 1–4-month
  FRED publication lag plus a conservative execution lag, the **primary** spec applies
  a **1-month lag**: ranking at month-end *t* uses `rate_ccy(t)` (the value stamped to
  month *t*, already a strictly-prior forward-fill in the asset). The lag sensitivity
  (0, 1, 2 months) is a frozen robustness axis (§7), not a tuning knob.

## §4. Factor construction (frozen) — exposures only, Phase 2

At each rebalance month-end *t* (monthly rebalance):

### §4.1 Currency cross-section (primary)
1. Rank the 8 currencies by `rate_ccy(t)` (descending).
2. **HML-k portfolio:** long the top **k** currencies (equal weight `+1/k`), short the
   bottom **k** (`−1/k`); middle currencies weight 0. **Primary k = 3.** (k = 2 is a
   robustness axis.) USD participates as one of the 8 — it is ranked, not privileged.
3. **Rank-weighted portfolio (continuous):** weight currency *i*
   `w_i ∝ (rank_centered_i)`, normalized so `Σ|w_i| = 2` (dollar-neutral, gross
   exposure 2). A monotone alternative to the discrete HML; reported alongside.

### §4.2 Instrument cross-section (secondary)
1. Rank the 15 instruments by `carry(inst,t)`.
2. **HML-m portfolio:** long top **m = 4**, short bottom **m = 4**, equal weight.
   Reconstructed-mid returns only (no cross spreads). Consistency check on §4.1.

Exposures (weights per month) are the **only** Phase-2 output — **no forward return is
computed in Phase 2.**

## §5. Response windows & return definition (frozen)

- **Holding horizons:** **1, 3, 6, 12 months** (carry is a slow, monthly-cadence
  signal; intraday is a category error and out of scope).
- **Portfolio forward return at horizon *h*** for a rebalance at *t*:
  - **Spot component (H1 test):** `R_spot(t,h) = Σ_i w_i(t) · [ln S_i(t+h) − ln S_i(t)]`
    where `S_i` is the currency's USD value (currency layer) or the instrument mid
    (instrument layer).
  - **Carry-accrual component:** `R_carry(t,h) = Σ_i w_i(t) · (yield_i(t) · h/12)` where
    `yield_i` is `rate_ccy(t) − rate_USD(t)` (currency layer) or `carry(inst,t)`
    (instrument layer), in decimal — the interbank carry earned over the holding period
    (gross of any broker markup).
  - **Primary metric (H2):** **total gross return** `R_tot = R_spot + R_carry`.
  - **Secondary metric (H1):** **spot-only** `R_spot` (the pure UIP-failure component).
- Overlapping horizons are used (monthly rebalance, *h*-month hold). Significance
  accounts for the overlap (§6). Per horizon the **number of independent
  (non-overlapping) windows** is reported as the honest power denominator.

## §6. Statistics & significance (frozen)

For each (layer, portfolio, metric, horizon) cell:

- **Point stats:** mean forward return, std, **annualized mean/std ratio** (a
  Sharpe-like descriptive, *not* a tradable Sharpe), **sign consistency** (% of
  rebalances with positive return), **t-stat with Newey–West HAC** SE (lag = `h`, to
  correct overlap), and the empirical distribution.
- **Rank stability / persistence:** month-over-month **Spearman correlation** of the
  carry ranks, and the autocorrelation of HML weights, to confirm the signal is the
  slow object it claims to be (and to bound the effective independent-sample count).
- **Decisive inferential test:** **matched-Z** of the realised HML mean against the
  **null distribution** (§ Phase 5), `Z = (mean_obs − mean_null) / std_null`, with the
  null built from **2000** resamples (frozen seed = **20260531**).
- **Multiple-comparison control:** the primary verdict rests on a **single
  pre-registered cell** — *currency layer, HML-3, total return, 3-month horizon* — to
  avoid best-of-N. All other cells are **supporting/robustness** context. Across the
  4×(reported cells) grid, a **Holm–Bonferroni** adjustment is applied and reported; a
  result that is significant only before adjustment is labelled accordingly.
- **Significance bar:** the primary cell must clear **matched-Z ≥ 2 against every null**
  *and* survive Holm–Bonferroni across the horizon family, *and* be correctly signed.

### §6.1 The single pre-registered primary cell
> **Currency cross-section, HML-3 (long top-3 / short bottom-3 of 8 currencies by
> interbank rate, 1-month lag), total gross return, 3-month holding horizon, monthly
> rebalance.** Verdict-decisive. Everything else is corroboration.

## §7. Robustness axes (frozen — Phase 6, robustness *not* optimization)

Evaluated as a stability grid around the primary cell; the verdict is **not** re-chosen
from the best cell:
- **k:** {2, 3} (currency HML); **m:** {3, 4, 5} (instrument HML).
- **Ranking variable:** {rate level (primary), 3-month change in rate (carry momentum)}.
- **Lag:** {0, 1 (primary), 2} months.
- **Weighting:** {equal-weight HML (primary), rank-weighted}.
- **Horizon:** {1, 3 (primary), 6, 12} months.
A factor is *robust* if the sign and rough magnitude hold across these neighbours; it is
*fragile* if only the primary cell (or a single neighbour) is positive.

## §8. Null methodology (frozen — Phase 5)

All nulls preserve the realised return panel and only break the **carry→return** link;
2000 draws each, seed 20260531:
1. **Randomized carry ranks:** independently permute the currency→rank assignment each
   rebalance month, recompute HML. Kills any genuine carry information; preserves the
   cross-sectional return covariance and the marginal return distribution.
2. **Shuffled-timestamp carry:** permute the *months* of the carry matrix (block-shuffle
   the rank vector across time), detaching the signal from its forward window.
3. **Matched (regime) null:** randomly select long/short baskets of the **same size**
   from the same month, ignoring carry (regime/time-matched random selection).
4. **Unconditional baseline:** the equal-weight, dollar-neutral "all currencies" return
   and the simple cross-sectional mean — does carry-sorting add over no sorting?
The observed HML must beat **all four** to survive.

## §9. Regimes & subsamples (frozen — Phase 4)

- **Year:** per-calendar-year HML mean (2021…2026).
- **Rate regime:** months classified by the **USD policy-rate direction** (hiking /
  on-hold / cutting) from `rate_USD` 3-month change — does carry survive outside the
  2022–23 hiking episode?
- **Risk regime:** months split by the realised cross-sectional **dispersion of FX
  returns** (a model-free risk-on/off proxy, since no VIX is in-corpus) into calm vs
  turbulent halves — tests H3 (carry-crash asymmetry).
- **Currency drop-one:** recompute HML dropping each currency in turn (is it one
  currency's story?). **Instrument drop-one** likewise.

## §10. Outputs & integrity

- The runner `scripts/run_carry_factor_validation.py` writes **all** numbers to
  `research/carry/factor_validation/*.json` and `*.csv`; **every figure quoted in the
  Phase 3–7 docs is read back from those on-disk artifacts** (the standing integrity
  lesson: never quote a buffered/expected number — verify the written file).
- Frozen RNG seed **20260531** everywhere a resample is drawn.
- Import-isolation: the research module imports no `forex_bot.broker` / `loops` /
  `approval` / `execution`.

**Freeze status unchanged:** `approved:[]`; paper/demo/live remain blocked. This
protocol authorizes a *measurement*, never a trade.
