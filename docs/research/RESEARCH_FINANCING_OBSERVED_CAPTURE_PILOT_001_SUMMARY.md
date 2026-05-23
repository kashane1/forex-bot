# Financing Observed-Capture Pilot Sprint 001 — Summary & Handoff

**Date:** 2026-05-23 · **Branch:** `research-financing-observed-capture-pilot-001`
`strategy_evidence: false`

Sprint outcome and handoff for the first sprint with explicit
human authorization for read-only OANDA practice transaction
reads.

**Script shipped, 27 safety tests pass, dry-run attempted (no
credentials present → exited 2 as designed), no broker data
fetched, no MODELED financing produced.** The capture pipeline
+ safety rails are now in place; a future credentialed sprint
can execute the actual capture without designing schema or
plumbing under pressure.

> **No strategy is approved. CAMPAIGN_002 remains REJECT.**
> Paper / demo / live remain blocked. No QC / LEAN. **No OANDA
> data fetched.** No orders, trades, or positions touched.
> `configs/approved_strategies.yaml` stays `approved: []`.
> `MODELED` financing remains unreachable through every layer
> of the pipeline, with belt-and-braces defense in depth
> across the loader, calculator, reconciliation CLI, and now
> the capture script.

## 1. Headline outcome

`scripts/capture_oanda_observed_financing_pilot.py` + 5 docs +
1 test module are shipped:

- 1 new pilot script (~620 lines): allowlisted HTTP wrapper,
  practice-only host, hashed account id, fixture-shape JSON
  output.
- 27 new tests in `tests/research/test_observed_capture_pilot.py`,
  all using mocked HTTP — zero network call in CI.
- 0 changes to `src/forex_bot/`, `research/financing/`,
  `configs/`, `backtests/`, or any other production path.
- Full repo suite: **686 passes** (659 prior + 27 new).
- Ruff: clean over `src tests scripts
  research/parity_verifier research/walk_forward
  research/financing`.
- Archive validator, freeze checker, secret scan all PASS.
- Paper-loop and demo-loop still refuse; no live-loop command
  exists.

## 2. Commit log (this sprint)

| commit | phase | scope |
|---|---|---|
| `ff9f690` | 0 | plan doc |
| `4a605ff` | 1 | existing-path audit |
| `a05df56` | 2 | capture script |
| `1111520` | 3 | 27 safety tests |
| `8262a95` | 4 | pilot run record (not run — no creds) |
| `b7c66f7` | 5 | reconciliation (blocked — no captured events) |
| `72c95c0` | 6 | status doc + EVIDENCE_INDEX update |
| _this_ | 7 | this summary + EVIDENCE_INDEX summary-link + final validation |

## 3. Files changed

- **Docs (new):**
  - `docs/research/FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md`
  - `docs/research/FINANCING_OBSERVED_CAPTURE_EXISTING_PATH_AUDIT.md`
  - `docs/research/FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md`
  - `docs/research/FINANCING_OBSERVED_CAPTURE_RECONCILIATION.md`
  - `docs/research/FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`
  - `docs/research/RESEARCH_FINANCING_OBSERVED_CAPTURE_PILOT_001_SUMMARY.md`
- **Docs (edited):**
  - `docs/research/EVIDENCE_INDEX.md` — adds an observed-
    financing capture pilot subsection.
- **Code (new):**
  - `scripts/capture_oanda_observed_financing_pilot.py`
- **Tests (new):**
  - `tests/research/test_observed_capture_pilot.py`

No file in `src/forex_bot/`, `research/financing/`,
`configs/`, `backtests/`, or `research/walk_forward/` was
modified. No `*.sqlite3` was created or committed. No `.env`
was read. **No OANDA call** was made.

## 4. Validation commands run

Final pass (Phase 7), all green:

- `python -m pytest -q` — **686 passed in 2.43 s** (659
  prior + 27 new)
- `ruff check src tests scripts research/parity_verifier
  research/walk_forward research/financing` — **All checks
  passed!**
- `python scripts/validate_research_archive.py` — **ALL
  CHECKS PASSED**
- `python scripts/check_research_freeze.py` — **ALL CHECKS
  PASSED**
- `python scripts/scan_artifacts_for_secrets.py` —
  **PASSED** (1,975 files; no credentials)
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml`
  — refuses
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml`
  — refuses
- `python -m forex_bot.cli --help` — no `live-loop` command
  listed

## 5. Confirmation no strategy is approved
`configs/approved_strategies.yaml` verified `approved: []`.
Freeze checker passes.

## 6. Confirmation CAMPAIGN_002 remains REJECT
No CAMPAIGN_002 artifact, config, or report was touched.
Archive validator's `verdicts_non_approval` and
`report_verdict_tokens` checks pass.

## 7. Confirmation paper/demo/live remain blocked
- `paper-loop` refuses (`['trend_following']` not approved).
- `demo-loop` refuses (same).
- `python -m forex_bot.cli --help` does not list `live-loop`.

## 8. Confirmation practice-only read scope

**Yes (structurally, would also be enforced at runtime).** The
script's `_is_allowed_url` allowlist restricts every HTTP GET
to four practice-account read endpoints; the live REST host
(`api-fxtrade.oanda.com`) and live stream host
(`stream-fxtrade.oanda.com`) are denied via two independent
checks:

1. **Substring deny:** `_safe_get` rejects any URL containing
   `fxtrade`.
2. **URL-prefix allowlist:** `_is_allowed_url` only matches
   `https://api-fxpractice.oanda.com/v3/accounts/{accountID}{path}`
   where `{path}` is one of the read-only paths.

Additionally:

- The script hard-codes `PRACTICE_REST_HOST =
  "https://api-fxpractice.oanda.com"` — there is no parameter
  or flag that switches it.
- The script reads only `OANDA_ACCESS_TOKEN_PRACTICE` /
  `OANDA_ACCOUNT_ID_PRACTICE`; `OANDA_*_LIVE` are explicitly
  never consulted (test pinned).
- `--require-practice-tag` (default on) calls
  `GET /v3/accounts/{id}` and refuses (exit 3) if `tags` does
  not include `"PRACTICE"`.
- 4 separate tests pin each layer of the allowlist /
  denylist.

## 9. Was any OANDA data fetched?

**No.** Phase 4 attempted only a dry-run, which exited with
code `2` (`EXIT_MISSING_CREDS`) before any HTTP request was
made — no practice credentials are visible in this worktree
(`OANDA_*_PRACTICE` env vars are UNSET; `.env` is ABSENT).
Zero OANDA calls, zero `httpx.Client.get` invocations against
any real host.

## 10. Were any orders/trades/positions mutated?

**No.** The script:

- has zero `POST` / `PUT` / `DELETE` / `PATCH` references in
  executable code;
- has zero `submit_order` / `close_trade` / `cancel_order` /
  `modify_trade` references (grep rail);
- does not import `forex_bot.broker.oanda.OandaBroker` (the
  parser logic is mirrored locally, preserving the
  package-wide import isolation pattern);
- structurally cannot address any mutation endpoint via its
  allowlist.

Even if a future bug introduced a mutation reference, the
allowlist and the `fxtrade`-substring check would still refuse
any non-practice or non-read URL.

## 11. Capture script summary

`scripts/capture_oanda_observed_financing_pilot.py`:

- **CLI:** `--output DIR` (default `/tmp/...`),
  `--since-transaction-id ID` | `--range FROM TO` | (default
  discovery via `/summary`), `--dry-run`,
  `--require-practice-tag` (default on),
  `--provenance LABEL`.
- **Pipeline (default mode):**
  1. read `OANDA_ACCESS_TOKEN_PRACTICE` +
     `OANDA_ACCOUNT_ID_PRACTICE` (refuse with exit 2 if
     either is missing);
  2. build `httpx.Client` with `Bearer` token in header (never
     logged or printed);
  3. `GET /v3/accounts/{id}` — verify `"PRACTICE"` in
     `account.tags` (refuse with exit 3 if absent);
  4. `GET /v3/accounts/{id}/summary` — discover
     `lastTransactionID`;
  5. `GET /v3/accounts/{id}/transactions/sinceid?id=<last>`;
  6. parse each transaction via local mirror of
     `map_daily_financing` /
     `observed_financing_events`;
  7. hash account id via SHA-256;
  8. write one JSON file
     `<output>/observed_financing.json` in fixture schema
     (`kind: observed_financing_events`, `schema_version:
     1`, `synthetic: false`, `provenance`,
     `account_currency`, `account_id_hash`, sorted `events`).
- **Defense in depth:** practice REST host hard-coded; URL
  prefix + substring denylist; no `forex_bot` import; no
  mutation-helper reference; no token / raw-account-id in any
  artifact; `OANDA_*_LIVE` never consulted; mock-only tests
  for every code path.
- **Exit codes:** `0` OK / `2` missing creds / `3` not
  practice / `4` I/O / `5` HTTP / `6` RuntimeError.

## 12. Test status

**27 new tests pass** in
`tests/research/test_observed_capture_pilot.py`. Full repo
suite: **686 passes** (659 prior + 27 new). Ruff clean.

Coverage: exit-code rails, URL allowlist / denylist (practice
vs live REST/stream hosts, /orders, /trades, /positions,
/pricing, /pricing/stream, /configuration,
/transactions/stream), `_safe_get` refusal rails, parser
correctness on DAILY_FINANCING (per-trade, per-instrument,
account-level) + ORDER_FILL-with-financing, full
mock-HTTP round-trip writing fixture-shape JSON consumable by
the existing `research/financing/fixtures.load_observed_event_fixture`,
account_id_hash redaction with raw id absent from output, no
credential value in stdout/stderr/output, token reaches
factory but not stdout, grep + subprocess rails for no
`forex_bot` import and no mutation references, default-mode
`/summary` discovery, no output written on refusal.

## 13. Pilot capture result

**Not run.** Phase 4 attempted `--dry-run` and exited `2`
(`EXIT_MISSING_CREDS`) — practice credentials are not present
in this worktree's environment. This is a **valid** pilot
result per the sprint instructions. No output directory
created, no HTTP call attempted, no credential value
printed.

A future credentialed sprint (run by a human with practice
creds sourced) can execute the same script unchanged to
produce a real captured-events file.

## 14. Reconciliation result

**Blocked.** Phase 5 is structurally blocked because Phase 4
produced no observed-events file. The reconciliation CLI
([`scripts/reconcile_financing_fixtures.py`](../../scripts/reconcile_financing_fixtures.py),
sister sprint) is ready to consume any future captured output
that satisfies the fixture schema. The would-be command is
recorded in
[`FINANCING_OBSERVED_CAPTURE_RECONCILIATION.md`](FINANCING_OBSERVED_CAPTURE_RECONCILIATION.md)
for the future credentialed sprint.

## 15. Is MODELED financing now available?

**No.** All four layers refuse `MODELED`:

- `TableRateSource(treatment=MODELED)` raises at construction
  (fixture-loader sprint).
- `calculate_run` raises if a rate source self-reports
  `MODELED` (calculator sprint).
- `_build_report` in `scripts/reconcile_financing_fixtures.py`
  raises before writing if `financing_treatment == modeled`
  (reconciliation-tooling sprint).
- The new capture script produces only an observed-events
  file; it does not declare a `financing_treatment` at all
  (observed events feed *into* rate sources, they are not
  themselves a rate source).

The five-criterion MODELED checklist from
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
§11 is unchanged:

| # | criterion | status |
|---:|---|---|
| 1 | ≥ 60 captured rollovers across the traded universe | **0 — capture not run** |
| 2 | per-event reconciliation passes against captured data | blocked (no data) |
| 3 | `MODELED` `FinancingModel` implementation | not implemented |
| 4 | engine-PnL integration | not implemented |
| 5 | documented human approval | not granted |

## 16. Remaining limitations

- **No real captured data.** Pilot did not run; capture
  pipeline is built and tested but unfed.
- **One-shot capture, not a daemon.** Future productionization
  needs a scheduled runner with retries + cursor persistence
  + writes to the `observed_financing_events` SQLite table.
- **No SQLite write yet.** Script dumps to JSON only.
- **Only EUR_USD has a rate fixture** for the natural
  reconciliation target; other H4 pairs need a future
  rate-fixture-expansion sprint or captured-rate-derived
  source.
- **Practice account `longRate`/`shortRate` are 0.** Even a
  successful future credentialed practice capture is likely
  to find zero financing events — practice accounts don't
  carry real carry costs. A funded-account pilot (separate
  human authorization) is required for empirically useful
  data.
- **MODELED still many sprints away.** This sprint built the
  capture *primitive*; productionization, model
  implementation, engine integration, and human approval all
  remain.

## 17. Recommended next branch

Two options, both freeze-compatible:

1. **`research-financing-bp-day-fixture-expansion-001`** —
   add rate-fixture variants for the remaining 6 H4 universe
   pairs (GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF,
   NZD_USD). Still synthetic, still `ESTIMATED`. Broadens the
   reconciliation surface so a future credentialed capture
   sprint can reconcile every pair from day one. **No new
   broker permissions required.**

2. **A credentialed re-run of the existing pilot script** —
   the operator (a human) sources `.env` with
   `OANDA_ACCESS_TOKEN_PRACTICE` and `OANDA_ACCOUNT_ID_PRACTICE`,
   then re-runs the dry-run + a narrow capture window. This
   is **not** a new branch — it is the same script,
   re-executed with credentials. The Phase 4 doc in this
   sprint already records the exact command. If that future
   run produces non-zero financing events, Phase 5
   reconciliation against the EUR_USD rate fixture (or
   whatever pairs were captured) is the natural follow-up.

A **third** option — funded-account observed-capture
(`research-financing-funded-capture-002`) — is the only path
that produces empirically *useful* data (practice rates are 0).
That path requires its **own** explicit human authorization
**and** a separately-funded account; it is not a follow-on
from this sprint without further authorization. **Not
recommended unless and until the operator chooses to fund an
account specifically for this.**

## 18. Files to review first (priority order)

1. **[`docs/research/FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md)**
   — sprint scope, authorization scope, endpoint
   allow/denylist, credential / redaction rules, safety
   invariants.
2. **[`docs/research/FINANCING_OBSERVED_CAPTURE_EXISTING_PATH_AUDIT.md`](FINANCING_OBSERVED_CAPTURE_EXISTING_PATH_AUDIT.md)**
   — what already exists (parser, schema, repo, read-only
   endpoint) and the minimal-pilot-script wiring that builds
   on it.
3. **[`docs/research/FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`](FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md)**
   — headline status (script helpers, tests, limitations,
   safety state).
4. **[`docs/research/FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md)**
   — Phase 4 record (no creds → exit 2; would-be summary
   shape for a future credentialed run).
5. **[`docs/research/FINANCING_OBSERVED_CAPTURE_RECONCILIATION.md`](FINANCING_OBSERVED_CAPTURE_RECONCILIATION.md)**
   — Phase 5 blocker + the exact would-be reconciliation
   command.
6. **[`scripts/capture_oanda_observed_financing_pilot.py`](../../scripts/capture_oanda_observed_financing_pilot.py)**
   — the pilot script. Key functions: `_is_allowed_url`,
   `_safe_get`, `confirm_practice_account`,
   `parse_daily_financing`, `build_capture_output`.
7. **[`tests/research/test_observed_capture_pilot.py`](../../tests/research/test_observed_capture_pilot.py)**
   — 27 mock-only safety tests.

## 19. Cross-links

- Plan: [`FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md)
- Existing-path audit:
  [`FINANCING_OBSERVED_CAPTURE_EXISTING_PATH_AUDIT.md`](FINANCING_OBSERVED_CAPTURE_EXISTING_PATH_AUDIT.md)
- Pilot run:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md)
- Reconciliation:
  [`FINANCING_OBSERVED_CAPTURE_RECONCILIATION.md`](FINANCING_OBSERVED_CAPTURE_RECONCILIATION.md)
- Status: [`FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`](FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md)
- Future-capture pilot spec (this sprint executes its first
  step):
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Sister sprints:
  [`RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md`](RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md),
  [`RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md`](RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md),
  [`RESEARCH_FINANCING_MODEL_001_SUMMARY.md`](RESEARCH_FINANCING_MODEL_001_SUMMARY.md)
- Calculator protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Evidence index: [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
