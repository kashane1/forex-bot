# Observed Cost / Financing Overlay — Local-First Sprint Plan

**Branch:** `infra-observed-cost-financing-overlay-local-first-001`  
**Base:** `infra-shared-audit-warn-remediation-and-next-bar-open-001` @ `8a96f41`  
**Date:** 2026-05-27

## Purpose

Build a **local-first financing and observed-cost overlay framework** that applies to existing campaign trade ledgers **without rerunning strategy logic**. Quantify how spread-adjacent carry (rollover/financing) and hold-duration costs affect prior research evidence, especially weekly/overnight/multi-day strategies.

This sprint produces **infrastructure, diagnostics, and overlay reports** — not new strategy evidence.

## Non-goals

- No CAMPAIGN_020 or new strategy campaign
- No strategy parameter tuning
- No changes to `configs/approved_strategies.yaml` (remains `approved: []`)
- No paper/demo/live enablement
- No broker order/trade/position mutation APIs
- No live credentials
- No verdict rewrites to PASS
- No C019 rerun (overlay on ledger only if useful)

## Safety rules

1. Overlay-only; no backtest engine changes for campaign evidence
2. Local committed fixtures and compact trade CSVs only
3. Financing modes: `none`, `synthetic_fixture`, `manual_observed_fixture`, `unavailable`
4. Synthetic/manual fixtures must be labeled; never treated as broker-observed truth
5. Do not infer tradable edge from financing-adjusted metrics
6. No `.env`, SQLite DBs, raw candle exports, or bulky artifacts committed

## Existing financing modules (inspected)

| Module | Role |
|--------|------|
| `src/forex_bot/financing.py` | Conservative bp/day stress, `risk_usd` |
| `research/financing/overlay.py` | CSV trade load + `apply_financing_overlay` |
| `research/financing/calculator.py` | Daily rollover, triple-swap, weekend skip |
| `research/financing/models.py` | `PositionInterval`, config |
| `research/financing/rates.py` | `default_stress_rate_source()` (synthetic stress) |
| `research/financing/fixtures.py` | `load_rate_fixture`, validation |
| `src/forex_bot/research/financing_overlay.py` | **New** ledger contract + modes |

## Local fixture / data sources

- `research/financing/fixtures/rates_two_week_*.json` — committed synthetic rate tables
- `research/financing/c008_c009_c018_financing_exposure.json` — prior diagnostic overlay
- `research/cost_atlas/` — pair/session spread-ATR compact CSV + JSON
- `backtests/CAMPAIGN_*/**/*_trades.csv` — compact per-pair trade ledgers

## Campaign trade ledgers available

See `docs/research/FINANCING_OVERLAY_LEDGER_INVENTORY.md` (Phase 1). Inventory scan covers C015–C019, C008/C009 forensic, weekly C016/C017 folds.

## Selected reference ledgers

| Label | Campaign | Rationale |
|-------|----------|-----------|
| `c019_train_validation_base` | C019 | Recent H4 mean-reversion reference; multi-day holds |
| `c016_weekly_momentum_folds_base` | C016 | Weekly rebalance; financing-sensitive |
| `c017_weekly_vol_breakout_folds_base` | C017 | Weekly breakout family |
| `c008_deduped_forensic_train` | C008 | Prior financing diagnostic baseline |

## Expected overlay modes

- `none` — gross R only (baseline)
- `synthetic_fixture` — `default_stress_rate_source()` (conservative stress, labeled synthetic)
- `manual_observed_fixture` — merged `rates_two_week_*.json` (diagnostic schedules, not broker history)
- `unavailable` — fail-closed; no silent financing

## Expected artifacts

Under `research/financing_overlay_local_first/`:

- `run_manifest.json`
- `ledger_inventory_used.json`
- `overlay_summary_by_campaign.json`
- `overlay_summary_by_pair.csv`
- `overlay_summary_by_hold_bucket.csv`
- `adjusted_metric_delta.json`
- `unavailable_rates_report.json`

Large per-trade outputs → `research/financing_overlay_local_first/local_adjusted_trades/` (gitignored).

## Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
python scripts/apply_financing_overlay_to_trade_ledgers.py
```

## Prior docs verified

- `docs/research/SHARED_AUDIT_WARN_REMEDIATION_AND_NEXT_BAR_OPEN_001_SUMMARY.md`
- `docs/research/NEXT_BAR_OPEN_REFERENCE_COMPARISON_RESULT.md`
- `docs/research/CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_WARN_REMEDIATION.md`
- `docs/research/OBSERVED_COST_FINANCING_OVERLAY_NEXT_SCOPE.md`
- `docs/research/COST_SPREAD_SLIPPAGE_FINANCING_AUDIT_RESULT.md`

## Baseline validation (Phase 0)

| Check | Result |
|-------|--------|
| Branch | `infra-observed-cost-financing-overlay-local-first-001` |
| `approved_strategies.yaml` | `approved: []` |
| pytest | 1744 passed |
| research freeze / archive | PASS |
| secret scan | PASS (pattern; no live creds in env) |

## No-approval statement

**No strategy is approved by this sprint.** Financing-adjusted metrics are diagnostic infrastructure only. C019 remains **REJECT**. CAMPAIGN_020 is not created.
