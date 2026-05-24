# Regime-Switcher ATR-Percentile — Scaffold Readiness

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-001`
`strategy_evidence: false`

One-page scaffold-readiness summary for **CAMPAIGN_012 /
`regime_switcher_atr_percentile 0.1.0-c012`**. The scaffold is GREEN
across all dimensions below; the future evidence sprint can begin
once a human authorizes it. **This document is not strategy evidence.
A passing scaffold is not edge.**

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
> remain REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked. CAMPAIGN_011 is
> the **null baseline only**, not a trading candidate.

## 1. Scaffold readiness (GREEN across all dimensions)

| dimension | status | detail |
|---|:---:|---|
| strategy module | ✓ | `src/forex_bot/strategies/regime_switcher_atr_percentile.py` implements R1-R8 per binding spec |
| strategy registered | ✓ | `RegimeSwitcherAtrPercentileStrategy` exported from `src/forex_bot/strategies/__init__.py` |
| config schema | ✓ | `RegimeSwitcherAtrPercentileStrategyConfig` (Pydantic v2, `extra="forbid"`) + `StrategyConfig.regime_switcher_atr_percentile` slot + enabled-list check in `src/forex_bot/config.py` |
| frozen-parameter pre-commit | ✓ | all 12 parameters from [`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md) §2 bound by validator |
| candidate YAML | ✓ | `configs/campaign_012_regime_switcher_atr_percentile.yaml` (7-pair H4 universe; `trading_enabled: false`) |
| unit tests | ✓ | 47 deterministic tests in `tests/unit/test_regime_switcher_atr_percentile.py` covering config validation, R1-R8, no-lookahead audit, rejected-family contamination, approval regression |
| no-lookahead audit | ✓ | structural source-grep tests pass: no bar-`t` reads of `high` / `low` / `open` / `volume`; reference is most recent emitted D1AGG; trailing slice exactly `[-(N+1):-1]`; close-`t` read only in R5/R7 |
| no PRNG / no broker | ✓ | source-grep tests pass: no `random` / `numpy.random` / `secrets` / builtin `hash()`; no `forex_bot.broker` / `.execution` / `.loops` imports |
| no rejected-family contamination | ✓ | source-grep tests pass: no CAMPAIGN_002 / 010 / 011 strategy-specific parameter keys |
| approval regression | ✓ | `configs/approved_strategies.yaml` unchanged at `approved: []`; not enabled in `paper.yaml` / `practice.yaml`; no approval-shaped public attribute |
| D1AGG usage | ✓ | uses existing `aggregate_h4_to_d1` from `src/forex_bot/backtesting/d1_aggregation.py`; only `aggregated` (= completed + `rollover_safe`) days consumed |
| pre-commit checklist | ✓ | [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md) committed |
| repo-wide pytest | ✓ | 818 passing (771 baseline + 47 new) |
| repo-wide ruff | ✓ | 3 pre-existing in `research/lean_parity/algorithms/` (untouched); no new findings |
| validate_research_archive | ✓ | ALL CHECKS PASSED |
| check_research_freeze | ✓ | ALL CHECKS PASSED (loops refuse; no credentials) |
| scan_artifacts_for_secrets | ✓ | PASSED |
| paper-loop / demo-loop | ✓ | both refuse (`approved_strategies.yaml` empty) |
| `live-loop` command | ✓ | does not exist |

## 2. Future evidence branch identity

| field | value |
|---|---|
| name | `research-regime-switcher-atr-percentile-walk-forward-001` |
| relation | mirrors `research-asian-london-session-breakout-walk-forward-001` (CAMPAIGN_010 evidence) and `research-random-entry-diagnostic-anchor-walk-forward-001` (CAMPAIGN_011 evidence) exactly |
| spec | [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md) (binding from discovery-003) |
| readiness docs | [`CAMPAIGN_012_WALK_FORWARD_READINESS.md`](CAMPAIGN_012_WALK_FORWARD_READINESS.md), [`CAMPAIGN_012_FINANCING_RISK_READINESS.md`](CAMPAIGN_012_FINANCING_RISK_READINESS.md), [`CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md) (Phase 6) |

## 3. Data expectations

| dimension | value |
|---|---|
| source | `data/campaign_002.sqlite3` (gitignored symlink) — same physical store as CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011; provenance hashes already recorded |
| universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD (7 pairs; H4 OANDA practice) |
| span | 2020-01-01 → 2026-05-19 inclusive |
| new fetch needed | **no** |
| new credentials | **no** |
| D1AGG aggregator | already exists; no edit needed |

## 4. Known limitations

- **Verifier capability lock.** The independent verifier
  (item 5 of the six-evidence ladder) is capability-locked to
  CAMPAIGN_002 / `trend_following`; it cannot validate
  `regime_switcher_atr_percentile`. The verifier extension
  `infra-free-local-parity-verifier-regime-switcher-001` is **only
  required** if CAMPAIGN_012's evidence verdict is
  `RESEARCH_PASS_UNAPPROVED`. A clean REJECT does not need it.
- **MODELED financing.** Live promotion requires MODELED financing,
  which is refused at 4 layers in `src/forex_bot/financing.py`. Even
  a passing CAMPAIGN_012 retains the live-promotion financing blocker
  unless the separately-authorized credentialed pilot
  `research-financing-modeled-capture-credentialed-001` runs. Paper
  promotion is acceptable under ESTIMATED with explicit human
  override per the existing rule.
- **DST in synthetic test fixtures.** The Phase 3 test fixtures use
  fixed UTC slot hours that match the D1AGG aggregator's NY-EST
  expected slots. The fixtures start at 2024-11-04 22:00 UTC (after
  DST 2024 ends) and stay within ≤ 95 days (well before DST 2025
  starts on 2025-03-09). The real OANDA H4 store handles DST per
  OANDA's convention; the strategy's bar timestamps are already
  validated by the aggregator. This is a test-fixture choice, not a
  strategy limitation.

## 5. D1AGG usage

The strategy uses the existing
`src/forex_bot/backtesting/d1_aggregation.py` aggregator unchanged:

```python
from forex_bot.backtesting.d1_aggregation import aggregate_h4_to_d1

# In RegimeSwitcherAtrPercentileStrategy.generate_signal:
h4_candles = _df_to_completed_h4_candle_list(df, ctx.instrument.name)
agg = aggregate_h4_to_d1(h4_candles, instrument=ctx.instrument.name)
d1_candles = agg.candles  # only `aggregated` (= completed + rollover_safe) days
```

- The aggregator's `aggregated` contract guarantees each emitted candle
  represents a fully closed trading day with all 6 well-formed H4 bars,
  whose timestamp clears the NY 16:45–17:15 rollover blackout.
- The strategy never asks the aggregator for the current incomplete
  trading day.
- D1AGG bars feed a Wilder ATR-14 (`_wilder_atr_over_d1agg`); the most
  recent emitted ATR is the reference; the trailing 60 values strictly
  preceding the reference form the percentile window.

This structurally prevents the CAMPAIGN_006 rollover-contamination bug
from re-entering daily-timeframe research.

## 6. Null-baseline comparison

The future evidence sprint **must** compare CAMPAIGN_012's per-fold +
aggregate metrics to CAMPAIGN_011's null-baseline floor (verbatim from
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)):

| metric | CAMPAIGN_011 floor | CAMPAIGN_012 must beat |
|---|---|---|
| aggregate expectancy R | −0.0024 | by ≥ **+0.0524** (→ ≥ 0.05) |
| aggregate profit factor | 0.91 | by ≥ **+0.19** (→ ≥ 1.10) |
| aggregate return (4 y) | −0.53 % | meaningfully positive (≥ **+5 %**) |
| `pairs_positive` | 3 / 7 | ≥ **4 / 7** |
| `fold_pass_rate` | 0 / 8 | **100 %** |
| `single_fold_dominance` | 40.1 % | ≤ **60 %** |

"Indistinguishable from null" REJECT band (within
± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair of CAMPAIGN_011): the verdict
doc must classify it as **REJECT (indistinguishable from null)**,
regardless of which inherited gates technically pass.

## 7. Why this is a real candidate (but not approved)

The C3 regime switcher is a **real-edge candidate** in the sense that:

- It has a directional hypothesis (regime-conditional trend continuation).
- It is fully deterministic from price (no PRNG; no `master_seed`).
- It is structurally distinct from every prior rejected family (≥ 5/6
  distinctness vs each of CAMPAIGN_002 / 010 / 011).
- The H4 → D1AGG aggregator unblocks a daily-timeframe regime feature
  that CAMPAIGN_006 could not validly test.

But **the candidate is not approved**:

- No backtest has run; no walk-forward; no financing overlay; no risk
  diagnostics; no verifier corroboration.
- A passing scaffold is **not** evidence of edge — that is the entire
  point of the
  [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
  null-baseline gate.
- Approval requires the full six-evidence ladder + a deliberate human
  approval action per
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

## 8. Pre-flight checklist for the future evidence sprint

- [ ] Scaffold sprint committed and merged or rebased onto main.
- [ ] `configs/approved_strategies.yaml` still `approved: []`.
- [ ] CAMPAIGN_002 / 010 / 011 verdicts unchanged.
- [ ] 818-pytest baseline preserved.
- [ ] `configs/campaign_012_regime_switcher_atr_percentile.yaml` loads
      cleanly via `load_settings()`.
- [ ] `RegimeSwitcherAtrPercentileStrategy` instantiates and the import
      smoke runs.
- [ ] Loops refuse; no `live-loop`.
- [ ] No `backtests/CAMPAIGN_012_*` artifact directory yet.
- [ ] Verifier capability gap acknowledged; verifier-extension
      `infra-free-local-parity-verifier-regime-switcher-001` is a
      separately-authorized future sprint required only on
      `RESEARCH_PASS_UNAPPROVED`.
- [ ] MODELED financing blocker acknowledged; CAMPAIGN_012's overlay
      will use ESTIMATED + conservative stress only.

## 9. Cross-links

- [`REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md)
- [`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_012_STATUS.md`](CAMPAIGN_012_STATUS.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
