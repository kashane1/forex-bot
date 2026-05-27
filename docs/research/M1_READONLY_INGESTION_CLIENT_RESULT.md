# M1 Read-Only Ingestion Client Result

## Status

Implemented `scripts/ingest_oanda_m1_candles.py` with safety tests in `tests/unit/test_ingest_oanda_m1_candles.py`.

## Safety Contract

- Practice host only: `api-fxpractice.oanda.com`
- Live host refused: `api-fxtrade.oanda.com`
- Candle endpoint only: `/v3/instruments/{instrument}/candles`
- Account, order, trade, position, and transaction endpoint fragments refused
- `M1` granularity only
- Bounded `--start` and `--end` required
- Dry-run behavior by default unless `--execute-readonly-ingestion` is passed
- Instrument allowlist restricted to the seven major pairs already used in research
- Compact manifest output only; no raw broker payloads written
- Credentials and store URLs are redacted in outputs

## Flags

- `--instrument EUR_USD`
- `--start YYYY-MM-DD`
- `--end YYYY-MM-DD`
- `--granularity M1`
- `--dry-run`
- `--execute-readonly-ingestion`
- `--max-chunks`
- `--store-uri` reserved for CLI compatibility
- `--manifest-out`

## Chunking

The script chunks requests into one-day M1 windows and supports `--max-chunks` for bounded smoke runs. Large ranges without `--max-chunks` are refused as `BLOCKED_DATE_RANGE`.

## Blocked Conditions

- Missing practice token: `BLOCKED_READONLY_CREDENTIALS`
- Missing or unsafe local store: existing research DB blockers
- Live OANDA environment: refused
- Non-candle or non-practice endpoint: refused

## Tests

Added tests for:

- candle endpoint allowed
- order endpoint refused
- trade endpoint refused
- position endpoint refused
- live host refused
- missing date range refused
- large range without chunk limit refused
- dry-run makes no network call
- M1 payload parses to `CandleRecord`
- no executor/order submission imports

## Validation

```bash
pytest tests/unit/test_ingest_oanda_m1_candles.py -q
ruff check scripts/ingest_oanda_m1_candles.py tests/unit/test_ingest_oanda_m1_candles.py
```

Both passed.

## Approval Statement

No ingestion was executed, no raw candle data was committed, no strategy evidence was run, and no strategy was approved.
