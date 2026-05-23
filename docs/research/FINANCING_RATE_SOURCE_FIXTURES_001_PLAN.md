# Financing Rate-Source Fixtures Sprint 001 — Plan

**Date:** 2026-05-23 · **Branch:** `research-financing-rate-source-fixtures-001`
**Base commit:** `1ad87c6` (HEAD of `research-financing-model-001`)
`strategy_evidence: false`

Infrastructure sprint. Defines and tests the **fixture format,
adapter contract, and reconciliation expectations** needed
*before* any future observed-financing capture pilot. Sister
sprint to `research-financing-model-001`: that sprint built the
calculator; this one prepares the data pipeline so a future
capture sprint has somewhere to land its observed events without
having to design a schema under pressure.

> **No strategy is approved. CAMPAIGN_002 remains REJECT.** Paper
> / demo / live remain blocked. No QuantConnect / LEAN. **No
> OANDA API calls.** No new strategy campaign. **This sprint
> cannot, and will not, approve a strategy or lift the live
> blocker.** It builds research infrastructure on top of
> committed local data only.

## 1. Purpose

Three things:

1. **Define a stable on-disk fixture format** for observed
   financing events and per-(date, instrument) financing rates.
   The format must align with the existing
   `ObservedFinancingEvent` schema in
   [`src/forex_bot/domain/transactions.py`](../../src/forex_bot/domain/transactions.py)
   so a future capture pilot can normalize into the same shape
   without an additional translation layer.
2. **Ship a small set of committed fixture files** that exercise
   every protocol-relevant case (long/short, JPY precision,
   USD-base, same-day no-rollover, multi-day, Wednesday triple
   swap, missing-rate fallback, weekend skip). Synthetic only —
   no real account ids, no real transaction ids, no broker
   exports.
3. **Implement a tiny loader / adapter module** under
   `research/financing/fixtures.py` that turns those files into
   `FinancingRateSource` and reconcilable event lists, with
   deterministic sorting and strict error messages. The loader
   is import-isolated from `forex_bot`; the same grep-enforced
   rail as the calculator.

The point is to *prepare for* real observed financing — not to
fetch it. When a future authorized pilot starts capturing
`DAILY_FINANCING` transactions, the schema, fixtures, and
loader already exist; the pilot's only job is to populate the
database and dump events through the same shape.

## 2. Non-goals

- **Not a broker integration.** Zero OANDA calls, zero
  `DAILY_FINANCING` fetches, zero transaction-stream queries.
  The `ObservedFinancingEventRepo` write path stays untouched.
- **Not a strategy.** No backtest, no campaign, no signal logic.
- **Not a calculator change.** The existing
  `research/financing/calculator.py` semantics are frozen — the
  loader emits inputs the calculator already accepts.
- **Not a `FinancingTreatment` change.** `MODELED` remains
  refused everywhere in `research/financing/`. The existing
  `financing_treatment_blocks_approval` rule in
  `src/forex_bot/financing.py` remains authoritative.
- **Not a CAMPAIGN_002 revival.** No CAMPAIGN_002 artifact is
  loaded, parsed, or replayed.
- **Not an engine-PnL change.** Bespoke engine PnL is unchanged.
- **Not a paper / demo / live enabler.** Refusals stand.
- **Not a real historical rate dataset.** Fixtures are
  hand-built illustrative examples; they are explicitly *not*
  authoritative historical data.
- **Not an `ObservedFinancingEvent` schema rewrite.** Fixtures
  align with the existing shape; the on-disk format may carry a
  small superset of fields (e.g. an explicit
  `rate_long_annual_bp` for rate-source fixtures), but every
  observed-event fixture row must round-trip to a valid
  `ObservedFinancingEvent` via the loader.

## 3. Safety invariants

1. `configs/approved_strategies.yaml` stays `approved: []`.
2. CAMPAIGN_002 remains REJECT. No verdict edit, no re-run.
3. Paper / demo loops keep refusing; no `live-loop` exists.
4. No QC / LEAN command. Retirement stands.
5. **No OANDA API call.** No transaction-stream query. No
   pricing or candle fetch.
6. No `.env` read. No credential value printed.
7. No `*.sqlite3`, candle CSV, or bulky output gets staged.
8. The bespoke engine under `src/forex_bot/` is **not modified**.
9. `src/forex_bot/financing.py` is **not modified**.
10. `src/forex_bot/domain/transactions.py`,
    `src/forex_bot/broker/mapping.py`, and the observed-event
    repo / migration are **not modified**. (The fixture loader
    in `research/financing/` may not import from `forex_bot` at
    all, so this is enforced structurally.)
11. The walk-forward harness under `research/walk_forward/` is
    **not modified**.
12. The free / local verifier under `research/parity_verifier/`
    is **not modified**.
13. No new external dependency is added.
14. No file under `research/financing/` may import from
    `forex_bot`. The grep-enforced rail in
    `tests/research/test_financing_models.py` continues to
    cover the whole package (so it covers the new loader too).
15. Every artifact written by the loader carries
    `strategy_evidence: false`.
16. Every committed fixture file carries explicit
    `synthetic: true` provenance, no real account ids, no real
    transaction ids, no token-shaped strings, and is small
    (< 10 KB per file).
17. The `event_key` derivation in
    `ObservedFinancingEvent` (sha1 of
    `tx_id|instrument|trade_id`) is preserved verbatim — a
    fixture row's `event_key`, when round-tripped, must match
    the canonical implementation.

## 4. Current financing model status (from the sister sprint)

- `research/financing/` calculator is implemented and tested
  (594-pass repo suite; 71 new financing tests).
- Two rate sources: `TableRateSource` (per-date map) and
  `ConservativeStressRateSource` (debit-only pessimistic
  bp/day). Both `ESTIMATED`. `MODELED` refused.
- `ObservedFinancingEventRepo` table exists and ships **empty**;
  no event has ever been captured.
- `financing_treatment_blocks_approval` in
  `src/forex_bot/financing.py` remains the authoritative gate;
  `live` unconditionally requires `MODELED`.

This sprint adds **inputs** to the calculator (fixtures + a
loader). It does **not** change anything else.

## 5. Why this sprint precedes observed capture

A capture pilot fetches real transactions and needs to persist
them. Three concerns are usually mixed in that work:

1. **What does the on-disk format look like?**
2. **How does the loader validate it?**
3. **How do we tell whether the captured data reconciles?**

If those are answered for the first time inside a capture sprint,
the sprint has to design schema, write tests, *and* talk to the
broker simultaneously. That mixes safety surfaces: the schema
work touches no credentials, the broker work does. Doing them
together makes it harder to keep the broker work narrow.

Designing the schema and loader against synthetic fixtures
*first*, with the broker not in the picture at all, lets the
capture sprint focus purely on the read-only OANDA fetch +
write path. The fixtures double as test data for that pipeline
once it exists.

The future capture sprint's spec is also drafted here (Phase 5)
— as a forward-looking document only, with no implementation.

## 6. Planned phases

| phase | output | commit |
|---|---|---|
| 0 | This plan doc + baseline validators | docs-only |
| 1 | `docs/research/FINANCING_OBSERVED_FIXTURE_SCHEMA.md` | docs-only |
| 2 | `research/financing/fixtures/` tiny fixture files + docs | data + docs |
| 3 | `research/financing/fixtures.py` loader/adapter | code |
| 4 | `tests/research/test_financing_fixtures.py` (incl. reconciliation) | tests |
| 5 | `docs/research/FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md` | docs-only |
| 6 | `docs/research/FINANCING_RATE_SOURCE_FIXTURES_STATUS.md` + `EVIDENCE_INDEX.md` update | docs |
| 7 | `docs/research/RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md` + final validation | docs |

Each phase ends with a commit and (where relevant) the standard
validators: `pytest -q`, `ruff check ...`, archive validator,
freeze checker, secret scanner.

## 7. Expected artifacts

Code:

- `research/financing/fixtures.py` — loader/adapter:
  - `load_observed_event_fixture(path) -> list[ObservedEventRow]`
  - `load_rate_fixture(path) -> TableRateSource`
  - `to_observed_financing_events(rows, source) -> list[ObservedEventDict]`
    (a serializable dict whose shape matches the existing
    `ObservedFinancingEvent` field set; the loader does not
    import the canonical model — import isolation rail — but
    every field name, type, and validation rule mirrors it)
  - Strict validation: missing required fields, naive
    timestamps, non-canonical `account_id_hash` (must be a
    64-char hex digest), bad instrument shape, all raise
    `FixtureValidationError`.
  - Deterministic sorting: events sorted by
    `(time, instrument or "", trade_id or "")`.

Fixture data (small, committed):

- `research/financing/fixtures/observed_eur_usd_long_debit.json`
- `research/financing/fixtures/observed_eur_usd_short_credit.json`
- `research/financing/fixtures/observed_usd_jpy_precision.json`
- `research/financing/fixtures/observed_usd_cad_short_debit.json`
- `research/financing/fixtures/observed_same_day_no_rollover.json`
- `research/financing/fixtures/observed_multi_day_with_triple.json`
- `research/financing/fixtures/observed_missing_rate_fallback.json`
- `research/financing/fixtures/observed_weekend_skip.json`
- `research/financing/fixtures/rates_two_week_eur_usd.json`
- `research/financing/fixtures/README.md`

Each JSON file is < 10 KB, carries `"synthetic": true` and a
deterministic, fake `account_id_hash` (a SHA-256 of a literal
fixture string), and a `provenance` block explaining what the
fixture demonstrates.

Tests:

- `tests/research/test_financing_fixtures.py`
- existing tests in `tests/research/test_financing_*.py` are
  not modified.

Docs:

- This plan
- `FINANCING_OBSERVED_FIXTURE_SCHEMA.md`
- `FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`
- `FINANCING_RATE_SOURCE_FIXTURES_STATUS.md`
- `RESEARCH_FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md`
- update to `EVIDENCE_INDEX.md` (and the manifest only if the
  validator's logic genuinely calls for it; expected no-op,
  same as the sister sprint)

## 8. Validation surface

Per-phase: `python -m pytest -q`, archive validator, freeze
checker, artifact secret scanner.

Final phase (Phase 7) adds:

- `ruff check src tests scripts research/parity_verifier research/walk_forward research/financing`
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml`
  (must refuse)
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml`
  (must refuse)
- `python -m forex_bot.cli --help` (must not list `live-loop`)

## 9. Explicit statement on approval, MODELED, and verdicts

**This sprint cannot approve a strategy.** Implementing a
fixture format and loader — even one perfectly aligned with the
existing observed-event schema — does not satisfy any of the
approval criteria in
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§7. Specifically:

- **`MODELED` financing remains unavailable.** No fixture in this
  sprint is reconciled against a real captured event. A
  `TableRateSource` built from a fixture continues to declare
  `ESTIMATED` (and the loader will refuse to construct one with
  `MODELED`).
- **The live blocker remains.** `financing_treatment_blocks_approval`
  in `src/forex_bot/financing.py` is unchanged. `live`
  unconditionally requires `MODELED` and no rate source in
  `research/financing/` produces `MODELED`.
- **CAMPAIGN_002 verdict is not modified.** No CAMPAIGN_002
  artifact is loaded.
- **`configs/approved_strategies.yaml` is not modified.**

For a campaign to ever reach `MODELED` financing in the
future, the sequence is (Phase 5 of this sprint spells it out):
authorize a read-only capture pilot → forward-capture
`DAILY_FINANCING` transactions for ≥ 60 rollovers across the
universe → reconcile observed against fixture-derived predicted
financing within a tight tolerance → implement a `MODELED`
`FinancingModel` in `src/forex_bot/financing.py` → wire it into
engine PnL → document a human approval. None of those happen
in this sprint.

## 10. Cross-links

- Sister sprint summary:
  [`RESEARCH_FINANCING_MODEL_001_SUMMARY.md`](RESEARCH_FINANCING_MODEL_001_SUMMARY.md)
- Calculator protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Calculator status:
  [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- Current assumptions audit:
  [`FINANCING_MODEL_CURRENT_ASSUMPTIONS.md`](FINANCING_MODEL_CURRENT_ASSUMPTIONS.md)
- Existing observed-event capture design (dormant):
  [`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md)
- Existing per-trade overlay:
  [`FINANCING_MODEL_DESIGN.md`](FINANCING_MODEL_DESIGN.md)
- Research-freeze decision memo:
  [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- Strategy approval process:
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
