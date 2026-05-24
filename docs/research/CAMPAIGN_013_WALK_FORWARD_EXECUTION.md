# CAMPAIGN_013 Walk-Forward Execution (Phase 4)

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-walk-forward-001`
`strategy_evidence: false`

Phase 4 per-fold execution record for **CAMPAIGN_013 /
`cross_pair_currency_strength_rotation 0.1.0-c013`**. 8 folds × 7
pairs = 56 local backtests executed against the validated H4
OANDA-practice store. **Result: REJECT on inherited gates** (verdict
classification per Phase 5).

> No strategy approved. No broker call. No credentials read. No data
> fetched. `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_011 is the **null baseline only**.

## 1. Command run

```bash
python scripts/run_campaign_013.py \
  --config configs/campaign_013_cross_pair_currency_strength_rotation.yaml \
  --plan backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/plan.json \
  --out backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation
```

Runtime: **~20.2 seconds** for 8 folds × 7 pairs = 56 backtests.
Much faster than CAMPAIGN_012's ~33 min because the cross-pair
strategy does only one log-return lookup per pair per bar (no
D1AGG aggregation).

## 2. Data source

| dimension | value |
|---|---|
| SQLite store | `data/campaign_002.sqlite3` (gitignored symlink) |
| data label | `oanda-practice` (runner-enforced) |
| span | 2020-01-01 → 2026-05-19 |
| H4 candles per pair | 9931–9935 |
| provenance | matches CAMPAIGN_010 / 011 / 012 verbatim |

## 3. Strategy version + frozen-parameter confirmation

All 9 frozen parameters re-asserted by the runner's `_assert_frozen()`
before any backtest fired. Mismatches: **0**.

| parameter | value |
|---|---|
| `version` | `0.1.0-c013` |
| `timeframe` | `H4` |
| `currency_strength_lookback_bars` | `24` |
| `rank_gap_threshold` | `4` |
| `atr_lookback` | `14` |
| `atr_stop_multiple` | `2.0` |
| `trailing_stop_atr_multiple` | `None` |
| `max_bars_in_trade` | `6` |
| `min_atr_pips` | `{}` |

**No parameter tuning at any point.**

## 4. Cross-pair runner integration contract status

**CONTRACT SATISFIED on all 8 folds.** No fold was BLOCKED.

| fold | common_index_length (bars) | notes |
|---|---:|---|
| 0 | 1,841 | clean alignment across all 7 pairs |
| 1 | 1,848 | clean |
| 2 | 1,837 | clean |
| 3 | 1,830 | clean |
| 4 | 1,835 | clean |
| 5 | 1,836 | clean |
| 6 | 1,825 | clean |
| 7 | 1,829 | clean (USD_CHF had 0 trades in this fold; downstream artifact of rank-gap not exceeding threshold for USD_CHF, not a contract failure) |

All 7 pairs aligned to a common index for each fold; no
missing/non-finite/insufficient pair endpoints. The cross-pair runner
contract did **NOT block** the verdict — the REJECT comes from
inherited gates alone.

## 5. No-parameter-optimization confirmation

- `parameter_mode = frozen` (asserted before execution).
- No per-fold parameter adaptation.
- No re-run with altered parameters.
- No grid search.
- No relaxing of `max_open_positions = 1` or any risk setting.
- Every fold used the same 9 frozen parameter values.

## 6. Implementation bug fixes during execution

**None.** Strategy module + runner unchanged from Phase 3 commits.

## 7. Fold execution table

| # | test window | trades | exp R | return % | profit factor | max DD % | win % | per-fold gates |
|---|---|---:|---:|---:|---:|---:|---:|:---:|
| 0 | 2021-12-21 → 2022-06-18 | 794 | −0.1017 | −19.33 | 0.000 | 0.00 | 19.0% | **REJECT** |
| 1 | 2022-06-19 → 2022-12-15 | 321 | −0.0027 | −0.28 | 0.000 | 0.00 | 6.9% | **REJECT** |
| 2 | 2022-12-16 → 2023-06-13 | 1,166 | −0.0452 | −13.29 | 0.000 | −3.99 | 26.6% | **REJECT** |
| 3 | 2023-06-14 → 2023-12-10 | 810 | −0.0874 | −17.03 | 0.000 | 0.00 | 18.7% | **REJECT** |
| 4 | 2023-12-11 → 2024-06-07 | 1,255 | −0.0452 | −14.93 | 0.000 | −3.73 | 25.3% | **REJECT** |
| 5 | 2024-06-08 → 2024-12-04 | 1,252 | −0.0498 | −16.31 | 0.000 | −5.74 | 25.8% | **REJECT** |
| 6 | 2024-12-05 → 2025-06-02 | 1,149 | −0.0253 | −6.86 | 0.126 | −3.51 | 26.4% | **REJECT** |
| 7 | 2025-06-03 → 2025-11-29 | 1,193 | −0.0794 | −25.32 | 0.000 | −5.76 | 25.3% | **REJECT** |

**Folds passing: 0 / 8** (pass rate 0 %). Note: 7 of 8 folds show
`PF = 0.000` — this means in those folds, the *sum of positive
pair-level returns* was 0 (i.e. all 7 pairs were negative in that
fold). The PF being literally zero is striking.

## 8. Per-fold-per-pair execution

The runner emitted `summary.json` + `trades.csv` for each of the 56
(fold × pair) cells. Only 1 pair-fold cell had 0 trades:

- Fold 7 USD_CHF: 0 trades (the rank gap for USD_CHF never exceeded
  the threshold in fold 7's test window).

All other 55 cells produced 200–1,400 trades each.

## 9. Aggregate (8-fold)

| metric | value |
|---|---|
| fold count | 8 |
| folds passing | **0** |
| **fold pass rate** | **0 / 8 = 0 %** |
| total trades across folds | **7,940** |
| aggregate expectancy R | **−0.0564** |
| aggregate return % (4-year window) | **−113.36 %** |
| profit factor | **0.000** |
| pairs_positive_count | **1 / 7** (only USD_JPY at +0.0000) |
| single_fold_dominance % | 22.34 % |
| single_pair_dominance % | 36.7 % (NZD_USD dominates losses) |

### 9.1 Aggregate gate vector

| gate | result |
|---|:---:|
| `fold_pass_rate_eq_100pct` | **FAIL** (0 % vs 100 %) |
| `fold_count_ge_6` | PASS (8) |
| `expectancy_r_ge_0p05` | **FAIL** (−0.0564 vs ≥ 0.05) |
| `profit_factor_ge_1p10` | **FAIL** (0.000 vs ≥ 1.10) |
| `trade_count_ge_200` | PASS (7,940) |
| `pairs_positive_ge_4_of_7` | **FAIL** (1 vs ≥ 4) |
| `single_fold_dominance_le_60pct` | PASS (22.3 %) |
| `single_pair_dominance_le_40pct` | PASS (36.7 %) |

**5 of 8 aggregate gates FAIL.** Verdict: **REJECT**.

### 9.2 Per-pair aggregate (all 8 folds combined)

| pair | trade count | aggregate return (%) | aggregate expectancy R |
|---|---:|---:|---:|
| EUR_USD | 1,412 | −16.93 | −0.0478 |
| GBP_USD | 648 | −9.79 | −0.0604 |
| USD_JPY | 310 | **+0.45** | **+0.0000** |
| AUD_USD | 1,942 | −20.26 | −0.0413 |
| USD_CAD | 958 | −10.40 | −0.0309 |
| USD_CHF | 807 | −14.67 | −0.0801 |
| NZD_USD | 1,863 | **−41.76** | **−0.0897** |

USD_JPY is again at the **random-walk floor +0.0000 R** (same
signature CAMPAIGN_011 and CAMPAIGN_012 surfaced). NZD_USD is the
worst pair (−41.76 % over 4 years). AUD_USD generated 1,942 trades —
more than any other pair — yet lost 20.26 %.

## 10. Comparison to CAMPAIGN_010 / 011 / 012 (diagnostic context)

| metric | CAMPAIGN_010 | CAMPAIGN_011 (null) | CAMPAIGN_012 (regime) | **CAMPAIGN_013 (cross-pair)** |
|---|---|---|---|---|
| total trades (8-fold) | 2,791 | 1,177 | 3,726 | **7,940** |
| aggregate expectancy R | −0.085 | −0.0024 | −0.0521 | **−0.0564** |
| aggregate return % | −1.02 % | −0.53 % | −43.52 % | **−113.36 %** |
| profit factor | — | 0.91 | 0.034 | **0.000** |
| pairs positive | — | 3 / 7 | 1 / 7 | **1 / 7** |
| fold pass rate | 0 / 8 | 0 / 8 | 0 / 8 | **0 / 8** |
| verdict | REJECT | REJECT (null) | REJECT | **REJECT** |

**CAMPAIGN_013 has by far the worst aggregate result of any campaign
to date:**

- **Most trades** (7,940 — ~2.1× CAMPAIGN_012 and ~6.7× CAMPAIGN_011).
- **Worst aggregate return** (−113.36 % vs CAMPAIGN_012's −43.52 %).
- **Worst profit factor** (0.000 — literally zero positive fold-pair contribution in 7 of 8 folds).

The cross-pair rotator fires *much* more often than CAMPAIGN_012 and
loses on essentially every fold-pair combination. The
`MAX_OPEN_POSITIONS_EXCEEDED` rejection mechanism did **not** rescue
trade count — the strategy still fired ~7,940 fills (vs CAMPAIGN_012's
3,726).

## 11. Committed artifacts

| path | what |
|---|---|
| `backtests/CAMPAIGN_013_*/folds/fold_NN/fold_NN_<PAIR>_summary.json` | per-fold per-pair summary (56 files; 1 with 0 trades — fold 7 USD_CHF) |
| `backtests/CAMPAIGN_013_*/folds/fold_NN/fold_NN_<PAIR>_trades.csv` | per-fold per-pair trade log (56 files) |
| `backtests/CAMPAIGN_013_*/walk_forward/results.json` | machine-readable aggregate |
| `backtests/CAMPAIGN_013_*/walk_forward/results.md` | human-readable summary |
| `backtests/CAMPAIGN_013_*/walk_forward/fold_detail.json` | full fold + pair + gate detail + cross-pair diagnostics |

## 12. Explicit no-approval statement

- `configs/approved_strategies.yaml` remains `approved: []`.
- `cross_pair_currency_strength_rotation` is **not** enabled in
  `configs/paper.yaml` / `configs/practice.yaml`.
- The current verdict (REJECT) is the published verdict.
- The cross-pair runner contract WAS satisfied; the REJECT is on
  inherited gates alone.

## 13. Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md)
- [`CAMPAIGN_013_WALK_FORWARD_PLAN.md`](CAMPAIGN_013_WALK_FORWARD_PLAN.md)
- [`CAMPAIGN_013_DATA_PROVENANCE.md`](CAMPAIGN_013_DATA_PROVENANCE.md)
- [`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md) (Phase 5; pending)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- `scripts/run_campaign_013.py`
