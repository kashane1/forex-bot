# Non-time-bar literature review

**Sprint:** `research-external-non-time-bar-thesis-discovery-001` · Phase 2
**Type:** literature synthesis. No code, no claims, no PnL.

> **[established]** = documented in the cited literature; **[synthesis]** = my
> inference for this repo. No performance numbers asserted. Sources at the end.

---

## 1. López de Prado — *Advances in Financial Machine Learning* (2018)

**[established]** The foundational modern treatment of non-time bars (Ch. 2) and a
research *process* (Ch. 3+):

- **Why not time bars:** time sampling oversamples quiet periods and undersamples
  active ones, producing returns with poor statistical properties (fat tails, serial
  correlation, heteroskedasticity).
- **Standard alt bars:** tick / volume / **dollar** bars sample by activity. Dollar
  bars have the **most stable bar count** and returns closest to IID/normal.
- **Information-driven bars:** tick/volume/dollar **imbalance** and **run** bars fire
  when signed-flow imbalance or same-sign runs exceed expectation — designed to detect
  informed trading *early*.
- **CUSUM event filter:** sample an event when a cumulative (vol-scaled) deviation
  crosses a threshold — symmetric, resets on trigger.
- **Triple-barrier labeling + meta-labeling:** label outcomes by which of
  {profit-target, stop, time} is hit first; meta-labeling trains a secondary model to
  *filter false positives* (improve precision/sizing of a primary signal).

**Data requirement:** imbalance/run bars need **signed trade flow**; dollar/volume
bars need traded volume. **Repo fit [synthesis]:** dollar/tick-volume bars and the
CUSUM event filter are **buildable** on M1 + tick-count volume; imbalance/run bars are
**not** without a BVC proxy. Triple-barrier/meta-labeling are *labeling/sizing*
techniques (not bars) and could overlay a future candidate — but C018/C019 found **no
exit edge**, so meta-labeling is a precision tool, not an edge source.

## 2. Market microstructure & order-flow toxicity

**[established]**
- **VPIN** (Easley, López de Prado, O'Hara): volume-bucketed order-flow toxicity
  metric; volume bucketing reduces volatility-clustering contamination. Used as a
  liquidity/turbulence gauge; its flash-crash *prediction* claim is **contested**
  (Andersen–Bondarenko critique and rejoinders).
- **Trade classification:** when signed flow is absent, **BVC** estimates buy/sell
  split from vol-scaled price change; the **tick rule** / Lee-Ready are more accurate
  at the *aggressor* (~78–95%), but **BVC is better correlated with informed-trading
  proxies**, and improves with larger bars; extreme one-way moves mislabel it.

**Repo fit [synthesis]:** no ticks/L2 → only **proxy** toxicity/imbalance at M1, with
explicit accuracy caveats. Best use is **regime conditioning** (is the current
activity "toxic"/one-sided?), not a standalone bar or signal.

## 3. Volatility clustering & realized variance

**[established]** Volatility is strongly **autocorrelated/clustered** (ARCH/GARCH,
realized-variance literature); intraday FX vol is **seasonal** (W-shape at Tokyo/
London/NY opens) and intraday **realized-vol commonality across pairs** is strong and
stable. Activity-clock bars (volume/dollar) partly *absorb* vol clustering by
sampling faster when vol is high.

**Repo fit [synthesis]:** clustering is the most **reliably documented** intraday
regularity available to us. It motivates **conditioning** (trade only certain
activity/vol regimes) and **bar design** (vol-normalised CUSUM). But clustering is
about the *magnitude* of moves, not their *direction* — and the repo's own
vol-compression→expansion thread already found direction ≈ null. So a vol-clustering
idea must monetise something **other than direction** (e.g. straddle-like or
regime-gating), which is hard within a directional FX bot.

## 4. Trend persistence / time-series momentum

**[established]** Moskowitz, Ooi & Pedersen (2012), *Time Series Momentum*: 1–12 month
return **persistence** that partially **reverses** at longer horizons, across 58
futures incl. currencies; CTAs/managed futures demonstrably run this; **volatility
scaling** (sizing ∝ 1/realized-vol) drives much of the realized performance.

**Conflicting note [established]:** subsequent work argues much of TSMOM's alpha is
the vol-scaling/risk-parity overlay rather than the raw momentum signal — i.e. *how
you size*, not *when you trade*.

**Repo fit [synthesis]:** TSMOM is a **real, replicated external phenomenon** — the
strongest candidate "external thesis" anchor. The novel angle for *this* repo:
measure momentum/persistence in **event/activity time** (per N dollar/CUSUM bars)
rather than calendar time, where the signal-to-noise of "trend" may differ because
bars are equal-information rather than equal-time. This is distinct from C025/C026
(which only slowed the *time* clock) and from C029 (price-travel breakout, not
persistence-of-sign).

## 5. Mean reversion & breakout

**[established]** Short-horizon **mean reversion** (bid-ask bounce, liquidity
provision) and longer **breakout/continuation** coexist; which dominates is
**horizon- and regime-dependent**. FX intraday has documented reversal at very short
horizons and continuation around session/liquidity events.

**Repo fit [synthesis]:** the repo has already rejected H4 z-score reversion (C027),
range mean-reversion (C008), and breakout families (C015/C017/C025/C029). New
mean-reversion/breakout ideas are only admissible if the **bar clock itself** changes
the conditioning in a way prior time-bar tests could not see (e.g. reversion measured
*per equal-activity bar* vs per fixed time) — otherwise it's a re-run.

## 6. Session behaviour & FX-specific research

**[established]** FX is decentralised (no consolidated tape/volume); liquidity and vol
follow a **session cycle**; rollover/late hours have **fat-tailed spreads** (confirmed
in our own feasibility data: USD_JPY rollover spread ~2.9p vs ~1.6p in liquid
sessions). Session-open breakouts and Asian-range strategies are heavily studied by
practitioners with mixed published evidence.

**Repo fit [synthesis]:** session structure is data-available and our feasibility
study already quantified per-session spread. But the repo's USD_JPY
London-continuation lead **failed** a hardened test, so a session idea must be (a)
cross-pair, (b) structurally new, (c) cost-aware (avoid rollover).

## 7. Recurring findings (cross-literature)

1. **Sampling by activity beats sampling by clock** for statistical properties
   (López de Prado, mlfinlab, microstructure).
2. **Volatility clusters and is seasonal** — the most dependable intraday regularity.
3. **Trend persistence (TSMOM)** is real and externally replicated; **sizing/vol-
   scaling** matters as much as timing.
4. **Order-flow/imbalance** is informative but **data-hungry**; proxies are noisy.
5. **Direction is hard in FX**; much published "edge" is structure, sizing, or
   cost-sensitive.

## 8. Conflicting findings

- VPIN's predictive value: claimed vs contested.
- TSMOM: raw-signal alpha vs vol-scaling-overlay alpha.
- Alt bars: better *statistical properties* (well-supported) vs better *trading edge*
  (not established — the property improvement is for downstream ML, not a P&L claim).
- Imbalance proxies: BVC worse at aggressor ID but better at informed-trading linkage.

## 9. Data & implementation requirements (gate every hypothesis)

| technique | needs | available here? |
|---|---|---|
| time/range/volatility bars | OHLC | ✅ |
| tick/volume bars | volume count | ✅ (M1 tick-count) |
| dollar bars | price × volume | ✅ (approx: mid × tick-count) |
| CUSUM event bars | OHLC + vol estimate | ✅ |
| imbalance / run bars | **signed** trade flow | ❌ (BVC proxy only) |
| VPIN / footprint | tick + aggressor + true volume | ❌ |
| TSMOM in event time | any activity-clock bar series | ✅ (derivable) |
| session-structure bars | timestamps + sessions | ✅ (infra exists) |
| meta-labeling / triple-barrier | a primary signal + labels | ✅ as overlay (not a bar) |

## 10. Applicability verdict for this repo

The literature points away from "a new bar = a new edge" and toward **"a better clock
+ an externally-evidenced edge + disciplined sizing."** The two externally-strongest
anchors we can actually build on are **(a) activity-clock sampling** (dollar/tick-
volume/CUSUM, better statistical properties, distinct from C029/C026) and **(b)
time-series momentum / trend persistence measured in event time with volatility
scaling**. Volatility clustering is dependable but mostly a **conditioning/sizing**
input (direction-neutral). Order-flow ideas are proxy-limited. These shape Phase 4.

## Sources

- López de Prado, *Advances in Financial Machine Learning* (2018) — bars, CUSUM,
  triple-barrier, meta-labeling: [mlfinlab triple-barrier/meta-labeling docs](https://random-docs.readthedocs.io/en/latest/implementations/tb_meta_labeling.html),
  [Hudson & Thames: Does meta-labeling add to signal efficacy?](https://hudsonthames.org/does-meta-labeling-add-to-signal-efficacy-triple-barrier-method/).
- VPIN / toxicity: [Easley–López de Prado–O'Hara, Flow Toxicity & Liquidity (NYU Stern)](https://www.stern.nyu.edu/sites/default/files/assets/documents/con_035928.pdf);
  contested: [VPIN and the flash crash (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S1386418113000189).
- BVC trade classification: [BVC vs tick rule vs Lee-Ready (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S1386418115000415).
- Time-series momentum: [Moskowitz, Ooi & Pedersen, *Time Series Momentum* (NYU Stern PDF)](https://w4.stern.nyu.edu/facdir/lpederse/papers/TimeSeriesMomentum.pdf);
  vol-scaling caveat: [Time series momentum and volatility scaling (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S1386418116301379).
- Intraday FX vol seasonality / RV commonality: [Functional GARCH intraday FX vol (arXiv)](https://arxiv.org/html/2311.18477v3),
  [Volatility forecasting with intraday commonality (arXiv)](https://arxiv.org/pdf/2202.08962).
