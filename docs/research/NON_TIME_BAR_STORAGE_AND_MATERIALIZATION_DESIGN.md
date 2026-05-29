# Non-Time Bar Storage & Materialization Design

**Sprint:** `infra-range-and-volatility-bars-001` · Phase 7
**Status:** **design only.** Nothing is materialized in this sprint. No strategy, no approval.

This document proposes how range/volatility bars *would* be persisted into the
local Postgres research store **if and when** a future campaign needs them. It
deliberately stops at design: per the sprint's hard rules, we do **not**
bulk-materialize unless it is small and clearly safe, and the recommendation
below is to **delay** until a campaign requires it.

---

## 1. Why not materialize now

- Non-time bars are a pure, deterministic function of canonical M1 + a small
  config (threshold, basis, method). They are cheap to regenerate on demand
  (full corpus folds in seconds-to-minutes per pair; see the full-corpus
  diagnostic) and add no information that M1 + the builder does not already
  contain.
- Materializing now would commit us to a schema and a threshold grid before a
  campaign has told us which thresholds/bases/methods actually matter — risking
  premature, wrong-shaped tables and stale rows.
- The freeze platform's bias is to keep generated bulk artifacts gitignored and
  regenerable, not stored. Materialization is storage; it should be justified by
  a concrete consumer.

**Recommendation: do NOT materialize in this sprint.** Materialize only when a
scaffolded campaign (e.g. a USD_JPY range-bar campaign) pins a specific
`(pair, bar_type, threshold, basis, method)` set and needs repeatable, indexed
reads.

## 2. Proposed schema (when the time comes)

Two viable shapes; the recommended one is a **dedicated table**, not an
extension of `candles`, because non-time bars have extra mandatory provenance
(threshold, basis, method, completion metadata) and a non-time index.

### 2a. Recommended: dedicated `non_time_bars` table

```sql
CREATE TABLE IF NOT EXISTS market_data.non_time_bars (
    instrument           text        NOT NULL,
    bar_type             text        NOT NULL,   -- 'range' | 'volatility'
    method               text        NOT NULL,   -- 'range' | 'abs_close' | 'true_range'
    threshold_mode       text        NOT NULL,   -- 'fixed' | 'atr_scaled'
    threshold_pips       numeric     NOT NULL,   -- effective threshold (per-bar for atr_scaled)
    price_basis          text        NOT NULL,   -- 'bid' | 'ask' | 'mid'
    seq                  bigint      NOT NULL,   -- 0-based ordinal within the (instrument,bar_type,method,threshold,basis) series
    open_time_utc        timestamptz NOT NULL,
    close_time_utc       timestamptz NOT NULL,   -- canonical bar timestamp
    open                 double precision NOT NULL,
    high                 double precision NOT NULL,
    low                  double precision NOT NULL,
    close                double precision NOT NULL,
    volume               bigint      NOT NULL,
    source_count         integer     NOT NULL,
    source_start_utc     timestamptz NOT NULL,
    source_end_utc       timestamptz NOT NULL,
    completion_reason    text        NOT NULL,   -- 'range_up'|'range_down'|'volatility'|'incomplete'
    thresholds_crossed   integer     NOT NULL,
    overshoot_pips       double precision NOT NULL,
    movement_pips        double precision,        -- volatility only (NULL for range)
    incomplete           boolean     NOT NULL DEFAULT false,
    -- provenance / reproducibility
    source_granularity   text        NOT NULL DEFAULT 'M1',
    builder_config_hash  text        NOT NULL,    -- sha256 of the frozen build config
    fetch_batch_id       text        NOT NULL,    -- generating run id
    data_hash            text,                     -- optional per-bar content hash
    created_at_utc       timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (instrument, bar_type, method, threshold_pips, price_basis, seq)
);
CREATE INDEX IF NOT EXISTS non_time_bars_close_idx
    ON market_data.non_time_bars (instrument, bar_type, method, threshold_pips, price_basis, close_time_utc);
```

The natural key is the *series identity* + ordinal `seq` (because two bars can
share a `close_time_utc` is impossible within one series, but indexing by close
time is what HTF-context joins need). `close_time_utc` is the canonical
timestamp for aligning to higher-timeframe context.

### 2b. Rejected: extend `market_data.candles`

Reusing `candles` with a synthetic `granularity` like `RANGE10` is rejected:
the `candles` row has no place for threshold/basis/method/completion metadata,
its `(instrument, granularity, time_utc, source)` key cannot express the
non-time series identity cleanly, and overloading it risks contaminating the
verified M1/M5/M15/H1/H4 materialization invariants. Keep non-time bars in their
own table.

## 3. Bar-type naming convention

- `bar_type`: `range` | `volatility`.
- `method`: `range` (for range bars), `abs_close` | `true_range` (volatility).
- Series label (for filenames / logs / config): `<METHOD>_<THRESHOLD>pip`, e.g.
  `range_10pip`, `abs_close_20pip`, `true_range_10pip`. Matches the diagnostic
  script's labels so artifacts and tables line up.

## 4. Threshold metadata

`threshold_mode`, `threshold_pips`, `method`, `price_basis` are part of the key
and stored per row. For `atr_scaled`, `threshold_pips` is the **per-bar**
effective snapshot; `atr_multiple` and `atr_window` go into `builder_config_hash`
and the run manifest (not a per-row column).

## 5. Source provenance fields

Carried verbatim from the `RangeBar`/`VolatilityBar` records:
`source_count`, `source_start_utc` (= open), `source_end_utc` (= close),
`source_granularity = 'M1'`, plus `completion_reason`, `thresholds_crossed`,
`overshoot_pips`, `movement_pips`, `incomplete`. This makes every stored bar
traceable back to the exact M1 span that produced it.

## 6. `data_hash` / `fetch_batch_id` handling

- `fetch_batch_id`: the generating run's id (uuid), mirroring the M1
  materialization convention — lets a backfill be identified and re-run.
- `builder_config_hash`: sha256 over the frozen builder config (bar_type,
  method, threshold_mode, threshold_pips, atr params, price_basis,
  source_granularity, dedupe policy). Two rows with the same series key but
  different `builder_config_hash` indicate a rule change and must not be mixed —
  the same provenance-fingerprint discipline as `aggregation_config_hash()`.
- `data_hash` (optional): per-bar content hash (OHLC + provenance) for drift
  detection against a re-fold, analogous to the M1 candle `data_hash`.

## 7. Generated-artifact policy (unchanged)

- Full generated bars stay **gitignored** (`research/non_time_bars/**` minus the
  whitelisted `*_summary.json` / `*_manifest.json`). They are regenerable.
- If materialized into Postgres, the DB is the store of record for bulk bars;
  git still only carries compact summaries/manifests. **No DB dumps committed.**
- A materialization run would write a compact `*_manifest.json` (pairs, series,
  row counts, first/last, config hash) — the same compact-artifact discipline as
  `materialize_campaign_026_m3_m30.py`.

## 8. Why full generated bars stay gitignored

They are (a) bulky (tens-to-hundreds of thousands of rows per pair/series),
(b) exactly reproducible from committed M1 + the committed builder + a tiny
config, and (c) carry no reviewable decision content. Committing them would bloat
the repo and duplicate what the deterministic builder already guarantees. The
compact summaries/manifests carry everything a human needs to review.

## 9. If a small, safe materialization is ever wanted now

The only case that would clear the "small and clearly safe" bar: a **single
pair, single series** (e.g. USD_JPY `range_10pip`, mid) — on the order of ~70k
rows. Even then, prefer to let the consuming campaign own the materialization so
the schema is shaped by a real read pattern. This sprint does **not** do it.
