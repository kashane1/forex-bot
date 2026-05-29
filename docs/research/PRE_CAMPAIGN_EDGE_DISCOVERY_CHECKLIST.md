# PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST

**Status:** process doc (binding). A copy-per-idea checklist to fill in *before*
asking for a campaign. Diagnostic/governance only — approves nothing, opens no
test lockbox.

> Decisions reference lab flags from `research/edge_discovery/`. See
> [`FUTURE_CAMPAIGN_REENTRY_GATES.md`](FUTURE_CAMPAIGN_REENTRY_GATES.md) for the
> binding gate phrasing.

---

Copy this block, fill it in, attach the lab artifacts. An idea earns a campaign
only when every "deserves a campaign?" sub-answer is yes.

```
Idea: <one-line description — signal, filters, exits, pairs, timeframe, session>
Thesis source: <external thesis / market fact / prior diagnostic — NOT a tweak>
Precommitted before any run? <yes/no>   (must be yes)

1. DATA COVERAGE
   - Pairs × timeframe available locally? <yes/no — which store>
   - Date span and any gaps? <...>
   - Enough bars for the forward window + warmup? <yes/no>

2. COST FEASIBILITY            [cost_feasibility]
   - spread/ATR on target timeframe/session: <ratio>
   - flag: <COST_FEASIBLE | COST_HOSTILE | TIMEFRAME_TOO_FAST | SESSION_HOSTILE>
   - min target R to overcome cost: <value>
   - PASS only if COST_FEASIBLE on the cell we will actually trade.

3. SIGNAL INFORMATION          [windows.compute_forward_returns]
   - mean fwd log-return by horizon (1/3/6/12/24 bars): <...>
   - directional or mean-reverting? <...>
   - flag: <DIRECTIONAL_SIGNAL_PRESENT | NO_FORWARD_RETURN_EDGE | INCONCLUSIVE_SPARSE>

4. MATCHED NULL                [matched_nulls.matched_null_baseline]
   - mode(s) matching the thesis structure: <...>
   - strategy expectancy vs null (post-cost): <...>
   - prob_null_ge_strategy / percentile: <...>
   - flag: <BEATS_MATCHED_NULL | ABOVE_MATCHED_NULL | WITHIN/BELOW_MATCHED_NULL>
   - PASS only if it beats the *structure-matched* null, not just a generic one.

5. FILTER CONTRIBUTION         [filter_ablation]
   - per filter: marginal gain, reduction ratio, flag
   - flags: <FILTER_ADDS_EDGE | FILTER_ONLY_REDUCES_SAMPLE | FILTER_HURTS_EDGE | FILTER_TOO_SPARSE>
   - PASS only if every retained filter ADDS_EDGE.

6. EXIT DECOMPOSITION          [studies/exit_asymmetry_*]
   - real/null entry × real/null exit expectancies: <...>
   - flag: <ENTRY_EDGE_PRESENT | EXIT_EDGE_PRESENT | BOTH_NO_EDGE | COST_DOMINATED>
   - PASS only if the claimed source of edge (entry or exit) is the one present.

7. MULTIPLE-COMPARISON RISK    [multiple_comparison.matrix_sanity]
   - n variants screened: <N>
   - best vs null / best-of-N noise: <...>
   - flag: <ROBUST_MATRIX_SIGNAL | LIKELY_SELECTION_NOISE | TOO_MANY_VARIANTS_FOR_EVIDENCE>
   - PASS only if not selection noise.

8. PAIR/TIMEFRAME/SESSION CONCENTRATION
   - top-pair concentration: <...>
   - pair-holdout sign flip? <yes/no>  (FRAGILE_SINGLE_PAIR_RESULT)
   - time-block-holdout sign flip? <yes/no>  (FRAGILE_TIME_BLOCK_RESULT)
   - PASS unless precommitted single-pair research.

9. EXPECTED TRADE COUNT
   - projected trades on train/validation: <...>
   - enough to reach campaign gate minimums? <yes/no>

10. FAILURE CONDITIONS HIT?  (any one is a block)
   - [ ] COST_HOSTILE / TIMEFRAME_TOO_FAST on target
   - [ ] WITHIN/BELOW_MATCHED_NULL
   - [ ] BOTH_NO_EDGE
   - [ ] all filters FILTER_ONLY_REDUCES_SAMPLE
   - [ ] LIKELY_SELECTION_NOISE / TOO_MANY_VARIANTS_FOR_EVIDENCE
   - [ ] FRAGILE_SINGLE_PAIR_RESULT (without single-pair mandate)

DESERVES A FULL CAMPAIGN?  <yes/no>
   yes  → scaffold per FUTURE_STRATEGY_SEARCH_WORKFLOW step 7; emit the
          artifacts in FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.
   no   → one-line rejected-idea note in FUTURE_RESEARCH_BACKLOG (idea, the
          diagnostic that killed it, the flag, the lesson). No campaign.
```

## Notes

- The checklist measures **one precommitted idea**. It is not a search over
  variants to find one that passes (that is parameter mining — see the
  protocol).
- All steps run on **screening data only**; the test lockbox stays sealed.
- A "no" is a success of the process: it cost a checklist, not a campaign.
