# AI Build Prompt for Codex or Claude

Copy this prompt into Codex or Claude when starting the repo.

```text
You are building a production-minded but demo-first forex research and execution bot. This is engineering research, not financial advice. The repo must default to safety and must not place live trades unless all explicit live gates are enabled.

Use the docs in this founders pack as binding requirements:

- 01_DECISION_MEMO.md
- 02_PRD.md
- 03_ARCHITECTURE.md
- 04_OANDA_ADAPTER_SPEC.md
- 05_RISK_POLICY.md
- 06_STRATEGY_SPEC.md
- 07_DATA_BACKTEST_VALIDATION.md
- 08_REPO_SCAFFOLD_AND_TASKS.md
- 10_RUNBOOKS.md
- 11_CONFIG_EXAMPLES.md
- 12_ACCEPTANCE_CRITERIA.md

Build the repository from scratch in Python 3.12+.

Core rules:

1. No LLM or AI component in the live trading decision path.
2. Strategies emit Signal objects only.
3. The risk engine is the only component allowed to approve an order plan.
4. The broker adapter may submit only approved order plans.
5. OANDA practice mode comes before live mode.
6. Live mode must be impossible unless environment is live, allow_order_submission is true, allow_live_trading is true, and the live acknowledgement phrase exactly matches config.
7. No secrets in code, logs, tests, docs, or fixtures.
8. Every order attempt must be auditable from signal to risk decision to order plan to broker response to transaction reconciliation.
9. Implement tests before or alongside code. Safety tests are mandatory.
10. Prefer simple, readable code with explicit types over clever abstractions.

Initial implementation target:

- Project scaffold with pyproject.toml.
- Typer CLI.
- Pydantic config.
- JSON logging with secret redaction.
- SQLite ledger with idempotent migrations.
- Domain models.
- OANDA read-only adapter: account summary, instruments, candles, prices.
- Trend-following strategy signal generator.
- Risk engine: sizing, spread filter, daily/weekly loss checks, max position checks, kill switch.
- Backtest engine with bid/ask-aware fill model.
- Paper loop that cannot submit broker orders.
- Practice execution only after explicit flag, with stop-loss-on-fill and reconciliation.
- Weekly report.

Do not implement live trading until all acceptance criteria pass. You may include a live config template, but it must be inert and safe.

Use official OANDA docs as source of truth for endpoint details. Do not trust sample repos as production code. Use mocked HTTP tests for OANDA responses. Add practice-account smoke tests behind explicit environment variables but skip them by default in CI.

After each milestone:

- Run tests.
- Update README.
- Update docs if behavior differs.
- Summarize safety implications.

Start with Milestone 0 from 08_REPO_SCAFFOLD_AND_TASKS.md. Show the file tree and then implement the minimal safe skeleton.
```

## Review prompt for changes

```text
Review this change as if it could cause real broker orders. Focus on:

- Can this bypass risk checks?
- Can this submit live orders accidentally?
- Can this duplicate orders on retry?
- Can this trade on stale, incomplete, or misaligned data?
- Can this hide reconciliation mismatches?
- Can secrets leak through logs, reports, errors, or tests?
- Are backtest assumptions different from practice/live assumptions?
- Are there new parameters that encourage overfitting?

Return blockers, non-blocking concerns, and required tests.
```

## Weekly strategy review prompt

```text
Analyze the attached weekly bot report. Do not propose live changes first. Identify:

- rule violations
- risk rejections
- reconciliation issues
- spread/slippage anomalies
- strategy performance by instrument and session
- difference between backtest assumptions and practice execution
- signs of overfitting or parameter chasing
- one conservative experiment for paper/demo only

Any proposed change must include a hypothesis, expected effect, affected config hash, validation plan, rollback plan, and promotion gate.
```
