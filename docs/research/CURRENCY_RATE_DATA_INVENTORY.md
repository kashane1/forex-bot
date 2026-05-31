# Currency Rate-Data Inventory

**Sprint:** `research-financing-rate-data-ingestion-001` · Phase 1
**Type:** data inventory. Docs-only (probe results from FRED). No factor work.
**Date:** 2026-05-31.

Per-currency interest-rate source inventory for the 8 programme currencies. The
chosen harmonized series is the **OECD 3-month interbank rate** on FRED
(`IR3TIB01<CC>M156N`) — a single cross-country-comparable family, the academic
standard short-rate carry proxy. Figures below are from a throttled live probe
(public data; no trading API).

---

## 1. Primary series per currency (chosen)

| Ccy | FRED series | Description | Coverage | Freq | Last obs | Recent values (2021–26) |
|-----|-------------|-------------|----------|------|----------|--------------------------|
| USD | `IR3TIB01USM156N` | 3-month interbank, US | 1995-01 → 2026-04 | monthly | 2026-04 | ~0.1 → 5.5 → 3.8% |
| EUR | `IR3TIB01EZM156N` | 3-month interbank, Euro area | 1995-01 → 2026-01 | monthly | 2026-01 | ~−0.5 → 3.9 → 2.0% |
| GBP | `IR3TIB01GBM156N` | 3-month interbank, UK | 1995-01 → 2026-01 | monthly | 2026-01 | ~0.1 → 6.0 → 3.7% |
| JPY | `IR3TIB01JPM156N` | 3-month interbank, Japan | 2002-04 → 2026-03 | monthly | 2026-03 | ~−0.1 → 1.3% |
| AUD | `IR3TIB01AUM156N` | 3-month interbank, Australia | 1995-01 → 2026-04 | monthly | 2026-04 | ~0.0 → 4.3% |
| NZD | `IR3TIB01NZM156N` | 3-month interbank, New Zealand | 1995-01 → 2026-04 | monthly | 2026-04 | ~0.3 → 5.7 → 2.6% |
| CHF | `IR3TIB01CHM156N` | 3-month interbank, Switzerland | 1999-07 → 2026-04 | monthly | 2026-04 | ~−0.9 → 1.7 → 0.0% |
| CAD | `IR3TIB01CAM156N` | 3-month interbank, Canada | 1995-01 → 2026-04 | monthly | 2026-04 | ~0.1 → 5.0 → 2.3% |

All values are **annualized percent**.

## 2. Historical coverage vs the corpus window

- The spot corpus window is **2021-05-26 → 2026-05-26**. **Every currency has full
  monthly coverage of this window.**
- **Bonus depth:** the rate series extend back **25–30 years** (1995; JPY 2002, CHF
  1999) — far longer than the ~5y spot corpus. A future carry study could, in
  principle, run on a much longer rate history if paired with longer spot data
  (relevant to the design + readiness discussion; not used here).
- **Publication lag:** the latest observation trails real-time by **1–4 months**
  (EUR/GBP to 2026-01; JPY to 2026-03; USD/AUD/NZD/CHF/CAD to 2026-04). The final
  ~1–4 months of the corpus window are covered by **lookahead-safe forward-fill** of
  the last known monthly value.

## 3. Update frequency & latency

- **Frequency: monthly** for all 8 (median observation gap ≈31 days). Adequate for
  carry (a slow, persistent signal) — intramonth rate variation is small relative to
  the differential. Forward-filled to any finer (daily/bar) grid.
- **Latency:** monthly publish + 1–4 month lag. A future study must apply rates with
  a **publication-lag-safe rule** (use a month's value only from a date at/after it
  could have been known), which the construction encodes.

## 4. Limitations

1. **Monthly, not daily** — no intramonth rate dynamics; fine for carry, but the
   response grid for any future study should respect the monthly information cadence
   (avoid implying daily rate signals).
2. **Interbank, not broker financing** — `IR3TIB` is the *economic* interbank rate
   with **no broker markup**. It is **not** OANDA's tradable financing (which adds a
   spread/markup — the C031 ≈4× reality). This dataset captures the carry *signal*,
   **not** the carry *cost*. Tradability needs the separate OANDA-financing ingest.
3. **Post-LIBOR transition** — some OECD `IR3TIB` series were re-based as benchmarks
   moved off LIBOR (to €STR/SONIA/SOFR/TONA, etc.). FRED serves a continuous
   harmonized history, but the *definition* of "3-month interbank" shifted late in
   the sample — a minor consistency caveat (the level/differential remains
   representative).
4. **Shorter JPY/CHF history** (2002/1999) — irrelevant for the 2021–26 window;
   relevant only to any deep-history extension.

## 5. Gaps

- **Within the corpus window:** none at monthly frequency — all 8 series are
  complete 2021-05 → their last obs.
- **Tail gap:** the 1–4 month publication lag at the window end (handled by
  forward-fill; flagged in validation).
- No mid-sample holes were observed in the probe (monthly cadence is regular).

## 6. Proxy requirements

- **None required for the primary build** — all 8 currencies have a direct
  harmonized `IR3TIB` series. (The whole point of choosing the OECD family is that no
  per-currency bespoke proxy is needed, maximizing cross-country comparability.)
- **Documented fallbacks** (not used unless a primary series is later withdrawn):
  USD `DGS3MO`/`FEDFUNDS`; EUR `IRSTCI01EZM156N`; central-bank policy rates per
  currency. Any fallback would be a *different definition* and must be flagged.

## 7. Inventory verdict

All 8 currencies have a **direct, harmonized, sufficiently-deep, regime-sensible**
monthly interbank-rate series covering the corpus window. The data is buildable from
public FRED with no broker/trading API. The binding limitations are **monthly
cadence**, the **publication lag** (both handled lookahead-safely), and — most
importantly for any future tradability claim — that this is the **interbank signal,
not the broker financing cost**. Construction proceeds in Phase 2.
