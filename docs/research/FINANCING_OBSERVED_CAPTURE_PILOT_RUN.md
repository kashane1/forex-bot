# Observed-Capture Pilot Run

**Date:** 2026-05-23 · **Branch:** `research-financing-observed-capture-pilot-001`
Phase 4 · `strategy_evidence: false`

Record of the **attempted** pilot capture run. Per the sprint
instructions ("Only run this phase if practice credentials are
visible"), the actual capture did **not** execute — practice
credentials are not present in the worktree's environment. The
attempted dry-run is documented here as a valid pilot result,
along with what a future credentialed run would look like.

> No broker / OANDA data was fetched. No order, trade, or
> position was touched. `configs/approved_strategies.yaml`
> remains `approved: []`. CAMPAIGN_002 remains REJECT. Paper /
> demo / live remain blocked. `MODELED` financing remains
> unavailable.

## 1. Environment snapshot (no values printed)

Verified by `python3 -c "import os; ..."` at sprint start:

| variable | state |
|---|---|
| `OANDA_ACCESS_TOKEN_PRACTICE` | UNSET |
| `OANDA_ACCOUNT_ID_PRACTICE` | UNSET |
| `OANDA_ACCESS_TOKEN_LIVE` | UNSET |
| `OANDA_ACCOUNT_ID_LIVE` | UNSET |
| `.env` (worktree root) | ABSENT |

No credential value was read or printed at any point.

## 2. Attempted dry-run command

```bash
python scripts/capture_oanda_observed_financing_pilot.py \
  --dry-run \
  --output /tmp/financing_capture_pilot_dryrun/
```

## 3. Output

```
[capture_oanda_observed_financing_pilot] missing practice credentials:
  set OANDA_ACCESS_TOKEN_PRACTICE and OANDA_ACCOUNT_ID_PRACTICE; refusing.
exit=2
```

- **Exit code:** `2` (`EXIT_MISSING_CREDS`)
- **Output directory:** not created (the script exits before
  writing anything when credentials are absent — confirmed by
  `test_no_output_written_on_refusal`)
- **Credential value printed:** **no** — only env var names
  appear in the message
- **Live tripwire check:** the script does not consult
  `OANDA_*_LIVE` variables at all; if either had been set, it
  would have made no difference (a separate test —
  `test_refuses_when_only_live_creds_present` — pins this)

This is the expected and **valid** pilot result for an
environment without practice credentials. The script refuses
loudly and safely.

## 4. Endpoint class — what the script *would* have done

Per [`FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md)
§4 and `_is_allowed_url` in the script:

| step | endpoint | method |
|---|---|---|
| 1. account + practice-tag check | `GET /v3/accounts/{accountID}` | GET |
| 2. dry-run: connectivity probe | `GET /v3/accounts/{accountID}/summary` | GET |
| 3a. since-mode capture | `GET /v3/accounts/{accountID}/transactions/sinceid?id=<last>` | GET |
| 3b. range-mode capture | `GET /v3/accounts/{accountID}/transactions?from=...&to=...` | GET |
| 3c. default mode | `GET /v3/accounts/{accountID}/summary` → use `lastTransactionID` → `GET /transactions/sinceid` | GET |

All read-only. No `POST`, no `PUT`, no `DELETE`, no `PATCH`.
A test pins that the only URLs ever requested by a real run
are members of this allowlist.

## 5. Environment

| dimension | value |
|---|---|
| Authorized scope | read-only OANDA **practice** transaction history |
| REST host | `https://api-fxpractice.oanda.com` (hard-coded; tests pin) |
| Account-tag verification | `--require-practice-tag` (default on) — checks `account.tags` contains `"PRACTICE"`; absent → exit 3 |
| Live REST host | denied (URL-prefix allowlist refuses; `_safe_get` raises on any `fxtrade` substring) |
| Live stream host | denied (same) |

## 6. Read-only confirmation

- The script never imports `submit_order`, `close_trade`,
  `cancel_order`, or any other mutation helper (grep rail
  `test_script_does_not_reference_mutation_helpers`).
- No HTTP method other than `GET` is anywhere in the script's
  executable code (verified by reading `_safe_get` and the
  endpoint helpers).
- No `POST` / `PUT` / `DELETE` / `PATCH` string appears
  outside docstrings.

## 7. Window

Not applicable — the dry-run does not fetch transactions, and
no full run was performed.

A future credentialed run would either:

- accept `--since-transaction-id <id>` (operator chooses the
  starting cursor), or
- accept `--range FROM_ISO TO_ISO` (operator chooses dates),
  or
- use the default mode (script discovers `lastTransactionID`
  via `/summary` and fetches `since`).

## 8. Redacted counts (would-be summary)

| metric | value (this run) |
|---|---:|
| Transactions scanned | 0 (no capture attempted) |
| Financing events found | 0 |
| Transaction types seen | none |
| Date range | n/a |
| Instruments | none |
| Total observed financing by currency | n/a |

A future credentialed run would surface these counts here, in
the same shape, with no raw account id and no token in any
field.

## 9. Output path

- Default path: `/tmp/financing_observed_capture/`
  (gitignored by the OS).
- This sprint: nothing was written.
- A future credentialed run would write one JSON file:
  `<output>/observed_financing.json`, fixture-shape,
  `synthetic: false`, `account_id_hash` (SHA-256 of raw
  account id), and the `events[]` parsed via the script's
  local mirror of the canonical parser.

**No raw output committed.** Per the sprint plan, raw
output is excluded from the repo unconditionally — the
artifact secret scanner is the safety net.

## 10. Were financing events found?

**No capture attempted; no events to count.**

If a future credentialed run finds zero financing events,
that is also a **valid** pilot result: it would confirm the
fetch + parse path works end-to-end and that the chosen
practice account has had no `DAILY_FINANCING` transactions
in the chosen window (likely — the practice account's
`longRate`/`shortRate` are `0` per
[`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md)).

If a future credentialed run finds non-zero financing
events, the next step is Phase 5 (reconciliation against
the existing synthetic rate fixtures or, ideally, a future
real rate fixture).

## 11. Was reconciliation possible?

**No.** No captured events to reconcile. Phase 5 is therefore
not applicable in this sprint's documented run; the
reconciliation step is documented as a future capability that
the now-existing CLI
([`scripts/reconcile_financing_fixtures.py`](../../scripts/reconcile_financing_fixtures.py))
can perform against any future captured output that satisfies
the fixture schema.

## 12. MODELED status

**`MODELED` financing remains unavailable.** The five-
criterion checklist in
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
§11 is unchanged:

| # | criterion | this sprint? |
|---:|---|:--:|
| 1 | ≥ 60 captured rollovers across the traded universe | **0 — no capture attempted** |
| 2 | per-event reconciliation passes against captured data | n/a — nothing captured |
| 3 | `MODELED` `FinancingModel` implementation | no |
| 4 | engine-PnL integration | no |
| 5 | documented human approval | no |

This sprint did not, and could not, satisfy criterion 1. A
single successful pilot capture — even a future credentialed
one — would only count toward criterion 1; it would still
leave 2–5 untouched. `MODELED` remains many sprints away.

## 13. Cross-links

- Sprint plan:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md)
- Existing-path audit:
  [`FINANCING_OBSERVED_CAPTURE_EXISTING_PATH_AUDIT.md`](FINANCING_OBSERVED_CAPTURE_EXISTING_PATH_AUDIT.md)
- Future-capture pilot spec:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Reconciliation CLI:
  [`FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md`](FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md)
- Capture script:
  [`scripts/capture_oanda_observed_financing_pilot.py`](../../scripts/capture_oanda_observed_financing_pilot.py)
- Capture tests:
  [`tests/research/test_observed_capture_pilot.py`](../../tests/research/test_observed_capture_pilot.py)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
