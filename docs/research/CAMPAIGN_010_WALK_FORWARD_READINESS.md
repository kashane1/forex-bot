# CAMPAIGN_010 — Walk-Forward Readiness

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-001`
`strategy_evidence: false`

Phase 6 walk-forward integration-readiness assessment for the
**CAMPAIGN_010 research candidate** (`session_breakout 0.1.0-c010`).
**Reading this document does not approve the strategy and does
not constitute a campaign verdict.** It records whether the
scaffold is *structurally ready* for a future evidence sprint to
generate `WalkForwardResults`.

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked. This document only certifies that
> the candidate plugs into the existing harness — it does not run
> a campaign.

## 1. Headline status

| dimension | status | note |
|---|---|---|
| Harness plug-in (plan generation, `validate_plan`) | **READY** | proven by Phase 5 dry-run: 8-fold plan generated and validated; ≥ 6 floor satisfied |
| Strategy module conforms to the `Strategy` protocol | **READY** | Phase 3 unit tests assert `name`, `version`, `warmup_bars_required()`, `generate_signal(ctx) -> Signal | None` |
| `parameter_mode = "frozen"` compatibility | **READY** | design + spec mandate frozen mode (only authorised); confirmed in `configs/campaign_010_session_breakout.yaml` |
| Per-fold backtest invocation | **NOT EXECUTED** in this sprint | requires (a) candle data, (b) a future evidence sprint to drive `BacktestEngine` per fold; this sprint deliberately does not run any backtest |
| `WalkForwardResults` emission | **NOT EXECUTED** in this sprint | future evidence sprint |

**Net: harness-plumbing readiness is GREEN; backtest evidence
readiness is BLOCKED on a future, separately-authorized
evidence sprint with candle data.**

## 2. Walk-forward fold plan

Phase 5 produced and validated the fold plan with the design's
parameters (rolling, frozen, 540/180/180/180 days,
`2020-01-01 → 2026-05-20`). Output committed to `/tmp` (not
committed to the repo per the prior sprints' convention; the
*evidence-grade* plan must commit to
`backtests/CAMPAIGN_010_session_breakout/walk_forward/`).

### 2.1 Smoke plan summary (reproducible)

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
| **fold count emitted by harness** | **8** |
| design §7 sketch projection | ~9 |
| reason for the −1 vs sketch | harness trims the final fold whose test window would extend past `universe-end` (a `validate_plan` invariant) |
| ≥ 6 minimum gate satisfied | **yes** |

### 2.2 Fold-by-fold (from the harness's `plan.json`)

| fold | train start | train end | val end | test end |
|---:|---|---|---|---|
| 0 | 2020-01-01 | 2021-06-23 | 2021-12-20 | 2022-06-18 |
| 1 | 2020-06-29 | 2021-12-20 | 2022-06-18 | 2022-12-15 |
| 2 | 2020-12-26 | 2022-06-18 | 2022-12-15 | 2023-06-13 |
| 3 | 2021-06-24 | 2022-12-15 | 2023-06-13 | 2023-12-10 |
| 4 | 2021-12-21 | 2023-06-13 | 2023-12-10 | 2024-06-07 |
| 5 | 2022-06-19 | 2023-12-10 | 2024-06-07 | 2024-12-04 |
| 6 | 2022-12-16 | 2024-06-07 | 2024-12-04 | 2025-06-02 |
| 7 | 2023-06-14 | 2024-12-04 | 2025-06-02 | 2025-11-29 |

(These dates are illustrative; the future evidence sprint will
regenerate via its own `run_walk_forward_dry_run.py` invocation
and commit the authoritative `plan.json` / `plan.md` under
`backtests/CAMPAIGN_010_session_breakout/walk_forward/`.)

## 3. Missing adapters (none required for plumbing; data adapter is required for backtest)

| adapter | required for | status |
|---|---|---|
| `Strategy` protocol implementation | bespoke `BacktestEngine` to drive per-fold | **DONE** — `src/forex_bot/strategies/session_breakout.py` |
| `StrategyConfig.session_breakout` slot | `forex_bot.config.load_settings` to recognise the candidate | **DONE** — `src/forex_bot/config.py` |
| YAML config that the bespoke engine can drive | the per-fold backtest invocation | **DONE** — `configs/campaign_010_session_breakout.yaml` |
| Per-fold backtest driver (campaign script) | iterating folds, slicing date windows, invoking `BacktestEngine`, accumulating `FoldMetrics` | **NOT DONE** — this is the future evidence sprint's task (see §5) |
| Local historical candle data (the 7-pair SQLite store) | per-fold backtest execution | **NOT PRESENT** — `data/` contains only `.gitkeep`; this sprint will not fetch |

## 4. Future evidence-sprint commands (recorded; not run here)

The future
`research-asian-london-session-breakout-walk-forward-001`
sprint must run (after restoring candle data with the human's
explicit credentialed-run authorization):

```bash
# 1. Regenerate the authoritative walk-forward plan.
.venv/bin/python scripts/run_walk_forward_dry_run.py \
    --campaign-name CAMPAIGN_010 \
    --universe-start 2020-01-01 --universe-end 2026-05-20 \
    --style rolling --parameter-mode frozen \
    --train-days 540 --validation-days 180 --test-days 180 \
    --step-days 180 \
    --output backtests/CAMPAIGN_010_session_breakout/walk_forward/

# 2. Drive per-fold backtests (campaign script TBD by that sprint).
.venv/bin/python -m forex_bot.cli backtest \
    -c configs/campaign_010_session_breakout.yaml \
    --from <fold.test_start> --to <fold.test_end> \
    --export backtests/CAMPAIGN_010_session_breakout/folds/<fold_index>/

# 3. Assemble FoldMetrics + AggregateMetrics + WalkForwardResults
#    via a campaign-specific script (mirrors the pattern of
#    scripts/build_campaign_*_report.py for prior campaigns).

# 4. Emit results.json + results.md via render_results_md(...).
```

This sprint **does not** run any of these.

## 5. Data requirements (the only soft blocker)

- **OANDA practice H4 candles for the 7-pair universe,
  2020-01-01 → 2026-05-20.** Currently absent in the worktree
  (`data/` only has `.gitkeep`). The CAMPAIGN_002 SQLite store
  is the documented data source
  ([`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
  §6 and the data rehydration runbook
  [`DATA_REHYDRATION_RUNBOOK.md`](DATA_REHYDRATION_RUNBOOK.md)).
- Data rehydration is a **separately-authorized human action**.
  This sprint does not invoke
  `scripts/rehydrate_oanda_h4_store.py` and does not read OANDA
  credentials.

## 6. Strict gates (verbatim from design §8–§15; restated for the future sprint)

Every per-fold and aggregate gate from the candidate's
pre-commit checklist
([`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
§10) is binding on the future sprint. The summary:

- **Strict pass:** `aggregate.fold_pass_rate == 100 %`. Any
  failed test fold = REJECT.
- **Min trade count:** 30/fold, 200/aggregate.
- **Dominance:** ≤ 60 % per pair per test fold; ≤ 40 % per pair
  on aggregate; ≤ 60 % per fold on aggregate.
- **Net of financing:** every PnL number must be reported
  **after** the conservative-stress overlay.

No gate is relaxed after seeing results.

## 7. Why the scaffold sprint cannot grant a verdict

- It produced no `FoldMetrics`.
- It produced no `AggregateMetrics`.
- It produced no `WalkForwardResults`.
- It produced no per-pair expectancy R.
- It produced no per-pair profit factor.
- It produced no per-pair / per-fold dominance number.
- It executed no `BacktestEngine` invocation.
- It did not load any candle data.

A non-evidence smoke (Phase 5) cannot promote to evidence.
Only the future evidence sprint can.

## 8. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.**
- No broker / OANDA call made by this readiness check.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.

## 9. Cross-links

- [`CAMPAIGN_010_FINANCING_RISK_READINESS.md`](CAMPAIGN_010_FINANCING_RISK_READINESS.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_010_SMOKE_RESULT.md`](CAMPAIGN_010_SMOKE_RESULT.md)
- [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md)
- [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`DATA_REHYDRATION_RUNBOOK.md`](DATA_REHYDRATION_RUNBOOK.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
