# Infrastructure Free / Local Parity Verifier Sprint 003 — Plan

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-003-with-data`
**Base commit:** `387e51a` (HEAD of `infra-free-local-parity-verifier-002-full-data-run`)

The guarded OANDA-practice historical rehydrate + export + full-data
verifier sprint. The previous sprint (002) ended BLOCKED because no
local SQLite store and no OANDA practice credentials were available.
This sprint attempts the unblock under strict safety rules.

> `strategy_evidence: false`. This sprint cannot approve a strategy.
> CAMPAIGN_002 remains REJECT. Paper / demo / live remain blocked.
> `configs/approved_strategies.yaml` stays empty.

## 1. Purpose

- Detect whether OANDA practice credentials are configured locally.
- If they are: run the existing `scripts/rehydrate_oanda_h4_store.py`
  to fetch historical H4 candles (read-only `GET .../candles`),
  re-export the seven CSVs via `scripts/export_lean_parity_data.py`,
  and run the free / local independent verifier against the
  no-RiskEngine bespoke reference (1,647 trades).
- If they are not: stop and document the BLOCKER honestly. Do not
  fabricate data. Do not run any network call.

## 2. Non-goals

- Not a strategy approval. CAMPAIGN_002 stays REJECT regardless.
- Not a CAMPAIGN_002 re-run — the bespoke engine is not invoked.
- Not a tuning loop.
- Not a paper / demo / live trigger.
- Not a broker order — no order endpoint is touched.
- Not a QuantConnect / LEAN reopening.

## 3. Safety invariants

Apply at every phase, every commit:

1. `configs/approved_strategies.yaml` stays `approved: []`.
2. CAMPAIGN_002 remains REJECT. No campaign re-run.
3. Paper / demo loops keep refusing; no `live-loop` command exists.
4. No QC credential is requested, read, written, or echoed.
5. OANDA practice credentials are used **only** for historical
   `GET .../candles` calls. No order placement, no live mode, no
   account / trade mutation endpoint.
6. No credential value is printed. Presence checks only.
7. No `.env`, `*.sqlite3`, candle CSV, or bulky verifier output gets
   staged or committed.
8. No new external dependency.
9. The bespoke engine under `src/forex_bot/` is not modified to match
   the verifier.
10. Validators must pass on every commit: pytest, ruff, archive
    validator, freeze checker, secret scanner.

## 4. Credential-presence status (no values printed)

Inspected 2026-05-22 on this branch, **no secrets read or echoed**:

| check | result |
|---|---|
| `.env` file in repo root | **absent** (only `.env.example` present) |
| `$OANDA_API_TOKEN` set in shell | **unset** |
| `$OANDA_ACCOUNT_ID` set in shell | **unset** |
| `$OANDA_API_KEY` set in shell | **unset** |
| `$OANDA_ENVIRONMENT` set in shell | **unset** |
| `$OANDA_PRACTICE_API_TOKEN` set in shell | **unset** |
| `$OANDA_PRACTICE_ACCOUNT_ID` set in shell | **unset** |

No credential value of any kind exists in this environment. The check
used a presence-only Python one-liner that prints `SET` or `unset`
for each variable name — the value is never read into Python's
output stream.

`scripts/rehydrate_oanda_h4_store.py --verify` (the read-only
verification mode that does not need credentials) reports:

```text
BLOCKER: no H4 store at data/oanda_h4_research.sqlite3. Run a
rehydration fetch first (requires OANDA practice credentials).
```

## 5. Scripts inspected and the historical-only confirmation

| script | path | role | order endpoints? |
|---|---|---|---|
| Rehydrate | [`scripts/rehydrate_oanda_h4_store.py`](../../scripts/rehydrate_oanda_h4_store.py) | Fetches H4 candles via OANDA `GET .../candles`; writes `data/oanda_h4_research.sqlite3` | **No** — module-level comment reads "(`GET .../candles`). No synthetic data. No order was submitted." Guards on practice-only env. |
| Export | [`scripts/export_lean_parity_data.py`](../../scripts/export_lean_parity_data.py) | Reads from the local SQLite store, writes a Lean-format CSV + provenance JSON per pair | **No** — pure local-SQLite read. Refuses synthetic candles. |
| Verifier | [`scripts/run_free_local_parity_verifier.py`](../../scripts/run_free_local_parity_verifier.py) | Reads exported CSVs, runs the in-tree event-loop verifier, writes summary + trades | **No** — no network, no broker. |

Confirmed by grep: only `candles` endpoints are referenced; no
`/v3/orders`, `/v3/trades`, or position-management calls anywhere in
either rehydrate or export.

## 6. Target pairs & timeframe (confirmed)

Seven CAMPAIGN_002 H4 instruments, full window 2020-01-01 → 2026-05-20:

EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD.

This matches the no-RiskEngine bespoke reference scope exactly
(`research/lean_parity/campaign_002_h4_bespoke_reference.json`):

- `parity_target`: `"CAMPAIGN_002 H4 trend_following baseline"`
- `risk_engine_used`: `false`
- `fill_timing`: `"signal_bar_close"`
- `window`: `["2020-01-01", "2026-05-20"]`
- `config_hash`: `d536a9b06818197f9915de6224e0b8ae58e77abe2c6f3c19426338646fb077bf`
- `strategy_evidence`: `false`
- `total_trades`: `1647`
- 7 pairs.

The 1,032-trade with-RiskEngine reference is **not** the target.

## 7. Expected plan path given the credential state

Because no credentials are configured and no SQLite store exists,
Phases 1 → 4 will be **BLOCKED honestly** with no fetch attempted.
Per the sprint rules ("If credentials are absent, stop and document
the blocker"), the verifier sprint cannot complete an end-to-end
data flow on this branch.

The verifier script (Sprint 001/002) already handles the absent-CSV
state cleanly: 7 × BLOCKED messages, exit code 2, no crash, no
fabricated data. The harness runs through that path again this
sprint to confirm the implementation continues to behave correctly
in a no-data environment.

## 8. Planned commands (recorded for the record)

These are the commands the sprint **would** run if credentials were
present. They are **not** invoked on this branch because the
prerequisite is missing.

```bash
# 1. Verify-only check (read-only, no creds needed) — DOES run.
python scripts/rehydrate_oanda_h4_store.py --verify

# 2. Rehydrate (would require OANDA practice creds) — NOT run.
python scripts/rehydrate_oanda_h4_store.py --config configs/paper.yaml

# 3. Export 7 CSVs from the local store — NOT run.
for inst in EUR_USD GBP_USD USD_JPY AUD_USD USD_CAD USD_CHF NZD_USD; do
  python scripts/export_lean_parity_data.py \
    --db data/oanda_h4_research.sqlite3 \
    --instrument "$inst" --from 2020-01-01 --to 2026-05-20
done

# 4. Verifier — runs against absent CSVs (reports BLOCKED).
python scripts/run_free_local_parity_verifier.py \
  --output research/parity_verifier/results/campaign_002_h4_full_data/

# 5. Comparison harness against the 1,647-trade no-RiskEngine reference
#    — invoked programmatically via compare.blocked_report; produces
#    a structurally identical BLOCKED report.
```

## 9. Expected generated local files (not committed)

If a future invocation in a creds-configured environment runs this
plan end-to-end, the local files produced will be:

| path | committed? | rationale |
|---|---|---|
| `data/oanda_h4_research.sqlite3` | no (gitignored) | bulk SQLite store |
| `research/lean_parity/exports/campaign_002_h4/*_H4_lean.csv` (× 7) | no (gitignored) | bulk candle data |
| `research/lean_parity/exports/campaign_002_h4/*_H4_lean.provenance.json` (× 7) | yes (already in repo) | small hash files |
| `research/parity_verifier/results/campaign_002_h4_full_data/parity_summary.json` | only if small and useful | verifier summary |
| `research/parity_verifier/results/campaign_002_h4_full_data/parity_summary.md` | only if small and useful | human-readable |
| `research/parity_verifier/results/campaign_002_h4_full_data/trades.csv` | no (gitignored) | bulk trade list |

On this branch, no `data/oanda_h4_research.sqlite3` is created, no
CSV is exported, and the verifier produces only its BLOCKED summary
(written outside the repo to `/tmp/parity_verifier_003_run/`).

## 10. Explicit statement on approval

This sprint cannot and does not approve a strategy. It does not edit
`configs/approved_strategies.yaml`, the bespoke engine, the
CAMPAIGN_002 rules, the campaign reports, or `EVIDENCE_MANIFEST.json`
campaign verdicts. Its outputs are diagnostic only — every committed
verifier artifact carries `strategy_evidence: false` and the
comparison-report model rejects construction with the rail flipped.

## 11. Cross-links

- Retirement: [`QUANTCONNECT_LEAN_RETIREMENT_DECISION.md`](QUANTCONNECT_LEAN_RETIREMENT_DECISION.md)
- Original design: [`FREE_LOCAL_PARITY_VERIFIER_PLAN.md`](FREE_LOCAL_PARITY_VERIFIER_PLAN.md)
- Sprint 001 (implementation): [`INFRA_FREE_LOCAL_PARITY_VERIFIER_001_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_001_SUMMARY.md)
- Sprint 002 (first attempted unblock): [`INFRA_FREE_LOCAL_PARITY_VERIFIER_002_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_002_SUMMARY.md)
- Headline status: [`FREE_LOCAL_PARITY_VERIFIER_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_STATUS.md)
- Bespoke no-RiskEngine reference: `research/lean_parity/campaign_002_h4_bespoke_reference.json` (1,647 trades)
- Rehydrate script: [`scripts/rehydrate_oanda_h4_store.py`](../../scripts/rehydrate_oanda_h4_store.py)
- Export script: [`scripts/export_lean_parity_data.py`](../../scripts/export_lean_parity_data.py)
- Verifier script: [`scripts/run_free_local_parity_verifier.py`](../../scripts/run_free_local_parity_verifier.py)
