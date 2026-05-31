# Multi-Market Front Gate & Non-USD Crosses 001 — Summary

**Branch:** `research-multi-market-front-gate-and-nonusd-crosses-001`
**Type:** research infrastructure + preparation. **Docs-only.** No
strategy, no campaign, no backtest, no ingestion, no broker calls.
**Freeze intact.**
**Date:** 2026-05-29.

This sprint prepares the repo to explore new markets and datasets: a
designed multi-market universe, a generalized front-gate framework, a
non-USD-cross feasibility verdict, a prioritized data-acquisition
roadmap, a single chosen expansion path, and the exact next
implementation prompt — all without creating a strategy, campaign, or
trading system.

---

## 1. Branch

`research-multi-market-front-gate-and-nonusd-crosses-001` (from clean
`origin/main`).

## 2. Commit hashes by phase

| Phase | Hash | Deliverable |
|-------|------|-------------|
| 0 | `f6d7e1a` | `MULTI_MARKET_FRONT_GATE_001_PLAN.md` (baseline audit + plan) |
| 1 | `a4abb7f` | `MULTI_MARKET_RESEARCH_UNIVERSE.md` |
| 2 | `05e4289` | `MULTI_MARKET_FRONT_GATE_FRAMEWORK.md` |
| 3 | `d9971bb` | `NON_USD_CROSS_FEASIBILITY_STUDY.md` |
| 4 | `2cb13d5` | `MULTI_MARKET_DATA_ACQUISITION_ROADMAP.md` |
| 5 | `1a65180` | `NEXT_DATA_EXPANSION_DECISION.md` |
| 6 | `f3d25f2` | `NEXT_PROMPT_AFTER_MULTI_MARKET_FRONT_GATE.md` |
| 7 | _this commit_ | this summary + validation |

## 3. Files changed

Eight documents, all additions under `docs/research/` (docs-only; no
code, config, registry, or executor change; `git diff --name-only
origin/main..HEAD -- '*.py'` is empty):

1. `MULTI_MARKET_FRONT_GATE_001_PLAN.md`
2. `MULTI_MARKET_RESEARCH_UNIVERSE.md`
3. `MULTI_MARKET_FRONT_GATE_FRAMEWORK.md`
4. `NON_USD_CROSS_FEASIBILITY_STUDY.md`
5. `MULTI_MARKET_DATA_ACQUISITION_ROADMAP.md`
6. `NEXT_DATA_EXPANSION_DECISION.md`
7. `NEXT_PROMPT_AFTER_MULTI_MARKET_FRONT_GATE.md`
8. `MULTI_MARKET_FRONT_GATE_AND_NONUSD_CROSSES_001_SUMMARY.md` (this)

## 4. Market universe recommendation

Adopt the full multi-market universe as the gate's **target scope** but
**stage ingestion**:
- **Tier 0 (have):** 7 USD majors → control/baseline & null reference.
- **Tier 1 (first expansion):** non-USD crosses — EUR_GBP, EUR_JPY,
  GBP_JPY, AUD_JPY (first wave), then NZD_JPY, EUR_AUD, EUR_CHF, GBP_CHF.
- **Tier 2 (later):** crypto → metals/index → futures → equities/ETFs.

## 5. Non-USD cross findings

Crosses are **worth adding, with scoped expectations.** They are the
cheapest, lowest-risk new data (same OANDA model/pipeline) and they
**fix what crosses can fix** — USD-leg crowding and breadth-poverty
(enabling cross-sectional/carry/relative-value families and independent
replications for factors like C1). They **do not** relieve the two-sided
cost squeeze (crosses are *wider* than EUR_USD), do not extend history
(~6.4y), and do not unlock microstructure. Caveats: carry crosses
(AUD_JPY, NZD_JPY) need an instrument-specific financing model; EUR_CHF
has the 2015 SNB structural break; JPY/CHF "breadth" partially collapses
in risk-off. Framed as a **breadth/replication + capability** expansion,
not a cost fix.

## 6. Multi-market framework summary

One gate, one evidence bar, instrument-specific cost models. Each
instrument registers an **adapter + cost model + calendar**; the shared
pipeline (the import-isolated lab at `research/edge_discovery/` —
`matched_nulls.py`, `filter_ablation.py`, `multiple_comparison.py`,
`cost_feasibility.py`) runs five staged gates:
1. **Discovery** (cheap, no pre-reg) — documented lookahead-free dataset
   + candidate effects with mechanisms.
2. **Factor validation** — beats matched-null, survives filter-ablation
   + multiple-comparison correction → `GENUINE_FACTOR`.
3. **Front-gate screen** (pre-registered, frozen thresholds) —
   cost-feasibility net of instrument-specific costs + stability +
   generalization → `PASS`/`FAIL`. (The decisive gate the whole seven
   -major programme failed on cost.)
4. **Campaign** (pre-commit, train→validation, sealed test lockbox) —
   *not run this sprint*.
5. **Promotion** (human approval, MODELED financing, registry entry) —
   *not done this sprint*.

Stages 1–3 are research under the freeze; Stage 4 needs a pre-commit;
Stage 5 needs human approval.

## 7. Recommended expansion path

**Add non-USD FX crosses** (first wave EUR_GBP, EUR_JPY, GBP_JPY,
AUD_JPY) — chosen over crypto/futures/alternate-feed because it is the
cheapest, reuses all infra, directly attacks crowding/breadth, and
exercises the generalized gate end-to-end on familiar ground before the
heavier crypto/futures infra is built.

## 8. Was any campaign created?

**No.** No CAMPAIGN_032, no campaign of any number.

## 9. Was any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`
(empty; `forex_bot.approval` fails closed).

## 10. Do paper/demo/live remain blocked?

**Yes.** The freeze gate confirms both loops refuse
(`paper-loop refuses ['trend_following'] — frozen`, `demo-loop refuses
['trend_following'] — frozen`). No executor/broker/loop change.

## 11. Validation commands run

| Command | Result |
|---------|--------|
| `pytest tests/ -q` | **2389 passed, 3 skipped** (skips = absent local data) — exit 0 |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** — exit 0 |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** — exit 0 (23 campaigns; 747 evidence-index links resolve) |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** — exit 0 |
| `ruff check src scripts tests` | **exit 1** — see note below |
| `git status --short` | clean after the Phase 7 commit (docs-only) |

**Ruff note (honest, carried from the prior sprint):** `ruff check`
reports the same 4 **pre-existing** errors in
`scripts/run_edge_discovery_vol_managed_tsmom.py` (a CAMPAIGN_031 script
on `origin/main`). This docs-only sprint added **zero** Python
(`git diff --name-only origin/main..HEAD -- '*.py'` is empty), so the
ruff failure is a pre-existing repo condition, not a regression. It is
auto-fixable (`ruff check --fix`) and is already flagged for a separate
cleanup task; fixing it is out of scope for this docs-only sprint.

## 12. Recommended next sprint

Implement the chosen expansion: **non-USD cross ingestion + cost
models**, per `NEXT_PROMPT_AFTER_MULTI_MARKET_FRONT_GATE.md` (branch
`research-nonusd-cross-ingestion-and-cost-models-001`). It ingests
first-wave crosses, adds instrument-specific cost models, registers them
into the multi-market front gate, and produces data-quality diagnostics —
**stopping before any front-gate screen, factor validation, or
campaign.**

## 13. Files to review first

1. `NEXT_DATA_EXPANSION_DECISION.md` — the chosen path.
2. `MULTI_MARKET_FRONT_GATE_FRAMEWORK.md` — the generalized gate.
3. `NON_USD_CROSS_FEASIBILITY_STUDY.md` — why crosses, with caveats.
4. `MULTI_MARKET_RESEARCH_UNIVERSE.md` — the universe + per-instrument
   profiles.
5. `MULTI_MARKET_DATA_ACQUISITION_ROADMAP.md` — prioritized acquisition.
6. `NEXT_PROMPT_AFTER_MULTI_MARKET_FRONT_GATE.md` — the next sprint.

---

## Bottom line

The repo is now **prepared to explore new markets**: a staged universe,
a single generalized front gate that holds every asset class to the same
evidence bar, a clear-eyed non-USD-cross verdict (worth adding for
breadth/replication, not for cost), a prioritized acquisition roadmap, a
single chosen next step (**non-USD crosses**), and the exact
implementation prompt for it. **No strategy, no campaign, no trading
system; freeze intact; nothing approved; paper/demo/live blocked.**
