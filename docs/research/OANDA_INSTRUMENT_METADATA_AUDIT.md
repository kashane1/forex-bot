# OANDA Instrument Metadata Audit — `oanda-practice-readonly-001` Phase 3

**Generated:** 2026-05-22T20:27:29.954685+00:00 · **Branch:** `oanda-practice-readonly-001`
**Config:** `configs/paper.yaml` · **Overall:** **PASS**

> Read-only diagnostic. Instrument metadata was fetched from the OANDA **practice** `GET /v3/accounts/{id}/instruments` endpoint. **No order was submitted.** This is not a strategy campaign and produces no trading verdict.

## Environment

| field | value |
|---|---|
| OANDA host | `https://api-fxpractice.oanda.com` |
| account id (redacted) | `101…001` |
| instruments exposed by account | 68 |

## Six-pair H4 research universe

| instrument | type | pip_loc | pip_size | disp_prec | units_prec | min_size | margin_rate | stable fields |
|---|---|---|---|---|---|---|---|---|
| EUR_USD | CURRENCY | -4 | 0.0001 | 5 | 0 | 1 | 0.02 | OK |
| GBP_USD | CURRENCY | -4 | 0.0001 | 5 | 0 | 1 | 0.05 | OK |
| USD_JPY | CURRENCY | -2 | 0.01 | 3 | 0 | 1 | 0.05 | OK |
| AUD_USD | CURRENCY | -4 | 0.0001 | 5 | 0 | 1 | 0.03 | OK |
| USD_CAD | CURRENCY | -4 | 0.0001 | 5 | 0 | 1 | 0.02 | OK |
| USD_CHF | CURRENCY | -4 | 0.0001 | 5 | 0 | 1 | 0.03 | OK |

## Historical extra — NZD_USD (not in the six-pair universe)

NZD_USD was used by CAMPAIGN_001 / 002 / 003. It is audited here for completeness but is **kept separate** from the six-pair H4 research universe.

| instrument | type | pip_loc | pip_size | disp_prec | units_prec | min_size | margin_rate | stable fields |
|---|---|---|---|---|---|---|---|---|
| NZD_USD | CURRENCY | -4 | 0.0001 | 5 | 0 | 1 | 0.03 | OK |

## Required fields present

Every audited instrument exposes all six fields the bot relies on (instrument name, pip location, display precision, trade-units precision, minimum trade size, margin rate):

- **EUR_USD**: all required fields present.
- **GBP_USD**: all required fields present.
- **USD_JPY**: all required fields present.
- **AUD_USD**: all required fields present.
- **USD_CAD**: all required fields present.
- **USD_CHF**: all required fields present.
- **NZD_USD**: all required fields present.

## Precision & pip checks

Stable, intrinsic fields are checked against the repo's expectation. JPY-quoted pairs are expected at pip location -2 / display precision 3; all other majors at -4 / 5; trade-units precision 0 and minimum trade size 1 for every major.

- no mismatch — every audited instrument's stable fields match the repo's expectation.

### JPY pip handling

- **USD_JPY**: pip location -2, pip size `0.01` — `Instrument.pip_size = 10 ** pip_location` resolves JPY pips correctly.

## Margin checks (informational)

Margin rate is **broker / account / region specific** and varies; it is recorded as the authoritative live value, not pass/failed. Position sizing must read the live `margin_rate`, never a hard-coded constant.

- **EUR_USD**: live margin rate `0.02`.
- **GBP_USD**: live margin rate `0.05`.
- **USD_JPY**: live margin rate `0.05`.
- **AUD_USD**: live margin rate `0.03`.
- **USD_CAD**: live margin rate `0.02`.
- **USD_CHF**: live margin rate `0.03`.
- **NZD_USD**: live margin rate `0.03`.

## Differences from the local instrument cache

The repo has **no committed instrument-metadata cache** — instrument metadata is otherwise only fetched live (`bot sync-instruments` into the gitignored DB) or hard-coded in test fixtures (`tests/conftest.py`: EUR_USD pip -4 / precision 5, USD_JPY pip -2 / precision 3). This audit establishes the first committed, reproducible metadata record. The live stable fields match those test-fixture assumptions; the test-fixture margin rates (EUR_USD 0.02, USD_JPY 0.04) are illustrative only and are expected to differ from the live account's margin rates.

## Implications for sizing and PnL

- **Pip math:** `pip_size = 10 ** pip_location` — correct for both JPY (-2) and non-JPY (-4) majors, so pip-denominated stops, ATR filters, and spread filters size correctly.
- **Units precision 0:** all majors trade in whole units; `Instrument.round_units` floors to integer units.
- **Minimum trade size 1:** sizing must not emit sub-unit orders.
- **Margin rate:** sizing / margin checks must use the live `margin_rate` per instrument; it is variable and must not be assumed constant across instruments or over time.

## Blockers

- none — every audited instrument was found and every stable field matched the repo's expectation.

## Safety statement

- Read-only: only `GET /v3/accounts/{id}/instruments` was called. **No order was submitted, created, modified, or closed.**
- Practice environment only; the live host was never contacted.
- The account id is redacted; the access token was never printed or written. `strategy_evidence: false` — approves no strategy.
