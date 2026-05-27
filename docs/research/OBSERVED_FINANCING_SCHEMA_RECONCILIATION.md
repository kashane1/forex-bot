# Observed Financing Schema Reconciliation

**Date:** 2026-05-27  
**Machine-readable:** [`observed_financing_schema_reconciliation.json`](../../research/financing/observed/observed_financing_schema_reconciliation.json)

> Capture status: **OBSERVED_FINANCING_EMPTY**. Reconciliation documents readiness path, not live observed data.

---

## 1. Parser vs overlay

| layer | shape |
|---|---|
| **Observed parser** (`research/financing/observed.py`) | `SanitizedDailyFinancingTransaction` → flat `SanitizedFinancingEvent` rows |
| **Overlay utility** (`research/financing/overlay.py`) | `PositionInterval` + `FinancingRateSource` → per-trade financing drag |
| **Gap** | Observed events are **post-hoc charges** at rollover; overlay needs **rate schedule** or event-to-hold matching |

---

## 2. Bridge required

When observed data exists, a bridge must:

1. Aggregate `SanitizedFinancingEvent` rows into per-(date, instrument) `(long_bp, short_bp)` via `TableRateSource`
2. Or match observed charges to closed trade intervals by instrument/trade/time
3. Reconcile totals against `ConservativeStressRateSource` for sanity bounds

**Current overlay cannot consume observed events directly** without this bridge.

---

## 3. Schema coverage (parser ready)

| OANDA field | parser support |
|---|---|
| DAILY_FINANCING type | ✓ |
| transaction time | ✓ |
| financing amount | ✓ |
| accountBalance | ✓ |
| positionFinancings | ✓ |
| instrument | ✓ |
| baseFinancing / quoteFinancing | ✓ |
| openTradeFinancings | ✓ |
| tradeID (redacted) | ✓ |
| financingRate | ✓ |
| accountFinancingMode | ✓ |
| homeConversionFactors | deferred (not in test fixtures) |

---

## 4. Empty capture impact

With zero DAILY_FINANCING transactions:

- No committed `observed_daily_financing_sanitized.json`
- Synthetic diagnostic (`SYNTHETIC_FINANCING_DIAGNOSTIC`) remains authoritative for C008/C009/C018
- **MODELED treatment not ready**

---

## 5. Verdict impact

**None.** C008/C009/C018 REJECT unchanged.
