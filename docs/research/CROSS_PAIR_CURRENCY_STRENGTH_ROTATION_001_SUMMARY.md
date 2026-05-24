# `research-cross-pair-currency-strength-rotation-001` — Sprint Summary

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-001`
(worktree branch `claude/affectionate-fermi-d950fc`) · `strategy_evidence: false`

End-of-sprint summary for the CAMPAIGN_013 scaffold sprint.
Scaffolds the C6 Cross-Pair Currency Strength Rotation candidate
(`cross_pair_currency_strength_rotation 0.1.0-c013`) per the binding
design from `research-new-candidate-strategy-discovery-004`.
**Scaffold sprint only — no historical backtest, no walk-forward
evidence, no broker call, no strategy approval.**

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 remain
> REJECT. `configs/approved_strategies.yaml` remains `approved: []`.
> Paper / demo / live remain blocked. CAMPAIGN_011 is the **null
> baseline only**, not a trading candidate.

## 1. What changed

| dimension | value |
|---|---|
| commits this sprint | 8 (Phase 0 through Phase 7) |
| files added | 11 NEW (1 strategy module + 1 test file + 1 candidate config YAML + 8 docs) |
| files edited | 4 (3 source files in Phase 2 + EVIDENCE_INDEX + STRATEGY_STATUS in Phase 7) |
| Python LOC added | ~430 (strategy module ~311 + config edits ~62 + `__init__` edits ~5) |
| test LOC added | ~1,066 (57 deterministic tests) |
| markdown LOC added | ~3,200 (10 NEW docs + 2 EDITED) |
| pytest count | **818 → 875** (+57 new; old tests preserved) |
| ruff findings | 3 pre-existing in `research/lean_parity/algorithms/` (unchanged baseline) |

### 1.1 Phase-by-phase commits

| phase | commit | scope |
|---|---|---|
| Phase 0 | `dcb34ef` | repo truth audit & scaffold plan |
| Phase 1 | `f045073` | binding implementation spec |
| Phase 2 | `71af89a` | strategy + config implementation |
| Phase 3 | `343979d` | unit tests (57 new) |
| Phase 4 | `592f669` | research config + CAMPAIGN_013 docs |
| Phase 5 | `bfa3319` | non-evidence smoke |
| Phase 6 | `66394b7` | future evidence-readiness docs |
| Phase 7 | (this commit) | summary + EVIDENCE_INDEX + STRATEGY_STATUS update + final validation |

### 1.2 Files added (NEW)

| file | purpose |
|---|---|
| `src/forex_bot/strategies/cross_pair_currency_strength_rotation.py` | R1-R8 implementation |
| `tests/unit/test_cross_pair_currency_strength_rotation.py` | 57 deterministic unit tests |
| `configs/campaign_013_cross_pair_currency_strength_rotation.yaml` | research-only candidate config |
| `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md` | Phase 0 |
| `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md` | Phase 1 |
| `docs/research/CAMPAIGN_013_PRECOMMIT_CHECKLIST.md` | Phase 4 |
| `docs/research/CAMPAIGN_013_STATUS.md` | Phase 4 |
| `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_READINESS.md` | Phase 4 |
| `docs/research/CAMPAIGN_013_SMOKE_RESULT.md` | Phase 5 |
| `docs/research/CAMPAIGN_013_WALK_FORWARD_READINESS.md` | Phase 6 |
| `docs/research/CAMPAIGN_013_FINANCING_RISK_READINESS.md` | Phase 6 |
| `docs/research/CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md` | Phase 6 |
| `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md` | Phase 7 (this doc) |

### 1.3 Files edited

| file | edit |
|---|---|
| `src/forex_bot/strategies/__init__.py` | re-export `CrossPairCurrencyStrengthRotationStrategy` |
| `src/forex_bot/config.py` | add `CrossPairCurrencyStrengthRotationStrategyConfig` + `StrategyConfig.cross_pair_currency_strength_rotation` slot + enabled-list check |
| `docs/research/EVIDENCE_INDEX.md` | add CAMPAIGN_013 scaffold sub-section (Phase 7) |
| `docs/research/STRATEGY_STATUS.md` | update C6/CAMPAIGN_013 annotation from "selected" to "scaffolded; awaiting evidence" (Phase 7) |

## 2. What did NOT change

- `configs/approved_strategies.yaml` — still `approved: []` (verified).
- `configs/paper.yaml` — does NOT enable `cross_pair_currency_strength_rotation`.
- `configs/practice.yaml` — does NOT enable `cross_pair_currency_strength_rotation`.
- CAMPAIGN_002 / 010 / 011 / 012 verdicts — unchanged.
- `src/forex_bot/financing.py` — unchanged (MODELED still refused at 4 layers).
- `src/forex_bot/backtesting/d1_aggregation.py` — unchanged (not used by C6).
- RiskEngine / BacktestEngine / loops — unchanged.
- `research/walk_forward/` / `research/financing/` / `research/parity_verifier/` — unchanged.
- `docs/research/EVIDENCE_MANIFEST.json` — unchanged (manifest entries added only after evidence verdict; CAMPAIGN_013 has none).

## 3. Implementation status (Phase 2)

- `CrossPairCurrencyStrengthRotationStrategy` implements R1-R8 per
  binding spec.
- Helpers: `_parse_pair`, `_log_return_n`, `_compute_strength`,
  `_compute_ranks`, `_stable_signal_id` — all purely functional,
  no module-level mutable state.
- Module constants: `EXPECTED_PAIRS` (7-pair universe),
  `_PAIR_NONUSD_CURRENCY` (pair → non-USD currency + sign convention),
  `NON_USD_CURRENCIES` (the 7 non-USD currencies).
- Strategy re-exported from `src/forex_bot/strategies/__init__.py`.
- `CrossPairCurrencyStrengthRotationStrategyConfig` (Pydantic v2,
  `extra="forbid"`, `@model_validator(mode="after")`) with all 9
  frozen parameters; rejects invalid bounds + non-`None`
  `trailing_stop_atr_multiple` in v1; rejects `rank_gap_threshold`
  outside `[1, 7]`.
- `StrategyConfig.cross_pair_currency_strength_rotation` slot +
  enabled-list check.

## 4. Config status (Phase 4)

- `configs/campaign_013_cross_pair_currency_strength_rotation.yaml`
  loads cleanly via `forex_bot.config.load_settings()`.
- 7-pair H4 universe: EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD,
  USD_CHF, NZD_USD.
- `app.trading_enabled = false`; `app.allow_order_submission = false`;
  `app.allow_live_trading = false`.
- `risk.max_open_positions = 1`; `risk.max_positions_per_instrument = 1`;
  `risk.risk_per_trade_pct = 0.25`.
- All 9 frozen parameters parse to the expected Python types and values.

## 5. Test status (Phase 3)

| metric | value |
|---|---|
| new tests added | **57** (target was ≥ 40) |
| targeted test runtime | 0.13 s |
| full repo pytest count | **875 passed** (818 baseline + 57 new) |
| full repo runtime | 3.65 s |
| test sections | 15 (config validation 11, pair parser 2, strength mapping 5, rank computation 4, rank-gap rule 3, side selection 2, R1/R2/R6/R7 fixtures 4, R3/R4 fail-closed 5, no-lookahead audit 4, forbidden imports 4, rejected-family contamination 4, approval regression 4, signal-emission shape 2, helper-level no-state audit 2, module constants consistency 1) |

All 57 new tests cover the binding test sections from the
implementation spec §7 and 4 contamination-audit sections from
[`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md).

## 6. Smoke status (Phase 5)

| smoke command | result |
|---|---|
| config-load | PASS |
| import / instantiation | PASS — `cross_pair_currency_strength_rotation 0.1.0-c013`, warmup 50 |
| targeted unit suite | PASS — 57 in 0.13 s |
| full repo regression | PASS — 875 in 3.65 s |
| walk-forward dry-run (plan only) | PASS — **8 folds** emitted; identical to CAMPAIGN_010 / 011 / 012 plans; output to `/tmp` and NOT committed |

**Smoke is NOT evidence.** No backtest, no walk-forward strategy
execution, no financing overlay, no risk diagnostics, no verifier
run, no data fetch, no broker call, no `.env` read.

## 7. Walk-forward readiness status

**GREEN.** The future evidence sprint
`research-cross-pair-currency-strength-rotation-walk-forward-001` has
plan parameters inherited verbatim from CAMPAIGN_010 / 011 / 012
(rolling, frozen, 540/180/180/180 days, 2020-01-01 → 2026-05-20).
Expected 8 folds — confirmed by Phase 5 dry-run. Per-fold +
aggregate gates inherited verbatim. PLUS the binding null-baseline
comparison gate. **PLUS the binding cross-pair runner integration
contract** (see §10). See
[`CAMPAIGN_013_WALK_FORWARD_READINESS.md`](CAMPAIGN_013_WALK_FORWARD_READINESS.md).

## 8. Financing / risk readiness status

**GREEN.**

- **Financing.** ESTIMATED + `default_stress_rate_source()`
  (conservative stress) only. MODELED refused at 4 layers; not
  lifted. Live-promotion blocker stands. Cross-pair rotation
  expected to produce ~net-neutral financing impact (systematic
  long/short balance).
- **Risk diagnostics.** Standard CAMPAIGN_010/011/012 battery PLUS
  CAMPAIGN_013-specific:
  - rank-gap distribution histogram
  - simultaneous-signal frequency (2+, 3+, 4+, 5+ concurrent pairs)
  - **`MAX_OPEN_POSITIONS_EXCEEDED` rejection rate** (KNOWN behavior
    — `max_open_positions = 1` + cross-pair concurrent signals →
    high rejection rate expected; **do NOT relax to rescue trade
    count**)
  - currency-rank flip rate
  - pair-direction conflict rate

See [`CAMPAIGN_013_FINANCING_RISK_READINESS.md`](CAMPAIGN_013_FINANCING_RISK_READINESS.md).

## 9. Verifier readiness status

**GREEN-with-caveat.** Verifier is capability-locked to CAMPAIGN_002
/ `trend_following`. **Not required** for REJECT verdict. **Required**
before any paper-promotion consideration if CAMPAIGN_013 reaches
`RESEARCH_PASS_UNAPPROVED` — via the suggested follow-up sprint
`infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001`.
Cross-pair rotators are especially well-suited to verifier
corroboration (discrete log returns + integer ranks + binary
rank-gap rule). See
[`CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md).

## 10. Cross-pair runner integration contract (binding for future evidence sprint)

The CAMPAIGN_013 evidence runner is **structurally different** from
CAMPAIGN_010 / 011 / 012 runners. It MUST:

1. Load all 7 pairs' completed H4 candles for the test window +
   warm-up margin.
2. Align all 7 pairs to a common H4 timestamp index (intersection).
3. Build per-pair closes-only `pd.Series` indexed by the common index.
4. Inject `{pair: pd.Series}` into `strategy_config["cross_pair_closes"]`
   for each pair's engine invocation.

Binding invariants from
[`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)
§4 R3:

- Completed-only series.
- Intersection index.
- Align before invoke.
- One-way runner → strategy via `ctx.config` (no direct sibling-pair
  access).

If the runner cannot satisfy these invariants, **classify verdict as
`BLOCKED`** (do not partial-evaluate; do not approximate; do not
silently substitute zero).

## 11. Final validation

| command | result |
|---|---|
| `python -m pytest -q` | **875 passed** in 3.65 s |
| `ruff check src tests scripts research` | **3 pre-existing findings** in `research/lean_parity/algorithms/` (`2× RUF100` unused-noqa + `1× I001` unsorted-imports); identical to the base-commit (`ff34e96`) ruff state; no new findings introduced |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED (12 campaigns; 14 diagnostic artifacts; clean credential scan) |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED |
| `python -m forex_bot.cli paper-loop -c configs/paper.yaml` | refused |
| `python -m forex_bot.cli demo-loop -c configs/practice.yaml` | refused |
| `python -m forex_bot.cli --help` | no `live-loop` command present |
| `git status --short` | clean at commit boundary |

## 12. Safety state (verified)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | REJECT (null-model anchor; untouched) |
| CAMPAIGN_012 | REJECT (untouched) |
| CAMPAIGN_013 | scaffold only; no evidence verdict; **NOT approved** |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | **no** (4 refusal layers) |
| live-promotion financing blocker | stands |
| pytest baseline | 875 (818 prior + 57 new) |
| ruff baseline | 3 pre-existing in `research/lean_parity/` (unchanged) |
| broker / OANDA call this sprint | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| historical campaign verdict change | **none** |
| parameter "tweak" or "rescue" | **none** (frozen parameters unchanged) |
| `D1AGG` aggregator edit | **none** (not used by C6) |
| `src/forex_bot/financing.py` edit | **none** |
| RiskEngine / engine / loops edit | **none** |
| new external dependency | **none** |

## 13. Remaining blockers

| blocker | affects | next step |
|---|---|---|
| **MODELED financing refused at 4 layers** | live promotion of any candidate | `research-financing-modeled-capture-credentialed-001` (separately authorized) |
| **Independent verifier capability-locked to CAMPAIGN_002** | item 5 of six-evidence ladder for non-`trend_following` paper-promotion | `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001` (required only if CAMPAIGN_013 unexpectedly passes) |
| **3 pre-existing ruff findings** | code-quality only; no runtime impact | `infra-ruff-lean-parity-archive-cleanup-001` (low priority) |

**None of these block CAMPAIGN_013's evidence sprint.**

## 14. Recommended next branch

### **`research-cross-pair-currency-strength-rotation-walk-forward-001`** (evidence sprint)

The 10-phase evidence-branch prompt is the full text of
[`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md).
High-level shape (mirrors CAMPAIGN_012 evidence sprint):

- **Phase 0** — repo truth audit + sprint plan
- **Phase 1** — data availability + provenance (hashes match CAMPAIGN_010 / 011 / 012 verbatim)
- **Phase 2** — authoritative walk-forward plan
- **Phase 3** — per-fold runner (`scripts/run_campaign_013.py`) — **critical: must implement cross-pair runner integration contract** (see §10)
- **Phase 4** — execute per-fold backtests (8 folds × 7 pairs = 56 backtests)
- **Phase 5** — walk-forward verdict (REJECT / REJECT_INDISTINGUISHABLE_FROM_NULL / RESEARCH_PASS_UNAPPROVED / BLOCKED; must include "Null-baseline comparison" section)
- **Phase 6** — financing overlay (ESTIMATED + conservative stress; MODELED refused)
- **Phase 7** — portfolio-risk diagnostics (standard + CAMPAIGN_013-specific)
- **Phase 8** — independent verifier status (capability-locked; not run unless `RESEARCH_PASS_UNAPPROVED`)
- **Phase 9** — final summary + EVIDENCE_MANIFEST entry (12 → 13 campaigns) + final validation

**Approval allowed by this future sprint?** **NO** — even a clean
PASS produces `RESEARCH_PASS_UNAPPROVED`. Human approval action is
separate per [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

## 15. Exact files to review first

In review order:

1. **[`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md)** — one-page sprint summary; start here for orientation.
2. **[`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)** — binding R1-R8 + 9 frozen parameters + 14 no-lookahead invariants + 51 expected test sections.
3. **`src/forex_bot/strategies/cross_pair_currency_strength_rotation.py`** — the implementation (~311 LOC); reads cleanly against the spec.
4. **`tests/unit/test_cross_pair_currency_strength_rotation.py`** — 57 deterministic unit tests; all green.
5. **[`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md)** — binding pre-commit (frozen parameters; cross-pair-closes contract; null-baseline comparison gate; unexpected-PASS protocol).
6. **[`CAMPAIGN_013_STATUS.md`](CAMPAIGN_013_STATUS.md)** — scaffold-only status; CAMPAIGN_002 / 010 / 011 / 012 relationship.
7. **[`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_READINESS.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_READINESS.md)** — scaffold readiness GREEN; pre-flight checklist for the future evidence sprint.
8. **[`CAMPAIGN_013_SMOKE_RESULT.md`](CAMPAIGN_013_SMOKE_RESULT.md)** — Phase 5 NON-EVIDENCE smoke; 8-fold dry-run confirmed.
9. **[`CAMPAIGN_013_WALK_FORWARD_READINESS.md`](CAMPAIGN_013_WALK_FORWARD_READINESS.md)** — future evidence-sprint plan + gate vector + **cross-pair runner integration contract**.
10. **[`CAMPAIGN_013_FINANCING_RISK_READINESS.md`](CAMPAIGN_013_FINANCING_RISK_READINESS.md)** — ESTIMATED + conservative stress; CAMPAIGN_013-specific diagnostics; MAX_OPEN_POSITIONS_EXCEEDED note.
11. **[`CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md)** — verifier capability lock; suggested follow-up sprint.
12. **`configs/campaign_013_cross_pair_currency_strength_rotation.yaml`** — the loadable research config.
13. (Reference) **[`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md)** — Phase 0 plan.

## 16. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md) (discovery sprint that selected C6)
- [`NEXT_PREFERRED_DIRECTION_004.md`](NEXT_PREFERRED_DIRECTION_004.md) (Phase 5 of discovery-004)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md) (discovery-004 binding design)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md) (binding spec for this sprint)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md) (binding spec for the next evidence sprint)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
