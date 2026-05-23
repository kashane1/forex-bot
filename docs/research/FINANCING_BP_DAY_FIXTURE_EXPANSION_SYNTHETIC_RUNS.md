# bp/day Fixture Expansion — Synthetic Reconciliation Runs

**Date:** 2026-05-23 · **Branch:** `research-financing-bp-day-fixture-expansion-001`
Phase 5 · `strategy_evidence: false`

Records of running `scripts/reconcile_financing_fixtures.py`
against the newly-expanded synthetic fixtures, with exact
commands, exit codes, and per-run summaries. **All runs are
diagnostic only.** No broker / OANDA data was fetched. No
campaign verdict changed. `MODELED` financing remains
unavailable.

> Runs were performed locally; outputs written to
> `/tmp/financing_recon_batch/run-N/` (gitignored).
> Per-run summaries are committed here; per-run JSON /
> markdown artifacts are **not committed** to keep the repo
> small. The committed tests
> (`tests/research/test_financing_pair_fixture_expansion.py`)
> already exercise these reconciliations.

## 1. Environment

- Repo HEAD on
  `research-financing-bp-day-fixture-expansion-001`.
- `--generated-at-utc 2026-05-23T12:00:00+00:00` injected on
  every run for byte-identical reproducibility (modulo the
  output path, which varies per run).
- Output directory: `/tmp/financing_recon_batch/<runname>/`.
- Python `.venv` interpreter; no OANDA env vars set; no
  `.env` read; no network call attempted.

## 2. Commands run

Seven commands, two showing real reconciliation (AUD_USD
under skip + conservative policy) and five smoke-checking
that every new pair's rate fixture is consumable end-to-end:

```bash
# Run 1 — AUD_USD reconciliation under skip
python scripts/reconcile_financing_fixtures.py \
  --observed research/financing/fixtures/observed_aud_usd_long_credit.json \
  --rates    research/financing/fixtures/rates_two_week_aud_usd.json \
  --output   /tmp/financing_recon_batch/aud_skip/ \
  --units 10000 --entry-price 0.6600 --side long \
  --missing-rate-policy skip \
  --generated-at-utc 2026-05-23T12:00:00+00:00

# Run 2 — AUD_USD reconciliation under conservative (default policy)
python scripts/reconcile_financing_fixtures.py \
  --observed research/financing/fixtures/observed_aud_usd_long_credit.json \
  --rates    research/financing/fixtures/rates_two_week_aud_usd.json \
  --output   /tmp/financing_recon_batch/aud_conservative/ \
  --units 10000 --entry-price 0.6600 --side long \
  --missing-rate-policy conservative \
  --generated-at-utc 2026-05-23T12:00:00+00:00

# Runs 3–7 — empty-observed smoke check for each non-EUR pair
for pair in usd_jpy usd_cad usd_chf gbp_usd nzd_usd; do
  python scripts/reconcile_financing_fixtures.py \
    --observed research/financing/fixtures/observed_same_day_no_rollover.json \
    --rates    research/financing/fixtures/rates_two_week_${pair}.json \
    --output   /tmp/financing_recon_batch/${pair}_empty/ \
    --generated-at-utc 2026-05-23T12:00:00+00:00
done
```

## 3. Results

| # | run | rates | observed | policy | exit | rows | match | mismatch | other |
|---:|---|---|---|---|---:|---:|---:|---:|---|
| 1 | `aud_skip` | rates_two_week_aud_usd | observed_aud_usd_long_credit | skip | 0 | 3 | 3 | 0 | — |
| 2 | `aud_conservative` | rates_two_week_aud_usd | observed_aud_usd_long_credit | conservative | 0 | 4 | 3 | 0 | 1 `missing_in_observed` (5/19, fallback fired) |
| 3 | `usd_jpy_empty` | rates_two_week_usd_jpy | observed_same_day_no_rollover | conservative | 0 | 0 | — | — | empty observed → empty report |
| 4 | `usd_cad_empty` | rates_two_week_usd_cad | observed_same_day_no_rollover | conservative | 0 | 0 | — | — | empty |
| 5 | `usd_chf_empty` | rates_two_week_usd_chf | observed_same_day_no_rollover | conservative | 0 | 0 | — | — | empty |
| 6 | `gbp_usd_empty` | rates_two_week_gbp_usd | observed_same_day_no_rollover | conservative | 0 | 0 | — | — | empty |
| 7 | `nzd_usd_empty` | rates_two_week_nzd_usd | observed_same_day_no_rollover | conservative | 0 | 0 | — | — | empty |

### 3.1 Run 1 — `aud_skip` (exit 0)

| metric | value |
|---|---|
| rows | 3 |
| match | 3 |
| mismatch | 0 |
| missing_in_observed | 0 |
| missing_in_calculated | 0 |
| rate_was_missing_count | 0 |
| financing_treatment | `estimated` |

Both the rate fixture and the observed-events fixture omit
2026-05-19. Under `skip` policy, the calculator emits no
event for 5/19; the resulting three calculator events
(Mon 5/18, Wed 5/20 ×3 triple, Thu 5/21) match the
observed `financing` values exactly at rel=1e-9.

### 3.2 Run 2 — `aud_conservative` (exit 0)

| metric | value |
|---|---|
| rows | 4 |
| match | 3 |
| mismatch | 0 |
| missing_in_observed | 1 (5/19) |
| missing_in_calculated | 0 |
| rate_was_missing_count | 1 |
| financing_treatment | `estimated` |

Under `conservative` policy, the calculator fires its
`-1.2 bp/day` fallback on 5/19 (notional 6600 × -1.2/10000
= -0.792). The observed file has no 5/19 row, so the row
is classified `missing_in_observed`, not `mismatch`. Exit
0 is correct: per the protocol, `missing_in_*` rows are
**informational** and do not trigger non-zero exit.

This contrast between runs 1 and 2 is the documented
behaviour for an observed-events fixture that intentionally
agrees with the rate fixture's `missing_dates` list.

### 3.3 Runs 3–7 — empty-observed smoke (exit 0)

Each pair's rate fixture is consumed cleanly against the
empty `observed_same_day_no_rollover.json` fixture:

- The script discovers no observed events.
- Builds zero `PositionInterval`s.
- Calculator returns an empty run report.
- Reconciliation produces `row_count: 0`, exit 0.

The point of these runs is **smoke** — confirming that no
new fixture has a schema problem or content surprise that
breaks the CLI end-to-end. A real reconciliation for these
pairs requires a per-pair observed fixture; only AUD_USD
has one in this sprint (the existing USD_CAD and USD_JPY
event fixtures exist but are intentionally not aligned
with the corresponding rate fixtures — they were designed
for the original calculator tests, not for end-to-end
reconciliation).

## 4. Mismatch classifications

Across all 7 runs, **zero** rows are classified `mismatch`.
The single `missing_in_observed` row in Run 2 is the
intended behaviour, not a regression: the conservative
fallback fires on the rate fixture's deliberate
`missing_dates` entry, and the observed fixture's
deliberate omission of that date keeps it in the
informational `missing_in_observed` bucket.

## 5. Known limitations

- **Only AUD_USD has a real end-to-end observed reconciliation
  pair.** USD_JPY, USD_CAD, USD_CHF, GBP_USD, NZD_USD have
  rate fixtures but no aligned observed fixtures; the
  empty-observed smoke runs (3-7) verify the rate-fixture
  side only. A future sprint could add per-pair observed
  fixtures if a specific test scenario justifies it; the
  conventions doc (§7) explicitly does not require one.
- **No real data anywhere.** Every fixture is synthetic. A
  successful reconciliation against synthetic data shows
  the calculator's conventions are internally consistent
  with the fixture authors' arithmetic — nothing about real
  broker behaviour.
- **`/tmp` outputs are not committed.** Per the sprint
  plan, raw run outputs live under `/tmp/financing_recon_batch/`
  and are excluded from the repo. The summaries above are
  the only committed evidence of the runs.

## 6. No broker / OANDA data was fetched

- No OANDA endpoint was called.
- No transaction stream was opened.
- No order was submitted.
- No credential was read.
- `.env` was not loaded.
- No network connection was attempted.

The runs are pure local-file operations against the
committed synthetic fixtures under
[`research/financing/fixtures/`](../../research/financing/fixtures/).

## 7. MODELED status

**`MODELED` financing remains unavailable.** Every report
above carries `financing_treatment: estimated`. The
four-layer defense-in-depth (loader, calculator,
reconciliation CLI `_build_report`, no rate-source emission
from the capture script) is unchanged. The five-criterion
checklist from
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
§11 is unchanged.

## 8. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- CAMPAIGN_002 remains REJECT.
- Paper / demo / live remain blocked.
- `strategy_evidence` across all runs: `false`.
- `financing_in_engine_pnl` across all runs: `false`.
- `financing_is_live_blocker` across all runs: `true`.

## 9. Cross-links

- Sprint plan:
  [`FINANCING_BP_DAY_FIXTURE_EXPANSION_001_PLAN.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_001_PLAN.md)
- Conventions:
  [`FINANCING_BP_DAY_FIXTURE_EXPANSION_CONVENTIONS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_CONVENTIONS.md)
- Reconciliation CLI:
  [`scripts/reconcile_financing_fixtures.py`](../../scripts/reconcile_financing_fixtures.py)
- Reconciliation protocol:
  [`FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md`](FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md)
- Tests pinning every reconciliation above:
  [`tests/research/test_financing_pair_fixture_expansion.py`](../../tests/research/test_financing_pair_fixture_expansion.py)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
