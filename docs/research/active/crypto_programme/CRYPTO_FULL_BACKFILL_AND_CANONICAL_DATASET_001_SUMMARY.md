# Crypto Full Backfill and Canonical Dataset Sprint 001 — Summary

**Sprint:** `crypto-full-backfill-and-canonical-dataset-001`
**Date:** 2026-06-01
**Branch:** `main`

---

## 26-Item Summary

### 1. Current branch

`main` (direct work, no feature branch or worktree)

### 2. Commit hashes by phase

| Phase | Commit | Message |
|-------|--------|---------|
| 0 | `2f1519e` | Phase 0 plan |
| 1 | `a14588d` | Phase 1 preflight |
| 2 | `18194bb` | Phase 2 full backfill |
| 3 | `957a0f9` | Phase 3 validation |
| 4 | `018d73f` | Phase 4 materialization + D1 fix |
| 5 | `70b5348` | Phase 5 cost model |
| 6 | `f47079e` | Phase 6 readiness |
| 7 | `1f70c16` | Phase 7 next prompt |
| 8 | *(this commit)* | Phase 8 summary |

### 3. Files changed by phase

| Phase | Key files |
|-------|-----------|
| 0 | `CRYPTO_FULL_BACKFILL_AND_CANONICAL_DATASET_001_PLAN.md` |
| 1 | `CRYPTO_FULL_BACKFILL_001_PREFLIGHT.md` |
| 2 | `CRYPTO_FULL_BACKFILL_001_RESULT.md`, 5 ingest manifests |
| 3 | `CRYPTO_CANONICAL_DATASET_VALIDATION_001.md`, `validation/canonical_m1_outlier_scan_001.json` |
| 4 | `CRYPTO_DERIVED_TIMEFRAME_MATERIALIZATION_001.md`, 2 materialization manifests, `timeframe_aggregation.py` |
| 5 | `CRYPTO_COST_MODEL_001.md` |
| 6 | `CRYPTO_FAMILY_C_PREDIAGNOSTIC_READINESS_001.md` |
| 7 | `NEXT_PROMPT_CRYPTO_FAMILY_C_TREND_PERSISTENCE_DIAGNOSTICS_001.md` |
| 8 | This summary |

### 4. Commands run

```bash
pytest tests/ -q                                    # Phase 0, 8 — 2471 passed
python scripts/check_research_freeze.py             # Phase 0, 8 — PASS
python scripts/validate_research_archive.py         # Phase 0, 8 — PASS
python scripts/scan_artifacts_for_secrets.py        # Phase 0, 8 — PASS
ruff check src tests scripts research               # Phase 0, 8 — 25 pre-existing issues

python scripts/ingest_crypto_candles_postgres.py \
  --instrument BTC_USD --granularity M1 \
  --start 2021-05-31T00:00:00Z --end 2026-05-31T23:57:53Z

python scripts/ingest_crypto_candles_postgres.py \
  --instrument ETH_USD --granularity M1 \
  --start 2021-05-31T00:00:00Z --end 2026-05-31T23:57:53Z

python scripts/validate_crypto_store.py \
  --instrument BTC_USD --start 2021-05-31T00:00:00Z --end 2026-05-31T23:57:53Z

python scripts/validate_crypto_store.py \
  --instrument ETH_USD --start 2021-05-31T00:00:00Z --end 2026-05-31T23:57:53Z

python scripts/materialize_crypto_derived_timeframes.py \
  --instrument BTC_USD --start 2021-05-31T00:00:00Z \
  --end 2026-05-31T23:57:53Z --targets M5,M15,H1,H4,D1

python scripts/materialize_crypto_derived_timeframes.py \
  --instrument ETH_USD --start 2021-05-31T00:00:00Z \
  --end 2026-05-31T23:57:53Z --targets M5,M15,H1,H4,D1
```

### 5. Validation results

| Check | Result |
|-------|--------|
| pytest | 2471 passed |
| research freeze | ALL CHECKS PASSED |
| archive validation | ALL CHECKS PASSED |
| secret scan | PASSED |
| ruff | 25 pre-existing issues (unchanged scope) |
| M1 validation BTC | WARN (gaps), coverage PASS |
| M1 validation ETH | WARN (gaps), coverage PASS |

### 6. Backfill source

Coinbase Exchange public REST (`coinbase-spot`), products `BTC-USD` and `ETH-USD`, M1 granularity.

### 7. Requested date range

`2021-05-31T00:00:00Z` → `2026-05-31T23:57:53Z` (~5 calendar years)

### 8. Actual BTC_USD M1 row count

**2,629,439**

### 9. Actual ETH_USD M1 row count

**2,629,403**

### 10. BTC_USD coverage

**99.945%** (1,439 missing bars of 2,630,878 expected)

### 11. ETH_USD coverage

**99.944%** (1,475 missing bars of 2,630,878 expected)

### 12. Gap summary

Exchange-side feed outages; largest gaps ~391 bars (May 2026), ~349 bars (Oct 2025), ~277 bars (Mar 2023). BTC and ETH share identical outage windows. No interpolation applied.

### 13. Outlier summary

Zero zero-price bars, zero return outliers (>20%), zero flash-wick outliers (>15%), zero stale flat runs (>60 bars) for both instruments.

### 14. Materialized timeframe row counts

| TF | BTC_USD | ETH_USD |
|----|---------|---------|
| M5 | 525,706 | 525,699 |
| M15 | 175,197 | 175,189 |
| H1 | 43,764 | 43,756 |
| H4 (H4M1) | 10,907 | 10,899 |
| D1 | 1,783 | 1,779 |

### 15. D1 availability

**Available** for both assets. BTC: 1,783 complete UTC days (last: 2026-05-29). ETH: 1,779 complete UTC days (last: 2026-05-29). Last 2 UTC days omitted as incomplete at cutoff.

### 16. Cost model status

**Frozen** in `CRYPTO_COST_MODEL_001.md`. BTC half-spread 5 bps, ETH 8 bps, taker round-trip 120 bps, 2× stress defined.

### 17. Family C readiness classification

**READY_WITH_WARNINGS** — all hard gates pass; exchange-side M1 gaps documented for operator review.

### 18. Factors created

**No.**

### 19. Strategies created

**No.**

### 20. Campaigns created

**No.**

### 21. Approved strategies empty

**Yes.** `configs/approved_strategies.yaml` → `approved: []`

### 22. Paper/demo/live blocked

**Yes.** Research freeze loop refusal checks pass.

### 23. Raw data committed

**No.** ~5.26M M1 rows per asset in local Postgres only.

### 24. Remaining blockers or warnings

- Operator review of exchange-side M1 gaps (recommended, not blocking)
- D1/H4 last bars truncated at backfill cutoff (expected under omit policy)
- `verify_materialized_pair()` uses forex NY alignment — not applicable to crypto UTC path

### 25. Recommended next step

Run Family C Trend Persistence exploratory diagnostics using `NEXT_PROMPT_CRYPTO_FAMILY_C_TREND_PERSISTENCE_DIAGNOSTICS_001.md`.

### 26. Files to review first

1. `CRYPTO_FAMILY_C_PREDIAGNOSTIC_READINESS_001.md`
2. `CRYPTO_CANONICAL_DATASET_VALIDATION_001.md`
3. `CRYPTO_FULL_BACKFILL_001_RESULT.md`
4. `CRYPTO_DERIVED_TIMEFRAME_MATERIALIZATION_001.md`
5. `CRYPTO_COST_MODEL_001.md`

---

## Sprint outcome

Full BTC_USD and ETH_USD Coinbase spot M1 backfill **complete**. Dataset validated, derived timeframes materialized, cost model frozen, Family C readiness classified. No factor, strategy, campaign, approval, or trading enablement created.
