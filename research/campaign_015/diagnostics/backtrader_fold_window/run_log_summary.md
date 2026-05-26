# Backtrader Lane — Run Log — `CAMPAIGN_015`

> `strategy_evidence: false`. Verification infrastructure only. Does not approve any strategy. Paper / demo / live remain blocked.

- generated_at: `2026-05-26T03:18:35+00:00`
- git_commit: `e0a5d812f3295ba148c058912cea86065ad965a4`
- git_dirty: `True`
- backtrader: `1.9.78.123`
- python: `3.12.3` on `macOS-26.5-arm64-arm-64bit`
- strategy: `failed_breakout_reversal` `0.1.0-c015`
- instruments run: 7 · blocked: 0
- total trades: **532**
- total PnL (account ccy): **-3.9167**

| instrument | candles | trades | wins | losses | win rate | PnL acct |
|---|---|---|---|---|---|---|
| AUD_USD | 9227 | 101 | 30 | 71 | 0.2970 | -15.8015 |
| EUR_USD | 9227 | 79 | 30 | 49 | 0.3797 | 11.2521 |
| GBP_USD | 9227 | 95 | 30 | 65 | 0.3158 | 21.6602 |
| NZD_USD | 9231 | 53 | 16 | 37 | 0.3019 | -9.5542 |
| USD_CAD | 9227 | 81 | 19 | 62 | 0.2346 | -13.7473 |
| USD_CHF | 9227 | 70 | 23 | 47 | 0.3286 | -18.8763 |
| USD_JPY | 9227 | 53 | 20 | 33 | 0.3774 | 21.1502 |

### Approximation flags
- FILL_TIMING_APPROXIMATION: the bespoke engine fills at fill_timing = 'next_bar_open' (the open of the bar *following* the signal bar). The BT lane emulates this by queuing the entry on the signal bar via `_pending_side` and executing it at the next bar's open inside `_execute_pending_entry`. This is the closest faithful BT analogue; minor microstructure drift (1-bar scheduler timing) is expected and is the canonical reason this lane is classified `FILL_TIMING_APPROXIMATION` rather than `PASS`.
- RANGE_PRIOR_BARS_ONLY: prior_high / prior_low read bars [-1..-N] via `self.data.high[-offset]` / `self.data.low[-offset]`, matching the bespoke strategy's `high.iloc[-(range_lookback+1):-1]` window (strictly excludes the current bar).
- ADX_AND_ATR_CURRENT_BAR: ADX(14) and ATR(14) are read at the current bar (`self._adx[0]` / `self._atr[0]`), matching the bespoke `adx_series.iloc[-1]` / `atr_series.iloc[-1]`.
- ADVERSE_STOP_WINS: the same-bar adverse-stop rule fires on the entry bar when bar_low <= stop (long) or bar_high >= stop (short). Matches `same_bar_adverse_stop_wins = True` in the pre-commit.
- NO_TRAILING_STOP: trailing_stop_atr_multiple = None on both sides; the only exits are hard stop and 12-bar time stop. No take-profit.
- BACKTRADER_BROKER_BYPASSED: Cerebro broker is not used for fills; the strategy maintains its own one-position state machine and fills at next-bar-open using bid/ask + slippage.
- MANUAL_SIZING_RISK_FRACTION: 0.25% of compounding NAV; whole-units floor; pip value derived from quote/base currency at entry price.
- NO_FINANCING: financing/swap not modeled in either engine; comparison is pre-financing (CAMPAIGN_015 inherits the project-standard ESTIMATED-only financing posture).
