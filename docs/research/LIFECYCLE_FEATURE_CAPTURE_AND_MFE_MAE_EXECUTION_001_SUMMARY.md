# Lifecycle Feature Capture & MFE/MAE Execution 001 — Summary

**Date:** 2026-05-28
**Branch:** `infra-lifecycle-feature-capture-and-mfe-mae-execution-001`
**Type:** infrastructure / research diagnostics — **NOT a strategy campaign.**
**Outcome:** R-convention bug proven & locked; forward feature-capture schema +
opt-in C022 exporter delivered; MFE/MAE reconstruction re-attempted and again
**BLOCKED_LOCAL_DATA**; C023 deferred, C024 not ready.

## 1. Branch

`infra-lifecycle-feature-capture-and-mfe-mae-execution-001`, based on the prior
sprint tip `20928c1` (= `main` 608eece + the unmerged but required lifecycle-001
artifacts; no divergence).

## 2. Commits by phase

| phase | hash | title |
|---|---|---|
| 0 | `4e92658` | branch, audit, data readiness, plan |
| 1 | (no commit) | MFE/MAE reconstruction re-attempt — BLOCKED, output byte-identical to committed blocked artifact |
| 2 | `d31c3e9` | C022 R-multiple convention audit |
| 3 | `4b765fc` | lifecycle feature-capture schema |
| 4 | `04a6fd4` | opt-in lifecycle export in C022 runner |
| 5 | `00320b6` | stop-model comparison still blocked |
| 6 | `431ad7f` | conclusions + C024 readiness |
| 7 | (this commit) | final validation + summary |

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

**BLOCKED_LOCAL_DATA.** `FOREX_BOT_RESEARCH_DATABASE_URL` unset; no `PG*` env; no
repo `.env`; Postgres on `:5432` rejects all connections (`fe_sendauth: no password
supplied`) across tcp/socket, OS-user, and `postgres` roles; `data/bot.sqlite3` has
0 candle rows; no local candle corpora. Exact unblock command is in the plan doc.

## 5. Did C022 MFE/MAE reconstruction complete?

**No — still blocked** (see #4). Re-ran `scripts/reconstruct_mfe_mae_for_campaign_trades.py`;
it wrote the same `BLOCKED_LOCAL_DATA` status (no fabrication). Logic remains
implemented + unit-tested (11 synthetic-candle tests).

## 6. Key MFE/MAE findings

None — blocked. The straight-to-stop vs reached-favorable-first question (the
decisive one for any stop campaign) remains unanswered pending local data.

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

**Not executed — gated on MFE/MAE (blocked).** No counterfactuals fabricated. The
5 stop families are designed and the Phase 3/4 work now makes their missing inputs
(ATR-at-entry, pullback/reclaim geometry) capturable in future runs.

## 11. C023 execute/defer recommendation

**Defer.** A single ADX 20→22 bump will not fix a broadly-failing system; wait for
MFE/MAE evidence to drive the next design.

## 12. C024 readiness decision

**Not ready.** Failure point unverified (MFE/MAE blocked) and historical R was just
shown inconsistent. Prerequisites: unblock M15 data + run reconstruction; one
instrumented `--emit-lifecycle-features` export; adopt `price_based_r`; then
classify entry-edge vs stop-geometry.

## 13. Did any verdict change?

**No.** All campaign verdicts unchanged (C022 REJECT, C023 SCAFFOLD_ONLY).

## 14. Was any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []` (verified, not
modified).

## 15. Do paper / demo / live remain blocked?

**Yes.** Freeze gate confirms the loops refuse `trend_following` — frozen. No
enablement performed.

## 16. Tests & validation commands run

- `pytest tests/ -q` → **1951 passed, 1 skipped, 1 failed** (+28 new tests this
  sprint; the 1 failure is the pre-existing unrelated `test_c008_entry_comparison_runs`).
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

- **MFE/MAE reconstruction (Phase 1) and stop-model comparison (Phase 5)** —
  `BLOCKED_LOCAL_DATA`: no reachable materialized M15 store. Unblock via the plan
  command, then both run unchanged.
- ATR-at-entry / H1 pullback / M15 reclaim geometry are not in *historical* C022
  artifacts; they require a future instrumented `--emit-lifecycle-features` rerun
  (now possible) before ATR/structure/reclaim stop variants can be compared.

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

**MFE/MAE execution once local M15 is reachable** (the genuinely blocking
dependency): (a) populate/point to a materialized M15 research store and run
`reconstruct_mfe_mae_for_campaign_trades.py`; (b) run one C022-style diagnostic
export with `--emit-lifecycle-features` to capture ATR/pullback/reclaim geometry;
(c) execute the stop-model comparison (Phase 5) and answer straight-to-stop vs
reached-favorable-first; (d) classify the failure as entry-edge vs stop-geometry
and only then design C024 around the verified point. Optionally, a separate,
explicitly-scoped repair sprint to recompute historical per-pair R with the
pair-agnostic convention (verdicts unchanged).
