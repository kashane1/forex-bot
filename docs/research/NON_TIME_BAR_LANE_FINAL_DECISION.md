# Non-time-bar lane — final decision (Phase 7)

**Sprint:** `research-non-time-bar-thin-move-frontgate-001` · Phase 7
**Type:** lane-level decision. Docs only. No campaign, no approval, no code change.

---

## Decision

# `RETIRE_DIRECTIONAL_NON_TIME_BAR_SEARCH` on the current corpus

With **H03 (thin-move fade) → `FAIL_FRONT_GATE`** joining **H16 (overshoot-exhaustion
fade) → `FAIL_FRONT_GATE`**, the non-time-bar thesis-discovery sprint's pre-registered
**stop-criterion is met**:

> *"if both H16 and the H03 fallback fail matched-null-post-cost on ≥ 2 pairs,
> directional/conditional non-time-bar search is exhausted on this corpus; reopen only
> with new data."* — `NON_TIME_BAR_THESIS_DISCOVERY_001_SUMMARY.md` / `NEXT_PROMPT_AFTER_H16_FRONTGATE.md`

The directional / microstructure non-time-bar search is therefore **retired on the data
we have.** The infrastructure is **kept** (it is tested and lookahead-free); only the
*search* is closed.

## Why retire (the evidence is now overwhelming)

The non-time-bar lane was opened to ask whether a better *clock* (range/volatility bars,
event sampling) would surface an edge that time bars missed. Across the whole programme
the answer has been consistently **no edge, only a cost gradient**:

| stage | result |
|---|---|
| Feasibility (7 pairs × 13 thresholds) | cost-feasibility is threshold-specific; **cost-feasible ≠ edged** — no edge demonstrated |
| C029 (10-pip USD_JPY range-bar campaign) | `REJECT_TRAIN_GATE` — gross +0.084R but **net −0.019R**, fully cost-defeated |
| C026 (M3–M30 timeframe ladder) | REJECT — cost/expectancy improve as TF slows but best cell still net-negative |
| C031 (vol-managed TSMOM, portfolio) | `WITHIN_NULL` + financing-defeated; TSMOM direction null on these 7 USD majors |
| **H16** overshoot-exhaustion fade (screen) | **`FAIL_FRONT_GATE`** — no gradient, rev ≈ 0.50, cost-defeated, null-internal |
| **H03** thin-move fade (screen) | **`FAIL_FRONT_GATE`** — non-monotone, rev ≈ 0.50, cost-defeated 2/3 pairs, null-internal, confounded by H16 overshoot |

And the broader repo has independently rejected **breakout** (C015/017/025/029),
**pullback** (C020–023), **price-level reversion** (C008/027), **cross-sectional
momentum** (C016), **time-series momentum** (C031), and **relative-value/cointegration**
(C028) on this same 7-major M1 corpus. Phase-3 external research (web-cited, in
`NON_TIME_BAR_LITERATURE_REVIEW.md`) found **no public out-of-sample non-time-bar trading
edge in spot FX**; alt bars are a *sampling* improvement, not an edge source, and FX
"volume" is only a tick-count proxy.

The two screens that remained — completion-geometry (H16) and move-quality/participation
(H03) — were the cheapest, most distinct, financing-free microstructure ideas on the
shortlist. Both failed cleanly. Continuing to mine this corpus would be **variant
hunting against a freeze**, the exact C028 selection-noise anti-pattern.

## What is NOT being retired

- **Infrastructure stays.** `forex_bot.data.non_time_bars` (range + volatility bar
  builders), the feasibility analyzer, the H16 + H03 screen harnesses, and their tests
  remain in the tree — deterministic, lookahead-free, reusable the moment a *new thesis
  or new data* justifies them.
- **The front-gate discipline stays.** The lab (`research/edge_discovery/`) and its
  matched-null / cost-feasibility / multiple-comparison gates remain the mandated entry
  point for any future idea.
- **The remaining shortlist items are parked, not deleted.** H01 (dollar-bar TSMOM) is
  DEFERRED on C031 evidence; H05 (CUSUM event drift) and H12 (spread-state overlay) were
  lower-ranked and H12 is a filter that *cannot create edge* on its own — none is a live
  candidate now, but all remain documented for a future, differently-resourced attempt.

## Explicit reopening criteria

Reopen the directional/microstructure non-time-bar search **only** when at least one of
the following is true — and then only via a **fresh pre-registered front-gate screen**
(never a re-tune of H16/H03 on the same data):

1. **New data — longer history.** ≥ 10–15 years of M1 (vs the current ~5y), enough to
   test slow/event-time signals across multiple macro regimes without forking paths.
2. **New data — breadth.** **Non-USD crosses** (EUR/JPY, GBP/JPY, EUR/GBP, …) so a
   signal is not a structural USD bet on 7 collinear pairs (the C031 limiter).
3. **New data — true microstructure.** Genuine **tick / Level-2 / order-flow** data
   (not the M1 tick-*count* proxy), which would make participation-, imbalance-, and
   flow-based hypotheses (H03/H10/H11/H13) testable for real rather than via a proxy that
   this screen showed is entangled with overshoot, duration, spread, and session.
4. **A fundamentally new external thesis** with an out-of-sample anchor — not a parameter
   tweak, not a new clock for a rejected directional bet, not a re-skin of a failed family.

Absent one of these, the honest position is that **non-time bars give a better clock but
no tradeable edge in spot FX on the data we have** — and that is a successful, decisive
research outcome.

## Status

No campaign created; nothing approved; no lockbox opened; no train/validation/test
evidence; paper/demo/live remain blocked; the research freeze is intact. The non-time-bar
**campaign** lane was already PAUSED; it is now formally **RETIRED for directional search
on this corpus**, with the reopen criteria above.
