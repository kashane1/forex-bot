# Next Prompt — Crypto Family C Trend Persistence Diagnostics 001

**Sprint:** Follow-on from `crypto-full-backfill-and-canonical-dataset-001`
**Date:** 2026-06-01
**Type:** Diagnostics prompt only — **NOT** a strategy or campaign prompt
**Prerequisite:** `CRYPTO_FAMILY_C_PREDIAGNOSTIC_READINESS_001.md` classified **READY_WITH_WARNINGS**

---

## Agent instructions

You are authorized to run **exploratory trend-persistence diagnostics only** for the crypto programme Family C lane.

Work directly on `main` unless instructed otherwise. This is a diagnostics sprint — not a strategy sprint.

---

## Scope

### Instruments (only)

- `BTC_USD`
- `ETH_USD`

### Dataset

- Canonical Coinbase spot M1 base with materialized derived timeframes
- Source: `coinbase-spot` (ingest) / `m1_materialized` (derived)
- Storage: local Postgres (`FOREX_BOT_RESEARCH_DATABASE_URL`)
- Window: full 5y backfill `2021-05-31T00:00:00Z` → `2026-05-31T23:57:53Z`

### Timeframes to analyze

- M15
- H1
- H4 (stored as `H4M1`)
- D1

### Cost reporting (mandatory)

Use frozen assumptions from `CRYPTO_COST_MODEL_001.md`. Report all four variants:

1. **Gross** (mid-price)
2. **Spread-only net** (`2 × half_spread_bps`)
3. **All-in net** (spread + slippage + taker fee)
4. **2× stress** (double all cost components)

BTC half-spread: 5 bps. ETH half-spread: 8 bps. Taker round-trip: 120 bps.

---

## Required analyses

1. **Trend persistence** — autocorrelation / momentum decay / run-length statistics at M15/H1/H4/D1
2. **Null baselines** — shuffled returns, random sign flips, or block-bootstrap nulls
3. **BTC/ETH split** — per-asset and pooled comparison
4. **Horizon sensitivity** — compare persistence across M15 → D1 ladder
5. **Regime sensitivity** — high-vol vs low-vol subsamples (e.g. rolling ATR percentile splits)
6. **Turnover/cost sensitivity** — show gross vs spread-only vs all-in vs 2× at each horizon

---

## Hard rules (do not violate)

| Prohibited | Reason |
|------------|--------|
| Create strategy entries/exits | Diagnostics only |
| Create campaigns | No front-gate runs |
| Approve any strategy | `approved_strategies.yaml` must stay empty |
| Enable paper/demo/live | Trading loops frozen |
| Call broker/trading APIs | Research data only |
| Create factors (production) | Exploratory diagnostics only |
| Tune cost model to results | Pre-registered in `CRYPTO_COST_MODEL_001.md` |
| Interpolate M1 gaps | Use data as-is; document gap impact |

---

## Data references

| Document | Content |
|----------|---------|
| `CRYPTO_FULL_BACKFILL_001_RESULT.md` | Row counts, coverage |
| `CRYPTO_CANONICAL_DATASET_VALIDATION_001.md` | Gap report |
| `CRYPTO_DERIVED_TIMEFRAME_MATERIALIZATION_001.md` | Derived TF row counts |
| `CRYPTO_COST_MODEL_001.md` | Frozen cost assumptions |
| `CRYPTO_DATA_VALIDATION_REQUIREMENTS.md` | Full validation spec |

---

## Deliverables (diagnostics sprint)

1. Diagnostic report(s) under `docs/research/active/crypto_programme/` or `research/crypto/diagnostics/`
2. Compact JSON artifacts (no raw candle commits)
3. Explicit verdict: does trend persistence survive costs at any horizon?
4. Explicit statement: no strategy created, no approval granted

---

## Success criteria

- Exploratory persistence analysis complete for BTC and ETH
- All four cost variants reported
- Null baselines included
- No strategy/campaign/approval artifacts created
- Research freeze gate still passes
