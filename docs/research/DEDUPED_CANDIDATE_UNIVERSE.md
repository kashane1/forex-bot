# Deduped Candidate Universe

**Sprint:** NEW_CANDIDATE_DISCOVERY_DEDUPED_001  
**Branch:** `research-new-candidate-strategy-discovery-deduped-001`  
**Date:** 2026-05-26

Six structurally distinct strategy candidates for the first post-dedup
implementation sprint. None are approved; this is a discovery document only.

**Null baseline for comparison:** deduped CAMPAIGN_011 aggregate exp_r
**−0.0029154071495408797**, 1,180 trades, fold mean/std −0.0027 / 0.0479.

---

## Ranking criteria

| criterion | weight | rationale |
|---|---|---|
| Structural novelty vs retired families | high | Must not retune 002–015 |
| Low turnover | high | H4 event systems failed on costs |
| No financing blocker | high | Carry hypotheses blocked without model |
| H4/D1AGG data compatibility | high | Existing SQLite universe |
| Simple / falsifiable implementation | high | Precommit before code |
| Cost robustness | high | 2× stress mandatory |
| No contaminated positive evidence | binding | Dedup-safe null only |
| Backtrader-verifiable | medium | Secondary lane parity |

---

## Candidate 1: `weekly_cross_sectional_momentum_low_turnover`

### Thesis

Weekly currency-pair **relative momentum** may produce lower turnover and lower
cost sensitivity than H4 event/reversal/breakout systems. Rank seven majors by
multi-week volatility-adjusted return; trade only the strongest and weakest
with USD exposure caps; rebalance weekly; hold multi-day.

### Why structurally distinct

- **Cross-sectional ranking** across pairs — not single-pair trend or breakout.
- **Weekly cadence** — not H4 bar triggers or session windows.
- No failed-breakout, mean-reversion, regime-switcher, or event-calendar logic.

### Why not a retune

Not EMA/Donchian (002), ADX (003), ATR compression breakout (004), pullback
(007), range MR (008/009), session (010), regime switcher (012), strength
rotation timing (013), calendar (014), or failed breakout (015). The ranking
horizon and rebalance schedule differ materially from 013's daily strength.

### Expected trade frequency

Low–moderate: ~1–2 positions per rebalance × ~52 weeks × 8 folds ≈ **400–800**
round-trip legs over full walk-forward (order of magnitude; precommit will fix).

### Data required

- H4 OANDA practice SQLite via deduped `CandleRepo.list`
- Weekly aggregation (5 trading-day or calendar-week boundary, deterministic)

### Infra blockers

- None critical; weekly bar builder from H4 is straightforward
- Portfolio exposure / USD cap logic exists from prior campaigns

### Financing blockers

**None** — momentum on spot FX without explicit carry tilt.

### Expected cost sensitivity

**Low–moderate** — weekly rebalance limits spread churn vs H4 systems.

### Risks / overfit paths

- Momentum crash in FX (post-2008 literature mixed for G10)
- Pair concentration if one currency dominates rankings
- Lookback blend (4w/12w) may overfit if grid expanded — precommit tiny set
- Sparse folds if weekly gates require high per-fold trade counts

### vs deduped null

Must beat −0.0029 R aggregate with statistical separation (anti-overfit gates).
Low turnover gives clearer cost headroom than 015 (−0.0101 R, 375 trades).

### First-candidate assessment

**Strong yes** — best balance of novelty, low turnover, no financing blocker,
data compatibility, falsifiability.

---

## Candidate 2: `weekly_volatility_contraction_breakout`

### Thesis

After **multi-week volatility contraction** (Bollinger/ATR percentile squeeze
on weekly aggregates), trade directional breakout of the contraction range on
H4 entry with weekly-scale stops. Distinct from CAMPAIGN_004's H4 ATR
compression by timeframe and hold period.

### Why structurally distinct

- Weekly squeeze definition + H4 execution — hybrid timeframe
- Breakout direction from range, not failed-breakout reversal (015)
- Hold period measured in days/weeks, not H4 bars

### Why not a retune

004 used H4 ATR compression with H4 holds. This uses **weekly** contraction
state and multi-day holds. Not 015's false-break fade.

### Expected trade frequency

Low: ~20–60 trades/pair/year → **~150–400** total across 7 pairs × 8 folds.

### Data required

- H4 SQLite (deduped)
- Weekly ATR/Bollinger aggregates

### Infra blockers

- Weekly indicator pipeline (minor)

### Financing blockers

None.

### Expected cost sensitivity

Moderate — fewer entries than H4 systems but breakout entries may hit spread.

### Risks / overfit paths

- Conceptually adjacent to rejected 004 family — "volatility breakout" label
  triggers skepticism even if timeframe differs
- Squeeze definition parameters tempting to optimize
- May correlate with 004 failures if edge is timeframe-independent negative

### vs deduped null

Must clear null band; 004's −0.163 R (contaminated) is a warning, not evidence.

### First-candidate assessment

**Moderate** — structurally different timeframe but thematically close to retired
004/015 breakout family; higher overfit narrative risk.

---

## Candidate 3: `multi_day_carry_trend_hybrid`

### Thesis

Combine **interest-rate differential proxy** (static or slow-moving carry
rank) with **multi-day trend filter** — long high-carry appreciating pairs,
short low-carry depreciating, with trend confirmation on D1/H4 aggregate.

### Why structurally distinct

- Explicit carry + trend fusion — not tested in 002–015
- Multi-day hold; not H4 reversal

### Why not a retune

Not pure trend (002) or pure strength rotation (013). Carry signal is explicit.

### Expected trade frequency

Low: rebalance weekly or bi-weekly → **~200–500** trades total.

### Data required

- H4/D1 aggregates
- **Financing / swap rate time series** or OANDA financing model

### Infra blockers

- Financing overlay exists but **conservative stress** showed sensitivity in
  CAMPAIGN_010/013 docs

### Financing blockers

**BLOCKED** unless modeled financing is sufficient for the hypothesis. Current
ESTIMATED + conservative overlay may not support carry-as-alpha claims.

### Expected cost sensitivity

Low turnover but **financing drag** dominates P&L for carry tilt.

### Risks / overfit paths

- Carry crashes (AUD/JPY 2008, 2013 taper)
- Financing model mismatch vs live
- Confounded with simple momentum

### vs deduped null

Cannot validly test until financing path is certified for carry hypothesis.

### First-candidate assessment

**Defer** — financing blocker unless sprint scope includes financing upgrade.

---

## Candidate 4: `portfolio_volatility_regime_filter_then_signal`

### Thesis

Apply a **portfolio-level volatility regime filter** (e.g., cross-pair realized
vol percentile) that gates a simple underlying signal (e.g., weekly momentum or
random-direction baseline). Trade only when portfolio vol is in a precommitted
band. Distinct from 012's per-pair ATR regime **switcher**.

### Why structurally distinct

- **Filter-before-signal** architecture vs 012's switch-between-strategies
- Portfolio-level vol, not per-pair ATR percentile routing

### Why not a retune

012 switched between trend and MR by pair ATR. This gates *one* simple signal
by portfolio vol state — different mechanism.

### Expected trade frequency

Moderate-low: filter reduces trades vs unfiltered baseline → **~300–700**.

### Data required

- H4 deduped; cross-pair vol estimate

### Infra blockers

- Portfolio vol aggregator (minor)

### Financing blockers

None (depends on underlying signal — if momentum, none).

### Expected cost sensitivity

Moderate — fewer trades but added parameter (vol band edges).

### Risks / overfit paths

- Narrative overlap with rejected 012 "regime" family
- Filter may just reduce sample size without adding edge
- Two-layer system harder to falsify cleanly

### vs deduped null

Must beat null on filtered trades; unfiltered subset should be documented.

### First-candidate assessment

**Moderate-low** — novel architecture but "regime" label and 012 baggage.

---

## Candidate 5: `session_range_reversal_cost_gated`

### Thesis

Identify **prior session range** (e.g., Asian range on H4), trade reversal at
range extremes **only when spread/ATR ratio** passes a cost gate. Multi-hour
hold, not session open breakout (010).

### Why structurally distinct

- **Reversal at range extreme** with explicit cost gate — not 010's breakout
- Cost gate is primary filter, not session filter alone

### Why not a retune

010 traded Asian/London **breakout**; this fades range extremes with cost veto.
015 traded failed **breakout** reversal on different pattern.

### Expected trade frequency

Moderate: **~400–900** if cost gate permissive; lower if strict.

### Data required

- H4 deduped; session boundary definitions (UTC)

### Infra blockers

- Session labeling exists from CAMPAIGN_010 infra

### Financing blockers

None.

### Expected cost sensitivity

**High sensitivity by design** — cost gate is central; may leave too few trades.

### Risks / overfit paths

- Thematically adjacent to rejected 010 (session) and 015 (reversal)
- Session boundary choice (UTC vs broker) fragile
- Reviewers will ask "why not another session variant of 010?"

### vs deduped null

010 rejected on walk-forward (contaminated metrics); 015 deduped WITHIN_NULL.
Session/reversal space is **exhausted** for this archive.

### First-candidate assessment

**No** — not clearly distinct enough from 010/015 family despite cost gate.

---

## Candidate 6: `pair_specific_research_lab` (lab only, not campaign)

### Thesis

Run **pair-specific exploratory analysis** (e.g., USD_JPY vs EUR_USD regime
differences) to generate hypotheses without a unified campaign. Outputs feed
future precommits, not a walk-forward verdict.

### Why structurally distinct

- Meta-research process, not a single strategy family

### Why not a retune

N/A — no strategy to retune.

### Expected trade frequency

N/A — lab produces reports, not trades.

### Data required

- H4 deduped

### Infra blockers

None.

### Financing blockers

None.

### Expected cost sensitivity

N/A.

### Risks / overfit paths

- Becomes unfalsifiable fishing expedition
- Violates "one precommitted campaign" discipline if promoted to campaign

### vs deduped null

No null comparison until hypothesis crystallizes into campaign.

### First-candidate assessment

**Lab only** — useful parallel track, not the next implementation sprint.

---

## Ranking table

| rank | candidate | novelty | turnover | financing | data fit | falsifiable | cost robust | BT feasible | contaminated dep | **score** |
|---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | weekly_cross_sectional_momentum_low_turnover | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★☆ | ★★★★★ | **A** |
| 2 | weekly_volatility_contraction_breakout | ★★★★☆ | ★★★★☆ | ★★★★★ | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ | **B+** |
| 3 | portfolio_volatility_regime_filter_then_signal | ★★★★☆ | ★★★★☆ | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | ★★★★★ | **B** |
| 4 | multi_day_carry_trend_hybrid | ★★★★★ | ★★★★☆ | ★☆☆☆☆ | ★★★☆☆ | ★★★☆☆ | ★★☆☆☆ | ★★★☆☆ | ★★★★★ | **C (blocked)** |
| 5 | session_range_reversal_cost_gated | ★★☆☆☆ | ★★★☆☆ | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★☆☆☆ | ★★★★☆ | ★★★★★ | **D** |
| — | pair_specific_research_lab | ★★★☆☆ | n/a | ★★★★★ | ★★★★★ | ★★☆☆☆ | n/a | n/a | ★★★★★ | **Lab** |

---

## Recommendation for Phase 3

Proceed with **`weekly_cross_sectional_momentum_low_turnover`** as CAMPAIGN_016
unless Phase 3 review finds a blocking issue. It ranks first on structural
novelty, turnover, financing freedom, and distance from all retired families.

See `NEXT_CANDIDATE_SELECTION_DEDUPED_001.md` for formal selection.
