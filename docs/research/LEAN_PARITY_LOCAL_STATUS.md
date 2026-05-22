# Lean Parity — Local Status

**Date:** 2026-05-22 · **Branch:** `infra-data-parity-001` · Phase 4

Records whether QuantConnect Lean can be run locally for the CAMPAIGN_002
H4 parity dry run, and — when it cannot — exactly how to enable it.

## Detection result (2026-05-22)

| component | status |
|---|---|
| `lean` CLI on `PATH` | **not installed** |
| `lean` Python package | **not installed** |
| Docker | installed (Docker 29.1.3) |
| Lean workspace in repo | none |

**Lean is not available locally. The parity dry run was NOT executed.**
No Lean result was produced, and none was fabricated. There is no
`docs/research/LEAN_PARITY_CAMPAIGN_002_RESULT.md` and no
`research/lean_parity/results/campaign_002_h4/` — those exist only after
a real local run.

This is the documented manual boundary from
`docs/research/LEAN_PARITY_DESIGN.md` §12: installing the Lean toolchain
is a deliberate, human-initiated step. Docker being present is helpful —
it is one of the two prerequisites — but the `lean` CLI itself is not
installed.

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

# 4. Build the local OANDA H4 store and the parity export bundle
#    (from this repo — needs OANDA practice credentials):
python scripts/rehydrate_oanda_h4_store.py
python scripts/export_lean_parity_data.py \
    --db data/oanda_h4_research.sqlite3 --instrument EUR_USD \
    --from 2020-01-01 --to 2026-05-20

# 5. Create the Lean algorithm from the skeleton in
#    research/lean_parity/campaign_002_h4_spec.md, consuming the
#    exported EUR_USD_H4_lean.csv as custom data.

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

1. The `lean` CLI is not installed (this doc's reason for skipping).
2. Even with Lean installed, the export bundle needs the local OANDA H4
   store, which needs OANDA practice credentials (Phase 1) — see
   `docs/research/OANDA_H4_DATA_REHYDRATION.md`.

Both are deliberate human steps. Until both are done, the local Lean
parity dry run stays documented-but-unexecuted.
