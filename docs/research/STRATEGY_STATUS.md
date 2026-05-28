# Strategy Status Registry

**Date:** 2026-05-28 · **Branch:** `research-campaign-021-ltf-mtf-confluence-execution-001`

This is the human-readable status of every strategy family the project
has built. It is the companion to the machine-enforced registry
`configs/approved_strategies.yaml`, which gates the paper / demo / live
loops.

> ## No strategy is approved for paper, demo, or live trading.
>
> Every strategy below is **paper: NO · demo: NO · live: NO.**
> `configs/approved_strategies.yaml` is empty; every order-capable loop
> refuses to start. See `docs/research/FINAL_RESEARCH_DECISION_MEMO.md`.

### Broad strategy search — PAUSED (2026-05-26)

Post-dedup failure meta-analysis (`POST_DEDUP_FAILURE_META_ANALYSIS_001`)
classified the C015–C017 cluster as **NO_RELIABLE_ARCHETYPE** and selected
**pause broad strategy search**. CAMPAIGN_015–017 remain **REJECT** on
dedup-safe evidence; CAMPAIGN_011 remains the **canonical deduped null**
(−0.0029 R, 1,180 trades). **CAMPAIGN_018 is not created.** No retuning of
C015/C016/C017 is authorized.

### H4-only entry research — PAUSED pending LTF lane readiness (2026-05-27)

CAMPAIGN_020 remains **REJECT**. The infrastructure sprint
`infra-m1-canonical-data-and-ltf-execution-lane-001` prepared a
canonical M1 data and lower-timeframe execution lane so future research
can evaluate M15/M5 entries with H1/H4/D1AGG context. It created no
CAMPAIGN_021 evidence, no strategy verdict, and no approval. M1 full-corpus
validation (`infra-m1-full-corpus-validation-and-aggregation-001`) is
**READY_WITH_WARNINGS**. CAMPAIGN_021 executed train-only evidence 2026-05-28;
**REJECT** (train −0.0174 R); validation/test not run per gate discipline.

| document | purpose |
|---|---|
| [`BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md`](BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md) | Pause rationale, comparison table, re-entry gates |
| [`POST_DEDUP_FAILURE_META_ANALYSIS_001_SUMMARY.md`](POST_DEDUP_FAILURE_META_ANALYSIS_001_SUMMARY.md) | Meta-analysis close-out |
| [`NEXT_NON_STRATEGY_WORKSTREAM_DECISION.md`](NEXT_NON_STRATEGY_WORKSTREAM_DECISION.md) | Next sprint: observed cost / spread diagnostics |

### Evidence integrity (dedupe audit 001)

Pre-fix bespoke campaigns on `data/campaign_002.sqlite3` may be
**LIKELY_CONTAMINATED** by duplicate UTC H4 bars. **C008/C009 updated:**
deduped forensic replay (`infra-deduped-c008-c009-rerun-forensic-only-001`)
confirmed descriptive claims — label now **`DEDUPED_FORENSIC_REPLAY_CONFIRMED`**
(verdicts unchanged REJECT). See
[`C008_C009_EVIDENCE_INTEGRITY_DECISION.md`](C008_C009_EVIDENCE_INTEGRITY_DECISION.md).
Other pre-fix campaigns: see
[`CAMPAIGN_EVIDENCE_INTEGRITY_AFTER_DEDUP_FIX.md`](CAMPAIGN_EVIDENCE_INTEGRITY_AFTER_DEDUP_FIX.md).
Verdicts are **unchanged**; metrics before dedupe-fix rerun carry
**EVIDENCE INTEGRITY UNKNOWN — RERUN REQUIRED BEFORE USE** unless
marked **DEDUP-SAFE** or **DEDUPED_FORENSIC_REPLAY_CONFIRMED**.

## Status legend

- **rejected** — tested on real data, failed its pre-committed gates;
  not a promotion candidate.
- **research-only** — may be backtested for research; never approved for
  any trading loop.
- **blocked** — cannot be validly tested with current infrastructure.

Backtesting any strategy for research is always allowed. "Approved" here
means *only* "permitted to run in a paper / demo / live loop", and **no
strategy is approved.**

## Summary table

| strategy / version | status | paper | demo | live | primary evidence |
|---|---|:--:|:--:|:--:|---|
| `trend_following 0.1.0` (EMA + Donchian baseline) | rejected | NO | NO | NO | CAMPAIGN_002 |
| `trend_following` + ADX-14 gate (the "0.2.0 ADX" variant) | rejected | NO | NO | NO | CAMPAIGN_003 |
| `volatility_breakout 0.1.0-c004` | rejected | NO | NO | NO | CAMPAIGN_004 |
| `pullback_continuation` | rejected | NO | NO | NO | CAMPAIGN_007 |
| `mean_reversion 0.1.0-c008` | rejected (research-only) | NO | NO | NO | CAMPAIGN_008 |
| `mean_reversion 0.2.0-c009` | rejected (research-only) | NO | NO | NO | CAMPAIGN_009 |
| `mean_reversion_protective_stop 0.1.0-c018` | rejected | NO | NO | NO | CAMPAIGN_018 |
| `mean_reversion_thesis_invalidation 0.1.0-c019` | rejected | NO | NO | NO | CAMPAIGN_019 |
| `session_breakout 0.1.0-c010` | rejected | NO | NO | NO | CAMPAIGN_010 |
| `random_entry_anchor 0.1.0-c011` | rejected (null model anchor) | NO | NO | NO | CAMPAIGN_011 |
| `regime_switcher_atr_percentile 0.1.0-c012` | rejected | NO | NO | NO | CAMPAIGN_012 |
| `cross_pair_currency_strength_rotation 0.1.0-c013` | rejected | NO | NO | NO | CAMPAIGN_013 |
| `calendar_event_window_anomaly 0.1.0-c014` | rejected | NO | NO | NO | CAMPAIGN_014 |
| `failed_breakout_reversal 0.1.0-c015` | rejected (deduped rerun) | NO | NO | NO | CAMPAIGN_015 deduped |
| `weekly_cross_sectional_momentum_low_turnover 0.1.0-c016` | rejected (deduped) | NO | NO | NO | CAMPAIGN_016 deduped |
| `weekly_volatility_contraction_breakout 0.1.0-c017` | rejected (deduped) | NO | NO | NO | CAMPAIGN_017 deduped |
| `multi_timeframe_confluence_pullback 0.1.0-c020` | rejected | NO | NO | NO | CAMPAIGN_020 |
| `lower_timeframe_mtf_confluence_entry 0.1.0-c021` | rejected | NO | NO | NO | CAMPAIGN_021 |
| `h4_h1_pullback_resolution_entry 0.1.0-c022` | rejected | NO | NO | NO | CAMPAIGN_022 |
| `h4_h1_pullback_resolution_entry 0.1.0-c023` (ADX22 sibling of C022) | scaffold-only (not executed) | NO | NO | NO | CAMPAIGN_023 (scaffold) |

There is also a daily-trend hypothesis (CAMPAIGN_006) that is **blocked**
— not a strategy verdict but an infrastructure one: D1 candles cannot be
validly backtested by the current engine.

`failed_breakout_reversal 0.1.0-c015` is **rejected** on deduped evidence
(sprint `infra-canonical-candle-dedup-and-campaign015-rerun-001`):
prior bespoke metrics were **evidence-contaminated** by duplicate SQLite
H4 candles. Deduped rerun: base exp_r **-0.0101**, 375 trades, 2/8 fold
pass, anti-overfit **`WITHIN_NULL`**. See
[`CAMPAIGN_015_DEDUPED_RERUN_INTERPRETATION.md`](CAMPAIGN_015_DEDUPED_RERUN_INTERPRETATION.md)
and [`CAMPAIGN_015_DUPLICATE_CANDLE_CONTAMINATION_MEMO.md`](CAMPAIGN_015_DUPLICATE_CANDLE_CONTAMINATION_MEMO.md).
Prior post-run diagnostics marked **SUPERSEDED BY DEDUP RERUN**.

`session_breakout 0.1.0-c010` is **rejected**: the
`research-asian-london-session-breakout-walk-forward-001`
evidence sprint ran the full 8-fold walk-forward (rolling, frozen,
540/180/180/180 days, 7-pair OANDA practice H4 universe), the
ESTIMATED + conservative-stress financing overlay, and the
portfolio-risk diagnostics, and recorded a clean REJECT against
the verbatim gates in
[`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
§10. The independent verifier did not run (it is capability-locked
to CAMPAIGN_002); this matters only for a hypothetical PASS, not
for a REJECT. See
[`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
for the gate-by-gate evidence.

### `random_entry_anchor 0.1.0-c011`

> **EVIDENCE INTEGRITY UNKNOWN — RERUN REQUIRED BEFORE USE.** Null-model
> metrics below were produced on pre-fix `CandleRepo.list` loads.
> Deduped null baseline **promoted** (`research/null_baselines/campaign_011_deduped_null_baseline.json`).
> CAMPAIGN_012–014 null-comparison sections **refreshed** against deduped null
> ([`CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md),
> [`CAMPAIGN_013_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_013_POST_DEDUP_NULL_REFERENCE.md),
> [`CAMPAIGN_014_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_014_POST_DEDUP_NULL_REFERENCE.md));
> campaign metrics remain **LIKELY_CONTAMINATED** pending deduped reruns.
> See [`POST_DEDUP_RERUN_BACKLOG.md`](POST_DEDUP_RERUN_BACKLOG.md).

- **Status:** rejected (null model anchor — cannot be approved
  by design).
- **Evidence:** CAMPAIGN_011 deduped canonical null baseline
  (`research-campaign-011-deduped-null-baseline-001`),
  real OANDA practice H4, 7-pair universe, 8 folds
  rolling/frozen, **1,180** trades total: **fold pass rate 0 / 8,
  aggregate expectancy −0.0029 R (≈ 0; null-model signature),
  profit factor **0.89** (≈ 1), aggregate return **−0.68 %** over 4
  years (≈ 0), 3 / 7 pairs positive (≈ uniform-noise
  expectation). Canonical rollup:
  [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json).
  Pre-fix metrics (1,177 trades, −0.0024 R) are **SUPERSEDED /
  LIKELY_CONTAMINATED**.
- **Paper / demo / live:** NO / NO / NO (structurally
  impossible — null model by design).
- **Reason:** Diagnostic anchor / null model. The REJECT
  verdict is the *expected and desired outcome* — it validates
  the evidence pipeline by demonstrating the gates correctly
  REJECT a known-zero-edge strategy with metrics consistent
  with random expectations. Per-pair distribution near-uniform
  (ratio max/min 1.65 vs CAMPAIGN_010's 12.0); session
  distribution diffuse across all 4 UTC buckets (vs
  CAMPAIGN_010's 100 % London); 79 % time-stop exit (matches
  CAMPAIGN_010's exit mechanics — confirms cost model
  consistency); 8 / 8 pipeline sanity checks pass.
  Conservative-stress financing strictly worsens (USD_JPY flips
  +→−; pairs_positive → 2 / 7). `master_seed = 20260523` was
  the only seed used; no seed optimization. The anchor
  establishes the falsifiability floor (aggregate expectancy
  −0.0024 R, profit factor 0.91, 3 / 7 pairs positive, 0 / 8
  fold pass rate) that every future C2 / C3 / C4 / new-family
  candidate must beat by a meaningful margin to count as
  evidence of an edge.

`regime_switcher_atr_percentile 0.1.0-c012` is **rejected**: the
`research-regime-switcher-atr-percentile-walk-forward-001` evidence
sprint ran the full 8-fold walk-forward (rolling, frozen,
540/180/180/180 days, 7-pair OANDA practice H4 universe), the
ESTIMATED + conservative-stress financing overlay, and the
portfolio-risk diagnostics, and recorded a REJECT against both the
verbatim CAMPAIGN_010 / CAMPAIGN_011 inherited gates (5 of 8
aggregate gates fail) and the CAMPAIGN_011 null-baseline comparison
codified in
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
(the metrics diverge from null in the **worse** direction, far
outside the symmetric indistinguishability band on three of four
binding axes). The independent verifier did not run (it is
capability-locked to CAMPAIGN_002); this matters only for a
hypothetical paper-promotion candidate, not for a REJECT. See
[`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md)
for the gate-by-gate evidence and
[`CAMPAIGN_012_EVIDENCE_SUMMARY.md`](CAMPAIGN_012_EVIDENCE_SUMMARY.md)
for the one-page summary.

### `regime_switcher_atr_percentile 0.1.0-c012`

- **Status:** rejected.
- **Evidence:** CAMPAIGN_012 walk-forward
  (`research-regime-switcher-atr-percentile-walk-forward-001`),
  real OANDA practice H4, 7-pair universe, 8 folds rolling/frozen,
  3,726 trades total: **fold pass rate 0 / 8, aggregate expectancy
  −0.0521 R, profit factor 0.034, aggregate return −43.52 % over 4
  years, 1 / 7 pairs positive (USD_JPY +0.0004 R — random-walk
  floor)**.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** The C3 daily-ATR-percentile regime gate (HIGH-VOL iff
  prior-day D1AGG ATR-14 ≥ P70 of trailing 60 D1AGG bars) **did not
  rescue** trend-following on H4 majors. It amplified trade count
  (3,726 vs CAMPAIGN_011's 1,177) without improving signal quality,
  accumulating cost drag. CAMPAIGN_012 is **markedly worse than the
  CAMPAIGN_011 null baseline** on every binding axis (expectancy
  −0.0497 R lower, PF −0.876 lower, return −42.99 pp lower, pairs
  −2 lower); classification is **REJECT** (not
  REJECT_INDISTINGUISHABLE_FROM_NULL because the divergence is in
  the worse direction). The hypothesis "high-vol regimes are
  trend-friendly on H4 majors" is falsified by the evidence on this
  universe + timeframe. USD_JPY's +0.0004 R is the same near-exact-
  zero random-walk floor CAMPAIGN_011 surfaced. Verifier did not
  run (capability-locked to CAMPAIGN_002; not required for REJECT;
  the suggested follow-up
  `infra-free-local-parity-verifier-regime-switcher-001` is
  **deferred indefinitely**). Financing overlay (ESTIMATED +
  conservative stress; MODELED refused at 4 layers) confirms the
  REJECT — adds −$65.07 drag; no pair flip; the
  `conservative_stress_run_does_not_flip_verdict` gate PASSES
  (verdict was already REJECT pre-financing). Per-pair distribution
  near-uniform (ratio max/min 1.60 vs CAMPAIGN_010's 12.0; close to
  CAMPAIGN_011's 1.65); session distribution diffuse across all 4
  UTC buckets (no concentration > 50 %; like CAMPAIGN_011, unlike
  CAMPAIGN_010's 100 % London); 79.3 % time-stop exit (matches
  CAMPAIGN_011's ~75 %); 8 / 8 pipeline sanity checks pass.

### `cross_pair_currency_strength_rotation 0.1.0-c013`

- **Status:** rejected.
- **Evidence:** CAMPAIGN_013 walk-forward
  (`research-cross-pair-currency-strength-rotation-walk-forward-001`),
  real OANDA practice H4, 7-pair universe, 8 folds rolling/frozen,
  **7,940 trades** total: **fold pass rate 0 / 8, aggregate expectancy
  −0.0564 R, profit factor 0.000, aggregate return −113.36 % over 4
  years, 1 / 7 pairs positive (USD_JPY +0.0000 R — random-walk
  floor)**.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** The C6 cross-pair 8-currency-strength rank-gap rule
  (long strong-base / short strong-quote pair when
  `|rank(quote) − rank(base)| ≥ 4`) over a 6-bar holding period
  **did not produce a directional edge** on H4 majors. It amplified
  trade count (7,940 vs CAMPAIGN_011's 1,177 — ~6.7 × as many)
  without improving signal quality, accumulating cost drag.
  CAMPAIGN_013 is **catastrophically worse than the CAMPAIGN_011 null
  baseline** on every binding axis (expectancy −0.0540 R lower, PF
  −0.910 lower, return −112.83 pp lower, pairs −2 lower);
  classification is **REJECT** (not REJECT_INDISTINGUISHABLE_FROM_NULL
  because the divergence is in the worse direction). The hypothesis
  "cross-pair currency-strength rank-gap predicts pair direction on
  6-bar holding period" is falsified by the evidence on this universe
  + timeframe. USD_JPY's +0.0000 R is the same near-exact-zero
  random-walk floor CAMPAIGN_011 and CAMPAIGN_012 surfaced; NZD_USD
  is catastrophic at −41.76 % over 4 years on 1,863 trades. The
  cross-pair runner integration contract was **SATISFIED on all 8
  folds** (common_index 1,825-1,848 H4 bars) — the REJECT is on
  inherited gates alone, not BLOCKED. Verifier did not run
  (capability-locked to CAMPAIGN_002; not required for REJECT; the
  suggested follow-up
  `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001`
  is **deferred indefinitely**). Financing overlay (ESTIMATED +
  conservative stress; MODELED refused at 4 layers) confirms the
  REJECT — adds −$139.99 drag (7,154 rollover events); **USD_JPY
  flips + → −** under financing (+$2.27 → −$5.89), taking
  `pairs_positive` from 1/7 to 0/7 post-financing; the
  `conservative_stress_run_does_not_flip_verdict` gate PASSES (verdict
  was already REJECT pre-financing). Architectural diagnostic:
  `MAX_OPEN_POSITIONS_EXCEEDED = 0` (per-pair runner; engine is
  single-instrument); simultaneous-signal frequency ~40 % of trading
  bars (cross-pair signal often fires on 2-4 pairs at the same H4
  timestamp; a portfolio-aware runner would cut trade count by ~40 %
  but cannot rescue per-pair negative expectancy on 6 of 7 pairs).
  **CAMPAIGN_013 is the worst-performing campaign to date by
  aggregate return / profit factor / trade count** (~214 × worse than
  CAMPAIGN_011 null floor; ~2.6 × worse than CAMPAIGN_012
  regime-switcher).

**Anti-pattern established by CAMPAIGN_012 + CAMPAIGN_013:** adding a
turnover-amplifying filter to a negative-edge entry direction on H4
majors makes results materially **worse**, not better — the
incremental complexity buys trade frequency without buying signal
quality. The slope is monotonic in trade count: CAMPAIGN_011 (1,177
trades, −0.53 %) → CAMPAIGN_012 (3,726 trades, −43.52 %) →
CAMPAIGN_013 (7,940 trades, −113.36 %). Any future discovery sprint
should explicitly disqualify turnover-amplifying filters on top of
rejected entry directions on this universe. **The discovery-005
sprint codified this as a first-class binding anti-pattern**
(Patterns M–Q in
[`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md))
and selected the next candidate accordingly.

`calendar_event_window_anomaly 0.1.0-c014` is **rejected**: the
`research-calendar-event-window-anomaly-walk-forward-001` evidence
sprint ran the full 8-fold walk-forward (rolling, frozen,
540/180/180/180 days, 7-pair OANDA practice H4 universe), the
ESTIMATED + conservative-stress financing overlay, and the
portfolio-risk diagnostics (including CAMPAIGN_014-specific event-
class clustering + per-event-class per-pair heatmap + concurrent-
firing diagnostic). The verdict is REJECT against both the verbatim
CAMPAIGN_010 / 011 / 012 / 013 inherited gates (6 of 8 aggregate
gates fail) and the CAMPAIGN_011 null-baseline comparison
(materially WORSE than null on all 4 PnL-direction axes; OUTSIDE
the symmetric ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair
indistinguishability band on the WORSE side, so classified
REJECT — direction-of-trade falsification — not
REJECT_INDISTINGUISHABLE_FROM_NULL). Turnover budget INTACT (720
trades ≤ 800 hard cap; 1,240 raw signals ≤ 1,500); fixture-coverage
gate PASS on all 8 folds. Phase 7 diagnostics surfaced two findings
of independent research value: (1) FOMC = 0 trades — all 51 FOMC
events SESSION_BLOCKED because the 19:00-UTC FOMC time → 22:00-UTC
trigger bar overlaps the rollover window, so the C7 hypothesis's
claim about FOMC is structurally untestable on this universe +
session filter; (2) NFP = 571 trades (79 % of all) generating
−$151.17 (98 % of total losses) — the REJECT is overwhelmingly an
"NFP counter-trend is wrong" finding (post-event H4 bar continues
the event-bar direction, does not revert). The independent
verifier did not run (capability-locked to CAMPAIGN_002; not
required for REJECT). See
[`CAMPAIGN_014_WALK_FORWARD_RESULT.md`](CAMPAIGN_014_WALK_FORWARD_RESULT.md)
for the gate-by-gate evidence and
[`CAMPAIGN_014_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_014_PORTFOLIO_RISK_DIAGNOSTICS.md)
for the FOMC-block + NFP-falsification analysis.

## Per-strategy detail

### `trend_following 0.1.0` — EMA + Donchian baseline

- **Status:** rejected.
- **Evidence:** CAMPAIGN_001 (synthetic data — harness validation only,
  not evidence), then CAMPAIGN_002 on real OANDA H4/H1 majors,
  2020–2026: **−0.085 R, profit factor 0.75, −1.02 %**.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Negative expectancy on real data; CAMPAIGN_005 showed it
  is no better than random entry once spreads are paid. Retired as a
  live candidate.

### `trend_following` + ADX-14 > 25 gate — the "0.2.0 ADX" variant

- **Status:** rejected.
- **Evidence:** CAMPAIGN_003 — the frozen baseline plus an ADX-14 > 25
  trend-strength gate, real OANDA H4, 6-pair universe:
  **−0.071 R, profit factor 0.77, −0.63 %**.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** The ADX gate was the obvious fix for the baseline; it did
  not rescue it. Still negative expectancy. Retired.

### `volatility_breakout 0.1.0-c004`

- **Status:** rejected.
- **Evidence:** CAMPAIGN_004 — breakout out of an ATR-compressed
  regime, no EMA trend filter, real OANDA H4:
  **−0.163 R, profit factor 0.63, −1.40 %** — the worst of the four
  trend/breakout families.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Negative expectancy on real data; a genuinely different
  entry family that still failed. Retired.

### `pullback_continuation`

- **Status:** rejected.
- **Evidence:** CAMPAIGN_007 (Research Marathon 001) — H4
  pullback-continuation. Screening failed outright: **train −0.164 R,
  validation −0.166 R**. The 2025–2026 test window was never opened.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Negative expectancy on both screening splits. Retired.

### `mean_reversion 0.1.0-c008`

- **Status:** rejected — research-only by design (`paper_only = True`).
- **Evidence integrity:** **`DEDUPED_FORENSIC_REPLAY_CONFIRMED`** (deduped forensic
  replay 2026-05-27; prior label LIKELY_CONTAMINATED superseded for descriptive use).
- **Evidence:** CAMPAIGN_008 — regime-filtered (ADX-14 < 20) reversion
  of z-score extremes, real OANDA H4. Screening **failed**: train expectancy
  **−0.025 R** (deduped replay; original −0.017 R) against "train ≥ 0" gate.
  Validation (2023–2024) **+0.161 R, PF 1.29, 6/6 pairs positive** (deduped;
  original +0.172 R), surviving 2× cost stress — strongest positive signal in
  the project, but **unconfirmed** (test lockbox unopened).
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Failed pre-committed train-split gate; capped at research-only.
  See [`C008_C009_EVIDENCE_INTEGRITY_DECISION.md`](C008_C009_EVIDENCE_INTEGRITY_DECISION.md).

### `mean_reversion_protective_stop 0.1.0-c018`

- **Status:** rejected — research-only (`paper_only = True`).
- **Evidence:** CAMPAIGN_018 — C008-identical entries + protective stop after +1R MFE
  (break-even). Deduped H4 run 2026-05-27. Train **−0.119 R** (236 trades); validation
  **+0.194 R** (142 trades, 6/6 pairs, PF 1.58). Screening **FAIL** (train gate, full
  stress_15x). Test lockbox **not opened**. Mechanism active (53% armed, 0% targets).
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Failed precommitted train-split gate. Protective-stop hypothesis **falsified**
  on train despite validation uplift vs C008. See [`CAMPAIGN_018_FINAL_INTERPRETATION.md`](CAMPAIGN_018_FINAL_INTERPRETATION.md).

### `mean_reversion_thesis_invalidation 0.1.0-c019`

- **Status:** rejected — research-only (`paper_only = True`).
- **Evidence:** CAMPAIGN_019 — C008-identical entries + z-score continuation thesis
  invalidation exit (long z ≤ −3.0 / short z ≥ +3.0 at bar close). Deduped H4 run
  2026-05-27. Train **−0.072 R** (219 trades); validation **+0.0962 R** (138 trades,
  6/6 pairs, PF 1.14). Screening **FAIL** (train gate, train vs C008, stress_15x).
  Test lockbox **not opened**. Mechanism active (12.6% thesis_invalidation; 0% targets/protective).
  Backtrader parity **PASS** (±1 trade).
- **Fill timing:** committed run used `signal_bar_close` (**optimistic upper bound** on
  validation); `next_bar_open` comparison validation **+0.0175 R** (~−0.079 R delta).
  See [`FILL_TIMING_APPROVAL_BOUND_POLICY.md`](FILL_TIMING_APPROVAL_BOUND_POLICY.md).
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Failed precommitted train-split gate. Thesis-invalidation hypothesis **falsified**
  on train despite validation uplift and beat-null vs C011. See
  [`CAMPAIGN_019_FINAL_INTERPRETATION.md`](CAMPAIGN_019_FINAL_INTERPRETATION.md).

### `lower_timeframe_mtf_confluence_entry 0.1.0-c021`

- **Status:** rejected — research-only.
- **Evidence:** CAMPAIGN_021 — M15 MTF confluence; **`next_bar_open`** 2026-05-28.
  Train **−0.0174 R** (1,438 trades); train gate **FAIL**. Validation/test/parity
  **not run** (no validation rescue). Test lockbox **closed**.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Train expectancy negative despite improvement vs C020 H4 train
  (−0.035 R). Higher M15 turnover did not earn non-negative train gate.
  See [`CAMPAIGN_021_FINAL_INTERPRETATION.md`](CAMPAIGN_021_FINAL_INTERPRETATION.md).

### `h4_h1_pullback_resolution_entry 0.1.0-c023` — ADX22 sibling of C022

- **Status:** scaffold-only — **PRECOMMITTED_NOT_EXECUTED / SCAFFOLD_ONLY**
  (no evidence verdict).
- **Evidence:** None in scaffold sprint. M15 execution with H4 (bias) + H1
  (pullback-holds) context; no D1 / D1AGG layer; three M1-derived layers
  (M15/H1/H4). Preflight-only.
- **Sibling:** identical to CAMPAIGN_022 (`0.1.0-c022`) **except** the H4
  directional-bias strength gate — `h4_adx_min` **22.0** (C022 uses **20.0**).
  No other intentional strategy-logic delta; the two share one strategy class.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Pre-registered ADX-sensitivity sibling; scaffold/precommit sprint
  only. C022 is itself unexecuted, so this is pre-registration, not tuning after
  results. Future execution sprint required for any train/validation gates. See
  [`CAMPAIGN_023_H4_H1_PULLBACK_RESOLUTION_ADX22_PRECOMMIT.md`](CAMPAIGN_023_H4_H1_PULLBACK_RESOLUTION_ADX22_PRECOMMIT.md).

### `multi_timeframe_confluence_pullback 0.1.0-c020`

- **Status:** rejected — research-only.
- **Evidence:** CAMPAIGN_020 — D1AGG + H4 MTF confluence pullback; **`next_bar_open`**
  execution 2026-05-27. Train **−0.035 R** (353 trades); validation **+0.053 R** (204 trades,
  PF 1.13). Screening **FAIL** (train gate, Backtrader parity not run). Test lockbox **closed**.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Train expectancy negative under approval-bound fill timing. Validation uplift
  does not rescue per gate discipline. See
  [`CAMPAIGN_020_FINAL_INTERPRETATION.md`](CAMPAIGN_020_FINAL_INTERPRETATION.md).

### `mean_reversion 0.2.0-c009`

- **Status:** rejected — research-only (`paper_only = True`).
- **Evidence integrity:** **`DEDUPED_FORENSIC_REPLAY_CONFIRMED`** (deduped forensic
  replay 2026-05-27; prior label LIKELY_CONTAMINATED superseded for descriptive use).
- **Evidence:** CAMPAIGN_009 — human-authorized follow-up adding midline-target exit.
  Screening **failed**: train expectancy **−0.025 R** (deduped; original −0.062 R —
  material change but gate outcome unchanged); validation **+0.186 R** (deduped;
  original +0.170 R). Midline exit caps reversion winners — falsified rescue hypothesis.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Failed pre-committed train-split gate. Test window 2025–2026 never opened.
  See [`C008_C009_EVIDENCE_INTEGRITY_DECISION.md`](C008_C009_EVIDENCE_INTEGRITY_DECISION.md).

### `session_breakout 0.1.0-c010`

- **Status:** rejected.
- **Evidence:** CAMPAIGN_010 walk-forward
  (`research-asian-london-session-breakout-walk-forward-001`),
  real OANDA practice H4, 7-pair universe, 8 folds rolling/frozen,
  2,791 trades total: **fold pass rate 0 / 8, aggregate
  expectancy −0.041 R, profit factor 0.04, aggregate return
  −36.6 %, 1 / 7 pairs positive (USD_CHF only)**.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Negative expectancy on out-of-sample data on the
  pre-committed 7-pair × 6-year universe under frozen parameters.
  Conservative-stress financing strictly worsens the verdict; the
  only marginally positive pair (USD_CHF) flips to net negative.
  The breakout direction does not persist over a 6-bar H4 holding
  window; 75.5 % of trades hit the time stop.

### D1 daily trend (CAMPAIGN_006) — blocked, not a strategy verdict

- **Status:** blocked (infrastructure).
- **Evidence:** CAMPAIGN_006 — could not be validly tested. D1 candles
  close at the 17:00 NY rollover; the engine's intraday fill / session /
  spread logic is invalid for them.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** No valid result is possible until the engine gains
  next-bar-open fills and a non-rollover spread reference. This is an
  infrastructure task, not a strategy.

## How a strategy could become approved (it has not)

Approval is a deliberate human action, never a default:

1. A genuinely new, human-approved thesis (not a tweak of a rejected
   campaign).
2. A fresh pre-commit with gates fixed before the run.
3. A campaign that passes every screening gate **and** every test-window
   gate on real OANDA data, earning at most PAPER-TRADE-ONLY.
4. A human edits `configs/approved_strategies.yaml` to add the strategy
   name, with review.
5. Live trading additionally requires every existing config-layer live
   gate (acknowledgement phrase, approved config hash, etc.) and a
   modelled financing cost — none of which is satisfied today.
