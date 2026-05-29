# USD_JPY non-time-bar feasibility result (diagnostic-only)

**Sprint:** `research-range-volatility-bar-feasibility-001` · Phase 4
**Window:** C029 train `2021-05-27 → 2023-12-31` (946.9 days, 955,316 M1 rows) —
entirely outside the test lockbox.
**Artifacts:** [`research/non_time_bar_feasibility/usdjpy/feasibility_matrix.csv`](../../research/non_time_bar_feasibility/usdjpy/feasibility_matrix.csv),
[`pair_threshold_summary.json`](../../research/non_time_bar_feasibility/usdjpy/pair_threshold_summary.json),
[`cost_floor_summary.json`](../../research/non_time_bar_feasibility/usdjpy/cost_floor_summary.json),
[`non_time_bar_feasibility_report.md`](../../research/non_time_bar_feasibility/usdjpy/non_time_bar_feasibility_report.md).

> Diagnostic geometry + cost only. **No** signals, PnL, or returns were computed;
> nothing is approved; C029 is not tuned; no campaign is created. Labels are
> hypotheses about where it is worth looking, **not** gate passes.

---

## 0. Cost basis

USD_JPY all-candle mean spread over the window = **1.795 pips** (median 1.7); by
session: London/overlap/NY ≈ **1.6 pips**, Tokyo ≈ 1.68, **rollover_late ≈ 2.93**
(fat tail). The diagnostic uses the conservative all-candle mean → **round-trip cost
≈ 2.195 pips** (`spread + 0.4` slippage). This is ~4% below C029's realised
**2.29 pips**, so the picture is, if anything, slightly *optimistic* vs C029 and the
conclusions hold a fortiori.

## 1. The matrix (baseline stop = 2× threshold for range, 1× for volatility)

| bar | thr | bars/yr | cadence | median min/bar | overshoot | cost/risk (base) | cost/risk (wide) | label |
|---|---:|---:|---|---:|---:|---:|---:|---|
| range | 10 | 12,906 | sane | 10 | 2.71 | **0.110** | 0.055 | `COST_DOMINATED` |
| range | 15 | 6,121 | sane | 21 | 3.36 | 0.073 | 0.037 | `FEASIBLE_ONLY_WITH_LARGER_STOPS` |
| range | 20 | 3,585 | sane | 38 | 3.80 | 0.055 | 0.027 | `FEASIBLE_ONLY_WITH_LARGER_STOPS` |
| range | 25 | 2,382 | sane | 59 | 4.32 | **0.044** | 0.022 | `FEASIBLE_FOR_STRATEGY_RESEARCH` |
| range | 30 | 1,698 | sane | 83 | 4.64 | **0.037** | 0.018 | `FEASIBLE_FOR_STRATEGY_RESEARCH` |
| abs_close | 20 | 21,598 | very_high | 13 | 1.64 | 0.110 | 0.055 | `TOO_NOISY` |
| abs_close | 30 | 14,746 | sane | 20 | 1.69 | 0.073 | 0.037 | `FEASIBLE_ONLY_WITH_LARGER_STOPS` |
| abs_close | 40 | 11,199 | sane | 26 | 1.73 | 0.055 | 0.027 | `FEASIBLE_ONLY_WITH_LARGER_STOPS` |
| abs_close | 50 | 9,027 | sane | 33 | 1.76 | **0.044** | 0.022 | `FEASIBLE_FOR_STRATEGY_RESEARCH` |
| true_range | 20 | 38,228 | very_high | 7 | 2.13 | 0.110 | 0.055 | `TOO_NOISY` |
| true_range | 30 | 26,273 | very_high | 10 | 2.20 | 0.073 | 0.037 | `TOO_NOISY` |
| true_range | 40 | 20,032 | very_high | 14 | 2.24 | 0.055 | 0.027 | `TOO_NOISY` |
| true_range | 50 | 16,186 | sane | 17 | 2.27 | **0.044** | 0.022 | `FEASIBLE_FOR_STRATEGY_RESEARCH` |

## 2. Answers to the Phase-4 questions

### Was the C029 10-pip range-bar threshold too cost-sensitive? **Yes.**
At the baseline 2× stop (20 pips) the 10-pip bar pays **cost/risk = 0.110** — i.e. a
strategy must clear **+0.110R of gross edge just to break even on cost**. C029's
actual gross edge was **+0.084R**, and its ~24-pip stop gave cost/risk ≈ 0.095. Both
sit **above the ~0.08R best gross edge this lab has ever observed**. The 10-pip cell
is the *only* USD_JPY range cell labelled `COST_DOMINATED`. **The failure is the
threshold being too small, not range bars per se.**

### Which USD_JPY range thresholds are cost-feasible?
- **25 pip (0.044) and 30 pip (0.037)** clear the feasible band at the baseline 2×
  stop.
- 15–20 pip are `FEASIBLE_ONLY_WITH_LARGER_STOPS` (need a 3–4× stop to drop below
  0.05).
- 10 pip is cost-dominated at any sane stop short of the wide 4× scenario (0.055).

### Which USD_JPY volatility thresholds are cost-feasible?
- **abs_close 50 pip (0.044)** and **true_range 50 pip (0.044)** clear at baseline.
- abs_close 30–40 are feasible-only-with-larger-stops.
- true_range 20–40 and abs_close 20 are `TOO_NOISY` — cadence exceeds
  **20,000 bars/yr** (true_range 20 pip is a staggering 38,228/yr ≈ 105/day), so cost
  is paid on a torrent of bars regardless of the per-trade ratio.

### Does widening the threshold reduce cost domination enough? **Yes, monotonically.**
Cost is ~fixed in pips (≈2.2) while nominal risk scales with the threshold, so
cost/risk falls roughly as `1/threshold`: 0.110 → 0.073 → 0.055 → 0.044 → 0.037
across 10→15→20→25→30 pip. By 25–30 pip range (and 50-pip volatility) cost is no
longer the binding constraint.

### Which thresholds are too sparse or too noisy?
- **Too noisy:** true_range 20/30/40 and abs_close 20 (cadence > 20k/yr).
- **Too sparse:** none in the train window — even 30-pip range gives ~1,698 bars/yr.
- Overshoot grows with threshold (range 30-pip overshoots ~4.6 pips ≈ 15% of the
  threshold) but stays well within sane bounds.

### Is there a candidate lane worth a future precommit?
**Cost-feasibility is necessary but NOT sufficient — and this is the crux.** The
diagnostics show that at **25–30 pip range bars** (and **50-pip volatility bars**)
cost stops being the killer. They show **nothing whatsoever about whether a gross
edge exists** at those thresholds. C029 demonstrated the 10-pip breakout's gross
edge was a thin **+0.084R**; there is no reason to assume a 25–30 pip *breakout* has
any gross edge at all — wider bars mean fewer, slower signals and the breakout
premise may weaken, not strengthen.

So the only defensible candidate is one that (a) targets a **wider** threshold where
cost ≠ destiny, **and** (b) rests on a **genuinely new external thesis** for why that
non-time bar carries a gross edge — **not** a re-run of C029's MTF-breakout rule at a
bigger number, which would be a forking-path retune of a rejected family. Absent
such a thesis, the correct action is **pause** (see the lane decision in Phase 6).

## 3. What this does NOT establish

- No edge is demonstrated at any threshold. `FEASIBLE_*` means "cost alone would not
  kill it", nothing more.
- The cost basis is an all-candle spread mean; real fills cluster in liquid sessions
  (~1.6-pip spread) but also occasionally in rollover (fat-tailed ~2.9). The
  conservative mean keeps the floor honest.
- The test lockbox (2025-01-01 → 2026-05-20) was not touched; this window is the
  C029 train span.
