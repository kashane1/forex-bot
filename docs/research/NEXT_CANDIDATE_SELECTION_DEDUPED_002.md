# Next Candidate Selection — Deduped 002

**Sprint:** NEW_CANDIDATE_DISCOVERY_DEDUPED_002  
**Branch:** `research-new-candidate-strategy-discovery-deduped-002`  
**Date:** 2026-05-26

## Selection

| field | value |
|---|---|
| **Selected candidate** | `weekly_volatility_contraction_breakout` |
| **Proposed campaign id** | **CAMPAIGN_017** |
| **Proposed strategy version** | `weekly_volatility_contraction_breakout 0.1.0-c017` |
| **Approval status** | **NOT APPROVED** — selection for next implementation sprint only |

---

## Exact thesis

After **multi-week volatility contraction** — when a pair's completed weekly
true range falls in the bottom quartile of its trailing 12-week range
distribution — a **confirmed directional breakout** from the compressed week's
high/low boundary may offer better payoff asymmetry than continuous H4 breakout
systems, with **lower turnover** and **lower cost drag**.

Each pair is evaluated **independently**. There is **no cross-sectional ranking**
across pairs. Entry occurs on the first H4 open after a completed close beyond
the compressed range (with buffer), using deduped H4 data aggregated to synthetic
weekly boundaries. Stops anchor to the opposite side of the compressed range.
Hold period is bounded by a frozen maximum (one calendar week of H4 bars).

The edge hypothesis is **single-pair volatility cycle**: contraction phases
precede expansion; trading the expansion leg after observable compression may
beat random entry at weekly cadence — without carry, without pair ranking, and
without H4-bar compression churn.

---

## Why this is the best post-C016 candidate

1. **CAMPAIGN_016 retired cross-sectional momentum.** Weekly rank long-top /
   short-bottom produced exp_r −0.0633, WITHIN_NULL, and only 137 trades.
   CAMPAIGN_017 explicitly avoids cross-sectional selection.

2. **Structural distance from CAMPAIGN_004.** 004 fired on **H4-bar** ATR
   percentile + 20-bar Donchian every qualifying bar. CAMPAIGN_017 uses
   **12-week** range compression state and trades **at most one expansion per
   compression cycle per pair** — different cadence, different state machine.

3. **Low turnover.** Target 120–350 aggregate trades vs 016's 137 (under gate)
   and 015's 375. Weekly compression cycles naturally limit entries.

4. **No financing blocker.** Pure spot breakout without carry tilt.

5. **Data compatibility.** Deduped H4 only; synthetic weekly aggregation —
   no native D1/W1 engine work (CAMPAIGN_006 blocker avoided).

6. **Falsifiable.** Tiny frozen parameter set in `CAMPAIGN_017_PRECOMMIT_DRAFT.md`.
   Gates defined before implementation.

7. **Backtrader feasible.** Single-pair state machine is simpler than 016's
   cross-pair rebalance portfolio. CAMPAIGN_015 achieved TOLERABLE_DRIFT.

8. **Ranking consensus.** Scored **A** in `DEDUPED_CANDIDATE_UNIVERSE_002.md`.
   No higher-scoring candidate without a blocker.

---

## Why this is not a retune of previous failed families

| retired family | campaign | why CAMPAIGN_017 differs |
|---|---|---|
| H4 ATR compression breakout | 004 | **Weekly** compression percentile (12-week lookback); not H4 ATR P40 + 20-bar Donchian on same bar |
| Failed-breakout reversal | 015 | **With-breakout** follow-through; not counter-trend fade of false break |
| Weekly cross-sectional momentum | 016 | **Single-pair** compression cycle; no rank long-top / short-bottom |
| Currency-strength rotation | 013 | No cross-pair ranking |
| ATR regime switcher | 012 | No per-pair strategy routing; one rule per pair |
| Session breakout | 010 | No session gate; weekly compression state |
| Mean-reversion | 008/009 | Breakout **with** expansion, not fade to midline |

CAMPAIGN_017 is thematically in the "volatility cycle" space but operates on
**weekly state** with **single-pair** entries — materially different from 004's
H4 churn and 016's cross-sectional portfolio.

---

## Expected universe

| field | value |
|---|---|
| Instruments | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD |
| Data source | OANDA practice H4 SQLite (deduped loads) |
| Walk-forward window | Same 8-fold rolling plan as CAMPAIGN_011/015/016 |

---

## Timeframe

| layer | resolution |
|---|---|
| Compression detection | Synthetic weekly true range from deduped H4 |
| Breakout confirmation | Completed H4 close beyond compressed week boundary |
| Entry fill | Next H4 open after confirmation |
| Stop / max hold | H4 bar evaluation |

---

## Expected trade count

| estimate | range |
|---|---|
| Per fold (~180 days test) | ~15–45 round trips (all pairs) |
| Aggregate (8 folds) | **~120–350** total |
| Minimum for gates (precommit draft) | ≥ **120** aggregate; ≥ **12** per fold |

Lower bound set above CAMPAIGN_016's 137 but honest for weekly cadence.
Upper bound below H4 event systems.

---

## Expected blockers

| blocker | severity | mitigation |
|---|---|---|
| Thematic adjacency to 004 | medium | Precommit documents structural differences; weekly cadence frozen |
| Sparse compression weeks | medium | Monitor per-pair trade count; abort if aggregate < 120 projected |
| Weekly boundary ambiguity | medium | Freeze Monday UTC week boundary (016 precedent) |
| Breakout whipsaw at expansion | high | Buffer + opposite-range stop; accept rejection |
| Backtrader weekly aggregation | medium | Fold-window spot check in implementation Phase 0 |
| WITHIN_NULL outcome | high | Accept rejection; do not retune |

---

## Implementation complexity

| area | effort |
|---|---|
| Weekly true-range aggregator | moderate |
| Per-pair compression / breakout state machine | moderate |
| Walk-forward integration | low (reuse harness) |
| Backtrader adapter | moderate (single-pair; simpler than 016) |
| **Overall** | **moderate** |

---

## Backtrader verification feasibility

**Feasible with caveats.**

- Weekly compression state from H4 requires explicit bar-alignment contract.
- CAMPAIGN_015 deduped achieved **TOLERABLE_DRIFT** — parity infrastructure exists.
- CAMPAIGN_016 achieved boundary parity tests; full portfolio BT was BLOCKED.
- CAMPAIGN_017 single-pair logic should be **easier** to parity-check than 016.
- Target classification: **TOLERABLE_DRIFT** or better; **DATA_MISMATCH** is stop condition.

---

## Stop conditions (reject before or during implementation)

1. Weekly boundary cannot be made deterministic across bespoke and Backtrader lanes.
2. Backtrader feasibility spike shows >50% trade-count mismatch on fold 0.
3. Precommit review classifies CAMPAIGN_017 as CAMPAIGN_004 retune — abort and re-select.
4. Aggregate trade count projection falls below **120** — insufficient sample.
5. Financing requirement discovered — defer to carry sprint.
6. Any use of contaminated 002–014 metrics to justify parameter choices.
7. Any drift toward cross-sectional ranking or 016 parameter reuse.

---

## Reasons to reject after implementation (expected failure modes)

1. Aggregate exp_r **WITHIN_NULL** (like 015, 016).
2. 2× cost stress collapses edge below null centre.
3. Single-pair or single-fold dominance >60%.
4. LOO fold stability fails.
5. Fold pass rate below precommitted minimum.
6. Backtrader drift exceeds TOLERABLE.
7. Trade count below 120 aggregate.

**None of these trigger approval.** REJECT remains the default outcome.

---

## Alternatives considered and not selected

| candidate | reason not selected |
|---|---|
| multi_day_range_expansion_after_compression | Viable B+ alternate; higher turnover; closer to 004 thematically — defer unless 017 precommit blocked |
| portfolio_volatility_regime_filter_then_simple_signal | Regime narrative overlap with 012; harder to falsify |
| daily_close_reversal_after_extreme_range | Reversal family exhausted (008/009/015); higher skepticism |
| carry_trend_hybrid | **Financing blocked** |
| pair_specific_research_lab | Lab track only, not implementation campaign |
| weekly_cross_sectional_momentum (016 retune) | **Explicitly forbidden** — family retired |

---

## Next artifact

Implementation sprint begins with review and hardening of
`docs/research/CAMPAIGN_017_PRECOMMIT_DRAFT.md` — still a draft, not code.

**No strategy approved. Paper / demo / live remain blocked.**
