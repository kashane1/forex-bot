# Financing Observed-Fixture Schema

**Date:** 2026-05-23 · **Branch:** `research-financing-rate-source-fixtures-001`
Phase 1 · `strategy_evidence: false`

Defines the on-disk fixture format for **observed financing
events** and **per-(date, instrument) financing rates** used by
`research/financing/`. Strictly aligned with the existing
[`ObservedFinancingEvent`](../../src/forex_bot/domain/transactions.py)
schema so a future capture pilot's output normalizes into the
same shape without an additional translation layer.

> Fixtures are committed local data. They are **synthetic**, not
> real broker exports. They do not establish historical
> financing, do not lift the live-promotion blocker, and do not
> approve any strategy.

## 1. File format and top-level shape

Every fixture is a UTF-8 JSON file with two top-level shapes —
**event fixtures** and **rate fixtures**. The loader picks the
shape from the `"kind"` field at the top.

```json
{
  "kind": "observed_financing_events",
  "schema_version": 1,
  "synthetic": true,
  "provenance": "<one-line description of what this fixture demonstrates>",
  "account_currency": "USD",
  "account_id_hash": "<64-char SHA-256 hex>",
  "events": [ ... ]
}
```

or

```json
{
  "kind": "financing_rates",
  "schema_version": 1,
  "synthetic": true,
  "provenance": "<one-line description>",
  "rate_unit": "annual_bp",
  "missing_dates": [],
  "rates": [ ... ]
}
```

Top-level required fields, both shapes:

| field | type | meaning |
|---|---|---|
| `kind` | string | `"observed_financing_events"` or `"financing_rates"` |
| `schema_version` | integer | `1` for this version of the schema |
| `synthetic` | boolean | must be `true` for committed fixtures |
| `provenance` | string | one-line human description; loader stores it verbatim into the loaded object's `source` field |

Files **must not** contain any other top-level keys. The loader
rejects unknown top-level keys (`extra="forbid"` parity).

## 2. Event fixture rows

For `"kind": "observed_financing_events"`, the `events` array
contains rows whose shape mirrors
[`ObservedFinancingEvent`](../../src/forex_bot/domain/transactions.py)
field-for-field.

| field | type | required | meaning |
|---|---|:--:|---|
| `transaction_id` | string | ✓ | opaque broker transaction id; synthetic only in fixtures |
| `instrument` | string \| null | optional | e.g. `EUR_USD`, `USD_JPY`; `null` means account-level event |
| `trade_id` | string \| null | optional | per-trade breakdown id; synthetic only in fixtures |
| `units` | string \| null | optional | unsigned absolute position units, stringified `Decimal` |
| `financing` | string | ✓ | signed cashflow, stringified `Decimal`. **Sign convention: credit `>0`, debit `<0`** — identical to OANDA's `DAILY_FINANCING.financing` field and the canonical `ObservedFinancingEvent.financing` field |
| `time` | string | ✓ | ISO-8601 with explicit timezone offset (e.g. `2026-05-19T21:00:00+00:00`). **Naive timestamps are rejected.** |

Account-level fields live on the **file**, not on each row, to
avoid repetition:

- `account_currency` — string, 3 uppercase letters; copies into
  every loaded event's `currency`.
- `account_id_hash` — 64-char lowercase hex SHA-256; copies into
  every loaded event's `account_id_hash`. **Must not be a real
  account-id hash** for committed fixtures (use the SHA-256 of
  a literal string like `"fixture-account-001"`).

### 2.1 Decimal-as-string rationale

`units` and `financing` are stringified to preserve `Decimal`
precision through JSON. The loader parses them with
`Decimal(value)`. Bare numeric literals are **rejected** so a
JSON parser cannot silently coerce them to `float`.

### 2.2 Rules on synthetic ids

The loader **does not** verify that `transaction_id` or
`trade_id` are synthetic — only the fixture author is
responsible. The file-level `synthetic: true` flag is a
declaration of intent. The contributor's checklist (§7) makes
this explicit.

### 2.3 `event_key` parity

The fixture loader does **not** independently compute
`event_key`. The canonical `ObservedFinancingEvent.event_key`
derivation (sha1 of `transaction_id|instrument|trade_id`) is
preserved automatically because the loaded shape matches the
canonical schema field-for-field. A reconciliation test in
Phase 4 confirms that a loaded fixture row's `event_key`
matches a hand-computed sha1 (see
[`tests/research/test_financing_fixtures.py`]).

## 3. Rate fixture rows

For `"kind": "financing_rates"`, the `rates` array contains rows
that feed `TableRateSource`.

| field | type | required | meaning |
|---|---|:--:|---|
| `date_utc` | string | ✓ | `YYYY-MM-DD` UTC date |
| `instrument` | string | ✓ | `[A-Z]{3}_[A-Z]{3}` |
| `long_annual_bp` | number | ✓ | annual long-side rate, basis points; sign follows §4 |
| `short_annual_bp` | number | ✓ | annual short-side rate, basis points; sign follows §4 |

File-level fields:

- `rate_unit` — must be `"annual_bp"`; the only unit v1
  supports. Future versions could add `"bp_per_day"` and the
  loader would convert.
- `missing_dates` — optional list of `YYYY-MM-DD` strings
  representing dates the fixture deliberately omits to exercise
  the calculator's missing-rate fallback. The loader does not
  insert rows for these dates; it surfaces them so tests can
  assert "the fallback fired here".

`long_annual_bp` and `short_annual_bp` are JSON numbers (not
strings) because rate-source fixtures feed
`TableRateSource.rate_for(...)` which returns float-backed
`RatePair` values. Tests pin precision to 1e-9 where needed.

## 4. Sign convention

| domain | sign |
|---|---|
| `financing` (event row, OANDA convention) | credit `>0`, debit `<0` |
| `long_annual_bp` / `short_annual_bp` (rate row) | applies the §4 convention from `docs/research/FINANCING_MODEL_PROTOCOL.md`: positive ⇒ the position **receives** (credit); negative ⇒ the position **pays** (debit) |
| `cashflow_home` on a calculator-emitted event | mirrors the rate sign ⇒ credit `>0`, debit `<0` |
| `cashflow_home_stress` on a calculator-emitted event | clamped to `≤0` ⇒ stress mode never assumes a credit |

A long position with `long_annual_bp = -36.5` (= -0.1 bp/day)
*pays* 0.1 bp/day on its notional. A short position with
`short_annual_bp = +18.25` (= +0.05 bp/day) *receives* 0.05
bp/day.

## 5. Timezone requirements

- All datetimes are **ISO-8601 with explicit offset**
  (`+00:00`, `-04:00`, …).
- The loader **rejects** naive timestamps (no `tzinfo`) via the
  same `ValueError` semantics as `PositionInterval`.
- Dates in `rate_unit` rows are **UTC dates**. The calculator
  decides whether a position interval crosses the UTC
  rollover-hour boundary on each date.
- Fixture authors should not embed local time without an
  offset; if a fixture targets a New York 17:00 rollover, the
  fixture row should be `21:00:00+00:00` (NY EST) or the
  equivalent UTC offset, with a `provenance` note.

## 6. Account-currency assumptions

- `account_currency` is exactly **one** value per file — fixtures
  do not mix home currencies. A campaign that needs both USD-
  and EUR-home runs supplies two fixture files.
- Loaded events copy this value into their `currency` field,
  matching the canonical `ObservedFinancingEvent.currency`
  semantics ("the account home currency the financing settled
  in").
- Default in v1 examples: `"USD"`. Other 3-letter ISO 4217
  codes are accepted; the loader validates the `^[A-Z]{3}$`
  shape only.

## 7. Instrument naming, units, sign

- Instrument names follow OANDA's `BASE_QUOTE` convention with
  underscore: `EUR_USD`, `USD_JPY`, `EUR_GBP`.
- `units` is the **unsigned absolute** position size at the
  moment of the rollover. The fixture row does not encode
  direction; direction is implicit in the sign of `financing`
  (a long position with negative carry shows `financing < 0`;
  a short with negative carry shows `financing < 0` as well).
  To make the direction explicit in event fixtures, supply
  `trade_id`s whose synthetic naming carries the side (e.g.
  `"trade_id": "synthetic-long-eu-1"`); this is a *convention*,
  not a schema constraint.
- For rate fixtures, direction is explicit: separate
  `long_annual_bp` and `short_annual_bp` per row.

## 8. Rollover-date and triple-swap representation

- Event fixtures encode rollover events *one per row* — the row
  is dated at the actual rollover moment. The fixture does
  **not** encode the triple-swap multiplier explicitly;
  Wednesday rollover rows simply carry a financing value 3×
  the surrounding rows' magnitude (matching how OANDA
  `DAILY_FINANCING` transactions arrive — a single
  transaction at the Wednesday rollover with the larger
  amount).
- Rate fixtures encode **annualized** rates per date; the
  `triple_swap_weekday` knob lives on
  `FinancingCalculatorConfig` (default Wednesday). A rate
  fixture that wants to test Wednesday triple-swap behaviour
  simply provides the Wednesday rate; the calculator
  multiplies.

## 9. Weekend-skip representation

- Event fixtures **do not** emit rollover events for Saturday
  or Sunday (no broker `DAILY_FINANCING` arrives on those
  days).
- Rate fixtures **may** include weekend dates; the calculator's
  `skip_weekends` config (default True) suppresses them. A
  weekend-skip-disabled run will consume those dates.

## 10. Missing-rate handling

Rate fixtures express missing dates in two ways:

1. **Omission** — the date simply isn't in `rates`. The
   calculator's `missing_rate_policy=conservative` (default)
   will fire its fallback and flag the event.
2. **Explicit `missing_dates`** — the date is listed in the
   top-level `missing_dates` array. The loader surfaces this
   list separately so tests can assert which dates are
   intentional gaps vs accidental omissions.

A test asserts that every date in `missing_dates` is also
absent from `rates` (the fixture's two representations agree).

## 11. How fixtures differ from real broker exports

| dimension | real OANDA export | committed fixture |
|---|---|---|
| `account_id` | real, must hash before storing | hash of a literal fixture string; **never** a real id |
| `transaction_id` | real broker id | synthetic stable string (e.g. `fix-txn-eur-001`) |
| `trade_id` | real broker id | synthetic stable string |
| `time` | precise broker timestamp | ISO-8601 UTC, hand-picked for the case being demonstrated |
| File size | can be megabytes | < 10 KB per file (enforced by §7 of the sprint plan) |
| `synthetic` | always `false` (real data) | always `true` (committed fixture) |
| `provenance` | source-system label (e.g. `oanda-practice`) | one-line human description of the case |
| Storage path | the `observed_financing_events` table | `research/financing/fixtures/*.json`, then loaded into memory at test time |
| Credential surface | hashing required at the broker boundary | already hashed; no credential ever present |

A real export normalized into this fixture format is **not**
something we ship — the schema lives here as a reference for
the future capture pilot, which will write directly to the
`observed_financing_events` table.

## 12. How future observed-capture data normalizes into this format

The forward path (covered by
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md),
Phase 5):

1. **Capture pipeline** subscribes to the OANDA transaction
   stream (read-only, no orders), parses `DAILY_FINANCING`
   transactions through the existing
   [`broker/mapping.map_daily_financing`](../../src/forex_bot/broker/mapping.py),
   and writes events to the `observed_financing_events` table.
2. **Hashing happens at the broker boundary** before any event
   reaches the table; raw account ids are never stored.
3. **Export step (optional)** dumps captured events to a
   fixture-shaped JSON file for offline research:
   - `kind`: `"observed_financing_events"`
   - `schema_version`: `1`
   - `synthetic`: `false`  ← the only field that changes
     between fixtures and real exports
   - `account_currency`: the practice account's home currency
   - `account_id_hash`: the captured hash (already redacted)
   - `provenance`: a label like `"oanda-practice-2026-05-19"`
   - `events`: the table's rows for the chosen window
4. **The loader** in `research/financing/fixtures.py` accepts
   both `synthetic: true` and `synthetic: false`, but tests pin
   that committed files under `research/financing/fixtures/`
   always carry `synthetic: true` (rule 16 of the plan).

The fixture format and the capture pipeline's dump shape are
therefore intentionally identical. The loader does not care
which side wrote the file.

## 13. Loader-rejection rules (preview)

The loader (Phase 3) raises `FixtureValidationError` for:

- unknown top-level keys
- missing required top-level fields
- `synthetic` not boolean
- `schema_version != 1`
- `kind` not in `{"observed_financing_events", "financing_rates"}`
- (event fixtures) `account_id_hash` not a 64-char lowercase
  hex digest
- (event fixtures) `account_currency` not matching
  `^[A-Z]{3}$`
- (event fixtures) `events` not an array
- (event row) missing `transaction_id` / `financing` / `time`
- (event row) `time` naive (no `tzinfo`)
- (event row) `units` / `financing` not a string (numeric
  literal forbidden)
- (event row) `units` / `financing` not parseable as `Decimal`
- (event row) `instrument` set but not `[A-Z]{3}_[A-Z]{3}`
- (rate fixtures) `rate_unit != "annual_bp"`
- (rate fixtures) `rates` not an array
- (rate row) missing `date_utc` / `instrument` /
  `long_annual_bp` / `short_annual_bp`
- (rate row) `date_utc` not `YYYY-MM-DD`
- (rate row) `instrument` not `[A-Z]{3}_[A-Z]{3}`
- (rate row) `long_annual_bp` / `short_annual_bp` not numeric
- `missing_dates` entry also present in `rates`
- duplicate `(date_utc, instrument)` row in `rates`
- file contains a top-level key besides those declared above

Every rejection carries a strict, human-readable message
naming the file path, the row index (where applicable), and
the offending field.

## 14. Determinism

- Loaded events are sorted by
  `(time, instrument or "", trade_id or "")`. Two loads of the
  same file return identical lists.
- `TableRateSource.rate_for(...)` is already deterministic for
  any given input table; the loader does not introduce
  iteration order or hash-seed dependence.
- Dumping a loaded fixture (for diagnostic purposes) uses
  sorted keys, ISO-8601 dates, 2-space indent, identical to
  the calculator's `dump_events_json`.

## 15. Cross-links

- Sprint plan:
  [`FINANCING_RATE_SOURCE_FIXTURES_001_PLAN.md`](FINANCING_RATE_SOURCE_FIXTURES_001_PLAN.md)
- Canonical `ObservedFinancingEvent` schema:
  [`src/forex_bot/domain/transactions.py`](../../src/forex_bot/domain/transactions.py)
- Existing parser:
  [`src/forex_bot/broker/mapping.py`](../../src/forex_bot/broker/mapping.py)
  (`map_daily_financing` + `observed_financing_events`)
- Observed-event capture design (dormant):
  [`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md)
- Calculator protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Future-capture pilot spec (Phase 5 of this sprint):
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
