# External Data Ingest Still Blocked

**Diagnostic only** — `strategy_evidence: false`

## Status

**BLOCKED** — `FRED_API_KEY` is not configured in the operator environment (checked without printing the key). No files exist under `data/external_features/`.

The full-window FRED fetch did **not** run. Prior fixture-window normalized data must **not** be treated as full-window real coverage.

## Local setup (no secrets)

1. Obtain a free FRED API key from https://fred.stlouisfed.org/docs/api/api_key.html
2. Create a local `.env` file (gitignored) in the repo root:

```bash
FRED_API_KEY=your-key-here
```

Or export in your shell:

```bash
export FRED_API_KEY='your-key-here'
```

3. Run the full-window pipeline:

```bash
python scripts/run_external_data_full_window_pipeline.py
```

Or fetch only:

```bash
python scripts/fetch_cross_asset_fred_features.py --observation-start 2018-01-01
```

4. Align to H4:

```bash
python scripts/align_cross_asset_features_to_h4.py
```

5. Re-run diagnostics:

```bash
python scripts/run_mtf_confluence_diagnostics.py \
  --skip-doc \
  --summary-name confluence_diagnostic_summary_full_window_cross_asset.json \
  --counts-name confluence_reason_code_counts_full_window_cross_asset.csv
```

## Alternative: manual CSV drop

See [`EXTERNAL_FEATURE_LOCAL_CSV_TEMPLATE.md`](EXTERNAL_FEATURE_LOCAL_CSV_TEMPLATE.md). Place CSVs in `data/external_features/` (gitignored).

## Target window

| parameter | value |
|---|---|
| H4 research | 2020-01-01 → 2026-05-24 UTC |
| Observation start | 2018-01-01 (warmup) |
| Observation end | 2026-05-24 |

## Expected outcome when unblocked

- `fred_fetch_status_real_window.json` → `overall_status: OK`
- `normalized_features.csv` → thousands of daily rows (not 7 fixture rows)
- `cross_asset_missing` in confluence diagnostics should **decrease materially**

## No strategy evidence

This blocker affects **data readiness only**. No strategy approved. No edge claims.
