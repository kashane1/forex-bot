# Multi-Market Data Acquisition Roadmap

**Purpose:** a prioritized plan for *how* each future market's data would
be acquired, stored, preprocessed, and integrated — so the next
implementation sprint can pick one item and execute it cleanly. This is a
**roadmap**, not an ingestion: nothing is fetched here, no broker/vendor
APIs are called, no credentials are used. Where a market needs paid data
or live credentials, that is recorded as a **blocker**, not an action.

## Ground rules (inherited)

- **Free/local first.** Prefer data already obtainable without paid feeds
  or live credentials. Paid/credentialed acquisition is a documented
  blocker for a human decision, never auto-performed.
- **Same execution-realism bar.** Every dataset must be lookahead-free,
  parity-checked, and carry an **instrument-specific cost model** before
  it can enter the front gate.
- **Reuse existing infra.** The current OANDA ingestion + research candle
  store + M1 materialization + parity/validation scripts
  (`scripts/ingest_oanda_candles_postgres.py`,
  `scripts/export_postgres_research_candles.py`,
  `scripts/materialize_m1_derived_timeframes.py`,
  `scripts/verify_m1_materialized_coverage.py`,
  `scripts/validate_m1_canonical_store.py`, and the loaders in
  `src/forex_bot/data/`) are the template; new markets extend it rather
  than replace it.

---

## Priority 1 — Non-USD FX crosses (the chosen first expansion)

- **Data source options:** same OANDA practice/historical candle source
  already used for the majors (read-only history). The eight crosses are
  standard OANDA instruments → **same source, same schema**.
- **Free/local options:** **yes** — identical to current majors; no new
  vendor. (If, and only if, OANDA history is unavailable without live
  calls, fall back to documenting the blocker; do not fetch under the
  freeze.)
- **Expected storage:** small — ~8 crosses × H4 bid/ask × ~6.4y ≈ the
  same per-instrument footprint as a major (low MB each); M1-derived
  timeframes materialized on demand as for the majors.
- **Preprocessing:** dedup/contamination check (the C015 lesson),
  lookahead-free aggregation, M1 materialization + coverage verification,
  and **instrument-specific spread/financing calibration** (do **not**
  reuse EUR_USD costs); window EUR_CHF around the 2015 SNB break.
- **Integration complexity:** **low** — same loaders, same cost-model
  shape, same parity harness; the only genuinely new work is per-cross
  cost calibration and registering them in the universe.

## Priority 2 — Additional / alternate FX data sources

- **Data source options:** a second FX feed (e.g. another retail/ECN
  vendor or a free historical FX dataset) to (a) extend history beyond
  ~6.4y and (b) **cross-check the cost model** across venues.
- **Free/local options:** partial — some free historical FX datasets
  exist; deep tick-level is usually paid.
- **Expected storage:** low–medium (longer history × more instruments).
- **Preprocessing:** **feed normalization** (timestamp/timezone, bid/ask
  vs mid, session boundaries) into the common schema; reconcile spreads
  against OANDA to quantify the cost-model's realism.
- **Integration complexity:** medium — a normalization adapter + a
  provenance/registry entry; conceptually compatible with the store.

## Priority 3 — Crypto (BTC/ETH + liquid alts)

- **Data source options:** abundant **free** public historical OHLCV from
  major venues/aggregators; funding-rate history for perpetuals.
- **Free/local options:** **yes — best free-data story** (deep, granular,
  free).
- **Expected storage:** medium–high (24/7, granular history, multiple
  symbols, plus funding series).
- **Preprocessing:** 24/7 calendar (no weekend gap), venue selection +
  dedup, **funding-rate cost model** (not FX swap), outlier/wick
  handling, optional cross-sectional universe assembly.
- **Integration complexity:** medium–high — new calendar/session
  assumptions and a funding-based cost model; bar schema otherwise
  compatible.

## Priority 4 — Futures (FX futures, then index/metal futures)

- **Data source options:** vendor historical futures (CME etc.); some
  free continuous series, deep clean history typically paid.
- **Free/local options:** partial.
- **Expected storage:** medium (per-contract + continuous series).
- **Preprocessing:** **continuous-contract roll** construction
  (back-adjusted vs ratio), contract calendar, basis/roll-based carry
  model, session handling.
- **Integration complexity:** medium — a futures adapter + roll logic are
  net-new; this is the main reason futures are sequenced after crypto
  despite their attractive cost profile.

## Priority 5 — Everything else (metals-as-FX, index CFDs, equities/ETFs)

- **Metals via OANDA (XAU/XAG):** **low** complexity (OANDA instruments,
  free/local) — could be pulled forward as a quick Tier-2 probe if a
  metals thesis appears; carry = lease/storage model.
- **Index CFDs via OANDA (US500/NAS100/…):** low–medium; retail
  financing cost model.
- **Equities/ETFs:** medium–high — corporate-action handling,
  survivorship-free universes, dividend adjustment; free EOD only,
  intraday paid. Lowest priority on complexity-vs-readiness.

---

## Priority summary

| Pri | Market | Free/local | Storage | New infra | Complexity |
|----:|--------|-----------|---------|-----------|------------|
| 1 | Non-USD FX crosses | yes | low | none (reuse) | **low** |
| 2 | Alt/extra FX feed | partial | low–med | normalization adapter | medium |
| 3 | Crypto | **yes** | med–high | 24/7 calendar + funding cost | med–high |
| 4 | Futures | partial | medium | roll + contract calendar | medium |
| 5 | Metals/index CFD/equities | mixed | mixed | per-class (actions, etc.) | low→high |

**Roadmap stance:** execute **Priority 1 first** (cheapest, reuses
everything, directly attacks crowding/breadth). Priorities 2–5 are staged
behind it and behind proof that the multi-market gate works end-to-end on
crosses. The single chosen next step is in
`NEXT_DATA_EXPANSION_DECISION.md`; its concrete implementation prompt is
in `NEXT_PROMPT_AFTER_MULTI_MARKET_FRONT_GATE.md`.
