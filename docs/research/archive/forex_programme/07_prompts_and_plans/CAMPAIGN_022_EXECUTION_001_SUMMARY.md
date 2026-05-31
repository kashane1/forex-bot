# CAMPAIGN_022 — Execution Sprint 001 Summary

**Date:** 2026-05-28
**Branch:** `research-campaign-022-h4-h1-pullback-resolution-execution-001`
**Verdict:** **REJECT** (train gate failed) · **Test lockbox:** NOT opened · **Approval:** none

## 1. Branch

`research-campaign-022-h4-h1-pullback-resolution-execution-001` (from frozen C022 scaffold).

## 2. Commit hashes by phase

| phase | commit | content |
|---|---|---|
| scaffold (base) | `ecbefad` (+ shared-strategy `71cbced`) | frozen C022 strategy/config/tests/docs + C021 fix |
| 0 — plan | `d5cd1a0` | execution plan, frozen splits, gates, no-retune/no-lookahead |
| 1 — runner | `67944a2` | runner + M15/H1/H4 loader; preflight 7/7 PASS |
| 1.5 — perf | `4975431` | results-identical speedups + resumable cells |
| 2 — train/val | `8561e6e` | train/validation evidence (REJECT) |
| 3 — diagnostics | `bf072c1` | behavior diagnostics |
| 4–6 — parity/gate/interp | `b67ff10` | parity moot, gate decision, final interpretation |
| 7–8 — archive/summary | (this commit) | manifest/index/status + this summary |

## 3. Files changed by phase

- 0: `docs/research/CAMPAIGN_022_EXECUTION_001_PLAN.md`
- 1: `scripts/run_campaign_022_h4_h1_pullback_resolution.py`, `src/forex_bot/research/campaign_022_loader.py`
- 1.5: `src/forex_bot/backtesting/engine.py` (opt-in `max_signal_window_bars`, default None), runner perf/resume
- 2: `research/campaign_022/*.json`, `backtests/CAMPAIGN_022_h4_h1_pullback_resolution/**` (equity curves gitignored)
- 3: `docs/research/CAMPAIGN_022_BEHAVIOR_DIAGNOSTICS.md`, `research/campaign_022/behavior_diagnostics.json`
- 4–6: `docs/research/CAMPAIGN_022_{BACKTRADER_PARITY_RESULT,GATE_DECISION,FINAL_INTERPRETATION}.md`
- 7–8: `docs/research/EVIDENCE_MANIFEST.json`, `EVIDENCE_INDEX.md`, `STRATEGY_STATUS.md`, this summary

## 4. Train metrics (base)

1369 trades · expectancy **−0.1042R** · PF 0.752 · 0/7 pairs positive.

## 5. Validation metrics (base)

1027 trades · expectancy **−0.1663R** · PF 0.690 · 1/7 pairs positive (USD_JPY +0.0004R ≈ flat).

## 6. Pair / fold summary

All 7 train pairs negative (−0.0017 to −0.3877). Validation: only USD_JPY non-negative (flat).
No walk-forward sub-folds were used; train/validation/test are fixed contiguous windows per the plan.

## 7. Cost-stress (2× spread + slippage, validation)

565 trades · expectancy **−0.2468R** · PF 0.495 · 0/7 positive. Fails.

## 8. Behavior diagnostics summary

Win rate 32.6%; avg win +1.24R / avg loss −0.79R (≈39% breakeven needed). Exit mix 60% hard-stop
(−0.86R) / 40% time (+0.96R); 42% of trades lose ≥0.9R; avg hold 0.31 calendar days (~19 of 32 bars).
The M15 reclaim after an H1 holding-pullback is whipsawed too often — continuation, where it occurs,
pays but survives in only 40% of trades.

## 9. Comparison vs C020 / C021

- **C020 (all-green H4):** train −0.035R, validation +0.053R. **C022 is worse on both.**
- **C021 (all-green M15):** scaffold only — no executed evidence; structural/behavioral comparison
  only, no fabricated numeric head-to-head.

## 10. Comparison vs C011 null

C011 deduped null −0.0029R; C022 validation −0.1663R → far below; `beat_null = false`.

## 11. Backtrader parity result

**NOT run — moot.** Train-gate REJECT closes the lockbox; parity is a pre-lockbox gate only.

## 12. Lockbox opened?

**No.**

## 13. Final verdict

**REJECT.** The H4/H1 pullback-resolution framework did not beat the prior all-green campaigns; it
underperformed C020 and lost to the C011 null. Hypothesis not supported.

## 14. Any retuning?

**No.** Frozen `0.1.0-c022` parameters used throughout (H4 ADX 20, M15 ADX 18, 2×ATR stop, 32-bar
time stop). No sweeps, no gate softening, no validation rescue.

## 15. Any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`.

## 16. Paper/demo/live blocked?

**Yes.** `trading_enabled: false`, `allow_order_submission: false`, `allow_live_trading: false`.
No broker/executor change; no OANDA mutation/order APIs; no live trading; no cloud execution.

## 17. Remaining blockers / honest notes

- **Shared strategy file:** the parallel CAMPAIGN_023 (ADX-22 sibling) sprint committed
  `h4_h1_pullback_resolution_entry.py` with `campaign_id` parameterized (default `CAMPAIGN_022`).
  C022's frozen behavior is preserved: version and the H4 ADX threshold are config-driven, C022's
  config carries ADX=20, and all 22 C022 unit tests pass. **No C023 ADX-22 threshold leaked into
  C022.** The C022 run constructed the strategy with the default `CAMPAIGN_022` label and C022's
  frozen config.
- **Backtrader parity** not executed (moot under REJECT); would be required only if lockbox-eligible.
- **Diagnostic gaps:** H4-ADX / H1-pullback-depth distributions and MFE/MAE are not recorded by the
  trade exporter; flagged honestly, not fabricated (not needed for the verdict).
- **Engine change:** `max_signal_window_bars` is opt-in and defaults to None — existing campaigns
  and their config hashes are unaffected; verified trade-for-trade identical for C022.

## 18. Files to review first

1. `docs/research/CAMPAIGN_022_EXECUTION_001_PLAN.md`
2. `docs/research/CAMPAIGN_022_TRAIN_VALIDATION_RESULT.md`
3. `docs/research/CAMPAIGN_022_GATE_DECISION.md`
4. `docs/research/CAMPAIGN_022_FINAL_INTERPRETATION.md`
5. `scripts/run_campaign_022_h4_h1_pullback_resolution.py`
6. `research/campaign_022/{train_metrics,validation_metrics,cost_stress_2x,gate_result}.json`
