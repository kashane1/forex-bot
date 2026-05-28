# USD_JPY M15 Microstructure-Confirmation — Entry Lane Closeout

**Date:** 2026-05-28 · **Sprint:** `research-usdjpy-m15-microstructure-confirmation-diagnostic-001`
**Type:** research closeout. Approves nothing, changes no verdict, tunes nothing,
creates no campaign, claims no edge.

> This memo closes the USD_JPY M15 microstructure-confirmation lane **as an
> entry-alpha path**. It changes no verdict (C022 stays REJECT, C023 stays
> scaffold-only), creates no CAMPAIGN_024, and approves nothing. It records what
> remains potentially useful — post-entry behavior, for **trade management only**.

Inputs:
[`USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_001_SUMMARY.md`](USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_001_SUMMARY.md),
[`USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_RESULT.md`](USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_RESULT.md),
[`USDJPY_C024_READINESS_DECISION.md`](USDJPY_C024_READINESS_DECISION.md).

---

## 1. Diagnostic summary

USD_JPY-only, read-only, over the C022 base trade set:

- **306 USD_JPY C022 base trades** — train 133, validation 173.
- **MFE/MAE reconstructed: 299 OK / 7 NO_BARS** (no fabrication for the 7 data-edge trades).
- **172 hard stops / 134 time exits**; straight-to-stop 79 (45.9% of hard stops).
- **Near-flat outcome:** win rate 0.379; mean R −0.0005 (train −0.0017, validation +0.0004).
  USD_JPY is "less bad," **not** positive.
- **No live M15 detector had material, stable winner/loser separation.** Continuous-score
  winner AUCs (train/validation): `reclaim_plus_impulse` 0.491/0.433,
  `reclaim_plus_micro_swing_break` 0.470/0.486, `range_expansion_after_compression`
  0.484/0.383 (all stable but negligible), `liquidity_sweep_plus_displacement`
  0.465/0.583 (direction-**unstable**).
- **Best stable live effect = |AUC−0.5| 0.016** (range-expansion) — **below the 0.05
  action floor**, and the old EMA20-reclaim baseline is itself inert/unstable
  (0.539/0.486).
- **The only above-floor separation was post-entry:** `reclaim_plus_retest_hold`
  (AUC 0.611/0.552, effect 0.052) and `failed_reclaim_or_trap` — both inspect
  post-entry bars (`uses_post_decision=True`) and cannot gate a live entry.

## 2. Decision

- **USD_JPY M15 microstructure confirmation is CLOSED as an entry-alpha lane.**
- **C024 remains `NOT_READY`** (USD_JPY-only). No CAMPAIGN_024 is created.
- **C023 remains deferred / not executed.**

## 3. Why

1. **Live entry primitives did not outperform the old EMA reclaim in a usable way.**
   Every live primitive is either negligible (|AUC−0.5| ≤ 0.016, below the floor) or
   direction-unstable across train/validation. None clears, let alone beats, a trigger
   that is itself inert.
2. **Post-entry separation cannot be a live entry trigger.** The only above-floor
   signal (retest-hold/trap) is observed *after* entry — it describes what already
   happened (winners hold their reclaim; losers trap) and is partly tautological with
   the outcome. It is not available at the entry decision bar.
3. **Small sample, high overfit risk.** USD_JPY per-split samples are small (winners
   46 train / 70 validation); the one stable boolean lift (sweep+displacement,
   +0.10/+0.14 win-rate) sits on an 81%-present majority with a tiny "absent" group
   (23/34), an unstable continuous AUC, and **no** straight-to-stop reduction. A large
   effect on one small pair is a reason for more scrutiny, not less. Selecting any cut
   here would be threshold mining.

## 4. What remains potentially useful (trade management only, not entry alpha)

The post-entry retest-hold / trap behavior **separated outcomes** even though it cannot
gate an entry. That makes it a candidate for **trade-management diagnostics** — used
*after* a trade is already open, never to decide whether to enter:

- **Early invalidation** — exit when an early trap (close back through the reclaimed
  level against the trade) appears, before the full stop is reached.
- **Hold / exit decision** — keep trades that hold their post-entry retest; cut those
  that do not continue.
- **Stop-avoidance** — whether early-trap exits reduce hard-stop losses.
- **Time-stop refinement** — whether "no continuation within N bars" is a useful early
  exit vs the current time stop.

These are **diagnostic hypotheses for a separate read-only sprint**, explicitly framed
as trade management, and must be tested out-of-sample and pre-committed before any use.
They are **not** entry alpha and do **not** reopen the entry lane.

## 5. Explicit statements (hard rules upheld)

- **No strategy approved** — `configs/approved_strategies.yaml` remains `approved: []`.
- **No paper/demo/live** — no broker/executor/order/live code touched; no OANDA calls.
- **No CAMPAIGN_024 created**; no thresholds drafted as parameters.
- **No verdict changed** — C022 REJECT, C023 scaffold-only, all prior verdicts intact;
  no historical metric rewritten.
- **USD_JPY is not presented as proven edge.** The post-entry behavior is a management
  *diagnostic hypothesis*, not a tradable rule.
