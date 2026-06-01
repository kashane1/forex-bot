# Crypto Cost Model 001 — Frozen Spot Assumptions

**Sprint:** `crypto-full-backfill-and-canonical-dataset-001` · Phase 5
**Date:** 2026-06-01
**Status:** **FROZEN** — pre-registered before any Family C diagnostics
**Authority:** Canonical entry point referencing `CRYPTO_DATA_VALIDATION_REQUIREMENTS.md` §1

---

## 1. Purpose

Freeze initial Coinbase spot cost assumptions for Family C Trend Persistence diagnostics. Costs are **not** tuned to signal results. All diagnostics must report gross, spread-only, all-in, and 2× stress variants.

---

## 2. Spread proxy assumptions

Public candle APIs provide mid OHLC only. Apply assumed half-spread at entry and exit:

| Instrument | Half-spread (bps) | 2× stress (bps) | Source |
|------------|-------------------|-----------------|--------|
| BTC_USD | 5.0 | 10.0 | `research/crypto/registry.py` |
| ETH_USD | 8.0 | 16.0 | `research/crypto/registry.py` |

Conservative vs typical tight Coinbase spot. Not calibrated from this sprint's data.

---

## 3. Taker fee assumption

Research diagnostics assume **taker round-trip** (conservative default tier):

| Component | Rate |
|-----------|------|
| Maker | 0.40% |
| Taker | 0.60% |
| **Round-trip (taker)** | **1.20%** (= 120 bps) |

Stress tier: **2.00%** round-trip (= 200 bps).

---

## 4. All-in round-trip cost formula

```
cost_rt_bps = 2 × half_spread_bps + 2 × slippage_bps + taker_fee_rt_bps
```

### 4.1 Slippage by horizon (bps per leg)

| Signal horizon | Slippage (bps/leg) | 2× stress |
|----------------|-------------------|-----------|
| D1 / H4 | 0 | 0 |
| H1 / M15 | 2 | 4 |
| M5 / M1 | 5 | 10 |

### 4.2 Worked examples (1× cost)

**BTC_USD at H4 horizon:**

```
cost_rt = 2×5 + 2×0 + 120 = 130 bps = 1.30%
```

**ETH_USD at M15 horizon:**

```
cost_rt = 2×8 + 2×2 + 120 = 136 bps = 1.36%
```

---

## 5. Reporting variants (mandatory in Family C)

Every diagnostic must report:

| Variant | Definition |
|---------|------------|
| **Gross** | Mid-price returns, no costs |
| **Spread-only net** | Deduct `2 × half_spread_bps` round-trip |
| **All-in net** | Full formula at 1× assumptions |
| **2× stress** | Double spread, slippage, and fee stress tier |

---

## 6. What is intentionally excluded (spot v1)

| Excluded | Reason |
|----------|--------|
| Overnight financing | Spot has no FX-style rollover |
| Funding rates | Perpetuals deferred to Family E |
| Open interest | Not applicable to spot v1 |
| Maker fee optimization | Diagnostics assume taker unless explicitly modeling maker |
| Order-book slippage simulation | Fixed bps proxy only |
| USDT basis (Binance vs Coinbase USD) | Cross-venue sample not canonical |
| Tax / withdrawal fees | Out of research scope |

---

## 7. Why funding/open-interest is deferred

Family C Trend Persistence targets spot BTC/USD and ETH/USD on Coinbase. Financing and funding-rate mechanics apply to perpetuals (Family E). Introducing funding now would conflate spot cost structure with derivatives carry — a separate hypothesis lane.

---

## 8. Comparison to forex programme

| Aspect | Forex | Crypto spot v1 |
|--------|-------|----------------|
| Financing at slow horizons | Material (~4× spread squeeze) | **Zero** |
| Primary cost binding | Spread + financing | Spread + taker fees |
| Spread stress | 2× standard | 2× standard (same discipline) |
| Pre-registration | Required before diagnostics | **Frozen in this document** |

---

## 9. Immutability rule

Do **not** adjust half-spread, fee, or slippage assumptions based on Family C signal results. If assumptions change, require a new cost-model document and re-run diagnostics from scratch.

---

## 10. Implementation references

| Component | Location |
|-----------|----------|
| Half-spread registry | `research/crypto/registry.py` |
| Full requirements | `CRYPTO_DATA_VALIDATION_REQUIREMENTS.md` §1 |
| Ingestion spread on bid/ask | `research/crypto/coinbase.py` (`_mid_with_spread`) |

---

## Related documents

- `CRYPTO_DATA_VALIDATION_REQUIREMENTS.md`
- `CRYPTO_FAMILY_C_PREDIAGNOSTIC_READINESS_001.md`
