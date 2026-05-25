# Backtrader Lane — Data Adapter Spec

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-001`
**Phase:** 2 of `INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md`
**`strategy_evidence: false`**

The data adapter is the single path the Backtrader secondary lane uses
to reach local candle data. It reads the existing Lean parity export
CSVs (and their committed provenance sidecars), validates them, and
returns Backtrader-ready pandas frames plus per-bar half-spread.

It does **not** call OANDA. It does **not** re-fetch candles. It does
**not** modify source CSVs. It does **not** import the bespoke engine.

## 1. Source artifacts

The lane consumes the same artifact set CAMPAIGN_002 / Lean parity uses:

| artifact | role | committed? |
|---|---|:--:|
| `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv` | candle data (10 cols, OHLC bid + ask + volume) | NO (gitignored bulk) |
| `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.provenance.json` | sha256, count, hash-of-data-request | YES |
| `research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.md` | human-readable manifest | YES |

The CSVs are gitignored regenerable bulk data, locally produced by:

```bash
python scripts/export_lean_parity_data.py \
    --db data/oanda_h4_research.sqlite3 \
    --instrument EUR_USD --from 2020-01-01 --to 2026-05-20
```

(repeat per instrument; the script reads the local SQLite store written
by `scripts/rehydrate_oanda_h4_store.py`. The OANDA store itself is
also gitignored.)

The instrument set is the seven-pair CAMPAIGN_002 universe:

```
EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD
```

## 2. CSV format (consumed, not produced)

Reproduced from `research/lean_parity/lean_h4_export_format.md` so the
contract is documented in the adapter's spec too:

| column | meaning |
|---|---|
| `time` | bar OPEN time, ISO-8601 with UTC offset (17:00-NY aligned H4) |
| `bid_open` `bid_high` `bid_low` `bid_close` | bid OHLC, exact decimal strings |
| `ask_open` `ask_high` `ask_low` `ask_close` | ask OHLC, exact decimal strings |
| `volume` | OANDA tick volume (integer) |

Only completed H4 candles. ISO-8601 timestamps with explicit `+00:00`.
Ascending by time. **No incomplete candles ever pass through this
adapter.**

## 3. Generated outputs

The adapter does not generate persistent files. It is read-only.

If the user wishes to regenerate the CSVs the adapter consumes, they
use the existing `scripts/export_lean_parity_data.py` — **the adapter
does not own that script and does not call it.**

For per-run Backtrader output artifacts (Phase 3+), the runner writes
to `research/backtrader_lane/results/<campaign>/`, which is gitignored
by the new `.gitignore` block:

```
research/backtrader_lane/results/
research/backtrader_lane/exports/**/*.csv
```

## 4. Adapter API (summary)

Module: `research/backtrader_lane/data_adapter.py`.

| symbol | role |
|---|---|
| `EXPECTED_CSV_HEADER` | tuple of the 10 column names in canonical order |
| `CandleProvenance` | dataclass mirror of one `*.provenance.json` |
| `CandleAdapterResult` | dataclass with `mid_df`, `bid_ohlc_df`, `ask_ohlc_df`, `half_spread_close`, `first_ts`, `last_ts`, `bar_count`, `approximation_flags`, plus the verified `csv_sha256` and the loaded `provenance` |
| `compute_csv_sha256(csv_path)` | recompute the sha256 the exporter wrote (`"\|".join(row)` per row, time-sorted) |
| `load_candles(instrument, export_dir=DEFAULT, strict=True)` | the main entry point; returns `CandleAdapterResult` |
| `available_instruments(export_dir)` | sorted list of instruments whose CSV is locally present |
| `expected_instruments(export_dir)` | sorted list of instruments whose provenance sidecar is present (CSV may be gitignored / absent) |
| `manifest_for(result)` | compact dict the Phase 3 runner serialises into `run_manifest.json` |

Error types (all raise with descriptive messages):

| error | when |
|---|---|
| `FileNotFoundError` | CSV or provenance sidecar missing |
| `CandleSchemaError` | CSV header / column order wrong |
| `CandleProvenanceError` | sha256 or row-count drift versus committed provenance (in `strict=True` mode) |
| `ValueError` | empty CSV, OHLC invariants violated, non-monotonic or sub-H4 timestamps |

## 5. Candle completeness rule

The adapter does **not** filter incomplete candles — the exporter has
already filtered them. If an incomplete candle ever slipped through
into a CSV, the adapter would still consume it (no `complete` column
exists in the Lean format). This is consistent with the existing
parity verifier and the bespoke engine, both of which trust the
exporter's filter. The exporter's gate is therefore the single source
of truth for "completed only".

## 6. Timezone / alignment handling

- Timestamps are parsed strictly with `datetime.fromisoformat`.
- Bare `Z` suffix is converted to `+00:00` before parse.
- Timestamps without an explicit timezone are forced to UTC.
- The bar timestamp is the **OPEN** time (per Lean export contract).
  A Backtrader strategy must remember this: `self.data.datetime[0]` is
  the bar's open, not its close.
- 17:00-New-York alignment is inherited from the exporter; the adapter
  does not re-align.

## 7. Bid / ask / mid handling

The Backtrader feed sees **mid** OHLC, computed per-bar as
`(bid + ask) / 2` for each of O, H, L, C. Bid and ask OHLC are carried
separately on the `CandleAdapterResult` so the runner / strategy can
implement a faithful bid/ask-aware fill model in Phase 3 if needed.

A per-bar `half_spread_close = (ask_close - bid_close) / 2` series is
also carried. The default Phase 3 runner will use it as a per-bar
slippage offset applied to the mid close:

```
long fill price  ≈ close_mid + half_spread_close + fixed_slippage_pips
short fill price ≈ close_mid - half_spread_close - fixed_slippage_pips
```

This is a **documented approximation**, not a faithful reproduction of
the bespoke engine. See §8.

## 8. Known approximation points

Recorded by the adapter on every load via
`CandleAdapterResult.approximation_flags`:

1. **`MID_OHLC_DERIVED`** — Backtrader sees mid OHLC, derived from
   bid/ask. The bespoke engine fills at bid/ask directly.
2. **`BAR_OPEN_TIMESTAMP`** — the index is the bar's open time.
   Backtrader strategies must not assume close-aligned timestamps.
3. **`HALF_SPREAD_CLOSE`** — only the close-time half-spread is carried.
   Intra-bar spread dynamics are not modelled.

Additional approximations that emerge in Phase 3+ (slippage formula,
sizing precision, Donchian prior-bars-only, time-stop bar counter, no
RiskEngine, no financing) are flagged on the runner's manifest, not on
the adapter's.

## 9. Tests (Phase 2)

Tiny deterministic fixture: `tests/unit/backtrader_lane/fixtures/`
contains `TEST_PAIR_H4_lean.csv` (12 rows) and a matching
`*.provenance.json`. Built once with
`tests/unit/backtrader_lane/fixtures/build_tiny_csv.py`; the result is
deterministic and committed. The fixture is **synthetic** and **not**
real OANDA data — `strategy_evidence: false`.

| test | what it proves |
|---|---|
| `test_fixture_files_are_present` | the committed fixture is intact |
| `test_expected_csv_header_matches_lean_format_doc` | the contractual column order is preserved |
| `test_load_candles_basic_shape` | adapter returns the documented dataclass |
| `test_load_candles_provenance_sha_round_trip` | sha256 the adapter computes equals the committed sidecar value |
| `test_load_candles_mid_ohlc_invariants` | mid OHLC invariants hold; half-spread > 0 |
| `test_load_candles_monotonic_4h_spacing` | timestamps are strictly monotonic and exactly 4h apart on the fixture |
| `test_load_candles_first_last_ts` | the reported `first_ts` / `last_ts` match the fixture |
| `test_load_candles_missing_provenance_raises_file_not_found` | clean error when sidecar absent |
| `test_load_candles_missing_csv_raises_file_not_found` | clean error when CSV gitignored / absent |
| `test_load_candles_sha_drift_raises_provenance_error` | tampered CSV → `CandleProvenanceError` |
| `test_load_candles_bad_header_raises_schema_error` | column-order drift → `CandleSchemaError` |
| `test_available_and_expected_instruments` | helper instrument-discovery functions |
| `test_manifest_for_includes_approximation_flags` | manifest carries the approximation flags |
| `test_data_adapter_imports_no_forex_bot` | independence from `src/forex_bot/` |
| `test_data_adapter_imports_no_broker_modules` | no OANDA / LEAN imports |

Validation:

```bash
python -m pytest tests/unit/backtrader_lane/test_data_adapter.py -v
# → 15 passed in 0.13s
```

## 10. Safety

- No file under `src/forex_bot/backtesting/` is touched.
- No network. No broker. No credentials.
- No CSV is modified — read-only consumer.
- `research/backtrader_lane/results/` is gitignored.
- The adapter has no `forex_bot` import (CI-grep enforced).
- The adapter has no `backtrader.brokers.oandabroker` /
  `backtrader.stores.oandastore` / `backtrader.feeds.oanda` / LEAN /
  QuantConnect import (CI-grep enforced).

`strategy_evidence: false`. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011,
CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
CAMPAIGN_014 remains scaffold-only. Paper / demo / live remain blocked.
