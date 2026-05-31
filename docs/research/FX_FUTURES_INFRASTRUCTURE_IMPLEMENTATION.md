# FX Futures Infrastructure Implementation (Phase 1)

**Sprint:** `research-fx-futures-carry-diagnostic-001`
**Type:** Additive research infrastructure for the carry diagnostic. No trading logic.
**Date:** 2026-05-31

Implements only what the carry diagnostic requires, following the frozen
`FX_FUTURES_UNIVERSE_DESIGN.md`. All new code lives under `research/fx_futures/`
(import-isolated; no `forex_bot.broker`/`loops`/`approval`/`execution` imports).
`research/carry/carry_factor.py` and `carry_rates.py` are **not modified**.

---

## Modules

### `research/fx_futures/registry.py`
Seven full-size CME FX futures, one per spot-major currency. Each `FuturesContract`
records root, Yahoo continuous symbol (`=F`), currency, spot analogue, contract
spec, and a `spot_inverted` flag.

**Quote-convention handling (the design's "inversion" item):** every CME FX future
quotes the foreign currency as base (USD per 1 foreign unit). So each contract's
price *is* that currency's USD value — exactly what the carry factor's per-currency
USD-level matrix needs, with **no inversion**. `spot_inverted` (True for JPY/CHF/CAD)
only documents that the contract is quoted opposite to the spot corpus's `USD_xxx`
pairs; it is round-trip-mapping metadata, not applied in the gross diagnostic.

### `research/fx_futures/ingest.py`
Yahoo Finance chart v8 endpoint (key-less public). Fetches daily closes for each
`=F` continuous symbol, writes one raw CSV per currency plus `provenance.json`
(source URL, fetch range, row count, first/last close, **sha256** of content).
`load_raw()` re-reads without network. EOD-only ⇒ lookahead-safe. **SSL uses the
`certifi` CA bundle** (`_ssl_context()`), which was required: macOS framework
Python otherwise fails every HTTPS fetch with `CERTIFICATE_VERIFY_FAILED`.

### `research/fx_futures/continuous.py`
`month_end_levels()` resamples each raw daily series to **month-end last
observation**, stamps it to month-start (MS) to match the carry convention, and
assembles a `USD + 7-currency` level matrix (USD ≡ 1.0), restricted to the common
fully-populated window. `currency_log_returns()`, `instrument_log_levels_from_currency()`,
and `coverage_report()` (continuity/missing-month audit) support validation.

### `research/fx_futures/fred.py`
Deep-history robustness only: key-less FRED CSV for the reachable OECD 3M interbank
series (also via `certifi`). **JPY (`IR3TIB01JPM156N`) is retired upstream (HTTP
404)** ⇒ deep run is JPY-excluded (handled by the runner). The PRIMARY run does
**not** use this — it reuses the cached frozen signal CSV.

### `research/fx_futures/carry_diagnostic.py`
Runs the **frozen** carry factor on futures levels by **reusing
`research.carry.carry_factor` functions unmodified** (`build_weights`, `hml_weights`,
`forward_spot_return`, `cell_stats`, `nw_tstat`, `matched_z`, `holm_bonferroni`,
`rank_stability`).

**Venue identity (frozen design + cost model §4):** in futures the carry
differential lives in the basis and converges into price, so **futures total =
futures price return** — no separate accrual leg, financing = 0. The null battery
(randomized ranks, shuffled timestamp, matched-random baskets, unconditional
baseline) is computed **price-only** for internal consistency; this required a thin
re-implementation of the null loop in the futures module (so `carry_factor`'s
accrual-adding `_portfolio_total` stays untouched) — the *generic* helpers are
reused as-is. `drop_one_currency()` reproduces the spot study's single-name test.

### `scripts/run_fx_futures_carry_diagnostic.py`
Orchestrates ingest → levels → coverage → PRIMARY (cached signal) → DEEP (FRED) →
nulls, writing JSON under `research/fx_futures/diagnostic/`. `--offline` reuses
ingested data. Deep run wrapped in try/except (optional robustness). **Run with
`PYTHONPATH=$PWD`** (the `research` package is not installed; the runner imports
`research.fx_futures`).

---

## Roll / continuous-contract note (honest deviation from design)

The Phase-1 venue design specified a bespoke lookahead-safe **volume/OI-crossover
roll** over individual quarterly contracts. **Free data does not expose individual
historical quarterlies with depth** — only the vendor-continuous `=F` series, for
which Yahoo applies its own roll. At **monthly** rebalance cadence (carry's frozen
horizon) the exact intra-quarter roll rule is second-order, so this is an
acceptable, explicitly-documented limitation rather than a definitional change.
The bespoke roll adapter is moot for free data and is **not** built (YAGNI).

---

## What was deliberately NOT built

- No position sizing / margin / order logic (that is trading).
- No bespoke per-contract roll adapter (free data can't feed it; moot).
- No modification to frozen carry code or spot pipelines.
- No latency/microstructure model (S4 is out of scope).

## Tests

`tests/test_fx_futures_carry_diagnostic.py` (6, no network): registry quote
convention; month-end resample + USD≡1; direct USD-per-currency mapping (no
inversion); HML dollar-neutrality; diagnostic runs and is **price-only**
(matches `forward_spot_return` to 1e-12); `drop_one_currency` keys. All pass.
