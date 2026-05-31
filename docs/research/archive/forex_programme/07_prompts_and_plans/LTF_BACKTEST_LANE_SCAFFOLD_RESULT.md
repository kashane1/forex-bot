# LTF Backtest Lane Scaffold Result

## Status

Implemented `src/forex_bot/backtesting/ltf_preflight.py` with tests in `tests/unit/test_ltf_backtest_preflight.py`.

## Scope

This is a preflight scaffold only. It does not run a strategy, does not generate evidence, and does not import broker or executor modules.

## Checks

- execution timeframe must be `M15` or `M5`
- execution frame must be non-empty
- final-bar signals return `NEXT_BAR_OPEN_UNAVAILABLE`
- next-bar-open lookup uses the next execution-frame bar
- context frames are restricted to H1/H4/D1AGG
- context frames must contain completed rows
- time stops are represented as execution bars

## Tests

Added tests for:

- next-bar-open on M15 uses the next M15 open
- final-bar signal is unavailable
- time stop uses M15 execution bars
- time stop of N bars is not interpreted as H4 bars
- valid LTF preflight leaves risk sizing untouched by this scaffold
- no broker/executor imports

## Validation

```bash
ruff check src/forex_bot/backtesting/ltf_preflight.py tests/unit/test_ltf_backtest_preflight.py
pytest tests/unit/test_ltf_backtest_preflight.py -q
```

Both passed.

## Approval Statement

No CAMPAIGN_021 evidence was created, no strategy verdict was created, and no strategy was approved.
