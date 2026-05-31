# FX Futures Carry Diagnostic — PLAN (Phase 0: Baseline Audit)

**Sprint:** `research-fx-futures-carry-diagnostic-001`
**Type:** Decision-forcing **diagnostic / factor evaluation**. The first code-bearing futures sprint. **No campaign, no strategy, no front gate, no trading logic, no train/validation/test.**
**Date:** 2026-05-31
**Freeze:** must remain intact. Paper/demo/live remain blocked.

---

## Why this sprint exists

The FX-Futures Venue & Diagnostic sprint returned **`VIABLE_WITH_LIMITATIONS`**: carry is the only frozen factor with a meaningful, free/local futures test path (S4 infeasible, C1 needs paid intraday, S2 rejected). This sprint executes that test and resolves the **final major uncertainty** of the programme:

> *Was spot carry merely **financing-defeated** (→ it might survive a fair venue that has no nightly financing wall), or is it **genuinely non-predictive** (→ it will be null even in futures)?*

### The prior to verify (from the feasibility study + cost model)

The futures cost model established an exact, falsifiable prediction:

- Futures **removes the nightly financing wall** (the ≈4× spread squeeze that defeated C031/spot carry).
- Futures **simultaneously removes the carry accrual benefit** — the rate differential is embedded in the **basis** and realized via convergence **into the futures price**, not handed out as a nightly accrual.
- Because spot carry's gross premium was **mechanical accrual** with a **statistically-zero spot-predictive leg**, the honest prior is: **carry-in-futures gross ≈ the spot-predictive component ≈ ~0.**

This sprint tests that prediction with real futures data and the **frozen** carry factor.

---

## Baseline audit findings

### Carry Factor Validation (spot, `research-carry-factor-validation-001`) → `FACTOR_REAL_BUT_WEAK`
- Primary cell (currency HML-3, total, 3-month): mean **+0.74%/quarter**, NW-HAC t = **1.68** (< 2).
- **Spot-predictive (price-only) leg is statistically zero at every horizon** (t = 0.12 / 0.10 / 0.01 / −0.27). ~94% of the 3m total is mechanical accrual.
- **Single-name:** drop-JPY collapses the premium **+0.0075 → +0.0003**.
- **No timing content:** fails shuffled-timestamp null (Z=0.72); carry-momentum spec flips negative.
- Window: **61 months, 2021-06 → 2026-05.** Seed 20260531.

### FX Futures Venue & Diagnostic → `VIABLE_WITH_LIMITATIONS`
- Carry is free/local-feasible on EOD futures with decades of history; S4 excluded; C1 data-gated.

### Futures Cost Model
- Round-trip ~2.3–2.9 bp, **financing = 0**, quarterly roll ~3.7 bp/yr — vs spot ~3–5 bp **plus** nightly financing.
- Key identity: futures removes financing *penalty* and accrual *benefit* together → futures total return = **futures price return** (no separate accrual leg).

### Futures Diagnostic Framework
- Definitions frozen; only permitted change is **substituting the futures series for the spot series** (with quote-convention handling). Reuse the existing matched-null / multiple-comparison / cost-feasibility gates. No optimization, no new thresholds.

### Programme Direction Decision
- Decision-forcing: `CARRY_SURVIVES_IN_FUTURES` → one future pre-registered screen; `CARRY_DOES_NOT_SURVIVE_IN_FUTURES` → pre-committed archive (Option E).

---

## Data acquired (pre-registration of what is used — confirmed reachable this session)

### Futures returns — Yahoo Finance continuous front-month (`=F`), EOD daily
| Contract | Currency | Coverage (this fetch) | Last close | Native quote |
|----------|----------|------------------------|-----------|--------------|
| 6E=F | EUR | 1999-07-08 → 2026-05-29 | 1.12623 | USD per EUR |
| 6B=F | GBP | 2002-02-13 → 2026-05-29 | 1.34673 | USD per GBP |
| 6J=F | JPY | 2002-02-13 → 2026-05-29 | 0.00692873 | USD per JPY |
| 6S=F | CHF | 2002-02-13 → 2026-05-29 | 1.22269 | USD per CHF |
| 6A=F | AUD | 2002-02-13 → 2026-05-29 | 0.64789 | USD per AUD |
| 6C=F | CAD | 2002-02-13 → 2026-05-29 | 0.65629 | USD per CAD |
| 6N=F | NZD | 2002-02-13 → 2026-05-29 | 0.64789 | USD per NZD |

Two findings already material:
1. **6J is NOT scaled ×100 on Yahoo** — it reports the true ~0.0069 USD/JPY. The design's flagged "6J ×100" hazard does **not** apply to this source (verified; will re-verify in Phase 2).
2. **All contracts are natively USD-per-foreign-currency** — they map *directly* to the carry factor's per-currency USD-level matrix. The "quote inversion" the spot corpus needed (USD_JPY = 1/price) is **absent** in futures; the only sign care needed is when relating back to the spot USD_xxx convention (documented in Phase 1).
3. Yahoo's `=F` is a **vendor-continuous** series (Yahoo applies its own front-month roll). The Phase-1 design's bespoke vol/OI-crossover roll is **moot for free data** because individual historical quarterly contracts are not freely available with depth — only the continuous series is. This is an honest deviation, acceptable at **monthly** cadence (carry rebalances monthly), and documented as a limitation.

### Carry signal — frozen, two sources
- **PRIMARY:** the **cached frozen signal** `research/carry/factor_validation/signal_currency_rate_lag1.csv` (FRED OECD 3M interbank, lag-1), **61 months 2021-06 → 2026-05**, all 8 currencies **including JPY**. Reused **unchanged**.
- **DEEP (secondary/robustness):** live FRED CSV for the 7 reachable series. **JPY's FRED series `IR3TIB01JPM156N` now returns HTTP 404** (retired upstream), so the deep-history run is necessarily **JPY-excluded**. Since drop-JPY already collapsed the spot premium to ≈0, a deep JPY-excluded run is a clean **breadth-over-24-years** test, explicitly labeled as such.

---

## Diagnostic design (frozen factor, venue swapped)

| Element | Value (frozen — unchanged from spot protocol) |
|---------|-----------------------------------------------|
| Currencies | USD + 7 (USD funding numeraire) |
| Signal | FRED OECD 3M interbank rate, **lag 1 month** (unchanged) |
| Portfolio | currency **HML-3**, long top-3 / short bottom-3, dollar-neutral (Σ|w|=2), monthly rebalance |
| Horizons | 1 / 3 / 6 / 12 months |
| Primary cell | currency HML-3, **total, 3-month** |
| Seed | 20260531 |
| Nulls | randomized ranks, matched-random baskets (shuffled contracts), shuffled-timestamp, unconditional baseline |
| Multiple comparison | Holm–Bonferroni across the horizon family |

**The only change vs spot:** the **return series** is the futures continuous price return instead of the spot mid. **Critical venue identity:** in futures the carry differential is in the basis, so **futures total return = futures price return** (financing = 0; no separate accrual leg is added). The spot-style FRED accrual is computed and reported **separately** only to show what futures gives up — it is **not** added to the futures total.

This means the futures diagnostic measures exactly the quantity the prior says is ~0: **does ranking currencies by interbank carry predict subsequent futures price moves?**

---

## What gets built (minimum required for the diagnostic)

- `research/fx_futures/registry.py` — futures instrument registry (contract specs, currency mapping, native-quote/inversion flags).
- `research/fx_futures/ingest.py` — Yahoo EOD fetch → raw per-contract CSV + provenance (hash, source, fetch window).
- `research/fx_futures/continuous.py` — raw → monthly month-end USD-per-currency level matrix; validation (coverage, continuity, inversion correctness).
- `research/fx_futures/carry_diagnostic.py` — runs the **frozen** carry factor (reusing `research.carry.carry_factor` functions **unmodified**) on the futures level matrix; futures-total = price-only.
- `scripts/run_fx_futures_carry_diagnostic.py` — runner producing JSON artifacts.
- `tests/test_fx_futures_carry_diagnostic.py` — unit tests (inversion, month-end resample, HML neutrality, null plumbing).

`research/carry/carry_factor.py` and `carry_rates.py` are **NOT modified** (freeze on definitions). Spot majors/crosses code untouched. Futures support is **additive**.

---

## Hard constraints (binding, restated)

- No CAMPAIGN_032; no campaign of any kind.
- No entry/exit rules, no trading logic, no strategy, no approval.
- No alteration of carry definitions after data review; no threshold retuning; no reopening rejected factors.
- Paper/demo/live stay blocked; freeze intact.
- No vendor credential committed (Yahoo/FRED are key-less public endpoints); secret-scan stays green.
- No result presented as an edge — gross/net survival diagnostic only, with honest caveats.

## Phase outputs

0 plan (this) · 1 infrastructure + impl doc · 2 data validation · 3 carry diagnostic result · 4 null comparison · 5 verdict (binary) · 6 programme implication · 7 next prompt · 8 validation + summary.
