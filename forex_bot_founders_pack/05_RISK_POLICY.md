# Risk Policy

## Mission

The first mission is survival and clean data, not income. A USD 500 bankroll is too small to justify aggressive leverage. The bot should behave like an instrumented research system with strict capital preservation.

## Hard prohibitions

The bot must never implement these in live or demo order submission:

- Martingale.
- Grid averaging.
- Averaging down after loss.
- Doubling after loss.
- Removing or widening stop loss because a trade is losing.
- Opening multiple correlated positions during v0.
- Trading without a protective stop.
- Trading during an unreconciled broker/local state mismatch.
- Trading while kill switch is active.
- Trading during configured market blackout windows.
- LLM-generated live trade decisions.

## Default risk limits

```yaml
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
  max_positions_per_instrument: 1
  require_stop_loss: true
  require_server_side_protection: true
  allow_martingale: false
  allow_grid: false
  allow_averaging_down: false
```

## Position sizing

The core sizing formula:

```text
risk_amount_home = account_nav_home * risk_per_trade_pct / 100
stop_distance_price = abs(entry_price - stop_price)
pip_size = 10 ** instrument.pip_location
stop_distance_pips = stop_distance_price / pip_size
pip_value_per_unit_home = broker_or_conversion_model(instrument, account_currency, current_prices)
raw_units = risk_amount_home / (stop_distance_pips * pip_value_per_unit_home)
units = round_down_to_trade_units_precision(raw_units)
```

Then apply constraints:

- `units >= minimumTradeSize`
- `units <= maximumOrderUnits`
- estimated margin required fits configured margin buffer
- position value does not exceed max notional exposure
- currency exposure is within caps
- spread and slippage assumptions do not invalidate the stop/risk

If any input is missing, reject the trade.

## Spread filter

Reject new trades when:

- price status is not tradeable
- bid or ask is missing
- spread pips exceeds instrument-specific max
- spread / ATR exceeds configured threshold
- current spread is above recent percentile threshold

Example:

```yaml
spread_filter:
  enabled: true
  max_spread_pips:
    EUR_USD: 1.5
    USD_JPY: 2.0
    GBP_USD: 2.5
    AUD_USD: 2.0
    USD_CAD: 2.5
  max_spread_to_atr_pct: 8.0
```

## Time and event filters

In v0, avoid known problematic windows rather than trying to model them:

- no new trades around daily rollover
- no new trades near Friday close
- no new trades immediately after Sunday open
- no weekend holds unless explicitly enabled
- no trading around high-impact news until a calendar module exists

Example:

```yaml
session_filter:
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

## Daily and weekly loss controls

Track realized and unrealized P/L. If either daily or weekly loss threshold is breached:

- block new trades
- continue monitoring open trades
- do not widen stops
- optionally flatten positions only if `auto_flatten_on_loss_limit: true`

Flattening can reduce tail risk but can also crystallize temporary drawdowns. Default in v0: block new trades and preserve existing protective exits unless a critical risk condition exists.

## Margin buffer

The bot must treat broker leverage as a ceiling, not a target. Add a margin buffer rule:

```yaml
margin:
  min_margin_available_pct_of_nav: 80
  max_margin_used_pct_of_nav: 10
  reject_if_margin_closeout_percent_above: 20
```

## Exposure rules

Because forex pairs share currencies, a long EUR/USD and long GBP/USD are both short USD exposure. v0 should have only one open position. Later versions should track currency-level exposure.

## Kill switch

Implement both:

- config kill switch: `trading_enabled: false`
- file kill switch: if `./KILL_SWITCH` exists, block all new orders immediately

Optional emergency mode:

```yaml
kill_switch:
  block_new_orders: true
  cancel_pending_orders: true
  flatten_positions: false
```

## Risk decision audit

Every signal must receive a stored risk decision:

- approved/rejected
- rejection reason codes
- account NAV used
- instrument metadata version
- spread snapshot
- stop distance
- units before and after rounding
- estimated risk
- estimated margin
- config hash

## Manual approval gates

No strategy can move to live unless:

1. Unit tests pass.
2. Backtest passes minimum criteria.
3. Out-of-sample passes.
4. Walk-forward passes.
5. Practice demo period passes.
6. Reconciliation is clean.
7. Manual review approves exact config hash.
