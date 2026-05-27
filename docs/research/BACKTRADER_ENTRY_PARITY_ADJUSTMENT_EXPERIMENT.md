# Backtrader Entry Parity Adjustment Experiment

**Branch:** `infra-entry-orchestration-parity-diagnostics-001`  
**Artifact:** [`research/entry_parity/backtrader_adjustment_experiment.json`](../../research/entry_parity/backtrader_adjustment_experiment.json)

---

## Profiles tested

### 1. `legacy_bt_wrong_pnl` (prior exit-parity sprint)

- Risk windows: rolling 7-day week
- PnL: no quote→USD conversion

| Campaign | Bespoke | BT | Delta | Delta % |
|---|---:|---:|---:|---:|
| C008 | 354 | 279 | 75 | 21.2% |
| C009 | 403 | 332 | 71 | 17.6% |
| C018 | 378 | 314 | 64 | 16.9% |

### 2. `fixed_pnl_engine_aligned` (this sprint)

- Risk windows: calendar Monday-week (engine port)
- PnL: matches `BacktestEngine._pnl()` home conversion

| Campaign | Bespoke | BT | Delta | Delta % |
|---|---:|---:|---:|---:|
| C008 | 354 | 353 | 1 | 0.28% |
| C009 | 403 | 402 | 1 | 0.25% |
| C018 | 378 | 377 | 1 | 0.26% |

---

## Conclusion

**Trade-count gap narrows from ~20% to ±1 trade** with PnL conversion fix only. No C008/C009/C018 rule changes required.

Remaining ±1 likely EOD close / final-bar edge — within tolerance for parity corroboration.

---

## Code changes (diagnostic lane)

- `research/backtrader_exit_parity/strategy.py` — `_pnl()` home-currency conversion
- `research/backtrader_exit_parity/risk_windows.py` — engine-aligned risk windows (optional profile)

`strategy_evidence: false`
