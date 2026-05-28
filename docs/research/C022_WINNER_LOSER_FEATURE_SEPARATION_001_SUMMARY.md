# C022 Winner/Loser Feature-Separation — Sprint 001 Summary

**Status:** diagnostic-only sprint complete. No strategy approved, no verdict
changed, no parameter tuned, no CAMPAIGN_024 created, C023 not executed,
paper/demo/live still blocked.

## 1. Branch

`research-c022-winner-loser-feature-separation-001` (off `main` @ 88c2432).

## 2. Commit hashes by phase

| Phase | Hash | Title |
|---|---|---|
| 0 | `fa78c96` | branch, audit, plan |
| 1 | `805f01e` | feature-data inventory |
| 2 | `a7f3bca` | reconstruct per-trade feature dataset |
| 3 | `553bfee` | diagnostic labels (no lookahead leakage) |
| 4 | `ec1047a` | feature-separation analysis |
| 5 | `0f4d8c2` | C024 readiness = NOT_READY |
| 6 | _this commit_ | final validation + summary |

## 3. Files changed by phase

- **0:** `docs/research/C022_WINNER_LOSER_FEATURE_SEPARATION_001_PLAN.md`
- **1:** `docs/research/C022_FEATURE_DATA_INVENTORY.md`
- **2:** `src/forex_bot/research/c022_entry_features.py`,
  `scripts/build_c022_feature_separation_dataset.py`, `.gitignore`,
  `research/c022_feature_separation/{feature_dataset_manifest.json,feature_summary_stats.json,c022_lifecycle_features_preview.csv}`
- **3:** `src/forex_bot/research/feature_separation.py`,
  `tests/unit/test_c022_feature_separation.py`
- **4:** `scripts/analyze_c022_feature_separation.py`,
  `research/c022_feature_separation/feature_separation_summary.json`,
  `docs/research/C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md`
- **5:** `docs/research/C024_READINESS_FROM_C022_FEATURE_SEPARATION.md`
- **6:** this file

The full per-trade dataset
(`research/c022_feature_separation/c022_lifecycle_features.parquet`, ~468 KB) is
**gitignored** and local-only; only the manifest, summary stats, and a 70-row
stratified preview are committed.

## 4. Was local data available?

**Yes.** Materialized M15/H1/H4 candles were reachable read-only via the
authorized, gitignored `.env` symlinks (probe: EUR_USD 2021-06→2023-12 returned
59218 M15 / 13654 H1 / 4031 H4). The C022 base trade CSVs (gitignored) were
present on disk in the main checkout and read read-only.

## 5. Were lifecycle feature records generated?

**Yes — reconstructed read-only**, not via `--emit-lifecycle-features` (that flag
leaves numeric HTF features `None`). Numeric entry-time features were
reconstructed at each trade's decision bar from the materialized frames, reusing
the strategy's own indicator/alignment helpers **without editing strategy logic**.
Per-trade MFE/MAE was reconstructed from post-entry M15 candles.

## 6. Dataset row count and missingness

2396 base trades (train 1369, validation 1027). Entry-feature missingness: **0**.
MFE/MAE: OK on 2311, NO_BARS on 85 — exactly matching the committed aggregate
`c022_mfe_mae_summary.json`. **Alignment sanity check: reconstructed H4 bias
matched the trade side for 100% of trades**, confirming the reconstruction is
faithful.

## 7. Labels created

`profitable_trade` (781), `survived_to_time_exit` (957), `hard_stop_loss`
(1439), `reached_plus_0_5r` (1389), `clean_winner` (485), `straight_to_stop`
(706). Labels are post-hoc (outcome-based) by design — diagnostic only, kept
strictly out of feature scoring via a `FEATURE_DENYLIST`.

## 8. Strongest feature-separation findings

Winner = `result_r > 0` (overall win rate 32.6%). Effect = |AUC−0.5|.

- **Structural entry-signal features carry no winner/loser signal** — all at
  AUC ≈ 0.50 (H4 ADX 0.515/0.501, H4 bias score 0.515/0.484, H4 slope
  0.500/0.497, H1 pullback depth 0.545/0.537, H1 RSI 0.509/0.501, M15 reclaim
  0.494/0.485, M15 ADX 0.504/0.521). Strongest *stable signal-quality* effect:
  `h4_close_dist_ema50_atr` at 0.044 — **below the 0.05 negligibility floor**.
- The only stable separators above the floor are **context**:
  `spread_to_atr_pct` (cost, 0.077 — mechanical, cost reduces net R directly),
  `atr_at_entry` (volatility, 0.068), `hour` (time-of-day, 0.074). All weak
  (AUC ≲ 0.58).

## 9. Train/validation stability

Reported per feature on each split separately. The context separators are
direction-stable across splits; cost shows a clean monotonic quintile decline
(win-rate 0.43→0.25 as spread/ATR rises). The signal-quality features are either
unstable in direction (h4_bias_score, m15_close_dist_ema50) or stable-but-
negligible.

## 10. Actionable or exploratory?

**Exploratory only.** No structural entry-signal edge was found. The weak
context effects (volatility, time-of-day) are low-confidence, hypothesis-
generating leads at best; selecting any threshold from this same dataset would be
overfitting. The cost effect is mechanical, not an edge.

## 11. C023 execute/defer recommendation

**Defer, and consider retiring.** C023's only change is raising the H4 ADX gate
20→22, but `h4_adx_at_entry` does not separate winners from losers
(AUC 0.515/0.501; flat quintile win-rates). No evidence a stricter ADX gate helps.

## 12. C024 readiness decision

**`NOT_READY`.** No structural entry-signal feature separates winners from
losers, so there is no basis for a C024 that refines the pullback-resolution
signal. No C024 created; no thresholds or thesis numbers drafted. Recommend
pausing/retiring the C022–C023 pullback-resolution family.

## 13. Did any verdict change?

**No.** C022 remains REJECT; C023 remains scaffold-only/deferred; all prior
campaign artifacts untouched (only linked).

## 14. Was any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`.

## 15. Do paper/demo/live remain blocked?

**Yes.** No broker/executor/order/live code touched; no OANDA mutation/order
calls; freeze gate `loops_refuse` still passes.

## 16. Tests and validation commands run

- `pytest tests/ -q` → 1968 passed, 1 skipped, 1 pre-existing failure (§17).
  Includes 7 new tests in `tests/unit/test_c022_feature_separation.py` (all pass).
- `ruff check src tests scripts research` → 23 pre-existing errors, **0 in sprint
  files** (sprint files lint clean in isolation).
- `python scripts/check_research_freeze.py` → ALL CHECKS PASSED.
- `python scripts/validate_research_archive.py` → ALL CHECKS PASSED.
- `python scripts/scan_artifacts_for_secrets.py` → PASSED (value scan active for 2
  practice credentials; none found).
- `git status --short` → clean.

## 17. Pre-existing failures (unrelated to this sprint)

Observed on clean `main` @ 88c2432 before any change:

- `pytest`: `tests/unit/entry_parity/test_compare_entries.py::test_c008_entry_comparison_runs`
  (`bespoke_entry_count > 0` → 0) — data-dependent; needs C008 entry CSVs
  gitignored/absent in a fresh worktree. Plus 1 skip (`local H4 store absent`).
- `ruff check src tests scripts research`: 23 lint errors (unused imports, import
  sorting, ambiguous `l`) across pre-existing `tests/`, `scripts/`, `src/`,
  `research/` files. This sprint added none.
- A financing-overlay test/tool rewrites the tracked
  `research/financing_overlay_local_first/ledger_inventory_used.json` based on
  locally present backtest CSVs; in a fresh worktree it shrinks. Reverted after
  each pytest run; not part of this sprint's changes.

## 18. Remaining blockers

None for this diagnostic. The full per-trade parquet is local-only (gitignored);
re-run the build locally with `.env` sourced to regenerate it.

## 19. Files to review first

1. `docs/research/C024_READINESS_FROM_C022_FEATURE_SEPARATION.md` — the decision.
2. `docs/research/C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md` — the evidence.
3. `src/forex_bot/research/c022_entry_features.py` — the reconstruction (the part
   to scrutinize for lookahead-safety; bias/side agreement = 1.0 is the check).
4. `scripts/analyze_c022_feature_separation.py` — the separation method.

## 20. Recommended next sprint

Retire (or formally pause) the C022–C023 pullback-resolution family rather than
opening C024. If entry research continues, it should pursue a **structurally
different** thesis (the "filter the existing pullback signal" lever is empty per
this analysis), pre-committed and tested out-of-sample in its own sprint. Any
volatility/time-of-day idea must be pre-registered, not threshold-mined from this
dataset.
