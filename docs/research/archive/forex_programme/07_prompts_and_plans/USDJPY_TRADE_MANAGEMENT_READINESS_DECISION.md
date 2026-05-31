# USD_JPY Post-Entry Trade-Management Readiness Decision

**Date:** 2026-05-28 · **Sprint:** `research-usdjpy-post-entry-trade-management-diagnostic-001`
**Type:** diagnostic decision memo. Approves nothing, changes no verdict, tunes nothing,
creates no campaign, claims no edge. No CAMPAIGN_024 is created here.

Inputs:
[`USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_RESULT.md`](USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_RESULT.md),
[`USDJPY_POST_ENTRY_MANAGEMENT_COUNTERFACTUALS.md`](USDJPY_POST_ENTRY_MANAGEMENT_COUNTERFACTUALS.md),
`research/usdjpy_trade_management_diagnostic/{post_entry_analysis_summary.json,post_entry_counterfactuals.json}`.

---

## Decision

### `NOT_READY`

No live-manageable post-entry signal yields a net-useful early-invalidation / hold rule
on USD_JPY. The post-entry events that **descriptively** separate outcomes do **not**
survive a counterfactual early-exit test: acting on them **reduces** expectancy.

## Evidence against readiness

The seven-part bar requires a live-manageable post-entry event that (1) is stable across
train/validation, (2) reduces hard-stop/straight-to-stop behavior, (3) does not destroy
time-exit winners, (4) has plausible logic, (5) preserves sample, (6) does not rely on
hindsight, and (7) can be precommitted without threshold mining.

- **Descriptive separation exists but is not actionable.** EXIT-type events
  (`early_reclaim_failure`, `early_adverse_expansion` @ h2/h4, `no_continuation` @ h4,
  `trap_or_failed_breakout`) stably flag higher hard-stop rates and lower win rates among
  trades still open at the horizon. That satisfies a *descriptive* reading of (1)/(2) —
  but it fails the decisive test below.

- **Every predeclared early-exit rule makes expectancy WORSE (fails (3), and the point of
  the lane).** The counterfactual exited each flagged, still-open trade at the
  next-bar-open after the horizon (optimistic: perfect action, mid mark, no spread/slippage):

  | rule | Δ expectancy (train) | Δ expectancy (validation) |
  |---|---|---|
  | early_reclaim_failure @ h2 | −0.134R | −0.112R |
  | early_reclaim_failure @ h4 | −0.098R | −0.090R |
  | early_adverse_expansion @ h2 | −0.091R | −0.077R |
  | no_continuation @ h4 | −0.106R | −0.065R |
  | trap_or_failed_breakout @ h2 | −0.124R | −0.106R |

  All five are **negative on both splits**. The signals flag trades that are *more
  likely* to stop — but many of those trades recover before the stop, so exiting early
  locks in a loss that would not have been realized, and the rules additionally cut
  9–20 eventual winners per split (forfeiting ~0.7–4.5R of winner excursion). The
  loss-reduction does not outweigh the winner damage; **early-exiting hurts**, even under
  optimistic, cost-free marks. This directly violates (3).

- **The separation is largely tautological / already-priced.** "Closed back through the
  EMA," "no +0.25R yet," and "adverse-before-favorable" are partly mechanical correlates
  of an eventual loss; they carry little *incremental* information that the realized
  stop/time exit does not already capture. Conditioning on them and acting earlier
  removes optionality (the recoveries) without a compensating edge.

- **Hold-type signals add nothing actionable.** `reached_plus_05` raises win-rate
  (tautological — a trade already +0.5R tends to end positive); `early_retest_hold` is
  weak/unstable. Neither implies a hold/exit rule that improves on simply letting the
  trade run to its existing stop/time exit.

- **Small sample / hindsight.** USD_JPY subgroups are small once restricted to
  still-open trades; the only stronger separators (realized MAE-at-exit, full
  time-to-threshold) are hindsight-only and unusable (fails (6)). Selecting any horizon
  or cut to chase a positive delta would be threshold mining (fails (7)).

## Recommendation

**Close the USD_JPY post-entry trade-management lane.** The post-entry retest-hold/trap
behavior is a *descriptive* property of winners vs losers, not an actionable management
edge: every honest counterfactual early-exit rule reduces expectancy. Combined with the
closed entry lane and `NOT_READY` C024, this means USD_JPY microstructure — at both the
entry and the management layer — shows **no demonstrated, actionable edge**.

Next-step options (each a *fresh, pre-committed* diagnostic, not a campaign):

1. **Stop here / hold the freeze** — record USD_JPY microstructure (entry + management)
   as closed; pursue a genuinely new external thesis only when one appears. **Recommended default.**
2. **Different structural lane** — per
   [`NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md`](NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md),
   a thesis that changes *what is detected*, not another overlay on the C022 entry.

There is **no** sanctioned USD_JPY follow-up that continues mining these post-entry
signals; the counterfactual already shows acting on them is net-negative.

## What is NOT being done (hard rules upheld)

- No CAMPAIGN_024 created; no thresholds drafted as parameters; no rule adopted.
- No C023 execution; no C022 retune; no verdict changed; no historical metric rewritten.
- No strategy approved; `configs/approved_strategies.yaml` remains `approved: []`.
- No paper/demo/live; no broker/executor/order/live changes; no OANDA calls.
- USD_JPY is **not** presented as proven edge; post-entry diagnostics are **not** entry
  alpha and are **not** a tradable management rule.
