# CAMPAIGN_017 Pre-Commit — `weekly_volatility_contraction_breakout 0.1.0-c017`

**Date:** 2026-05-26 · **Branch:** `research-weekly-volatility-contraction-breakout-001`
`strategy_evidence: false`

Phase 0 binding pre-commit for **CAMPAIGN_017 /
`weekly_volatility_contraction_breakout 0.1.0-c017`**. This pre-commit
freezes the hypothesis, structural distinctness rationale, strategy rules,
frozen parameters, fill timing, cost treatment, walk-forward plan, gate
vector, anti-overfit gate vector, null comparison plan, Backtrader
secondary-lane plan, and BLOCKED conditions **before** any code in this
sprint runs `generate_signal` against real candles.

> **Maximum possible verdict for this sprint is `PASS_RESEARCH_SCREEN`
> ("candidate for human review"). No strategy is approved. Even a
> clean screen pass leaves `configs/approved_strategies.yaml` at
> `approved: []`. Paper / demo / live loops remain blocked.**

CAMPAIGN_001 — CAMPAIGN_016 are historical evidence and remain untouched.

---

## 1. Thesis (binding)

Weekly volatility contraction followed by confirmed breakout may offer
lower turnover and better payoff asymmetry than continuous H4 breakout
systems. Synthesize weekly compression ranges from deduped H4 candles only,
trade breakouts from compressed weeks per pair independently, and avoid
native D1/W1 candles.

---

## 2. Why structurally distinct from CAMPAIGN_004 and CAMPAIGN_016

| dimension | CAMPAIGN_004 | CAMPAIGN_016 | CAMPAIGN_017 |
|---|---|---|---|
| compression | H4 ATR-14 ≤ P40 of 60 H4 bars | N/A (momentum rank) | weekly TR ≤ P25 of 12 weeks |
| trigger | Donchian 20 on same H4 bar | weekly rebalance top/bottom | close beyond compressed week H/L |
| cadence | every qualifying H4 bar | weekly cross-section | event-driven per compression cycle |
| stop | ATR multiple | 2.5 × ATR H4 | opposite compressed range boundary |
| selection | single-pair | portfolio rank | single-pair independent |
| expected trades | high H4 churn | 120–500 | **120–350** |

CAMPAIGN_004 tests quiet H4 bar → immediate Donchian break. CAMPAIGN_017
tests quiet **week** → confirmed expansion on next H4 boundary. Retuning
004 lookbacks would not satisfy structural distinctness — rejected.

CAMPAIGN_016 tests cross-sectional momentum rank/rebalance. CAMPAIGN_017
has no ranking, no rebalance, no USD exposure gate — independent per-pair
compression → breakout state machine.

---

## 3. Why this is not a retune

* Compression is measured in **weeks** (12), not H4 bars (60).
* Trigger uses **compressed week high/low**, not Donchian or momentum rank.
* Cadence is **once per compression cycle**, not every H4 bar or weekly rebalance.
* Stop is **thesis-native** (opposite range side), not ATR multiple from entry.
* No ADX, Donchian, z-score, session, event, failed-sweep, or rank logic.

Any deviation from §5 constitutes a **NEW candidate**; the runner rejects it.

---

## 4. Implementation files (committed by this sprint)

| file | role |
|---|---|
| `src/forex_bot/features/weekly_volatility.py` | synthetic weekly TR + compression |
| `tests/unit/test_weekly_volatility.py` | weekly feature unit tests |
| `src/forex_bot/strategies/weekly_volatility_contraction_breakout.py` | strategy module |
| `src/forex_bot/config.py` | `WeeklyVolatilityContractionBreakoutStrategyConfig` |
| `configs/campaign_017_weekly_volatility_contraction_breakout.yaml` | research config |
| `scripts/run_campaign_017.py` | walk-forward runner |
| `research/anti_overfit/campaign_017.py` | anti-overfit classifier |
| `scripts/run_campaign_017_anti_overfit_diagnostics.py` | null / anti-overfit runner |
| `research/backtrader_lane/strategies/campaign_017_weekly_volatility_contraction_breakout.py` | BT adapter stub |
| `docs/research/CAMPAIGN_017_WEEKLY_VOLATILITY_CONTRACTION_BREAKOUT_PRECOMMIT.md` | this document |

`configs/approved_strategies.yaml` is **not** modified.

---

## 5. Frozen parameters (binding, verbatim)

```yaml
strategy: weekly_volatility_contraction_breakout
version: 0.1.0-c017
timeframe: H4
source_timeframe: H4
aggregation: synthetic_weekly_from_h4
week_boundary: monday_00_00_utc
week_completion: last_completed_h4_before_next_monday_00_00_utc
compression_lookback_weeks: 12
compression_percentile_threshold: 25
compressed_range_source: most_recent_completed_compressed_week
breakout_buffer_atr_multiple: 0.25
atr_lookback_h4: 14
entry_timing: next_bar_open
long_trigger: close > compressed_week_high + 0.25 * ATR(14)
short_trigger: close < compressed_week_low - 0.25 * ATR(14)
stop_long: compressed_week_low - buffer
stop_short: compressed_week_high + buffer
max_hold_h4_bars: 42
max_positions_total: 2
max_positions_per_pair: 1
take_profit_r: null
trailing_stop_atr_multiple: null
pyramiding: none
re_entry_same_cycle: forbidden
spread_to_atr_max: 0.15
same_bar_adverse_stop_wins: true
risk.risk_per_trade_pct: 0.50
```

**Universe (7 majors):** `EUR_USD`, `GBP_USD`, `USD_JPY`, `AUD_USD`,
`USD_CAD`, `USD_CHF`, `NZD_USD`

**Weekly aggregation:** H4 deduped candles only. No native D1/W1/OANDA
daily candles. Monday 00:00 UTC week boundary. Incomplete current week
excluded from compression labeling and range selection.

**Compression:** current completed week true range ≤ 25th percentile of
trailing 12 weekly TR values (inclusive). Minimum 12 completed weeks before
first compression label.

**Breakout:** prior completed compressed week high/low + 0.25 × ATR(14) H4
buffer. One shot per compression cycle. Fill at next H4 open.

**Portfolio limits:** max 2 open positions total; max 1 per pair; priority
order when >2 signals same bar: universe list order, take first two.

**Cost stress:** base (1.0×) and 2× spread/slippage/commission mandatory.

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
| Warm-up margin | 120 calendar days (12-week lookback + H4 burn-in) |
| `strategy_evidence` | false |

Fold windows: `research/null_baselines/campaign_011_deduped_null_baseline.json` §fold_windows.

---

## 7. Pass / fail gates

### Null centre

* **Source:** `research/null_baselines/campaign_011_deduped_null_baseline.json`
* **Centre exp_r:** −0.0029154071495408797
* **Per-fold std:** 0.0479
* **Band:** ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair (informational)

### Aggregate gates (base cost)

| gate | threshold |
|---|---|
| aggregate expectancy R | ≥ **0.03** R (> null + 0.03 R) |
| aggregate trades | ≥ **120**, ≤ **350** |
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
| trade count | ≥ **12** |
| expectancy R | ≥ **0.0** |
| pairs positive | ≥ **2 / 7** |
| single-pair dominance | ≤ **60%** |

### Verdict rule

* **REJECT** if any primary gate fails OR 2× stress gates fail.
* **PASS_RESEARCH_SCREEN** only if all gates pass AND anti-overfit label
  is `ROBUST_ABOVE_NULL` or `ABOVE_NULL_BUT_FRAGILE` — still **not approved**.
* **BLOCKED** if local data missing or preflight fails.
* Default expected outcome: **REJECT**.

---

## 8. Anti-overfit gates

| gate | threshold |
|---|---|
| LOO min mean gap vs null | ≥ **0.05 R** |
| median per-fold exp_r | ≥ **0** |
| trade-level cumulative R | **> 0** |
| pair concentration (gross +R) | ≤ **70%** |
| fold concentration (return share) | ≤ **60%** |
| cost dominance | ≤ **50%** |

Classifier labels: `ROBUST_ABOVE_NULL`, `ABOVE_NULL_BUT_FRAGILE`,
`SELECTED_CELL_ARTIFACT`, `WITHIN_NULL`, `WORSE_THAN_NULL`, `BLOCKED`.

---

## 9. Backtrader plan

| step | action |
|---|---|
| Phase 0 | Weekly boundary + compression parity unit tests |
| Phase 1 | Adapter stub with frozen parameters |
| Phase 2 | Fold-window comparison deferred if bespoke REJECT |
| Classification | PASS / TOLERABLE_DRIFT / BLOCKED / non-decision-blocking |

**Non-decision-blocking** if bespoke lane already REJECT on primary gates.

Artifacts:

* `research/campaign_017/diagnostics/backtrader_comparison.json`
* `docs/research/BACKTRADER_CAMPAIGN_017_COMPARISON.md`

---

## 10. Blocked conditions

1. Precommit review classifies C017 as CAMPAIGN_004 retune.
2. Weekly boundary non-deterministic across bespoke / Backtrader.
3. Local SQLite missing or zero candles for any fold/pair.
4. Projected aggregate trades < **120** (insufficient sample).
5. Native D1/W1 data required.
6. Parameter grid beyond §5 frozen set proposed.
7. Contaminated pre-dedupe metrics used as positive evidence.

---

## 11. Explicit non-goals

* **No approval** — `configs/approved_strategies.yaml` stays `approved: []`
* **No paper / demo / live** enablement
* **No OANDA / broker API** calls in research sprint
* **No tuning** after seeing walk-forward results
* **No financing / carry** assumptions

---

## 12. Approval statement

**No strategy is approved.** This pre-commit does not modify
`configs/approved_strategies.yaml`. Paper, demo, and live trading remain
blocked regardless of walk-forward outcome.

Maximum possible verdict after implementation: **PASS_RESEARCH_SCREEN**
(candidate for human review). Default expected verdict: **REJECT**.
