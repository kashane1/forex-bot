# Backtrader Lane — Run Log — `CAMPAIGN_015`

> `strategy_evidence: false`. Verification infrastructure only. Does not approve any strategy. Paper / demo / live remain blocked.

- generated_at: `2026-05-26T01:52:53+00:00`
- git_commit: `bbe818b05186ffd329eb520bb01f8078d175409e`
- git_dirty: `True`
- backtrader: `1.9.78.123`
- python: `3.12.3` on `macOS-26.5-arm64-arm-64bit`
- strategy: `failed_breakout_reversal` `0.1.0-c015`
- instruments run: 7 · blocked: 0
- total trades: **575**
- total PnL (account ccy): **-51.4285**

| instrument | candles | trades | wins | losses | win rate | PnL acct |
|---|---|---|---|---|---|---|
| EUR_USD | 9933 | 82 | 26 | 56 | 0.3171 | -12.0142 |
| GBP_USD | 9933 | 97 | 33 | 64 | 0.3402 | 9.9709 |
| USD_JPY | 9934 | 64 | 24 | 40 | 0.3750 | 6.2727 |
| AUD_USD | 9933 | 99 | 30 | 69 | 0.3030 | -18.0921 |
| USD_CAD | 9933 | 85 | 22 | 63 | 0.2588 | -15.5338 |
| USD_CHF | 9933 | 79 | 25 | 54 | 0.3165 | -16.8003 |
| NZD_USD | 9937 | 69 | 22 | 47 | 0.3188 | -5.2318 |

### Approximation flags
- FILL_TIMING_APPROXIMATION: the bespoke engine fills at fill_timing = 'next_bar_open' (the open of the bar *following* the signal bar). The BT lane emulates this by queuing the entry on the signal bar via `_pending_side` and executing it at the next bar's open inside `_execute_pending_entry`. This is the closest faithful BT analogue; minor microstructure drift (1-bar scheduler timing) is expected and is the canonical reason this lane is classified `FILL_TIMING_APPROXIMATION` rather than `PASS`.
- RANGE_PRIOR_BARS_ONLY: prior_high / prior_low read bars [-1..-N] via `self.data.high[-offset]` / `self.data.low[-offset]`, matching the bespoke strategy's `high.iloc[-(range_lookback+1):-1]` window (strictly excludes the current bar).
- ADX_AND_ATR_CURRENT_BAR: ADX(14) and ATR(14) are read at the current bar (`self._adx[0]` / `self._atr[0]`), matching the bespoke `adx_series.iloc[-1]` / `atr_series.iloc[-1]`.
- ADVERSE_STOP_WINS: the same-bar adverse-stop rule fires on the entry bar when bar_low <= stop (long) or bar_high >= stop (short). Matches `same_bar_adverse_stop_wins = True` in the pre-commit.
- NO_TRAILING_STOP: trailing_stop_atr_multiple = None on both sides; the only exits are hard stop and 12-bar time stop. No take-profit.
- BACKTRADER_BROKER_BYPASSED: Cerebro broker is not used for fills; the strategy maintains its own one-position state machine and fills at next-bar-open using bid/ask + slippage.
- MANUAL_SIZING_RISK_FRACTION: 0.25% of compounding NAV; whole-units floor; pip value derived from quote/base currency at entry price.
- NO_FINANCING: financing/swap not modeled in either engine; comparison is pre-financing (CAMPAIGN_015 inherits the project-standard ESTIMATED-only financing posture).
