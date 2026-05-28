# Next-Sprint Prompt — USD_JPY Post-Entry Trade-Management Diagnostic

**Date:** 2026-05-28 · **Sprint:** `research-usdjpy-m15-microstructure-confirmation-diagnostic-001`
**Type:** prompt draft. This file *contains* the next sprint's prompt; it executes nothing itself.

> Copy the fenced block below verbatim into Claude/Cursor to run the next sprint. It is
> a **read-only USD_JPY post-entry trade-management diagnostic**. The entry lane is
> already CLOSED (see
> [`USDJPY_MICROSTRUCTURE_ENTRY_LANE_CLOSEOUT.md`](USDJPY_MICROSTRUCTURE_ENTRY_LANE_CLOSEOUT.md));
> this follow-up treats post-entry retest-hold/trap and early MFE/MAE behavior as
> possible **trade-management** information (early invalidation / hold / stop-avoidance
> / time-stop), **explicitly not entry alpha**. It creates no C024, executes no C023,
> implements no strategy, runs no campaign, approves nothing, and touches no
> paper/demo/live or broker/executor/order/live code.

---

```text
We are starting a forex-bot READ-ONLY USD_JPY post-entry TRADE-MANAGEMENT diagnostic sprint.

Branch/worktree:
Create a fresh worktree from current `main` (or from the USD_JPY microstructure branch
HEAD if not yet merged — do NOT go back to a main that lacks the closeout docs).

Branch name:
research-usdjpy-post-entry-trade-management-diagnostic-001

This is NOT a strategy implementation sprint.
This is NOT C024 (do not create CAMPAIGN_024).
This is NOT C023 execution.
This is NOT an entry-signal / entry-alpha sprint — the USD_JPY entry lane is CLOSED.
This is NOT paper/demo/live enablement.
This is NOT approval.
This is USD_JPY ONLY.

Context:
The USD_JPY M15 microstructure-confirmation ENTRY lane is closed: no live entry
primitive showed material, stable winner/loser separation, and none beat the inert
EMA20-reclaim trigger (C024 = NOT_READY). The ONLY above-floor separation was
POST-ENTRY (retest-hold AUC 0.611/0.552; failed-reclaim/trap) — observed after entry,
so it cannot gate an entry. This sprint asks a different, honest question: can that
post-entry behavior be used for TRADE MANAGEMENT (deciding to exit early or hold a
trade that is ALREADY open), without claiming any entry edge? See:
  docs/research/USDJPY_MICROSTRUCTURE_ENTRY_LANE_CLOSEOUT.md
  docs/research/USDJPY_C024_READINESS_DECISION.md
  docs/research/USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_001_SUMMARY.md
Reuse the existing read-only artifacts and modules — do not edit strategy logic:
  src/forex_bot/research/microstructure_confirmations.py  (detectors, incl. post-decision)
  src/forex_bot/research/mfe_mae.py                       (per-trade MFE/MAE path)
  scripts/build_usdjpy_microstructure_diagnostic_dataset.py (USD_JPY per-trade dataset)

Main goal:
Determine, READ-ONLY, whether post-entry retest-hold/trap and early MFE/MAE behavior
can identify USD_JPY trades that should be exited early or held — i.e. whether an
early-invalidation / hold-management rule would diagnostically improve outcomes —
WITHOUT claiming entry alpha and WITHOUT threshold-mining a tradable rule. End with a
trade-management readiness classification.

Hard rules:
* Do not create CAMPAIGN_024.
* Do not execute C023.
* Do not implement a trading strategy or edit any strategy's entry/exit logic.
* Do not run a campaign.
* Do not change any campaign verdict or rewrite historical metrics.
* Do not modify configs/approved_strategies.yaml except to verify it stays approved: [].
* Do not enable paper/demo/live; do not modify broker/executor/order/live behavior.
* Do not call OANDA mutation/order APIs; do not use live trading credentials.
* Do not commit .env, credentials, DBs, raw candle dumps, huge CSVs, or bulky artifacts
  (gitignore the per-trade dataset; commit only manifest + small preview + summary JSON).
* USD_JPY ONLY. Use the existing C022 USD_JPY trade records and M15 paths.
* Treat ALL post-entry signals as trade-management-only. Never reintroduce them as
  entry features and never present any of this as entry alpha.
* Do not threshold-mine an exit rule and present it as tradable. Any candidate rule is a
  pre-committed, out-of-sample hypothesis only.
* Distinguish, for every signal: live-manageable post-entry information (knowable in
  real time while the trade is open) vs hindsight-only diagnostics (knowable only at/after
  exit). Only live-manageable information could ever become a management rule.

Work in phases. Commit after each meaningful phase.

PHASE 0 — branch, audit, plan
1. Create the branch above from the closeout HEAD (not an older main).
2. Verify: C020/C021/C022 REJECT; C023 scaffold-only/not executed; C024 absent;
   approved_strategies.yaml is approved: []; paper/demo/live guards intact.
3. Confirm the USD_JPY C022 trades + materialized M15 store are reachable READ-ONLY and
   the existing USD_JPY microstructure dataset rebuilds (306 trades).
4. Run baselines: pytest tests/ -q; ruff check src tests scripts research;
   python scripts/check_research_freeze.py; python scripts/validate_research_archive.py;
   python scripts/scan_artifacts_for_secrets.py. Document pre-existing skips.
5. Create docs/research/USDJPY_TRADE_MANAGEMENT_DIAGNOSTIC_001_PLAN.md (purpose,
   USD_JPY-only scope, trade-management-not-entry framing, signal list, live-vs-hindsight
   policy, readiness bar, validation commands, explicit no-C024/no-approval/no-entry-alpha
   statement). Commit.

PHASE 1 — post-entry signal inventory
Create docs/research/USDJPY_POST_ENTRY_SIGNAL_INVENTORY.md. For each post-entry signal,
give a precise definition, the bar(s) it is knowable, and a live-manageable vs
hindsight-only classification:
  * retest-hold after entry (reclaimed level holds within N bars),
  * failed reclaim / trap (close back through reclaim level against the trade),
  * no continuation within N bars (no progress toward +R),
  * adverse close through reclaim level,
  * early MFE failure (no +0.25R/+0.5R reached within N bars),
  * early MAE expansion (adverse excursion past a level within N bars),
  * post-entry range contraction/expansion.
Commit.

PHASE 2 — read-only post-entry feature extraction
Reuse src/forex_bot/research/microstructure_confirmations.py (post-decision detectors)
and mfe_mae.py. Extend the USD_JPY dataset with per-trade, per-horizon post-entry
features (e.g. state at +2/+4/+6/+8 M15 bars after entry), each tagged
live-manageable vs hindsight-only. Add unit tests for any new extraction. Gitignore the
full dataset; commit manifest + small preview + summary JSON only. Commit.

PHASE 3 — early-invalidation / hold-management analysis
Create scripts/analyze_usdjpy_trade_management.py. For each candidate management signal,
compute DIAGNOSTICALLY (no rule is adopted):
  * would acting on it (early exit) reduce hard-stop losses? by how much R?
  * would it cut winners too early? (lost favorable R on trades that would have won)
  * net diagnostic expectancy change vs the realized C022 USD_JPY outcome,
  * train vs validation stability of the effect,
  * USD_JPY sample size retained at each horizon,
  * separation of "should-exit" vs "should-hold" using ONLY live-manageable info.
Report the realized USD_JPY baseline (mean R near-flat) and every counterfactual as a
DIAGNOSTIC delta, never as a tradable result. Output:
  research/usdjpy_trade_management_diagnostic/analysis_summary.json
  docs/research/USDJPY_TRADE_MANAGEMENT_DIAGNOSTIC_RESULT.md
Be explicit: counterfactual early-exit deltas are optimistic (they assume the signal is
acted on perfectly) and are NOT net of the entry problem already documented. Commit.

PHASE 4 — trade-management readiness decision
Create docs/research/USDJPY_TRADE_MANAGEMENT_READINESS_DECISION.md. Classify:
  * TRADE_MANAGEMENT_PRECOMMIT_READY — a live-manageable post-entry signal stably
    reduces hard-stop losses without cutting winners materially, on adequate sample,
    with plausible logic and no threshold mining; would justify a SEPARATE pre-committed
    out-of-sample trade-management study (still not a campaign, still not C024).
  * DEFER_PENDING_MORE_DIAGNOSTICS — suggestive but unstable / small-sample / hindsight-
    dependent.
  * NOT_READY — no live-manageable signal helps, or only hindsight-only signals separate.
Apply strict criteria; default to the more conservative class when unsure. Create NO
CAMPAIGN_024, propose NO thresholds as parameters, approve nothing. Commit.

PHASE 5 — final validation + summary
Run pytest / ruff / check_research_freeze / validate_research_archive /
scan_artifacts_for_secrets / git status --short. Verify: no verdict changed; no strategy
approved; approved_strategies.yaml still approved: []; no C024 created; C023 not executed;
no paper/demo/live; no broker/executor changes; no OANDA mutation/order calls; no
credentials/DBs/huge artifacts staged. Create
docs/research/USDJPY_TRADE_MANAGEMENT_DIAGNOSTIC_001_SUMMARY.md (branch, commit hashes by
phase, files by phase, signals tested, live-manageable vs hindsight split, hard-stop-
reduction vs winners-cut tradeoff, train/validation stability, sample sizes, readiness
classification, what would justify a future pre-committed trade-management study,
verification that nothing was approved/executed, tests run, pre-existing skips, files to
review first, recommended next sprint). Commit.
```

---

## Notes for whoever runs the above

- **Trade management, not entry alpha.** Every signal here is knowable only after a
  trade is open. Nothing in this sprint reopens the closed USD_JPY entry lane or claims
  USD_JPY has edge.
- **Counterfactuals are optimistic.** Early-exit deltas assume the management signal is
  acted on perfectly and do not net out the entry-edge problem already documented —
  report them as diagnostic, never tradable.
- **Live-manageable vs hindsight.** Only signals knowable in real time while the trade is
  open could ever become a management rule; clean MFE/MAE-at-exit style fields are
  hindsight-only and must be labelled as such.
- The sprint ends at a readiness classification; even `TRADE_MANAGEMENT_PRECOMMIT_READY`
  only unlocks a *separate* pre-committed, out-of-sample study — never a campaign or C024
  inside this diagnostic.
