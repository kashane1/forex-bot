# Edge Discovery Lab — Real Artifact Inventory (Hydrate Sprint 001)

**Sprint id:** `research-edge-discovery-lab-hydrate-001`
**Phase:** 1
**Date:** 2026-05-24
**Status:** descriptive inventory — no strategy approval, no
campaign verdict change.

> No strategy approved by this document. CAMPAIGN_001–014 keep their
> existing verdicts. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live loops still refuse every
> configured strategy.

---

## 1. Goal of this inventory

Before Phase 2 extends the edge-discovery loaders, this document
enumerates every real research artifact already present in this
branch's working tree that the lab could legitimately ingest, plus
the artifacts that are intentionally absent and why.

The "real vs local-only vs committed" status determines what each
real-data study can rerun under git-pull-and-go reproducibility,
versus what depends on the operator's local OANDA snapshot.

## 2. Committed and reachable from `git clone`

### 2.1 Walk-forward result roll-ups (CAMPAIGN_010–014)

Per-campaign aggregate walk-forward results, suitable for the
pair-baseline and null-baseline studies. All five files share the
schema:
`{plan, fold_metrics[], aggregate{...}, overall_verdict, strategy_evidence}`.

| campaign | path | verdict | strategy_evidence | folds | total_trades | aggregate_expectancy_r |
|---|---|---|:---:|---:|---:|---:|
| CAMPAIGN_010 session_breakout | [`backtests/CAMPAIGN_010_session_breakout/walk_forward/results.json`](../../backtests/CAMPAIGN_010_session_breakout/walk_forward/results.json) | REJECT | false | 8 | 2,791 | −0.0408 |
| CAMPAIGN_011 random_entry_anchor (**null model**) | [`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json) | REJECT | false | 8 | 1,177 | **−0.0024** |
| CAMPAIGN_012 regime_switcher_atr_percentile | [`backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/results.json`](../../backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/results.json) | REJECT | false | 8 | 3,726 | −0.0521 |
| CAMPAIGN_013 cross_pair_currency_strength_rotation | [`backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/results.json`](../../backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/results.json) | REJECT | false | 8 | 7,940 | −0.0564 |
| CAMPAIGN_014 calendar_event_window_anomaly | [`backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/results.json`](../../backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/results.json) | REJECT | false | 8 | 720 | −0.1477 |

CAMPAIGN_011 is explicitly a **null-model anchor**, not a candidate
strategy. Per
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
it is the floor every future real candidate must clear by a
meaningful margin. The hydrate sprint will use this for the new real
null baseline (replacing the lab's prior reliance on CAMPAIGN_005's
fixed-30-bar random-entry expectancy by pair).

### 2.2 Per-fold per-pair backtest summaries

Each campaign has `folds/fold_NN/fold_NN_<PAIR>_summary.json` (8
folds × 7 pairs × 5 campaigns = **280 summary JSONs**). Schema
(verified against CAMPAIGN_010, 011, 014 — identical):

```
{
  "instrument", "strategy_name", "strategy_version",
  "granularity": "H4",
  "from_time", "to_time",
  "config_hash", "data_request_hash",
  "fill_model", "fill_timing",
  "metrics": {
    "total_return_pct", "final_equity", "starting_equity",
    "max_drawdown_pct", "max_drawdown_duration_bars",
    "sharpe", "sortino", "profit_factor",
    "expectancy_r", "average_r", "median_r",
    "win_rate", "average_win", "average_loss",
    "trade_count", "largest_single_loss",
    "average_spread_paid_pips", "exposure_pct"
  }
}
```

These power the real per-pair turnover and pair-level baseline
studies — no need to re-execute any backtest, just aggregate
across folds and pairs.

### 2.3 Per-fold per-pair trade ledgers

Each fold/pair also has `fold_NN_<PAIR>_trades.csv` (5 campaigns ×
8 folds × 7 pairs = **280 trade CSVs**). Schema (verified against
CAMPAIGN_014 EUR_USD fold_00):

```
instrument, side, units, entry_time, exit_time,
entry_price, exit_price, stop_price,
pnl, r_multiple, bars_held,
spread_paid_pips, exit_reason, fill_timing
```

Row counts per campaign (sum across all folds × pairs, minus
header):

| campaign | trade rows (total) |
|---|---:|
| CAMPAIGN_010 session_breakout | 2,791 |
| CAMPAIGN_011 random_entry_anchor | 1,177 |
| CAMPAIGN_012 regime_switcher_atr_percentile | 3,726 |
| CAMPAIGN_013 cross_pair_currency_strength_rotation | 7,940 |
| CAMPAIGN_014 calendar_event_window_anomaly | 720 |

These power the real event-window continuation-vs-reversal study
(CAMPAIGN_014 entries with timestamps already aligned to the event
fixture) and the real turnover/cost study (spread_paid_pips and
r_multiple per executed trade).

### 2.4 CAMPAIGN_014 event fixture

| dimension | value |
|---|---|
| path | [`research/calendar/fixtures/campaign_014_events.json`](../../research/calendar/fixtures/campaign_014_events.json) |
| schema version | `campaign_014.event_fixture.v1` |
| coverage | 2020-01-01 → 2026-05-20 UTC |
| event classes | NFP, FOMC, ECB, BoJ, BoE |
| total events | **281** (NFP 77, FOMC 51, ECB 51, BoJ 51, BoE 51) |
| event schema | `event_id` (string), `event_class` (string), `event_time_utc` (RFC-3339 with TZ) |
| source attribution | each class has a `name` + canonical official URL in the fixture header |

This is the real fixture the lab's prior sprint flagged as missing.
It powers the real event-window continuation-vs-reversal study
directly.

### 2.5 Lean-parity H4 provenance manifests

Per-pair JSON sidecars that record the SHA-256 of the corresponding
gitignored CSV export. Useful for the hydrated lab to **verify which
candle bytes the local CSV came from** without re-fetching:

```
research/lean_parity/exports/campaign_002_h4/
  AUD_USD_H4_lean.provenance.json
  EUR_USD_H4_lean.provenance.json
  GBP_USD_H4_lean.provenance.json
  NZD_USD_H4_lean.provenance.json
  USD_CAD_H4_lean.provenance.json
  USD_CHF_H4_lean.provenance.json
  USD_JPY_H4_lean.provenance.json
  EXPORT_MANIFEST.md
```

Each manifest holds: `instrument`, `granularity`, `source`,
`candle_count`, `first_ts`, `last_ts`, `data_sha256`,
`campaign_002_data_request_hash`. Example
[`EUR_USD_H4_lean.provenance.json`](../../research/lean_parity/exports/campaign_002_h4/EUR_USD_H4_lean.provenance.json):
9,931 candles, range 2020-01-01T22:00:00Z → 2026-05-19T21:00:00Z,
`data_sha256 = 866d75446030655b…`.

### 2.6 Existing committed campaign reports (CAMPAIGN_001–009)

The lab's existing pair-baseline study (`study_pair_baseline.py`)
already cites these verbatim from
`backtests/CAMPAIGN_00X_*_REPORT.md`. No change required — the lab
keeps using them, but the hydrate addendum will note that
**CAMPAIGN_011 is now the binding null baseline** (per its
NULL_BASELINE_INTERPRETATION) and CAMPAIGN_005 becomes a secondary
cross-reference for the fixed-30-bar shape only.

### 2.7 Synthetic fixtures from the prior lab sprint

Committed and unchanged by this sprint:

```
research/edge_discovery/sample_fixtures/
  synthetic_EUR_USD_H4.csv   (480 bars, seed-42)
  synthetic_events.csv       (6 events × 3 classes)
  _generate_fixtures.py
```

These remain the fallback the lab uses when a real artifact is
absent. The hydrate sprint does NOT delete or modify them.

## 3. Available locally but **not** committed (gitignored)

The lab can read these on the operator's machine but cannot
distribute them via git. The hydrate sprint's loaders must detect
their presence, log it, and gracefully fall back to synthetic
fixtures with `synthetic-fallback` provenance when they are absent.

### 3.1 H4 SQLite candle store

| dimension | value |
|---|---|
| canonical worktree-relative path | `data/campaign_002.sqlite3` |
| actual physical location (operator) | `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` |
| size | ~110 MB |
| pattern in `.gitignore` | `*.sqlite3`, `/data/` |
| schema (tables) | `candles`, `data_sources`, `instruments`, `schema_version`, + ops tables |
| H4 coverage | 7 majors × 9,931–9,935 candles = 69,522 H4 bars, 2020-01-01T22:00 → 2026-05-19T21:00 UTC |
| also holds | D1 + H1 bars for the same pairs |
| canonical `data_sources` rows | each pair has a CAMPAIGN_002 full-range row with `raw_sha256` and `normalized_sha256` matching CAMPAIGN_010/011/012/013/014 data-provenance docs verbatim |
| present **in this worktree?** | **NO** (worktree's `data/` has `bot.sqlite3` only — the operator's symlink lives at the main checkout, `/Users/kashane/dev/forex-bot/data/`) |

### 3.2 Lean-parity H4 CSV exports

`research/lean_parity/exports/**/*.csv` — gitignored per the
top-level `.gitignore`. Regenerable via
`scripts/export_lean_parity_data.py` against the SQLite store. Only
the provenance JSONs (§2.5) are committed.

These are equivalent to the SQLite store for read-only lab use; the
lab will prefer the SQLite store because it carries the canonical
`data_sources` provenance rows and avoids any CSV-canonicalization
ambiguity.

## 4. Genuinely absent (not committed and not local)

Nothing in scope for this sprint is genuinely absent on this branch
once items §2 and §3 are considered. The two items the prior lab
summary listed as "blockers / limitations" are both now addressable:

| prior limitation | resolution |
|---|---|
| CAMPAIGN_010–014 artifacts missing | **PRESENT** on this branch — see §2.1–2.3 |
| Real seven-pair H4 OHLC fixture missing | **PRESENT** in §3.1 (operator-local SQLite); the lab will read it through the existing `data/campaign_002.sqlite3` worktree convention used by every CAMPAIGN_010+ sprint, with explicit synthetic fallback. |
| Real NFP / FOMC / CPI event fixture missing | **PRESENT** in §2.4 (CAMPAIGN_014 events fixture). Note: ECB / BoJ / BoE are present *instead* of CPI — same dimensional category (scheduled macro release), so the lab can either widen its "event class" terminology or run the study on the exact NFP+FOMC subset. |

CPI events are not in the committed fixture. The lab will report
that absence in the study output instead of fabricating CPI dates.

## 5. Files the hydrate sprint may NOT modify

To preserve the freeze and the prior lab summary's verdict-word
ban, this sprint will not modify any of:

- `configs/approved_strategies.yaml`
- `configs/paper.yaml`, `configs/practice.yaml`,
  `configs/live.example.yaml`
- the loops module (`src/forex_bot/loops/...`)
- the broker module (`src/forex_bot/broker.py` and friends)
- the evidence manifest (`docs/research/EVIDENCE_MANIFEST.json`)
- the evidence index (`docs/research/EVIDENCE_INDEX.md`)
- `docs/research/STRATEGY_STATUS.md`
- any `backtests/CAMPAIGN_*/walk_forward/results.json` or
  per-fold summary / trade CSV (read-only inputs to the lab)
- `docs/research/CAMPAIGN_*_STATUS.md` /
  `CAMPAIGN_*_WALK_FORWARD_RESULT.md` (verdict-bearing campaign
  docs)

## 6. Provenance requirements every Phase 3 output must satisfy

Each real-data study output (`.json` and `.md`) must include a
`provenance` block with:

- `data_kind`: `real` or `synthetic-fallback` (never silent
  substitution).
- `inputs[]`: list of `{path, sha256, kind, rows}` for every
  artifact actually consumed.
- `date_coverage`: `{start_utc, end_utc}` of the input window.
- `pair_universe`: list of pairs actually included.
- `limitations[]`: anything the study could *not* answer due to
  artifact absence (e.g. "CPI events absent from committed fixture
  → study restricted to NFP / FOMC / ECB / BoJ / BoE").
- `exploratory_only: true` — non-removable.

The existing `research/edge_discovery/report.py` reporter already
enforces the verdict-word ban; Phase 2 will extend it (or add a
small companion) to require this provenance block when the new
loaders are used.
