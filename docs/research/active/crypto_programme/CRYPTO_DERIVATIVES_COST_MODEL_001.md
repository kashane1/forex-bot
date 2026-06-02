# Crypto Derivatives Cost Model 001 — Frozen Perp Assumptions

**Sprint:** `crypto-derivatives-backfill-001`
**Date:** 2026-06-02
**Status:** **FROZEN** — pre-registered before any Family E diagnostics.
**Scope:** BTC/ETH perpetuals (Deribit-canonical, USD-quoted). Separate from the spot freeze (`CRYPTO_COST_MODEL_001.md`).

---

## 1. Purpose

Freeze conservative perpetual-swap cost assumptions so Family E diagnostics report gross, spread-only, all-in, and 2× stress variants without tuning costs to results. Costs are **not** calibrated from signal outcomes.

## 2. Taker fee (perp)

Deribit BTC/ETH perpetual published taker ≈ 0.05% (5 bps); maker ≈ 0.00%. Research diagnostics assume **taker round-trip** (conservative):

| Component | Rate (bps) | 2× stress |
|-----------|-----------|-----------|
| Taker (per leg) | 5 | 10 |
| **Round-trip (taker)** | **10** | **20** |
| Maker (recorded, not default) | 0 | — |

This is far cheaper than spot Coinbase taker (120 bps round-trip) — perps are the cheaper venue, which is exactly why Family E is worth testing despite spot being cost-defeated.

## 3. Spread proxy (perp half-spread)

Public candle/funding data is mid/mark; apply assumed half-spread at entry and exit. Perp books are tighter than spot:

| Instrument | Half-spread (bps) | 2× stress |
|------------|-------------------|-----------|
| BTC_PERP_USD | 2.0 | 4.0 |
| ETH_PERP_USD | 3.0 | 6.0 |

## 4. Slippage by horizon (bps per leg)

| Signal horizon | Slippage (bps/leg) | 2× stress |
|----------------|-------------------|-----------|
| D1 / H4 | 0 | 0 |
| H1 / 8h-funding | 1 | 2 |
| sub-hour | 3 | 6 |

## 5. All-in round-trip cost

```
cost_rt_bps = 2 × half_spread_bps + 2 × slippage_bps + taker_fee_rt_bps
```

**BTC_PERP_USD at 8h/H1 horizon (1×):** `2×2 + 2×1 + 10 = 16 bps`.
**ETH_PERP_USD at 8h/H1 horizon (1×):** `2×3 + 2×1 + 10 = 18 bps`.
**2× stress (BTC):** `2×4 + 2×2 + 20 = 32 bps`.

## 6. Funding cashflow (the distinguishing perp cost)

- **Sign convention (single source of truth):** when `funding_rate > 0`, **longs pay shorts**. Long funding PnL over an interval = `−funding_rate × notional`; short = `+funding_rate × notional` (`derivatives_models.funding_cashflow`).
- Deribit funding is **continuous/hourly-realized**: realized funding over a holding period = Σ(`interest_1h` × notional) with the sign convention. The stored `funding_interval_hours = 1`.
- Any diagnostic that holds across funding settlements **must** include funding cashflow in all-in and 2× variants. Funding can dominate carry-style diagnostics — it is the perp analogue of FX financing.

## 7. Reporting variants (mandatory in Family E)

| Variant | Definition |
|---------|------------|
| Gross | Mid/mark returns, no costs, no funding |
| Spread-only | Deduct `2 × half_spread_bps` |
| All-in | Full formula §5 **+ realized funding §6** |
| 2× stress | Double spread, slippage, fee; funding as observed (not halved) |

## 8. Intentionally excluded (perp v1)

| Excluded | Reason |
|----------|--------|
| Liquidation/insurance fees | No leverage modelled; diagnostics are unlevered return studies |
| Maker-rebate optimization | Conservative taker default |
| Order-book depth simulation | Fixed-bps proxy only |
| USDT basis | Deribit perps are USD inverse — no USDT confound |
| Cross-venue fee arbitrage | Single canonical venue |
| Tax / withdrawal | Out of research scope |

## 9. Immutability rule

Do **not** adjust fee/spread/slippage based on diagnostic results. Changing assumptions requires a new cost-model document and a re-run from scratch.

## 10. Implementation references

| Component | Location |
|-----------|----------|
| Funding sign helper | `research/crypto/derivatives_models.py` (`funding_cashflow`) |
| Basis helper | `research/crypto/derivatives_models.py` (`compute_basis`) |
| Backfilled funding (USD, hourly) | `research/crypto/derivatives/backfill/<inst>/funding.csv` (gitignored) |

---

## Related documents
- `CRYPTO_DERIVATIVES_DATA_MODEL.md`
- `CRYPTO_FAMILY_E_DIAGNOSTIC_DESIGN.md`
- `CRYPTO_COST_MODEL_001.md` (spot — separate freeze)
