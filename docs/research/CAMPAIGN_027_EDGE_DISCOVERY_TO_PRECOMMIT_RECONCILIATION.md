# CAMPAIGN_027_EDGE_DISCOVERY_TO_PRECOMMIT_RECONCILIATION

**Status:** SCAFFOLD_ONLY / PRECOMMITTED / NOT_RUN / NOT_APPROVED. Phase 1 of
`research-campaign-027-h4-filtered-zscore-reversion-scaffold-001`. Diagnostic /
governance reconciliation only — approves nothing, runs no evidence, opens no
test lockbox.

This document reconciles the front-gate diagnostics
(`research-edge-discovery-front-gate-idea-selection-001`) into a single, precise
precommit decision for **CAMPAIGN_027 — `h4_filtered_zscore_reversion`
0.1.0-c027**. The exact frozen rule lives in
[`CAMPAIGN_027_PRECOMMIT_H4_FILTERED_ZSCORE_REVERSION_SCOPE.md`](CAMPAIGN_027_PRECOMMIT_H4_FILTERED_ZSCORE_REVERSION_SCOPE.md)
(Phase 2). Here we record *why* each rule is what it is, traced to evidence.

---

## Standing facts this document asserts (unchanged by this sprint)

- **C025 remains REJECT.** (M5 Donchian + HTF confluence breakout.)
- **C026 remains REJECT.** (Donchian + HTF timeframe ladder, M3–M30.)
- **C011 remains the null benchmark.** (Random-entry anchor.)
- **CAMPAIGN_027 is NOT approved.** It is a scaffold/precommit only.
- **The test lockbox remains closed** (2025-01-01 → 2026-05-20).
- `configs/approved_strategies.yaml` stays `approved: []`; paper/demo/live stay
  blocked.

## 1. Opportunity-map evidence (Phase 2)

The opportunity map established the *venue* facts that shape every rule below:

- **H4 is the cheapest feasible timeframe** (spread/ATR ≈ 0.04–0.10), comfortably
  below the 0.25 cost-hostile gate — the timeframe C025/C026 failed on. → freeze
  **timeframe = H4**.
- **USD_JPY is cost-advantaged** (cheapest + most volatile) but its *signal* is
  not special (see §2). → USD_JPY is a cost-advantaged *member* of the universe,
  never a standalone thesis.
- **Session-vol gradient is weak**, but spreads are widest in `new_york`/`late`
  and tightest in `asia`/`london`. → motivates the quiet-session filter on cost
  grounds, corroborated by ablation (§4).
- **Sub-H1 data is blocked** in the isolated lab. → no lower-TF variant is in
  scope; H4 only.

## 2. Signal-probe evidence (Phase 3)

- z-score reversion (H4, n≈11,934): pre-cost mean **rises monotonically with
  horizon** (+0.000009 → +0.000341, h1→h24) — a genuine, persistent
  mean-reversion drift. Beats the cost-matched random-timestamp null with
  `prob_null_ge = 0.00` from **h6** onward (effect +2.6 → +5.6).
- Post-cost turns positive at **h12** (+0.000055, hit 0.505) and stays positive
  at h24. → freeze the measured horizon **h12 (12 H4 bars ≈ 48h)** as the
  exit/hold reference.
- The **USD_JPY-specific** overlay is *weaker* than the all-pair signal and below
  null at short horizons → **refutes a USD_JPY-specific edge**; the precommit is
  an **all-pair** strategy.
- Honesty caveats carried forward: the post-cost positive is **wafer-thin** and
  inside the cost-assumption band; a more conservative slip would erase the
  trigger-level h12 positive. → conservative cost is the **binding** metric, and
  recency/stress become kill conditions.

## 3. Matched-null evidence (Phase 4)

- At h12, under the **conservative** overlay (1.5-pip spread + 0.2-pip slip +
  financing), the *trigger-level* signal `BEATS_MATCHED_NULL` on **all six**
  modes (incl. side-shuffled and full pair+side+session+weekday+hold) at
  percentile 100, effect 3.7–6.0 — the timing **and direction** carry real
  information. **But** the trigger-level post-cost expectancy is **negative**
  (−0.000033): "beats the matched null" = *loses less than random*, not *makes
  money*. The filters (§4) are what lift it clear of the cost band.
- `matrix_sanity` over the raw screened variants flagged the best variant
  (`zscore_reversion_h4_usdjpy`) as **`LIKELY_SELECTION_NOISE`**
  (`prob_best_le_null_max = 0.9375`). → standing caution; the campaign must
  demonstrate `ROBUST_MATRIX_SIGNAL` on its **own** train matrix (kill #3/#5).
- Trigger-level holdout: **pair-robust** but **time-fragile (2023-dominated)** at
  the trigger level — which §4 shows the filters cure.

## 4. Filter-ablation evidence (Phase 5) — the decisive phase

Prototype `zscore_reversion_h4` at h12, base trigger |z|≥2.0 over a 20-bar mean,
side toward the mean. Five filters, chosen on structural/prior grounds:

| filter | definition | marginal gain | flag | retained? |
|---|---|---|---|---|
| `f_low_vol` | trailing-250 ATR-14 percentile ≤ 0.33 | **+0.000301** | `FILTER_ADDS_EDGE` | **YES** |
| `f_strong_extension` | \|z\| ≥ 2.5 | **+0.000208** | `FILTER_ADDS_EDGE` | **YES** |
| `f_quiet_session` | UTC session ∈ {asia, london} | **+0.000234** | `FILTER_ADDS_EDGE` | **YES** |
| `f_cost_adv_pair` | pair ∈ {USD_JPY,GBP_USD,AUD_USD,EUR_USD} | +0.000098 | `FILTER_ONLY_REDUCES_SAMPLE` | no (drop) |
| `f_long_side` | direction = long | **−0.000199** | `FILTER_HURTS_EDGE` | no → **short-only** |

- **Best evidence-backed configuration:** `f_low_vol & f_strong_extension &
  f_quiet_session`, **short-biased** (cumulative post-cost +0.000761 optimistic,
  n=1,065, hit 0.552 — ~14× trigger-only). Leave-one-out confirms each of the
  three is load-bearing; dropping `f_long_side` *raises* expectancy.
- On the edge-adding subset (n=1,065): **survives conservative cost**
  (+0.000626), **pair-robust 6/7** (only USD_CHF ≈ −0.00006), and the filters
  **cured the Phase-4 single-year dominance** (now multi-year positive: +ve 2020,
  2022, 2023, 2025; **−ve 2021, 2024, 2026-partial** → 4/7 conservative).

## 5. Multiple-comparison sanity evidence

- The cross-variant "best" was selection noise (§3). The chosen subset is **not**
  the matrix winner — it is the *precommitted structural* configuration, which is
  why this sprint freezes it **before** any campaign run and why the campaign
  must re-confirm `ROBUST_MATRIX_SIGNAL` on its own train matrix (not reuse the
  front-gate screen as evidence).

## 6. Known limitations (explicitly carried, not resolved here)

- Wafer-thin edge inside the cost band; hit ≈ 0.50.
- Recency: 2024 and 2026-partial negative under conservative cost.
- Filter forking-path (three of five filters retained post-ablation).
- Selection-noise context from the raw matrix.
- The front gate measured a **fixed-horizon h12 proxy with no intrabar stop and
  entry at the signal-bar mid close**. The campaign trades the
  **approval-bound** convention (`next_bar_open`) with a mandatory protective
  stop — both are *additions* the train sprint must verify do not degrade the
  measured proxy.

## Exact reason this idea is allowed to become CAMPAIGN_027

It is the **first and only idea in the program** to clear the full edge-discovery
battery together: cost feasibility (PASS), forward-return information (PASS),
**all six** matched nulls (PASS), filter-adds-edge ablation (3/5 PASS, with a
clean short bias), conservative financing-inclusive cost (PASS), pair-robustness
(6/7), and multi-year positivity (4/7). Every cheap gate that C025/C026 failed,
this idea passed. Per `FUTURE_CAMPAIGN_REENTRY_GATES.md` G1–G6 the *information*
gates are met; G7–G9 (validation-not-selection, lockbox-sealed-pre-parity,
trade-count + `next_bar_open`) are campaign-discipline gates this scaffold
precommits and a future sprint must satisfy.

## Exact reason this is still only scaffold/precommit

The post-cost edge is **wafer-thin and inside the cost-assumption band**, two of
the three most recent periods are **negative**, the filters carry **forking-path
risk**, and the raw matrix flagged **selection noise**. None of these is
front-gate-disqualifying, but each is a *pre-registered kill condition* that can
only be adjudicated on a clean train/validation/test split with the campaign's
own ledgers — work this sprint deliberately does **not** do. Information ≠ a
proven tradable strategy.

## Why the long side is excluded (diagnostic-only)

`f_long_side` is the **only** filter that *hurts* edge (`FILTER_HURTS_EDGE`,
−0.000199), and leave-one-out shows removing it *raises* post-cost expectancy.
The reversion edge lives on the **short** side (selling rich extensions in an
up-drifting carry universe). The precommit is therefore **short-only**; long
signals (z ≤ −2.5) may be *logged for diagnostics* but are **never entered** in
v1 and carry no evidence weight.

## Why low-vol, strong-extension, and quiet-session filters are retained

All three are `FILTER_ADDS_EDGE` (marginal gain exceeds the noise band, not
merely a smaller sample) — the first filter battery in the program to do so.
Each is also **structurally motivated**: reversion works in calm/range regimes
(`f_low_vol`), deeper extensions revert harder (`f_strong_extension`), and quiet
sessions are calmer and cheaper (`f_quiet_session`, corroborated by the spread
gradient). They are retained **as a precommitted set**, not re-selected.

## Why 2024/2026 recency risk must become a binding future gate

The conservative-cost subset is negative in 2021, 2024, and 2026-partial — the
**two most recent** full/partial periods are negative. A decayed edge averaged
over a long window can look positive while being untradeable now. The future
sprint must therefore **REJECT** if the validation window (especially the most
recent fold) is not positive post-cost. This is kill condition #4 and may not be
weakened.

## Why no strategy is approved

Approval is a separate, reviewed human action on
`configs/approved_strategies.yaml`, available only after a precommitted champion
passes train + validation (recent fold positive), survives Backtrader parity, and
clears a human-gated single-use test. None of that has happened. This sprint
produces a scaffold and a frozen rule; it produces **no evidence and no
approval**.
