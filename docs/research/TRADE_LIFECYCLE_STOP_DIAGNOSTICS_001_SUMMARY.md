# Trade Lifecycle & Stop Diagnostics 001 — Summary

**Date:** 2026-05-28
**Branch:** `infra-trade-lifecycle-feature-capture-and-stop-diagnostics-001`
**Type:** infrastructure / research diagnostics — **NOT a strategy campaign.**
**Outcome:** local-only lifecycle + stop diagnostics tooling delivered; C022
realized stop/exit behavior reproduced exactly; MFE/MAE reconstruction designed,
coded, unit-tested, and **BLOCKED_LOCAL_DATA** for the real run in this checkout.

## 1. Branch

`infra-trade-lifecycle-feature-capture-and-stop-diagnostics-001` (from `main` @ 608eece).

## 2. Commits by phase

| phase | hash | title |
|---|---|---|
| 0 | `f6d9139` | branch, audit, plan |
| 1 | `db3bfe0` | trade artifact inventory |
| 2 | `a0ee722` | normalized lifecycle schema + loader |
| 3 | `69dfa38` | realized stop/exit diagnostics |
| 4 | `488948a` | MFE/MAE reconstruction design + module |
| 5 | `01df870` | MFE/MAE reconstruction script (blocked here) |
| 6 | `8f04edb` | stop-model comparison (deferred, blocked) |
| 7 | `cfa0958` | lifecycle improvement roadmap |
| 8 | (this commit) | final validation + summary |

## 3. Files changed by phase (all additions; 0 modifications to existing files)

- **P0:** `docs/research/TRADE_LIFECYCLE_STOP_DIAGNOSTICS_001_PLAN.md`
- **P1:** `scripts/inventory_trade_lifecycle_artifacts.py`,
  `docs/research/TRADE_LIFECYCLE_ARTIFACT_INVENTORY.md`,
  `research/trade_lifecycle_diagnostics/artifact_inventory.json`
- **P2:** `src/forex_bot/research/trade_lifecycle.py`, `tests/unit/test_trade_lifecycle.py`
- **P3:** `scripts/analyze_trade_lifecycle_stops.py`,
  `research/trade_lifecycle_diagnostics/stop_exit_summary.{json,md}`
- **P4:** `src/forex_bot/research/mfe_mae.py`, `tests/unit/test_mfe_mae.py`,
  `docs/research/MFE_MAE_RECONSTRUCTION_FEASIBILITY.md`
- **P5:** `scripts/reconstruct_mfe_mae_for_campaign_trades.py`,
  `docs/research/CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md`,
  `research/trade_lifecycle_diagnostics/c022_mfe_mae_summary.json`
- **P6:** `docs/research/DIAGNOSTIC_STOP_MODEL_COMPARISON.md`,
  `research/trade_lifecycle_diagnostics/diagnostic_stop_model_comparison.json`
- **P7:** `docs/research/TRADE_LIFECYCLE_IMPROVEMENT_ROADMAP.md`
- **P8:** this summary

## 4. Existing artifact inventory result

Only **CAMPAIGN_022** has committed per-trade CSVs (21 files, 7 pairs,
train+validation, 2961 rows incl. 2× stress). **C019 / C020 / C021** trade CSVs
are **gitignored and absent** from the checkout — only aggregate `*_summary.json`
are committed (per-trade lifecycle data would need a local re-export). **C023** is
scaffold-only with no trades. No campaign records full MFE/MAE or signal features;
C022 carries only a conditional `protective_stop_arm_mfe_r` proxy. (Details:
`TRADE_LIFECYCLE_ARTIFACT_INVENTORY.md`.)

## 5. C022 stop/exit diagnostics — reproduced

Exactly reproduced the published C022 aggregates from the committed CSVs:

| metric | value | matches published |
|---|---|---|
| base train+val trades | 2396 | ✅ |
| train expectancy | −0.1042R | ✅ |
| validation expectancy | −0.1663R | ✅ |
| validation 2× cost stress | −0.2468R | ✅ |
| hard-stop share / mean R | 60.1% / −0.86R | ✅ |
| time-stop share / mean R | 39.9% / +0.96R | ✅ |
| win rate / breakeven | 32.6% / ~39.0% | ✅ |
| trades losing ≥0.9R | 42.3% | ✅ |
| per-pair train expectancy | all 7 match | ✅ |

Reproduction check object asserts trades==2396, hard-stop≈60%, stop bucket
negative, time bucket positive — all **True**.

## 6. Was MFE/MAE reconstruction feasible?

**Design: yes. Real run: BLOCKED_LOCAL_DATA.** The C022 trade CSVs carry enough
anchor fields (instrument, side, entry/exit time, entry price, initial stop, M15
timeframe) to join local candles. But the materialized M15 research store is
unreachable here (`FOREX_BOT_RESEARCH_DATABASE_URL` unset; default local Postgres
needs a password; `data/bot.sqlite3` has 0 candles). The reconstruction geometry
is implemented (`src/forex_bot/research/mfe_mae.py`) and **unit-tested with 11
synthetic-candle tests**; the script writes a clean `BLOCKED_LOCAL_DATA` note with
the exact local command and fabricates nothing.

## 7. MFE/MAE findings

None produced — blocked on local data (no fabrication). Will run unchanged once a
populated materialized M15 store is reachable (Phase 5 command in the feasibility
doc and the blocked summary).

## 8. Diagnostic stop-model comparison

**Deferred** — gated on MFE/MAE (blocked). Recorded the 5 designed stop families
and the exact missing inputs (per-bar M15, ATR-at-entry, H1 pullback geometry,
M15 reclaim level) instead of fabricating counterfactuals. No "best" stop selected
or promoted; labeled diagnostic-sensitivity only.

## 9. Main lifecycle failure hypothesis

**Most likely: weak/absent entry edge — not stop placement.** Win rate 32.6% vs
~39% breakeven, uniformly negative across all 7 pairs, worsening out-of-sample and
under cost stress. Survivors are profitable (time-exits +0.96R) but too few
survive. Whether the 60% stop-share reflects a too-tight stop *or* entries that go
straight to the stop **cannot be distinguished without MFE/MAE** — that is the
single highest-value missing measurement. (Roadmap §1.)

## 10. Should C023 run next, or be deferred?

**Defer.** A single ADX-threshold bump (20→22) is very unlikely to convert C022's
broad, all-pair failure into an edge. Execute C023 only if MFE/MAE capture later
implicates low-ADX weak-trend entries specifically.

## 11. Was CAMPAIGN_024 created?

**No.** None created. Roadmap recommends *not* creating C024 until future
campaigns capture MFE/MAE + signal features + ATR + stop geometry.

## 12. Was any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []` (verified, not
modified).

## 13. Do paper / demo / live remain blocked?

**Yes.** Freeze gate confirms paper-loop and demo-loop refuse `trend_following` —
frozen. No enablement performed.

## 14. Tests & validation commands run

- `pytest tests/ -q` → **1923 passed, 1 skipped, 1 failed** (the 1 failure is the
  pre-existing, unrelated `test_c008_entry_comparison_runs`; +21 new tests added
  by this sprint all pass).
- `ruff check src tests scripts research` → 23 **pre-existing** errors only; all
  files added by this sprint are ruff-clean.
- `python scripts/check_research_freeze.py` → ALL CHECKS PASSED.
- `python scripts/validate_research_archive.py` → ALL CHECKS PASSED.
- `python scripts/scan_artifacts_for_secrets.py` → PASSED (value scan skipped — no
  creds in env; pattern scan clean).
- `git status --short` → clean.

## 15. Pre-existing failures (unrelated to this sprint, present on `main`)

- **pytest:** `tests/unit/entry_parity/test_compare_entries.py::test_c008_entry_comparison_runs`
  (`bespoke_entry_count == 0`; needs a local H4 store / bespoke C008 entries absent
  in this checkout).
- **ruff:** 23 errors — unused imports / unsorted import blocks / ambiguous `l`
  names in existing C020/C021 fill-timing modules and their tests.

Neither was touched or worsened by this sprint.

## 16. Remaining blockers

- **MFE/MAE reconstruction (Phase 5)** and **stop-model comparison (Phase 6)** are
  `BLOCKED_LOCAL_DATA`: no reachable materialized M15 research store in this
  environment. Run the Phase 5 command locally with a populated store to unblock.
- ATR-at-entry, H1 pullback geometry, and M15 reclaim level are **not captured** in
  C022 artifacts and cannot be recovered from them — they require future-campaign
  writer changes (roadmap §2) before structure/ATR stop variants can be compared.

## 17. Exact files to review first

1. `docs/research/TRADE_LIFECYCLE_IMPROVEMENT_ROADMAP.md` — the conclusions.
2. `research/trade_lifecycle_diagnostics/stop_exit_summary.md` — the reproduced
   C022 stop/exit evidence.
3. `docs/research/TRADE_LIFECYCLE_ARTIFACT_INVENTORY.md` — what data exists / is
   missing.
4. `docs/research/MFE_MAE_RECONSTRUCTION_FEASIBILITY.md` — design + why blocked.
5. `src/forex_bot/research/mfe_mae.py` + `tests/unit/test_mfe_mae.py` — the
   reconstruction geometry.

## 18. Recommended next sprint

**Lifecycle feature capture instrumentation** (infra, no campaign): extend the
campaign trade writer to emit MFE/MAE, threshold-before-stop flags, ATR-at-entry,
H4 ADX / H1 pullback depth / M15 reclaim distance, and session/regime tags — and
fix the JPY/CAD R-convention inconsistency at the writer. Then, with a populated
materialized M15 store reachable, run Phase 5/6 here to get the MFE/MAE and stop
sensitivity that decide whether the C022-family failure is entry-edge or
stop-geometry — and only then design C024 around the verified failure point.
