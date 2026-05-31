# Carry Dataset — Plausibility Review (Phase 4)

**Sprint:** `research-financing-rate-data-ingestion-001` · Phase 4
**Type:** research-only plausibility review (does the history behave as expected?).
Docs-only. **No factor study, no edge claim.**
**Date:** 2026-05-31.

Checks the carry history against known macro reality: rate regimes, central-bank
cycles, and cross sensibility. Figures from the committed dataset.

---

## 1. Rate snapshots across the window (annualized %)

```
date         USD    EUR    GBP    JPY    AUD    NZD    CHF    CAD
2021-06     0.09  -0.54   0.08  -0.07   0.03   0.33  -0.74   0.13
2022-06     1.87  -0.24   1.57   0.01   1.60   2.68  -0.51   1.83
2023-01     4.61   2.34   4.01  -0.01   3.32   4.81   0.99   4.33
2023-07     5.35   3.67   5.49  -0.00   4.30   5.67   1.72   4.93
2024-01     5.26   3.93   5.20   0.03   4.35   5.64   1.69   4.95
2025-01     4.33   2.70   4.55   0.77   4.33   4.05   0.41   3.06
2026-01     3.63   2.03   3.71   1.12   3.77   2.50  -0.04   2.19
```

## 2. Do known rate regimes appear? — YES

- **2021 post-COVID ZIRP:** every currency near zero or **negative** (EUR −0.54,
  CHF −0.74, JPY −0.07). The negative-rate regime is faithfully present.
- **2022–23 global hiking:** rates rise everywhere, peaking 2023-07 → 2024-01 (USD
  ~5.3, GBP ~5.5, NZD ~5.7). The most aggressive tightening in decades is captured.
- **2024–26 easing:** rates roll over (USD 5.26 → 3.63; NZD 5.64 → 2.50; CHF 1.69 →
  −0.04). The cutting cycle is present.

## 3. Do major central-bank cycles appear? — YES

- **Fed (USD):** 0.09 (2021) → 5.35 (2023 peak) → 3.63 (2026). The full hike-and-cut
  arc.
- **BoJ (JPY) — the signature check:** **−0.07 (2021) → ~0 through 2023 → 0.77
  (2025) → 1.12 (2026).** The historic **exit from negative/zero rates** is exactly
  where it belongs — JPY is the late mover, validating the funding-currency role and
  the 2022–24 USD_JPY divergence.
- **ECB / SNB lag then follow:** EUR/CHF stay negative into 2022 (−0.24 / −0.51 in
  2022-06) while the Fed/RBNZ are already hiking — the well-documented ECB/SNB lag —
  then catch up (EUR 3.93, CHF 1.72 at peak) and ease back (CHF → −0.04 by 2026).
- **RBNZ / RBA (NZD/AUD):** NZD leads the high-yield side (highest-rate currency 66%
  of months), peaking 5.67; AUD tracks. Consistent with the aggressive RBNZ cycle.

## 4. Do cross relationships look sensible? — YES

- **USD_JPY carry: 0.16 (2021) → 5.35 (2023) → 2.50 (2026).** The explosion to >5%
  during the Fed-vs-BoJ divergence is the **textbook 2022–24 carry trade** — the
  single most-discussed FX carry episode of the period, reproduced exactly.
- **AUD_JPY carry: 0.10 → 4.30 (2023) → 3.07** — the classic risk-on carry cross,
  positive throughout and peaking with the rate divergence.
- **EUR_USD carry: −0.63 → −2.27 (2023) → −1.74** — long-EUR pays carry throughout
  (USD out-yields EUR), most negative at the peak Fed–ECB gap. Correct sign and
  shape.
- **Funding pair stability:** CHF/JPY are the lowest-yield currencies in **100%** of
  months between them — the persistent funding base every carry cross is built on.

## 5. Any anomalies / caveats?

- **None macro-inconsistent.** Every regime, cycle, and cross matches reality.
- The **sign-flips** in AUD_USD/GBP_USD/NZD_USD/USD_CAD/EUR_JPY are **not** anomalies
  — they are the USD hiking cycle reordering the cross-section (USD overtaking
  AUD/GBP/NZD in 2022–23), which is correct and, notably, gives the carry signal
  genuine **time-variation** (not a static ranking).
- The only data caveat remains structural, not a plausibility failure: **monthly
  cadence** + the **interbank-vs-broker-financing gap** (Phase 1 §4) — relevant to
  readiness (Phase 6), not to whether the history is real.

## 6. Plausibility verdict

The carry history is **macro-faithful**: it reproduces the 2021 ZIRP/negative-rate
regime, the 2022–23 global hiking peak, the 2024–26 easing, the BoJ's historic exit
from negative rates, the ECB/SNB lag, the RBNZ-led high-yield side, and the
signature 2022–24 USD_JPY/AUD_JPY carry-trade episode — with funding currencies
(JPY/CHF) persistently lowest. The dataset behaves exactly as a credible carry
dataset should. **No edge is claimed** — only that the data is real and sensible.
Readiness for a formal carry study is assessed in Phase 6 after the study design
(Phase 5).
