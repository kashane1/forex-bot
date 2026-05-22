# Lean H4 export format

The format `scripts/export_lean_parity_data.py` writes — the candle data
a Lean parity backtest consumes. Defined so the Lean side can implement
a stable custom-data reader and so an export is byte-verifiable.

## What the exporter produces

For each instrument, two files in `--out-dir`
(default `research/lean_parity/exported/`, not committed):

1. `<INSTRUMENT>_H4_lean.csv` — the candle data.
2. `<INSTRUMENT>_H4_lean.provenance.json` — the provenance sidecar.

The exporter reads **real, already-stored OANDA H4 candles** from a
local SQLite store. It refuses any candle whose `source` is not an
`oanda-*` label, and it never fabricates data — if no real store is
present it exits non-zero and writes nothing.

## CSV format

UTF-8, comma-separated, one header row, one row per completed H4 candle,
ascending by time. Columns (exact order):

| column | meaning |
|---|---|
| `time` | OANDA bar **open** time, ISO-8601 with UTC offset. 17:00-NY aligned. |
| `bid_open` `bid_high` `bid_low` `bid_close` | bid OHLC, exact decimal strings |
| `ask_open` `ask_high` `ask_low` `ask_close` | ask OHLC, exact decimal strings |
| `volume` | OANDA tick volume (integer) |

Notes:

- **`time` is the bar OPEN**, the OANDA convention. The Lean custom-data
  reader must treat it as the open and align to the same 4-hour, 17:00-NY
  boundaries — do not resample Lean's native hourly feed.
- Prices are written as **exact decimal strings** from the stored
  `Decimal` values — no float round-trip — so the export is reproducible.
- **Bid and ask are both carried.** The bespoke engine fills a long at
  the ask and a short at the bid; the Lean algorithm needs both columns
  to replicate that. Lean's own FX feed (mid-price) is not sufficient.
- Only `complete=true` candles are exported. Incomplete candles are
  never written.

### Illustrative example

Illustrative only — **not real OANDA data**. A real export comes solely
from the stored OANDA candle store.

```
time,bid_open,bid_high,bid_low,bid_close,ask_open,ask_high,ask_low,ask_close,volume
2020-01-01T22:00:00+00:00,1.12010,1.12180,1.11960,1.12090,1.12022,1.12193,1.11974,1.12103,4120
2020-01-02T02:00:00+00:00,1.12090,1.12240,1.12040,1.12155,1.12103,1.12252,1.12053,1.12168,3880
```

## Provenance sidecar (`*.provenance.json`)

| key | meaning |
|---|---|
| `instrument`, `granularity` | always `H4` here |
| `source` | the OANDA source label (e.g. `oanda-practice`) |
| `requested_from`, `requested_to` | the export window |
| `candle_count`, `first_ts`, `last_ts` | coverage |
| `data_sha256` | SHA-256 over the exported rows — verifies the CSV |
| `campaign_002_data_request_hash` | `compute_data_request_hash(...)` over the same inputs the CAMPAIGN_002 artifacts recorded |
| `exported_by`, `exported_at` | provenance trail |

**Before a parity comparison**, confirm `campaign_002_data_request_hash`
matches the value in the CAMPAIGN_002 artifacts. That single check
proves both engines replay the *same* candles, so a divergence cannot be
blamed on the data.

## What this format is not

It carries no signals, no trades, no metrics, and no verdict — only
candles. It is verification input, not research evidence, and nothing
that consumes it can approve a strategy.
