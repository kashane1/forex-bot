# Financing Model Research Sprint 001 — Plan

**Date:** 2026-05-23 · **Branch:** `research-financing-model-001`
**Base commit:** `e138613` (HEAD of `research-walk-forward-harness-001`)
`strategy_evidence: false`

Infrastructure sprint. Designs and implements a **research-grade
financing / carry / rollover cost model** so future forex strategy
candidates can be evaluated with more realistic costs *before* any
paper / demo promotion. Per
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§5.4, financing is required infrastructure before any strategy
candidate can be promoted to paper.

> **No strategy is approved. CAMPAIGN_002 remains REJECT.** Paper /
> demo / live remain blocked. No QuantConnect / LEAN. No OANDA API
> calls. No new strategy campaign. **This sprint cannot, and will
> not, approve a strategy.** It builds research infrastructure.

## 1. Purpose

Provide a reusable, deterministic, **research-only** financing
calculator under `research/financing/` that:

- Reasons in **daily rollover events** keyed on (date, position
  interval), rather than the existing per-trade bp/day overlay's
  single-number debit.
- Treats **long and short carry separately**, instead of always
  applying the worst of the two like the existing overlay does.
- Handles **calendar conventions** explicitly: weekends, the
  Wednesday triple-rollover convention, and missing rate days.
- Produces **per-event records** + per-position summaries + a
  position-set aggregate, all dumpable to JSON and markdown.
- Supports a **stress-only mode** for cases where actual historical
  rates are unavailable (the current reality for 2020–2026), and a
  **observed-rate mode** seam for the future when capture is in
  place (does not implement observed-rate fetching).
- Stays **completely independent** of broker / order code,
  `forex_bot`, OANDA, and QuantConnect / LEAN.

The new module is **additive**. It does **not** replace, modify, or
weaken:

- `src/forex_bot/financing.py` — the existing per-trade `bp/day`
  conservative stress overlay, its `FinancingTreatment` enum, the
  `financing_treatment_blocks_approval` gate, or
  `financing_metadata`.
- The `ObservedFinancingEvent` schema / migration / repository.
- Campaign reports' existing `financing_treatment = estimated`
  posture or the live-promotion blocker.

Existing infrastructure remains the authoritative source of truth
for live-blocker semantics. The new module is an offline research
calculator that runs against committed/local inputs.

## 2. Non-goals

- **Not a strategy.** This sprint does not write strategy code,
  run a backtest, run a campaign, or emit any trade outputs.
- **Not a CAMPAIGN_002 revival.** CAMPAIGN_002 is used in Phase 5
  as a rejected-historical-example only, for diagnostic
  retrospective framing. **Verdict does not change.**
- **Not a backtest engine rewrite.** The bespoke engine under
  `src/forex_bot/backtesting/` is not modified; the financing
  module does not touch its PnL stream.
- **Not a broker integration.** No OANDA fetch, no
  `DAILY_FINANCING` capture pipeline, no observed-event ingest
  trigger. The observed-event schema already exists and stays
  empty under the freeze.
- **Not a financing live-promotion gate change.** The existing
  `financing_treatment_blocks_approval` gate in
  `src/forex_bot/financing.py` is the authoritative live blocker;
  this sprint does not change its rules.
- **Not a paper / demo / live enabler.** Approval requires the
  full evidence package per
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §8.
- **Not a real historical financing dataset.** OANDA exposes no
  historical financing-rate time series. This sprint cannot
  retroactively create one; it only provides a *calculator* that
  can consume rates from any source once available.

## 3. Safety invariants

1. `configs/approved_strategies.yaml` stays `approved: []`.
2. CAMPAIGN_002 remains REJECT. No re-run, no parameter tweak, no
   verdict change.
3. Paper / demo loops keep refusing; no `live-loop` command exists.
4. No QC / LEAN command. Retirement stands.
5. No OANDA API call. No `.env` read. No credential value printed.
6. No `*.sqlite3`, candle CSV, or bulky output gets staged.
7. The bespoke engine under `src/forex_bot/` is **not modified**.
8. `src/forex_bot/financing.py` is **not modified**.
9. The observed-event schema / repo / migration is **not
   modified**.
10. The walk-forward harness under `research/walk_forward/` is
    **not modified** by this sprint.
11. The free / local verifier under `research/parity_verifier/` is
    **not modified** by this sprint.
12. No new external dependency is added.
13. No file under `research/financing/` may import from
    `forex_bot`. A grep-enforced test rail guards independence
    (matching the pattern used in
    `tests/research/test_walk_forward_models.py`).
14. Every artifact written by this module carries
    `strategy_evidence: false`.

## 4. Current financing assumptions (preview — fully audited in Phase 1)

The repo already documents that financing is **not solved**:

- `src/forex_bot/financing.py` implements a per-trade conservative
  stress overlay (one `bp/day` debit per pair, the worse of long
  and short). Debit is computed from `bars_held * hours_per_bar`,
  always `>= 0`, never assumes a credit.
- `FinancingTreatment` enum (`MODELED` / `ESTIMATED` /
  `UNMODELED`) ties financing posture to approval; `live` mode
  unconditionally requires `MODELED`.
- `FutureOandaObservedFinancingModel` is a `MODELED` placeholder
  whose `__init__` raises — no campaign can reach `MODELED` state.
- Campaign reports apply the overlay as a financing-stressed
  column; backtest engine PnL stays financing-`UNMODELED`.
- `ObservedFinancingEvent` schema + repo + parser ship dormant;
  the table is empty.
- `docs/financing_decision.md`, `docs/research/FINANCING_MODEL_DESIGN.md`,
  and `docs/research/OBSERVED_FINANCING_CAPTURE.md` document the
  posture in detail.

Phase 1 will audit the actual code paths (cost model, fill model,
spread / slippage model, PnL conversion, instrument metadata,
risk engine) and produce
`docs/research/FINANCING_MODEL_CURRENT_ASSUMPTIONS.md`.

## 5. Known gaps the new module addresses

| gap | existing overlay | new research module |
|---|---|---|
| Calendar awareness | none (raw `bars × hours / 24`) | explicit per-date events with weekend skip + Wednesday triple-rollover handling |
| Long vs short asymmetry | flattened to the worse side | distinct long/short rates |
| Per-day event log | none | one record per rollover date per position |
| Stress vs observed | hard-coded conservative table | pluggable `FinancingRateSource` (table, fixture, future observed) |
| Currency conversion | USD-base heuristic only | base / quote / home currency conversion stub with conservative fallback |
| Missing-rate behaviour | implicit (table default) | explicit conservative fallback with provenance |
| Diagnostic outputs | none | per-event JSON + per-position summary + markdown report |

## 6. Planned phases

| phase | output | commit |
|---|---|---|
| 0 | This plan doc + baseline validators | docs-only |
| 1 | `docs/research/FINANCING_MODEL_CURRENT_ASSUMPTIONS.md` audit | docs-only |
| 2 | `docs/research/FINANCING_MODEL_PROTOCOL.md` design | docs-only |
| 3 | `research/financing/` skeleton (models, rates, calculator, reporting) | code + initial tests |
| 4 | `tests/research/test_financing_*.py` full fixture coverage | tests |
| 5 | `docs/research/CAMPAIGN_002_FINANCING_RETROSPECTIVE.md` (metadata-only) | docs |
| 6 | `docs/research/FINANCING_MODEL_STATUS.md` + EVIDENCE_INDEX update | docs |
| 7 | `docs/research/RESEARCH_FINANCING_MODEL_001_SUMMARY.md` + final validation | docs |

Each phase ends with a commit and (where relevant) the standard
validators: `pytest -q`, `ruff check ...`, the archive validator,
the freeze checker, and the secret scanner.

## 7. Expected artifacts

Code:

- `research/financing/__init__.py` — public API
- `research/financing/models.py` — Pydantic models for inputs,
  outputs, and rate sources
- `research/financing/rates.py` — `FinancingRateSource` interface
  + a fixture-backed `TableRateSource` + a stress
  `ConservativeStressRateSource`
- `research/financing/calculator.py` — pure functions building
  daily events from a position interval and a rate source
- `research/financing/reporting.py` — `render_summary_md`,
  `dump_events_json`
- `research/financing/README.md` — usage + isolation rails

Tests:

- `tests/research/test_financing_models.py`
- `tests/research/test_financing_rates.py`
- `tests/research/test_financing_calculator.py`
- `tests/research/test_financing_reporting.py`

Docs:

- `docs/research/FINANCING_MODEL_001_PLAN.md` (this file)
- `docs/research/FINANCING_MODEL_CURRENT_ASSUMPTIONS.md`
- `docs/research/FINANCING_MODEL_PROTOCOL.md`
- `docs/research/CAMPAIGN_002_FINANCING_RETROSPECTIVE.md`
- `docs/research/FINANCING_MODEL_STATUS.md`
- `docs/research/RESEARCH_FINANCING_MODEL_001_SUMMARY.md`

Evidence index:

- `docs/research/EVIDENCE_INDEX.md` — append financing-model
  artifacts as `strategy_evidence: false`.
- `docs/research/EVIDENCE_MANIFEST.json` — touched only if the
  validator finds it appropriate; the manifest tracks **campaigns**
  today, not infrastructure sprints, so we expect this to be a
  no-op (documented in Phase 6 if so).

## 8. Validation surface

Per-phase: `python -m pytest -q`, the archive validator, the
freeze checker, the artifact secret scanner.

Final phase (Phase 7) adds:

- `ruff check src tests scripts research/parity_verifier research/walk_forward research/financing`
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml`
  (must refuse)
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml`
  (must refuse)
- `python -m forex_bot.cli --help` (must not list `live-loop`)

## 9. Explicit statement on approval and verdicts

**This sprint cannot approve a strategy.** Implementing a
financing model — even a research-grade one with calendar and
currency handling — does not by itself satisfy any of the
approval criteria in
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§7. Specifically:

- The financing module does **not** lift the live-promotion
  blocker. The existing `financing_treatment_blocks_approval`
  rule still requires `MODELED` for live, and **no model in this
  repo produces `MODELED` financing** — neither the existing
  per-trade overlay (`ESTIMATED`) nor this new research-only
  calculator (also `ESTIMATED` at best, unless fed real observed
  rates from a forward-looking capture that has not started).
- The financing module does **not** modify any campaign verdict.
  CAMPAIGN_002 remains REJECT regardless of what its financing
  retrospective in Phase 5 shows.
- The financing module does **not** modify
  `configs/approved_strategies.yaml`. The list remains `[]`.

Any future move toward `MODELED` financing requires (i) a
forward-looking capture of real `DAILY_FINANCING` transactions
from a funded or longer-lived practice account, (ii) a regression
test reconciling modeled vs observed financing within a tight
tolerance, and (iii) a documented human approval. None of these
happen in this sprint.

## 10. Cross-links

- Existing financing docs:
  - [`docs/financing_decision.md`](../financing_decision.md)
  - [`docs/research/FINANCING_MODEL_DESIGN.md`](FINANCING_MODEL_DESIGN.md)
  - [`docs/research/OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md)
- Recommended next branch motivation:
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §5.4
- Walk-forward harness (recently completed sister sprint):
  [`RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md`](RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md)
- Research freeze:
  [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- Strategy approval process:
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
