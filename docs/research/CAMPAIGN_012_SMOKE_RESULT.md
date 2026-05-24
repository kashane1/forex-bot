# CAMPAIGN_012 Smoke Result — `regime_switcher_atr_percentile 0.1.0-c012`

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-001`
`strategy_evidence: false`

Phase 5 NON-EVIDENCE smoke for the CAMPAIGN_012 scaffold. **This is not
strategy evidence.** It proves the scaffold loads, the strategy
instantiates, the unit tests pass, and the walk-forward dry-run plan
produces the expected 8-fold structure — nothing more.

> No backtest fired. No broker call. No credentials read. No data
> fetched. No `.env` accessed. No strategy approved.
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_002 / 010 / 011 remain REJECT and untouched. CAMPAIGN_011
> is the **null baseline only**, not a trading candidate.

## 1. Commands run

| command | purpose | result |
|---|---|---|
| `python -c "from forex_bot.config import load_settings; s = load_settings('configs/campaign_012_regime_switcher_atr_percentile.yaml')"` | config-load smoke | **PASS** — all 12 frozen parameters parse to the expected types + values; `app.mode = paper`; `trading_enabled = false`; `allow_order_submission = false`; `allow_live_trading = false`; `strategy.enabled = ['regime_switcher_atr_percentile']`; `risk.max_open_positions = 1`; `risk.max_positions_per_instrument = 1` |
| `python -c "from forex_bot.strategies import RegimeSwitcherAtrPercentileStrategy; s = RegimeSwitcherAtrPercentileStrategy(); print(s.name, s.version, s.warmup_bars_required())"` | import / instantiation smoke | **PASS** — `regime_switcher_atr_percentile 0.1.0-c012 500` |
| `python -m pytest tests/unit/test_regime_switcher_atr_percentile.py -q` | targeted unit suite | **PASS** — 47 passed in 0.35 s |
| `python -m pytest -q` | full repo regression | **PASS** — 818 passed in 3.33 s (771 baseline + 47 new) |
| `python scripts/run_walk_forward_dry_run.py --campaign-name CAMPAIGN_012_regime_switcher_atr_percentile --style rolling --parameter-mode frozen --train-days 540 --validation-days 180 --test-days 180 --step-days 180 --universe-start 2020-01-01 --universe-end 2026-05-20 --output /tmp/campaign_012_smoke_dry_run` | future walk-forward fold-count check (plan-only; no strategy execution) | **PASS** — 8 folds emitted, identical to CAMPAIGN_010 / CAMPAIGN_011 plans verbatim |
| `python scripts/validate_research_archive.py` | research-archive validator | **PASS** |
| `python scripts/check_research_freeze.py` | freeze-gate validator | **PASS** (loops refuse) |
| `python scripts/scan_artifacts_for_secrets.py` | credential scanner | **PASS** |
| `ruff check src tests scripts research` | repo-wide lint | 3 pre-existing in `research/lean_parity/algorithms/`; unchanged from baseline |

## 2. Walk-forward dry-run plan (NOT EVIDENCE)

The plan-only output written to `/tmp/campaign_012_smoke_dry_run/`
(deliberately under `/tmp`; not committed; gitignored by location):

| fold | train | validation | test |
|---|---|---|---|
| 0 | 2020-01-01 → 2021-06-23 | 2021-06-24 → 2021-12-20 | 2021-12-21 → 2022-06-18 |
| 1 | 2020-06-29 → 2021-12-20 | 2021-12-21 → 2022-06-18 | 2022-06-19 → 2022-12-15 |
| 2 | 2020-12-26 → 2022-06-18 | 2022-06-19 → 2022-12-15 | 2022-12-16 → 2023-06-13 |
| 3 | 2021-06-24 → 2022-12-15 | 2022-12-16 → 2023-06-13 | 2023-06-14 → 2023-12-10 |
| 4 | 2021-12-21 → 2023-06-13 | 2023-06-14 → 2023-12-10 | 2023-12-11 → 2024-06-07 |
| 5 | 2022-06-19 → 2023-12-10 | 2023-12-11 → 2024-06-07 | 2024-06-08 → 2024-12-04 |
| 6 | 2022-12-16 → 2024-06-07 | 2024-06-08 → 2024-12-04 | 2024-12-05 → 2025-06-02 |
| 7 | 2023-06-14 → 2024-12-04 | 2024-12-05 → 2025-06-02 | 2025-06-03 → 2025-11-29 |

Style: `rolling`. Parameter mode: `frozen`. Fold count: **8** —
matches CAMPAIGN_010 / CAMPAIGN_011 verbatim. The validator
(`research.walk_forward.validate.validate_plan`) passes.

**The dry-run produced no strategy evidence.** It only produces a
machine-readable plan that the future evidence sprint can hand to the
per-fold runner. It does not load any candles, does not run any
backtest, does not call any broker, does not read `.env`.

## 3. What passed

- Strategy module imports cleanly.
- Strategy instantiates with defaults (`name = "regime_switcher_atr_percentile"`,
  `version = "0.1.0-c012"`, `warmup_bars_required() = 500`).
- Config schema accepts the candidate YAML verbatim.
- All 12 frozen parameters round-trip through `load_settings()`
  exactly (see Phase 4 commit message for the verbatim print-out).
- Targeted unit-test suite (47 cases) passes in 0.35 s.
- Full repo pytest suite (818 cases) passes in 3.33 s.
- Walk-forward dry-run plan produces 8 folds matching CAMPAIGN_010 /
  CAMPAIGN_011.
- Research-archive validator, freeze-gate validator, and credential
  scanner all pass.

## 4. What was NOT run

- **No historical backtest.** The Phase 5 protocol prohibits any
  strategy-evidence run on real data.
- **No walk-forward strategy execution.** Only the plan was generated
  (no per-fold runner invocation; no `BacktestEngine.run()` call on
  any pair).
- **No financing overlay.** The financing calculator is untouched.
- **No portfolio-risk diagnostics.** The risk-diagnostics pipeline is
  untouched.
- **No independent verifier.** The verifier is capability-locked to
  CAMPAIGN_002 and was not run.
- **No data fetch.** No OANDA HTTP call; no `fetch-candles` invocation;
  `data/campaign_002.sqlite3` was not opened by this sprint.
- **No `.env` read.** No credential file or environment variable was
  accessed for value.
- **No `paper-loop` / `demo-loop` invocation except the standing
  refusal check.** No broker session opened; no orders submitted.

## 5. Is the smoke evidence?

**No.** A passing config-load + import + unit-test suite + plan dry-run
is the **lowest tier** of validation; it proves the scaffold is
*structurally well-formed*, not that the strategy has edge.

The only way to produce strategy evidence is to run the future
`research-regime-switcher-atr-percentile-walk-forward-001` evidence
sprint with the full ladder:

1. Walk-forward execution on the real 7-pair × 6-year H4 store.
2. Financing overlay (ESTIMATED + conservative stress; MODELED
   refused at 4 layers).
3. Portfolio-risk diagnostics.
4. Null-baseline comparison vs CAMPAIGN_011 per
   [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md).
5. Independent-verifier corroboration (required for paper promotion
   only; via the suggested follow-up sprint
   `infra-free-local-parity-verifier-regime-switcher-001`).
6. A deliberate human approval action per
   [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

This sprint produces **none** of those.

## 6. Was any broker call made?

**No.** Verified by:

- No broker / OANDA HTTP request was issued by any command above.
- The strategy module imports nothing from `forex_bot.broker` /
  `forex_bot.execution` / `forex_bot.loops` (verified by source-grep
  unit tests in Phase 3).
- `paper-loop` and `demo-loop` were invoked only to confirm refusal;
  both refused at the `approved_strategies.yaml` gate before any
  broker code path was reached.
- The walk-forward dry-run is plan-only; it does not load any candles
  and does not call any broker.

## 7. Were any credentials read?

**No.** Verified by:

- `scan_artifacts_for_secrets.py` PASSED on 2302 committed artifact
  files (no credential-shaped strings).
- The smoke commands did not source `.env` or set any credential
  environment variable.
- The strategy module does not import `os.environ` directly; it
  receives config via `ctx.config: dict` only.

## 8. Was any data fetched?

**No.** Verified by:

- No `python -m forex_bot.cli fetch-candles ...` call.
- No OANDA HTTP request to `/v3/instruments/.../candles`.
- The walk-forward dry-run is plan-only; it does not open
  `data/campaign_002.sqlite3` (it computes fold boundaries from CLI
  arguments).
- The Phase 3 unit tests use only synthetic in-memory `Candle`
  fixtures (no DB / no disk reads).

## 9. Explicit no-approval statement

This smoke result **cannot approve any strategy**.
`configs/approved_strategies.yaml` remains `approved: []` and the
candidate is not enabled in any active loop. Approval requires the
full six-evidence ladder + a deliberate human approval action per
[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md);
none of those have happened.

## 10. Local files created but not committed

| path | committed? | reason |
|---|:---:|---|
| `/tmp/campaign_012_smoke_dry_run/plan.json` | **no** | scratch dry-run output; deliberately under `/tmp` to avoid accidental commit |
| `/tmp/campaign_012_smoke_dry_run/plan.md` | **no** | same |

The dry-run plan path is **deliberately** under `/tmp` so it does not
appear in `git status` and cannot be accidentally staged.

## 11. Cross-links

- [`REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md)
- [`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_012_STATUS.md`](CAMPAIGN_012_STATUS.md)
- [`REGIME_SWITCHER_ATR_PERCENTILE_READINESS.md`](REGIME_SWITCHER_ATR_PERCENTILE_READINESS.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
