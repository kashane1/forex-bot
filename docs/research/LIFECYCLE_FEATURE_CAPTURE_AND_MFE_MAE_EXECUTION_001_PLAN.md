# Lifecycle Feature Capture & MFE/MAE Execution 001 — Plan

**Date:** 2026-05-28
**Branch:** `infra-lifecycle-feature-capture-and-mfe-mae-execution-001`
**Type:** infrastructure / research diagnostics — **NOT a strategy campaign.**

## Purpose

Two goals, continuing `infra-trade-lifecycle-feature-capture-and-stop-diagnostics-001`:

1. **Execute** the previously BLOCKED_LOCAL_DATA per-trade MFE/MAE reconstruction
   for CAMPAIGN_022 against the local materialized M15 store — *if reachable*.
2. **Future-proof** lifecycle diagnostics by adding a reusable feature-capture
   schema and an **opt-in** diagnostic export mode to the C022 runner, so future
   campaigns record MFE/MAE + stop geometry + signal features without a rebuild.

Plus a focused audit of the USD_JPY / USD_CAD R-multiple convention quirk the
prior sprint surfaced.

## Branch base note (important)

The prior sprint branch `infra-trade-lifecycle-feature-capture-and-stop-diagnostics-001`
was **not merged into `main`**, yet this sprint depends on its artifacts
(`src/forex_bot/research/mfe_mae.py`, `trade_lifecycle.py`,
`scripts/reconstruct_mfe_mae_for_campaign_trades.py`, the lifecycle docs). That
prior branch was itself cut from the current `main` HEAD (608eece), so this branch
is based on the prior branch tip (20928c1) = `main` + the prior sprint, with **no
divergence**. All prior artifacts verified present at Phase 0.

## Local data readiness (Phase 0 probe, 2026-05-28)

**Result: BLOCKED_LOCAL_DATA — materialized M15 store unreachable in this checkout.**

- `FOREX_BOT_RESEARCH_DATABASE_URL` — **unset**; no `PG*` env vars; no repo `.env`.
- Postgres *is* listening on `:5432` but every connection (tcp + socket, OS user,
  `postgres` role, `forex_bot` and `postgres` DBs) fails `fe_sendauth: no password
  supplied` — no credentials available here.
- `data/bot.sqlite3` holds **0 candle rows**.
- No local candle corpora on disk (`*.parquet`, `*candle*.csv`, `*m15*`): none found.

→ Phase 1 (MFE/MAE reconstruction) and Phase 5 (stop-model comparison, gated on
Phase 1) remain **BLOCKED_LOCAL_DATA**. Phases 2, 3, 4, 6 do **not** need the DB
and proceed fully. No excursion numbers are fabricated.

**Exact command to unblock locally:**
```bash
# 1. populate a local research Postgres with materialized M15 (one-time):
python scripts/prepare_local_research_data.py            # fetch/import candles
python scripts/materialize_m1_derived_timeframes.py --all-majors
python scripts/verify_m1_materialized_coverage.py
# 2. point the tools at it and run reconstruction:
export FOREX_BOT_RESEARCH_DATABASE_URL=postgresql://<user>:<pass>@localhost/forex_bot
python scripts/reconstruct_mfe_mae_for_campaign_trades.py \
    --campaign-dir backtests/CAMPAIGN_022_h4_h1_pullback_resolution --campaign-id CAMPAIGN_022
```

## Non-goals (explicit)

- **Not** CAMPAIGN_024. **Not** C023 execution. **Not** C022 retuning.
- **Not** a tuning / optimization sprint; no "best" stop selected as tradable.
- **Not** paper / demo / live enablement.
- Does **not** alter any existing strategy verdict or historical C022 metric.

## Safety rules (binding)

- `configs/approved_strategies.yaml` stays `approved: []` (verify only).
- No paper/demo/live; no broker/executor/order/live changes.
- No OANDA mutation/order API calls; no live credentials.
- No committing `.env`, credentials, SQLite DBs, raw candle dumps, huge CSVs, or
  bulky generated artifacts. Diagnostics emit **compact JSON + md** only.
- Any stop-model comparison is labeled **diagnostic / sensitivity**, never an edge.
- Runner retrofit (Phase 4) is **opt-in**; default behavior and frozen C022
  parameters are unchanged; no strategy-logic change.

## Previous-sprint dependency

`docs/research/TRADE_LIFECYCLE_STOP_DIAGNOSTICS_001_SUMMARY.md` and siblings;
`src/forex_bot/research/{trade_lifecycle,mfe_mae}.py`;
`scripts/reconstruct_mfe_mae_for_campaign_trades.py`. All verified present.

## Expected artifacts

- P0: this plan.
- P1: re-run reconstruction → `c022_mfe_mae_summary.json` +
  `CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md` (BLOCKED state here).
- P2: `docs/research/C022_R_MULTIPLE_CONVENTION_AUDIT.md` (+ tests if a bug found).
- P3: `src/forex_bot/research/lifecycle_features.py` (+ tests).
- P4: opt-in diagnostic export in `scripts/run_campaign_022_h4_h1_pullback_resolution.py`
  (+ tests).
- P5: `diagnostic_stop_model_comparison.json` +
  `DIAGNOSTIC_STOP_MODEL_COMPARISON_EXECUTED.md` (only if Phase 1 ran).
- P6: `LIFECYCLE_FEATURE_CAPTURE_AND_MFE_MAE_EXECUTION_001_CONCLUSIONS.md`.
- P7: `LIFECYCLE_FEATURE_CAPTURE_AND_MFE_MAE_EXECUTION_001_SUMMARY.md`.

## Validation commands

```
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

## Phase 0 baseline (pre-existing, unrelated to this sprint)

- freeze / archive / secrets — **ALL PASS**.
- pytest — **1923 passed, 1 skipped, 1 FAILED** (`test_c008_entry_comparison_runs`,
  needs local H4 store; pre-existing).
- ruff — **23 pre-existing errors** in existing C020/C021 fill-timing files & tests.
  New code in this sprint is ruff-clean.

## No-approval / no-tuning statement

This sprint approves no strategy, tunes no campaign, changes no verdict, enables no
trading loop. MFE/MAE and stop-model work is diagnostic. Deliverables are tooling +
diagnostics + a readiness decision, not an edge.
