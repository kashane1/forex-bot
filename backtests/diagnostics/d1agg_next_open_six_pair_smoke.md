# D1AGG + next-bar-open — six-pair diagnostic smoke report

**DIAGNOSTIC-ONLY.** This report contains **no strategy evidence**, **no trading recommendation**, and **no approval**. It is a mechanical plumbing check of the D1AGG aggregation path and the `next_bar_open` fill timing across the six major pairs. The engine here is driven by a deterministic fixed-bar *diagnostic probe* with no indicators and no edge logic; its trades are mechanical artifacts, not results. No strategy was run, no campaign was opened, no test-window research decision was made, and the research freeze is unaffected.

- Generated: `2026-05-22T12:29:24`
- Data mode: **committed D1AGG sample (no real OANDA H4 store present)**
- Overall mechanical status: **PASS**
- See `docs/research/FILL_TIMING_MODEL.md`, `docs/research/D1_AGGREGATION_DESIGN.md`, and `docs/research/OANDA_H4_DATA_REHYDRATION.md`.

## Instrument coverage (six majors)

| pair | status |
|---|---|
| EUR_USD | blocked — no H4 store |
| GBP_USD | blocked — no H4 store |
| USD_JPY | blocked — no H4 store |
| AUD_USD | blocked — no H4 store |
| USD_CAD | blocked — no H4 store |
| USD_CHF | blocked — no H4 store |

## Blockers / limitations

- no real OANDA H4 candle store at data/oanda_h4_research.sqlite3 — the six-pair H4→D1AGG aggregation smoke could not run for EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF

A blocker here is a *data-availability* limitation, not a mechanical failure. The six-pair H4→D1AGG smoke needs a real OANDA practice H4 store — rebuild it with `scripts/rehydrate_oanda_h4_store.py` (see `docs/research/OANDA_H4_DATA_REHYDRATION.md`). The store is gitignored and never committed. The mechanical D1AGG→`next_bar_open` verification below still runs on real, provenance-tracked data.

## EUR_USD

- Data source: committed real D1AGG sample research/d1_aggregation/sample_EUR_USD_H4_to_D1.csv
- D1AGG bars: 22
- Data hash: `5b05561e0f2788df9de1f8ef325f919f654519af6c8fa2061a6d8449d7eb5b79`

| check | status | detail |
|---|---|---|
| `data_is_real_oanda` | PASS | committed sample derived from 133 real OANDA H4 candles, source_hash 5b05561e0f2788df… — not synthetic |
| `d1agg_timestamps_clear_blackout` | PASS | all 22 D1AGG timestamps clear the 16:45–17:15 NY rollover blackout (so a rollover-window session filter would not block them) |
| `next_bar_open_data_available` | PASS | all 21 non-final D1AGG bars have a usable next-bar open quote |
| `engine_fills_at_next_bar_open` | PASS | probe entry filled at D1AGG bar N+1 open: 2024-01-11 ask_open=1.09734 |
| `missing_next_bar_detected` | PASS | final-bar probe signal recorded as an explicit NEXT_BAR_OPEN_UNAVAILABLE skip; no trade opened |

## What this does and does not establish

**Does:** the D1AGG aggregation output feeds the backtest engine; `next_bar_open` fills an entry at bar N+1's open; D1AGG timestamps clear the rollover blackout; a final-bar signal is skipped explicitly. Pure mechanics.

**Does not:** measure, suggest, or imply any strategy edge. The diagnostic probe is not a strategy. Nothing here is evidence for or against any strategy, and nothing here approves anything.
