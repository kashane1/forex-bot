# Product Requirements Document

## Product name

Working name: `oanda-forex-research-bot`

## Product summary

A local Python application for researching, paper/demo trading, risk-controlling, executing, reconciling, and reporting low-frequency OANDA forex strategies. It is designed to start in OANDA practice mode and make live trading deliberately hard to enable.

## Primary user

A software engineer who wants to build and operate a personal forex automation system with strong engineering controls, broker-state reconciliation, local logs, and AI-assisted review outside the live decision path.

## Goals

1. Provide a clean OANDA practice-trading bot that is reliable enough to run unattended but conservative enough to fail safe.
2. Separate strategy signal generation from risk approval and broker execution.
3. Make every decision auditable through durable logs and a local ledger.
4. Support deterministic backtests and paper/demo comparisons.
5. Allow weekly/monthly review by humans and coding assistants without exposing live broker credentials.

## Non-goals for v0

- No promise of profit.
- No live trading by default.
- No LLM-based live trade decisions.
- No tick scalping or high-frequency trading.
- No triangular arbitrage.
- No grid, martingale, averaging down, or recovery schemes.
- No ML/GA live strategy in v0.
- No multi-broker support beyond interfaces and stubs.
- No cloud deployment until local demo stability exists.

## MVP scope

### Must have

- CLI commands:
  - `bot doctor`
  - `bot sync-instruments`
  - `bot fetch-candles`
  - `bot backtest`
  - `bot paper-loop`
  - `bot demo-loop`
  - `bot reconcile`
  - `bot report weekly`
- OANDA practice account integration.
- Read-only mode by default.
- Explicit `allow_order_submission: true` required for any broker order.
- Separate `allow_live_trading: true` required for live environment.
- Strategy plugins that return signals, not orders.
- Risk engine that converts approved signals into order plans.
- Broker adapter that submits, modifies, closes, and reconciles only approved order plans.
- Server-side stop loss required for every new position where supported.
- Local persistence for candles, spreads, signals, orders, fills, transactions, account snapshots, and risk events.
- Structured logs in JSONL.
- Unit tests for sizing, pip value, risk approvals, order planning, OANDA response parsing, and config safety.

### Should have

- Lean parity harness for at least one strategy.
- Weekly report generation in Markdown and HTML.
- Export of trades/signals to CSV/Parquet.
- Launchd plist template for macOS.
- Notification hook abstraction for future email/Slack/Telegram/webhook support.

### Could have later

- DuckDB/Parquet research store.
- Economic calendar/news blackout module.
- Carry/swap-aware filters.
- Multi-account support.
- VPS deployment.
- Cloud dashboards.

## User stories

1. As the operator, I can verify my OANDA practice credentials and account metadata without submitting orders.
2. As the operator, I can backfill candles for allowed instruments and inspect missing data.
3. As the operator, I can run a backtest and see metrics, trades, and configuration hash.
4. As the operator, I can run a paper loop that generates would-have-traded signals without broker orders.
5. As the operator, I can run a practice demo loop that submits tiny OANDA practice orders only when all guards pass.
6. As the operator, I can stop the bot by setting a kill-switch file or config flag.
7. As the operator, I can reconcile local state with OANDA account state after restart, network loss, or order submission.
8. As the operator, I can produce a weekly report and ask an AI assistant to review it without exposing secrets.

## Safety requirements

- Secrets must come only from environment variables or a local ignored secrets file.
- Live account IDs and tokens must never be committed.
- The app must refuse to start in live mode unless all live gates are explicitly enabled.
- The app must refuse to submit orders when local ledger and broker state disagree.
- The app must stop opening new positions after daily/weekly loss limits or drawdown thresholds are hit.
- The app must block orders when spread, price status, market status, or instrument metadata is invalid.
- The app must round order units and prices using OANDA instrument metadata.

## Success metrics

Engineering success is measured before trading performance:

- 0 unauthorized order submissions.
- 0 live orders unless live gates are explicitly enabled.
- 0 unreconciled positions after restart.
- 100% of order attempts linked to signal, order plan, risk decision, broker response, and transaction IDs.
- Backtest and demo execution assumptions documented for every strategy version.
- Weekly report generated without manual database edits.

Trading research success requires:

- Positive out-of-sample expectancy after realistic costs.
- Acceptable max drawdown under stress tests.
- Stable performance across reasonable parameter ranges.
- Demo results not materially worse than backtest beyond predefined tolerance.
