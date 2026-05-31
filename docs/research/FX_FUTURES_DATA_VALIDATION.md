# FX Futures Data Validation (Phase 2)

**Sprint:** `research-fx-futures-carry-diagnostic-001`
**Type:** Data ingestion + validation. No trading logic.
**Date:** 2026-05-31
**Source:** Yahoo Finance chart v8 (futures, key-less public) + FRED CSV (deep rates, key-less public). SSL via the `certifi` CA bundle (system trust store rejected the chain with `CERTIFICATE_VERIFY_FAILED`).

> Numbers below are read from the **committed** JSON artifacts
> (`research/fx_futures/raw/provenance.json`, `diagnostic/coverage.json`,
> `diagnostic/primary.json`, `diagnostic/deep.json`). The diagnostic docs are
> generated directly from these JSONs so figures are not eye-transcribed.

---

## 0. Reproducibility caveat (read first — important)

Yahoo's `=F` series is a **vendor-continuous** contract:

1. **Absolute price levels and the deep-history start date are NOT stable across fetches.** Re-fetching returns a different splice (different first date and different absolute closes for the same date) because the vendor re-applies its roll/back-adjustment with a different anchor.
2. **Return-based, dollar-neutral quantities ARE stable.** The carry factor is computed on monthly **log returns**, invariant to a constant multiplicative roll-adjustment. The diagnostic is therefore reproducible **from the committed CSVs**: an offline re-run on the committed `raw/` reproduces `primary.json` byte-for-byte (verified — `git status` shows no change after re-running).

Treat the provenance table as **the committed canonical snapshot**; treat absolute levels/start dates as fetch-dependent. The scientific conclusion depends only on returns.

---

## 1. What was ingested (committed snapshot, with provenance)

Seven full-size CME FX-futures continuous series. `provenance.json` records source, fetch date, per-contract row count, first/last date, first/last close, and a **sha256** of each series. The exact CSVs are committed under `research/fx_futures/raw/`. (Per §0 the per-contract start dates and absolute closes are fetch-specific; the committed CSVs are the canonical snapshot the result reproduces from.)

- Contracts: 6E (EUR), 6B (GBP), 6J (JPY), 6S (CHF), 6A (AUD), 6C (CAD), 6N (NZD).
- All seven end 2026-05-29; each has a distinct sha256 (verified seven distinct files; AUD≠NZD confirmed by `cmp`).
- Native quote: **USD per one foreign-currency unit** for every contract.

### Correction to the Phase-0 plan (integrity note)
The Phase-0 plan's draft coverage table listed **unverified placeholder start dates** (6E from 1999; others 2002-02), written while the network was failing on an SSL trust error. They were wrong and have been removed/annotated in the plan. The authoritative monthly coverage is **305 months / 2001-01 → 2026-05** (see §2).

---

## 2. Continuity / coverage of the analysis matrices

From the committed `coverage.json` and `deep.json`:

- **PRIMARY level matrix:** **305 months, 2001-01-01 → 2026-05-01, 0 missing** (gap-free common window across all seven contracts after `dropna(how="any")`). 8 columns: USD (≡1.0) + 7 currencies. ~25 y deep history vs the spot corpus's ~6.4 y.
- The **diagnostic** runs on the intersection of this matrix with each carry signal (PRIMARY: 2021-05 → 2026-05; DEEP: 2001-01 → 2026-04).

---

## 3. Inversion correctness (verified)

Every CME FX future quotes **USD per one foreign-currency unit**, so each contract price maps **directly** to that currency's USD level — **no inversion** (unlike spot, where USD_JPY/USD_CHF/USD_CAD needed `1/price`).

- **6J check:** 6J reports the *true* ~0.006–0.007 USD/JPY (e.g. ~0.0063–0.0069 across fetches), confirming Yahoo does **NOT** apply the ×100 vendor scaling the universe-design flagged as the top hazard. No rescaling applied or needed.
- The registry `spot_inverted` flag (True for JPY/CHF/CAD) is documentation only; not applied in the gross diagnostic.
- Unit test `test_direct_mapping_no_inversion` asserts the month-end level equals the raw month-end close directly.

---

## 4. Roll handling (honest limitation)

The Phase-1 venue design specified a bespoke lookahead-safe volume/OI-crossover roll over individual quarterly contracts. **Free data does not expose individual historical quarterlies with usable depth** — only the vendor-continuous `=F` series, with the vendor's own roll/adjustment (§0). At **monthly** rebalance cadence, and because the factor is return-based and dollar-neutral, the exact roll rule is second-order. This is an explicit **data limitation**, not a definitional change. The bespoke roll adapter was not built (free data cannot feed it).

---

## 5. Two carry-signal sources (both frozen) — BOTH RUNS OBTAINED

- **PRIMARY:** cached frozen FRED signal `research/carry/factor_validation/signal_currency_rate_lag1.csv` (OECD 3M interbank, lag-1), 61 months 2021-05 → 2026-05, all 8 currencies **including JPY**. Reused **unchanged**; intersected with futures levels → diagnostic window 2021-05 → 2026-05 (usable rebalances 59/57/54/48 at h1/h3/h6/h12). Apples-to-apples with the spot study.
- **DEEP:** live FRED CSV for the reachable OECD 3M interbank series, fetched this session via `certifi` SSL (cached under `research/fx_futures/raw_fred/`). **JPY series `IR3TIB01JPM156N` is retired upstream (HTTP 404)**, so the deep run is **JPY-excluded** (6 currencies: EUR/GBP/AUD/NZD/CHF/CAD). Coverage: **304 months, 2001-01 → 2026-04** (≈283–301 usable rebalances across horizons). Result committed in `deep.json`.

> Note: FRED reachability was intermittent this session (some attempts timed out). The deep run that succeeded is committed; an offline re-run reuses the cached `raw_fred/_deep_rate_matrix.csv`.

---

## 6. Lookahead safety

- EOD closes only; month level = that month's last observed close (no forward data).
- Signal is lag-1 month (frozen); forward returns computed strictly forward of the signal month.
- No back/ratio adjustment applied by our code; we consume the vendor series as-fetched and compute returns (invariant to a constant adjustment factor).

---

## 7. Provenance & secrets

- `provenance.json` carries source, fetch date, row counts, first/last, sha256 per contract → auditable.
- No credentials: Yahoo and FRED are key-less public endpoints. Nothing credential-shaped is written.

## 8. Artifacts committed

- `research/fx_futures/raw/*.csv` (7 contracts) + `provenance.json`
- `research/fx_futures/raw_fred/*.csv` (6 FRED series + `_deep_rate_matrix.csv`)
- `research/fx_futures/diagnostic/coverage.json`, `primary.json`, `deep.json`

**Verdict:** the committed snapshot is gap-free (0 missing / 305 months), correctly mapped (no inversion; 6J unscaled; AUD≠NZD), provenance-tracked, and deep (~25 y). Both the PRIMARY (incl-JPY) and DEEP (ex-JPY) runs were obtained and committed. The return-based diagnostic is reproducible from the committed CSVs. **Data is READY** — with the vendor-continuous absolute-level non-determinism documented honestly.
