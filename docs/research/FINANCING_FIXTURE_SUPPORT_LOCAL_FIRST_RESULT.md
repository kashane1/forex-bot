# Financing Fixture Support — Local-First Result

**Sprint:** `infra-observed-cost-financing-overlay-local-first-001`

## Fixture paths

| Path | Label |
|------|-------|
| `research/financing/fixtures/rates_two_week_*.json` | Committed rate tables (`financing_rates` schema) |
| `research/financing/rates.py` | `default_stress_rate_source()` — synthetic conservative stress |

## Schema

Loaded via `research.financing.fixtures.load_rate_fixture` → `TableRateSource` keyed by `(date, instrument)` with long/short bp or rate fields per existing financing sprint conventions.

## Source labels

- **Synthetic stress:** `default_stress_rate_source()` — `synthetic: true` in overlay manifest
- **Manual fixture mode:** merged table name `manual_fixture_table`; warnings state fixtures are **diagnostic synthetic schedules**, not broker-observed history (even when filenames contain `observed`)

## Limitations

- No broker API calls in this sprint
- No live credential reads
- Committed fixtures do not represent actual account financing charges
- Missing instrument/date → `unavailable_rate_trades` / `HTF_UNAVAILABLE_RATE` per trade

## Why no broker calls

Sprint scope is **local-first overlay infrastructure**. True observed financing requires a future **read-only transaction capture** sprint (`docs/research/OBSERVED_FINANCING_CAPTURE_READ_ONLY_NEXT_PROMPT.md`).

## Tests

Fixture merge, synthetic labeling, unavailable mode — `tests/unit/test_financing_overlay_local_first.py`.

## No-approval statement

Fixtures do not validate strategy edge.
