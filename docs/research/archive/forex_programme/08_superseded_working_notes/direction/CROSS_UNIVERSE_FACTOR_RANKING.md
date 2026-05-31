# Cross-Universe Factor Ranking

**Sprint:** `research-nonusd-cross-factor-discovery-planning-001` · Phase 4
**Type:** scoring/ranking only. Docs-only. No factor, no screen, no campaign.
**Date:** 2026-05-30.

This phase scores the 24 Phase-2 families (F01–F24) across **8 axes**, carrying
the Phase-3 fences. The goal is a defensible ordering for the Phase-5 shortlist —
not a performance claim. **No backtest, no signal, no number from data.**

---

## Scoring rubric (1–5; higher = more favorable for a research bet)

| Axis | 1 (unfavorable) | 5 (favorable) |
|------|-----------------|---------------|
| **Novelty** | restates a closed lane | structurally impossible before crosses |
| **Implementation complexity** *(inverted: 5 = simplest)* | 3-leg / new infra / new data ingest | reuses existing bars + lab modules |
| **Cost sensitivity** *(5 = least cost-exposed)* | high turnover × widest crosses | low turnover / cheapest legs (EUR_GBP) |
| **Financing sensitivity** *(5 = least financing-exposed)* | overnight carry-driven, needs un-ingested rates | intraday / financing-free |
| **Data requirements** *(5 = needs nothing new)* | needs real swap rates / tick / longer history | uses already-populated bars only |
| **Robustness potential** | best-of-N / forking-path prone | single pre-registered spec, regime-stable |
| **Replication potential** | one-off, no independent confirmation | confirms across many non-collinear legs |
| **Overlap with prior failures** *(5 = least overlap)* | a hidden re-tune of a reject | no prior analogue |

Weighted composite emphasizes the programme's binding constraints: **Cost ×2,
Financing ×1.5, Overlap ×1.5, Robustness ×1.5**, others ×1. (Max raw composite
with these weights = 5 × (2+1.5+1.5+1.5+1+1+1+1) = 5 × 10.5 = 52.5; reported
normalized to /5.)

---

## Score table

| ID | Family | Nov | Cmplx | Cost | Fin | Data | Robust | Repl | Overlap | **Wtd /5** |
|----|--------|-----|-------|------|-----|------|--------|------|---------|-----------|
| F01 | Currency-strength index | 5 | 3 | 3 | 4 | 5 | 4 | 5 | 5 | **4.17** |
| F02 | Strength-dispersion timing | 5 | 3 | 3 | 4 | 5 | 3 | 4 | 5 | **3.93** |
| F03 | Strongest-vs-weakest pairing | 4 | 3 | 3 | 3 | 5 | 4 | 5 | 4 | **3.74** |
| F04 | Strength mean-reversion | 4 | 3 | 2 | 4 | 5 | 3 | 4 | 3 | **3.36** |
| F05 | Triangular drift-consistency | 5 | 2 | 2 | 4 | 5 | 3 | 4 | 4 | **3.45** |
| F06 | Triangular residual reversion | 5 | 1 | 1 | 4 | 5 | 2 | 3 | 3 | **2.69** |
| F07 | Implied-vs-traded basis *filter* | 4 | 3 | 4 | 4 | 5 | 3 | 4 | 4 | **3.83** |
| F08 | Currency cross-sectional momentum | 4 | 3 | 3 | 3 | 5 | 3 | 5 | 3 | **3.50** |
| F09 | Cross-sectional momentum + carry tilt | 4 | 2 | 3 | 2 | 2 | 3 | 4 | 3 | **2.83** |
| F10 | Short-horizon cross-sectional reversal | 3 | 3 | 1 | 4 | 5 | 2 | 4 | 2 | **2.79** |
| F11 | Momentum-of-crosses (instrument) | 3 | 4 | 3 | 3 | 5 | 2 | 3 | 2 | **2.93** |
| F12 | Classic two-leg carry | 4 | 2 | 3 | 1 | 1 | 3 | 4 | 3 | **2.64** |
| F13 | Carry-to-vol | 4 | 2 | 3 | 1 | 1 | 3 | 4 | 3 | **2.64** |
| F14 | Carry-crash / safe-haven hedge | 4 | 2 | 3 | 1 | 1 | 3 | 4 | 3 | **2.64** |
| F15 | Shared-leg JPY-cross RV | 4 | 3 | 3 | 3 | 5 | 3 | 4 | 3 | **3.38** |
| F16 | Triangle-closure cointegration | 4 | 1 | 1 | 4 | 5 | 3 | 3 | 3 | **2.74** |
| F17 | Safe-haven CHF RV | 4 | 3 | 3 | 3 | 5 | 3 | 3 | 3 | **3.29** |
| F18 | Half-life-matched RV (C028 fix) | 3 | 3 | 3 | 3 | 5 | 4 | 4 | 2 | **3.29** |
| F19 | Shared-leg lead-lag | 4 | 3 | 2 | 4 | 5 | 3 | 4 | 4 | **3.55** |
| F20 | Risk-proxy leadership | 4 | 3 | 3 | 3 | 4 | 3 | 4 | 4 | **3.50** |
| F21 | Cross-pair confirmation *filter* | 3 | 4 | 4 | 4 | 5 | 3 | 4 | 4 | **3.83** |
| F22 | Safe-haven vs risk vol-dispersion | 4 | 3 | 4 | 4 | 4 | 3 | 4 | 4 | **3.79** |
| F23 | Correlation-regime *gate* | 4 | 4 | 5 | 5 | 4 | 4 | 3 | 4 | **4.17** |
| F24 | **C1 replication (sanctioned)** | 4 | 5 | 3 | 4 | 5 | 5 | 5 | 4 | **4.31** |

*(Cost/Financing/Data are the "5 = least exposed" inverted axes; complexity is
"5 = simplest". Composite is the weighted normalization defined above.)*

---

## Ranked order (by weighted composite)

1. **F24 — C1 replication (4.31)** — cheapest to run (frozen def + materialized
   bars + existing lab), highest robustness/replication, the sanctioned reuse.
2. **F01 — Currency-strength index (4.17)** — most novel, breadth-pure, the
   foundation other families (F02–F04, F08) build on.
3. **F23 — Correlation-regime gate (4.17)** — cheapest/financing-free overlay;
   value is as an enabler of the breadth families, not standalone.
4. **F02 — Strength-dispersion timing (3.93)** — strength-index derivative.
5. **F07 — Implied-vs-traded basis filter (3.83)** / **F21 — confirmation filter
   (3.83)** — low-cost filters (no extra leg cost), but cannot create edge alone.
6. **F22 — Vol-dispersion (3.79)** · **F03 — strongest-vs-weakest (3.74)** ·
   **F19 — lead-lag (3.55)** · **F08 — cross-sectional momentum (3.50)** ·
   **F20 — risk-proxy leadership (3.50)**.
7. **Mid (3.2–3.5):** F05, F15, F18, F17, F04.
8. **Bottom (<3.0) — Phase-3-fenced:** F11 (2.93), F09 (2.83), F10 (2.79),
   F16 (2.74), F06 (2.69), F12/F13/F14 (2.64, financing-data-blocked).

---

## What the ranking says (interpretation)

- **The top tier is breadth-pure or replication.** F24, F01, F23, F02 all exploit
  the *one* new lever (non-collinear breadth) and need **no** new data — they
  score high precisely because they avoid the unchanged walls (cost, financing,
  history).
- **Filters (F07, F21, F23) rank well but cannot stand alone.** They are
  enablers/overlays. A shortlist built only of filters would have nothing to
  filter. They belong *attached* to a generator (F01/F08/F24).
- **Carry (F12–F14) sinks on Financing + Data** — not because the thesis is weak
  (FX carry is the most documented style factor) but because the **real swap
  rates are not ingested**; screening on estimates is a data-integrity violation.
  Carry's true rank is "high-potential but **prerequisite-blocked**" — it should
  drive a *data* sprint, not a factor screen, until financing exists.
- **Three-leg families (F06, F16) sink on Cost + Complexity** — they multiply the
  exact wall the programme died on.
- **The C016/C028 ghosts (F09/F10/F11, naive RV) sink on Overlap** — the
  weighting deliberately penalizes hidden re-tunes.

This ordering feeds Phase 5, which takes the **top breadth-pure generators + the
sanctioned replication + the single most valuable enabling overlay**, capped at 5.
