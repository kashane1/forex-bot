# Repo Scaffold and Implementation Tasks

## Recommended tooling

- Python 3.12+
- uv or pip-tools for dependency management
- pydantic for config/domain validation
- httpx for HTTP client
- pandas/numpy for indicators and research data frames
- sqlalchemy or sqlite-utils for persistence; raw sqlite is acceptable in v0
- duckdb and pyarrow optional for research exports
- typer for CLI
- rich for console output
- structlog or Python logging JSON formatter
- pytest for tests
- respx or responses for mocked HTTP tests
- ruff for linting
- mypy or pyright for type checking

## Initial commands

```bash
mkdir forex-bot
cd forex-bot
git init
uv init --package
uv add pydantic pydantic-settings httpx pandas numpy typer rich python-dotenv tenacity
uv add --dev pytest pytest-cov respx ruff mypy freezegun
mkdir -p configs src/forex_bot tests/unit tests/integration tests/fixtures docs scripts
```

Use equivalent pip/poetry commands if not using uv.

## Milestone 0: Safety skeleton

Tasks:

- Create project layout.
- Add `.gitignore` and `.env.example`.
- Add `Config` model with safety gates.
- Add CLI with `doctor` command.
- Add redacted logging.
- Add tests proving live mode refuses unsafe config.

Definition of done:

- `pytest` passes.
- `bot doctor --config configs/practice.yaml` works without credentials and reports missing env vars safely.
- No order-related code exists yet.

## Milestone 1: Domain models and storage

Tasks:

- Implement domain models.
- Implement SQLite connection and migrations.
- Implement repositories for instruments, candles, signals, risk decisions, order plans, transactions, account snapshots.
- Add config hash utility.

Definition of done:

- Domain model validation tests pass.
- Migrations are idempotent.
- Test fixtures can insert/read candles and decisions.

## Milestone 2: OANDA read-only adapter

Tasks:

- Implement authenticated HTTP client.
- Implement `get_account_summary`.
- Implement `list_instruments`.
- Implement `get_candles`.
- Implement `get_prices`.
- Implement retry/backoff for safe GET requests.
- Add mocked endpoint tests.

Definition of done:

- No order submission methods implemented or they raise `NotImplementedError`.
- Read-only smoke test can be run manually against practice when env vars exist.
- Instrument metadata is stored locally.

## Milestone 3: Indicators and first backtest

Tasks:

- Implement EMA, ATR, Donchian helpers.
- Implement trend-following strategy signal generation.
- Implement simple backtest engine using bid/ask aware fills.
- Add metrics.
- Add `bot backtest`.

Definition of done:

- Backtest uses only completed candles.
- Backtest saves run config hash and trade list.
- Unit tests catch lookahead mistakes in Donchian breakout.

## Milestone 4: Risk engine

Tasks:

- Implement position sizing.
- Implement spread filters.
- Implement daily/weekly loss checks.
- Implement exposure checks.
- Implement kill switch.
- Implement risk decision persistence.

Definition of done:

- Given a signal, risk engine returns approved/rejected with reason codes.
- Position sizing tests include EUR_USD, JPY pair, and non-USD quote conversion cases.
- All rejected trades are stored.

## Milestone 5: Paper loop

Tasks:

- Implement loop that fetches latest complete candles.
- Generate signals.
- Run risk checks.
- Save paper order plans.
- No broker order submission.

Definition of done:

- Running paper loop cannot submit orders even if credentials exist.
- Weekly report includes would-have-traded events.

## Milestone 6: Practice execution

Tasks:

- Implement OANDA order submission for practice only.
- Use idempotent client IDs.
- Attach stop-loss-on-fill.
- Save broker response.
- Implement transaction catch-up.
- Implement reconciliation after order submit.

Definition of done:

- Practice execution requires `allow_order_submission: true` and `environment: practice`.
- Live environment still blocked.
- Unknown order status blocks further orders until reconciliation.

## Milestone 7: Reporting

Tasks:

- Implement `bot report weekly`.
- Include P/L, risk decisions, execution quality, slippage, spread, strategy attribution, reconciliation issues.
- Export Markdown and HTML.

Definition of done:

- Report can be generated from SQLite only.
- No secrets appear in report.

## Milestone 8: Lean parity harness

Tasks:

- Add Lean project directory or instructions.
- Implement trend-following strategy in Lean or document why deferred.
- Compare selected backtest window with native engine.

Definition of done:

- Differences are documented.
- No Lean requirement to run core OANDA bot.

## Milestone 9: Live readiness but not live by default

Tasks:

- Add live config template only.
- Add live safety prompts/acknowledgement.
- Add launchd templates.
- Add incident runbooks.

Definition of done:

- Tests prove live mode is impossible without all gates.
- Manual checklist exists.
- No real live secrets in repo.

## Issue backlog labels

- `safety`
- `broker-oanda`
- `risk`
- `strategy`
- `backtest`
- `data`
- `reconciliation`
- `reporting`
- `lean`
- `ops`
- `docs`

## First 10 tickets

1. Scaffold project with config, CLI, logging, and test setup.
2. Implement safe config gates and live-mode refusal tests.
3. Implement SQLite migrations and repositories.
4. Implement OANDA read-only account summary and instrument sync.
5. Implement candle fetch and storage with complete flag.
6. Implement indicators and trend-following signal generation.
7. Implement backtest engine with bid/ask fill model.
8. Implement risk sizing and spread filters.
9. Implement paper loop and report of would-have-traded signals.
10. Implement practice order submission with stop-loss-on-fill and reconciliation.
