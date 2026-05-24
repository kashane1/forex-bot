# CAMPAIGN_012 Walk-Forward Plan (Phase 2)

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-walk-forward-001`
`strategy_evidence: false`

Authoritative Phase 2 walk-forward plan for **CAMPAIGN_012 /
`regime_switcher_atr_percentile 0.1.0-c012`**. Generated via the
existing `research.walk_forward` harness; **no strategy evidence
produced** by this phase.

> `strategy_evidence: false`. The harness produces fold plans, not
> strategy verdicts. **A clean plan does not approve a strategy.**
> No backtest fired. No broker call.

## 1. Plan structure (inherited verbatim from CAMPAIGN_010 / CAMPAIGN_011)

| field | value | notes |
|---|---|---|
| `--style` | `rolling` | rolling windows (not expanding) |
| `--parameter-mode` | `frozen` | strategy parameters do not adapt across folds |
| `--train-days` | `540` | ~18 months |
| `--validation-days` | `180` | ~6 months |
| `--test-days` | `180` | ~6 months |
| `--step-days` | `180` | fold start increments by 180 days |
| `--universe-start` | `2020-01-01` | inherited from CAMPAIGN_010 / 011 |
| `--universe-end` | `2026-05-20` | inherited from CAMPAIGN_010 / 011 |
| **fold count** | **8** | matches CAMPAIGN_010 / CAMPAIGN_011 verbatim |
| `strategy_evidence` (Pydantic-pinned) | `false` | the harness produces plans, not strategy verdicts |

## 2. Generation command

```bash
python scripts/run_walk_forward_dry_run.py \
  --campaign-name CAMPAIGN_012_regime_switcher_atr_percentile \
  --style rolling --parameter-mode frozen \
  --train-days 540 --validation-days 180 --test-days 180 --step-days 180 \
  --universe-start 2020-01-01 --universe-end 2026-05-20 \
  --output backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward
```

Output (committed):

- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/plan.json`
- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/plan.md`

## 3. Fold date ranges

| # | train | validation | test |
|---|---|---|---|
| 0 | 2020-01-01 → 2021-06-23 | 2021-06-24 → 2021-12-20 | 2021-12-21 → 2022-06-18 |
| 1 | 2020-06-29 → 2021-12-20 | 2021-12-21 → 2022-06-18 | 2022-06-19 → 2022-12-15 |
| 2 | 2020-12-26 → 2022-06-18 | 2022-06-19 → 2022-12-15 | 2022-12-16 → 2023-06-13 |
| 3 | 2021-06-24 → 2022-12-15 | 2022-12-16 → 2023-06-13 | 2023-06-14 → 2023-12-10 |
| 4 | 2021-12-21 → 2023-06-13 | 2023-06-14 → 2023-12-10 | 2023-12-11 → 2024-06-07 |
| 5 | 2022-06-19 → 2023-12-10 | 2023-12-11 → 2024-06-07 | 2024-06-08 → 2024-12-04 |
| 6 | 2022-12-16 → 2024-06-07 | 2024-06-08 → 2024-12-04 | 2024-12-05 → 2025-06-02 |
| 7 | 2023-06-14 → 2024-12-04 | 2024-12-05 → 2025-06-02 | 2025-06-03 → 2025-11-29 |

**These fold boundaries are identical to CAMPAIGN_010's and
CAMPAIGN_011's plans.** Verified by running `run_walk_forward_dry_run.py`
with the same arguments.

## 4. Plan validation

The harness's `validate_plan()` (in `research.walk_forward.validate`)
verifies:

- ✓ minimum fold count requirement met (8 ≥ 6)
- ✓ test windows do not overlap
- ✓ fold boundaries are inside the universe (`2020-01-01 → 2026-05-20`)
- ✓ rolling-mode no-leakage (each fold's train < validation < test)
- ✓ parameter_mode = `frozen`
- ✓ `strategy_evidence = False` (Pydantic-pinned)

(The dry-run script exits successfully only if `validate_plan()` passes;
the Phase 2 invocation exited 0.)

## 5. Frozen-parameter statement

The runner (Phase 3) will hand the strategy these parameters verbatim
from `configs/campaign_012_regime_switcher_atr_percentile.yaml`,
asserting them before any backtest fires:

| parameter | value |
|---|---|
| `version` | `0.1.0-c012` |
| `atr_lookback` | `14` |
| `atr_stop_multiple` | `2.0` |
| `trailing_stop_atr_multiple` | `null` |
| `max_bars_in_trade` | `6` |
| `min_atr_pips` | `{}` |
| `daily_atr_lookback` | `14` |
| `regime_lookback_days` | `60` |
| `regime_percentile_threshold` | `0.70` |
| `min_close_move_atr_fraction` | `0.25` |
| `trend_lookback_h4_bars` | `4` |

**Any deviation from any value above aborts the runner before any
backtest fires.** Pre-commit binding from
[`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md)
§2.

## 6. No parameter optimization statement

- The plan uses `parameter_mode = frozen`.
- The strategy has no per-fold tuning.
- The runner enforces frozen parameters by comparing the loaded YAML
  against the pre-commit table in
  [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)
  §4 and aborting on any mismatch.
- No grid search. No parameter sweep. No seed sweep (the regime
  switcher has no PRNG; the strategy is fully deterministic from price).

## 7. Null-baseline comparison requirement (binding for Phase 5)

The Phase 5 verdict doc **must** include a "Null-baseline comparison"
section per
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
§3 + [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)
§8 with explicit margins:

| metric | CAMPAIGN_011 floor | CAMPAIGN_012 must beat |
|---|---|---|
| aggregate expectancy R | −0.0024 | by ≥ **+0.0524 R** (→ ≥ 0.05 R) |
| aggregate profit factor | 0.91 | by ≥ **+0.19** (→ ≥ 1.10) |
| aggregate return (4 y) | −0.53 % | meaningfully positive (≥ **+5 %**) |
| `pairs_positive` | 3 / 7 | ≥ **4 / 7** |
| `fold_pass_rate` | 0 / 8 | **100 %** |

"Indistinguishable from null" REJECT band: if CAMPAIGN_012's aggregate
metrics cluster within **±0.005 R / ±0.10 PF / ±2 pp / ±1 pair** of
CAMPAIGN_011's, the verdict must be classified
**REJECT_INDISTINGUISHABLE_FROM_NULL**, regardless of which inherited
gates technically pass.

## 8. Data source

| dimension | value |
|---|---|
| SQLite store | `data/campaign_002.sqlite3` (gitignored symlink) |
| data label | `oanda-practice` (runner-enforced) |
| H4 candles per pair | 9931–9935 (per pair) |
| span | 2020-01-01 22:00:00 UTC → 2026-05-19 21:00:00 UTC |
| provenance | see [`CAMPAIGN_012_DATA_PROVENANCE.md`](CAMPAIGN_012_DATA_PROVENANCE.md) (matches CAMPAIGN_010 / 011 verbatim) |
| committed bulky data | **none** |

## 9. Limitations

- **DST handling.** The H4 store covers the real DST transitions
  exactly as OANDA records them. The D1AGG aggregator
  (`src/forex_bot/backtesting/d1_aggregation.py`) classifies days as
  `aggregated` only when all 6 H4 slots match the expected NY hours;
  days with mis-aligned slots (DST transitions) are classified
  `ambiguous` and dropped. The strategy fail-closes if D1AGG history
  is insufficient (R3); this may reduce effective D1AGG candle count
  in DST-adjacent windows. This is structural, not a tuning artifact.
- **Last test window's right edge.** Fold 7's test ends 2025-11-29
  but the data store extends to 2026-05-19. The next fold (fold 8)
  would need a test window starting 2026-06-04, which is outside the
  data span; the harness correctly stops at 8 folds.
- **Fold 0's left edge.** Fold 0's train starts on 2020-01-01, which
  is the first day of the data store; the strategy's warm-up
  (500 H4 bars ≈ 83 trading days) is computed inside each fold's
  train window, so fold 0's effective signal start is around early
  May 2020. This is normal and matches CAMPAIGN_010 / 011 behavior.

## 10. Why this plan does not approve anything

- This is a **plan** — a fold-boundary specification. No strategy
  has been run. No metrics exist. No gate has been evaluated. No
  verdict has been classified.
- The strategy parameters are pre-committed (Phase 1 of the scaffold
  sprint); the plan does not tune them.
- Approval requires the full six-evidence ladder + a deliberate human
  approval action per
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md);
  this plan is item 1 (and only the *plan* portion of item 1) of the
  ladder.

## 11. Committed artifacts

| path | committed? |
|---|:---:|
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/plan.json` | ✓ |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/plan.md` | ✓ |
| `docs/research/CAMPAIGN_012_WALK_FORWARD_PLAN.md` (this doc) | ✓ |

## 12. Cross-links

- [`REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md)
- [`CAMPAIGN_012_DATA_PROVENANCE.md`](CAMPAIGN_012_DATA_PROVENANCE.md)
- [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`CAMPAIGN_010_WALK_FORWARD_PLAN.md`](CAMPAIGN_010_WALK_FORWARD_PLAN.md) (sibling)
- [`CAMPAIGN_011_WALK_FORWARD_PLAN.md`](CAMPAIGN_011_WALK_FORWARD_PLAN.md) (sibling)
