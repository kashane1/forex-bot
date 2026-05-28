# Trade Lifecycle & Stop Diagnostics 001 — Plan

**Date:** 2026-05-28
**Branch:** `infra-trade-lifecycle-feature-capture-and-stop-diagnostics-001`
**Type:** Infrastructure / research diagnostics — **NOT a strategy campaign.**

## Purpose

The project has spent many campaigns (C015–C023) on *entry logic* and every
one has been REJECT or scaffold-only. C022's behavior diagnostics
(`CAMPAIGN_022_BEHAVIOR_DIAGNOSTICS.md`) show a 60% hard-stop / 40% time-stop
exit mix where stops average −0.86R and time-exits average +0.96R — i.e. the
edge, where it exists, is *slow* and is being cut off by the stop. That is a
**trade-lifecycle** observation, not an entry observation.

This sprint builds **local-only, read-only** trade-lifecycle and stop-loss
diagnostics tooling that can:

1. inventory what trade-level data already exists across recent campaigns,
2. normalize existing trade artifacts into a reusable lifecycle schema,
3. produce stop/exit diagnostics from *realized* outcomes,
4. assess whether per-bar MFE/MAE reconstruction is feasible from local
   materialized candles (and do it for C022 only if local data is present),
5. compare stop models **diagnostically** (sensitivity only, never as an edge),
6. recommend what every future campaign must capture before C024 is designed.

## Non-goals (explicit)

- **Not** CAMPAIGN_024. No new campaign is created.
- **Not** an execution of CAMPAIGN_023 (ADX22) evidence.
- **Not** a rerun of C022 as a tuned strategy.
- **Not** a tuning / optimization sprint. No "best stop" is selected to promote.
- **Not** a paper / demo / live enablement sprint.
- Does **not** alter any existing strategy verdict.

## Safety rules (binding)

- `configs/approved_strategies.yaml` stays `approved: []` (verify only).
- No paper / demo / live enablement.
- No broker / executor / order / live behavior changes.
- No OANDA mutation / order API calls. No live credentials.
- No committing of `.env`, credentials, SQLite DBs, raw candle dumps, huge
  CSVs, or bulky generated artifacts. Diagnostics emit **compact JSON + md**.
- Any hypothetical stop comparison is labeled **diagnostic / sensitivity**,
  never a campaign verdict and never an edge claim.
- No optimizing stop parameters after seeing results and presenting as edge.

## Source campaigns

| campaign | verdict (manifest) | trade artifacts |
|---|---|---|
| C019 | (rejected, see status) | check inventory |
| C020 | REJECT | check inventory |
| C021 | REJECT (train-only) | check inventory |
| C022 | REJECT | per-pair `*_trades.csv` under `backtests/CAMPAIGN_022_h4_h1_pullback_resolution/{train,validation}/base/` + 2× stress |
| C023 | SCAFFOLD_ONLY | none — not executed, no trades |

C022 trade CSV schema (confirmed Phase 0):
`instrument, side, units, entry_time, exit_time, entry_price, exit_price,
stop_price, pnl, r_multiple, bars_held, spread_paid_pips, exit_reason,
fill_timing, ambiguous_exit, gap_fill, gap_fill_distance_pips,
protective_stop_armed, protective_stop_arm_time, protective_stop_arm_mfe_r,
protective_stop_exit, thesis_invalidation_exit, zscore_at_exit`.

**Present:** entry/exit time+price, initial stop_price, r_multiple, bars_held,
spread, exit_reason, side. **Absent:** full per-trade MFE/MAE, H4 ADX at entry,
H1 pullback depth, M15 reclaim distance, session bucket, volatility regime.
(`protective_stop_arm_mfe_r` is a partial, conditional MFE proxy only.)

## Lifecycle questions this sprint scopes

Is C022's (and the broader entry-research cluster's) failure driven by:
entry timing · initial stop placement · stop distance · stop-model mismatch ·
time stop · exit logic · pair/session/regime concentration · spread/cost drag ·
or absence of true edge?

## Expected artifacts

- `scripts/inventory_trade_lifecycle_artifacts.py` → `research/trade_lifecycle_diagnostics/artifact_inventory.json` + `docs/research/TRADE_LIFECYCLE_ARTIFACT_INVENTORY.md`
- `src/forex_bot/research/trade_lifecycle.py` (+ tests) — `TradeLifecycleRecord` + loaders
- `scripts/analyze_trade_lifecycle_stops.py` → `research/trade_lifecycle_diagnostics/stop_exit_summary.{json,md}`
- `docs/research/MFE_MAE_RECONSTRUCTION_FEASIBILITY.md` + `src/forex_bot/research/mfe_mae.py` (+ synthetic-candle tests)
- (conditional) `scripts/reconstruct_mfe_mae_for_campaign_trades.py` → `c022_mfe_mae_summary.json` + `docs/research/CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md`, else BLOCKED_LOCAL_DATA note
- (conditional) `docs/research/DIAGNOSTIC_STOP_MODEL_COMPARISON.md` + json
- `docs/research/TRADE_LIFECYCLE_IMPROVEMENT_ROADMAP.md`
- `docs/research/TRADE_LIFECYCLE_STOP_DIAGNOSTICS_001_SUMMARY.md`

## Validation commands (run at Phase 0 baseline and Phase 8)

```
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

## Phase 0 baseline result (pre-existing state on this commit, == main)

- `check_research_freeze.py` — **ALL CHECKS PASSED**
- `validate_research_archive.py` — **ALL CHECKS PASSED**
- `scan_artifacts_for_secrets.py` — **PASSED** (value scan skipped, no creds in env)
- `pytest` — **1902 passed, 1 skipped, 1 FAILED** → `tests/unit/entry_parity/test_compare_entries.py::test_c008_entry_comparison_runs` (`bespoke_entry_count == 0`; requires local H4 store / bespoke C008 entries absent in this checkout). **Pre-existing, unrelated to this sprint.**
- `ruff check` — **23 pre-existing errors** (unused imports / unsorted import blocks / ambiguous `l` names in existing C020/C021 fill-timing files and their tests). **Pre-existing, unrelated to this sprint.** New code in this sprint will be ruff-clean.

## No-approval / no-tuning statement

This sprint approves no strategy, tunes no campaign, changes no verdict, and
enables no trading loop. All stop-model comparisons are diagnostic sensitivity
analyses. The deliverable is **tooling + diagnostics + a roadmap**, not an edge.
