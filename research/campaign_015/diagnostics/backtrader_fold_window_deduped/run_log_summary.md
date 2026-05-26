# Backtrader Lane — Run Log — `CAMPAIGN_015`

> `strategy_evidence: false`. Verification infrastructure only. Does not approve any strategy. Paper / demo / live remain blocked.

- generated_at: `2026-05-26T05:09:04+00:00`
- git_commit: `38ab9c4acf9efef1efef04548fec774a532bbad9`
- git_dirty: `True`
- backtrader: `1.9.78.123`
- python: `3.12.3` on `macOS-26.5-arm64-arm-64bit`
- strategy: `failed_breakout_reversal` `0.1.0-c015`
- instruments run: 7 · blocked: 0
- total trades: **288**
- total PnL (account ccy): **38.1740**

| instrument | candles | trades | wins | losses | win rate | PnL acct |
|---|---|---|---|---|---|---|
| AUD_USD | 9227 | 60 | 19 | 41 | 0.3167 | -10.0147 |
| EUR_USD | 9227 | 31 | 13 | 18 | 0.4194 | 1.9865 |
| GBP_USD | 9227 | 56 | 21 | 35 | 0.3750 | 37.5430 |
| NZD_USD | 9231 | 36 | 13 | 23 | 0.3611 | 3.8755 |
| USD_CAD | 9227 | 41 | 11 | 30 | 0.2683 | -1.9265 |
| USD_CHF | 9227 | 37 | 13 | 24 | 0.3514 | -9.8137 |
| USD_JPY | 9227 | 27 | 12 | 15 | 0.4444 | 16.5238 |

### Approximation flags
- FILL_TIMING_APPROXIMATION: the bespoke engine fills at fill_timing = 'next_bar_open' (the open of the bar *following* the signal bar). The BT lane emulates this by queuing the entry on the signal bar via `_pending_side` and executing it at the next bar's open inside `_execute_pending_entry`. This is the closest faithful BT analogue; minor microstructure drift (1-bar scheduler timing) is expected and is the canonical reason this lane is classified `FILL_TIMING_APPROXIMATION` rather than `PASS`.
- RANGE_PRIOR_BARS_ONLY: prior_high / prior_low read bars [-1..-N] via `self.data.high[-offset]` / `self.data.low[-offset]`, matching the bespoke strategy's `high.iloc[-(range_lookback+1):-1]` window (strictly excludes the current bar).
- ADX_AND_ATR_CURRENT_BAR: ADX(14) and ATR(14) are read at the current bar (`self._adx[0]` / `self._atr[0]`), matching the bespoke `adx_series.iloc[-1]` / `atr_series.iloc[-1]`.
- ENTRY_BAR_STOP_POLICY: default BT mode applies same-bar adverse stop on the entry bar (`backtrader_default`). Parity mode `bespoke_current_no_entry_bar_stop` skips entry-bar adverse stop to mirror current bespoke BacktestEngine behaviour; later-bar stops unchanged.
- ADVERSE_STOP_WINS_LATER_BARS: on bars after entry, adverse stop wins when bar_low <= stop (long) or bar_high >= stop (short).
- NO_TRAILING_STOP: trailing_stop_atr_multiple = None on both sides; the only exits are hard stop and 12-bar time stop. No take-profit.
- BACKTRADER_BROKER_BYPASSED: Cerebro broker is not used for fills; the strategy maintains its own one-position state machine and fills at next-bar-open using bid/ask + slippage.
- MANUAL_SIZING_RISK_FRACTION: 0.25% of compounding NAV; whole-units floor; pip value derived from quote/base currency at entry price.
- NO_FINANCING: financing/swap not modeled in either engine; comparison is pre-financing (CAMPAIGN_015 inherits the project-standard ESTIMATED-only financing posture).
