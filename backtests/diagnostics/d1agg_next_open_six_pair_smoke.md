# D1AGG + next-bar-open — six-pair diagnostic smoke report

**DIAGNOSTIC-ONLY.** This report contains **no strategy evidence**, **no trading recommendation**, and **no approval**. It is a mechanical plumbing check of the D1AGG aggregation path and the `next_bar_open` fill timing across the six major pairs. The engine here is driven by a deterministic fixed-bar *diagnostic probe* with no indicators and no edge logic; its trades are mechanical artifacts, not results. No strategy was run, no campaign was opened, no test-window research decision was made, and the research freeze is unaffected.

- Generated: `2026-05-22T13:36:09`
- Data mode: **real OANDA H4 store (data/oanda_h4_research.sqlite3)**
- Overall mechanical status: **PASS**
- `strategy_evidence: false` — a diagnostic artifact is never strategy evidence; this approves nothing and recommends nothing.
- See `docs/research/FILL_TIMING_MODEL.md`, `docs/research/D1_AGGREGATION_DESIGN.md`, and `docs/research/OANDA_H4_DATA_REHYDRATION.md`.

## Instrument coverage (six majors)

| pair | status |
|---|---|
| EUR_USD | aggregated — 1655 D1AGG bars, source_hash e418a507b8a2… |
| GBP_USD | aggregated — 1655 D1AGG bars, source_hash 793d1e3863f9… |
| USD_JPY | aggregated — 1655 D1AGG bars, source_hash 80cc8526260a… |
| AUD_USD | aggregated — 1655 D1AGG bars, source_hash 8d4177819e60… |
| USD_CAD | aggregated — 1655 D1AGG bars, source_hash 31c899acea82… |
| USD_CHF | aggregated — 1655 D1AGG bars, source_hash 7ac5e36f1c95… |

## EUR_USD

- Data source: OANDA H4 → D1AGG (9931 H4 bars)
- D1AGG bars: 1655
- Data hash: `e418a507b8a2227afcb116290e3d8bae489fb6b9ade6f4de1fbfc692dbc2f67b`

| check | status | detail |
|---|---|---|
| `data_is_real_oanda` | PASS | H4 source(s) ['oanda-practice']; 1655 trading days aggregated; source_hash e418a507b8a2227a… |
| `d1agg_timestamps_clear_blackout` | PASS | all 1655 D1AGG timestamps clear the 16:45–17:15 NY rollover blackout (so a rollover-window session filter would not block them) |
| `next_bar_open_data_available` | PASS | all 1654 non-final D1AGG bars have a usable next-bar open quote |
| `engine_fills_at_next_bar_open` | PASS | probe entry filled at D1AGG bar N+1 open: 2020-01-13 ask_open=1.11255 |
| `missing_next_bar_detected` | PASS | final-bar probe signal recorded as an explicit NEXT_BAR_OPEN_UNAVAILABLE skip; no trade opened |

## GBP_USD

- Data source: OANDA H4 → D1AGG (9931 H4 bars)
- D1AGG bars: 1655
- Data hash: `793d1e3863f9be0ed736462650ed1cb96c15bff24ff05c5b71aef9167ea26bcf`

| check | status | detail |
|---|---|---|
| `data_is_real_oanda` | PASS | H4 source(s) ['oanda-practice']; 1655 trading days aggregated; source_hash 793d1e3863f9be0e… |
| `d1agg_timestamps_clear_blackout` | PASS | all 1655 D1AGG timestamps clear the 16:45–17:15 NY rollover blackout (so a rollover-window session filter would not block them) |
| `next_bar_open_data_available` | PASS | all 1654 non-final D1AGG bars have a usable next-bar open quote |
| `engine_fills_at_next_bar_open` | PASS | probe entry filled at D1AGG bar N+1 open: 2020-01-13 ask_open=1.30405 |
| `missing_next_bar_detected` | PASS | final-bar probe signal recorded as an explicit NEXT_BAR_OPEN_UNAVAILABLE skip; no trade opened |

## USD_JPY

- Data source: OANDA H4 → D1AGG (9932 H4 bars)
- D1AGG bars: 1655
- Data hash: `80cc8526260a262b8b90b04a153f640bf2b2c3ac623460b469cd970abb7afad0`

| check | status | detail |
|---|---|---|
| `data_is_real_oanda` | PASS | H4 source(s) ['oanda-practice']; 1655 trading days aggregated; source_hash 80cc8526260a262b… |
| `d1agg_timestamps_clear_blackout` | PASS | all 1655 D1AGG timestamps clear the 16:45–17:15 NY rollover blackout (so a rollover-window session filter would not block them) |
| `next_bar_open_data_available` | PASS | all 1654 non-final D1AGG bars have a usable next-bar open quote |
| `engine_fills_at_next_bar_open` | PASS | probe entry filled at D1AGG bar N+1 open: 2020-01-13 ask_open=109.550 |
| `missing_next_bar_detected` | PASS | final-bar probe signal recorded as an explicit NEXT_BAR_OPEN_UNAVAILABLE skip; no trade opened |

## AUD_USD

- Data source: OANDA H4 → D1AGG (9931 H4 bars)
- D1AGG bars: 1655
- Data hash: `8d4177819e60f04988ba6203b72bd8c825f915a26c9f9c655a6be648a2da0648`

| check | status | detail |
|---|---|---|
| `data_is_real_oanda` | PASS | H4 source(s) ['oanda-practice']; 1655 trading days aggregated; source_hash 8d4177819e60f049… |
| `d1agg_timestamps_clear_blackout` | PASS | all 1655 D1AGG timestamps clear the 16:45–17:15 NY rollover blackout (so a rollover-window session filter would not block them) |
| `next_bar_open_data_available` | PASS | all 1654 non-final D1AGG bars have a usable next-bar open quote |
| `engine_fills_at_next_bar_open` | PASS | probe entry filled at D1AGG bar N+1 open: 2020-01-13 ask_open=0.69029 |
| `missing_next_bar_detected` | PASS | final-bar probe signal recorded as an explicit NEXT_BAR_OPEN_UNAVAILABLE skip; no trade opened |

## USD_CAD

- Data source: OANDA H4 → D1AGG (9931 H4 bars)
- D1AGG bars: 1655
- Data hash: `31c899acea82703c9aed1f8669e337de920adc2db15eaa07986168812054be74`

| check | status | detail |
|---|---|---|
| `data_is_real_oanda` | PASS | H4 source(s) ['oanda-practice']; 1655 trading days aggregated; source_hash 31c899acea82703c… |
| `d1agg_timestamps_clear_blackout` | PASS | all 1655 D1AGG timestamps clear the 16:45–17:15 NY rollover blackout (so a rollover-window session filter would not block them) |
| `next_bar_open_data_available` | PASS | all 1654 non-final D1AGG bars have a usable next-bar open quote |
| `engine_fills_at_next_bar_open` | PASS | probe entry filled at D1AGG bar N+1 open: 2020-01-13 ask_open=1.30640 |
| `missing_next_bar_detected` | PASS | final-bar probe signal recorded as an explicit NEXT_BAR_OPEN_UNAVAILABLE skip; no trade opened |

## USD_CHF

- Data source: OANDA H4 → D1AGG (9931 H4 bars)
- D1AGG bars: 1655
- Data hash: `7ac5e36f1c95028d6f352db57ea7ace8eda106b20732a585e7c77d06eeaa068e`

| check | status | detail |
|---|---|---|
| `data_is_real_oanda` | PASS | H4 source(s) ['oanda-practice']; 1655 trading days aggregated; source_hash 7ac5e36f1c95028d… |
| `d1agg_timestamps_clear_blackout` | PASS | all 1655 D1AGG timestamps clear the 16:45–17:15 NY rollover blackout (so a rollover-window session filter would not block them) |
| `next_bar_open_data_available` | PASS | all 1654 non-final D1AGG bars have a usable next-bar open quote |
| `engine_fills_at_next_bar_open` | PASS | probe entry filled at D1AGG bar N+1 open: 2020-01-13 ask_open=0.97409 |
| `missing_next_bar_detected` | PASS | final-bar probe signal recorded as an explicit NEXT_BAR_OPEN_UNAVAILABLE skip; no trade opened |

## What this does and does not establish

**Does:** the D1AGG aggregation output feeds the backtest engine; `next_bar_open` fills an entry at bar N+1's open; D1AGG timestamps clear the rollover blackout; a final-bar signal is skipped explicitly. Pure mechanics.

**Does not:** measure, suggest, or imply any strategy edge. The diagnostic probe is not a strategy. Nothing here is evidence for or against any strategy, and nothing here approves anything.
