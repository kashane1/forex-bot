# Carry Dataset — Construction (Phase 2)

**Sprint:** `research-financing-rate-data-ingestion-001` · Phase 2
**Type:** data construction (DATA asset only — **no signal, no factor study, no
trade logic**). Code: `research/carry/carry_rates.py`; runner
`scripts/build_carry_rate_dataset.py` (reuses `fetch_fred_observations`).
**Date:** 2026-05-31.

Carry is constructed as an **un-validated data asset** and is **not** presented as
an edge anywhere here.

---

## 1. Sources (provenance)

- **FRED** (Federal Reserve Bank of St. Louis), **OECD harmonized 3-month interbank
  rates**, series `IR3TIB01<CC>M156N`, one per currency (Phase 1 inventory).
- Public data, fetched over HTTPS with a throttled (3 s) reader; `FRED_API_KEY` read
  from env/`.env` and **never committed**. Raw responses cached to a **gitignored**
  dir (`data/external_features/.carry_rate_cache/`) for reproducibility.
- Provenance recorded in `docs/research/carry_rates/rate_provenance.json` (series
  ids, source=fred/cache, n_obs, first/last per currency, fetch window,
  `strategy_evidence: false`).

## 2. Construction pipeline (reproducible, lookahead-safe)

1. **Fetch** each currency's monthly interbank series (1995→2026 window; JPY 2002,
   CHF 1999 by availability).
2. **Rate panel** (`rate_series.csv`): tidy long table `[date, currency, rate,
   series_id]` — the raw monthly observations (annualized %).
3. **Monthly rate matrix:** pivot to month-indexed wide matrix (rows = month-start,
   cols = 8 currencies), **forward-filled** so each month carries the latest *known*
   value. Forward-fill is **lookahead-safe at monthly cadence** — a month uses only
   that month's published value or earlier; the 1–4-month publication lag at the
   window tail is filled from the last known value (flagged in validation, and any
   future study must additionally apply a ≥1-month implementation lag — see design).
4. **Carry differentials** (`carry_differentials.csv`): for all 15 instruments,
   `carry(BASE_QUOTE) = r_base − r_quote` (annualized %), long table `[month,
   instrument, base_ccy, quote_ccy, base_rate, quote_rate, carry_diff]`. Long the
   pair earns the base-leg rate and pays the quote-leg rate; **positive carry = base
   out-yields quote.** Descriptive only.

## 3. Universe constructed

- **Majors (7):** EUR_USD, GBP_USD, USD_JPY, AUD_USD, NZD_USD, USD_CAD, USD_CHF.
- **Crosses (8):** EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY, NZD_JPY, EUR_CHF, GBP_CHF,
  EUR_AUD.
- Each gets a full monthly carry-differential history (back to 2002-04, bounded by
  JPY's start; corpus-window analysis uses 2021-05 → 2026-05 = **59 months**).

## 4. Internal-consistency guarantee (built in)

A **triangular rate-residual** check (`triangular_rate_residual`) verifies that each
cross's carry equals the difference of its two USD-leg carries — an identity for
additive rate differentials:
`(r_base − r_quote) − [(r_base − r_USD) − (r_quote − r_USD)] ≡ 0`.
Measured **max |residual| = 1.78e-15** (machine zero) → the rate matrix is perfectly
internally consistent; no per-currency inconsistency leaks into the crosses.

## 5. Output artifacts (committed)

| Path | Contents |
|---|---|
| `docs/research/carry_rates/rate_series.csv` | raw monthly rates (2,859 rows, 8 ccy) |
| `docs/research/carry_rates/carry_differentials.csv` | monthly carry per instrument (5,043 rows, 15 inst) |
| `docs/research/carry_rates/rate_provenance.json` | sources, coverage, tri-residual, attribution |
| `docs/research/carry_rates/diagnostics.json` | corpus-window summary stats, distributions, rankings |

(Raw FRED JSON/CSV cache is **gitignored**, not committed; the script regenerates it
on demand — reproducible.)

## 6. What was NOT built

No carry signal, no entry/exit, no holding/return computation, no factor response,
no null, no backtest, no cost-feasibility gate, no approval. **A data asset and its
descriptive diagnostics only.** Tradable carry cost (OANDA broker financing) is a
separate, later, user-authorized ingest — not in this dataset.
