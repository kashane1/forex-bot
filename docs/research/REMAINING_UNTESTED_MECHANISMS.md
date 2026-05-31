# Remaining Untested Mechanisms

**Sprint:** `research-cross-factor-programme-synthesis-001` · Phase 3
**Type:** mechanism-space gap analysis. Docs-only. No testing performed.
**Date:** 2026-05-30.

What return sources / constraint regimes the programme has **not** genuinely tested.
A mechanism counts as "tested" only if it was evaluated with adequate data and
cleared (or failed) the front-gate discipline. "Data-blocked" or "never attempted"
mechanisms are the genuine frontier.

---

## 1. Carry (interest-rate differential) — GENUINELY UNTESTED

- **Status:** **data-blocked for the entire programme.** Carry is the return to
  holding a higher-yielding currency vs a lower-yielding one — a *different return
  source* than every spread-capture/reversion mechanism tested. It was untestable on
  7 USD majors (carry needs non-USD high/low-yield pairs) and on estimate rates.
- **What changed:** the cross expansion added **real carry pairs** — AUD_JPY,
  NZD_JPY, EUR_JPY (high-yield/commodity vs funding currencies). The *spot* data is
  populated; the **financing/swap rates are still un-ingested** (the registry
  carries qualitative *estimates* only).
- **Why it is the cleanest open mechanism:** it does not rely on predicting price
  direction or on capturing a sub-spread reversion — its return accrues from the
  rate differential. It is the single most-documented FX factor (decades of
  literature) and has **never** been touched here.
- **Known headwind (honest):** C031 found financing ≈4× spread on this venue, and
  carry crashes in risk-off (AUD/NZD_JPY co-move down). So carry on this *retail*
  venue may be financing-defeated too — but that is a *result to be measured*, not a
  reason to skip the one untested mechanism.
- **Prerequisite:** ingest **real OANDA financing/swap rates** (a data sprint), then
  a later pre-registered carry factor-validation. **Carry cannot be honestly tested
  on estimate rates** (that repeats C031's financing-defeat on guessed costs).

## 2. Financing as a first-class data object — UNTESTED / UN-INGESTED

- Distinct from carry-the-factor: the programme has **modeled** financing (C031's
  estimate, the two-legged carry cost model) but never **ingested observed
  financing**. Real swap rates would (a) enable carry, (b) sharpen every overnight
  cost estimate, and (c) let the financing wall be measured rather than assumed.
- This is the **enabling prerequisite** for §1 and a permanent data asset regardless
  of the carry verdict.

## 3. Alternative-venue / lower-cost execution effects — UNTESTED

- Every result is on **OANDA practice, retail spreads, mid-price**. S4 proved
  genuine no-arb RV structure exists but is sub-*retail*-cost-band. Whether that (or
  any cost-defeated effect) survives at **institutional / ECN spreads** is
  completely untested — a different *cost regime*, not a different idea.
- Requires a lower-cost venue or a realistic institutional-cost model; the highest
  ceiling but the largest lift and overfit risk.

## 4. True tick / Level-2 / order-flow microstructure — UNTESTED

- "Volume" here is a tick-count proxy; there is no order book or trade flow.
  Participation/imbalance/flow hypotheses (H03/H10/H11/H13) were never honestly
  testable. Genuine microstructure is a distinct mechanism behind a paid-data wall.

## 5. Futures (FX / index) — UNTESTED, different cost structure

- FX/index futures have a **different cost profile** (no per-side spread squeeze in
  the same way; centralized, deep history) and real **volume**. The corpus review
  flagged them as the **best structural fix to the cost squeeze**, deferred for roll
  infrastructure. A genuinely different venue + cost regime + history depth.

## 6. Metals / crypto / equities — UNTESTED, different markets

- **Crypto:** deep free history, larger gross edges, 24/7 — but regime/venue and
  funding costs. **Metals:** FX-like or futures. **Equities/ETFs:** survivorship +
  corporate actions. All are *new markets* (edge diversity) rather than new
  *mechanisms*; large infra lifts.

## 7. Longer history / multi-regime — UNTESTED

- ~5y underpowers slow/macro/regime signals. ≥10–15y would let slow mechanisms
  (incl. carry's crash dynamics) be tested across multiple macro regimes without
  forking paths. A data-depth constraint, orthogonal to cost.

## 8. Alternative data (macro/rates/sentiment) — PARTIALLY TESTED, weak

- FRED macro/rates context was ingested and tested as **slow conditioning** →
  **no actionable tradeability** (rate-regime non-identifiable on ~5y, JP leg
  absent). Sentiment/positioning/flow data is untouched but speculative and
  data-hungry.

---

## 9. Frontier summary (ranked by "genuinely new mechanism" + readiness)

| Mechanism / regime | New return source? | Testable now in-repo? | Main blocker |
|---|---|---|---|
| **Carry (interest-rate differential)** | **Yes** | **Almost — needs financing ingest** | un-ingested swap rates |
| Financing as data | enabler | **Yes (a data sprint)** | not yet ingested |
| Lower-cost / institutional venue | No (cost regime) | No | venue/data access |
| True tick / L2 / order flow | Yes (microstructure) | No | paid data |
| Futures (FX/index) | partly (cost regime + volume) | No | roll infra + ingest |
| Metals / crypto / equities | new markets | No | new pipelines |
| Longer history (10–15y) | No (depth) | No | data acquisition |
| Alternative/sentiment data | maybe | No | data + speculative |

**The single mechanism that is both genuinely new (a different return source) and
nearly testable in-repo is CARRY — gated only on a real-financing-data ingest.**
Everything else is either a *cost/venue regime change* (large lift) or a *new
market* (large lift) or *already weakly tested* (macro). This frames Phase 4/5.
