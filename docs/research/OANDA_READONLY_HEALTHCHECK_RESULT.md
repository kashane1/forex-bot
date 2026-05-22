# OANDA Read-Only Healthcheck Result — `oanda-practice-readonly-001` Phase 2

**Generated:** 2026-05-22T20:24:11.232991+00:00 · **Branch:** `oanda-practice-readonly-001`
**Config:** `configs/paper.yaml` · **Overall:** **PASS**

> Read-only diagnostic. This healthcheck calls only OANDA **practice** read-only (`GET`) endpoints. **No order was submitted, created, modified, or closed.** It is not a strategy campaign and produces no trading verdict.

## Environment

| field | value |
|---|---|
| broker environment | `practice` |
| OANDA host | `https://api-fxpractice.oanda.com` |
| account id (redacted) | `101…001` |

## Endpoint results

| endpoint | HTTP | status | latency | detail |
|---|---|---|---|---|
| account summary | `GET /v3/accounts/{id}/summary` | OK | 103 ms | currency=USD openTrades=0 openPositions=0 pendingOrders=0 |
| account details | `GET /v3/accounts/{id}` | OK | 72 ms | openTradeIds=0 openPositionInstruments=0 pendingOrderIds=0 |
| instruments list | `GET /v3/accounts/{id}/instruments` | OK | 85 ms | 68 tradeable instruments |
| pricing snapshot | `GET /v3/accounts/{id}/pricing` | OK | 73 ms | 2 quote(s) for EUR_USD, USD_JPY |
| latest EUR_USD H4 candle | `GET /v3/accounts/{id}/instruments/EUR_USD/candles` | OK | 87 ms | 5 candle(s) returned, 4 complete |
| transaction history (read) | `GET /v3/accounts/{id}/transactions/sinceid` | OK | 70 ms | 0 transaction(s) since last id — read-only history endpoint reachable |
| open trades (read) | `GET /v3/accounts/{id}/openTrades` | OK | 75 ms | 0 open trade(s) |
| open positions (read) | `GET /v3/accounts/{id}/openPositions` | OK | 80 ms | 0 open position(s) |
| pending orders (read) | `GET /v3/accounts/{id}/pendingOrders` | OK | 75 ms | 0 pending order(s) |

**9 OK · 0 FAIL · 0 SKIP** out of 9 read-only endpoint checks.

## Instrument metadata

- instrument count: 68
- sample instruments: AUD_CAD, AUD_CHF, AUD_HKD, AUD_JPY, AUD_NZD, AUD_SGD, AUD_USD, CAD_CHF

## Sample market data

- sample price snapshot: EUR_USD @ 2026-05-22T20:24:03.010077+00:00
- latest complete candle: EUR_USD H4 @ 2026-05-22T13:00:00+00:00

## Rate-limit / retry observations

- none — no HTTP 429 or retry was observed during this run.

## Failures and follow-ups

- none — every read-only endpoint check passed.

## Endpoints NOT called (forbidden in this sprint)

This healthcheck never calls any order / trade / position mutating endpoint:

- `POST /v3/accounts/{id}/orders`
- `PUT /v3/accounts/{id}/orders/{id}`
- `PUT /v3/accounts/{id}/orders/{id}/cancel`
- `PUT /v3/accounts/{id}/trades/{id}/close`
- `PUT /v3/accounts/{id}/trades/{id}/orders`
- `PUT /v3/accounts/{id}/positions/{instrument}/close`

## Safety statement

- **No order was submitted, created, modified, or closed.** Only read-only (`GET`) endpoints were called.
- The run was gated to the OANDA **practice** environment; the live host was never contacted.
- The account id is redacted (first-3 / last-3); the access token was never printed, logged, or written.
- This is a diagnostic only — `strategy_evidence: false`. It approves no strategy and produces no trading recommendation.
