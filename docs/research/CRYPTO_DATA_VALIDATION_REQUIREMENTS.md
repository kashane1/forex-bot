# Crypto Data — Validation and Cost Requirements (Phase 3)

**Sprint:** `crypto-data-design-001` · Phase 3
**Date:** 2026-05-31
**Type:** Requirements only. No validation code or data in this sprint.

---

## 1. Cost model assumptions

Crypto has **no overnight financing leg** like FX retail rollover. Cost stack for research:

### 1.1 Spread (primary binding constraint for fast signals)

Public candle APIs provide **mid OHLC only**. Apply half-spread at entry and exit:

| Venue (canonical) | Assumed half-spread (bps) | 2× stress (bps) | Notes |
|-------------------|---------------------------|-----------------|-------|
| Coinbase BTC-USD | 5 | 10 | Conservative vs typical tight spot |
| Coinbase ETH-USD | 8 | 16 | ETH slightly wider |
| Binance USDT pairs | 3 | 6 | Often tighter; USDT basis separate |

**Implementation:** `half_spread_bps_assumed` stored in provenance; cost engine reads from sidecar or instrument table.

**Optional calibration:** periodic `bookTicker` sample → update assumed bps; document in manifest if changed.

### 1.2 Trading fees (taker/maker)

Research diagnostics assume **taker round-trip** unless strategy explicitly models maker:

| Tier | Maker | Taker | Round-trip (taker) |
|------|-------|-------|---------------------|
| Conservative default | 0.40% | 0.60% | **1.20%** |
| Optimistic retail | 0.25% | 0.40% | 0.80% |
| Stress | — | 1.00% | **2.00%** |

**Family C (Trend Persistence)** at daily/4h horizons: spread dominates; fees still applied on turnover.

**Family at 5m/15m:** spread + fees both material — report gross, spread-only, and all-in net.

### 1.3 Slippage proxy

No order-book simulation in v1. Add fixed slippage bps on top of half-spread:

| Signal horizon | Slippage (bps per leg) |
|----------------|------------------------|
| D1 / H4 | 0 (spread-only) |
| H1 / M15 | 2 |
| M5 / M1 | 5 |

Stress: 2× slippage table.

### 1.4 Financing / funding

**Spot v1:** financing = **0**.

**Perpetuals (future):** funding rate series from `funding_rates` table; applied per 8h hold — **not used until Family E**.

### 1.5 Total round-trip cost formula (research)

```
cost_rt = 2 × half_spread_bps + 2 × slippage_bps + taker_fee_rt_bps
```

Report all diagnostics at **1× and 2×** cost stress (forex programme standard).

### 1.6 Comparison to forex lessons

- No financing wall at slow horizons — crypto spot removes FX's ≈4× spread financing squeeze
- Spread may still defeat small gross effects (same discipline as S4, C029)
- Cost model must be **pre-registered** before Family C diagnostics

---

## 2. Provenance and reproducibility

Match forex programme standards:

| Requirement | Implementation |
|-------------|----------------|
| Source documented | `source`, `venue`, `venue_symbol` in sidecar |
| Fetch window | `requested_from`, `requested_to` UTC |
| Batch identity | `fetch_batch_id` UUID per run |
| Row integrity | `data_sha256` over normalized CSV or table export |
| No secrets committed | API keys env-only; sidecar notes `note_no_api_key` |
| Idempotent re-ingest | Upsert on `(instrument, granularity, time_utc, venue)` |
| Manifest per run | JSON in `research/crypto/manifests/` |
| Git policy | Bulk CSV/SQLite **gitignored**; provenance + small samples committed |

### Reproducibility checklist (pre-diagnostic gate)

- [ ] Provenance sidecar exists for each instrument × granularity
- [ ] `data_sha256` verifies against on-disk export
- [ ] Gap report generated and reviewed
- [ ] Cost assumptions documented in sidecar or `CRYPTO_COST_MODEL.md` stub
- [ ] Materialization config hash recorded if derived TFs used

---

## 3. Minimum historical depth

| Asset | Minimum | Desirable | Notes |
|-------|---------|-----------|-------|
| BTC/USD | 5 years | 10+ years | Coinbase/Binance support |
| ETH/USD | 5 years | From 2017 launch | ETH history shorter than BTC |

**Matched-window discipline:** primary diagnostics on rolling 5y window; deep history as robustness arm (like FX futures deep carry run).

**Lockbox:** if train/validation split used later, test window sealed until train gates pass (forex campaign standard).

---

## 4. Validation checks

### 4.1 Ingestion validation (run after authorized backfill)

| Check | Threshold / action |
|-------|-------------------|
| Timestamp monotonicity | Strictly increasing bar opens per series |
| OHLC invariants | high ≥ max(open,close,low); low ≤ min(open,close,high) |
| Duplicate bars | Zero duplicates on PK |
| Gap detection | Report all gaps >1 bar; no silent interpolation |
| Coverage vs request | `actual_bars / expected_bars ≥ 99.5%` for 1m over requested window |
| Volume non-negative | Reject negative volume rows |
| Zero-price bars | Reject or quarantine |

### 4.2 Outlier bounds

| Check | Rule |
|-------|------|
| Single-bar return | Flag if \|return\| > 20% on M1 (likely bad tick); quarantine bar |
| Flash wick | Flag if (high-low)/mid > 15% on M1 |
| Stale flat runs | Flag >60 consecutive identical closes (possible feed freeze) |

Outliers: **quarantine, do not auto-fix.** Document count in manifest.

### 4.3 Cross-venue consistency (BTC/ETH)

On overlapping 1h window (sample ≥30 days):

| Metric | Threshold |
|--------|-----------|
| Close correlation (Coinbase vs Binance) | > 0.999 |
| Mean absolute return diff | < 5 bps per bar |
| USDT basis (Binance vs Coinbase USD) | Document mean/std basis bps |

Failures → investigate before canonical series trusted.

### 4.4 Materialization validation

Reuse forex `verify_materialized_pair`:

- Aggregated M5 count matches expected from M1 source
- OHLCV recomputation spot-check on random 100 buckets
- `aggregation_config_hash` matches manifest

### 4.5 Pre-diagnostic gate (Family C)

Before any trend-persistence diagnostic:

1. All Section 4.1 checks pass for canonical venue
2. Cost model section 1 documented and frozen
3. BTC and ETH each have ≥5y D1 and ≥1y M15 clean coverage
4. Gap report reviewed by operator
5. `check_research_freeze.py` passes

---

## 5. What this sprint does not validate

- No live API calls
- No ingested data
- No factor diagnostics
- No campaigns

Validation **code** is specified here; implementation belongs to the authorized ingestion sprint.

---

## Related documents

- `CRYPTO_DATA_SOURCE_EVALUATION.md` — source selection
- `CRYPTO_DATA_SCHEMA.md` — field definitions
- `CRYPTO_DATA_INGESTION_PLAN.md` — implementation sequence
- `FOREX_STRUCTURAL_COST_CONSTRAINTS.md` — forex cost baseline for comparison
