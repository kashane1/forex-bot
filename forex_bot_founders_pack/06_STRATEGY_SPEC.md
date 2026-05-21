# Strategy Specification

## Strategy interface

Strategies emit signals. They do not size positions, submit orders, read credentials, or mutate broker state.

```python
class Strategy(Protocol):
    name: str
    version: str

    def warmup_bars_required(self) -> int: ...

    def generate_signal(
        self,
        instrument: Instrument,
        candles: CandleFrame,
        market_state: MarketState,
        open_positions: list[Position],
        config: StrategyConfig,
    ) -> Signal | None: ...
```

Signal fields:

```text
signal_id
strategy_name
strategy_version
instrument
timeframe
timestamp
side: long | short | flat
entry_intent: market | stop | limit
confidence: optional numeric, not used for leverage in v0
stop_model
stop_price
exit_model
features: dict
reason: text
```

## V1 strategy: trend following

### Hypothesis

Major FX pairs sometimes trend across H1/H4 horizons. A simple trend-following breakout system with ATR-based risk, strict spread filters, and low leverage may produce a realistic research baseline.

### Timeframes

- Primary: H4
- Optional: H1 for entries with H4 direction filter

### Instruments

Start with a small whitelist:

- EUR_USD
- USD_JPY
- GBP_USD
- AUD_USD
- USD_CAD

Add pairs only after spread/financing/liquidity checks.

### Indicators

- EMA fast: 50
- EMA slow: 200
- Donchian lookback: 20 or 55 bars
- ATR lookback: 14

### Long setup

- EMA fast > EMA slow
- close breaks above Donchian high from prior completed bars
- ATR is above minimum threshold
- spread filter passes
- no open position
- session filter passes

### Short setup

- EMA fast < EMA slow
- close breaks below Donchian low from prior completed bars
- ATR is above minimum threshold
- spread filter passes
- no open position
- session filter passes

### Stops and exits

- Initial stop: `entry - atr_multiple * ATR` for long, `entry + atr_multiple * ATR` for short
- Default ATR multiple: 2.0 to 3.0; optimize only inside predefined ranges
- Exit on trailing ATR stop, opposite breakout, or max bars in trade
- Never widen stop after entry

### Validation notes

The evidence for broad time-series momentum supports this as a research candidate, not as proof of profitability. The exact implementation must survive costs, spread, financing, slippage, candle alignment, and parameter robustness tests.

## V1 strategy: volatility breakout

### Hypothesis

Breakouts following range compression can capture trend expansions, but false breakouts are common. This strategy is closely related to trend following and should share most infrastructure.

### Setup

- H1/H4 timeframe
- Compression defined by lower-than-recent ATR or Donchian width percentile
- Entry on break of compression range
- Direction filter optional: higher timeframe EMA regime
- Spread/ATR ratio must pass
- No trade near rollover or thin sessions

### Stops and exits

- Initial stop on opposite side of compression range or ATR stop
- Optional take-profit at fixed R only during testing
- Prefer trailing stop or time-based exit

## Paper-only strategy: mean reversion

### Hypothesis

Range-bound FX markets may revert after overextension, but trend regimes can cause severe losses. Therefore mean reversion must remain paper-only until validated.

### Setup

- Active only when trend-strength filter says range
- Example filters: ADX below threshold, EMA distance low, Donchian width stable
- Entry: z-score, Bollinger, or RSI-style overbought/oversold
- Exit: midline, fixed R, or time stop

### Mandatory guards

- Disabled during strong trend
- Disabled during high volatility expansion
- Disabled when spread/ATR is high
- Hard stop required

## Strategy families excluded from v0

### Triangular arbitrage

Rejected for this project. A MacBook, retail broker API, and small account are not suitable for competing on short-lived FX arbitrage opportunities.

### Grid / martingale

Rejected. These approaches often hide risk until a trend or gap creates catastrophic drawdown.

### ML/GA optimized indicator systems

Research-only. Overfitting risk is high. ML/GA can later assist with parameter search, regime classification, or feature analysis, but not live decision-making until validation standards are much stronger.

### News prediction

Rejected for v0. News-driven trading requires latency, event data, and execution controls that are outside the first build.

## Parameter governance

Every strategy config must have:

- explicit parameter values
- allowed parameter ranges
- strategy version
- config hash
- training window
- test window
- out-of-sample window
- validation report link

No parameter change can go live without generating a new strategy version and validation report.

## Strategy promotion gates

A strategy can move from research to paper/demo only if:

- no lookahead bias detected
- no use of incomplete candles unless designed for it
- realistic bid/ask spread and slippage modeled
- transaction costs and financing considered
- out-of-sample performance not materially worse than in-sample
- parameter sensitivity is reasonable
- drawdown is within policy

A strategy can move from demo to live only if:

- demo execution matches expected behavior
- no reconciliation failures
- no unprotected trades
- no risk policy violations
- manual approval of exact config hash
