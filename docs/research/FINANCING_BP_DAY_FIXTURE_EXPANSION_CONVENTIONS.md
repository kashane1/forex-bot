# Financing bp/day Fixture Expansion — Conventions

**Date:** 2026-05-23 · **Branch:** `research-financing-bp-day-fixture-expansion-001`
Phase 1 · `strategy_evidence: false`

Conventions for adding **synthetic** per-pair financing rate
fixtures under
[`research/financing/fixtures/`](../../research/financing/fixtures/).
Fixtures conform to the v1 schema
([`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md))
and feed `TableRateSource(treatment=ESTIMATED)`.

> These conventions are for hand-built synthetic data only. A
> future credentialed pilot capture produces real data through
> [`scripts/capture_oanda_observed_financing_pilot.py`](../../scripts/capture_oanda_observed_financing_pilot.py)
> with `synthetic: false`; that path is unchanged by this
> sprint. `MODELED` financing remains unreachable through any
> fixture, real or synthetic.

## 1. Synthetic-rate convention

- Every committed fixture is **hand-built**, not derived
  from a broker source.
- `synthetic: true` is mandatory.
- The `provenance` string explains what the fixture
  demonstrates (e.g. "synthetic GBP_USD rates — long
  modestly negative, short modestly positive — for
  reconciliation pattern coverage"). It must not contain a
  real account id, a real broker transaction id, or any
  credential value.
- Rate magnitudes are chosen for **pedagogical clarity**,
  not realism. Where a fixture exists to reconcile against
  a specific observed-event fixture, the rate is chosen so
  the calculator's stress output matches the observed
  values exactly at synthetic `1e-9` tolerance.
- Where no observed companion exists, the rate is chosen
  to exercise either a **clear debit** or a **clear
  credit** pattern, with the sign documented in
  `provenance`.

## 2. Sign convention

Inherited verbatim from
[`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
§4:

- `long_annual_bp > 0` ⇒ a long position **receives**
  financing (credit).
- `long_annual_bp < 0` ⇒ a long position **pays**
  financing (debit).
- `short_annual_bp > 0` ⇒ a short position **receives**.
- `short_annual_bp < 0` ⇒ a short position **pays**.

Across the 6 new fixtures, signs are deliberately varied so
no single test caches a misleading "all-long-debits"
intuition:

| pair | long_annual_bp sign | short_annual_bp sign | rationale |
|---|:--:|:--:|---|
| GBP_USD | `−` | `+` | typical USD-quote with USD-yield > GBP-yield |
| USD_JPY | `+` | `−` | USD-yield > JPY-yield → long USD/JPY earns carry |
| AUD_USD | `+` | `−` | classic AUD-carry pattern (long AUD earns) |
| USD_CAD | `−` | `+` | USD vs CAD spread varies; pick debit-long for variety |
| USD_CHF | `+` | `−` | CHF low rates → long USD/CHF earns |
| NZD_USD | `+` | `−` | NZD-carry similar to AUD |

These are illustrative shapes, not historical claims. The
sign-variety check is enforced by a Phase 4 test
(`test_rate_sign_variety_across_pairs`).

## 3. Long / short convention

- Per-row independence: `long_annual_bp` and
  `short_annual_bp` may have any combination of signs and
  magnitudes; the calculator selects whichever side
  matches the position's `side`.
- No symmetry rule. A fixture may set
  `long_annual_bp = -18.25` and `short_annual_bp = +9.125`
  (the EUR_USD fixture's pattern) or any other
  combination; the calculator handles both.

## 4. USD-quote pair convention

For pairs of the form `XXX_USD` (EUR_USD, GBP_USD, AUD_USD,
NZD_USD):

- Notional in USD home currency: `units × entry_price`
  (computed by the calculator).
- Cashflow units in the reconciliation report are USD.
- Synthetic rate magnitudes are typically small (single-
  digit annual bp) — the resulting per-day cashflow is on
  the order of cents for a 10,000-unit position.

## 5. USD-base pair convention

For pairs of the form `USD_YYY` (USD_JPY, USD_CAD,
USD_CHF):

- Notional in USD home currency: `units` (already USD;
  the calculator does not multiply by `entry_price`).
- Cashflow units in the reconciliation report are USD,
  identical to USD-quote pairs.
- This is the same convention as the existing per-trade
  overlay in `src/forex_bot/financing.py` (`_USD_BASE`
  set) and is honoured by the calculator's
  `_notional_home` helper.

## 6. JPY precision convention

For `USD_JPY` (the only JPY pair in the H4 universe):

- JPY-precision entry prices (e.g. `155.123`) are
  meaningless for the bp/day reconciliation in USD home
  currency — `notional_home = units` regardless of price.
- The fixture's rate magnitudes are chosen so reconcile
  arithmetic lands on stable cents-region values
  (`bp/day * units / 10000`).
- The existing
  [`observed_usd_jpy_precision.json`](../../research/financing/fixtures/observed_usd_jpy_precision.json)
  + `long_annual_bp = 18.25` example shows the pattern:
  `+0.05` bp/day × 10000 USD = `+0.05` USD credit per
  rollover.

## 7. Missing-rate convention

- Every new fixture **must** include at least one entry in
  `missing_dates`, **except** where the fixture
  specifically targets a "no-missing-rate" reconciliation
  path. The default convention: include exactly one
  intentional missing date, chosen to fall inside the
  window so the calculator's `conservative` and `skip`
  policies are both exercisable against the fixture.
- The fixture's loader validates `missing_dates` does not
  overlap with `rates`. (Existing rail in
  [`research/financing/fixtures.py`](../../research/financing/fixtures.py).)
- The `provenance` string explains *why* the missing date
  is missing (typically: "exercise the conservative
  fallback").

## 8. Wednesday / triple-swap compatibility

- Rate-fixture rows are **annualized**; the
  `triple_swap_weekday` multiplier (default Wednesday)
  lives on `FinancingCalculatorConfig` and is applied by
  the calculator, not the fixture.
- A fixture that wants to exercise Wednesday triple-swap
  simply ensures the rate is defined on the relevant
  Wednesday; the calculator multiplies by 3 automatically.
- The fixtures in this sprint use the same two-week May
  2026 window as
  [`rates_two_week_eur_usd.json`](../../research/financing/fixtures/rates_two_week_eur_usd.json)
  to keep tests cross-comparable. That window contains
  one Wednesday (2026-05-20), one Wednesday at the start
  of the next week (2026-05-27), so triple-swap is
  naturally exercised.

## 9. Weekend-skip compatibility

- Rate-fixture rows **may** include weekend dates;
  whether the calculator emits an event for a weekend
  date depends on `skip_weekends` (default True). A
  fixture that wants to exercise the weekend-skip path
  simply omits weekend dates (matching real-broker
  behaviour) — that is what the new fixtures do.
- The existing
  [`observed_weekend_skip.json`](../../research/financing/fixtures/observed_weekend_skip.json)
  event fixture demonstrates the observed side of the
  same pattern (Fri + Mon rows, no Sat/Sun).

## 10. Why values are synthetic and not broker-observed

- OANDA's v20 REST API does not publish a historical
  financing-rate time series; there is nothing to derive
  per-day rates from for 2020–2026.
- The practice account's `longRate` / `shortRate` are 0
  per
  [`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md);
  even a credentialed practice account cannot serve as a
  source of rate values.
- A future capture pilot can produce real **observed
  events**, but those are after-the-fact charges, not
  per-day rates. Deriving rates from events is a separate
  step (a future `ObservedRateSource` would do it; the
  current sprint does not implement one).
- Until either a long forward-capture window completes or
  a market-rate-derived model is implemented (the latter
  explicitly **not** recommended without ground-truth
  data), all rate fixtures in this repo are synthetic.

## 11. Why fixtures are ESTIMATED, not MODELED

- The fixture loader
  ([`research/financing/fixtures.py`](../../research/financing/fixtures.py))
  refuses
  `TableRateSource(treatment=MODELED)` at construction —
  enforced by an existing test in the sister sprint's
  `test_financing_rates.py`.
- `calculate_run` refuses any rate source self-reporting
  `MODELED`.
- The reconciliation CLI's `_build_report` raises
  `RuntimeError` if asked to emit `modeled` as the
  treatment.
- The capture script never emits a rate source at all;
  observed events feed *into* rate sources downstream.

Adding more synthetic fixtures changes none of these
properties. The full 5-criterion MODELED checklist
(per
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
§11) is unchanged by this sprint.

## 12. Contributor checklist for a new pair fixture

Before committing a new `rates_*_<pair>.json`:

- [ ] `kind == "financing_rates"`, `schema_version == 1`,
      `synthetic == true`, `rate_unit == "annual_bp"`.
- [ ] `provenance` is a one-line description; no account
      id, no broker transaction id, no credential.
- [ ] At least one entry in `missing_dates` (unless
      explicitly justified in `provenance`); cross-checked
      against `rates` (loader rejects overlap).
- [ ] No duplicate `(date_utc, instrument)` rows.
- [ ] Signs of `long_annual_bp` / `short_annual_bp`
      explicitly documented in `provenance` and consistent
      with this sprint's per-pair table (§2).
- [ ] File size < 10 KB (rule from the sister sprint).
- [ ] All dates use ISO-8601 `YYYY-MM-DD`.
- [ ] All numeric rate fields are JSON numbers (not
      stringified Decimals — only `units` / `financing`
      on event fixtures are stringified).
- [ ] Loaded successfully by
      `research.financing.load_rate_fixture(...)`
      (Phase 4 test covers this for every committed file).
- [ ] Archive validator and freeze checker remain green.
- [ ] Secret scanner remains green.

## 13. Cross-links

- Sprint plan:
  [`FINANCING_BP_DAY_FIXTURE_EXPANSION_001_PLAN.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_001_PLAN.md)
- Calculator protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Fixture schema:
  [`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md)
- Reconciliation CLI protocol:
  [`FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md`](FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md)
- Future-capture pilot spec:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Sister sprint summaries:
  [`RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md`](RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md),
  [`RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md`](RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
