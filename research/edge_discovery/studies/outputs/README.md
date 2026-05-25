# Edge-discovery lab output corpus — synthetic vs real

This directory holds **two** parallel output sets. They are NOT
interchangeable as evidence.

## `./` (this directory) — synthetic / legacy

The four file pairs at this level are static snapshots from the
original `research-edge-discovery-lab-001` sprint. They were
generated against the committed **synthetic** fixtures in
`research/edge_discovery/sample_fixtures/`:

| file | data kind | underlying fixture |
|---|---|---|
| `study_session.{json,md}` | **synthetic** | `sample_fixtures/synthetic_EUR_USD_H4.csv` (480 H4 bars, seed 42) |
| `study_event_window.{json,md}` | **synthetic** | `sample_fixtures/synthetic_events.csv` (6 events × 3 classes) |
| `study_pair_baseline.{json,md}` | **synthetic-derived** | cites CAMPAIGN_001-009 report Markdown verbatim — superseded by the real-data version |
| `study_turnover_cost.{json,md}` | **analytical** | no candle input — analytical sweep, but constants were derived from synthetic-shape calibration |

**The Markdown files** carry an "Exploratory lab output. Not a
strategy verdict" header and (for the two that have a candle
input) cite the synthetic CSV path explicitly in their "inputs"
block.

**The JSON files DO NOT carry a machine-readable `data_kind` /
`exploratory_only` field** (this is a historical labeling
weakness; the schema convention was introduced in the
hydrate sprint and not back-applied to these legacy files).

> Reader check: if you are scripting against `outputs/*.json` and
> you have not opened the corresponding `.md`, treat every file
> in this directory as `data_kind = "synthetic"` and
> `exploratory_only = True` by default.

**No current code reads these legacy files.** `grep -rln` across
`research/`, `tests/`, and `src/` returns zero hits on
`outputs/study_*`. They are static cited-only artifacts of the
LAB_001 sprint.

## `./real/` — real-data outputs

Every file in `outputs/real/` carries the standard provenance
block in its JSON:

- `provenance.data_kind == "real"` (never `"synthetic"` — silent
  substitution is explicitly disallowed by
  `assert_real_data_kind` in `research/edge_discovery/real_data.py`)
- `provenance.exploratory_only == True`
- `provenance.inputs[]` with `{path, sha256, kind, rows}` for
  every artifact actually consumed
- `verdict_word_ban_acknowledged: true`
- `refusals.{approves_strategy, changes_campaign_verdict,
  proposes_parameter_tune, writes_to_approved_strategies_yaml}`
  all `false`

These are the files the lab's binding tests in
`tests/research/edge_discovery/` validate.

## Which directory should new studies write to?

- **Synthetic-fixture studies** (used by tests, illustrative
  reproductions for fresh-clone CI) → write here, top-level
  `outputs/`, and add an entry to this README.
- **Real-data studies** → write to `outputs/real/`, carry the
  full provenance block, never substitute synthetic data without
  setting `data_kind = "synthetic-fallback"`.

Mixing the two in the same JSON file is **not allowed**. If your
study has both a real-data path and a synthetic-fallback path
(like `study_real_session_by_hour.py` does), the single output
file lands in `outputs/real/` and the provenance.data_kind field
distinguishes which path the run actually took.

## Bias-of-fixtures audit (2026-05-24)

The `research-bias-of-fixtures-audit-001` sprint scanned this
corpus and confirmed:

- the legacy synthetic JSONs (above) have no active code reading
  them → low risk from the missing `data_kind` field;
- every real-data output in `./real/` carries the full provenance
  block;
- the binding tests in `tests/research/edge_discovery/
  test_bias_of_fixtures.py` lock both directories' invariants in
  place.

See `docs/research/BIAS_OF_FIXTURES_AUDIT_001_RESULT.md` for the
full audit result.
