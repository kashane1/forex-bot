# Lean Parity — CAMPAIGN_002 H4 dry run BLOCKED

**Date:** 2026-05-22 · **Branch:** `infra-lean-parity-run-001` · Phase 4
**Supersedes:** the `infra-lean-parity-001` Phase 4 blocker (the faithful
algorithm now exists; the blocker has moved downstream).

The local Lean parity **dry run for CAMPAIGN_002 H4 was not executed.**
No Lean result was produced and **none was fabricated** — there is no
`LEAN_PARITY_CAMPAIGN_002_RESULT.md` and no
`research/lean_parity/results/campaign_002_h4/`; those exist only after
a real local run.

This is an honest, precise blocker. CAMPAIGN_002 remains **REJECT**;
nothing here approves a strategy.

## What is ready

The entire parity harness is now in place — the run is one workspace
away:

- **Faithful Lean algorithm** —
  `research/lean_parity/algorithms/campaign_002_h4_baseline/main.py`
  (Phase 2), with implementation notes.
- **Mapping spec** — `docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md`.
- **No-RiskEngine bespoke reference** —
  `research/lean_parity/campaign_002_h4_bespoke_reference.json`
  (1,647 trades).
- **Comparison harness** — `scripts/compare_lean_campaign_002_parity.py`
  (tested), method in `LEAN_PARITY_COMPARISON_METHOD.md`.
- **Seven-pair Lean export bundle** —
  `research/lean_parity/exports/campaign_002_h4/`.
- **Lean CLI** — `lean 1.0.225` in an isolated venv; **Docker present**.

## The blocker — `lean init` requires a QuantConnect account

The standard first step to create a local Lean workspace, `lean init`,
**requires QuantConnect account credentials** (a user id + API token).
It authenticates to the QuantConnect API to scaffold the workspace and
download Lean's reference-data bundle, and **aborts without them**.

Exact CLI output:

```
$ lean init
...
Your user id and API token are needed to make authenticated requests to
the QuantConnect API
You can request these credentials on https://www.quantconnect.com/account
Both will be saved in /Users/kashane/.lean/credentials
User id: Aborted!
```

`lean init` exits without scaffolding a workspace; without a workspace
(and its reference-data bundle) `lean backtest` cannot run.

**Why this is a hard stop for this sprint:** the sprint rules state
**"Do not use QuantConnect cloud"** and **"Do not require paid
services"**, and the prior `oanda-practice-readonly-001` /
`infra-lean-parity-001` sprints set **"do not require user credentials
for Lean cloud."** Although a QuantConnect account is free to create,
`lean init` is a **cloud-authenticated** step — entering a QC user id
and API token is exactly the cloud-credential dependency those rules
forbid. This sprint therefore does **not** authenticate to QuantConnect,
and the local Lean backtest cannot proceed within its constraints.

The `quantconnect/lean` Docker **engine image** was not reached either —
it would be pulled by `lean backtest`, which is downstream of the
blocked `lean init`.

## Exact next steps (deliberate human decision)

A human who chooses to create a free QuantConnect account can complete
the run — the algorithm and harness are ready:

```bash
# 1. Lean CLI (already installable in a dedicated venv):
python3 -m venv ~/lean-cli-venv && ~/lean-cli-venv/bin/pip install lean

# 2. Initialise a Lean workspace OUTSIDE this repo. This step asks for a
#    QuantConnect user id + API token (free account, quantconnect.com/account):
cd ~/scratch && ~/lean-cli-venv/bin/lean init

# 3. Create a project; copy in the committed algorithm:
#    research/lean_parity/algorithms/campaign_002_h4_baseline/{main.py,config.json}

# 4. Place the exported candle CSVs where the custom-data reader expects
#    them — a campaign_002_h4/ folder under the Lean data directory
#    (regenerate via research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.md).

# 5. Run the local backtest (pulls the quantconnect/lean image once):
~/lean-cli-venv/bin/lean backtest "<project>"

# 6. Compare against the bespoke reference:
python3 scripts/compare_lean_campaign_002_parity.py \
    --lean <path-to>/parity_summary.json \
    --out docs/research/LEAN_PARITY_CAMPAIGN_002_RESULT.md
```

Per `LEAN_ALGORITHM_IMPLEMENTATION_NOTES.md`, the algorithm is authored
offline and **not yet validated**; the first run is expected to need a
debugging iteration (custom-data path, resolution, slice semantics)
before its numbers are trustworthy.

## Safety

No QuantConnect cloud was used, no account was created, no paid service
was engaged, no credentials were entered. The Lean CLI remains in an
isolated venv that cannot affect the forex-bot environment. CAMPAIGN_002
stays REJECT; `strategy_evidence: false`; nothing here approves a
strategy.
