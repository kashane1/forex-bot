# Free / Local Parity Verifier — Data Unblock Status

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-002-full-data-run`
**Phase:** 1 · `strategy_evidence: false`

Whether the seven-pair H4 CSV exports needed by the verifier are
locally available, and if not, why. **Status: BLOCKED.** This is a
data / credential availability blocker, not a verifier-implementation
gap.

> No strategy is approved. CAMPAIGN_002 remains REJECT. Paper / demo /
> live remain blocked. No orders were submitted. No QuantConnect /
> LEAN command was run. `configs/approved_strategies.yaml` remains
> `approved: []`.

## Status — BLOCKED

The seven H4 CSV exports required for a full-data verifier run are
**not present locally** on this branch, and they cannot be
regenerated under the rules this sprint operates under.

## Source used

**None — no source data is available locally and no fetch was
performed.** The two repo-approved sources are:

1. The local `data/oanda_h4_research.sqlite3` H4 store — **absent**.
2. The OANDA practice historical-candle re-fetch (via
   `scripts/rehydrate_oanda_h4_store.py`) — **not run** because no
   practice credentials are configured on this branch (no `.env`, no
   `OANDA_*` environment variables).

## Whether SQLite was present or regenerated

| check | result |
|---|---|
| `data/oanda_h4_research.sqlite3` file present | **NO** (only `data/.gitkeep`) |
| `scripts/rehydrate_oanda_h4_store.py --verify` (read-only, no creds needed) | reports `BLOCKER: no H4 store at data/oanda_h4_research.sqlite3` |
| Regeneration attempted | **No** — would have required OANDA practice credentials, none configured |

## Whether OANDA practice historical fetch was used

**No.** No call was made to any OANDA endpoint. The rehydrate script
was invoked only in `--verify` mode (the read-only mode that confirms
store absence without needing credentials). Per the sprint rules
("If credentials or source data are missing, stop this phase and
document the blocker. Do not fabricate data."), the fetch was not
attempted on the user's behalf.

## Practice credential state

Inspected without printing values:

- `.env` file in repo root: **absent**. Only `.env.example` is present.
- `OANDA_API_KEY` / `OANDA_ACCOUNT_ID` / `OANDA_*` environment
  variables in the current shell: **none set**.

No credential value was read, echoed, copied, or logged. The
inspection used `ls .env*` and `env | grep -i OANDA | sed 's/=.*/=<REDACTED>/'`.

## Exact commands run (no secrets)

```bash
# Read-only artifact inventory
ls data/                                          # data/ contains only .gitkeep
ls research/lean_parity/exports/campaign_002_h4/  # only *.provenance.json files
ls .env*                                          # only .env.example

# Read-only env-presence check, values stripped before any print
env | grep -iE "OANDA" | sed 's/=.*/=<REDACTED>/'  # empty — no OANDA_* set

# Read-only sqlite verify (no creds needed)
python scripts/rehydrate_oanda_h4_store.py --verify
# -> BLOCKER: no H4 store at data/oanda_h4_research.sqlite3.
```

No fetch, no export, no credential read. No regenerated data on
disk.

## Seven CSV export status

For each of the seven CAMPAIGN_002 H4 instruments, the CSV is
**missing locally**:

| instrument | CSV present? | provenance.json present? | rows | first ts | last ts |
|---|---|---|---|---|---|
| EUR_USD | **NO** | yes | — | — | — |
| GBP_USD | **NO** | yes | — | — | — |
| USD_JPY | **NO** | yes | — | — | — |
| AUD_USD | **NO** | yes | — | — | — |
| USD_CAD | **NO** | yes | — | — | — |
| USD_CHF | **NO** | yes | — | — | — |
| NZD_USD | **NO** | yes | — | — | — |

The seven `*.provenance.json` files are committed and pin the
SHA-256 each CSV must match if it is ever regenerated. They confirm
the data shape the verifier expects (e.g. EUR_USD: 9,931 H4 candles
from `2020-01-01T22:00:00+00:00` to `2026-05-19T21:00:00+00:00`).

## Files generated but not committed

**None.** This sprint phase generated no files. The verifier was
neither re-fetched, re-exported, nor re-run.

## Blocker — what is missing and how a future invocation can resolve it

To resolve this blocker, a future invocation needs **either**:

1. **A local `data/oanda_h4_research.sqlite3` H4 store** with the
   full CAMPAIGN_002 seven-pair window. The user can transfer one
   from another machine where the store already exists; no new code
   is required. Then re-run the seven `scripts/export_lean_parity_data.py`
   invocations to produce the CSVs, and re-run the verifier script.

   **OR**

2. **OANDA practice credentials in `.env`** (account id + token,
   practice-mode). With those, `scripts/rehydrate_oanda_h4_store.py`
   does the historical fetch, then the export script + verifier
   script complete the chain. The fetch is read-only (historical
   candles only) — no trading happens.

Either path is purely an environment / credential question; the
verifier code path itself is implemented and tested at fixture level
(85 verifier-side fixture tests pass in Sprint 001).

## Why the blocker is not silently worked around

- **No synthetic data.** The verifier reads only real OANDA practice
  H4 bid/ask candles, exactly as the LEAN-era plumbing was designed
  to. Synthetic fallback would be an immediate divergence and a
  loud-rejected design choice (see
  `scripts/export_lean_parity_data.py` — "Real data only. The export
  refuses synthetic candles").
- **No "partial" run.** The verifier script reports BLOCKED per
  pair and exits 2 if every pair is blocked; it does **not** silently
  produce a zero-trade summary. This is verified by the Sprint 001
  smoke test that ran on this same locally-absent state.
- **No tuning workaround.** Even if a partial slice of data appeared,
  the sprint rules forbid running the comparison and labelling a
  divergence as PASS without evidence — and a partial slice has no
  meaningful comparison against the seven-pair bespoke reference.

## Safety statement

- **No orders submitted.** This phase touched no broker, no exchange,
  no execution path.
- **No QC credentials requested / read / written / printed.**
- **No broker credentials printed.** The env-variable presence check
  redacts the right-hand side before any print.
- **No strategy approved.** `configs/approved_strategies.yaml`
  remains `approved: []`.
- **No `.env` staged.** `git status` is clean.
- **No SQLite store staged.** None exists locally.
- **No candle CSV staged.** None exists locally.
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.**
