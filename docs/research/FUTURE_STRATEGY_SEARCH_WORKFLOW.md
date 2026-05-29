# FUTURE_STRATEGY_SEARCH_WORKFLOW

**Status:** process doc (binding). The end-to-end order of operations for future
strategy search, with the edge-discovery lab as the cheap front gate.
Diagnostic/governance only — approves nothing, opens no test lockbox.

> See [`EDGE_DISCOVERY_PROTOCOL.md`](EDGE_DISCOVERY_PROTOCOL.md),
> [`FUTURE_CAMPAIGN_REENTRY_GATES.md`](FUTURE_CAMPAIGN_REENTRY_GATES.md),
> [`PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md`](PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md).

---

## The workflow

Steps 1–6 are **cheap lab screening** (hours, local data, no campaign). A
campaign is only scaffolded at step 7, and only if steps 1–6 clear the re-entry
gates.

1. **Market / opportunity map.** Where is the idea even tradable? Run
   `cost_feasibility` across pairs/timeframes/sessions and the existing
   session/pair studies. Discard cost-hostile cells now (C025/C026 lesson).
   *Lab:* `cost_feasibility.py`, `studies/study_session`, `study_pair_baseline`.
2. **Signal forward-return diagnostic.** Does the signal point anywhere over the
   horizons it will trade? *Lab:* `windows.compute_forward_returns`.
3. **Filter ablation.** Keep only filters that add edge, not sample shrinkage.
   *Lab:* `filter_ablation.py`.
4. **Matched-null benchmark.** Beat a null that reproduces the idea's own
   structure, post-cost. *Lab:* `matched_nulls.py`.
5. **Entry/exit decomposition.** Locate the edge (entry vs exit vs neither).
   *Lab:* `studies/exit_asymmetry_*`.
6. **Multiple-comparison sanity.** If variants were screened, confirm the best
   is not selection noise and survives pair/time-block holdout. *Lab:*
   `multiple_comparison.py`.

   → **Gate review** ([`FUTURE_CAMPAIGN_REENTRY_GATES.md`](FUTURE_CAMPAIGN_REENTRY_GATES.md)).
   If any gate blocks, stop and write a one-line rejected-idea note. Do **not**
   scaffold a campaign.

7. **Scaffold a campaign** (only for ideas that cleared the gates). Precommit
   the full rule set, pairs, timeframe, session, fill timing (`next_bar_open`),
   gates, and split windows **before** any run. Emit the artifacts in
   [`FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md`](FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md)
   so the lab can re-screen the campaign later.
8. **Train / validation.** Select the champion on **train only**; validation is
   confirmation, never parameter selection.
9. **Backtrader parity.** Verify engine parity at `next_bar_open` before any
   lockbox consideration.
10. **Test lockbox.** Open only after 7–9 pass, exactly once, per the campaign's
    precommit. Lab diagnostics never touch the lockbox.
11. **Promotion review.** A human reviews a cleared campaign and may add it to
    `configs/approved_strategies.yaml`. This is the only path to paper/demo/live
    and remains outside the lab.

## What changed vs. the old loop

Old loop: idea → full campaign → REJECT (most of the time), at days of cost
each. New loop: idea → hours of lab screening → gate review → campaign only for
survivors. The cost of a "no" drops from a campaign to a note. C025 (M5
cost-defeated) and C026 (cost-ladder, still no edge) would both have been
"no"s at step 1 / step 4.

## Invariants that never move

- `configs/approved_strategies.yaml` stays `approved: []` until step 11.
- No paper/demo/live until step 11.
- Test lockbox sealed until step 10.
- The lab is import-isolated and emits no verdict words.
- C011 remains the null benchmark; C025/C026 remain REJECT.
