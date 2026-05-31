# USD_JPY M15 Microstructure-Confirmation Diagnostic — Sprint 001 Summary

**Date:** 2026-05-28 · **Type:** read-only diagnostic. Approves nothing, executes
nothing, creates no campaign, changes no verdict, claims no edge.

## 1. Branch

`research-usdjpy-m15-microstructure-confirmation-diagnostic-001` (off the C022
closeout/amendment HEAD `384d99e`).

## 2. Commit hashes by phase

| Phase | Hash | Title |
|---|---|---|
| 0 | `a6f85ac` | branch, audit, plan |
| 1 | `239dd62` | USD_JPY dataset inventory |
| 2 | `da1fb3a` | read-only detector primitives |
| 3 | `2c0f1e9` | build USD_JPY diagnostic dataset |
| 4 | `a259fc2` | winner/loser separation analysis |
| 5 | `264c864` | USD_JPY C024 readiness = NOT_READY |
| 6 | _this commit_ | final validation + summary |

## 3. Files changed by phase

- **0:** `docs/research/USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_001_PLAN.md`.
- **1:** `scripts/inventory_usdjpy_microstructure_dataset.py`,
  `docs/research/USDJPY_MICROSTRUCTURE_DATASET_INVENTORY.md`,
  `research/usdjpy_microstructure_diagnostic/dataset_inventory.json`, `.gitignore`.
- **2:** `src/forex_bot/research/microstructure_confirmations.py`,
  `tests/unit/test_microstructure_confirmations.py`.
- **3:** `scripts/build_usdjpy_microstructure_diagnostic_dataset.py`,
  `research/usdjpy_microstructure_diagnostic/{usdjpy_microstructure_manifest.json,
  usdjpy_microstructure_features_preview.csv}` (full parquet gitignored).
- **4:** `scripts/analyze_usdjpy_microstructure_confirmation.py`,
  `research/usdjpy_microstructure_diagnostic/analysis_summary.json`,
  `docs/research/USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_RESULT.md`.
- **5:** `docs/research/USDJPY_C024_READINESS_DECISION.md`.
- **6:** this file.

## 4. USD_JPY dataset size and coverage

306 USD_JPY C022 base trades — **train 133, validation 173**. Exits: hard_stop 172,
time_stop 134. Win rate 0.379 (train 0.346, validation 0.405); mean R −0.0005
(near-flat — consistent with "less bad," **not** positive). MFE/MAE reconstructed
read-only: **299 OK / 7 NO_BARS**; straight-to-stop 79 (45.9% of hard stops, matching
the C022 aggregate). All 306 decision bars located in the materialized M15 store.

## 5. Detector primitives implemented

Live (lookback-only, decision-bar): `reclaim_plus_impulse`,
`reclaim_plus_micro_swing_break`, `liquidity_sweep_plus_displacement`,
`range_expansion_after_compression`. Post-entry (diagnostic-only, flagged
`uses_post_decision=True`): `reclaim_plus_retest_hold`, `failed_reclaim_or_trap`.
Context helpers: `session_bucket` (Tokyo/London/overlap/NY/rollover), `volatility_context`
(ATR + ATR-percentile), and the C022 `reclaim_distance_atr` baseline. 17 unit tests,
including causality (future bars do not change live detectors) and post-decision
dependence.

## 6. Strongest findings

- **Baseline (old EMA20-reclaim) is inert and unstable:** `reclaim_distance_atr` AUC
  0.539 train / 0.486 validation (not direction-stable).
- **No live primitive shows material separation.** Best *stable live* effect is
  `range_expansion_after_compression` at |AUC−0.5| = 0.016 — far below the 0.05 floor.
  `liquidity_sweep_plus_displacement` is direction-**unstable** (0.465 / 0.583).
- **The one stable boolean lift is fragile:** sweep+displacement *present* lifts
  win-rate +0.10 / +0.14, but is present on 81% of trades (tiny absent group), has an
  unstable continuous AUC, and yields **no straight-to-stop reduction**.
- **The only above-floor separators are post-entry:** `reclaim_plus_retest_hold`
  (AUC 0.611 / 0.552, effect 0.052) and `failed_reclaim_or_trap` describe post-entry
  behavior (winners hold the reclaim; losers trap) — partly tautological and **not
  live-usable** as entry filters.

## 7. Train/validation stability

Live detectors that are direction-stable are all negligible (≤ 0.016). The detector
with an above-floor effect (retest-hold) is post-entry. `liquidity_sweep` and the
trap detector's continuous score are **unstable** across splits. The baseline itself
is unstable. No live primitive is both stable and material.

## 8. Live-usable vs post-entry-only

Live (could gate an entry): impulse, micro-swing-break, sweep+displacement,
range-expansion — **none material/stable**. Post-entry (diagnostic-only, cannot gate
entry): retest-hold, failed-reclaim/trap — the only place above-floor separation
appears, and it is not usable as an entry signal.

## 9. Straight-to-stop impact

No live primitive reduces straight-to-stop in a stable way. Sweep+displacement
(the only stable live boolean lift) shows ≈0 straight-to-stop reduction (−0.02 /
−0.01). Post-entry retest-hold reduces straight-to-stop (0.36 / 0.15) but only
descriptively (it is observed after entry).

## 10. Sample-size impact

USD_JPY per-split samples are small (train 133 / validation 173; winners 46 / 70).
Any boolean filter further shrinks the comparison groups (e.g. sweep "absent" = 23/34).
This is flagged throughout: small-sample effects are treated as fragile, and large
single-pair effects as suspicious rather than reassuring.

## 11. C024 readiness decision

**`NOT_READY`** (USD_JPY-only). No live microstructure primitive separates winners
from losers materially, stably, and better than the inert baseline; the above-floor
separation is post-entry and not live-usable. No CAMPAIGN_024 created; no thresholds
drafted. Recommendation: deprioritize/close the USD_JPY microstructure *entry* lane;
the only honest follow-up reframes the post-entry retest-hold/trap signal as a
*trade-management* diagnostic (exit/early-invalidation), explicitly **not** entry alpha.
See [`USDJPY_C024_READINESS_DECISION.md`](USDJPY_C024_READINESS_DECISION.md).

## 12. Whether C023 executed

**No.** C023 remains scaffold-only / not executed.

## 13. Whether C024 was created

**No.** No CAMPAIGN_024 exists (verified: no config, no source).

## 14. Whether any verdict changed

**No.** C022 remains REJECT; C023 scaffold-only; all prior verdicts untouched.

## 15. Whether any strategy was approved

**No.** `configs/approved_strategies.yaml` remains `approved: []`.

## 16. Whether paper/demo/live remain blocked

**Yes.** No broker/executor/order/live code touched; no OANDA mutation/order calls;
freeze gate `loops_refuse` still passes.

## 17. Tests and validation commands run (Phase 6)

| command | result |
|---|---|
| `pytest tests/ -q` | **1984 passed, 3 skipped** (17 new microstructure tests; 3 data-dependent skips). |
| `ruff check src tests scripts research` | **All checks passed.** |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED.** |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED.** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** — with `.env` sourced the **value scan was active** for 2 practice credentials over 5669 files; none leaked. |
| `git status --short` | clean (all work committed). |

## 18. Pre-existing failures / skips

None as failures. 3 data-dependent pytest skips (cost-atlas H4 store path; two C008
entry-parity cases needing gitignored CSVs) — unchanged from baseline.

## 19. Remaining blockers

None for this diagnostic. The full per-trade parquet is local-only (gitignored);
rebuild with `.env` sourced via the Phase 3 build script to regenerate it.

## 20. Exact files to review first

1. [`USDJPY_C024_READINESS_DECISION.md`](USDJPY_C024_READINESS_DECISION.md) — the decision (NOT_READY) + recommendation.
2. [`USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_RESULT.md`](USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_RESULT.md) — the evidence tables.
3. [`USDJPY_MICROSTRUCTURE_DATASET_INVENTORY.md`](USDJPY_MICROSTRUCTURE_DATASET_INVENTORY.md) — the dataset.
4. `src/forex_bot/research/microstructure_confirmations.py` — the detectors (scrutinize the live/post-decision split and causality).

## 21. Recommended next sprint

**Default: record USD_JPY microstructure confirmation as closed (no live entry edge
found) and hold the freeze.** If one more USD_JPY diagnostic is wanted, the only
honest one is a **trade-management** study: treat the post-entry retest-hold/trap
signal as a candidate *exit / early-invalidation* rule on USD_JPY (read-only,
pre-committed, out-of-sample), explicitly **not** as entry alpha and **not** a C024.
Otherwise, move to a structurally different lane per
[`NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md`](NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md).
Any future USD_JPY C024 requires a fresh pre-committed thesis clearing the full §5 bar —
which this evidence does not provide.
