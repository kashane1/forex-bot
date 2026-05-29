# EDGE_DISCOVERY_IDEA_RANKING_AND_DECISION

**Status:** diagnostic / idea-selection decision (Phase 6 of
`research-edge-discovery-front-gate-idea-selection-001`). Ranks the candidate
families on the cheap edge-discovery evidence and decides whether any deserves a
*future* campaign. **This document approves nothing, creates no campaign, opens
no test lockbox, and enables no paper/demo/live.** A campaign begins only if a
human later issues an explicit instruction acting on the Phase-7 precommit prompt.

> Evidence: Phase 2 [opportunity map](EDGE_DISCOVERY_OPPORTUNITY_MAP_REFRESH.md),
> Phase 3 [signal probes](EDGE_DISCOVERY_SIGNAL_PROBE_RESULTS.md), Phase 4
> [matched-null](EDGE_DISCOVERY_MATCHED_NULL_SCREENING_RESULTS.md), Phase 5
> [filter ablation](EDGE_DISCOVERY_FILTER_ABLATION_RESULTS.md). Gate phrasing:
> [`FUTURE_CAMPAIGN_REENTRY_GATES.md`](FUTURE_CAMPAIGN_REENTRY_GATES.md).

---

## Status legend

`REJECT_CHEAPLY` · `INCONCLUSIVE_NEEDS_BETTER_DATA` · `COMPATIBILITY_BLOCKED` ·
`WATCHLIST` · `CAMPAIGN_ELIGIBLE`.

## Campaign-eligibility criteria (all must hold)

cost feasibility passes · forward-return information present · beats the
*structure-matched* null by a meaningful margin · not purely one-pair/one-session
unless precommitted as such · filters add evidence (not only reduce sample) ·
multiple-comparison sanity does not flag selection noise · expected trade count
sufficient · required data exists.

## Ranking

### Rank 1 — z-score mean reversion (H4, low-vol · strong-extension · quiet-session, short-biased) — **CAMPAIGN_ELIGIBLE (borderline/conditional)**
- **Evidence:** cost-feasible (H4 ratio 0.04–0.10); forward-return information
  rising monotonically with horizon; **beats all six matched nulls** (incl.
  side-shuffled, session-matched, full) at percentile 100, effect 3.7–6.0;
  **3/5 filters add edge**; edge-adding subset (n=1,065) post-cost **+0.000626
  conservative / +0.000754 optimistic**, hit 0.55; **pair-robust 6/7**;
  **multi-year positive 4/7**.
- **Cost feasibility:** PASS (survives financing-inclusive conservative cost).
- **Signal information:** PASS (monotone with horizon; short side carries it).
- **Matched null:** PASS — `BEATS_MATCHED_NULL` on every mode.
- **Ablation:** PASS — low_vol/strong_extension/quiet_session `FILTER_ADDS_EDGE`;
  long-side hurts (→ short bias); cost-adv-pair sample-only.
- **Concentration:** pair-robust (6/7); session/vol-conditioned **by design** —
  must be **precommitted** as a low-vol quiet-session reversion strategy.
- **Multiple-comparison risk:** the raw-variant matrix flagged
  `LIKELY_SELECTION_NOISE` (driven by the USD_JPY single-pair artifact, *not* the
  chosen all-pair subset) — standing caution; the 3-of-5 filter retention is a
  **forking-path** risk requiring precommit + clean re-confirmation.
- **Data:** exists (H4, 7 majors, 2020–2026).
- **Open risks (→ pre-registered campaign kill-conditions):** recency (2024 and
  2026-partial negative); filter forking-path; conditioning narrowness.
- **Next action:** Phase-7 precommit prompt (the single one this sprint permits).
  Borderline: it clears every defined criterion, with the two marginal items
  (selection-noise context, one-session-unless-precommitted) handled by explicit
  precommit. It is the **first idea in the program to clear the full battery.**

### Rank 2 — failed-breakout fade (H4) — **REJECT_CHEAPLY** (→ WATCHLIST note)
- Beats all matched nulls (real information) and is pair-robust, **but**
  net-negative post-cost at trigger level, year-fragile (2023-dominated), and not
  ablated (a second reversion idea overlapping Rank 1). Rejected for *this* round;
  may be revisited only as a variant inside the Rank-1 campaign if Rank 1 proceeds.

### Rank 3 — USD_JPY single-pair probe — **REJECT_CHEAPLY (as a standalone edge)**
- USD_JPY is cost-advantaged (cheapest + most volatile) but its reversion overlay
  is **weaker than the all-pair signal** and below-null at short horizons; the
  matrix-sanity "best" USD_JPY variant is `LIKELY_SELECTION_NOISE`. **USD_JPY's
  value is cost, not signal.** It remains a *cost-advantaged venue* inside Rank 1,
  never a standalone thesis. (Closes the recurring "USD_JPY must have edge" hope.)

### Rank 4 — Asia-range breakout (H1) — **REJECT_CHEAPLY**
- Pre-cost ≈ 0; post-cost negative at every horizon; low hit rate (0.40–0.49);
  only above-null at h1 where both ≈ −cost. No usable forward-return edge.

### Rank 5 — NY-open continuation (H1) — **REJECT_CHEAPLY**
- At/below null (prob_null≥strat 0.55, effect −0.42). Continuation at the NY
  handoff is null.

### Rank 6 — volatility compression→expansion (H4) — **REJECT_CHEAPLY**
- *Worse* than null (prob 0.95, effect −1.38). Confirms, at a fresh H4 band, the
  recurring pattern: vol expansion is real, its **direction is null**. (Consistent
  with the prior USD_JPY vol-compression falsification.)

### Rank 7 — London open expansion (H1) — **REJECT_CHEAPLY (weakly supported a priori)**
- Phase 2: H1 London-bucket ATR ≈ Asian-bucket ATR — little session-open
  expansion to trade. Not separately probed; demoted by the market facts.

### Rank 8 — high-volatility exhaustion → reversal — **INCONCLUSIVE_NEEDS_BETTER_DATA**
- Not directly probed. Phase 2 shows high-vol cells carry the widest spreads
  (cost-adverse exactly at signal); the z-score probe's `f_low_vol`-adds-edge /
  high-vol-hurts result is *indirect evidence against* an exhaustion-reversal edge
  in high-vol regimes. Would need a dedicated probe; low priority.

### Rank 9 — Asia range fade (H1) — **INCONCLUSIVE_NEEDS_BETTER_DATA**
- Not separately probed (H1 cannot see the true intrabar sweep wick; the
  failed-breakout fade is its H4 cousin and was rejected). Sub-hour data needed
  for a faithful sweep test.

### Rank 10 — event-window anomaly — **COMPATIBILITY_BLOCKED / sparse**
- Only the single committed `campaign_014_events.json` fixture; event spreads
  blow out; likely `INCONCLUSIVE_SPARSE`. No new fetch permitted.

### Rank 11 — carry / financing-aware swing — **COMPATIBILITY_BLOCKED**
- No local carry/swap-rate table; FRED has the US leg only. Only a financing-drag
  *stress* note is possible (which is already folded into the conservative cost
  overlay). No carry edge can be screened here.

### Rank 12 — pair/timeframe/session opportunity mining — **completed (Phase 2)**
- Produced the opportunity map; its facts (H4 cheapest, USD_JPY cost-advantaged,
  weak session-vol gradient, sub-H1 data-blocked) shaped every selection above.

## Decision

**One idea is `CAMPAIGN_ELIGIBLE (borderline/conditional)`:** the H4 low-vol
quiet-session strong-extension **short-biased z-score mean-reversion** strategy.
It is the first idea in the program to pass cost feasibility, forward-return
information, the structure-matched null, filter-adds-edge ablation, conservative
financing cost, pair-robustness, and multi-year positivity together.

Therefore Phase 7 drafts the **single permitted precommit prompt** for a future
campaign scaffold — to be executed **only on explicit future instruction**. It
is *not* CAMPAIGN_027; it creates nothing; it approves nothing; paper/demo/live
stay blocked; `approved_strategies.yaml` stays `approved: []`.

All other families are `REJECT_CHEAPLY`, `INCONCLUSIVE_NEEDS_BETTER_DATA`, or
`COMPATIBILITY_BLOCKED` and do **not** earn a campaign. C011 remains the null
benchmark; C025/C026 remain rejected; the lower-timeframe Donchian+HTF family
stays closed.
