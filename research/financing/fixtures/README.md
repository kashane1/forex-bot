# research/financing/fixtures — synthetic observed-financing fixtures

Tiny, committed, hand-built fixture files exercising every
protocol-relevant case for the `research/financing/` calculator
and the loader in `research/financing/fixtures.py`. Every file
is **synthetic** — no real account ids, no real transaction
ids, no broker export.

> `strategy_evidence: false`. These fixtures are research-only
> diagnostic infrastructure. They do not approve a strategy.
> CAMPAIGN_002 remains REJECT. `configs/approved_strategies.yaml`
> stays empty. Paper / demo / live remain blocked. The
> calculator's `financing_treatment` over these fixtures remains
> `estimated`; `MODELED` is not reachable through any file here.

## Schema

See [`docs/research/FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](../../../docs/research/FINANCING_OBSERVED_FIXTURE_SCHEMA.md)
for the field-by-field schema (two top-level shapes:
`observed_financing_events` and `financing_rates`).

## Files

| file | kind | what it demonstrates |
|---|---|---|
| `observed_eur_usd_long_debit.json` | events | A 4-day long EUR_USD position with two Tue/Thu rollovers, both debits |
| `observed_eur_usd_short_credit.json` | events | A 2-day short EUR_USD position with one rollover that arrives as a credit (positive carry on the short side) |
| `observed_usd_jpy_precision.json` | events | A USD_JPY (USD-base) event with JPY-precision entry-price-region values; financing settles in the USD home currency |
| `observed_usd_cad_short_debit.json` | events | A 5-day short USD_CAD position with three rollovers including a Wednesday triple (encoded as a single Wednesday row whose `financing` is ~3× the surrounding rows) |
| `observed_same_day_no_rollover.json` | events | A position opened and closed within a single UTC day before the rollover boundary → zero events. File ships an empty `events: []` to assert the loader handles this case cleanly |
| `observed_multi_day_with_triple.json` | events | A 5-day long EUR_USD position spanning Mon → Fri with four rollovers, including the Wednesday triple |
| `observed_missing_rate_fallback.json` | events | An event-fixture variant that omits a known-missing date to assert the loader does not invent rows |
| `observed_weekend_skip.json` | events | A position held across a weekend, with rollovers only on Fri and Mon (no Sat/Sun rows present) |
| `rates_two_week_eur_usd.json` | rates | Two business weeks of EUR_USD long/short rates with one explicit `missing_dates` entry to exercise the calculator's conservative fallback |

## Synthetic id provenance

- `account_id_hash` in every event file is the SHA-256 of the
  literal string `fixture-account-001`:

  ```
  c4e91d9f7c03827938cbb2c82608bba023e98f23d52b2f84784cbcf9652df69f
  ```

  This is **not** a real account-id hash. The literal preimage
  is in this README so reviewers can verify.

- `transaction_id` and `trade_id` values follow `fix-txn-<pair>-<n>`
  and `fix-trade-<pair>-<n>` conventions. They are stable,
  short, and obviously non-real.

## Contributor checklist

When adding a new fixture file under this directory:

- [ ] File is under 10 KB.
- [ ] `synthetic` is `true`.
- [ ] `account_id_hash` is the documented fixture hash above
      (never a real account-id hash).
- [ ] `transaction_id` / `trade_id` are obviously non-real
      strings (start with `fix-`).
- [ ] `time` is ISO-8601 with explicit UTC offset.
- [ ] `units` and `financing` are stringified `Decimal`s, not
      bare numbers.
- [ ] `provenance` is a one-line human description of what the
      fixture demonstrates.
- [ ] Adding the file makes a Phase 4 test that loads it pass;
      no fixture is committed without a test that consumes it.
- [ ] Archive validator (`scripts/validate_research_archive.py`)
      and freeze checker (`scripts/check_research_freeze.py`)
      remain green after the addition.
