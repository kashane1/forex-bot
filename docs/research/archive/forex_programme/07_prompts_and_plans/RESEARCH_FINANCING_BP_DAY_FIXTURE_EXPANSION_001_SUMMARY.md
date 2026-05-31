# Financing bp/day Fixture Expansion Sprint 001 — Summary & Handoff

**Date:** 2026-05-23 · **Branch:** `research-financing-bp-day-fixture-expansion-001`
`strategy_evidence: false`

Sprint outcome and handoff for the synthetic rate-fixture
expansion sprint. **Seven rate fixtures committed (one per H4
universe pair), one new observed-event companion, 16 new tests
pass, 7 synthetic reconciliation runs all clean. No broker
data fetched. No MODELED financing produced.**

> **No strategy is approved. CAMPAIGN_002 remains REJECT.**
> Paper / demo / live remain blocked. No QC / LEAN. No OANDA
> API calls. `configs/approved_strategies.yaml` stays
> `approved: []`. The four-layer MODELED refusal (loader,
> calculator, reconciliation CLI, capture script) is
> unchanged. The live-promotion blocker remains.

## 1. Headline outcome

7 new fixture files + 4 new docs + 1 new test module are
shipped:

- **6 new rate fixtures** under
  `research/financing/fixtures/`, one per non-EUR H4 pair
  (GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD).
- **1 new observed-event companion**
  (`observed_aud_usd_long_credit.json`) reconciling exactly
  against `rates_two_week_aud_usd.json`.
- **16 new tests** in
  `tests/research/test_financing_pair_fixture_expansion.py`,
  pinning 7-pair coverage, schema invariants, sign variety,
  USD-base vs USD-quote notional paths, AUD reconciliation,
  CLI subprocess run, MODELED refusal at two layers, and
  the subprocess import-isolation rail.
- **0 changes to** `src/forex_bot/`,
  `research/financing/{models,rates,calculator,reporting,fixtures}.py`,
  `research/financing/__init__.py`,
  `scripts/reconcile_financing_fixtures.py`, or
  `scripts/capture_oanda_observed_financing_pilot.py`.
- Full repo suite: **702 passes** (686 prior + 16 new).
- Ruff: clean over `src tests scripts
  research/parity_verifier research/walk_forward
  research/financing`.
- Archive validator, freeze checker, secret scan all PASS.
- Paper-loop and demo-loop still refuse; no live-loop
  command exists.

## 2. Commit log (this sprint)

| commit | phase | scope |
|---|---|---|
| `c5abca7` | 0 | plan doc |
| `b73a3d7` | 1 | conventions |
| `5dfc351` | 2 | 6 new rate fixtures |
| `6ab1903` | 3 | AUD_USD observed-event companion |
| `2baf86b` | 4 | 16 expansion tests |
| `cc9a9e7` | 5 | synthetic reconciliation runs doc |
| `b944e78` | 6 | status doc + EVIDENCE_INDEX update |
| _this_ | 7 | summary + EVIDENCE_INDEX summary-link + final validation |

## 3. Files changed

- **Docs (new):**
  - `docs/research/FINANCING_BP_DAY_FIXTURE_EXPANSION_001_PLAN.md`
  - `docs/research/FINANCING_BP_DAY_FIXTURE_EXPANSION_CONVENTIONS.md`
  - `docs/research/FINANCING_BP_DAY_FIXTURE_EXPANSION_SYNTHETIC_RUNS.md`
  - `docs/research/FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md`
  - `docs/research/RESEARCH_FINANCING_BP_DAY_FIXTURE_EXPANSION_001_SUMMARY.md`
- **Docs (edited):**
  - `docs/research/EVIDENCE_INDEX.md` — adds the bp/day
    fixture expansion subsection.
  - `research/financing/fixtures/README.md` — adds rows for
    every new fixture.
- **Fixture data (new):**
  - `research/financing/fixtures/rates_two_week_gbp_usd.json`
  - `research/financing/fixtures/rates_two_week_usd_jpy.json`
  - `research/financing/fixtures/rates_two_week_aud_usd.json`
  - `research/financing/fixtures/rates_two_week_usd_cad.json`
  - `research/financing/fixtures/rates_two_week_usd_chf.json`
  - `research/financing/fixtures/rates_two_week_nzd_usd.json`
  - `research/financing/fixtures/observed_aud_usd_long_credit.json`
- **Tests (new):**
  - `tests/research/test_financing_pair_fixture_expansion.py`

No file in `src/forex_bot/`, `research/financing/` Python
modules, `configs/`, or `backtests/` was modified. No
`*.sqlite3` created or committed. No `.env` read. **No OANDA
call.**

## 4. Validation commands run

Final pass (Phase 7), all green:

- `python -m pytest -q` — **702 passed in 2.67 s** (686
  prior + 16 new)
- `ruff check src tests scripts research/parity_verifier
  research/walk_forward research/financing` — **All checks
  passed!**
- `python scripts/validate_research_archive.py` — **ALL
  CHECKS PASSED**
- `python scripts/check_research_freeze.py` — **ALL CHECKS
  PASSED**
- `python scripts/scan_artifacts_for_secrets.py` —
  **PASSED** (1,987 files; no credentials)
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml`
  — refuses
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml`
  — refuses
- `python -m forex_bot.cli --help` — no `live-loop` command
  listed

## 5. Confirmation no strategy is approved
`configs/approved_strategies.yaml` verified `approved: []`.
Freeze checker passes.

## 6. Confirmation CAMPAIGN_002 remains REJECT
No CAMPAIGN_002 artifact, config, or report was touched.
Archive validator's `verdicts_non_approval` and
`report_verdict_tokens` checks pass.

## 7. Confirmation paper/demo/live remain blocked
- `paper-loop` refuses (`['trend_following']` not approved).
- `demo-loop` refuses (same).
- `python -m forex_bot.cli --help` does not list
  `live-loop`.

## 8. Fixture expansion summary

7 new JSON files under `research/financing/fixtures/` (each
<2 KB; aggregate ~12 KB):

| file | bytes | kind | notes |
|---|---:|---|---|
| `rates_two_week_gbp_usd.json` | 1686 | rates | USD-quote; long -14.6 / short +7.3 annual bp |
| `rates_two_week_usd_jpy.json` | 1865 | rates | USD-base + JPY precision; long +18.25 / short -36.5 |
| `rates_two_week_aud_usd.json` | 1707 | rates | USD-quote, long-AUD carry; long +10.95 / short -21.9 |
| `rates_two_week_usd_cad.json` | 1781 | rates | USD-base; long -10.95 / short +5.475; missing date is Wed |
| `rates_two_week_usd_chf.json` | 1717 | rates | USD-base; long +25.55 / short -50.4 (CHF low rates → long USD earns) |
| `rates_two_week_nzd_usd.json` | 1691 | rates | USD-quote, long-NZD carry; long +9.125 / short -18.25 |
| `observed_aud_usd_long_credit.json` | 1188 | events | non-EUR USD-quote, all-credits, Wed triple; reconciles exactly against rates_two_week_aud_usd under skip policy |

All carry `synthetic: true`, `schema_version: 1`, exactly
one `missing_dates` entry (per the conventions doc),
documented synthetic `account_id_hash` only, and
`fix-*`-prefixed broker ids only.

Sign variety across pairs is enforced by
`test_rate_sign_variety_across_pairs` — at least one
fixture with each of {long+, long-, short+, short-}.

## 9. Seven-pair coverage status

**All seven H4 universe pairs have a committed rate
fixture.** (`test_every_h4_pair_has_a_rate_fixture`
enforces this.)

| pair | rate fixture | base / quote | sample signs (long/short annual bp) |
|---|---|---|---|
| EUR_USD | `rates_two_week_eur_usd.json` (existing) | USD-quote | -18.25 / +9.125 |
| GBP_USD | `rates_two_week_gbp_usd.json` (this sprint) | USD-quote | -14.6 / +7.3 |
| USD_JPY | `rates_two_week_usd_jpy.json` (this sprint) | USD-base + JPY | +18.25 / -36.5 |
| AUD_USD | `rates_two_week_aud_usd.json` (this sprint) | USD-quote | +10.95 / -21.9 |
| USD_CAD | `rates_two_week_usd_cad.json` (this sprint) | USD-base | -10.95 / +5.475 |
| USD_CHF | `rates_two_week_usd_chf.json` (this sprint) | USD-base | +25.55 / -50.4 |
| NZD_USD | `rates_two_week_nzd_usd.json` (this sprint) | USD-quote | +9.125 / -18.25 |

## 10. Test status

**16 new tests pass** in
`tests/research/test_financing_pair_fixture_expansion.py`.
Full repo suite: **702 passes** (686 prior + 16 new). Ruff
clean.

Coverage: 7-pair coverage, every fixture loads, synthetic
+ size + required-keys invariants, ≥1 missing_dates per
fixture, no real account-shaped ids, sign-variety across
pairs, USD-base notional path (USD_JPY) with JPY-precision
entry price, USD-quote notional path (AUD_USD), AUD_USD
observed ↔ rate reconciliation at rel=1e-9, reconciliation
CLI subprocess run, loader MODELED refusal extended to
every new fixture, defense-in-depth calculator refusal of
post-construction MODELED mutation, CLI smoke against
every pair with empty observed, subprocess rail confirming
zero `forex_bot` modules pulled in.

## 11. Synthetic reconciliation run summary

Seven runs documented in
[`FINANCING_BP_DAY_FIXTURE_EXPANSION_SYNTHETIC_RUNS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_SYNTHETIC_RUNS.md):

| # | run | exit | summary |
|---:|---|---:|---|
| 1 | aud_usd × aud_long_credit / skip | 0 | 3 match, 0 mismatch |
| 2 | aud_usd × aud_long_credit / conservative | 0 | 3 match + 1 missing_in_observed (intended) |
| 3 | usd_jpy × empty | 0 | empty smoke |
| 4 | usd_cad × empty | 0 | empty smoke |
| 5 | usd_chf × empty | 0 | empty smoke |
| 6 | gbp_usd × empty | 0 | empty smoke |
| 7 | nzd_usd × empty | 0 | empty smoke |

Zero `mismatch` rows across all 7 runs. Per-run JSON /
markdown outputs live under `/tmp/financing_recon_batch/`
and are **not committed**.

## 12. Whether any broker/OANDA data was fetched

**No.** Zero OANDA calls, zero transaction-stream queries,
zero orders, zero `.env` reads. All fixtures are synthetic;
all reconciliation runs are local-file operations.

## 13. Whether MODELED financing is now available

**No.** All four pipeline layers continue to refuse
`MODELED`:

- `TableRateSource(treatment=MODELED)` raises at
  construction. The new
  `test_no_new_fixture_can_construct_modeled_rate_source`
  extends this rail to every committed rate fixture.
- `calculate_run` raises if a rate source self-reports
  `MODELED`. The new
  `test_calculator_refuses_modeled_for_new_fixture_treatments`
  confirms this even when the treatment is mutated
  post-construction (the only way to bypass the loader).
- `_build_report` in `scripts/reconcile_financing_fixtures.py`
  raises before writing if `financing_treatment == modeled`.
- The capture script never emits a rate-source treatment.

The five-criterion MODELED checklist from
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
§11 is unchanged: 0 captured rollovers, blocked
reconciliation, no `MODELED` model implementation, no
engine integration, no human approval.

## 14. Remaining limitations

- **Only AUD_USD has an end-to-end observed reconciliation
  pair** (rate fixture + matching observed-event fixture).
  USD_JPY, USD_CAD, USD_CHF, GBP_USD, NZD_USD have rate
  fixtures only; the existing USD_CAD and USD_JPY event
  fixtures are intentionally not aligned with the new rate
  fixtures (they were authored for the original calculator
  tests, not for end-to-end reconciliation). A future
  sprint could add aligned observed-event fixtures per
  pair if a specific test scenario justifies it.
- **No real data.** Every fixture is synthetic. Successful
  reconciliations show internal consistency only — not
  real broker behaviour.
- **Two-week window is fixed.** All fixtures use the same
  May 2026 two-week window for cross-pair comparability.
  Longer windows or other date ranges would require
  additional fixtures.
- **One missing-date per fixture.** Convention; trivially
  expandable.
- **`/tmp` outputs not committed.** Synthetic-run outputs
  live under `/tmp/financing_recon_batch/`; this is the
  intended behaviour but means a reviewer must re-run the
  CLI to see the full per-row report.

## 15. Recommended next branch

Three options, all freeze-compatible:

1. **`research-financing-observed-capture-pilot-funded-001`** —
   a credentialed re-run of the existing capture script
   against a long-lived practice account. The Phase 4
   doc of the prior sprint
   ([`FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md))
   records the exact command. With the 7-pair rate
   fixtures now in place, any captured pair can be
   reconciled from day one. **Practice account financing
   rates are typically 0**, so this may produce zero
   events — still a valid pilot result.

2. **`research-financing-rate-fixture-windows-expansion-001`** —
   add more time windows (e.g. a four-week window, a
   month-boundary window for end-of-month rate effects).
   Still synthetic, still ESTIMATED. Useful for testing
   the calculator against richer time patterns.

3. **`research-financing-observed-companions-fill-001`** —
   add per-pair observed-event companions for the
   remaining 5 pairs (GBP_USD, USD_JPY, USD_CAD, USD_CHF,
   NZD_USD) so every pair has an end-to-end
   reconciliation pair. Pure data sprint; no new tests
   beyond the per-pair reconciliation pattern.

A **fourth** option — implementing a market-interest-rate-
differential `MODELED` model — remains **not recommended**
until a credentialed capture pilot provides ground-truth
data to reconcile against.

## 16. Files to review first (priority order)

1. **[`docs/research/FINANCING_BP_DAY_FIXTURE_EXPANSION_001_PLAN.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_001_PLAN.md)**
   — sprint scope, safety invariants, target pair coverage.
2. **[`docs/research/FINANCING_BP_DAY_FIXTURE_EXPANSION_CONVENTIONS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_CONVENTIONS.md)**
   — per-pair sign / precision / missing-rate / triple-swap
   conventions; contributor checklist.
3. **[`docs/research/FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md)**
   — headline status (7-pair coverage, fixture files,
   tests, synthetic run table, safety state).
4. **[`docs/research/FINANCING_BP_DAY_FIXTURE_EXPANSION_SYNTHETIC_RUNS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_SYNTHETIC_RUNS.md)**
   — 7-run table with commands, exit codes, summaries.
5. **[`research/financing/fixtures/rates_two_week_aud_usd.json`](../../research/financing/fixtures/rates_two_week_aud_usd.json)**
   + **[`research/financing/fixtures/observed_aud_usd_long_credit.json`](../../research/financing/fixtures/observed_aud_usd_long_credit.json)** —
   the canonical non-EUR end-to-end reconciliation pair.
6. **[`research/financing/fixtures/rates_two_week_usd_jpy.json`](../../research/financing/fixtures/rates_two_week_usd_jpy.json)**
   — the USD-base + JPY-precision exemplar (the most
   exotic of the new fixtures).
7. **[`tests/research/test_financing_pair_fixture_expansion.py`](../../tests/research/test_financing_pair_fixture_expansion.py)**
   — 16 tests pinning every rail.

## 17. Cross-links

- Plan: [`FINANCING_BP_DAY_FIXTURE_EXPANSION_001_PLAN.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_001_PLAN.md)
- Conventions: [`FINANCING_BP_DAY_FIXTURE_EXPANSION_CONVENTIONS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_CONVENTIONS.md)
- Synthetic runs: [`FINANCING_BP_DAY_FIXTURE_EXPANSION_SYNTHETIC_RUNS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_SYNTHETIC_RUNS.md)
- Status: [`FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md)
- Sister sprint summaries:
  [`RESEARCH_FINANCING_MODEL_001_SUMMARY.md`](RESEARCH_FINANCING_MODEL_001_SUMMARY.md),
  [`RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md`](RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md),
  [`RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md`](RESEARCH_FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md),
  [`RESEARCH_FINANCING_OBSERVED_CAPTURE_PILOT_001_SUMMARY.md`](RESEARCH_FINANCING_OBSERVED_CAPTURE_PILOT_001_SUMMARY.md)
- Future-capture pilot spec:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Calculator protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Evidence index: [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
