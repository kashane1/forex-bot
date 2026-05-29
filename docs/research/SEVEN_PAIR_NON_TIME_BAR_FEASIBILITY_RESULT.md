# Seven-pair non-time-bar feasibility result (diagnostic-only)

**Sprint:** `research-range-volatility-bar-feasibility-001` · Phase 5
**Window:** C029 train `2021-05-27 → 2023-12-31` (~947 days) — outside the test lockbox.
**Pairs:** EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD (91 cells).
**Artifacts:** [`research/non_time_bar_feasibility/feasibility_matrix.csv`](../../research/non_time_bar_feasibility/feasibility_matrix.csv),
[`feasibility_summary.json`](../../research/non_time_bar_feasibility/feasibility_summary.json),
[`pair_threshold_summary.json`](../../research/non_time_bar_feasibility/pair_threshold_summary.json),
[`cost_floor_summary.json`](../../research/non_time_bar_feasibility/cost_floor_summary.json),
[`non_time_bar_feasibility_report.md`](../../research/non_time_bar_feasibility/non_time_bar_feasibility_report.md).

> Diagnostic geometry + cost only. No signals, PnL, or returns; nothing approved; no
> C029 tuning; no campaign. Labels are hypotheses about where it is worth looking.

---

## 0. Label tally (91 cells)

| label | n |
|---|---:|
| FEASIBLE_FOR_STRATEGY_RESEARCH | 25 |
| FEASIBLE_ONLY_WITH_LARGER_STOPS | 41 |
| COST_DOMINATED | 10 |
| TOO_NOISY | 15 |
| TOO_SPARSE | 0 |
| INCONCLUSIVE | 0 |

## 1. Cost ranking by pair (all-candle mean spread → round-trip cost)

| pair | spread (p) | round-trip cost (p) | 10-pip range cost/risk | 10-pip label | min feasible range thr |
|---|---:|---:|---:|---|---:|
| AUD_USD | 1.49 | 1.89 | 0.094 | `FEASIBLE_ONLY_WITH_LARGER_STOPS` | **20** |
| EUR_USD | 1.61 | 2.02 | 0.101 | `COST_DOMINATED` | 25 |
| USD_JPY | 1.80 | 2.20 | 0.110 | `COST_DOMINATED` | 25 |
| NZD_USD | 1.89 | 2.29 | 0.114 | `COST_DOMINATED` | 25 |
| USD_CHF | 1.94 | 2.34 | 0.117 | `COST_DOMINATED` | 25 |
| USD_CAD | 2.11 | 2.51 | 0.126 | `COST_DOMINATED` | 30 |
| GBP_USD | 2.17 | 2.57 | 0.129 | `COST_DOMINATED` | 30 |

## 2. Answers to the Phase-5 questions

### Which pairs are least / most cost-dominated?
- **Least cost-dominated: AUD_USD** (spread 1.49, the only pair where 10-pip range is
  not outright dominated; 12/13 cells feasible). Then EUR_USD.
- **Most cost-dominated: GBP_USD and USD_CAD** (spread 2.1–2.2; 10-pip cost/risk
  0.126–0.129; need a 30-pip range bar before cost stops dominating).
- The ordering tracks spread almost perfectly — cost feasibility **is** a spread story.

### Is USD_JPY special? **No.**
USD_JPY sits in the **middle of the pack** (spread 1.80, 10-pip cost/risk 0.110,
min feasible range threshold 25 pip). It behaves like a typical mid-spread major.
Its overshoot/cadence geometry is unremarkable. The C029 10-pip failure was **not a
USD_JPY idiosyncrasy** — it would have failed on six of the seven majors, and only
narrowly survived (to "needs larger stops") on the cheapest, AUD_USD.

### Which thresholds produce sane cadence across pairs?
- **Range 20–30 pip** is sane on every pair (no TOO_SPARSE, no TOO_NOISY).
- **Volatility true_range 20 pip is TOO_NOISY on all 7 pairs**; true_range 30 on 4,
  true_range 40 on 2, abs_close 20 on 2. Volatility bars front-load cadence: the
  small-threshold cells fire tens of thousands of bars/yr.
- Nothing is too sparse in the train window even at 30 pip / 50-pip-volatility.

### Range bars vs volatility bars — which looks more promising?
**Range bars.** Feasible share 0.83 (29/35) vs volatility 0.66 (37/56), and
volatility's losses are concentrated in TOO_NOISY small-threshold cells. Range bars
give a cleaner cost-vs-cadence trade-off; volatility bars only become comparable at
the 50-pip end (where abs_close and true_range are feasible on all 7 pairs,
cost/risk 0.038–0.051). Note range and volatility are **not** edge-equivalent — this
is a cost/cadence statement only.

### Are per-pair thresholds necessary, or is one shared threshold realistic?
- The **minimum feasible range threshold differs by pair** (AUD 20, most 25,
  GBP/CAD 30) — driven by spread — so a *tuned* per-pair threshold would let the
  cheap pairs use a slightly tighter bar.
- But a **single shared 30-pip range bar is realistic and cost-feasible on every
  major** (and 50-pip for volatility). A shared threshold is *not* unrealistic; it is
  merely conservative for the cheap pairs. So per-pair thresholds are an
  optimisation, **not** a necessity — and tuning per-pair thresholds on this same
  data would itself be a forking-path risk.

## 3. The decisive caveat (same as Phase 4)

Across all seven pairs, **cost-feasibility at wide thresholds is necessary but not
sufficient.** Nothing here demonstrates a gross edge anywhere. The study tells us
*where cost would not by itself kill a strategy* (range ≥ 25–30 pip; volatility
50 pip), not *where an edge lives*. C029 already showed that even a real, positive
gross edge (+0.084R) at 10 pip was thin; there is no evidence such an edge persists —
let alone grows — at 25–30 pip, and wider bars give fewer, slower signals.

A future candidate is only defensible if it pairs a **wide, cost-feasible threshold**
with a **new external thesis** for the gross edge, run through the front gate as a
fresh pre-commit — never a re-run of the rejected C029 breakout rule at a bigger
number. See the lane decision (Phase 6).
