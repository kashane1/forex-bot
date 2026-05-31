# Asian/London Session Breakout — Sprint 001 Summary

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-001`
(worktree branch: `claude/affectionate-fermi-d950fc`)
`strategy_evidence: false`

End-of-sprint summary and handoff for the **CAMPAIGN_010 research
candidate scaffold** sprint. Adds the strategy module, the
`StrategyConfig.session_breakout` slot, the candidate config YAML,
33 unit + structural-audit tests, and the candidate's
pre-commit / status / smoke / readiness docs. **CANDIDATE
SCAFFOLD ONLY — not approved for paper / demo / live.** Paper /
demo / live remain blocked; CAMPAIGN_002 remains REJECT;
`configs/approved_strategies.yaml` remains `approved: []`. The
735-test baseline (702 prior + 33 new) is preserved.

> A passing unit test suite or smoke test is **not** strategy
> approval. A config-load or fixture-smoke result is **not** a
> campaign verdict. A future full evidence sprint must still run
> walk-forward, financing overlays, risk diagnostics, and
> independent verification before any paper/demo consideration.

## 1. What changed

| component | added / edited |
|---|---|
| Strategy module | new `src/forex_bot/strategies/session_breakout.py` (~190 LOC) implementing the `Strategy` protocol |
| Strategy re-export | `src/forex_bot/strategies/__init__.py` adds `SessionBreakoutStrategy` |
| Config schema | new `SessionBreakoutStrategyConfig` sub-model in `src/forex_bot/config.py` + new `StrategyConfig.session_breakout` slot + matching `@model_validator` check |
| Unit tests | new `tests/unit/test_session_breakout.py` (33 cases) |
| Research config | new `configs/campaign_010_session_breakout.yaml` |
| Sprint docs | 8 new files under `docs/research/` (plan, spec, pre-commit checklist, status, smoke result, walk-forward readiness, financing+risk readiness, this summary) |
| Evidence index | new sub-section in `docs/research/EVIDENCE_INDEX.md` (8 doc rows) |
| Strategy registry | `docs/research/STRATEGY_STATUS.md` adds a `candidate-scaffold (no verdict)` row for `session_breakout 0.1.0-c010` |

## 2. What did NOT change

- `configs/approved_strategies.yaml` — still `approved: []`.
- Any `backtests/CAMPAIGN_*` — every prior campaign verdict
  remains untouched. CAMPAIGN_002 remains REJECT.
- `src/forex_bot/backtesting/engine.py` — bespoke engine
  untouched. No engine-PnL change.
- `src/forex_bot/risk/policy.py` — RiskEngine untouched. No
  new gate.
- `src/forex_bot/financing.py` — production financing path
  untouched. `financing_treatment_blocks_approval` remains
  authoritative; `MODELED` remains refused at four layers.
- `src/forex_bot/broker/`, `src/forex_bot/loops.py`,
  `src/forex_bot/approval.py`, `src/forex_bot/cli.py` —
  untouched.
- Any existing strategy module (`trend_following.py`,
  `volatility_breakout.py`, `pullback_continuation.py`,
  `mean_reversion.py`) — only `__init__.py` re-exports list
  changed; the strategy modules themselves are untouched.
- Existing `configs/campaign_*.yaml` — no other campaign
  config touched.
- `pyproject.toml` — no new external dependency.
- `EVIDENCE_MANIFEST.json` — no new campaign verdict to
  manifest (the candidate has no backtest, so no manifest row
  is added; the same convention the financing sprints
  followed).

## 3. Sprint commits

| phase | commit | message |
|---|---|---|
| 0 | `1c7d771` | repo truth audit & sprint plan |
| 1 | `e0374cf` | implementation spec |
| 2 | `4e4a84d` | strategy scaffold |
| 3 | `ecfe03d` | unit tests |
| 4 | `f93b305` | research config + CAMPAIGN_010 docs |
| 5 | `78f34b0` | smoke evaluation |
| 6 | `a10d20b` | walk-forward + financing + risk readiness |
| 7 | (this commit) | summary + final validation + EVIDENCE_INDEX update |

## 4. Implementation status

| dimension | status |
|---|---|
| `Strategy` protocol implementation | **complete**; emits `Signal | None` per H4 bar |
| `StrategyConfig.session_breakout` slot | **complete**; rejects invalid session hours, equal asian start/end, `london_start >= london_end` at construction |
| Strategy module imports no broker / execution code | **verified** by AST audit test |
| Strategy module has no `.shift(-N)` / same-bar lookahead | **verified** by source-grep test |
| Strategy independent from CAMPAIGN_002 / `trend_following` | **verified** by source-grep test |
| Determinism (signal_id stable across repeated calls) | **verified** by unit test |
| Frozen parameter set matches design verbatim | **complete**; documented in `CAMPAIGN_010_PRECOMMIT_CHECKLIST.md` §5 |

## 5. Config status

| dimension | status |
|---|---|
| `configs/campaign_010_session_breakout.yaml` loads via `load_settings` | **complete** (Phase 5 smoke) |
| `app.trading_enabled` | `false` (verified) |
| `app.allow_order_submission` | `false` (verified) |
| `app.allow_live_trading` | `false` (verified) |
| 7-pair H4 universe | **complete** (EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD) |
| `configs/approved_strategies.yaml` | **`approved: []`** (verified verbatim; `session_breakout` deliberately absent) |
| `session_breakout` in any active paper/demo loop | **no** (Phase 3 regression test pins it) |

## 6. Test status

- `tests/unit/test_session_breakout.py`: **33 cases pass**.
- Full repo suite: **735 passes in 2.69 s** (702 prior + 33 new).
- `ruff check src/forex_bot/strategies/session_breakout.py
  src/forex_bot/strategies/__init__.py src/forex_bot/config.py
  tests/unit/test_session_breakout.py` — **all checks passed**.

## 7. Smoke status

Phase 5 ran three credential-free smokes (see
[`CAMPAIGN_010_SMOKE_RESULT.md`](CAMPAIGN_010_SMOKE_RESULT.md)):

| smoke | exit | evidence? |
|---|---:|---|
| config-load | 0 | non-evidence |
| signal-generation unit suite (33 cases) | 0 | non-evidence |
| walk-forward dry-run (8-fold validated plan) | 0 | non-evidence |
| local historical-data backtest | — | **BLOCKED** (no SQLite store; will not fetch) |

No broker call. No `.env` read. No credentials printed. No
bulky output committed.

## 8. Walk-forward readiness

Per
[`CAMPAIGN_010_WALK_FORWARD_READINESS.md`](CAMPAIGN_010_WALK_FORWARD_READINESS.md):

- Harness plug-in: **READY** — 8-fold plan validated under the
  design's parameters.
- Strategy protocol conformance: **READY**.
- `parameter_mode = "frozen"`: **READY**.
- Per-fold backtest execution: **NOT EXECUTED** in this sprint.
  Future evidence sprint required.

## 9. Financing readiness

Per
[`CAMPAIGN_010_FINANCING_RISK_READINESS.md`](CAMPAIGN_010_FINANCING_RISK_READINESS.md):

- ESTIMATED rate source available
  (`default_stress_rate_source()`).
- Per-pair `TableRateSource` diagnostic sample available (the
  committed 2-week fixtures).
- **`MODELED` refused at four layers**; live-promotion
  financing blocker stands.
- Expected holding period: 0–1 rollover events per trade
  (max_bars_in_trade=6 H4 bars ≈ 1 trading day).
- `financing_treatment` will be `"estimated"`;
  `financing_in_engine_pnl: false`; `financing_is_live_blocker:
  true`.

## 10. Portfolio-risk readiness

- RiskEngine `mode='backtest'` integration: **READY** (no new
  gate required).
- Diagnostic checklist (per-pair exposure, concurrent
  positions, notional, correlation, loss limit, session
  blackout): **STRUCTURALLY READY**; actual computation
  requires the backtest (future evidence sprint).
- Note: `max_open_positions = 1` is a deliberately
  conservative posture; the design's `> 3` diagnostic
  threshold is for less-conservative future variants.

## 11. Known limitations

| limitation | impact |
|---|---|
| Fixed-UTC session windows + DST | Under NY-DST H4 alignment, the eligible London bar starts at 09:00 UTC (t-1 at 05:00 UTC); under NY-standard it starts at 06:00 UTC (t-1 at 02:00 UTC). One opportunity per pair per trading day under both alignments. Documented in [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md) §3.4. |
| No holiday calendar | Holiday bars are treated as ordinary bars; the Asian-range gate tends to under-fire on holidays naturally. Consistent with the rest of `src/forex_bot/` (no holiday calendar anywhere). |
| Single-bar Asian-range definition | Brittle for instruments with sparse Asian volume (e.g. USD_JPY). Accepted as a v1 simplification per the design. |
| 2-week per-pair financing fixtures | Only a sample; the full-window walk-forward uses `default_stress_rate_source()` (Option 1 from design §10.1). |
| `MODELED` financing unavailable | The candidate is structurally ineligible for live promotion. Paper / demo also blocked by the empty approved-strategy registry. |
| Local SQLite candle store absent | A future sprint with explicit human credentialed-run authorization must restore the OANDA-practice H4 store before any backtest. |
| 11 pre-existing ruff UP042 hints | In `research/{walk_forward,financing,parity_verifier}/models.py` and `research/lean_parity/algorithms/...`. Not introduced by this sprint. Recommended separate cleanup sprint: `infra-ruff-up042-stress-enum-001`. |

## 12. Safety state (unchanged across the sprint)

| dimension | status |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified verbatim in Phase 0, Phase 4, Phase 7) |
| CAMPAIGN_002 verdict | **REJECT** (untouched) |
| `session_breakout` in approved registry | **no** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| broker / OANDA call this sprint | none |
| `.env` read this sprint | none |
| credentials printed this sprint | none |
| engine-PnL change | none |
| `src/forex_bot/financing.py` change | none |
| new external dependency | none |
| `MODELED` financing reachable | no (four refusal layers) |
| live-promotion financing blocker | stands |
| pytest baseline preserved | **735 passes** (702 prior + 33 new) |
| ruff baseline preserved | 11 pre-existing UP042 hints in untouched files; matches Phase 0 |
| archive validator | PASS (9 campaigns, 14 diagnostic artifacts, **135** evidence-index links, 2004 artifact files clean) |
| freeze checker | PASS |
| secret scanner | PASS (2062 files pattern-scanned) |
| `git status --short` | clean (after Phase 7 commit) |

## 13. Remaining blockers

Soft, sprint-independent:

- **Local SQLite candle store absent.** Any backtest run by a
  future evidence sprint requires either (a) rehydrating the
  OANDA-practice H4 store with explicit human credentialed-run
  authorization (via
  [`DATA_REHYDRATION_RUNBOOK.md`](DATA_REHYDRATION_RUNBOOK.md)),
  or (b) the evidence sprint shipping its own data-restore
  step.
- **MODELED financing unavailable.** Live promotion blocked
  pending a credentialed-pilot capture sprint that produces
  ≥ 60 reconciled `DAILY_FINANCING` events and a human
  approval flipping the MODELED slot.
- **Independent corroboration coverage.** The free/local
  parity verifier currently covers `trend_following` only;
  extending coverage to `session_breakout` is a separate
  future verifier-side sprint. The candidate's deterministic
  reproducibility is a partial substitute; the future paper-
  promotion reviewer chooses between accepting it for v1 or
  opening a verifier-extension sprint first.
- **11 pre-existing UP042 ruff hints** in
  `research/{walk_forward,financing,parity_verifier}/models.py`
  + `research/lean_parity/algorithms/...`. Not introduced by
  this sprint.

## 14. Recommended next branch

**`research-asian-london-session-breakout-walk-forward-001`** —
the evidence sprint that:

1. Restores the OANDA-practice H4 candle store (with explicit
   human credentialed-run authorization), OR documents the
   data restore as a prerequisite blocker.
2. Regenerates the authoritative walk-forward plan and commits
   `backtests/CAMPAIGN_010_session_breakout/walk_forward/plan.{json,md}`.
3. Drives per-fold backtests via the bespoke `BacktestEngine`
   and commits per-fold artifacts + an aggregate
   `WalkForwardResults`.
4. Computes the financing overlay via
   `research.financing.calculate_run` with
   `default_stress_rate_source()` and commits
   `backtests/CAMPAIGN_010_session_breakout/financing/financing_run.{json,md}`.
5. Computes the portfolio-risk diagnostic checklist.
6. Writes the campaign report
   (`backtests/CAMPAIGN_010_SESSION_BREAKOUT_REPORT.md`).
7. Updates `docs/research/EVIDENCE_MANIFEST.json` with a row
   carrying `strategy_approved: false`.
8. Updates `docs/research/STRATEGY_STATUS.md` to flip the
   status from `candidate-scaffold (no verdict)` to either
   `PASS-candidate (awaiting human approval)` or `rejected`,
   per the verdict.

Alternative branches (if the human reviewer wants to address a
prerequisite first):

- `research-financing-multi-year-fixture-expansion-001` —
  extend per-pair `TableRateSource` fixtures to the full
  2020–2026 universe (optional; current plan uses
  `default_stress_rate_source()`).
- `infra-ruff-up042-stress-enum-001` — clean up the 11
  pre-existing UP042 hints.
- `research-financing-modeled-capture-credentialed-001` —
  separately-authorized credentialed capture sprint required
  before MODELED can become available (required before any
  candidate can be live-promoted; not required for the
  CAMPAIGN_010 walk-forward to produce ESTIMATED evidence).

## 15. Exact files to review first

For the next reviewer / future-sprint operator:

1. [`ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md)
   — Phase 0 sprint plan + repo audit.
2. [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md)
   — machine-facing rule table the strategy module implements
   verbatim.
3. [`src/forex_bot/strategies/session_breakout.py`](../../src/forex_bot/strategies/session_breakout.py)
   — the strategy module.
4. [`src/forex_bot/config.py`](../../src/forex_bot/config.py)
   — `SessionBreakoutStrategyConfig` + `StrategyConfig.session_breakout`.
5. [`tests/unit/test_session_breakout.py`](../../tests/unit/test_session_breakout.py)
   — 33 unit + structural-audit tests.
6. [`configs/campaign_010_session_breakout.yaml`](../../configs/campaign_010_session_breakout.yaml)
   — research candidate config.
7. [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
   — the candidate's pre-commit / evaluation checklist (binding
   on the future evidence sprint).
8. [`CAMPAIGN_010_SMOKE_RESULT.md`](CAMPAIGN_010_SMOKE_RESULT.md)
   — non-evidence smoke results.
9. [`CAMPAIGN_010_WALK_FORWARD_READINESS.md`](CAMPAIGN_010_WALK_FORWARD_READINESS.md)
   — walk-forward integration readiness.
10. [`CAMPAIGN_010_FINANCING_RISK_READINESS.md`](CAMPAIGN_010_FINANCING_RISK_READINESS.md)
    — financing + risk readiness.
11. (this doc) — sprint summary.

For standing safety state:

- [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
- [`docs/research/STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
  (now includes the candidate-scaffold row)
- [`docs/research/FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`docs/research/STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)

## 16. Cross-links

- [`ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md)
- [`CAMPAIGN_010_SMOKE_RESULT.md`](CAMPAIGN_010_SMOKE_RESULT.md)
- [`CAMPAIGN_010_WALK_FORWARD_READINESS.md`](CAMPAIGN_010_WALK_FORWARD_READINESS.md)
- [`CAMPAIGN_010_FINANCING_RISK_READINESS.md`](CAMPAIGN_010_FINANCING_RISK_READINESS.md)
- [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
