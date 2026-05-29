# Non-time-bar final shortlist

**Sprint:** `research-external-non-time-bar-thesis-discovery-001` · Phase 6
**Type:** final shortlist (≤ 5). No code, no backtests, **no performance claims**.

> Five hypotheses, ranked. Three are standalone, falsifiable signals (H16, H03, H05);
> one is a cost-state **conditioning layer** (H12); one (H01) is **deferred** on new
> evidence. None is approved; each must pass the full front gate before any campaign.

---

## ⚠️ Update since Phase 5 — new cross-branch evidence (CAMPAIGN_031)

After Phase 5 was committed, a **parallel research sprint** screened a **vol-managed
time-series-momentum** book (reserved as CAMPAIGN_031) on this same corpus and reached
`COST_FINANCING_DEFEATED + WITHIN_NULL → DOES_NOT_EARN_A_SCAFFOLD`. Its decisive
findings (artifacts live on a separate, still-unmerged branch — cross-link when merged):

1. **TSMOM direction on these 7 USD-legged majors is `WITHIN_NULL`** (pre-cost Sharpe
   modest; net negative; naive variant beats the managed config → selection-fragile).
2. **The book is a structural USD bet** — all available pairs are USD-legged; no crosses
   → no real breadth; a slow signal is underpowered on 7 instruments.
3. **Overnight financing ≈ 4× the spread cost** for multi-day holds — a cost channel the
   non-time-bar feasibility study (spread + slippage only) **did not model**.

**Consequences for this shortlist:**
- **H01 (dollar-bar TSMOM)** is **demoted to DEFERRED.** Re-testing time-series momentum
  on a different *clock* when the underlying directional effect is already `WITHIN_NULL`
  on this exact data risks being a **re-tune of a freshly-rejected idea** — the cardinal
  anti-pattern. It should not be pursued until C031's own revival criteria are met
  (≥ 10–15y history, non-USD crosses, an explicit financing model).
- A new hard screen applies to every candidate: **financing cost.** Any idea that can
  **hold across the 17:00 NY rollover** inherits the ≈4× financing penalty. This
  **strongly favors short-horizon / intraday ideas that close within a session.**

The ranking below reflects this update; it supersedes the Phase-5 ordering for H01.

---

## #1 — H16 · Overshoot-exhaustion fade

- **Detailed thesis.** The feasibility tooling already computes `overshoot_pips` (how far
  price travelled *beyond* the bar threshold in the completing candle). Test whether
  **unusually large overshoot** — a violent single-candle completion — predicts
  short-horizon **reversion** (exhaustion) over the next bar(s), on a cost-feasible bar
  size, closing intraday.
- **Why it survived & is now #1.** **Lowest implementation cost** (metric exists),
  clearly falsifiable, **intraday → financing-free**, and **not pre-empted by any prior
  rejection**: it is neither directional persistence (C031/C025/C029) nor price-level
  reversion (C008/C027) — it conditions on **completion geometry**.
- **Why it differs from prior campaigns.** Orthogonal signal (bar shape/overshoot), not
  price level, channel, or trend; never tested here.
- **Expected failure modes (honest).** (a) Large overshoot may equally signal
  **continuation** (momentum ignition) — sign unknown a priori; (b) overshoot
  concentrates in **jumps/news** where slippage is worst; (c) the effect is likely small
  and may not clear even the lifted (wide-threshold) cost floor.
- **Required infrastructure.** Existing bar builders + overshoot metric (exist) + a
  forward-return harness; the front-gate lab.
- **Front gate first?** **Yes** — G1/G2 matched null (beat a geometry-matched null
  post-cost), G3 cost-feasibility, G5 ≥ 2 pairs.

## #2 — H03 · Thin-move fade (price-travel ÷ volume disagreement)

- **Detailed thesis.** When a range/volatility bar completes its travel on **unusually
  low tick-volume** (a "thin" move), test short-horizon **reversion**; contrast with
  high-volume completions. The signal is **travel-per-unit-volume**, not travel itself;
  intraday exit (financing-free).
- **Why it survived.** Clean microstructure intuition (low-participation moves retrace)
  that **combines both clocks**; genuinely novel here; cheap; non-directional-persistence
  so **not pre-empted by C031**.
- **Why it differs.** No prior campaign used **volume as a move-quality filter**; not a
  breakout, not price-level reversion.
- **Expected failure modes.** (a) FX tick-volume is a **proxy** — "thin" may be noise;
  (b) reversion may be a bid-ask-bounce artefact; (c) too small vs cost.
- **Required infrastructure.** Range/volatility bars (exist) + per-bar tick-volume + the
  disagreement metric; front gate.
- **Front gate first?** **Yes** — matched null must hold the move fixed so the *volume*
  conditioning is what's tested (G4).

## #3 — H05 · Symmetric volatility-scaled CUSUM event drift

- **Detailed thesis.** Sample events with a **symmetric, vol-scaled CUSUM filter**
  (fire+reset when |cumulative signed deviation| crosses k·σ). Test **post-event drift**
  over the next few events on a cost-feasible size.
- **Why it survived.** A documented López de Prado construct the repo has **never built**
  (the `abs_close` bar is a one-sided, fixed-threshold cousin); regime-adaptive sampling.
- **Why it differs.** Vol-scaled + symmetric + event-reset, unlike fixed-pip bars or any
  time-bar family.
- **Expected failure modes.** (a) Post-event drift may be **≈ null** at tradeable horizons
  (most likely, given repo history); (b) **financing risk if events span the rollover** —
  must enforce intraday exit or model financing; (c) the vol-estimate look-back is a
  forking-path risk; (d) may collapse onto an existing volatility bar (verify it samples
  differently).
- **Required infrastructure.** A CUSUM event-bar builder + realized-vol estimate; front
  gate.
- **Front gate first?** **Yes.**

## #4 — H12 · Spread-state (liquidity-regime) conditioning layer *(overlay, not a standalone entry)*

- **Detailed thesis.** Restrict any primary signal to act only when the **current spread
  is in its low/liquid regime** (per pair/session), structurally excluding the
  fat-tailed rollover window (which is *also* where financing is charged). 
- **Why it survived.** Grounded in **our own** feasibility evidence; **lowest
  cost-sensitivity and overfit risk**; directly lifts the cost/risk ceiling that killed
  C029; and excluding rollover **also dodges the C031 financing channel**.
- **Why it differs.** A **cost-state filter**, not a directional bet; complementary to
  any rejected family.
- **Expected failure modes.** (a) A filter **cannot create edge**, only protect it — if
  the base signal is null, H12 changes nothing; (b) tight gating can shrink the sample
  below evidential thresholds.
- **Required infrastructure.** Per-bar spread from M1 bid/ask (exists) + a regime
  threshold; plugs into the front gate as a **G4 filter-ablation** test.
- **Front gate first?** **Yes — as a filter on a primary signal**, never alone.

## #5 — H01 · Dollar-bar trend persistence (TSMOM in event time) — **DEFERRED**

- **Status.** **Deferred, do not front-gate now.** It was Phase-5's #1, but the
  CAMPAIGN_031 evidence above shows TSMOM direction is `WITHIN_NULL` and
  financing-defeated on this corpus, and the book is a structural USD bet with no
  breadth. Re-testing it on a dollar-bar clock would be a re-tune of a just-rejected
  idea (anti-pattern §3) and, at wide dollar-bar sizes that span days, would inherit the
  financing penalty.
- **Reopen condition.** Only after C031's revival criteria are satisfied (≥ 10–15y
  history, **non-USD crosses** for real breadth, an explicit **financing model**) — at
  which point the *event-time* framing becomes a genuinely fresh question rather than a
  re-tune.

---

## How the shortlist would be combined

The intended shape of any *future* (still front-gated, not-yet-a-campaign) candidate is
**one short-horizon, intraday primary signal (H16 ▸ H03 ▸ H05) on a cost-feasible
non-time-bar clock, conditioned by the H12 spread-state filter, closing before the NY
rollover to avoid financing**, screened on ≥ 2 pairs. The recommended **first**
front-gate screen is **H16** (cheapest, most distinct, financing-free), with **H03** as
the immediate fallback.

## What would make the whole shortlist fail (an acceptable outcome)

The accumulated repo evidence is now sobering: breakout (C015/C017/C025/C029), pullback
(C020–C023), reversion (C008/C027), cross-sectional momentum (C016), **time-series
momentum (C031)**, and relative-value (C028) have **all** been rejected or found
within-null on this 7-major corpus. If the short-horizon microstructure signals here
also fail their **structure-matched nulls post-cost** on ≥ 2 pairs, the honest
conclusion is that non-time bars give a better *clock* but **no edge** in spot FX on the
data we have — consistent with Phase 3's finding that no public out-of-sample FX
non-time-bar trading edge exists. **A null result is a successful sprint outcome.**
