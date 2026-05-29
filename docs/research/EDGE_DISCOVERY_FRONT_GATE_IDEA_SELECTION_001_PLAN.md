# EDGE_DISCOVERY_FRONT_GATE_IDEA_SELECTION_001_PLAN

**Status:** process / diagnostic / idea-selection sprint plan. Infrastructure
and screening only. Approves nothing, opens no test lockbox, creates no
campaign. Produces at most a ranked idea-selection memo and — only if an idea
earns it — a *draft* precommit prompt for one future candidate.

**Branch:** `research-edge-discovery-front-gate-idea-selection-001`
(started from `origin/main` @ `5063011`, the merged
`research-edge-discovery-null-benchmark-lab-001` tip).

> Companion docs (the merged lab this sprint consumes):
> [`EDGE_DISCOVERY_PROTOCOL.md`](EDGE_DISCOVERY_PROTOCOL.md),
> [`PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md`](PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md),
> [`FUTURE_CAMPAIGN_REENTRY_GATES.md`](FUTURE_CAMPAIGN_REENTRY_GATES.md),
> [`FUTURE_STRATEGY_SEARCH_WORKFLOW.md`](FUTURE_STRATEGY_SEARCH_WORKFLOW.md),
> [`EDGE_DISCOVERY_NULL_BENCHMARK_LAB_001_SUMMARY.md`](EDGE_DISCOVERY_NULL_BENCHMARK_LAB_001_SUMMARY.md).

---

## Purpose

Use the merged edge-discovery / null-benchmark lab (`research/edge_discovery/`)
as a **front gate** to evaluate several candidate strategy-idea families
*cheaply* — cost feasibility, forward-return information, matched-null
benchmark, filter ablation, multiple-comparison sanity — **before** any future
campaign is scaffolded.

Primary research question: *which, if any, future strategy idea deserves a full
campaign after passing the edge-discovery front gate?*

The expensive, repeatedly-confirmed lesson (C025 → C026) is that a full
campaign is the wrong place to first learn an idea is cost-bound or null. This
sprint moves that learning to the front, at level-2 (signal diagnostic) cost.

## Relationship to the merged edge-discovery lab

This sprint *consumes* the lab; it does not extend the package's analysis core.
It adds a new study sub-area `research/edge_discovery/front_gate_idea_selection/`
for this sprint's artifacts and uses the existing modules/CLIs:

- `cost_feasibility.py` / `costs.py` / `scripts/build_cost_atlas.py` — opportunity map
- `windows.py` (`compute_forward_returns`) — signal probes
- `matched_nulls.py` / `scripts/run_edge_discovery_matched_null.py` — matched-null screening
- `filter_ablation.py` / `scripts/run_edge_discovery_filter_ablation.py` — filter contribution
- `multiple_comparison.py` / `scripts/run_edge_discovery_matrix_sanity.py` — selection-noise sanity
- `null.py`, `report.py`, `loaders.py`, `real_data.py` — supporting primitives

## Why this is idea screening, not CAMPAIGN_027

This sprint operates only at **level 2** of the protocol's object hierarchy
(signal diagnostic — "candidate hypothesis with cheap supporting evidence,
never a verdict"). It cannot and will not:

- create CAMPAIGN_027 or any campaign scaffold;
- approve a strategy or touch `configs/approved_strategies.yaml`;
- run train/validation/test, open the test lockbox, or claim a verdict;
- enable paper/demo/live or modify executor/broker/OANDA behavior.

The deliverable is a **ranked idea-selection memo**. A future campaign is a
separate, explicitly-instructed step that begins only if an idea is rated
`CAMPAIGN_ELIGIBLE` and a human asks for it.

## Candidate idea families

1. Asia range breakout
2. Asia range fade
3. London open expansion
4. New York open continuation / reversal
5. USD_JPY single-pair opportunity probe (cheapest/least-bad historically — but no edge assumed)
6. z-score mean reversion with regime/context filters
7. Failed-breakout fade
8. Volatility compression → expansion
9. High-volatility exhaustion → reversal
10. Event-window anomaly (existing committed fixtures only)
11. Carry / financing-aware swing diagnostic
12. Pair / timeframe / session opportunity-map mining (let market facts suggest ideas)

## Available data (Phase 0 audit, local-only)

Canonical store: `data/campaign_002.sqlite3` (worktree-aware resolution; the
H4 SQLite store every CAMPAIGN_002+ config references).

| Granularity | Pairs | Span | Bars/pair | Status |
|---|---|---|---|---|
| **H4** | 7 majors | 2020-01-01 → 2026-05-24 | ~19,880 | native (canonical) |
| **H1** | 7 majors | 2020-01 → 2026-05 | ~39,700 | native |
| **D** | 7 majors | 2020 → 2026 | ~1,656 | native |
| M3 / M5 / M15 / M30 | — | — | — | **NOT present; no M1 to materialize from** |

Seven majors: EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD.

Other local artifacts:
- Event fixture: `research/calendar/fixtures/campaign_014_events.json` (committed).
- Slow-macro caches: `data/external_features/.fred_cache/` (DTWEXBGS, DGS2, DGS10,
  SP500, NASDAQCOM, DCOILWTICO, VIXCLS). No event calendar table, no
  financing/carry rate table materialized.
- Financing stress proxy: `forex_bot.financing` (used by `costs.financing_stress_fraction`).
- C011 null baseline: `research/null_baselines/campaign_011_deduped_null_baseline.json`.

**Critical data-coverage consequence for this sprint:** the sub-H1 timeframe
families implied by the candidate list (and by the rejected C025/C026 lower-TF
Donchian work) are **COMPATIBILITY_BLOCKED** for screening here — there is no
M1/M5/M15/M30 data locally. Screening is confined to **H1 and H4** on the seven
majors (with D for context). This is consistent with the C025/C026 finding that
lower timeframes are cost-hostile anyway, and it focuses the front gate on
H1/H4 session/range/mean-reversion/volatility-regime ideas.

## Diagnostics to run (by phase)

- **Phase 1** — idea inventory & feasibility (no computation; structured table).
- **Phase 2** — opportunity-map refresh: spread/ATR, ATR-in-pips, round-trip
  cost, cost-in-R, session/weekday/volatility behavior across the 7 majors ×
  {H1, H4} × sessions. Cost-feasibility flags.
- **Phase 3** — cheap forward-return signal probes for 4–6 prototypes chosen
  from Phases 1–2 (forward returns by horizon vs random-timestamp comparison).
- **Phase 4** — matched-null + matrix-sanity screening for any probe with
  preliminary information.
- **Phase 5** — filter ablation for the single strongest surviving prototype, if any.
- **Phase 6** — idea ranking + campaign-eligibility decision.
- **Phase 7** — draft next-campaign prompt *iff* one idea is `CAMPAIGN_ELIGIBLE`;
  else a "no campaign eligible" memo.
- **Phase 8** — future artifact-contract + compatibility-checklist updates.
- **Phase 9** — status/index/manifest/backlog updates (as diagnostic evidence).
- **Phase 10** — validation + 27-item summary.

## Non-goals

Not a campaign. Not CAMPAIGN_027. Not paper/demo/live enablement. Not strategy
approval. Not a test-lockbox open. Not a tune/revival of C025/C026 or the
lower-timeframe Donchian+HTF family. Not a broker-data fetch (local data only).

## Safety invariants (held for the whole sprint)

- Do not approve any strategy; do not edit `configs/approved_strategies.yaml`
  (stays `approved: []`).
- Do not enable paper/demo/live; do not modify executor/broker/OANDA files.
- Do not call OANDA order/trade/position/transaction/live endpoints; no live creds.
- Do not fetch new broker data; local existing data only.
- Do not commit `.env`, credentials, DB dumps, raw candle data, or bulky artifacts.
- Do not open the test lockbox; do not create CAMPAIGN_027; do not revive/tune
  rejected campaigns.
- C011 stays the null benchmark (not a candidate); C025 and C026 stay rejected.

## Artifacts

- `research/edge_discovery/front_gate_idea_selection/` — opportunity maps,
  signal-probe summaries, matched-null/matrix-sanity/ablation JSON+CSV
  (compact; no raw candles, no DB dumps).
- `docs/research/EDGE_DISCOVERY_IDEA_INVENTORY.md`
- `docs/research/EDGE_DISCOVERY_OPPORTUNITY_MAP_REFRESH.md`
- `docs/research/EDGE_DISCOVERY_SIGNAL_PROBE_RESULTS.md`
- `docs/research/EDGE_DISCOVERY_MATCHED_NULL_SCREENING_RESULTS.md`
- `docs/research/EDGE_DISCOVERY_FILTER_ABLATION_RESULTS.md`
- `docs/research/EDGE_DISCOVERY_IDEA_RANKING_AND_DECISION.md`
- `docs/research/NEXT_CAMPAIGN_PROMPT_FROM_EDGE_DISCOVERY_FRONT_GATE.md` **or**
  `docs/research/NO_CAMPAIGN_ELIGIBLE_AFTER_FRONT_GATE.md`
- `docs/research/FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md` (update),
  `docs/research/EDGE_DISCOVERY_COMPATIBILITY_CHECKLIST.md`
- `docs/research/EDGE_DISCOVERY_FRONT_GATE_IDEA_SELECTION_001_SUMMARY.md`

## Validation commands

```
PYTHONPATH=$PWD/src python -m pytest tests/ -q
ruff check src tests scripts research
PYTHONPATH=$PWD/src python scripts/check_research_freeze.py
PYTHONPATH=$PWD/src python scripts/validate_research_archive.py
PYTHONPATH=$PWD/src python scripts/scan_artifacts_for_secrets.py
```

(Worktree note: the lab resolves the H4 store from the primary checkout's
`data/`; CLIs that read it may need `--db-path` / `EDGE_DISCOVERY_H4_DB`.
Editable install points at the primary checkout, so lab runs use
`PYTHONPATH=$PWD/src`.)

## Phase 0 baseline (recorded)

- Branch created from `origin/main` @ `5063011`; diff vs `main` empty at start.
- Lab present: all modules, 5 CLIs, and the 5 named process docs exist.
- Evidence present: C011 deduped null baseline JSON; C025 & C026 rejection docs;
  C025/C026 retrospectives under `research/edge_discovery/retrospectives/`.
- `configs/approved_strategies.yaml` = `approved: []`.
- `pytest`: **2157 passed, 3 skipped** (skips are local-data-absent only).
- `ruff check src tests scripts research`: **All checks passed**.
- `check_research_freeze.py`: **ALL CHECKS PASSED** (loops refuse; no creds).
- `validate_research_archive.py`: **ALL CHECKS PASSED**.
- `scan_artifacts_for_secrets.py`: **PASSED** (pattern scan; no real creds in env).

## Blocked conditions (this sprint stops and documents rather than proceeds)

- Any idea requiring sub-H1 data → `COMPATIBILITY_BLOCKED` (no local M1/M5/M15/M30).
- Carry/financing swing → diagnostic only; if no usable financing/carry rate
  table beyond the conservative `forex_bot.financing` proxy, mark data-blocked.
- Event-window → existing committed fixtures only; no new fetch.
- If no idea satisfies every campaign-eligibility criterion, the sprint states
  plainly that **no CAMPAIGN_027 should be created yet** and drafts no prompt.
