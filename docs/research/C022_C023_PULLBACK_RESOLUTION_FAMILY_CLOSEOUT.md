# C022 / C023 Pullback-Resolution Family — Closeout Memo

**Date:** 2026-05-28 · **Sprint:** `research-post-c022-family-retirement-and-new-thesis-selection-001`
**Type:** research closeout. Approves nothing, changes no verdict, tunes nothing, creates no campaign.

> This memo formally closes out the C022/C023 pullback-resolution family. It
> **does not** change any verdict (C022 stays REJECT, C023 stays scaffold-only),
> rewrite any historical metric, create CAMPAIGN_024, or execute C023. It records a
> classification and the criteria that would be required to reopen the family.

The family in scope: `h4_h1_pullback_resolution_entry` — an H4 directional-regime
gate → H1 pullback → M15 EMA-reclaim trigger. CAMPAIGN_022 is the executed member
(`0.1.0-c022`); CAMPAIGN_023 (`0.1.0-c023`) is its scaffold-only ADX22 sibling.

---

## 1. C022 final metrics summary

All figures below are **as previously recorded** in the linked diagnostic
artifacts; nothing here is recomputed or restated as new evidence.

### 1.1 Expectancy / verdict

- **CAMPAIGN_022 verdict: REJECT.** Realized price-based expectancy
  **−0.1402R** (per [`DIAGNOSTIC_STOP_MODEL_COMPARISON_EXECUTED.md`](DIAGNOSTIC_STOP_MODEL_COMPARISON_EXECUTED.md)
  baseline sanity check); cost-free simulated 2.0×ATR baseline expectancy
  **−0.0732R** — still negative even with no spread/slippage.
- Overall win rate **32.6%** across 2396 base train+validation trades
  (train 1369, validation 1027), per
  [`C022_WINNER_LOSER_FEATURE_SEPARATION_001_SUMMARY.md`](C022_WINNER_LOSER_FEATURE_SEPARATION_001_SUMMARY.md).

### 1.2 Stop / time behavior (stop-model comparison)

From [`DIAGNOSTIC_STOP_MODEL_COMPARISON_EXECUTED.md`](DIAGNOSTIC_STOP_MODEL_COMPARISON_EXECUTED.md)
(fixed C022 entries, exit rule varied, 2396 reconstructed paths):

| stop | expectancy_r | win_rate | mean_loss_r |
|---|---|---|---|
| 1.5×ATR | −0.0513 | 0.2892 | −0.7219 |
| 2.0×ATR (baseline) | −0.0732 | 0.3472 | −0.9294 |
| 2.5×ATR | −0.0637 | 0.4007 | −1.0984 |
| 3.0×ATR | −0.0777 | 0.4257 | −1.2292 |

| time-invalidation rule | expectancy_r | win_rate |
|---|---|---|
| no +0.25R by 8 bars | −0.0748 | 0.3205 |
| no +0.5R by 8 bars | −0.0603 | 0.3397 |
| no +0.5R by 12 bars | −0.0728 | 0.3364 |

**Every** ATR-multiple and **every** time-invalidation variant stays in a tight
negative band. Wider stops only enlarge `mean_loss_r`; tighter stops cut losses and
winners alike. **Stop geometry is not the lever.**

### 1.3 MFE/MAE findings

From [`CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md`](CAMPAIGN_022_MFE_MAE_STOP_DIAGNOSTICS.md)
(2311/2396 trades reconstructed; 85 dropped at data edges, no fabrication):

- Of hard-stopped trades: **45.9% never reached +0.25R** before being stopped
  (effectively straight-to-stop); 36.6% reached +0.5R first; mean MFE before stop
  **+0.47R**.
- Of profitable time-exit trades: mean MAE **−0.40R**; only **4.7%** ever touch
  −0.9R. Live winners rarely approach the stop.
- Overall excursion: mean MFE +1.12R, mean MAE −0.89R.
- Stop-outs are **not** concentrated by pair (hard-stop share 0.55–0.61 across all
  seven pairs) or side (long 0.59, short 0.58).

**Reading (as recorded):** a large plurality of trades are dead on arrival —
consistent with an entry-quality problem, not a stop-distance problem.

### 1.4 Winner/loser feature separation

From [`C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md`](C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md)
and [`C024_READINESS_FROM_C022_FEATURE_SEPARATION.md`](C024_READINESS_FROM_C022_FEATURE_SEPARATION.md)
(effect = |AUC−0.5|, reported train/validation):

| family | feature | AUC (train/val) |
|---|---|---|
| H4 regime | `h4_adx_at_entry` | 0.515 / 0.501 |
| H4 regime | `h4_bias_score` | 0.515 / 0.484 (direction unstable) |
| H4 regime | `h4_ema_slope_atr` | 0.500 / 0.497 |
| H4 regime | `h4_close_dist_ema50_atr` | 0.544 / 0.555 |
| H1 pullback | `h1_pullback_depth_atr` | 0.545 / 0.537 |
| H1 pullback | `h1_rsi_at_entry` | 0.509 / 0.501 |
| M15 trigger | `m15_reclaim_distance_atr` | 0.494 / 0.485 |
| M15 trigger | `m15_adx_at_entry` | 0.504 / 0.521 |
| M15 trigger | `m15_body_atr` | 0.497 / 0.478 |

- **Every structural entry-signal feature sits at AUC ≈ 0.50.** The strongest
  *stable signal-quality* effect (`h4_close_dist_ema50_atr`, |AUC−0.5| = 0.044) is
  **below the 0.05 negligibility floor**.
- The only separators above the floor are **context, not signal**:
  `spread_to_atr_pct` (cost, 0.077 — mechanical), `atr_at_entry` (volatility, 0.068),
  `hour` (time-of-day, 0.074). All weak (AUC ≲ 0.58). Cost shows a clean monotonic
  quintile decline (win-rate 0.43→0.25 as spread/ATR rises).

---

## 2. Why C022 is rejected

C022 is **REJECT** because its entries carry no edge, and the failure has now been
localized to the **entry signal**, not its surrounding mechanics:

1. **Negative expectancy survives every non-entry intervention.** Stop multiple,
   time-invalidation, and even a **cost-free mid-price baseline** all stay negative.
   If the problem were stop placement or cost, at least one of these would clear
   zero. None do.
2. **Live winners don't get stopped and dead trades don't get going.** 4.7% of
   time-exit winners touch −0.9R, while 45.9% of stop-outs never reach +0.25R — the
   signature of poor entry timing, not a mis-sized stop.
3. **No structural entry feature separates winners from losers.** The H4 regime, H1
   pullback, and M15 reclaim features the thesis is built on are all at AUC ≈ 0.50.
   There is no univariate handle to filter on.

The conclusion is consistent across four independent diagnostics: **C022's failure
is an entry-edge / signal-quality failure.**

---

## 3. Why C023 (ADX22) should not be executed now

C023's **only** difference from C022 is raising the H4 directional-bias ADX gate
from 20.0 → 22.0.

- **H4 ADX does not separate winners from losers.** `h4_adx_at_entry` is at AUC
  0.515 (train) / 0.501 (validation), and quintile win-rates by H4 ADX are flat
  (~0.30–0.35 across all quintiles). A stricter ADX gate would **only shrink the
  sample**, with no evidence it lifts outcomes.
- **ADX22 is not a structurally new thesis.** It is a threshold nudge on the same
  regime gate that already failed to separate. Executing it would be tuning a
  parameter the data says is inert — exactly the kind of move the freeze exists to
  prevent.

**Recommendation: do not execute C023.** It remains scaffold-only and deferred.

---

## 4. Why C024 is not ready

Per [`C024_READINESS_FROM_C022_FEATURE_SEPARATION.md`](C024_READINESS_FROM_C022_FEATURE_SEPARATION.md),
the readiness decision is **`NOT_READY`**:

- **No entry-time structural feature separated winners.** The readiness bar
  required at least one feature family to separate winners/losers in both train and
  validation with plausible non-overfit logic. Zero structural families clear it.
- **No justified filter hypothesis.** The only above-floor separators are context
  (cost/volatility/hour). Cost is mechanical (not an edge); volatility and hour are
  weak (AUC ≲ 0.58) and would be **post-hoc threshold mining** if selected from this
  same dataset. A ~5–6 AUC-point context filter would not plausibly turn a REJECT
  expectancy positive while keeping a usable sample.

There is therefore no evidential basis for a C024 that refines the
pullback-resolution signal. **No CAMPAIGN_024 is created.**

---

## 5. Retirement classification

**`C022_C023_FAMILY_RETIRED_OR_PAUSED` → recommended status: `RETIRED_UNLESS_NEW_EXTERNAL_THESIS`.**

The pullback-resolution family (H4 regime → H1 pullback → M15 EMA reclaim) is
**retired**. The "filter / re-gate the existing pullback signal" lever has been
shown empty: stop, time, ADX, and cost-free variants all stay negative, and no
structural entry feature carries winner/loser information. Continuing to tweak gates
on this signal (C023, and any C024 of the same shape) is not productive.

This is a retirement, not a permanent ban — but reopening requires a genuinely new
external thesis (see §6), not a threshold change.

---

## 6. What evidence would be required to reopen this family

Reopening C022/C023 (or opening a same-shaped C024) would require **all** of:

1. **A new external market-structure thesis** — a reason, sourced from outside this
   dataset, to believe the pullback-resolution context contains edge that the
   current encoding missed (e.g. a published order-flow / liquidity mechanism), not
   a re-reading of these same AUCs.
2. **A materially different trigger** — something structurally distinct from the M15
   EMA reclaim (which is at AUC ≈ 0.49), e.g. a sweep+displacement or break/retest
   confirmation, not a threshold or indicator-period change on the existing trigger.
3. **Independent evidence** — separation demonstrated out-of-sample on data **not**
   used to form the hypothesis, pre-registered before execution.
4. **Not just threshold changes** — re-gating ADX, EMA distance, RSI, pullback
   depth, or stop multiple on the same signal is explicitly **insufficient** and
   does not constitute a reopening case.

Absent all four, the family stays retired and no further C02x pullback-resolution
campaign should be opened.

---

## 7. What this memo does not do

- Does **not** change C022's REJECT verdict or any historical metric.
- Does **not** execute C023 or create CAMPAIGN_024.
- Does **not** approve any strategy; `configs/approved_strategies.yaml` stays
  `approved: []`.
- Does **not** enable paper/demo/live or touch broker/executor/order/live code.
- Does **not** present any context effect (cost/volatility/hour) as a tradable edge.
