# Non-USD Cross Factor-Discovery PLANNING 001 — Plan & Baseline Audit

**Branch:** `research-nonusd-cross-factor-discovery-planning-001`
**Type:** factor-discovery **PLANNING and research design only**. Docs-only.
**Date:** 2026-05-30.
**Freeze status:** intact. No strategy, no campaign, no front-gate screen,
no factor, no train/validation/test evidence, no broker/credential use.

> **What this sprint IS:** a roadmap. It maps the expanded FX search space,
> enumerates the factor families the cross data newly enables, rejects the
> ones that would repeat known failures, ranks and shortlists the survivors,
> and names exactly one next discovery direction plus the literal prompt that
> would open it.
>
> **What this sprint is NOT:** it does not discover a factor, write a signal,
> run a screen, build entry/exit logic, create CAMPAIGN_032 (or any campaign),
> approve a strategy, or unblock paper/demo/live. Those are out of scope by
> hard rule.

---

## PHASE 0 — Baseline audit

Before designing the next generation of factor discovery, this phase records
exactly where the programme stands, so every later phase reasons from the same
evidence rather than from assumption. Eight bodies of prior work were reviewed.

### 0.1 Corpus viability review (`FOREX_CORPUS_VIABILITY_AND_MARKET_SELECTION_001`)

Project-level verdict: the seven-USD-major OANDA corpus is
**`CONTINUE_ONLY_WITH_NEW_EXTERNAL_THESIS`** — broad undirected mining and all
re-tunes are closed. Root cause = a **two-sided cost squeeze**: fast strategies
die on the **spread wall** (gross edges 1–3 pips vs same-order round-trip cost);
slow strategies die on the **financing wall** (C031 financing ≈4× spread cost).
Compounding limiters: slippage is worst where signals are strongest (wide-spread
high-vol bars), the 7 USD-legged majors are crowded and collectively a
structural USD bet, ~6.4y underpowers slow signals, and there is no true
tick/L2. The recommended next direction was a **multi-market front-gate lab
seeded with non-USD crosses** (infra + data, no campaign) — which is the lineage
this sprint sits inside.

### 0.2 Multi-market review (`MULTI_MARKET_FRONT_GATE_AND_NONUSD_CROSSES_001`)

Docs-only design sprint that generalized `research/edge_discovery/` into a
**five-stage framework** (Discovery → FactorValidation → FrontGateScreen →
Campaign → Promotion), with the governing principle: *any action a market can
take to earn a campaign, every other market must take too — one gate, one
evidence bar, instrument-specific cost models, no shortcuts.* It rendered the
non-USD-cross verdict **WORTH ADDING for breadth/replication, NOT for cost**,
and chose: **add non-USD crosses first.** Stages 1–3 run under the freeze;
Stage 4 needs a pre-commit; Stage 5 needs human approval. This sprint plans
work that lives entirely in **Stages 1–2** (and the *design* of Stage 3 gates),
nothing further.

### 0.3 Non-USD cross support sprint (`NONUSD_CROSS_INGESTION_AND_COST_MODELS_001`)

Capability sprint: additive cross registry (`domain/cross_instruments.py`, 4
primary + 4 extended wave-1), ingestion/materialization gates widened to
`SUPPORTED_PAIRS` (majors untouched as control), a new
`forex_bot.research.cost_models` package implementing **two-legged carry** (no
copied USD assumptions), and `validate_nonusd_cross_data.py`. Capability only —
**no data ingested** at that point, nothing approved, freeze intact.

### 0.4 Non-USD cross data population sprint (`NONUSD_CROSS_DATA_POPULATION_001`)

The **first real data population** (credentials present). All **8 first-wave
crosses** (4 required + 4 optional) ingested over the majors' window
(2021-05-26 → 2026-05-26):

- **14,720,522 M1 rows** — clean: 0 duplicate timestamps, 0 bid>ask, 0
  non-positive spreads, 100% `data_hash`, single `fetch_batch_id` per cross.
- **4,050,884 materialized bars** (M5/M15/H1/H4M1) — parity **PASS 8/8**.
- Cost baseline (`NONUSD_CROSS_COST_BASELINE.md`): crosses are **wider and
  fatter-tailed** than the comparable majors — cross median **1.4–3.1p** vs
  major **1.3–1.9p**; cross p99 **8.4–19.9p** vs major **4.9–11.8p**; cross
  spread-std **1.3–3.2p** vs major **0.65–1.5p**. **EUR_GBP (1.4p)** is the only
  near-major-cost cross; **GBP_JPY/EUR_AUD/GBP_CHF/NZD_JPY** carry a clearly
  higher cost wall.
- Decision: **`DATA_READY_FOR_DISCOVERY_PLANNING`** — technically justified to
  *plan*, not to *run*. No edge/screen/campaign/strategy created.

### 0.5 H16 / H03 results (non-time-bar front-gate screens)

- **H16 (overshoot-exhaustion fade)** → **`FAIL_FRONT_GATE`**: no bucket
  gradient, reversion ≈0.50 (coin-flip), every extreme mean within ~1 SEM of 0,
  cost-defeated (large overshoots have *wider* spreads), null-indistinguishable.
- **H03 (thin-move fade)** → **`FAIL_FRONT_GATE`**: weak correctly-signed tilt
  but rev ≈0.50, non-monotone, GBP-absent, cost-defeated 2/3 pairs,
  null-internal, and confounded by H16 overshoot.
- Both were the cheapest, most distinct, financing-free microstructure ideas on
  the shortlist; both failed cleanly on the same cost/no-effect wall.

### 0.6 C1 factor results (`C1_CROSS_PAIR_STUDY` + `project_c1_factor_validation`)

C1 (fade H4+H1+M15 bullish alignment → reverts down 30–60min) is the **one
genuine factor** the whole programme produced. On the 7 USD majors it is
**sign-universal** (C1_long 60-min signed return negative on 7/7),
**magnitude-concentrated** (significant only on EUR_USD + USD_JPY — the
discovery pairs — marginal GBP_USD, within-null on the other four), its
pair-space sign does **not** track the USD leg (evidence *against* a pure USD
artifact), and it is **cost-defeated everywhere** (reversion ≈0.65–0.73× spread
even on the strongest pair). It then **FAILED its own front-gate screen**: the
high-vol-conditioned path beats a vol-matched null (genuine, C1-specific) but is
**net-of-cost negative on all three pairs** → the M1/HTF time-bar confluence
directional lane is **CLOSED on this corpus**; reopen only with new data/thesis
via a **fresh** screen (never a re-tune).

### 0.7 Non-time-bar retirement (`NON_TIME_BAR_LANE_FINAL_DECISION`)

Pre-registered stop-criterion met (H16 + H03 both failed) →
**`RETIRE_DIRECTIONAL_NON_TIME_BAR_SEARCH` on the current corpus.** Alt bars are
a *sampling* fix, not an edge source; no public OOS non-time-bar edge exists in
spot FX; FX "volume" is a tick-count proxy. Infrastructure is **kept**; only the
*search* is closed. Explicit reopen conditions named **non-USD crosses** (so a
signal is not a structural USD bet on 7 collinear pairs) — a condition this
sprint's data population has now partially satisfied, but **only via a fresh
pre-registered screen, never a re-tune of H16/H03.**

### 0.8 Approved-strategy registry (`configs/approved_strategies.yaml`)

`approved: []` — **empty.** Every order-capable / signal-emitting loop refuses
to start; `forex_bot.approval` fails closed. No strategy has earned even
PAPER-TRADE-ONLY status. This sprint does not touch it.

---

## What changed since the corpus verdict

The corpus verdict (`CONTINUE_ONLY_WITH_NEW_EXTERNAL_THESIS`) listed **non-USD
crosses** among the conditions that could reopen broad search. Two of the named
reopen levers are now materially different from when that verdict was written:

| Reopen lever | Status at corpus verdict | Status now |
|---|---|---|
| Non-USD crosses (breadth) | Not ingested | **8 crosses populated, validated, materialized, cost-profiled** |
| Independent (non-collinear) legs for cross-sectional / RV / carry | Absent | **Present** — JPY/CHF/AUD/EUR/GBP/NZD legs now expressible without USD |
| Genuine carry legs (AUD_JPY, NZD_JPY, EUR_JPY) | Data-blocked | **Available** (financing still un-measured — see open question) |
| ~10–15y history | ~5–6.4y | **Unchanged** (~5y) — crosses add breadth, **not** history |
| True tick / L2 | Absent | **Unchanged** — still tick-count proxy |
| Lower-cost venue | Same OANDA spreads | **Unchanged** — crosses are *wider*, not cheaper |

**Net:** exactly **one** of the four "new data" reopen levers (breadth) has been
pulled; history, microstructure, and cost are unchanged. This is the single most
important framing for the whole sprint: **crosses reopen the breadth-and-
replication question, and nothing else.** Every candidate family this roadmap
proposes must be a family that *breadth* unlocks — not one that needs history,
microstructure, or cheaper cost, because those walls still stand.

---

## Hard boundaries for this sprint (restated)

- **No CAMPAIGN_032 / no campaign of any number.**
- No trading logic, no entry/exit rules, no signal construction.
- No factor discovery; no front-gate screen executed; no train/validation/test.
- No strategy approved; paper/demo/live stay blocked.
- No credentials, no broker/trading-API calls.
- **No rejected idea revived** — the one sanctioned reuse is a *fresh,
  independent, pre-registered* C1 replication on cross data (planned, not run).

## Deliverables (one document per phase)

| Phase | Document | Purpose |
|---|---|---|
| 0 | `NONUSD_CROSS_FACTOR_DISCOVERY_PLANNING_001_PLAN.md` (this) | baseline audit + plan |
| 1 | `EXPANDED_FX_SEARCH_SPACE_MAP.md` | map the 15-instrument universe by research category |
| 2 | `NEW_FACTOR_FAMILIES_ENABLED_BY_CROSSES.md` | ≥20 candidate families crosses newly enable |
| 3 | `DO_NOT_REPEAT_LIST.md` | families likely to repeat prior failures; hidden re-tunes; traps |
| 4 | `CROSS_UNIVERSE_FACTOR_RANKING.md` | score every family across 8 axes |
| 5 | `CROSS_UNIVERSE_FACTOR_SHORTLIST.md` | ≤5 families with thesis / novelty / failure modes |
| 6 | `NEXT_FACTOR_DISCOVERY_DIRECTION.md` | choose exactly one direction |
| 7 | `NEXT_PROMPT_AFTER_CROSS_FACTOR_DISCOVERY_PLANNING.md` | the literal next coding-agent prompt |
| 8 | `NONUSD_CROSS_FACTOR_DISCOVERY_PLANNING_001_SUMMARY.md` | validation + final summary |

## Method principles carried into the design

1. **Open from measured cost, not assumption.** Every family is judged against
   the real `NONUSD_CROSS_COST_BASELINE` (wider + fatter-tailed than majors),
   not a hoped-for cheaper venue.
2. **Breadth is the only new lever.** Prefer families that *need* multiple
   independent legs (cross-sectional, RV, basket, triangular, leadership) and
   that majors structurally could not express.
3. **Replication over re-tuning.** The single sanctioned reuse (C1) is framed as
   independent replication on non-collinear data to settle the residual-USD
   question — not as a search for a friendlier parameterization.
4. **Cost-realism gate up front.** Every family must clear net-of-cost via
   `forex_bot.research.cost_models` (round-trip measured spread + two-legged
   carry, `debit_r`) *before* it could earn a single screen — the bar the majors
   faced, here higher.
5. **Stop criteria pre-stated.** The roadmap must say what result closes the
   cross lane, so eventual discovery work cannot drift into open-ended mining.
