# `research-regime-switcher-atr-percentile-walk-forward-001` — Sprint Plan (Phase 0)

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-walk-forward-001`
(worktree branch `claude/affectionate-fermi-d950fc`) · `strategy_evidence: false`

Phase 0 repo truth audit + 10-phase evidence-sprint plan for
**CAMPAIGN_012 / `regime_switcher_atr_percentile 0.1.0-c012`**, the C3
daily-ATR-percentile regime-switcher candidate. **Evidence sprint —
runs walk-forward + financing overlay + risk diagnostics + verifier
assessment.** Even a clean PASS produces `RESEARCH_PASS_UNAPPROVED`.

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
> remain REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked. **CAMPAIGN_011
> is the null baseline only, not a trading candidate.** This sprint
> **cannot approve any strategy**; even a clean walk-forward PASS
> produces `RESEARCH_PASS_UNAPPROVED` pending the verifier extension
> + a deliberate human approval action per
> [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

## 1. Branch / base commit / repo state

| dimension | value |
|---|---|
| git branch (worktree) | `claude/affectionate-fermi-d950fc` |
| logical sprint branch | `research-regime-switcher-atr-percentile-walk-forward-001` |
| base commit (HEAD before Phase 0) | `e7a0d87` — Phase 7 of `research-regime-switcher-atr-percentile-001` (scaffold sprint close) |
| working tree at Phase 0 start | clean (`git status --short` empty) |

## 2. Repo truth summary (verified)

| dimension | value |
|---|---|
| pytest count (baseline) | **818 passed** in 3.47 s |
| ruff status (baseline) | **3 pre-existing** in `research/lean_parity/algorithms/` (`2× RUF100` unused-noqa + `1× I001` unsorted-imports); untouched LEAN-parity archive; out of scope |
| `validate_research_archive.py` | ALL CHECKS PASSED (11 campaigns; 14 diagnostic artifacts; 205 evidence-index links resolve; 2,311 committed artifact files clean) |
| `check_research_freeze.py` | ALL CHECKS PASSED (loops refuse; no credentials) |
| `scan_artifacts_for_secrets.py` | PASSED |
| `paper-loop -c configs/paper.yaml` | **refused** — `trend_following` not approved |
| `demo-loop -c configs/practice.yaml` | **refused** — `trend_following` not approved |
| `forex_bot.cli --help` | **no `live-loop` command** present |
| `configs/approved_strategies.yaml` | `approved: []` (verified verbatim) |

## 3. CAMPAIGN_012 scaffold status (verified)

| artifact | status |
|---|---|
| `src/forex_bot/strategies/regime_switcher_atr_percentile.py` | **present** (Phase 2 of scaffold sprint) |
| `RegimeSwitcherAtrPercentileStrategyConfig` in `src/forex_bot/config.py` | **present** |
| `StrategyConfig.regime_switcher_atr_percentile` slot + enabled-list check | **present** |
| `tests/unit/test_regime_switcher_atr_percentile.py` | **present** (47 tests, all passing) |
| `configs/campaign_012_regime_switcher_atr_percentile.yaml` | **present**; loads cleanly via `load_settings()` |
| `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_*` (5 docs) | **all present** |
| `docs/research/CAMPAIGN_012_*` (5 docs) | **all present** |
| `backtests/CAMPAIGN_012_*/` directory | **does NOT exist yet** — this evidence sprint creates it |

## 4. Local data status (verified)

| dimension | value |
|---|---|
| symlink | `data/campaign_002.sqlite3` → `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` |
| target file size | 112 MB (gitignored at `*.sqlite3`) |
| tables | `candles`, `instruments`, `data_sources`, `observed_financing_events`, + others |
| H4 coverage | **all 7 pairs present** (EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD) |
| H4 candle counts | EUR_USD 9931, GBP_USD 9931, USD_JPY 9932, AUD_USD 9931, USD_CAD 9931, USD_CHF 9931, NZD_USD 9935 |
| span | **2020-01-01T22:00:00+00:00 → 2026-05-19T21:00:00+00:00** (matches CAMPAIGN_010 / 011) |
| data source label | `oanda-practice` (runner-enforced) |
| **regeneration needed?** | **NO** — local data covers the exact universe + span required |
| committed bulky data | **none** (`*.sqlite3` gitignored; symlink target outside repo) |

## 5. Frozen parameters (verified from `configs/campaign_012_regime_switcher_atr_percentile.yaml`)

| parameter | value | source |
|---|---|---|
| `version` | `0.1.0-c012` | config + Pydantic schema |
| `timeframe` | `H4` | config |
| `atr_lookback` | `14` | config |
| `atr_stop_multiple` | `2.0` | config |
| `trailing_stop_atr_multiple` | `null` (validator rejects non-None) | config |
| `max_bars_in_trade` | `6` | config |
| `min_atr_pips` | `{}` | config |
| `daily_atr_lookback` | `14` | config |
| `regime_lookback_days` | `60` | config |
| `regime_percentile_threshold` | `0.70` | config |
| `min_close_move_atr_fraction` | `0.25` | config |
| `trend_lookback_h4_bars` | `4` | config |
| `warmup_bars_required()` | `500` | strategy class |

**Universe (frozen):** 7 pairs — EUR_USD, GBP_USD, USD_JPY, AUD_USD,
USD_CAD, USD_CHF, NZD_USD (matches CAMPAIGN_010 / 011 verbatim).

**Risk settings (frozen):** `risk.max_open_positions = 1`,
`risk.max_positions_per_instrument = 1`, `risk.risk_per_trade_pct = 0.25`.

## 6. Safety state (verified)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | REJECT/null-model anchor (untouched) |
| CAMPAIGN_012 | scaffold only; no evidence verdict yet; this sprint will produce the verdict |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | **no** (4 refusal layers; not lifted by this sprint) |
| live-promotion financing blocker | stands |

## 7. Files inspected (Phase 0 audit)

- `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md`
- `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`
- `docs/research/CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`
- `docs/research/CAMPAIGN_012_STATUS.md`
- `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_READINESS.md`
- `docs/research/CAMPAIGN_012_SMOKE_RESULT.md`
- `docs/research/CAMPAIGN_012_WALK_FORWARD_READINESS.md`
- `docs/research/CAMPAIGN_012_FINANCING_RISK_READINESS.md`
- `docs/research/CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md`
- `docs/research/CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`
- `docs/research/NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`
- `src/forex_bot/strategies/regime_switcher_atr_percentile.py`
- `src/forex_bot/backtesting/d1_aggregation.py`
- `src/forex_bot/config.py` (RegimeSwitcherAtrPercentileStrategyConfig)
- `tests/unit/test_regime_switcher_atr_percentile.py` (47 tests, all green)
- `configs/campaign_012_regime_switcher_atr_percentile.yaml`
- `scripts/run_campaign_011.py` (template for `run_campaign_012.py`)
- `scripts/build_campaign_011_financing_overlay.py` (template)
- `scripts/build_campaign_011_risk_diagnostics.py` (template)
- `scripts/run_walk_forward_dry_run.py` (Phase 2 plan generator)
- `research/walk_forward/__init__.py` (harness API)
- `research/financing/__init__.py` (financing API)

## 8. Evidence pipeline phases

| phase | output | binding rule |
|---|---|---|
| 0 | this plan doc | repo truth + safety state |
| 1 | `docs/research/CAMPAIGN_012_DATA_PROVENANCE.md` | data hashes; same physical store as CAMPAIGN_010 / 011 |
| 2 | `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/plan.{json,md}` + `docs/research/CAMPAIGN_012_WALK_FORWARD_PLAN.md` | 8 folds rolling/frozen, inherited from CAMPAIGN_010 / 011 |
| 3 | `scripts/run_campaign_012.py` | mirrors `run_campaign_011.py`; frozen-parameter assertion before any backtest fires |
| 4 | per-fold-per-pair `summary.json` + `trades.csv`; `walk_forward/results.{json,md}` + `walk_forward/fold_detail.json`; `docs/research/CAMPAIGN_012_WALK_FORWARD_EXECUTION.md` | 8 folds × 7 pairs = 56 backtests; honest execution |
| 5 | `docs/research/CAMPAIGN_012_WALK_FORWARD_RESULT.md` | verdict classification: REJECT / REJECT_INDISTINGUISHABLE_FROM_NULL / RESEARCH_PASS_UNAPPROVED / BLOCKED; null-baseline comparison gate |
| 6 | `scripts/build_campaign_012_financing_overlay.py` + `backtests/.../financing/*.{json,md}` + `docs/research/CAMPAIGN_012_FINANCING_OVERLAY.md` | ESTIMATED + conservative stress; MODELED refused |
| 7 | `scripts/build_campaign_012_risk_diagnostics.py` + `backtests/.../risk/*.{json,md}` + `docs/research/CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md` | regime-period clustering signature |
| 8 | `docs/research/CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md` | verifier capability lock; not required for REJECT |
| 9 | `docs/research/CAMPAIGN_012_EVIDENCE_SUMMARY.md` + `docs/research/CAMPAIGN_012_STATUS.md` (updated) + `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md` + `docs/research/EVIDENCE_INDEX.md` (updated) + `docs/research/EVIDENCE_MANIFEST.json` (updated if convention requires) + `docs/research/STRATEGY_STATUS.md` (updated) | final validation; safety-state preservation |

## 9. Expected commands

### Phase 2 — plan generation
```bash
python scripts/run_walk_forward_dry_run.py \
  --campaign-name CAMPAIGN_012_regime_switcher_atr_percentile \
  --style rolling --parameter-mode frozen \
  --train-days 540 --validation-days 180 --test-days 180 --step-days 180 \
  --universe-start 2020-01-01 --universe-end 2026-05-20 \
  --output backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward
```

### Phase 4 — per-fold execution
```bash
python scripts/run_campaign_012.py \
  --config configs/campaign_012_regime_switcher_atr_percentile.yaml \
  --plan backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/plan.json \
  --out backtests/CAMPAIGN_012_regime_switcher_atr_percentile
```

### Phase 6 — financing overlay
```bash
python scripts/build_campaign_012_financing_overlay.py \
  --folds-dir backtests/CAMPAIGN_012_regime_switcher_atr_percentile/folds \
  --out-dir backtests/CAMPAIGN_012_regime_switcher_atr_percentile/financing
```

### Phase 7 — risk diagnostics
```bash
python scripts/build_campaign_012_risk_diagnostics.py \
  --folds-dir backtests/CAMPAIGN_012_regime_switcher_atr_percentile/folds \
  --walk-forward-dir backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward \
  --out-dir backtests/CAMPAIGN_012_regime_switcher_atr_percentile/risk
```

## 10. Validation plan (per phase + at sprint close)

```bash
python -m pytest -q
ruff check src tests scripts research
python scripts/validate_research_archive.py
python scripts/check_research_freeze.py
python scripts/scan_artifacts_for_secrets.py
python -m forex_bot.cli paper-loop -c configs/paper.yaml      # expect refusal
python -m forex_bot.cli demo-loop -c configs/practice.yaml    # expect refusal
python -m forex_bot.cli --help                                 # expect no live-loop
git status --short
```

Test-count target: **818 baseline → maintained or grown** (any runner-test
additions in Phase 3 must not regress old tests).

## 11. Non-goals (binding)

- **Do not approve any strategy.** Even a clean walk-forward PASS produces `RESEARCH_PASS_UNAPPROVED`.
- **Do not modify `configs/approved_strategies.yaml`.**
- **Do not enable** `regime_switcher_atr_percentile` in `configs/paper.yaml` or `configs/practice.yaml`.
- **Do not run paper-loop or demo-loop** except for the standing refusal check.
- **Do not create or invoke a `live-loop` command.**
- **Do not submit / create / modify / cancel / close / query any broker order.**
- **Do not query account orders / trades / positions / account snapshots / transaction streams.**
- **Do not use QuantConnect / LEAN.** No `lean` commands.
- **Do not tune CAMPAIGN_012 parameters** based on intermediate results.
- **Do not weaken null-baseline comparison gates** after seeing results.
- **Do not change any historical campaign verdict** (CAMPAIGN_002 / 010 / 011 all stay REJECT).
- **Do not present a trading recommendation.**
- **Do not commit bulky data** (`*.sqlite3` already gitignored; financial CSVs per-fold-per-pair are committed at the same pattern as CAMPAIGN_010 / 011 — small files only).
- **Do not use live broker credentials** or demo/practice order execution.

## 12. Safety invariants (binding)

- `configs/approved_strategies.yaml` must read `approved: []` at every phase boundary.
- CAMPAIGN_002 / 010 / 011 verdicts unchanged at every phase boundary.
- MODELED financing remains refused at all 4 layers.
- Loops continue to refuse; no `live-loop` command appears.
- No broker call at any phase.
- No `.env` read; no credential printed.
- No account/order/trade/position/transaction endpoint queried.
- Frozen parameters unchanged across all 10 phases.

## 13. Explicit safety statements

1. **This sprint cannot approve any strategy.** Even RESEARCH_PASS_UNAPPROVED is not approval; approval is a separate human action per [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).
2. **A research pass remains unapproved.** The verdict options are REJECT / REJECT_INDISTINGUISHABLE_FROM_NULL / RESEARCH_PASS_UNAPPROVED / BLOCKED. No phase or combination of phases can produce APPROVED.
3. **CAMPAIGN_011 is only the null baseline, not a trading candidate.** This sprint compares CAMPAIGN_012's metrics to CAMPAIGN_011's verbatim floor (aggregate expectancy −0.0024 R, PF 0.91, return −0.53 %, pairs_positive 3/7, fold_pass_rate 0/8); it does not revive CAMPAIGN_011 as a tradable strategy. CAMPAIGN_011 is structurally impossible to approve (null model by design).

## 14. Cross-links

- [`REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md) (scaffold-sprint summary)
- [`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md) (binding gate vector)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null-baseline comparison)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md) (sibling reference)
- [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md) (sibling reference)
- [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md) (binding sprint spec)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
