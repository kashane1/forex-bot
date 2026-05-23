# Free / Local Parity Verifier — Full-Data Run

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-002-full-data-run`
**Phase:** 2 · `strategy_evidence: false`

The first attempted full-data execution of the free / local
independent verifier. **Status: BLOCKED** — the seven H4 export CSVs
are not present locally on this branch (see
[`FREE_LOCAL_PARITY_VERIFIER_DATA_UNBLOCK_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_DATA_UNBLOCK_STATUS.md)).
The verifier script ran cleanly, reported BLOCKED per pair, exited 2,
and wrote a deterministic zero-trade summary — exactly the behavior
the implementation was designed to produce when bulk inputs are
missing.

> No strategy is approved. CAMPAIGN_002 remains REJECT. Paper /
> demo / live remain blocked. No orders were submitted. No
> QuantConnect / LEAN command was run.

## Command run

```bash
python scripts/run_free_local_parity_verifier.py \
    --output /tmp/parity_verifier_002_run/
```

The output directory is **outside the repo** (under `/tmp/`) and is
not committed. Even if a successful run had produced a `trades.csv`,
it would have been gitignored — the `.gitignore` rule
`research/parity_verifier/results/**/trades.csv` was added in Sprint
001 and the verifier never writes outside its `--output` argument.

## Input CSV paths checked (all absent)

The script attempts to open each per-pair CSV under
`research/lean_parity/exports/campaign_002_h4/`:

- `AUD_USD_H4_lean.csv` — missing
- `EUR_USD_H4_lean.csv` — missing
- `GBP_USD_H4_lean.csv` — missing
- `NZD_USD_H4_lean.csv` — missing
- `USD_CAD_H4_lean.csv` — missing
- `USD_CHF_H4_lean.csv` — missing
- `USD_JPY_H4_lean.csv` — missing

The seven `*.provenance.json` siblings are present (committed) and
pin each CSV's expected SHA-256. No CSV regeneration was performed
this sprint (see the data unblock status doc for the reasoning).

## Output path

`/tmp/parity_verifier_002_run/` — three files written:

- `parity_summary.json` — valid `VerifierResult` shape; `total_trades: 0`,
  `pairs: []`, `strategy_evidence: false`, `risk_engine_used: false`.
- `trades.csv` — header row only; no trades.
- `parity_summary.md` — markdown summary with the "Pairs blocked"
  section listing all seven instruments.

## Run status — BLOCKED

```text
Loaded bespoke reference: …campaign_002_h4_bespoke_reference.json (1647 trades, 7 pairs).
BLOCKED — AUD_USD: CSV not found …
BLOCKED — EUR_USD: CSV not found …
BLOCKED — GBP_USD: CSV not found …
BLOCKED — NZD_USD: CSV not found …
BLOCKED — USD_CAD: CSV not found …
BLOCKED — USD_CHF: CSV not found …
BLOCKED — USD_JPY: CSV not found …

Wrote: /tmp/parity_verifier_002_run/parity_summary.json
       /tmp/parity_verifier_002_run/trades.csv
       /tmp/parity_verifier_002_run/parity_summary.md
Verifier total trades: 0
Blocked pairs: ['AUD_USD', 'EUR_USD', 'GBP_USD', 'NZD_USD', 'USD_CAD', 'USD_CHF', 'USD_JPY']
```

Exit code: **2** (the verifier's documented signal that no pair
produced a usable result).

## Per-pair status

| instrument | status | rows processed | trades | warnings / errors |
|---|---|---|---|---|
| EUR_USD | BLOCKED | — | — | CSV not found |
| GBP_USD | BLOCKED | — | — | CSV not found |
| USD_JPY | BLOCKED | — | — | CSV not found |
| AUD_USD | BLOCKED | — | — | CSV not found |
| USD_CAD | BLOCKED | — | — | CSV not found |
| USD_CHF | BLOCKED | — | — | CSV not found |
| NZD_USD | BLOCKED | — | — | CSV not found |

## Totals

- **Total verifier trades:** 0 (no pair ran).
- **Trades by pair:** all 0.
- **Long / short counts:** 0 / 0.
- **First / last trade timestamps:** N/A (no trades).
- **Pairs processed:** 0 of 7.
- **Pairs blocked:** 7 of 7.

## Warnings / errors

- 7 × `FileNotFoundError` (handled cleanly by the script's BLOCKED
  branch — does not crash).
- 0 crashes, 0 stack traces, 0 unhandled exceptions.

## Known limitations

- **Cannot produce comparison numbers** without the seven CSVs.
  Phase 3 will run the comparison harness against the
  `compare.blocked_report` path to record a structurally identical
  BLOCKED comparison report.
- **Cannot exercise the bespoke engine cross-check** until the data
  is present. The verifier's fixture-level tests (85 cases pass in
  Sprint 001) cover the implementation's behavior on synthetic bars;
  they do not stand in for a real-candle parity check.
- **No verifier-side debugging signal.** Phase 4 of this sprint is
  conditional on a material divergence from a full-data run; with
  no full-data run, there is no divergence to localize and the
  debugging pass is correctly skipped.

## Local output files (not committed)

| path | purpose | committed? |
|---|---|---|
| `/tmp/parity_verifier_002_run/parity_summary.json` | shape-valid VerifierResult, all zeros | no — outside repo |
| `/tmp/parity_verifier_002_run/trades.csv` | header-only, zero data rows | no — outside repo |
| `/tmp/parity_verifier_002_run/parity_summary.md` | markdown summary listing blocked pairs | no — outside repo |
| `/tmp/parity_verifier_002_run/run.log` | captured stdout/stderr from the invocation | no — outside repo |

`git status` is clean after the run (only the doc this phase commits
is staged); no data files staged.

## Verifier-side bugs

**None found.** The script reported the BLOCKED state cleanly, wrote
a valid `parity_summary.json` (shape passes the Pydantic
`VerifierResult` model with `strategy_evidence: false`,
`risk_engine_used: false`, and total trades consistent with the
empty `pairs` list), and returned exit code 2 — the documented
signal for "every requested pair was blocked".

## Bespoke-engine bugs

**N/A.** The bespoke engine was not exercised this sprint. No
real-candle cross-check happened, so no bespoke-side divergence was
observable.

## What this proves

- The verifier script handles a fully-blocked input cleanly: clear
  per-pair BLOCKED messages, valid output shape, deterministic exit
  code 2, no crash, no fabricated data.
- The implementation from Sprint 001 holds up against a real
  invocation in a no-data environment.

## What this does NOT prove

- It does not corroborate the bespoke engine on real candles —
  requires the absent CSVs.
- It does not approve any strategy. CAMPAIGN_002 remains REJECT.
- It does not lift the research freeze.
- It does not enable any paper / demo / live loop.
- It does not contact any broker, cloud, or external service.

## Cross-links

- Data unblock status: [`FREE_LOCAL_PARITY_VERIFIER_DATA_UNBLOCK_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_DATA_UNBLOCK_STATUS.md)
- Sprint plan: [`INFRA_FREE_LOCAL_PARITY_VERIFIER_002_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_002_PLAN.md)
- Event-loop status (Sprint 001): [`FREE_LOCAL_PARITY_VERIFIER_EVENT_LOOP_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_EVENT_LOOP_STATUS.md)
- Verifier script: [`scripts/run_free_local_parity_verifier.py`](../../scripts/run_free_local_parity_verifier.py)
