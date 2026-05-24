# CAMPAIGN_012 Walk-Forward Execution (Phase 4)

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-walk-forward-001`
`strategy_evidence: false`

Phase 4 per-fold execution record for **CAMPAIGN_012 /
`regime_switcher_atr_percentile 0.1.0-c012`**. 8 folds × 7 pairs = 56
local backtests executed against the validated H4 OANDA-practice store.
**Result: REJECT on inherited gates** (verdict classification per Phase 5).

> No strategy approved. No broker call. No credentials read. No data
> fetched. `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_011 is the **null baseline only**; this sprint compares
> CAMPAIGN_012's metrics to CAMPAIGN_011's verbatim floor and does
> **not** revive CAMPAIGN_011 as a tradable strategy.

## 1. Command run

```bash
python scripts/run_campaign_012.py \
  --config configs/campaign_012_regime_switcher_atr_percentile.yaml \
  --plan backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/plan.json \
  --out backtests/CAMPAIGN_012_regime_switcher_atr_percentile
```

Runtime: **~2,022 seconds (~33.7 min)** for 8 folds × 7 pairs = 56
backtests. The regime switcher is notably slower than CAMPAIGN_010
(7.9 s) and CAMPAIGN_011 (5.6 s) because the strategy reconstructs
H4 → D1AGG aggregates per bar (R3); this is a structural cost of the
regime feature, not a tuning artifact. The slowness does not affect
correctness or the verdict.

## 2. Data source

| dimension | value |
|---|---|
| SQLite store | `data/campaign_002.sqlite3` (gitignored symlink) |
| data label | `oanda-practice` (runner-enforced; aborts on mismatch) |
| span | 2020-01-01 → 2026-05-19 |
| H4 candles per pair | 9931–9935 |
| provenance | matches CAMPAIGN_010 / 011 verbatim; see [`CAMPAIGN_012_DATA_PROVENANCE.md`](CAMPAIGN_012_DATA_PROVENANCE.md) |

## 3. Strategy version + frozen-parameter confirmation

| field | value |
|---|---|
| strategy id | `regime_switcher_atr_percentile` |
| strategy version | `0.1.0-c012` |
| `version` | `0.1.0-c012` |
| `atr_lookback` | `14` |
| `atr_stop_multiple` | `2.0` |
| `trailing_stop_atr_multiple` | `None` |
| `max_bars_in_trade` | `6` |
| `min_atr_pips` | `{}` |
| `daily_atr_lookback` | `14` |
| `regime_lookback_days` | `60` |
| `regime_percentile_threshold` | `0.70` |
| `min_close_move_atr_fraction` | `0.25` |
| `trend_lookback_h4_bars` | `4` |

The runner's `_assert_frozen()` confirmed every parameter matched the
pre-commit table verbatim before any backtest fired. **No
parameter tuning occurred at any point.**

## 4. No-parameter-optimization confirmation

- The runner uses `parameter_mode = frozen` (asserted before execution).
- No seed sweep (the strategy has no PRNG; signal generation is fully
  deterministic from price).
- No per-fold parameter adaptation.
- No re-run with altered parameters to improve results.
- No grid search.
- Every fold used the same 12 frozen parameter values.

## 5. Implementation bug fixes during execution

**None.** The execution completed without any code change. No fix was
applied to `src/forex_bot/strategies/regime_switcher_atr_percentile.py`,
`src/forex_bot/backtesting/d1_aggregation.py`, or any other source
file during this phase. Strategy logic is exactly as committed in
Phase 2 of the scaffold sprint (commit `07bd9f3`).

## 6. Fold execution table

| # | test window | trades | exp R | return % | profit factor | max DD % | win % | per-fold gates |
|---|---|---:|---:|---:|---:|---:|---:|:---:|
| 0 | 2021-12-21 → 2022-06-18 | 678 | −0.0815 | −13.29 | 0.016 | −2.17 | 43.6% | **REJECT** |
| 1 | 2022-06-19 → 2022-12-15 | 811 | −0.0680 | −12.94 | 0.097 | −2.41 | 45.8% | **REJECT** |
| 2 | 2022-12-16 → 2023-06-13 | 320 | −0.0787 | −7.68 | 0.030 | −1.89 | 43.8% | **REJECT** |
| 3 | 2023-06-14 → 2023-12-10 | 254 | −0.0424 | −2.83 | 0.455 | −1.03 | 46.8% | **REJECT** |
| 4 | 2023-12-11 → 2024-06-07 | 358 | −0.0437 | −2.05 | 0.557 | −1.06 | 48.3% | **REJECT** |
| 5 | 2024-06-08 → 2024-12-04 | 407 | −0.0077 | +1.52 | 1.363 | −1.11 | 50.1% | **REJECT** |
| 6 | 2024-12-05 → 2025-06-02 | 638 | −0.0365 | −4.76 | 0.482 | −1.78 | 47.1% | **REJECT** |
| 7 | 2025-06-03 → 2025-11-29 | 260 | −0.0221 | −1.50 | 0.568 | −1.35 | 46.6% | **REJECT** |

**Folds passing: 0 / 8** (fold pass rate **0%**).

## 7. Per-fold-per-pair execution

The runner emitted `summary.json` + `trades.csv` for each of the 56
(fold × pair) cells under
`backtests/CAMPAIGN_012_regime_switcher_atr_percentile/folds/fold_NN/`.
Inline highlights from the run log:

- **Fold 0** (Dec 2021 → Jun 2022): USD_CHF −0.21 R / −5.88 %; AUD_USD −0.14 R / −3.88 %. The Russia-Ukraine + USD-strength cycle.
- **Fold 1** (Jun 2022 → Dec 2022): AUD_USD −0.17 R / −5.40 %; EUR_USD −0.12 R / −3.18 %. Fed hike cycle peaking.
- **Fold 2** (Dec 2022 → Jun 2023): USD_CAD −0.19 R / −2.97 %; AUD_USD −0.19 R / −2.08 %. Banking-crisis volatility.
- **Fold 3** (Jun 2023 → Dec 2023): USD_CHF −0.31 R / −1.33 %; **EUR_USD +0.25 R / +2.36 % (outlier positive)**.
- **Fold 4** (Dec 2023 → Jun 2024): USD_JPY +0.001 R / +1.70 %; EUR_USD +0.085 R / +0.84 %; AUD_USD −0.10 R / −1.28 %.
- **Fold 5** (Jun 2024 → Dec 2024): GBP_USD −0.11 R / −2.40 %; AUD_USD +0.14 R / +1.96 %; USD_JPY +0.001 R / +2.66 %. (Fold 5 has the best aggregate return: +1.52 %.)
- **Fold 6** (Dec 2024 → Jun 2025): USD_CAD −0.11 R / −4.27 %; GBP_USD −0.10 R / −3.20 %; USD_CHF +0.10 R / +1.80 %.
- **Fold 7** (Jun 2025 → Nov 2025): USD_CAD −0.10 R / −2.02 %; EUR_USD +0.14 R / +0.98 %.

**USD_JPY's expectancy is essentially zero across every fold**
(+0.000 / +0.001 / −0.000 / etc.). This is the same textbook
random-walk signature CAMPAIGN_011 surfaced — USD_JPY's tick-by-tick
gain/loss distribution averages so close to symmetric that any
zero-edge strategy on H4 produces exactly +0.0000 (to 4 dp) expectancy.
The regime gate's inability to move USD_JPY off this signature is
diagnostic of the gate failing to identify a real edge.

## 8. Aggregate (8-fold)

| metric | value |
|---|---|
| fold count | 8 |
| folds passing | **0** |
| **fold pass rate** | **0 / 8 = 0 %** |
| total trades across folds | **3,726** |
| aggregate expectancy R | **−0.0521** |
| aggregate return % (4-year window) | **−43.52 %** |
| profit factor | **0.034** |
| pairs_positive_count | **1 / 7** (only USD_JPY; expectancy +0.0004) |
| single_fold_dominance % | 28.54 % |
| single_pair_dominance % | 22.39 % |

### 8.1 Aggregate gate vector

| gate | result |
|---|:---:|
| `fold_pass_rate_eq_100pct` | **FAIL** (0 % vs 100 % required) |
| `fold_count_ge_6` | PASS (8) |
| `expectancy_r_ge_0p05` | **FAIL** (−0.0521 vs ≥ 0.05) |
| `profit_factor_ge_1p10` | **FAIL** (0.034 vs ≥ 1.10) |
| `trade_count_ge_200` | PASS (3,726) |
| `pairs_positive_ge_4_of_7` | **FAIL** (1 vs ≥ 4) |
| `single_fold_dominance_le_60pct` | PASS (28.5 %) |
| `single_pair_dominance_le_40pct` | PASS (22.4 %) |

**5 of 8 aggregate gates FAIL.** Verdict: **REJECT**.

### 8.2 Per-pair aggregate (all 8 folds combined)

| pair | trade count | aggregate return (%) | aggregate expectancy R |
|---|---:|---:|---:|
| EUR_USD | 479 | −1.07 | −0.0092 |
| GBP_USD | 555 | −8.12 | −0.0582 |
| USD_JPY | 624 | **+8.34** | +0.0004 |
| AUD_USD | 551 | −13.48 | −0.0986 |
| USD_CAD | 584 | −12.71 | −0.0621 |
| USD_CHF | 542 | −5.74 | −0.0459 |
| NZD_USD | 391 | −10.74 | −0.1080 |

The single positive pair (USD_JPY) is statistically indistinguishable
from zero (+0.0004 R, essentially random-walk noise). Every other pair
is solidly negative.

## 9. Comparison to CAMPAIGN_010 and CAMPAIGN_011 (diagnostic context only)

| metric | CAMPAIGN_002 (trend_following) | CAMPAIGN_010 (session_breakout) | CAMPAIGN_011 (random_entry_anchor null) | **CAMPAIGN_012 (regime_switcher)** |
|---|---|---|---|---|
| total trades | (per-fold, not 8-fold) | 2,791 | 1,177 | **3,726** |
| aggregate expectancy R | −0.085 | −0.085 | −0.0024 | **−0.0521** |
| aggregate return % | −1.02 % | −1.02 % | −0.53 % | **−43.52 %** |
| profit factor | 0.75 | — | 0.91 | **0.034** |
| pairs_positive | — | — | 3 / 7 | **1 / 7** |
| fold pass rate | (n/a) | 0 / 8 | 0 / 8 | **0 / 8** |
| verdict | REJECT | REJECT | REJECT (null anchor) | **REJECT** |

**CAMPAIGN_012 is markedly WORSE than CAMPAIGN_011** on every metric
that matters: lower expectancy, lower profit factor, fewer positive
pairs, vastly worse aggregate return. The regime gate did not rescue
trend-following on H4 majors — it amplified cost drag by allowing
more bars to qualify for trading (3,726 trades vs CAMPAIGN_011's
1,177) without improving signal quality enough to overcome those
costs.

This is a clean REJECT on its own gates; the null-baseline comparison
(applied in Phase 5) classifies it as **REJECT** (not
REJECT_INDISTINGUISHABLE_FROM_NULL) because CAMPAIGN_012's metrics
diverge from CAMPAIGN_011's *in the worse direction*, far outside the
±0.005 R / ±0.10 PF / ±2 pp / ±1 pair indistinguishability band.

## 10. Committed artifacts

| path | what |
|---|---|
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/folds/fold_NN/fold_NN_<PAIR>_summary.json` | per-fold per-pair summary (56 files) |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/folds/fold_NN/fold_NN_<PAIR>_trades.csv` | per-fold per-pair trade log (56 files) |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/results.json` | machine-readable aggregate |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/results.md` | human-readable summary |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/fold_detail.json` | full fold + pair + gate detail |

## 11. Explicit no-approval statement

This phase produced research evidence (per-fold metrics, aggregate
metrics, gate-vector status). It **does not approve** any strategy.

- `configs/approved_strategies.yaml` remains `approved: []` (verified).
- `regime_switcher_atr_percentile` is **not** enabled in
  `configs/paper.yaml` or `configs/practice.yaml`.
- Even if some future re-execution under different conditions gave a
  passing result, this Phase 4 record stands as published research
  evidence; the candidate would still require the verifier extension
  + a deliberate human approval action per
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).
- The current verdict (REJECT) is the published verdict.

## 12. Cross-links

- [`REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md)
- [`CAMPAIGN_012_WALK_FORWARD_PLAN.md`](CAMPAIGN_012_WALK_FORWARD_PLAN.md)
- [`CAMPAIGN_012_DATA_PROVENANCE.md`](CAMPAIGN_012_DATA_PROVENANCE.md)
- [`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md) (Phase 5 formal verdict — to be written)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- `scripts/run_campaign_012.py`
- `src/forex_bot/strategies/regime_switcher_atr_percentile.py`
