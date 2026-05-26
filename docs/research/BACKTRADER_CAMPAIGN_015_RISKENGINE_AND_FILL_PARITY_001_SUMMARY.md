# Backtrader CAMPAIGN_015 RiskEngine & Fill Parity 001 — Summary

**Branch:** `infra-backtrader-campaign-015-riskengine-and-fill-parity-001`
**Date:** 2026-05-26
**Verdict label:** `BT_PARITY_STILL_DIVERGED`

## Commits by phase

| phase | commit | summary |
|---|---|---|
| 0 | `28ec6f5` | Phase 0 plan doc |
| 1 | `db6bf47` | Entry-bar stop policy + tests |
| 2 | `40cafc3` | RiskEngine parity layer + CLI |
| 3–8 | (this commit) | Preflight/run/comparison docs + aggregation fix + parity summary |

## Files changed (code)

- `research/backtrader_lane/risk_parity.py` — new read-only RiskEngine wrapper
- `research/backtrader_lane/strategies/campaign_015_failed_breakout_reversal.py` — parity kwargs
- `research/backtrader_lane/runner.py` — RunOptions, manifest, rejection aggregation fix
- `scripts/run_backtrader_parity.py` — CLI flags
- `tests/unit/backtrader_lane/test_campaign_015_entry_bar_stop_policy.py`
- `tests/unit/backtrader_lane/test_campaign_015_risk_parity.py`

## Commands run

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py

python scripts/run_backtrader_parity.py ... --dry-run
python scripts/run_backtrader_parity.py ... --entry-bar-stop-policy bespoke_current_no_entry_bar_stop --risk-engine-parity
python scripts/compare_campaign_015_fold_windows.py ...
```

## Entry-bar stop policy

- Added `entry_bar_stop_policy` with `backtrader_default` (legacy) and
  `bespoke_current_no_entry_bar_stop` (parity).
- Parity mode skips entry-bar adverse stop; later-bar stops unchanged.

## RiskEngine parity

- Read-only `RiskEngine.evaluate` at next-bar-open fill using local CSV bid/ask.
- Rejection counts: SPREAD_TOO_WIDE 55, SPREAD_TO_ATR 63, SESSION_BLOCKED 27.
- No broker/OANDA/execution imports.

## Trade counts

| lane | trades |
|---|---:|
| BT prior fold-window | 532 |
| BT parity fold-window | **416** |
| Bespoke rehydrate | **164** |

Gap: 368 → **252** (−116).

## Classification

| when | label |
|---|---|
| Before | SIGNAL_RULE_MISMATCH (532 vs 164) |
| After | SIGNAL_RULE_MISMATCH (416 vs 164) |

## First divergence

Prior `same_bar_adverse_stop` entry-bar mismatch **expected resolved** under parity policy.

## Fill semantics audit

Precommit `same_bar_adverse_stop_wins` vs bespoke entry-bar behaviour is **ambiguous**.
Recommend deferring bespoke engine correction to a separate sprint.

## Approval / safety

- CAMPAIGN_015: **unapproved**
- Paper / demo / live: **blocked**
- `configs/approved_strategies.yaml`: `approved: []`

## Recommended next step

Debug remaining BT parity (CSV/sqlite spread alignment, session timing, position-state).

## Review first

1. `docs/research/BACKTRADER_CAMPAIGN_015_RISKENGINE_AND_FILL_PARITY_RESULT.md`
2. `docs/research/BACKTRADER_CAMPAIGN_015_RISKENGINE_FILL_COMPARISON.md`
3. `docs/research/CAMPAIGN_015_ENTRY_BAR_STOP_SEMANTICS_AUDIT.md`
4. `research/campaign_015/diagnostics/backtrader_fold_window_riskengine_fill_parity/parity_run_summary.json`
5. `research/backtrader_lane/risk_parity.py`
