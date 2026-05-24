---
status: complete
priority: p2
issue_id: 002
tags: [code-review, sprint:infra-exit-fidelity-001, typing, mypy-strict]
dependencies: []
---

# Tighten `gap_fill_policy` typing from `str` to `GapFillPolicy` Literal

## Problem Statement

The kieran-python-reviewer noted that `GapFillPolicy = Literal["none", "gap_through"]` is defined in `src/forex_bot/backtesting/fills.py` but never imported by the engine or `BacktestResult`. Both type the field as plain `str`, losing static narrowing at every call site.

`fill_timing` has a similar pattern (typed as `FillTiming` in some places, `str` in others). The plan called for mirroring `fill_timing` exactly — but this is one place where the precedent could be tighter and we have a chance to do it right.

## Findings

- **src/forex_bot/backtesting/fills.py:43** — `GapFillPolicy = Literal["none", "gap_through"]` defined but only used in `config.py`.
- **src/forex_bot/backtesting/engine.py:124** — `gap_fill_policy: str = "none"` (engine kwarg).
- **src/forex_bot/backtesting/engine.py:91** — `gap_fill_policy: str = "none"` (BacktestResult field).
- Both should use the Literal: `gap_fill_policy: GapFillPolicy = "none"`. Mypy strict would then catch any caller passing an invalid string at static-analysis time (today only the CLI runtime check catches it).

## Proposed Solutions

### Option A (recommended): import and use the Literal in both places

Import `GapFillPolicy` from `fills.py` in `engine.py` (where `FillTiming` is already imported); update both annotations.

- **Pros**: static narrowing throughout; matches `FillTiming` import pattern; one-line change in 3 places.
- **Cons**: None.
- **Effort**: Small (5 min).
- **Risk**: None.

### Recommended Action: Option A

## Acceptance Criteria

- [ ] `BacktestEngine.__init__` `gap_fill_policy` typed `GapFillPolicy`
- [ ] `BacktestResult.gap_fill_policy` typed `GapFillPolicy`
- [ ] CLI still works (`# type: ignore[arg-type]` on the engine kwarg if mypy complains about `str` → `Literal` narrowing)
- [ ] `pytest tests/` green
- [ ] `ruff check src tests scripts` clean

## Work Log

- 2026-05-24: created from kieran-python-reviewer item 7.
- 2026-05-24: **resolved**. Imported `GapFillPolicy` from `fills.py` into `engine.py`; typed (a) `BacktestEngine.__init__` kwarg, (b) `self.gap_fill_policy`, (c) `BacktestResult.gap_fill_policy` as `GapFillPolicy` instead of `str`. pytest 792 passed, ruff clean.
