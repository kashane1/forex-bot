# Free / Local Parity Verifier — Sprint-003 Full-Data Run

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-003-with-data`
**Phase:** 3 · `strategy_evidence: false`

The Sprint-003 invocation of the verifier script against the seven
H4 CSVs. **Status: BLOCKED** — the CSVs were not exported at Phase 2
(no SQLite store; no OANDA credentials → no rehydrate fetch). The
script handled the no-data state exactly as designed: 7 × BLOCKED
messages, exit code 2, valid zero-trade summary, no crash, no
fabricated data.

> No strategy is approved. CAMPAIGN_002 remains REJECT. Paper /
> demo / live remain blocked. No orders were submitted. No
> QuantConnect / LEAN command was run.

## Command run

```bash
python scripts/run_free_local_parity_verifier.py \
    --output /tmp/parity_verifier_003_run/
```

The output directory is **outside the repo** (`/tmp/`) and is not
committed. The `.gitignore` rule
`research/parity_verifier/results/**/trades.csv` from Sprint 001
would have applied if the verifier had written into the repo.

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

## Output directory

`/tmp/parity_verifier_003_run/` — four files written:

- `parity_summary.json` — valid `VerifierResult` shape;
  `total_trades: 0`, `pairs: []`, `strategy_evidence: false`,
  `risk_engine_used: false`.
- `trades.csv` — header row only.
- `parity_summary.md` — markdown summary with the "Pairs blocked"
  section listing all seven instruments.
- `run.log` — captured stdout/stderr.

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

Wrote: /tmp/parity_verifier_003_run/parity_summary.json
       /tmp/parity_verifier_003_run/trades.csv
       /tmp/parity_verifier_003_run/parity_summary.md
Verifier total trades: 0
Blocked pairs: ['AUD_USD', 'EUR_USD', 'GBP_USD', 'NZD_USD', 'USD_CAD', 'USD_CHF', 'USD_JPY']
```

Exit code: **2**.

## Per-pair status

| instrument | status | trades | warnings / errors |
|---|---|---|---|
| EUR_USD | BLOCKED | — | CSV not found |
| GBP_USD | BLOCKED | — | CSV not found |
| USD_JPY | BLOCKED | — | CSV not found |
| AUD_USD | BLOCKED | — | CSV not found |
| USD_CAD | BLOCKED | — | CSV not found |
| USD_CHF | BLOCKED | — | CSV not found |
| NZD_USD | BLOCKED | — | CSV not found |

## Totals

- **Total verifier trades:** 0.
- **Trades by pair:** all 0.
- **Long / short counts:** 0 / 0.
- **First / last trade timestamps:** N/A.
- **Pairs processed:** 0 / 7.
- **Pairs blocked:** 7 / 7.

## Warnings / errors

- 7 × `FileNotFoundError` (handled cleanly by the script's BLOCKED
  branch — no crash, no stack trace).

## Generated outputs not committed

| path | committed? |
|---|---|
| `/tmp/parity_verifier_003_run/parity_summary.json` | no — outside repo |
| `/tmp/parity_verifier_003_run/trades.csv` | no — outside repo |
| `/tmp/parity_verifier_003_run/parity_summary.md` | no — outside repo |
| `/tmp/parity_verifier_003_run/run.log` | no — outside repo |

`git status` shows only the documentation files this phase commits.

## Verifier-side bugs

**None found.** The script reported the BLOCKED state cleanly,
produced a valid `parity_summary.json` (shape passes the Pydantic
`VerifierResult` model with `strategy_evidence: false`,
`risk_engine_used: false`), and returned exit code 2 as designed.

## What this proves

- The verifier continues to behave correctly under a no-data
  environment: deterministic per-pair BLOCKED messages, valid output
  shape, no crash, no fabricated data, no silent zero-trade
  "success".

## What this does NOT prove

- It does not corroborate the bespoke engine on real candles —
  requires the absent CSVs.
- It does not approve any strategy. CAMPAIGN_002 remains REJECT.

## Cross-links

- Rehydrate status: [`FREE_LOCAL_PARITY_VERIFIER_003_REHYDRATE_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_003_REHYDRATE_STATUS.md)
- Export status: [`FREE_LOCAL_PARITY_VERIFIER_003_EXPORT_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_003_EXPORT_STATUS.md)
- Sprint plan: [`INFRA_FREE_LOCAL_PARITY_VERIFIER_003_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_003_PLAN.md)
- Verifier script: [`scripts/run_free_local_parity_verifier.py`](../../scripts/run_free_local_parity_verifier.py)
