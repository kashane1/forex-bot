# M1 Ingestion Smoke Blocked

## Status

`BLOCKED_READONLY_CREDENTIALS` and `BLOCKED_LOCAL_STORE`.

## Preconditions Checked

- Practice token present: no
- OANDA environment: `practice`
- Local research DB URL present: no
- Dry run: pass
- Network called: no
- Raw payload written: no

Dry-run command:

```bash
python scripts/ingest_oanda_m1_candles.py --instrument EUR_USD --start 2024-01-02 --end 2024-01-03 --max-chunks 1
```

Result:

- status: `DRY_RUN`
- instrument: `EUR_USD`
- granularity: `M1`
- chunk_count: 1
- candles_written: 0
- network_called: false
- raw_payload_committed: false

## No-Trade Statement

No OANDA network call was made. No order/trade/position endpoint was called. No live host was used. No raw candle data was written or committed.
