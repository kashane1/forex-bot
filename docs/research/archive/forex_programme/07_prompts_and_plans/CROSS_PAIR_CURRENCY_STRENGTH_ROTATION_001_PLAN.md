# `research-cross-pair-currency-strength-rotation-001` — Sprint Plan (Phase 0)

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-001`
(worktree branch `claude/affectionate-fermi-d950fc`) · `strategy_evidence: false`

Phase 0 repo truth audit + 8-phase scaffold plan for **CAMPAIGN_013 /
`cross_pair_currency_strength_rotation 0.1.0-c013`** — the C6
Cross-Pair Currency Strength Rotation real candidate selected by the
[`research-new-candidate-strategy-discovery-004`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md)
discovery sprint. **Scaffold sprint only — no historical backtest,
no walk-forward evidence, no broker call, no approval.**

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
> CAMPAIGN_012 all remain REJECT. `configs/approved_strategies.yaml`
> remains `approved: []`. CAMPAIGN_011 is **only the null baseline**,
> not a trading candidate. C6 / CAMPAIGN_013 is **selected but not
> approved** — this sprint cannot approve any strategy. Even a clean
> unit-test suite + smoke pass is not evidence. The future evidence
> sprint must run walk-forward, null-baseline comparison, financing
> overlay, risk diagnostics, and verifier-status assessment before
> any research verdict exists; any approval requires the full
> six-evidence ladder + a deliberate human approval action per
> [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

## 1. Current branch / base commit

| dimension | value |
|---|---|
| git branch (worktree) | `claude/affectionate-fermi-d950fc` |
| logical sprint branch | `research-cross-pair-currency-strength-rotation-001` |
| base commit (HEAD before Phase 0) | `ff34e96` — Phase 9 of `research-new-candidate-strategy-discovery-004` |
| working tree at Phase 0 start | clean (only `.claude/` tooling cache untracked) |

## 2. Files inspected (Phase 0 audit)

**Discovery-004 binding outputs:**

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md)
- [`NEXT_PREFERRED_DIRECTION_004.md`](NEXT_PREFERRED_DIRECTION_004.md)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md) (binding design)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md) (binding scaffold spec — this sprint's prompt)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md)
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md)
- [`NEXT_DIRECTION_REASSESSMENT_004.md`](NEXT_DIRECTION_REASSESSMENT_004.md)

**Project-wide research guards:**

- [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md) (Patterns H–L; binding)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)

**Implementation patterns to mirror (sibling strategy modules):**

- `src/forex_bot/strategies/session_breakout.py` (CAMPAIGN_010 scaffold)
- `src/forex_bot/strategies/random_entry_anchor.py` (CAMPAIGN_011 scaffold)
- `src/forex_bot/strategies/regime_switcher_atr_percentile.py` (CAMPAIGN_012 scaffold)
- `src/forex_bot/strategies/__init__.py` (re-export pattern)
- `src/forex_bot/strategies/base.py` (`StrategyContext` + `Strategy` protocol)
- `src/forex_bot/strategies/indicators.py` (`atr` helper)
- `src/forex_bot/config.py` (`SessionBreakoutStrategyConfig` / `RandomEntryAnchorStrategyConfig` / `RegimeSwitcherAtrPercentileStrategyConfig`)
- `tests/unit/test_session_breakout.py`, `tests/unit/test_random_entry_anchor.py`, `tests/unit/test_regime_switcher_atr_percentile.py`
- `configs/campaign_010_session_breakout.yaml`, `configs/campaign_011_random_entry_anchor.yaml`, `configs/campaign_012_regime_switcher_atr_percentile.yaml`

## 3. Repo truth summary (verified)

| dimension | value |
|---|---|
| pytest count (baseline) | **818 passed** in 3.59 s |
| ruff status (baseline) | **3 pre-existing** in `research/lean_parity/algorithms/` (`2× RUF100` unused-noqa + `1× I001` unsorted-imports); untouched LEAN-parity archive; out of scope |
| `validate_research_archive.py` | ALL CHECKS PASSED (12 campaigns; 14 diagnostic artifacts; 227 evidence-index links resolve; 2,454 committed artifact files clean) |
| `check_research_freeze.py` | ALL CHECKS PASSED (loops refuse; no credentials) |
| `scan_artifacts_for_secrets.py` | PASSED |
| `paper-loop -c configs/paper.yaml` | **refused** — `trend_following` not approved |
| `demo-loop -c configs/practice.yaml` | **refused** — `trend_following` not approved |
| `forex_bot.cli --help` | **no `live-loop` command** present |
| `configs/approved_strategies.yaml` | `approved: []` (verified verbatim) |
| existing strategy modules | trend_following, volatility_breakout, pullback_continuation, mean_reversion, session_breakout, random_entry_anchor, regime_switcher_atr_percentile — **no** `cross_pair_currency_strength_rotation.py` yet |
| existing strategy configs | 7 strategy configs in `src/forex_bot/config.py` — **no** `CrossPairCurrencyStrengthRotationStrategyConfig` yet |
| existing `backtests/CAMPAIGN_013_*` artifacts | **none** — clean slate |

## 4. Current safety state (verified)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | REJECT (null-model anchor; untouched) |
| CAMPAIGN_012 | REJECT (untouched) |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | **no** (4 refusal layers; intact) |
| pytest baseline | 818 passes |
| ruff baseline | 3 pre-existing in `research/lean_parity/algorithms/` (out of scope) |
| live-promotion financing blocker | stands |

## 5. CAMPAIGN_013 purpose

Build the scaffold for `cross_pair_currency_strength_rotation 0.1.0-c013`
so the future evidence sprint can run walk-forward against it. The C6
hypothesis (verbatim from
[`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md)
§1):

> The G7 USD-denominated H4 universe contains 4 USD-base pairs
> (EUR_USD, GBP_USD, AUD_USD, NZD_USD) and 3 USD-quote pairs
> (USD_JPY, USD_CAD, USD_CHF). For each USD-base pair, the non-USD
> currency's relative-performance can be inferred from the H4
> close-to-close return. For each USD-quote pair, the non-USD
> currency's relative-performance is the inverse of the H4
> close-to-close return. Aggregating across all 7 pairs over a fixed
> rolling window yields a currency-strength rank for each of the 8
> currencies represented (USD plus the 7 others). The C6 hypothesis
> is that the strongest-vs-weakest currency rank gap predicts the
> direction of that pair over the next ~6 H4 bars, provided the
> rank gap exceeds a threshold large enough to overcome H4 cost
> drag.

This sprint **scaffolds the candidate only**; it cannot demonstrate
edge. The scaffold adds the strategy module, the config schema, ≥ 40
unit tests, the candidate YAML, and the CAMPAIGN_013 readiness docs
— nothing more.

## 6. Implementation files expected

| file | action | purpose |
|---|---|---|
| `src/forex_bot/strategies/cross_pair_currency_strength_rotation.py` | **NEW** | `CrossPairCurrencyStrengthRotationStrategy` implementing the `Strategy` protocol per R1-R8 |
| `src/forex_bot/strategies/__init__.py` | EDIT | re-export `CrossPairCurrencyStrengthRotationStrategy` |
| `src/forex_bot/config.py` | EDIT | add `CrossPairCurrencyStrengthRotationStrategyConfig` + `StrategyConfig.cross_pair_currency_strength_rotation` slot + enabled-list check |

No edits to engine, financing, RiskEngine, walk-forward harness,
broker / execution / loops, or any other source file.

## 7. Test files expected

| file | action | purpose |
|---|---|---|
| `tests/unit/test_cross_pair_currency_strength_rotation.py` | **NEW** | ≥ 40 deterministic unit tests covering config validation, pair-parser, strength mapping, rank-gap rule, R1-R8 fixtures, no-lookahead audit, rejected-family contamination audit, approval regression |

## 8. Docs expected

| file | action | purpose |
|---|---|---|
| `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md` | **NEW** (this doc; Phase 0) | scaffold-sprint plan + repo truth + safety state |
| `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md` | **NEW** (Phase 1) | binding R1-R8 + frozen parameters + sign convention + no-lookahead invariants |
| `docs/research/CAMPAIGN_013_PRECOMMIT_CHECKLIST.md` | **NEW** (Phase 4) | candidate pre-commit; null-baseline comparison gate; cross-pair-closes contract; gate vector inherited from CAMPAIGN_010 / 011 / 012; UNEXPECTED-PASS playbook |
| `docs/research/CAMPAIGN_013_STATUS.md` | **NEW** (Phase 4) | scaffold-only status; CAMPAIGN_002 / 010 / 011 / 012 remain REJECT; no evidence yet |
| `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_READINESS.md` | **NEW** (Phase 4) | scaffold-readiness summary; cross-pair runner requirement; null-baseline comparison; why this is a real candidate but not approved |
| `docs/research/CAMPAIGN_013_SMOKE_RESULT.md` | **NEW** (Phase 5) | smoke commands + outputs; explicit NON-EVIDENCE framing |
| `docs/research/CAMPAIGN_013_WALK_FORWARD_READINESS.md` | **NEW** (Phase 6) | future evidence-branch identity + inherited plan parameters + cross-pair runner integration requirement |
| `docs/research/CAMPAIGN_013_FINANCING_RISK_READINESS.md` | **NEW** (Phase 6) | financing overlay (ESTIMATED + conservative stress; MODELED refused) + risk diagnostics expectations |
| `docs/research/CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md` | **NEW** (Phase 6) | verifier capability lock; required only for an unexpected PASS; suggested future branch `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001` |
| `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md` | **NEW** (Phase 7) | end-of-scaffold summary; final validation; remaining blockers; recommended next branch (the evidence sprint) |
| `docs/research/EVIDENCE_INDEX.md` | EDIT (Phase 7) | add CAMPAIGN_013 scaffold sub-section |
| `docs/research/STRATEGY_STATUS.md` | EDIT (Phase 7) | update C6/CAMPAIGN_013 annotation to "scaffolded; awaiting evidence" |

## 9. Config files expected

| file | action | purpose |
|---|---|---|
| `configs/campaign_013_cross_pair_currency_strength_rotation.yaml` | **NEW** (Phase 4) | research-only loadable YAML; 7-pair H4 universe; frozen parameters; no paper/demo/live enablement |

## 10. Frozen parameters (binding — taken verbatim from discovery-004)

| parameter | value | notes |
|---|---|---|
| `version` | `0.1.0-c013` | |
| `timeframe` | `"H4"` | execution timeframe |
| `currency_strength_lookback_bars` | `24` | ~4 trading days |
| `rank_gap_threshold` | `4` | top-half vs bottom-half rank spectrum (|gap| ≥ 4 of 8) |
| `atr_lookback` | `14` | H4 ATR for stop sizing (mirrors CAMPAIGN_010/011/012) |
| `atr_stop_multiple` | `2.0` | matches CAMPAIGN_010/011/012 |
| `trailing_stop_atr_multiple` | `None` (forbidden in v1; validator rejects) | |
| `max_bars_in_trade` | `6` | time stop (≈ 1 trading day; matches CAMPAIGN_010/011/012) |
| `min_atr_pips` | `{}` | per-pair floor; default empty |
| `warm_up_bars` | `50` (effective via `warmup_bars_required()`) | covers `currency_strength_lookback_bars = 24` + ATR-14 + slack |

**Any deviation from these values constitutes a NEW candidate** that
requires its own discovery + design cycle. The runner / config loader
must reject any deviation.

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
- **Phase 3:** `pytest tests/unit/test_cross_pair_currency_strength_rotation.py -q`.
- **Phase 4:** config-load smoke for `configs/campaign_013_cross_pair_currency_strength_rotation.yaml`.
- **Phase 5:** the same as Phase 4 + a tiny fixture signal-generation smoke (already covered by tests).
- **Phase 7:** the full battery above + final repo `git status --short` clean check.

Test-count target: **818 baseline → ≥ 858 after Phase 3** (≥ 40 new
unit tests).

## 12. Non-goals (binding)

This scaffold sprint **must not** do any of the following:

- Run a historical backtest (any campaign).
- Run a walk-forward evidence sprint.
- Run a financing overlay or portfolio-risk diagnostics evidence run.
- Run a verifier evidence run.
- Fetch new candle data.
- Read `.env` or print any credential.
- Submit / create / modify / cancel / close / query any broker order.
- Query account orders / trades / positions / account snapshots /
  transaction streams.
- Use live broker credentials or demo / practice order execution.
- Run `paper-loop` or `demo-loop` for any purpose other than the
  refusal check.
- Create or invoke any `live-loop` command.
- Use QuantConnect or LEAN.
- Modify `configs/approved_strategies.yaml` (must remain `approved: []`).
- Add `cross_pair_currency_strength_rotation` to `configs/paper.yaml`
  or `configs/practice.yaml`.
- Revive / tune / parameter-search CAMPAIGN_002 / 010 / 011 / 012.
- Use CAMPAIGN_011 as a trading candidate.
- Change any historical campaign verdict.
- Optimize any C6 parameter based on smoke behavior or any prior
  campaign's result.
- Relax `max_open_positions` or risk settings to make cross-pair
  signals "fit" — the binding cross-pair-runner integration contract
  in the Phase 6 design explicitly documents that
  `MAX_OPEN_POSITIONS_EXCEEDED` rejections are known behavior, NOT
  bugs to fix.
- Present a trading recommendation.
- Claim readiness for paper / demo / live.
- Add `CAMPAIGN_013` to `docs/research/EVIDENCE_MANIFEST.json` (the
  manifest takes only campaigns that have produced an evidence
  verdict; CAMPAIGN_013 has none — see Phase 7).

## 13. Explicit safety statements

1. **This scaffold sprint cannot approve any strategy.** Approval is
   a deliberate, reviewed human action per
   [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md);
   no scaffold sprint can substitute for it.
2. **This scaffold sprint must not run evidence.** Walk-forward,
   financing overlay, portfolio-risk diagnostics, and verifier
   corroboration are all reserved for the future evidence sprint
   `research-cross-pair-currency-strength-rotation-walk-forward-001`.
   A passing unit-test suite or smoke test is **not** evidence.
3. **CAMPAIGN_011 is only the null baseline, not a trading
   candidate.** Its metrics are used as the falsifiability floor that
   CAMPAIGN_013 must beat by the margins codified in
   [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md);
   it is structurally impossible to approve CAMPAIGN_011 (null model
   by design).
4. **C6 / CAMPAIGN_013 is selected but not approved.** Selection
   means a future evidence sprint may evaluate it; selection does
   not mean any current sprint can deploy or paper-trade it.

## 14. Phase plan

| phase | output | commits |
|---|---|---|
| 0 | this plan doc | 1 |
| 1 | binding implementation spec | 1 |
| 2 | strategy module + config schema | 1 |
| 3 | ≥ 40 unit tests | 1 |
| 4 | research config + CAMPAIGN_013 docs (precommit + status + readiness) | 1 |
| 5 | non-evidence smoke result | 1 |
| 6 | future evidence-readiness docs (walk-forward + financing/risk + verifier) | 1 |
| 7 | sprint summary + EVIDENCE_INDEX + STRATEGY_STATUS update + final validation | 1 |

Each phase is a self-contained commit; if a phase is blocked, that
fact is documented and the next independent safe phase proceeds.

## 15. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md) (discovery sprint summary)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md) (binding design)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md) (this sprint's binding prompt)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md) (future evidence sprint's prompt)
- [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
