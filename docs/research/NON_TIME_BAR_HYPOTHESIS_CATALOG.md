# Non-time-bar hypothesis catalog

**Sprint:** `research-external-non-time-bar-thesis-discovery-001` · Phase 4
**Type:** hypothesis generation. No code, no backtests, **no performance claims**.

> 24 candidate hypotheses. Each is checked against the Phase-0 anti-patterns
> (§3: not a C029 retune, not a threshold tweak, not "same strategy slower/bigger",
> not a known rejected family) and the data reality (§4: M1 OHLCV + bid/ask +
> tick-count volume; no ticks/signed-flow/L2). "Why it might work" is a *hypothesis*,
> never an assertion of returns.
>
> **Scores (1–5):** *novelty* = distance from prior repo work + public commodity ideas;
> *fit* = how well current data/infra support it. **Overfit risk** = low/med/high.
> **Infra** = can it be built on existing infra? yes / partial / no.

Legend for the "anchor" column maps each idea to a Phase-1/2/3 external anchor:
`ACT` activity-clock sampling · `CUSUM` event sampling · `TSMOM` time-series momentum
· `VOLCL` volatility clustering/seasonality · `MICRO` microstructure/flow proxy ·
`XPAIR` cross-pair RV commonality · `DUR` conditional duration (ACD) · `SESS` session
structure · `SIZE` vol-scaled sizing.

---

## A. Activity-clock (dollar / tick-volume) bar hypotheses

### H01 — Dollar-bar trend persistence (TSMOM in event time)
- **Anchor:** TSMOM + ACT. **Desc:** build dollar bars (mid × tick-volume); test
  whether the sign of cumulative return over the last N dollar bars predicts the next
  dollar bar's return, sized inversely to realized vol.
- **Why it might work:** TSMOM is the most externally-replicated systematic effect;
  sampling in equal-information (dollar) time may sharpen the persistence signal vs
  calendar time, and partly auto-normalises for activity.
- **Distinct?** Yes — not a breakout (C029) and not a time-clock slowdown (C026); it is
  persistence-of-sign in activity time.
- **Data:** M1 mid + tick-volume. **Complexity:** med. **Novelty 4 · Fit 4 · Overfit
  med · Infra partial** (need a dollar-bar builder; range/vol builders exist as a
  template).

### H02 — Tick-volume "dollar bar" vs time-bar activity-surprise
- **Anchor:** ACT + VOLCL. **Desc:** measure how many dollar bars form per fixed clock
  window (activity surprise); test short-horizon behaviour conditional on
  activity-surge vs activity-drought.
- **Why:** activity bursts mark information arrival; behaviour (continuation vs
  reversion) may differ by regime.
- **Distinct?** Yes — a *conditioning* signal on the activity clock, untested here.
- **Data:** M1 + tick-volume. **Complexity:** med. **Novelty 3 · Fit 4 · Overfit med ·
  Infra partial.**

### H03 — Thin-move fade (price-travel ÷ volume disagreement)
- **Anchor:** ACT + MICRO. **Desc:** when a large price *travel* (range-bar completion)
  occurs on unusually *low* tick-volume (a "thin" move), test short-horizon **reversion**;
  contrast with high-volume travels (continuation).
- **Why:** thin, low-participation moves are more likely liquidity artefacts that
  retrace — a microstructure intuition combining the two clocks.
- **Distinct?** Yes — uses *both* range and volume clocks jointly; novel combination.
- **Data:** M1 + tick-volume. **Complexity:** med. **Novelty 5 · Fit 4 · Overfit med ·
  Infra partial.**

### H04 — Dollar-bar realized-variance ratio regime
- **Anchor:** ACT + VOLCL. **Desc:** ratio of realized variance measured in dollar-bar
  time vs clock time as a regime label; use only as a **gate** for a separate signal.
- **Why:** divergence between activity time and clock time flags regime shifts.
- **Distinct?** Yes. **Data:** M1 + tick-volume. **Complexity:** med. **Novelty 3 ·
  Fit 3 · Overfit med · Infra partial.**

## B. CUSUM / event-bar hypotheses

### H05 — Symmetric vol-scaled CUSUM event drift
- **Anchor:** CUSUM. **Desc:** sample events with a symmetric CUSUM filter (threshold ∝
  local realized vol); test post-event continuation/reversion over the next few events.
- **Why:** CUSUM samples *real* vol-scaled moves and resets, unlike the repo's one-sided
  `abs_close` bar; post-event drift is a classic event-study question.
- **Distinct?** Yes — symmetric, vol-scaled, event-reset; not the fixed abs_close bar.
- **Data:** M1 OHLC + vol estimate. **Complexity:** med. **Novelty 4 · Fit 4 · Overfit
  med · Infra partial** (abs_close bar is a starting template).

### H06 — CUSUM event clustering ("event storm") conditioning
- **Anchor:** CUSUM + VOLCL. **Desc:** when CUSUM events arrive in rapid succession
  (clustered), label an "event storm" regime; condition behaviour on storm vs calm.
- **Why:** vol/events cluster; behaviour likely differs inside storms.
- **Distinct?** Yes. **Data:** M1 OHLC. **Complexity:** med. **Novelty 3 · Fit 4 ·
  Overfit med · Infra partial.**

### H07 — CUSUM threshold asymmetry (up vs down) as skew signal
- **Anchor:** CUSUM + MICRO. **Desc:** track the relative frequency/size of up- vs
  down-CUSUM events as a running directional-pressure/skew estimate.
- **Why:** asymmetric event arrival may proxy directional pressure without signed flow.
- **Distinct?** Yes. **Data:** M1 OHLC. **Complexity:** med. **Novelty 3 · Fit 3 ·
  Overfit high · Infra partial.**

## C. Conditional-duration (time-between-bars) hypotheses

### H08 — Bar-duration clustering (ACD-style) regime gate
- **Anchor:** DUR + VOLCL. **Desc:** model the *duration* between non-time-bar
  completions (Engle–Russell Autoregressive Conditional Duration is the external
  anchor); short durations cluster; use the duration regime as a conditioning filter.
- **Why:** ACD is a documented property of event arrival; duration ≈ inverse activity,
  another lens on vol clustering.
- **Distinct?** Yes — duration as a *feature* is untested here.
- **Data:** M1 + any bar series. **Complexity:** med. **Novelty 4 · Fit 4 · Overfit
  med · Infra partial.**

### H09 — Duration-shock continuation
- **Anchor:** DUR. **Desc:** a sudden collapse in bar duration (activity shock) — test
  whether the move that triggered it continues over the next few bars.
- **Why:** activity shocks often accompany information arrival/trend initiation.
- **Distinct?** Yes. **Data:** M1 + bars. **Complexity:** med. **Novelty 3 · Fit 4 ·
  Overfit med · Infra partial.**

## D. Microstructure / flow-proxy hypotheses (data-risk flagged)

### H10 — BVC-proxy imbalance bars + post-bar drift
- **Anchor:** MICRO. **Desc:** approximate signed flow per M1 with **Bulk Volume
  Classification** (vol-scaled price change), accumulate signed tick-volume, sample a
  bar at an imbalance threshold; test post-bar drift.
- **Why:** information-driven bars fire early on informed flow; even a proxy may carry
  some of that.
- **Distinct?** Yes — but **proxy quality is a first-class risk** (BVC mislabels extreme
  moves; FX volume is itself a proxy).
- **Data:** M1 + tick-volume. **Complexity:** high. **Novelty 4 · Fit 2 · Overfit high
  · Infra no** (needs a BVC layer + imbalance-bar builder).

### H11 — Close-location-in-range (CLV) micro-pressure
- **Anchor:** MICRO. **Desc:** use where each M1 closes within its own bid-ask/OHLC
  range as a buying/selling-pressure proxy; accumulate across a bar.
- **Why:** persistent close-near-high/low is a weak pressure proxy not needing volume.
- **Distinct?** Yes. **Data:** M1 OHLC + bid/ask. **Complexity:** med. **Novelty 3 ·
  Fit 3 · Overfit high · Infra partial.**

### H12 — Spread-state (liquidity-regime) conditioning filter
- **Anchor:** MICRO + SESS. **Desc:** turn the feasibility study's per-session spread
  finding into a rule: only act when the current spread is in its **low/liquid** regime;
  structurally exclude fat-tailed rollover.
- **Why:** our own data shows cost is session-dependent; trading only in low-spread
  states directly lifts the cost/risk ceiling.
- **Distinct?** Yes — a cost-state *filter*, complementary to any signal; grounded in
  our own evidence.
- **Data:** M1 bid/ask + sessions. **Complexity:** low. **Novelty 3 · Fit 5 · Overfit
  low · Infra yes.**

## E. Cross-pair / relative hypotheses

### H13 — Cross-pair activity lead-lag (event-time)
- **Anchor:** XPAIR + ACT. **Desc:** when one major's dollar-bar activity surges, test
  whether correlated majors show short-horizon follow-through in **event time**.
- **Why:** intraday RV commonality across pairs is strong/stable; activity may lead
  price in laggards.
- **Distinct?** Yes — *activity* lead-lag, **not** the price-spread cointegration
  reversion C028 already screened out.
- **Data:** M1 × 7 pairs + tick-volume. **Complexity:** high. **Novelty 4 · Fit 3 ·
  Overfit med · Infra partial.**

### H14 — Common-vol-factor regime gate
- **Anchor:** XPAIR + VOLCL. **Desc:** estimate a common intraday realized-vol factor
  across majors; use deviations from it as a regime filter for a separate signal.
- **Why:** commonality is documented; idiosyncratic-vol states may behave differently.
- **Distinct?** Yes. **Data:** M1 × pairs. **Complexity:** high. **Novelty 3 · Fit 3 ·
  Overfit med · Infra partial.**

### H15 — USD-bloc activity breadth
- **Anchor:** XPAIR. **Desc:** breadth of simultaneous activity across USD pairs
  (how many fire a CUSUM/dollar bar together) as a USD-wide impulse indicator.
- **Why:** synchronized activity may mark USD-driven macro impulses.
- **Distinct?** Yes. **Data:** M1 × pairs. **Complexity:** high. **Novelty 3 · Fit 3 ·
  Overfit med · Infra partial.**

## F. Geometry-of-bar hypotheses (reuse feasibility geometry)

### H16 — Overshoot-exhaustion fade
- **Anchor:** VOLCL + MICRO. **Desc:** the feasibility study already computes
  `overshoot_pips` (travel beyond the threshold at completion); test whether unusually
  large overshoot signals short-horizon **reversion** (exhaustion).
- **Why:** large overshoot = a violent single-candle move = possible over-extension.
- **Distinct?** Yes — uses a geometry metric we already produce; novel signal.
- **Data:** M1 + bars. **Complexity:** low. **Novelty 4 · Fit 4 · Overfit med · Infra
  partial.**

### H17 — Multi-threshold-crossing (gap) regime
- **Anchor:** VOLCL. **Desc:** bars whose forming candle crossed the threshold >1×
  (the feasibility "multi_threshold_rate") mark gap/jump events; condition behaviour on
  jump vs smooth completion.
- **Why:** jumps vs diffusion are economically different; cheap to label.
- **Distinct?** Yes. **Data:** M1 + bars. **Complexity:** low. **Novelty 3 · Fit 4 ·
  Overfit med · Infra partial.**

### H18 — Bar-shape (body/range) continuation
- **Anchor:** MICRO. **Desc:** non-time-bar body-to-range ratio (decisive vs indecisive
  completion) as a continuation/again-reversion feature.
- **Why:** decisive bars may persist; classic candlestick intuition put on an event clock.
- **Distinct?** Partial — candlestick-flavoured; mild novelty on event clock. **Data:**
  M1 + bars. **Complexity:** low. **Novelty 2 · Fit 4 · Overfit high · Infra partial.**

## G. Sizing / labeling-overlay hypotheses (front-half discipline only)

### H19 — Volatility-scaled sizing overlay (event-time)
- **Anchor:** SIZE + TSMOM. **Desc:** apply vol-scaled position sizing (size ∝
  1/realized-vol) to *any* event-time signal; test whether scaling — not timing —
  improves risk-adjusted behaviour.
- **Why:** TSMOM literature attributes much performance to vol scaling.
- **Distinct?** Yes — a sizing study, never run here on event-time bars.
- **Data:** M1 + vol. **Complexity:** med. **Novelty 3 · Fit 4 · Overfit med · Infra
  partial.**

### H20 — Triple-barrier exit-horizon comparison (event-time)
- **Anchor:** CUSUM/TSMOM. **Desc:** compare fixed-bar-count exits vs triple-barrier
  (profit/stop/time) labeling in event time, for a neutral entry.
- **Why:** event-time barriers may dominate fixed horizons.
- **Distinct?** Partial — exit research; **caution:** C018/C019 found *no exit edge* on
  time bars. **Data:** M1 + bars. **Complexity:** med. **Novelty 2 · Fit 3 · Overfit
  high · Infra partial.**

## H. Session-structure hypotheses

### H21 — Cross-pair session-open activity impulse
- **Anchor:** SESS + XPAIR. **Desc:** one structural bar per session (Tokyo/London/NY
  open); test whether an outsized open-impulse across multiple pairs carries through
  the session.
- **Why:** W-shaped vol seasonality concentrates information at opens.
- **Distinct?** Yes if **cross-pair** (the failed USD_JPY London lead was single-pair,
  intrabar-stop-fragile); must avoid that exact construct.
- **Data:** M1 + sessions × pairs. **Complexity:** med. **Novelty 3 · Fit 4 · Overfit
  high · Infra partial.**

### H22 — Asian-range structural bar (cross-pair, cost-aware)
- **Anchor:** SESS. **Desc:** define the Asian-session range as one structural unit; test
  behaviour of the subsequent London move relative to that range, across pairs, only in
  low-spread states.
- **Why:** a classic FX structure; framed cross-pair + cost-aware to dodge prior failure.
- **Distinct?** Partial — well-known retail structure; novelty is the cross-pair +
  cost-state framing. **Data:** M1 + sessions. **Complexity:** med. **Novelty 2 · Fit 4
  · Overfit high · Infra partial.**

## I. Deliberately-included "tempting but should fail" hypotheses

### H23 — Wider range-bar MTF breakout (25–30 pip)
- **Desc:** C029's rule at a cost-feasible threshold. **Why it's here:** it is the
  obvious temptation the feasibility study invites. **Verdict preview:** this is a
  **C029 threshold retune** (anti-pattern §3.1) — included **so the screen explicitly
  rejects it**. **Novelty 1 · Fit 5 · Overfit high · Infra yes.**

### H24 — Renko/P&F trend-following
- **Desc:** classic renko brick / P&F column trend follow. **Why it's here:** ubiquitous
  retail idea. **Verdict preview:** no edge evidence + virtual-price backtest hazard
  (Phase 3) → **reject**. **Novelty 1 · Fit 2 · Overfit high · Infra partial.**

---

## Cross-cutting notes

- **Most promising shape:** *conditioning/sizing* ideas (H03, H05, H12, H16, H08, H19)
  and *activity-clock persistence* (H01) — because they don't re-bet on raw FX
  direction (which the repo has repeatedly found ≈ null) and several lift the cost
  ceiling directly.
- **Riskiest:** anything depending on a **flow proxy** (H10, H11, H07) — proxy quality
  is unproven and could manufacture spurious signal.
- **Pre-flagged rejects:** H23 (C029 retune), H24 (renko), and any idea that collapses
  to "smaller/bigger bar of a rejected rule".
- Every surviving idea still owes the **full front gate** (matched null, cost
  feasibility on the traded cell, filter ablation, pair-holdout) before any campaign.
