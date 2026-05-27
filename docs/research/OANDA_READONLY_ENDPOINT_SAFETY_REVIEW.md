# OANDA Read-Only Endpoint Safety Review

**Sprint:** `infra-observed-financing-capture-readonly-002`  
**Module:** `src/forex_bot/research/oanda_readonly.py`  
**Script:** `scripts/capture_oanda_observed_financing_readonly.py`

## Allowed endpoints (GET, practice host)

- Account metadata: `/v3/accounts/{id}`
- Summary: `/v3/accounts/{id}/summary`
- Transactions (bounded): `/v3/accounts/{id}/transactions?from=&to=`
- Since-id / id-range / numeric transaction id reads

## Forbidden endpoints

| Endpoint family | Reason |
|-----------------|--------|
| `api-fxtrade.oanda.com` | Live environment refused |
| `POST/PUT/PATCH/DELETE` any path | Mutation methods blocked at broker + not invoked |
| `/orders` | Order creation/modification |
| `/trades/*/close` | Trade close |
| `/positions/*/close` | Position close |
| `/pendingOrders`, `/openTrades`, `/openPositions` | Trading state mutation surface |
| `/transactions/stream` | Streaming (not needed; deny by fragment) |
| `/configure`, `/funding` | Account configuration |

Existing `OandaBroker.submit_order` / `close_trade` remain unchanged and **are not called** by this sprint.

## Tests added

`tests/unit/test_oanda_readonly_capture_002.py` — allowlist pass, order/trade-close/live refusal, auth log guard, fixture sanitization, dry-run without network, execute credential gate.

## Credential handling

- Dry-run: no credential read required
- Execute: practice token + account id from env; practice account tag verified
- Never printed to stdout/logs in capture script

## Live environment rejection

`reject_live_host()` and `OANDA_ENVIRONMENT=live` → `BLOCKED_PRACTICE_ENV_NOT_CONFIRMED` before any request.

## Unresolved risks

- Transaction list may include non-financing types — classifier counts unknown types, does not infer meaning
- Sparse practice account may return zero `DAILY_FINANCING` rows (documented empty fixture path)
- Rate inference from observed events still requires denser sample + future bridge to `financing_rates` table

## No-approval statement

Safety review is infrastructure only.
