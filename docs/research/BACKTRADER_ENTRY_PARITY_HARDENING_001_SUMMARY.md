# Backtrader Entry Parity Hardening 001 — Summary

**Branch:** `infra-backtrader-entry-parity-hardening-001`  
**Date:** 2026-05-27  
**Evidence class:** `parity_diagnostic_only` — `strategy_evidence: false`

---

## 1. Branch name

`infra-backtrader-entry-parity-hardening-001` (branched from `infra-entry-orchestration-parity-diagnostics-001`)

---

## 2. Commit hashes by phase

| Phase | Commit | Description |
|---|---|---|
| 0 | `25d17a8` | Plan + truth audit |
| 1 | `d22f8e5` | PnL module + tests + engine-aligned default |
| 2 | `6a306f1` | Refreshed exit parity artifacts |
| 3 | `5810ada` | Refreshed entry parity comparison |
| 4 | `dd1ccc2` | Parity hardened status memo |
| 5 | `92b8edb` | Archive/backlog updates |
| 6 | *(this commit)* | Final validation + summary |

---

## 3. Files changed by phase

| Phase | Key files |
|---|---|
| 0 | `docs/research/BACKTRADER_ENTRY_PARITY_HARDENING_001_PLAN.md` |
| 1 | `research/backtrader_exit_parity/pnl.py`, `strategy.py`, `runner.py`, `tests/unit/backtrader_exit_parity/test_pnl_home_currency.py` |
| 2 | `research/backtrader_exit_parity/c008|c009|c018_parity_summary.json`, `*_parity_trades.jsonl`, `exit_reason_comparison.csv`, `parity_run_manifest.json` |
| 3 | `research/entry_parity/entry_timestamp_comparison.json`, `.csv`, `backtrader_adjustment_experiment.json`, `docs/research/BACKTRADER_ENTRY_PARITY_HARDENING_RESULT.md` |
| 4 | `docs/research/BACKTRADER_PARITY_HARDENED_STATUS.md` |
| 5 | `docs/research/EVIDENCE_INDEX.md`, `EVIDENCE_MANIFEST.json`, `FUTURE_RESEARCH_BACKLOG.md` |
| 6 | `docs/research/BACKTRADER_ENTRY_PARITY_HARDENING_001_SUMMARY.md` |

---

## 4. PnL conversion fix summary

Extracted `pnl_home_currency()` in `research/backtrader_exit_parity/pnl.py` mirroring
`BacktestEngine._pnl`:

- **USD-quote pairs** (EUR_USD, GBP_USD, …): gross PnL already in USD.
- **USD-base pairs** (USD_JPY, USD_CAD, USD_CHF): divide quote-currency gross by exit price.
- **Cross pairs** (e.g. GBP_JPY): raise `ValueError` — same limitation as bespoke engine.

Mode: `home_currency_v1`. Default risk windows: `engine_aligned` (calendar Monday-week).

---

## 5. Tests added/updated

- **New:** `tests/unit/backtrader_exit_parity/test_pnl_home_currency.py` (7 tests)
  - EUR_USD unchanged
  - USD_JPY / USD_CAD / USD_CHF conversion
  - Unsupported cross raises
  - JPY drawdown inflation regression
  - Correct PnL keeps drawdown below limit
- **Updated:** `tests/unit/entry_parity/test_pnl_conversion.py` imports `pnl_home_currency`

**Total test suite:** 1708 passed (7 new tests).

---

## 6. C008 refreshed parity result

| Metric | Bespoke | Backtrader |
|---|---:|---:|
| Total trades | 354 | 353 |
| Exit verdict | — | CLOSE_MATCH |
| Stop share | 68.27% | 68.27% |
| Time share | 31.44% | 31.44% |

---

## 7. C009 refreshed parity result

| Metric | Bespoke | Backtrader |
|---|---:|---:|
| Total trades | 403 | 402 |
| Exit verdict | — | CLOSE_MATCH |
| Stop share | 56.47% | 56.47% |
| Target share | 40.80% | 40.80% |

---

## 8. C018 refreshed parity result

| Metric | Bespoke | Backtrader |
|---|---:|---:|
| Total trades | 378 | 377 |
| Exit verdict | — | CLOSE_MATCH |
| Protective stop share | 38.20% | 38.20% |
| Stop share | 46.15% | 46.15% |

---

## 9. Entry gap after hardening

| Campaign | Gap | BT-only | Common |
|---|---:|---:|---:|
| C008 | 1 | 0 | 353 |
| C009 | 1 | 0 | 402 |
| C018 | 1 | 0 | 377 |

Single shared bespoke-only entry: GBP_USD 2024-01-16T06:00:00+00:00 (validation).

---

## 10. Exit-reason comparison after hardening

All campaigns **CLOSE_MATCH**. Train splits PASS exact match. Validation splits
within ≤0.46 pp share delta. See `research/backtrader_exit_parity/exit_reason_comparison.csv`.

---

## 11. Final parity status

**HARDENED — VIABLE** for C008/C009/C018 within ±1 trade tolerance. Independent
Backtrader parity lane established for these campaigns only.

---

## 12. Custom engine bug suspected

**No.**

---

## 13. Campaign verdict changed

**No.** C008/C009/C018 remain REJECT.

---

## 14. Strategy approved

**No.** `configs/approved_strategies.yaml` → `approved: []`.

---

## 15. CAMPAIGN_019 created

**No.**

---

## 16. Paper/demo/live blocked

**Yes.**

---

## 17. Archive/freeze validation results

| Check | Result |
|---|---|
| `pytest tests/ -q` | 1708 passed |
| `ruff check src tests scripts research` | PASS |
| `check_research_freeze.py` | ALL CHECKS PASSED |
| `validate_research_archive.py` | ALL CHECKS PASSED (after summary committed) |
| `scan_artifacts_for_secrets.py` | PASSED |

---

## 18. Remaining limitations

1. One unexplained bespoke-only GBP_USD entry across all three campaigns.
2. Parity lane not generalized beyond C008/C009/C018.
3. Non-USD cross pairs unsupported (by design, matches bespoke).
4. Manual financing sample remains paused.

---

## 19. Recommended next sprint and why

**`research-exit-hypothesis-precommit-002`**

Parity lane is hardened (±1 trade, CLOSE_MATCH exits). Exit pathology was
previously corroborated; next logical step is pre-commit exit hypothesis variants
on the validated baseline rather than further infrastructure work.

---

## 20. Files to review first

1. [`docs/research/BACKTRADER_PARITY_HARDENED_STATUS.md`](BACKTRADER_PARITY_HARDENED_STATUS.md)
2. [`research/backtrader_exit_parity/pnl.py`](../../research/backtrader_exit_parity/pnl.py)
3. [`research/backtrader_exit_parity/parity_run_manifest.json`](../../research/backtrader_exit_parity/parity_run_manifest.json)
4. [`research/entry_parity/entry_timestamp_comparison.json`](../../research/entry_parity/entry_timestamp_comparison.json)
5. [`docs/research/BACKTRADER_ENTRY_PARITY_HARDENING_RESULT.md`](BACKTRADER_ENTRY_PARITY_HARDENING_RESULT.md)
