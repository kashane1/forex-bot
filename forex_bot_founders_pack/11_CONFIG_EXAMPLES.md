# Configuration Examples

## `.env.example`

```bash
OANDA_ENVIRONMENT=practice
OANDA_ACCOUNT_ID_PRACTICE=replace_me
OANDA_ACCESS_TOKEN_PRACTICE=replace_me
OANDA_ACCOUNT_ID_LIVE=replace_me_only_when_ready
OANDA_ACCESS_TOKEN_LIVE=replace_me_only_when_ready
```

## `configs/paper.yaml`

```yaml
app:
  name: oanda-forex-research-bot
  mode: paper
  trading_enabled: false
  allow_order_submission: false
  allow_live_trading: false
  database_path: ./data/bot.sqlite3
  log_path: ./logs/bot.jsonl
  kill_switch_path: ./KILL_SWITCH

broker:
  name: oanda
  environment: practice
  account_id_env: OANDA_ACCOUNT_ID_PRACTICE
  token_env: OANDA_ACCESS_TOKEN_PRACTICE
  request_timeout_seconds: 10
  max_retries: 3

market:
  account_currency: USD
  instruments:
    - EUR_USD
    - USD_JPY
    - GBP_USD
    - AUD_USD
    - USD_CAD
  granularity: H4
  candle_price_components: BA
  daily_alignment: 17
  alignment_timezone: America/New_York
  weekly_alignment: Friday

strategy:
  enabled:
    - trend_following
  trend_following:
    version: 0.1.0
    timeframe: H4
    ema_fast: 50
    ema_slow: 200
    donchian_lookback: 20
    atr_lookback: 14
    atr_stop_multiple: 2.5
    max_bars_in_trade: 80

risk:
  starting_equity_usd: 500
  risk_per_trade_pct: 0.25
  max_risk_per_trade_pct: 0.50
  max_daily_loss_pct: 1.00
  max_weekly_loss_pct: 2.00
  max_total_drawdown_pct: 8.00
  max_open_positions: 1
  max_pending_orders: 1
  max_correlated_positions: 1
  require_stop_loss: true
  require_server_side_protection: true
  allow_martingale: false
  allow_grid: false
  allow_averaging_down: false

spread_filter:
  enabled: true
  max_spread_to_atr_pct: 8.0
  max_spread_pips:
    EUR_USD: 1.5
    USD_JPY: 2.0
    GBP_USD: 2.5
    AUD_USD: 2.0
    USD_CAD: 2.5

session_filter:
  enabled: true
  timezone: America/New_York
  block_new_trades:
    - name: rollover
      start: "16:45"
      end: "17:15"
    - name: friday_close
      day: Friday
      start: "15:00"
      end: "23:59"
    - name: sunday_open
      day: Sunday
      start: "00:00"
      end: "19:00"
```

## `configs/practice.yaml`

```yaml
app:
  name: oanda-forex-research-bot
  mode: practice
  trading_enabled: true
  allow_order_submission: true
  allow_live_trading: false
  database_path: ./data/bot.sqlite3
  log_path: ./logs/bot.jsonl
  kill_switch_path: ./KILL_SWITCH

broker:
  name: oanda
  environment: practice
  account_id_env: OANDA_ACCOUNT_ID_PRACTICE
  token_env: OANDA_ACCESS_TOKEN_PRACTICE
  request_timeout_seconds: 10
  max_retries: 3

# Inherit or duplicate market, strategy, risk, spread_filter, session_filter from paper config.
```

## `configs/live.example.yaml`

This is intentionally inert. Do not rename to `live.yaml` until all acceptance criteria pass.

```yaml
app:
  name: oanda-forex-research-bot
  mode: live
  trading_enabled: false
  allow_order_submission: false
  allow_live_trading: false
  live_acknowledgement: "NOT_APPROVED"
  required_live_acknowledgement: "I_ACCEPT_THE_RISK_AND_APPROVE_THIS_EXACT_CONFIG_HASH"
  approved_config_hash: "replace_with_manual_approval_hash"
  database_path: ./data/live-bot.sqlite3
  log_path: ./logs/live-bot.jsonl
  kill_switch_path: ./KILL_SWITCH

broker:
  name: oanda
  environment: live
  account_id_env: OANDA_ACCOUNT_ID_LIVE
  token_env: OANDA_ACCESS_TOKEN_LIVE
  request_timeout_seconds: 10
  max_retries: 3

risk:
  risk_per_trade_pct: 0.25
  max_risk_per_trade_pct: 0.50
  max_daily_loss_pct: 1.00
  max_weekly_loss_pct: 2.00
  max_open_positions: 1
  require_stop_loss: true
  require_server_side_protection: true
  allow_martingale: false
  allow_grid: false
  allow_averaging_down: false
```

## Config validation rules

The app must reject:

- `environment: live` with practice account env vars
- `mode: live` without `allow_live_trading: true`
- `allow_live_trading: true` without exact acknowledgement phrase
- `allow_order_submission: true` with `trading_enabled: false`
- `risk_per_trade_pct > max_risk_per_trade_pct`
- `require_stop_loss: false`
- `allow_martingale: true`
- `allow_grid: true`
- `allow_averaging_down: true`
- empty instrument whitelist
- missing spread filter for enabled instrument
- missing or invalid kill switch path
