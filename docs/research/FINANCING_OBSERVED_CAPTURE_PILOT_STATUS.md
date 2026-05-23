# Observed-Capture Pilot — Status

**Date:** 2026-05-23 · **Branch:** `research-financing-observed-capture-pilot-001`
`strategy_evidence: false`

Headline status of the read-only OANDA practice observed-
financing capture pilot. **Script shipped, 27 safety tests
pass, dry-run executed (no creds present → exited 2 as
designed), no broker data fetched, no MODELED financing
produced.**

> No strategy approved. CAMPAIGN_002 remains REJECT. Paper /
> demo / live remain blocked. The script writes
> `strategy_evidence: false` and is structurally incapable of
> emitting `modeled` financing. The live-promotion blocker
> remains.

## 1. Implementation status

[`scripts/capture_oanda_observed_financing_pilot.py`](../../scripts/capture_oanda_observed_financing_pilot.py)
is implemented, tested, and ruff-clean. Layout:

| section | role |
|---|---|
| `PRACTICE_REST_HOST` | hard-coded `https://api-fxpractice.oanda.com`; the script has no way to address the live host |
| `PRACTICE_TOKEN_ENV` / `PRACTICE_ACCOUNT_ENV` | only env-var names consulted; `OANDA_*_LIVE` are explicitly never read |
| `_is_allowed_url(url, account_id)` | URL-prefix allowlist (account root, `/summary`, `/transactions`, `/transactions/sinceid`, numeric-id `/transactions/{id}`); rejects `/transactions/stream` via the digit-only id requirement |
| `_safe_get(client, url, account_id, params)` | defensive HTTP wrapper — rejects any URL containing `fxtrade`, rejects any URL outside the allowlist, surfaces 4xx/5xx with non-credential messages |
| `confirm_practice_account(...)` | `GET /v3/accounts/{id}`; verifies `account.tags` contains `"PRACTICE"` when `--require-practice-tag` is on |
| `get_account_summary_practice(...)` | `GET /v3/accounts/{id}/summary` |
| `get_transactions_since(..., since_transaction_id)` | `GET /v3/accounts/{id}/transactions/sinceid?id=...` |
| `get_transactions_range(..., from_iso, to_iso)` | `GET /v3/accounts/{id}/transactions?from=...&to=...` |
| `parse_daily_financing(...)` | per-trade / per-instrument / account-level breakdown — mirrors `forex_bot.broker.mapping.map_daily_financing` without importing it |
| `parse_observed_financing_events(...)` | dispatcher; ORDER_FILL-with-financing path included for completeness |
| `build_capture_output(...)` | fixture-shape dict (`kind: observed_financing_events`, `schema_version: 1`, `synthetic: False/True`, `provenance`, `account_currency`, `account_id_hash`, sorted `events[]`) |
| `dump_capture(output_dir, payload)` | writes one JSON file: `<output>/observed_financing.json` |
| `run(argv, *, client_factory=None)` / `main(argv)` | top-level entrypoints; `client_factory` is injectable for mock-only tests |

Strict no-go list (enforced by code + tests):

- no `forex_bot` import (grep + subprocess pin)
- no `submit_order` / `close_trade` / `cancel_order` /
  `modify_trade` reference in executable code (grep rail)
- no `POST` / `PUT` / `DELETE` / `PATCH` method in any code
  path
- no `OANDA_*_LIVE` env var read
- no token or raw account id printed, logged, or written
  into any artifact
- no SQLite write
- no commit of raw output

## 2. Was any broker / OANDA data fetched?

**No.** Phase 4 attempted a dry-run only and exited `2`
(`EXIT_MISSING_CREDS`) because practice credentials are not
present in this worktree. No HTTP call was issued. See
[`FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md).

## 3. Were only read-only practice endpoints used?

**Yes (structurally — and would also be enforced in a future
credentialed run).** The script's `_is_allowed_url` allowlist
restricts every HTTP GET to:

- `GET /v3/accounts/{accountID}` (account + practice-tag
  check)
- `GET /v3/accounts/{accountID}/summary` (transaction-cursor
  discovery + dry-run health check)
- `GET /v3/accounts/{accountID}/transactions` (range query)
- `GET /v3/accounts/{accountID}/transactions/sinceid` (since
  query)
- `GET /v3/accounts/{accountID}/transactions/{numericID}`
  (single-id lookup; `/transactions/stream` rejected because
  `stream` is not digit-only)

Everything else — orders, trades, positions, pricing,
configuration, instrument candles, the live REST host, the
live stream host — is denied. Tests
(`test_allows_practice_account_path`,
`test_refuses_live_host_url`,
`test_refuses_mutation_or_unrelated_paths`,
`test_safe_get_refuses_live_host_url`,
`test_safe_get_refuses_non_allowlisted_url`) pin this.

## 4. Were any financing events found?

**Zero.** No capture attempted. Phase 4 documents this as a
valid pilot result for an environment without practice
credentials.

## 5. Was raw output committed?

**No.** Per the sprint plan rule, raw output lives under
`/tmp/` (gitignored by the OS) and is excluded from the repo
unconditionally. Phase 4 wrote nothing (the script exits
before writing on a missing-credentials refusal). A future
credentialed run would also write only to `/tmp/...` by
default.

The artifact secret scanner remains a safety net for any
accidental commit.

## 6. Is `MODELED` financing now available?

**No.** Three layers refuse `MODELED` in the existing
pipeline; one more in the new capture script for
defense-in-depth:

- `TableRateSource(treatment=MODELED)` raises at construction
  (fixture-loader sprint).
- `calculate_run` raises if a rate source self-reports
  `MODELED` (calculator sprint).
- `_build_report` in `scripts/reconcile_financing_fixtures.py`
  raises before writing if `financing_treatment == modeled`
  (reconciliation-tooling sprint).
- The new capture script's `build_capture_output` only ever
  produces an observed-event file (`kind: observed_financing_events`)
  — it does **not** declare a `financing_treatment`, because
  observed events feed downstream rate sources rather than
  being a rate source themselves.

The five-criterion MODELED checklist from
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
§11 is unchanged:

| # | criterion | status |
|---:|---|---|
| 1 | ≥ 60 captured rollovers across the traded universe | **0 — no capture attempted** |
| 2 | per-event reconciliation passes against captured data | blocked (no captured data) |
| 3 | `MODELED` `FinancingModel` implementation | not implemented |
| 4 | engine-PnL integration | not implemented |
| 5 | documented human approval | not granted |

## 7. Is the live blocker lifted?

**No.** `financing_treatment_blocks_approval` in
`src/forex_bot/financing.py` is unchanged. `live`
unconditionally requires `MODELED`; no source produces it.
Paper / demo are also still blocked by the empty
approved-strategy registry.

## 8. Tests

| file | new cases |
|---|---:|
| `tests/research/test_observed_capture_pilot.py` | 27 |

Coverage (full list in the Phase 3 commit message):

- exit-code rails (missing creds, only-live creds present,
  account without PRACTICE tag, dry-run success)
- URL allowlist + denylist (live REST host, live stream
  host, orders, trades, positions, pricing,
  /pricing/stream, configuration, /transactions/stream)
- parser correctness on DAILY_FINANCING (per-trade,
  per-instrument, account-level) and ORDER_FILL with
  non-zero/zero financing
- full capture round-trip writes fixture-shape JSON
  consumable by the existing
  `research/financing/fixtures.load_observed_event_fixture`
- account_id_hash is SHA-256 of raw id; raw id ABSENT from
  output file
- no credential value in stdout/stderr/output
- token reaches the injected factory but is never echoed
- grep + subprocess pins on no `forex_bot` import; no
  mutation-helper references
- no output file written on refusal

**27 tests pass.** Full repo suite: **686** passes (659
prior + 27 new). Ruff clean over `src tests scripts
research/parity_verifier research/walk_forward research/financing`.

## 9. Known limitations

- **No real data captured.** The pilot run did not execute
  (no credentials in this worktree's environment). A future
  credentialed sprint is required to produce real captured
  events; this sprint built only the pipeline.
- **One-shot, not a daemon.** The script is a one-shot
  read; it does not subscribe to the transaction stream,
  does not retry on transient errors, does not persist a
  cursor across runs. The future long-running capture
  pipeline (per
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md))
  will add daemon semantics on top of this primitive.
- **No SQLite write.** The script dumps to a fixture-shape
  JSON; it does not write to the existing
  `observed_financing_events` table. A future productionization
  will route through `ObservedFinancingEventRepo`.
- **Only EUR_USD has a rate fixture for reconciliation.**
  Real captured data on other H4 pairs would require either
  a future rate-fixture-expansion sprint or a captured-rate-
  derived `TableRateSource`.
- **Practice-account `longRate`/`shortRate` are 0 per
  [`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md).**
  A practice-account capture is very likely to find zero
  `DAILY_FINANCING` events; that is also a valid pilot
  result but is not the empirical input a real model needs.
  A future funded-account pilot (with its own separate
  human authorization) would be required to collect
  reconcilable data.

## 10. Safety state (unchanged by this sprint)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.** `paper-loop` and
  `demo-loop` refuse; no `live-loop` exists.
- **No bespoke-engine edit.**
- **No `src/forex_bot/financing.py` edit.**
- **No `src/forex_bot/broker/oanda.py` edit.**
- **No `ObservedFinancingEventRepo` write.**
- **No `research/financing/` edit.**
- **No OANDA call performed.** Dry-run refused before any
  HTTP request.
- **No `.env` read.** Script reads `OANDA_*_PRACTICE` env
  vars only; `.env` is absent.
- **No credential printed.**
- **No `*.sqlite3`, candle CSV, raw account export, or
  bulky output committed.**
- **No new external dependency.** The script uses `httpx`
  (already a project dependency).
- **Import isolation grep + subprocess pinned.**
- **No `MODELED` financing reachable** anywhere in the
  pipeline.
- **No QuantConnect / LEAN.**

## 11. EVIDENCE_MANIFEST.json

The manifest tracks **campaigns**; this sprint adds no
campaign, so `docs/research/EVIDENCE_MANIFEST.json` requires
no entry. Same posture as the three prior financing sprints.
The archive validator continues to PASS.

## 12. Cross-links

- Sprint plan:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md)
- Existing-path audit:
  [`FINANCING_OBSERVED_CAPTURE_EXISTING_PATH_AUDIT.md`](FINANCING_OBSERVED_CAPTURE_EXISTING_PATH_AUDIT.md)
- Pilot run (Phase 4 — not run):
  [`FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md)
- Reconciliation (Phase 5 — blocked):
  [`FINANCING_OBSERVED_CAPTURE_RECONCILIATION.md`](FINANCING_OBSERVED_CAPTURE_RECONCILIATION.md)
- Future-capture pilot spec (this sprint executes its first
  step):
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Sister sprints:
  [`RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md`](RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md),
  [`RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md`](RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md),
  [`RESEARCH_FINANCING_MODEL_001_SUMMARY.md`](RESEARCH_FINANCING_MODEL_001_SUMMARY.md)
- Calculator protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
