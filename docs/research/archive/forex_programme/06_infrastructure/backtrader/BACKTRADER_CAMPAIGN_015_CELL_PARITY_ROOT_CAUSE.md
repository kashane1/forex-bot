# CAMPAIGN_015 Cell Parity Root Cause — fold 1 × AUD_USD

**Branch:** `infra-backtrader-campaign-015-cell-parity-drilldown-001`
**Cell:** fold 1 / AUD_USD
**Date:** 2026-05-26

> Diagnostic-only. Does **not** approve any strategy.

## Headline

| metric | value |
|---|---:|
| Bespoke accepted | 2 |
| BT parity accepted | 13 |
| Delta | +11 |
| First BT-only entry | `2022-05-06T17:00:00+00:00` long |

## Primary root cause

**`CSV_SQLITE_DATA_MISMATCH`**

The Backtrader lane reads **deduped** Lean CSV exports. The bespoke rehydrate lane reads **SQLite** candles that contain **duplicate timestamps** (2× row count: 2328 rows, 1162 duplicates for this fold load window).

Evidence:

- SQLite fold-1 AUD_USD load: `2328` rows, `index.is_unique == False`, `1162` duplicated timestamps (each H4 bar appears twice).
- CSV export for the same instrument/window is deduped (`load_candles` enforces unique index).
- At the first BT-only signal bar (`2022-05-06T13:00:00+00:00`):
  - **CSV (deduped):** strategy emits `long`; RiskEngine approves at next-bar-open fill.
  - **SQLite (duplicated window):** strategy emits `None` on the same nominal timestamp when replayed with the duplicated frame the bespoke engine uses.
- Isolated probe on deduped SQLite (`keep='last'`) **does** emit `long`, confirming duplicates — not subtly different OHLC — are what suppress the bespoke signal.

BT therefore accepts trades on bars where bespoke never sees a valid CAMPAIGN_015 candidate because indicator/range state is corrupted by duplicated bars.

## Secondary labels

**`TIMESTAMP_SESSION_GATE_MISMATCH`** (secondary, minor for this cell)

- Fold 1 test window: `2022-06-19` .. `2022-12-15`.
- **3 of 13** BT trades have `entry_time` **before** `test_start` (including the first BT-only trade on `2022-05-06`).
- BT parity run used `strict_test_window=False` (documented in run manifest).
- Bespoke rehydrate produces only **2** trades, both inside the test window — but the dominant gap (+8 inside window) is not explained by test-window filtering alone.

## Question checklist

| # | question | answer |
|---|---|---|
| 1 | Raw strategy candidate signals match before RiskEngine? | **No** on duplicated SQLite vs deduped CSV at first BT-only bar (BT `long`, bespoke `none`). |
| 2 | RiskEngine same accept/reject when signals exist? | **Not reached** at first BT-only bar on bespoke (no signal). Where both fire (simulated deduped path), decisions align (`approved`). |
| 3 | RiskEngine feature diff if decisions differ? | N/A at first divergence; later cell gap also driven by missing bespoke signals. |
| 4 | BT differs due to position/re-entry? | **No** at first BT-only bar; both lanes flat. |
| 5 | CSV candle/spread identical to SQLite for the bar? | **Mostly** — mid/bid/ask match at `2022-05-06T13:00`; sub-1e-5 mid close drift on some bars (`ohlc_match=mismatch` from rounding). |
| 6 | Deduped CSV vs duplicated SQLite rows? | **Yes — proven** (1162 duplicate timestamps in SQLite). |
| 7 | Warmup alters ATR/ADX? | Duplicate bars **double-count** history, shifting ATR/ADX/range windows vs CSV. |
| 8 | BT opens while bespoke still in position? | Not at first BT-only trade; position state matched (`flat`). |
| 9 | Same-bar exit/re-entry sequencing? | Not implicated at first BT-only trade. |

## Artifacts

- `research/campaign_015/diagnostics/cell_parity_drilldown/fold_01_AUD_USD_trade_diff.json`
- `research/campaign_015/diagnostics/cell_parity_drilldown/fold_01_AUD_USD_bar_trace.json`
- `docs/research/BACKTRADER_CAMPAIGN_015_CELL_BAR_TRACE.md`
