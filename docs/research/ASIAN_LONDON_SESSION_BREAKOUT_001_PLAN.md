# Asian/London Session Breakout — Sprint 001 Plan

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-001`
(worktree branch: `claude/affectionate-fermi-d950fc`)
**Base commit:** `356d356` (`Phase 6
(research-new-candidate-strategy-discovery-001): summary & final
validation`)
`strategy_evidence: false`

Phase 0 truth audit + sprint plan for the **first code scaffold**
of candidate C1 (session_breakout) selected by the prior
docs-only discovery sprint. **This sprint may add strategy/research
code, config scaffolding, tests, and documentation needed to make
the candidate evaluable later. It must not approve the strategy,
must not run paper/demo/live trading, and must not treat any
result as deployable.**

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked. CAMPAIGN_010, if created in this
> sprint, is **candidate scaffold only** — no campaign verdict, no
> backtest evidence, no approval implied. The future evidence
> sprint must still run walk-forward, financing overlays, risk
> diagnostics, and independent verification before any
> paper/demo consideration.

## 1. Worktree state

| field | value |
|---|---|
| working directory | `/Users/kashane/dev/forex-bot/.claude/worktrees/affectionate-fermi-d950fc` |
| git branch | `claude/affectionate-fermi-d950fc` |
| sprint label (commit prefix) | `research-asian-london-session-breakout-001` |
| base commit | `356d356ad...` |
| `git status` before this commit | clean |
| project venv | `/Users/kashane/dev/forex-bot/.venv/bin/python` |

## 2. Files inspected (Phase 0 read-only)

### Design / protocol (from prior sprint)

- [`NEXT_BRANCH_DECISION_AUDIT.md`](NEXT_BRANCH_DECISION_AUDIT.md)
  — verified base state (702 tests passing, financing complete,
  walk-forward complete).
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
  — binding protocol every future candidate must follow.
- [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
  — §1 candidate name `session_breakout`, version `0.1.0-c010`,
  campaign `CAMPAIGN_010`; §2 verbatim hypothesis; §3 frozen
  parameter set; §4 7-pair universe; §5 H4 timeframe; §7
  walk-forward fold design; §8–§15 gates; §16 required artifacts;
  §17 corroboration; §19 pre-flight checklist.
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
  — C1 distinctness scoring vs every prior rejected family.
- [`STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md)
  — `Strategy` protocol, existing strategy modules, indicator
  primitives, RiskEngine surface, StrategyConfig binding
  constraints, walk-forward + financing APIs.
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md)
  — prior sprint summary; recommended next branch is this sprint.

### Code surfaces (read-only)

- [`src/forex_bot/strategies/base.py`](../../src/forex_bot/strategies/base.py)
  — `Strategy` Protocol + `StrategyContext` dataclass (instrument,
  candles, market_state, open_positions, config dict).
- [`src/forex_bot/strategies/volatility_breakout.py`](../../src/forex_bot/strategies/volatility_breakout.py)
  — the closest pattern for an Asian/London breakout (session-of-day
  variant of a Donchian-style breakout). Implementation uses
  `df = ctx.candles.completed_only().df`, blocks re-entry on
  open positions, returns `Signal` with `side`, `stop_price`,
  `features`, uses `_isnan` + `_stable_signal_id` helpers.
- [`src/forex_bot/strategies/indicators.py`](../../src/forex_bot/strategies/indicators.py)
  — `atr()` is the only primitive the new candidate needs. No new
  indicator function required (session hour is derived from the
  bar timestamp).
- [`src/forex_bot/config.py`](../../src/forex_bot/config.py)
  — `StrategyConfig` is `extra="forbid"` and explicitly enumerates
  the four existing families. Adding `session_breakout` requires
  adding (a) a new `SessionBreakoutStrategyConfig` sub-model and
  (b) a new `session_breakout` slot on `StrategyConfig`, plus
  matching `@model_validator` updates. This is a CODE edit; per the
  sprint rules it is **allowed** because this sprint is the
  candidate-scaffold sprint.
- [`tests/unit/test_strategies.py`](../../tests/unit/test_strategies.py)
  — synthetic-frame test pattern (`_build_frame` + `_ctx` helpers)
  the new test suite will mirror.
- [`tests/unit/conftest.py`](../../tests/unit/conftest.py) (verified
  via the test imports above) — provides instrument fixtures.

### Configs

- [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
  — `approved: []`. **Will NOT be modified.**
- `configs/campaign_*.yaml` — six existing campaign configs;
  this sprint adds a new research-only candidate config named
  `configs/campaign_010_session_breakout.yaml`.

## 3. Verified preconditions

| precondition | command | result |
|---|---|---|
| `approved_strategies.yaml` is `approved: []` | grep | ✓ verbatim |
| CAMPAIGN_002 REJECT | manifest + index unchanged | ✓ |
| no `live-loop` command | `cli --help` | ✓ commands: `doctor sync-instruments fetch-candles backtest audit-data paper-loop demo-loop reconcile report` |
| paper-loop refuses | `cli paper-loop -c configs/paper.yaml` | ✓ refused |
| demo-loop refuses | `cli demo-loop -c configs/practice.yaml` | ✓ refused |
| QuantConnect/LEAN not used | retirement decision stands | ✓ |
| pytest baseline | `pytest -q` | **702 passed in 2.85s** |
| archive validator | `validate_research_archive.py` | **PASS** (9 campaigns, 14 diagnostic artifacts, 135 evidence-index links, 1996 artifact files clean) |
| freeze checker | `check_research_freeze.py` | **PASS** (loops refuse `['trend_following']`) |
| secret scanner | `scan_artifacts_for_secrets.py` | **PASS** (2054 files pattern-scanned) |
| ruff baseline | `ruff check src tests scripts research` | **11 pre-existing UP042 errors** in `research/{walk_forward,financing,parity_verifier}/models.py` and `research/lean_parity/algorithms/campaign_002_h4_baseline/main.py` — matches the prior sprint's documented disclosure; this sprint will not refactor them |

## 4. Preferred candidate requirements (from design)

Extracted from
[`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md):

| field | value |
|---|---|
| `Strategy.name` | `session_breakout` |
| `Strategy.version` | `0.1.0-c010` |
| campaign label | `CAMPAIGN_010` |
| universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD (the 7 CAMPAIGN_002 H4 pairs) |
| timeframe | H4 |
| frozen `asian_session_hours_utc_start` | `22` |
| frozen `asian_session_hours_utc_end` | `6` |
| frozen `london_session_hours_utc_start` | `6` |
| frozen `london_session_hours_utc_end` | `12` |
| frozen `min_asian_range_atr_fraction` | `0.30` |
| frozen `atr_lookback` | `14` |
| frozen `atr_stop_multiple` | `2.0` |
| frozen `trailing_stop_atr_multiple` | `None` |
| frozen `max_bars_in_trade` (= design's `time_stop_bars`) | `6` |
| frozen `min_atr_pips` | `{}` |
| frozen `risk_per_trade_pct` | `0.25` (existing `RiskConfig` slot) |
| `max_positions_per_instrument` | `1` (existing `RiskConfig` constant) |
| walk-forward `parameter_mode` | `frozen` (only authorized) |
| walk-forward fold design | rolling, 540/180/180/180 days, ≈ 9 folds |
| financing overlay | conservative-stress source as default (Option 1 from design §10.1) |
| no-lookahead inputs | `high[t-1]`, `low[t-1]`, `atr_14[t-1]`, `close[t]` only |

## 5. Implementation files (Phase 2/4 additions)

| file | purpose | size estimate |
|---|---|---:|
| `src/forex_bot/strategies/session_breakout.py` | new strategy module implementing the `Strategy` protocol | ~180 LOC |
| `src/forex_bot/strategies/__init__.py` | add `SessionBreakoutStrategy` to re-exports | +2 LOC |
| `src/forex_bot/config.py` | add `SessionBreakoutStrategyConfig` sub-model + `StrategyConfig.session_breakout` slot + validator | +60 LOC |
| `tests/unit/test_session_breakout.py` | unit tests per Phase 3 task list | ~300 LOC |
| `configs/campaign_010_session_breakout.yaml` | research-only candidate config | ~120 LOC |

No edits to:

- [`src/forex_bot/backtesting/engine.py`](../../src/forex_bot/backtesting/engine.py)
- [`src/forex_bot/risk/policy.py`](../../src/forex_bot/risk/policy.py)
- [`src/forex_bot/financing.py`](../../src/forex_bot/financing.py)
- [`src/forex_bot/broker/`](../../src/forex_bot/broker/)
- [`src/forex_bot/loops.py`](../../src/forex_bot/loops.py)
- [`src/forex_bot/approval.py`](../../src/forex_bot/approval.py)
- [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
- any existing `configs/campaign_*.yaml`
- any CAMPAIGN_002 doc / artifact
- any existing strategy module (other than the `__init__.py`
  re-export)

## 6. Documents to add

| doc | phase | purpose |
|---|---|---|
| `ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md` (this file) | 0 | sprint plan + Phase 0 audit |
| `ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md` | 1 | machine-facing implementation spec |
| `CAMPAIGN_010_PRECOMMIT_CHECKLIST.md` | 4 | pre-commit / evaluation checklist |
| `CAMPAIGN_010_STATUS.md` | 4 | candidate-scaffold-only status |
| `CAMPAIGN_010_SMOKE_RESULT.md` | 5 | smoke evaluation (or blocked) |
| `CAMPAIGN_010_WALK_FORWARD_READINESS.md` | 6 | walk-forward readiness |
| `CAMPAIGN_010_FINANCING_RISK_READINESS.md` | 6 | financing + risk readiness |
| `ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md` | 7 | sprint summary |
| `EVIDENCE_INDEX.md` | 7 | append candidate-scaffold sub-section (existing doc edit) |

## 7. Test plan (Phase 3 task list)

The Phase 3 test suite (`tests/unit/test_session_breakout.py`)
must cover, at minimum:

1. Asian range is built only from completed bars in the defined
   range window (uses `high[t-1]`, `low[t-1]` only).
2. No signal occurs before the warm-up window is complete.
3. Long breakout signal triggers only after valid upper range
   breach.
4. Short breakout signal triggers only after valid lower range
   breach.
5. No same-bar lookahead — only `close[t]` is consulted at bar `t`;
   bar `t`'s high/low are NOT used.
6. Missing bars / incomplete frames fail closed (None returned).
7. Insufficient data (warm-up not met) returns None.
8. Session/timezone conversion is deterministic (UTC hour is
   derived from `df.index[-1].hour`).
9. Max-bars-in-trade exit semantics are RiskEngine-managed; the
   strategy itself emits the `exit_model` string.
10. Stop-loss is `ATR * multiple` and is on the correct side
    of `close[t]`.
11. Take-profit / trailing-stop: v1 has none; test asserts
    `Signal.exit_model` reflects "time_stop_only" and there is
    no take-profit price emitted.
12. Duplicate entries are prevented while a position is open
    (same pattern as `TrendFollowingStrategy.generate_signal`,
    lines 82–84).
13. Frozen parameters are not mutated during a run (cfg dict
    is read but not written).
14. Session-window boundary cases: bar at exactly the start hour
    counts; bar at the end hour does not (half-open `[start, end)`
    convention).
15. Range-fraction gate rejects when Asian range < threshold.
16. Candidate does not depend on CAMPAIGN_002 config or
    parameters — independent test fixture.
17. Candidate module imports no `forex_bot.broker.*` execution
    code (grep test).
18. The strategy emits no approval artifact (it returns a
    `Signal` only).

## 8. Validation plan

Per phase (`pytest`/`ruff` targeted to touched paths first;
full-suite at the end):

| phase | validation |
|---|---|
| 0 | full pytest, full ruff, archive validator, freeze checker, secret scanner, refusal commands, `--help` |
| 1 | docs validator (archive validator catches link breakage) |
| 2 | targeted `pytest tests/unit/test_session_breakout.py` once test file exists; otherwise `pytest -q` to confirm baseline preserved + targeted ruff on touched Python files |
| 3 | full `pytest tests/unit/test_session_breakout.py` ≥ 18 cases; ruff on touched files |
| 4 | config-load test if available; archive validator; freeze checker; secret scanner |
| 5 | smoke test invocation; safety checks |
| 6 | walk-forward dry-run if safe (no broker call); safety checks |
| 7 | full pytest; full ruff; archive validator; freeze checker; secret scanner; refusal commands; `--help`; `git status --short` |

## 9. Non-goals (binding)

This sprint **does not**:

- approve any strategy (no edit to
  `configs/approved_strategies.yaml`);
- run paper-loop / demo-loop / live-loop (refusal checks only);
- introduce a `live-loop` command;
- submit, create, modify, cancel, close, or query broker orders;
- read live broker credentials;
- read `.env`;
- print credentials;
- commit `.env`, SQLite stores, candle CSVs, bulky raw outputs,
  tokens, credentials, cache files, or local-only generated data;
- use QuantConnect / LEAN;
- revive, tune, or repromote CAMPAIGN_002;
- change any historical campaign verdict;
- perform broad parameter search;
- optimize parameters based on results;
- present a trading recommendation;
- claim readiness for paper/demo/live.

## 10. Safety invariants (held across every phase)

| invariant | enforcement |
|---|---|
| `configs/approved_strategies.yaml` is `approved: []` | Phase 7 re-greps; freeze checker re-asserts |
| CAMPAIGN_002 untouched | grep `git log --since` for any `CAMPAIGN_002` edit |
| paper-loop / demo-loop refuse | Phase 7 re-runs the refusals |
| no `live-loop` command | Phase 7 re-inspects CLI help |
| no broker / OANDA call | no script in this sprint imports `forex_bot.broker.oanda`; targeted grep |
| no `.env` read | no `os.environ.get('OANDA_*')` in any new file |
| no QuantConnect / LEAN | no `lean` command issued; no `src/forex_bot/lean/` edit |
| ruff clean on touched files | per-phase ruff check (the 11 pre-existing UP042 in untouched files are **not** addressed by this sprint and remain documented) |
| pytest passes | per-phase + final full run |
| no bulky/raw outputs committed | `.gitignore` + manual review of `git status --short` |
| `CAMPAIGN_010` is candidate scaffold only | every CAMPAIGN_010 doc carries explicit "no approval / no verdict / no paper/demo/live" disclaimer |

## 11. Explicit no-approval statements (recorded at sprint start)

- **This sprint cannot approve the strategy.** Even a fully
  passing test suite, a successful smoke evaluation, and a
  successful walk-forward dry-run do not constitute approval.
- **CAMPAIGN_010 is candidate research only.** Any
  `CAMPAIGN_010_*` doc created during this sprint says so
  verbatim and includes the no-approval disclaimer.
- **No backtest verdict is implied by this sprint.** A smoke
  result is not a verdict; a config-load test is not a verdict;
  the candidate's evidence ladder (per
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §8 / six items) is **not** completed by this sprint and is
  the work of separate future sprints.
- **Paper / demo / live remain blocked** for the duration of
  this sprint and after it completes.

## 12. Recommended next sprints (after this one completes)

- `research-asian-london-session-breakout-walk-forward-001` —
  generate + commit `plan.json` / `plan.md` + run per-fold
  backtests for CAMPAIGN_010.
- `research-financing-multi-year-fixture-expansion-001` (if
  per-pair multi-year `TableRateSource` is desired before the
  walk-forward run).
- `infra-ruff-up042-stress-enum-001` — clean up the 11
  pre-existing UP042 errors before more code is added.

None of these is initiated by this sprint.

## 13. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
- [`STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
