# CAMPAIGN_022 — H4/H1 Pullback Resolution Scaffold Sprint Summary

**Date:** 2026-05-27
**Branch:** `claude/loving-hawking-7ab830`
**Verdict:** **SCAFFOLD_ONLY** — precommitted, not executed

## 1. Precommitted strategy identity

`h4_h1_pullback_resolution_entry` · `0.1.0-c022` · CAMPAIGN_022

## 2. Hypothesis

H4 sets directional bias; H1 must be in a **counter-trend pullback that holds**; M15 fires
when that pullback **resolves back** into the H4 direction. H1 is **not** required to agree
with H4 — the structural departure from C020/C021's "all-green" alignment.

## 3. Universe / timeframe

Seven majors; execution **M15**; context **H4 (top) + H1**. **No D1 / D1AGG layer.**

## 4. Files added / changed

| area | file |
|---|---|
| precommit | `docs/research/CAMPAIGN_022_H4_H1_PULLBACK_RESOLUTION_PRECOMMIT.md` |
| distinctness | `docs/research/CAMPAIGN_022_STRUCTURAL_DISTINCTNESS_MEMO.md` |
| strategy | `src/forex_bot/strategies/h4_h1_pullback_resolution_entry.py` |
| config model + slot | `src/forex_bot/config.py` (`H4H1PullbackResolutionEntryStrategyConfig`) |
| export | `src/forex_bot/strategies/__init__.py` |
| frozen config | `configs/campaign_022_h4_h1_pullback_resolution.yaml` |
| tests | `tests/unit/test_h4_h1_pullback_resolution_entry.py` (22 tests) |
| summary | this file |

### Paired bug fix (CAMPAIGN_021)

`src/forex_bot/strategies/lower_timeframe_mtf_confluence_entry.py` —
`_aligned_h1_trend` EMA slope now anchored at the `align_last_completed` bar
(`htf_times <= aligned_time`) instead of the frame tail, closing a lookahead leak.
Regression: `tests/unit/test_lower_timeframe_mtf_confluence_entry.py::test_h1_slope_ignores_future_bars`.

## 5. H4 bias rules (frozen)

3 votes — `close>EMA50`, `EMA20>EMA50`, `EMA50 slope(3) > 0`; **bias if ≥2/3 AND ADX(14) ≥ 20**;
else range/no-trade. ADX is a strength gate, never a directional vote.

## 6. H1 pullback-holds rules (frozen)

Within last 6 completed H1 bars: `low` touched EMA20 **OR** RSI(14) reset (<45 long / >55
short) — AND latest H1 `close` still on the trend side of EMA50 ("holds").

## 7. M15 trigger (frozen)

8-bar pullback touch to EMA20/50; reclaim = `close` crosses EMA20 in trend direction;
M15 ADX(14) ≥ 18 execution floor; optional `min_atr_pips`. (Reuses the C021
`m15_pullback_and_reclaim` primitive.)

## 8. Risk / exit (frozen)

2.0× M15 ATR(14) hard stop; 32 M15-bar time stop (~8h); no TP; no trailing
(`hard_stop_or_time`).

## 9. Data provenance

Three `m1_derived` layers (M15/H1/H4). **No daily layer** — `validate_c022_data_provenance`
rejects any `d1agg_*` / `d1_*` key. No `aggregate_h4_to_d1` dependency.

## 10. No-lookahead discipline

All H4/H1 values read at the `align_last_completed` bar; EMA slope and pullback windows
bounded to `time <= aligned_feature_time`. `htf_feature_times` (h4, h1) recorded on every
signal; `validate_signal_provenance` returns `[]`. Covered by
`test_h4_bias_ignores_future_bars`.

## 11. Fill timing / execution realism

`research_metadata`: `fill_timing: next_bar_open`, `execution_realism: conservative`,
`evidence_use: approval_bound`, `promotion_eligible: false`.

## 12. Tests

`tests/unit/test_h4_h1_pullback_resolution_entry.py` — 22 tests (provenance, H4 score+ADX
gate, H4 no-lookahead, H1 pullback-holds positive/negative, M15 plumbing, neutral/non-hold
blocks, wrong-granularity, frozen config, RSI-threshold validation, no daily provenance,
approved-empty, slot present, no broker imports). **PASS.**

Combined C022 + C021 + C020 strategy suites: **55 passed.**

## 13. Full evidence run?

**No** — SCAFFOLD_ONLY. No train/validation/test. Test lockbox not opened.

## 14. CAMPAIGN_022 approved?

**No.** `approved_strategies.yaml` remains `approved: []`. Paper/demo/live blocked.

## 15. Executor / broker / OANDA mutation / live env?

**None.** No broker, execution, loops, or oanda imports in the strategy
(`test_strategy_no_broker_imports`).

## 16. Remaining WARN / BLOCKED / deferred

| item | status |
|---|---|
| Preflight runner (`scripts/run_campaign_022_*.py`) | DEFERRED to execution sprint |
| Backtrader parity design | DEFERRED to execution sprint |
| Train/validation/test evidence | BLOCKED until execution sprint |
| `entry_parity/test_compare_entries.py::test_c008_*` | PRE-EXISTING worktree-data failure (untracked `research/` parity artifacts absent in worktree; passes on main checkout) — not introduced by this sprint |

## 17. Prior verdicts unchanged

CAMPAIGN_020 remains **REJECT**. CAMPAIGN_021 verdict unchanged (scaffold; bug fix only).

## Review first

1. `docs/research/CAMPAIGN_022_H4_H1_PULLBACK_RESOLUTION_PRECOMMIT.md`
2. `docs/research/CAMPAIGN_022_STRUCTURAL_DISTINCTNESS_MEMO.md`
3. `src/forex_bot/strategies/h4_h1_pullback_resolution_entry.py`
4. `configs/campaign_022_h4_h1_pullback_resolution.yaml`
5. `tests/unit/test_h4_h1_pullback_resolution_entry.py`
