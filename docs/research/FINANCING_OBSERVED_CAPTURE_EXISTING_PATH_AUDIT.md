# Observed-Financing Capture — Existing-Path Audit

**Date:** 2026-05-23 · **Branch:** `research-financing-observed-capture-pilot-001`
Phase 1 · `strategy_evidence: false`

A code-level audit of the existing repo path for observed
financing events. Documents what is already implemented and
identifies the minimal pilot-script wiring needed to fetch +
parse + dump real practice transactions, without modifying any
existing module.

> No broker call performed in this phase. CAMPAIGN_002 remains
> REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.

## 1. Summary

| concern | status | location |
|---|---|---|
| `ObservedFinancingEvent` schema (hashed account id, signed financing) | implemented | [`src/forex_bot/domain/transactions.py`](../../src/forex_bot/domain/transactions.py) |
| `hash_account_id(raw)` redactor at parser boundary | implemented | [`src/forex_bot/domain/transactions.py`](../../src/forex_bot/domain/transactions.py) |
| `map_daily_financing(payload, source, account_currency)` parser | implemented | [`src/forex_bot/broker/mapping.py`](../../src/forex_bot/broker/mapping.py) |
| `observed_financing_events(payload, ...)` per-transaction parser | implemented | [`src/forex_bot/broker/mapping.py`](../../src/forex_bot/broker/mapping.py) |
| `ObservedFinancingEventRepo` (idempotent insert by `event_key`) | implemented; dormant (table empty) | [`src/forex_bot/data/repositories.py`](../../src/forex_bot/data/repositories.py) |
| `observed_financing_events` table (migration v3) | implemented | [`src/forex_bot/data/migrations.py`](../../src/forex_bot/data/migrations.py) |
| Read-only `OandaBroker.get_transactions_since(last_tx_id)` | implemented | [`src/forex_bot/broker/oanda.py`](../../src/forex_bot/broker/oanda.py) |
| Read-only `OandaBroker.get_account_summary()` / `get_account_details()` | implemented | same |
| `OandaBroker(environment="practice")` hard-coded REST host | implemented | same |
| `submit_order` defense against live | implemented (raises `ConfigError`) | same |
| Read-only date-range `GET /v3/accounts/{id}/transactions` | **not exposed** as a helper | gap |
| `tags`-based PRACTICE confirmation | **not exposed** by `AccountDetails` | gap (handled differently — see §4) |
| `synthetic: false` capture-dump tool | **does not exist** | gap (this sprint's Phase 2) |

**Net:** the parser, the redactor, the schema, the repo, and
the read-only transaction-since endpoint are all already
implemented. The only missing piece is a thin orchestrator
that:

1. instantiates `OandaBroker(environment="practice", ...)`
   with creds from `OANDA_ACCESS_TOKEN_PRACTICE` /
   `OANDA_ACCOUNT_ID_PRACTICE`;
2. discovers a starting transaction id;
3. calls `get_transactions_since` (or the date-range
   endpoint via a raw HTTPS GET against the practice host);
4. funnels payloads through `observed_financing_events(...)`;
5. dumps the parsed events to a fixture-shape JSON file
   under `/tmp/` with `synthetic: false`.

## 2. Existing parser / schema

`ObservedFinancingEvent`
([transactions.py](../../src/forex_bot/domain/transactions.py)):

- frozen Pydantic model, `extra="ignore"`
- fields: `transaction_id`, `account_id_hash` (validator
  refuses any non-64-char-hex value — a raw account id can
  never be persisted by mistake), `instrument` (optional),
  `trade_id` (optional), `units` (optional), `financing`
  (signed `Decimal`: credit `>0`, debit `<0`), `currency`
  (account home), `time` (datetime), `source` (string
  provenance)
- `event_key` property: `sha1("{tx_id}|{instrument}|{trade_id}")`
- `hash_account_id(raw)` → 64-char SHA-256 hex; deterministic

`map_daily_financing(payload, *, source, account_currency)`
([mapping.py:230-285](../../src/forex_bot/broker/mapping.py)):

- accepts an OANDA v20 `DAILY_FINANCING` transaction dict;
- hashes `accountID` at entry (raw id never reaches the
  returned events);
- emits per-trade events when `positionFinancings[].openTradeFinancings`
  is present;
- otherwise emits per-instrument events from
  `positionFinancings[].financing`;
- otherwise emits one account-level event from the
  transaction's `financing` field;
- returns `list[ObservedFinancingEvent]`.

`observed_financing_events(payload, *, source, account_currency)`
([mapping.py:289-313](../../src/forex_bot/broker/mapping.py)):

- general dispatcher: routes `DAILY_FINANCING` to
  `map_daily_financing`, and routes any other transaction
  with non-zero `financing` to a single event (handles e.g.
  `ORDER_FILL` that realized financing on close).

## 3. Existing storage path

`ObservedFinancingEventRepo`
([repositories.py:697+](../../src/forex_bot/data/repositories.py)):

- `insert_many(events) -> int` — idempotent via
  `INSERT OR IGNORE` on `event_key`.
- `count_events() -> int` — total rows.
- `select_for_window(...) -> list[ObservedFinancingEvent]` —
  read with filters.
- Backed by SQLite (`observed_financing_events` table,
  migration v3).

Index includes `(instrument, time DESC)` and
`(account_id_hash, time DESC)` for fast lookup.

The repo is **dormant** in practice: no current loop or
script writes to it. The pilot script in Phase 2 does
**not** write to the repo either (per the plan's "no SQLite
write from the pilot script" rule) — it produces a
fixture-shape JSON file under `/tmp/` that the operator can
later feed to the reconciliation CLI. The repo remains the
intended landing zone for the eventual long-running capture
pipeline; this pilot is a one-shot dry run + capture.

## 4. Transaction-ingestion assumptions

The existing broker class
([oanda.py](../../src/forex_bot/broker/oanda.py)):

- `OandaBroker.__init__(*, environment, account_id, access_token, ...)`
  — accepts environment as `Literal["practice", "live"]`,
  binds the REST host accordingly. The practice host is
  `https://api-fxpractice.oanda.com`.
- `get_account_summary() -> AccountSnapshot` — calls
  `GET /v3/accounts/{id}/summary`. Includes `last_transaction_id`
  which is the discovery cursor for the pilot.
- `get_account_details() -> AccountDetails` — calls
  `GET /v3/accounts/{id}`. Returns trades/positions/orders
  metadata; the underlying payload includes the OANDA `tags`
  field but `AccountDetails` does **not** currently expose
  it. (The pilot script will either parse the raw response
  for `tags` or skip that check and rely on
  `environment="practice"` plus a `--practice-confirm` CLI
  flag — see §6.)
- `get_transactions_since(last_transaction_id) -> list[Transaction]`
  — calls `GET /v3/accounts/{id}/transactions/sinceid?id=...`
  and parses every record through `map_transaction`. **This
  is the primary read-only endpoint the pilot uses.**

`map_transaction(payload)`
([mapping.py](../../src/forex_bot/broker/mapping.py)) keeps
the raw payload on `Transaction.raw`. The pilot script must
re-route through `observed_financing_events(...)` (which uses
the raw OANDA payload, not the `Transaction` wrapper) so the
per-trade `openTradeFinancings` breakdown is preserved.

Concretely: the pilot fetches via `get_transactions_since`,
then iterates the raw payloads (using a small inline call to
the same endpoint, or by re-routing through
`observed_financing_events` after the fact).

## 5. Are account ids hashed at the parser boundary?

**Yes.** `map_daily_financing` calls
`hash_account_id(str(payload.get("accountID", "")))` as its
first action, and the resulting hash is what flows into
every `ObservedFinancingEvent`. The model validator on
`account_id_hash` refuses any non-64-char-hex value, so a
raw account id literally cannot be persisted.

The pilot script must therefore **also not log the raw
account id elsewhere**. The plan's credential-handling rules
(no print, no log, no secondary file) make this explicit.

## 6. Are raw transaction ids safe to store?

**Yes, as broker-internal references** — they are not
credentials. The fixture schema treats them the same as the
synthetic fixtures' `fix-txn-*` ids. The capture dump's
output will include real broker `transaction_id` and
`trade_id` values, **but**:

- the file will not be committed;
- the file will not include any raw account id (only the
  hashed form);
- the file's `provenance` label will be a generic string
  (e.g. `"oanda-practice-2026-05-23"`), not a sentence that
  includes account identity;
- the operator may further redact transaction ids before
  sharing the file outside the local machine.

For committed artifacts (per the plan, none of the pilot's
output is committed), the existing artifact secret scanner
would catch any token-shaped string anyway.

## 7. Gaps and proposed minimal pilot implementation

| gap | proposed handling |
|---|---|
| No date-range transaction helper on `OandaBroker` | Add no new method to the broker; the pilot calls `GET /v3/accounts/{id}/transactions` via a small inline `httpx.get` against the practice host. The call is allowlisted by URL prefix (see §8). |
| `AccountDetails` doesn't expose `tags` | The pilot script does its own `GET /v3/accounts/{id}` and inspects `payload["account"]["tags"]` for `"PRACTICE"` when `--require-practice-tag` is on (default on). If absent, exit 3. |
| `synthetic: false` dump tool | The pilot script is the dump tool. It builds a fixture-shape payload matching the v1 schema (`kind: observed_financing_events`, `schema_version: 1`, `synthetic: false`, `provenance`, `account_currency`, `account_id_hash`, `events`) and writes one JSON file under `/tmp/`. |
| Existing `oanda_readonly_healthcheck.py` exists but is not financing-specific | Pattern reuse only; the pilot does not depend on it. |
| `OANDA_*_PRACTICE` env-var convention | The pilot uses these exact names. `OANDA_*_LIVE` are explicitly **not** consulted. |

The pilot does **not**:

- modify `src/forex_bot/broker/oanda.py`
- modify `src/forex_bot/domain/transactions.py`
- modify `src/forex_bot/broker/mapping.py`
- modify `src/forex_bot/data/repositories.py`
- modify `src/forex_bot/data/migrations.py`
- modify `research/financing/` (the loader already accepts
  `synthetic: false`)
- write to the `observed_financing_events` table (deferred
  to the future long-running capture pipeline)

## 8. Endpoint allowlist (enforced in the pilot script)

The pilot's HTTP wrapper rejects any URL not matching one of:

```
https://api-fxpractice.oanda.com/v3/accounts/{accountID}
https://api-fxpractice.oanda.com/v3/accounts/{accountID}/transactions
https://api-fxpractice.oanda.com/v3/accounts/{accountID}/transactions?from=...&to=...
https://api-fxpractice.oanda.com/v3/accounts/{accountID}/transactions/sinceid?id=...
https://api-fxpractice.oanda.com/v3/accounts/{accountID}/transactions/{transactionID}
```

A test mocks the HTTP client and asserts only these paths
are attempted across every code path in the script.
Anything against `api-fxtrade.oanda.com` (the live REST
host) or `stream-fxtrade.oanda.com` (the live stream host)
is automatically denied.

`OandaBroker.submit_order` already raises `ConfigError` when
called against the live environment; the pilot script does
not import or use `submit_order` at all.

## 9. Safety concerns

| concern | mitigation |
|---|---|
| Pilot accidentally calls live host | `OandaBroker(environment="practice")` hard-codes the REST host to `api-fxpractice.oanda.com`; the URL-prefix allowlist additionally rejects any non-practice URL. Tests pin both. |
| Pilot accidentally submits / modifies / closes an order, trade, or position | The script does not import `submit_order`, `close_trade`, or any mutation helper. A grep rail in the test suite confirms no `submit_order` / `close_trade` / `POST` / `PUT` reference in the script. The HTTP allowlist additionally blocks `POST` / `PUT` URLs. |
| Pilot logs the raw account id or the token | The script reads `OANDA_*_PRACTICE` directly; never echoes the value; produces only `account_id_hash` in any artifact. Tests use tripwire env values and assert absence in stdout/stderr/file contents. |
| Pilot commits raw output | Default `--output` lives under `/tmp/`; the per-phase docs commit only counts and types, not events; the artifact secret scanner is the safety net. |
| Pilot enables a strategy | The script doesn't touch `configs/approved_strategies.yaml`. Freeze checker enforces. |
| Pilot promotes financing to `MODELED` | The output's `provenance` field and any docstring make the `ESTIMATED`-at-most posture explicit. The fixture loader still refuses `MODELED` for `TableRateSource`; the calculator still refuses `MODELED` self-reports. |

## 10. No-secret / no-order guarantees

Belt-and-braces:

1. **No `submit_order` import** — grep rail.
2. **No `close_trade` import** — grep rail.
3. **No `POST` / `PUT` / `DELETE` / `PATCH` URL in script** —
   grep rail.
4. **No live URL in script** — grep rail (`api-fxtrade` /
   `stream-fxtrade` absent).
5. **`OandaBroker(environment="practice")` hard-coded** — no
   parameter accepts `"live"`.
6. **`OANDA_*_LIVE` env vars never read** — only `*_PRACTICE`
   keys appear in the script.
7. **Tripwire test** — tests set `OANDA_*_LIVE` tripwires,
   run the script with mocked HTTP, assert the script never
   read those values and the tripwire values do not appear
   anywhere in stdout/stderr/output.
8. **Mock-only test HTTP** — every Phase 3 test injects a
   mock client; no real network call attempted.

## 11. Cross-links

- Sprint plan:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md)
- Future-capture pilot spec (this sprint executes step 1):
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Fixture schema (the capture output mirrors it with
  `synthetic: false`):
  [`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md)
- Existing observed-event capture design (dormant; this
  sprint reuses its schema + repo seam):
  [`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md)
- Reconciliation CLI (Phase 5 may invoke it):
  [`FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md`](FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md)
- Calculator status:
  [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- Existing per-trade overlay and `FinancingTreatment` gate:
  [`FINANCING_MODEL_DESIGN.md`](FINANCING_MODEL_DESIGN.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
