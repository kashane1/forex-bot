# New Factor Families Enabled by Non-USD Crosses

**Sprint:** `research-nonusd-cross-factor-discovery-planning-001` · Phase 2
**Type:** research enumeration only. Docs-only. **No factor is built, no signal
is written, no screen is run, no campaign is created.** Each entry is a
*candidate family* with a falsifiable mechanism — not a strategy.
**Date:** 2026-05-30.

This phase enumerates **24 candidate factor families** that became *possible to
test* only once non-USD cross data existed (or are materially strengthened by
it). The focus is deliberately on families that **breadth** unlocks — multiple
non-collinear legs sharing currencies — because breadth is the only new data
lever the population sprint actually pulled (history, microstructure, and cost
walls are unchanged; see Phase 0).

Each family lists: **mechanism** (the falsifiable economic story), **legs/data
it needs**, and **why majors-only could not test it**. Cost/financing/novelty
scoring is deferred to Phase 4; rejection of the weak ones to Phase 3.

---

## Group I — Currency-strength & dispersion (Category E)

**F01 — Cross-implied currency-strength index.**
*Mechanism:* estimate a per-currency strength vector (e.g. average log-return
across all pairs containing that currency, or a least-squares decomposition of
the 15-instrument return matrix), then trade pairs whose realized move diverges
from the implied strength of their two legs. *Needs:* all 15 instruments'
returns; overlapping legs. *Majors-only:* every strength estimate is
USD-anchored and degenerate (one factor).

**F02 — Currency-strength dispersion timing.**
*Mechanism:* the cross-sectional spread of currency strengths (max−min, or std)
is a breadth/volatility-of-the-cross-section signal; trade only when dispersion
is high (signals more separable) and stand down when currencies move together.
*Needs:* the F01 strength vector over time. *Majors-only:* dispersion collapses
to "USD vs the field" — not a true cross-currency dispersion.

**F03 — Strongest-vs-weakest currency pairing.**
*Mechanism:* go long the strongest currency against the weakest, expressed
through the *tightest available* instrument linking them (cost-aware
instrument selection across majors+crosses). *Needs:* strength ranking + a
spread-cost map to pick the cheapest expressing instrument. *Majors-only:* the
only expressible pairings route through USD.

**F04 — Currency-strength mean-reversion (over-extension fade).**
*Mechanism:* a currency that has become extremely strong/weak vs the whole field
(not just vs USD) reverts; fade the extreme leg. *Needs:* F01 vector + extremity
percentile. *Majors-only:* "extreme vs USD" only — confounds the USD leg.

## Group II — Triangular / no-arbitrage consistency (Category F)

**F05 — Triangular drift-consistency.**
*Mechanism:* for a closed triangle (e.g. EUR_USD·USD_JPY·EUR_JPY) the implied
cross should track the traded cross; persistent *signed* deviations (not
instantaneous arb, which is latency-defeated) may predict which leg corrects.
*Needs:* three co-quoted instruments per triangle; 9+ triangles available.
*Majors-only:* impossible — no cross to close any triangle.

**F06 — Triangular residual reversion.**
*Mechanism:* the (tiny, cost-bound) triangular residual, smoothed, is a
stationary series; its excursions beyond a band mean-revert via the *cheapest*
leg. *Needs:* synchronized M1/M5 across the triangle + cost map. *Majors-only:*
no triangle exists.

**F07 — Implied-cross vs traded-cross basis as a confirmation filter.**
*Mechanism:* use the sign of (implied cross − traded cross) as a *filter* on an
independently-derived directional signal, not as a standalone signal. *Needs:*
triangle + a host signal. *Majors-only:* no implied cross.

## Group III — Cross-sectional momentum / value (Category D)

**F08 — Pure currency cross-sectional momentum.**
*Mechanism:* rank the 8 currencies by trailing strength (F01), long top-k /
short bottom-k expressed through non-collinear instruments, rebalanced weekly.
*Needs:* strength vector + instrument map. *Majors-only:* C016's "cross-section"
was a USD bet; crosses make it a genuine currency cross-section.

**F09 — Cross-sectional momentum with carry tilt.**
*Mechanism:* combine trailing momentum with the carry sign (high-yielder bias),
a classic FX style-factor blend, across the currency cross-section. *Needs:*
strength + carry estimate. *Majors-only:* carry leg absent.

**F10 — Cross-sectional reversal (short-horizon).**
*Mechanism:* at short horizons currencies that outperformed the field revert;
long recent losers / short recent winners across the cross-section. *Needs:*
strength vector. *Majors-only:* USD-collinear, underpowered.

**F11 — Momentum-of-crosses (instrument-level, not currency-level).**
*Mechanism:* rank the 8 *crosses themselves* by trailing return and trade the
spread between top/bottom crosses (instrument cross-section, agnostic to the
currency decomposition). *Needs:* the 8 cross return series. *Majors-only:* no
crosses to rank.

## Group IV — Carry / financing (Category G — gated on financing data)

**F12 — Classic two-leg carry (high-yield vs low-yield).**
*Mechanism:* hold long high-interest-rate currency vs low (AUD/NZD vs JPY/CHF)
through crosses; the carry accrues while spot risk is managed. *Needs:* **real
financing/swap rates** (not yet ingested) + the cross spot. *Majors-only:*
classic carry pairs (AUD_JPY, NZD_JPY) didn't exist.

**F13 — Carry-to-vol (risk-adjusted carry).**
*Mechanism:* scale carry exposure by inverse realized vol of the cross
(Koijen-style), down-weighting carry when crash risk (vol) is high. *Needs:*
financing + cross vol. *Majors-only:* no carry leg.

**F14 — Carry-crash / safe-haven hedge overlay.**
*Mechanism:* carry crosses (AUD_JPY, NZD_JPY) crash in risk-off; condition or
hedge carry exposure on a safe-haven stress signal (JPY/CHF strength surge).
*Needs:* financing + JPY/CHF basket. *Majors-only:* neither carry nor a
non-USD safe-haven basket existed.

## Group V — Relative-value / cointegration (Category H)

**F15 — Shared-leg spread reversion (JPY-cross complex).**
*Mechanism:* EUR_JPY, GBP_JPY, AUD_JPY, NZD_JPY all share the JPY leg; the
spread between two (after a hedge ratio) is dominated by the *non-JPY* legs and
may cointegrate. *Needs:* two JPY crosses + cointegration test. *Majors-only:*
only one JPY pair (USD_JPY).

**F16 — Triangle-closure cointegration (EUR_GBP vs EUR_USD/GBP_USD).**
*Mechanism:* EUR_GBP is pinned by EUR_USD/GBP_USD; a synthetic spread should be
stationary by construction — test whether its deviations mean-revert tradeably
net of three-leg cost. *Needs:* the triangle. *Majors-only:* EUR_GBP absent.

**F17 — Safe-haven pair cointegration (EUR_CHF vs USD_CHF complex).**
*Mechanism:* CHF crosses share safe-haven behaviour; EUR_CHF vs (EUR_USD,
USD_CHF) synthetic should track. *Needs:* CHF crosses. *Majors-only:* no CHF
cross.

**F18 — Half-life-matched RV (C028 fix on cross spreads).**
*Mechanism:* the parked C028 variant — only trade RV spreads whose estimated
half-life matches the intended hold — applied to *economically-motivated cross
spreads* rather than collinear USD combos. *Needs:* cross spreads + half-life
estimate. *Majors-only:* candidate spreads were USD-collinear (the C028 failure).

## Group VI — Lead-lag / leadership / confirmation (Category I)

**F19 — Shared-leg lead-lag (liquid pair leads its cross).**
*Mechanism:* the more liquid USD pair (EUR_USD) may lead the cross sharing its
base (EUR_JPY, EUR_GBP, EUR_AUD) at short horizons; trade the laggard toward the
leader. *Needs:* synchronized M1 across leader+laggard. *Majors-only:* only
USD-anchored lead-lag (part of the USD-bet critique).

**F20 — Risk-proxy leadership (AUD/NZD vs JPY/CHF as a risk clock).**
*Mechanism:* AUD_JPY / NZD_JPY are textbook risk-on barometers; their move may
lead or confirm directional setups in other crosses during risk transitions.
*Needs:* carry crosses + a host instrument. *Majors-only:* no carry barometer.

**F21 — Cross-pair confirmation filter (multi-pair agreement).**
*Mechanism:* require two non-collinear instruments sharing a leg to agree in
direction before taking a signal (a *filter*, not a generator), reducing
single-pair noise. *Needs:* ≥2 pairs sharing a leg. *Majors-only:* agreement is
trivially USD-driven.

## Group VII — Volatility / regime baskets (Category K-basket)

**F22 — Safe-haven vs risk vol-dispersion.**
*Mechanism:* the vol spread between safe-haven crosses (EUR_CHF, GBP_CHF) and
risk crosses (AUD_JPY, NZD_JPY) signals regime; condition exposure on it.
*Needs:* cross vol series grouped by character. *Majors-only:* can't form a
non-USD safe-haven vs risk grouping.

**F23 — Cross-currency correlation-regime conditioning.**
*Mechanism:* when JPY/CHF crosses co-move strongly (risk-off) "breadth"
collapses; use the realized correlation of the cross complex as a *stand-down /
regime* gate on any breadth strategy. *Needs:* rolling correlation of the 8
crosses. *Majors-only:* correlation collapses to "everything vs USD."

## Group VIII — Replication (Category J — the sanctioned reuse)

**F24 — Independent C1 replication on crosses (fresh pre-registered screen).**
*Mechanism:* re-screen the *locked* C1 definition (fade H4+H1+M15 bullish
alignment → reverts down 30–60min) on the 8 non-collinear crosses to settle
whether C1 is a genuine multi-TF-confluence effect or a residual-USD artifact.
**Replication, not re-tune** — frozen thresholds, no parameter search. *Needs:*
cross H4M1/H1/M15 bars (all materialized) + matched-null + cost model.
*Majors-only:* all 7 majors are USD-collinear, so the residual-USD question is
unanswerable there.

---

## Count & coverage

**24 candidate factor families** (F01–F24) across 8 groups, spanning all seven
cross-reopened research categories (D, E, F, G, H, I, K-basket) plus the
sanctioned replication (J). Every family names a falsifiable mechanism and the
specific non-collinear legs it requires — i.e. every one is a family that
*breadth* unlocks and majors-only structurally could not test.

**Honest caveats carried forward (to Phase 3/4):**
- Several families (F05–F07 triangular, F16 triangle-RV) are **three-leg**, so
  they multiply the cost wall — the binding constraint the whole programme died
  on. They are listed because they are *newly testable*, not because they are
  cheap.
- The carry group (F12–F14) is **gated on financing data that is not yet
  ingested** — the registry carry figures are estimates. These cannot be honestly
  screened until real swap rates exist.
- Replication F24 is the *one* reuse of a rejected lane and only as a fresh
  independent screen; it must never become a C1 re-tune.

No family here is endorsed. Phase 3 removes the ones likely to repeat known
failures; Phase 4 scores the survivors; Phase 5 shortlists ≤5.
