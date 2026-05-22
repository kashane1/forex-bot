# Data Rehydration Runbook

**Date:** 2026-05-22 · **Branch:** `infra-data-parity-001` · Phase 5

How to recreate every local, non-committed research data store from
scratch — safely, reproducibly, and on a practice account only. None of
the data this runbook produces is committed; all of it is rebuilt from
here.

> **Practice only.** Every step uses the OANDA **practice** environment.
> No live credentials, no orders, no strategy campaigns, no approvals.
> The research freeze is never touched.

## 0. One-command path

```bash
# Preview the whole pipeline without running anything:
python scripts/prepare_local_research_data.py --dry-run

# Run it (rehydrate → verify → six-pair smoke → freeze gate):
python scripts/prepare_local_research_data.py

# Also export the Lean-parity data:
python scripts/prepare_local_research_data.py --with-lean-export
```

`prepare_local_research_data.py` refuses a live environment, prints no
credentials, and only ever invokes the data-prep / read-only scripts
below. The manual step-by-step path follows.

## 1. OANDA practice setup

1. Create a free OANDA **practice** account at <https://www.oanda.com/>.
2. In the account portal, generate a **practice** API token.
3. Copy `.env.example` to a local `.env` (gitignored) and fill in:

   | env var | value |
   |---|---|
   | `OANDA_ACCOUNT_ID_PRACTICE` | your practice account id |
   | `OANDA_ACCESS_TOKEN_PRACTICE` | your practice API token |

   Leave `OANDA_ENVIRONMENT` unset or `practice`. **Never** set the
   `*_LIVE` variables for this work.

4. Confirm: `bot doctor --config configs/paper.yaml` reports broker
   credentials present.

## 2. Output paths (all gitignored — never committed)

| path | contents |
|---|---|
| `data/oanda_h4_research.sqlite3` | the real-OANDA H4 candle store |
| `research/lean_parity/exports/campaign_002_h4/*.csv` | Lean-parity candle exports |
| `logs/` | runtime logs |

`data/` and `*.sqlite3` are gitignored; the Lean export CSVs are
gitignored via `research/lean_parity/exports/**/*.csv`. Committed
artifacts are scripts, docs, small manifests, and provenance JSONs only.

## 3. Rehydrate the H4 data store

```bash
python scripts/rehydrate_oanda_h4_store.py
```

Fetches real OANDA practice H4 bid/ask candles for the six majors
(EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF), 2020-01-01 →
2026-05-20, completed candles only, into `data/oanda_h4_research.sqlite3`.
Details: `docs/research/OANDA_H4_DATA_REHYDRATION.md`.

## 4. Verify the H4 hashes

```bash
python scripts/rehydrate_oanda_h4_store.py --verify
```

Read-only (no credentials needed). Prints, per pair, the candle count,
coverage window, and a fetch-order-independent `content_hash`. Provenance
(`raw_sha256`, `normalized_sha256`) is also in the store's `data_sources`
table:

```sql
SELECT instrument, candles_written, raw_sha256, normalized_sha256
FROM data_sources WHERE campaign = 'h4_research_rehydration';
```

## 5. Aggregate D1AGG and run the six-pair smoke

```bash
python scripts/smoke_d1agg_next_open.py
```

Aggregates H4 → D1AGG for all six majors and runs the diagnostic
D1AGG + next-bar-open smoke, writing
`backtests/diagnostics/d1agg_next_open_six_pair_smoke.md`. **Diagnostic
only** — no strategy verdict, no recommendation, no approval. A
standalone D1AGG CSV can also be produced with
`scripts/aggregate_h4_to_d1.py`.

## 6. Export Lean parity data

```bash
python scripts/export_lean_parity_data.py \
    --db data/oanda_h4_research.sqlite3 --instrument EUR_USD \
    --from 2020-01-01 --to 2026-05-20
```

Writes the Lean custom-data CSV and a provenance sidecar into
`research/lean_parity/exports/campaign_002_h4/`. See
`docs/research/LEAN_PARITY_EXECUTION_GUIDE.md` and that bundle's
`EXPORT_MANIFEST.md`.

## 7. Validate the archive and the research freeze

```bash
python scripts/validate_research_archive.py
python scripts/check_research_freeze.py
```

Both must exit 0. The freeze gate confirms the registry is empty, the
archive is consistent, no artifact looks credential-shaped, and the
loops still refuse. Run these after any data-prep work.

## 8. Cleanup

The data stores are safe to delete — they are fully rebuilt by this
runbook:

```bash
rm -f data/oanda_h4_research.sqlite3 data/oanda_h4_research.sqlite3-*
rm -rf research/lean_parity/exports/campaign_002_h4/*.csv
```

Do **not** delete committed scripts, docs, manifests, or provenance
JSONs. Never commit a `data/*.sqlite3` store or a candle-export CSV.

## 9. Credential safety rules

- **Practice only.** Never use `OANDA_*_LIVE` variables for this work.
  `scripts/rehydrate_oanda_h4_store.py` and
  `scripts/prepare_local_research_data.py` both refuse a live or
  ambiguous environment.
- **Never commit `.env`.** It is gitignored (`.env`, `.env.*`). Keep
  the token there, never in a config file or a script.
- **No credential ever appears in output.** The scripts print redacted
  account ids at most, and never a token. Committed artifacts carry
  hashes and counts only.
- **Verify before committing.** `git diff --staged` must never show a
  `.sqlite3`, a `.env`, or a candle-export CSV. The credential scan in
  `scripts/validate_research_archive.py` covers committed artifacts.
- This runbook prepares **data**. It never trades, never enables a
  loop, and never approves a strategy.
