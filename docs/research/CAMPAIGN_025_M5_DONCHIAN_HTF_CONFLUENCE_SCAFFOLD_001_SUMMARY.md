# CAMPAIGN_025 — M5 Donchian + HTF confluence breakout (SCAFFOLD_001 summary)

**Status:** `SCAFFOLD_ONLY / NOT_RUN / NOT_APPROVED`. No evidence run; test
lockbox closed; no strategy approved; paper/demo/live blocked.

> **Campaign-number note.** This scaffold was originally built as **CAMPAIGN_024**
> (phases 0–7, hashes below) and then renamed wholesale to **CAMPAIGN_025** in a
> follow-up commit, because the number "C024" had already been used in the record
> for the abandoned C022/C023 pullback-resolution continuation
> (`C024_READINESS_FROM_C022_FEATURE_SEPARATION.md`, `C024 NOT_READY`). The phase
> hashes below are the original C024-era commits (history is unchanged); the rename
> commit sits on top.

---

### 1. Branch
`research-campaign-025-m5-donchian-htf-confluence-scaffold-001` (off `origin/main`).

### 2. Commit hashes by phase
| Phase | Hash | Title |
|---|---|---|
| 0 | `ad224b7` | baseline audit + scaffold plan |
| 1 | `4277173` | frozen precommit spec |
| 2 | `6851374` | strategy module + unit tests |
| 3 | `7fa0dac` | config + gates + registry |
| 4 | `e20bfda` | data-feature preflight runner |
| 5 | `50d5a90` | Backtrader parity design stub |
| 6 | `f9eab91` | distinctness + prior-lessons memo |
| 7 | `30fb4c8` | scaffold validation + summary |
| rename | _this commit_ | rename CAMPAIGN_024 → CAMPAIGN_025 |

### 3. Files changed by phase
- **0:** `docs/research/CAMPAIGN_025_M5_DONCHIAN_HTF_CONFLUENCE_SCAFFOLD_001_PLAN.md`
- **1:** `docs/research/CAMPAIGN_025_PRECOMMIT_M5_DONCHIAN_HTF_CONFLUENCE_SCOPE.md`
- **2:** `src/forex_bot/strategies/m5_donchian_htf_confluence_breakout.py`,
  `src/forex_bot/strategies/__init__.py`, `src/forex_bot/config.py`,
  `tests/unit/test_m5_donchian_htf_confluence_breakout.py`
- **3:** `configs/campaign_025_m5_donchian_htf_confluence_breakout.yaml`,
  `src/forex_bot/research/campaign_025_gates.py`,
  `tests/unit/test_campaign_025_gates.py`, `docs/research/STRATEGY_STATUS.md`,
  `docs/research/EVIDENCE_INDEX.md`, `docs/research/EVIDENCE_MANIFEST.json`,
  `docs/research/FUTURE_RESEARCH_BACKLOG.md`
- **4:** `scripts/run_campaign_025_m5_donchian_htf_confluence.py`,
  `src/forex_bot/research/campaign_025_loader.py`,
  `research/campaign_025/preflight/*.json`
- **5:** `docs/research/CAMPAIGN_025_BACKTRADER_PARITY_DESIGN.md`
- **6:** `docs/research/CAMPAIGN_025_DISTINCTNESS_AND_PRIOR_LESSONS_MEMO.md`
- **7:** this summary + EVIDENCE_INDEX/MANIFEST link completion

### 4. Strategy identity
`m5_donchian_htf_confluence_breakout 0.1.0-c025`. M5 execution; M15 setup;
H1/H4M1 trend; D1AGG (native-H4-derived) regime. CAMPAIGN_025.

### 5. Data provenance
M5/M15/H1/H4(=H4M1) from materialized M1-derived Postgres bars
(`source=m1_materialized`); D1AGG from native-H4-derived aggregation
(`native_h4_derived_d1agg`). M1-derived D1AGG rejected.

### 6. Exact precommitted rules
Frozen in `CAMPAIGN_025_PRECOMMIT_M5_DONCHIAN_HTF_CONFLUENCE_SCOPE.md`. Long:
H4 bullish (close>EMA50 & EMA20≥EMA50) + H1 bullish (EMA20>EMA50 & EMA20 slope≥0
over 3 bars) + D1AGG not-bearish (close≥EMA50 OR EMA20 slope≥0) + M15 setup
(low touched ≤EMA20 within 8 bars OR Donchian(12) width/ATR(14)≤3.0) + M5 close >
prior-20-bar Donchian high; entry next M5 open. Short is the mirror. Stop = farther
of (2.0×ATR(14) at prior bar) and (opposite prior-20-bar channel side). Time stop
48 M5 bars. No TP/trailing/protective. `next_bar_open` only.

### 7. How the Donchian breakout is calculated
`donchian_high(high, 20)` / `donchian_low(low, 20)` use `.shift(1)`, so the
channel at bar *t* is the max/min of the **prior 20 completed bars**, excluding
bar *t*. Long fires when the signal bar's close exceeds that prior channel high;
short when below the prior channel low. No current-bar lookahead (unit-tested).

### 8. How M15/H1/H4/D1AGG confluence is calculated
All HTF features are read at the M5 decision timestamp via
`align_last_completed`, which selects the **last completed** HTF bar ≤ decision —
no HTF lookahead. EMAs (20/50) computed per HTF; H1 and D1AGG also use a 3-bar
EMA20 slope anchored at the aligned bar. D1AGG comes from `aggregate_h4_to_d1`
over native H4. If any context is blocked/unavailable → no trade.

### 9. How `next_bar_open` is enforced
The strategy emits a signal stamped at the completed signal bar; entry is the
**next M5 bar open** (config `fill_timing: next_bar_open`, `approval_bound`,
`conservative`). No `signal_bar_close`; no same-bar entry. The runner's metadata
guard rejects any non-`next_bar_open` timing. (Unit test confirms the next bar
open is strictly after the signal timestamp.)

### 10. Unit tests added
- `tests/unit/test_m5_donchian_htf_confluence_breakout.py` (26 tests): prior-bar
  Donchian, no-breakout-when-current-bar-only, H1/H4 context required, short
  mirror, D1AGG block, M15 pullback/compression anti-chasing, next_bar_open,
  deterministic farther-of stop, time stop at exactly 48 bars, stop>time>eod
  priority, no target/trailing/protective, no HTF lookahead, provenance,
  granularity guard, open-position block, no broker/executor/OANDA imports.
- `tests/unit/test_campaign_025_gates.py` (7 tests): frozen thresholds, train
  reject/pass, validation screening + parity-still-required, 100-trade floor,
  SINGLE_PAIR_REVIEW_ONLY flag, promotion-review max status.

### 11. Preflight results
`--preflight-only`: **all 7 pairs PASS** materialized M5/M15/H1/H4 coverage over
the train window; registry empty; metadata valid; live aggregation off. Artifact:
`research/campaign_025/preflight/preflight_result.json`,
`pair_coverage_summary.json`.

### 12. Data-feature preflight results
`--data-feature-preflight`: **all 7 pairs PASS**; **0 lookahead violations**;
warmup OK; D1AGG (native) present (≈779 D1 bars/pair). Artifacts:
`data_feature_preflight.json`, `htf_alignment_sample.json`,
`feature_warmup_summary.json`.

### 13. Whether sample signals were generated
Yes — bounded, single-pair probes only (no fills, no PnL, **not evidence**):
USD_JPY 90d/step5 → 24 signals (10 long / 14 short); USD_JPY 120d → 70; GBP_USD
120d → 39. Confirms the feature → signal pipeline runs end-to-end and produces
directionally-varied signals. Artifact: `sample_signal_summary.json`.

### 14. Whether full evidence was run
**No.** No train/validation/test evidence; the runner contains no
train/validation/test machinery.

### 15. Whether test lockbox opened
**No.** Lockbox stays closed; the runner cannot open it.

### 16. Whether any strategy is approved
**No.** `configs/approved_strategies.yaml` remains `approved: []`.

### 17. Whether paper/demo/live remain blocked
**Yes, blocked.** Config has `trading_enabled: false`, `allow_order_submission:
false`, `allow_live_trading: false`; paper/demo loops still refuse all strategies.

### 18. Archive / freeze / secrets status
research-freeze **PASS**; research-archive **PASS**; secret scan **PASS**.

### 19. Ruff / pytest results
ruff **clean**; pytest **2029 passed / 3 skipped** (1996 baseline + 26 strategy
+ 7 gates).

### 20. Known blockers / warnings
- **M5 materialized coverage begins ~2021-05-27** inside the 2020-01-01 train
  window: the early train period (2020 → 2021-05) has **no M5 bars**. Not a
  scaffold blocker, but the future train sprint must either narrow the train
  window to the materialized M5 range or backfill M5 before claiming full-window
  train coverage. Documented, not improvised.
- A future financing/cost overlay and the Backtrader parity build remain
  precommitted gates (not done in this scaffold).

### 21. Recommended next sprint
`research-campaign-025-m5-donchian-htf-confluence-train-validation-001` — run
**train/validation only**, no test lockbox unless the precommitted gates **and**
Backtrader parity pass. First action there: resolve the 2020 M5-coverage gap
(narrow window or backfill) before any train claim.

---

**Files to review first:** the precommit spec
(`CAMPAIGN_025_PRECOMMIT_M5_DONCHIAN_HTF_CONFLUENCE_SCOPE.md`), the strategy
module (`src/forex_bot/strategies/m5_donchian_htf_confluence_breakout.py`), and
its tests (`tests/unit/test_m5_donchian_htf_confluence_breakout.py`).
