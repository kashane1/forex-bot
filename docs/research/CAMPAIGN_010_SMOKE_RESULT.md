# CAMPAIGN_010 — Smoke Result

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-001`
`strategy_evidence: false`

Phase 5 smoke results for the **CAMPAIGN_010 research candidate**
(`session_breakout 0.1.0-c010`). **This is non-evidence.** Smoke
checks prove the scaffold loads, instantiates, generates signals
on synthetic frames, and is structurally compatible with the
walk-forward harness — they do **not** establish an edge, do
**not** approve the strategy, and do **not** constitute a
campaign verdict.

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked. The historical-data backtest
> remains **blocked** for this sprint (no local SQLite candle
> store present); only fixture-based and dry-run smokes were run.

## 1. Smoke commands run

| # | command | scope | data source | exit |
|---:|---|---|---|---:|
| 1 | config-load smoke (Python one-liner: `load_settings('configs/campaign_010_session_breakout.yaml')`) | candidate config parses + `SessionBreakoutStrategyConfig` instantiates with frozen design params | the YAML file only — no broker, no SQLite | 0 |
| 2 | `python -m pytest tests/unit/test_session_breakout.py -q` | 33 unit + structural-audit cases | synthetic OHLC fixtures + AST/source-grep | 0 |
| 3 | `python scripts/run_walk_forward_dry_run.py --campaign-name CAMPAIGN_010_SMOKE --universe-start 2020-01-01 --universe-end 2026-05-20 --style rolling --parameter-mode frozen --train-days 540 --validation-days 180 --test-days 180 --step-days 180 --output /tmp/campaign_010_smoke` | walk-forward fold-plan generation + `validate_plan(...)` | none (date arithmetic only) | 0 |

### 1.1 Was any broker call made?

**No.** Zero OANDA calls, zero transaction queries, zero orders,
zero network traffic, zero `.env` reads, zero credentials
printed. Every smoke ran offline against either the YAML file,
synthetic in-memory OHLC fixtures, or pure date arithmetic.

### 1.2 Was a credential used?

**No.** None of the smoke commands consults `OANDA_*` env
variables. The CLI never invoked an order-capable loop (the
`paper-loop` / `demo-loop` refusals are recorded separately in
the sprint's Phase 0 + Phase 7).

### 1.3 Is this evidence?

**No.** This is non-evidence by charter. See §5.

## 2. Smoke 1: config-load

```text
CONFIG-LOAD: PASS
  enabled: ['session_breakout']
  session_breakout.version: 0.1.0-c010
  session_breakout.atr_lookback: 14
  session_breakout.atr_stop_multiple: 2.0
  session_breakout.min_asian_range_atr_fraction: 0.3
  universe size: 7
  trading_enabled: False
  allow_order_submission: False
  allow_live_trading: False
```

Confirms:

- the candidate YAML parses through `forex_bot.config.load_settings`;
- `StrategyConfig.session_breakout` slot resolves;
- the design's frozen parameters round-trip through Pydantic;
- the 7-pair H4 universe is honoured;
- every order-capable flag (`trading_enabled`,
  `allow_order_submission`, `allow_live_trading`) is **false**,
  matching the candidate-scaffold-only posture.

## 3. Smoke 2: signal-generation unit suite

```text
.................................                                        [100%]
33 passed in 0.05s
```

Confirms (per
[`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md)
§12 task list):

- session-window helpers (in_asian, in_london) honour half-open
  intervals and the midnight wrap;
- the `SessionBreakoutStrategyConfig` rejects invalid session
  hours, equal asian start/end, and `london_start >= london_end`
  at construction time (`ValidationError`);
- the strategy returns `None` on insufficient warm-up;
- the strategy returns `None` when a position is already open
  on the instrument;
- the strategy emits the correct directional `Signal` when the
  London-bar close penetrates the prior Asian bar's high (long)
  or low (short);
- the Asian-range gate trips when the range is below
  `min_asian_range_atr_fraction * ATR`;
- the strategy returns `None` when bar `t` is not in London or
  bar `t-1` is not in Asian;
- the strategy returns `None` on close-equals-prior-high /
  close-equals-prior-low (the tie cases);
- the stop distance equals `atr_stop_multiple * prior_atr` on
  the correct side of `close[t]`;
- the `min_atr_pips` floor blocks when set high;
- the features dict carries the required keys
  (`prior_high`, `prior_low`, `prior_range`, `prior_atr`,
  `last_close`, `range_fraction`, `prior_hour_utc`,
  `current_hour_utc`, `atr_pips`);
- the `signal_id` is deterministic across repeated calls;
- the strategy does not mutate the input config dict;
- the `exit_model` string is `"time_stop_only"` and no
  `take_profit_price` is emitted;
- an incomplete latest bar is filtered out by
  `CandleFrame.completed_only()` (no same-bar lookahead via
  incomplete bars);
- the strategy module imports no `forex_bot.broker.*` or
  `forex_bot.execution.*` (AST audit);
- the strategy module has no `.shift(-N)` / `df["high"].iloc[-1]`
  / `df["low"].iloc[-1]` lookahead anti-patterns (source grep);
- the candidate references no CAMPAIGN_002 / `trend_following`
  config keys (independence test);
- `Signal` carries no approval-shaped field;
- `configs/approved_strategies.yaml` remains empty;
- `session_breakout` is not in any loop-enabled strategy list
  when the paper config is loaded.

## 4. Smoke 3: walk-forward dry-run

Command (full):

```bash
.venv/bin/python scripts/run_walk_forward_dry_run.py \
    --campaign-name CAMPAIGN_010_SMOKE \
    --universe-start 2020-01-01 \
    --universe-end 2026-05-20 \
    --style rolling \
    --parameter-mode frozen \
    --train-days 540 --validation-days 180 \
    --test-days 180 --step-days 180 \
    --output /tmp/campaign_010_smoke
```

Output:

```text
Wrote: /tmp/campaign_010_smoke/plan.json
       /tmp/campaign_010_smoke/plan.md
Fold count: 8
Style: rolling · parameter_mode: frozen
```

Plan-level facts:

- `validate_plan(...)` PASSED (the harness's plan-level rules
  enforce min fold count ≥ 3, forward-only ordering, no
  consecutive test-window overlap, all boundaries inside
  universe).
- **fold count: 8** (the design's §7 sketch projected ~9; the
  actual is one fewer because the harness trims the final fold
  whose test window would extend past `universe-end`). 8 ≥ 6
  satisfies the design's minimum-fold-count gate.
- first fold: train `2020-01-01 → 2021-06-23`, val
  `2021-06-24 → 2021-12-20`, test `2021-12-21 → 2022-06-18`.
- last fold: train `2023-06-14 → 2024-12-04`, val
  `2024-12-05 → 2025-06-02`, test `2025-06-03 → 2025-11-29`.
- `parameter_mode = frozen` (only authorized mode).

### 4.1 Was any strategy executed?

**No.** The dry-run script generates and validates the *plan*
only. It does not invoke `SessionBreakoutStrategy.generate_signal`
on any data; it does not invoke `BacktestEngine`; it does not
import `forex_bot.broker.*`. (See the docstring at
[`scripts/run_walk_forward_dry_run.py`](../../scripts/run_walk_forward_dry_run.py).)

### 4.2 Where do the output files live?

Under `/tmp/campaign_010_smoke/` (gitignored by the OS) — **not
committed**. Per the prior sprints' convention, walk-forward
plan/result artifacts only commit when they are evidence-grade,
under `backtests/CAMPAIGN_010_session_breakout/walk_forward/`,
in a *future* evidence sprint.

## 5. Blocked items (recorded honestly)

| item | blocker | safe next step |
|---|---|---|
| Local historical backtest (1 pair, 1 fold) | No SQLite candle store present in `data/` (only `.gitkeep`). | A future sprint should either (a) restore the OANDA-practice H4 candle store via the documented rehydration runbook in [`DATA_REHYDRATION_RUNBOOK.md`](DATA_REHYDRATION_RUNBOOK.md) **with the human's explicit credentialed-run authorization**, or (b) defer the backtest to the evidence sprint that opens its own data-rehydration step. **This sprint will not fetch candle data.** |
| Per-pair financing overlay sample | Requires running the calculator over a sample trade list, which requires running a backtest, which is blocked above. | Future evidence sprint. |
| Independent corroboration | Verifier currently covers `trend_following`; extending to `session_breakout` is a separate verifier-side sprint. | Future verifier-extension sprint. |

## 6. Smoke summary

| smoke | status | evidence? |
|---|---|---|
| config-load | **PASS** | non-evidence (mechanical) |
| signal-generation unit suite (33 cases) | **PASS** | non-evidence (synthetic fixtures) |
| walk-forward dry-run (fold-plan + `validate_plan`) | **PASS** (8 folds; ≥ 6 floor satisfied) | non-evidence (no strategy executed) |
| local historical-data backtest | **BLOCKED** (no SQLite store) | not run |

**Overall: scaffold load + signal-shape + harness-plan smokes
all green; no evidence produced; no verdict implied.**

## 7. Explicit no-approval statement

These smokes do **not** approve `session_breakout`. Approval
requires the six-evidence ladder per
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§8 — items 2–5 (backtest report, walk-forward result, financing
reconciliation, independent corroboration) are **future-sprint
work** that this sprint does not undertake. Item 6 (human
approval entry in
[`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml))
is the bright-line gate, also not exercised here.

## 8. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.**
- No broker / OANDA call made by any smoke.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No bulky output committed (dry-run wrote 2 files totaling
  3.4 KB under `/tmp/`, not committed).

## 9. Cross-links

- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md)
- [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`DATA_REHYDRATION_RUNBOOK.md`](DATA_REHYDRATION_RUNBOOK.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
