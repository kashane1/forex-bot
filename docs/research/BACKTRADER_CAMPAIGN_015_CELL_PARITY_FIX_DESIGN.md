# CAMPAIGN_015 Cell Parity Fix Design — fold 1 × AUD_USD

**Branch:** `infra-backtrader-campaign-015-cell-parity-drilldown-001`
**Primary root cause:** `CSV_SQLITE_DATA_MISMATCH` (duplicate SQLite timestamps vs deduped CSV)
**Date:** 2026-05-26

> No fix implemented in this sprint. Design only.

## Proposed fix (small, proven scope)

**Normalize candle loads to one row per timestamp before any strategy logic runs.**

### Option A (preferred): dedupe at SQLite read boundary

In `CandleRepo.list` consumer paths used by CAMPAIGN_015 bespoke runs (or in `CandleFrame.from_candles`), apply:

```python
if not df.index.is_unique:
    df = df[~df.index.duplicated(keep="last")]
```

`keep="last"` matches the CSV export dedupe policy used by `load_candles`.

### Option B: repair SQLite source data

Remove duplicate `(instrument, granularity, time)` rows from `campaign_002.sqlite3` via a one-off migration. Higher risk; requires data-integrity verification across all campaigns.

## Tests required

1. Unit: duplicated timestamp frame dedupes to unique index before strategy warmup.
2. Integration: fold 1 × AUD_USD bespoke re-run produces **fewer** “missing signal” bars vs BT on the same deduped timeline (trade count should move toward BT, not necessarily match yet).
3. Regression: existing CAMPAIGN_015 rehydrate trade CSVs for fold 1 AUD_USD change — **expected**; document as evidence rerun.

## Lane impact

| lane | impact |
|---|---|
| Backtrader | **None** (already deduped CSV) |
| Bespoke / rehydrate | **Yes** — signal path changes when duplicates removed |

## Evidence rerun

**Required** after fix:

- `walk_forward_rehydrate` bespoke fold trades
- `compare_campaign_015_fold_windows.py` parity report
- Do **not** rerun until dedupe is merged and tested

## Not in scope yet

- `strict_test_window=True` for BT (addresses 3/13 out-of-window BT trades only)
- RiskEngine rejection mix tuning
- CAMPAIGN_015 gate or approval changes

## Verdict

Root cause is **proven** on fold 1 × AUD_USD. Fix is **small and isolated** but touches bespoke data ingestion — implement in a follow-up infra sprint, not this drilldown branch, until dedupe tests land.
