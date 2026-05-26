# Future Exit Research Hypotheses

**Date:** 2026-05-26  
**Branch:** `research-stop-and-exit-diagnostics-001`

> **Diagnostic only** — `strategy_evidence: false`. These are **pre-registration candidates**, not approved experiments. No retune of C008/C009.

---

## Context from this sprint

- Stop/time sign split is **framework-wide** (visible even in C011 null).
- C008 time exits show high MFE tail; C009 midline targets **cap** that tail.
- ~half of C008 stops saw ≥1R favorable before stopping; ~half never reached 1R.
- C008/C009 evidence **LIKELY_CONTAMINATED** — hypotheses must be tested on **new campaign IDs** with frozen entries.

---

## A. Allowed future hypotheses (if pre-registered)

### A1. Volatility-scaled stop redesign

| field | requirement |
|---|---|
| market-structure rationale | Range MR needs invalidation beyond normal H4 noise; ATR percentile defines "normal" |
| precommit | Fixed ATR lookback + multiplier declared before any run; no sweep from C008 stops |
| datasets | H4 deduped candles, cost atlas, 2× stress |
| fold plan | train → validation → closed test lockbox |
| min trades | validation ≥ 30; per-exit-bucket ≥ 15 |
| beat-null | vs C011 deduped or successor null on same entries |
| cost/financing | 2× spread stress; financing if hold > 24h |
| Backtrader parity | exit reason + bars_held must match primary engine |
| not a C008 retune | **new multiplier** not chosen from C008 MAE distribution; entries frozen separately |

### A2. Regime-dependent time stop

| field | requirement |
|---|---|
| rationale | Mean reversion speed varies by vol/risk regime (FRED features pre-declared) |
| precommit | Regime buckets + time-stop lengths fixed before run |
| datasets | FRED normalized features, H4 alignment audit |
| fold plan | Regime labels computed causal-only; no peek at validation winners |
| min trades | ≥ 30 validation; ≥ 10 per regime bucket or collapse buckets |
| beat-null | required |
| cost/financing | financing mandatory if 40+ bar holds cross rollovers |
| parity | required |
| not a retune | **not** "40 bars because C008 validation winners" — must cite ex-ante literature or pilot on **different** strategy version |

### A3. Counter-signal exit

| field | requirement |
|---|---|
| rationale | Exit when opposite-band touch or RSI recross invalidates MR thesis |
| precommit | Counter-signal definition frozen |
| datasets | standard H4 + cost atlas |
| fold plan | standard three-way split |
| min trades | ≥ 30 validation |
| beat-null | required |
| cost/financing | standard |
| parity | required |
| not a retune | different exit **mechanism**, not re-distancing C008 stop |

### A4. ATR trail after favorable excursion

| field | requirement |
|---|---|
| rationale | Lock partial reversion after X ATR favorable move without fixed midline target |
| precommit | X ATR and trail offset declared ex-ante |
| datasets | H4 + cost atlas |
| fold plan | standard |
| min trades | ≥ 30 |
| beat-null | required |
| cost/financing | standard |
| parity | required |
| not a retune | **not** fitted to C008 time-exit MFE distribution |

### A5. Partial exit + runner (bundle pre-registered only)

| field | requirement |
|---|---|
| rationale | Take structural partial at band midline; runner uses separate pre-registered exit |
| precommit | **Both** legs declared as one bundle before run |
| datasets | standard |
| fold plan | standard |
| min trades | ≥ 30; runner leg ≥ 15 |
| beat-null | required on **combined** expectancy |
| cost/financing | financing on runner leg |
| parity | both legs |
| not a retune | not C009 midline-only rehash — runner exit must be **new** rule |

### A6. No-target mean reversion with invalidation stop only

| field | requirement |
|---|---|
| rationale | C009 showed targets cap tail; test hold-to-time or trail **without** midline TP |
| precommit | Explicit absence of profit target; stop rule frozen |
| datasets | standard |
| fold plan | standard |
| min trades | ≥ 30 |
| beat-null | required |
| cost/financing | financing required (40-bar holds) |
| parity | required |
| not a retune | **new campaign ID** — not rerunning C008 with same 40-bar learned from validation |

### A7. Break-even stop after objective favorable excursion

| field | requirement |
|---|---|
| rationale | Reduce −1R stop-outs on trades that reached ≥1R MFE (59% of C008 stops) |
| precommit | Favorable excursion threshold (e.g. 1R) declared **before** seeing new fold results |
| datasets | standard |
| fold plan | standard |
| min trades | ≥ 30 |
| beat-null | required |
| cost/financing | standard |
| parity | required |
| not a retune | threshold **not** set to C008's observed 58.9% crossing rate post-hoc |

---

## B. Dangerous / likely overfit (forbidden without new thesis + lockbox)

| forbidden action | why |
|---|---|
| Choose stop length from C008 validation winners | direct validation winner tuning |
| Remove weak pairs from C008 validation only | pair selection from contaminated OOS |
| Optimize time stop from C008/C009 outcomes | post-hoc hold-period fit |
| Fit divergence thresholds after seeing winners | confluence weight tuning |
| Choose session filters from validation winners | session cherry-pick without pre-registration |
| Promote C008 40-bar time exit as "optimal" | descriptive finding ≠ approved rule |
| Revive C009 midline target because validation +0.19R | failed train gate; contaminated |

---

## Question 5 answer

Legitimate future exit research requires: **new campaign ID**, **frozen entries before exit tests**, **one exit change per campaign** (or pre-registered bundle), **beat-null**, **financing for long holds**, **dedup-safe engine**, and **no parameter selection from C008/C009 artifacts**. This sprint classifies hypotheses; it does **not** authorize any.
