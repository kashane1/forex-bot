# Currency-Strength Factor — Verdict (Phase 7)

**Sprint:** `research-currency-strength-factor-validation-001` · Phase 7
**Type:** verdict. The **frozen verdict map** (protocol §15) is applied
mechanically to the Phase 2–6 evidence. The factor definition was never altered
after results were observed.
**Date:** 2026-05-30.

---

## Verdict

# `FACTOR_REJECTED`

Cross-implied currency strength is a **real, breadth-diverse descriptor** of the
contemporaneous FX state, but it carries **no forward-predictive information**.
Conditioning on the strongest / weakest / rapidly-strengthening / rapidly-weakening
currency yields forward currency returns that are statistically **indistinguishable
from random** at every horizon, under all four nulls, in every currency / year /
session sub-population, and across every nearby lookback / ranking / aggregation
definition. It is not a factor.

---

## How the frozen criteria resolve

`FACTOR_REJECTED` triggers if the effect is **within null**, **sign-incoherent**,
**single-currency/period-driven**, or **reducible to the USD axis**. The evidence:

### Effect within null ✓ (decisive)
- **0 of 80** null cells clear |z| ≥ 2; **global max |z| = 1.65** (Phase 5). All
  four nulls (randomized-rank, shuffled-currency, session-matched, unconditional)
  coincide — there is no strength→return link to break.
- Mean forward returns are **~0.01–0.13 bp vs ±6–14 bp path noise** (Phase 3) —
  ≈1–2% signal-to-noise; hit rates 0.49–0.51; MFE ≈ −MAE (symmetric).

### Sign-incoherent across slices ✓
- Signs split ~**50/50 across currencies, years, and sessions** with sub-bp
  magnitudes (Phase 4); flip across **lookbacks** (Phase 6). No coherent
  continuation or reversion in any sub-population.

### Not single-currency/period-driven — but moot
- No single currency or year carries the (absent) effect; the largest blip
  (`rapid_weaken` 15m, z≈−1.6) is the expected noise maximum over 80 cells and
  does not persist. There is no concentrated signal to attribute.

### NOT reducible to the USD axis — and yet still rejected (the important nuance)
- Uniquely among the programme's rejects, the **breadth hypothesis H2 PASSED**:
  PC1 explains only 47% and is a **haven-vs-risk** axis (USD/JPY vs AUD/NZD/CAD),
  not a USD axis; PC2/PC3 add independent structure (Phase 2). The strength vector
  is **genuinely multi-currency**. So this is **not** the feared "USD artifact in
  new clothes."
- The factor fails not because it is degenerate breadth, but because **even a
  genuine, breadth-diverse currency-strength state does not predict forward
  currency returns** on this corpus. Strength is **persistent** (rank_persist 84%
  at 5m) yet **non-predictive** — a contemporaneous descriptor, not a forecast.

### Success criteria — not met
`FACTOR_FRONT_GATE_CANDIDATE` required existence + null-separation on multiple
cells under all four nulls + robustness + breadth. Breadth holds, but **existence
and null-separation fail outright** (0/80 cells), so the candidate bar is not met.

### Why not FACTOR_REAL_BUT_WEAK
`REAL_BUT_WEAK` requires a coherent, **null-separated** effect existing *somewhere*
stable, merely too narrow for a front gate. Here **nothing clears any null in any
slice or neighbour** — the effect is not weak, it is **absent**. A result that is
null under all four nulls, sign-incoherent across all slices, and stable-null
across all neighbours is `REJECTED`, not `REAL_BUT_WEAK`. (The construction is
"real" as a descriptor — hence the breadth pass — but the *predictive factor* the
verdict map grades does not exist.)

---

## What this verdict asserts / does not assert

**Asserts:** on this 5-year, 15-instrument M5 corpus, a cross-implied
currency-strength **ranking/Δ does not forecast** forward currency returns at
5–240 min — the cross-section is intraday-efficient at the currency level. The
construction is sound and breadth-diverse; the *predictability* is absent.

**Does NOT assert:**
- **Anything about tradability** (out of scope; never computed — no cost gate
  entered this verdict).
- **That currency-strength indices are meaningless** — they are a valid,
  multi-currency *descriptor* (H2 passed); they simply have no forward edge here.
- **That a different construction/horizon/data could never work** — only that the
  pre-registered family, and its nearby neighbours, is null on this corpus.

## Relationship to the programme

This is the **third** independent line of evidence that intraday directional
structure on this corpus is ~efficient (after C1's cost-defeat + cross-replication
failure). Notably it **clears the USD-artifact suspicion** (breadth passed) — the
problem is not collinearity this time, it is the **absence of forward
predictability** in the currency cross-section itself.

## Boundaries (unchanged)

No campaign created. No strategy approved (`approved: []`). No entry/exit logic, no
trading system, no front gate built, no train/validation/test. Paper/demo/live
remain blocked. No trading-API calls. **Definition not altered after results.**
Phase 8 records the next step (S3 vs financing-data prerequisite) and validation.
