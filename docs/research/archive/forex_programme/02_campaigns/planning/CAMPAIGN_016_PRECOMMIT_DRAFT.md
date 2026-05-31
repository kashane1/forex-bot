# CAMPAIGN_016 Precommit Draft

**Status:** DRAFT ONLY — not implementation, not approval  
**Sprint:** NEW_CANDIDATE_DISCOVERY_DEDUPED_001  
**Branch:** `research-new-candidate-strategy-discovery-deduped-001`  
**Date:** 2026-05-26

> This document is a **precommit draft** for the next implementation sprint.
> No strategy code, config, or walk-forward run exists yet. Passing gates
> does **not** approve the strategy for paper, demo, or live trading.

---

## 1. Identity

| field | value |
|---|---|
| Campaign id | **CAMPAIGN_016** |
| Strategy name | `weekly_cross_sectional_momentum_low_turnover` |
| Strategy version | `0.1.0-c016` |
| Hypothesis class | Cross-sectional relative momentum, weekly cadence |
| Prior art distance | Not a retune of CAMPAIGN_002–015 (see selection doc) |

---

## 2. Core thesis

Weekly currency-pair relative momentum may have lower turnover and lower
cost sensitivity than H4 event/reversal/breakout systems. Rank seven major
pairs by multi-week return adjusted by volatility, trade only the strongest
and weakest pairs with USD exposure caps, rebalance weekly, and hold for
multi-day windows.

---

## 3. Candidate sketch

### Universe

Same seven majors as all prior campaigns:

`EUR_USD`, `GBP_USD`, `USD_JPY`, `AUD_USD`, `USD_CAD`, `USD_CHF`, `NZD_USD`

### Timeframe

- **Signal:** weekly — aggregate deduped H4 closes to 5-trading-day returns
  (or calendar-week with deterministic boundary; see §3.4).
- **Execution:** H4 bar fills at rebalance open.
- **Stops:** ATR-based on H4, wide enough to avoid H4 noise (precommitted multiple).

### Signal cadence

- **Rebalance:** once per week.
- **Boundary (draft):** first H4 bar whose UTC timestamp falls on or after
  Monday 00:00 UTC after the prior rebalance, using completed bars only.
- Alternative (if Monday illiquid): first completed H4 bar of the trading week
  per OANDA calendar — **must pick one in final precommit; no grid search.**

### Lookback (frozen tiny set)

| parameter | value | notes |
|---|---:|---|
| short momentum lookback | 4 weeks | 20 trading days |
| long momentum lookback | 12 weeks | 60 trading days |
| blend weight (short) | 0.5 | equal blend |
| blend weight (long) | 0.5 | equal blend |
| vol adjustment | divide raw return by 20-day realized vol (H4) | rank stability |

No other lookback values permitted without new precommit sprint.

### Trade selection

1. Compute blended vol-adjusted momentum score for each pair.
2. Rank descending.
3. **Long** top-ranked pair; **short** bottom-ranked pair.
4. If USD exposure cap blocks one leg, take the unblocked leg only (document).
5. If both blocked, skip week (no trade).
6. Max **2** concurrent positions (one long, one short).

### Holding period

- Hold until next weekly rebalance **or** stop hit, whichever first.
- No intraweek rebalance except stop exit.

### Stop

- **Stop distance:** 2.5 × 20-day ATR (H4) from entry — precommitted.
- Stop evaluated on H4 bar close (same as prior campaigns).
- No trailing stop in v0.1.0-c016.

### Risk

- Per-position risk: **0.5%** of equity (precommitted).
- Portfolio gross exposure cap: **2.0%** combined (two 0.5% legs + headroom).
- USD exposure cap: net USD delta ≤ **1.0%** equity equivalent (precommitted).
- No pyramiding, no martingale, no grid.

### Cost filters

- Skip entry if spread / ATR > **0.15** (precommitted, same order of magnitude as 015).
- Weekend / rollover: hold through unless stop; document financing in overlay.
- 2× cost stress lane mandatory.

### Expected trade count

- **Target aggregate:** 400–700 round-trip legs over 8 folds.
- **Minimum gate (draft):** ≥ **300** aggregate trades.
- **Per-fold minimum (draft):** ≥ **25** trades (adapted for weekly cadence).

---

## 4. Walk-forward plan

| field | value |
|---|---|
| Folds | 8 rolling (same windows as CAMPAIGN_011/015 unless audit finds reason to change) |
| Split style | rolling |
| Parameter mode | frozen |
| Train / val / test | 540 / 180 / 180 / 180 days (inherited) |
| strategy_evidence | false until walk-forward completes |

Data path: **deduped `CandleRepo.list` only.**

---

## 5. Gates

### Primary gates

| gate | threshold (draft) |
|---|---|
| aggregate expectancy R | > deduped null + band (see §6) |
| aggregate trades | ≥ 300 |
| fold pass rate | ≥ 3 / 8 (adapted for weekly — lower bar than H4 systems) |
| per-fold minimum trades | ≥ 25 |
| 2× cost aggregate exp_r | > null centre |
| pair positivity | ≥ 3 / 7 |
| single-pair dominance | ≤ 70% return share |
| single-fold dominance | ≤ 60% return share |

### Null comparison

- **Centre:** deduped CAMPAIGN_011 aggregate exp_r **−0.0029154071495408797**
- **Band:** ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair
- **Source:** `research/null_baselines/campaign_011_deduped_null_baseline.json`

### Anti-overfit gates

| gate | threshold |
|---|---|
| LOO min mean gap vs null | ≥ 0.05 R |
| per-fold t-stat | ≥ 2.0 |
| median per-fold expectancy | ≥ 0 |
| trade-level cumulative R | > 0 |
| pair concentration | ≤ 70% |
| fold concentration | ≤ 60% |
| cost dominance | ≤ 50% of gross P&L |

Label: **ROBUST_ABOVE_NULL** only if all pass; else **WITHIN_NULL** or **BELOW_NULL**.

### Backtrader gates

| gate | threshold |
|---|---|
| fold-window spot check | fold 0 + fold 3 minimum |
| trade count drift | ≤ 35% aggregate (TOLERABLE_DRIFT per 015 precedent) |
| classification | TOLERABLE_DRIFT or better |

### Approval gate

| gate | value |
|---|---|
| Add to approved_strategies.yaml | **FORBIDDEN** in this campaign |
| Paper / demo / live | **FORBIDDEN** regardless of screen outcome |

---

## 6. Blocked conditions (stop before run)

1. Config or code uses non-deduped SQLite path.
2. Parameter count exceeds precommitted tiny set.
3. Backtrader feasibility spike fails TOLERABLE_DRIFT on fold 0.
4. Weekly boundary differs between bespoke and Backtrader without documented fix.
5. Any gate threshold tuned using contaminated CAMPAIGN_002–014 metrics.
6. Revival of CAMPAIGN_015 or session/reversal logic.

---

## 7. Null comparison plan

1. Run CAMPAIGN_016 walk-forward on deduped data.
2. Compute aggregate and per-fold exp_r.
3. Load canonical null from `campaign_011_deduped_null_baseline.json`.
4. Compute gap = CAMPAIGN_016 exp_r − null exp_r on each axis.
5. Run anti-overfit diagnostic script (same framework as CAMPAIGN_015 deduped).
6. Document in `CAMPAIGN_016_NULL_AND_ANTI_OVERFIT.md`.
7. If WITHIN_NULL: **REJECT** — do not retune.

---

## 8. Backtrader plan

1. Export deduped Lean CSVs from same SQLite as bespoke (existing pipeline).
2. Implement weekly momentum signal in Backtrader lane with H4 execution.
3. Run `fold_windows` mode with `strict_test_window=true`.
4. Compare fold 0 and fold 3 trade counts and exp_r.
5. Classify per `BACKTRADER_CAMPAIGN_015_DEDUPED_COMPARISON.md` precedent.
6. Document in `BACKTRADER_CAMPAIGN_016_DEDUPED_COMPARISON.md`.
7. Full 8-fold BT comparison optional if spot check passes.

---

## 9. Financing treatment

- **Primary lane:** spot P&L without carry alpha claim.
- **Overlay:** run ESTIMATED + conservative financing overlay (same as 010/013)
  for documentation only — not used to rescue a failing spot screen.
- **No carry tilt** in signal; financing is risk disclosure, not edge source.

---

## 10. Exact reasons this candidate will be rejected

Expect **REJECT** if any of the following hold (likely scenarios):

1. **WITHIN_NULL** — weekly FX momentum indistinguishable from random entry.
2. **BELOW_NULL** — worse than null baseline on aggregate exp_r.
3. **2× cost failure** — edge disappears under spread stress.
4. **Concentration** — one pair (likely GBP_USD or USD_JPY) dominates P&L.
5. **Fold instability** — LOO gaps fail anti-overfit gates.
6. **Insufficient trades** — USD cap + cost filter reduce sample below 300.
7. **Backtrader DATA_MISMATCH** — cannot trust bespoke results.
8. **Retune pressure** — team tempted to adjust lookback blend after seeing
   results (violates precommit; abort rather than tune).

---

## 11. Implementation sprint checklist (future, not this sprint)

- [ ] Finalize weekly boundary choice
- [ ] Write `configs/campaign_016_weekly_cross_sectional_momentum.yaml`
- [ ] Implement strategy module under `src/forex_bot/strategies/`
- [ ] Add walk-forward runner hook
- [ ] Backtrader feasibility spike (fold 0)
- [ ] Full 8-fold walk-forward + 2× cost
- [ ] Null and anti-overfit diagnostics
- [ ] Evidence summary and REJECT/PASS screen (PASS ≠ approval)
- [ ] Update `STRATEGY_STATUS.md` and `EVIDENCE_INDEX.md`

---

## 12. Related documents

| doc | purpose |
|---|---|
| `POST_DEDUP_EVIDENCE_MAP.md` | Evidence integrity context |
| `DEDUPED_CANDIDATE_UNIVERSE.md` | Full candidate ranking |
| `NEXT_CANDIDATE_SELECTION_DEDUPED_001.md` | Selection rationale |
| `campaign_011_deduped_null_baseline.json` | Null centre |
| `CAMPAIGN_015_DEDUPED_NULL_AND_ANTI_OVERFIT.md` | Anti-overfit template |

---

## 13. Draft disclaimer

This precommit is **DRAFT ONLY**. Thresholds marked "draft" require review
during the implementation sprint opening. No code, config, or backtest artifacts
exist for CAMPAIGN_016 on this branch.

**No strategy is approved. Paper, demo, and live remain blocked.**
