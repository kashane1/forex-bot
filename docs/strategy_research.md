# Strategy Research Notes

## v1: Trend Following (default enabled)

- Timeframe: H4 (primary), H1 (optional with H4 direction filter).
- Indicators: EMA(50), EMA(200), Donchian(20), ATR(14).
- Long entry: `EMA_fast > EMA_slow` AND `close > Donchian_high[prior]`.
- Short entry: mirror.
- Stop: `entry ± 2.5 * ATR` (configurable, never widened after entry).
- Exit: trailing ATR stop, opposite breakout, or `max_bars_in_trade`.

The Donchian implementation in `strategies/indicators.py` shifts the
high/low series by one bar so the current bar's high/low does NOT
participate in the breakout boundary. See
`tests/unit/test_indicators.py::test_donchian_excludes_current_bar`.

## v1: Volatility Breakout (opt-in)

- Enters when current Donchian width is in the bottom Nth percentile
  of the lookback window and the close breaks the Donchian boundary
  in the direction agreeing with the regime EMA.
- Stop: opposite range edge or ATR-based, whichever is closer to entry.

## Paper-only: Mean Reversion

- Disabled in `mode != paper` by `loops.build_strategies`.
- Filters: low regime-EMA slope, RSI extremity, z-score outside band.
- Hard stop required even in paper mode.

## Excluded from v0

- Triangular arbitrage
- Grid / martingale
- ML / GA optimized live strategies
- News prediction

## Parameter governance

Every strategy config carries:

- explicit parameter values
- strategy `version`
- config hash (from the surrounding `Settings`)
- the validation period it was tested against (recorded in the
  weekly report when run)

No parameter change can move to live without a new strategy `version`
and validation report.

## Promotion gates

Research → paper/demo:

- no lookahead bias detected
- bid/ask spread and slippage modeled
- transaction costs and financing considered
- OOS performance not materially worse than IS
- parameter sensitivity acceptable
- drawdown within policy

Demo → live (not implemented in v0):

- 30+ days of clean reconciliation
- no unprotected practice trades
- no duplicate practice orders
- no risk-policy violations
- manual approval of exact config hash
