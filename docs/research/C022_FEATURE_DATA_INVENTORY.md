# C022 Feature-Data Inventory

**Status:** diagnostic-only. No verdict change, no approval, no tuning, no C024.
Part of `research-c022-winner-loser-feature-separation-001`, Phase 1.

Goal: determine exactly what entry-time feature data is available now for a
C022 winner/loser feature-separation study, what is missing, and what is
reconstructable read-only from the local materialized DB without touching
strategy logic.

## Existing C022 artifacts

| Artifact | Location | Per-trade? | Committed? |
|---|---|---|---|
| Base trade CSVs (7 pairs × {train, validation}) | `backtests/CAMPAIGN_022_h4_h1_pullback_resolution/{split}/base/*_trades.csv` | yes | **no** — gitignored; present on disk in main checkout (2396 base trades) |
| Stress-2x trade CSVs | `…/{split}/stress_2x/*_trades.csv` | yes | no — gitignored |
| MFE/MAE reconstruction | `research/trade_lifecycle_diagnostics/c022_mfe_mae_summary.json` | **no — aggregate only** | yes |
| Stop-model comparison | `research/trade_lifecycle_diagnostics/diagnostic_stop_model_comparison.json` | no — aggregate | yes |
| Stop-exit summary | `research/trade_lifecycle_diagnostics/stop_exit_summary.{json,md}` | no — aggregate | yes |
| Campaign metrics / cells | `research/campaign_022/…` | no — aggregate | yes |
| Lifecycle feature CSVs (`--emit-lifecycle-features`) | — | — | **none exist anywhere** |

### Key conclusions

1. **Per-trade MFE/MAE records do not exist** — only the aggregate
   `c022_mfe_mae_summary.json`. Per-trade MFE/MAE is **reconstructable** from
   post-entry M15 candles via `forex_bot.research.mfe_mae.compute_mfe_mae`
   (already unit-tested), using the same read-only materialized store the
   reconstruction summary used.
2. **No lifecycle feature CSVs have ever been generated.** The
   `--emit-lifecycle-features` opt-in flag on the C022 runner post-processes the
   trades dataframe through `records_from_trade_rows`, which **leaves all numeric
   HTF/M15 entry features and MFE/MAE as `None`** (see
   `src/forex_bot/research/lifecycle_features.py:record_from_trade_row`). It adds
   nothing beyond the columns already in the trades CSV plus derived
   `session_bucket`/`weekday`/`stop_distance_pips`/corrected `result_r`.
3. **The C022 runner can be run in `--emit-lifecycle-features` diagnostic mode
   without changing strategy logic or frozen parameters**, but doing so would
   re-execute the (deterministic, results-identical) strategy and reproduce the
   trades CSVs that already exist on disk — and it would still not populate the
   numeric HTF features. Therefore re-running is unnecessary; this sprint reads
   the existing on-disk trades CSVs read-only and reconstructs the numeric
   entry-time features independently from the DB.

## Available per-trade fields (directly from trades CSV)

`instrument`, `side`, `units`, `entry_time`, `exit_time`, `entry_price`,
`exit_price`, `stop_price`, `pnl`, `r_multiple`, `bars_held`,
`spread_paid_pips`, `exit_reason`, `fill_timing`, `ambiguous_exit`, `gap_fill`,
`protective_stop_*`, `thesis_invalidation_exit`, `zscore_at_exit`.

Trivially derivable from `entry_time` with no lookahead: `session_bucket`,
`weekday`, `hour`. Derivable from prices: `stop_distance_pips`, corrected
pair-agnostic `result_r` (`price_based_r`).

## Field availability map (target schema for separation study)

Legend — **CSV**: in trades CSV; **DB**: reconstructable read-only from
materialized M15/H1/H4 at decision time; **none**: not available without
instrumented strategy export.

| Field | Source | Lookahead-safe? | Notes |
|---|---|---|---|
| campaign_id, split, instrument, side | CSV / path | yes | |
| entry_time, exit_time, entry/exit price, stop_price | CSV | yes | |
| result_r | CSV (recomputed) | label | outcome — used as label, not feature |
| exit_reason, bars_held | CSV | label | outcome-adjacent — labels, not features |
| spread_pips | CSV | yes | known at/just-before entry |
| mfe_r, mae_r, reached_+{0.25,0.5,1.0}R, touched_−{0.5,0.9}R | **DB** (mfe_mae) | label | post-entry path — labels only |
| atr_at_entry | **DB** (M15) | yes | prior-bar ATR at decision bar |
| m15_adx_at_entry | **DB** (M15) | yes | |
| m15_reclaim_distance_atr | **DB** (M15) | yes | dist of reclaim close to EMA20 / ATR |
| spread_to_atr_pct | CSV + **DB** | yes | spread_pips ÷ atr_pips |
| volatility_regime | **DB** (M15) | yes | ATR percentile bucket (in-sample percentile noted) |
| h4_adx_at_entry | **DB** (H4) | yes | last completed H4 bar ≤ decision |
| h4_bias_score | **DB** (H4) | yes | bull−bear vote score (−3…+3) |
| h4_ema_slope | **DB** (H4) | yes | EMA50 slope over slope_bars |
| h4_close_dist_ema50_atr | **DB** (H4) | yes | |
| h1_rsi_at_entry | **DB** (H1) | yes | |
| h1_pullback_depth_atr | **DB** (H1) | yes | min low→EMA50 (long) over lookback / ATR |
| h1_close_dist_ema50_atr | **DB** (H1) | yes | |
| session_bucket, weekday, hour | derived | yes | from entry_time (UTC) |
| h1_feature_time, h4_feature_time | **DB** (alignment) | yes | provenance of HTF bar used |

### Missing / requires instrumented export

No field in the target schema is strictly *unrecoverable*, but two caveats:

- The **exact** decision-time numeric values the strategy used internally
  (h4 ADX, slope, h1 RSI, reclaim distance) were **not persisted** — the signal
  only carries categorical `h4_bias` and `h1_pullback_holds`. We therefore
  **reconstruct** these numerics from the DB at the decision bar, reusing the
  strategy's own indicator/alignment helpers without editing the strategy. This
  is a faithful, lookahead-safe **approximation**; an exact match would require a
  future instrumented `--emit-lifecycle-features` that writes the numerics. The
  reconstruction is sufficient for a diagnostic separation study and is labeled
  as such everywhere.
- `protective_stop_arm_mfe_r` is present but only populated for the (rare)
  protective-stop-armed trades; it is not a general MFE proxy.

## Lookahead policy for reconstruction

- The trades CSV `entry_time` is the **fill** time (`fill_timing =
  next_bar_open`); the signal was decided on the prior completed M15 bar.
  Reconstruction computes M15 indicators on bars with `time < entry_time` (the
  decision bar and earlier) and HTF features on the last completed H4/H1 bar at
  or before the decision time. No bar at/after the fill is used for any feature.
- Outcome fields (result_r, mfe_r, mae_r, exit_reason, bars_held, threshold
  flags) are **labels only** and never enter feature scoring.

## Decision

Sufficient data exists to build a compact per-trade feature dataset
(2396 base trades) with reconstructed entry-time features + reconstructed
per-trade MFE/MAE labels, entirely read-only, with no strategy change and no
verdict impact. Proceed to Phase 2.
