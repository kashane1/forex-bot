# Infrastructure Execution-Fidelity Sprint 001 — Summary

**Date:** 2026-05-22 · **Branch:** `infra-execution-fidelity-001`
**Base commit:** `107b3d5` (HEAD of `infra-foundation-001`)

Companion to [`INFRA_EXECUTION_FIDELITY_001_PLAN.md`](INFRA_EXECUTION_FIDELITY_001_PLAN.md).
This sprint improved backtest / execution **fidelity** and
**independent-validation readiness**. It searched for no trading edge,
ran no strategy campaign, produced no verdict, and approved nothing.

## What changed

| phase | commit | change |
|---|---|---|
| 0 | `ab08be0` | Baseline verification; this sprint's plan. Modernized `FinancingTreatment` to `enum.StrEnum` (a pre-existing form the current ruff flags). |
| 1 | `990112c` | **Next-bar-open fill model.** The backtester has a configurable `fill_timing`: `signal_bar_close` (default) and `next_bar_open`. `next_bar_open` fills at bar N+1's open; a final-bar signal is an explicit `NEXT_BAR_OPEN_UNAVAILABLE` skip. `fill_timing` flows into `TradeRecord`, the trades CSV, and the metrics/summary exports. `--fill-timing` CLI flag and `backtest.fill_timing` config. |
| 2 | `60440c9` | **D1AGG + next-bar-open smoke.** `scripts/smoke_d1agg_next_open.py` — a diagnostic-only check that the D1AGG path and `next_bar_open` run together mechanically. Report at `backtests/diagnostics/d1agg_next_open_smoke.md`. |
| 3 | `5acb1e9` | **Lean parity executable prep.** `scripts/build_lean_parity_config.py` (authoritative parameter extraction) and `scripts/export_lean_parity_data.py` (real-H4 → Lean CSV export); export-format spec, parity checklist, and `LEAN_PARITY_EXECUTION_GUIDE.md`. |
| 4 | `915fbfe` | **Observed financing capture.** `ObservedFinancingEvent` schema (account id stored as a SHA-256 hash only), an OANDA `DAILY_FINANCING` parser, `ObservedFinancingEventRepo`, and migration v3. Dormant — no loop writes to it. |
| 5 | `fbec482` | **Research-freeze regression hardening.** `scripts/check_research_freeze.py` — a CI-style gate — and 12 regression tests anchoring the freeze. A "before merging research infrastructure" checklist in `docs/runbooks.md`. |
| 6 | _(this commit)_ | Final docs, full validation, handoff. README links updated. |

New / changed files by phase are listed in each commit message.

## What did NOT change

- **No strategy campaign was run** and **no strategy verdict** was
  produced. CAMPAIGN_001–009 remain REJECT; Research Marathon 001
  remains NO-GO.
- **No strategy was approved.** `configs/approved_strategies.yaml` is
  still `approved: []`.
- **No order path changed.** paper-loop, demo-loop, and the live path
  still refuse every strategy. Nothing made paper/demo/live easier to
  run — the new fill-timing model is a backtest-only feature, and the
  freeze gate only *adds* a guard.
- **No OANDA connection** was made; no credentials were used or staged.
- **No prior campaign artifact** was modified or overwritten. Prior
  campaign reports are referenced, never edited.
- **Financing is still not in engine PnL.** It remains `ESTIMATED`
  (a conservative stress overlay) / `UNMODELED` in the engine — a hard
  live-promotion blocker.
- **Default backtest behaviour is unchanged.** `signal_bar_close` is the
  default and only enters the `config_hash` when it departs from the
  default, so prior campaign configs reproduce their exact behaviour and
  hashes.

## Validation results

All run from the repo root on the final commit:

| check | result |
|---|---|
| `pytest -q` | **286 passed** (224 baseline + 62 new) |
| `ruff check src tests scripts` | **All checks passed** |
| `scripts/validate_research_archive.py` | **ALL CHECKS PASSED** |
| `scripts/check_research_freeze.py` | **ALL CHECKS PASSED** (11 checks) |
| `bot paper-loop --config configs/paper.yaml --once` | refused, **exit 2** |
| `bot demo-loop --config configs/practice.yaml --once` | refused, **exit 2** |
| `configs/approved_strategies.yaml` | `approved: []` — empty |
| credentials staged | none; `.env` / `.env.*` gitignored |

## Safety state

All sprint safety invariants hold:

1. The approved-strategy registry is empty.
2. paper-loop, demo-loop, and the live path refuse every strategy.
3. Backtesting / research commands remain available — loop-only gating.
4. No credentials staged, logged, or committed; no OANDA call made.
5. Prior campaign reports and artifacts are immutable.
6. `signal_bar_close` reproduces prior campaign behaviour and hashes.
7. `pytest` and `ruff check` are green.

## Deliverable status

- **Fill timing:** delivered. `signal_bar_close` (default) and
  `next_bar_open`, with no-lookahead and missing-bar handling tested.
- **D1AGG + next-bar-open smoke:** delivered as diagnostic-only. All
  mechanical checks PASS on the committed EUR_USD D1AGG sample; the
  six-pair run is data-availability blocked (see below).
- **Lean parity executable prep:** delivered. Config extraction runs
  now; data export runs the moment a real H4 store exists; the Lean
  backtest itself stays a documented manual step.
- **Observed financing capture:** delivered as dormant infrastructure.
  Schema, parser, repository, and migration are in place and tested on
  fixtures; nothing writes to the table.
- **Research-freeze regression:** delivered. A CI-style gate plus 12
  regression anchors.

## Remaining blockers

1. **No real OANDA H4 candle store is committed** (`data/` is
   gitignored and empty). This blocks:
   - the six-pair H4→D1AGG smoke (Phase 2 ran on the single committed
     EUR_USD D1AGG sample instead);
   - a real Lean-parity data export (Phase 3's exporter is wired and
     tested but has nothing to read).
   Not a code gap — both run once real candles are fetched.
2. **QuantConnect Lean is not installed and was not run.** Installing
   the toolchain, writing the Lean algorithm, and running the local
   backtest remain deliberate manual steps.
3. **Historical financing is still unsolved.** OANDA publishes no
   historical financing-rate series and this bot has no trade history.
   Financing stays `UNMODELED` in engine PnL — a hard live blocker.
4. **No strategy has earned PAPER-TRADE-ONLY.** The research freeze
   holds; this sprint did not change that and was not meant to.

## Recommended next human decision points

These are decisions for a human; this sprint does not pre-empt them.

1. **Fetch real OANDA practice H4 data?** A practice-account fetch
   (`bot fetch-candles`) would unblock the six-pair D1AGG smoke and a
   real Lean-parity export. It needs practice credentials and is a
   deliberate, authorized step.
2. **Run the Lean parity backtest?** With H4 data exported, a human
   could install Lean and run the CAMPAIGN_002 parity check
   (`docs/research/LEAN_PARITY_EXECUTION_GUIDE.md`). A PASS corroborates
   the bespoke engine; a FAIL localizes a bug. It approves nothing.
3. **Re-run a campaign under `next_bar_open`?** This would be **new
   research**, not infrastructure — it needs a fresh pre-committed
   campaign per `STRATEGY_APPROVAL_PROCESS.md`. Do not treat a
   `next_bar_open` re-run as a continuation of a prior campaign.
4. **Financing remains the gating problem.** No live consideration is
   possible until a real financing model exists. The observed-financing
   capture layer is the first step; a future paper/demo observation
   phase would populate it — itself a separate, human-authorized
   decision.

## Files to review first

1. [`INFRA_EXECUTION_FIDELITY_001_PLAN.md`](INFRA_EXECUTION_FIDELITY_001_PLAN.md)
   — scope, non-goals, safety invariants.
2. [`src/forex_bot/backtesting/engine.py`](../../src/forex_bot/backtesting/engine.py)
   — the fill-timing resolution (the core fidelity change).
3. [`FILL_TIMING_MODEL.md`](FILL_TIMING_MODEL.md) — why and how.
4. [`scripts/check_research_freeze.py`](../../scripts/check_research_freeze.py)
   — the freeze gate.
5. This summary.
