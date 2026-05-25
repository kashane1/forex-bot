# Bias-of-Fixtures Audit — Artifact Inventory

**Sprint:** `research-bias-of-fixtures-audit-001` · Phase 1
**Date:** 2026-05-24
**Status:** descriptive inventory — no strategy approval, no
campaign verdict change.

> No strategy approved by this document. CAMPAIGN_001–014 keep their
> existing verdicts. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live loops still refuse every
> configured strategy.

This is the audit's enumeration of every fixture and artifact in
scope. Anything below is **read-only** for this sprint; the
inventory simply records its presence, provenance, and any
labeling gap. Nothing here is fabricated — items absent from the
worktree are recorded as such.

The downstream Phase 2 (null-baseline bias) and Phase 3
(cross-campaign comparability) scripts derive their inputs from
this inventory.

---

## 1. Committed campaign artifacts

### 1.1 Walk-forward roll-ups

`backtests/CAMPAIGN_*/walk_forward/{plan.json, results.json}` for
all five campaigns. Every file is present, parseable, and carries
8 fold definitions on the same universe (`2020-01-01` →
`2026-05-20`).

| campaign | results.json sha256 (16) | results size | plan.json sha256 (16) | n_folds | sum(fold_metrics.total_trades) | overall_verdict |
|---|---|---:|---|---:|---:|---|
| CAMPAIGN_010 session_breakout | `36792d75d32b3101` | 5,937 B | `30b7bad99edc9b50` | 8 | 2,791 | REJECT |
| CAMPAIGN_011 random_entry_anchor (null) | `ac6e72942d1a016c` | 5,942 B | `eff542e1a5e5d66e` | 8 | 1,177 | REJECT |
| CAMPAIGN_012 regime_switcher_atr_percentile | `3bea07f2399bda31` | 5,996 B | `f0977b42905125ef` | 8 | 3,726 | REJECT |
| CAMPAIGN_013 cross_pair_currency_strength_rotation | `ddef199dc95b0f38` | 5,852 B | `d7b56323e625866c` | 8 | 7,940 | REJECT |
| CAMPAIGN_014 calendar_event_window_anomaly | `fbf8a0762c3de288` | 6,508 B | `19bf2f69e361fd8a` | 8 | 720 | REJECT |

Inventory totals:
- **5** walk-forward `results.json` files
- **5** walk-forward `plan.json` files
- **16,354** trade rows in fold-metrics aggregation across the five
  campaigns (sum)
- **5** REJECT verdicts (zero remaining ambiguity)

### 1.2 Per-fold per-pair summaries and trade ledgers

Each campaign has 8 folds × 7 pairs = **56** per-pair summary
JSONs and **56** trade CSVs. Every campaign has the full 56 + 56;
no slot is missing.

| campaign | summary.json count | trades.csv count | trades.csv row total (excl. header) |
|---|---:|---:|---:|
| CAMPAIGN_010 session_breakout | 56 | 56 | 2,791 |
| CAMPAIGN_011 random_entry_anchor | 56 | 56 | 1,177 |
| CAMPAIGN_012 regime_switcher_atr_percentile | 56 | 56 | 3,726 |
| CAMPAIGN_013 cross_pair_currency_strength_rotation | 56 | 56 | 7,940 |
| CAMPAIGN_014 calendar_event_window_anomaly | 56 | 56 | 720 |

CSV row totals match the `fold_metrics.total_trades` sums in §1.1
exactly. The per-pair summary `metrics.trade_count` field also
matches the corresponding CSV row count (spot-checked for fold-0
EUR_USD across all five campaigns: 48/48, 12/12, 88/88, 296/296,
15/15).

### 1.3 Trade-CSV schema

The fourteen-column schema is **identical** across all five
campaigns and across all 8 folds × 7 pairs of each (spot check
ran over all 280 trade CSVs; one distinct header set per
campaign; all five header sets equal):

```
bars_held, entry_price, entry_time, exit_price, exit_reason,
exit_time, fill_timing, instrument, pnl, r_multiple, side,
spread_paid_pips, stop_price, units
```

This is the schema the lab's `research.edge_discovery.real_data.
load_campaign_trades()` consumes; the exit-asymmetry, single-pair-
probe, and the new bias-audit scripts all expect it.

### 1.4 Exit-reason vocabulary

Three exit reasons, identical vocabulary across all five campaigns:

| campaign | `time` | `stop` | `eod` |
|---|---:|---:|---:|
| CAMPAIGN_010 session_breakout | 2,107 | 661 | 23 |
| CAMPAIGN_011 random_entry_anchor (null) | 929 | 241 | 7 |
| CAMPAIGN_012 regime_switcher_atr_percentile | 2,953 | 760 | 13 |
| CAMPAIGN_013 cross_pair_currency_strength_rotation | 6,087 | 1,830 | 23 |
| CAMPAIGN_014 calendar_event_window_anomaly | 537 | 174 | 9 |

No campaign is missing an exit class. (CAMPAIGN_014's `eod` class
has only 9 events, but it is present — not zero.)

### 1.5 Walk-forward fold plan alignment

Confirmed: all five campaigns share the **same 8-fold layout**.
The full fold-window tuple
`(fold_index, train_start, train_end, validation_start,
validation_end, test_start, test_end)` matches CAMPAIGN_010's
fold-0 layout exactly for the other four campaigns. The 8 fold
windows are:

| fold | train | validation | test |
|---:|---|---|---|
| 0 | 2020-01-01 → 2021-06-23 | 2021-06-24 → 2021-12-20 | 2021-12-21 → 2022-06-18 |
| 1 | 2020-01-01 → 2021-09-24 | 2021-09-25 → 2022-03-23 | 2022-03-24 → 2022-09-20 |
| 2 | 2020-01-01 → 2021-12-26 | 2021-12-27 → 2022-06-24 | 2022-06-25 → 2022-12-22 |
| 3 | 2020-01-01 → 2022-03-28 | 2022-03-29 → 2022-09-24 | 2022-09-25 → 2023-03-24 |
| 4 | 2020-01-01 → 2022-06-28 | 2022-06-29 → 2022-12-25 | 2022-12-26 → 2023-06-24 |
| 5 | 2020-01-01 → 2022-09-28 | 2022-09-29 → 2023-03-27 | 2023-03-28 → 2023-09-24 |
| 6 | 2020-01-01 → 2022-12-29 | 2022-12-30 → 2023-06-27 | 2023-06-28 → 2023-12-25 |
| 7 | 2020-01-01 → 2023-03-31 | 2023-04-01 → 2023-09-28 | 2023-09-29 → 2024-03-27 |

(Read off `backtests/CAMPAIGN_010_session_breakout/walk_forward/
plan.json`; all four other plans match.)

### 1.6 Pair universe

The 7-major universe is identical across all five campaigns and
all 8 folds of each:

```
AUD_USD, EUR_USD, GBP_USD, NZD_USD, USD_CAD, USD_CHF, USD_JPY
```

### 1.7 Fill model and fill timing

Identical across all five campaigns (per `fold_00_EUR_USD_summary.
json`):

- `granularity`: H4
- `fill_model`: `FillModel(fixed_slippage_pips=Decimal('0.2'),
  spread_slippage_multiplier=Decimal('0.5'))`
- `fill_timing`: `signal_bar_close`

### 1.8 Per-campaign data-request divergence

| campaign | config_hash (12) | data_request_hash (16) | summary `from_time` (fold 0 EUR_USD) | summary `to_time` (fold 0 EUR_USD) |
|---|---|---|---|---|
| CAMPAIGN_010 session_breakout | `c3b236b24b32` | `46318435eea44ad7` | 2021-12-21T02:00:00+00:00 | 2022-06-17T17:00:00+00:00 |
| CAMPAIGN_011 random_entry_anchor | `d5f1238ff3ee` | `46318435eea44ad7` | 2021-12-21T02:00:00+00:00 | 2022-06-17T17:00:00+00:00 |
| CAMPAIGN_012 regime_switcher_atr_percentile | `1ecd6f639a8e` | `7639b8cef0c5f86a` | 2021-04-15T01:00:00+00:00 | 2022-06-17T17:00:00+00:00 |
| CAMPAIGN_013 cross_pair_currency_strength_rotation | `c32083b9b4ab` | `7639b8cef0c5f86a` | 2021-04-15T01:00:00+00:00 | 2022-06-17T17:00:00+00:00 |
| CAMPAIGN_014 calendar_event_window_anomaly | `1757fddc7fe9` | `6c4f9a8fd52f895b` | 2021-06-24T01:00:00+00:00 | 2022-06-17T17:00:00+00:00 |

This is the source of the trade-window asymmetry recorded in the
plan's §6 F0-2:
- {C010, C011} share `data_request_hash 46318435eea44ad7` and
  start their data window at the test_start of the fold (no
  pre-test data fed to the strategy).
- {C012, C013} share `data_request_hash 7639b8cef0c5f86a` and
  start their data window inside the train sub-window
  (≈ 8 months of pre-test history fed to the strategy).
- C014 has its own `data_request_hash 6c4f9a8fd52f895b` and
  starts at the validation_start of the fold (≈ 6 months of
  pre-test history fed to the strategy).

**Implication recorded for Phase 3:** the C012/013/014 strategies
emit trades over `[from_time, to_time]`, not over `[test_start,
test_end]`. C010/011 are clean test-window-only. This is the
single most material comparability finding so far.

## 2. CAMPAIGN_014 event fixture

| dimension | value |
|---|---|
| path | `research/calendar/fixtures/campaign_014_events.json` |
| sha256 (16) | `584a19a8182bb338` |
| size | 37,466 B |
| schema_version | `campaign_014.event_fixture.v1` |
| total events | 281 |
| classes | NFP × 77, FOMC × 51, ECB × 51, BoJ × 51, BoE × 51 |

CPI events are intentionally absent (per
`EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.md` §4). Five classes are
present; CPI was a study aspiration in earlier sprints but is not
in the committed fixture.

## 3. Lean-parity H4 provenance JSONs

Per-pair JSON sidecars recording SHA-256s of the gitignored CSV
exports. All 7 present and parseable.

| pair | candle count | first_ts | last_ts | data_sha256 (16) |
|---|---:|---|---|---|
| AUD_USD | 9,931 | 2020-01-01 | 2026-05-19 | `fb9e619a93fb24d1` |
| EUR_USD | 9,931 | 2020-01-01 | 2026-05-19 | `866d75446030655b` |
| GBP_USD | 9,931 | 2020-01-01 | 2026-05-19 | `354a2da02ce350f8` |
| NZD_USD | 9,935 | 2020-01-01 | 2026-05-19 | `3ba489b194c63734` |
| USD_CAD | 9,931 | 2020-01-01 | 2026-05-19 | `77f9bf8839b20831` |
| USD_CHF | 9,931 | 2020-01-01 | 2026-05-19 | `64ab6151e649080e` |
| USD_JPY | 9,932 | 2020-01-01 | 2026-05-19 | `868b90906652525b` |

Candle counts vary by 1-4 across pairs (9,931-9,935). That is
expected for H4 (different DST schedules / weekend boundaries per
pair) and is not a bias — but it should be noted: per-pair bar
counts are not literally identical.

## 4. H4 candle store (gitignored)

| dimension | value |
|---|---|
| canonical path | `data/campaign_002.sqlite3` |
| present in this worktree? | **NO** — `data/` directory holds `bot.sqlite3` only on this worktree |
| reason | gitignored per `*.sqlite3` + `/data/` in top-level `.gitignore`; the operator's main checkout at `/Users/kashane/dev/forex-bot/data/` holds the canonical file (per `EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.md` §3.1). |
| impact for this audit | This audit runs against **committed** trade ledgers and per-pair summaries. It does **not** need the SQLite store for any of its checks. |

If a future bias check needed the underlying candle bytes (e.g.
to verify candle gaps or DST handling), it would need the
operator's machine. This audit does not need it.

## 5. Synthetic fixtures

| file | size | sha256 (16) | shape |
|---|---:|---|---|
| `research/edge_discovery/sample_fixtures/synthetic_EUR_USD_H4.csv` | 50,001 B | `73c94e5a40a035bb` | 480 H4 bars, deterministic seed 42 |
| `research/edge_discovery/sample_fixtures/synthetic_events.csv` | 199 B | `271641020754eecc` | 6 events × 3 classes |
| `research/edge_discovery/sample_fixtures/_generate_fixtures.py` | 3,884 B | `eea7a238797842ba` | seed-42 generator |
| `research/edge_discovery/sample_fixtures/README.md` | 1,103 B | `a993743cdaff3cdc` | "None of these files is research evidence" |

The README is explicit:
> Small, **committed** fixtures so the lab utilities and Phase 3
> studies are reproducible without a hydrated local SQLite store.
> **None of these files is research evidence**; they are
> illustrative inputs that exercise the lab's loaders, windows,
> costs, and null code-paths end-to-end.

That disclaimer is clear in the README and in the original
synthetic studies' MD outputs (see §6 below). Phase 4 of this
audit confirms whether the disclaimer is sufficient or whether a
machine-readable label needs to be added to the JSON outputs.

## 6. Synthetic vs real-data lab study outputs

There are **two parallel output directories**:

### 6.1 `research/edge_discovery/studies/outputs/` (synthetic / legacy)

Four JSON+MD pairs from the original `research-edge-discovery-lab-
001` sprint:

| file | data_kind in JSON | exploratory_only in JSON | MD has "Exploratory lab output" header? | MD cites synthetic input path? |
|---|---|---|---|---|
| `study_event_window.{json,md}` | **MISSING** | **MISSING** | YES | YES (`sample_fixtures/synthetic_events.csv`) |
| `study_pair_baseline.{json,md}` | **MISSING** | **MISSING** | YES | n/a (cites CAMPAIGN_001–009 report MD verbatim) |
| `study_session.{json,md}` | **MISSING** | **MISSING** | YES | YES (`sample_fixtures/synthetic_EUR_USD_H4.csv`) |
| `study_turnover_cost.{json,md}` | **MISSING** | **MISSING** | YES | n/a (analytical, no candle input) |

**Gap identified:** the JSON forms of these four legacy outputs
do **not** carry a machine-readable `data_kind` field. The MDs
have the disclaimer header, and two of them explicitly name the
synthetic CSV path, but a script that reads only the JSON cannot
tell the file is synthetic-derived. Phase 4 will decide whether
to (a) annotate these JSONs with `data_kind`, (b) move them to
an explicitly-named subdirectory, or (c) add an `outputs/README`
that maps each file to its data kind without modifying the
historical JSON bytes.

### 6.2 `research/edge_discovery/studies/outputs/real/` (real-data)

Eight JSON+MD pairs from the hydrate / single-pair-probe / exit-
asymmetry sprints. **Every one** carries the standard provenance
block (`data_kind == "real"`, `exploratory_only == True`, full
`inputs[]` with sha256, `refusals` block).

| file | data_kind | exploratory_only |
|---|---|---|
| `exit_asymmetry_cross_campaign.{json,md}` | real | True |
| `exit_asymmetry_robustness.{json,md}` | real | True |
| `probe_robustness_eur_usd_c012.{json,md}` | real | True |
| `probe_single_pair_eur_usd_c012.{json,md}` | real | True |
| `real_study_event_window.{json,md}` | real | True |
| `real_study_pair_baseline.{json,md}` | real | True |
| `real_study_session_by_hour.{json,md}` | real | True |
| `real_study_turnover_cost.{json,md}` | real | True |

The real-data corpus is well-labeled and self-describing.

### 6.3 Cross-references from docs

The docs that cite the legacy synthetic outputs:

- `EDGE_DISCOVERY_LAB_001_RESULTS.md` lines 33-37
- `EDGE_DISCOVERY_LAB_001_SUMMARY.md` lines 60-63, 217

These docs internally label their content as synthetic-derived
(the LAB_001 sprint was explicitly the synthetic-fixture sprint
that preceded the hydrate sprint). A reader of those docs is not
misled. The risk is **only** if a script reads the legacy JSON
outputs directly without reading the docs first.

### 6.4 Code that reads the legacy synthetic outputs

`grep -rln "outputs/study_session\|outputs/study_event_window\|
outputs/study_pair_baseline\|outputs/study_turnover_cost"
research/ tests/ src/` returns **zero hits**. No current
production script, lab study, or test reads from
`outputs/study_*.json` or `outputs/study_*.md`. They are static
snapshots cited only by the LAB_001 sprint's own results /
summary docs.

This significantly lowers the severity of the `data_kind`-
missing gap: the gap is a labeling weakness, not an active risk
to any current finding.

## 7. Approval boundary (re-check)

| file | content | invariant satisfied? |
|---|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (with surrounding comments) | YES |
| `forex_bot.approval.StrategyNotApprovedError` | importable | YES |
| `paper-loop refuses` | `['trend_following']` (frozen) | YES |
| `demo-loop refuses` | `['trend_following']` (frozen) | YES |

The audit does not touch any of these. Phase 6's final-validation
re-confirms them.

## 8. Items that are **absent** and the audit accepts as absent

- The H4 SQLite candle store (`data/campaign_002.sqlite3`) is
  gitignored and is not in this worktree. The audit does not
  require it.
- CPI events (intentionally absent from the CAMPAIGN_014 event
  fixture; documented in `EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.
  md` §4). The audit does not require them.
- No artifact silently missing without acknowledgment was
  discovered during this Phase-1 inventory.

## 9. Provenance gaps (logged for Phase 4)

| gap | severity | scope |
|---|---|---|
| legacy synthetic JSONs in `outputs/` lack `data_kind` machine-readable field | low | descriptive; no current script consumes them; MDs are labeled |
| per-pair H4 candle bar counts vary 9,931–9,935 across pairs | informational | expected DST/weekend variance; not a bias |
| C012/013/014 trade ledgers span wider than `[test_start, test_end]` | **moderate** | cross-campaign comparability — Phase 3 must restrict to test window and confirm headline numbers survive |

Phase 4 will decide what to do about the low-severity labeling
gap. Phase 3 will quantify the moderate-severity comparability
gap with the test-window-restricted re-aggregation.

## 10. Inputs every downstream phase will use

For the Phase 2 / Phase 3 bias scripts, the input set is:

```
backtests/CAMPAIGN_010_session_breakout/walk_forward/plan.json
backtests/CAMPAIGN_010_session_breakout/walk_forward/results.json
backtests/CAMPAIGN_010_session_breakout/folds/fold_NN/fold_NN_<PAIR>_summary.json   (56 files)
backtests/CAMPAIGN_010_session_breakout/folds/fold_NN/fold_NN_<PAIR>_trades.csv     (56 files)
… same paths for CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013, CAMPAIGN_014 …
research/calendar/fixtures/campaign_014_events.json    (CAMPAIGN_014 event audit only)
```

Total **285** input files. Every one is committed and reachable
from `git clone`. The audit therefore reproduces from a fresh
clone without operator-local data.

---

## Appendix A — Phase 1 done-conditions

Phase 1 is done when:
- this inventory is committed.
- the inventory makes every committed artifact and every
  intentionally-absent artifact explicit.
- every provenance gap is named, scored for severity, and
  routed to the phase that resolves it.
- `configs/approved_strategies.yaml` is still `approved: []`.

All four pre-conditions are satisfied as of this commit.
