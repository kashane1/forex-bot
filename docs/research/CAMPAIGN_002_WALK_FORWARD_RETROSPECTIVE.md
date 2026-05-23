# CAMPAIGN_002 H4 — Walk-Forward Retrospective (Dry-Run, Metadata-Only)

**Date:** 2026-05-22 · **Branch:** `research-walk-forward-harness-001`
`strategy_evidence: false`

A **metadata-only** retrospective showing how the new walk-forward
harness ([`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
+ [`research/walk_forward/`](../../research/walk_forward/)) would
frame the already-rejected CAMPAIGN_002 H4 `trend_following 0.1.0`
baseline. No backtest was re-run. No CAMPAIGN_002 rule was changed.
No verdict was relabelled. **CAMPAIGN_002 remains REJECT.**

> Used here only as a worked example of the harness's plan and
> report structure. The reported per-fold metrics in §3 are
> **derived from the existing committed CAMPAIGN_002 evidence**
> (the bespoke 1,647-trade no-RiskEngine reference, the
> CAMPAIGN_002 report, the free / local verifier's accepted
> output) and are clearly labelled as such. Nothing in this doc
> generates a new trade list.

## 1. Why a retrospective on a rejected campaign?

Three reasons:

1. **Dogfood the harness shape.** Exercising the harness against
   a real-world campaign confirms that the
   `WalkForwardPlan` / `FoldMetrics` / `WalkForwardResults`
   schema is fit-for-purpose for the project's actual research
   workflow.
2. **Document what walk-forward would have shown.** CAMPAIGN_002
   was rejected on a single-window backtest. Framing it as a
   walk-forward result tells us whether the single-window REJECT
   verdict would have been an accident of one bad window (it
   wouldn't) or a consistent rejection across windows.
3. **Make the harness immediately useful** to whichever campaign
   uses it first as a real, freshly-run walk-forward — by
   producing a concrete reference of what the plan + report
   sections look like.

This is **not** a CAMPAIGN_002 revival. It does not change the
campaign's REJECT verdict. It does not approve any strategy.

## 2. Plan (produced by the harness)

Command (dry-run, output written outside the repo to `/tmp/`):

```bash
python scripts/run_walk_forward_dry_run.py \
    --campaign-name CAMPAIGN_002_RETROSPECTIVE \
    --universe-start 2020-01-01 --universe-end 2026-05-20 \
    --style rolling \
    --train-days 730 --validation-days 90 --test-days 365 \
    --step-days 365 \
    --output /tmp/wf_c002_retro/
```

Plan output:

- **Universe:** 2020-01-01 → 2026-05-20
- **Split style:** `rolling`
- **Parameter mode:** `frozen` (matches CAMPAIGN_002's already-frozen
  parameters — no per-fold fitting)
- **Fold count:** **4** (≥ 3 minimum)

| # | train | validation | test |
|---|---|---|---|
| 0 | 2020-01-01 → 2021-12-30 | 2021-12-31 → 2022-03-30 | 2022-03-31 → 2023-03-30 |
| 1 | 2020-12-31 → 2022-12-30 | 2022-12-31 → 2023-03-30 | 2023-03-31 → 2024-03-29 |
| 2 | 2021-12-31 → 2023-12-30 | 2023-12-31 → 2024-03-29 | 2024-03-30 → 2025-03-29 |
| 3 | 2022-12-31 → 2024-12-29 | 2024-12-30 → 2025-03-29 | 2025-03-30 → 2026-03-29 |

The plan passes `validate_plan` (4 folds ≥ 3; test windows
strictly forward; no consecutive test-window overlap; all
boundaries inside the universe).

For frozen-parameter strategies, the train / validation columns
are **documentation-only** — CAMPAIGN_002 has no fitting step;
the strategy uses the same frozen parameters
(`research/lean_parity/lean_parity_config.json`) on every fold's
test window.

Plan JSON:
`/tmp/wf_c002_retro/plan.json` (written outside the repo; not
committed; regenerable from the command above).

## 3. Metadata-only fold metrics (derived from existing evidence)

The retrospective does **not** run the bespoke engine again. The
existing committed CAMPAIGN_002 evidence covers the full window
2020-01-01 → 2026-05-20 as a single backtest — not as 4 windowed
sub-runs. To show the harness's per-fold reporting shape without
re-running anything, this section reports the **already-known
single-window verdict** annotated per fold by its calendar-year
test window:

| # | test window | already-known verdict |
|---|---|---|
| 0 | 2022-03-31 → 2023-03-30 | REJECT (within the full-window REJECT) |
| 1 | 2023-03-31 → 2024-03-29 | REJECT (within the full-window REJECT) |
| 2 | 2024-03-30 → 2025-03-29 | REJECT (within the full-window REJECT) |
| 3 | 2025-03-30 → 2026-03-29 | REJECT (within the full-window REJECT) |

These are **annotations**, not freshly-computed per-fold metrics.
Producing real per-fold metrics requires running the bespoke
engine against each fold's test window separately, which is the
job of the campaign code that would consume the plan — explicitly
out of scope for this retrospective (and CAMPAIGN_002 will not be
re-run).

If a future campaign uses this harness with real per-fold runs,
its `FoldMetrics` payloads will populate the per-fold
`total_trades`, `expectancy_r`, `return_pct`, etc. columns
described in
[`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
§8.

## 4. Aggregate metrics — what's known vs what would require a real run

What we already know from the full-window CAMPAIGN_002 evidence:

- **Aggregate verdict (full window):** REJECT.
- **Aggregate expectancy R (full window, RiskEngine-gated):**
  −0.085 R.
- **Aggregate return % (full window, RiskEngine-gated):** −1.02 %.
- **Full-window total trades (RiskEngine-gated):** 1,032
  (CAMPAIGN_002 report).
- **Full-window total trades (no-RiskEngine):** 1,647 (bespoke
  reference); 1,655 (free / local verifier; WARN-band agreement).

What would require a real per-fold run:

- `fold_metrics[*].total_trades` (per-fold trade counts).
- `fold_metrics[*].expectancy_r` (per-fold expectancy).
- `fold_metrics[*].return_pct`.
- `aggregate.aggregate_expectancy_r` (trade-weighted across the
  4 fold test windows).
- `aggregate.aggregate_return_pct` (compounded across windows).
- `aggregate.fold_pass_rate` against any pre-committed gate.

Per the retrospective's metadata-only scope, none of these are
produced here.

## 5. What the retrospective tells us (without re-running)

- The harness produces a clean, structurally-valid 4-fold rolling
  plan for the CAMPAIGN_002 universe.
- For a campaign whose single-window verdict is REJECT with
  negative expectancy on every pair (as CAMPAIGN_002 is), the
  per-fold expectation is **REJECT in every fold under the
  strict-pass interpretation** — the single-window expectancy is
  negative, the universe-wide negative-edge claim is supported by
  two independent engines, and there is no reason to expect any
  individual ~1-year test window to flip the verdict.
- A real walk-forward run is therefore expected to:
  - Pass plan-validation cleanly.
  - Report `fold_pass_rate = 0 / 4 = 0.0`.
  - Report `aggregate_expectancy_r` negative (matching the
    full-window expectancy).
  - Produce **overall verdict: REJECT** under both the strict-pass
    rule and the aggregate-expectancy rule.

If those expected numbers were instead observed (e.g. one fold
showing positive expectancy while the others are negative), that
would be the §9 "variance across folds masks a single lucky
fold" rejection case and would still be REJECT — but for a
different reason.

## 6. What this does not do

- It does **not** re-run the CAMPAIGN_002 backtest.
- It does **not** change CAMPAIGN_002's REJECT verdict.
- It does **not** modify any campaign config, report, or
  `configs/approved_strategies.yaml`.
- It does **not** produce real `FoldMetrics` numbers.
- It does **not** approve any strategy.
- It does **not** lift the research freeze.

## 7. Local files created but not committed

- `/tmp/wf_c002_retro/plan.json` — harness plan JSON for the
  retrospective (outside repo, not staged).
- `/tmp/wf_c002_retro/plan.md` — harness plan markdown (outside
  repo, not staged).

`git status` shows only this single doc file as the change.

## 8. Cross-links

- Protocol:
  [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- Harness package:
  [`research/walk_forward/README.md`](../../research/walk_forward/README.md)
- Dry-run script:
  [`scripts/run_walk_forward_dry_run.py`](../../scripts/run_walk_forward_dry_run.py)
- CAMPAIGN_002 evidence:
  - Verifier accepted status: [`FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md)
  - Mapping spec: [`CAMPAIGN_002_LEAN_MAPPING_SPEC.md`](CAMPAIGN_002_LEAN_MAPPING_SPEC.md)
  - CAMPAIGN_002 report: [`backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md`](../../backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md)
- Next research direction:
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
