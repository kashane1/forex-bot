# Cross-Universe Factor Shortlist

**Sprint:** `research-nonusd-cross-factor-discovery-planning-001` · Phase 5
**Type:** shortlist (≤5). Docs-only. No factor, no screen, no campaign, no
approval. **Nothing here is built or run.**
**Date:** 2026-05-30.

From the Phase-4 ranking, five families are carried forward. The selection logic:
take the **sanctioned replication** (settles the one open scientific question),
the **breadth-pure generator and its foundation** (the genuinely new territory),
one **economically-grounded RV** (the one prior-failure concept that crosses
legitimately reopen), and the **single most valuable regime overlay** (which the
others depend on). Filters (F07/F21) are folded into the families they enable
rather than shortlisted standalone, since a filter cannot create edge.

The five, in execution-priority order:

| Rank | ID | Family | One-line role |
|------|----|--------|--------------|
| 1 | **S1** | F24 — C1 replication on crosses | settle the residual-USD question on the one genuine factor |
| 2 | **S2** | F01 — Cross-implied currency-strength index | the new breadth-pure foundation |
| 3 | **S3** | F08 — Currency cross-sectional momentum | the canonical breadth style-factor, done right |
| 4 | **S4** | F15/F18 — Economically-motivated, half-life-matched cross RV | the legitimate C028 reopen |
| 5 | **S5** | F23 — Cross-currency correlation/vol regime gate | the overlay the breadth families require |

---

## S1 — Independent C1 replication on crosses (F24)

**Thesis.** C1 (fade simultaneous H4+H1+M15 bullish alignment → price reverts
down 30–60min) is the programme's one GENUINE factor: sign-universal on 7/7 USD
majors, pair-space sign independent of the USD leg. The unresolved question is
whether the *significant magnitude* (concentrated on EUR_USD + USD_JPY) is a real
multi-TF-confluence effect or a residual-USD-regime artifact. Non-collinear
crosses can answer this directly.

**Why it differs from prior work.** It is **replication, not re-tuning**: the
locked C1 definition and frozen thresholds are applied unchanged to 8 instruments
that share *no* USD leg. The majors could not answer this (all USD-collinear);
this is the explicitly-sanctioned single reuse of a closed lane and the *reason*
crosses were named as C1's reopen condition.

**Expected failure modes.** (a) C1 vanishes on crosses → it was a USD-regime
artifact (a clean, publishable negative). (b) C1 sign-replicates but is again
**cost-defeated** (likely — cross spreads are wider; even on majors C1 was
~0.65–0.73× spread). (c) Significance concentrates again on the JPY crosses,
re-raising the discovery-pair-selection caution. **A positive net-of-cost result
is not expected**; the value is scientific (settling the artifact question),
not a tradable.

**Expected data requirements.** None new — materialized cross H4M1/H1/M15 bars
(present), matched-null seeds, and the two-legged cost model. Cheapest family to
run.

**Expected front-gate requirements.** Frozen C1 thresholds pre-registered *before*
any cross number; matched-null + multiple-comparison over 8 pairs; **net-of-cost
via measured cross spreads** as the decisive gate; no per-cross re-tuning. Reuse
is replication only.

---

## S2 — Cross-implied currency-strength index (F01)

**Thesis.** Decompose the 15-instrument return matrix into a per-currency
strength vector (average-of-pairs or least-squares); a currency's strength
relative to the *whole field* (not just USD) is a cleaner state variable than any
single pair. Trade pairs whose realized move diverges from their legs' implied
strength, expressed through the cheapest linking instrument.

**Why it differs from prior work.** This is structurally impossible with
USD-only majors, where every strength estimate is USD-anchored and degenerate.
It directly removes the **USD-collinearity** that made C016 a USD bet and C031's
book "a structural USD bet." It is breadth in its purest form.

**Expected failure modes.** (a) The strength vector is dominated by the USD/EUR
liquidity axis and adds little over a single pair. (b) Divergence signals are
real but **sub-cost** once expressed through real (wider) cross spreads.
(c) Collinearity sneaks back in (EUR loads on 5 instruments) and overstates
breadth — mitigated by proper decomposition, but a live risk.

**Expected data requirements.** None new — return series from already-populated
M5/M15/H1 bars across all 15 instruments. Some new *analysis* code (a
decomposition utility) but no ingest.

**Expected front-gate requirements.** Pre-registered decomposition method and one
lookback/horizon (no best-of-N); cost-first evaluation choosing the cheapest
expressing instrument per signal; matched-null on the strength construction;
explicit collinearity diagnostic (variance explained per currency).

---

## S3 — Currency cross-sectional momentum (F08)

**Thesis.** Rank the 8 currencies by trailing strength (built on S2), go long
top-k / short bottom-k expressed through non-collinear instruments, rebalanced on
a pre-set cadence. The canonical FX cross-sectional style factor — but over
*currencies*, not USD-collinear pairs.

**Why it differs from prior work.** C016 ran "cross-sectional momentum" on 7
USD-legged majors, so its cross-section was a USD-strength bet with ~7 collinear
names → REJECT. S3 ranks genuine currencies via the S2 decomposition, the very
breadth C016 lacked. **It is explicitly NOT** "C016 with crosses added to the
rank" (a hidden re-tune fenced in Phase 3).

**Expected failure modes.** (a) Cost-defeated — wider cross spreads × periodic
rebalance turnover (the most likely outcome; C016's verdict on a wider venue).
(b) Best-of-(lookback, k, horizon) forking path if not pre-registered.
(c) Regime-dependent: momentum and breadth both collapse in risk-off when crosses
co-move — exactly why S5 (regime gate) is shortlisted alongside.

**Expected data requirements.** None new — depends on S2's strength vector.

**Expected front-gate requirements.** One pre-registered (lookback, k, horizon,
rebalance) tuple; turnover-aware **net-of-cost** with measured per-instrument
spreads; matched-null + multiple-comparison; risk-off stress slice; the S5 gate
as a *declared* overlay, not a post-hoc filter.

---

## S4 — Economically-motivated, half-life-matched cross RV (F15 + F18)

**Thesis.** Among crosses sharing a leg (the JPY-cross complex: EUR_JPY, GBP_JPY,
AUD_JPY, NZD_JPY) or pinned by a triangle (EUR_GBP vs EUR_USD/GBP_USD), a
hedge-ratio spread can be stationary for a *stated economic reason*; trade its
band excursions **only when the estimated half-life ≤ the intended hold**.

**Why it differs from prior work.** C028 (RV spread) was LIKELY_SELECTION_NOISE
because it searched USD-collinear combinations for the best-of-N and ignored the
half-life ≫ hold mismatch. S4 fixes both C028 failure modes: (i) spreads are
**economically motivated and pre-named** (shared leg / triangle closure), not
best-of-N mined; (ii) the **half-life-matched-hold** guard (the parked C028
variant) is built into the candidate definition. This is the legitimate reopen
of the RV concept that crosses enable.

**Expected failure modes.** (a) Two-leg (or three-leg for triangle) cost
hostility — C028's other wall; cross spreads are wider, so this is the primary
risk. (b) Cointegration that holds in-sample breaks in risk-off (JPY-cross
co-movement). (c) Half-life estimates unstable, re-creating the mismatch.

**Expected data requirements.** None new — M5/M15/H1 cross bars + a cointegration/
half-life utility (the C028 `relative_value_spread.py` module already exists and
is reusable).

**Expected front-gate requirements.** Pre-named spreads with written economic
rationale (no spread search); half-life ≤ hold as a *precondition*, not a fitted
parameter; **two-/three-leg measured-cost** gate; matched-null on the spread
construction; multiple-comparison across the small pre-named set only.

---

## S5 — Cross-currency correlation/vol regime gate (F23)

**Thesis.** The realized correlation (and vol dispersion) of the 8-cross complex
is itself a regime variable: when JPY/CHF crosses co-move strongly (risk-off),
breadth collapses and cross-sectional/RV signals degrade; when dispersion is high,
they are most separable. Use it as a **stand-down / sizing gate** on S2–S4.

**Why it differs from prior work.** It is not a generator and makes no directional
claim — it is the **overlay** the breadth families structurally require, and it
directly addresses the feasibility study's "independence is regime-dependent"
warning and Phase-3's "regime-dependent independence" trap. No prior analogue
because the cross complex did not exist to measure.

**Expected failure modes.** (a) Adds no value — the gate's on/off states don't
separate good from bad signal periods (then it is correctly dropped). (b)
Look-ahead if the correlation window is not strictly trailing. (c) Over-fitting
the gate threshold (mitigated: pre-register one threshold).

**Expected data requirements.** None new — rolling correlation/vol of populated
cross returns. Financing-free, intraday-computable, the cheapest family.

**Expected front-gate requirements.** Strictly trailing window, one
pre-registered threshold; evaluated as a *conditioner* of S2–S4 (does gating
improve net-of-cost vs ungated?), never as a standalone signal; matched-null on
the conditioning to rule out a spurious split.

---

## Shortlist coherence

The five are **one coherent programme, not five independent bets**: S2
(strength) is the foundation S3 (cross-sectional momentum) consumes; S5 (regime
gate) is the overlay S2–S4 require; S4 (RV) is the independent-leg complement;
and S1 (C1 replication) is the parallel scientific question that needs none of
them. **All five need zero new data** except the carry families deliberately left
off (F12–F14), which are prerequisite-blocked on financing ingest and therefore
belong to a *data* sprint, not a factor screen.

**None is endorsed for a screen here.** Phase 6 picks exactly one as the next
discovery target; Phase 7 writes the prompt that would open it (a discovery
sprint, never a campaign).
