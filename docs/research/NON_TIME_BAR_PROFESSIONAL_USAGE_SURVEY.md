# Non-time-bar professional usage survey

**Sprint:** `research-external-non-time-bar-thesis-discovery-001` · Phase 1
**Type:** external research synthesis. No code, no claims, no PnL.

> Sourcing note: claims tagged **[established]** are well-documented in the cited
> literature/practitioner sources; **[synthesis]** is my inference for *this repo's*
> context (M1 OHLCV + bid/ask + tick-count volume, 7 FX majors). No performance
> numbers are asserted. Sources listed at the end.

---

## 1. How each bar type is actually used by professionals

### Range bars
- **[established]** Invented ~1990 by Brazilian broker Vicente Nicolellis; each bar
  closes after a fixed price travel, so bars are dense in fast markets and sparse in
  quiet ones. In professional futures/FX they are mostly a **discretionary charting
  and execution aid** (cleaner visual trends, noise suppression), not the basis of a
  published systematic edge.
- **[established]** Their backtests are notoriously corrupted by **virtual/repainting
  prices** — range/renko bars have synthetic open/close levels that never traded, so
  naive backtests book fills at non-existent prices and inflate results. Practitioners
  warn this is a primary reason range-bar systems fail live.
- **[synthesis]** This is exactly the trap C029 avoided by resolving every bar on the
  **M1 tape** with conservative fills + independent parity (PASS). Any future non-time
  idea here inherits that discipline — but it also means we never get the "free" pips
  the retail backtests imagine.

### Volatility bars (CUSUM / cumulative-move sampling)
- **[established]** López de Prado's **CUSUM filter** samples an event when a
  cumulative (optionally vol-scaled) price move crosses a threshold, resetting on the
  move. It is used in professional ML pipelines as an **event-selection** step
  (where to *evaluate*), not as a standalone signal.
- **[synthesis]** The repo's `abs_close` volatility bar is essentially a one-sided
  CUSUM; a symmetric, **volatility-normalised** CUSUM bar is a close cousin we have
  not built or tested.

### Renko & Point-and-Figure
- **[established]** Renko (Japanese origin, close-driven bricks) and P&F (X/O columns
  on a box+reversal rule) are old, **predominantly discretionary** trend/breakout
  visualisation tools. P&F has a long practitioner history for breakout/target
  counting; neither has strong peer-reviewed evidence of a systematic edge.
- **[established]** Both share the range-bar **repaint/virtual-price backtest hazard**.
- **[synthesis]** Renko ≈ a range bar that only records closes; P&F ≈ range bar +
  reversal filter. For our cost reality they offer nothing range/volatility bars don't,
  and add backtest-fidelity risk. **Low priority** for us.

### Volume bars & dollar bars
- **[established]** Sample a bar every fixed quantity of **volume** (volume bars) or
  **price×volume traded** (dollar bars). López de Prado shows dollar bars have the
  most **stable bar-count over time** and the best statistical properties (returns
  closer to IID/normal, less autocorrelation) because they sample by *activity*, not
  the clock — they oversample active periods and undersample dead ones.
- **[established]** mlfinlab (Hudson & Thames) implements tick/volume/dollar bars from
  even 1-minute OHLC inputs (open source, tested).
- **[synthesis]** FX has **no consolidated traded volume**, but OANDA M1 carries a
  **tick-count `volume`** (number of price updates) with ~0.9 reported correlation to
  real volume on major venues. So **tick/"dollar" bars are approximable** here (dollar
  ≈ mid × tick-count). This is genuinely different sampling from range/time bars and is
  **buildable with current data** — a real candidate space.

### Imbalance bars & run bars (information-driven)
- **[established]** Sample when the **signed** order-flow imbalance (or a run of
  same-signed trades) crosses an expected threshold; designed to fire *early* when
  informed traders move size. Require **trade-level signed flow**.
- **[established]** Since we lack signed trades, the standard proxy is **Bulk Volume
  Classification (BVC)** — split a bar's volume into buy/sell using the (vol-scaled)
  price change. Literature: BVC is *less* accurate than the tick rule at identifying
  the aggressor (tick/Lee-Ready ~78–95%), but BVC is **better correlated with
  *informed*-trading proxies**, and BVC improves as bar size grows; extreme one-way
  moves mislabel it.
- **[synthesis]** True imbalance bars are **out** (no signed ticks). A **BVC-proxy
  imbalance bar at M1** is *possible* but the proxy quality is itself a research risk
  to flag loudly — not a clean edge source.

### Order-flow-style bars (footprint, delta, VPIN)
- **[established]** **VPIN** (Easley–López de Prado–O'Hara) buckets trades into equal
  *volume* buckets and measures order-flow **toxicity**; used by professionals as a
  liquidity/turbulence early-warning, though its flash-crash predictive claim is
  academically **contested**. Footprint/delta charts are discretionary order-flow
  tools needing tick + aggressor data.
- **[synthesis]** Full footprint/VPIN need data we lack; a **volume-bucketed
  toxicity proxy** (BVC within tick-volume buckets) could be a *regime/context*
  feature, not a standalone bar — and inherits BVC's caveats.

### Event bars (scheduled & data-driven)
- **[established]** Professionals routinely **resample around events** — macro releases
  (NFP/CPI/FOMC), session opens, rollover. The repo already has session/macro/calendar
  context infra. Event *conditioning* is standard; event *bars* (a bar per event window)
  are a clean, lookahead-safe construct.
- **[synthesis]** Note C014 found event-trading (NFP/FOMC) lost or produced no trades;
  so an **event bar** is interesting only as a *context/clock*, not a re-run of
  event-direction trading.

### Session-structure bars
- **[established]** FX intraday volatility is strongly **seasonal** (W-shaped: Tokyo /
  London / NY opens), and intraday realized-volatility **commonality across pairs** is
  strong and stable. Professionals build the day around these session blocks.
- **[synthesis]** A **session-anchored bar** (e.g. one bar per session, or
  Asian-range / London-breakout structural bars) is a real, data-available construct —
  but the repo's own USD_JPY London-continuation thread already **failed** a hardened
  test, so any session idea must be cross-pair and structurally new, not that lead.

## 2. What professionals do — vs what retail incorrectly believes

| topic | retail belief | professional reality |
|---|---|---|
| Range/renko backtests | "look how clean and profitable" | virtual/repaint prices inflate results; must resim on real tape **[established]** |
| Why alt bars help | "they predict direction" | they mostly fix **sampling** (stationarity, IID-ness) for *downstream* models; not a signal themselves **[established]** |
| FX volume | "real traded volume" | tick-count **proxy**; intensity, not a cash counter (~0.9 corr) **[established]** |
| Imbalance bars | "free order-flow edge" | need signed trades; proxies (BVC) are noisy and only loosely informed-trading-linked **[established]** |
| Smaller bars = more edge | "more signals = more profit" | smaller bars = more **cost** per unit risk (the C029/feasibility finding) **[synthesis]** |
| VPIN | "predicts crashes" | useful toxicity gauge; predictive claim **contested** **[established]** |

## 3. Concepts that appear repeatedly (cross-source)

1. **Activity-clock sampling** (volume/dollar bars) → better statistical properties
   than the wall clock. Recurs in López de Prado, mlfinlab, Alpaca, practitioner blogs.
2. **Event/CUSUM sampling** → sample where something happened, then label/evaluate.
3. **Volatility normalisation / scaling** → ubiquitous in CTA/TSMOM and in CUSUM
   thresholds; sizing inversely to realized vol.
4. **Order-flow toxicity / imbalance** → recurring informed-trading theme, but
   data-hungry.
5. **Session/seasonality structure** → universal in FX practice.

## 4. Which ideas seem robust vs mostly discretionary vs data-blocked

- **More robust (real statistical motivation, data available):** dollar/tick-volume
  **activity-clock bars**; volatility-normalised **CUSUM event bars**; session-structure
  bars (with new framing); volatility-clustering / activity-regime *conditioning*.
- **Mostly discretionary (weak systematic evidence):** renko, point-and-figure, naive
  range-bar breakout (≈ C029).
- **Data-blocked here (need tick/signed flow/L2):** true imbalance & run bars, VPIN
  proper, footprint/delta. Only **proxy** versions are possible, with explicit caveats.

## 5. Implications for hypothesis generation (carried to Phase 4)

- Treat alt bars primarily as a **sampling/clock** choice whose payoff is *cleaner
  conditioning and turnover control*, not an intrinsic signal — then pair the clock
  with an **externally-evidenced edge** (e.g. activity-time trend persistence,
  vol-clustering regimes).
- Prefer **activity-clock (tick-volume/dollar) and CUSUM** bars — buildable now, real
  literature, genuinely distinct from C029's price-travel range bar.
- Use signed-flow only as a **clearly-flagged proxy** (BVC), never as a clean edge.
- Anything renko/P&F/virtual-price is low priority (no edge evidence + fidelity risk).

## Sources

- M. López de Prado, *Advances in Financial Machine Learning* (2018), Ch. 2 (bars) — via
  [TDS: imbalance bars](https://medium.com/data-science/information-driven-bars-for-financial-machine-learning-imbalance-bars-dda9233058f0),
  [Sefidian: advanced candlesticks](https://www.sefidian.com/2021/06/12/introduction-to-advanced-candlesticks-in-finance-tick-bars-dollar-bars-volume-bars-and-imbalance-bars/),
  [TDS: volume & dollar bars](https://medium.com/data-science/advanced-candlesticks-for-machine-learning-ii-volume-and-dollar-bars-6cda27e3201d).
- [mlfinlab data structures (Hudson & Thames, GitHub)](https://github.com/hudson-and-thames/mlfinlab/blob/master/mlfinlab/data_structures/__init__.py).
- Range vs renko: [Marketcalls](https://www.marketcalls.in/trading-lessons/understanding-the-basic-difference-between-range-bars-and-renko-bars.html);
  backtest fidelity hazard: [AZ-INVEST](https://www.az-invest.eu/how-to-properly-backtest-rangebars-medianrenko-renko-and-pointo-using-tick-data),
  [QuantifiedStrategies renko](https://www.quantifiedstrategies.com/renko-trading-strategy/).
- FX tick volume proxy: [EarnForex tick volume](https://www.earnforex.com/guides/tick-volume-in-forex/),
  [Tradeciety](https://tradeciety.com/why-fake-volumes-in-forex-can-help-you-win-using-volume-in-forex).
- VPIN / toxicity: Easley, López de Prado, O'Hara — [Flow Toxicity and Liquidity (NYU Stern)](https://www.stern.nyu.edu/sites/default/files/assets/documents/con_035928.pdf);
  contested: [VPIN and the flash crash (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S1386418113000189).
- BVC: [Evaluating trade classification: BVC vs tick rule vs Lee-Ready (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S1386418115000415).
- FX intraday seasonality / RV commonality: [Functional GARCH intraday FX vol (arXiv)](https://arxiv.org/html/2311.18477v3),
  [Volatility forecasting w/ intraday commonality (arXiv)](https://arxiv.org/pdf/2202.08962).
