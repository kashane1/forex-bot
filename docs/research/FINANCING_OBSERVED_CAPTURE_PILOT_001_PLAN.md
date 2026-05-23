# Financing Observed-Capture Pilot Sprint 001 — Plan

**Date:** 2026-05-23 · **Branch:** `research-financing-observed-capture-pilot-001`
**Base commit:** `1747cef` (HEAD of `research-financing-reconciliation-tooling-001`)
`strategy_evidence: false`

The first sprint with **explicit human authorization** for
read-only OANDA practice transaction reads. This sprint:

- builds a small, allowlisted, redaction-mandatory pilot
  script;
- documents what it would do against the practice account;
- attempts a tiny run **only** if practice credentials are
  available and explicitly tagged practice;
- never submits or modifies any order, trade, or position.

> **Human authorization granted (this sprint only):** read-only
> OANDA practice transaction history access. Authorization does
> **not** cover orders, trades, positions, pricing, account
> mutation, or live-account access.
>
> **No strategy is approved. CAMPAIGN_002 remains REJECT.**
> `configs/approved_strategies.yaml` stays `approved: []`. Paper
> / demo / live remain blocked. **This sprint cannot, and will
> not, approve a strategy or make financing `MODELED`.** One
> pilot capture is never enough for `MODELED` — the
> five-criterion checklist in
> [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
> §11 still applies.

## 1. Purpose

To execute the **first** of the five MODELED criteria for the
financing model:

1. **Forward-capture observed financing.** ← this sprint
2. Per-event reconciliation passes against captured data.
3. `MODELED` `FinancingModel` implementation in
   `src/forex_bot/financing.py`.
4. Engine-PnL integration.
5. Documented human approval.

Specifically:

- Add a small read-only script under `scripts/` that:
  - reads from OANDA's practice `transactions/sinceid` (or
    `transactions` range) endpoint;
  - parses `DAILY_FINANCING` and (secondarily) any
    transaction carrying a non-zero `financing` field;
  - hashes the account id at the boundary
    (`hash_account_id`);
  - writes a redacted, fixture-shape JSON output under
    `/tmp/` (gitignored);
  - never writes to `configs/`, `backtests/`, `research/`, or
    `docs/`;
  - exits cleanly with a documented exit-code matrix.
- Add safety tests that use **mocked** HTTP responses only —
  no real network call in CI.
- Execute the script's dry-run (or one-off verify) and, if
  credentials are present and tagged practice, a narrow
  read-only window.
- Document the captured count + redacted summary; commit only
  the docs, never the raw output.

## 2. Non-goals

- **Not a strategy.** No backtest, no campaign, no signal
  logic, no order. The script does not import any order /
  trade / position mutation code path.
- **Not `MODELED` financing.** One pilot run, even a clean
  one, is one of five criteria. The script writes
  `strategy_evidence: false` and never claims `MODELED`.
- **Not a CAMPAIGN_002 revival.** No CAMPAIGN_002 artifact
  loaded.
- **Not a paper / demo / live enabler.** The script does not
  edit `configs/approved_strategies.yaml`.
- **Not a long-running data pipeline.** This is a one-shot
  pilot, not a daemon. The follow-on capture sprint will
  productionize the path with scheduled fetches and retries.
- **Not a real `FinancingModel` implementation.**
  `FutureOandaObservedFinancingModel` in
  `src/forex_bot/financing.py` remains a placeholder whose
  `__init__` raises.
- **Not bulky-output writer.** One small JSON output per run;
  no SQLite write from the pilot script; no candle dump.

## 3. Human authorization scope

| permission | granted |
|---|:--:|
| read OANDA **practice** transaction history (sinceid + by-id) | ✓ |
| read OANDA **practice** account-level transaction range | ✓ |
| any **live**-environment call | ✗ |
| order endpoints (`/orders`) | ✗ |
| trade modify / close (`/trades/.../orders` / `/trades/.../close`) | ✗ |
| position close (`/positions/.../close`) | ✗ |
| `pricing` (read or stream) | ✗ |
| account configuration mutation (`PATCH /accounts/.../configuration`) | ✗ |
| writing captured data to `configs/`, `backtests/`, `research/`, `docs/` | ✗ |
| committing raw account-identifying data | ✗ |
| printing or logging credential values | ✗ |

The script's allowlist enforces all of the above
structurally; tests pin it.

## 4. Endpoint allowlist

The pilot script may call only these endpoints (and only via
the existing `OandaBroker.get_transactions_since` helper, or a
minimal in-script `httpx.get` for `/transactions` if a date
range is needed):

| endpoint | use |
|---|---|
| `GET /v3/accounts/{accountID}` | once at startup to verify auth + confirm the account is practice (parses `tags` or uses the `OANDA_ENV=practice` tag the operator sets) |
| `GET /v3/accounts/{accountID}/transactions` | range query (`from` / `to`) to discover the last-transaction-id cursor when no cursor is supplied |
| `GET /v3/accounts/{accountID}/transactions/sinceid` | the existing
  `OandaBroker.get_transactions_since` helper; primary capture path |
| `GET /v3/accounts/{accountID}/transactions/{transactionID}` | optional one-off lookup if a single id needs to be re-fetched (not used in v1) |

## 5. Endpoint denylist

The script structurally cannot reach:

- `POST /v3/accounts/.../orders`
- `PUT /v3/accounts/.../orders/...`
- `PUT /v3/accounts/.../trades/.../close`
- `PUT /v3/accounts/.../trades/.../orders`
- `PUT /v3/accounts/.../positions/.../close`
- `PATCH /v3/accounts/.../configuration`
- `GET /v3/accounts/.../pricing` / `pricing/stream`
- `GET /v3/instruments/.../candles`
- the OANDA **live** REST or stream hosts
  (`api-fxtrade.oanda.com`, `stream-fxtrade.oanda.com`)

Enforcement:

- The script holds an explicit allowlist of URL paths and
  rejects anything else **inside the HTTP call wrapper**.
- A test mocks `httpx.Client.request` and asserts the only
  paths invoked are members of the allowlist.
- A test asserts the base URL is the practice REST host, not
  the live host.

## 6. Credential handling

- Practice token + account id are read from environment
  variables: `OANDA_ACCESS_TOKEN_PRACTICE` and
  `OANDA_ACCOUNT_ID_PRACTICE` (matching the convention in
  `configs/practice.yaml`).
- If either is missing, the script exits with a clear message
  (e.g. `[capture] missing practice credentials — refusing`)
  and exit code `2`. No credential value is read or printed.
- If the operator has only `OANDA_ACCESS_TOKEN_LIVE` /
  `OANDA_ACCOUNT_ID_LIVE` set, the script does **not** fall
  back; it refuses with the same message. Live creds are
  ignored entirely.
- The script never logs the token or the raw account id.
- The script never writes `.env` or any other file with
  credential content.
- A `--require-practice-tag` flag (default on) calls
  `GET /v3/accounts/{accountID}` and inspects the response's
  `tags` for a `"PRACTICE"` token before any further calls.
  If absent, the script aborts with exit code `3`.
- The artifact scanner already enforces no credential string
  in committed artifacts.

## 7. Redaction rules

- The raw account id **never** reaches a written artifact.
  Every event uses `account_id_hash =
  hash_account_id(raw_account_id)` (SHA-256 hex).
- `transaction_id` and `trade_id` are persisted as-is (they
  are broker-internal references, not credentials) but are
  not logged alongside the token or account id.
- The pilot output uses the **fixture schema**
  ([`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md))
  with `synthetic: false` and a `provenance` label like
  `"oanda-practice-<YYYY-MM-DD>"`. The loader already accepts
  `synthetic: false`.
- The output `provenance` line and any console message are
  scanned by the secret scanner at commit time; the operator
  must keep the provenance label generic.

## 8. Expected local outputs

Per run, the script writes one JSON file under
`<output>/observed_financing.json`:

- `kind`: `"observed_financing_events"`
- `schema_version`: `1`
- `synthetic`: `false` (real capture) or `true` (mocked test
  capture)
- `provenance`: a generic label (no account id, no token)
- `account_currency`: from
  `GET /v3/accounts/{accountID}` response (`currency` field)
- `account_id_hash`: SHA-256 of the raw account id (never
  raw)
- `events[]`: rows mirroring `ObservedFinancingEvent`; the
  parser is the existing `broker.mapping.observed_financing_events`
  helper (already in repo)

Default output path: `/tmp/financing_observed_capture/`
(gitignored by the OS). The operator passes `--output` to
override. **No raw output is committed** to the repo under
any circumstance.

## 9. Planned phases

| phase | output | commit |
|---|---|---|
| 0 | This plan doc + baseline | docs-only |
| 1 | `FINANCING_OBSERVED_CAPTURE_EXISTING_PATH_AUDIT.md` | docs-only |
| 2 | `scripts/capture_oanda_observed_financing_pilot.py` | code |
| 3 | `tests/research/test_observed_capture_pilot.py` (mock-only) | tests |
| 4 | `FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md` (run summary or "not run" reason) | docs |
| 5 | `FINANCING_OBSERVED_CAPTURE_RECONCILIATION.md` (or "blocked" reason) | docs |
| 6 | `FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md` + `EVIDENCE_INDEX.md` update | docs |
| 7 | `RESEARCH_FINANCING_OBSERVED_CAPTURE_PILOT_001_SUMMARY.md` + final validation | docs |

## 10. Safety invariants

1. `configs/approved_strategies.yaml` stays `approved: []`.
2. CAMPAIGN_002 remains REJECT.
3. Paper / demo loops keep refusing; no `live-loop` exists.
4. No QC / LEAN command.
5. **No live OANDA call.** Practice base URL only
   (`https://api-fxpractice.oanda.com`). Live host is on the
   denylist.
6. **No order/trade/position mutation call.** Allowlist
   enforces.
7. No `.env` read or write. The script reads named env vars
   directly; the operator is responsible for sourcing them.
8. **No credential value printed or logged.** Tests pin this
   via tripwire env values and stdout/stderr capture.
9. **No raw output committed.** Outputs live under `/tmp/`;
   the per-run docs only contain redacted counts.
10. The bespoke engine, `src/forex_bot/financing.py`, the
    observed-event repo, and the fixture loader are **not
    modified**.
11. `research/financing/` is **not modified**.
12. No new external dependency. The script uses `argparse` +
    `json` + the existing `OandaBroker` (or a minimal
    in-script httpx call against the allowlisted URLs).
13. Every artifact written carries `strategy_evidence: false`,
    `financing_treatment` ∈ `{estimated, unmodeled}` — never
    `modeled`. The pilot is a **capture** step, not a
    treatment claim.

## 11. Test surface

- All Phase 3 tests use **mocked** HTTP responses. No
  network call is attempted in any test.
- Tests cover:
  - refuses missing creds (exit `2`); no credential value
    printed
  - refuses live env / live host (exit `3`)
  - refuses an account whose `tags` lack `PRACTICE` (when
    `--require-practice-tag` is on)
  - redacts account id in every output row
  - writes fixture-shape JSON consumable by the existing
    loader
  - exit codes follow a stable matrix
  - the script does not call any denylisted URL path (mock
    HTTP spy)
  - the script does not import any order-mutation helper
    (grep rail)
  - test outputs use `synthetic: true` (mock data, not real
    capture); only the production run sets `false`

## 12. Why MODELED remains unavailable after this sprint

Even a successful pilot capture run fulfils **only**
criterion 1 of the 5 in
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
§11:

| # | criterion | this sprint? |
|---:|---|:--:|
| 1 | ≥ 60 captured rollovers across the traded universe | partial — pilot can confirm the pipeline; ≥ 60 requires forward time |
| 2 | per-event reconciliation passes against captured data | partial — Phase 5 attempts only if data is captured |
| 3 | `MODELED` `FinancingModel` implementation in `src/forex_bot/financing.py` | **no** |
| 4 | engine-PnL integration | **no** |
| 5 | documented human approval | **no** |

The script and every output it writes therefore continue to
declare `financing_treatment ∈ {estimated, unmodeled}` and
`financing_is_live_blocker: true`.

## 13. Cross-links

- Future-capture pilot spec (this sprint executes the first
  step of it):
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Existing observed-event capture design (dormant; this
  sprint reuses its schema + repo seam):
  [`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md)
- Reconciliation CLI (Phase 5 may invoke it):
  [`FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md`](FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md)
- Fixture schema (capture output mirrors it with
  `synthetic: false`):
  [`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md)
- Calculator status:
  [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- Existing per-trade overlay and `FinancingTreatment` gate:
  [`FINANCING_MODEL_DESIGN.md`](FINANCING_MODEL_DESIGN.md)
- Strategy approval process:
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
