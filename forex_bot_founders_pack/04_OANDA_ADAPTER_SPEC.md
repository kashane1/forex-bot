# OANDA Adapter Specification

## Purpose

Implement a broker adapter that maps the internal domain model to OANDA v20 REST API calls. The adapter must support read-only operations first, then practice order submission after risk approval.

## Credentials and environments

Use environment variables only:

- `OANDA_ENVIRONMENT`: `practice` or `live`
- `OANDA_ACCOUNT_ID_PRACTICE`
- `OANDA_ACCESS_TOKEN_PRACTICE`
- `OANDA_ACCOUNT_ID_LIVE`
- `OANDA_ACCESS_TOKEN_LIVE`

The app must refuse live mode unless:

- `environment: live`
- `allow_live_trading: true`
- `allow_order_submission: true`
- `live_acknowledgement` matches an exact configured phrase
- the account ID comes from the live env var, not practice

## Adapter interface

`Broker` should expose:

```python
class Broker(Protocol):
    def get_account_summary(self) -> AccountSnapshot: ...
    def get_account_details(self) -> AccountDetails: ...
    def list_instruments(self) -> list[Instrument]: ...
    def get_candles(self, request: CandleRequest) -> list[Candle]: ...
    def get_prices(self, instruments: list[str]) -> list[Quote]: ...
    def stream_prices(self, instruments: list[str]) -> Iterator[Quote | Heartbeat]: ...
    def list_open_orders(self) -> list[BrokerOrder]: ...
    def list_open_trades(self) -> list[Trade]: ...
    def list_positions(self) -> list[Position]: ...
    def submit_order(self, plan: OrderPlan) -> BrokerOrderResult: ...
    def close_trade(self, trade_id: str, units: Decimal | None = None) -> BrokerOrderResult: ...
    def get_transactions_since(self, last_transaction_id: str) -> list[Transaction]: ...
    def stream_transactions(self) -> Iterator[Transaction | Heartbeat]: ...
```

## Endpoint plan

Use the OANDA docs as source of truth. v0 needs:

- `GET /v3/accounts` - verify token and accounts.
- `GET /v3/accounts/{accountID}` - full account details for reconciliation.
- `GET /v3/accounts/{accountID}/summary` - NAV, balance, margin, P/L snapshot.
- `GET /v3/accounts/{accountID}/instruments` - instrument metadata.
- `GET /v3/accounts/{accountID}/instruments/{instrument}/candles` - historical candles.
- `GET /v3/accounts/{accountID}/pricing` - current bid/ask prices and tradeable status.
- `GET /v3/accounts/{accountID}/pricing/stream` - streaming prices when needed.
- `POST /v3/accounts/{accountID}/orders` - order submission.
- `GET /v3/accounts/{accountID}/orders` - open/pending orders.
- `GET /v3/accounts/{accountID}/trades` - open trades.
- `GET /v3/accounts/{accountID}/positions` - positions.
- `GET /v3/accounts/{accountID}/transactions/sinceid` - catch-up after disconnect.
- `GET /v3/accounts/{accountID}/transactions/stream` - broker events.

## Important OANDA-specific details

### Candle data

- Store candle `complete` flag and refuse to trade on incomplete candles unless a strategy explicitly supports it.
- Store bid, ask, and midpoint components when requested.
- Do not silently use midpoint prices for fills.
- Respect OANDA daily alignment and timezone settings.
- Store the exact request parameters used for any backtest dataset.

### Price stream

OANDA's pricing stream is not a full tick feed. It can provide at most 4 prices per second for each requested instrument and may not send every price during rapid movement. The strategy should therefore remain low-frequency. Do not design a scalper around this stream.

### Instrument metadata

Instrument metadata includes fields such as:

- name
- type
- display precision
- pip location
- trade units precision
- minimum trade size
- margin rate
- trailing stop distance constraints

Use these fields for rounding, sizing, pip calculations, margin checks, and validation.

### Order metadata and idempotency

Use OANDA `clientExtensions` where appropriate:

- deterministic client order ID derived from strategy run ID + signal ID + timestamp bucket
- tag with strategy name and version
- comment with config hash

Before submitting an order, check local ledger and broker open orders/trades for the same client ID to avoid duplicate orders after retries.

### Order types for v0

Implement only:

- Market order with stop-loss-on-fill.
- Optional take-profit-on-fill.
- Optional trailing stop only after basic stop-loss flow is reliable.

Do not implement complex order types until the reconciliation layer is proven.

### Protective stops

Every new position must include a stop loss on fill when supported. If OANDA rejects the stop loss or creates an order without protection, the execution layer must immediately block further trading and reconcile. Depending on configuration, it may close the unprotected trade.

## Error handling

Classify errors:

- Auth errors: exit and block.
- Invalid account/instrument: exit and block.
- 4xx order validation error: record rejection, block signal, do not retry blindly.
- 429/rate limit or transient 5xx: retry with bounded exponential backoff and jitter.
- Network timeout before knowing order status: do not retry the same order until idempotency check and reconciliation complete.
- Stream disconnect: reconnect and backfill transactions using last transaction ID.

## Reconciliation requirement

After startup and after every order submission:

1. Fetch account details.
2. Fetch open orders/trades/positions.
3. Fetch transactions since the last stored transaction ID.
4. Compare against local ledger.
5. If mismatch cannot be explained, set `trading_blocked = true`.

## Testing requirements

- Unit tests for mapping OANDA instrument metadata to domain model.
- Unit tests for candle parsing and complete/incomplete handling.
- Unit tests for order request construction.
- Unit tests for idempotency key generation.
- Integration tests using mocked OANDA responses.
- Optional practice-account smoke tests gated behind explicit environment variables.

## Security requirements

- Never log tokens.
- Redact account IDs in logs unless `debug_sensitive: true`, which must never be enabled in committed configs.
- Do not write secrets to the SQLite ledger.
- Provide `.env.example` only, not `.env`.
