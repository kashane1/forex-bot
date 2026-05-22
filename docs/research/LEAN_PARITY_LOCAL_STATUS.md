# Lean Parity — Local Status

**Date:** 2026-05-22 · **Branch:** `infra-data-parity-001` · Phase 4
**Updated:** 2026-05-22 · `oanda-practice-readonly-001` Phase 8 — Lean
re-detected (still not installed); the data prerequisite is now cleared.

Records whether QuantConnect Lean can be run locally for the CAMPAIGN_002
H4 parity dry run, and — when it cannot — exactly how to enable it.

## Detection result (2026-05-22, oanda-practice-readonly-001 Phase 8)

| component | status |
|---|---|
| `lean` CLI on `PATH` | **not installed** |
| `lean` Python package | **not installed** |
| `dotnet` on host | not installed (not required — see note) |
| Docker | installed (Docker 29.1.3) |
| Lean workspace in repo | none |

**Lean is not available locally. The parity dry run was NOT executed.**
No Lean result was produced, and none was fabricated. There is no
`docs/research/LEAN_PARITY_CAMPAIGN_002_RESULT.md` and no
`research/lean_parity/results/campaign_002_h4/` — those exist only after
a real local run.

Per Phase 8's rule ("if Lean is already installed, run it; if not,
document the blocker"), Lean is **not already installed**, so this
sprint documents the blocker and skips execution. Installing the Lean
toolchain is a deliberate, human-initiated step — the documented manual
boundary from `docs/research/LEAN_PARITY_DESIGN.md` §12 and
`docs/research/LEAN_PARITY_EXECUTION_GUIDE.md` §3. This sprint does not
install it.

> **Note on `dotnet`:** the Lean engine is .NET-based, but the local
> backtester runs the engine **inside a Docker image** that already
> carries the .NET runtime. A host `dotnet` install is therefore **not**
> required — only the `lean` CLI (a Python package) and Docker are.

## What changed since the infra-data-parity-001 status

The earlier status listed **two** blockers. The second is now cleared:

- ~~The export bundle needs the local OANDA H4 store, which needs OANDA
  practice credentials.~~ **Cleared.** The local real-OANDA H4 store
  was built in `oanda-practice-readonly-001` Phase 4
  (`data/oanda_h4_research.sqlite3`) and the CAMPAIGN_002 H4 export
  bundle was produced in Phase 7
  (`research/lean_parity/exports/campaign_002_h4/`).

So the **only remaining blocker is the Lean toolchain itself.** The data
side is ready: a Lean run now needs only the CLI installed and an
algorithm written.

## Exact setup steps (to enable a local parity run)

All local and free — no QuantConnect cloud, no paid tier, no brokerage
connection.

```bash
# 1. Install the open-source Lean CLI.
pip install lean

# 2. Docker is already installed here; ensure Docker Desktop is running
#    (Lean's local backtester executes algorithms in Docker).

# 3. Initialize a Lean workspace OUTSIDE this repo's package tree.
cd ~/some/scratch/dir
lean init

# 4. DATA — already done (oanda-practice-readonly-001 Phases 4 & 7):
#    the local H4 store and the CAMPAIGN_002 export bundle exist. The
#    exported candle CSVs are at
#    research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv
#    (gitignored — regenerate with the commands in EXPORT_MANIFEST.md if
#    they are not present in your checkout).

# 5. Create the Lean algorithm from the skeleton in
#    research/lean_parity/campaign_002_h4_spec.md, consuming the
#    exported EUR_USD_H4_lean.csv as custom data. Use the authoritative
#    parameters in research/lean_parity/lean_parity_config.json.

# 6. Run the local backtest:
lean backtest "TrendFollowingC002Parity"
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

1. The `lean` CLI is not installed — this doc's reason for skipping. A
   deliberate human step (`pip install lean` + a Lean workspace +
   writing the algorithm).

The data prerequisite (a local OANDA H4 store and the parity export
bundle) is **no longer a blocker** — both exist as of Phases 4 and 7.
Until the Lean toolchain is installed and an algorithm written, the
local Lean parity dry run stays documented-but-unexecuted.
