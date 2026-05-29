# Non-time-bar lane decision after CAMPAIGN_029

**Sprint:** `research-range-volatility-bar-feasibility-001` · Phase 6
**Inputs:** C029 train result; this sprint's USD_JPY (Phase 4) and seven-pair
(Phase 5) feasibility diagnostics.

> This is a research-direction decision, not an approval. Nothing here adds a
> strategy, tunes C029, creates a campaign, or enables paper/demo/live.

---

## 1. Decision

**Option 3 — keep the non-time-bar infrastructure, PAUSE non-time-bar strategy
research.** A narrow, pre-conditioned door to Option 1 (precommit a future
candidate) remains, openable only by a **new external thesis** that meets the
re-entry criteria in §4. We explicitly do **not** choose options 1, 2, or 4 now.

## 2. Why this and not the others

### What the diagnostics established (the genuinely new finding)
- The C029 rejection was **threshold-specific, not lane-fatal.** At the baseline
  2× stop the 10-pip range bar costs **0.094–0.129 cost/risk** across the majors
  (USD_JPY 0.110) — at or above the **~0.08R best gross edge this lab has ever
  observed**, hence cost-dominated on 6 of 7 pairs.
- Cost falls ~`1/threshold`. By **25–30 pip range** (and **50-pip volatility**) the
  cost/risk drops to **0.037–0.051** on every major — cost is no longer the binding
  constraint. A single shared **30-pip range bar** is cost-feasible across all seven
  pairs.
- USD_JPY is **mid-pack, not special**; the feasibility ordering is essentially a
  spread ordering (AUD cheapest → GBP/CAD dearest).
- Range bars dominate volatility bars on the cost/cadence trade-off (feasible share
  0.83 vs 0.66; volatility's small thresholds are TOO_NOISY — true_range 20-pip fires
  ~20k–38k bars/yr on every pair).

### Why NOT Option 4 (retire)
Retiring would assert range/volatility-bar strategy search is dead on current data.
The diagnostics show the opposite of cost-death: at wider thresholds **cost is not
destiny**. Retiring would throw away a still-open question and contradict this
sprint's own evidence. Too strong.

### Why NOT Option 1 (precommit a candidate now) or Option 2 (keep open for more
larger-threshold *diagnostics*)
Because **cost-feasibility is necessary but not sufficient, and we have no edge.**
The study located *where cost would not by itself kill a strategy*; it located
**no edge anywhere**. C029's one real gross edge (+0.084R at 10 pip) was thin, and a
wider-threshold *breakout* would have fewer, slower signals — the breakout premise
plausibly weakens, not strengthens. Precommitting a candidate now would either:
  - be a **C029 retune at a bigger number** (a forking-path revival of a rejected
    family — forbidden by the lab's restart rules), or
  - chase a feasible-but-unmotivated cell with no thesis (exactly the
    selection-noise trap C026/C028 already documented).
More *diagnostics* (Option 2) would not change this: we have already mapped the cost
and cadence surface across 7 pairs × 13 thresholds. The missing ingredient is an
**edge thesis**, which no further geometry run can supply.

### Why Option 3 fits the lab's established posture
This mirrors the standing pattern for C022/C027/C028: when price-structure mining is
exhausted and no edge survives, the lab **pauses and requires a new external thesis,
not a parameter tweak**. The infrastructure (`non_time_bars.py`,
`range_bar_execution.py`, the feasibility analyzer + script) is valuable, tested, and
stays. The freeze is untouched; nothing is approved.

## 3. What stays vs pauses

| item | status |
|---|---|
| `src/forex_bot/data/non_time_bars.py` builders | **keep** (merged, tested) |
| `src/forex_bot/research/range_bar_execution.py` | **keep** (C029 engine, reusable) |
| `src/forex_bot/research/non_time_bar_feasibility.py` + script | **keep** (this sprint) |
| Range/volatility-bar **strategy search** | **paused** |
| CAMPAIGN_029 family (10-pip USD_JPY breakout) | **closed** (per C029) — not revived |
| `configs/approved_strategies.yaml` | unchanged (`approved: []`) |
| paper/demo/live | unchanged (blocked) |

## 4. Strict re-entry criteria (to open the Option-1 door)

A non-time-bar campaign may be **scaffolded** (never auto-approved) only when **all**
of the following hold and are pre-committed before any evidence run:

1. **External thesis (mandatory).** A documented, falsifiable reason — sourced
   outside this codebase's own backtests — for why a *specific* non-time bar carries
   a gross edge. Not "C029 but wider". Examples: a microstructure/liquidity argument,
   an order-flow/auction-theory basis, an instrument-class change. The thesis must
   predict direction/conditioning, not just bar geometry.
2. **Threshold/cost ratio.** Target threshold must give **cost/threshold ≤ 0.10**
   (round-trip cost ≤ 10% of the bar threshold). C029's 10-pip was 0.22.
3. **Cost-to-risk ceiling.** At the candidate's *actual* nominal stop, **cost/risk ≤
   0.05** (margin below the ~0.08R achievable gross edge). On current spreads this
   means **range ≥ 25–30 pip** (pair-dependent) or **volatility ≥ 50 pip**.
4. **Cadence floor & ceiling.** **200 ≤ bars/yr ≤ 20,000** for the target
   pair/threshold (no TOO_SPARSE, no TOO_NOISY). Rules out all `true_range ≤ 40 pip`.
5. **Front gate first.** The candidate must pass the mandated edge-discovery
   front-gate screen (`research/edge_discovery/`, matched-null / multiple-comparison
   / cost-feasibility) **before** a CAMPAIGN number is assigned — same gate C028 was
   held to.
6. **Distinctness.** Must be structurally distinct from C029 and the retired
   pullback/breakout families (a distinctness memo, as for C020/C021).

Only then: assign the next free campaign number (**not** retroactively C029), write a
fresh pre-commit, scaffold, and — separately and later — run evidence.

## 5. What would be required to *reopen* beyond a new thesis

Any one of these materially changes the cost surface and would justify revisiting
even the tighter thresholds:
- **Lower-cost broker / spread evidence** (e.g. sub-1-pip majors) — would pull the
  cost/risk floor down and could rehabilitate 15–20 pip cells.
- **True tick data** (vs M1-resolved) — sharper fills, better overshoot/cadence
  measurement, and a more accurate (likely lower) effective spread.
- **A different instrument class** (futures, crypto, indices) with different cost or
  volatility structure.
- **Materially wider thresholds** paired with a thesis (already covered by §4).
- **Better independent evidence** that a wide-threshold non-time bar has a gross
  edge (external study, not our own re-mine).

## 6. Bottom line

The non-time-bar **lane is not dead — it is edge-unproven.** Cost ceases to dominate
at wide thresholds, USD_JPY is unremarkable, range bars beat volatility bars on
cost/cadence, and a shared 30-pip range threshold is cost-feasible across the
majors. None of that is an edge. We keep the (good, tested) infrastructure, pause the
strategy search, and require a real external thesis through the front gate before any
future scaffold. Until then: nothing approved, freeze intact.
