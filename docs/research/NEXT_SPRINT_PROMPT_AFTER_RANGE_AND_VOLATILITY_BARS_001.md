# Next-Sprint Prompt — after `infra-range-and-volatility-bars-001`

This drafts the prompt for the **next** Claude instance. It is **not executed**
by the current sprint. The non-time-bar infrastructure (range + volatility bar
builders, diagnostics, specs) is built, tested, and validated; full-corpus
diagnostics identified sane default thresholds.

## State handed over

- `src/forex_bot/data/non_time_bars.py`: deterministic, lookahead-free range +
  volatility bar builders (`build_*` and memory-bounded `stream_*`), pip-correct
  (JPY 0.01 / else 0.0001), bid/ask/mid basis, full provenance, `atr_scaled`
  volatility mode (prior-window-only).
- Specs: `RANGE_BAR_CONSTRUCTION_SPEC.md`, `VOLATILITY_BAR_CONSTRUCTION_SPEC.md`.
- Diagnostics: `scripts/generate_non_time_bar_diagnostics.py` (compact JSON only;
  full bars gitignored). Smoke + full-corpus results documented.
- Tests: `tests/unit/test_non_time_bars.py`, `tests/unit/test_non_time_bar_diagnostics.py`.
- Recommended defaults (from full-corpus diagnostics): **range 10 pip** primary,
  15 pip secondary; **volatility true_range 20 pip** primary, abs_close 20 pip
  companion; per-pair or `atr_scaled` thresholds to equalise cross-pair cadence.
- `configs/approved_strategies.yaml` = `approved: []`; paper/demo/live blocked;
  QuantConnect/LEAN retired.

## Recommended next sprint — pick ONE

The recommended successor is **Option 1** (a single-pair, single-series scaffold
keeps scope tight and lets bar-based signals be evaluated before broadening).

---

### Option 1 (recommended): scaffold a single-pair USD_JPY range-bar campaign

> We are starting a research sprint to scaffold (NOT approve, NOT run-to-edge) a
> single-pair USD_JPY range-bar campaign on top of the non-time-bar
> infrastructure from `infra-range-and-volatility-bars-001`.
>
> Branch: `research-usdjpy-range-bar-campaign-scaffold-001`
>
> Context: `src/forex_bot/data/non_time_bars.py` builds deterministic,
> lookahead-free range bars from local M1. Full-corpus diagnostics recommend a
> **10-pip** primary range threshold for USD_JPY (~73k bars over ~5y, ~M15–H1
> cadence). Approved strategies remain empty; paper/demo/live blocked; this is a
> scaffold sprint only.
>
> Goal: produce a scaffold (config, thesis pre-registration, train/validation
> split plan, null/cost gates wired to the existing edge-discovery front gate)
> for a USD_JPY 10-pip range-bar strategy idea **with higher-timeframe (H4/D1AGG)
> context**, plus a fresh-precommit registration. Do NOT run the campaign to a
> verdict, do NOT tune parameters, do NOT approve anything.
>
> Hard rules: reuse the existing builders (no re-implementation); run the
> edge-discovery front gate BEFORE any scaffold earns a campaign number; full
> generated bars stay gitignored; no OANDA/paper/demo/live; commit per phase;
> obey the research freeze and `check_research_freeze.py` /
> `validate_research_archive.py` / `scan_artifacts_for_secrets.py`.
>
> Phase 0: baseline audit + plan. Phase 1: thesis pre-registration + front-gate
> screen (does a range-bar HTF-context idea even earn a scaffold?). Phase 2:
> scaffold config + split plan IF the gate passes. Phase 3: validation + summary
> + honest decision (likely SELECTION_NOISE / DOES_NOT_EARN_A_SCAFFOLD unless the
> front gate clears, mirroring C026/C028).

### Option 2: non-time-bar research preflight / comparison lane

> Build an import-isolated preflight lane that compares range vs volatility vs
> time bars (M15/H1) on identical windows for cost feasibility, autocorrelation,
> and matched-null behaviour — BEFORE any strategy is written — extending the
> existing `research/edge_discovery/` front gate to accept non-time-bar inputs.
> Branch `research-non-time-bar-preflight-comparison-lane-001`. Infra/diagnostics
> only; no strategy, no approval.

### Option 3: materialize chosen non-time bars into Postgres

> Implement the `market_data.non_time_bars` table from
> `NON_TIME_BAR_STORAGE_AND_MATERIALIZATION_DESIGN.md` and materialize ONLY the
> diagnostic-recommended series (e.g. USD_JPY range 10-pip, mid) with full
> provenance + verification (re-fold cross-check), committing compact manifests
> only. Branch `infra-materialize-non-time-bars-001`. Do this only if a campaign
> actually needs indexed reads; otherwise prefer Option 1/2 first.

## Do NOT (carry-over guardrails)

- Do not approve any strategy or add a name to `approved_strategies.yaml`.
- Do not run paper/demo/live; do not modify executor/broker; do not call OANDA.
- Do not tune parameters to manufacture an edge; honour the front gate.
- Do not commit credentials, DB dumps, or bulky generated bars.
