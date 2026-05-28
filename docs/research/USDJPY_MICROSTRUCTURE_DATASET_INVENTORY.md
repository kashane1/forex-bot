# USD_JPY Microstructure Diagnostic — Dataset Inventory

**Status:** read-only inventory. No verdict change, no approval, no tuning, no C024, no campaign. USD_JPY-only.

- Instrument: **USD_JPY** · source: CAMPAIGN_022 base trades (gitignored local CSVs).
- Total USD_JPY base trades: **306** (train 133, validation 173).
- Local M15 path data: **reachable**.

## Counts by split

| split | n | hard_stop | time_stop | winners | win_rate | mean_r | long | short |
|---|---|---|---|---|---|---|---|---|
| train | 133 | 81 | 52 | 46 | 0.3459 | -0.001717 | 93 | 40 |
| validation | 173 | 91 | 82 | 70 | 0.4046 | 0.000396 | 89 | 84 |
| **total** | 306 | 172 | 134 | 116 | 0.3791 | -0.000522 | — | — |

## MFE/MAE coverage & straight-to-stop (reconstructed read-only)

- MFE/MAE available (status OK): **299** / 306; NO_BARS: 7; other: {'NO_BARS': 7}.
- OK by split: train 130, validation 169.
- **Straight-to-stop** (hard-stopped AND never reached +0.25R before stop): **79** (0.4593 of hard stops).
- Mean MFE_r 1.1709 · mean MAE_r -0.8842 (price-based R; adverse-first intrabar; diagnostic only).

## Notes

- Entry-time numeric features are **not** pre-persisted by C022 and **not** yet reconstructed here; Phase 3 reconstructs them read-only for USD_JPY only.
- Splits use the C022 windows: train 2021-06-01..2023-12-31, validation 2024-01-01..2025-06-30. The 2025-07+ test window stays a sealed lockbox and is **not** part of this diagnostic.
- USD_JPY scope is a research-scoping decision, **not** an edge claim.
