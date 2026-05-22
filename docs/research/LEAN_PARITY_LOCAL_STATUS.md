# Lean Parity — Local Status

**Date:** 2026-05-22 · **Branch:** `infra-data-parity-001` · Phase 4
**Updated:** 2026-05-22 · `oanda-practice-readonly-001` Phase 8 — Lean
re-detected (not installed); data prerequisite cleared.
**Updated:** 2026-05-22 · `infra-lean-parity-001` Phase 3 — the `lean`
CLI is now **installed in an isolated venv** (see below).

Records whether QuantConnect Lean can be run locally for the CAMPAIGN_002
H4 parity dry run, and — when it cannot — exactly how to enable it.

## Detection result (2026-05-22, infra-lean-parity-001 Phase 3)

| component | status |
|---|---|
| `lean` CLI on system `PATH` | not on PATH |
| `lean` CLI in isolated venv `/tmp/lean-venv` | **installed — `lean 1.0.225`** |
| `lean` Python package (isolated venv) | installed |
| `dotnet` on host | not installed (not required — see note) |
| Docker | installed (Docker 29.1.3) |
| `quantconnect/lean` Docker engine image | not pulled |
| Lean workspace | none |

## Install attempt (Phase 3)

`pip install lean` was attempted and **succeeded**, installing `lean
1.0.225` into a **dedicated, isolated virtual environment** at
`/tmp/lean-venv`. The isolated venv is deliberate: installing the Lean
CLI into the same environment as `forex-bot` risks dependency-version
conflicts that could break the project's test suite. The isolated venv
**cannot disturb** the forex-bot environment — `pytest` and `ruff` are
unaffected.

The Lean CLI is run as `/tmp/lean-venv/bin/lean`. The venv is a
session-local working install; it is not committed and not referenced
by any repo code. For a persistent local setup, a human should create a
dedicated venv they control (see the steps below).

> **Note on `dotnet`:** the Lean engine is .NET-based, but the local
> backtester runs the engine **inside a Docker image** that already
> carries the .NET runtime. A host `dotnet` install is therefore **not**
> required — only the `lean` CLI (a Python package) and Docker are.

## What is now in place vs. what remains

**In place** (as of this sprint):
- The seven-pair CAMPAIGN_002 H4 data and Lean export bundle
  (`research/lean_parity/exports/campaign_002_h4/`, Phases 1–2).
- The authoritative parity config (`lean_parity_config.json`).
- The `lean` CLI (isolated venv).
- Docker.

**Still required for a meaningful Lean backtest:**
1. A Lean workspace (`lean init`) outside this repo's package tree.
2. The `quantconnect/lean` Docker engine image (pulled on first
   `lean backtest` — a multi-GB download).
3. A **faithful** Lean algorithm reimplementing the CAMPAIGN_002 H4
   `trend_following` baseline, consuming the exported CSV as custom
   data. Faithfulness is the hard part: an unfaithful algorithm yields
   a divergence that reflects authoring error, not a custom-engine bug.
   The skeleton is `research/lean_parity/campaign_002_h4_spec.md`.

## Exact setup steps (to enable a local parity run)

All local and free — no QuantConnect cloud, no paid tier, no brokerage
connection.

```bash
# 1. Install the Lean CLI in a dedicated venv (NOT the forex-bot venv,
#    to avoid dependency conflicts).
python3 -m venv ~/lean-cli-venv
~/lean-cli-venv/bin/pip install lean

# 2. Docker is already installed here; ensure Docker Desktop is running.

# 3. Initialize a Lean workspace OUTSIDE this repo's package tree.
cd ~/some/scratch/dir
~/lean-cli-venv/bin/lean init

# 4. DATA — already done (Phases 1-2): the seven-pair CAMPAIGN_002 H4
#    export bundle exists at
#    research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv
#    (gitignored — regenerate via EXPORT_MANIFEST.md if absent).

# 5. Write a faithful Lean algorithm from the skeleton in
#    research/lean_parity/campaign_002_h4_spec.md, using the
#    authoritative parameters in
#    research/lean_parity/lean_parity_config.json.

# 6. Run the local backtest (pulls the quantconnect/lean image once):
~/lean-cli-venv/bin/lean backtest "TrendFollowingC002Parity"
```

Then capture the result into `research/lean_parity/results/campaign_002_h4/`
(gitignored — bulky) and write the comparison into
`docs/research/LEAN_PARITY_CAMPAIGN_002_RESULT.md`, following
`docs/research/LEAN_PARITY_EXECUTION_GUIDE.md` §4–5 and
`research/lean_parity/CAMPAIGN_002_PARITY_CHECKLIST.md`.

## When the run does happen

- It is **verification, not research.** CAMPAIGN_002 is already REJECT;
  a parity result corroborates the bespoke engine or localizes a bug in
  it. It **cannot** approve any strategy.
- A **material divergence** must be documented as an engine discrepancy
  to investigate — never tuned away, never reported as a strategy result.
- The research freeze is unaffected either way.

## Current blockers

1. **No Lean workspace + faithful algorithm.** The `lean` CLI is now
   installed, but a meaningful backtest still needs a `lean init`
   workspace and a *faithful* CAMPAIGN_002 algorithm. Authoring a
   faithful reimplementation is a deliberate, careful step — an
   unfaithful algorithm produces a misleading parity result.
2. **The `quantconnect/lean` Docker image is not pulled** — a multi-GB
   download performed on the first `lean backtest`.

No QuantConnect cloud account and no paid tier are required — the local
Docker backtester is free and open-source.
