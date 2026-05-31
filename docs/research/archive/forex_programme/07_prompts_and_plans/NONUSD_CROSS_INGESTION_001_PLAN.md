# Non-USD Cross Ingestion & Cost Models — Sprint 001 Plan

**Branch:** `research-nonusd-cross-ingestion-and-cost-models-001`
**Date:** 2026-05-29
**Type:** research **infrastructure** sprint — adds *capability* to ingest,
validate, materialize, and cost-model non-USD FX crosses. No strategy, no
campaign, no factor screen, no backtest evidence, no broker mutation, no
approval. Freeze stays intact.

## 0. Why this sprint exists

The viability review (`FOREX_CORPUS_VIABILITY_AND_MARKET_SELECTION_001`)
and the multi-market front-gate review
(`MULTI_MARKET_FRONT_GATE_AND_NONUSD_CROSSES_001`) concluded:

- The seven USD-major corpus is structurally **cost-defeated** and
  **breadth-poor** (every pair shares the USD leg → correlated signals).
- Broad undirected mining and all re-tunes are **closed**.
- The highest-information, lowest-risk, cheapest next expansion is
  **non-USD FX crosses** — they break USD-leg crowding, enable
  breadth/carry families that were data-blocked, and supply *independent
  replications* for genuine factors (e.g. C1) via fresh pre-registered
  screens (NOT re-tunes). They do **not** fix the cost wall (their
  spreads are wider) — they are a breadth/replication+capability
  expansion, framed honestly.

This sprint builds the **infrastructure** for crosses to the same
research standard as the majors. It deliberately **stops before** any
factor discovery, hypothesis, front-gate screen, campaign, or strategy.

**Success criterion:** the repo can ingest, validate, materialize, and
cost-model non-USD FX crosses using the same standards as the major-pair
universe — with the seven USD majors left *bit-for-bit unchanged* as the
control/baseline universe.

## 1. Hard rules (non-negotiable)

- Do **not** create CAMPAIGN_032 or any campaign.
- Do **not** implement any strategy or entry/exit logic.
- Do **not** run train/validation/test evidence.
- Do **not** approve any strategy; paper/demo/live stay blocked.
- Do **not** call mutation APIs; use only existing read-only research
  ingestion patterns and credentials.
- Do **not** revive rejected ideas.
- Do **not** weaken the freeze; the seven majors stay the control
  universe and their code paths/semantics stay unchanged.

## 2. Target instruments (wave 1)

| Tier | Cross | Quote | Pip | Cost band (feasibility) | Notes |
|------|-------|-------|-----|-------------------------|-------|
| primary  | EUR_GBP | GBP | 0.0001 | near-major (~1–2p) | best cost candidate |
| primary  | EUR_JPY | JPY | 0.01   | near-major (~1–2p) | JPY-funded |
| primary  | GBP_JPY | JPY | 0.01   | wide (~2.5–4p)     | volatile, breadth |
| primary  | AUD_JPY | JPY | 0.01   | moderate (~1.5–3p) | classic carry; financing first-order |
| extended | NZD_JPY | JPY | 0.01   | wide (~2.5–4p)     | carry; thinner |
| extended | EUR_CHF | CHF | 0.0001 | moderate (~1.5–3p) | **2015-01-15 SNB break** |
| extended | GBP_CHF | CHF | 0.0001 | wide (~2.5–4p)     | thin, wide |
| extended | EUR_AUD | AUD | 0.0001 | moderate (~1.5–3p) | cross-region breadth |

The 4 **primary** are required; the 4 **extended** are included in the
registry/metadata because that is low-effort and the feasibility study
already characterizes them. Extended crosses carry the same code paths;
EUR_CHF carries an explicit structural-break flag.

## 3. Design decision — additive single source of truth

There is **no** single instrument registry today; the seven majors are
duplicated across `m1_corpus_validation.MAJOR_PAIRS`, the two ingestion
scripts, `cost_atlas`, the campaign loaders, and `financing.py`. To honor
"majors unchanged" we do **not** edit `MAJOR_PAIRS`. Instead:

1. New domain module `forex_bot.domain.cross_instruments` — the single
   source of truth for cross metadata (pip conventions, settlement/quote
   currency, carry legs, cost band, structural breaks). It reuses the
   existing tested `Instrument` model for pip/precision handling.
2. `m1_corpus_validation` gains `NONUSD_CROSS_PAIRS` (from the registry)
   and `SUPPORTED_PAIRS = MAJOR_PAIRS + NONUSD_CROSS_PAIRS`. `MAJOR_PAIRS`
   is untouched; campaign loaders that import it are unaffected.
3. Ingestion/materialization gates widen from `MAJOR_PAIRS` to
   `SUPPORTED_PAIRS` (union) while preserving every safety restriction
   (practice-only, candle-endpoint-only, no mutation paths).
4. Cost models live in a new `forex_bot.research.cost_models` package —
   crosses get **instrument-specific** spread bands and a **two-legged**
   financing structure; the majors' assumptions in `financing.py` are
   **not** copied (its USD-base notional logic is wrong for crosses).

## 4. Phase plan

- **P0** baseline audit + this plan (commit).
- **P1** cross instrument registry + metadata + pip/precision + validation
  rules + tests + `NONUSD_CROSS_INSTRUMENT_SUPPORT.md` (commit).
- **P2** ingestion support (widen allow-lists, preserve safety,
  provenance, coverage checks) + tests (commit).
- **P3** materialization support (M1→M5/M15/H1/H4M1 for crosses) + tests +
  `NONUSD_CROSS_MATERIALIZATION_SUPPORT.md` (commit).
- **P4** cost-model framework (`cost_models/` package: spread bands +
  financing legs, no copied majors assumptions) + tests +
  `NONUSD_CROSS_COST_MODEL_DESIGN.md` (commit).
- **P5** `scripts/validate_nonusd_cross_data.py` + tests +
  `NONUSD_CROSS_VALIDATION_AND_DIAGNOSTICS.md` (commit).
- **P6** `NONUSD_CROSS_RESEARCH_READINESS.md` (commit).
- **P7** `NEXT_PROMPT_AFTER_NONUSD_CROSS_INGESTION.md` (commit).
- **P8** full validation + `..._001_SUMMARY.md` (commit).

## 5. Baseline audit (run at P0, clean `origin/main` tip)

- `pytest tests/ -q` → **2389 passed, 3 skipped** (3 skips are local-data
  absent, pre-existing).
- `ruff check src scripts tests` → **4 errors, all pre-existing** in
  `scripts/run_edge_discovery_vol_managed_tsmom.py` (C031, not this
  sprint). New code in this sprint must be ruff-clean.
- `python scripts/check_research_freeze.py` → **ALL CHECKS PASSED**.
- `python scripts/validate_research_archive.py` → **ALL CHECKS PASSED**
  (747 evidence links resolve).
- `python scripts/scan_artifacts_for_secrets.py` → **PASSED** (value scan
  skipped — no real OANDA creds in env; pattern scan ran clean).
- Majors load: `MAJOR_PAIRS` intact (7 pairs); approved registry empty
  (`configs/approved_strategies.yaml` → `approved: []`); loops refuse.

## 6. Data-availability note

Cross M1/H4 data is **not ingested** in this sprint (no real OANDA
credentials are present in the environment, and ingestion of new history
is out of scope here — this sprint adds the *capability*). Every piece of
validation/diagnostic tooling must therefore degrade gracefully to a
clear `NOT_INGESTED` state for crosses with no rows, never crash. Actual
fetching happens in a later, explicitly-scoped run once credentials and a
go-ahead are present.
