# Next Coding-Agent Prompt — Implement the Non-USD Cross Data Expansion

This is the **exact prompt** for the next sprint, derived from
`NEXT_DATA_EXPANSION_DECISION.md`: implement the **non-USD FX cross data
expansion** and register the crosses into the generalized multi-market
front gate, with instrument-specific cost models and data-quality
diagnostics. It is an **implementation (data + infra)** sprint. It
**stops before strategy research and before campaign creation.**

---

## PROMPT (copy below this line)

We are starting an implementation (data + infrastructure) sprint from
clean, updated `origin/main`.

**Branch:** `research-nonusd-cross-ingestion-and-cost-models-001`

**Context:**

The multi-market front-gate design sprint
(`docs/research/MULTI_MARKET_FRONT_GATE_AND_NONUSD_CROSSES_001_SUMMARY.md`)
chose **non-USD FX crosses** as the first data expansion
(`docs/research/NEXT_DATA_EXPANSION_DECISION.md`) and defined the
generalized framework (`docs/research/MULTI_MARKET_FRONT_GATE_FRAMEWORK.md`)
and acquisition roadmap (`docs/research/MULTI_MARKET_DATA_ACQUISITION_ROADMAP.md`).
This sprint ingests the crosses and makes them registerable in the front
gate — **no strategy, no screen, no campaign.**

**Goal:** deliver (a) lookahead-free, parity-checked candle data for the
first-wave non-USD crosses, (b) instrument-specific cost models
(spread/slippage/financing) for them, (c) registration of these
instruments into the multi-market research universe / front-gate
interface, and (d) data-quality + cost diagnostics. Capability and data
only.

**This is not a strategy sprint.**

**Hard rules:**

- Do **not** create a campaign (no CAMPAIGN_032 / any campaign number).
- Do **not** build a strategy or implement entry/exit logic.
- Do **not** run a front-gate *screen*, factor validation, or any
  train/validation/test evidence; do **not** backtest.
- Do **not** perform parameter tuning or revive rejected ideas.
- Do **not** approve any strategy; confirm `configs/approved_strategies.yaml`
  stays empty. Do **not** enable paper/demo/live; do not modify
  executor/broker/loop behavior.
- Use **free/local or already-available data only**. Do **not** call
  trading APIs or use credentials. If cross history cannot be obtained
  without live calls, **document the blocker and stop** — do not fetch
  under the freeze.
- Do **not** weaken the research freeze or its checks.

**PHASE 0 — plan & guardrails**
Review the design docs above, the existing OANDA ingestion + research
candle store + M1 materialization (`scripts/ingest_oanda_candles_postgres.py`,
`scripts/export_postgres_research_candles.py`,
`scripts/materialize_m1_derived_timeframes.py`,
`scripts/verify_m1_materialized_coverage.py`, loaders in
`src/forex_bot/data/`), and the edge-discovery lab
(`research/edge_discovery/`). Write
`docs/research/NONUSD_CROSS_INGESTION_001_PLAN.md` (ingestion design,
crosses, cost-model plan, freeze guardrails, EUR_CHF 2015-break
handling). Commit.

**PHASE 1 — cross ingestion (lookahead-free, parity-checked)**
Ingest first-wave crosses **EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY** (H4
bid/ask + M1-derived) using only free/local or already-available data;
dedup/contamination-check; verify M1 coverage; run the existing parity
harness. Add unit tests. If data is unavailable without live calls,
document the blocker and stop. Commit.

**PHASE 2 — instrument-specific cost models**
Add per-cross spread/slippage and financing models (do **not** reuse
EUR_USD costs); carry model appropriate to each (JPY-funding crosses,
carry crosses). Window EUR_CHF around the 2015 SNB break (defer EUR_CHF/
GBP_CHF to a second wave if the break complicates first delivery). Add
tests. Commit.

**PHASE 3 — register into the multi-market front gate**
Register the crosses in the research universe / front-gate registration
interface so they can later be run through Stages 1–3 of
`MULTI_MARKET_FRONT_GATE_FRAMEWORK.md` (adapter + cost model + calendar).
Keep the 7-major behavior unchanged (no regression). Do **not** run any
stage. Add tests. Commit.

**PHASE 4 — data-quality & cost diagnostics**
Produce coverage, spread/financing-realism, and
correlation-to-existing-majors diagnostics for the new crosses (evidence
of how much independent breadth they add). Evaluate **no** strategy.
Write `docs/research/NONUSD_CROSS_DATA_QUALITY_AND_COST_DIAGNOSTICS.md`.
Commit.

**PHASE 5 — validation & summary**
Run: `pytest tests/ -q`, `ruff check src scripts tests`,
`python scripts/check_research_freeze.py`,
`python scripts/validate_research_archive.py`,
`python scripts/scan_artifacts_for_secrets.py`, `git status --short`.
Write `docs/research/NONUSD_CROSS_INGESTION_001_SUMMARY.md` (branch,
commit hashes by phase, files changed, crosses ingested + cost models +
data-quality findings, confirmation that no campaign/strategy/approval
was created and paper/demo/live remain blocked, validation results, and
the recommended next step — propose, do not execute, the first factor to
re-screen on crosses). Commit.

**Success criteria:** clean, cost-realistic, parity-checked non-USD cross
data registered in the multi-market front gate, with honest diagnostics —
no strategy, no screen, no campaign, freeze intact. A specific factor
re-screen is *proposed* for a later, separately-gated sprint.

---

## Notes for whoever runs this

- This prompt stops at **registerable data + diagnostics**. The first
  front-gate *screen* on crosses (e.g. re-screening the C1 factor for
  independent replication) is a **later** sprint with its own
  pre-registration — do not run it here.
- Keep the freeze boundary: ingestion and cost modeling are research
  infrastructure; screening/factor-validation are gated stages that come
  after, separately.
- Honor any naming/pairing conventions enforced by
  `scripts/validate_research_archive.py`, and keep all artifacts free of
  credential-shaped strings.
