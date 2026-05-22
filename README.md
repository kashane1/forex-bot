# forex-bot

Demo-first OANDA forex research and execution bot.

**This is engineering research, not financial advice.** Trading carries
substantial risk of loss. The v0 build is intentionally limited to OANDA
practice mode. Live trading is gated behind multiple explicit flags and
a manually approved config hash; see
[`forex_bot_founders_pack/12_ACCEPTANCE_CRITERIA.md`](forex_bot_founders_pack/12_ACCEPTANCE_CRITERIA.md).

## Research status — FROZEN (NO-GO)

**This repository is currently a research / backtesting platform. There
is no approved trading strategy.**

Nine backtest campaigns (CAMPAIGN_001–009) and Research Marathon 001
tested five strategy families on real OANDA practice data. None earned
even PAPER-TRADE-ONLY status under its pre-committed gates. The research
is frozen — see [`docs/research/FINAL_RESEARCH_DECISION_MEMO.md`](docs/research/FINAL_RESEARCH_DECISION_MEMO.md).

- **No approved strategy.** `configs/approved_strategies.yaml` is empty.
- **Order-capable loops are blocked.** `paper-loop`, `demo-loop`, and
  live mode refuse to start unless a strategy is explicitly listed in
  the approved-strategy registry — a deliberate human action that has
  not been taken.
- **All existing campaigns are historical research.** Their reports and
  artifacts are immutable evidence; see
  [`docs/research/EVIDENCE_INDEX.md`](docs/research/EVIDENCE_INDEX.md).
- **Backtesting and research remain fully available** — only the
  signal-emitting / order-capable loops are gated.
- **Research platform (infra-foundation-001 sprint):** D1 research now
  has a valid path via H4→D1 aggregation
  (`scripts/aggregate_h4_to_d1.py`); financing has an explicit
  treatment interface (`forex_bot.financing`); the research archive is
  auditable via `scripts/validate_research_archive.py`.
- **Standing live-promotion blockers:** financing/swap is still only
  *estimated* (a conservative stress overlay), never modeled in engine
  PnL; native OANDA D1 remains invalid — use the aggregate source. Both
  must be resolved before any live consideration.

Research-freeze documents:
[decision memo](docs/research/FINAL_RESEARCH_DECISION_MEMO.md) ·
[strategy status](docs/research/STRATEGY_STATUS.md) ·
[evidence index](docs/research/EVIDENCE_INDEX.md) ·
[future backlog](docs/research/FUTURE_RESEARCH_BACKLOG.md) ·
[approval process](docs/research/STRATEGY_APPROVAL_PROCESS.md).

Infrastructure-foundation sprint:
[plan](docs/research/INFRA_FOUNDATION_001_PLAN.md) ·
[summary](docs/research/INFRA_FOUNDATION_001_SUMMARY.md) ·
[D1 aggregation](docs/research/D1_AGGREGATION_DESIGN.md) ·
[financing model](docs/research/FINANCING_MODEL_DESIGN.md) ·
[Lean parity](docs/research/LEAN_PARITY_DESIGN.md).

### Validating the archive & starting future research

```bash
# Audit the research archive — reports, manifest, registry, credentials:
python scripts/validate_research_archive.py
```

Future research must follow
[`STRATEGY_APPROVAL_PROCESS.md`](docs/research/STRATEGY_APPROVAL_PROCESS.md)
and [`FUTURE_RESEARCH_BACKLOG.md`](docs/research/FUTURE_RESEARCH_BACKLOG.md):
a pre-commit before any run, the 2025–2026 test window sealed until
screening passes, and — only after a campaign passes every gate — a
deliberate human approval entry in `configs/approved_strategies.yaml`.
Backtesting and the research tooling are always available; only the
order-capable loops are gated.

## Non-negotiable principles

1. **No LLM in the live order path.**
2. **No live trading by default**, and not until every promotion gate passes.
3. **Risk engine approves every order plan** — strategies cannot place orders.
4. **Every position has a server-side stop-loss** at submission time when supported.
5. **No grid, no martingale, no averaging down.**
6. **Reconciled or blocked**: if the local ledger and broker disagree, the bot stops opening new positions.

## Quickstart

```bash
# 1. Set up Python 3.12+ and install in editable mode with dev tools.
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 2. Create an OANDA practice account at https://www.oanda.com/, generate a
#    personal access token, and put credentials in a local .env file.
cp .env.example .env
# Edit .env: set OANDA_ACCOUNT_ID_PRACTICE and OANDA_ACCESS_TOKEN_PRACTICE.

# 3. Validate config (no broker calls needed if creds missing).
bot doctor --config configs/paper.yaml

# 4. Sync instrument metadata and pull some candles.
bot sync-instruments --config configs/paper.yaml
bot fetch-candles --config configs/paper.yaml --instrument EUR_USD --granularity H4 --count 1000

# 5. Run a backtest of the configured strategies.
bot backtest --config configs/paper.yaml --instrument EUR_USD --granularity H4

# 6. Run a single paper-loop iteration.
#    NOTE: the paper-loop currently REFUSES to run — the research freeze
#    means no strategy is approved (see "Research status" above).
bot paper-loop --config configs/paper.yaml --once

# 7. Generate a weekly report.
bot report weekly --config configs/paper.yaml --out reports/
```

The practice (demo) loop uses `configs/practice.yaml`. It enables
`trading_enabled` and `allow_order_submission`, but `allow_live_trading`
and the broker environment remain practice-only. **As of the research
freeze the demo-loop also refuses to run** — no strategy is approved in
`configs/approved_strategies.yaml`.

```bash
bot demo-loop --config configs/practice.yaml --once
bot reconcile --config configs/practice.yaml
```

## Architecture (one screen)

```
market data
  → candle builder / SQLite store
  → strategy.generate_signal()           [no orders, no credentials]
  → risk.RiskEngine.evaluate()           [only approver of OrderPlan]
  → execution.Executor.submit()          [only caller of broker.submit_order]
  → broker (OANDA v20 REST)
  → transactions stream / account snapshot
  → reconciliation
  → reporting
```

- `src/forex_bot/config.py` — Pydantic settings, all safety gates.
- `src/forex_bot/domain/` — frozen domain models.
- `src/forex_bot/broker/` — Broker Protocol + OANDA adapter + error taxonomy.
- `src/forex_bot/data/` — SQLite ledger + idempotent migrations.
- `src/forex_bot/strategies/` — pure indicator + signal generators.
- `src/forex_bot/risk/` — sizing, policy, kill switch, exposure.
- `src/forex_bot/execution/` — planner, executor, reconciler.
- `src/forex_bot/backtesting/` — bid/ask-aware fills + metrics.
- `src/forex_bot/reporting/` — weekly report builder + renderers.
- `src/forex_bot/lean/` — parity notes for the optional Lean track.
- `src/forex_bot/approval.py`, `research_archive.py`, `financing.py` —
  research platform: approval registry, archive validation, financing.
- `src/forex_bot/backtesting/d1_aggregation.py` — H4→D1 research candles.

## Safety properties (tested)

See `tests/unit/test_config_safety.py`, `tests/unit/test_executor_safety.py`,
and `tests/unit/test_risk_policy.py`. Highlights:

- `test_live_example_config_refuses` — the committed `live.example.yaml`
  cannot start the bot in live mode.
- `test_paper_with_order_submission_refused` — paper mode forbids
  `allow_order_submission=true`.
- `test_paper_mode_executor_refuses` — even with a real Executor, paper
  mode does not call `broker.submit_order`.
- `test_unknown_status_blocks_trading` — a timed-out POST blocks the
  executor until reconciliation succeeds.
- `test_filled_without_protection_blocks` — a fill without
  `stopLossOnFill` blocks all new orders.
- `test_duplicate_client_id_in_local_ledger_blocks` — same client order
  id cannot be submitted twice.
- `test_submit_order_refused_on_live_environment` — the OANDA adapter
  itself refuses to call live, even if the Executor doesn't gate it.

## Configs

- [`configs/paper.yaml`](configs/paper.yaml) — paper mode. No broker
  orders. Safe to leave running.
- [`configs/practice.yaml`](configs/practice.yaml) — OANDA practice
  account. Submits orders, but only to the practice environment.
- [`configs/live.example.yaml`](configs/live.example.yaml) —
  **intentionally inert** live template. Do not rename to `live.yaml`
  until every acceptance gate passes.

See [`forex_bot_founders_pack/11_CONFIG_EXAMPLES.md`](forex_bot_founders_pack/11_CONFIG_EXAMPLES.md)
for the source spec.

## Runbooks

See [`docs/runbooks.md`](docs/runbooks.md) — kill switch, unknown order
status, transaction stream disconnect, data gaps, token rotation.

## Lean

See [`src/forex_bot/lean/README.md`](src/forex_bot/lean/README.md). Lean is
not required for the OANDA bot to run; it is an optional research /
parity track.

## Tests

```bash
pytest                 # all unit + integration tests
pytest tests/unit      # unit only
pytest -m smoke        # OANDA practice smoke tests (require creds)
ruff check .
mypy src
```

## License

Proprietary. All rights reserved.
