# Decision Memo

## Context

The intended project is a forex trading bot for OANDA, built by a software engineer, with interest in QuantConnect Lean tooling. The initial bankroll discussed in the notes is USD 500. The engineering goal is not to build an income machine; it is to build a controlled research and execution system that can survive, log reality, and support disciplined iteration.

## Decision

Build OANDA-first with a native Python runtime for the MVP. Keep the code broker-neutral at the domain layer, but implement only the OANDA adapter initially. Use QuantConnect Lean as a deliberate secondary path for research and parity testing, not as an undefined side tool.

Recommended MVP stack:

- Python 3.12+
- OANDA v20 REST API
- OANDA practice account first
- SQLite for operational ledger; optional DuckDB/Parquet for research data
- Pydantic for config/domain validation
- httpx or requests for HTTP
- pandas/numpy for indicator calculations
- pytest/respx or equivalent for tests
- Typer CLI for operational commands
- launchd on macOS only after demo stability

## Why OANDA-first is reasonable

OANDA documents the v20 REST API for practice/live account access, token-based authentication, accounts, pricing, candles, orders, trades, positions, and transaction streams. This makes it a straightforward engineering target for a local bot.

OANDA also exposes account-specific instrument metadata such as instrument name, pip location, display precision, margin rate, minimum trade size, and trailing-stop limits. The bot should fetch and cache this metadata instead of hardcoding pip sizes, margin assumptions, or trade-size constraints.

## Lean decision

Lean is valuable, but the pack recommends not making it the main runtime in v0 unless you intentionally choose Lean-first. Lean brings a professional event-driven engine, backtesting, optimization, research notebooks, reports, and live trading pathways, including OANDA integration. However, using Lean's CLI/live deployment has platform requirements, and the QuantConnect docs currently state that using the CLI requires membership in an organization on a paid tier.

Lean should enter the project in one of these ways:

### Option A: Native Python canonical runtime, Lean as independent benchmark

Use the Python bot to define strategy, risk, broker adapter, and ledger. Separately implement a Lean version of the same strategy to detect whether results are broadly consistent. This is best for fast MVP iteration.

### Option B: Lean-first

Use Lean for research, backtests, and live deployment from the beginning. This reduces custom infrastructure but increases framework coupling and may require paid QuantConnect organization access. This is best if you want formal reports, optimization, and event-driven live trading as the core product from day one.

### Option C: Hybrid shared core

Create pure Python strategy/risk functions that can run inside both the native bot and Lean. This is possible but needs discipline, wrappers, and parity tests. Avoid this in v0 unless you are prepared to write the adapter layer carefully.

## Recommended final stance

Use native Python OANDA for v0. Add Lean after the first stable data and risk pipeline exists. The main reason is not that Lean is bad; it is that two runtimes before you have validated the domain model will create unnecessary surface area.

## Alternatives considered

### FOREX.com first

The original notes understate FOREX.com a little. FOREX.com advertises REST API trading with streaming prices and account/order functionality, though access may require contacting support after opening a standard account. Since the user has already chosen OANDA, this does not change the recommendation. It only means the original claim that FOREX.com lacks a usable API path should be softened.

### MT5/MQL5 first

MT5 is a viable trading ecosystem, but it is not the cleanest Mac-native Python path. The official MetaTrader5 Python package on PyPI currently distributes Windows x86-64 wheels, and MT5-on-mac setups tend to introduce terminal/Wine/bridge complexity. If an MT5 route is ever required, prefer an MQL5 Expert Advisor or a Windows/VPS setup instead of a fragile Python-to-MT5 bridge on macOS.

### Backtrader first

Backtrader remains useful for local strategy experimentation, but it should not be the live OANDA layer for this project. If used, treat it as exploratory research only.

## Evidence-backed assumptions

- OANDA v20 API exists and supports account access, REST calls, token authentication, prices, candles, orders, and transaction streams.
- OANDA instrument metadata should be queried from the account, not hardcoded.
- Lean supports OANDA live brokerage workflows through its CLI/cloud documentation and OANDA brokerage plugin.
- Lean has useful research/backtesting/optimization/live-trading tooling.
- FOREX.com does have an advertised REST API route, so it should not be dismissed as impossible.
- MT5 Python package distribution is Windows-oriented on PyPI at the time of this pack.
- Trend-following/time-series momentum has academic evidence across asset classes including currencies, but that evidence does not prove a small retail OANDA implementation will be profitable.
- Retail forex and CFD trading carry high risk, and simulated performance has known limitations.

## Risky or overconfident assumptions in the original notes

1. "Trend following is strongest first strategy" is directionally defensible, but it is not proof that a Donchian/EMA/ATR strategy on a few OANDA pairs will survive spread, financing, slippage, and regime changes.
2. "H1/H4 avoids scalping problems" is sensible but not sufficient. You still need spread filters, rollover avoidance, execution realism, weekend controls, and liquidity checks.
3. "OANDA samples are a good starting point" is true only as examples. They are not production scaffolds.
4. "$500 can run a real bot" is mechanically possible, but economically constrained. It is mainly enough for learning and data collection, not reliable income.
5. "Use Lean whenever possible" is dangerous unless you define ownership boundaries and parity tests.
6. "Weekly AI-assisted improvement" can help with review, but it can also encourage parameter chasing. Require validation gates before any change goes live.
7. "Carry filter later" is fine, but carry/swap data availability and financing treatment must be solved before using carry as a signal.

## Decision checkpoints

Revisit this decision after:

- 30 demo trading days with no reconciliation mismatches.
- At least 100 closed paper/demo trades, or 3 months of low-frequency live-equivalent demo operation, whichever comes first.
- A complete execution-quality report covering spread, slippage, skipped trades, order rejects, latency, financing, and gaps.
- A Lean parity backtest that either agrees with the native engine within tolerance or documents why it differs.
