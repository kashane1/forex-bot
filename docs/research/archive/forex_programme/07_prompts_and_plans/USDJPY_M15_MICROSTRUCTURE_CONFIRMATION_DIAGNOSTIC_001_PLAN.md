# USD_JPY M15 Microstructure Confirmation Diagnostic — Sprint 001 Plan

**Date:** 2026-05-28 · **Branch:** `research-usdjpy-m15-microstructure-confirmation-diagnostic-001`
(off the C022 closeout/amendment HEAD `384d99e` of
`research-post-c022-family-retirement-and-new-thesis-selection-001`).
**Type:** read-only diagnostic. Approves nothing, executes no campaign, implements no
strategy, tunes nothing, changes no verdict, creates no C024, claims no edge.

> This sprint is a **read-only, USD_JPY-only** winner/loser separation diagnostic for
> M15 microstructure-confirmation primitives. It produces decision docs + compact
> artifacts (manifest, preview, summary JSON) + a readiness decision. It does **not**
> create CAMPAIGN_024, execute C023, implement a strategy, run a campaign, approve
> anything, or touch paper/demo/live or broker/executor/order/live code.

## 1. Purpose

C022 failed on **entry signal quality**: the M15 EMA20-reclaim trigger is inert
(`m15_reclaim_distance_atr` AUC 0.494/0.485), and stop/time/ADX/cost-free variants all
stay negative. The selected next lane is **market-microstructure-style confirmation**,
narrowed (2026-05-28 amendment) to **USD_JPY only**. The question this sprint answers,
read-only and for USD_JPY alone: **do any stronger M15 microstructure-confirmation
primitives separate winners from losers better than the old EMA20-reclaim trigger?**

## 2. USD_JPY-only scope

- **USD_JPY only.** No seven-pair aggregation; no other pair enters the analysis set.
- **M15 execution context**; H1/H4 used only where a primitive needs higher-timeframe
  context for reconstruction (do not broaden the thesis).
- Local materialized M15/H1/H4 store, **read-only** (probed reachable this sprint:
  USD_JPY M15/H1/H4 frames load).
- USD_JPY C022 base trades on disk: **133 train + 173 validation = 306** (gitignored).
- USD_JPY focus is a **research-scoping decision, not an edge claim** and does not
  bring approval or demo any closer; it does **not** lower the evidence bar.

## 3. Prior evidence summary

| Source | Finding |
|---|---|
| [`C022_C023_PULLBACK_RESOLUTION_FAMILY_CLOSEOUT.md`](C022_C023_PULLBACK_RESOLUTION_FAMILY_CLOSEOUT.md) | Family RETIRED; failure localized to entry signal. |
| [`C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md`](C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md) | Every structural entry feature at AUC ≈ 0.50; M15 reclaim inert. |
| [`C024_READINESS_FROM_C022_FEATURE_SEPARATION.md`](C024_READINESS_FROM_C022_FEATURE_SEPARATION.md) | C024 `NOT_READY`; no justified filter hypothesis. |
| [`NEXT_THESIS_SELECTION_DECISION.md`](NEXT_THESIS_SELECTION_DECISION.md) | Lane D selected; §1a USD_JPY scope; §5 five-part C024 bar (unchanged). |
| `CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md` | 45.9% of stop-outs never reach +0.25R (straight-to-stop signature). |

## 4. Non-goals

Not a strategy implementation; not C024; not C023 execution; not a campaign; not a
tuning/threshold-mining sprint; not paper/demo/live enablement.

## 5. Safety rules (hard)

- No CAMPAIGN_024; no C023 execution; no strategy/entry-exit logic edits; no campaign run.
- No verdict change; no historical-metric rewrite.
- `configs/approved_strategies.yaml` stays `approved: []` (verify only).
- No paper/demo/live; no broker/executor/order/live changes; no OANDA mutation/order
  calls; no live trading credentials. `.env` used **only** read-only for the research DB;
  credentials never printed.
- Do not commit `.env`, credentials, DBs, raw candle dumps, huge CSVs, or bulky
  generated artifacts (gitignore the full per-trade dataset; commit only
  manifest + small preview + summary JSON, as the C022 feature-separation sprint did).
- Detectors are strictly causal / decision-bar-anchored; any detector that reads
  post-entry bars is labelled **post-entry diagnostic only**, never a live entry feature.
- No threshold is selected as a parameter; no USD_JPY edge claimed.

## 6. Detector categories (Phase 2)

1. `reclaim_plus_impulse` — reclaim + unusually large body/range vs recent ATR/median.
2. `reclaim_plus_micro_swing_break` — reclaim + break of prior N-bar local extreme in trade direction.
3. `reclaim_plus_retest_hold` — reclaim, then a small window retests the reclaimed level and holds.
4. `failed_reclaim_or_trap` — reclaim that quickly closes back through the level (trap; avoid).
5. `liquidity_sweep_plus_displacement` — prior local extreme swept, then a directional displacement candle.
6. `range_expansion_after_compression` — compressed recent range then directional expansion.
7. `session_context` — Tokyo / London / NY / overlap / rollover buckets (USD_JPY-relevant).
8. `spread_volatility_context` — spread/ATR, ATR percentile, volatility bucket (if data exists).

Each detector is pure, read-only, no-lookahead relative to its evaluation time, with
synthetic-bar unit tests. Missing prerequisites are made explicit (no fabrication).

## 7. Expected artifacts

- `docs/research/USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_001_PLAN.md` (this, Phase 0).
- `docs/research/USDJPY_MICROSTRUCTURE_DATASET_INVENTORY.md` + `research/usdjpy_microstructure_diagnostic/dataset_inventory.json` (Phase 1).
- `src/forex_bot/research/microstructure_confirmations.py` + unit tests (Phase 2).
- `scripts/build_usdjpy_microstructure_diagnostic_dataset.py` + compact outputs (Phase 3).
- `scripts/analyze_usdjpy_microstructure_confirmation.py` + `analysis_summary.json` + `docs/research/USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_RESULT.md` (Phase 4).
- `docs/research/USDJPY_C024_READINESS_DECISION.md` (Phase 5).
- `docs/research/USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_001_SUMMARY.md` (Phase 6).

The full per-trade USD_JPY microstructure dataset (parquet, local) is **gitignored**;
only the manifest, a small stratified preview CSV, and summary JSON are committed.

## 8. Separation method

Reuse the C022 feature-separation method: AUC = P(winner value > loser value),
effect = |AUC−0.5|, negligible below **0.05**; "stable" = train and validation AUC on
the same side of 0.5; minimum per-class N for trust = 30 (relaxed/flagged for the
smaller USD_JPY sample). Post-hoc outcome labels kept strictly out of features via the
existing `FEATURE_DENYLIST`. Each primitive is additionally compared against the old
C022 EMA20-reclaim trigger and assessed for straight-to-stop reduction.

## 9. Validation commands

`pytest tests/ -q` · `ruff check src tests scripts research` ·
`python scripts/check_research_freeze.py` · `python scripts/validate_research_archive.py` ·
`python scripts/scan_artifacts_for_secrets.py` · `git status --short`.

## 10. Phase-0 baseline (executed on this branch)

| Check | Result |
|---|---|
| Prior docs present | All 7 present. |
| C022 / C023 / C024 | C022 REJECT; C023 scaffold-only/not executed; C024 absent (verified). |
| `approved_strategies.yaml` | `approved: []`. |
| USD_JPY data | DB reachable read-only; M15/H1/H4 frames load; 306 USD_JPY base trades on disk. |
| `pytest tests/ -q` | 1967 passed, 3 skipped (data-dependent). |
| `ruff check src tests scripts research` | All checks passed. |
| `check_research_freeze` / `validate_research_archive` | ALL CHECKS PASSED. |
| `scan_artifacts_for_secrets` | PASSED. |

## 11. Known pre-existing skips (unrelated)

3 data-dependent pytest skips: `tests/research/test_cost_atlas.py` (local H4 store
absent — note: H4 *is* reachable for USD_JPY here, but that test targets a different
store path) and two `tests/unit/entry_parity/test_compare_entries.py` cases (C008
bespoke CSVs gitignored/absent). None are failures.

## 12. Explicit no-C024 / no-C023 / no-approval statement

This sprint creates **no CAMPAIGN_024**, executes **no C023**, runs **no campaign**,
approves **no strategy** (`approved: []` unchanged), changes **no verdict**, and keeps
**paper/demo/live blocked**. It ends at a USD_JPY-only C024 *readiness decision*; even
`READY_FOR_PRECOMMIT` only unlocks a separate future precommit sprint. USD_JPY is not
presented as proven edge.
