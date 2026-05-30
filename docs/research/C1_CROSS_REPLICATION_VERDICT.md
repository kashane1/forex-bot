# C1 Cross-Replication — Verdict (Phase 5)

**Sprint:** `research-c1-cross-replication-screen-001` · Phase 5
**Type:** verdict. The **frozen verdict map** (protocol §10) is applied
mechanically to the Phase 2–4 evidence. No interpretation latitude beyond that
table; the factor definition was never altered after results were observed.
**Date:** 2026-05-30.

---

## Verdict

# `REPLICATION_FAILED`

The C1 factor — sign-universal, null-clearing, year- and spec-robust on the seven
USD majors — **does not replicate on the non-USD crosses.** On the required
cross universe the effect is sign-inconsistent, indistinguishable from the
session-matched null, and unstable across years, sessions, volatility, and
one-knob perturbations. The only convincing single-pair signal (GBP_CHF,
optional) is period- and off-hours-concentrated — a regime/microstructure
artifact consistent with multiple-comparison noise, not the C1 mechanism.

---

## How the frozen criteria resolve

The protocol's `REPLICATION_FAILED` triggers if **any** dominant pattern holds.
**All three** hold here:

### 1. Inconsistent sign ✓ (triggered)
- Majors: C1_long 60-min negative **7/7**. Crosses: **2/4 negative on the
  required set** (EUR_JPY +0.162, AUD_JPY +0.045 are positive), and the negatives
  (EUR_GBP −0.059, GBP_JPY −0.071) are ≈ zero.
- Sign flips **year to year** on every required pair (Phase 4 §2) and **across
  sessions** (§3). The one required pair clearing the null at 30 min (EUR_JPY)
  **reverses sign by 60 min** — the opposite of the majors' 30→60 strengthening.

### 2. Indistinguishable from null ✓ (triggered)
- **Zero required crosses** clear |matched-Z| ≥ 2 at 60 min. The single required
  30-min hit (EUR_JPY −2.26) does not persist.
- Observed C1 means sit **inside one matched-null SD** on every required pair at
  60 min. C1 events earn what a **session-matched random event** earns.
- Over 16 cells (8 pairs × 2 horizons), 1–2 isolated |Z|≈2 hits are the **null
  expectation** by chance; exactly 1 (GBP_CHF-60) appears.

### 3. Inconsistent / single-pair behavior ✓ (triggered)
- The only 60-min null-clearing pair is **GBP_CHF — a single optional cross.** By
  the pre-registered multiple-comparison rule (§6) a lone clearing pair is
  selection noise, not replication.
- GBP_CHF's effect is **period-concentrated (2022–23 risk-off), off-hours/
  wide-spread, single-pair** (Phase 4 §2–§4) — a regime/microstructure fingerprint,
  not the C1 confluence mechanism.

### Success criteria — not met
`REPLICATION_SUCCESS` required majority-negative 60-min sign **and** |mZ|≥2 on
**multiple** pairs **and** magnitude in the majors' band. None holds: required
sign is 2/4, multiple-pair null-clearing fails (0 required, 1 optional), and
magnitudes are **~10× smaller** than the majors (|mean60| ≤ 0.16 vs ~1.1).

### Why not PARTIAL_REPLICATION
`PARTIAL` would require sign **mostly stable** with null-separation on **some**
pairs, or merely weaker magnitude. The sign is **not** mostly stable on the
required set (flips within-pair across years/sessions, and 2/4 flip outright at
60 min), and the null-separation that exists is a **single optional pair** the
frozen rule classifies as noise — plus that pair fails the robustness slices.
A non-persistent 30-min tilt on the JPY-quote crosses that **reverses** by 60 min
and dissolves under year/session/spec slicing is not "partial replication" — it
is the absence of the effect with residual noise. The evidence is not *mixed*;
it is *consistently negative* for replication. The frozen map therefore resolves
to `REPLICATION_FAILED`, not `PARTIAL`.

---

## What this verdict does and does not assert

**Asserts:** the *magnitude* of the C1 effect observed on EUR_USD/USD_JPY **does
not generalize** to non-collinear, non-USD instruments. Combined with the prior
majors finding that C1's pair-space sign does not track the USD leg, the most
consistent reading is that C1's significant magnitude was **specific to the
USD-major discovery pairs / USD-regime structure**, not a universal multi-TF
confluence law. The crosses answered the residual-USD question: **the effect that
mattered did not survive outside the USD majors.**

**Does NOT assert:**
- **Anything about tradability.** Tradability was out of scope and not evaluated;
  no net-of-cost gate entered this verdict. (C1 was already cost-defeated on the
  cheaper majors; nothing here changes or revisits that.)
- **That C1 was fabricated or mis-measured on the majors.** The majors result
  reproduced exactly (Phase 0 / prior integrity checks). C1 is a real, if small,
  *USD-major* effect; it simply does not replicate out-of-universe.
- **That the crosses are useless.** They did their job as an independent
  replication test — a clean negative is a valid, informative scientific result.

---

## Mapping to the planning sprint's pre-stated branches

The Phase-6 direction doc pre-stated three branches. This verdict lands on
**`C1_ARTIFACT`** ("C1's significant magnitude was a USD-regime artifact; the
M1/HTF confluence lane stays closed; pivot priors toward S2 or data
prerequisites"). It is **not** `C1_GENUINE_BUT_COST_DEFEATED` (which would have
required genuine replication that then failed on cost) and **not**
`C1_GENUINE_AND_COST_SURVIVING`.

## Boundaries (unchanged)

No campaign created. No strategy approved (`approved: []`). No entry/exit logic,
no trading system, no train/validation/test. Paper/demo/live remain blocked. No
trading-API calls. Phase 6 draws implications; Phase 7 recommends the next step
(S2). **The C1 definition was not altered after results were observed.**
