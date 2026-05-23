# Financing Observed-Capture Pilot — Specification

**Date:** 2026-05-23 · **Branch:** `research-financing-rate-source-fixtures-001`
Phase 5 · `strategy_evidence: false`

A **future-facing specification** for a forward-looking
`DAILY_FINANCING` observed-capture pilot. **This sprint does not
implement it.** No OANDA call is made, no broker code is
written, no order capability is enabled. The spec exists so the
follow-on sprint that *does* implement capture has a narrow,
pre-reviewed scope to operate within.

> **Nothing here is authorized.** Each authorization requirement
> below requires an explicit human decision before any code is
> written. Until those decisions exist, this document is a
> reference, not a license. CAMPAIGN_002 remains REJECT. No
> strategy is approved. Paper / demo / live remain blocked.
> `MODELED` financing remains unavailable.

## 1. Purpose

To collect a forward-looking dataset of **actual OANDA
`DAILY_FINANCING` transactions** against a long-lived practice
or funded account, *without* submitting any orders during the
capture window. The dataset is the empirical input a future
`MODELED` financing model would consume; it cannot retroactively
fix 2020–2026.

Specifically the pilot must:

- Subscribe to (or poll) the OANDA v20 transaction stream in a
  **read-only** mode.
- Parse `DAILY_FINANCING` transactions through the existing
  [`broker/mapping.map_daily_financing`](../../src/forex_bot/broker/mapping.py)
  function (already in the repo; no rewrite).
- Hash the account id at the boundary
  ([`hash_account_id`](../../src/forex_bot/domain/transactions.py)),
  never persist the raw id.
- Write the parsed events to the existing
  `observed_financing_events` table via
  [`ObservedFinancingEventRepo`](../../src/forex_bot/data/repositories.py)
  (already in the repo; no schema change).
- Optionally dump captured rows to a fixture-shaped JSON file
  for offline research, using the format defined by
  [`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md).
  This dump path is what makes the captured data
  interchangeable with this sprint's synthetic fixtures.

It must not:

- Submit, modify, cancel, or query any **order**.
- Modify positions.
- Change a campaign verdict.
- Mark financing as `MODELED`.
- Lift the live-promotion blocker.

## 2. Required human authorization

Before the implementation sprint may begin:

1. **Live-account-or-practice decision.** A funded account
   produces real financing rates; a practice account
   typically reports zero. The pilot's value scales with the
   chosen environment. The choice is a human decision, not an
   agent decision.
2. **Read-only credential issued.** OANDA accounts already
   expose only read access through the standard token in
   v0.x; the pilot must operate with the existing read-only
   token. No new permission scopes are requested.
3. **Documented start/end window.** A human-approved start
   date and minimum-duration commitment (recommended ≥ 60
   rollovers across the traded universe per
   `FINANCING_MODEL_DESIGN.md` §7).
4. **Documented absence of order activity** during the
   capture window. The pilot does **not** open positions;
   captured financing comes from positions opened by a
   separate human-driven workflow (or from a long-lived test
   position whose existence is also explicitly approved).
5. **Confirmation that the freeze remains in effect.** The
   capture sprint must not accidentally bundle in a strategy
   approval or a `live-loop` enablement. The pilot is
   data-collection only.

If any of (1)–(5) is missing, the pilot does not start.

## 3. Exact read-only scope

OANDA v20 endpoints the pilot may use:

| endpoint | use | notes |
|---|---|---|
| `GET /v3/accounts/{accountID}/transactions/stream` | subscribe to transaction events | filter to `DAILY_FINANCING` and `RESETTABLE_PL`; ignore everything else |
| `GET /v3/accounts/{accountID}/transactions/sinceid` | catch-up / resume after restart | strictly read; the response's `lastTransactionID` updates a cursor stored locally |
| `GET /v3/accounts/{accountID}/transactions/{transactionID}` | optional one-off transaction fetch for reconciliation | only if a streamed event was dropped mid-pipeline |

OANDA v20 endpoints the pilot **must not** use:

- Any `POST` or `PUT` endpoint.
- `/orders`, `/trades`, `/positions` (read or write — pilot is
  transaction-stream only).
- `/instruments/{instrument}/candles` (out of scope; candle data
  is fetched by other pipelines).
- `/pricing` (no live pricing read).
- `/accounts/{accountID}/instruments` (the per-account
  instrument metadata endpoint; not needed by the pilot, and
  reads the practice `longRate`/`shortRate` which are 0).

A test rail in the capture sprint must verify no other
endpoint is touched (e.g. by mocking the HTTP client and
asserting the call set).

## 4. Expected OANDA transaction types

From the existing parser
([`src/forex_bot/broker/mapping.py:230-313`](../../src/forex_bot/broker/mapping.py))
and the observed-event capture design doc
([`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md)):

- **`DAILY_FINANCING`** — primary signal. Per-day rollover
  charge / credit. Broken down by `positionFinancings[].instrument`
  and optionally `openTradeFinancings[].tradeID`. The parser
  emits one `ObservedFinancingEvent` per breakdown row, or one
  account-level event if no breakdown is present.
- **Any other transaction with a non-zero `financing` field**
  (e.g. `ORDER_FILL` that realized financing on close) — the
  parser already handles this via `observed_financing_events`.
  These are secondary signal but may be useful for
  reconciliation against `DAILY_FINANCING` totals.
- **`RESETTABLE_PL`** — captured only for context; not a
  financing event itself.

All other transaction types (`MARKET_ORDER`,
`MARKET_ORDER_REJECT`, `TRADE_CLOSE`, etc.) are ignored. The
pilot does not need or consume order-life-cycle transactions
because the pilot does not submit orders.

## 5. What must never be queried or mutated

- **Orders.** No `POST /orders`, no `PUT
  /orders/{orderSpecifier}`, no `DELETE /orders`. The capture
  pipeline does not touch the order endpoint at all.
- **Trades.** No `PUT /trades/{tradeSpecifier}/orders`
  (modify-stop-loss / take-profit), no `PUT
  /trades/{tradeSpecifier}/close`.
- **Positions.** No `PUT /positions/{instrument}/close`.
- **Configuration.** No `PATCH /accounts/{accountID}/configuration`.
- **The `configs/approved_strategies.yaml`.** The pilot does
  not edit it. The capture sprint's CI must include the
  existing freeze checker.
- **The bespoke backtest engine.** No PnL change. No engine
  call.
- **The `src/forex_bot/financing.py` `FinancingTreatment`
  ladder.** Captured data does not by itself promote
  treatment from `ESTIMATED` to `MODELED`.

## 6. Credential handling rules

- OANDA credentials live in `.env`; the freeze's existing
  `scripts/scan_artifacts_for_secrets.py` continues to enforce
  no-credential-in-artifact. The capture sprint adds no new
  credential surfaces.
- `.env` is **not** committed.
- Credentials are **never** printed, logged, or written to any
  artifact under `docs/`, `backtests/`, `research/`, `configs/`,
  or `scripts/`.
- A read-only token is used — even if the account separately
  has write access, the pilot's code path must never call a
  write endpoint (enforced by §3's allowlist).
- Token validity is checked **once** at pipeline start via
  `GET /v3/accounts/{accountID}` (the cheapest read). The
  response is not persisted.

## 7. Redaction rules

- The account id is **never** stored. The existing
  `hash_account_id` redactor produces a SHA-256 hex digest at
  the parser boundary. The model validator
  (`ObservedFinancingEvent.account_id_hash`) refuses any
  non-digest input — a raw id cannot be persisted by mistake.
- Trade ids and transaction ids that come from a real account
  *are* persisted (they are not credentials — they are
  broker-internal references) but are **not** logged to
  external systems and **never** printed alongside the
  account id or token.
- If a captured-event dump is shared (e.g. for offline
  reconciliation), every committed artifact still passes the
  archive validator's credential scan.

## 8. Local storage rules

- All captured events go to
  [`ObservedFinancingEventRepo`](../../src/forex_bot/data/repositories.py)
  → the `observed_financing_events` table (already in
  migration v3). No new schema is required.
- The SQLite database file (`*.sqlite3`) is **not committed**.
  The freeze's existing artifact policy (see plan §16 of this
  sprint) covers this.
- Periodic dumps to fixture-shape JSON files **may** be
  committed under `research/financing/fixtures/` — provided
  every committed dump satisfies the same fixture rules as
  this sprint's synthetic fixtures (file size < 10 KB, no real
  account id, `synthetic: false` is the only field that
  differs from a synthetic fixture). Larger captured datasets
  should be referenced from a status doc but stored outside
  the repo (cf. the candle CSV pattern documented elsewhere).
- The capture pipeline's state (last-transaction-id cursor,
  retry counters, runtime metadata) lives in the same SQLite
  database or in a tiny JSON sidecar; neither is committed.

## 9. Fixture-normalization path

The forward path that connects this pilot to the rest of
`research/financing/`:

1. **Capture step.** Read-only transaction stream → `map_daily_financing`
   → `ObservedFinancingEventRepo.write(...)`. Events accumulate
   in the database.
2. **Hashing step.** `hash_account_id` at the parser boundary.
   The raw account id never reaches the table.
3. **Export step (optional).** A dump utility reads the table
   for a chosen window and writes JSON files that satisfy
   [`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md):
   - `kind`: `"observed_financing_events"` (unchanged from
     synthetic fixtures)
   - `schema_version`: `1` (unchanged)
   - `synthetic`: `false` ← the only field that differs from
     this sprint's fixtures
   - `provenance`: source label like `"oanda-practice-2026-05-19"`
   - `account_currency`, `account_id_hash`, `events`: as
     captured
4. **Loader step.** `research/financing/fixtures.load_observed_event_fixture(path)`
   already accepts both synthetic and non-synthetic files. No
   loader change is needed. The same import-isolation rail
   applies.
5. **Calculator step.** A campaign code path takes captured
   events + a `TableRateSource` (built from observed-event
   aggregation) → `calculate_run` → diagnostic report.

The pilot sprint's *only* code change is the capture loop
(item 1) and optionally a small dump CLI (item 3). The schema,
loader, calculator, and reporting are already done.

## 10. Reconciliation steps

For each window of captured events, the pilot's analysis must
produce:

1. **Per-pair, per-direction empirical bp/day.** Aggregate
   captured `financing` per (instrument, side) over the
   window; divide by total holding-day-units. Compare to the
   conservative bp/day table in
   `src/forex_bot/financing.CONSERVATIVE_BP_PER_DAY`. Document
   the per-pair ratio (empirical / conservative); a ratio < 1
   means the existing overlay is appropriately conservative.
2. **Wednesday-multiplier verification.** Filter captured rows
   by `time.weekday() == 2`; assert the per-pair mean is ≈ 3 ×
   the per-pair non-Wednesday mean. Significant deviation
   indicates either a broker behaviour the protocol's
   triple-swap model misses, or sample-size artefacts.
3. **Weekend-skip verification.** Assert zero captured rows
   on Saturday and Sunday (the broker emits no
   `DAILY_FINANCING` on those days). A non-zero count is a
   pipeline bug, not a financing fact.
4. **Per-event reconciliation against the calculator.** For
   each captured event, run `calculate_position` with the
   matching `PositionInterval` and a fixture-shaped rate
   source built from the captured rows. Assert per-event
   `cashflow_home == observed.financing` within a tight
   tolerance (e.g. ≤ $0.01 per event for 10k-unit positions).
   This is the test that establishes whether the calculator's
   conventions reproduce real broker behaviour.

Step (4) is the gating condition for any future move toward
`MODELED` financing. The current sprint already provides the
reconciliation pattern (see
`tests/research/test_financing_fixtures.py::test_reconciliation_skips_missing_date_matches_observed_per_row`).

## 11. Acceptance criteria for calling future data `MODELED`

The `FinancingTreatment` ladder is owned by
[`src/forex_bot/financing.py`](../../src/forex_bot/financing.py)
and is **not** changed by the capture pilot. A future
`MODELED` declaration requires **all** of:

1. **≥ 60 captured rollovers** across the traded universe (per
   `FINANCING_MODEL_DESIGN.md` §7), in a continuous window with
   no significant gaps.
2. **Per-event reconciliation passes** at a tight tolerance
   (recommended ≤ $0.01 per event for 10k-unit positions; the
   exact tolerance is set in the capture sprint's pre-commit).
3. **A `MODELED` `FinancingModel` implementation** in
   `src/forex_bot/financing.py` — concretely, a successor to
   `FutureOandaObservedFinancingModel` whose `__init__` no
   longer raises. The implementation must:
   - declare `treatment = FinancingTreatment.MODELED`,
   - be reconcilable against captured data within the
     tolerance,
   - have its own test suite under `tests/unit/`,
   - not silently change historical backtest reproducibility
     (introduce it as an opt-in code path with a clear flag).
4. **Engine-PnL integration** as an opt-in path in
   `src/forex_bot/backtesting/engine.py` (a separate sprint
   from the capture pilot — capture, then implement, then
   integrate).
5. **A documented human approval** per the strategy approval
   process, attached to the campaign whose verdict depends on
   `MODELED` financing.

None of (1)–(5) happens in the current sprint. None of (1)–(5)
will happen in the capture pilot sprint alone — the pilot
delivers (1) and (2) only.

## 12. Why `MODELED` remains blocked even after this sprint

After the current `research-financing-rate-source-fixtures-001`
sprint:

- We have a **schema** and a **loader** that can ingest
  observed events.
- We have a **calculator** that can compute predictions from a
  rate source.
- We have a **reconciliation pattern** (test
  `test_reconciliation_skips_missing_date_matches_observed_per_row`)
  that demonstrates per-event equality at the rel=1e-9 level
  on synthetic data.

We do **not** have:

- Real captured events. (None exist; capture has not started.)
- A `MODELED` `FinancingModel` implementation. (The
  placeholder still refuses to instantiate.)
- Engine-PnL integration. (The bespoke engine still treats
  financing as `UNMODELED` in PnL terms.)
- A human approval. (The freeze stands.)

Per the `financing_treatment_blocks_approval` rule in
`src/forex_bot/financing.py`, `live` mode unconditionally
requires `MODELED`. `MODELED` is unreachable without each of
the four items above. Therefore the live-promotion blocker
remains, and **paper / demo / live remain blocked**
regardless of this sprint's outcome.

## 13. Cross-links

- This sprint's plan:
  [`FINANCING_RATE_SOURCE_FIXTURES_001_PLAN.md`](FINANCING_RATE_SOURCE_FIXTURES_001_PLAN.md)
- Fixture schema:
  [`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md)
- Existing capture design (dormant, this sprint does not
  modify):
  [`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md)
- Existing parser:
  [`src/forex_bot/broker/mapping.py`](../../src/forex_bot/broker/mapping.py)
- Existing observed-event schema:
  [`src/forex_bot/domain/transactions.py`](../../src/forex_bot/domain/transactions.py)
- Existing repository:
  [`src/forex_bot/data/repositories.py`](../../src/forex_bot/data/repositories.py)
- Calculator protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Existing per-trade overlay and `FinancingTreatment` gate:
  [`FINANCING_MODEL_DESIGN.md`](FINANCING_MODEL_DESIGN.md)
- Approval process (authoritative for human approval):
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- Research-freeze decision memo:
  [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
