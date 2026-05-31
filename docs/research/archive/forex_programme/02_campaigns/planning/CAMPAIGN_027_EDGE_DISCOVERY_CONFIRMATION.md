# CAMPAIGN_027_EDGE_DISCOVERY_CONFIRMATION

**Status:** TRAIN/VALIDATION EXECUTION — Phase 6 / REJECT_TRAIN_GATE /
TEST_LOCKBOX_CLOSED / NOT_APPROVED. Branch
`research-campaign-027-h4-filtered-zscore-reversion-train-validation-001`.

Re-screens the campaign's **own** train ledgers through the edge-discovery lab
(`research/edge_discovery/`) — matched-null + filter-ablation — to test whether
the train evidence is random or filter-mined. (Validation modes were not run; train
failed the gates.)

> Inputs: `research/campaign_027/train_validation/matched_null_result.json`,
> `filter_ablation_confirmation.json`, `filter_stage_ledger.csv`. Lab modules:
> `research.edge_discovery.matched_nulls`, `.filter_ablation`, `.costs`.

---

## Matched-null results (train; post conservative cost; seeds 0–49; window 12 bars)

The lab reconstructs the strategy's forward log-return from the frame's close
prices at each trade's `entry_time` over `bars_held` — a timing/direction
**information** benchmark (close-to-close), deliberately distinct from the realized
`next_bar_open` post-cost PnL in the trade ledger (the plan's compatibility note).
Both strategy and null pay the same conservative overlay.

| mode | matched structure | strategy | null mean | percentile | flag |
|---|---|---|---|---|---|
| timestamp_random_same_pair | pair counts | +0.000392 | −0.000483 | 90 | ABOVE_MATCHED_NULL |
| session_matched_random | pair+side+session | +0.000392 | −0.000526 | 90 | ABOVE_MATCHED_NULL |
| full_matched_null | pair+side+session+weekday+hold | +0.000329 | −0.000286 | 90 | ABOVE_MATCHED_NULL |
| side_shuffled | entry bars fixed, sides permuted | — | — | 0 | WITHIN (degenerate) |

**Interpretation.** The entry timing and short direction carry **real information**:
on all three informative modes the strategy sits ~90th percentile, above the
structure-matched null. `side_shuffled` is **degenerate** for a short-only ledger
(every side is identical, so the shuffle reproduces the strategy) and is
uninformative here — expected, documented, not a failure.

**But this is the precommit's central caveat made concrete.** "Above the matched
null" means the strategy **loses less than random**, not that it **makes money**:
the null means are all *negative* (≈ −0.0003 to −0.0005), and the strategy's
information edge (+0.0003) is consumed by the realized execution frictions
(`next_bar_open` fill, the 3×ATR protective stop, and conservative financing-
inclusive cost). The realized post-cost expectancy is +0.00012 with PF 1.043 and a
negative 2× stress — failing the profit, year-robustness, and cost-stress gates.
**Information ≠ a tradable edge.**

So the matched-null *information* gate is satisfied (this was never the campaign's
weak point — the front gate already showed it beats all six nulls). It is **not**
why the campaign is rejected.

## Filter-ablation confirmation (train; value = fixed-horizon h12 log return)

Re-derives `FILTER_ADDS_EDGE` for each retained filter on the campaign's own
base-trigger funnel (trigger-only expectancy −0.00004947; all-filters n=113):

| filter | role | marginal gain | reduction | flag | front-gate gain |
|---|---|---|---|---|---|
| **f_low_vol** | retained | **+0.000572** | 0.671 | FILTER_ADDS_EDGE ✅ | +0.000301 |
| **f_quiet_session** | retained | **+0.000339** | 0.552 | FILTER_ADDS_EDGE ✅ | +0.000234 |
| **f_strong_extension** | retained | +0.000034 | 0.538 | **FILTER_ONLY_REDUCES_SAMPLE** ❌ | +0.000208 |
| f_cost_adv_pair | dropped | −0.000150 | 0.428 | FILTER_ONLY_REDUCES_SAMPLE (correctly dropped) | +0.000098 |
| f_long_side | dropped | −0.000372 | 0.514 | FILTER_HURTS_EDGE (correctly dropped → short-only) | −0.000199 |

**Interpretation.**

- **Two of three retained filters confirm.** `f_low_vol` and `f_quiet_session`
  re-derive `FILTER_ADDS_EDGE` on the campaign's own data, with marginal gains
  *larger* than the front gate — structurally robust (reversion works in calm,
  quiet regimes).
- **The third retained filter fails confirmation.** `f_strong_extension` (|z|≥2.5)
  adds only +0.000034 on the campaign's train fold (below the noise tolerance),
  versus +0.000208 in the front gate — it now merely **reduces the sample**. This
  is the pre-registered **filter forking-path risk** (3 of 5 filters retained
  post-ablation) materializing: a filter chosen on a prior screen does not survive
  re-derivation on an independent fold. It fails the filter-ablation train gate
  (kill condition #6).
- **The dropped filters behave as expected.** `f_long_side` still hurts edge
  (confirming short-only) and `f_cost_adv_pair` still only reduces sample
  (confirming the universe is not narrowed).

## Compatibility gaps

- `side_shuffled` is uninformative for a single-side ledger (noted).
- The matched-null information benchmark is close-to-close, not the realized
  `next_bar_open` post-cost PnL; the two are reported separately by design (no
  rolled-up-only gap, unlike C025/C026 — the campaign carries full per-signal and
  per-trade ledgers).
- Validation-fold matched-null / ablation were not computed (train gates failed;
  validation not run).

## Does C027 still satisfy the edge-discovery requirements?

**Partially, and not enough to proceed.** The *information* requirement (beats/above
the structure-matched null) holds, but the *filter-adds-edge* requirement fails for
`f_strong_extension`, and — decisively — the **realized post-cost edge does not
survive** (profit factor, year-robustness, 2× cost stress all fail). Edge-discovery
information was never sufficient on its own; the campaign existed to test whether it
became a *tradable* strategy on a clean split. It did not.

## No-approval statement

No strategy is approved. `configs/approved_strategies.yaml` stays `approved: []`.
The test lockbox was not opened; paper/demo/live remain blocked.
</content>
