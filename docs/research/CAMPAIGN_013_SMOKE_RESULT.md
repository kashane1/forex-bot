# CAMPAIGN_013 Smoke Result — `cross_pair_currency_strength_rotation 0.1.0-c013`

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-001`
`strategy_evidence: false`

Phase 5 NON-EVIDENCE smoke for the CAMPAIGN_013 scaffold. **This is
not strategy evidence.** It proves the scaffold loads, the strategy
instantiates, the unit tests pass, and the walk-forward dry-run plan
produces the expected 8-fold structure — nothing more.

> No backtest fired. No broker call. No credentials read. No data
> fetched. No `.env` accessed. No strategy approved.
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_002 / 010 / 011 / 012 remain REJECT and untouched.
> CAMPAIGN_011 is the **null baseline only**, not a trading
> candidate.

## 1. Commands run

| command | purpose | result |
|---|---|---|
| `python -c "from forex_bot.config import load_settings; s = load_settings('configs/campaign_013_cross_pair_currency_strength_rotation.yaml')"` | config-load smoke | **PASS** — all 9 frozen parameters parse to the expected types + values; `app.mode = paper`; `trading_enabled = false`; `allow_order_submission = false`; `allow_live_trading = false`; `strategy.enabled = ['cross_pair_currency_strength_rotation']`; `risk.max_open_positions = 1`; `risk.max_positions_per_instrument = 1` |
| `python -c "from forex_bot.strategies import CrossPairCurrencyStrengthRotationStrategy; s = CrossPairCurrencyStrengthRotationStrategy(); print(s.name, s.version, s.warmup_bars_required())"` | import / instantiation smoke | **PASS** — `cross_pair_currency_strength_rotation 0.1.0-c013 50` |
| `python -m pytest tests/unit/test_cross_pair_currency_strength_rotation.py -q` | targeted unit suite | **PASS** — 57 passed in 0.13 s |
| `python -m pytest -q` | full repo regression | **PASS** — 875 passed in 3.65 s (818 baseline + 57 new) |
| `python scripts/run_walk_forward_dry_run.py --campaign-name CAMPAIGN_013_cross_pair_currency_strength_rotation --style rolling --parameter-mode frozen --train-days 540 --validation-days 180 --test-days 180 --step-days 180 --universe-start 2020-01-01 --universe-end 2026-05-20 --output /tmp/campaign_013_smoke_dry_run` | future walk-forward fold-count check (plan-only; no strategy execution) | **PASS** — 8 folds emitted, identical to CAMPAIGN_010 / 011 / 012 plans verbatim |
| `python scripts/validate_research_archive.py` | research-archive validator | **PASS** |
| `python scripts/check_research_freeze.py` | freeze-gate validator | **PASS** (loops refuse) |
| `python scripts/scan_artifacts_for_secrets.py` | credential scanner | **PASS** |
| `ruff check src tests scripts research` | repo-wide lint | 3 pre-existing in `research/lean_parity/algorithms/`; unchanged from baseline |

## 2. Walk-forward dry-run plan (NOT EVIDENCE)

The plan-only output written to `/tmp/campaign_013_smoke_dry_run/`
(deliberately under `/tmp`; not committed):

- Style: `rolling`. Parameter mode: `frozen`. Fold count: **8** —
  matches CAMPAIGN_010 / 011 / 012 verbatim.
- Universe: 2020-01-01 → 2026-05-20.

**The dry-run produced no strategy evidence.** It only produces a
machine-readable fold-boundary plan that the future evidence sprint
can hand to the per-fold runner. It does not load any candles, does
not run any backtest, does not call any broker, does not read `.env`.

## 3. What passed

- Strategy module imports cleanly.
- Strategy instantiates with defaults (`name = "cross_pair_currency_strength_rotation"`,
  `version = "0.1.0-c013"`, `warmup_bars_required() = 50`).
- Config schema accepts the candidate YAML verbatim.
- All 9 frozen parameters round-trip through `load_settings()`
  exactly.
- Targeted unit-test suite (57 cases) passes in 0.13 s.
- Full repo pytest suite (875 cases) passes in 3.65 s.
- Walk-forward dry-run plan produces 8 folds matching CAMPAIGN_010 /
  011 / 012.
- Research-archive validator, freeze-gate validator, and credential
  scanner all pass.

## 4. What was NOT run

- **No historical backtest.** Phase 5 protocol prohibits any
  strategy-evidence run on real data.
- **No walk-forward strategy execution.** Only the plan was generated
  (no per-fold runner invocation; no `BacktestEngine.run()` call on
  any pair).
- **No financing overlay.** Financing calculator untouched.
- **No portfolio-risk diagnostics.** Risk-diagnostics pipeline
  untouched.
- **No independent verifier.** Verifier is capability-locked to
  CAMPAIGN_002 and was not run.
- **No cross-pair runner orchestration test against real data.** The
  cross-pair runner is the future evidence sprint's deliverable; this
  scaffold sprint exercises the strategy's `ctx.config["cross_pair_closes"]`
  contract only via synthetic fixtures in the unit tests.
- **No data fetch.** No OANDA HTTP call; no `fetch-candles`
  invocation; `data/campaign_002.sqlite3` was not opened by this
  sprint.
- **No `.env` read.** No credential file or environment variable
  accessed.
- **No `paper-loop` / `demo-loop` invocation except the standing
  refusal check.** No broker session opened; no orders submitted.

## 5. Is the smoke evidence?

**No.** A passing config-load + import + unit-test suite + plan
dry-run is the **lowest tier** of validation; it proves the scaffold
is *structurally well-formed*, not that the strategy has edge.

The only way to produce strategy evidence is to run the future
`research-cross-pair-currency-strength-rotation-walk-forward-001`
evidence sprint with the full ladder:

1. Walk-forward execution on the real 7-pair × 6-year H4 store
   (with the cross-pair runner orchestration injecting
   `cross_pair_closes` into each pair's `strategy_config`).
2. Financing overlay (ESTIMATED + conservative stress; MODELED
   refused at 4 layers).
3. Portfolio-risk diagnostics (standard battery + CAMPAIGN_013-
   specific rank-gap / simultaneous-signal / rejection-rate
   diagnostics).
4. Null-baseline comparison vs CAMPAIGN_011.
5. Independent-verifier corroboration (required for paper promotion
   only; via the suggested follow-up sprint
   `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001`).
6. A deliberate human approval action per
   [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

This sprint produces **none** of those.

## 6. Was any broker call made?

**No.** Verified by:

- No broker / OANDA HTTP request issued by any command above.
- The strategy module imports nothing from `forex_bot.broker` /
  `forex_bot.execution` / `forex_bot.loops` (verified by source-grep
  unit tests in Phase 3).
- `paper-loop` and `demo-loop` were invoked only to confirm refusal;
  both refused at the `approved_strategies.yaml` gate before any
  broker code path was reached.
- The walk-forward dry-run is plan-only; it does not load any
  candles and does not call any broker.

## 7. Were any credentials read?

**No.** Verified by:

- `scan_artifacts_for_secrets.py` PASSED on 2,456 committed artifact
  files.
- The smoke commands did not source `.env` or set any credential
  environment variable.
- The strategy module does not import `os.environ` directly; it
  receives config via `ctx.config: dict` only.

## 8. Was any data fetched?

**No.** Verified by:

- No `python -m forex_bot.cli fetch-candles ...` call.
- No OANDA HTTP request to `/v3/instruments/.../candles`.
- The walk-forward dry-run is plan-only; it does not open
  `data/campaign_002.sqlite3`.
- The Phase 3 unit tests use only synthetic in-memory `pd.Series`
  fixtures (no DB / no disk reads).

## 9. Explicit no-approval statement

This smoke result **cannot approve any strategy**.
`configs/approved_strategies.yaml` remains `approved: []` and the
candidate is not enabled in any active loop. Approval requires the
full six-evidence ladder + a deliberate human approval action per
[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md); none
of those have happened.

## 10. Local files created but not committed

| path | committed? | reason |
|---|:---:|---|
| `/tmp/campaign_013_smoke_dry_run/plan.json` | **no** | scratch dry-run output; deliberately under `/tmp` |
| `/tmp/campaign_013_smoke_dry_run/plan.md` | **no** | same |

The dry-run plan path is **deliberately** under `/tmp` so it does
not appear in `git status` and cannot be accidentally staged.

## 11. Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_013_STATUS.md`](CAMPAIGN_013_STATUS.md)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_READINESS.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_READINESS.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
