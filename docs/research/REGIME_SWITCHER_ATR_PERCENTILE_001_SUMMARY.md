# `research-regime-switcher-atr-percentile-001` — Sprint Summary

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-001`
(worktree branch `claude/affectionate-fermi-d950fc`) · `strategy_evidence: false`

End-of-sprint summary for the CAMPAIGN_012 scaffold sprint. Scaffolds
the C3 daily-ATR-percentile regime switcher
(`regime_switcher_atr_percentile 0.1.0-c012`) per the binding design
from `research-new-candidate-strategy-discovery-003`. **Scaffold sprint
only — no historical backtest, no walk-forward evidence, no broker
call, no strategy approval.**

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
> remain REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked. CAMPAIGN_011 is
> the **null baseline only**, not a trading candidate.

## 1. What changed

| dimension | value |
|---|---|
| commits this sprint | 8 (Phase 0 through Phase 7) |
| files added | 11 |
| files edited | 4 (3 source files in Phase 2 + EVIDENCE_INDEX / STRATEGY_STATUS in Phase 7) |
| Python LOC added | ~410 (strategy module ~310 + config edits ~65 + `__init__` edits ~3) |
| test LOC added | ~880 (47 deterministic tests) |
| markdown LOC added | ~3,650 (10 NEW docs + 2 EDITED) |
| pytest count | **771 → 818** (+47 new; old tests preserved) |
| ruff findings | 3 pre-existing in `research/lean_parity/algorithms/` (unchanged baseline) |

### 1.1 Phase-by-phase commits

| phase | commit | scope |
|---|---|---|
| Phase 0 | `c0cb53d` | repo truth audit & scaffold plan |
| Phase 1 | `7429738` | binding implementation spec |
| Phase 2 | `07bd9f3` | strategy + config implementation |
| Phase 3 | `532936e` | unit tests (47 new) |
| Phase 4 | `32aa0d5` | research config + CAMPAIGN_012 docs |
| Phase 5 | `61a6627` | non-evidence smoke |
| Phase 6 | `52fc8cc` | future evidence-readiness docs |
| Phase 7 | (this commit) | summary + EVIDENCE_INDEX + STRATEGY_STATUS update + final validation |

### 1.2 Files added (NEW)

| file | purpose |
|---|---|
| `src/forex_bot/strategies/regime_switcher_atr_percentile.py` | R1-R8 implementation |
| `tests/unit/test_regime_switcher_atr_percentile.py` | 47 deterministic unit tests |
| `configs/campaign_012_regime_switcher_atr_percentile.yaml` | research-only candidate config |
| `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md` | Phase 0 |
| `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md` | Phase 1 |
| `docs/research/CAMPAIGN_012_PRECOMMIT_CHECKLIST.md` | Phase 4 |
| `docs/research/CAMPAIGN_012_STATUS.md` | Phase 4 |
| `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_READINESS.md` | Phase 4 |
| `docs/research/CAMPAIGN_012_SMOKE_RESULT.md` | Phase 5 |
| `docs/research/CAMPAIGN_012_WALK_FORWARD_READINESS.md` | Phase 6 |
| `docs/research/CAMPAIGN_012_FINANCING_RISK_READINESS.md` | Phase 6 |
| `docs/research/CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md` | Phase 6 |
| `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md` | Phase 7 (this doc) |

### 1.3 Files edited

| file | edit |
|---|---|
| `src/forex_bot/strategies/__init__.py` | re-export `RegimeSwitcherAtrPercentileStrategy` |
| `src/forex_bot/config.py` | add `RegimeSwitcherAtrPercentileStrategyConfig` + `StrategyConfig.regime_switcher_atr_percentile` slot + enabled-list check |
| `docs/research/EVIDENCE_INDEX.md` | add CAMPAIGN_012 scaffold sub-section (Phase 7) |
| `docs/research/STRATEGY_STATUS.md` | update C3/CAMPAIGN_012 annotation from "selected" to "scaffolded; awaiting evidence" (Phase 7) |

## 2. What did NOT change

- `configs/approved_strategies.yaml` — still `approved: []` (verified).
- `configs/paper.yaml` — does NOT enable `regime_switcher_atr_percentile`.
- `configs/practice.yaml` — does NOT enable `regime_switcher_atr_percentile`.
- CAMPAIGN_002 / 010 / 011 verdicts — unchanged.
- `src/forex_bot/financing.py` — unchanged (MODELED still refused at 4 layers).
- `src/forex_bot/backtesting/d1_aggregation.py` — unchanged (read-only use).
- RiskEngine / BacktestEngine / loops — unchanged.
- `research/walk_forward/` / `research/financing/` / `research/parity_verifier/` — unchanged.
- `docs/research/EVIDENCE_MANIFEST.json` — unchanged (manifest entries are added only after an evidence verdict exists; CAMPAIGN_012 has none).

## 3. Implementation status (Phase 2)

- `RegimeSwitcherAtrPercentileStrategy` implements R1-R8 per the binding
  spec.
- Helpers: `_df_to_completed_h4_candle_list`, `_wilder_atr_over_d1agg`,
  `_compute_regime`, `_stable_signal_id` — all purely functional, no
  module-level mutable state.
- D1AGG aggregation via the existing
  `src/forex_bot/backtesting/d1_aggregation.py` (no edits to that
  module).
- Wilder ATR via the existing `forex_bot.strategies.indicators.atr`
  helper (applied to both H4 directly and D1AGG mid OHLC).
- Deterministic signal-id via SHA-1 (mirrors session_breakout /
  random_entry_anchor).
- Strategy re-exported from `src/forex_bot/strategies/__init__.py`.
- `RegimeSwitcherAtrPercentileStrategyConfig` (Pydantic v2,
  `extra="forbid"`, `@model_validator(mode="after")`) with all 12
  frozen parameters; rejects invalid bounds + non-`None`
  `trailing_stop_atr_multiple` in v1.
- `StrategyConfig.regime_switcher_atr_percentile` slot + enabled-list
  check.

## 4. Config status (Phase 4)

- `configs/campaign_012_regime_switcher_atr_percentile.yaml` loads
  cleanly via `forex_bot.config.load_settings()`.
- 7-pair H4 universe: EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD,
  USD_CHF, NZD_USD.
- `app.trading_enabled = false`; `app.allow_order_submission = false`;
  `app.allow_live_trading = false`.
- `risk.max_open_positions = 1`; `risk.max_positions_per_instrument = 1`;
  `risk.risk_per_trade_pct = 0.25`.
- All 12 frozen parameters from the implementation spec parse to the
  expected Python types and values.

## 5. Test status (Phase 3)

| metric | value |
|---|---|
| new tests added | **47** (target was ≥ 30) |
| targeted test runtime | 0.35 s |
| full repo pytest count | **818 passed** (771 baseline + 47 new) |
| full repo runtime | 3.33 s |
| test sections | 10 (config validation 13, strategy core 6, regime gate 5, trend sub-signal 3, no-lookahead audit 4, forbidden imports 4, rejected-family contamination 3, approval regression 4, D1AGG integration 3, Signal-emission structural 2) |

All 47 new tests cover the 13 binding test sections from the
implementation spec §6 and 4 contamination-audit sections from
[`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md).

## 6. Smoke status (Phase 5)

| smoke command | result |
|---|---|
| config-load | PASS |
| import / instantiation | PASS |
| targeted unit suite | PASS — 47 cases |
| full repo regression | PASS — 818 cases |
| walk-forward dry-run (plan only) | PASS — **8 folds** emitted; identical to CAMPAIGN_010 / 011 plans verbatim |

**Smoke is NOT evidence.** No backtest, no broker call, no data fetch,
no `.env` read, no credentials. Dry-run output written to `/tmp` and
**not committed**.

## 7. Walk-forward readiness (Phase 6)

GREEN. The future evidence sprint
`research-regime-switcher-atr-percentile-walk-forward-001` has:

- Plan parameters inherited verbatim from CAMPAIGN_010 / 011 (rolling,
  frozen, 540/180/180/180 days, 2020-01-01 → 2026-05-20, expected 8
  folds — confirmed by the Phase 5 dry-run).
- Per-fold + aggregate gates inherited verbatim.
- **Plus** the binding null-baseline comparison gate (must beat
  CAMPAIGN_011 by ≥ +0.0524 R / ≥ +0.19 PF / ≥ +5.5 pp / ≥ +1 pair /
  100 % fold pass rate; indistinguishable-from-null band
  ± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair).
- Expected artifact paths enumerated (mirror CAMPAIGN_010 / 011
  structure).

## 8. Financing / risk readiness (Phase 6)

GREEN.

- **Financing:** ESTIMATED + `default_stress_rate_source()`
  (conservative stress) only. MODELED **refused at 4 layers in
  `src/forex_bot/financing.py`** — not lifted by this sprint or by the
  future evidence sprint. Live-promotion financing blocker stands.
- **Risk diagnostics:** max 1 concurrent position per instrument
  (engine-enforced + R2 + config); expected time-stop fraction ~75 %;
  expected regime-period clustering signature (trades cluster in
  HIGH-VOL periods); session-of-day distribution expected diffuse
  across all 4 UTC buckets (like CAMPAIGN_011, unlike CAMPAIGN_010's
  100 % London concentration).
- 8 pipeline sanity checks required (identical to CAMPAIGN_010 / 011).

## 9. Verifier readiness (Phase 6)

GREEN-with-caveat.

- Verifier is capability-locked to CAMPAIGN_002 / `trend_following`.
- **Not required for a clean REJECT verdict.**
- **Required before any paper-promotion consideration** if CAMPAIGN_012
  reaches `RESEARCH_PASS_UNAPPROVED` — suggested future sprint
  `infra-free-local-parity-verifier-regime-switcher-001`.

## 10. Final validation

| command | result |
|---|---|
| `python -m pytest -q` | **818 passed** in 3.33 s |
| `ruff check src tests scripts research` | **3 pre-existing findings** in `research/lean_parity/algorithms/` (`2× RUF100` unused-noqa + `1× I001` unsorted-imports); identical to the base-commit (`384314a`) ruff state; no new findings introduced by this sprint |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED (11 campaigns; 14 diagnostic artifacts; 195+ evidence-index links resolve after the Phase 7 EVIDENCE_INDEX update; clean credential scan) |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED |
| `python -m forex_bot.cli paper-loop -c configs/paper.yaml` | refused |
| `python -m forex_bot.cli demo-loop -c configs/practice.yaml` | refused |
| `python -m forex_bot.cli --help` | no `live-loop` command present |
| `git status --short` | clean at commit boundary |

## 11. Safety state (verified)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | REJECT (null-model anchor; untouched) |
| CAMPAIGN_012 | scaffold only; no evidence verdict; **NOT approved** |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | **no** (4 refusal layers) |
| live-promotion financing blocker | stands |
| pytest baseline | 818 (771 prior + 47 new) |
| ruff baseline | 3 pre-existing in `research/lean_parity/` (unchanged) |
| broker / OANDA call this sprint | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| historical campaign verdict change | **none** |
| parameter "tweak" or "rescue" | **none** (frozen parameters unchanged) |
| `D1AGG` aggregator edit | **none** (read-only use) |
| `src/forex_bot/financing.py` edit | **none** |
| RiskEngine / engine / loops edit | **none** |
| new external dependency | **none** |

## 12. Remaining blockers

| blocker | affects | next step |
|---|---|---|
| **MODELED financing refused at 4 layers** | live promotion of any candidate that survives walk-forward | `research-financing-modeled-capture-credentialed-001` — separately authorized credentialed pilot |
| **Independent verifier capability-locked to CAMPAIGN_002** | item 5 of six-evidence ladder for paper promotion of any non-`trend_following` candidate | `infra-free-local-parity-verifier-regime-switcher-001` — required only if CAMPAIGN_012 reaches `RESEARCH_PASS_UNAPPROVED` |
| **3 pre-existing ruff findings** in `research/lean_parity/algorithms/` | code-quality only; no runtime impact | `infra-ruff-lean-parity-archive-cleanup-001` — low-priority cleanup |

**None of these block CAMPAIGN_012's evidence sprint** (the next
recommended sprint). The walk-forward + financing + risk diagnostics
all run against ESTIMATED + conservative stress without MODELED; the
verifier is needed only on PASS; the ruff findings are out-of-scope
LEAN-archive code.

## 13. Recommended next branch

### **`research-regime-switcher-atr-percentile-walk-forward-001`** (evidence sprint)

The 9-phase evidence-branch prompt is the full text of
[`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md).
High-level shape (mirrors CAMPAIGN_010 / CAMPAIGN_011 exactly):

- **Phase 0** — repo truth audit + sprint plan
- **Phase 1** — data availability + provenance (hashes should match
  CAMPAIGN_010 / 011 verbatim; same physical store)
- **Phase 2** — authoritative walk-forward plan
- **Phase 3** — per-fold runner
- **Phase 4** — execute per-fold backtests (8 folds × 7 pairs)
- **Phase 5** — walk-forward verdict (REJECT / REJECT (indistinguishable from null) / RESEARCH_PASS_UNAPPROVED / BLOCKED; must include "Null-baseline comparison" section)
- **Phase 6** — financing overlay (ESTIMATED + conservative stress; MODELED refused)
- **Phase 7** — portfolio-risk diagnostics
- **Phase 8** — independent verifier status (capability-locked; not run unless RESEARCH_PASS_UNAPPROVED)
- **Phase 9** — final summary + EVIDENCE_MANIFEST entry + final validation

**Approval allowed by this future sprint?** **NO** — even a clean PASS
produces `RESEARCH_PASS_UNAPPROVED`. Human approval action is separate
per [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

## 14. Exact files to review first

In review order (each fully self-contained; later docs cite earlier
ones):

1. **[`REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md)** — this one-page sprint summary; start here for orientation.
2. **[`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md)** — the binding R1-R8 + frozen parameters + no-lookahead invariants + 40 expected tests.
3. **`src/forex_bot/strategies/regime_switcher_atr_percentile.py`** — the implementation; ~310 LOC; reads cleanly against the spec.
4. **`tests/unit/test_regime_switcher_atr_percentile.py`** — the 47 unit tests; all green.
5. **[`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)** — the binding pre-commit (frozen parameters; null-baseline comparison gate; unexpected-PASS protocol).
6. **[`CAMPAIGN_012_STATUS.md`](CAMPAIGN_012_STATUS.md)** — scaffold-only status; CAMPAIGN_002 / 010 / 011 relationship; why this is a real candidate (but not approved).
7. **[`REGIME_SWITCHER_ATR_PERCENTILE_READINESS.md`](REGIME_SWITCHER_ATR_PERCENTILE_READINESS.md)** — scaffold readiness; pre-flight checklist for the future evidence sprint.
8. **[`CAMPAIGN_012_SMOKE_RESULT.md`](CAMPAIGN_012_SMOKE_RESULT.md)** — Phase 5 NON-EVIDENCE smoke result; 8-fold dry-run confirmed.
9. **[`CAMPAIGN_012_WALK_FORWARD_READINESS.md`](CAMPAIGN_012_WALK_FORWARD_READINESS.md)** — future evidence sprint plan + gate vector + artifact paths.
10. **[`CAMPAIGN_012_FINANCING_RISK_READINESS.md`](CAMPAIGN_012_FINANCING_RISK_READINESS.md)** — ESTIMATED + conservative stress; MODELED refused; risk diagnostics expectations.
11. **[`CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md)** — verifier capability lock; suggested future verifier-extension sprint.
12. **`configs/campaign_012_regime_switcher_atr_percentile.yaml`** — the loadable research config; verify the 12 frozen parameters and the `trading_enabled: false` flags.
13. (Reference) **[`REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md)** — Phase 0 plan + repo truth audit.

## 15. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md) (the discovery sprint that selected C3)
- [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
- [`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md)
- [`NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md) (the binding spec for this scaffold sprint)
- [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md) (the binding spec for the next evidence sprint)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
