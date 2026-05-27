# CAMPAIGN_019 — Exit Hypothesis Implementation Design

**Date:** 2026-05-27  
**Branch:** `research-exit-hypothesis-precommit-002`  
**Status:** **DESIGN ONLY — NO CODE IN THIS SPRINT**

> **Precommit only** — `strategy_evidence: false`. Describes future execution work.

---

## Overview

Future execution sprint implements **one exit behavior change** — z-score continuation
thesis invalidation — while keeping C008 entries frozen. No executor/broker changes.

---

## Required strategy / config changes (future sprint)

### New strategy module variant

| item | action |
|---|---|
| Strategy class | new `MeanReversionThesisInvalidationStrategy` (or sibling module) |
| Version string | `0.1.0-c019` |
| Config file | `configs/campaign_019_mean_reversion_thesis_invalidation.yaml` (new) |
| Parameters | copy C008 frozen params + thesis_invalidation block |

### New config parameters (frozen in precommit)

```yaml
mean_reversion_thesis_invalidation:
  version: 0.1.0-c019
  # ... all C008 entry params unchanged ...
  atr_stop_multiple: 1.5
  max_bars_in_trade: 40
  midline_exit: false
  thesis_invalidation:
    enabled: true
    zscore_lookback: 20          # must match entry
    long_exit_zscore: -3.0       # fixed — not configurable per run
    short_exit_zscore: 3.0       # fixed — not configurable per run
```

No protective_stop block. No target. Thresholds **±3.0** fixed in precommit — config
validator rejects overrides.

---

## Expected files to add/modify (future sprint)

| path | action |
|---|---|
| `src/forex_bot/strategies/mean_reversion_thesis_invalidation.py` | new strategy + exit state |
| `configs/campaign_019_mean_reversion_thesis_invalidation.yaml` | new campaign config |
| `scripts/run_campaign_019_thesis_invalidation.py` | execution entrypoint |
| `tests/unit/test_mean_reversion_thesis_invalidation.py` | unit tests |
| `tests/fixtures/thesis_invalidation_*.csv` | small candle fixtures |
| `backtests/CAMPAIGN_019_mean_reversion_thesis_invalidation/` | output root (gitignored) |
| `research/campaign_019/` | compact JSON summaries (committed) |
| `research/backtrader_exit_parity/` | parity replay artifacts if extended |

**Do not modify:**

- `configs/approved_strategies.yaml`
- C008/C009/C018 configs or historical artifacts
- Executor/broker order paths

---

## Keeping entry rules frozen

1. **Shared entry helper** — same signal generation as C008; C019 adds exit layer only.
2. **Config guard test** — C019 entry block byte-identical to C008 (excluding strategy name, version, thesis_invalidation section).
3. **No new entry filters.**
4. **Pair universe validator** — rejects changes from six-pair list.

---

## Exit behavior (backtest engine)

1. On entry: set `initial_stop`, track open trade.
2. Each bar close while open:
   a. Compute z-score (20-bar).
   b. If long and z ≤ −3.0 → exit `thesis_invalidation` at bar close.
   c. If short and z ≥ +3.0 → exit `thesis_invalidation` at bar close.
   d. Else evaluate hard stop, then time stop, then EOD.
3. Record `exit_reason` including new bucket `thesis_invalidation`.

No OANDA API calls. Paper/demo/live disabled.

---

## Trade record fields (required)

| field | description |
|---|---|
| `exit_reason` | thesis_invalidation \| stop \| time \| eod |
| `zscore_at_exit` | z-score value triggering invalidation (nullable) |
| `bars_held` | integer |
| `mfe_r` / `mae_r` | excursion stats |

Mechanism diagnostics JSON: thesis_invalidation rate, share vs stop/time, median R at invalidation exit.

---

## Backtrader parity lane extension

Extend `research/backtrader_exit_parity/strategy.py` with C019 variant:

- Same `pnl_home_currency` and `engine_aligned` windows
- `process_bar_exit` or parallel path for thesis_invalidation check
- Runner accepts `--campaign C019` when implemented

Parity run mandatory post-execution; ±1 trade tolerance.

---

## Gate evaluation script

Reuse C018 gate evaluation pattern:

- Load `research/campaign_019/gate_result.json`
- Compare vs C008/C009/C018/C011 JSON baselines
- Emit `CAMPAIGN_019_TRAIN_VALIDATION_RESULT.md`, `CAMPAIGN_019_FINAL_INTERPRETATION.md`

---

## Financing overlay

Run `scripts/generate_c008_c009_c018_financing_exposure.py` pattern extended for C019 trades
(or inline overlay in runner). Report gross vs net exp_r. Do not change verdict logic from
overlay alone — overlay blocks REVISE recommendation only.

---

## Explicit non-goals (execution sprint)

- Approve strategy
- Tune ±3.0 threshold or any parameter from validation
- Open test without screening pass
- Enable paper/demo/live
