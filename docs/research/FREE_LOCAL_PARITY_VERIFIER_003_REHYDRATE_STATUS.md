# Free / Local Parity Verifier — Sprint-003 Rehydrate Status

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-003-with-data`
**Phase:** 1 · `strategy_evidence: false`

Whether the `data/oanda_h4_research.sqlite3` H4 research store was
created or refreshed via the existing
`scripts/rehydrate_oanda_h4_store.py` historical-fetch script.
**Status: BLOCKED — no fetch attempted, no credentials present.**

> No strategy is approved. CAMPAIGN_002 remains REJECT. Paper /
> demo / live remain blocked. **No orders were submitted.** No
> OANDA endpoint other than `--verify` (which makes no API call) was
> exercised.

## OANDA practice historical fetch used?

**No.** No call was made to any OANDA endpoint. The credential
presence check confirmed no `.env` file and no `OANDA_*` environment
variable in the shell. Per the sprint rules ("If credentials are
absent, stop and document the blocker. Do not fabricate data."), no
fetch was attempted.

The only invocation of the rehydrate script was the read-only
`--verify` mode, which makes **no** API call and requires no
credentials:

```bash
python scripts/rehydrate_oanda_h4_store.py --verify
# -> BLOCKER: no H4 store at data/oanda_h4_research.sqlite3. Run a
#    rehydration fetch first (requires OANDA practice credentials).
```

## Commands run (no secrets)

```bash
# Credential-presence check, values are never read into stdout.
python -c "import os; vars=['OANDA_API_TOKEN','OANDA_ACCOUNT_ID', \
                            'OANDA_API_KEY','OANDA_ENVIRONMENT', \
                            'OANDA_PRACTICE_API_TOKEN', \
                            'OANDA_PRACTICE_ACCOUNT_ID']; \
   [print(f'{v}: {\"SET\" if os.environ.get(v) else \"unset\"}') for v in vars]"
# -> all six lines print 'unset'.

ls -la .env*
# -> .env.example only; no .env

python scripts/rehydrate_oanda_h4_store.py --verify
# -> BLOCKER: no H4 store at data/oanda_h4_research.sqlite3.

ls data/
# -> data/.gitkeep only.
```

No credential value entered stdout, a log, or a file.

## Pairs / timeframe / row counts / timestamp ranges

**Not applicable** — no rehydrate was attempted. The seven expected
pairs and the full 2020-01-01 → 2026-05-20 H4 window remain the
target the next-attempt sprint must produce, matching the bespoke
reference scope.

## Generated files not committed

**None.** Nothing was generated this phase. The data directory is
unchanged (`data/.gitkeep` only), the SQLite store is not created,
and no candle CSV exists.

## Blockers

1. **No OANDA practice credentials configured.** `.env` is absent;
   no `OANDA_*` env var is set in the shell.

   **Unblock options for a future invocation:**
   - Configure OANDA practice credentials in a `.env` file in the
     repo root (account id + token, practice-mode only) and re-run
     this sprint. The rehydrate script is historical-only
     (`GET .../candles`); no order is placed.
   - Alternatively, copy a pre-existing `data/oanda_h4_research.sqlite3`
     from another machine the user controls. The export and verifier
     steps then proceed with no OANDA touch at all.

2. **`scripts/rehydrate_oanda_h4_store.py` would refuse to run**
   without practice credentials anyway: the docstring states "the
   practice-data environment guard must pass; a live environment, an
   ambiguous one, or missing credentials all abort the fetch."

## Safety statement

- **No orders submitted.** The rehydrate script has no order
  endpoints; even if it had been executed, it could not place a trade.
- **No OANDA endpoint contacted.** Only the read-only `--verify`
  mode of the script ran, and that mode makes no API call.
- **No QC credentials requested / read / printed.** No QuantConnect
  / LEAN action of any kind.
- **No broker credentials printed.** The env-presence check used a
  Python one-liner that prints `SET` or `unset` per variable name;
  the value never entered the output stream.
- **No `.env` staged.** No `.env` file exists locally.
- **No SQLite store staged.** None exists.
- **No candle CSV staged.** None exists.
- **No strategy approved.** `configs/approved_strategies.yaml`
  remains `approved: []`.
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.**
