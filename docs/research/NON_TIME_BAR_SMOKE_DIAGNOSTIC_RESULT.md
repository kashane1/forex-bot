# Non-Time Bar Smoke Diagnostic Result

**Sprint:** `infra-range-and-volatility-bars-001` · Phase 5
**Date:** 2026-05-29
**Status:** infrastructure smoke test. **No strategy evidence. No approval.**

A bounded, single-pair smoke run to confirm the diagnostic pipeline executes
end-to-end against local M1 without broker/API calls and emits only compact
summaries.

---

## Commands run

```
python scripts/generate_non_time_bar_diagnostics.py --bar-type range \
    --pairs USD_JPY --from 2023-01-01 --to 2023-03-01 --thresholds 10 --run-label smoke

python scripts/generate_non_time_bar_diagnostics.py --bar-type volatility --method abs_close \
    --pairs USD_JPY --from 2023-01-01 --to 2023-03-01 --thresholds 20 --run-label smoke
```

## Data source

Local Postgres research store, `market_data.candles`, `granularity = 'M1'`,
source = OANDA practice (read-only, local). **No broker/network calls** (the
script never imports the broker; reads go only through `PostgresCandleStore`).

- Pair: **USD_JPY** (pip = 0.01)
- Window: 2023-01-01 → 2023-03-01 (UTC)
- M1 source rows in window: **59,813**
- Price basis: mid

## Thresholds

- Range: **10 pip**
- Volatility (cumulative absolute close-to-close): **20 pip**

## Output summary

Compact JSON only, under `research/non_time_bars/smoke/`:

| file | committed? |
|------|-----------|
| `USD_JPY_range_summary.json` | yes (compact) |
| `USD_JPY_volatility_summary.json` | yes (compact) |
| `range_diagnostics_manifest.json` | yes (compact) |
| `volatility_diagnostics_manifest.json` | yes (compact) |
| `full_bars/*.csv` (only if `--save-full-bars`) | **no — gitignored** |

### Range bars — USD_JPY 10 pip
- **3,539 bars**; completion reasons near-balanced: 1,771 `range_up` / 1,768
  `range_down` (no directional artifact).
- Compression: **×16.9 vs M1**, **×1.13 vs M15 (approx)** — a 10-pip USD_JPY
  range bar is close to M15 cadence in early-2023.
- Source M1 rows per bar: median **8**, mean 16.9, max 359.
- Elapsed wall-clock per bar: median **7 min**, p75 18 min, max ~3,188 min
  (weekend-gap-spanning).
- Multi-threshold bars (one M1 candle crossing >1 threshold): **158** (~4.5%);
  `thresholds_crossed` tail extends to 16 (single volatile minute).
- Overshoot pips per bar: median **1.4**, mean 3.0.
- Session distribution (UTC-hour buckets): london_ny_overlap 1,061 · tokyo 934 ·
  london 844 · new_york 501 · rollover_late 199.

### Volatility bars — USD_JPY abs_close 20 pip
- **4,747 bars**; compression **×12.6 vs M1**.
- Source M1 rows per bar: median **11**.
- Same window; one data-quality note (weekend gaps).

## Warnings

- Both bar types report `"8 bar(s) span >24h (weekend/holiday gaps — expected
  in FX)"`. This is the intended weekend/holiday-gap signal, not a defect: FX
  M1 has structural gaps and an event-driven bar can straddle one. The
  `source_start_time`/`source_end_time` provenance makes such bars inspectable.

## Structural sanity assessment

Results look **structurally sane**:
- Range up/down completions are near-symmetric (no accidental directional bias).
- Compression ratios are monotone and physically plausible (range 10-pip ≈ M15
  frequency; volatility 20-pip slightly coarser than M1×12).
- The multi-threshold-crossing policy fires as designed on volatile minutes and
  is recorded, not hidden.
- Timestamps are UTC-normalised (psycopg returns timestamptz in session-local
  tz; the summary converts to UTC before session/weekday bucketing — a bug
  caught and fixed during this smoke).
- Chunk-boundary duplicate M1 rows from `iter_m1_chunks` are de-duplicated in the
  reader (the corpus itself is verified duplicate-free).

## Explicit scope note

This is **infrastructure validation only**. There is **no strategy evidence**
here, no backtest, no edge claim, and **nothing is approved**. The numbers
describe bar *geometry*, not profitability; pip thresholds are price-space, not
cost-net. `configs/approved_strategies.yaml` remains `approved: []` and
paper/demo/live remain blocked.

## Verification performed

- Script ran to completion with no broker/API import or call.
- Only compact JSON summaries/manifests are tracked; `git add -n` confirmed the
  four JSON files stage and nothing else.
- `--save-full-bars` writes `full_bars/USD_JPY_10pip.csv`; `git check-ignore`
  confirms it is ignored (not committed).
- `python scripts/scan_artifacts_for_secrets.py` → PASSED.
