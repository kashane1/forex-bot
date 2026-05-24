# Infrastructure Exit-Fidelity Sprint 001 — Plan

**Date:** 2026-05-24 · **Branch:** `claude/keen-leakey-a15799`
**Sprint id:** `infra-exit-fidelity-001`
**Origin:** [docs/plans/2026-05-24-feat-backtest-exit-fidelity-plan.md](../plans/2026-05-24-feat-backtest-exit-fidelity-plan.md) (workflow plan, deepened by 8 review/research agents)

## Purpose

The repo is research-only and frozen ([forex-bot-research-freeze](../../README.md)). Two fidelity gaps in the backtest engine's exit logic were discovered during a walk-forward audit on 2026-05-24:

1. **Same-bar SL+TP collisions are silently resolved.** [engine.py:259-291](../../src/forex_bot/backtesting/engine.py) uses an `if/elif` chain where the adverse stop wins a same-bar tie ([CAMPAIGN_009_PRECOMMIT.md:59](CAMPAIGN_009_PRECOMMIT.md)). The tie-break is intentional, but the engine writes no record of when both exits were touchable on the same bar — a mean-reversion strategy with a midline TP could silently under-report TP wins.

2. **Stop / TP fills ignore bar-open gaps.** Stops fill at exactly `stop_price`, even when the bar OPENED past it (weekend gap, news jump). Real stop-market orders fill at the open (worse than stop). Acknowledged as a known Lean mismatch in [CAMPAIGN_002_LEAN_MAPPING_SPEC.md:131-133](CAMPAIGN_002_LEAN_MAPPING_SPEC.md) but never closed bespoke-side.

This sprint **improves backtest exit fidelity** by (a) instrumenting same-bar SL+TP collisions (always-on) and (b) adding an opt-in `gap_fill_policy` that activates four gap-fill cases. Default mode preserves byte-identical `config_hash` for every CAMPAIGN_001–009 artifact.

It **does not look for a trading edge.** It runs no strategy campaign, produces no strategy verdict, approves nothing, and does not make paper/demo/live execution any easier to start.

## Non-goals

This sprint will **not**:

- run any strategy campaign or produce any new strategy result or verdict;
- approve any strategy, or edit `configs/approved_strategies.yaml` except to verify it remains empty (`approved: []`);
- paper-trade, enable the demo-loop, submit any order, or make any of those easier to run;
- use live credentials or touch any live broker environment;
- connect to OANDA at all (no candle fetch, no account calls);
- tune any strategy parameter;
- rerun or modify prior campaigns (CAMPAIGN_001–009) or their artifacts, except to *link* to them from new documents;
- regenerate Lean parity baselines for the new opt-in `gap_through` mode (deferred to a future sprint);
- backfill the two new metric counts into existing `_index.json` files (would violate the freeze).

## Phases

| phase | deliverable | independent? |
|---|---|---|
| 0 | Baseline verification, this plan, pre-sprint hash snapshot with `_doc` guardrail | — |
| 1 | Schema additions on `TradeRecord`/`BacktestMetrics`/`BacktestResult` + same-bar ambiguous-exit detection (always-on, no hash change) | depends on 0 |
| 2 | `gap_fill_policy` plumbing (config + CLI + engine kwarg + conditional hash inclusion). Default `"none"` preserves all prior hashes. | depends on 1 |
| 3 | Gap-fill exit logic (4 cases). Pre-trailing-stop snapshot. bid/ask_open `None` fallback. 16-case parametrized matrix + 1 property test. | depends on 2 |
| 4 | Exporter propagation (CSV columns + JSON/MD/summary). `_index.json` forward+backward read tolerance tests. | depends on 1, 2, 3 |
| 5 | [GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md](GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md) — semantics + ordering caveat + parity-impact + asymmetry. | depends on 1-4 |
| 6 | Final validation: full pytest+ruff, hash regression vs Phase 0 snapshot, `_index.json` builder load check, sprint summary. | depends on 0-5 |

Each phase commits separately with `Phase N (infra-exit-fidelity-001): <summary>`. If a phase is blocked, the blocker is documented in this file's "Status" section and the next independent phase proceeds.

## Safety invariants (must hold at every commit)

1. `configs/approved_strategies.yaml` remains **empty** (`approved: []`).
2. `paper-loop`, `demo-loop`, and the live/practice path **refuse** every current strategy via the approved-strategy guard.
3. Backtesting / research commands remain **available** — the new gap-fill flag is a backtest-fidelity feature and never relaxes a loop gate.
4. No real credentials are staged, logged, or committed; `.env` and `.env.*` stay gitignored. No OANDA connection is made.
5. Prior campaign reports and run artifacts (CAMPAIGN_001–009) are **immutable** — referenced, never edited or overwritten.
6. The default `gap_fill_policy = "none"` reproduces prior campaign behaviour exactly. The pinned hash snapshot at [tests/fixtures/pre_sprint_config_hashes.json](../../tests/fixtures/pre_sprint_config_hashes.json) is the ground truth.
7. The same-bar ambiguous-exit counter is **pure observation** — never changes any `exit_price`, `pnl`, `r_multiple`, or `final_equity`.
8. `pytest` and `ruff check` stay green (modulo the pre-existing `test_real_manifest_has_all_nine_campaigns` stale fixture, unrelated to this sprint).

## Naming choices (pinned by the deepen-plan reviews)

- **Sprint id:** `infra-exit-fidelity-001` (mirrors `infra-execution-fidelity-001` precedent — every numbered sprint uses an `infra-`/`research-` prefix).
- **Opt-in value:** `gap_fill_policy="gap_through"` (not `next_open` — avoids collision with `fill_timing="next_bar_open"`).
- **Local var renames in engine code:** `did_gap_fill` (not `gap_fill` — prevents kwarg-shadowing); `tp_also_in_range` (not `ambiguous` — meaningful at call site).
- **No separate `_STATUS.md`** — running status lives in commit messages (per-phase commits) and inline in this file's "Status" section. Matches `INFRA_EXECUTION_FIDELITY_001_*` precedent which shipped PLAN + SUMMARY only.

## Status

**Phase 0 — IN PROGRESS (2026-05-24).** Baseline pytest+ruff green (701 pass + 1 pre-existing failure unrelated to sprint: `test_real_manifest_has_all_nine_campaigns` — stale 9-vs-actual-14 manifest count). Freeze verified empty. Pre-sprint hash snapshot generated at [tests/fixtures/pre_sprint_config_hashes.json](../../tests/fixtures/pre_sprint_config_hashes.json) covering campaign_001 (vanilla trend), campaign_004 (vol breakout), campaign_009 (mean reversion with TP). Regenerator at [scripts/snapshot_pre_sprint_hashes.py](../../scripts/snapshot_pre_sprint_hashes.py).

## Cross-references (read-only)

- Workflow-style plan (deepened): [docs/plans/2026-05-24-feat-backtest-exit-fidelity-plan.md](../plans/2026-05-24-feat-backtest-exit-fidelity-plan.md)
- Precedent sprint: [INFRA_EXECUTION_FIDELITY_001_PLAN.md](INFRA_EXECUTION_FIDELITY_001_PLAN.md) + [INFRA_EXECUTION_FIDELITY_001_SUMMARY.md](INFRA_EXECUTION_FIDELITY_001_SUMMARY.md)
- Precedent opt-in fidelity feature: [FILL_TIMING_MODEL.md](FILL_TIMING_MODEL.md)
- Same-bar tie-break rule: [CAMPAIGN_009_PRECOMMIT.md:59](CAMPAIGN_009_PRECOMMIT.md)
- Gap-fill mismatch acknowledged: [CAMPAIGN_002_LEAN_MAPPING_SPEC.md:131-133](CAMPAIGN_002_LEAN_MAPPING_SPEC.md)
