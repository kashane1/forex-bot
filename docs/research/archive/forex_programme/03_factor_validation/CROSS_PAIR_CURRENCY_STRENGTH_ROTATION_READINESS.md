# Cross-Pair Currency Strength Rotation — Scaffold Readiness

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-001`
`strategy_evidence: false`

One-page scaffold-readiness summary for **CAMPAIGN_013 /
`cross_pair_currency_strength_rotation 0.1.0-c013`**. The scaffold is
GREEN across all dimensions; the future evidence sprint can begin
once a human authorizes it. **This document is not strategy evidence.
A passing scaffold is not edge.**

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 remain
> REJECT. `configs/approved_strategies.yaml` remains `approved: []`.
> Paper / demo / live remain blocked. CAMPAIGN_011 is the **null
> baseline only**, not a trading candidate.

## 1. Scaffold readiness (GREEN across all dimensions)

| dimension | status | detail |
|---|:---:|---|
| strategy module | ✓ | `src/forex_bot/strategies/cross_pair_currency_strength_rotation.py` implements R1-R8 per binding spec |
| strategy registered | ✓ | `CrossPairCurrencyStrengthRotationStrategy` exported from `src/forex_bot/strategies/__init__.py` |
| config schema | ✓ | `CrossPairCurrencyStrengthRotationStrategyConfig` (Pydantic v2, `extra="forbid"`) + `StrategyConfig.cross_pair_currency_strength_rotation` slot + enabled-list check in `src/forex_bot/config.py` |
| frozen-parameter pre-commit | ✓ | all 9 parameters bound by validator |
| candidate YAML | ✓ | `configs/campaign_013_cross_pair_currency_strength_rotation.yaml` (7-pair H4 universe; `trading_enabled: false`) |
| unit tests | ✓ | 57 deterministic tests in `tests/unit/test_cross_pair_currency_strength_rotation.py` |
| no-lookahead audit | ✓ | structural source-grep tests pass: no bar-`t` reads of `high` / `low` / `open` / `volume`; close-`t` read only in R7; ranks deterministic with alphabetic tiebreak; helpers purely functional |
| no PRNG / no broker | ✓ | source-grep tests pass: no `random` / `numpy.random` / `secrets` / builtin `hash()`; no `forex_bot.broker` / `.execution` / `.loops` imports |
| no rejected-family contamination | ✓ | source-grep tests pass: no CAMPAIGN_002 / 010 / 011 / 012 strategy-specific parameter keys |
| approval regression | ✓ | `configs/approved_strategies.yaml` unchanged at `approved: []`; not enabled in `paper.yaml` / `practice.yaml`; no approval-shaped public attribute |
| pre-commit checklist | ✓ | [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md) committed |
| repo-wide pytest | ✓ | 875 passing (818 baseline + 57 new) |
| repo-wide ruff | ✓ | 3 pre-existing in `research/lean_parity/algorithms/` (untouched); no new findings |
| validate_research_archive | ✓ | ALL CHECKS PASSED |
| check_research_freeze | ✓ | ALL CHECKS PASSED (loops refuse; no credentials) |
| scan_artifacts_for_secrets | ✓ | PASSED |
| paper-loop / demo-loop | ✓ | both refuse (`approved_strategies.yaml` empty) |
| `live-loop` command | ✓ | does not exist |

## 2. Future evidence branch identity

| field | value |
|---|---|
| name | `research-cross-pair-currency-strength-rotation-walk-forward-001` |
| relation | mirrors `research-regime-switcher-atr-percentile-walk-forward-001` (CAMPAIGN_012 evidence) exactly |
| spec | [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md) (binding from discovery-004) |
| readiness docs | [`CAMPAIGN_013_WALK_FORWARD_READINESS.md`](CAMPAIGN_013_WALK_FORWARD_READINESS.md), [`CAMPAIGN_013_FINANCING_RISK_READINESS.md`](CAMPAIGN_013_FINANCING_RISK_READINESS.md), [`CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md) (Phase 6) |

## 3. Data expectations

| dimension | value |
|---|---|
| source | `data/campaign_002.sqlite3` (gitignored symlink) — same physical store as CAMPAIGN_002 / 010 / 011 / 012; provenance hashes already recorded |
| universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD (7 pairs; H4 OANDA practice) |
| span | 2020-01-01 → 2026-05-19 inclusive |
| new fetch needed | **no** |
| new credentials | **no** |
| cross-pair runner integration | required at evidence-sprint time (see §5) |

## 4. Known limitations

- **Verifier capability lock.** The independent verifier
  (item 5 of the six-evidence ladder) is capability-locked to
  CAMPAIGN_002 / `trend_following`; it cannot validate
  `cross_pair_currency_strength_rotation`. The verifier extension
  `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001`
  is **only required** if CAMPAIGN_013's evidence verdict is
  `RESEARCH_PASS_UNAPPROVED`. A clean REJECT does not need it.
- **MODELED financing.** Live promotion requires MODELED financing,
  refused at 4 layers in `src/forex_bot/financing.py`. Live-promotion
  financing blocker stands unless the separately-authorized
  credentialed pilot
  `research-financing-modeled-capture-credentialed-001` runs. Paper
  promotion is acceptable under ESTIMATED with explicit human
  override per the existing rule.
- **`MAX_OPEN_POSITIONS_EXCEEDED` rejection rate.** Cross-pair
  rotation generates *multiple simultaneous signals* (3–5 pairs may
  signal at the same H4 bar). With `risk.max_open_positions = 1`,
  only the first-encountered pair's signal would fill; subsequent
  signals would be rejected as `MAX_OPEN_POSITIONS_EXCEEDED`. **This
  is known behavior of C6, NOT a bug to fix.** The evidence sprint
  records the rejection rate honestly and does not relax
  `max_open_positions` to "rescue" trade count. If C6 cannot clear
  `trade_count_min = 200` under the existing risk cap, that itself
  is part of the research evidence (the candidate is operationally
  infeasible under the project's current risk envelope).

## 5. Cross-pair runner integration requirement (binding for future evidence sprint)

The strategy requires sibling-pair close series at each invocation.
The future runner (in
`research-cross-pair-currency-strength-rotation-walk-forward-001`)
**MUST**:

1. Load all 7 pairs' completed H4 candles for the test window +
   warm-up margin.
2. Align all 7 pairs to a common H4 timestamp index (intersection of
   completed bars).
3. Build per-pair closes-only `pd.Series` indexed by the common
   index.
4. Inject the dict `{pair: pd.Series}` into
   `strategy_config["cross_pair_closes"]` for each pair's engine
   invocation.

Binding invariants (from `CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`
§4 R3):

- Completed-only series.
- Intersection index across pairs.
- Align before invoke.
- One-way runner → strategy via `ctx.config` (no direct sibling-pair
  access from the strategy module).

If the runner cannot satisfy these invariants, the evidence sprint
must classify the verdict as **BLOCKED**.

## 6. Null-baseline comparison

The future evidence sprint **must** compare CAMPAIGN_013's per-fold +
aggregate metrics to CAMPAIGN_011's null-baseline floor (verbatim from
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)):

| metric | CAMPAIGN_011 floor | CAMPAIGN_013 must beat |
|---|---|---|
| aggregate expectancy R | −0.0024 | by ≥ **+0.0524** (→ ≥ 0.05) |
| aggregate profit factor | 0.91 | by ≥ **+0.19** (→ ≥ 1.10) |
| aggregate return (4 y) | −0.53 % | meaningfully positive (≥ **+5 %**) |
| `pairs_positive` | 3 / 7 | ≥ **4 / 7** |
| `fold_pass_rate` | 0 / 8 | **100 %** |

"Indistinguishable from null" REJECT band (within ± 0.005 R / ± 0.10
PF / ± 2 pp / ± 1 pair of CAMPAIGN_011): the verdict must classify
as **REJECT_INDISTINGUISHABLE_FROM_NULL**, regardless of which
inherited gates technically pass.

## 7. Why this is a real candidate (but not approved)

The C6 cross-pair rotation is a **real-edge candidate** in the sense
that:

- It has a directional hypothesis (cross-pair rank-gap predicts
  pair direction).
- It is fully deterministic from price (no PRNG; no `master_seed`).
- It is structurally distinct from every prior rejected family
  (distinctness 6 / 6 vs CAMPAIGN_002 / 004 / 007 / 008 / 009 / 010 /
  011 / 012).
- It is the first multi-pair (cross-pair orchestration) candidate to
  reach scaffold.

But **the candidate is not approved**:

- No backtest has run; no walk-forward; no financing overlay; no
  risk diagnostics; no verifier corroboration.
- A passing scaffold is **not** evidence of edge.
- Approval requires the full six-evidence ladder + a deliberate
  human approval action per
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

## 8. Pre-flight checklist for the future evidence sprint

- [ ] Scaffold sprint committed and merged or rebased onto main.
- [ ] `configs/approved_strategies.yaml` still `approved: []`.
- [ ] CAMPAIGN_002 / 010 / 011 / 012 verdicts unchanged.
- [ ] 875-pytest baseline preserved.
- [ ] `configs/campaign_013_cross_pair_currency_strength_rotation.yaml`
      loads cleanly via `load_settings()`.
- [ ] `CrossPairCurrencyStrengthRotationStrategy` instantiates and
      the import smoke runs.
- [ ] Loops refuse; no `live-loop`.
- [ ] No `backtests/CAMPAIGN_013_*` artifact directory yet.
- [ ] Verifier capability gap acknowledged; verifier-extension
      `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001`
      is a separately-authorized future sprint required only on
      `RESEARCH_PASS_UNAPPROVED`.
- [ ] MODELED financing blocker acknowledged; CAMPAIGN_013's
      overlay will use ESTIMATED + conservative stress only.
- [ ] Cross-pair runner integration contract (§5) acknowledged and
      planned.

## 9. Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_013_STATUS.md`](CAMPAIGN_013_STATUS.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
