# Carry Factor-Validation — Future-Study Design (Phase 5)

**Sprint:** `research-financing-rate-data-ingestion-001` · Phase 5
**Type:** **DESIGN ONLY — the study is NOT executed here.** This is a draft
pre-registration for a *future* sprint, not a frozen protocol to run now. No factor
study, no nulls, no verdict, no signal. Docs-only.
**Date:** 2026-05-31.

This designs how carry *would* be validated, applying the lessons from C1
(replication failure), S2 (real-but-non-predictive), and S4 (real-but-within-cost-
band). It deliberately stops at design.

---

## 1. Frozen hypotheses (to be pre-registered in the future sprint)

- **H1 (carry premium exists):** instruments/currencies with higher carry
  differential earn higher *spot-adjusted* forward returns than lower-carry ones —
  i.e. the carry is **not** fully offset by anticipated spot depreciation (a test of
  the uncovered-interest-parity failure that underlies the carry premium).
- **H2 (cross-sectional carry):** ranking the 8 currencies (or 15 instruments) by
  carry and going long top / short bottom earns a positive **gross** spread beyond a
  matched null.
- **H3 (carry-crash asymmetry):** carry returns are negatively skewed / crash in
  risk-off (the JPY/CHF-funding unwind) — a *risk* property to characterize, not an
  edge.
- **Direction is an empirical output**, not assumed; "carry pays" must be measured,
  never presumed (the hard rule).

## 2. Universe & data

- Carry leg: the **monthly interbank carry differential** built here (the economic
  signal). Spot leg: existing M5/H1/H4/D1 cross + major bars.
- Carry pairs of primary interest: **AUD_JPY, NZD_JPY, EUR_JPY** (genuine high-yield
  vs funding) + the full 15 for the cross-section.

## 3. Possible response windows

Carry is a **slow, monthly-information** signal, so the response grid must respect
that — **NOT** intraday:
- **Holding horizons:** 1, 3, 6, 12 **months** (carry accrues over holding periods;
  monthly rebalance).
- Spot return measured over the holding horizon; **carry earned** approximated from
  the differential × horizon (economic) — and, in the *tradability* extension, from
  **real OANDA financing** (separate ingest).
- Intraday horizons are explicitly **out of scope** for carry (a category error —
  the rate signal has monthly cadence).

## 4. Possible nulls

- **Unconditional baseline:** mean forward return ignoring carry rank.
- **Randomized carry ranks:** shuffle the carry→instrument assignment per rebalance.
- **Shuffled-timestamp carry:** detach the carry signal from its forward window.
- **Matched null:** regime/volatility-matched random selection.
- **Spot-only control:** does carry add over a no-carry momentum/value baseline?
- Decisive statistic: matched-Z on the carry-sorted spread, multiple-comparison
  aware across horizons.

## 5. Cost / financing considerations (the binding gate)

- **The interbank differential is the SIGNAL, not the COST.** A carry study that
  claims tradability **must** use **real OANDA broker financing** (interbank +
  markup) — the C031 reality (financing ≈4× spread). That data is a **separate,
  later, user-authorized ingest** and is the **decisive gate**.
- **Pre-registered cost outcome label:** a positive *gross* carry premium that is
  **negative net of real financing** is **`FINANCING_DEFEATED`**, not a factor —
  exactly the C031 failure mode, to be guarded against explicitly.
- Crosses are wider-spread than majors; rebalancing cost compounds the financing
  wall. The gate must charge round-trip spread + real financing at a stress multiple.

## 6. Potential failure modes (pre-identified)

- **Financing-defeated** (most likely on this retail venue, per C031) — gross carry
  premium eaten by broker financing + spread.
- **Underpowered slow signal** — ~5y spot window = few independent monthly
  rebalances; the carry premium needs long history to separate from noise (the deep
  rate history helps the *signal* but the *spot* window bounds the test). Forking-
  path risk if horizons/rebalances are mined.
- **Carry-crash regime dependence** — a premium that exists in calm and crashes in
  risk-off (2008/2020-style) may be absent or reversed in a 5y window dominated by
  the hiking cycle.
- **Collinearity to a USD/rate-level bet** — like C016/C031, the carry book may
  collapse to "a structural USD or risk-on bet"; a proper currency-cross-sectional
  construction (not USD-anchored) is required (the S2 breadth lesson).
- **Monthly-cadence overfit** — treating monthly rates as if higher-frequency.

## 7. Lessons applied from C1 / S2 / S4

- **From C1 (replication failure):** do not trust an effect on a few pairs; require
  **breadth + an independent/out-of-sample check**, and never re-tune to rescue a
  result. A carry premium must hold across the cross-section, not one carry pair.
- **From S2 (real but non-predictive):** *existence of a signal ≠ predictive power.*
  Carry differentials clearly **exist and vary** (Phase 3/4) — but the study must
  test **forward predictability against the nulls**, not assume the dispersion pays.
- **From S4 (real but within cost band):** a *genuine gross* effect can still be
  sub-cost. The **net-of-real-financing** gate is decisive; report the gross effect
  honestly but verdict on net, with the no-edge-before-validation rule.
- **From all three:** pre-register before touching forward returns; matched-null +
  multiple-comparison mandatory; tradability is a *separate, later* gate; one
  frozen spec, no best-of-N.

## 8. Proposed verdict map (for the future sprint, draft)

| Verdict | Condition |
|---|---|
| `CARRY_FRONT_GATE_CANDIDATE` | gross premium clears all nulls, breadth-robust, **and survives net of real OANDA financing** at a stress multiple |
| `CARRY_REAL_BUT_WEAK` | genuine null-separated gross premium but narrow / sub-cost-band / regime-fragile |
| `FINANCING_DEFEATED` | gross premium exists but **negative net of real financing** |
| `CARRY_REJECTED` | no premium beyond nulls / sign-incoherent / collapses to a USD bet |

## 9. Explicit non-execution

This document **designs** the study. It runs **nothing** — no carry return, no null,
no verdict. The future sprint must (a) ingest real OANDA financing (user-authorized),
(b) freeze this design into a protocol, and (c) execute it as a pre-registered
factor-validation — **not** a campaign. Carry remains an **un-validated data asset**
until then.
