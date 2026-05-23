# Financing bp/day Fixture Expansion Sprint 001 — Plan

**Date:** 2026-05-23 · **Branch:** `research-financing-bp-day-fixture-expansion-001`
**Base commit:** `1a795be` (HEAD of `research-financing-observed-capture-pilot-001`)
`strategy_evidence: false`

Pure docs + synthetic-data sprint. Expands the synthetic
financing rate fixtures so all **seven** CAMPAIGN_002 H4
universe pairs have deterministic rate fixtures for future
reconciliation and stress testing. No broker call, no
credential read, no network, no production-code change.

> **No strategy is approved. CAMPAIGN_002 remains REJECT.**
> Paper / demo / live remain blocked. No QC / LEAN. **No OANDA
> API calls.** No new strategy campaign. **This sprint cannot,
> and will not, approve a strategy or make financing
> `MODELED`.** Every committed fixture carries
> `synthetic: true` and feeds rate sources that declare at most
> `ESTIMATED`.

## 1. Purpose

The reconciliation CLI
([`scripts/reconcile_financing_fixtures.py`](../../scripts/reconcile_financing_fixtures.py))
and the calculator
([`research/financing/`](../../research/financing/)) can
consume rate fixtures for any pair; today only `EUR_USD` has a
committed fixture
([`rates_two_week_eur_usd.json`](../../research/financing/fixtures/rates_two_week_eur_usd.json)).
This sprint adds the other six H4 universe pairs so:

- The reconciliation CLI has a non-EUR test surface; the
  Phase 5 batch runs exercise it.
- Any future credentialed pilot capture (or any retrospective
  analysis) has a rate fixture for **every** pair it might
  observe.
- The conventions doc (Phase 1) pins how a contributor
  should choose sign, missing-dates, and triple-swap
  compatibility for any new synthetic fixture — so a
  follow-on sprint can copy the pattern cleanly.

## 2. Non-goals

- **Not real data.** Fixtures are hand-built synthetic. No
  broker call. No OANDA. No `.env`.
- **Not a strategy.** No backtest, no campaign, no signal,
  no order.
- **Not a calculator or loader change.**
  `research/financing/calculator.py` and `fixtures.py` are
  **not** modified.
- **Not a CAMPAIGN_002 revival.** No CAMPAIGN_002 artifact
  touched.
- **Not a `MODELED` claim.** Fixtures continue to feed
  `TableRateSource(treatment=ESTIMATED)`; the four-layer
  MODELED refusal across the loader, calculator,
  reconciliation CLI, and capture script remains in place.
- **Not a fixture-size expansion.** Each new file is <10 KB;
  the convention from the prior sprint stands.
- **Not a paper / demo / live enabler.** Refusals stand.

## 3. Safety invariants

1. `configs/approved_strategies.yaml` stays `approved: []`.
2. CAMPAIGN_002 remains REJECT.
3. Paper / demo loops keep refusing; no `live-loop` exists.
4. No QC / LEAN command.
5. **No OANDA API call.** No transaction-stream query, no
   pricing read, no candle fetch.
6. **No `.env` read.** No credential value printed.
7. **No `*.sqlite3` or candle CSV** committed. Per-run
   reconciliation outputs (Phase 5) live under `/tmp/` and
   are not committed.
8. `src/forex_bot/`, `research/financing/{models,rates,calculator,reporting,fixtures}.py`,
   `research/financing/__init__.py`, and `research/walk_forward/`
   are **not modified**.
9. `scripts/reconcile_financing_fixtures.py` and
   `scripts/capture_oanda_observed_financing_pilot.py` are
   **not modified**.
10. No new external dependency is added.
11. Every new fixture file carries `synthetic: true`, a
    non-account-identifying `provenance` string,
    `schema_version: 1`, no real broker ids, no
    credential-shaped strings, and is <10 KB.
12. Every fixture continues to feed
    `TableRateSource(treatment=ESTIMATED)`. The loader
    already refuses `MODELED` for any input.

## 4. Current fixture coverage

From the sister sprints — committed under
[`research/financing/fixtures/`](../../research/financing/fixtures/):

| file | kind | pair(s) |
|---|---|---|
| `observed_eur_usd_long_debit.json` | events | EUR_USD |
| `observed_eur_usd_short_credit.json` | events | EUR_USD |
| `observed_usd_jpy_precision.json` | events | USD_JPY |
| `observed_usd_cad_short_debit.json` | events | USD_CAD |
| `observed_same_day_no_rollover.json` | events | (empty) |
| `observed_multi_day_with_triple.json` | events | EUR_USD |
| `observed_missing_rate_fallback.json` | events | EUR_USD |
| `observed_weekend_skip.json` | events | EUR_USD |
| `rates_two_week_eur_usd.json` | rates | **EUR_USD only** |
| `README.md` | docs | — |

Event-fixture coverage is OK (EUR_USD, USD_JPY, USD_CAD).
**Rate-fixture coverage is the gap** — only EUR_USD has a
committed rates file. This sprint closes that gap for the
remaining six H4 pairs.

## 5. Target pair coverage

After this sprint, `research/financing/fixtures/` will
contain one rate fixture for **each** of the seven H4
universe pairs:

| pair | rate fixture (this sprint) | base / quote convention |
|---|---|---|
| EUR_USD | `rates_two_week_eur_usd.json` (already committed) | USD-quote |
| GBP_USD | `rates_two_week_gbp_usd.json` (new) | USD-quote |
| USD_JPY | `rates_two_week_usd_jpy.json` (new) | USD-base + JPY precision |
| AUD_USD | `rates_two_week_aud_usd.json` (new) | USD-quote |
| USD_CAD | `rates_two_week_usd_cad.json` (new) | USD-base |
| USD_CHF | `rates_two_week_usd_chf.json` (new) | USD-base |
| NZD_USD | `rates_two_week_nzd_usd.json` (new) | USD-quote |

Phase 3 will add a small set of observed-event companions
where they're useful for tests — priority on filling the
USD-base / JPY-precision / non-EUR USD-quote gaps that the
existing event fixtures don't already cover. Phase 1's
conventions doc will pin the rules for each pair's
sign/precision/missing-rate choices.

## 6. Planned phases

| phase | output | commit |
|---|---|---|
| 0 | This plan doc | docs-only |
| 1 | `FINANCING_BP_DAY_FIXTURE_EXPANSION_CONVENTIONS.md` | docs-only |
| 2 | 6 new rate-fixture JSON files | data |
| 3 | small set of observed-event companions (if useful) | data |
| 4 | test additions / extensions | tests |
| 5 | `FINANCING_BP_DAY_FIXTURE_EXPANSION_SYNTHETIC_RUNS.md` | docs (no committed runs) |
| 6 | `FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md` + `EVIDENCE_INDEX.md` | docs |
| 7 | `RESEARCH_FINANCING_BP_DAY_FIXTURE_EXPANSION_001_SUMMARY.md` | docs |

Each phase ends with a commit and the standard validators
(`pytest -q`, `ruff check ...`, archive validator, freeze
checker, secret scanner).

## 7. Expected artifacts

- **New rate fixtures (6):**
  - `research/financing/fixtures/rates_two_week_gbp_usd.json`
  - `research/financing/fixtures/rates_two_week_usd_jpy.json`
  - `research/financing/fixtures/rates_two_week_aud_usd.json`
  - `research/financing/fixtures/rates_two_week_usd_cad.json`
  - `research/financing/fixtures/rates_two_week_usd_chf.json`
  - `research/financing/fixtures/rates_two_week_nzd_usd.json`
- **Small set of observed-event companions (Phase 3):**
  one each for the USD-base, JPY-precision, and non-EUR
  USD-quote paths that exercise a non-EUR reconciliation.
- **Conventions doc** (Phase 1).
- **Synthetic-runs doc** (Phase 5; no committed
  reconciliation outputs).
- **Status doc** (Phase 6).
- **Summary doc** (Phase 7).
- **`fixtures/README.md`** updated to list the new files.
- **`EVIDENCE_INDEX.md`** updated with a new subsection.

## 8. Validation surface

Per-phase: `python -m pytest -q`, archive validator, freeze
checker, secret scanner.

Final phase (Phase 7) adds:

- `ruff check src tests scripts research/parity_verifier research/walk_forward research/financing`
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml`
  (must refuse)
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml`
  (must refuse)
- `python -m forex_bot.cli --help` (must not list
  `live-loop`)

## 9. Explicit statement on approval and MODELED

**This sprint cannot approve a strategy.** Adding synthetic
rate fixtures, even for all seven pairs, satisfies **none**
of the five MODELED criteria from
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
§11:

| # | criterion | status |
|---:|---|---|
| 1 | ≥ 60 captured rollovers across the traded universe | unchanged — capture pilot has not run |
| 2 | per-event reconciliation passes against captured data | unchanged — no captured data |
| 3 | `MODELED` `FinancingModel` implementation | not implemented |
| 4 | engine-PnL integration | not implemented |
| 5 | documented human approval | not granted |

Fixture expansion is **preparatory infrastructure** for a
future credentialed capture sprint. It is not, and cannot
be, evidence that the calculator matches real broker
behaviour. Every fixture continues to feed a rate source
declaring `ESTIMATED` at best; the loader refuses
`MODELED`; the calculator refuses `MODELED`; the
reconciliation CLI refuses `MODELED`.

## 10. Cross-links

- Calculator protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Fixture schema:
  [`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md)
- Reconciliation CLI protocol:
  [`FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md`](FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md)
- Observed-capture pilot status (Phase 4 of that sprint did
  not run — no creds; this sprint prepares the rate-fixture
  side for when it does):
  [`FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`](FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md)
- Future-capture pilot spec:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Sister sprint summaries:
  [`RESEARCH_FINANCING_MODEL_001_SUMMARY.md`](RESEARCH_FINANCING_MODEL_001_SUMMARY.md),
  [`RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md`](RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md),
  [`RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md`](RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md),
  [`RESEARCH_FINANCING_OBSERVED_CAPTURE_PILOT_001_SUMMARY.md`](RESEARCH_FINANCING_OBSERVED_CAPTURE_PILOT_001_SUMMARY.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
