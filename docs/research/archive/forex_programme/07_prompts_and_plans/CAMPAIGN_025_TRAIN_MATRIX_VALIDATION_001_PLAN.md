# CAMPAIGN_025 — train-matrix + selected-champion validation (001) PLAN

**Branch:** `research-campaign-025-m5-donchian-htf-confluence-train-matrix-validation-001`
**Date:** 2026-05-28
**Campaign:** CAMPAIGN_025 · `m5_donchian_htf_confluence_breakout 0.1.0-c025`
**Status entering sprint:** SCAFFOLD_ONLY / NOT_RUN / NOT_APPROVED.

> **This sprint runs evidence (train matrix + one champion validation).** It does
> **not** open the test lockbox, approve any strategy, enable paper/demo/live, tune
> after results, or use validation to select parameters. Maximum attainable status:
> `TRAIN_MATRIX_VALIDATION_PASS_PARITY_REQUIRED / TEST_LOCKBOX_CLOSED / NOT_APPROVED`.

---

## Purpose

Test a **small, pre-committed set of strategy archetypes** inside the C025 family
to determine whether the M5-Donchian-breakout-with-HTF-confluence thesis has any
robust evidence across a few plausible breakout/exit designs — **not** to
brute-force optimal parameters. Exit models (time-only, fixed 2R/3R, breakeven+ATR
trail, Donchian channel exit) are treated as **first-class strategy hypotheses**,
not tuning knobs.

## Source scaffold docs (authoritative)

- `docs/research/CAMPAIGN_025_PRECOMMIT_M5_DONCHIAN_HTF_CONFLUENCE_SCOPE.md`
- `docs/research/CAMPAIGN_025_M5_DONCHIAN_HTF_CONFLUENCE_SCAFFOLD_001_PLAN.md`
- `docs/research/CAMPAIGN_025_M5_DONCHIAN_HTF_CONFLUENCE_SCAFFOLD_001_SUMMARY.md`
- `docs/research/CAMPAIGN_025_BACKTRADER_PARITY_DESIGN.md`
- `docs/research/CAMPAIGN_025_DISTINCTNESS_AND_PRIOR_LESSONS_MEMO.md`
- `configs/campaign_025_m5_donchian_htf_confluence_breakout.yaml`
- `src/forex_bot/strategies/m5_donchian_htf_confluence_breakout.py`
- `scripts/run_campaign_025_m5_donchian_htf_confluence.py`
- `src/forex_bot/research/campaign_025_loader.py`, `campaign_025_gates.py`

## Why a small archetype matrix, not unrestricted optimization

A purposeful matrix of **≤ 24** candidates (target 16–20), each a *coherent
trading idea* (a baseline, scalps, balanced continuations, trend runners,
compression breakouts, channel followers), sampled from the pre-committed
parameter dimensions. This is **not** a Cartesian sweep (3×3×5×3×2×3 = 810
combos), not genetic search, not validation-set mining. The point is robustness
across designs, not the single best knob setting.

## Exact no-validation-selection rule

The complete candidate matrix is frozen **before** any evidence (Phase 2). The
**entire** matrix runs on the **train window only**. Champion selection uses a
**train-only** filter + ranking rule. Validation runs **once**, on the **single**
train-selected champion only. Validation metrics may **never** influence which
candidate or parameters are chosen. Non-selected candidates are **never** run on
validation.

## Exact no-tuning rule

No candidate definition, parameter value, gate threshold, selection rule, or split
boundary may be changed after seeing train or validation results. If the train
matrix is weak/sparse/unstable/over-concentrated, **select no champion** — there is
no "rescue" path.

## Exact no-test-lockbox rule

The test window (2025-01-01 → 2026-05-20) stays **closed**. The runner refuses to
run it (`--fail-if-test-window` default true). No promotion, no approval.

## Data coverage warning & proposed split handling

Materialized M5/M15/H1/H4M1 begin ~**2021-05-26**; the binding constraint is
**USD_CHF H4M1 from 2021-06-17**. The pre-committed scaffold splits (train
2020–2022) therefore have **missing M5 coverage** and cannot be used verbatim.

**Proposed narrowed split (finalized & justified in Phase 1):**
- **Train:** 2021-07-01 → 2023-06-30 (after all-pair H4M1 warmup).
- **Validation:** 2023-07-01 → 2024-12-31 (strictly after train).
- **Test (LOCKED, NOT run):** 2025-01-01 → 2026-05-20 (unchanged from precommit).

Chronological order preserved; validation strictly after train; test untouched.
If Phase 1 finds coverage too short/uneven, classify `BLOCKED_DATA_COVERAGE`
instead of forcing evidence.

## Matrix candidate plan

Parameter dimensions (frozen, from the sprint brief):
- **A** M5 Donchian length: 12 / 20 / 30
- **B** initial stop: farther of {1.5, 2.0, 2.5}× M5 ATR(14) and the opposite
  prior Donchian channel side
- **C** exit model: `time_stop_only`, `fixed_2r_target`, `fixed_3r_target`,
  `breakeven_then_atr_trail`, `donchian_channel_exit`
- **D** time stop: 36 / 48 / 72 M5 bars
- **E** H1 trend mode: `standard` / `strict`
- **F** M15 setup mode: `pullback_or_compression` / `pullback_only` / `compression_only`

16 coherent archetypes (IDs `C025_MTX_001`…), deduplicated by exact signature,
each ≤ the allowed sets. Full table frozen in `CAMPAIGN_025_TRAIN_MATRIX_SPEC.md`
and `research/campaign_025/train_matrix/candidate_registry.json`.

## Exit-model candidate plan (frozen before run)

- **Fixed target:** R from initial stop distance; long target = entry +
  R·risk_dist; short = entry − R·risk_dist.
- **Breakeven:** activation on **intrabar** M5 high/low crossing +1.0R (conservative);
  stop → entry. After +1.5R, trail by 1.5× M5 ATR(14) on **completed** bars.
- **ATR trail:** long stop = max(existing, close − 1.5·ATR); short = min(existing,
  close + 1.5·ATR); completed bars only.
- **Donchian channel exit:** exit when a **completed** M5 close crosses the *prior*
  opposite Donchian channel; fill at next bar open (conservative).
- **Exit priority:** hard stop → fixed target → breakeven/trail → channel exit →
  time stop → end-of-data. **Same-bar stop+target ambiguity resolves adverse-first.**

## Candidate selection rule (train only)

Filter: train trades ≥ 100 aggregate (else `MATRIX_TOO_SPARSE`); expectancy ≥ 0;
PF ≥ 1.03; ≥ 3/7 pairs non-negative; 2× cost-stress expectancy ≥ −0.005R;
spread/ATR not structurally hostile; no single pair > 50% of total positive R
(else `SINGLE_PAIR_REVIEW_ONLY`); profits not dependent on ambiguous same-bar
target/stop. Rank by: cost-stress-adjusted expectancy → non-negative pair count →
lower single-pair concentration → stability proxy → PF → lower turnover → simpler
candidate. Select **at most one** champion; if none pass, select none.

## Validation rule

Run **once** on the champion only. Gates: validation expectancy > 0; PF ≥ 1.05;
trades ≥ 100; ≥ 4/7 pairs non-negative; 2× cost-stress expectancy ≥ 0; beat C011
null by +0.010R; holding period + spread/ATR documented; exit distribution
documented; Backtrader parity required before any promotion-review; lockbox closed.

## Safety invariants

- `configs/approved_strategies.yaml` stays `approved: []`; paper/demo/live blocked.
- No broker/executor/OANDA-mutation changes; no live env/credentials.
- `next_bar_open` only; no `signal_bar_close`; no same-bar entry; HTF from last
  completed bar only; no lookahead.
- No bulky/raw-candle/credential/.env/DB artifacts committed (compact JSON/CSV only).

## Evidence artifacts

Under `research/campaign_025/train_matrix/` (and `…/validation/`): candidate
registry, run manifest, per-candidate metrics/gate-filters/pair/side/exit-reason/
cost-stress/holding/spread-atr/signal-funnel/C011-comparison tables, candidate
selection JSON, blocked/warning conditions. Docs: this plan, coverage/split
decision, matrix spec, train-matrix result, champion validation result,
interpretation, parity readiness, summary.

## Validation commands

```
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
python scripts/run_campaign_025_m5_donchian_htf_confluence.py --preflight-only
python scripts/run_campaign_025_m5_donchian_htf_confluence.py --data-feature-preflight
```

## Blocked conditions

- `BLOCKED_DATA_COVERAGE` — available M5 history too short/uneven for a valid split.
- `BLOCKED_MATRIX_TOO_SPARSE` — no candidate reaches 100 train trades.
- `REJECT_MATRIX_NO_TRAIN_CANDIDATE` — candidates run but none pass train filters.
- `TRAIN_MATRIX_VALIDATION_REJECT` — champion fails validation gates.
- `SINGLE_PAIR_REVIEW_ONLY` — one pair strong but aggregate fails.

## Phase 0 baseline audit result

Branch created off the completed C025 scaffold. `approved_strategies.yaml` =
`approved: []`. Remaining `C024` references are historical (C022/C023 family) or
rename-history notes. No broker/executor/OANDA files changed. Guards: research
freeze **PASS**, research archive **PASS**, secret scan **PASS**, preflight
**ok=True**. Coverage queried (see Phase 1). Baseline `pytest tests/ -q` run.
