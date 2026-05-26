# CAMPAIGN_017 Precommit Draft

**Status:** DRAFT ONLY — not implementation, not approval  
**Sprint:** NEW_CANDIDATE_DISCOVERY_DEDUPED_002  
**Branch:** `research-new-candidate-strategy-discovery-deduped-002`  
**Date:** 2026-05-26

> This document is a **precommit draft** for the next implementation sprint.
> No strategy code, config, or walk-forward run exists yet. Passing gates
> does **not** approve the strategy for paper, demo, or live trading.

---

## 1. Identity

| field | value |
|---|---|
| Campaign id | **CAMPAIGN_017** |
| Strategy name | `weekly_volatility_contraction_breakout` |
| Strategy version | `0.1.0-c017` |
| Hypothesis class | Weekly volatility contraction → confirmed expansion breakout |
| Prior art distance | Not a retune of CAMPAIGN_002–016 (see selection doc) |

---

## 2. Core thesis

After **multi-week volatility contraction**, a completed breakout from the
compressed weekly/multi-day range may have better payoff asymmetry than
continuous H4 breakout systems, with **lower turnover** and **lower cost drag**.

Each pair trades independently when its own weekly compression cycle completes
and price confirms expansion beyond the compressed range. No cross-sectional
ranking. No carry alpha claims.

---

## 3. Frozen candidate settings (binding draft)

### Universe

Same seven majors as all prior campaigns:

`EUR_USD`, `GBP_USD`, `USD_JPY`, `AUD_USD`, `USD_CAD`, `USD_CHF`, `NZD_USD`

### Data source

- OANDA practice H4 SQLite via **deduped `CandleRepo.list` only**
- Policy: `keep_last`
- **No native D1/W1 candles** — all weekly aggregates synthetic from H4

### Weekly aggregation (frozen)

| parameter | value |
|---|---|
| week boundary | Monday 00:00 UTC |
| week completion | last completed H4 bar whose open time falls before next Monday 00:00 UTC |
| weekly true range | `max(weekly_high) − min(weekly_low)` from H4 bars in week |
| aggregation module | new `weekly_volatility` feature (implementation sprint) |

### Compression detection (frozen)

| parameter | value |
|---|---|
| compression lookback | **12 weeks** |
| compression metric | current completed week's true range |
| compression threshold | current week TR **≤ 25th percentile** of trailing 12 weekly TR values (inclusive) |
| minimum history | 12 completed weeks before first compression signal |
| concurrent compression | allowed on multiple pairs independently |

When compression holds, record **compressed week high** and **compressed week low**
as the breakout range for the subsequent expansion watch.

### Breakout confirmation (frozen)

| parameter | value |
|---|---|
| breakout range | prior compressed week's high (long) / low (short) |
| confirmation bar | completed H4 bar after compression week ends |
| long trigger | `close[t] > compressed_high + buffer` |
| short trigger | `close[t] < compressed_low − buffer` |
| breakout buffer | **0.25 × ATR(14) H4** at bar `t` (Wilder) |
| direction | breakout direction only — **no fade** |
| one shot per compression | after entry or invalidation, wait for next compression cycle |

### Entry (frozen)

| parameter | value |
|---|---|
| fill timing | **next H4 open** after confirmation bar close |
| entry type | market at open |
| cost filter | skip if `spread / ATR(14) > 0.15` (same order of magnitude as 015/016) |
| pyramiding | **none** |
| re-entry same cycle | **forbidden** |

### Stop (frozen — choice locked)

**Chosen: opposite side of compressed range.**

| direction | stop price |
|---|---|
| long | `compressed_low − buffer` (same buffer as entry) |
| short | `compressed_high + buffer` |

Rationale: stop is **thesis-native** — if price returns inside the compressed
range, the expansion hypothesis failed. The rejected alternative (2.5 × ATR H4)
is **not permitted** in v0.1.0-c017 without new precommit sprint.

Stop evaluated on H4 bar **close** (consistent with prior campaigns).

### Max hold (frozen — choice locked)

**Chosen: 42 H4 bars (~one calendar week of H4 bars).**

| parameter | value |
|---|---|
| max hold | **42 H4 bars** from entry bar |
| exit at max hold | market close of bar when count reached |
| take-profit | **none** |
| trailing stop | **none** in v0.1.0-c017 |

The rejected alternative (10 H4 bars) is **not permitted** without new precommit.

### Position limits (frozen)

| parameter | value |
|---|---|
| max open positions per pair | **1** |
| max open positions portfolio | **2** |
| selection when >2 signals same bar | priority order: `EUR_USD`, `GBP_USD`, `USD_JPY`, `AUD_USD`, `USD_CAD`, `USD_CHF`, `NZD_USD` — take first two eligible; skip rest |
| risk per trade | **0.50%** equity |

### Cost stress (frozen)

| lane | spread multiplier |
|---|---|
| base | 1.0× |
| stress | **2.0×** |

Both lanes mandatory for walk-forward verdict.

---

## 4. Expected trade count

| estimate | value |
|---|---|
| target aggregate | 120–350 round trips over 8 folds |
| minimum gate | ≥ **120** aggregate |
| per-fold minimum | ≥ **12** trades |

Honest for low-turnover weekly cadence. Below 120 → **BLOCKED** (insufficient sample).

---

## 5. Walk-forward plan

| field | value |
|---|---|
| Folds | 8 rolling (same windows as CAMPAIGN_011/015/016) |
| Split style | rolling |
| Parameter mode | frozen |
| Train / val / test | inherited (540 / 180 / 180 day pattern) |
| strategy_evidence | false until walk-forward completes |
| input path | deduped `CandleRepo.list` only |

Fold windows: `research/null_baselines/campaign_011_deduped_null_baseline.json` §fold_windows.

---

## 6. Pass / fail gates

### Primary gates (base lane)

| gate | threshold |
|---|---|
| aggregate expectancy R | ≥ **0.03 R** |
| aggregate profit factor | ≥ **1.05** |
| aggregate trades | ≥ **120** and ≤ **500** |
| fold pass rate | ≥ **3 / 8** (adapted for low turnover) |
| per-fold minimum trades | ≥ **12** |
| pairs with positive exp_r | ≥ **3 / 7** |
| single-pair dominance (gross +R share) | ≤ **60%** |
| single-fold dominance (return share) | ≤ **60%** |

### 2× cost stress gates

| gate | threshold |
|---|---|
| aggregate expectancy R | ≥ **0.0 R** |
| aggregate profit factor | ≥ **1.0** |

### Verdict rule

- **REJECT** if any primary gate fails OR 2× stress gates fail.
- **PASS_RESEARCH_SCREEN** only if all gates pass AND anti-overfit passes — still **not approved** for paper/demo/live.
- Default expected outcome: **REJECT**.

---

## 7. Null comparison plan

| field | value |
|---|---|
| null centre exp_r | **−0.0029154071495408797** |
| null source | `research/null_baselines/campaign_011_deduped_null_baseline.json` |
| null per-fold std | **0.0479** |
| comparison band | ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair |

Report:

- aggregate exp_r gap vs null centre
- per-fold exp_r vs null fold distribution
- anti-overfit classifier label (WITHIN_NULL / WORSE_THAN_NULL / ROBUST_ABOVE_NULL)

---

## 8. Anti-overfit gates

| gate | threshold |
|---|---|
| LOO min mean gap vs null | ≥ **0.05 R** |
| per-fold t-stat (exp_r > 0) | ≥ **2.0** on median fold |
| median per-fold exp_r | ≥ **0** |
| trade-level cumulative R | **> 0** |
| pair concentration (gross +R) | ≤ **70%** |
| fold concentration (return share) | ≤ **60%** |
| cost dominance (spread / gross P&L) | ≤ **50%** |

Classifier defaults to **WITHIN_NULL** unless aggregate floor and multi-axis
separation both pass.

---

## 9. Backtrader plan

| step | action |
|---|---|
| Phase 0 | Weekly boundary + compression state parity unit tests (016 precedent) |
| Phase 1 | Single-pair adapter stub with frozen parameters |
| Phase 2 | Fold-window comparison on fold 0 (all seven pairs) |
| Phase 3 | If fold 0 TOLERABLE_DRIFT, spot-check folds 2 and 5 |
| Classification | TOLERABLE_DRIFT / MATERIAL_DRIFT / DATA_MISMATCH / BLOCKED |

**Non-decision-blocking** if bespoke lane already REJECT on primary gates.
**Stop condition** if DATA_MISMATCH on fold 0 before bespoke walk-forward completes.

Target: simpler than CAMPAIGN_016 (no cross-pair rebalance state).

Artifacts path (implementation sprint):

- `research/campaign_017/diagnostics/backtrader_comparison.json`
- `research/backtrader_lane/strategies/campaign_017_weekly_volatility_contraction_breakout.py`

---

## 10. Why not CAMPAIGN_004 volatility breakout retune

| dimension | CAMPAIGN_004 | CAMPAIGN_017 |
|---|---|---|
| compression measure | H4 ATR-14 ≤ P40 of **60 H4 bars** | weekly TR ≤ P25 of **12 weeks** |
| trigger | Donchian 20-bar on **same H4 bar** | close beyond **compressed week** high/low |
| cadence | every qualifying H4 bar | once per compression cycle per pair |
| hold | H4 trailing stop + max bars | opposite-range stop + **42 H4 bar** cap |
| expected trades | high H4 churn | **120–350** aggregate |
| cross-section | single-pair | single-pair (same) but **different state machine** |

004 tested "quiet H4 bar → immediate Donchian break." 017 tests "quiet **week**
→ confirmed expansion break on next H4 boundary." Retuning 004 lookbacks (60→12,
P40→P25) would **not** satisfy structural distinctness — rejected.

---

## 11. Why not CAMPAIGN_016 retune

| dimension | CAMPAIGN_016 | CAMPAIGN_017 |
|---|---|---|
| signal | cross-sectional momentum rank | per-pair compression → breakout |
| selection | long rank-1, short rank-7 | independent per-pair breakout |
| rebalance | weekly momentum rebalance | event-driven on compression cycle |
| stop | 2.5 × ATR H4 | opposite compressed range boundary |
| hold | until next rebalance (42 bars max implicit) | 42 H4 bars from entry |
| result | REJECT exp_r −0.0633 | untested |

Any reuse of 016 lookbacks (4w/12w momentum), blend weights, rank rules, or
USD caps constitutes a **retune** — forbidden.

---

## 12. Blocked conditions (abort before implementation)

1. Precommit review classifies C017 as CAMPAIGN_004 retune.
2. Weekly boundary non-deterministic across bespoke / Backtrader.
3. Projected aggregate trades < **120**.
4. Design drifts toward cross-sectional ranking (013/016).
5. Design drifts toward failed-breakout fade (015).
6. Native D1/W1 data required.
7. Carry/financing alpha required.
8. Parameter grid beyond §3 frozen set proposed.
9. Contaminated 002–014 metrics used to justify parameters.

---

## 13. Explicit non-goals

- **No approval** — `configs/approved_strategies.yaml` stays `approved: []`
- **No paper / demo / live** enablement
- **No OANDA / broker API** calls in research sprint
- **No CAMPAIGN_016 retune**
- **No CAMPAIGN_015 revival**
- **No strategy code** in this discovery sprint (draft only)

---

## 14. Implementation files (future sprint — not committed here)

| file | role |
|---|---|
| `src/forex_bot/features/weekly_volatility.py` | synthetic weekly TR + compression detection |
| `src/forex_bot/strategies/weekly_volatility_contraction_breakout.py` | strategy module |
| `configs/campaign_017_weekly_volatility_contraction_breakout.yaml` | research config |
| `scripts/run_campaign_017.py` | walk-forward runner |
| `research/anti_overfit/campaign_017.py` | anti-overfit classifier |
| `research/backtrader_lane/strategies/campaign_017_*.py` | BT adapter |

---

## 15. Approval statement

**No strategy is approved.** This precommit draft does not modify
`configs/approved_strategies.yaml`. Paper, demo, and live trading remain
blocked regardless of future walk-forward outcome.

Maximum possible verdict after implementation: **PASS_RESEARCH_SCREEN**
(candidate for human review). Default expected verdict: **REJECT**.
