# Financing Reconciliation — Synthetic Runs

**Date:** 2026-05-23 · **Branch:** `research-financing-reconciliation-tooling-001`
Phase 4 · `strategy_evidence: false`

Records of running `scripts/reconcile_financing_fixtures.py`
against the committed synthetic fixtures, with the exact
commands, inputs, exit codes, and per-row summaries. **All
runs are diagnostic only.** No broker / OANDA data was
fetched. No campaign verdict changed. `MODELED` financing
remains unavailable.

> Runs were performed locally; outputs written to
> `/tmp/financing_reconcile_runs/run{1..5}/` (gitignored).
> Only the per-run summaries are committed here; the
> per-run JSON / markdown artifacts themselves are
> **deliberately not committed** to keep the repo small and
> avoid duplicating tested deterministic output. The committed
> tests
> (`tests/research/test_financing_reconciliation_tooling.py`)
> already exercise every input pair below.

## 1. Environment

- Repo HEAD on `research-financing-reconciliation-tooling-001`
  branch.
- `--generated-at-utc 2026-05-23T12:00:00+00:00` injected
  on every run for byte-identical reproducibility.
- Output directory: `/tmp/financing_reconcile_runs/runN/`.
- Python `.venv` interpreter; no env vars set; no `.env`
  read; no network call attempted.

## 2. Commands run

All commands are pure local-file operations.

```bash
# Run 1 — full match with skip policy
python scripts/reconcile_financing_fixtures.py \
  --observed research/financing/fixtures/observed_multi_day_with_triple.json \
  --rates    research/financing/fixtures/rates_two_week_eur_usd.json \
  --output   /tmp/financing_reconcile_runs/run1/ \
  --missing-rate-policy skip \
  --generated-at-utc 2026-05-23T12:00:00+00:00

# Run 2 — default conservative policy (expected mismatch on the
# rate fixture's intentional 5/19 gap)
python scripts/reconcile_financing_fixtures.py \
  --observed research/financing/fixtures/observed_multi_day_with_triple.json \
  --rates    research/financing/fixtures/rates_two_week_eur_usd.json \
  --output   /tmp/financing_reconcile_runs/run2/ \
  --missing-rate-policy conservative \
  --generated-at-utc 2026-05-23T12:00:00+00:00

# Run 3 — observed file that already omits the missing-rate
# date, paired with the same rates fixture under skip policy
python scripts/reconcile_financing_fixtures.py \
  --observed research/financing/fixtures/observed_missing_rate_fallback.json \
  --rates    research/financing/fixtures/rates_two_week_eur_usd.json \
  --output   /tmp/financing_reconcile_runs/run3/ \
  --missing-rate-policy skip \
  --generated-at-utc 2026-05-23T12:00:00+00:00

# Run 4 — observed file with zero rollover events (same-day open/close)
python scripts/reconcile_financing_fixtures.py \
  --observed research/financing/fixtures/observed_same_day_no_rollover.json \
  --rates    research/financing/fixtures/rates_two_week_eur_usd.json \
  --output   /tmp/financing_reconcile_runs/run4/ \
  --generated-at-utc 2026-05-23T12:00:00+00:00

# Run 5 — error policy explicitly exercising the missing-rate
# trap (expected exit 5)
python scripts/reconcile_financing_fixtures.py \
  --observed research/financing/fixtures/observed_multi_day_with_triple.json \
  --rates    research/financing/fixtures/rates_two_week_eur_usd.json \
  --output   /tmp/financing_reconcile_runs/run5/ \
  --missing-rate-policy error \
  --generated-at-utc 2026-05-23T12:00:00+00:00
```

## 3. Results

### Run 1 — `skip` policy, multi-day fixture

| field | value |
|---|---|
| observed | `research/financing/fixtures/observed_multi_day_with_triple.json` |
| rates | `research/financing/fixtures/rates_two_week_eur_usd.json` |
| missing_rate_policy | `skip` |
| **exit code** | **0** |
| rows | 4 |
| match | 3 |
| mismatch | 0 |
| missing_in_observed | 0 |
| missing_in_calculated | 1 (the 5/19 the rate fixture omits) |
| rate_was_missing_count | 0 |
| rate_missing_dates (from rates file) | `["2026-05-19"]` |

The skipped date matches the rate fixture's
`missing_dates` entry — agreement between the two
representations is precisely the reconciliation pattern's
intent.

### Run 2 — `conservative` policy, multi-day fixture

| field | value |
|---|---|
| observed | `research/financing/fixtures/observed_multi_day_with_triple.json` |
| rates | `research/financing/fixtures/rates_two_week_eur_usd.json` |
| missing_rate_policy | `conservative` (default) |
| **exit code** | **2** |
| rows | 4 |
| match | 3 |
| mismatch | **1** (Tue 2026-05-19) |
| missing_in_observed | 0 |
| missing_in_calculated | 0 |
| rate_was_missing_count | 1 |

On 2026-05-19 the calculator fires its conservative
fallback (`-1.2 bp/day * 10800 = -1.296` USD) while the
observed fixture has `-0.054` USD — the diff is `1.242`.
The exit code `2` correctly flags this as a `mismatch`,
demonstrating that the script will surface a real
calculator-vs-broker disagreement at the per-row level.

### Run 3 — `skip` policy, fallback-paired observed

| field | value |
|---|---|
| observed | `research/financing/fixtures/observed_missing_rate_fallback.json` |
| rates | `research/financing/fixtures/rates_two_week_eur_usd.json` |
| missing_rate_policy | `skip` |
| **exit code** | **0** |
| rows | 2 |
| match | 2 |
| mismatch | 0 |
| missing_in_observed | 0 |
| missing_in_calculated | 0 |
| rate_was_missing_count | 0 |

The fallback-paired observed file deliberately omits the
5/19 row that the rate fixture also omits. Under `skip`
both the observed and the calculator are silent on 5/19,
so no row appears for that date. The remaining 5/18 and
5/20 rows match exactly.

### Run 4 — same-day no-rollover observed

| field | value |
|---|---|
| observed | `research/financing/fixtures/observed_same_day_no_rollover.json` |
| rates | `research/financing/fixtures/rates_two_week_eur_usd.json` |
| missing_rate_policy | `conservative` |
| **exit code** | **0** |
| rows | 0 |
| match | 0 |
| mismatch | 0 |
| missing_in_observed | 0 |
| missing_in_calculated | 0 |
| rate_was_missing_count | 0 |

Empty observed fixture ⇒ empty PositionInterval list ⇒
zero calculator events ⇒ zero report rows. The script
exits cleanly. The window field uses the injected
`--generated-at-utc` so the empty-path output is
deterministic.

### Run 5 — `error` policy, intentional missing-rate trap

| field | value |
|---|---|
| observed | `research/financing/fixtures/observed_multi_day_with_triple.json` |
| rates | `research/financing/fixtures/rates_two_week_eur_usd.json` |
| missing_rate_policy | `error` |
| **exit code** | **5** (`EXIT_MISSING_RATE_ERROR`) |
| rows | n/a (script aborted before writing) |

The calculator raises `MissingFinancingRateError` on
2026-05-19; the CLI catches it, prints a strict error
message to stderr (no credential value, no path
disclosure beyond the user-supplied fixture path), and
exits with code 5. No `reconciliation.json` /
`reconciliation.md` are written. This exit-code path is
also covered by the test suite.

## 4. Mismatch classifications observed

Across the five runs, the only `mismatch` row produced is
in Run 2 on 2026-05-19, exactly the date the rate fixture
flags in `missing_dates`. Every other reconciliation is
either `match` or one of the informational
`missing_in_*` classes.

## 5. Why these results are diagnostic only

A perfect reconciliation between calculator predictions and
**synthetic** observed events demonstrates only that the
calculator's conventions reproduce the values the fixtures
were constructed to encode. It is not evidence of
real-broker behaviour. The numbers are determined by:

- the bp/day table mirrored from
  `src/forex_bot/financing.CONSERVATIVE_BP_PER_DAY`;
- the conservative fallback in
  `FinancingCalculatorConfig.conservative_fallback_bp_per_day`;
- the synthetic event-row values in the fixtures, which
  were chosen to reconcile against that bp/day table.

Until a future capture pilot produces real
`DAILY_FINANCING` events, the tool cannot establish that
the calculator matches OANDA — only that the calculator
matches itself.

## 6. Confirmation no broker / OANDA data was fetched

- No OANDA endpoint was called.
- No transaction stream was opened.
- No order was submitted.
- No credential was read.
- `.env` was not loaded.
- No network connection was attempted.

The runs were pure local-file operations against the
committed synthetic fixtures under
`research/financing/fixtures/`.

## 7. Confirmation no committed bulky output

- Per-run artifacts (`reconciliation.json`,
  `reconciliation.md`) live under
  `/tmp/financing_reconcile_runs/runN/` and are
  **not** committed.
- This document lists only the per-run summaries and exit
  codes (small, hand-summarized).
- No SQLite, no candle CSV, no large export.

## 8. Safety state (unchanged by Phase 4)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- CAMPAIGN_002 remains REJECT.
- Paper / demo / live remain blocked.
- `financing_treatment` across all runs: `estimated`
  (never `modeled`).
- `strategy_evidence` across all runs: `false`.
- `financing_in_engine_pnl` across all runs: `false`.
- `financing_is_live_blocker` across all runs: `true`.

## 9. Cross-links

- Sprint plan:
  [`FINANCING_RECONCILIATION_TOOLING_001_PLAN.md`](FINANCING_RECONCILIATION_TOOLING_001_PLAN.md)
- CLI protocol:
  [`FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md`](FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md)
- Script:
  [`scripts/reconcile_financing_fixtures.py`](../../scripts/reconcile_financing_fixtures.py)
- Tests:
  [`tests/research/test_financing_reconciliation_tooling.py`](../../tests/research/test_financing_reconciliation_tooling.py)
- Fixtures:
  [`research/financing/fixtures/README.md`](../../research/financing/fixtures/README.md)
- Future capture pilot spec:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
