# Observed-to-Modeled Financing Bridge — Design

**Date:** 2026-05-27  
**Sprint:** `PRACTICE_OVERNIGHT_FINANCING_SAMPLE_PLAN_001`  
**Type:** Design only — `strategy_evidence: false`  
**Implementation:** deferred to `infra-financing-observed-to-modeled-bridge-001`

---

## 1. Problem

Two representations exist today:

| layer | input | output |
|---|---|---|
| **Observed capture** | OANDA `DAILY_FINANCING` JSON | `SanitizedFinancingEvent` point charges |
| **Overlay / calculator** | `PositionInterval` + `FinancingRateSource` | per-trade financing drag in R |

They are **not directly composable**. Observed events are **post-hoc cashflows at rollover**; the overlay expects **rate schedules** or stress tables over hold intervals.

---

## 2. Bridge objective

Transform sanitized observed events into inputs the existing `research/financing/` stack can consume:

1. **`TableRateSource`** — per-(date, instrument) `(long_annual_bp, short_annual_bp)` derived from observed charges
2. Optional **`ObservedEventRateSource`** — direct lookup of observed charge for matching (date, instrument, side) with fallback to stress

Goal: enable **OBSERVED_FINANCING_DIAGNOSTIC** on historical trade CSVs without claiming **MODELED** until reconciliation criteria pass.

---

## 3. Required fields (from observed parser)

| field | source | bridge use |
|---|---|---|
| `time` | DAILY_FINANCING transaction time | rollover date key |
| `instrument` | positionFinancings | pair key |
| `financing` | signed amount (credit > 0) | infer rate or direct charge |
| `units` | openTradeFinancings | notional for bp derivation |
| `financingRate` | openTradeFinancings (if present) | direct rate when available |
| `side` | inferred from units sign | long vs short rate split |
| `baseFinancing` / `quoteFinancing` | positionFinancings | decomposition audit |
| `homeConversionFactors` | if present | home-currency conversion |
| `account_currency` | file-level | home currency for overlay |

---

## 4. Per-instrument vs per-trade treatment

**Preference order:**

1. If `openTradeFinancings` present → use **per-trade** financing and units to derive implied daily rate for that side
2. Else if `positionFinancings` only → **per-instrument** position-level charge; split equally or assign to dominant side if units known elsewhere
3. Else account-level total → **discard for rate table** (insufficient granularity); keep for reconciliation totals only

---

## 5. Conversion factors

When `homeConversionFactors` appear in observed payloads:

- Map quote/base conversion to home currency before annualizing bp
- If absent: use existing calculator heuristic (USD quote/base) and flag `"conversion_deferred"` note on derived rates

Sparse samples may not exercise all conversion paths — document limitations in reconciliation JSON.

---

## 6. Account currency handling

- File-level `account_currency` (typically USD on practice) flows into `FinancingCalculatorConfig.home_currency`
- All derived rates expressed in **home currency** consistent with overlay

---

## 7. Triple rollover / weekend handling

Bridge must tag derived rate rows with:

- Rollover date (UTC date of transaction `time`)
- Whether date is Wednesday (triple swap) — infer from financing magnitude vs adjacent days if sample spans multiple days
- Weekend: OANDA may skip Saturday/Sunday rollovers — calculator already skips weekends; bridge should not invent weekend rates without observations

With **sparse samples** (1–3 DAILY_FINANCING events), triple/weekend rules cannot be validated — conservative stress remains fallback for unmatched dates.

---

## 8. Limitations of sparse samples

| limitation | impact |
|---|---|
| 1–3 financing events | Cannot build full 2020–2026 rate history |
| Few instruments | Unobserved pairs fall back to stress |
| Single account | One broker's practice rates only |
| Practice vs live | Rates may differ from live promotion target |
| Side inference | Short vs long rate separation may be underdetermined |

Sparse samples support **parser validation**, **reconciliation methodology**, and **proof-of-pipeline** — not full backtest MODELED treatment.

---

## 9. MODELED readiness criteria (future gate)

MODELED treatment (`FinancingTreatment.MODELED`) requires **all** of:

1. **Non-empty** observed capture (`daily_financing_count > 0`) committed and sanitized
2. **Bridge implemented** and unit-tested
3. **Reconciliation pass**: derived rates vs observed charges within tolerance on sample window; stress bounds sanity check
4. **Coverage policy** documented: which pairs/dates use observed vs fallback stress
5. **Human review** of readiness memo — no automatic promotion
6. Opt-in engine flag still **off by default** until separate engine sprint

Minimum sample for **pipeline proof**: ≥1 DAILY_FINANCING, ≥1 instrument, ≥1 side inferred.

Minimum sample for **MODELED consideration** (not this sprint's bar): multi-week observed history or reconciled external rate table — TBD in post-sample sprint.

---

## 10. Future implementation sprint outline

**Sprint:** `infra-financing-observed-to-modeled-bridge-001`

1. Load `observed_daily_financing_sanitized.json`
2. Implement `ObservedDerivedRateSource(FinancingRateSource)` with `source_type=observed_future`, `treatment=ESTIMATED` until reconciliation passes
3. Derive `(date, instrument) → RatePair` from events
4. Wire optional path in `apply_modeled_financing_overlay.py` (`--rate-source observed`)
5. Reconciliation report JSON vs conservative stress
6. Update readiness decision — still **not MODELED** unless gate passes
7. No engine PnL change unless separate opt-in sprint

**Prerequisite sprint:** `infra-observed-financing-post-sample-capture-001` after human sample + capture with `daily_financing_count > 0`.

---

## 11. Verdict impact

**None.** C008/C009/C018 REJECT unchanged. No strategy approval.
