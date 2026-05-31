# `research-regime-switcher-atr-percentile-001` — Sprint Plan (Phase 0)

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-001`
(worktree branch `claude/affectionate-fermi-d950fc`) · `strategy_evidence: false`

Phase 0 repo truth audit + 8-phase scaffold plan for **CAMPAIGN_012 /
`regime_switcher_atr_percentile 0.1.0-c012`** — the C3 daily-ATR-percentile
regime-switcher real candidate selected by the
[`research-new-candidate-strategy-discovery-003`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md)
discovery sprint. **Scaffold sprint only — no historical backtest, no
walk-forward evidence, no broker call, no approval.**

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 remain
> REJECT. `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_011 is **only the null baseline**, not a trading candidate.
> This scaffold sprint **cannot approve any strategy** — even a clean
> unit-test suite or smoke pass is **not** evidence. The future evidence
> sprint must run walk-forward, null-baseline comparison, financing
> overlay, risk diagnostics, and verifier status before any research
> verdict exists; any approval requires the full six-evidence ladder +
> a deliberate human approval action per
> [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

## 1. Current branch / base commit

| dimension | value |
|---|---|
| git branch (worktree) | `claude/affectionate-fermi-d950fc` |
| logical sprint branch | `research-regime-switcher-atr-percentile-001` |
| base commit (HEAD before Phase 0) | `384314a` — Phase 8 of discovery-003 (`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md` + EVIDENCE_INDEX update + STRATEGY_STATUS annotation) |
| working tree at Phase 0 start | clean (`git status --short` empty) |

## 2. Files inspected (Phase 0 audit)

**Discovery-003 binding outputs:**

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md)
- [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
- [`NEXT_PREFERRED_REAL_CANDIDATE_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_003.md)
- [`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md)
- [`NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md)
- [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md)

**Project-wide research guards:**

- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)

**Implementation patterns to mirror:**

- `src/forex_bot/strategies/session_breakout.py` (CAMPAIGN_010 scaffold reference)
- `src/forex_bot/strategies/random_entry_anchor.py` (CAMPAIGN_011 scaffold reference)
- `src/forex_bot/strategies/__init__.py` (re-export pattern)
- `src/forex_bot/strategies/base.py` (`StrategyContext` + `Strategy` protocol)
- `src/forex_bot/strategies/indicators.py` (`atr` helper used for H4 ATR)
- `src/forex_bot/config.py` (`SessionBreakoutStrategyConfig` + `RandomEntryAnchorStrategyConfig` + `StrategyConfig`)
- `src/forex_bot/backtesting/d1_aggregation.py` (`aggregate_h4_to_d1`, `D1AggregationResult`, `rollover_safe`, `AGG_GRANULARITY="D1AGG"`)
- `tests/unit/test_session_breakout.py`, `tests/unit/test_random_entry_anchor.py`
- `configs/campaign_010_session_breakout.yaml`, `configs/campaign_011_random_entry_anchor.yaml`

## 3. Repo truth summary

| dimension | value |
|---|---|
| pytest count (baseline) | **771 passed** in 3.19 s (unchanged from base commit `384314a`) |
| ruff status (baseline) | **3 pre-existing findings** in `research/lean_parity/algorithms/`: `2× RUF100` unused-noqa + `1× I001` unsorted-imports. **Untouched; will NOT be refactored** in this scaffold sprint** (out-of-scope LEAN parity archive). |
| `validate_research_archive.py` | ALL CHECKS PASSED (11 campaigns, 14 diagnostic artifacts, 195 evidence-index links, 2,300 committed artifact files clean) |
| `check_research_freeze.py` | ALL CHECKS PASSED (loops_refuse, no_credentials) |
| `scan_artifacts_for_secrets.py` | PASSED (2,511 value-scan + 2,364 pattern-scan files) |
| `paper-loop -c configs/paper.yaml` | **refused** — strategy `['trend_following']` not approved |
| `demo-loop -c configs/practice.yaml` | **refused** — strategy `['trend_following']` not approved |
| `forex_bot.cli --help` | **no `live-loop` command** present |
| `configs/approved_strategies.yaml` | `approved: []` (verified verbatim) |
| existing strategy modules | trend_following, volatility_breakout, pullback_continuation, mean_reversion, session_breakout, random_entry_anchor — **no** `regime_switcher_atr_percentile.py` yet |
| existing strategy configs | `SessionBreakoutStrategyConfig`, `RandomEntryAnchorStrategyConfig` (+ 4 older) — **no** `RegimeSwitcherAtrPercentileStrategyConfig` yet |
| D1AGG infrastructure | **present and verified** — `aggregate_h4_to_d1`, `D1AggregationResult`, `rollover_safe`, `AGG_GRANULARITY` all exported from `src/forex_bot/backtesting/d1_aggregation.py`. Public API matches the binding design from `NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md` §3. |
| existing `backtests/CAMPAIGN_012_*` artifacts | **none** — clean slate |

## 4. Current safety state (verified)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | REJECT (null-model anchor; untouched) |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | **does not exist** |
| QuantConnect / LEAN | retired |
| `MODELED` financing reachable | **no** (4 refusal layers) |
| pytest baseline | 771 passes |
| ruff baseline | 3 pre-existing in `research/lean_parity/algorithms/` (out of scope) |
| live-promotion financing blocker | stands |

## 5. CAMPAIGN_012 purpose

Build the scaffold for `regime_switcher_atr_percentile 0.1.0-c012` so the
future evidence sprint can run walk-forward against it. The C3
hypothesis (verbatim from
[`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md)
§1):

> Trend persistence on H4 OANDA practice majors is regime-conditional.
> CAMPAIGN_002 / 003 demonstrated that unconditional EMA-Donchian
> momentum lost to costs. CAMPAIGN_010 demonstrated that liquidity-flow
> session momentum also lost. CAMPAIGN_011 demonstrated that random
> entry on the same universe + cost model is essentially flat. The C3
> hypothesis is that a simple regime gate — only trade trend signals
> when the prior completed day's D1AGG ATR-14 is in the top 30 % of
> the trailing 60 completed days — turns the cost-drag headwind into
> a survivable tailwind during high-vol periods, while suppressing
> trades during low-vol regimes when costs dominate. The headline gate
> vector is inherited verbatim from CAMPAIGN_010 / CAMPAIGN_011's
> pre-commit so the comparison is on the regime-gate hypothesis alone.
> CAMPAIGN_011's metrics provide the null-baseline floor that a
> passing CAMPAIGN_012 must beat by a meaningful margin.

This sprint **scaffolds the candidate only**; it cannot demonstrate
edge. The scaffold adds the strategy module, the config schema, ≥ 30
unit tests, the candidate YAML, and the CAMPAIGN_012 readiness docs
— nothing more.

## 6. Implementation files expected

| file | action | purpose |
|---|---|---|
| `src/forex_bot/strategies/regime_switcher_atr_percentile.py` | **NEW** | `RegimeSwitcherAtrPercentileStrategy` implementing the `Strategy` protocol per R1-R8 |
| `src/forex_bot/strategies/__init__.py` | EDIT | re-export `RegimeSwitcherAtrPercentileStrategy` |
| `src/forex_bot/config.py` | EDIT | add `RegimeSwitcherAtrPercentileStrategyConfig` + `StrategyConfig.regime_switcher_atr_percentile` slot + enabled-list check |

No edits to engine, financing, RiskEngine, walk-forward harness, or any
broker / execution / loops module. No new external dependency.

## 7. Test files expected

| file | action | purpose |
|---|---|---|
| `tests/unit/test_regime_switcher_atr_percentile.py` | **NEW** | ≥ 30 deterministic unit tests covering config validation, R1-R8 rules, no-lookahead structural audit, rejected-family contamination audit, approval/safety regression |

## 8. Docs expected

| file | action | purpose |
|---|---|---|
| `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md` | **NEW** (this doc; Phase 0) | scaffold-sprint plan + repo truth + safety state |
| `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md` | **NEW** (Phase 1) | binding R1-R8 + frozen parameters + no-lookahead invariants |
| `docs/research/CAMPAIGN_012_PRECOMMIT_CHECKLIST.md` | **NEW** (Phase 4) | candidate pre-commit; null-baseline comparison gate; gate vector inherited from CAMPAIGN_010/011; UNEXPECTED-PASS playbook |
| `docs/research/CAMPAIGN_012_STATUS.md` | **NEW** (Phase 4) | scaffold-only status; CAMPAIGN_002/010/011 remain REJECT; no evidence yet |
| `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_READINESS.md` | **NEW** (Phase 4) | scaffold readiness summary; D1AGG usage; null-baseline comparison; why this is a real candidate but not approved |
| `docs/research/CAMPAIGN_012_SMOKE_RESULT.md` | **NEW** (Phase 5) | smoke commands + outputs; explicit NON-EVIDENCE framing; no broker call; no credentials read; no data fetched |
| `docs/research/CAMPAIGN_012_WALK_FORWARD_READINESS.md` | **NEW** (Phase 6) | future evidence-branch identity + inherited plan parameters |
| `docs/research/CAMPAIGN_012_FINANCING_RISK_READINESS.md` | **NEW** (Phase 6) | financing overlay (ESTIMATED + stress; MODELED refused) + risk diagnostics expectations |
| `docs/research/CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md` | **NEW** (Phase 6) | verifier capability lock; required only for an unexpected PASS; suggested future branch `infra-free-local-parity-verifier-regime-switcher-001` |
| `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md` | **NEW** (Phase 7) | end-of-scaffold summary; final validation; remaining blockers; recommended next branch (the evidence sprint) |
| `docs/research/EVIDENCE_INDEX.md` | EDIT (Phase 7) | add CAMPAIGN_012 scaffold sub-section |
| `docs/research/STRATEGY_STATUS.md` | EDIT (Phase 7) | update C3/CAMPAIGN_012 annotation to "scaffolded; awaiting evidence" |

## 9. Config files expected

| file | action | purpose |
|---|---|---|
| `configs/campaign_012_regime_switcher_atr_percentile.yaml` | **NEW** (Phase 4) | research-only loadable YAML; 7-pair H4 universe; frozen parameters from Phase 1; no paper/demo/live enablement |

## 10. Frozen parameters (binding — taken verbatim from discovery-003)

| parameter | value | notes |
|---|---|---|
| `version` | `0.1.0-c012` | |
| `timeframe` | `"H4"` | execution timeframe |
| `atr_lookback` | `14` | **H4 ATR** for stop sizing (mirrors session_breakout / random_entry_anchor convention; the design doc calls this `atr_lookback_h4` for descriptive clarity but in code we keep the existing `atr_lookback` name) |
| `atr_stop_multiple` | `2.0` | |
| `trailing_stop_atr_multiple` | `None` (forbidden in v1) | |
| `max_bars_in_trade` | `6` | time stop |
| `min_atr_pips` | `{}` | per-pair floor; default empty |
| `daily_atr_lookback` | `14` | **D1AGG ATR** for regime feature |
| `regime_lookback_days` | `60` | trailing window for percentile |
| `regime_percentile_threshold` | `0.70` | |
| `min_close_move_atr_fraction` | `0.25` | trend filter floor |
| `trend_lookback_h4_bars` | `4` | `close[t]` vs `close[t-4]` |
| `warm_up_bars` | `500` | covers `60d × 6 H4-bars/day = 360` + `14` ATR + `4` trend lookback + slack |

**Any deviation from these values constitutes a NEW candidate** that
requires its own discovery + design cycle. The runner / config loader
must reject any modified value.

## 11. Validation commands

Phase-end commands repeated at each phase boundary:

```bash
python -m pytest -q
ruff check src tests scripts research
python scripts/validate_research_archive.py
python scripts/check_research_freeze.py
python scripts/scan_artifacts_for_secrets.py
python -m forex_bot.cli paper-loop -c configs/paper.yaml      # expect refusal
python -m forex_bot.cli demo-loop -c configs/practice.yaml    # expect refusal
python -m forex_bot.cli --help                                 # expect no live-loop
git status --short
```

Targeted commands per phase:

- **Phase 2:** import smoke + targeted ruff on touched files.
- **Phase 3:** `pytest tests/unit/test_regime_switcher_atr_percentile.py -q`.
- **Phase 4:** config-load smoke for `configs/campaign_012_regime_switcher_atr_percentile.yaml`.
- **Phase 5:** the same as Phase 4 + a tiny fixture signal-generation smoke (already covered by tests).
- **Phase 7:** the full battery above + final repo `git status --short` clean check.

Test-count target: **771 baseline → ≥ 796 after Phase 3** (≥ 25 new
tests minimum per the discovery-003 spec; aim for **30+** per this
sprint's prompt).

## 12. Non-goals

This scaffold sprint **must not** do any of the following:

- Run a historical backtest (any campaign).
- Run a walk-forward evidence sprint.
- Run a financing overlay evidence sprint.
- Run a portfolio-risk diagnostics evidence sprint.
- Fetch new candle data.
- Read `.env` or print any credential.
- Submit / create / modify / cancel / close / query any broker order.
- Query account orders, trades, positions, account snapshots, or
  transaction streams.
- Use live broker credentials or demo / practice order execution.
- Run `paper-loop` or `demo-loop` **for any purpose other than the
  refusal check**.
- Create or invoke any `live-loop` command.
- Use QuantConnect or LEAN.
- Modify `configs/approved_strategies.yaml` (must remain `approved: []`).
- Add `regime_switcher_atr_percentile` to `configs/paper.yaml` or
  `configs/practice.yaml`.
- Revive / tune / parameter-search CAMPAIGN_002 / CAMPAIGN_010 /
  CAMPAIGN_011.
- Use CAMPAIGN_011 as a trading candidate (it is the null baseline
  ONLY).
- Change any historical campaign verdict.
- Optimize any C3 parameter based on smoke behavior or any prior
  campaign's result.
- Present a trading recommendation.
- Claim readiness for paper / demo / live.
- Add `CAMPAIGN_012` to `docs/research/EVIDENCE_MANIFEST.json`
  (the manifest takes only campaigns that have produced an evidence
  verdict; CAMPAIGN_012 has none yet — see Phase 7).

## 13. Explicit safety statements

1. **This scaffold sprint cannot approve any strategy.** Approval is
   a deliberate, reviewed human action per
   [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md);
   no scaffold sprint can substitute for it.
2. **This scaffold sprint must not run evidence.** Walk-forward,
   financing overlay, portfolio-risk diagnostics, and verifier
   corroboration are all reserved for the future evidence sprint
   `research-regime-switcher-atr-percentile-walk-forward-001`. A
   passing unit-test suite or smoke test is **not** evidence.
3. **CAMPAIGN_011 is only the null baseline, not a trading
   candidate.** Its metrics are used as the falsifiability floor that
   CAMPAIGN_012 must beat by the margins codified in
   [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md);
   it is structurally impossible to approve CAMPAIGN_011 (null model
   by design).

## 14. Phase plan

| phase | output | commits |
|---|---|---|
| 0 | this plan doc | 1 |
| 1 | binding implementation spec | 1 |
| 2 | strategy module + config schema | 1 |
| 3 | ≥ 30 unit tests | 1 |
| 4 | research config + CAMPAIGN_012 docs (precommit + status + readiness) | 1 |
| 5 | non-evidence smoke result | 1 |
| 6 | future evidence-readiness docs (walk-forward + financing/risk + verifier) | 1 |
| 7 | sprint summary + EVIDENCE_INDEX + STRATEGY_STATUS update + final validation | 1 |

Each phase is a self-contained commit; if a phase is blocked, that
fact is documented and the next independent safe phase proceeds.

## 15. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md)
- [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
- [`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md)
- [`NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md)
- [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`D1_AGGREGATION_DESIGN.md`](D1_AGGREGATION_DESIGN.md) (if present)
- [`src/forex_bot/backtesting/d1_aggregation.py`](../../src/forex_bot/backtesting/d1_aggregation.py)
