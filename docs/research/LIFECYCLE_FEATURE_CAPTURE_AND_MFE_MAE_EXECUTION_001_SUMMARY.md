# Lifecycle Feature Capture & MFE/MAE Execution 001 — Summary

**Date:** 2026-05-28
**Branch:** `infra-lifecycle-feature-capture-and-mfe-mae-execution-001`
**Type:** infrastructure / research diagnostics — **NOT a strategy campaign.**
**Outcome:** R-convention bug proven & locked; forward feature-capture schema +
opt-in C022 exporter delivered. After a read-only local M15 store was made
reachable (gitignored `.env` symlink), **MFE/MAE reconstruction and the stop-model
comparison were EXECUTED** on real candles — verdict: the C022 failure is **entry
edge, not stop placement** (cost-free baseline still negative; no exit rule clears
zero). C023 deferred; C024 must be entry-feature-driven, not a stop/exit campaign.

> **Update note.** This summary supersedes the earlier "still blocked" framing:
> the data dependency was resolved mid-sprint and Phases 1 & 5 were executed.

## 1. Branch

`infra-lifecycle-feature-capture-and-mfe-mae-execution-001`, based on the prior
sprint tip `20928c1` (= `main` 608eece + the unmerged but required lifecycle-001
artifacts; no divergence).

## 2. Commits by phase

| phase | hash | title |
|---|---|---|
| 0 | `4e92658` | branch, audit, data readiness, plan |
| 2 | `d31c3e9` | C022 R-multiple convention audit |
| 3 | `4b765fc` | lifecycle feature-capture schema |
| 4 | `04a6fd4` | opt-in lifecycle export in C022 runner |
| 5 (blocked) | `00320b6` | stop-model comparison — initial blocked note |
| 6 | `431ad7f` | conclusions + C024 readiness (initial) |
| 7 | `4c9c6fa` | final validation + summary (initial) |
| 1 EXEC | `80b5759` | **MFE/MAE reconstruction executed on local M15** |
| 5 EXEC | `98de354` | **stop-model comparison executed on local M15** |
| post | (this commit) | conclusions + summary updated to executed outcomes |

(Phases ran 0→7 under the initial "blocked" assumption; after local M15 access was
granted mid-sprint, Phases 1 and 5 were executed and the conclusion/summary docs
updated. The DB-independent Phases 2–4 were unaffected.)

## 3. Files changed by phase

- **P0:** `docs/research/LIFECYCLE_FEATURE_CAPTURE_AND_MFE_MAE_EXECUTION_001_PLAN.md`
- **P1:** none (reconstruction re-run produced byte-identical BLOCKED_LOCAL_DATA
  output; nothing new to commit).
- **P2:** `docs/research/C022_R_MULTIPLE_CONVENTION_AUDIT.md`,
  `tests/unit/test_c022_r_convention_audit.py`
- **P3:** `src/forex_bot/research/lifecycle_features.py`,
  `tests/unit/test_lifecycle_features.py`
- **P4:** `scripts/run_campaign_022_h4_h1_pullback_resolution.py` (opt-in flag +
  helper), `src/forex_bot/research/lifecycle_features.py` (export helpers),
  `tests/unit/test_lifecycle_features.py`,
  `tests/unit/test_c022_runner_lifecycle_export.py`, `.gitignore`
- **P5:** `docs/research/DIAGNOSTIC_STOP_MODEL_COMPARISON_EXECUTED.md`
- **P6:** `docs/research/LIFECYCLE_FEATURE_CAPTURE_AND_MFE_MAE_EXECUTION_001_CONCLUSIONS.md`
- **P7:** this summary

(No modifications to broker/executor/order/live code; the only existing-file code
change is the C022 *research runner*, additive and opt-in.)

## 4. Local data readiness result

**Initially BLOCKED, then RESOLVED.** At first probe: env unset, Postgres rejected
all auth, sqlite empty. After the user authorized a gitignored `.env` symlink, a
**read-only** local research Postgres (`market_data` schema) became reachable with
materialized M15 for all 7 pairs spanning 2021-05 → 2026-05 (110k–118k bars/pair),
fully covering C022's train+validation windows. No OANDA calls; no credentials
committed or printed.

## 5. Did C022 MFE/MAE reconstruction complete?

**Yes — executed.** Reconstructed **2311 / 2396** base train+val trades (85 dropped
at data edges, no fabrication). `c022_mfe_mae_summary.json` +
`CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md`.

## 6. Key MFE/MAE findings

- **Stopped-out trades:** 45.9% never reached +0.25R before the stop; 54.1% reached
  +0.25R, 36.6% +0.5R, 16.3% +1.0R first (mean MFE before stop +0.47R).
- **Time-exit winners:** mean MAE −0.40R; only **4.7%** ever touched −0.9R — winners
  rarely approach the stop, so the stop is not cutting live winners.
- **Stop-outs uniform** across pairs (0.55–0.61) and sides (long 0.59 / short 0.58)
  — systemic, not a pair/side artifact.

## 7. R-multiple convention audit result

**Proven R-normalization inconsistency** in the C022 exporter. At hard stops
(price-based R = −1 for all pairs): USD-*quote* pairs record `r = −1.000`
(correct); USD-*base* pairs record `r = price_based_R / quote_rate` — exact:
`recorded_r × rate = −1.0000`. So USD_JPY records ≈ −0.008, USD_CAD ≈ −0.76,
USD_CHF ≈ −1.08 at full-stop losses, and the scaling applies to the whole `r`
column (confirmed on time-exits too: ratio ≈123 JPY, ≈1.31 CAD, ≈0.93 CHF, 1.0
EUR_USD). This explains `near_full_loss_share = 0` for JPY/CAD. **Correcting it
makes C022 more negative** (true JPY train ≈ −0.21R vs recorded −0.0017R) — REJECT
is reinforced, never rescued. No metric rewritten, no verdict changed; 8
characterization tests lock the finding. Detail:
`docs/research/C022_R_MULTIPLE_CONVENTION_AUDIT.md`.

## 8. Lifecycle feature-capture changes

New `src/forex_bot/research/lifecycle_features.py`: `LifecycleFeatureRecord` with
the full future-campaign field set (stop geometry, `atr_at_entry`,
`spread_to_atr_pct`, MFE/MAE, +0.25/0.5/1.0R & −0.5/−0.9R flags, H4/H1/M15 signal
features, session/weekday/regime, HTF provenance times), explicit missing-field
accounting, stable `CSV_COLUMNS`, roundtrip serialization, derivation helpers, and
a **pair-agnostic `price_based_r`** that fixes the audited convention going forward.

## 9. Was the C022 runner/exporter retrofitted?

**Yes — opt-in and backwards-compatible.** Added `--emit-lifecycle-features`
(default OFF) to `scripts/run_campaign_022_h4_h1_pullback_resolution.py`; when set,
it writes a compact `*_lifecycle_features.csv` beside each trades CSV via the pure
export helpers (corrected R, derived stop-distance/session/weekday; MFE/MAE +
signal features left None until reconstruction/instrumentation fills them). Default
trade/metric output, frozen parameters, strategy logic, and verdict are unchanged
(asserted by tests). New CSV is gitignored.

## 10. Diagnostic stop-model comparison result

**Executed** (`diagnostic_stop_model_comparison.py` over 2396 fixed entries on local
M15; new pure `stop_model_sim.py` + 10 tests). Every hard-stop multiple
(1.5×/2.0×/2.5×/3.0× ATR) and every time-to-invalidation rule sits in a tight
**negative** band (≈ −0.05 to −0.08R); the **cost-free** mid baseline (−0.073R) is
already negative vs realized −0.140R (gap ≈ cost drag). **No exit rule lifts
expectancy toward zero** → exits are second-order; the problem is entry edge.
Diagnostic sensitivity only — no "best" stop promoted, entries unchanged, no verdict
changed. (ATR-multiple/invalidation evaluated; structure/reclaim families still need
future signal-geometry capture.)

## 11. C023 execute/defer recommendation

**Defer.** A single ADX 20→22 bump will not fix a broadly-failing system; wait for
MFE/MAE evidence to drive the next design.

## 12. C024 readiness decision

**Failure point now verified = entry edge, not exits.** So C024 is **not** a
stop/exit campaign (exits proven second-order). It may become an *entry-feature*
campaign only after capturing entry signal features and demonstrating one separates
winners from losers; if none does, retire the pullback-resolution family rather than
re-tune it. No C024 created this sprint.

## 13. Did any verdict change?

**No.** All campaign verdicts unchanged (C022 REJECT, C023 SCAFFOLD_ONLY).

## 14. Was any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []` (verified, not
modified).

## 15. Do paper / demo / live remain blocked?

**Yes.** Freeze gate confirms the loops refuse `trend_following` — frozen. No
enablement performed.

## 16. Tests & validation commands run

- `pytest tests/ -q` → **1961 passed, 1 skipped, 1 failed** (+38 new tests this
  sprint: R-convention 8, lifecycle_features 14, runner-export 6, stop_model_sim 10;
  the 1 failure is the pre-existing unrelated `test_c008_entry_comparison_runs`).
- `ruff check src tests scripts research` → 23 **pre-existing** errors only; all
  sprint files ruff-clean.
- `check_research_freeze.py` / `validate_research_archive.py` /
  `scan_artifacts_for_secrets.py` → **all PASS**.
- `git status --short` → clean.

## 17. Pre-existing failures (unrelated, present on `main`)

- pytest: `tests/unit/entry_parity/test_compare_entries.py::test_c008_entry_comparison_runs`
  (`bespoke_entry_count == 0`; needs local H4 store).
- ruff: 23 errors (unused imports / unsorted blocks / ambiguous `l`) in existing
  C020/C021 fill-timing files & tests. Neither touched by this sprint.

## 18. Remaining blockers

- **None for the executed diagnostics** — MFE/MAE and the ATR-multiple /
  time-to-invalidation stop sweep ran on real M15.
- **Structure / reclaim stop families** and any **entry-feature separation test**
  still need signal geometry (ATR-at-entry, H1 pullback, M15 reclaim, ADX) that is
  absent from *historical* C022 artifacts — they require one instrumented
  `--emit-lifecycle-features` rerun (now wired). This is the gate for designing C024.
- DB access depends on the local research Postgres + the gitignored `.env` symlink
  (not committed); the diagnostics re-run only where that store is reachable.

## 19. Exact files to review first

1. `docs/research/C022_R_MULTIPLE_CONVENTION_AUDIT.md` — the proven R bug + impact.
2. `docs/research/LIFECYCLE_FEATURE_CAPTURE_AND_MFE_MAE_EXECUTION_001_CONCLUSIONS.md`
   — the C023/C024 decision and prerequisites.
3. `src/forex_bot/research/lifecycle_features.py` — the forward capture schema.
4. The C022 runner diff (`scripts/run_campaign_022_h4_h1_pullback_resolution.py`)
   — the opt-in exporter (verify default-OFF / no frozen-param change).
5. `docs/research/LIFECYCLE_FEATURE_CAPTURE_AND_MFE_MAE_EXECUTION_001_PLAN.md`
   — data-readiness probe + unblock command.

## 20. Recommended next sprint

**Entry-feature separation study** (the now-verified failure point): run one
instrumented C022-style diagnostic export with `--emit-lifecycle-features` to capture
H4 ADX / H1 pullback depth / M15 reclaim distance / ATR-at-entry / session-regime per
trade, join to the reconstructed MFE/MAE outcome, and test whether **any** entry
feature separates winners from losers. If one does → design a single, pre-registered
entry-filter C024 around it. If none does → conclude the pullback-resolution family
has no recoverable entry edge and retire it (no C024). Exits are already proven
second-order, so do **not** spend a campaign on stop tuning. Optionally, a separate
scoped repair sprint to recompute historical per-pair R with `price_based_r`
(verdicts unchanged).
