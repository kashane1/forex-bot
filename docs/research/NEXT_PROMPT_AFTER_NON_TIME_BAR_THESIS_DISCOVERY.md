# Next prompt after non-time-bar thesis discovery

**Sprint:** `research-external-non-time-bar-thesis-discovery-001` · Phase 7
**Status:** drafted only — **do NOT execute in this sprint.**

The Phase-7 decision is **Option 2: run a front-gate screen on one shortlisted idea
(H16 · overshoot-exhaustion fade, fallback H03)**. The prompt below opens a
**front-gate screening** sprint **only** — it screens an idea through the
edge-discovery lab and returns a pass/block verdict. It **must not** create a campaign,
scaffold a strategy, approve anything, or open the test lockbox.

---

## Prompt — non-time-bar overshoot-exhaustion front-gate screen

```
We are starting a front-gate screening sprint from clean, updated origin/main.

Branch:
research-non-time-bar-overshoot-frontgate-001

Context:
- The non-time-bar lane is PAUSED. The thesis-discovery sprint
  (research-external-non-time-bar-thesis-discovery-001) produced a shortlist and chose
  ONE idea to screen first:
    PRIMARY  = H16 overshoot-exhaustion fade
    FALLBACK = H03 thin-move fade
    FILTER   = H12 spread-state (liquidity-regime) conditioning
  See: docs/research/NON_TIME_BAR_FINAL_SHORTLIST.md,
       docs/research/NON_TIME_BAR_NEXT_RESEARCH_DECISION.md,
       docs/research/NON_TIME_BAR_HYPOTHESIS_CATALOG.md (H16/H03/H12).
- H16 thesis: when a range/volatility bar completes with unusually large overshoot
  beyond its threshold (a violent single-candle completion), the next bar(s) tend to
  REVERSE (exhaustion). Pre-register BOTH directions: if the data show continuation,
  that is a separate, separately-registered hypothesis, not a saved result.

Goal:
Screen H16 (and, only if H16 blocks, H03) through the EXISTING edge-discovery front
gate (research/edge_discovery/): matched nulls, cost feasibility on the traded cell,
filter ablation (incl. H12), multiple-comparison, pair-holdout. Return a pass/block
verdict per FUTURE_CAMPAIGN_REENTRY_GATES.md (G1-G5) and the lane re-entry criteria.

This is a SCREEN, not a campaign. Hard rules:
- No campaign, no CAMPAIGN_030, no scaffold, no strategy approval, no edit to
  configs/approved_strategies.yaml, no paper/demo/live, no OANDA, no credentials, no
  test lockbox, no train/validation/test campaign evidence.
- Do not tune C029 or revive a rejected family.
- Use the local M1 corpus only; restrict to the C029 train window
  (2021-05-27..2023-12-31) so the lockbox is untouched.
- Trade-cell realism: cost-feasible threshold only (range >= 25-30 pip or volatility
  >= 50 pip per the feasibility study); H12 spread-state filter ON; close intraday
  (before the 17:00 NY rollover) so overnight financing (the CAMPAIGN_031 ~4x-spread
  channel) does not apply. Account for spread + slippage as in C029.
- Commit only compact diagnostics, summaries, docs, and tests. No raw M1, full bars,
  ledgers, DB dumps, .env, or credentials.

Method (pre-registered to avoid the C028 selection-noise trap):
0. Baseline audit; create branch; confirm approved_strategies empty + loops refuse;
   run pytest -q / ruff / check_research_freeze / validate_research_archive /
   scan_artifacts_for_secrets.
1. Build a thin, tested adapter that, from the existing non_time_bars builders, emits
   (event timestamp, overshoot_pips, side) and computes forward returns over the next
   1/2/3 bars at the cost-feasible cell, on >= 2 pairs (G5). Reuse the feasibility
   overshoot metric; do not duplicate bar builders.
2. Run the edge-discovery lab on H16: forward-return information, MATCHED null
   (geometry-matched, holding the move fixed so the OVERSHOOT conditioning is what is
   tested), cost-feasibility on the traded cell, filter-ablation for H12, and the
   multiple-comparison best-of-N check across the (<= small, pre-declared) cells.
3. Verdict per G1-G5. If H16 blocks, run the identical screen on H03 ONCE; if both
   block, record the lane as exhausted on current data (new data required to reopen).
4. Write a PASS/BLOCK result doc + a compact diagnostics artifact; update the lane
   status docs. Do NOT create a campaign even on PASS — a PASS only authorises a future
   fresh pre-committed scaffold sprint, separately.
5. Final validation (the five validators) + a summary doc.

Deliver: branch name, commit hashes per phase, files changed, the lab flags for each
gate, the H16 (and if run, H03) verdict, explicit confirmation that no campaign was
created and nothing was approved, and the recommended next step (scaffold-prompt draft
ONLY if PASS; otherwise keep-paused / new-data-required).
```

---

## Why this prompt opens a screen and not a campaign

Per the lane decision and the front-gate process, an idea earns a campaign **only after**
it passes the front gate. This prompt runs exactly that screen and stops at a verdict.
On PASS it authorises *a separate future scaffold sprint* (with its own fresh
pre-commit and a newly-assigned campaign number — **not** retroactively 030/031); on
BLOCK it moves the lane toward retire/new-data-required. No step here creates or
implies a campaign.
