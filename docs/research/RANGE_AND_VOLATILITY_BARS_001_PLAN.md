# RANGE_AND_VOLATILITY_BARS_001 — Plan

**Sprint:** `infra-range-and-volatility-bars-001`
**Type:** Infrastructure + validation only. **NOT a strategy campaign.**
**Date opened:** 2026-05-29
**Status at open:** research freeze intact; `configs/approved_strategies.yaml` = `approved: []`; paper/demo/live blocked.

---

## Purpose

Build, test, and document **reusable, deterministic infrastructure** for constructing two
families of *non-time-based* bars from the existing local M1 corpus:

1. **Range bars** — a new bar completes when price travels a configured number of pips from
   the bar open.
2. **Volatility bars** — a new bar completes when a cumulative realized-movement proxy
   (absolute close-to-close, or true range) reaches a configured number of pips.

The deliverable is the *capability* plus compact diagnostics that let a **future** sprint
decide whether to scaffold a campaign on these bars (with higher-timeframe context). This
sprint deliberately stops short of any edge search.

## Non-goals (hard rules for this sprint)

- Do **not** approve any strategy. `approved_strategies.yaml` stays `approved: []`.
- Do **not** run a strategy campaign, backtest a strategy, or tune strategy parameters.
- Do **not** create `CAMPAIGN_0xx` (no placeholder campaign needed; this is data infra).
- Do **not** run paper/demo/live; do **not** modify executor/broker behavior.
- Do **not** call OANDA APIs or use live credentials.
- Do **not** commit `.env`, credentials, SQLite DBs, raw M1 data, bulky generated bar
  datasets, or Postgres dumps. Bulky generated artifacts stay gitignored.
- Commit only compact summaries / manifests.

## Source data assumptions

- Canonical source = **local OANDA-practice M1** in the Postgres research store
  (`market_data.candles`, `granularity = 'M1'`), reached only through the existing
  `PostgresCandleStore` / `ResearchDatabaseConfig` (local-host-guarded, prod/live name
  refused). No network.
- Seven majors, ~5y each (verified at open):
  EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD — ~1.79M–1.84M M1 rows,
  2021-05-27 → 2026-05-26, counts matching `EXPECTED_M1_COUNTS`.
- Each M1 row carries bid/ask/mid OHLC, `complete`, `volume`, `time_utc`.
- **Known modeling limit:** M1 OHLC is *not* tick data. Within one M1 candle we do not know
  the true path of price between open/high/low/close. All intrabar threshold logic must use
  an explicit, documented, deterministic ordering assumption (see specs).

## Bar definitions (summary; full rules in the spec docs)

- **Range bar:** opens at the close-context price of the first contributing M1 row; completes
  the first time `high - open >= threshold` or `open - low >= threshold` (in pips). One M1
  candle may complete several range bars in sequence (large-move handling) — this must be
  deterministic and lookahead-free.
- **Volatility bar:** accumulates a movement proxy bar-by-bar; completes when the running sum
  reaches the threshold. Two proxies implemented:
  - `abs_close` — cumulative |close_t − close_{t-1}| in pips.
  - `true_range` — cumulative true range in pips.
  - Optional `atr_scaled` threshold derived from a *prior completed* rolling window only.

## Lookahead-bias risks (and how we prevent them)

- **Future M1 leaking into the current bar.** Builders consume M1 strictly in timestamp
  order; a bar's OHLC and completion decision use only rows at-or-before the completing row.
- **Intrabar path ambiguity.** With OHLC-only data, the true within-candle path is unknown. We
  adopt a single documented assumption (open → first-extreme → second-extreme → close, with a
  conservative "adverse extreme first" tie-break) and never peek at the next candle to resolve
  it. The assumption is a *modeling choice*, documented as a limitation, not a hidden bias.
- **ATR-scaled thresholds.** Any ATR/volatility-scaled threshold uses only completed prior
  bars/windows; the current forming bar never contributes to its own threshold.
- **Incomplete final bar.** The trailing partial bar (threshold not yet reached at corpus end)
  is dropped by default and only emitted when explicitly requested, flagged `incomplete=True`.

## Generated-artifact policy

- Core builders are pure functions over in-memory rows — **no DB writes, no broker calls.**
- Diagnostics write **compact JSON summaries/manifests** under `research/non_time_bars/`.
- Full generated bars (CSV/parquet/JSONL) are **local-only and gitignored**
  (`research/non_time_bars/*` ignored; only `*_summary.json` / `*_manifest.json` whitelisted).
- No materialization into Postgres in this sprint (storage is *designed* in Phase 7, not run),
  unless trivially small and clearly safe — default is delay until a campaign needs it.

## Validation plan

- Unit tests (`tests/test_non_time_bars.py`) cover: fixed-pip completion, JPY vs non-JPY pip
  conversion, OHLC correctness, provenance fields, incomplete-final-bar default/override,
  determinism, unsorted/duplicate rejection, multi-threshold crossing within one M1 candle,
  both volatility proxies, ATR-scaled prior-only window, price-basis bid/ask/mid, and explicit
  no-future-leak assertions.
- Helper-function tests for the diagnostic script.
- Smoke diagnostic (one pair, bounded window) before any full-corpus run.
- Full-corpus diagnostic for all seven pairs across the recommended grid.
- Repo gates at open and close: `pytest tests/ -q`, `ruff check`,
  `check_research_freeze.py`, `validate_research_archive.py`, `scan_artifacts_for_secrets.py`.

## Future strategy-campaign handoff

Phase 8 drafts the next-sprint prompt. The recommended successor is **one** of:
(1) scaffold a single-pair USD_JPY range-bar campaign,
(2) scaffold a non-time-bar research preflight/comparison lane, or
(3) materialize chosen non-time bars into Postgres once diagnostics identify sane thresholds.
That sprint is **not** executed here.

## Phase map

| Phase | Output |
|------|--------|
| 0 | This plan; baseline audit; gitignore policy. |
| 1 | `RANGE_BAR_CONSTRUCTION_SPEC.md`, `VOLATILITY_BAR_CONSTRUCTION_SPEC.md`. |
| 2 | `src/forex_bot/data/non_time_bars.py` builders. |
| 3 | `tests/test_non_time_bars.py`. |
| 4 | `scripts/generate_non_time_bar_diagnostics.py` + helper tests. |
| 5 | Smoke diagnostic + `NON_TIME_BAR_SMOKE_DIAGNOSTIC_RESULT.md`. |
| 6 | Full-corpus diagnostic + `NON_TIME_BAR_FULL_CORPUS_DIAGNOSTIC_RESULT.md`. |
| 7 | `NON_TIME_BAR_STORAGE_AND_MATERIALIZATION_DESIGN.md` (design only). |
| 8 | `NEXT_SPRINT_PROMPT_AFTER_RANGE_AND_VOLATILITY_BARS_001.md`. |
| 9 | Final validation + `RANGE_AND_VOLATILITY_BARS_001_SUMMARY.md`. |
