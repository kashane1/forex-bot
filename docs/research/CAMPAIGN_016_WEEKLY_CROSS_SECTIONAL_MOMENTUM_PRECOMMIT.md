# CAMPAIGN_016 Pre-Commit — `weekly_cross_sectional_momentum_low_turnover 0.1.0-c016`

**Date:** 2026-05-26 · **Branch:** `research-weekly-cross-sectional-momentum-001`
`strategy_evidence: false`

Phase 0 binding pre-commit for **CAMPAIGN_016 /
`weekly_cross_sectional_momentum_low_turnover 0.1.0-c016`**. This
pre-commit freezes the hypothesis, structural distinctness rationale,
strategy rules, frozen parameters, fill timing, cost treatment,
walk-forward plan, gate vector, anti-overfit gate vector, null
comparison plan, Backtrader secondary-lane plan, and BLOCKED conditions
**before** any code in this sprint runs `generate_signal` against real
candles. The Phase 3 runner will `_assert_frozen()` against the values
below; any deviation aborts before any backtest fires.

> **Maximum possible verdict for this sprint is `PASS_RESEARCH_SCREEN`
> ("candidate for human review"). No strategy is approved. Even a
> clean screen pass leaves `configs/approved_strategies.yaml` at
> `approved: []`. Paper / demo / live loops remain blocked.**

CAMPAIGN_001 — CAMPAIGN_015 are historical evidence and remain
untouched.

---

## 1. Thesis (binding)

Weekly cross-sectional relative momentum across the seven-pair H4
universe may produce lower turnover and lower cost sensitivity than
prior H4 event/reversal/breakout systems. Rank all majors by blended
multi-week vol-adjusted momentum, go long the top-ranked pair and
short the bottom-ranked pair, rebalance once per week, and hold until
the next weekly rebalance or an H4 ATR stop — without carry/financing
alpha claims.

---

## 2. Why structurally distinct from CAMPAIGN_002–015

| campaign | family | cadence | selection | why C016 differs |
|---|---|---|---|---|
| 002–004 | trend / vol breakout | H4 bar | single-pair Donchian / compression | C016 ranks **all seven pairs** weekly; no Donchian; no breakout follow-through. |
| 007–009 | pullback / mean reversion | H4 bar | single-pair z-score / EMA | C016 is **cross-sectional relative** momentum, not mean reversion to a pair midline. |
| 010 | session breakout | H4 + session gate | Asian-range / London | C016 has **no session gate**; weekly rebalance only. |
| 011 | random entry anchor | H4 bar | null control | C016 is a **real hypothesis**, not a null model. |
| 012 | ATR regime switcher | H4 + D1 regime | regime-conditional direction | C016 has **no D1 regime input**; weekly cross-section only. |
| 013 | currency-strength rotation | H4 bar | 8-currency rank gap | C013 uses **H4 bar** strength; C016 uses **synthetic weekly** returns from H4; C013 trades any pair above gap; C016 trades **exactly top + bottom** only. |
| 014 | calendar event anomaly | event-conditional | macro calendar | C016 has **no event calendar**. |
| 015 | failed-breakout reversal | H4 bar | single-pair sweep fade | C016 is **with-momentum** cross-section, not counter-trend fade. |

C016 is the **first sprint** to test weekly cross-sectional momentum
with explicit low-turnover portfolio constraints. It is not a parameter
sweep of any prior candidate.

---

## 3. Why this is not a retune

* Lookbacks are **weeks** (4 / 12), not H4 bars (20 / 24 / 14).
* Signal fires on **weekly rebalance boundaries**, not every H4 bar.
* Selection is **portfolio-relative** (top/bottom of seven), not
  per-pair absolute rules.
* Expected trade count **120–500** aggregate (weekly cadence), not
  200–800 H4 churn.
* No ADX, Donchian, z-score, session, event, or failed-sweep logic.

Any deviation from §5 constitutes a **NEW candidate**; the runner
rejects it.

---

## 4. Implementation files (committed by this sprint)

| file | role |
|---|---|
| `src/forex_bot/features/weekly_momentum.py` | synthetic weekly aggregation from H4 |
| `tests/unit/test_weekly_momentum.py` | weekly feature unit tests |
| `src/forex_bot/strategies/weekly_cross_sectional_momentum_low_turnover.py` | strategy module |
| `src/forex_bot/config.py` | `WeeklyCrossSectionalMomentumLowTurnoverStrategyConfig` |
| `configs/campaign_016_weekly_cross_sectional_momentum.yaml` | research config |
| `scripts/run_campaign_016.py` | walk-forward runner |
| `research/anti_overfit/campaign_016.py` | anti-overfit classifier |
| `scripts/run_campaign_016_anti_overfit_diagnostics.py` | null / anti-overfit runner |
| `research/backtrader_lane/strategies/campaign_016_weekly_cross_sectional_momentum.py` | BT adapter |
| `docs/research/CAMPAIGN_016_WEEKLY_CROSS_SECTIONAL_MOMENTUM_PRECOMMIT.md` | this document |

`configs/approved_strategies.yaml` is **not** modified.

---

## 5. Frozen parameters (binding, verbatim)

```yaml
strategy: weekly_cross_sectional_momentum_low_turnover
version: 0.1.0-c016
timeframe: H4
source_timeframe: H4
aggregation: synthetic_weekly_from_h4
rebalance_cadence: weekly
rebalance_anchor: first_completed_h4_bar_on_or_after_monday_00_00_utc
momentum_lookback_fast_weeks: 4
momentum_lookback_slow_weeks: 12
momentum_blend_fast: 0.5
momentum_blend_slow: 0.5
volatility_lookback_weeks: 12
volatility_floor: 1.0e-8
selection: top_1_long_bottom_1_short
max_positions: 2
max_same_currency_exposure: 1
holding_period: until_next_weekly_rebalance_or_stop
atr_lookback: 14
atr_stop_multiple: 2.5
max_bars_in_trade: 42
take_profit_r: null
trailing_stop_atr_multiple: null
entry_timing: next_bar_open
same_bar_adverse_stop_wins: true
spread_to_atr_max: 0.15
min_atr_pips: {}
risk.risk_per_trade_pct: 0.50
```

**Universe (7 majors):** `EUR_USD`, `GBP_USD`, `USD_JPY`, `AUD_USD`,
`USD_CAD`, `USD_CHF`, `NZD_USD`

**Weekly aggregation:** H4 deduped candles only. No native D1/W1/OANDA
daily candles. Weekly close = last H4 close in each Monday-start UTC
week. Incomplete current week excluded from momentum lookback.

**Score:**

```
fast_ret = log(close_w / close_{w-4})
slow_ret = log(close_w / close_{w-12})
vol = stdev(weekly_log_returns, last 12 complete weeks)
fast_adj = fast_ret / vol
slow_adj = slow_ret / vol
score = 0.5 * fast_adj + 0.5 * slow_adj
```

Reject pair if `vol` is non-finite or `<= volatility_floor`.

**Selection:** rank descending by `score`; long rank-1; short rank-7.
Alphabetic pair-name tiebreak. If USD same-direction exposure blocks
one leg, take the unblocked leg only; if both blocked, skip week.

**Stop:** `2.5 × ATR(14)` H4 from entry reference close; hard stop
only; no trailing; no take-profit.

**Adverse stop ambiguity:** `same_bar_adverse_stop_wins = true`
(canonical `BacktestEngine` semantics).

**Cost stress:** base and 2× mandatory.

---

## 6. Walk-forward plan

| field | value |
|---|---|
| Folds | 8 rolling |
| Split style | rolling |
| Parameter mode | frozen |
| Train / val / test / step | 540 / 180 / 180 / 180 days |
| Universe | 2020-01-01 .. 2026-05-20 |
| Data path | deduped `CandleRepo.list` / `list_with_dedupe_stats` only |
| Warm-up margin | 400 calendar days (12-week weekly lookback + H4 burn-in) |
| `strategy_evidence` | false |

---

## 7. Pass / fail gates

### Null centre

* **Source:** `research/null_baselines/campaign_011_deduped_null_baseline.json`
* **Centre exp_r:** −0.0029154071495408797
* **Band:** ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair (informational)

### Aggregate gates (base cost)

| gate | threshold |
|---|---|
| aggregate expectancy R | ≥ **0.03** R (> null + 0.03 R) |
| aggregate trades | ≥ **120**, ≤ **500** |
| profit factor | ≥ **1.05** |
| fold pass rate | ≥ **5 / 8** |
| pairs positive | ≥ **4 / 7** |
| single-pair dominance (gross +R) | ≤ **60%** |

### Aggregate gates (2× cost)

| gate | threshold |
|---|---|
| aggregate expectancy R | ≥ **0.00** R |
| profit factor | ≥ **1.00** |

### Per-fold gates

| gate | threshold |
|---|---|
| trade count | ≥ **15** |
| expectancy R | ≥ **0.0** |
| pairs positive | ≥ **2 / 7** |
| single-pair dominance | ≤ **60%** |

**Verdict:** `PASS_RESEARCH_SCREEN` only if **base and 2×** aggregate
gates pass. Otherwise `REJECT`. Missing data → `BLOCKED`.

---

## 8. Anti-overfit gates

| gate | threshold |
|---|---|
| LOO min mean gap vs null | ≥ **0.05** R |
| per-fold t-stat | ≥ **2.0** |
| median per-fold expectancy | ≥ **0** |
| trade-level cumulative R | > **0** |
| pair concentration | ≤ **70%** |
| fold concentration | ≤ **60%** |
| cost dominance | ≤ **50%** |

Labels: `ROBUST_ABOVE_NULL`, `ABOVE_NULL_BUT_FRAGILE`,
`SELECTED_CELL_ARTIFACT`, `WITHIN_NULL`, `WORSE_THAN_NULL`, `BLOCKED`.

Minimum acceptable for a non-reject screen: `ROBUST_ABOVE_NULL` or
`ABOVE_NULL_BUT_FRAGILE`.

---

## 9. Backtrader verification plan

1. Export deduped Lean CSVs from same SQLite as bespoke.
2. Implement weekly momentum + rebalance in BT lane with H4 execution.
3. Run fold-window comparison (fold 0 + fold 3 minimum).
4. Classify: `PASS`, `TOLERABLE_DRIFT`, or documented non-blocking
   reason per CAMPAIGN_015 precedent (≤35% trade-count drift).
5. Document in `BACKTRADER_CAMPAIGN_016_COMPARISON.md`.

---

## 10. Blocked conditions

1. `database_path` missing or zero candles for any pair/fold.
2. Non-`oanda-practice` H4 source for any pair.
3. Frozen-parameter mismatch (`_assert_frozen` abort).
4. Native D1/W1 data used in signal path.
5. Parameter tuning after seeing results.
6. Revival of CAMPAIGN_015 / session / reversal logic.
7. Any attempt to add strategy to `approved_strategies.yaml`.

---

## 11. Explicit non-approval statement

**No strategy is approved by this sprint.** The best possible outcome
is **`PASS_RESEARCH_SCREEN`**, which means "worth human review as a
research candidate" — not paper, demo, or live enablement.
`configs/approved_strategies.yaml` remains `approved: []`.

---

## 12. Related documents

| doc | purpose |
|---|---|
| `CAMPAIGN_016_PRECOMMIT_DRAFT.md` | discovery sprint draft |
| `campaign_011_deduped_null_baseline.json` | null centre |
| `CAMPAIGN_015_DEDUPED_NULL_AND_ANTI_OVERFIT.md` | anti-overfit template |
