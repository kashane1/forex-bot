# CAMPAIGN_029 — USD_JPY 10-pip range-bar MTF breakout: scaffold plan & baseline audit

**Strategy family:** `usdjpy_range_bar_mtf_breakout`
**Version:** `0.1.0-c029`
**Campaign:** `CAMPAIGN_029`
**Branch:** `research-campaign-029-usdjpy-range-bar-scaffold-001`
**Base commit:** `4e2c532` (clean `origin/main`, range/volatility-bar infra merged)
**Date:** 2026-05-29
**Status:** `SCAFFOLD_ONLY / NOT_RUN / NOT_APPROVED`

> This sprint **scaffolds, preflights, and documents** a single-pair USD_JPY
> 10-pip range-bar research candidate with higher-timeframe context. It runs **no
> strategy evidence**, approves **nothing**, opens **no test lockbox**, and
> touches **no** broker / OANDA / paper / demo / live path.

---

## 0. Campaign-number correction (read this first)

The originating sprint prompt asked for **CAMPAIGN_028**. That number was **already
consumed** the day before by a *different* thread — the relative-value /
cointegration spread-reversion front-gate screen — and is committed on
`origin/main`:

- `1f3fe21` `research(campaign-028-relative-value-spread-front-gate-screen-001): phase 0`
- `f0516b9` `research(campaign-028-relative-value-spread-front-gate-screen-001): phase 2`
- tracked artifacts: `docs/research/CAMPAIGN_028_NEW_THESIS_BRIEF.md`,
  `docs/research/CAMPAIGN_028_FRONT_GATE_SCREEN_RESULTS.md`,
  `research/campaign_028/front_gate/relative_value_spread_screen.{md,json}`,
  `research/edge_discovery/relative_value_spread.py` (+ runner + tests).

Reusing 028 would collide with / overwrite a documented rejection on `main`. Per
the standing lab discipline (*"check identifier numbers are unused before
assigning — reuse already forced a C024→C025 rename"*), this range-bar lane is
numbered **CAMPAIGN_029**, the next genuinely-unused id. (`024` is also burned: an
abandoned pullback-family draft.) The user confirmed CAMPAIGN_029 on 2026-05-29.

| number | owner | status |
|--------|-------|--------|
| 024 | abandoned pullback draft | burned (renamed to 025) |
| 025 | `m5_donchian_htf_confluence_breakout` | scaffold; REJECT (C026 ladder) |
| 026 | C025 timeframe ladder | REJECT |
| 027 | `h4_filtered_zscore_reversion` | REJECT_TRAIN_GATE |
| 028 | relative-value spread reversion | LIKELY_SELECTION_NOISE / no scaffold |
| **029** | **`usdjpy_range_bar_mtf_breakout`** | **this sprint — scaffold only** |

## 1. Research thesis

Use **non-time-based 10-pip range bars** (built from USD_JPY M1 mid prices) to
strip clock-time noise and resample the tape by *price movement* instead of by
the clock. Combine that range-bar micro-structure with **higher-timeframe
trend/context** (M1-derived H4, and native-H4-derived D1AGG where available) so
the candidate is **structurally different** from every prior H4 / M15 / M5
time-bar campaign in the archive. The thesis is that trend-aligned continuation
*after a pullback-and-reclaim*, measured on range bars, is a cleaner trigger than
the same idea measured on fixed-clock bars.

This is a **hypothesis to be falsified later**, not a claim. The range-bar
infra's own full-corpus diagnostics recommended 10-pip as the primary USD_JPY
range threshold; this campaign is the first strategy lane to sit on top of it.

## 2. Baseline audit (Phase 0 — executed 2026-05-29)

All checks below were run from this branch off clean `origin/main`.

| audit item | result |
|------------|--------|
| `CAMPAIGN_029` unused | ✅ grep of tracked files: 001–028 used (024 burned); 029 free |
| non-time-bar infra present | ✅ `src/forex_bot/data/non_time_bars.py`, `scripts/generate_non_time_bar_diagnostics.py` |
| USD_JPY M1 corpus present | ✅ local Postgres research store; `PairRange(USD_JPY, 2021-05-27 → 2026-05-26)` |
| approved strategies empty | ✅ `configs/approved_strategies.yaml` → `approved: []` |
| paper/demo/live refusal holds | ✅ freeze gate: paper-loop & demo-loop refuse their configured strategies |
| `pytest tests/ -q` | ✅ 2249 passed, 3 skipped (local-data skips) |
| `ruff check src scripts tests` | ✅ all checks passed |
| `python scripts/check_research_freeze.py` | ✅ ALL CHECKS PASSED |
| `python scripts/validate_research_archive.py` | ✅ ALL CHECKS PASSED |
| `python scripts/scan_artifacts_for_secrets.py` | ✅ PASSED (no credential-shaped strings) |

**Worktree note:** runs need `PYTHONPATH=$PWD/src:$PWD` (the editable install
points at the primary checkout); the research DB URL comes from the linked `.env`
via `forex_bot.project_env.bootstrap_environ()`.

## 3. Scaffold scope (what this sprint delivers)

1. **Phase 0** — this plan + baseline audit. *(commit)*
2. **Phase 1** — `CAMPAIGN_029_PRECOMMIT_SCOPE.md` (frozen rule) + campaign config
   `configs/campaign_029_usdjpy_range_bar_mtf_breakout.yaml`. *(commit)*
3. **Phase 2** — `scripts/preflight_campaign_029_usdjpy_range_bars.py` + compact
   diagnostics under `research/campaign_029/preflight/`. *(commit)*
4. **Phase 3** — `CAMPAIGN_029_HTF_ALIGNMENT_DESIGN.md`. *(commit)*
5. **Phase 4** — `src/forex_bot/strategies/usdjpy_range_bar_mtf_breakout.py`
   (pure-signal research module) + tests. *(commit)*
6. **Phase 5** — `CAMPAIGN_029_BACKTRADER_PARITY_DESIGN.md` (design only). *(commit)*
7. **Phase 6** — final validation + `CAMPAIGN_029_USDJPY_RANGE_BAR_SCAFFOLD_SUMMARY.md`. *(commit)*

## 4. Hard rules honoured by this sprint

- Do **not** approve any strategy; `approved_strategies.yaml` stays `approved: []`.
- Do **not** enable paper / demo / live; no OANDA API calls; no live credentials.
- Do **not** tune parameters; the precommit rule is fixed *before* any evidence.
- Do **not** run the test lockbox; do **not** produce a trading recommendation.
- Do **not** run full historical strategy evidence. The Phase-2 preflight builds
  range bars purely to **characterise the bar stream** (counts, timing, session
  mix, overshoot) — it emits **no signals, trades, or P&L**, mirroring the already
  committed non-time-bar full-corpus diagnostics.
- Do **not** commit raw M1, DB dumps, generated full range-bar CSVs, `.env`,
  credentials, or bulky artifacts. Full bars stay local & gitignored
  (`research/campaign_029/**` whitelists only compact `*_summary.json` /
  `*_manifest.json` / `*_diagnostics.{json,md}`).

## 5. Known design constraint (carried into Phase 4)

`forex_bot.domain.candles.Granularity` is a **closed** `Literal`
(`M1/M3/M5/M15/M30/H1/H4/D/D1AGG`) — it has **no** range-bar member. Range bars
therefore **cannot** be wrapped in a `CandleFrame`, so the execution frame is a
sequence of `non_time_bars.RangeBar` records. The Phase-4 module is consequently a
**standalone pure-signal research strategy** (its own signal API over prebuilt
range bars + HTF `CandleFrame`s); it is **not** registered in
`strategies/__init__.py` and **not** wired to the executor/loop. This is a
deliberate scaffold boundary, re-stated in the precommit and summary as a blocker
for the future execution sprint.

## 6. Expected next sprint

`research-campaign-029-usdjpy-range-bar-execution-001` — a separate sprint that
runs train/validation evidence against the frozen precommit, builds Backtrader
parity, and only then (if every binding gate passes) classifies a
promotion-review status. **Not run here.**
