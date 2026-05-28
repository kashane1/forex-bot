# C022 Winner/Loser Feature-Separation — Sprint 001 Plan

**Status:** diagnostic-only research. Approves nothing, changes no verdict, tunes
no parameter, creates no campaign.

**Branch:** `research-c022-winner-loser-feature-separation-001`

---

## Purpose

CAMPAIGN_022 (`h4_h1_pullback_resolution_entry 0.1.0-c022`) is **REJECT**. The
lifecycle / MFE-MAE sprint
([`LIFECYCLE_FEATURE_CAPTURE_AND_MFE_MAE_EXECUTION_001_CONCLUSIONS.md`](LIFECYCLE_FEATURE_CAPTURE_AND_MFE_MAE_EXECUTION_001_CONCLUSIONS.md))
concluded the failure is an **entry-edge / signal-quality** problem, not a
stop-placement problem: every ATR-stop variant (1.5x–3.0x), time-to-invalidation
variant, and even a cost-free mid-price baseline stayed negative.

This sprint asks the next honest question: **do any entry-time features
distinguish C022 winners from losers?** If a feature family separates winners
from losers *stably* (train *and* validation), with plausible market logic and
no outcome leakage, that would justify drafting — in a *separate, later* sprint —
a pre-committed C024 entry-filter thesis. If nothing separates, the
pullback-resolution family (C022/C023) should be paused or retired.

The deliverable is an **honest feature-separation report and a C024-readiness
decision**, not a campaign.

## Prior evidence summary

From [`CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md`](CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md)
(2311/2396 base trades reconstructed):

- Hard-stopped trades: 45.9% never reached +0.25R before stop; 54% reached
  +0.25R; 37% reached +0.5R; 16% reached +1.0R; mean MFE-before-stop ≈ +0.47R.
- Time-exit winners: mean MAE ≈ −0.40R; only 4.7% ever touched −0.9R.
- Stop-outs broadly uniform across pairs and sides.
- Diagnostic stop-model comparison: all variants negative, including cost-free.

Interpretation already on record: stop geometry is second-order; the entry edge
is the problem. C023 ADX22 remains deferred; no C024 exists.

## Hard non-goals (this sprint will NOT)

- Create CAMPAIGN_024 (or any campaign).
- Execute CAMPAIGN_023.
- Retune C022 or change any frozen parameter.
- Modify any existing campaign verdict or rewrite any historical metric.
- Change `configs/approved_strategies.yaml` except to verify it stays `approved: []`.
- Enable paper/demo/live, or modify any broker/executor/order/live path.
- Call any OANDA mutation/order API, or use live credentials.
- Select "best" thresholds from the data and present them as edge.

Any C024 hypothesis that emerges is **hypothesis-generating only** and must be
pre-committed in a future sprint before any execution.

## Safety rules

- Local materialized M15/H1/H4 read **only**, via the already-authorized,
  gitignored `.env` symlinks. Never print, log, or commit a credential value.
- No fabricated data. Where a feature is unavailable, count it explicitly.
- Do not commit `.env`, credentials, SQLite/Postgres dumps, raw candle dumps,
  large CSVs, or bulky generated artifacts. Compact summaries + a small sampled
  preview only; gitignore the full local dataset.

## Data situation (audited in Phase 0)

- Materialized M15/H1/H4 candles are **reachable** read-only (probe: EUR_USD
  2021-06→2023-12 returned 59218 M15 / 13654 H1 / 4031 H4 candles).
- C022 per-trade `*_trades.csv` files are **gitignored** and absent from a fresh
  checkout, but exist on disk in the main checkout from the lifecycle sprint
  (14 base files, 2396 base trades, train+validation, 7 pairs). They will be
  read **read-only**; never copied into the repo.
- Trades CSV columns: instrument, side, units, entry/exit time+price, stop_price,
  pnl, r_multiple, bars_held, spread_paid_pips, exit_reason, fill_timing, …
  **No numeric HTF entry features are persisted** — the strategy computes h4_adx,
  h4 EMA slope, h1 RSI, pullback depth, m15 reclaim distance at decision time but
  only emits the *categorical* `h4_bias` / `h1_pullback_holds` to the signal.
- Per-trade MFE/MAE is **reconstructable** from M15 (the committed
  `c022_mfe_mae_summary.json` is aggregate-only; no per-trade dump exists).

## Feature families to inspect

- **H4 regime:** H4 ADX at entry, H4 bias vote score, H4 EMA50 slope, H4 close
  distance from EMA50.
- **H1 pullback:** H1 pullback depth (ATR units), H1 RSI at entry, H1 close
  distance to EMA50.
- **M15 trigger:** reclaim distance (ATR units), M15 ADX at entry, candle
  body/ATR, distance from EMA20/EMA50.
- **Volatility / cost:** ATR at entry, spread/ATR, volatility regime.
- **Time:** session bucket, weekday, hour.
- **Pair / side:** instrument, long/short.

Numeric HTF/M15 entry features will be **reconstructed read-only from the DB at
each trade's decision time**, reusing the strategy's own indicator/alignment
helpers (`aligned_h4_bias` building blocks, `ema/atr/adx/rsi`,
`align_last_completed`) **without modifying the strategy**. This is a lookahead-
safe reconstruction approximation (last-completed HTF bars at/before entry) and
will be documented as such. The strategy file is never edited.

## Method guardrails (anti-overfit)

- Entry-time features only in separation scoring; outcome fields (result_r,
  mfe_r, mae_r, exit_reason, bars_held) are **labels**, never features.
- Report effect direction in **train and validation separately**; a feature is
  only "interesting" if the direction agrees across splits.
- No threshold is selected as a campaign parameter. Any post-hoc cut is flagged
  hypothesis-generating only.
- "Edge" is claimed only if separation is strong, stable, plausible, and not
  pair/session overfit.

## Expected artifacts

- `docs/research/C022_WINNER_LOSER_FEATURE_SEPARATION_001_PLAN.md` (this file)
- `docs/research/C022_FEATURE_DATA_INVENTORY.md` (Phase 1)
- `scripts/build_c022_feature_separation_dataset.py` (Phase 2)
- `research/c022_feature_separation/feature_dataset_manifest.json` (Phase 2)
- compact dataset preview + summary stats (Phase 2; full local dataset gitignored)
- `src/forex_bot/research/feature_separation.py` + tests (Phase 3)
- `scripts/analyze_c022_feature_separation.py` (Phase 4)
- `research/c022_feature_separation/feature_separation_summary.json` (Phase 4)
- `docs/research/C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md` (Phase 4)
- `docs/research/C024_READINESS_FROM_C022_FEATURE_SEPARATION.md` (Phase 5)
- `docs/research/C022_WINNER_LOSER_FEATURE_SEPARATION_001_SUMMARY.md` (Phase 6)

## Validation commands (run each phase / at close)

```
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

## Explicit statement

This sprint produces diagnostics only. **No strategy is approved. No verdict
changes. No parameter is tuned. No CAMPAIGN_024 is created. C023 is not
executed. Paper/demo/live remain blocked.**

## Known pre-existing failures (Phase 0 baseline, unrelated to this sprint)

Observed on a clean `main` HEAD before any sprint change:

- `ruff check src tests scripts research`: 23 pre-existing lint errors (unused
  imports, import sorting, ambiguous `l` names) across `tests/`, `scripts/`,
  `src/`, `research/`. Not introduced here; this sprint will not add new ones.
- `pytest`: 1 pre-existing failure
  `tests/unit/entry_parity/test_compare_entries.py::test_c008_entry_comparison_runs`
  (`bespoke_entry_count > 0` → 0). Data-dependent: needs C008 entry CSVs that are
  gitignored/absent in a fresh worktree. 1 skip (`local H4 store absent`).
