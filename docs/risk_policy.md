# Risk Policy — operational summary

Binding spec: [`forex_bot_founders_pack/05_RISK_POLICY.md`](../forex_bot_founders_pack/05_RISK_POLICY.md).

## Hard prohibitions

These are enforced by `config.RiskConfig._check_bounds` and refuse
config load:

- `allow_martingale: true`
- `allow_grid: true`
- `allow_averaging_down: true`
- `require_stop_loss: false`

These are enforced at runtime by `RiskEngine.evaluate`:

- No trade without a protective stop (`MISSING_STOP_LOSS`).
- No trade during unreconciled state (`UNRECONCILED`).
- No trade with active kill switch (`KILL_SWITCH`).
- No trade in blocked session windows (`SESSION_BLOCKED`).
- No trade against tradeable=false or missing price (`NOT_TRADEABLE`, `STALE_PRICE`).
- No trade over spread caps (`SPREAD_TOO_WIDE`, `SPREAD_TO_ATR`).
- No trade over loss limits or drawdown caps (`DAILY_LOSS_LIMIT`, `WEEKLY_LOSS_LIMIT`, `DRAWDOWN_LIMIT`).
- No new trade above max open positions / per instrument / margin buffer.

## Default sizing

`risk_per_trade_pct = 0.25` of NAV per trade. `max_risk_per_trade_pct =
0.50`. Equity assumed USD 500. Daily loss cap 1%, weekly 2%, total
drawdown 8%.

For each trade, the engine records:

- account NAV used
- instrument metadata version
- spread snapshot
- stop distance pips
- raw_units before rounding, units after rounding
- estimated risk and margin
- config hash

## Position sizing formula

```
risk_amount_home = nav_home * risk_pct / 100
stop_distance_price = |entry - stop|
stop_distance_pips = stop_distance_price / pip_size
pip_value_per_unit_home = f(instrument, account_currency, current_prices)
raw_units = risk_amount_home / (stop_distance_pips * pip_value_per_unit_home)
units = round_down_to_trade_units_precision(raw_units)
```

`pip_value_per_unit_home` handles three cases:

- `quote == account_currency`: pip in home directly.
- `base == account_currency`: divide pip by the instrument's mid price.
- Cross: use a `<quote>_<home>` or `<home>_<quote>` quote.
