# CAMPAIGN_024 — distinctness & prior-lessons memo

**Strategy:** `m5_donchian_htf_confluence_breakout 0.1.0-c024`
**Status:** SCAFFOLD_ONLY / NOT_RUN / NOT_APPROVED.

This memo records how C024 deliberately recombines the parts of prior campaigns
that worked (as *structure*, not as approved edge) while engineering out the
specific failure modes that sank earlier attempts. Nothing here is a claim of
edge — C024 has no evidence yet.

---

## What C024 keeps from each lineage

### From the earliest Donchian / breakout idea (CAMPAIGN_002 lineage)
- **Keeps:** an explicit, falsifiable **price-action breakout trigger** — a
  Donchian channel break — rather than an indicator-soup entry.
- **Fixes the blunt-H4 problem:** the early idea broke an **H4** channel across
  all pairs, so each entry was a whole-H4-bar-coarse, regime-blind event. C024
  moves the *trigger* to **M5** (precise) and demotes H4 to a **trend gate**, not
  the channel itself. The breakout must occur *inside* an agreeing H4/H1 trend.

### From C020 / C021 (MTF confluence)
- **Keeps:** the multi-timeframe confluence discipline and **`align_last_completed`**
  HTF alignment — every higher-timeframe value at an M5 decision comes from the
  **last completed** HTF bar, so there is no HTF lookahead.
- **Keeps:** materialized **M1-derived** lower timeframes (M5/M15/H1/H4M1) as the
  data substrate, with **native-H4-derived D1AGG** (M1-derived D1AGG rejected
  until day-completeness is fixed).
- **Differs:** C020 executed on H4/H1; C021 executed on M15 with an EMA20-reclaim
  pullback trigger. C024 executes on **M5** with a **Donchian breakout** trigger —
  a materially different entry, not a re-parameterization of the C021 pullback.

### From C019 and the fill-timing / HTF-align infra sprints
- **Keeps:** **`next_bar_open`** realism and `approval_bound` / `conservative`
  execution metadata. C024 **forbids** `signal_bar_close` fills and any same-bar
  entry on the signal bar — the optimistic-fill lineage that flattered earlier
  backtests is structurally excluded.

### From the broad seven-pair strategy failures (C012, C013, C015–C017)
- **Avoids** assuming a single universal seven-pair edge. The runner reports
  **pair-level diagnostics**, and the precommit gates allow a future
  **`SINGLE_PAIR_REVIEW_ONLY`** classification (never an automatic PASS) if
  breadth fails but one pair is materially strong — pre-registered, not
  discovered after the fact.

### From the turnover-amplification failures
- **Requires a pullback/compression precondition on M15 before any breakout**, so
  C024 is not a high-turnover breakout chaser. The scaffold also tracks trade
  frequency (sample probe) and the precommit mandates documenting the
  **spread/ATR ratio** so spread-domination is caught before promotion.

### From the financing / cost-overlay lessons
- **Records holding period** (48-bar time stop bounds it) and the precommit
  requires a **2× cost-stress** validation gate (`expectancy ≥ 0` under doubled
  spread/slippage) and a future financing overlay — cost is a gate, not an
  afterthought.

## Why C024 is structurally distinct from specific rejected campaigns

| vs. | Their entry | C024 entry | Distinct because |
|---|---|---|---|
| **CAMPAIGN_002** (Donchian/breakout lineage) | H4 channel break, all pairs, optimistic fills | M5 channel break gated by H4/H1 trend + D1AGG regime + M15 setup, `next_bar_open` | trigger timeframe, regime gating, fill realism all differ |
| **C012** (regime switcher ATR percentile) | ATR-percentile regime classifier on H4 | price-action Donchian break on M5 | no ATR-percentile regime model; trigger is structural, not statistical |
| **C013** (cross-pair currency strength rotation) | cross-sectional currency-strength ranking | single-instrument breakout + own-pair trend | no cross-sectional ranking; per-pair, not rotational |
| **C020** (MTF confluence pullback, H4 exec) | H4 pullback into trend | M5 Donchian breakout into trend | execution timeframe (H4→M5) and trigger (pullback→breakout) |
| **C021** (LTF MTF confluence, M15 exec) | M15 EMA20-reclaim pullback | M5 Donchian channel break | execution timeframe (M15→M5) and trigger (EMA reclaim→Donchian breakout); not a threshold tweak |

## Relationship to the retired C022/C023 pullback family and the old "C024 NOT_READY" note

The C022/C023 family closeout recorded a prospective **"C024 NOT_READY"** — but
that referred to a *pullback-resolution continuation* (re-gating the same M15
EMA20-reclaim signal), which was never created. **This** CAMPAIGN_024 is a
different strategy that takes the C024 number. It is **not** a same-shaped
pullback-resolution campaign: the trigger is a Donchian channel break on M5, not
an M15 EMA20 reclaim. It therefore does not reopen the retired family and does
not rely on that family's (unmet) reopening bar.

## What would still kill C024 (pre-registered honesty)

- Train expectancy `< 0`, or validation expectancy `≤ 0` / PF `< 1.05`.
- Fewer than 100 validation trades, or fewer than 4/7 pairs non-negative (absent
  a pre-registered single-pair case).
- Negative expectancy under 2× cost stress, or failure to beat the C011 null by
  `+0.010R`.
- Average holding period so short that spread dominates.
- Backtrader parity failure.

Any of these → REJECT (or, at most, `SINGLE_PAIR_REVIEW_ONLY`). The maximum
attainable status for the whole campaign is `RESEARCH_PASS /
PROMOTION_REVIEW_REQUIRED` — **never approved** by this campaign.
