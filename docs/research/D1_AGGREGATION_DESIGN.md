# D1 Aggregation Design — valid daily-timeframe research

**Date:** 2026-05-22 · **Branch:** `infra-research-foundation-001` · Phase 1
**Module:** `src/forex_bot/backtesting/d1_aggregation.py`
**Script:** `scripts/aggregate_h4_to_d1.py`

> This document describes infrastructure only. It does **not** authorize
> a D1 strategy campaign. No strategy was run and no trading result was
> produced. A future D1 campaign needs its own human-authorized
> pre-commit.

## 1. Why native OANDA D1 is invalid for this repo

CAMPAIGN_006 tried to test a daily-trend hypothesis on native OANDA D1
candles and got **zero valid trades**. The cause is structural, not a
strategy fault:

- OANDA D1 candles, with `daily_alignment: 17` / `America/New_York`,
  **close at 17:00 NY** — the FX market rollover.
- A candle's timestamp is therefore 17:00 NY. The backtester evaluates a
  signal at the bar's timestamp, and the RiskEngine's **session filter**
  blocks new trades in the `rollover` window (`16:45`–`17:15` NY in the
  committed configs). Every D1 signal lands inside the blackout and is
  rejected.
- Liquidity collapses at the 17:00 rollover, so the **spread** measured
  at a D1 candle's close is abnormally wide. The RiskEngine's
  **spread filter** then rejects on `SPREAD_TOO_WIDE` / `SPREAD_TO_ATR`.

Native D1 is thus *doubly* contaminated — timestamp inside the session
blackout, and a rollover-inflated close spread. The engine's fill,
session, and spread machinery is intraday-designed and simply invalid
for a bar that closes at rollover. This is an **infrastructure blocker**,
recorded as such in CAMPAIGN_006.

## 2. The fix — aggregate D1 from H4

Real OANDA **H4** candles are valid and were used throughout
CAMPAIGN_002–009. This module builds synthetic daily candles by
aggregating them, in a way that never touches the rollover.

An OANDA trading day (17:00-aligned) contains **six H4 candles**, opening
at NY `17:00, 21:00, 01:00, 05:00, 09:00, 13:00`. The last one
(`13:00 → 17:00`) is the rollover-adjacent block.

The synthetic **`D1AGG`** bar:

- aggregates the **first five** H4 candles — a 20-hour "research day"
  spanning `17:00 → 13:00` NY;
- **excludes the sixth** (`13:00 → 17:00` NY), the rollover-adjacent
  block;
- `open` = first candle's open; `high`/`low` = extremes over the five;
  `close` = fifth candle's close; `volume` = sum. **Both bid and ask
  OHLC are preserved** — no synthetic prices, pure aggregation;
- is **timestamped at the research-day close = 13:00 NY** (the sixth
  candle's open time). This deliberately diverges from OANDA's
  open-timestamp convention. It is the whole point: 13:00 NY sits in
  liquid hours, well clear of the `16:45`–`17:15` blackout, and the
  close spread is the normal-liquidity 13:00 NY spread.

The aggregated granularity is tagged **`D1AGG`** — a distinct value in
`forex_bot.domain.candles.Granularity`, never to be confused with native
OANDA `D`.

### Classification, not silent dropping

- Only **complete** H4 candles are used.
- A trading day yields a `D1AGG` candle **only** if it has all six
  well-formed H4 candles (correct NY slots, full bid/ask OHLC).
- A day with fewer than six → `incomplete` (holiday, data gap, or a
  range-boundary partial day). A day with six but malformed slots or
  missing bid/ask → `ambiguous`. **Neither emits a candle** — both are
  recorded in `day_reports`.
- **Weekend gaps** are simply absent (no trading day Sat/Sun) and are
  **not** flagged.
- **Weekday gaps** (holidays / data gaps) are reported in
  `missing_weekdays` — classified, never hidden.
- **Provenance:** every result records `source_h4_count` and a
  `source_hash` (sha256 over the input H4 candles), so an aggregation is
  reproducible and traceable.

### Worked sample (real OANDA data)

`research/d1_aggregation/sample_EUR_USD_H4_to_D1.csv` was produced from
`data/campaign_002.sqlite3` for EUR_USD, 2024-01-01 → 2024-02-01:
133 H4 candles → 22 `D1AGG` candles, 1 `incomplete` day (a window
boundary), 0 `ambiguous`, 0 missing weekdays. The accompanying
`.meta.json` records the provenance hash.

## 3. Limitations (read before any D1 campaign)

1. **20-hour day, not 24.** The `D1AGG` bar excludes the `13:00–17:00`
   NY block. Any price action in those four hours — including a possible
   daily high or low — is not represented. This is the deliberate,
   documented cost of avoiding rollover contamination.
2. **Fill model unchanged.** This module only produces clean candles.
   The backtest engine still fills at the signal bar's close; rigorous
   daily research wants **next-bar-open fills**. That remains a separate,
   open engine limitation — `D1AGG` does not fix it.
3. **DST.** Aggregation groups by NY *local* time and is robust across
   daylight-saving transitions; on the two switch days one intraday H4
   candle is wall-clock shorter/longer, but the NY slot structure
   `{17,21,01,05,09,13}` and the six-candle count still hold.
4. **Financing is still unmodeled.** Daily holding periods accrue more
   overnight financing than intraday trades. Any `D1AGG` campaign must
   apply the conservative financing stress overlay and treat financing
   as a hard live blocker — see `docs/research/FINANCING_MODEL_DESIGN.md`.
5. **Not persisted to the candle store.** `D1AGG` candles are produced
   in memory (and optionally to CSV). Writing them into the SQLite
   candle store is a deliberate future step, not done here.

## 4. How future D1 research MUST use this

- A future daily-timeframe campaign **must** use the `D1AGG` aggregate
  source. It must **never** backtest native OANDA `D` candles — that is
  the CAMPAIGN_006 bug.
- Programmatic path:

  ```python
  from forex_bot.backtesting.d1_aggregation import aggregate_h4_to_d1
  from forex_bot.domain.candles import CandleFrame

  result = aggregate_h4_to_d1(h4_candles, instrument="EUR_USD")
  frame = CandleFrame.from_candles("EUR_USD", "D1AGG", result.candles)
  # `frame` is then fed to the BacktestEngine like any other CandleFrame.
  ```

- The campaign must **inspect the classification report**
  (`result.day_reports`, `result.missing_weekdays`) and refuse to
  proceed if coverage is poor.
- The campaign must record `result.source_hash` in its provenance.
- This is **infrastructure only.** Implementing `D1AGG` does not
  authorize a D1 campaign; the research freeze still holds.

## 5. Validation

```bash
.venv/bin/python -m pytest tests/unit/test_d1_aggregation.py -q
ruff check src/forex_bot/backtesting/d1_aggregation.py scripts/aggregate_h4_to_d1.py

# Reproduce the worked sample:
python scripts/aggregate_h4_to_d1.py \
    --db data/campaign_002.sqlite3 --instrument EUR_USD \
    --from 2024-01-01 --to 2024-02-01 \
    --out research/d1_aggregation/sample_EUR_USD_H4_to_D1.csv
```
