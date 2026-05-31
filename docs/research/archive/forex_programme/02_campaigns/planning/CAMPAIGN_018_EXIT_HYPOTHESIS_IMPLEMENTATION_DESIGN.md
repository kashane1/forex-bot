# CAMPAIGN_018 — Exit Hypothesis Implementation Design

**Date:** 2026-05-27  
**Branch:** `research-exit-hypothesis-precommit-001`  
**Status:** **DESIGN ONLY — NO CODE IN THIS SPRINT**

> **Precommit only** — `strategy_evidence: false`. Describes future execution work; **nothing implemented here.**

---

## Overview

Future execution sprint implements **one exit behavior change** in the backtest engine/strategy layer while keeping C008 entries frozen. No executor/broker changes. No live order submission.

---

## Required strategy / config changes (future sprint)

### New strategy module variant

| item | action |
|---|---|
| Strategy class | extend or fork `MeanReversionStrategy` with protective-stop state machine |
| Version string | `0.1.0-c018` |
| Config file | `configs/campaign_018_mean_reversion_protective_stop.yaml` (new) |
| Parameters | copy C008 frozen params + add protective-stop block |

### New config parameters (frozen in precommit)

```yaml
mean_reversion_protective_stop:
  version: 0.1.0-c018
  # ... all C008 entry params unchanged ...
  atr_stop_multiple: 1.5
  max_bars_in_trade: 40
  midline_exit: false
  protective_stop:
    enabled: true
    favorable_excursion_r_threshold: 1.0
    stop_after_transition: entry_price  # break-even
    ratchet: false
```

No other keys. Threshold **1.0** is fixed — not configurable per run.

---

## Expected files to add/modify (future sprint)

| path | action |
|---|---|
| `src/forex_bot/strategies/mean_reversion.py` (or sibling) | add protective-stop logic OR new `mean_reversion_protective_stop.py` |
| `configs/campaign_018_mean_reversion_protective_stop.yaml` | new campaign config |
| `scripts/run_campaign_018_protective_stop.py` (or reuse marathon runner) | execution entrypoint |
| `tests/unit/test_mean_reversion_protective_stop.py` | unit tests |
| `tests/fixtures/protective_stop_*.csv` | small candle fixtures |
| `docs/research/CAMPAIGN_018_PRECOMMIT_CHECKLIST.md` | execution checklist (copy gates) |
| `backtests/CAMPAIGN_018_mean_reversion_protective_stop/` | output root (gitignored trades) |
| `research/campaign_018/` | compact JSON summaries (committed) |

**Do not modify:**

- `configs/approved_strategies.yaml`
- C008/C009 configs or historical backtest folders
- Executor/broker order paths

---

## Keeping entry rules frozen

1. **Shared entry function** — extract C008 signal generation into a shared helper; C018 calls same helper without overrides.
2. **Config validation test** — assert C018 entry block byte-identical to C008 entry block (excluding strategy name/version and protective_stop section).
3. **No new entry filters** — ADX, z-score, RSI thresholds locked.
4. **Pair universe enforced** — config validator rejects NZD_USD or pair list changes.

---

## Adding exit behavior without executor/broker changes

Protective stop is a **backtest position-management rule** inside the strategy or sim layer:

1. On entry: set `initial_stop`, `active_stop = initial_stop`, `protective_triggered = false`.
2. Each bar: update MFE; if not triggered and MFE ≥ 1R, set `active_stop = entry_price`, `protective_triggered = true`, emit `stop_transition` event.
3. Exit checks: hit `active_stop`, time stop, or EOD — same priority as C008 stop handling.
4. Record exit_reason: `stop` (initial or BE), `time`, `eod`; add field `stop_was_protective: bool`.

No OANDA amend-stop API calls. Paper/demo/live remain disabled.

---

## Exit reason and stop-transition recording

### Trade record fields (required)

| field | description |
|---|---|
| `exit_reason` | stop \| time \| eod |
| `stop_was_protective` | true if active stop was break-even at exit |
| `protective_triggered` | true if transition ever fired |
| `bar_protective_triggered` | bar index when transition fired (nullable) |
| `mfe_r_at_exit` | MFE in R at exit bar |
| `mae_r_at_exit` | MAE in R at exit bar |
| `initial_stop_distance_pips` | unchanged from C008 |
| `bars_held` | unchanged |

### Event log (optional JSONL)

`stop_transition` events for debugging parity.

---

## MAE/MFE computation (post-run)

Reuse pattern from `scripts/rerun_c008_c009_deduped_forensic.py`:

1. Load deduped H4 candles for trade instrument/window.
2. Walk bars from entry+1 to exit.
3. R-normalize by entry-to-initial-stop distance.
4. Output `research/campaign_018/mae_mfe_summary.json`.

Compare stop ≥1R-before-stop rate vs C008 deduped (descriptive).

---

## No-lookahead preservation

- Protective trigger evaluated on **completed bar** extremes only.
- Stop transition effective **next bar open** (or same bar close per existing engine convention — must match C008 stop fill semantics).
- Unit tests must assert trigger cannot use future bars.
- FRED features: if joined for diagnostics, **shifted** per H4 alignment audit — not used for exit decisions in v0.1.0-c018.

---

## Cost atlas and FRED as diagnostics

| tool | usage |
|---|---|
| Cost atlas | post-run join on entry timestamp — spread/ATR decile tags |
| FRED features | post-run regime tags on entry date |
| Confluence | post-run grade tag |

None may filter trades in v0.1.0-c018 unless precommit amended.

---

## Fixture / unit-test plan

| test | asserts |
|---|---|
| `test_protective_triggers_at_1r_mfe` | synthetic bars: MFE hits 1R → stop moves to entry |
| `test_no_trigger_below_1r` | stops out at initial hard stop |
| `test_time_exit_after_protective` | after BE transition, time stop still exits at 40 bars |
| `test_no_midline_target` | target exit never emitted |
| `test_entry_params_match_c008` | config diff guard |
| `test_no_lookahead_trigger` | trigger bar ≤ current bar |
| `test_c018_config_frozen_threshold` | threshold locked at 1.0 |

Fixtures: 20–40 synthetic H4 bars per scenario — no full SQLite in git.

---

## Artifact paths (future execution sprint)

| artifact | path |
|---|---|
| Run manifest | `research/campaign_018/run_manifest.json` |
| Metrics summary | `research/campaign_018/metrics_summary.json` |
| Gate result | `research/campaign_018/gate_result.json` |
| Evidence status | `research/campaign_018/evidence_status.json` |
| Baseline comparison | `research/campaign_018/vs_c008_c009_null_comparison.json` |
| Exit anatomy | `research/campaign_018/exit_anatomy.json` |
| MAE/MFE | `research/campaign_018/mae_mfe.json` |
| Human report | `docs/research/CAMPAIGN_018_PROTECTIVE_STOP_RESULT.md` |
| Trade CSVs | `backtests/CAMPAIGN_018_mean_reversion_protective_stop/` (gitignored) |

All JSON artifacts: `strategy_evidence: false`, `precommit_id: CAMPAIGN_018`.

---

## Deduped input requirement

Execution script must:

1. Call dedupe preflight (`list_with_dedupe_stats` or equivalent).
2. Fail fast if duplicate rows detected without dedupe applied.
3. Record `dedupe_rows_dropped` in manifest.

---

## Financing overlay (execution sprint)

Before lockbox decision:

1. Run conservative financing overlay on all trades with hold ≥ 24h.
2. Record `validation_exp_r_financing_adjusted` in gate result.
3. If adjusted validation < 0 → note **financing blocker** in report.

---

## Out of scope for implementation sprint

- Backtrader parity (separate infra sprint if engine-specific assumptions dominate)
- Parameter sweeps
- Registry / approval updates
