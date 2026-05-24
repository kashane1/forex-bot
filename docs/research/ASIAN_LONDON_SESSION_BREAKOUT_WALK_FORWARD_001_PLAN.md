# Asian-London Session Breakout — Walk-Forward Evidence Sprint Plan

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-walk-forward-001`
`strategy_evidence: false`

Phase 0 truth audit + sprint plan for the **first evidence-grade
local research evaluation** of CAMPAIGN_010 / `session_breakout
0.1.0-c010` (the Asian-range / London-open breakout research
candidate).

**This document does not approve the candidate, does not assert a
verdict, and does not authorize paper / demo / live trading.** It
records the repo state and the pipeline this sprint will run.

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked. Even a clean walk-forward verdict
> from this sprint only produces *research evidence* — the
> human-approval gate per
> [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
> stands.

## 1. Repo state (Phase 0 audit)

| dimension | value |
|---|---|
| current branch | `claude/affectionate-fermi-d950fc` (the worktree of `research-asian-london-session-breakout-walk-forward-001`) |
| base commit | `801c98a` — Phase 7 of the prior scaffold sprint (`research-asian-london-session-breakout-001`) |
| worktree path | `/Users/kashane/dev/forex-bot/.claude/worktrees/affectionate-fermi-d950fc/` |
| `git status` at Phase 0 start | clean |
| `configs/approved_strategies.yaml` | `approved: []` (unchanged) |
| CAMPAIGN_002 status | REJECT (unchanged; untouched) |
| CAMPAIGN_010 status | candidate-scaffold (no verdict) — see [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md) |
| paper-loop / demo-loop | refuse — verified |
| live-loop | does not exist — verified |
| QuantConnect / LEAN | retired; not used |

### 1.1 Baseline validation results

| check | result |
|---|---|
| `python -m pytest -q` | **735 passed** in 2.73s |
| `ruff check src tests scripts research` | **11 pre-existing UP042 findings** in untouched files (research/parity_verifier/models.py, research/walk_forward/models.py, research/financing/models.py, research/lean_parity/algorithms/...). Matches the prior sprint's documented baseline. Not refactored here per "no scope creep" rule. |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED (143 evidence-index links resolve, 2005 artifact files clean) |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED (registry empty, loops refuse, archive valid, no credentials) |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED (pattern scan over 2063 files; no credential value or shape) |
| `python -m forex_bot.cli paper-loop -c configs/paper.yaml` | refused (registry empty) |
| `python -m forex_bot.cli demo-loop -c configs/practice.yaml` | refused (registry empty) |
| `python -m forex_bot.cli --help` | no `live-loop` command present |

### 1.2 Files inspected (read-only)

Strategy + config:

- [`src/forex_bot/strategies/session_breakout.py`](../../src/forex_bot/strategies/session_breakout.py)
- [`src/forex_bot/strategies/__init__.py`](../../src/forex_bot/strategies/__init__.py)
- [`src/forex_bot/config.py`](../../src/forex_bot/config.py)
- [`configs/campaign_010_session_breakout.yaml`](../../configs/campaign_010_session_breakout.yaml)
- [`tests/unit/test_session_breakout.py`](../../tests/unit/test_session_breakout.py)

Existing infrastructure:

- [`research/walk_forward/__init__.py`](../../research/walk_forward/__init__.py),
  `models.py`, `splits.py`, `validate.py`, `reporting.py`
- [`research/financing/__init__.py`](../../research/financing/__init__.py),
  `models.py`, `rates.py`, `calculator.py`, `reporting.py`,
  `fixtures.py`, `fixtures/`
- [`scripts/run_walk_forward_dry_run.py`](../../scripts/run_walk_forward_dry_run.py)
- [`scripts/run_campaign_009.py`](../../scripts/run_campaign_009.py)
  (template for per-fold runner pattern; same engine wiring this
  sprint will adapt for fold ranges)
- [`scripts/rehydrate_oanda_h4_store.py`](../../scripts/rehydrate_oanda_h4_store.py)
  (read-only fetch; verified to support `--verify` without
  credentials)
- [`scripts/prepare_local_research_data.py`](../../scripts/prepare_local_research_data.py)
  (orchestrator; refuses live, never prints credentials)
- [`src/forex_bot/backtesting/engine.py`](../../src/forex_bot/backtesting/engine.py)
  (BacktestEngine signature confirmed)

Authoritative docs:

- [`ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md)
- [`CAMPAIGN_010_SMOKE_RESULT.md`](CAMPAIGN_010_SMOKE_RESULT.md)
- [`CAMPAIGN_010_WALK_FORWARD_READINESS.md`](CAMPAIGN_010_WALK_FORWARD_READINESS.md)
- [`CAMPAIGN_010_FINANCING_RISK_READINESS.md`](CAMPAIGN_010_FINANCING_RISK_READINESS.md)
- [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`DATA_REHYDRATION_RUNBOOK.md`](DATA_REHYDRATION_RUNBOOK.md)
- [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)

## 2. Candidate scaffold status

Verified inherited from the prior sprint:

- `session_breakout 0.1.0-c010` is implemented as a `Strategy`
  protocol implementation (no broker imports, no engine edits).
- `StrategyConfig.session_breakout` slot present + frozen
  config-load smoke passing.
- 33 unit + structural-audit tests pass against
  `tests/unit/test_session_breakout.py`.
- The candidate is **not** in
  [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml).
- Frozen parameters per
  [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
  §5 are unchanged and will be enforced by this sprint via a
  runner-side guard.

## 3. Local data status

| dimension | value |
|---|---|
| expected store path (per CAMPAIGN_010 YAML) | `./data/campaign_002.sqlite3` |
| store in worktree at start | absent (`data/` had only `.gitkeep`) |
| store at the main checkout | present at `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` (115 MB) |
| action taken | created a **gitignored symlink** in the worktree: `data/campaign_002.sqlite3 → /Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` |
| verified pairs (per `CandleRepo.list(... 'H4', completed_only=True)`) | EUR_USD (9931), GBP_USD (9931), USD_JPY (9932), AUD_USD (9931), USD_CAD (9931), USD_CHF (9931), NZD_USD (9935) |
| coverage window per pair | first `2020-01-01T22:00:00+00:00`, last `2026-05-19T21:00:00+00:00` |
| recorded provenance source | `oanda-practice` (all pairs) |
| instrument metadata (`InstrumentRepo.get`) | present for all 7 pairs (pip_location / display_precision verified) |
| credential-shaped output during inspection | none (the audit uses repo read-only Python; never reads `.env`, never calls OANDA) |
| commit of the symlink | the symlink itself is under `/data/` → matched by `.gitignore` (`/data/` line 52 + `*.sqlite3` line 56); `git status --short` shows clean (verified) |
| credentials used for the inspection | none |

**Conclusion: no rehydration is required.** All 7 CAMPAIGN_010
pairs are already present in the local store at the main
checkout, sourced from `oanda-practice`, spanning the design's
2020-01-01 → 2026-05-20 universe. This sprint will reuse that
store via the gitignored symlink. **No OANDA call is made, no
credential is read, no rehydrate script runs.**

The standing read-only candle-data authorization (the rule the
human granted at sprint kickoff) is **honored by not exercising
it** — the data is already on disk and provably real OANDA
practice candles.

## 4. Sprint phases

| phase | scope | output |
|---|---|---|
| 0 (this doc) | Repo truth + sprint plan | `ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_PLAN.md` |
| 1 | Data provenance — record what's in the symlinked store; verify no committed bulk | `CAMPAIGN_010_DATA_PROVENANCE.md` |
| 2 | Authoritative walk-forward plan generation via `scripts/run_walk_forward_dry_run.py` (`--campaign-name CAMPAIGN_010`) → committed `backtests/CAMPAIGN_010_session_breakout/walk_forward/{plan.json,plan.md}` | `CAMPAIGN_010_WALK_FORWARD_PLAN.md` |
| 3 | Per-fold local backtest execution via a new `scripts/run_campaign_010.py` (mirrors `run_campaign_009.py`; honors fold windows from the plan; bespoke `BacktestEngine` + `RiskEngine(mode='backtest')`; per-fold per-pair runs) → committed compact summary tables (bulky CSV/JSON dumps kept under `backtests/CAMPAIGN_010_session_breakout/folds/<n>/` and gitignored where applicable) | `CAMPAIGN_010_WALK_FORWARD_EXECUTION.md` |
| 4 | Aggregate fold metrics, evaluate every gate from `CAMPAIGN_010_PRECOMMIT_CHECKLIST.md` §10, render `WalkForwardResults` JSON + Markdown via `research.walk_forward.render_results_md`, classify research verdict | `CAMPAIGN_010_WALK_FORWARD_RESULT.md` + `walk_forward/results.json` + `walk_forward/results.md` |
| 5 | Financing overlay via `research.financing.calculate_run(positions, default_stress_rate_source())`; MODELED remains refused | `CAMPAIGN_010_FINANCING_OVERLAY.md` + `financing/financing_run.{json,md}` |
| 6 | Portfolio-risk diagnostics — pair concentration, exposure trace, drawdown clustering, RiskEngine rejection table | `CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md` |
| 7 | Free / local independent verifier readiness — capability assessment vs `session_breakout`; do not claim corroboration unless the verifier actually runs | `CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md` |
| 8 | Update `CAMPAIGN_010_STATUS.md`, `STRATEGY_STATUS.md`, `EVIDENCE_INDEX.md`, `EVIDENCE_MANIFEST.json`; write `CAMPAIGN_010_EVIDENCE_SUMMARY.md` + `ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md`; final validation suite | sprint summary + updated indices |

Commits at the end of each phase.

## 5. Expected commands (Phase 2–8)

```bash
# Phase 2 — plan generation.
.venv/bin/python scripts/run_walk_forward_dry_run.py \
    --campaign-name CAMPAIGN_010 \
    --universe-start 2020-01-01 --universe-end 2026-05-20 \
    --style rolling --parameter-mode frozen \
    --train-days 540 --validation-days 180 --test-days 180 \
    --step-days 180 \
    --output backtests/CAMPAIGN_010_session_breakout/walk_forward/

# Phase 3 — per-fold backtest execution.
.venv/bin/python scripts/run_campaign_010.py \
    --config configs/campaign_010_session_breakout.yaml \
    --plan backtests/CAMPAIGN_010_session_breakout/walk_forward/plan.json \
    --out backtests/CAMPAIGN_010_session_breakout/

# Phase 4 — aggregate + render results (driven by run_campaign_010 in
# --phase aggregate, writes walk_forward/results.json + .md).

# Phase 5 — financing overlay (driven by run_campaign_010 in
# --phase financing, writes financing/financing_run.{json,md}).

# Phase 6 — portfolio-risk diagnostics (driven by run_campaign_010 in
# --phase risk, writes risk/diagnostics.{json,md}).

# Phase 7 — verifier capability check (read-only inspection of
# research.parity_verifier interfaces; no run unless capability +
# safety both green).

# Phase 8 — final validation (suite repeated; status docs updated).
```

## 6. Validation plan

After every commit:

- `python -m pytest -q` (unit + integration; expect ≥ 735 → ≥ 735 +
  any new tests added by this sprint)
- `ruff check src tests scripts research` — must not introduce any
  new finding; the 11 pre-existing UP042 findings remain documented
  and untouched
- `python scripts/validate_research_archive.py` — must remain PASS
- `python scripts/check_research_freeze.py` — must remain PASS
- `python scripts/scan_artifacts_for_secrets.py` — must remain PASS

Loops + CLI surface checks repeated at Phase 8.

## 7. Gates this sprint will evaluate (verbatim references)

Every per-fold + aggregate gate from
[`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
§10 is binding. The pre-commit-checklist values are the authority;
the runner will report the gate vector unmodified. No gate is
relaxed after seeing results — this is a load-bearing rule under
the protocol.

## 8. Non-goals (explicit)

- **No tuning.** Frozen-parameter mode only. The strategy version
  remains `0.1.0-c010`. Any code change required to *execute* (not
  to *tune*) the strategy is a bug fix and will be called out.
- **No CAMPAIGN_002 revival.** CAMPAIGN_002 is REJECT and stays
  REJECT. Its candle store is reused as data, not its strategy or
  parameters.
- **No paper / demo / live promotion.** Even a clean PASS produces
  research-only evidence. The candidate cannot enter
  `configs/approved_strategies.yaml` from this sprint.
- **No QuantConnect / LEAN action.** Retired.
- **No order submission.** No broker call. No `.env` read. No
  credential printed.
- **No new dependency.** Only the existing pip-installed stack is
  used.
- **No engine-PnL change.** Financing is an overlay on top of
  engine output; the engine PnL formula is unchanged.

## 9. Safety invariants

- `configs/approved_strategies.yaml`: **`approved: []`** (verified;
  remains).
- **CAMPAIGN_002 REJECT** — verdict frozen; only the candle store
  is reused.
- **Paper / demo / live blocked.** `paper-loop` and `demo-loop`
  refuse. No `live-loop` command.
- **No broker / OANDA call** this sprint — the existing
  symlinked store covers the entire 7-pair × 6-year universe.
- **No `.env` read; no credential printed; no broker account
  endpoint queried** (no orders, no trades, no positions, no
  transactions).
- **No QuantConnect / LEAN.**
- **No bespoke-engine edit.** No `src/forex_bot/financing.py`
  edit.
- **No `MODELED` financing** — overlay uses
  `default_stress_rate_source()` (ESTIMATED + conservative
  stress); the four-layer MODELED refusal stands.
- **Bulky artifacts uncommitted.** Per-fold CSV/JSON dumps stay
  under `backtests/CAMPAIGN_010_session_breakout/folds/` and rely
  on the `/data/`, `*.sqlite3`, and (if added) `backtests/**/*.csv`
  gitignore rules; only compact summary docs + a manifest are
  committed.

## 10. Explicit no-approval statements

1. **This sprint cannot approve CAMPAIGN_010.** Approval is a
   deliberate human action with a documented `ApprovalEntry` per
   [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).
2. **A passing walk-forward verdict is not paper/demo readiness.**
   It is item 3 of the six-evidence ladder in
   [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
   §8.
3. **A passing financing-overlay diagnostic is not MODELED
   financing.** It is ESTIMATED + conservative-stress under
   [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md);
   MODELED remains refused.
4. **The verifier status doc is not independent corroboration**
   unless the verifier actually runs against the candidate's
   trade artifacts under its declared tolerances.

## 11. Cross-links

- [`ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md)
- [`CAMPAIGN_010_WALK_FORWARD_READINESS.md`](CAMPAIGN_010_WALK_FORWARD_READINESS.md)
- [`CAMPAIGN_010_FINANCING_RISK_READINESS.md`](CAMPAIGN_010_FINANCING_RISK_READINESS.md)
- [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`DATA_REHYDRATION_RUNBOOK.md`](DATA_REHYDRATION_RUNBOOK.md)
- [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
