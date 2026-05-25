# Backtrader Secondary Lane 003 — Real Data Run — Plan

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-003-real-data-run`
**Sprint kind:** infrastructure / parity (NOT a strategy campaign)
**`strategy_evidence: false`**

## 0. Headline

The H4 source SQLite that Sprint 002 documented as the single
load-bearing blocker **was found locally** — in the main repository
working directory (not in this worktree's isolated `data/`). The
worktree's `data/` is gitignored and starts empty for each new
worktree (per `.gitignore` line 60: `/data/`), which is why Sprint 002
saw it as absent.

```
/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3   (115 MB, real)
```

This file contains all seven CAMPAIGN_002 H4 candle series matching
the committed provenance sidecars row-for-row:

```
AUD_USD 9931  EUR_USD 9931  GBP_USD 9931
NZD_USD 9935  USD_CAD 9931  USD_CHF 9931  USD_JPY 9932
                                                  ─────
                                            total 69 522
```

Source label `oanda-practice`. Time window
`2020-01-01T22:00:00+00:00 → 2026-05-19T21:00:00+00:00`. The seven
provenance sidecars' candle counts match exactly.

The Phase 1 path is therefore **B (regenerate CSVs from existing
local SQLite)** — no OANDA API call, no credentials read, no broker
contact, no new fetch.

## 1. Files found / missing

| artefact | path | state |
|---|---|---|
| H4 source SQLite | `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` | **PRESENT** (115 MB, 7 pairs, 69 522 candles, source `oanda-practice`) |
| campaign workhorse SQLite | `/Users/kashane/dev/forex-bot/data/campaign.sqlite3` | present (123 MB, not used by this sprint) |
| worktree `data/` | `data/` | **empty** except `bot.sqlite3` (167 KB operational) — gitignored |
| seven-pair H4 CSVs | `research/lean_parity/exports/campaign_002_h4/*.csv` | **absent** (gitignored bulk; to be regenerated to the worktree from the SQLite above) |
| seven-pair provenance JSONs | `research/lean_parity/exports/campaign_002_h4/*_H4_lean.provenance.json` | **committed** (7/7); each carries the expected `data_sha256` + `campaign_002_data_request_hash` |
| `data/oanda_h4_research.sqlite3` | (any worktree or main repo) | **absent under this exact name**, but the equivalent data lives in `campaign_002.sqlite3` |
| bespoke no-RiskEngine reference | `research/lean_parity/campaign_002_h4_bespoke_reference.json` | **committed** (1 647 trades, per-pair metrics) |
| `.env` | `.env` | **absent** (only `.env.example` is committed) |
| OANDA env vars | environment | **none set** (`env \| grep -c -i OANDA` → 0) |

## 2. Chosen restore path

**Path B from `BACKTRADER_REAL_DATA_RUN_002_PLAN.md` §2** — regenerate
the seven CSVs from the existing local SQLite. No fresh OANDA fetch.

The export script is `scripts/export_lean_parity_data.py`, which is
already in the repo and already understands the schema in
`campaign_002.sqlite3`. It accepts `--db` and `--out-dir` flags, so
we point it at the main-repo SQLite (read-only) and write CSVs into
this worktree's gitignored
`research/lean_parity/exports/campaign_002_h4/`.

CSVs are gitignored (`.gitignore` line 72:
`research/lean_parity/exports/**/*.csv`) and will not be committed.

## 3. Whether any API call is needed

**No.** The local SQLite at `data/campaign_002.sqlite3` (in the main
repo dir) already contains the seven-pair H4 candles. No OANDA call,
no broker contact, no credential read. Path C from
`BACKTRADER_REAL_DATA_RUN_002_PLAN.md` is **not** taken.

## 4. Exact next commands

Phase 1 — regenerate CSVs (one per pair):

```bash
for pair in EUR_USD GBP_USD USD_JPY AUD_USD USD_CAD USD_CHF NZD_USD; do
  python scripts/export_lean_parity_data.py \
      --db /Users/kashane/dev/forex-bot/data/campaign_002.sqlite3 \
      --instrument "$pair" \
      --from 2020-01-01 \
      --to 2026-05-20 \
      --out-dir research/lean_parity/exports/campaign_002_h4/
done
```

Phase 2 — real CAMPAIGN_002 run:

```bash
python scripts/run_backtrader_parity.py \
    --campaign CAMPAIGN_002 \
    --output research/backtrader_lane/results/campaign_002_real_data_003/
```

Phase 3 — comparison:

```bash
python scripts/compare_backtrader_parity.py \
    --campaign CAMPAIGN_002 \
    --backtrader-results research/backtrader_lane/results/campaign_002_real_data_003/ \
    --bespoke-reference research/lean_parity/campaign_002_h4_bespoke_reference.json \
    --output research/backtrader_lane/results/campaign_002_real_data_003/comparison/
```

## 5. Non-goals (binding, carried over)

1. No strategy approval. `configs/approved_strategies.yaml` stays
   `approved: []`.
2. No verdict mutation. CAMPAIGN_002 stays REJECT.
3. No bespoke-engine edit.
4. No OANDA API call (path B uses existing local SQLite).
5. No LEAN / QuantConnect.
6. No commit of `.env`, SQLite, bulk CSVs, raw Backtrader outputs.
7. No paper / demo / live enablement.

## 6. Safety invariants (verified at Phase 0)

```text
pytest tests/unit/backtrader_lane    → 75 passed
ruff check src tests scripts research/backtrader_lane → All checks passed
check_research_freeze.py             → ALL CHECKS PASSED
validate_research_archive.py         → ALL CHECKS PASSED
scan_artifacts_for_secrets.py        → PASSED
configs/approved_strategies.yaml     → approved: []
```

`strategy_evidence: false`. CAMPAIGN_002 stays REJECT regardless of
the comparison outcome.
