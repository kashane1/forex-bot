# Financing bp/day Fixture Expansion — Status

**Date:** 2026-05-23 · **Branch:** `research-financing-bp-day-fixture-expansion-001`
`strategy_evidence: false`

Headline status of the bp/day fixture expansion sprint.
**Seven rate fixtures committed (one per H4 universe pair),
one new observed-event companion, 16 new tests pass, 7
synthetic reconciliation runs all clean. No broker data
fetched. No MODELED financing produced.**

> No strategy approved. CAMPAIGN_002 remains REJECT. Paper /
> demo / live remain blocked. Every committed fixture
> declares `synthetic: true`; every reconciliation report
> emitted in Phase 5 carries `financing_treatment: estimated`.
> The live-promotion blocker remains.

## 1. Pair coverage

All seven H4 universe pairs now have a committed rate
fixture under
[`research/financing/fixtures/`](../../research/financing/fixtures/):

| pair | rate fixture | base/quote | sample sign (long/short annual bp) |
|---|---|---|---|
| EUR_USD | `rates_two_week_eur_usd.json` (sister sprint) | USD-quote | -18.25 / +9.125 |
| GBP_USD | `rates_two_week_gbp_usd.json` (this sprint) | USD-quote | -14.6 / +7.3 |
| USD_JPY | `rates_two_week_usd_jpy.json` (this sprint) | USD-base + JPY | +18.25 / -36.5 |
| AUD_USD | `rates_two_week_aud_usd.json` (this sprint) | USD-quote | +10.95 / -21.9 |
| USD_CAD | `rates_two_week_usd_cad.json` (this sprint) | USD-base | -10.95 / +5.475 |
| USD_CHF | `rates_two_week_usd_chf.json` (this sprint) | USD-base | +25.55 / -50.4 |
| NZD_USD | `rates_two_week_nzd_usd.json` (this sprint) | USD-quote | +9.125 / -18.25 |

Signs are deliberately varied across pairs (Phase 4 test
`test_rate_sign_variety_across_pairs` enforces this).

## 2. Fixture files added (this sprint)

Total: 7 new JSON files, all under
`research/financing/fixtures/`, each <2 KB:

| file | bytes | kind |
|---|---:|---|
| `rates_two_week_gbp_usd.json` | 1686 | rates |
| `rates_two_week_usd_jpy.json` | 1865 | rates |
| `rates_two_week_aud_usd.json` | 1707 | rates |
| `rates_two_week_usd_cad.json` | 1781 | rates |
| `rates_two_week_usd_chf.json` | 1717 | rates |
| `rates_two_week_nzd_usd.json` | 1691 | rates |
| `observed_aud_usd_long_credit.json` | 1188 | events |

All carry `synthetic: true`, `schema_version: 1`, the
documented synthetic `account_id_hash`
(`c4e91d9f7c03827938cbb2c82608bba023e98f23d52b2f84784cbcf9652df69f`,
SHA-256 of `"fixture-account-001"`), only `fix-*` opaque
ids, and ≥1 `missing_dates` entry per the conventions doc.

Phase 4's `test_no_real_account_looking_ids_in_any_fixture`
pins that no committed fixture contains an
OANDA-account-shaped id (`NNN-NNN-NNNNNNN-NNN`).

## 3. Tests

| file | new cases |
|---|---:|
| `tests/research/test_financing_pair_fixture_expansion.py` | 16 |

Coverage:

- 7-pair coverage (one rate fixture per H4 pair)
- Every rate fixture loads via `load_rate_fixture`
- Synthetic / size / required-keys invariants
- ≥1 `missing_dates` entry per fixture
- No real account-shaped ids anywhere
- Sign-variety across pairs (≥1 each of long+/long-/short+/short-)
- USD-base notional path (USD_JPY: notional = units)
- USD-quote notional path (AUD_USD: notional = units * price)
- AUD_USD observed ↔ rate reconciliation at rel=1e-9 (exact
  3-match, 0-mismatch under skip policy)
- Reconciliation CLI subprocess invocation on AUD_USD pair
- Loader refuses MODELED for every new fixture (existing
  rail extended)
- Defense-in-depth: `calculate_run` refuses a
  TableRateSource with `.treatment` mutated to MODELED
  post-construction (the only way to bypass the loader)
- CLI smoke: every pair runs cleanly against the empty
  observed file
- Subprocess rail: loading every rate fixture in a fresh
  interpreter pulls zero `forex_bot` modules

**16 tests pass.** Full repo suite: **702** passes (686
prior + 16 new). Ruff clean over `src tests scripts
research/parity_verifier research/walk_forward
research/financing`.

## 4. Synthetic run status

Documented in
[`FINANCING_BP_DAY_FIXTURE_EXPANSION_SYNTHETIC_RUNS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_SYNTHETIC_RUNS.md):

| # | run | exit | summary |
|---:|---|---:|---|
| 1 | aud_usd × aud_long_credit / skip | 0 | 3 match, 0 mismatch |
| 2 | aud_usd × aud_long_credit / conservative | 0 | 3 match + 1 missing_in_observed (5/19 fallback fired) |
| 3 | usd_jpy × empty | 0 | empty smoke |
| 4 | usd_cad × empty | 0 | empty smoke |
| 5 | usd_chf × empty | 0 | empty smoke |
| 6 | gbp_usd × empty | 0 | empty smoke |
| 7 | nzd_usd × empty | 0 | empty smoke |

Zero `mismatch` rows across all 7 runs. The single
`missing_in_observed` in Run 2 is the intended behaviour
(conservative fallback fires on the rate fixture's
deliberate 5/19 missing date; the observed fixture
deliberately omits the same date).

Per-run JSON / markdown outputs live under
`/tmp/financing_recon_batch/` and are **not committed**.

## 5. Was any broker / OANDA data fetched?

**No.** This sprint:

- Made zero OANDA calls.
- Issued zero transaction-stream queries.
- Submitted zero orders.
- Read zero credentials from `.env`.
- Did not enable any new endpoint surface.

The fixtures are entirely synthetic; the synthetic runs
operate against local files only.

## 6. Is `MODELED` financing now available?

**No.** Four layers continue to refuse `MODELED`:

- `TableRateSource(treatment=MODELED)` raises at
  construction (fixture-loader rail). The new
  `test_no_new_fixture_can_construct_modeled_rate_source`
  extends this to every committed rate fixture in the
  expanded set.
- `calculate_run` raises if the rate source self-reports
  `MODELED`.
- `_build_report` in the reconciliation CLI raises
  `RuntimeError` if asked to emit `modeled` as the
  treatment.
- The capture script never declares a `financing_treatment`
  at all.

The five-criterion MODELED checklist from
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
§11 is unchanged by this sprint.

## 7. Is the live blocker lifted?

**No.** `financing_treatment_blocks_approval` in
`src/forex_bot/financing.py` is unchanged. `live`
unconditionally requires `MODELED`; no source produces it.
Paper / demo are also still blocked by the empty
approved-strategy registry.

## 8. Safety state (unchanged by this sprint)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.** `paper-loop` and
  `demo-loop` refuse; no `live-loop` exists.
- **No bespoke-engine edit.**
- **No `src/forex_bot/financing.py` edit.**
- **No `src/forex_bot/broker/` edit.**
- **No `research/financing/` Python edit** (only fixture
  data + tests added).
- **No `scripts/reconcile_financing_fixtures.py` or
  `scripts/capture_oanda_observed_financing_pilot.py`
  edit.**
- **No OANDA call performed.**
- **No `.env` read. No credential printed.**
- **No `*.sqlite3` or candle CSV committed.** Per-run
  reconciliation outputs live under `/tmp` and are not
  committed.
- **No new external dependency.**
- **Import isolation grep + subprocess pinned** for every
  loaded fixture.
- **No `MODELED` financing reachable** anywhere in the
  pipeline.
- **No QuantConnect / LEAN.**

## 9. EVIDENCE_MANIFEST.json

The manifest tracks **campaigns**; this sprint adds no
campaign, so `docs/research/EVIDENCE_MANIFEST.json`
requires no entry. Same posture as the four prior
financing sprints. The archive validator continues to
PASS.

## 10. Cross-links

- Sprint plan:
  [`FINANCING_BP_DAY_FIXTURE_EXPANSION_001_PLAN.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_001_PLAN.md)
- Conventions:
  [`FINANCING_BP_DAY_FIXTURE_EXPANSION_CONVENTIONS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_CONVENTIONS.md)
- Synthetic runs:
  [`FINANCING_BP_DAY_FIXTURE_EXPANSION_SYNTHETIC_RUNS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_SYNTHETIC_RUNS.md)
- Sister sprint summaries:
  [`RESEARCH_FINANCING_MODEL_001_SUMMARY.md`](RESEARCH_FINANCING_MODEL_001_SUMMARY.md),
  [`RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md`](RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md),
  [`RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md`](RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md),
  [`RESEARCH_FINANCING_OBSERVED_CAPTURE_PILOT_001_SUMMARY.md`](RESEARCH_FINANCING_OBSERVED_CAPTURE_PILOT_001_SUMMARY.md)
- Fixture schema:
  [`FINANCING_OBSERVED_FIXTURE_SCHEMA.md`](FINANCING_OBSERVED_FIXTURE_SCHEMA.md)
- Calculator protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Future-capture pilot spec:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
