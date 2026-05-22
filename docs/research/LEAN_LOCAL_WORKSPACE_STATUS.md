# Lean Local Workspace — Status

**Date:** 2026-05-22 · **Branch:** `infra-lean-parity-execute-001` · Phase 1

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

1. **Lean CLI authentication is absent.** `lean init` requires a
   QuantConnect user id + API token to scaffold a workspace (it
   authenticates to the QuantConnect API and downloads Lean's
   reference-data bundle). Without `~/.lean/credentials`, `lean init`
   aborts at the credentials prompt and no workspace is created.

   Detail and the exact next steps: `LEAN_PARITY_EXECUTE_BLOCKED.md`.

2. **The `quantconnect/lean` Docker engine image is not pulled** —
   downstream of `lean init`; not reached.

## Safety statement

- No credential was read, echoed, or written. The check for
  `~/.lean/credentials` was a file-existence test only.
- No cloud job was submitted; no brokerage was contacted.
- The Lean CLI continues to live in an isolated venv that cannot
  affect the forex-bot environment.
- `strategy_evidence: false`. CAMPAIGN_002 stays REJECT regardless of
  any parity outcome.
