# Lean Parity Execute — BLOCKED (auth absent)

**Date:** 2026-05-22 · **Branch:** `infra-lean-parity-execute-001` · Phase 1

> **SUPERSEDED — QuantConnect/LEAN CLI execution is RETIRED for this
> project** (decision date 2026-05-22, branch
> `infra-retire-quantconnect-lean-001`). The blocker described here is
> no longer "auth absent, please log in"; it is now an explicit project
> decision **not to use QuantConnect/LEAN** because the free-tier
> QuantConnect account does not provide the API access required for
> the intended local LEAN CLI workflow, and a paid QuantConnect
> upgrade has been declined. **Do not run `lean login`, `lean init`, or
> any other command that authenticates to QuantConnect.** The "Exact
> next steps" below are retired and must not be acted on; they are
> retained only as historical evidence of what the prior plan was.
> See `docs/research/QUANTCONNECT_LEAN_RETIREMENT_DECISION.md` for the
> decision record and
> `docs/research/FREE_LOCAL_PARITY_VERIFIER_PLAN.md` for the replacement
> direction.

The local Lean parity **execution was not performed.** No Lean backtest
ran and no Lean result was fabricated — there is no
`LEAN_PARITY_CAMPAIGN_002_RESULT.md` (this sprint), no
`research/lean_parity/results/campaign_002_h4/`, and no
`LEAN_PARITY_CAMPAIGN_002_COMPARISON.md`; those exist only after a real
local run.

This is an honest, precise blocker. CAMPAIGN_002 remains **REJECT**;
nothing here approves a strategy.

## The blocker

Per the sprint's auth-handling rules, this sprint runs the local Lean
backtest **only if Lean CLI credentials are already present locally**
(`~/.lean/credentials`). It must not prompt for, request, or create
QuantConnect credentials itself.

The file `~/.lean/credentials` **does not exist on this machine**
(checked with `[ -f ~/.lean/credentials ]` — a file-existence test that
prints nothing about contents). Without that file, `lean init` aborts
at the credentials prompt and no Lean workspace can be scaffolded —
which means `lean backtest` cannot be invoked, even for a purely local
Docker backtest.

The blocker chain:

```
no ~/.lean/credentials
  → `lean init` cannot scaffold a workspace (it authenticates to QC's API)
    → no Lean workspace exists
      → `lean backtest` cannot run
        → no Lean parity result
          → no Lean ↔ bespoke comparison
```

The `quantconnect/lean` Docker engine image (downstream of the
blocked `lean init`) was not pulled either.

## What is ready

Everything the run needs except the workspace:

- **Lean CLI** — `lean 1.0.225` in `/tmp/lean-venv` (isolated).
- **Docker** — 29.1.3.
- **Faithful Lean algorithm** —
  `research/lean_parity/algorithms/campaign_002_h4_baseline/main.py`
  (`infra-lean-parity-run-001` Phase 2).
- **Mapping spec, implementation notes, comparison method** —
  `docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md`,
  `docs/research/LEAN_ALGORITHM_IMPLEMENTATION_NOTES.md`,
  `docs/research/LEAN_PARITY_COMPARISON_METHOD.md`.
- **No-RiskEngine bespoke reference** —
  `research/lean_parity/campaign_002_h4_bespoke_reference.json`.
- **Seven-pair Lean export CSVs** —
  `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv`
  (locally present, gitignored, regenerable).
- **Comparison harness** —
  `scripts/compare_lean_campaign_002_parity.py` (tested).

## Exact next steps (RETIRED — do not run)

> The command list below was the prior plan and is **retired**. The
> QuantConnect/LEAN CLI path will not be reopened unless the user
> explicitly says so. **Do not run `lean login`, `lean init`, or
> `lean backtest`. Do not create a QuantConnect account. Do not
> connect a paid QuantConnect upgrade.** This block is preserved only
> as historical evidence of what the prior plan would have done.

```bash
# RETIRED — do not run. Preserved for historical accuracy.
# /tmp/lean-venv/bin/lean login          # would authenticate to QuantConnect
# cd ~/scratch && /tmp/lean-venv/bin/lean init
# /tmp/lean-venv/bin/lean backtest "<project>"
# python3 scripts/compare_lean_campaign_002_parity.py \
#     --lean <path-to>/parity_summary.json \
#     --out docs/research/LEAN_PARITY_CAMPAIGN_002_RESULT.md
```

For the active path forward, see
`docs/research/FREE_LOCAL_PARITY_VERIFIER_PLAN.md`. The algorithm at
`research/lean_parity/algorithms/campaign_002_h4_baseline/main.py`
remains as historical infrastructure evidence only and is not
expected to be executed under this project.

## What this sprint did and did not do

- It did **not** prompt for, request, or write any QuantConnect
  credential. It did **not** invoke `lean login` or `lean init` —
  either could have requested credentials interactively.
- It did **not** submit any cloud backtest, did **not** contact any
  brokerage, did **not** trade.
- It did **not** fabricate a Lean result or a comparison; the
  `parity_summary.json` and the comparison docs simply do not exist
  this sprint.

## Safety

CAMPAIGN_002 stays **REJECT**. `configs/approved_strategies.yaml`
remains `approved: []`. The bespoke engine is unchanged. The freeze is
intact. `strategy_evidence: false`.
