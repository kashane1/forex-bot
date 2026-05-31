# Complete Programme Evidence Inventory

**Sprint:** `research-cross-factor-programme-synthesis-001` · Phase 1
**Type:** evidence classification. Docs-only. No new analysis.
**Date:** 2026-05-30.

Every major effort across the entire FX research programme, classified into the six
requested buckets. Sources are the committed verdict/summary docs. "Cost-defeated"
= a genuine or plausible gross effect that net-of-cost is negative; "rejected" =
within-null / no effect / sign-incoherent; "failed replication" = real on discovery
data but did not generalize; "real but weak" = genuine and null-separated but
insufficient (sub-cost-band / narrow); "financing-blocked" = limited by missing or
prohibitive financing; "infrastructure-only" = capability/data, no edge claim.

---

## 1. Master classification table

| Effort | Era | Mechanism | Classification |
|---|---|---|---|
| C015 / C017 / C025 breakout (Donchian etc.) | majors | directional breakout | **cost-defeated** |
| C026 timeframe ladder (M3–M30) | majors | breakout/TF | **cost-defeated** (cost gradient, no floor) |
| C020–C023 pullback / MTF pullback | majors | directional continuation | **rejected** (no entry edge; RETIRED) |
| C008 / C027 price-level / z-score reversion | majors | mean-reversion | **cost-defeated** (C027 failed train gate) |
| C1 multi-TF confluence (validation) | majors | directional confluence-reversion | **cost-defeated** (GENUINE factor, sub-spread) |
| C1 high-vol front gate | majors | directional, vol-conditioned | **cost-defeated** (FAIL_FRONT_GATE, net-neg 3/3) |
| C016 weekly cross-sectional momentum | majors | cross-sectional directional | **rejected** (a USD bet, collinear) |
| C028 relative-value spread | majors | cointegration reversion | **rejected** (LIKELY_SELECTION_NOISE) |
| C031 vol-managed TSMOM | majors | time-series momentum | **financing-blocked** (WITHIN_NULL + financing ≈4× spread) |
| C029 10-pip range-bar campaign | non-time-bar | directional (alt clock) | **cost-defeated** (net −0.019R) |
| Non-time-bar feasibility | non-time-bar | alt-clock sampling | **infrastructure-only** (kept infra, paused search) |
| H16 overshoot-exhaustion front gate | non-time-bar | microstructure fade | **rejected** (FAIL, rev≈0.50, null-internal) |
| H03 thin-move front gate | non-time-bar | microstructure/participation fade | **rejected** (FAIL → lane RETIRED) |
| C1 cross replication (S1) | crosses | directional confluence-reversion | **failed replication** (USD-regime artifact) |
| S2 currency-strength validation | crosses | cross-sectional currency strength | **rejected** (real descriptor, non-predictive) |
| S3 cross-sectional momentum | crosses | cross-sectional directional | **rejected** (pre-falsified by S2) |
| S4 cross relative-value (triangular) | crosses | no-arb reversion | **real but weak** (genuine, sub-cost-band) |
| S5 regime gate | crosses | overlay/conditioner | **rejected** (moot — no surviving generator) |
| Non-USD cross ingestion + population | crosses | — | **infrastructure-only** (breadth data; no edge) |
| Edge-discovery lab + null/cost gates | infra | — | **infrastructure-only** (working front gate) |
| Backtrader parity / risk-engine / financing model | infra | — | **infrastructure-only** (working) |
| Cross-asset FRED / macro-regime context | macro | slow conditioning | **rejected** (no actionable tradeability) + data-blocked |

## 2. Bucket roll-up

- **Rejected (no effect / within-null / sign-incoherent):** C020–023, C016, C028,
  H16, H03, S2, S3, S5, macro-regime context. → *Directional/cross-sectional
  prediction and microstructure fades do not exist or do not predict on this venue.*
- **Failed replication:** C1 cross replication (S1). → *The one genuine majors
  factor was a USD-regime artifact; did not generalize to non-collinear crosses.*
- **Real but weak:** S4 cross relative-value. → *The programme's ONLY genuine
  factor — real no-arb reversion, but ~10× inside the cost band.*
- **Cost-defeated (gross effect, net-negative):** C015/017/025, C026, C008/C027,
  C1 (validation + front gate), C029. → *Multiple plausible gross effects, all
  smaller than the round-trip spread on this venue.*
- **Financing-blocked:** C031 (financing ≈4× spread; book collapsed to a USD bet).
  → *Slow/overnight signals are defeated by financing, and real carry was never
  testable (no rate leg, no carry crosses) until the cross expansion.*
- **Infrastructure-only (capability/data, no edge claim):** non-time-bar infra,
  cross ingestion/population, the edge-discovery lab + gates, parity/risk/financing
  models, FRED ingest. → *The platform is sound and not the bottleneck.*

## 3. Cross-cutting reading

1. **The dominant failure mode is cost, not idea quality.** Where a gross effect
   exists (C1, C029, S4), it is **smaller than the cost of trading it** on this
   venue. Where cost is not the wall, the effect is simply **absent** (S2/S3/H16/
   H03) or a **USD artifact** (C1 replication).
2. **Breadth was real but insufficient.** The cross expansion did exactly what it
   promised — broke USD-collinearity (S2 breadth passed; S4 found genuine no-arb
   structure) — and **still** every effect is sub-cost-band. Breadth was not the
   binding constraint; **cost** is.
3. **One genuine factor exists (S4).** It is sub-retail-cost-band, which is itself
   informative: genuine RV structure is present, just not exploitable at retail
   spreads.
4. **The platform is not the bottleneck.** All infrastructure efforts are
   working; the project has not been code/infra-blocked since the lab + gates were
   built.
5. **Carry is the one mechanism never actually tested.** Every classification above
   is a spread-capture or reversion mechanism; **interest-rate-differential carry**
   — the canonical FX factor — was always **data-blocked** and only became testable
   when the cross expansion added real carry pairs (AUD_JPY, NZD_JPY, EUR_JPY).
