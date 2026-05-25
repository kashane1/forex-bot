# Backtrader Real-Data Preflight — Phase 1 — BLOCKED

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-002-real-data-run`
**Phase:** 1 of `BACKTRADER_REAL_DATA_RUN_002_PLAN.md`
**`strategy_evidence: false`**

## 0. Verdict

**BLOCKED.** All four data-availability conditions defined in the
Phase 0 plan (`BACKTRADER_REAL_DATA_RUN_002_PLAN.md` §6) hold at
Phase 1 re-check. No new data has appeared since the previous sprint's
Phase 6 documented the same gap. The Backtrader-lane runner correctly
reports every requested CAMPAIGN_002 instrument as `BLOCKED`; no fake
trade was produced.

Phases 2 (real run), 3 (real comparison), and 4 (fidelity debugging)
**cannot proceed** in this worktree — they depend on local candle
CSVs that are absent. Phase 5 (CAMPAIGN_011) also cannot proceed
because its precondition is "CAMPAIGN_002 reached PASS or
TOLERABLE_DRIFT, or divergence is clearly documented" — none of which
is true when CAMPAIGN_002 produced no real run at all.

## 1. Data source intended

The committed Lean parity export bundle at
`research/lean_parity/exports/campaign_002_h4/` (provenance JSONs
committed, CSVs gitignored). The Backtrader-lane data adapter reads
the same CSV format the existing
`research/parity_verifier/` lane consumes
(`research/lean_parity/lean_h4_export_format.md`).

## 2. Generated files

**None.** Phase 1 generated no candle CSVs and no derived artefacts.
The runner's preflight `/tmp/bt_preflight_002/` artefacts were not
committed (and the gitignore rule `research/backtrader_lane/results/`
would have caught any committed run output anyway).

## 3. Gitignore status

Unchanged from sprint 001:

```
research/lean_parity/exports/**/*.csv          # bulk CAMPAIGN_002 CSVs
research/backtrader_lane/results/              # runner output trees
research/backtrader_lane/exports/**/*.csv      # any future BT-only exports
/data/                                         # SQLite databases
.env                                           # secrets
```

## 4. Instruments

The seven-pair CAMPAIGN_002 universe:

```
EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD
```

## 5. Row counts

Per the committed `*.provenance.json` sidecars (verbatim,
2020-01-01 → 2026-05-19):

```
AUD_USD  candles= 9931  request_hash=f80ebeddf05ab414
EUR_USD  candles= 9931  request_hash=aadc096b771961e6
GBP_USD  candles= 9931  request_hash=f8e36995228587e4
NZD_USD  candles= 9935  request_hash=84c1e5b0e9ad2b07
USD_CAD  candles= 9931  request_hash=279da4f7950b782b
USD_CHF  candles= 9931  request_hash=ee37f52e9aee64b2
USD_JPY  candles= 9932  request_hash=68c0df540212891c
                  ─────
total            69 522
```

These are the *expected* counts. The *actual* counts in this worktree
are zero because no CSV exists locally.

## 6. First / last timestamps

Per the committed sidecars, every pair covers
`2020-01-01T22:00:00+00:00` → `2026-05-19T(20–22):00:00+00:00`. 17:00-NY
aligned H4 candles.

## 7. Hash / provenance status

All seven `*_H4_lean.provenance.json` sidecars are committed and
carry a `data_sha256` (over the row-strings the exporter would write)
plus a `campaign_002_data_request_hash` (the bespoke engine's request
hash for the same instrument + granularity + window + source +
candle_count). When the CSVs are restored locally, the Phase 2 data
adapter's `compute_csv_sha256(...)` must reproduce each sidecar's
`data_sha256` exactly — that is the contractual check the runner
enforces in `strict` mode (default).

## 8. Gaps / warnings (this run)

| check | status |
|---|---|
| `research/lean_parity/exports/campaign_002_h4/*.csv` | **0 files present** (expected 7) |
| `data/oanda_h4_research.sqlite3` | **missing** (`scripts/rehydrate_oanda_h4_store.py --verify` → `BLOCKER: no H4 store`) |
| `data/campaign_002.sqlite3` | **missing** (legacy symlink path) |
| OANDA env vars (`OANDA_TOKEN`, `OANDA_API_TOKEN`, `OANDA_ACCOUNT_ID`) | **none set** (`env \| grep -c -i OANDA` → 0) |
| `.env` file | **not present** (only `.env.example` is committed) |
| any alternative committed bundle of real CAMPAIGN_002 H4 candles | **none** (the committed CSVs under `backtests/`, `research/d1_aggregation/`, and `research/edge_discovery/` are diagnostic outputs, D1AGG samples, or labelled **synthetic** — none are real CAMPAIGN_002 H4) |

## 9. The Backtrader-lane preflight, verbatim

```text
$ python scripts/run_backtrader_parity.py \
      --campaign CAMPAIGN_002 \
      --output /tmp/bt_preflight_002 \
      --dry-run

{
  "available_in_export_dir": [],
  "campaign_id": "CAMPAIGN_002",
  "dry_run": true,
  "expected_in_export_dir": ["AUD_USD", "EUR_USD", "GBP_USD", "NZD_USD",
                             "USD_CAD", "USD_CHF", "USD_JPY"],
  "export_dir": "research/lean_parity/exports/campaign_002_h4",
  "instruments_blocked": ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD",
                          "USD_CAD", "USD_CHF", "NZD_USD"],
  "instruments_requested": ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD",
                            "USD_CAD", "USD_CHF", "NZD_USD"],
  "instruments_runnable": []
}
```

The runner correctly recognised that every provenance sidecar is
present (`expected_in_export_dir` = all 7) but no CSV is on disk
(`available_in_export_dir` = empty). It did **not** fabricate a fill,
did not emit a fake trade, and did not consume any uncalibrated
synthetic data fallback.

## 10. Exact file(s) that must be restored to unblock

**Single load-bearing artefact:**

> `data/oanda_h4_research.sqlite3`

A rehydrated local OANDA-practice H4 candle store covering the
seven-pair CAMPAIGN_002 universe over 2020-01-01 → 2026-05-19. The
store is the only input
`scripts/export_lean_parity_data.py` knows how to read, and the
exporter is the only path the Backtrader lane has to a real CSV.

Two restore paths:

### Path A — restore from a previous backup (PREFERRED, no broker call)

If a previous version of this SQLite file exists on this machine (or
on a backup), simply copy it back to `data/oanda_h4_research.sqlite3`.

```bash
# Example (the actual path will vary by operator):
cp ~/backups/forex-bot/oanda_h4_research.sqlite3 data/oanda_h4_research.sqlite3

# Verify the store loads:
python scripts/rehydrate_oanda_h4_store.py --verify
```

Once verified, run the export:

```bash
python scripts/export_lean_parity_data.py \
    --db data/oanda_h4_research.sqlite3 \
    --out-dir research/lean_parity/exports/campaign_002_h4/
```

Then proceed to Phase 2 of the Phase 0 plan.

### Path B — fresh rehydration (requires OANDA practice credentials)

If no backup exists, rehydrate via OANDA practice (read-only — the
rehydration script does not place orders):

```bash
# 1. Populate .env with OANDA practice credentials, then:
python scripts/rehydrate_oanda_h4_store.py [--config configs/paper.yaml]

# 2. Verify:
python scripts/rehydrate_oanda_h4_store.py --verify

# 3. Export the seven CSVs:
python scripts/export_lean_parity_data.py \
    --db data/oanda_h4_research.sqlite3 \
    --out-dir research/lean_parity/exports/campaign_002_h4/

# 4. Proceed with Phase 2 of the Phase 0 plan.
```

This sprint did **not** attempt Path B — no OANDA credential was
present, no `.env` was authored, and the prompt's safety rule
"Do not read or print credentials" was honoured throughout.

## 11. Recommended-next within this sprint

Skip Phases 2, 3, 4, and 5 (all depend on Phase 1 unblock). Proceed
directly to Phase 6 (sprint summary) which:

1. records the BLOCKED state across all phases,
2. confirms no campaign verdict changed and the freeze gate is green,
3. recommends the same restore recipe to the human operator who picks
   up the next branch.

The Backtrader-lane code on this branch needs **no change** to
proceed once `data/oanda_h4_research.sqlite3` is restored — the
adapter, runner, comparison harness, and tests are all already
in place from sprint 001.

## 12. Required disclosure

This BLOCKED preflight cannot approve any strategy and does not
enable paper / demo / live trading. CAMPAIGN_002 remains **REJECT**.
CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain
rejected/null/research-only. CAMPAIGN_014 remains scaffold-only.
`configs/approved_strategies.yaml` remains `approved: []`. Paper /
demo / live remain blocked. `strategy_evidence: false`.
