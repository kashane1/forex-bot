# Next Coding-Agent Prompt — After the Forex Corpus Viability Review

This is the **exact prompt** for the next sprint, derived from the Phase
6 decision (`NEXT_MARKET_SELECTION_DECISION.md`): build a **multi-market
front-gate discovery lab**, seeded with **non-USD FX crosses** as its
first ingested dataset. It is an **infrastructure + data** sprint. It
does **not** create a strategy campaign, run any strategy screen,
approve anything, or trade — consistent with the viability review and
the freeze.

---

## PROMPT (copy below this line)

We are starting an infrastructure + data sprint from clean, updated
`origin/main`.

**Branch:** `research-multi-market-front-gate-and-nonusd-crosses-001`

**Context:**

The forex corpus viability review
(`docs/research/FOREX_CORPUS_VIABILITY_AND_MARKET_SELECTION_001_SUMMARY.md`)
concluded that the seven-major OANDA FX corpus is structurally
cost-defeated and breadth-poor, that broad strategy search on it is
exhausted, and that the next-highest-leverage move is to make *new*
search spaces cheap and methodologically uniform to evaluate. The
recommended direction (`docs/research/NEXT_MARKET_SELECTION_DECISION.md`)
is to generalize the existing edge-discovery lab into a multi-market
front gate and seed it with non-USD FX crosses.

**Goal:** deliver (a) an instrument/asset-class-agnostic multi-market
front-gate capability that reuses the existing null / ablation /
multiple-comparison / cost-feasibility checks, and (b) clean,
parity-checked non-USD FX cross data with instrument-specific cost
models and data-quality diagnostics. Evidence and capability only.

**This is not a strategy sprint.**

**Hard rules:**

- Do **not** create a campaign (no CAMPAIGN_032 or any campaign number).
- Do **not** implement, scaffold, or backtest a strategy.
- Do **not** run a front-gate *screen* of any specific strategy/thesis,
  and do **not** run train/validation/test evidence.
- Do **not** approve any strategy; do not edit approved strategies
  except to confirm the registry remains empty.
- Do **not** enable paper/demo/live; do not modify executor/broker/loop
  behavior.
- Do **not** call OANDA APIs or use credentials; use only free/local or
  already-committed data sources. If data must be fetched, stop and
  document the blocker instead.
- Do **not** make trading recommendations.
- Do **not** weaken the research freeze or its checks.

**PHASE 0 — plan & guardrails**
Review `FOREX_CORPUS_VIABILITY_AND_MARKET_SELECTION_001_SUMMARY.md`,
`NEXT_MARKET_SELECTION_DECISION.md`,
`ALTERNATIVE_MARKET_AND_DATA_SOURCE_COMPARISON.md`, the edge-discovery
lab under `research/edge_discovery/`, and the existing OANDA candle
ingestion/loader code. Write
`docs/research/MULTI_MARKET_FRONT_GATE_001_PLAN.md` describing the
generalization design, the crosses to ingest, the instrument-specific
cost-model plan, and the freeze guardrails. Commit.

**PHASE 1 — multi-market front-gate interface**
Generalize the edge-discovery lab so an instrument (any asset class) can
be registered with: a candle source, an instrument-specific cost model
(spread/slippage/financing), and the existing matched-null /
filter-ablation / multiple-comparison / cost-feasibility checks. Keep
the current 7-major behavior as a special case (no regression). Add
unit tests. Commit.

**PHASE 2 — non-USD cross ingestion adapter**
Add a lookahead-free, parity-checked ingestion path for non-USD FX
crosses (e.g., EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY) on the existing
pipeline, with **instrument-specific** spreads/financing (do not reuse
EUR_USD costs). Use only free/local or already-available data; if none
is available, document the blocker and stop. Add tests. Commit.

**PHASE 3 — data-quality & cost diagnostics**
Produce coverage, spread/financing-realism, and
correlation-to-existing-majors diagnostics for the new crosses. Evidence
only — evaluate **no** strategy. Write
`docs/research/NONUSD_CROSS_DATA_QUALITY_AND_COST_DIAGNOSTICS.md`.
Commit.

**PHASE 4 — validation & summary**
Run: `pytest tests/ -q`, `ruff check src scripts tests`,
`python scripts/check_research_freeze.py`,
`python scripts/validate_research_archive.py`,
`python scripts/scan_artifacts_for_secrets.py`, `git status --short`.
Write `docs/research/MULTI_MARKET_FRONT_GATE_001_SUMMARY.md` with: branch,
commit hashes by phase, files changed, what the multi-market gate can
now do, the crosses ingested + their cost models + data-quality
findings, confirmation that no campaign/strategy/approval was created
and that paper/demo/live remain blocked, the validation command results,
and the recommended next step (which thesis/market to screen first —
proposed, not executed). Commit.

**Success criteria:** a reusable multi-market front-gate capability plus
clean, cost-realistic non-USD cross data and honest diagnostics — with
no strategy, no campaign, no trading, and the freeze fully intact. A
specific thesis screen, if any, is proposed for a *later* separately
-gated sprint, not run here.

---

## Notes for whoever runs this

- This prompt deliberately stops *before* screening any thesis. The
  viability review does **not** justify a campaign; it justifies making
  future screens cheap and uniform. Keep that boundary.
- If non-USD cross history is not freely/locally available without
  broker calls, the correct outcome is to **document the data blocker**
  (per the infra-sprint working style) and deliver the generalized gate
  with the majors only — not to fetch data under the freeze.
- Honor the PLAN/SUMMARY pairing convention enforced by
  `validate_research_archive.py` (every `*_NNN_PLAN.md` needs a matching
  `*_NNN_SUMMARY.md`).
