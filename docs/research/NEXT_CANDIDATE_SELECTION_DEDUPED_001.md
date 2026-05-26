# Next Candidate Selection — Deduped 001

**Sprint:** NEW_CANDIDATE_DISCOVERY_DEDUPED_001  
**Branch:** `research-new-candidate-strategy-discovery-deduped-001`  
**Date:** 2026-05-26

## Selection

| field | value |
|---|---|
| **Selected candidate** | `weekly_cross_sectional_momentum_low_turnover` |
| **Proposed campaign id** | **CAMPAIGN_016** |
| **Proposed strategy version** | `weekly_cross_sectional_momentum_low_turnover 0.1.0-c016` |
| **Approval status** | **NOT APPROVED** — selection for next implementation sprint only |

---

## Exact thesis

Weekly currency-pair **relative momentum** on the seven-major OANDA practice
universe may exhibit lower turnover and lower transaction-cost sensitivity
than the H4 event, reversal, and breakout systems tested in CAMPAIGN_002–015.

Each week, rank all seven pairs by a precommitted blend of 4-week and 12-week
volatility-adjusted returns computed from deduped H4 data aggregated to weekly
boundaries. Enter long the top-ranked pair and short the bottom-ranked pair
(subject to USD exposure caps and cost filters), hold until the next weekly
rebalance or a volatility-based stop, then repeat.

The edge hypothesis is **cross-sectional**, not directional trend on a single
pair: FX majors may exhibit short-horizon relative strength persistence at
weekly frequency when costs are controlled.

---

## Why this is the best first post-dedup candidate

1. **Structural novelty.** No prior campaign used weekly cross-sectional
   ranking with long-top / short-bottom selection. CAMPAIGN_013 used daily
   strength rotation with different mechanics and was rejected; this operates
   on a slower cadence with explicit vol adjustment and USD caps.

2. **Low turnover.** Weekly rebalance targets ~1–2 round trips per week vs
   hundreds of H4 triggers. Failed campaigns (012, 013, 015) showed cost and
   turnover amplification harm; this directly addresses that lesson.

3. **No financing blocker.** Pure spot relative momentum without carry tilt.
   Unlike `multi_day_carry_trend_hybrid`, no swap-rate modeling prerequisite.

4. **Data compatibility.** Uses existing H4 SQLite via deduped `CandleRepo.list`
   with deterministic weekly aggregation — no D1 engine work (CAMPAIGN_006
   blocker avoided).

5. **Falsifiable.** Tiny precommitted parameter set (lookback blend weights,
   rebalance day, vol-adjustment method, stop multiple). Gates defined before
   code in `CAMPAIGN_016_PRECOMMIT_DRAFT.md`.

6. **Clean evidence base.** No contaminated positive evidence to anchor
   expectations. Null comparison uses deduped CAMPAIGN_011 centre only.

7. **Ranking consensus.** Scored **A** in `DEDUPED_CANDIDATE_UNIVERSE.md` on
   novelty, turnover, financing, data fit, and independence from contaminated
   evidence. No other candidate scored higher without a blocker.

---

## Why this is not a retune of previous failed families

| retired family | why CAMPAIGN_016 differs |
|---|---|
| Trend-following 002/003 | Single-pair EMA/Donchian entry, not cross-sectional rank |
| Volatility breakout 004 | H4 compression breakout, not weekly relative momentum |
| Pullback 007 | Intra-trend pullback entry |
| Mean-reversion 008/009 | Fade to range midline |
| Session breakout 010 | Session open breakout |
| Regime switcher 012 | Per-pair ATR percentile strategy routing |
| Strength rotation 013 | Daily cross-pair rotation without weekly vol-adjusted momentum blend |
| Calendar anomaly 014 | Event-window trigger |
| Failed breakout 015 | H4 false-break fade |

CAMPAIGN_016 is closest to 013 in *spirit* (cross-pair relative) but differs
in signal definition (weekly vol-adjusted momentum blend), cadence (weekly vs
daily), selection rule (top/bottom rank vs rotation schedule), and hold period.

---

## Expected universe

| field | value |
|---|---|
| Instruments | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD |
| Data source | OANDA practice H4 SQLite (deduped loads) |
| Walk-forward window | Same 8-fold rolling plan as CAMPAIGN_011/015 unless precommit revises |

---

## Timeframe

| layer | resolution |
|---|---|
| Signal computation | Weekly (5 trading-day or deterministic Monday boundary from H4) |
| Execution / stops | H4 bar resolution for fills and ATR/vol stops |
| Hold period | ~1 week (until next rebalance) unless stop hit |

---

## Expected trade count

| estimate | range |
|---|---|
| Per fold (test window ~180 days) | ~25–50 round-trip legs |
| Aggregate (8 folds) | **~400–700** total legs |
| Minimum for gates | Precommit: ≥ **300** aggregate (honest for weekly cadence) |

Lower than CAMPAIGN_011 null (1,180) and CAMPAIGN_015 deduped (375) is
acceptable if weekly cadence is precommitted; gates must adapt fold-minimum
trade counts accordingly.

---

## Expected blockers

| blocker | severity | mitigation |
|---|---|---|
| Weekly bar boundary ambiguity | medium | Precommit deterministic UTC boundary |
| USD exposure cap reduces trades | low | Document one-sided mode when cap binds |
| Low fold trade count | medium | Adapt fold gates; aggregate minimum 300 |
| Backtrader weekly aggregation | medium | Feasibility spike in precommit Phase 0 |
| Momentum may be WITHIN_NULL like 015 | high | Accept rejection; do not retune |

---

## Implementation complexity

| area | effort |
|---|---|
| Weekly return / vol aggregator | moderate |
| Cross-sectional rank + USD cap | moderate |
| Walk-forward integration | low (reuse CAMPAIGN_011/015 harness) |
| Backtrader adapter | moderate (weekly signal, H4 execution) |
| **Overall** | **moderate** — no new data source or financing model |

---

## Backtrader verification feasibility

**Feasible with caveats.**

- Weekly signal on H4 data requires explicit bar-alignment contract (same as
  bespoke lane).
- CAMPAIGN_015 deduped achieved **TOLERABLE_DRIFT** — parity infrastructure
  exists for fold-window comparison.
- Precommit will require fold-window Backtrader spot check before full
  walk-forward verdict.
- Classification target: **TOLERABLE_DRIFT** or better; **DATA_MISMATCH** is
  a stop condition.

---

## Stop conditions (reject before or during implementation)

1. **Weekly boundary cannot be made deterministic** across bespoke and
   Backtrader lanes.
2. **Backtrader feasibility spike** shows >50% trade-count mismatch on fold 0.
3. **Precommit review** reveals overlap with CAMPAIGN_013 sufficient to classify
   as retune — abort and re-select from universe.
4. **Aggregate trade count projection** falls below 200 even with relaxed USD
   cap — insufficient sample for any gate.
5. **Financing requirement discovered** during design — defer to carry sprint.
6. **Any use of contaminated 002–014 metrics** to justify parameter choices.

---

## Reasons to reject after implementation (expected failure modes)

1. Aggregate exp_r **WITHIN_NULL** band (like deduped CAMPAIGN_015).
2. 2× cost stress collapses edge below null.
3. Single-pair or single-fold dominance >60%.
4. LOO fold stability fails.
5. Fold pass rate < precommitted minimum.
6. Backtrader drift exceeds TOLERABLE.

**None of these trigger approval.** REJECT remains the default outcome until
a future human-reviewed approval process explicitly changes policy.

---

## Alternatives considered and not selected

| candidate | reason not selected |
|---|---|
| weekly_volatility_contraction_breakout | Thematic overlap with rejected 004 breakout family |
| portfolio_volatility_regime_filter_then_signal | Regime narrative overlap with 012; harder to falsify |
| multi_day_carry_trend_hybrid | **Financing blocked** |
| session_range_reversal_cost_gated | Too close to rejected 010/015 session-reversal space |
| pair_specific_research_lab | Lab track only, not implementation campaign |

---

## Next artifact

Implementation sprint begins with review and hardening of
`docs/research/CAMPAIGN_016_PRECOMMIT_DRAFT.md` — still a draft, not code.
