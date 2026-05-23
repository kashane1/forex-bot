# Lean Local Workspace — Status

**Date:** 2026-05-22 · **Branch:** `infra-lean-parity-execute-001` · Phase 1

> **SUPERSEDED — QuantConnect/LEAN CLI execution is RETIRED for this
> project** (decision date 2026-05-22, branch
> `infra-retire-quantconnect-lean-001`). The workspace state described
> below is preserved as historical evidence of the environment at the
> point the LEAN path was retired. **Do not run `lean login`,
> `lean init`, or any other LEAN/QuantConnect-authenticating
> command.** The free-tier QuantConnect account does not provide the
> API access required for the intended local LEAN CLI workflow, and a
> paid QuantConnect upgrade has been declined. The local `/tmp/lean-venv`
> Lean CLI install and the absence of `~/.lean/credentials` are both
> left as-is; nothing in this project is expected to use them. See
> `docs/research/QUANTCONNECT_LEAN_RETIREMENT_DECISION.md` and
> `docs/research/FREE_LOCAL_PARITY_VERIFIER_PLAN.md`.

The factual state of the local Lean tooling, authentication, and
workspace, captured at the start of this sprint. The auth check is a
**file-presence test only** — no QuantConnect credential is read,
echoed, or written anywhere.

## Detected components

| component | status |
|---|---|
| `lean` CLI | **installed** — `lean 1.0.225` in `/tmp/lean-venv` (isolated venv) |
| Docker | **installed** — Docker 29.1.3 |
| `~/.lean/credentials` (QC user id + API token store) | **absent** |
| Lean workspace | **none** — no `lean init` has succeeded on this machine |
| `quantconnect/lean` Docker engine image | **not pulled** (would be pulled by the first `lean backtest`) |

## Local-only stance

- Cloud usage: **none.** No QuantConnect cloud backtest has been
  submitted, no `lean cloud …` command was run, and the absence of
  `~/.lean/credentials` means even `lean init`'s authenticated API call
  has not run this sprint.
- Brokerage usage: **none.** No `lean live …` command, no broker
  connection.
- Auth present: **no.** The presence check was `[ -f ~/.lean/credentials ]`
  — a file-existence test that prints nothing about the contents.

## Workspace path

There is no Lean workspace. The committed Lean algorithm lives at
`research/lean_parity/algorithms/campaign_002_h4_baseline/` inside this
repo; per the sprint plan and Lean's conventions, a Lean workspace is
created **outside** the repo (e.g. under the user's home), into which
the algorithm would be copied. None has been created here.

## Blockers

1. **QuantConnect/LEAN CLI path is RETIRED for this project.** The
   reason is no longer "auth absent": it is an explicit decision not
   to use QuantConnect because the free-tier account does not provide
   the API access required for the intended local LEAN CLI workflow,
   and a paid QuantConnect upgrade has been declined. **No further
   LEAN/QuantConnect authentication will be attempted.** See
   `QUANTCONNECT_LEAN_RETIREMENT_DECISION.md`. The replacement path is
   `FREE_LOCAL_PARITY_VERIFIER_PLAN.md`.

2. **The `quantconnect/lean` Docker engine image is not pulled** —
   downstream of `lean init`; not reached, and now retired.

## Safety statement

- No credential was read, echoed, or written. The check for
  `~/.lean/credentials` was a file-existence test only.
- No cloud job was submitted; no brokerage was contacted.
- The Lean CLI continues to live in an isolated venv that cannot
  affect the forex-bot environment.
- `strategy_evidence: false`. CAMPAIGN_002 stays REJECT regardless of
  any parity outcome.
