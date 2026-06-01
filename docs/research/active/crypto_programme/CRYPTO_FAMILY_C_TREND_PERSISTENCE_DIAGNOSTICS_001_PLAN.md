# Crypto Family C Trend Persistence Diagnostics 001 — Plan

**Sprint:** `crypto-family-c-trend-persistence-diagnostics-001`
**Date:** 2026-06-01
**Branch:** `main` (no feature branch)
**Type:** Exploratory diagnostics only

---

## 1. Purpose

Answer whether BTC/ETH Coinbase spot trend persistence is materially stronger than failed FX programme patterns, and whether any persistence survives frozen cost assumptions at any horizon (M15, H1, H4, D1).

This sprint does **not** create strategies, campaigns, factors in production, or trading enablement.

---

## 2. Non-goals

| Excluded | Reason |
|----------|--------|
| Strategy entries/exits | Diagnostics only |
| Strategy files | Hard rule |
| Campaigns / front-gate | Not authorized |
| Strategy approval | `approved_strategies.yaml` stays empty |
| Paper/demo/live | Remain blocked |
| Broker/trading APIs | No execution |
| Market-data ingestion APIs | Use stored Postgres only |
| Cost model tuning | Frozen in `CRYPTO_COST_MODEL_001.md` |
| M1 gap interpolation | Use bars as-is |

---

## 3. Source prompt

`docs/research/active/crypto_programme/NEXT_PROMPT_CRYPTO_FAMILY_C_TREND_PERSISTENCE_DIAGNOSTICS_001.md`

---

## 4. Readiness gate

**Classification:** `READY_WITH_WARNINGS` (`CRYPTO_FAMILY_C_PREDIAGNOSTIC_READINESS_001.md`)

| Evidence | Value |
|----------|-------|
| BTC M1 rows | 2,629,439 |
| ETH M1 rows | 2,629,403 |
| BTC M1 coverage | 99.945% |
| ETH M1 coverage | 99.944% |
| D1 derived | BTC 1,783 / ETH 1,779 |
| M15 derived | ~175k rows/asset (~5y) |
| Cost model | Frozen `CRYPTO_COST_MODEL_001.md` |
| OHLC failures | 0 |
| Outliers quarantined | 0 |
| Factor diagnostic prior | None |
| Strategy / campaign | None |

---

## 5. Accepted warnings (operator)

- Exchange-side M1 gaps (~1,439 BTC / ~1,475 ETH) accepted as **non-actionable** for exploratory diagnostics.
- **No interpolation** of gaps.
- D1 last complete day 2026-05-29 UTC at backfill cutoff.
- Diagnostics use **available bars only**; gap impact documented in synthesis.

---

## 6. Data window and instruments

| Field | Value |
|-------|-------|
| Venue | Coinbase spot |
| Storage | Local Postgres (`FOREX_BOT_RESEARCH_DATABASE_URL`) |
| Source (derived) | `m1_materialized` |
| Instruments | `BTC_USD`, `ETH_USD` only |
| Window | `2021-05-31T00:00:00Z` → `2026-05-31T23:57:53Z` |
| Timeframes | M15, H1, H4 (`H4M1` storage), D1 |

---

## 7. Cost assumptions (frozen, four variants)

| Variant | Definition |
|---------|------------|
| Gross | Mid-price returns |
| Spread-only | `2 × half_spread_bps` round-trip |
| All-in | spread + slippage + taker fee (120 bps RT) |
| 2× stress | Double spread/slippage; 200 bps fee RT |

| Instrument | Half-spread (bps) |
|------------|-------------------|
| BTC_USD | 5 |
| ETH_USD | 8 |

Slippage per leg: M15/H1 = 2 bps; H4/D1 = 0. See `CRYPTO_COST_MODEL_001.md`.

---

## 8. Planned diagnostics

1. **Trend persistence** — AC1/2/4/8, momentum decay quintiles, run-length, continuation after 1–4 bars, horizon-to-horizon (H4/D1 → lower TF), effect sizes.
2. **Null baselines** — shuffled returns, random sign flips, block bootstrap (fixed seed, recorded trials).
3. **BTC/ETH split** — per asset, pooled, driver attribution.
4. **Horizon ladder** — M15 → D1 comparison.
5. **Regime** — rolling ATR percentile terciles (33/34/33), pre-declared, no post-hoc tuning.
6. **Cost/turnover** — gross vs spread vs all-in vs 2×; break-even bps vs observed edge; turnover warnings.
7. **Gap impact** — summary from validation docs; confirm no interpolation.

---

## 9. Null baseline plan

- **Seed:** 42
- **Trials:** 500 per null type (reduce for slow series if needed)
- **Shuffle:** IID permute log returns
- **Sign flip:** random ±1 on returns
- **Block bootstrap:** block size scaled by timeframe (e.g. 24 bars M15, 5 D1)
- Report percentile vs null and two-sided p-value style metric without overclaiming significance

---

## 10. Safety rules

- Preserve research freeze and archive gates after every phase.
- No raw candles, DB dumps, secrets, or `.env` in commits.
- All markdown outputs state **diagnostics only**.
- Ruff: document pre-existing issues (29 errors, mostly F401/E402 in tests); do not block sprint on unrelated fixes.

---

## 11. Expected outputs

| Phase | Deliverable |
|-------|-------------|
| 0 | This plan |
| 1 | `research/crypto/diagnostics/trend_persistence.py`, loader, tests, run script |
| 2 | `CRYPTO_FAMILY_C_BASELINE_TREND_PERSISTENCE_RESULT.md` + JSON |
| 3 | `CRYPTO_FAMILY_C_NULL_BASELINE_RESULT.md` |
| 4 | `CRYPTO_FAMILY_C_REGIME_SENSITIVITY_RESULT.md` |
| 5 | `CRYPTO_FAMILY_C_COST_TURNOVER_SENSITIVITY_RESULT.md` |
| 6 | `CRYPTO_FAMILY_C_TREND_PERSISTENCE_DIAGNOSTICS_001_SYNTHESIS.md` |
| 7 | Next prompt per classification |
| 8 | Programme README / roadmap updates |
| 9 | `CRYPTO_FAMILY_C_TREND_PERSISTENCE_DIAGNOSTICS_001_SUMMARY.md` |

Artifact directory: `research/crypto/diagnostics/family_c_trend_persistence_001/`

---

## 12. Phase 0 baseline checks (2026-06-01)

| Check | Result |
|-------|--------|
| Branch `main` | PASS |
| Working tree clean | PASS |
| Readiness `READY_WITH_WARNINGS` | PASS |
| `approved_strategies.yaml` empty | PASS |
| `pytest tests/ -q` | 2475 passed |
| `check_research_freeze.py` | PASS |
| `validate_research_archive.py` | PASS |
| `scan_artifacts_for_secrets.py` | PASS |
| `ruff check src tests scripts research` | 29 pre-existing issues (documented) |
