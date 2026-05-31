# RANGE_AND_VOLATILITY_BARS_001 — Summary

**Branch:** `infra-range-and-volatility-bars-001`
**Type:** infrastructure + validation only. **Not a strategy campaign.**
**Date:** 2026-05-29
**Outcome:** non-time-bar (range + volatility) infrastructure built, tested,
and validated; full-corpus diagnostics produced; **no strategy approved**;
research freeze intact.

---

## 1. Commit hashes by phase

| Phase | Hash | Title |
|------|------|-------|
| 0 | `f465183` | baseline audit + plan |
| 1 | `63150a3` | construction specs |
| 2 | `7b09b08` | reusable bar builders |
| 3 | `408f302` | unit tests |
| 4 | `597743a` | diagnostics script + helpers |
| 5 | `2890900` | smoke diagnostic |
| 6 | `1ca23d9` | full-corpus diagnostics |
| 7 | `748a576` | storage/materialization design |
| 8 | `80d2f22` | next-sprint handoff prompt |
| 9 | _this commit_ | final validation + summary |

## 2. Files changed by phase

- **0:** `docs/research/RANGE_AND_VOLATILITY_BARS_001_PLAN.md`; `.gitignore`
  (non_time_bars artifact policy); `research/non_time_bars/.gitkeep`.
- **1:** `docs/research/RANGE_BAR_CONSTRUCTION_SPEC.md`,
  `docs/research/VOLATILITY_BAR_CONSTRUCTION_SPEC.md`.
- **2:** `src/forex_bot/data/non_time_bars.py`.
- **3:** `tests/unit/test_non_time_bars.py`.
- **4:** `scripts/generate_non_time_bar_diagnostics.py`,
  `tests/unit/test_non_time_bar_diagnostics.py`; `non_time_bars.py` (+ streaming
  builders); `tests/unit/test_non_time_bars.py` (+ stream tests); `.gitignore`
  (whitelist fix).
- **5:** `docs/research/NON_TIME_BAR_SMOKE_DIAGNOSTIC_RESULT.md`;
  `scripts/generate_non_time_bar_diagnostics.py` (dedup + UTC fixes);
  `research/non_time_bars/smoke/*.json`.
- **6:** `docs/research/NON_TIME_BAR_FULL_CORPUS_DIAGNOSTIC_RESULT.md`;
  `research/non_time_bars/full_corpus/*.json`,
  `research/non_time_bars/full_corpus_tr/*.json`.
- **7:** `docs/research/NON_TIME_BAR_STORAGE_AND_MATERIALIZATION_DESIGN.md`.
- **8:** `docs/research/NEXT_SPRINT_PROMPT_AFTER_RANGE_AND_VOLATILITY_BARS_001.md`.
- **9:** this summary.

## 3. Range bar implementation summary

`src/forex_bot/data/non_time_bars.py` → `RangeBarConfig`, `RangeBar`,
`build_range_bars` (full-materialise) + `stream_range_bars` (memory-bounded).
A bar completes the first time price moves `threshold_pips` from the bar open in
**either** direction; OHLC are the true M1 extremes across contributing rows;
canonical bar timestamp = close (completion) time. Bid/ask/mid basis (default
mid). Full provenance per bar.

## 4. Volatility bar implementation summary

`VolatilityBarConfig`, `VolatilityBar`, `build_volatility_bars` +
`stream_volatility_bars`. A bar completes when a cumulative movement proxy
reaches the threshold: **`abs_close`** (cumulative |Δclose|) or **`true_range`**
(cumulative TR). Threshold is **`fixed`** or **`atr_scaled`** (effective
threshold = `atr_multiple × ATR` of the trailing window of *prior completed* M1
rows, snapshot at bar open — lookahead-free, with warm-up).

## 5. Exact construction rules

- **Pip size:** 0.01 for names ending `JPY` (USD_JPY only here), else 0.0001.
  Pips = price_distance / pip_size. Internal math in `Decimal` for exact
  threshold-boundary completion; `float` OHLC exposed on records.
- **Price basis:** bid/ask/mid from the matching `Candle` components; mid falls
  back to `(bid+ask)/2`; missing required component raises.
- **Range completion:** `max(high−open, open−low) ≥ threshold_pips` →
  `range_up` if up-span ≥ down-span else `range_down` (tie → `range_up`).
- **Volatility completion:** running `movement ≥ effective_threshold`;
  per-row increment = |close−prev_close| (`abs_close`) or Wilder TR
  (`true_range`), `prev_close` carried across bar boundaries; first row seeds
  `prev_close := open`.
- **Multi-threshold (one M1 candle crosses several thresholds):** candle-atomic —
  one bar completes, with `thresholds_crossed = floor(move/threshold)` and
  `overshoot_pips` recorded. No synthetic sub-bars are fabricated (M1 OHLC cannot
  resolve the intrabar path).
- **Incomplete final bar:** dropped by default; emitted with `incomplete=True`
  only when `emit_incomplete_final=True`.
- **Ordering/duplicates:** `require_sorted=True` rejects unsorted (else sorts);
  `duplicate_policy` reject (default) / keep_first / keep_last. Mixed instruments
  rejected.

## 6. Lookahead-bias protections

Pure causal left-to-right fold: a bar's OHLC and completion use only rows
at-or-before the completing row; appending future rows never alters a completed
bar (unit-tested **causal-prefix** property for both builders). `atr_scaled`
thresholds use only prior-completed-window data and are fixed at bar open. No
"next candle" is ever read. Same input → identical output (Decimal-deterministic).

## 7. Unit test summary

`tests/unit/test_non_time_bars.py` (31) + `tests/unit/test_non_time_bar_diagnostics.py`
(7) = 38 new tests — all green. Cover: fixed-pip completion (JPY + non-JPY), OHLC/provenance,
up/down reason, multi-threshold determinism, incomplete-final default-drop vs
opt-in, deterministic re-run, unsorted reject/sort, duplicate
reject/keep_first/keep_last, mixed-instrument + empty input, bid/ask/mid +
mid-fallback + missing-basis raise, abs_close + true_range proxies (+JPY),
ATR-scaled prior-window-only (+ "current-bar rows don't raise own threshold" +
warm-up emits nothing), explicit no-lookahead causal-prefix, stream-vs-build
parity, stream out-of-order rejection, lazy-generator, and the diagnostic
helpers (session bucket, number stats, summarize_bars, warnings, counting
stream). Full suite: **2252 passed**.

## 8. Smoke diagnostic result

USD_JPY, 2023-01-01→2023-03-01 (59,813 M1 rows): range 10-pip → 3,539 bars
(×16.9 vs M1, balanced up/down); abs_close 20-pip → 4,747 bars (×12.6). Caught
and fixed two real bugs: `iter_m1_chunks` boundary-row duplication (de-duped in
reader) and psycopg session-local-tz timestamps (normalised to UTC before
session/weekday bucketing). Details:
`docs/research/NON_TIME_BAR_SMOKE_DIAGNOSTIC_RESULT.md`.

## 9. Full-corpus diagnostic result

All 7 majors (~1.8M M1 rows each, ~5y) across the full grid. Range 10-pip yields
20k–73k bars/pair (~M15–H1 cadence); 5-pip is noisy (3–12 min dwell, up to 9%
multi-threshold); 20-pip is sparse on AUD/NZD/CHF (~5–6k bars). `true_range`
produces ~1.7–1.8× more bars than `abs_close` at the same pip threshold.
A single pip threshold is **not** cadence-uniform across pairs (USD_JPY ~3×
NZD_USD). Details: `docs/research/NON_TIME_BAR_FULL_CORPUS_DIAGNOSTIC_RESULT.md`.

## 10. Recommended thresholds for future research

- **Range:** 10 pip primary, 15 pip secondary (10-pip-only for AUD_USD/NZD_USD).
- **Volatility:** `true_range 20 pip` primary, `abs_close 20 pip` companion.
- Use **per-pair** thresholds or the **`atr_scaled`** mode to equalise
  cross-pair cadence.

## 11. Storage / materialization

**Designed only — not implemented.** Proposed a dedicated
`market_data.non_time_bars` table with full provenance + `builder_config_hash`;
recommendation is to **delay** materialization until a campaign needs indexed
reads (bars are cheap and regenerable). See
`docs/research/NON_TIME_BAR_STORAGE_AND_MATERIALIZATION_DESIGN.md`.

## 12. Local artifacts created but not committed

- Optional `research/non_time_bars/**/full_bars/*.csv` (only when
  `--save-full-bars`) — gitignored; verified via `git check-ignore`. None remain
  on disk at sprint close.
- Background run logs (`research/non_time_bars/_*.log`) — gitignored; removed.
- Full generated bars are never written without `--save-full-bars`.

## 13. Validation commands run (sprint close)

- `pytest tests/ -q` → **2252 passed**.
- `ruff check src/ scripts/ tests/` → all checks passed.
- `python scripts/check_research_freeze.py` → ALL CHECKS PASSED.
- `python scripts/validate_research_archive.py` → ALL CHECKS PASSED.
- `python scripts/scan_artifacts_for_secrets.py` → PASSED.
- `git status --short` → clean.

## 14. Freeze / archive / secrets status

All green. Registry empty; paper-loop and demo-loop refuse (`trend_following`);
no credential-shaped strings; all evidence-index links resolve.

## 15. No strategy approved

`configs/approved_strategies.yaml` remains `approved: []`. No strategy was
created, backtested, tuned, or approved. The diagnostics describe bar *geometry*
only — **no edge claim, no strategy evidence.**

## 16. Paper / demo / live remain blocked

No paper/demo/live enablement; no executor/broker behavior change; no OANDA API
calls; no live credentials; QuantConnect/LEAN remains retired/blocked. Verified:
the diff vs `origin/main` touches no broker/execution/approval/loop/`.env`/lean
files.

## 17. Recommended next sprint

**Option 1 (recommended):** scaffold a single-pair USD_JPY 10-pip range-bar
campaign with H4/D1AGG context behind the edge-discovery front gate (scaffold
only, no approval). Alternatives: a non-time-bar preflight/comparison lane, or
materializing the recommended series into Postgres. See
`docs/research/NEXT_SPRINT_PROMPT_AFTER_RANGE_AND_VOLATILITY_BARS_001.md`.

## 18. Exact files to review first

1. `src/forex_bot/data/non_time_bars.py` — the builders (core deliverable).
2. `docs/research/RANGE_BAR_CONSTRUCTION_SPEC.md` +
   `docs/research/VOLATILITY_BAR_CONSTRUCTION_SPEC.md` — the rules.
3. `tests/unit/test_non_time_bars.py` — correctness + no-lookahead proofs.
4. `docs/research/NON_TIME_BAR_FULL_CORPUS_DIAGNOSTIC_RESULT.md` — findings +
   recommended thresholds.
5. `scripts/generate_non_time_bar_diagnostics.py` — how diagnostics are produced.
