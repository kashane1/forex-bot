# QuantConnect / LEAN — Retirement Decision Record

**Date:** 2026-05-22 · **Branch:** `infra-retire-quantconnect-lean-001`
**Status:** RETIRED — the QuantConnect/LEAN CLI execution path is closed
for this project and must not be reopened without explicit user
approval.

## Decision summary

QuantConnect (cloud platform) and the LEAN CLI workflow are **retired**
as the independent-engine parity tool for this project. The bespoke
backtest engine will not be corroborated by LEAN. The replacement
direction is a **free / local independent verifier** — see
[`FREE_LOCAL_PARITY_VERIFIER_PLAN.md`](FREE_LOCAL_PARITY_VERIFIER_PLAN.md).

Nothing in this decision relaxes the research freeze. **No strategy is
approved. CAMPAIGN_002 remains REJECT. Paper / demo / live remain
blocked. No broker credentials have been used. No orders have been
submitted.**

## Why QuantConnect / LEAN was considered

CAMPAIGN_002 (`trend_following` H4 baseline, real OANDA practice data)
closed REJECT. The bespoke backtest engine is internally reproducible —
the custom-engine reproduction in
`backtests/diagnostics/custom_campaign_002_h4_parity.md` matches the
committed report exactly (1,032 trades, zero per-pair deltas), and the
no-RiskEngine reference in
`research/lean_parity/campaign_002_h4_bespoke_reference.json` (1,647
trades) isolates the strategy + engine mechanics.

What is missing is **independent-engine corroboration** — proof that
the engine itself is not the source of the REJECT. The
`infra-lean-parity-001`, `infra-lean-parity-run-001`, and
`infra-lean-parity-execute-001` sprints prepared a LEAN-based path to
provide that corroboration locally (LEAN CLI + Docker, no cloud
backtest, no broker).

## What was successfully prepared (preserved as historical evidence)

The following artifacts are in the tree and remain valid as
**historical infrastructure evidence only**. They are *not* strategy
evidence; they did not produce a LEAN result; and they will not be
executed under this project.

- `docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md` — bespoke → LEAN
  behavior mapping spec.
- `docs/research/LEAN_ALGORITHM_IMPLEMENTATION_NOTES.md` — faithful vs
  approximated notes.
- `docs/research/LEAN_PARITY_COMPARISON_METHOD.md` — comparison metrics,
  tolerances, divergence taxonomy. The taxonomy carries over to the
  free / local verifier.
- `docs/research/LEAN_PARITY_DESIGN.md` and
  `docs/research/LEAN_PARITY_EXECUTION_GUIDE.md` — design / execution
  framing (now historical).
- `research/lean_parity/algorithms/campaign_002_h4_baseline/main.py` —
  authored-but-never-validated LEAN algorithm. Will not run.
- `scripts/compare_lean_campaign_002_parity.py` — comparison harness
  (tested against fixtures; the LEAN side will never feed it).
- `research/lean_parity/campaign_002_h4_bespoke_reference.json` — the
  no-RiskEngine bespoke reference. **Still useful**: it is the
  reference the free / local verifier will compare against.
- `research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.md` —
  the seven-pair H4 export bundle (CSVs are gitignored, regenerable
  from the manifest). **Still useful**: the free / local verifier can
  consume the same export bundle.

## What blocked LEAN execution

1. `lean init` (the standard step to scaffold a local LEAN workspace)
   authenticates to the QuantConnect API and aborts without
   `~/.lean/credentials`.
2. `~/.lean/credentials` was never created. The execute sprint
   explicitly **did not** prompt for, request, or write QuantConnect
   credentials — its rules forbade taking that step on the user's
   behalf.
3. The downstream `quantconnect/lean` Docker engine image was never
   pulled.

Detail: `LEAN_PARITY_EXECUTE_BLOCKED.md`,
`LEAN_LOCAL_WORKSPACE_STATUS.md`,
`INFRA_LEAN_PARITY_EXECUTE_001_SUMMARY.md` (all marked SUPERSEDED).

## User decision

The user has decided **not** to use QuantConnect / LEAN. The reasoning,
recorded here for posterity:

- The **free-tier QuantConnect account does not provide the API access
  required** for the intended local LEAN CLI workflow (e.g. data
  download, workspace scaffolding via `lean init`, and other
  authenticated operations). The free tier therefore fails to support
  the workflow this project specifically needs.
- A **paid QuantConnect upgrade is declined**. The user is not
  prepared to pay for QuantConnect access for this project's
  research-only purpose.

The combination of those two facts closes the QuantConnect / LEAN CLI
path. Reopening it requires the user to explicitly say so; no agent /
script / sprint is to attempt it on the user's behalf.

## Exact project consequence

- The bespoke backtest engine **remains internally reproducible** (the
  custom-engine reproduction matches the committed report exactly).
- The bespoke backtest engine **remains uncorroborated by an
  independent engine** as of this branch — and will stay uncorroborated
  until a free / local independent verifier is implemented and run.
- The LEAN-prepared artifacts (mapping spec, algorithm, comparison
  harness, export bundle) **stay in the tree** as historical
  infrastructure evidence. They are not removed.
- The research freeze is **intact**. The approved-strategy registry is
  empty; every order-capable loop refuses.

## What must NOT be attempted again without explicit user approval

- Creating a QuantConnect account (free or paid).
- Running `lean login`.
- Running `lean init`.
- Running `lean cloud …` or `lean live …`.
- Running any LEAN backtest, locally or otherwise.
- Connecting any brokerage to LEAN.
- Re-recommending the LEAN path in any new doc.

The local `/tmp/lean-venv` LEAN CLI install and the absence of
`~/.lean/credentials` are left as-is. Nothing in this project is
expected to use them. They are not deleted; deletion is an unrelated
local-environment housekeeping decision the user can make outside this
sprint.

## What remains valid from the prior work

- The custom-engine reproduction in
  `backtests/diagnostics/custom_campaign_002_h4_parity.md`.
- The no-RiskEngine bespoke reference at
  `research/lean_parity/campaign_002_h4_bespoke_reference.json` (1,647
  trades).
- The seven-pair H4 export bundle at
  `research/lean_parity/exports/campaign_002_h4/`.
- The CAMPAIGN_002 mapping spec, comparison method (tolerances and
  divergence taxonomy), and implementation notes — they describe the
  behavior the free / local verifier must also reproduce, even though
  the LEAN-specific implementation will not be executed.
- The comparison harness `scripts/compare_lean_campaign_002_parity.py`
  is kept; whether the free / local verifier reuses it or replaces it
  is a Phase-level decision in the verifier plan.

## Replacement direction — free / local independent verifier

See [`FREE_LOCAL_PARITY_VERIFIER_PLAN.md`](FREE_LOCAL_PARITY_VERIFIER_PLAN.md)
for the candidate approaches (minimal independent event-loop verifier,
vectorized pandas verifier, third-party-library feasibility,
fixture-level rule verifier), the recommended approach, the inputs and
outputs, the divergence taxonomy, the guardrails, and the proposed
phased implementation sprint.

The replacement path is **fully local, free, deterministic, no cloud,
no API, no broker credentials**. It does not change strategy rules. It
does not change CAMPAIGN_002 parameters. It does not approve a
strategy.

## Safety state at decision

- **No strategy approved.** `configs/approved_strategies.yaml`:
  `approved: []`.
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.** `paper-loop`, `demo-loop`,
  and the live path all refuse before broker construction; the
  research-freeze gate confirms this on every run.
- **No broker credentials used.** No OANDA practice or live credential
  was read in service of this decision.
- **No orders submitted.** This branch is documentation-only.
- **No QuantConnect credential** was requested, prompted-for, read,
  written, or committed at any point.
- **No LEAN run exists.** No `parity_summary.json`. No
  `LEAN_PARITY_CAMPAIGN_002_RESULT.md`. No
  `LEAN_PARITY_CAMPAIGN_002_COMPARISON.md`.

## Files to review first

1. This decision record.
2. `docs/research/FREE_LOCAL_PARITY_VERIFIER_PLAN.md` — the replacement
   direction.
3. `docs/research/INFRA_RETIRE_QUANTCONNECT_LEAN_001_SUMMARY.md` — the
   sprint summary (added in the final phase of this branch).
4. `docs/research/EVIDENCE_INDEX.md` — updated index.
