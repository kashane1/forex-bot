# Forex Bot Founders Pack

Date: 2026-05-21
Status: Engineering specification, not financial advice
Primary broker choice: OANDA
Preferred tooling: Native Python bot first, with QuantConnect Lean used deliberately as a research/backtest/live-engine option rather than casually mixed in.

## Executive verdict

The notes are directionally strong on engineering: OANDA-first is a reasonable path for a Mac-native autonomous bot because OANDA has a documented v20 REST API, practice/live account flow, pricing, candles, order endpoints, account state, and transaction streams. QuantConnect Lean is also a serious tool for research, backtesting, optimization, and live trading.

The main correction is this: do not use Lean "whenever possible" unless you define exactly what Lean owns. A common failure mode is to backtest in Lean, execute in a separate custom Python engine, and accidentally implement different candle handling, fill logic, spread logic, sizing, rounding, and order semantics. That creates false confidence. The repo should choose one of these patterns:

1. Native Python OANDA bot as canonical runtime, with a small internal backtester and optional Lean parity tests.
2. Lean-first strategy engine, with OANDA live trading through Lean.
3. Hybrid, but only if the strategy, risk model, and execution model are shared or mechanically generated from one canonical specification.

Recommended for this project: start with option 1 for the MVP because the bankroll is small, the strategy is simple, and direct OANDA integration gives you maximal control and minimal platform overhead. Use Lean as an independent benchmark/research harness after the OANDA adapter, ledger, risk engine, and backtest assumptions are stable. Re-evaluate Lean-first after the first validated demo/paper period.

## What this pack contains

- `01_DECISION_MEMO.md` - final architecture recommendation and alternative analysis.
- `02_PRD.md` - product requirements for the first repo build.
- `03_ARCHITECTURE.md` - component boundaries, runtime flow, and repo layout.
- `04_OANDA_ADAPTER_SPEC.md` - broker adapter contract and OANDA endpoint plan.
- `05_RISK_POLICY.md` - mandatory risk limits, kill switches, and position sizing.
- `06_STRATEGY_SPEC.md` - v1 strategy definitions and what is excluded.
- `07_DATA_BACKTEST_VALIDATION.md` - data, backtesting, and model validation rules.
- `08_REPO_SCAFFOLD_AND_TASKS.md` - implementation roadmap and file tree.
- `09_AI_BUILD_PROMPT.md` - prompt to give Codex or Claude.
- `10_RUNBOOKS.md` - local ops, incident response, and deployment notes.
- `11_CONFIG_EXAMPLES.md` - YAML examples and environment variables.
- `12_ACCEPTANCE_CRITERIA.md` - tests and go-live gates.
- `13_SOURCES.md` - source list used to ground the spec.

## Non-negotiable principles

1. No LLM in the live order path.
2. No live trading until the safety gates pass.
3. Risk engine must approve every order plan.
4. Every live order must have a server-side protective stop or equivalent risk-limiting order attached at submission time when supported.
5. No grid, no martingale, no averaging down.
6. Demo/paper first; live mode must require an explicit configuration flag and separate credentials.
7. Backtests are evidence, not proof. Strategy promotion requires out-of-sample tests, walk-forward tests, paper trading, and manual approval.

## First build target

Build a demo-only OANDA practice bot that can:

- Load config safely.
- Fetch account summary and tradeable instrument metadata.
- Fetch H1/H4 candles using bid/ask/mid data as required.
- Persist candles, prices, signals, order plans, orders, fills, transactions, and account snapshots.
- Produce signals from a trend-following strategy.
- Convert signals into risk-approved order plans.
- Submit practice orders only after all guards pass.
- Reconcile broker state against local ledger on every loop and after every order.
- Generate weekly reports.

The first version does not need ML, GA, news trading, scalping, triangular arbitrage, portfolio optimization, or fully automated live deployment.
