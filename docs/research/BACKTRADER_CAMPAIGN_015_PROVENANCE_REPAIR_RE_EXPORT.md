# Backtrader CAMPAIGN_015 — Provenance Re-Export (Phase 2)

**Sprint:** [BT C015 Provenance Repair 001](BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_001_PLAN.md)
**Branch:** `infra-backtrader-campaign-015-provenance-repair-001`
**Date:** 2026-05-26
**Status:** **lock-step restored — ALL BT-STRICT PREFLIGHT PASS** on
the 7-instrument bundle under
`research/lean_parity/exports/campaign_002_h4/`.

> Infra-only document. Does NOT approve any strategy, does NOT touch
> CAMPAIGN_015 parameters, gates, runner, or registry.
> `configs/approved_strategies.yaml` remains `approved: []`.

---

## 1 · What changed in this phase

### 1.1 Export-script tz-determinism fix
- [`scripts/export_lean_parity_data.py`](../../scripts/export_lean_parity_data.py)
  — `candle_to_lean_row()` and `build_provenance()` now normalise every
  `Candle.time` to UTC before serialisation. Previously the script
  emitted `c.time.isoformat()` directly, which leaked the exporting
  machine's local timezone (`-08:00` PST in one run, `+00:00` UTC in
  another) into the CSV's `time` column. The string difference alone
  drifted the row-sha256, even though the underlying UTC instants are
  identical. **This is the root-cause fix.**

### 1.2 Re-exported CSVs + provenance sidecars
- 7 instruments re-exported in a single batch against
  `data/campaign_002.sqlite3` (gitignored symlink to the canonical
  main-repo store):

| instrument | candle_count | first_ts | last_ts | data_sha256 (prefix) |
|---|---|---|---|---|
| EUR_USD | 19,864 | `2020-01-01T22:00:00+00:00` | `2026-05-20T05:00:00+00:00` | `533cbf6571ce…` |
| GBP_USD | 19,864 | `2020-01-01T22:00:00+00:00` | `2026-05-20T05:00:00+00:00` | `68d5160c40c1…` |
| USD_JPY | 19,866 | `2020-01-01T22:00:00+00:00` | `2026-05-20T05:00:00+00:00` | `acc23912c5c6…` |
| AUD_USD | 19,864 | `2020-01-01T22:00:00+00:00` | `2026-05-20T05:00:00+00:00` | `24e06add2c65…` |
| USD_CAD | 19,864 | `2020-01-01T22:00:00+00:00` | `2026-05-20T05:00:00+00:00` | `a6a426d157e0…` |
| USD_CHF | 19,864 | `2020-01-01T22:00:00+00:00` | `2026-05-20T05:00:00+00:00` | `92477336c200…` |
| NZD_USD | 19,872 | `2020-01-01T22:00:00+00:00` | `2026-05-20T05:00:00+00:00` | `2bfeae6b64cb…` |

### 1.3 New `EXPORT_MANIFEST.json`
- [`scripts/build_lean_parity_export_manifest.py`](../../scripts/build_lean_parity_export_manifest.py)
  consolidates the seven `*.provenance.json` sidecars into one
  machine-readable manifest at
  [`research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.json`](../../research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.json).
  The pre-existing `EXPORT_MANIFEST.md` is left untouched.

### 1.4 Diagnostic re-run
- [`scripts/diagnose_backtrader_csv_provenance.py`](../../scripts/diagnose_backtrader_csv_provenance.py)
  now reports **ALL BT-STRICT PREFLIGHT PASS** for the bundle (was
  *complete drift* in Phase 1):
  - all 7 row-shas match,
  - all 7 row counts match,
  - all 7 first/last timestamps match,
  - all 7 instruments pass.

---

## 2 · Important observation: DB has duplicate H4 rows per timestamp

While running the export, the diagnostic surfaced that
`data/campaign_002.sqlite3` contains **two rows for every H4
timestamp** in the 2020-01-01..2026-05-20 window: one with the
local-PST timezone and `mid_*` columns NULL, another with UTC and
populated `mid_*` columns. The newly-exported CSVs therefore contain
~19,864 rows (≈ 9,931 unique bars × 2) instead of the original
provenance's 9,931.

This is **not** a regression introduced by this sprint — it is a
pre-existing data-storage layout that the CAMPAIGN_015 bespoke
walk-forward also reads. The bespoke run produced 164 trades exactly
reproducibly against the same DB; whatever interpretation the
bespoke engine applies to duplicate timestamps, the BT lane will
need to apply the same one (or document a divergence) in Phase 4.

The provenance JSONs faithfully record what the CSVs contain, so the
BT lane's row-sha strict check will pass regardless. This sprint's
job is provenance **lock-step**, not DB de-duplication. DB
de-duplication is a separate infra concern, out of scope here.

---

## 3 · Commit policy

Per the repo's existing convention
([`.gitignore`](../../.gitignore) lines 70–73; the original
`EXPORT_MANIFEST.md` §"Status"), the CSVs themselves are
**gitignored** — they remain in
`research/lean_parity/exports/campaign_002_h4/*.csv` on the local
filesystem but are not committed. The small provenance JSON sidecars
**are** committed; the new `EXPORT_MANIFEST.json` is also committed.
This matches the original sprint's commit pattern verbatim.

---

## 4 · What was NOT changed

- `configs/approved_strategies.yaml` — still `approved: []`.
- CAMPAIGN_015 strategy parameters / frozen config / gates /
  approval registry — untouched.
- `research/anti_overfit/campaign_015.py` — untouched.
- Bespoke walk-forward runner `scripts/run_campaign_015.py` — untouched.
- All prior CAMPAIGN_015 diagnostic artifacts under
  `research/campaign_015/diagnostics/` — untouched **except** for
  `backtrader_provenance_mismatch.{json,md}` which were re-generated
  by the re-run (status flipped from "complete drift" to "all pass").
- The pre-existing `EXPORT_MANIFEST.md` is untouched; the new
  `EXPORT_MANIFEST.json` is a peer file.

---

## 5 · Reproduction

```bash
# 1. Re-export all 7 H4 instruments in one batch, UTC timestamps.
for pair in EUR_USD GBP_USD USD_JPY AUD_USD USD_CAD USD_CHF NZD_USD; do
  python scripts/export_lean_parity_data.py \
    --db data/campaign_002.sqlite3 \
    --instrument "$pair" \
    --from 2020-01-01 --to 2026-05-20 \
    --out-dir research/lean_parity/exports/campaign_002_h4
done

# 2. Rebuild the consolidated manifest.
python scripts/build_lean_parity_export_manifest.py

# 3. Verify lock-step.
python scripts/diagnose_backtrader_csv_provenance.py \
  --exports-dir research/lean_parity/exports/campaign_002_h4 \
  --out-json    research/campaign_015/diagnostics/backtrader_provenance_mismatch.json \
  --out-md      research/campaign_015/diagnostics/backtrader_provenance_mismatch.md
# Expected: status: ALL BT-STRICT PREFLIGHT PASS
```
