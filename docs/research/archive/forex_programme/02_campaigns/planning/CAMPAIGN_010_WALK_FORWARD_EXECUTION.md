# CAMPAIGN_010 — Walk-Forward Execution

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-walk-forward-001`
`strategy_evidence: false`

Phase 3 per-fold execution record for the CAMPAIGN_010 research
candidate (`session_breakout 0.1.0-c010`). **This document does not
approve the strategy.** It records the commands, data path, frozen
parameter enforcement, fold-by-fold execution outcomes, and exact
artifact paths produced by this sprint.

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. The
> walk-forward verdict classification lives in
> [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
> (Phase 4).

## 1. Commands

```bash
# Phase 2 plan (re-run for repeatability):
.venv/bin/python scripts/run_walk_forward_dry_run.py \
    --campaign-name CAMPAIGN_010 \
    --universe-start 2020-01-01 --universe-end 2026-05-20 \
    --style rolling --parameter-mode frozen \
    --train-days 540 --validation-days 180 --test-days 180 \
    --step-days 180 \
    --output backtests/CAMPAIGN_010_session_breakout/walk_forward/

# Phase 3 per-fold execution:
.venv/bin/python scripts/run_campaign_010.py \
    --config configs/campaign_010_session_breakout.yaml \
    --plan backtests/CAMPAIGN_010_session_breakout/walk_forward/plan.json \
    --out backtests/CAMPAIGN_010_session_breakout/
```

Runtime: **7.9 seconds** end-to-end on the 8 folds × 7 pairs = 56
backtests, single-machine local execution. No broker call, no
credential read.

## 2. Data and provenance (re-confirmed at runtime)

- `data/campaign_002.sqlite3` (gitignored symlink — see
  [`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md))
- per-pair source = `oanda-practice` (asserted at runtime; mismatch
  aborts the runner)
- per-pair H4 candles read with `completed_only=True`
- 7-pair universe matched exactly against the design

## 3. Frozen-parameter enforcement (binding)

The runner aborts before any backtest if the loaded YAML's
`strategy.session_breakout` deviates from the pre-commit. The
asserted-frozen set, verbatim from
[`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
§5:

| parameter | value |
|---|---|
| `version` | `0.1.0-c010` |
| `timeframe` | `H4` |
| `atr_lookback` | `14` |
| `atr_stop_multiple` | `2.0` |
| `trailing_stop_atr_multiple` | `None` |
| `max_bars_in_trade` | `6` |
| `min_atr_pips` | `{}` |
| `asian_session_hours_utc_start` | `22` |
| `asian_session_hours_utc_end` | `6` |
| `london_session_hours_utc_start` | `6` |
| `london_session_hours_utc_end` | `12` |
| `min_asian_range_atr_fraction` | `0.30` |

All values match. The runner also asserts
`parameter_mode == "frozen"` and `split_style == "rolling"` on the
loaded plan.

## 4. Per-fold execution table (test windows only)

| fold | test_start | test_end | total trades | aggregate return % | expectancy R | profit factor | pairs +ve | single-pair dom % |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 0 | 2021-12-21 | 2022-06-18 | 367 | -1.23 | -0.0042 | 0.69 | 5/7 | 51.1 |
| 1 | 2022-06-19 | 2022-12-15 | 390 | -12.05 | -0.1005 | 0.00 | 0/7 | 26.2 |
| 2 | 2022-12-16 | 2023-06-13 | 409 | -7.32 | -0.0623 | 0.13 | 2/7 | 27.3 |
| 3 | 2023-06-14 | 2023-12-10 | 374 | -3.25 | -0.0215 | 0.20 | 3/7 | 56.5 |
| 4 | 2023-12-11 | 2024-06-07 | 347 | -9.28 | -0.0833 | 0.03 | 1/7 | 29.6 |
| 5 | 2024-06-08 | 2024-12-04 | 265 | -4.25 | -0.0604 | 0.11 | 2/7 | 44.3 |
| 6 | 2024-12-05 | 2025-06-02 | 347 | +1.63 | +0.0211 | 1.57 | 3/7 | 21.2 |
| 7 | 2025-06-03 | 2025-11-29 | 292 | -0.81 | -0.0071 | 0.64 | 3/7 | 29.7 |
| **total** | | | **2791** | **-36.56** | **-0.0408** | **0.04** | | |

Profit factor 0.00 for fold 1 indicates zero gross wins (every test
fold's trade gross-pnl <= 0 after costs); the runner reports the
zero literally rather than dividing by zero.

## 5. Per-pair × all-folds aggregate (informational)

| pair | trades | aggregate return % | expectancy R |
|---|---:|---:|---:|
| EUR_USD | 310 | -6.21 | -0.0794 |
| GBP_USD | 565 | -6.11 | -0.0428 |
| USD_JPY | 492 | -5.36 | -0.0003 |
| AUD_USD | 511 | -9.63 | -0.0748 |
| USD_CAD | 434 | -9.26 | -0.0649 |
| USD_CHF | 432 | +1.69 | **+0.0185** |
| NZD_USD | 47 | -1.67 | -0.1399 |

USD_CHF is the only pair with a positive aggregate expectancy R
(+0.0185); the gate requires 4 of 7 pairs positive — far from
met. NZD_USD has very few trades (47) and a strongly negative
expectancy.

## 6. Implementation bug fixes during this sprint

**None required for the candidate itself.** The runner
(`scripts/run_campaign_010.py`) is a new artifact; it mirrors the
existing `scripts/run_campaign_009.py` pattern adapted to consume a
walk-forward plan and to drive 56 per-fold-per-pair backtests. One
incidental cleanup applied to the runner during code review:
`from dataclasses import field` was removed (unused import; ruff
F401). No edit to the strategy module, no edit to the engine, no
edit to financing.

## 7. Data issues found

None affecting the candidate's evaluation. The candidate ran
cleanly against every pair × every fold; no per-pair fold returned
a `nan`/`inf` metric or aborted due to missing candles. NZD_USD's
low trade count in early folds (4 in fold 0; 21 in fold 1; 9 in
fold 2; 5 in fold 3; 0 in fold 4; 2 in fold 5; 6 in fold 6; 0 in
fold 7) reflects the candidate's session-window precondition
producing few signals on NZD_USD — a property of the strategy, not
the data.

## 8. Committed artifacts (compact)

```
backtests/CAMPAIGN_010_session_breakout/
├── walk_forward/
│   ├── plan.json            # Phase 2
│   ├── plan.md              # Phase 2
│   ├── results.json         # Phase 3 (this phase)
│   ├── results.md           # Phase 3 (this phase)
│   └── fold_detail.json     # Phase 3 (this phase)
└── folds/
    ├── fold_00/             # Phase 3 (this phase)
    │   ├── fold_00_<PAIR>_summary.json   # 7 pairs
    │   └── fold_00_<PAIR>_trades.csv     # 7 pairs
    ├── fold_01/  ...        # ... 8 folds total
    ...
```

Total folds directory size: ~820 KB; full campaign artifact
directory ~892 KB. Equity-curve CSVs were intentionally **not**
emitted (would have added ≈ 60 K bar-level rows per pair-fold,
unnecessary bulk for this verdict).

## 9. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (untouched).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **No broker / OANDA call** — runner reads only the local store.
- **No `.env` read; no credential printed; no account / order /
  trade / position / transaction endpoint queried.**
- **No QuantConnect / LEAN** action.
- **No engine-PnL change.** No `src/forex_bot/financing.py` edit.
  The runner uses `BacktestEngine` and `RiskEngine(mode="backtest")`
  exactly as `scripts/run_campaign_009.py` does.
- **No parameter tuning.** The frozen-parameter assertion in the
  runner aborts before any backtest if a single value drifts.
- **`paper-loop` / `demo-loop` refuse**; no `live-loop` command.

## 10. Explicit no-approval statement

This phase produces *research evidence* — fold-level trade ledgers,
metrics, and a per-fold gate vector. It does not approve the
strategy. The Phase 4 doc
([`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md))
records the formal verdict against
[`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
§10; even a PASS at that step does not approve the strategy — the
six-evidence ladder per
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§8 stands.

## 11. Cross-links

- [`ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_PLAN.md)
- [`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md)
- [`CAMPAIGN_010_WALK_FORWARD_PLAN.md`](CAMPAIGN_010_WALK_FORWARD_PLAN.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`scripts/run_campaign_010.py`](../../scripts/run_campaign_010.py)
- [`backtests/CAMPAIGN_010_session_breakout/walk_forward/results.json`](../../backtests/CAMPAIGN_010_session_breakout/walk_forward/results.json)
- [`backtests/CAMPAIGN_010_session_breakout/walk_forward/results.md`](../../backtests/CAMPAIGN_010_session_breakout/walk_forward/results.md)
- [`backtests/CAMPAIGN_010_session_breakout/walk_forward/fold_detail.json`](../../backtests/CAMPAIGN_010_session_breakout/walk_forward/fold_detail.json)
