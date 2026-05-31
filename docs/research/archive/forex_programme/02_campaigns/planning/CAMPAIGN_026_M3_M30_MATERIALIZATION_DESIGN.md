# CAMPAIGN_026 — M3 / M30 materialization design

**Phase 1 of the timeframe-ladder diagnostic.** Adds M1-derived **M3** and **M30**
research timeframes so the C025 Donchian + HTF idea can be tested off M5. Infra-only;
no strategy evidence, no approval, no broker calls.

## 1. Did M3/M30 already exist?

**No.** Phase 0 DB audit (research Postgres `market_data.candles`) found:

- Present (materialized from M1, `source=m1_materialized`): **M5, M15, H1, H4M1**.
- Present (native, for D1AGG): **H4** (`source=oanda-practice`).
- Canonical source: **M1** (`source=oanda-practice-m1`), 12.79M rows, 7/7 majors,
  2021-05-27 → 2026-05-26.
- **M3 and M30: absent** — zero rows at either granularity.

So both must be materialized from canonical M1 (Phase 2).

## 2. Changes made (this commit)

All additive; no existing behavior altered.

| File | Change |
|---|---|
| `src/forex_bot/domain/candles.py` | `Granularity` literal: add `"M3"` (`"M30"` already present). Comment explains M3/M30 are M1-derived research TFs with no native broker source. |
| `src/forex_bot/data/timeframe_aggregation.py` | `TargetGranularity` literal: add `"M3"`, `"M30"`. `_TARGET_MINUTES`: add `M3:3`, `M30:30`. The generic `_aggregate_fixed_minutes` / `_bucket_start` already handle any non-240 bucket size, so no new bucketing logic. |
| `src/forex_bot/data/m1_timeframe_materialization.py` | Add `MATERIALIZED_DIAGNOSTIC_FROM_M1 = ("M3","M30")` and `SUPPORTED_MATERIALIZATION_TARGETS` (= canonical + diagnostic). `STORAGE_GRANULARITY`: add `M3→M3`, `M30→M30`. `_TARGET_MINUTES`: add `M3:3`, `M30:30`. `MATERIALIZED_FROM_M1` and `AGGREGATION_CONFIG` **unchanged**. |
| `scripts/materialize_m1_derived_timeframes.py` | `_resolve_targets` validates `--targets` against `SUPPORTED_MATERIALIZATION_TARGETS`; default (no `--targets`) stays the canonical core set. Help text updated. |
| `tests/unit/test_timeframe_aggregation.py` | New M3/M30 tests (OHLCV, timestamp, bucket alignment, incomplete-omit, mark-incomplete). |
| `tests/unit/test_m1_timeframe_materialization.py` | New tests: hash-stability guard, diagnostic-set membership, `verify_materialized_pair` for M3. |

## 3. Aggregation rules (identical to the canonical set)

M3/M30 are produced by the **same** `aggregate_m1_candles` path as M5/M15/H1:

- **Source:** canonical M1 only (`oanda-practice-m1`). No broker re-fetch.
- **Bucketing:** fixed-minute, UTC minute-of-day aligned. M3 buckets at minutes
  `00,03,06,…`; M30 at `00,30`. (H4 alone uses NY-17:00 alignment; M3/M30 do not.)
- **OHLCV build:** open = first source open; high = max source high; low = min source
  low; close = last source close; volume = Σ source volume; bid/ask/mid all preserved
  independently. (Verified in unit tests.)

## 4. Timestamp policy

**Bucket-start** timestamps (same convention as M5/M15/H1). An M3 bar stamped
`HH:00` covers source minutes `HH:00, HH:01, HH:02`. An M30 bar stamped `HH:00`
covers `HH:00…HH:29`.

## 5. Completeness policy

**Complete buckets only** (`missing_policy="omit"`, the materialization default). A
bucket is complete iff it has exactly `bucket_minutes` source M1 candles, none
missing, all `complete=True`. Incomplete buckets (weekend edges, gaps, partial
trailing bucket) are **omitted** — never fabricated. Confirmed by
`test_m3_missing_minute_omits_block_by_default`.

## 6. Source / provenance policy

- Stored `source = m1_materialized` (`MATERIALIZED_SOURCE`) — same tag as M5/M15/H1.
- Stored `granularity = "M3"` / `"M30"` (`STORAGE_GRANULARITY`). No native broker M3/M30
  exists in this repo, so there is **no name collision** (contrast H4, stored as
  `H4M1` to disambiguate from native broker H4).
- Each materialization stamps `aggregation_config_hash()` into its run manifest.

### Config-hash stability (deliberate)

`aggregation_config_hash()` fingerprints the **shared M1-derivation ruleset**
(`source_granularity`, `missing_policy`, alignment tz/hour). Its `targets` field lists
the **canonical recurring set** `(M5,M15,H1,H4)`. We **intentionally did not** add
M3/M30 to `MATERIALIZED_FROM_M1` / `AGGREGATION_CONFIG`, so the hash stays pinned at
**`f9b7246b79a0635c`** — the value already recorded in
`research/m1_timeframe_materialization/*.json` for the existing M5/M15/H1/H4M1 bars.

Rationale: M3/M30 obey the *identical* rules, only the bucket size differs (which is
implied by the granularity label itself). Keeping the hash stable means:
(a) the provenance of already-materialized canonical bars is untouched; (b) M3/M30
manifests carry the same ruleset fingerprint, correctly asserting "derived by the same
rules"; (c) routine incremental materialization behavior is unchanged (default targets
remain the canonical core; M3/M30 are opt-in). A unit test
(`test_aggregation_config_hash_unchanged_by_diagnostic_targets`) locks this invariant.

## 7. Validation commands

```
# unit (run with the worktree src ahead of the editable install):
PYTHONPATH=$PWD/src python -m pytest \
  tests/unit/test_timeframe_aggregation.py \
  tests/unit/test_m1_timeframe_materialization.py -q
ruff check src/forex_bot/data/timeframe_aggregation.py \
  src/forex_bot/data/m1_timeframe_materialization.py \
  src/forex_bot/domain/candles.py scripts/materialize_m1_derived_timeframes.py

# materialize (Phase 2), local M1 only, no broker:
PYTHONPATH=$PWD/src python scripts/materialize_m1_derived_timeframes.py \
  --all-majors --targets M3,M30
PYTHONPATH=$PWD/src python scripts/materialize_m1_derived_timeframes.py \
  --all-majors --targets M3,M30 --verify-only
```

> **Worktree note:** this repo's editable install (`_editable_impl_forex_bot.pth`)
> points at the *primary* checkout's `src`, so anything run from this worktree must
> prepend `PYTHONPATH=$PWD/src` or it will silently exercise the main checkout's code.

## 8. Safety notes

- No broker/OANDA calls; derivation reads canonical M1 already in Postgres.
- No raw candles, DB dumps, `.env`, or credentials committed — only code + tests now;
  Phase 2 commits compact JSON verification summaries only.
- No executor/broker/strategy/approval changes. `approved_strategies.yaml` untouched.
- Default recurring materialization unchanged; M3/M30 strictly opt-in via `--targets`.
