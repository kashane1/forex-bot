# Backtrader Lane — Run Log — `CAMPAIGN_015`

> `strategy_evidence: false`. Verification infrastructure only. Does not approve any strategy. Paper / demo / live remain blocked.

- generated_at: `2026-05-26T04:43:45+00:00`
- git_commit: `40cafc3da1a01e2559998e4c255dd7dd2cdf28f1`
- git_dirty: `True`
- backtrader: `1.9.78.123`
- python: `3.12.3` on `macOS-26.5-arm64-arm-64bit`
- strategy: `failed_breakout_reversal` `0.1.0-c015`
- instruments run: 7 · blocked: 0
- total trades: **416**
- total PnL (account ccy): **79.0479**

| instrument | candles | trades | wins | losses | win rate | PnL acct |
|---|---|---|---|---|---|---|
| AUD_USD | 9227 | 88 | 28 | 60 | 0.3182 | -4.1486 |
| EUR_USD | 9227 | 46 | 20 | 26 | 0.4348 | 7.3136 |
| GBP_USD | 9227 | 83 | 32 | 51 | 0.3855 | 75.9000 |
| NZD_USD | 9231 | 46 | 16 | 30 | 0.3478 | -1.4908 |
| USD_CAD | 9227 | 59 | 16 | 43 | 0.2712 | -3.0766 |
| USD_CHF | 9227 | 52 | 17 | 35 | 0.3269 | -17.2474 |
| USD_JPY | 9227 | 42 | 16 | 26 | 0.3810 | 21.7978 |

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
