# Deduped Candidate Universe 002

**Sprint:** NEW_CANDIDATE_DISCOVERY_DEDUPED_002  
**Branch:** `research-new-candidate-strategy-discovery-deduped-002`  
**Date:** 2026-05-26

Six structurally distinct strategy candidates for the second post-dedup
implementation sprint (CAMPAIGN_017). None are approved; discovery only.

**Null baseline:** deduped CAMPAIGN_011 aggregate exp_r
**−0.0029154071495408797**, 1,180 trades, fold mean/std −0.0027 / 0.0479.

**Context:** CAMPAIGN_016 (weekly cross-sectional momentum) **REJECT** on
deduped data — cross-sectional ranking is retired for CAMPAIGN_017.

---

## Ranking criteria

| criterion | weight | rationale |
|---|---|---|
| Dedup-safe compatibility | binding | Must use `CandleRepo.list` path |
| Structural novelty vs retired families | high | Must not retune 002–016 |
| Low turnover | high | H4 churn failed repeatedly |
| No financing blocker | high | Carry blocked without model |
| Not cross-sectional momentum | high | CAMPAIGN_016 REJECT |
| Not failed-breakout reversal | high | CAMPAIGN_015 REJECT |
| Not H4 compression churn | high | CAMPAIGN_004 REJECT |
| Simple / falsifiable | high | Precommit before code |
| Realistic trade count | medium | Weekly/low-turnover sample risk (016 lesson) |
| Backtrader feasible | medium | Secondary lane parity |

---

## Candidate 1: `weekly_volatility_contraction_breakout`

### Thesis

After **multi-week volatility contraction** (narrow weekly true range
relative to trailing 12-week distribution), trade directional breakout
from the compressed range on **completed** H4 or weekly boundaries.
Single-pair signals; no cross-sectional ranking.

### Why structurally distinct

- **Weekly/multi-day compression state** + breakout follow-through — not H4-bar ATR percentile trigger (004).
- **Single-pair** — not cross-sectional rank (013, 016).
- **With-breakout** direction — not failed-break fade (015).
- Hold period measured in **days/weeks**, not H4 bar churn.

### Why not a retune

| prior | difference |
|---|---|
| CAMPAIGN_004 | 004: H4 ATR P40 + 20-bar Donchian on **same H4 bar**; C017: **12-week** range percentile + compressed-week high/low boundary |
| CAMPAIGN_015 | 015 fades false breaks; C017 trades **confirmed** expansion breakout |
| CAMPAIGN_016 | 016 ranks pairs weekly; C017 is **per-pair** compression → breakout |

### Expected turnover

Low: ~15–40 trades/pair/year → **~120–350** aggregate over 8 folds.

### Data required

- Deduped H4 SQLite via `CandleRepo.list`
- Synthetic weekly true-range aggregation (no native W1)

### Infra blockers

- Weekly range / ATR aggregator (minor; analogous to `weekly_momentum.py`)

### Financing blockers

**None.**

### Cost sensitivity

Moderate — fewer entries than H4 systems; breakout entries may pay spread at expansion.

### Overfit risks

- "Volatility breakout" label invites 004-family skepticism — precommit must freeze cadence and thresholds.
- Compression percentile (25th) and lookback (12 weeks) must not become a grid.
- Sparse compression weeks may yield too few trades (016 low-N lesson).

### Backtrader feasibility

**Feasible** — single-pair state machine simpler than 016 cross-pair portfolio.
Fold-window comparison target: TOLERABLE_DRIFT (015 precedent).

### Expected rejection reasons

- WITHIN_NULL like 015/016.
- Too few trades below gate minimum.
- Breakout edge correlates with 004's negative H4 breakout family.
- 2× cost stress collapses marginal breakouts.

### Score

**A** — best balance of novelty (post-016), low turnover, no financing, no cross-section.

---

## Candidate 2: `multi_day_range_expansion_after_compression`

### Thesis

Identify **multi-day (3–5 trading day)** range compression on H4 aggregates;
enter when the range **expands** beyond a precommitted multiple of the
compressed range width. Distinct from weekly contraction (Candidate 1) by
**shorter compression window** and **range-width** (not ATR percentile) definition.

### Why structurally distinct

- Multi-day **range width** compression, not weekly TR percentile.
- Expansion trigger on range width, not Donchian channel (004).
- Single-pair; no ranking.

### Why not a retune

Not 004 (H4 ATR percentile + Donchian). Not 015 (reversal). Not 016 (cross-section).
Compression measured in **fixed multi-day bars**, not 60-bar ATR window.

### Expected turnover

Moderate-low: **~200–450** aggregate.

### Data required

- Deduped H4 only

### Infra blockers

- Multi-day range aggregator (minor)

### Financing blockers

**None.**

### Cost sensitivity

Moderate — more trades than weekly cadence but less than pure H4 event systems.

### Overfit risks

- Adjacent to Candidate 1 and 004 — reviewer may see "another compression breakout."
- Multi-day window choice (3 vs 5 days) tempting to optimize.

### Backtrader feasibility

**Feasible** — single-pair.

### Expected rejection reasons

- Thematic overlap with 004/017 if both tested — pick one per sprint.
- Cost sensitivity on moderate turnover.

### Score

**B+** — viable alternate if weekly contraction fails precommit review.

---

## Candidate 3: `portfolio_volatility_regime_filter_then_simple_signal`

### Thesis

Compute **portfolio-level realized volatility** (cross-pair equal-weight) and
trade a simple underlying signal (e.g., random-direction baseline or fixed
momentum rule) **only** when portfolio vol is in a precommitted band (e.g.,
20th–80th percentile of trailing 52-week portfolio vol). Filter-before-signal,
not strategy-switching.

### Why structurally distinct

- **Portfolio-level vol gate** — not per-pair ATR routing (012).
- Underlying signal is intentionally **simple** — tests whether vol filtering adds edge, not a complex alpha model.
- No cross-sectional rank.

### Why not a retune

012 switched between trend and MR by pair ATR percentile. This gates **one**
frozen simple signal by **portfolio** vol — different mechanism and architecture.

### Expected turnover

Moderate-low: filter reduces trades → **~250–600** depending on band width.

### Data required

- Deduped H4; cross-pair vol estimate

### Infra blockers

- Portfolio vol aggregator (minor)

### Financing blockers

**None** (if underlying signal has no carry tilt).

### Cost sensitivity

Moderate — fewer trades but added filter parameter.

### Overfit risks

- "Regime" narrative overlap with rejected 012.
- Two-layer system harder to falsify — filter may just shrink sample.
- Risk of becoming an implicit parameter search on vol band edges.

### Backtrader feasibility

**Moderate** — portfolio vol + gated signal needs careful alignment.

### Expected rejection reasons

- Filter removes edge and sample without improvement.
- WITHIN_NULL on filtered subset.
- Reviewer classifies as 012 retune.

### Score

**B** — novel architecture but regime baggage and falsifiability concerns.

---

## Candidate 4: `daily_close_reversal_after_extreme_range`

### Thesis

When a pair's **prior completed daily range** (synthetic from H4) exceeds the
90th percentile of trailing 20-day daily ranges, fade the move at the **next
H4 open** (reversal after extreme expansion day). Distinct from session
breakout (010) and failed-breakout (015).

### Why structurally distinct

- Trigger is **extreme prior-day range**, not session boundary or false break.
- **Reversal** after expansion, not breakout follow-through.
- Single-pair; daily-range context from H4 aggregation.

### Why not a retune

010: session open **breakout**. 015: H4 **failed sweep** fade. 008/009: range
**midline** mean reversion. This: **post-extreme-day** reversal at next open.

### Expected turnover

Moderate: **~300–600** aggregate (extreme days are sparse).

### Data required

- Deduped H4; synthetic daily OHLC

### Infra blockers

- Daily aggregation from H4 (minor)

### Financing blockers

**None.**

### Cost sensitivity

Moderate-high — reversal entries may fight momentum; spread at open matters.

### Overfit risks

- Reversal family exhausted by 008/009/015 rejections — reviewer skepticism.
- 90th percentile threshold fragile.
- Extreme-day sample sparsity per fold.

### Backtrader feasibility

**Feasible** — single-pair daily boundary logic.

### Expected rejection reasons

- Classified as another mean-reversion / reversal variant.
- WITHIN_NULL; fold sparsity.
- Momentum continuation on extreme days (wrong-side fade).

### Score

**C+** — structurally labeled distinct but thematically close to rejected reversal space.

---

## Candidate 5: `pair_specific_research_lab` (lab only)

### Thesis

Exploratory **pair-specific** analysis (regime differences, compression
frequency, cost asymmetry) to generate hypotheses for future precommits.
Outputs are reports, not walk-forward verdicts.

### Why structurally distinct

Meta-research process, not a unified strategy campaign.

### Why not a retune

N/A — no strategy to retune.

### Expected turnover

N/A — no trades.

### Data required

- Deduped H4

### Infra blockers

None.

### Financing blockers

None.

### Cost sensitivity

N/A.

### Overfit risks

Unfalsifiable fishing; violates one-campaign discipline if promoted without precommit.

### Backtrader feasibility

N/A until hypothesis crystallizes.

### Expected rejection reasons

N/A — not a campaign candidate.

### Score

**Lab** — parallel track only; not CAMPAIGN_017.

---

## Candidate 6: `carry_trend_hybrid`

### Thesis

Combine **interest-rate differential proxy** with multi-day trend filter —
long high-carry appreciating pairs, short low-carry depreciating.

### Why structurally distinct

Explicit carry + trend fusion — not tested as hybrid in 002–016.

### Why not a retune

Not pure trend (002) or pure strength rotation (013). Carry signal explicit.

### Expected turnover

Low: **~200–500** trades.

### Data required

- H4 aggregates
- **Financing / swap rate time series**

### Infra blockers

Financing overlay exists but may be insufficient for carry-as-alpha claims.

### Financing blockers

**BLOCKED** unless modeled financing is certified for the hypothesis.

### Cost sensitivity

Low turnover but financing drag dominates.

### Overfit risks

Carry crashes; financing model mismatch vs live.

### Backtrader feasibility

**Moderate** — financing wiring complexity.

### Expected rejection reasons

Cannot validly test until financing path certified.

### Score

**C (blocked)** — defer.

---

## Ranking table

| rank | candidate | novelty | turnover | financing | not X-section | not H4 churn | falsifiable | BT feasible | **score** |
|---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | weekly_volatility_contraction_breakout | ★★★★☆ | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★☆ | **A** |
| 2 | multi_day_range_expansion_after_compression | ★★★★☆ | ★★★★☆ | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★★★☆ | ★★★★☆ | **B+** |
| 3 | portfolio_volatility_regime_filter_then_simple_signal | ★★★★☆ | ★★★★☆ | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | **B** |
| 4 | daily_close_reversal_after_extreme_range | ★★★☆☆ | ★★★☆☆ | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★★★☆ | **C+** |
| 5 | carry_trend_hybrid | ★★★★★ | ★★★★☆ | ★☆☆☆☆ | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | **C (blocked)** |
| — | pair_specific_research_lab | ★★★☆☆ | n/a | ★★★★★ | n/a | n/a | ★★☆☆☆ | n/a | **Lab** |

---

## Recommendation for Phase 3

Proceed with **`weekly_volatility_contraction_breakout`** as CAMPAIGN_017.
CAMPAIGN_016 retired cross-sectional momentum; weekly single-pair
contraction → breakout is the highest-ranked structurally distinct,
low-turnover, financing-free candidate.

See `NEXT_CANDIDATE_SELECTION_DEDUPED_002.md` for formal selection.
