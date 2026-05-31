# FX Futures Data Validation (Phase 2)

**Sprint:** `research-fx-futures-carry-diagnostic-001`
**Type:** Data ingestion + validation. No trading logic.
**Date:** 2026-05-31
**Source:** Yahoo Finance chart v8 (key-less public endpoint), continuous front-month `=F` series, EOD daily. SSL via the `certifi` CA bundle (system trust store rejected the chain with `CERTIFICATE_VERIFY_FAILED`).

> Every number below was read back from the **committed** JSON artifacts
> (`research/fx_futures/raw/provenance.json`, `research/fx_futures/diagnostic/coverage.json`,
> `research/fx_futures/diagnostic/primary.json`) — not pre-registered placeholders.

---

## 0. Reproducibility caveat (read first — important)

Yahoo's `=F` series is a **vendor-continuous** contract. Two properties matter:

1. **Absolute price levels and the deep-history start date are NOT stable across fetches.** Re-fetching returns a different continuous splice — different first date (observed 2000-05 … 2002-06 across this session's fetches) and different absolute closes (e.g. EUR last close came back as 1.1673 on one fetch and 1.1262 on another for the *same* 2026-05-29 date), because the vendor re-applies its roll/back-adjustment with a different anchor each time.
2. **Return-based, dollar-neutral quantities ARE stable.** The carry factor is computed on monthly **log returns** within the **2021-05 → 2026-05 primary window**, and those returns are invariant to a constant multiplicative roll-adjustment factor. Consequently the **diagnostic result is reproducible**: across every fetch this session the primary 3-month cell came back **+0.000426, t = 0.093**, with identical nulls and drop-one values. The verdict rests on these return-based numbers, **not** on the absolute levels.

So: treat the provenance table below as **one canonical committed snapshot** (the data is committed so the result is reproducible *from the committed CSVs*), and treat the absolute levels / start dates as fetch-dependent. The scientific conclusion does not depend on them.

---

## 1. What was ingested (the committed snapshot, with provenance)

Seven full-size CME FX-futures continuous series. `provenance.json` records source, fetch date, per-contract row count, first/last date, first/last close, and a **sha256** of each series' content. The exact CSVs are committed under `research/fx_futures/raw/`.

| Contract | Symbol | Rows (daily) | First | Last | Last close | Native quote |
|----------|--------|--------------|-------|------|-----------|--------------|
| 6E | 6E=F | 6490 | 2000-09-12 | 2026-05-29 | 1.167300 | USD per EUR |
| 6B | 6B=F | 6404 | 2000-10-05 | 2026-05-29 | 1.346100 | USD per GBP |
| 6J | 6J=F | 6413 | 2000-09-13 | 2026-05-29 | 0.006287 | USD per JPY |
| 6S | 6S=F | 6398 | 2000-11-10 | 2026-05-29 | 1.282400 | USD per CHF |
| 6A | 6A=F | 6393 | 2000-11-08 | 2026-05-29 | 0.718050 | USD per AUD |
| 6C | 6C=F | 6510 | 2000-05-23 | 2026-05-29 | 0.725350 | USD per CAD |
| 6N | 6N=F | 6382 | 2000-06-09 | 2026-05-29 | 0.598750 | USD per NZD |

**Fetched on:** 2026-05-31. **Source string:** `yahoo_finance_chart_v8`. Each contract has a distinct sha256 (verified seven distinct files).

### Correction to the Phase-0 plan (integrity note)
The Phase-0 plan's draft coverage table listed inaccurate **start dates** (6E from 1999-07; others from 2002-02), written as placeholders *while the network was failing on an SSL trust error*. The committed snapshot's start dates are 2000-05 … 2000-11 (see §0 on why these vary). An intermediate scratch read also briefly mis-stated the common window as "286 months / 2002-06" due to a corrupted console read; the authoritative figure from `coverage.json` is **305 months / 2001-01**. The plan was corrected with a visible note; this document is authoritative.

---

## 2. Continuity / coverage of the analysis matrix

The diagnostic consumes a **monthly** month-end USD-per-currency level matrix (`research/fx_futures/continuous.py::month_end_levels`). From the committed `coverage.json`:

- **305 months, 2001-01-01 → 2026-05-01, 0 missing** (gap-free common window across all seven contracts after `dropna(how="any")`).
- 8 columns: USD (≡ 1.0) + EUR, GBP, JPY, AUD, NZD, CHF, CAD.

The common window starts 2001-01 even though individual contracts start a few months earlier (the latest-starting contract pins the common window). ~25 years of deep history — the key venue benefit over the spot corpus's ~6.4 y. **The diagnostic itself runs on the intersection of this matrix with the carry signal** (2021-05 → 2026-05), see §5.

---

## 3. Inversion correctness (verified)

Every CME FX future quotes **USD per one foreign-currency unit**, so each contract price maps **directly** to that currency's USD level — **no inversion** is needed (unlike spot, where USD_JPY/USD_CHF/USD_CAD needed `1/price`).

- **6J check:** last close **0.006287 USD/JPY** — the *true* ~0.0063 economic value, confirming Yahoo does **NOT** apply the ×100 vendor scaling the universe-design flagged as the top hazard. No rescaling applied or needed.
- The registry `spot_inverted` flag (True for JPY/CHF/CAD) is documentation only; it is **not** applied in the gross diagnostic.
- Unit test `test_direct_mapping_no_inversion` asserts the month-end level equals the raw month-end close directly.

---

## 4. Roll handling (honest limitation)

The Phase-1 venue design specified a bespoke lookahead-safe volume/OI-crossover roll over individual quarterly contracts. **Free data does not expose individual historical quarterlies with usable depth** — only the vendor-continuous `=F` series, with the vendor's own roll/adjustment (see §0). At **monthly** rebalance cadence (carry's frozen horizon), and because the factor is return-based and dollar-neutral, the exact roll rule is second-order. This is an explicit **data limitation**, not a definitional change. The bespoke roll adapter was not built (free data cannot feed it).

---

## 5. Two carry-signal sources (both frozen)

- **PRIMARY (used):** cached frozen FRED signal `research/carry/factor_validation/signal_currency_rate_lag1.csv` (OECD 3M interbank, lag-1), 61 months 2021-05 → 2026-05, all 8 currencies **including JPY**. Reused **unchanged**; intersected with futures levels → diagnostic window 2021-05 → 2026-05 (usable rebalances per horizon 59/57/54/48 at h1/h3/h6/h12). Apples-to-apples with the spot study, futures prices substituted.
- **DEEP (attempted, NOT obtained):** live FRED CSV for the reachable OECD 3M interbank series. **JPY series `IR3TIB01JPM156N` is retired upstream (HTTP 404)**, so the deep run would have been JPY-excluded. In this session **FRED was unreachable** (connection reset / timeout across retries), so the deep ~24-year run was **not produced** — there is **no `deep.json`** (no deep results are claimed). **The verdict rests on the PRIMARY incl-JPY run**, the correct apples-to-apples comparison to the spot study. The deep run remains available as a future robustness check if FRED reachability returns.

---

## 6. Lookahead safety

- EOD closes only; month level = that month's last observed close (no forward data).
- Signal is lag-1 month (frozen); forward returns are computed strictly forward of the signal month.
- No back/ratio adjustment is applied by our code; we consume the vendor series as-fetched and compute returns (invariant to a constant adjustment factor).

---

## 7. Provenance & secrets

- `provenance.json` carries source, fetch date, row counts, first/last, and sha256 per contract → auditable.
- No credentials: Yahoo and FRED are key-less public endpoints. Nothing credential-shaped is written.

## 8. Artifacts committed

- `research/fx_futures/raw/*.csv` (7 contracts) + `provenance.json`
- `research/fx_futures/diagnostic/coverage.json` (provenance + coverage report)
- `research/fx_futures/diagnostic/primary.json` (the diagnostic result)
- (No `deep.json` — the deep FRED run was not obtained; see §5.)

**Verdict:** the committed snapshot is complete, gap-free (0 missing over 305 months), correctly mapped (no inversion; 6J unscaled), provenance-tracked, and deep (~25 y). The return-based diagnostic on the PRIMARY window is reproducible from the committed CSVs (§0). **Data is READY for the diagnostic**, with the vendor-continuous absolute-level non-determinism and the unavailable deep-FRED robustness run documented honestly.
