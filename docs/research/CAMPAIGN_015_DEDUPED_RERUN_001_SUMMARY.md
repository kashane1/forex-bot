# CAMPAIGN_015 Deduped Rerun 001 — Summary

**Branch:** `infra-canonical-candle-dedup-and-campaign015-rerun-001`
**Date:** 2026-05-26

## Commits by phase

| phase | commit | summary |
|---|---|---|
| 0 | `cac03f3` | Contamination memo |
| 1 | `30b4654` | Canonical candle dedupe at load boundary |
| 2 | `38ab9c4` | CAMPAIGN_015 dedupe preflight reporting |
| 3–8 | (this commit) | Deduped rerun evidence + docs |

## Root cause

SQLite stored two rows per H4 bar (local-offset + UTC ISO strings for the
same instant). BT used deduped CSV; bespoke did not. Duplicate bars
corrupted ATR/ADX/range windows, suppressing bespoke signals.

## Dedupe implementation

`CandleRepo.list` → UTC normalise → dedupe `(instrument, granularity,
utc_time)` with `keep_last` → monotonic output. 64,509 duplicate rows
dropped across CAMPAIGN_015 preflight.

## Deduped verdict

**REJECT** — not approved for paper / demo / live.

## Metrics: contaminated vs deduped

| metric | contaminated (stale) | deduped |
|---|---:|---:|
| base exp_r | +0.2300 | **-0.0101** |
| 2x exp_r | +0.1909 | **-0.0283** |
| trades | 164 | **375** |
| fold pass | 0/8 | **2/8** |
| pairs positive | — | **3/7** |

## Null / anti-overfit

**`WITHIN_NULL`** (deduped CAMPAIGN_011 null baseline used).

## Backtrader comparison

**`TOLERABLE_DRIFT`** — BT 288 vs bespoke 375 trades (`strict_test_window=true`).

## Superseded artifacts

Prior CAMPAIGN_015 post-run docs annotated **SUPERSEDED BY DEDUP RERUN**;
contaminated `backtests/CAMPAIGN_015_failed_breakout_reversal/` retained
for audit.

## Safety checks

- `configs/approved_strategies.yaml`: `approved: []`
- No .env / credentials / sqlite3 / bulky trade dumps committed
- pytest 1493 passed; research freeze gate passed

## Files to review first

1. `docs/research/CAMPAIGN_015_DUPLICATE_CANDLE_CONTAMINATION_MEMO.md`
2. `docs/research/CAMPAIGN_015_DEDUPED_RERUN_INTERPRETATION.md`
3. `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/walk_forward/gate_result.json`
4. `src/forex_bot/data/candle_dedupe.py`
5. `docs/research/BACKTRADER_CAMPAIGN_015_DEDUPED_COMPARISON.md`

## Recommended next step

**Stop CAMPAIGN_015** as a promotion path. Prior promising diagnostics
were artifact of duplicate-candle contamination.
