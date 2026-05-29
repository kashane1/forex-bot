# CAMPAIGN_029 — USD_JPY 10-pip range-bar MTF breakout: scaffold close-out

**Strategy family:** `usdjpy_range_bar_mtf_breakout`
**Version:** `0.1.0-c029`
**Branch:** `research-campaign-029-usdjpy-range-bar-scaffold-001`
**Base:** `4e2c532` (clean `origin/main`)
**Date:** 2026-05-29
**Status:** `SCAFFOLD_ONLY / NOT_RUN / NOT_APPROVED`

> Scaffold + preflight + documentation for a single-pair USD_JPY 10-pip range-bar
> research candidate with higher-timeframe context. **No strategy evidence run.
> Nothing approved. Test lockbox closed. Paper/demo/live blocked.**

---

## 1. Campaign-number correction

The originating prompt said **CAMPAIGN_028**, but 028 was already committed on
`origin/main` (relative-value spread front-gate screen, `1f3fe21`/`f0516b9`).
Reusing it would clobber a documented rejection, so — per the no-reuse discipline
that already forced a C024→C025 rename — this lane is **CAMPAIGN_029** (next unused
id; 024 is also burned). User confirmed 029 on 2026-05-29.

## 2. Commits by phase

| phase | commit | content |
|-------|--------|---------|
| 0 | `d1836a8` | baseline audit + plan + gitignore whitelist |
| 1 | `6386fb5` | frozen precommit scope + campaign config |
| 2 | `7425ff7` | range-bar data preflight script + compact diagnostics |
| 3 | `2ec9d23` | HTF alignment design |
| 4 | `7b59757` | strategy scaffold module + 24 unit tests |
| 5 | `ebff1eb` | Backtrader/range-bar parity design (design only) |
| 6 | _this commit_ | EVIDENCE_INDEX entry + final validation + this summary |

## 3. Files added / changed

- `docs/research/CAMPAIGN_029_USDJPY_RANGE_BAR_SCAFFOLD_PLAN.md`
- `docs/research/CAMPAIGN_029_PRECOMMIT_SCOPE.md`
- `docs/research/CAMPAIGN_029_HTF_ALIGNMENT_DESIGN.md`
- `docs/research/CAMPAIGN_029_BACKTRADER_PARITY_DESIGN.md`
- `docs/research/CAMPAIGN_029_USDJPY_RANGE_BAR_SCAFFOLD_SUMMARY.md` (this file)
- `configs/campaign_029_usdjpy_range_bar_mtf_breakout.yaml`
- `scripts/preflight_campaign_029_usdjpy_range_bars.py`
- `src/forex_bot/strategies/usdjpy_range_bar_mtf_breakout.py`
- `tests/unit/test_usdjpy_range_bar_mtf_breakout.py`
- `research/campaign_029/preflight/USD_JPY_range_10pip_diagnostics.{json,md}`,
  `preflight_manifest.json` (compact; full bars gitignored)
- `docs/research/EVIDENCE_INDEX.md` (+ CAMPAIGN_029 section)
- `.gitignore` (whitelist compact diagnostics under `research/campaign_029/**`)

## 4. Preflight result summary (USD_JPY 10-pip range bars, full corpus)

Window `2021-05-27 → 2026-05-26`, **1,844,454 M1 rows** → **72,940 completed range
bars** (+1 incomplete final, never traded). Characterisation only — no signals,
trades, or P&L.

- M1 rows/bar: mean **25.3**, median **11**, max **1363**.
- elapsed/bar: median **600 s**; **261** weekend/holiday gap-spanning bars (>1 day),
  max ~74 h.
- multi-threshold crossing rate **4.34%** — the population the anti-spike overshoot
  guard (`thresholds_crossed > 1`) is designed to drop.
- overshoot pips: mean **2.72**, p99 **24.7**, max **265**.
- direction roughly balanced: `range_up` **36,859** / `range_down` **36,081**.
- session mix (UTC buckets): tokyo 21,001 · london 15,862 · london_ny_overlap
  21,363 · new_york 9,937 · pacific 4,778. Sat **0**; Sun 1,441 (Sunday open).
- **lookahead violations: 0** (per-bar structural invariants all held); the script
  exits non-zero on any violation or if `full_bars/` is not git-ignored.

## 5. Exact campaign scope (frozen — see precommit)

USD_JPY only · 10-pip range bars from M1 **mid** · no tick assumption · mandatory
H4 (H4M1, m1_derived) EMA50-slope trend bias · optional native-H4-derived D1AGG
"not against" confirmation · trigger = continuation after pullback-and-reclaim in
trend direction · anti-spike overshoot guard (`>1` threshold or `>10 pip`
overshoot rejected) · stop = `max(5-bar swing, 2.0×10pip = 20 pip floor)` · time
stop 12 range bars · **no** profit target · **next-range-bar-open** fill · frozen
splits `train 2021-05-27→2023-12-31 / validation 2024 / test(lockbox) 2025-01-01→2026-05-20`.

## 6. HTF alignment (design)

Decision instant = range bar `close_time` `t`. H4 and D1AGG resolved via the
existing `align_last_completed` to the **last completed** HTF bar `<= t`
(`completed_only` pre-filter → no partial HTF bars). **H4 missing/stale → no
trade** (mandatory bias); **D1AGG missing/stale → optional gate skipped**, trade
permitted on H4 alone. Entry (next range-bar open) is strictly `> t`, so the
authorising context is always older than the entry. Provenance fields
(`decision_time`, `available_data_cutoff`, `htf_feature_times`, …) are populated
and audited by `validate_signal_provenance`.

## 7. Strategy scaffold summary

Pure-signal research module: config dataclass (enforces the 10-pip identity),
provenance guard, H4/D1AGG trend wrappers over `align_last_completed`,
pullback-reclaim trigger, overshoot guard, structural stop, and a range-bar exit
resolver. Emits a `Signal` with `next_bar_open` semantics + full HTF provenance. It
has **no broker/executor/OANDA imports**, **refuses** live/paper/demo
(`LiveTradingRefused`), and is **not registered** in `strategies/__init__` (range
bars are not a `CandleFrame.Granularity`), so it cannot reach an order path.
Covered by **24 unit tests** (all green).

## 8. Tests / gates run (final, Phase 6)

- `pytest tests/ -q` → **all green** (see commit message for counts).
- `ruff check src scripts tests` → clean.
- `python scripts/check_research_freeze.py` → ALL CHECKS PASSED.
- `python scripts/validate_research_archive.py` → ALL CHECKS PASSED.
- `python scripts/scan_artifacts_for_secrets.py` → PASSED.
- `git status --short` → only intended docs/config/script/test/diagnostic files.

## 9. Confirmations

- **No strategy approved.** `configs/approved_strategies.yaml` remains `approved: []`.
- **Paper/demo/live remain blocked.** No executor/broker change; no OANDA endpoint;
  no live credentials; the strategy refuses live/paper/demo and is executor-unwired.
- **No test lockbox opened. No trading recommendation. No parameter tuning.**
- **No bulky/raw artifacts committed** — full generated range bars stay local &
  gitignored; only compact diagnostics are tracked.

## 10. Remaining blockers before evidence execution

1. **No execution engine for range bars yet.** A train/validation engine must
   resolve `next_bar_open` entries and `stop → time → end_of_data` exits on the
   **underlying M1** (not the range bar's compressed OHLC) — see parity design §2/§5.
2. **D1AGG availability.** Native-H4-derived D1AGG must be confirmed available over
   the USD_JPY window; if absent the optional gate is simply skipped (documented).
3. **Staleness bounds** for H4 (≈8 h) and D1AGG (≈3 d) are precommit defaults; the
   execution sprint must fix and document final values before running.
4. **Backtrader/range-bar parity harness** is design-only; it must be built and
   clear the §6 minimum bar before any `PROMOTION_REVIEW_REQUIRED` classification.
5. **Split boundary counts** (range bars per split) to be confirmed at execution
   time; the test window stays a sealed lockbox.

## 11. Recommended next sprint

`research-campaign-029-usdjpy-range-bar-execution-001` — build the M1-resolved
range-bar execution engine, run **train (2021-05-27→2023-12-31)** then, only if the
train gates pass, **validation (2024)** evidence against the frozen precommit,
build the parity cross-check, and classify a status no higher than
`RESEARCH_PASS / PROMOTION_REVIEW_REQUIRED`. **Do not** open the 2025–2026 test
lockbox unless the train/validation **and** parity gates pass. **Not run here.**

## 12. Files to review first

1. `docs/research/CAMPAIGN_029_PRECOMMIT_SCOPE.md` — the binding frozen rule.
2. `src/forex_bot/strategies/usdjpy_range_bar_mtf_breakout.py` — the scaffold.
3. `docs/research/CAMPAIGN_029_HTF_ALIGNMENT_DESIGN.md` — no-lookahead contract.
4. `research/campaign_029/preflight/USD_JPY_range_10pip_diagnostics.md` — what the
   bar stream actually looks like.
5. `docs/research/CAMPAIGN_029_BACKTRADER_PARITY_DESIGN.md` — parity bar before
   promotion.
