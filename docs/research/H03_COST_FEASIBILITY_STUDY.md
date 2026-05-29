# H03 thin-move fade — cost feasibility study (Phase 4)

**Sprint:** `research-non-time-bar-thin-move-frontgate-001` · Phase 4
**Type:** cost-adjusted significance of the conditional move. No PnL, no approval.
**Artifacts:** `research/h03_thin_move_frontgate/cost_study.json`.

> Cost model (the C029 model): round-trip ≈ per-pair mean spread + 2 × 0.2-pip
> slippage. Because thin bars carry *wider* spreads (Phase 2 §3.3), the low-bucket
> cost is computed on the **low-bucket's own spread**, not the pair average — the
> honest cost a thin-move trade would actually pay.

---

## 1. Effect magnitude vs round-trip cost

| pair | low-bucket RT cost | low fade h1/h2/h3 | beats cost? | ultra-thin fade h1/h2/h3 | beats cost? |
|---|--:|---|---|---|---|
| EUR_USD | **2.06** | +1.75 / +2.33 / +3.97 | h2✓ h3✓ | −1.48 / +0.93 / +5.34 | h3✓ |
| GBP_USD | **2.84** | +0.46 / +1.26 / +0.51 | none | +0.04 / +0.54 / −0.72 | none |
| USD_JPY | **2.90** | +0.21 / +0.57 / −0.68 | none | +1.11 / +2.37 / +0.70 | none |

## 2. Spread impact — thin bars are the *expensive* bars

Mean spread at completion is **higher** in the low-participation bucket on every pair
(Phase 2 §3.3): EUR_USD 1.66 vs 1.60, GBP_USD 2.44 vs 2.15, USD_JPY 2.50 vs 1.90. The
low-bucket round-trip cost (2.06 / 2.84 / 2.90 pips) is therefore *above* the pair
average. The thin-move cell is structurally the **least** cost-feasible cell to trade —
the opposite of what a tradeable edge needs.

## 3. Cost-adjusted significance

- **EUR_USD** is the **only** pair whose low-participation fade exceeds its own
  round-trip cost, and only at **h2 (+2.33 > 2.06)** and **h3 (+3.97 > 2.06)** — never at
  h1. The ultra-thin tail beats cost only at h3 (+5.34) and is **continuation** (−1.48,
  cost-defeated and wrong-signed) at h1.
- **GBP_USD** and **USD_JPY** low-bucket fades **never** exceed cost at any horizon. The
  USD_JPY low bucket is actually **negative** at h3 (−0.68); its only above-cost cells
  are the *medium* and *ultra-thin* buckets at h2 — not a thin-move-fade pattern, and not
  null-surviving (Phase 5).

So cost survival is a **single-pair (EUR_USD), longer-horizon-only** phenomenon. The
fade also *grows* with horizon on EUR_USD (1.75 → 2.33 → 3.97) while the reversion rate
stays ≈ 0.50 — the signature of a few large reverting moves dominating the mean, i.e.
**fat-tailed drift, not a consistent fade edge** that a stop-bounded trade could harvest.

## 4. Session effects

The low-participation bucket over-concentrates in thin-liquidity windows — USD_JPY in
**Tokyo (372 bars) and rollover_late (99)** — where spreads are widest and (for holds
spanning 17:00 NY) financing applies. Restricting to liquid sessions would shrink the
already-marginal low-bucket sample and remove most USD_JPY thin bars, not rescue the
effect. Conversely the EUR_USD low bucket sits mostly in london / london_ny_overlap, so
its (single-pair) cost survival is not a session artefact — but it is still single-pair
and null-internal (Phase 5).

## 5. Read

The hypothesised thin-move fade **does not clear a realistic, thin-bar-specific cost
floor on ≥ 2 of 3 pairs**. It clears cost only on EUR_USD, only at h2/h3, only as
fat-tailed drift, against a *wider* spread, in a cell that is collinear with the
already-failed H16 overshoot effect. By the pre-registered FAIL criterion §7.3
("conditional move below cost at all tradeable horizons … esp. if thin bars carry wider
spreads"), the cost gate is **failed** for GBP_USD and USD_JPY and **single-pair-only**
for EUR_USD.
