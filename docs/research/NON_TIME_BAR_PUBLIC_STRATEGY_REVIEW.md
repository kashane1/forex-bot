# Non-time-bar public strategy review

**Sprint:** `research-external-non-time-bar-thesis-discovery-001` · Phase 3
**Type:** review of public implementations / blogs / academic code. No code, no PnL.

> Scope: what publicly *recurs across independent sources* and how much **publication
> scrutiny** it survived. A blunt finding up front: **very few non-time-bar *trading
> systems* survive scrutiny.** Most durable public material is either a *pipeline /
> data-structure* (reproduced widely, but rarely with a clean out-of-sample edge
> claim) or *retail chart systems* (compromised by virtual-price backtests). That
> asymmetry is itself the most important result of this phase.

---

## 1. What recurs across independent sources

### A. The López de Prado pipeline (bars → events → labels → meta-label)
- **Independent reproductions:** Hudson & Thames `mlfinlab`; BlackArbsCEO
  `Adv_Fin_ML_Exercises`; numerous TDS/Medium walkthroughs; Alpaca "alternative bars".
- **Thesis:** sample by **activity** (dollar/volume/imbalance bars), pick events with a
  **CUSUM** filter, label with the **triple barrier**, optionally **meta-label** to
  filter false positives — to give ML cleaner, more stationary inputs.
- **Required data:** ideally tick + volume + signed flow; degrades to OHLC+volume for
  the standard (non-imbalance) bars.
- **Complexity:** moderate–high (bar construction + labeling + ML + purged CV).
- **Known weaknesses:** the books/repos demonstrate **better statistical properties**,
  **not** a published, robust, out-of-sample *trading* edge; results are dataset- and
  ML-pipeline-dependent; imbalance bars need data most FX shops lack; easy to overfit
  via the ML layer.
- **Repo fit:** the **bar + CUSUM + triple-barrier** front half is buildable on M1;
  the heavy ML/meta-label back half is **out of scope** for this lab (we test
  precommitted rules, not ML models). Take the **clock + labeling discipline**, leave
  the ML.

### B. Activity-clock (dollar/volume) bars as a sampling improvement
- **Independent sources:** López de Prado; mlfinlab; Alpaca; multiple blogs all show
  dollar bars give the most stable count + best return statistics.
- **Thesis:** equal-information sampling → cleaner downstream signals + naturally
  vol-adaptive turnover.
- **Required data:** volume (tick-count proxy OK in FX).
- **Weaknesses:** "better statistics" ≠ "edge"; FX volume is a proxy.
- **Repo fit:** **buildable now**; genuinely different from C029's price-travel range
  bar and C026's time-clock ladder.

### C. CTA / time-series-momentum systems
- **Independent sources:** Moskowitz–Ooi–Pedersen; AQR/Hurst–Ooi–Pedersen; Quantpedia
  "Time Series Momentum Effect"; CME education notes.
- **Thesis:** trend **persistence** over 1–12 months, vol-scaled sizing; the most
  *externally replicated* systematic effect in this whole survey.
- **Required data:** just prices; **vol estimate** for scaling.
- **Weaknesses:** it is a **slow, calendar-time** effect; much alpha is the vol-scaling
  overlay; at fast horizons it weakens.
- **Repo fit:** the *effect* is robust but lives at monthly horizons; the **novel,
  testable twist** is measuring persistence in **event/activity time** (per N
  dollar/CUSUM bars) — not the calendar-time version C025/C026 already explored.

### D. Retail renko / range-bar / P&F systems
- **Independent sources:** TradingView scripts, NinjaTrader/practitioner blogs,
  QuantifiedStrategies, az-invest.
- **Thesis:** "cleaner trends/breakouts" on price-travel charts.
- **Required data:** OHLC.
- **Known weaknesses (decisive):** **virtual/repaint prices** → backtests book fills at
  prices that never traded → inflated, non-reproducible results; vendors explicitly
  warn to use real-tick "market replay". This is the **single most common reason these
  systems fail live**.
- **Repo fit:** **avoid.** This is essentially C029's family and the fidelity hazard we
  already neutralised via M1 resolution + parity. No new edge here.

### E. Order-flow / VPIN / footprint systems
- **Independent sources:** Easley–López de Prado–O'Hara (VPIN); commercial order-flow
  platforms (Bookmap, Sierra/footprint).
- **Thesis:** trade where order-flow toxicity/imbalance signals informed activity.
- **Required data:** tick + aggressor side + true volume.
- **Weaknesses:** VPIN predictive claim **contested**; needs data FX retail/most APIs
  lack; proxies (BVC) are noisy.
- **Repo fit:** **data-blocked**; only a flagged BVC/toxicity *proxy* as a context
  feature is conceivable.

## 2. Per-idea summary table

| idea | thesis | data | complexity | key weakness | repo fit |
|---|---|---|---|---|---|
| LdP pipeline (bars+CUSUM+triple-barrier+meta-label) | cleaner ML inputs | tick/vol (degrades to OHLC+vol) | high | stats≠edge; ML overfit; imbalance needs ticks | partial (front half only) |
| Dollar / tick-volume activity bars | equal-information sampling | volume(proxy) | low–med | proxy; stats≠edge | **buildable** |
| CUSUM event bars | sample real moves, vol-scaled | OHLC+vol | low | event-selection, not a signal | **buildable** |
| TSMOM in event time | trend persistence per activity unit | prices+vol | med | slow effect; sizing-driven | **buildable, novel twist** |
| Renko / range / P&F breakout | clean trend/breakout | OHLC | low | virtual-price backtest inflation; ≈C029 | **avoid** |
| VPIN / footprint / true imbalance | order-flow toxicity | tick+aggressor+volume | high | contested; data-blocked | **blocked** |
| BVC imbalance proxy (context) | signed-flow proxy regime | OHLC+vol | med | proxy accuracy; mislabels extremes | weak/contextual |

## 3. What "survived publication scrutiny"

- **Strongly replicated:** dollar/volume bars' **statistical-property** advantage;
  **time-series momentum** as an effect; **volatility clustering/seasonality**.
- **Weak / contested:** VPIN's predictive value; any renko/range-bar P&L claim;
  meta-labeling as a universal win (mixed independent results).
- **Essentially absent:** a *publicly documented, independently reproduced,
  out-of-sample non-time-bar **trading** edge in spot FX*. This matters: it means a new
  FX non-time-bar hypothesis is **genuinely unproven territory**, so any candidate must
  be framed humbly and go through the full front gate — there is no public free lunch
  to copy.

## 4. Implications for Phase 4

- Borrow **constructs that survived scrutiny** (activity-clock sampling, CUSUM events,
  TSMOM persistence, vol-clustering/seasonality) — **not** retail chart systems.
- Keep only the **front half** of the LdP pipeline (bar + event + label discipline);
  the ML/meta-label back half is out of scope for a precommitted-rule lab.
- Treat the absence of a public FX non-time-bar edge as a **prior toward humility**:
  generate hypotheses, expect most to fail the front gate, and require external
  motivation for each.

## Sources

- [mlfinlab data structures (GitHub)](https://github.com/hudson-and-thames/mlfinlab/blob/master/mlfinlab/data_structures/__init__.py),
  [run/imbalance structures](https://github.com/hudson-and-thames/mlfinlab/blob/master/mlfinlab/data_structures/run_data_structures.py),
  [dollar/volume bars from 1-min OHLC (issue #142)](https://github.com/hudson-and-thames/mlfinlab/issues/142).
- [BlackArbsCEO, Adv_Fin_ML_Exercises (GitHub)](https://github.com/BlackArbsCEO/Adv_Fin_ML_Exercises/blob/master/notebooks/mlfinlab/corefns/core_functions.py).
- [Alpaca: Alternative Bars](https://alpaca.markets/learn/alternative-bars-01).
- Meta-labeling (mixed evidence): [Hudson & Thames](https://hudsonthames.org/does-meta-labeling-add-to-signal-efficacy-triple-barrier-method/).
- TSMOM: [Quantpedia: Time Series Momentum Effect](https://quantpedia.com/strategies/time-series-momentum-effect),
  [Moskowitz–Ooi–Pedersen (NYU Stern PDF)](https://w4.stern.nyu.edu/facdir/lpederse/papers/TimeSeriesMomentum.pdf).
- Renko backtest fidelity hazard: [az-invest](https://www.az-invest.eu/how-to-properly-backtest-rangebars-medianrenko-renko-and-pointo-using-tick-data),
  [QuantifiedStrategies renko](https://www.quantifiedstrategies.com/renko-trading-strategy/).
- VPIN (contested): [VPIN and the flash crash (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S1386418113000189).
