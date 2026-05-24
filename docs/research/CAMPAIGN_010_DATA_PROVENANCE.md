# CAMPAIGN_010 — Data Provenance

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-walk-forward-001`
`strategy_evidence: false`

Phase 1 data-provenance record for the **CAMPAIGN_010 walk-forward
evidence sprint**. **This document does not approve the strategy.**
It records what historical OANDA H4 candle data the per-fold backtest
will consume, how it got there, and what guarantees apply.

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper /
> demo / live remain blocked. CAMPAIGN_010 remains
> `candidate-scaffold` until the walk-forward evidence completes.

## 1. Data source — real OANDA practice H4, 7-pair universe

| dimension | value |
|---|---|
| local store | `data/campaign_002.sqlite3` (worktree-relative; symlink to `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3`) |
| broker environment | `practice` (`oanda-practice` source label, recorded per row) |
| host (from prior rehydration record) | `https://api-fxpractice.oanda.com` |
| price components | BA (bid + ask) |
| timeframe | H4 |
| candle completeness | completed candles only (`completed_only=True` on every read) |
| date span per pair | 2020-01-01 → 2026-05-19 (inclusive bar timestamps) |
| credentials used to materialize this data **this sprint** | **none** (the candles were rehydrated by a prior sprint — `oanda-practice-readonly-001` for the six majors and `infra-lean-parity-001` Phase 1 for NZD_USD — and persisted in the gitignored local store) |
| credentials printed | **none** |
| broker account/order/trade/position/transaction endpoint queried this sprint | **none** |
| rehydration script invoked this sprint | **none** (existing store reused; the symlink keeps the worktree fully self-contained for reads) |

## 2. Provenance — per-pair audit (this sprint)

Read-only audit via `forex_bot.data.repositories.{CandleRepo,
DataSourceRepo, InstrumentRepo}`. No OANDA call, no credential
read.

| pair | completed H4 candles | first bar (UTC) | last bar (UTC) | source label | recorded `raw_sha256` prefix | recorded `normalized_sha256` prefix | recomputed `content_hash` prefix |
|---|---:|---|---|---|---|---|---|
| EUR_USD | 9931 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `f56b30030f3abbd6…` | `f5d1d1b193020976…` | `c243674516673796…` |
| GBP_USD | 9931 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `6ea9b168cf234d1d…` | `2c751fec8b0e9f6d…` | `7dabfe8095007635…` |
| USD_JPY | 9932 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `568f4c6104e1f73a…` | `64836ea0f08e21c7…` | `f71d04e9a6c82809…` |
| AUD_USD | 9931 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `710f6aed5875367a…` | `7a19f3e957ea8ee5…` | `fa27466388fd0229…` |
| USD_CAD | 9931 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `9fe3b74d78c5cc5a…` | `dc04b583759ec5c6…` | `3b374b90c94e20e3…` |
| USD_CHF | 9931 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `46a0f6748c7dfc9c…` | `11b0a134792a62a3…` | `64d0a4af0813b658…` |
| NZD_USD | 9935 | 2020-01-01 22:00:00 | 2026-05-19 21:00:00 | `oanda-practice` | `c7c38eb2225dc801…` | `c8724ce78e4c601b…` | `dac3dc41b16b244d…` |
| **total** | **69,522** | | | | | | |

`raw_sha256` is the SHA-256 of the concatenated raw OANDA response
bytes captured at fetch time; `normalized_sha256` is over the
normalized, time-sorted candle rows (deterministic across
re-fetches); `content_hash` (recomputed here from the store) is the
same shape as `normalized_sha256` and must match. Recorded values
live in the `data_sources` table of the store.

Cross-check against the prior rehydration record
[`OANDA_H4_NZDUSD_REHYDRATION_RESULT.md`](OANDA_H4_NZDUSD_REHYDRATION_RESULT.md):
the `normalized_sha256` prefix `c8724ce78e4c601b…` for NZD_USD
matches exactly. The `raw_sha256` is allowed to differ across
re-fetches (cursor / wire-format metadata) but the normalized
content hash is stable — and it matches.

## 3. Instrument metadata audit

| pair | present in `InstrumentRepo` | `pip_location` | `display_precision` |
|---|:---:|---:|---:|
| EUR_USD | yes | -4 | 5 |
| GBP_USD | yes | -4 | 5 |
| USD_JPY | yes | -2 | 3 |
| AUD_USD | yes | -4 | 5 |
| USD_CAD | yes | -4 | 5 |
| USD_CHF | yes | -4 | 5 |
| NZD_USD | yes | -4 | 5 |

Sufficient for the bespoke `BacktestEngine` to size positions for
every CAMPAIGN_010 trade signal.

## 4. Gap summary (within scope this sprint)

The store has no out-of-spec gaps for the 7-pair × 6-year window:

- Every pair has ~9931 H4 bars (NZD_USD 9935; the slightly higher
  count reflects a small page-overlap difference recorded at
  rehydration time per
  [`OANDA_H4_NZDUSD_REHYDRATION_RESULT.md`](OANDA_H4_NZDUSD_REHYDRATION_RESULT.md)).
- First and last bar timestamps are identical across pairs.
- All seven pairs were fetched against the same OANDA practice
  endpoint with the BA price-component flag, identical alignment,
  and the H4 granularity.
- An exhaustive bar-level gap audit is out of scope for this Phase
  1 (the existing `scripts/audit_h4_data_quality.py` does that and
  has been run by prior sprints; the CAMPAIGN_010 backtest itself
  is robust to occasional missing bars because the strategy emits
  no signal when the session-window precondition does not hold).

## 5. Local files created this sprint (uncommitted)

| path | contents | gitignored | committed? |
|---|---|:---:|:---:|
| `data/campaign_002.sqlite3` (symlink) | symbolic link to `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` (the existing real OANDA practice H4 store) | yes (via `/data/` rule + `*.sqlite3` rule) | **no** |

The `git check-ignore -v data/campaign_002.sqlite3` invocation
prints the matching `.gitignore` rule (`.gitignore:52:/data/`);
`git status --short` is clean after the symlink is in place.

## 6. Explicit safety statements

- **No credential** of any kind is read, printed, or logged by this
  sprint's Phase 1.
- **No OANDA call** is made by this sprint's Phase 1.
- **No order, trade, position, or transaction endpoint** is queried
  by this sprint at any phase.
- **No SQLite store, candle CSV, or other bulky data is committed**
  by this sprint. The committed artifact is this document plus a
  pair of `plan.json` / `plan.md` (Phase 2), plus per-fold compact
  summary docs (Phases 3–6).
- **`configs/approved_strategies.yaml` remains `approved: []`**.
  This data provenance check does not approve the strategy.
- **CAMPAIGN_002 verdict (REJECT)** is unchanged; only the
  CAMPAIGN_002 candle store is reused as historical data input.

## 7. Cross-links

- [`ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_PLAN.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`DATA_REHYDRATION_RUNBOOK.md`](DATA_REHYDRATION_RUNBOOK.md)
- [`OANDA_H4_DATA_REHYDRATION.md`](OANDA_H4_DATA_REHYDRATION.md)
- [`OANDA_H4_NZDUSD_REHYDRATION_RESULT.md`](OANDA_H4_NZDUSD_REHYDRATION_RESULT.md)
- [`OANDA_H4_DATA_QUALITY_AUDIT_7PAIR.md`](OANDA_H4_DATA_QUALITY_AUDIT_7PAIR.md)
- [`configs/campaign_010_session_breakout.yaml`](../../configs/campaign_010_session_breakout.yaml)
