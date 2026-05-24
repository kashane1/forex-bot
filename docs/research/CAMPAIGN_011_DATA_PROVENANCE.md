# CAMPAIGN_011 — Data Provenance

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-walk-forward-001`
`strategy_evidence: false`

Phase 1 data-provenance record for the **CAMPAIGN_011
walk-forward evidence sprint**. **This document does not approve
the strategy.** It records what historical OANDA H4 candle data
the per-fold backtest will consume and verifies that data hashes
match the CAMPAIGN_010 audit verbatim (the comparison is on the
entry signal alone, so the data must be identical).

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.
> **CAMPAIGN_011 is a null model — cannot be approved by design.**

## 1. Data source — real OANDA practice H4, 7-pair universe (REUSED)

| dimension | value |
|---|---|
| local store | `data/campaign_002.sqlite3` (worktree-relative; **gitignored symlink** to `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3`) |
| symlink status | **already present** (created by `research-asian-london-session-breakout-walk-forward-001` Phase 1; verified read-only by Phase 0 of this sprint) |
| broker environment | `practice` (`oanda-practice` source label, recorded per row) |
| host (from prior rehydration record) | `https://api-fxpractice.oanda.com` |
| price components | BA (bid + ask) |
| timeframe | H4 |
| candle completeness | completed candles only (`completed_only=True` on every read) |
| date span per pair | 2020-01-01 → 2026-05-19 (inclusive bar timestamps) |
| credentials used to materialize this data **this sprint** | **none** (data was rehydrated by prior sprints — `oanda-practice-readonly-001` for the six majors and `infra-lean-parity-001` Phase 1 for NZD_USD — and persisted in the gitignored local store) |
| credentials printed | **none** |
| broker account/order/trade/position/transaction endpoint queried this sprint | **none** |
| rehydration script invoked this sprint | **none** (existing store reused) |

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

### 2.1 Verification against CAMPAIGN_010

**All hash prefixes match CAMPAIGN_010's
[`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md)
§2 verbatim.** This confirms:

- The same physical SQLite store backs both sprints.
- No data has changed since CAMPAIGN_010's evidence run.
- The CAMPAIGN_011 entry-signal comparison is on **identical
  data** to CAMPAIGN_010 — only the entry signal differs.

This is the key precondition for the comparison the null-model
anchor is designed to enable.

## 3. Gap summary (within scope this sprint)

The store has no out-of-spec gaps for the 7-pair × 6-year window
(identical to CAMPAIGN_010's audit):

- Every pair has ~9,931 H4 bars (NZD_USD 9,935; slightly higher
  count reflects a small page-overlap re-fetch recorded at
  rehydration time per
  [`OANDA_H4_NZDUSD_REHYDRATION_RESULT.md`](OANDA_H4_NZDUSD_REHYDRATION_RESULT.md)).
- First and last bar timestamps are identical across pairs.
- All seven pairs were fetched against the same OANDA practice
  endpoint with the BA price-component flag, identical
  alignment, and the H4 granularity.

## 4. Local files created this sprint (uncommitted)

| path | contents | gitignored | committed? |
|---|---|:---:|:---:|
| (none) | the `data/campaign_002.sqlite3` symlink was created by a prior sprint and is unchanged this sprint | yes (via `/data/` rule + `*.sqlite3` rule) | **no** |

No new file is created by this Phase 1. `git status --short`
remains clean. `git check-ignore -v data/campaign_002.sqlite3`
returns the matching `.gitignore` rule (`.gitignore:52:/data/`).

## 5. Explicit safety statements

- **No credential** of any kind is read, printed, or logged by
  this sprint's Phase 1.
- **No OANDA call** is made by this sprint's Phase 1.
- **No order, trade, position, or transaction endpoint** is
  queried by this sprint at any phase.
- **No SQLite store, candle CSV, or other bulky data is
  committed** by this sprint. The committed artifacts are
  this document plus a pair of `plan.json` / `plan.md`
  (Phase 2), plus per-fold compact summary docs (Phases 3–7).
- **`configs/approved_strategies.yaml` remains `approved: []`**.
  This data provenance check does not approve the strategy.
- **CAMPAIGN_002 verdict (REJECT)** is unchanged; only the
  CAMPAIGN_002 candle store is reused as historical data input.
- **CAMPAIGN_010 verdict (REJECT)** is unchanged.

## 6. Cross-links

- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md)
  (CAMPAIGN_011's hashes verify byte-for-byte against this)
- [`DATA_REHYDRATION_RUNBOOK.md`](DATA_REHYDRATION_RUNBOOK.md)
- [`OANDA_H4_DATA_REHYDRATION.md`](OANDA_H4_DATA_REHYDRATION.md)
- [`OANDA_H4_NZDUSD_REHYDRATION_RESULT.md`](OANDA_H4_NZDUSD_REHYDRATION_RESULT.md)
- [`configs/campaign_011_random_entry_anchor.yaml`](../../configs/campaign_011_random_entry_anchor.yaml)
