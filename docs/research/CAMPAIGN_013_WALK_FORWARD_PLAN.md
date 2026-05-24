# CAMPAIGN_013 Walk-Forward Plan (Phase 2)

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-walk-forward-001`
`strategy_evidence: false`

Authoritative Phase 2 walk-forward plan for **CAMPAIGN_013 /
`cross_pair_currency_strength_rotation 0.1.0-c013`**. Generated via
the existing `research.walk_forward` harness. **No strategy
evidence produced** by this phase.

> `strategy_evidence: false`. A clean plan does not approve a
> strategy. No backtest fired. No broker call.

## 1. Plan structure (inherited verbatim from CAMPAIGN_010 / 011 / 012)

| field | value |
|---|---|
| `--style` | `rolling` |
| `--parameter-mode` | `frozen` |
| `--train-days` | `540` |
| `--validation-days` | `180` |
| `--test-days` | `180` |
| `--step-days` | `180` |
| `--universe-start` | `2020-01-01` |
| `--universe-end` | `2026-05-20` |
| **fold count** | **8** |
| `strategy_evidence` (Pydantic-pinned) | `false` |

## 2. Generation command

```bash
python scripts/run_walk_forward_dry_run.py \
  --campaign-name CAMPAIGN_013_cross_pair_currency_strength_rotation \
  --style rolling --parameter-mode frozen \
  --train-days 540 --validation-days 180 --test-days 180 --step-days 180 \
  --universe-start 2020-01-01 --universe-end 2026-05-20 \
  --output backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward
```

Output (committed):

- `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/plan.json`
- `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/plan.md`

## 3. Fold date ranges (identical to CAMPAIGN_010 / 011 / 012)

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

## 4. Plan validation

The harness's `validate_plan()` verifies:

- ✓ minimum fold count requirement met (8 ≥ 6)
- ✓ test windows do not overlap
- ✓ fold boundaries are inside the universe
- ✓ rolling-mode no-leakage
- ✓ parameter_mode = `frozen`
- ✓ `strategy_evidence = False`

(The dry-run script exits successfully only if `validate_plan()` passes.)

## 5. Frozen-parameter statement

The runner (Phase 3) will hand the strategy these 9 parameters
verbatim from `configs/campaign_013_cross_pair_currency_strength_rotation.yaml`,
asserting them before any backtest fires.

## 6. No parameter optimization

- `parameter_mode = frozen`.
- No per-fold tuning.
- The runner enforces frozen parameters by comparing the loaded
  YAML against the pre-commit table in
  [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md)
  §4 and aborting on any mismatch.

## 7. Cross-pair runner contract requirement (binding for Phase 3)

The CAMPAIGN_013 runner is **structurally different** from
CAMPAIGN_010 / 011 / 012 runners. It MUST:

1. Load all 7 pairs' completed H4 candles for the test window +
   warm-up margin.
2. Align all 7 pairs' completed H4 close series to a common
   timestamp index (intersection of completed bars).
3. Build per-pair closes-only `pd.Series` indexed by the common index.
4. Inject `cross_pair_closes` into each pair's `strategy_config`
   dict.
5. Fail closed (classify verdict as `BLOCKED`) if any required pair
   is missing, misaligned, non-finite, or insufficient.

## 8. Null-baseline comparison requirement (binding for Phase 5)

Per
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
§3, the Phase 5 verdict doc must include a "Null-baseline comparison"
section with explicit margins; CAMPAIGN_013 must beat CAMPAIGN_011
by ≥ +0.0524 R / ≥ +0.19 PF / ≥ +5 % return / ≥ +1 pair / 100 %
fold pass rate to qualify even as `RESEARCH_PASS_UNAPPROVED`.

## 9. Data source

| dimension | value |
|---|---|
| SQLite store | `data/campaign_002.sqlite3` (gitignored symlink) |
| data label | `oanda-practice` (runner-enforced) |
| span | 2020-01-01 → 2026-05-19 |
| provenance | matches CAMPAIGN_010 / 011 / 012 verbatim; see [`CAMPAIGN_013_DATA_PROVENANCE.md`](CAMPAIGN_013_DATA_PROVENANCE.md) |

## 10. Limitations

- **Cross-pair index alignment.** Pairs with missing bars at a
  timestamp are absent from the common index for that timestamp.
  Effective fold trade count may be reduced vs CAMPAIGN_010 / 011 /
  012 by alignment drops.
- **`MAX_OPEN_POSITIONS_EXCEEDED` rejection.** Cross-pair rotation
  generates multiple simultaneous signals; `max_open_positions = 1`
  rejects most. Known behavior; not a tuning artifact.

## 11. Why this plan does not approve anything

- This is a **plan** — a fold-boundary specification. No strategy
  has been run.
- Approval requires the full six-evidence ladder + a deliberate
  human approval action per
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

## 12. Committed artifacts

| path | committed? |
|---|:---:|
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/plan.json` | ✓ |
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/plan.md` | ✓ |
| `docs/research/CAMPAIGN_013_WALK_FORWARD_PLAN.md` (this doc) | ✓ |

## 13. Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md)
- [`CAMPAIGN_013_DATA_PROVENANCE.md`](CAMPAIGN_013_DATA_PROVENANCE.md)
- [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`CAMPAIGN_012_WALK_FORWARD_PLAN.md`](CAMPAIGN_012_WALK_FORWARD_PLAN.md) (sibling)
