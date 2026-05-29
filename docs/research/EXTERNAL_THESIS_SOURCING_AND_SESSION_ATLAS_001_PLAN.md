# External Thesis Sourcing & Session Atlas 001 — Plan

**Sprint:** `external-thesis-sourcing-and-session-atlas-001`
**Branch:** `research-external-thesis-sourcing-and-session-atlas-001` (fresh from `origin/main` @ `018c0aa`)
**Date opened:** 2026-05-28
**Status:** research / diagnostic only — **NOT** a campaign, **NOT** an execution, **NOT** an approval.

---

## 1. Purpose

The C022/C023/USD_JPY microstructure diagnostic thread is closed and merged. Every
internal indicator-confluence variant we have tried (trend/pullback/MTF-confluence
families) has produced **no actionable entry edge** and no survivable post-entry
management edge. Continuing to invent internal indicator permutations is
threshold-mining, not research.

This sprint changes the search direction:

1. **Stop inventing internal indicator variants.** Define an explicit, written
   framework for evaluating *externally-sourced*, structurally-distinct FX strategy
   theses **before** any code is written.
2. **Build a USD_JPY session / volatility / spread atlas** from the existing
   read-only materialized M1/M5/M15/H1/H4 data, so that we can judge which theses are
   even *plausible* on this instrument before a future campaign is ever designed.
3. **Score** candidate theses against the atlas and against documented prior failures.
4. **Decide** whether one thesis is ready for a future *precommit-design* sprint, or
   whether more diagnostics are required, or whether strategy research should pause.

The atlas is descriptive market structure, not an edge. Nothing in this sprint asserts
tradable edge, and no thesis is implemented.

---

## 2. Non-goals (explicit)

This sprint will **NOT**:

- Create `CAMPAIGN_024` / C024.
- Execute `CAMPAIGN_023` / C023 (incl. the ADX22 sibling).
- Implement a trading strategy or signal.
- Run a campaign or backtest of a strategy.
- Alter any existing campaign verdict or rewrite historical metrics.
- Modify `configs/approved_strategies.yaml` except to *verify* it remains `approved: []`.
- Enable or unblock paper / demo / live.
- Modify broker / executor / order / live behavior.
- Call OANDA mutation / order APIs, or use live trading credentials.
- Commit `.env`, credentials, DBs, raw candle dumps, parquet, or large CSVs.
- Present descriptive statistics as tradable edge.
- Threshold-mine a strategy.

Any future campaign thesis must be **precommitted in a separate later sprint**, not here.

---

## 3. Safety rules (operating constraints)

- Work in phases; commit after each meaningful phase.
- Local materialized M1/M5/M15/H1/H4 data is read **read-only**.
- `.env` symlinks are locally authorized + gitignored; they may be used **only** for
  research-DB (`FOREX_BOT_RESEARCH_DATABASE_URL`) access. Credentials are never printed.
- The research DB is `localhost` Postgres (`forex_bot`, schema `market_data`). No
  production DB, no OANDA APIs are touched.
- The 2025-07+ test window remains a **sealed lockbox** and is not opened.
- Bulky atlas outputs are gitignored; only compact summaries are committed.

---

## 4. Prior closeout summary (what we already know)

From the merged USD_JPY microstructure thread (`origin/main`):

- **C022/C023 pullback-resolution family: RETIRED** unless a genuinely new external
  thesis appears.
- **C023 ADX22 sibling: not executed, not supported.**
- **C024: not created / NOT_READY.**
- **USD_JPY microstructure entry diagnostic: CLOSED / NOT_READY.**
- **USD_JPY post-entry trade-management diagnostic: CLOSED / NOT_READY.**
- Post-entry early-exit counterfactuals *reduced* expectancy.
- No strategy is approved; `approved_strategies.yaml` is `approved: []`.
- Paper / demo / live remain blocked.

Reference closeout docs (verified present this sprint):

- `docs/research/C022_C023_USDJPY_MICROSTRUCTURE_THREAD_CLOSEOUT.md`
- `docs/research/NEXT_RESEARCH_LANE_AFTER_USDJPY_MICROSTRUCTURE_CLOSEOUT.md`
- `docs/research/NEXT_SPRINT_PROMPT_AFTER_USDJPY_MICROSTRUCTURE_CLOSEOUT.md`
- `docs/research/USDJPY_MICROSTRUCTURE_THREAD_CLOSEOUT_AND_MERGE_READINESS_SUMMARY.md`

USD_JPY base-trade sample from C022 (reference only): 306 trades (train 133 / val 173),
win rate 0.379, mean R −0.0005 — i.e. no entry edge in the prior family.

---

## 5. Local data availability (verified this sprint, read-only)

Research Postgres `market_data.candles`, instrument `USD_JPY`, full spread coverage
(`spread_open/high/low/close` non-null on every row):

| granularity | rows | min time | max time |
|---|---|---|---|
| M1 | 1,844,454 | 2021-05-26 | 2026-05-26 |
| M5 | 362,519 | 2021-05-26 | 2026-05-26 |
| M15 | 118,035 | 2021-05-26 | 2026-05-26 |
| H1 | 28,013 | 2021-05-26 | 2026-05-26 |
| H4 | 9,959 | 2020-01-01 | 2026-05-26 |
| H4M1 | 5,448 | 2021-05-26 | 2026-05-26 |

Columns available: bid/ask OHLC, mid OHLC, **spread OHLC**, volume, complete flag.
The sqlite DBs (`data/campaign*.sqlite3`) hold H1/H4/D only; M1/M5/M15 are Postgres-only.

**Split windows (C022 convention, reused for atlas slicing):**

- train: `2021-06-01 .. 2023-12-31`
- validation: `2024-01-01 .. 2025-06-30`
- test: `2025-07-01 .. present` — **SEALED LOCKBOX, not used in this sprint.**

M1/M15 history begins 2021-05-26, which covers the train-window start. The atlas is
built only on train+validation; the test window is excluded.

---

## 6. Atlas dimensions (Phase 2)

The atlas buckets USD_JPY M15 bars (with M1 used for finer spread/excursion stats and
H1/H4 for higher-timeframe context) along:

1. **Session bucket:** Tokyo, London, NY, London/NY overlap, rollover, off-hours
   (defined in NY time, with explicit UTC mapping and DST handling).
2. **Hour of day** in both New York time and UTC.
3. **Weekday.**
4. **Spread:** median, p90, p95 spread (pips); spread/ATR ratio.
5. **Volatility:** ATR, realized range, rolling volatility percentile / regime.
6. **Directional behavior:** forward return over 1/4/8/16 M15 bars; trend-continuation
   probability; mean-reversion probability; range-expansion probability.
7. **Noise / tradability:** average MFE/MAE after arbitrary timestamps; false-breakout
   likelihood (where measurable); whipsaw likelihood.

Outputs:

- `research/usdjpy_session_atlas/usdjpy_session_atlas_summary.json` (compact, committed)
- `docs/research/USDJPY_SESSION_VOLATILITY_SPREAD_ATLAS.md` (narrative findings)
- Any large per-bar dumps are gitignored.

Reuses existing `research/cost_atlas/` (session bucketing, spread metrics) and
`research/edge_discovery/costs.pip_value_for` where applicable.

---

## 7. External thesis sourcing criteria (Phase 1)

A candidate thesis is evaluated (before any code) on:

1. Structural distinctness from failed internal indicator-confluence families.
2. Plausible economic / market-structure mechanism.
3. Compatibility with USD_JPY.
4. Compatibility with M1/M15/H1/H4 data.
5. Sufficient sample size.
6. Objective codability.
7. Realistic transaction-cost survival.
8. Low lookahead risk.
9. Low threshold-mining risk.
10. Whether it can be precommitted cleanly.

Thesis categories considered: session/time-of-day; Tokyo/London/NY transitions;
macro/calendar windows; volatility expansion/compression; carry/rates/risk-off;
previous-session high/low sweeps; opening-range behavior; range breakout/fakeout;
trend-day vs chop-day; mean reversion after extreme intraday extension.

---

## 8. Expected artifacts

| phase | artifact |
|---|---|
| 0 | `docs/research/EXTERNAL_THESIS_SOURCING_AND_SESSION_ATLAS_001_PLAN.md` (this doc) |
| 1 | `docs/research/EXTERNAL_FX_THESIS_SOURCING_FRAMEWORK.md` |
| 2 | `scripts/build_usdjpy_session_volatility_spread_atlas.py`, `research/usdjpy_session_atlas/usdjpy_session_atlas_summary.json`, `docs/research/USDJPY_SESSION_VOLATILITY_SPREAD_ATLAS.md` |
| 3 | `docs/research/USDJPY_EXTERNAL_THESIS_CANDIDATE_SCORECARD.md` |
| 4 | `docs/research/NEXT_THESIS_AFTER_EXTERNAL_SOURCING_AND_ATLAS.md` |
| 5 | `docs/research/NEXT_SPRINT_PROMPT_AFTER_EXTERNAL_THESIS_AND_SESSION_ATLAS.md` |
| 6 | `docs/research/EXTERNAL_THESIS_SOURCING_AND_SESSION_ATLAS_001_SUMMARY.md` |

---

## 9. Validation commands (run Phase 0 baseline + Phase 6 final)

```
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

**Phase 0 baseline result (2026-05-28):**

- `pytest tests/ -q` → **1996 passed, 3 skipped** (pre-existing data-absence skips:
  `test_cost_atlas.py` local H4 store absent; 2× `test_compare_entries.py` C008 CSVs absent).
- `ruff check` → **All checks passed.**
- `check_research_freeze.py` → **ALL CHECKS PASSED** (loops refuse; `approved: []`; no credentials).
- `validate_research_archive.py` → **ALL CHECKS PASSED** (all campaign verdicts non-approval).
- `scan_artifacts_for_secrets.py` → **PASSED** (value scan skipped: no real creds in env; pattern scan clean).

---

## 10. Explicit no-C024 / no-C023 / no-approval statement

This sprint creates **no** `CAMPAIGN_024`, executes **no** `CAMPAIGN_023` (incl. ADX22),
implements **no** strategy, runs **no** campaign, changes **no** verdict, approves
**no** strategy, and leaves paper/demo/live **blocked**. `configs/approved_strategies.yaml`
remains `approved: []`. The output is documentation + one read-only analysis script +
compact atlas summaries. Any decision to design a campaign is deferred to a future,
separately-precommitted sprint.
