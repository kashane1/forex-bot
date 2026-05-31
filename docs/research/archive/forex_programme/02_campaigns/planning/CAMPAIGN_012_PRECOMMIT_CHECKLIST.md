# CAMPAIGN_012 — Pre-Commit Checklist (`regime_switcher_atr_percentile 0.1.0-c012`)

**Branch:** `research-regime-switcher-atr-percentile-001` (scaffold) /
`research-regime-switcher-atr-percentile-walk-forward-001` (future evidence)
**Date:** 2026-05-23 · `strategy_evidence: false`

Binding pre-commit for CAMPAIGN_012 / `regime_switcher_atr_percentile 0.1.0-c012`,
the C3 daily-ATR-percentile regime-switcher real candidate. **This pre-commit
binds the future evidence sprint to a specific gate vector, frozen parameters,
data source, no-lookahead invariants, and null-baseline comparison — all
agreed BEFORE any backtest fires.** Approval requires the full six-evidence
ladder + a deliberate human approval action per
[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 remain
> REJECT. `configs/approved_strategies.yaml` remains `approved: []`.
> Paper / demo / live remain blocked. CAMPAIGN_011 is the **null baseline
> only**, not a trading candidate.

## 1. Hypothesis (frozen, verbatim)

> Trend persistence on H4 OANDA practice majors is regime-conditional.
> CAMPAIGN_002 / 003 demonstrated that unconditional EMA-Donchian momentum
> lost to costs. CAMPAIGN_010 demonstrated that liquidity-flow session
> momentum also lost. CAMPAIGN_011 demonstrated that random entry on the
> same universe + cost model is essentially flat. The C3 hypothesis is
> that a simple regime gate — only trade trend signals when the prior
> completed day's D1AGG ATR-14 is in the top 30 % of the trailing 60
> completed days — turns the cost-drag headwind into a survivable
> tailwind during high-vol periods, while suppressing trades during
> low-vol regimes when costs dominate.

## 2. Implementation files (scaffold sprint deliverables)

| file | purpose |
|---|---|
| `src/forex_bot/strategies/regime_switcher_atr_percentile.py` | `RegimeSwitcherAtrPercentileStrategy` implementing R1-R8 |
| `src/forex_bot/strategies/__init__.py` | re-export `RegimeSwitcherAtrPercentileStrategy` |
| `src/forex_bot/config.py` | `RegimeSwitcherAtrPercentileStrategyConfig` + `StrategyConfig.regime_switcher_atr_percentile` slot + enabled-list check |
| `tests/unit/test_regime_switcher_atr_percentile.py` | 47 deterministic unit tests (config validation, R1-R8, no-lookahead audit, rejected-family contamination, approval regression) |

## 3. Config files

| file | purpose |
|---|---|
| `configs/campaign_012_regime_switcher_atr_percentile.yaml` | research-only loadable YAML; 7-pair H4 universe; frozen parameters; `trading_enabled: false`; `allow_order_submission: false`; `allow_live_trading: false`; `max_positions_per_instrument: 1` |
| `configs/approved_strategies.yaml` | **must remain `approved: []`** — this candidate cannot be added until the full six-evidence ladder + a human approval action are complete |
| `configs/paper.yaml` | **must NOT enable `regime_switcher_atr_percentile`** |
| `configs/practice.yaml` | **must NOT enable `regime_switcher_atr_percentile`** |

## 4. Frozen parameters (binding — runner must assert)

| parameter | value | type | role |
|---|---|---|---|
| `version` | `"0.1.0-c012"` | str | candidate id |
| `timeframe` | `"H4"` | Literal | execution timeframe |
| `atr_lookback` | `14` | int | H4 ATR for stop sizing |
| `atr_stop_multiple` | `2.0` | float | stop = `close[t] ± 2.0 × prior_atr_h4` |
| `max_bars_in_trade` | `6` | int | engine-enforced time stop (≈ 1 trading day) |
| `trailing_stop_atr_multiple` | `null` | None | forbidden in v1; validator rejects non-None |
| `min_atr_pips` | `{}` | dict | per-pair ATR floor; default empty |
| `daily_atr_lookback` | `14` | int | Wilder ATR over D1AGG for regime feature |
| `regime_lookback_days` | `60` | int | trailing percentile window |
| `regime_percentile_threshold` | `0.70` | float | HIGH-VOL gate threshold (P-inclusive) |
| `min_close_move_atr_fraction` | `0.25` | float | trend filter floor (× prior_atr_h4) |
| `trend_lookback_h4_bars` | `4` | int | `close[t]` vs `close[t-4]` |

**Any deviation from any value above constitutes a NEW candidate** that
requires its own discovery + design cycle. The runner / config loader
must reject any deviation.

## 5. No-lookahead checklist (binding — Phase 3 unit tests enforce)

- [x] D1AGG aggregator consumes only completed H4 bars (`completed_only().df`).
- [x] D1AGG bars used are only those tagged `aggregated` (= completed + `rollover_safe`).
- [x] Reference D1AGG ATR is the most recent emitted (`d1_atr_series[-1]`).
- [x] Trailing percentile window is exactly `d1_atr_series[-(regime_lookback_days + 1):-1]` — 60 values strictly preceding the reference; reference is **not** in the window.
- [x] Percentile uses the trailing window only — never global / full-sample / cross-fold.
- [x] HIGH-VOL is inclusive at the threshold (`reference >= P70`).
- [x] H4 ATR uses `iloc[-2]` (bar `t-1`'s ATR; matches CAMPAIGN_010 / 011 convention).
- [x] Bar `t`'s `close` is the only bar-`t` field read (R5/R7); `high` / `low` / `open` / `volume` at bar `t` are never read.
- [x] Strategy module imports nothing from `forex_bot.broker` / `.execution` / `.loops`.
- [x] Strategy module does not import `random` / `numpy.random` / `secrets` / use builtin `hash()`.
- [x] Strategy module does not reference CAMPAIGN_002 / 010 / 011 strategy-specific parameter keys.
- [x] Strategy does not mutate `ctx.config` during signal generation.
- [x] Strategy exposes no approval-shaped public attribute.

## 6. D1AGG completed-day rule (binding)

The regime feature uses the existing
`src/forex_bot/backtesting/d1_aggregation.py` aggregator. A trading day
becomes a D1AGG candle only when:

1. All 6 well-formed H4 candles are present (alignment slots match
   `[(alignment_hour + 4k) % 24 for k in 0..5]` in NY time).
2. The aggregated timestamp clears the NY 16:45–17:15 rollover blackout
   (`rollover_safe()` defensive check).

The strategy ignores `incomplete` / `ambiguous` days. Per the discovery-003
design, this structurally prevents the CAMPAIGN_006 rollover-contamination
bug from re-entering daily-timeframe research.

## 7. Rolling percentile rule (binding)

```python
trailing = d1_atr_series[-(regime_lookback_days + 1) : -1]
assert len(trailing) == regime_lookback_days  # exactly 60
pct_value = numpy.percentile(trailing, regime_percentile_threshold * 100)  # P70
regime = "HIGH_VOL" if reference >= pct_value else "LOW_VOL"
```

The percentile window:

- **Strictly precedes** the reference D1AGG candle (slice `[-(N+1):-1]`).
- Has **exactly** `regime_lookback_days = 60` entries.
- Is **rolling**, not expanding — there is no "first-fold full-history"
  shortcut.
- Is **never cached across runs / folds / pairs** — purely functional;
  recomputed per bar.

## 8. Null-baseline comparison requirement (binding; CAMPAIGN_011-derived)

Per
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
§3 + §8 + §9, the future evidence sprint's verdict doc **must include
a "Null-baseline comparison" section** with explicit margins:

| metric | CAMPAIGN_011 floor | CAMPAIGN_012 must beat to count as "real edge" |
|---|---|---|
| aggregate expectancy R | −0.0024 | by ≥ **+0.0524 R** (→ ≥ 0.05 R) |
| aggregate profit factor | 0.91 | by ≥ **+0.19** (→ ≥ 1.10) |
| aggregate return (4 y) | −0.53 % | meaningfully positive (≥ **+5 %**) |
| `pairs_positive` | 3 / 7 | ≥ **4 / 7** |
| `fold_pass_rate` | 0 / 8 | **100 %** |
| `single_fold_dominance` | 40.1 % | ≤ **60 %** (CAMPAIGN_010 gate) |

"Indistinguishable from null" REJECT band: if CAMPAIGN_012's aggregate
metrics cluster within **± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair** of
CAMPAIGN_011's, the verdict doc must classify the outcome as
**REJECT (indistinguishable from null)**, regardless of which inherited
gates technically pass.

## 9. Evidence-sprint prerequisites

Before the future
`research-regime-switcher-atr-percentile-walk-forward-001` evidence
sprint may begin, the following preconditions must hold:

- [ ] Scaffold sprint (`research-regime-switcher-atr-percentile-001`)
      committed and merged or rebased onto main.
- [ ] `configs/approved_strategies.yaml` still `approved: []`.
- [ ] CAMPAIGN_002 / 010 / 011 verdicts unchanged.
- [ ] 818-pytest baseline preserved (771 prior + 47 new scaffold tests).
- [ ] Strategy module + config + tests all present and passing.
- [ ] Loops refuse; no `live-loop`.
- [ ] No `backtests/CAMPAIGN_012_*` directory yet.

## 10. Walk-forward requirements (inherited from CAMPAIGN_010 / 011)

| field | value |
|---|---|
| `--style` | `rolling` |
| `--parameter-mode` | `frozen` |
| `--train-days` | `540` |
| `--validation-days` | `180` |
| `--test-days` | `180` |
| `--step-days` | `180` |
| `--universe-start` | `2020-01-01` |
| `--universe-end` | `2026-05-20` |
| expected fold count | **8** (matches CAMPAIGN_010 / 011) |
| min fold count gate | **≥ 6** |

### 10.1 Per-fold gates (inherited verbatim)

| level | gate | threshold |
|---|---|---|
| test fold | `expectancy_R_net_of_stress_financing` | ≥ 0.05 R |
| test fold | `profit_factor_net_of_stress_financing` | ≥ 1.10 |
| test fold | `pairs_positive_net_of_stress_financing` | ≥ 4 of 7 |
| test fold | `trade_count` | ≥ 30 |
| test fold | `single_pair_dominance` | ≤ 60 % |

### 10.2 Aggregate gates (inherited verbatim)

| level | gate | threshold |
|---|---|---|
| aggregate | `fold_pass_rate` | 100 % (strict) |
| aggregate | `fold_count` | ≥ 6 |
| aggregate | `expectancy_R_net_of_stress_financing` | ≥ 0.05 R |
| aggregate | `profit_factor_net_of_stress_financing` | ≥ 1.10 |
| aggregate | `pairs_positive` | ≥ 4 of 7 |
| aggregate | `trade_count` | ≥ 200 |
| aggregate | `single_fold_dominance` | ≤ 60 % |
| aggregate | `single_pair_dominance` | ≤ 40 % |
| financing | `conservative_stress_run_does_not_flip_verdict` | PASS |
| financing | `modeled_refused` | PASS |
| financing | `missing_rate_event_count` | 0 |
| null-baseline | meaningful improvement vs CAMPAIGN_011 (§8) | PASS |

## 11. Financing overlay requirements

- **ESTIMATED + `default_stress_rate_source()` (conservative stress) only.**
- **MODELED financing refused at all 4 layers in `src/forex_bot/financing.py`** — no code change permitted.
- Per-rollover cost recorded; pair-flip table required (e.g. USD_CHF / USD_JPY under stress).
- `cashflow_home_stress_total` recorded.
- `conservative_stress_run_does_not_flip_verdict` gate required to pass.
- Expected per-trade cost is similar order of magnitude to CAMPAIGN_010 / 011 (~$0.022–$0.023 per rollover event); the regime gate reduces total trade count, so total financing impact should scale with trade count.

## 12. Portfolio-risk diagnostic requirements

Identical battery to CAMPAIGN_010 / 011:

- Concurrency bounded by `RiskEngine.max_concurrent` cap.
- Per-pair ratio max/min — for a real-edge candidate expected to be
  intermediate between CAMPAIGN_010's 12.0 (highly concentrated) and
  CAMPAIGN_011's 1.65 (uniform).
- Session-of-day distribution diagnostic across 4 UTC buckets (no
  single bucket > 50 % concentration expected — the regime filter is
  daily, not session-of-day).
- Time-stop exit fraction (expected ~75 % matching CAMPAIGN_010 / 011).
- **Regime-period clustering** — informational; trades should cluster
  in HIGH-VOL periods (e.g. central-bank-announcement weeks); the
  diagnostics doc must report which fold's HIGH-VOL periods drove the
  trades.
- 8 / 8 pipeline sanity checks must pass.
- `RiskEngine` `mode='backtest'` rejection rate recorded.

## 13. Independent verifier status

- **Verifier is capability-locked to CAMPAIGN_002** (`trend_following 0.1.0`).
  It cannot validate `regime_switcher_atr_percentile`.
- For a clean **REJECT** verdict on CAMPAIGN_012, the verifier is
  **not required** — REJECT requires no independent corroboration.
- For an unexpected **`RESEARCH_PASS_UNAPPROVED`** verdict, the
  verifier-extension sprint
  **`infra-free-local-parity-verifier-regime-switcher-001`** must run
  **before** any human approval consideration. Item 5 of the
  six-evidence ladder is binding for paper-promotion.

## 14. Explicit no-approval statement

- Even a PASS verdict produces `RESEARCH_PASS_UNAPPROVED`.
- `configs/approved_strategies.yaml` cannot change as part of any
  research sprint (scaffold or evidence). Adding `regime_switcher_atr_percentile`
  to the registry is a deliberate, separate human action per
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).
- A passing CAMPAIGN_012 still has the live-promotion financing blocker
  (MODELED financing required for live; only ESTIMATED + conservative
  stress is currently authorized). Paper is acceptable under ESTIMATED
  with explicit human override per the existing rule.

## 15. Unexpected-PASS protocol (binding for the future evidence sprint)

If the future evidence sprint reports a verdict whose per-fold +
aggregate + financing gates ALL pass AND the null-baseline comparison
margins are met:

1. **Do not silently update STRATEGY_STATUS to `approved`** — that
   would violate this pre-commit.
2. **Do not modify `configs/approved_strategies.yaml`** — that requires
   a separate human approval action.
3. **Write the verdict doc with classification `RESEARCH_PASS_UNAPPROVED`** —
   not `APPROVED`.
4. **Open the suggested verifier-extension follow-up sprint**
   `infra-free-local-parity-verifier-regime-switcher-001` — without
   verifier corroboration, item 5 of the six-evidence ladder is unmet.
5. **Surface for human review** the seven binding artifacts:
   walk-forward result, financing overlay, risk diagnostics, the
   null-baseline comparison section, the data provenance doc, the
   STRATEGY_APPROVAL_PROCESS.md trail, and the verifier readiness.

This is not a recipe to approve. It is a recipe to **escalate cleanly
to human review**.

## 16. Rejection criteria

CAMPAIGN_012's verdict is **REJECT** if any of the following hold:

| level | criterion |
|---|---|
| per-fold | any gate from §10.1 fails on any test fold |
| aggregate | any gate from §10.2 fails |
| financing | conservative-stress overlay flips a passing verdict |
| null-baseline | metrics cluster within ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair of CAMPAIGN_011 (classified `REJECT (indistinguishable from null)`) |
| no-lookahead | any structural-audit unit test fails |
| pipeline | the runner aborts before completion (`BLOCKED`) |

## 17. Infrastructure policy (future precommits — post-2026-05-27)

CAMPAIGN_012 executed before these rules; this checklist is updated as a **template** for future campaigns.

| Requirement | Reference |
|-------------|-----------|
| `fill_timing: next_bar_open` for approval-bound evidence | [`FILL_TIMING_APPROVAL_BOUND_POLICY.md`](FILL_TIMING_APPROVAL_BOUND_POLICY.md) |
| HTF: `htf_align` / `d1agg_htf` or documented exception | [`HTF_ALIGNMENT_POLICY_FOR_FUTURE_STRATEGIES.md`](HTF_ALIGNMENT_POLICY_FOR_FUTURE_STRATEGIES.md) |
| D1AGG (not native OANDA D1) for daily regime gate | §5 no-lookahead; `d1agg_htf` module |
| `research_metadata` block in campaign YAML or manifest entry | `execution_realism.py` |

## 18. Cross-links

- [`REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md)
- [`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md)
- [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
- [`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
