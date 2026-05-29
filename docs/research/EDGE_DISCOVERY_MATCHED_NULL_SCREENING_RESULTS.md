# EDGE_DISCOVERY_MATCHED_NULL_SCREENING_RESULTS

**Status:** diagnostic / matched-null screening (Phase 4 of
`research-edge-discovery-front-gate-idea-selection-001`). Protocol **level 2**.
Descriptive only — no verdict word, no significance claim, no strategy, no
campaign, no test lockbox, no approval.

> Engine: `research/edge_discovery/front_gate_idea_selection/run_matched_null_screening.py`.
> Artifacts: `matched_null_probe_results.json`, `matched_null_probe_summary.csv`,
> `matrix_sanity_probe_results.json`, `probe_compatibility_gaps.json`.
> Frames/ledgers rebuilt in-memory; cost overlay = spread 1.5 pips + 0.2-pip
> slip + financing (the lab `apply_cost_overlay` default — stricter than the
> realized-spread overlay used in Phase 3).

---

## Prototypes screened

The two Phase-3 survivors at the horizon they would trade (**h12**, 40 seeds):
`zscore_reversion_h4` (11,925 trades) and `failed_breakout_fade_h4` (8,318
trades). Modes: timestamp_random_same_pair, side_shuffled, pair_matched_random,
session_matched_random, holding_period_matched_random, full_matched_null.

## Result 1 — both beat *every* structure-matched null …

| Prototype | strategy exp (post-cost) | best null mean | every-mode flag | prob_null≥strat | effect |
|---|---|---|---|---|---|
| zscore_reversion_h4 | **−0.000033** | −0.00035 … −0.00052 | `BEATS_MATCHED_NULL` ×6 | 0.00 | 3.7 – 6.0 |
| failed_breakout_fade_h4 | **−0.000010** | −0.00034 … −0.00036 | `BEATS_MATCHED_NULL` ×6 | 0.00 | 3.6 – 4.7 |

Both prototypes land at the **100th percentile of all six nulls** — including
`side_shuffled` (entries fixed, labels permuted) and `full_matched_null`
(pair+side+session+weekday+hold matched). So the **timing and direction of the
reversion signal carry genuine information** beyond random structure-matched
entries. This is a real, robust *market fact*: mean-reversion entries on H4
majors lose less than any structure-matched random baseline.

## Result 2 — … but the post-cost expectancy is still negative

The strategy expectancies above are **negative** (−0.000033, −0.000010). Under
the conservative cost overlay (1.5-pip spread + slip + **financing**), both
prototypes are net-negative. Phase 3's marginal *positive* at h12 (+0.000048,
realized-spread, no financing) **flips back negative once financing and a flat
1.5-pip spread are charged.** The entire apparent edge lives **inside the
cost-assumption band**: positive under optimistic cost, negative under
conservative cost. "Beats the matched null" here means *loses less than random*,
not *makes money*.

## Result 3 — the cross-variant "best" is selection noise

`matrix_sanity` over the six screened prototype variants (h12 post-cost):

- best variant = **`zscore_reversion_h4_usdjpy`** (+0.000117) — the single-pair
  USD_JPY result, the very thing Phase 3 already flagged as not robust.
- `prob_best_le_null_max = 0.9375` → a ~94% chance the best is **best-of-N
  selection noise**; `deflated_improvement = −0.000308` (negative after
  deflation).
- Flags: **`LIKELY_SELECTION_NOISE`, `FRAGILE_SINGLE_PAIR_RESULT`.**

The apparent "winner" is exactly what the multiple-comparison gate exists to
catch: the most extreme of several screened variants, indistinguishable from the
maximum of noise.

## Result 4 — the marginal edge is regime- and pair-fragile

Holdout fragility on the (optimistic-cost) h12 per-row post-cost means:

| Prototype | pair-holdout sign-flip | year-holdout sign-flip | dominant block |
|---|---|---|---|
| zscore_reversion_h4 | **YES** (drop AUD_USD → +0.0000480 → −0.0000057) | **YES** | year **2023** |
| failed_breakout_fade_h4 | no (pair-robust) | **YES** | year **2023** |

Per-year breakdown (both prototypes): the positive aggregate is **dominated by
2023** (+0.0013 / +0.00058) and is **negative in 2020, 2022, and 2026**. This is
the C022/London-continuation lesson again — *a trend-regime artifact*, not a
stationary edge. z-score reversion additionally collapses if any single pair
(AUD_USD) is removed and is strongly negative on USD_CHF (−0.00055).

## Does any prototype survive the front gate?

**No.** Mapping to the protocol's campaign-eligibility criteria:

| Criterion | zscore_reversion_h4 | failed_breakout_fade_h4 |
|---|---|---|
| cost feasibility passes | ✔ (H4 feasible) | ✔ |
| forward-return information present | ✔ | ✔ |
| **above matched null (post-cost, conservative)** | **✗ info only; expectancy < 0** | **✗ info only; expectancy < 0** |
| not one-pair/one-session artifact | **✗ pair-fragile** | partial (pair-robust) |
| not selection noise (matrix sanity) | **✗ LIKELY_SELECTION_NOISE** | **✗** |
| time-block stable | **✗ 2023-dominated** | **✗ 2023-dominated** |

Neither clears the bar. The reversion *information* is real and structure-robust,
but it is **not a robust, stationary, cost-surviving edge** — it is a 2023-regime
effect sitting inside the cost-uncertainty band, and the best single-pair variant
is selection noise.

## Should any be rejected cheaply?

- `failed_breakout_fade_h4` → **REJECT_CHEAPLY**: net-negative post-cost, year-
  fragile (2023), selection-noise context. No further work warranted.
- `zscore_reversion_h4` → **proceed to Phase 5 filter ablation** before final
  ranking: it is the strongest *information* signal, and the gate requires
  evidence on whether a session/volatility/|z|/pair filter can convert the
  marginal signal into a robust, cost-surviving edge — or whether filters only
  shrink the sample (the expected outcome given the 2023/pair fragility).

## Compatibility gaps (`probe_compatibility_gaps.json`)

- Carry/financing matched null — no local carry/swap-rate table.
- Sub-hour open-expansion matched null — no local M1/M5/M15/M30 frames.
- `holding_period_matched_random` ≈ `pair_matched_random` here because the
  probe ledgers use a fixed h12 hold (`bars_held = 12`); a real campaign with a
  variable hold distribution would exercise this mode distinctly.

**No edge is claimed.** Phase 5 tests filter contribution on the single
strongest prototype; Phase 6 ranks and decides campaign eligibility (expected:
none).
