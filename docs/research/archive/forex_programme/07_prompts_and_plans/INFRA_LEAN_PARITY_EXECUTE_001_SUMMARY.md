# Infrastructure Lean-Parity Execute Sprint 001 — Summary & Handoff

**Date:** 2026-05-22 · **Branch:** `infra-lean-parity-execute-001`
**Base commit:** `f1c9d9f` (HEAD of `infra-lean-parity-run-001`)

> **SUPERSEDED — QuantConnect/LEAN CLI execution is RETIRED for this
> project** (decision date 2026-05-22, branch
> `infra-retire-quantconnect-lean-001`). The free-tier QuantConnect
> account does not provide the API access required for the intended
> local LEAN CLI workflow, and a paid QuantConnect upgrade has been
> declined. **No further LEAN authentication attempts are to be made.**
> Any wording below that recommends creating a (free) QuantConnect
> account, running `lean login`, or running `lean init` is retired and
> must not be acted on. The existing LEAN algorithm / mapping spec /
> harness artifacts are preserved as **historical infrastructure
> evidence only**. No LEAN result exists; no LEAN comparison exists;
> no strategy is approved; CAMPAIGN_002 remains **REJECT**;
> paper / demo / live remain blocked.
> See `docs/research/QUANTCONNECT_LEAN_RETIREMENT_DECISION.md` for the
> decision record and
> `docs/research/FREE_LOCAL_PARITY_VERIFIER_PLAN.md` for the replacement
> direction.

This sprint was prepared to run the local Lean parity backtest if Lean
CLI credentials were already present on this machine. They were **not
present**, and per the sprint's auth-handling rules the sprint did not
prompt for, request, or create them. No Lean backtest was executed and
no result was fabricated. **CAMPAIGN_002 remains REJECT**; the research
freeze is intact.

## What changed

**New docs** (this sprint):
- `INFRA_LEAN_PARITY_EXECUTE_001_PLAN.md` — sprint plan with explicit
  auth-handling rules (detect presence only, never prompt, never echo).
- `LEAN_LOCAL_WORKSPACE_STATUS.md` — factual Lean tooling / auth /
  workspace state.
- `LEAN_PARITY_EXECUTE_BLOCKED.md` — precise execution blocker, the
  blocker chain, and the exact next human commands.
- `INFRA_LEAN_PARITY_EXECUTE_001_SUMMARY.md` — this summary.

**Updated**: `CAMPAIGN_002_H4_PARITY_STATUS.md`, `EVIDENCE_INDEX.md`.

**No script, code, test, or strategy changes.** The full pytest / ruff
state is unchanged from `infra-lean-parity-run-001` (**388 tests
pass**, ruff clean).

## What did NOT change

- `configs/approved_strategies.yaml` remains empty (`approved: []`).
- No strategy approved; no campaign / hypothesis / verdict; no
  parameter tuned; no CAMPAIGN_002 rule changed.
- The bespoke strategy and engine are unchanged.
- `paper-loop`, `demo-loop`, and the live path still refuse.
- Prior campaign artifacts (CAMPAIGN_001–009) untouched.
- No order submitted; no live / brokerage credentials used.
- No QuantConnect account was created, no QC user id or API token was
  read, prompted-for, written, or committed.
- No cloud backtest submitted; no `lean cloud` / `lean live` command
  invoked. No `lean login` / `lean init` invoked (either could have
  requested credentials interactively).
- CAMPAIGN_002 remains **REJECT**.

## Lean auth / workspace status

- `lean` CLI: **installed** (`lean 1.0.225` in `/tmp/lean-venv`).
- Docker: **installed** (29.1.3).
- `~/.lean/credentials`: **absent** (file-existence test only; no
  secret read or printed).
- Lean workspace: **none** (no `lean init` has succeeded on this
  machine).
- `quantconnect/lean` Docker engine image: **not pulled** (downstream
  of the blocked `lean init`).

Detail: `LEAN_LOCAL_WORKSPACE_STATUS.md` and `LEAN_PARITY_EXECUTE_BLOCKED.md`.

## Lean data preflight status

**Not run** — without a Lean workspace there is nothing to preflight.
The seven CAMPAIGN_002 H4 export CSVs and the bespoke reference JSON
are all present on disk and reproducible from committed scripts.

## Lean run status

**Not run.** No Lean backtest was invoked; no `parity_summary.json`
exists. `LEAN_PARITY_CAMPAIGN_002_RESULT.md` is **not** created this
sprint (it would only exist after a real run).

## Comparison status

**Not run** — no Lean result to compare. The comparison harness
`scripts/compare_lean_campaign_002_parity.py` is committed and tested
(11 fixture tests), runnable with `--lean <path>` the moment a Lean
result exists.

## Divergence summary

**None observed** — no Lean run happened, so there is no divergence to
classify.

## Validation results

- `pytest` — **388 passed**.
- `ruff check src tests scripts` — clean.
- `scripts/validate_research_archive.py` — all checks pass.
- `scripts/check_research_freeze.py` — all checks pass.
- `scripts/scan_artifacts_for_secrets.py` — PASSED.
- `bot paper-loop` / `bot demo-loop` — both refuse (exit 2).
- `configs/approved_strategies.yaml` — `approved: []`.
- No `*.sqlite3` store, no `.env`, no bulky Lean output / candle CSV
  staged.

## Safety state

The research freeze is **intact**. The approved-strategy registry is
empty; every order-capable loop refuses; the bespoke engine is
unchanged; no credential of any kind (forex-bot `.env`, OANDA, or
QuantConnect) was read, prompted-for, written, or committed. The Lean
CLI remains in an isolated venv.

## Local files created but NOT committed

- `data/oanda_h4_research.sqlite3` — the seven-pair H4 store (unchanged
  this sprint). Gitignored.
- `research/lean_parity/exports/campaign_002_h4/*.csv` — seven Lean
  candle CSVs (unchanged). Gitignored.
- `/tmp/lean-venv/` — the isolated Lean CLI venv. Outside the repo.

No new local files were created this sprint that aren't committed.

## Remaining blockers

1. **QuantConnect/LEAN CLI path is RETIRED** — see the supersedence
   banner above and
   `docs/research/QUANTCONNECT_LEAN_RETIREMENT_DECISION.md`. The
   free-tier QuantConnect account does not provide the API access
   required for the intended local LEAN CLI workflow; a paid
   QuantConnect upgrade is declined. **No further LEAN authentication
   attempts are to be made.**
2. **The Lean algorithm was never validated** — and will not be under
   this branch's direction. It remains in the tree as historical
   infrastructure evidence only.
3. **Financing is estimated / stress-only** — standing live blocker.

## Recommended next human decision points

1. **Do NOT** create a QuantConnect account, run `lean login`, or run
   `lean init`. The LEAN CLI path is retired. The replacement direction
   is a free / local independent verifier — see
   `docs/research/FREE_LOCAL_PARITY_VERIFIER_PLAN.md`.
2. Reviewing the comparison-method doc (`LEAN_PARITY_COMPARISON_METHOD.md`)
   is still useful: its tolerance and divergence-classification framing
   carries over to the free / local verifier, even though the LEAN
   implementation will not run.
3. The research freeze stands. The bespoke engine is internally
   reproducible (exact CAMPAIGN_002 reproduction), but **not** yet
   corroborated by an independent engine. The free / local verifier
   plan is the replacement path — and even a full PASS there would
   approve nothing.

## Files to review first

1. `docs/research/INFRA_LEAN_PARITY_EXECUTE_001_PLAN.md` — the sprint
   plan + auth-handling rules.
2. This summary.
3. `docs/research/LEAN_LOCAL_WORKSPACE_STATUS.md` — the workspace state.
4. `docs/research/LEAN_PARITY_EXECUTE_BLOCKED.md` — the precise blocker
   and exact next human commands.
5. `docs/research/CAMPAIGN_002_H4_PARITY_STATUS.md` — the
   independent-engine parity status (now re-confirmed by this sprint).
