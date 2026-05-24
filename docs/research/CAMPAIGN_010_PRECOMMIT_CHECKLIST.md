# CAMPAIGN_010 — Pre-Commit Checklist

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-001`
`strategy_evidence: false`

Pre-commit / evaluation checklist for the **CAMPAIGN_010 research
candidate** (`session_breakout 0.1.0-c010`). This document is the
gate any future evaluation sprint must satisfy before treating
its outputs as evidence. **Loading this checklist, the config
YAML, or running the strategy in unit/smoke mode does not
approve the candidate.**

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked. CAMPAIGN_010 is candidate
> scaffold only — no campaign verdict, no backtest evidence, no
> trading recommendation, and the six-evidence ladder remains
> open per
> [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
> §8.

## 1. Candidate identity

| field | value |
|---|---|
| campaign label | `CAMPAIGN_010` |
| strategy name | `session_breakout` |
| version | `0.1.0-c010` |
| sprint that scaffolded | `research-asian-london-session-breakout-001` |
| design source | [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md) |
| implementation spec | [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md) |

## 2. Candidate hypothesis (verbatim, frozen)

Cited verbatim from the design's §2 so the future evaluation
sprint inherits it unchanged:

> The H4 bar covering the first London session (roughly
> 07:00–11:00 UTC) is preceded by a low-liquidity Asian-session
> H4 bar. If the Asian-session H4 bar establishes a clean range
> AND the London-session H4 bar's close penetrates that range in
> one direction, the directional move tends to *continue*
> through the London/NY-overlap H4 bar.
>
> The edge — if any — comes from the liquidity-flow event of the
> London open, not from trend, not from compression, not from
> pullback, and not from mean-reversion. A frozen-parameter,
> walk-forward evaluation with strict pass-rate gates on the
> seven CAMPAIGN_002 H4 pairs will either confirm a small
> positive expectancy *net of conservative-stress financing*, or
> REJECT the candidate.

## 3. Implementation files (committed by this sprint)

| file | role |
|---|---|
| [`src/forex_bot/strategies/session_breakout.py`](../../src/forex_bot/strategies/session_breakout.py) | strategy module implementing the `Strategy` protocol; emits `Signal | None` per H4 bar; no broker imports; no engine edits |
| [`src/forex_bot/strategies/__init__.py`](../../src/forex_bot/strategies/__init__.py) | re-export `SessionBreakoutStrategy` |
| [`src/forex_bot/config.py`](../../src/forex_bot/config.py) | new `SessionBreakoutStrategyConfig` sub-model + `StrategyConfig.session_breakout` slot + `@model_validator` rejecting invalid session hours |
| [`tests/unit/test_session_breakout.py`](../../tests/unit/test_session_breakout.py) | 33 unit + structural-audit cases (Phase 3) |

## 4. Config files (committed by this sprint)

| file | role |
|---|---|
| [`configs/campaign_010_session_breakout.yaml`](../../configs/campaign_010_session_breakout.yaml) | research candidate config; loads via `load_settings(...)`; `app.trading_enabled=false`, `app.allow_order_submission=false`, `app.allow_live_trading=false`; 7-pair H4 universe; data reused from `data/campaign_002.sqlite3` |
| **NOT TOUCHED** [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml) | remains `approved: []`; the candidate is **deliberately absent** from this registry |

## 5. Frozen parameters (verbatim from the design)

| parameter | value |
|---|---|
| `version` | `0.1.0-c010` |
| `timeframe` | `H4` |
| `atr_lookback` | `14` |
| `atr_stop_multiple` | `2.0` |
| `trailing_stop_atr_multiple` | `null` (none in v1) |
| `max_bars_in_trade` | `6` (= design's `time_stop_bars`; see implementation-spec §4.1) |
| `min_atr_pips` | `{}` |
| `asian_session_hours_utc_start` | `22` |
| `asian_session_hours_utc_end` | `6` |
| `london_session_hours_utc_start` | `6` |
| `london_session_hours_utc_end` | `12` |
| `min_asian_range_atr_fraction` | `0.30` |
| `risk.risk_per_trade_pct` | `0.25` |
| `risk.max_positions_per_instrument` | `1` |

**Any change to any of these parameters constitutes a NEW
candidate** that requires its own discovery + evaluation cycle.

## 6. Required local-only evaluation commands (Phase 5 smoke + future evidence sprints)

### 6.1 Phase 5 (this sprint) smoke commands — credential-free, no broker call

```bash
# Pytest the candidate's full unit suite.
.venv/bin/python -m pytest tests/unit/test_session_breakout.py -q

# Config-load smoke (instantiate Settings from the YAML; no broker call).
.venv/bin/python -c "from forex_bot.config import load_settings; \
    s = load_settings('configs/campaign_010_session_breakout.yaml'); \
    print('loaded:', s.strategy.enabled, 'session_breakout?',
          s.strategy.session_breakout is not None)"
```

The full smoke result is recorded in
[`CAMPAIGN_010_SMOKE_RESULT.md`](CAMPAIGN_010_SMOKE_RESULT.md).

### 6.2 Future evidence sprint commands (NOT run by this sprint)

A separate future
`research-asian-london-session-breakout-walk-forward-001`
sprint must run:

```bash
# Walk-forward plan generation + dry-run (no strategy execution; just
# validates fold-boundary rules).
.venv/bin/python scripts/run_walk_forward_dry_run.py \
    --universe-start 2020-01-01 --universe-end 2026-05-20 \
    --train-days 540 --validation-days 180 --test-days 180 \
    --step-days 180 --parameter-mode frozen \
    --output backtests/CAMPAIGN_010_session_breakout/walk_forward/

# Per-fold backtest invocation (mediated by the campaign script).
.venv/bin/python -m forex_bot.cli backtest \
    -c configs/campaign_010_session_breakout.yaml \
    --from 2020-01-01 --to 2026-05-20 \
    --export backtests/CAMPAIGN_010_session_breakout/
```

The above commands are listed for future-sprint reference; this
sprint does **not** run them.

## 7. Required walk-forward artifacts (future evidence sprint)

Per
[`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
§16:

- `backtests/CAMPAIGN_010_session_breakout/walk_forward/plan.json`
- `backtests/CAMPAIGN_010_session_breakout/walk_forward/plan.md`
- `backtests/CAMPAIGN_010_session_breakout/walk_forward/results.json`
- `backtests/CAMPAIGN_010_session_breakout/walk_forward/results.md`

Constraints:

- `parameter_mode = "frozen"` (only authorized mode).
- `SplitStyle = "rolling"`.
- 540/180/180/180-day window/step; ≥ 6 folds; ~ 9 expected.
- `validate_plan(plan)` must pass.
- `WalkForwardResults.overall_verdict ∈ {"PASS", "REJECT"}`.

## 8. Required financing artifacts (future evidence sprint)

Per
[`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
§10 (Option 1 — `default_stress_rate_source()` for v1):

- `backtests/CAMPAIGN_010_session_breakout/financing/financing_run.json`
- `backtests/CAMPAIGN_010_session_breakout/financing/financing_run.md`

Required-embed fields verbatim:

- `financing_treatment = "estimated"` (MODELED refused)
- `financing_in_engine_pnl = false`
- `financing_is_live_blocker = true`
- `cashflow_home_total`
- `cashflow_home_stress_total`
- `missing_rate_event_count`
- per-pair `TableRateSource` overlay (sidecar) using
  `research/financing/fixtures/rates_two_week_*.json` for sample
  diagnostic purposes.

## 9. Required risk diagnostics (future evidence sprint)

Per
[`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
§11 (informational; do not gate the verdict):

- per-pair exposure trace at fold boundaries
- max concurrent open positions
- max aggregate notional
- correlation-cap activation count
- daily / weekly loss-limit activation count
- session-blackout activation count

## 10. Required rejection gates (verbatim from design §8–§15)

A REJECT verdict is **mandatory** if any of these hold (no
parameter tweaks, no gate relaxation, no per-pair save):

| level | gate | threshold |
|---|---|---|
| train fold | `expectancy_R_net_of_stress_financing` | ≥ 0.00 R |
| train fold | `trade_count` | ≥ 30 |
| train fold | `no_lookahead_audit` | PASS |
| validation fold | `expectancy_R_net_of_stress_financing` | ≥ 0.05 R |
| validation fold | `profit_factor_net_of_stress_financing` | ≥ 1.05 |
| validation fold | `pairs_positive_net_of_stress_financing` | ≥ 3 of 7 |
| validation fold | `trade_count` | ≥ 30 |
| test fold | `expectancy_R_net_of_stress_financing` | ≥ 0.05 R |
| test fold | `profit_factor_net_of_stress_financing` | ≥ 1.10 |
| test fold | `pairs_positive_net_of_stress_financing` | ≥ 4 of 7 |
| test fold | `trade_count` | ≥ 30 |
| test fold | `single_pair_dominance` | ≤ 60 % |
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
| financing | `missing_rate_event_count` | `0` against committed `TableRateSource` fixtures (or use `default_stress_rate_source()`) |

## 11. Explicit no-approval statement

This checklist, the candidate config, the implementation
spec, and the unit tests **do not approve the strategy**.

The candidate cannot be added to
[`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
until **all six** evidence items in
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§8 exist:

1. Pre-commit doc — **this file is the candidate-pre-commit**.
2. Backtest report with gate verdicts — **future sprint**.
3. Walk-forward result with `overall_verdict ∈ {PASS, REJECT}` — **future sprint**.
4. Financing reconciliation — **future sprint** (ESTIMATED-only with synthetic fixtures; MODELED still refused).
5. Independent corroboration (custom-engine reproduction or free / local verifier) — **future sprint**.
6. Human approval record — **future, deliberate human action per
   [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)**.

Items 2–5 are necessary but not sufficient; item 6 is the
bright-line human gate.

## 12. Safety state (unchanged from sprint Phase 0)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.** `paper-loop` and
  `demo-loop` refuse; no `live-loop` command exists.
- No broker / OANDA call this sprint.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.
- `MODELED` financing remains refused at four layers.
- live-promotion financing blocker stands.

## 13. Cross-links

- [`ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md)
- [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md)
- [`CAMPAIGN_010_SMOKE_RESULT.md`](CAMPAIGN_010_SMOKE_RESULT.md)
- [`CAMPAIGN_010_WALK_FORWARD_READINESS.md`](CAMPAIGN_010_WALK_FORWARD_READINESS.md)
- [`CAMPAIGN_010_FINANCING_RISK_READINESS.md`](CAMPAIGN_010_FINANCING_RISK_READINESS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
