# Next Candidate Scaffold Branch Spec (Phase 7a)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-004`
`strategy_evidence: false`

Phase 7a binding spec for the **future scaffold sprint** that
implements C6 / `cross_pair_currency_strength_rotation 0.1.0-c013`
(CAMPAIGN_013). This doc is a binding *prompt template* for the next
Claude Code instance to begin from.

> No strategy approved. `configs/approved_strategies.yaml` remains
> `approved: []`. **The future scaffold sprint cannot approve any
> strategy.** Even a clean unit-test suite + smoke pass is not
> evidence.

## 1. Future branch identity

| field | value |
|---|---|
| **branch name** | **`research-cross-pair-currency-strength-rotation-001`** |
| base commit | (latest of `research-new-candidate-strategy-discovery-004`) |
| type | scaffold sprint (no evidence run) |
| binding design | [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md) |
| sibling reference | `research-random-entry-diagnostic-anchor-001` (CAMPAIGN_011 scaffold) + `research-regime-switcher-atr-percentile-001` (CAMPAIGN_012 scaffold) |

## 2. Phase outline (8 phases; mirrors CAMPAIGN_012 scaffold sprint)

| phase | output | scope |
|---|---|---|
| 0 | `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md` | repo truth audit + 8-phase scaffold plan |
| 1 | `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md` | translate the design into a machine-facing implementation spec |
| 2 | `src/forex_bot/strategies/cross_pair_currency_strength_rotation.py` + `src/forex_bot/strategies/__init__.py` (EDIT) + `src/forex_bot/config.py` (EDIT) | strategy module + config schema + StrategyConfig slot + enabled-list check |
| 3 | `tests/unit/test_cross_pair_currency_strength_rotation.py` | ≥ 30 deterministic unit tests |
| 4 | `configs/campaign_013_cross_pair_currency_strength_rotation.yaml` + `docs/research/CAMPAIGN_013_PRECOMMIT_CHECKLIST.md` + `docs/research/CAMPAIGN_013_STATUS.md` + `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_READINESS.md` | candidate config YAML + binding pre-commit + scaffold-only status + readiness summary |
| 5 | `docs/research/CAMPAIGN_013_SMOKE_RESULT.md` | non-evidence smoke: config-load, import, unit suite, optional walk-forward dry-run plan only (no execution) |
| 6 | `docs/research/CAMPAIGN_013_WALK_FORWARD_READINESS.md` + `docs/research/CAMPAIGN_013_FINANCING_RISK_READINESS.md` + `docs/research/CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md` | future-evidence readiness docs |
| 7 | `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md` + EDIT `docs/research/EVIDENCE_INDEX.md` + EDIT `docs/research/STRATEGY_STATUS.md` | sprint summary + EVIDENCE_INDEX scaffold sub-section + STRATEGY_STATUS annotation |

## 3. Expected files

**NEW source files:**

- `src/forex_bot/strategies/cross_pair_currency_strength_rotation.py` (~280 LOC)
- `tests/unit/test_cross_pair_currency_strength_rotation.py` (~700–900 LOC; ≥ 30 cases)
- `configs/campaign_013_cross_pair_currency_strength_rotation.yaml`

**EDIT source files:**

- `src/forex_bot/strategies/__init__.py` (re-export `CrossPairCurrencyStrengthRotationStrategy`)
- `src/forex_bot/config.py` (add `CrossPairCurrencyStrengthRotationStrategyConfig` + `StrategyConfig.cross_pair_currency_strength_rotation` slot + enabled-list check)

**NEW docs:**

- `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md` (Phase 0)
- `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md` (Phase 1)
- `docs/research/CAMPAIGN_013_PRECOMMIT_CHECKLIST.md` (Phase 4)
- `docs/research/CAMPAIGN_013_STATUS.md` (Phase 4)
- `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_READINESS.md` (Phase 4)
- `docs/research/CAMPAIGN_013_SMOKE_RESULT.md` (Phase 5)
- `docs/research/CAMPAIGN_013_WALK_FORWARD_READINESS.md` (Phase 6)
- `docs/research/CAMPAIGN_013_FINANCING_RISK_READINESS.md` (Phase 6)
- `docs/research/CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md` (Phase 6)
- `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md` (Phase 7)

## 4. Validation commands (per-phase + at sprint close)

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

Test-count target: **818 baseline → ≥ 848** after Phase 3 (≥ 30 new
unit tests).

## 5. Safety rules (binding for the scaffold sprint)

- **NO historical backtest.** Phase 5 smoke is dry-run plan only;
  output to `/tmp` (not committed).
- **NO data fetch.** All tests use synthetic in-memory fixtures.
- **NO broker / account / order / trade / position / transaction
  endpoint queries.**
- **NO `.env` read.** No credential print.
- **NO `live-loop` command creation.**
- **NO `configs/approved_strategies.yaml` mutation.**
- **NO enabling** `cross_pair_currency_strength_rotation` in
  `configs/paper.yaml` or `configs/practice.yaml`.
- **NO QuantConnect / LEAN.**
- **NO parameter tuning** — the 9 frozen parameters in §5 of the
  Phase 6 design are pre-committed; the runner-test asserts them
  before any smoke.
- **NO modifying any rejected-family strategy module** or any
  CAMPAIGN_002 / 010 / 011 / 012 doc.

## 6. Non-goals (binding)

- No `scripts/run_campaign_013.py` runner (that is for the *evidence*
  sprint, not the scaffold).
- No `backtests/CAMPAIGN_013_*/` artifact directory creation.
- No financing-overlay or risk-diagnostics script (those are evidence-sprint deliverables).
- No verifier extension.

## 7. Final report requirements (Phase 7 of scaffold sprint)

The scaffold sprint's Phase 7 summary doc must report:

1. Branch name (`research-cross-pair-currency-strength-rotation-001`).
2. Commit hashes by phase (8 hashes).
3. Files changed by phase.
4. Tests / validation commands run.
5. Latest full test count (≥ 848).
6. Ruff status.
7. Strategy files added.
8. Config files added.
9. Tests added (≥ 30; aim for 30+).
10. Docs added / updated.
11. R1–R8 rule summary.
12. Frozen parameter summary.
13. Cross-pair currency-strength feature summary.
14. No-lookahead safeguards.
15. Unit test coverage summary.
16. Smoke status + non-evidence framing.
17. Walk-forward readiness status.
18. Financing/risk readiness status.
19. Verifier readiness status.
20. Confirmation CAMPAIGN_013 is scaffold-only.
21. Confirmation no strategy is approved.
22. Confirmation `configs/approved_strategies.yaml` remains `approved: []`.
23. Confirmation CAMPAIGN_002 / 010 / 011 / 012 remain REJECT.
24. Confirmation no rejected family was tuned / revived.
25. Confirmation no historical backtest / evidence campaign was run.
26. Confirmation no data was fetched.
27. Confirmation no credentials were read or printed.
28. Confirmation no broker endpoint was queried.
29. Confirmation paper / demo / live remain blocked.
30. Confirmation no QuantConnect / LEAN was used.
31. Research freeze / archive status.
32. Local files created but not committed.
33. Remaining blockers.
34. Recommended next branch
    (`research-cross-pair-currency-strength-rotation-walk-forward-001`).
35. Exact files to review first.

## 8. Approval boundary (binding)

**The future scaffold sprint cannot approve any strategy.** Approval
requires:

1. Walk-forward verdict (future evidence sprint).
2. Financing overlay verdict (future evidence sprint).
3. Portfolio-risk diagnostics verdict (future evidence sprint).
4. Independent verifier extension (only if walk-forward verdict is
   `RESEARCH_PASS_UNAPPROVED`).
5. A deliberate human approval action per
   [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

Even after all five, only a human editing
`configs/approved_strategies.yaml` adds an approval.

## 9. Paper / demo / live blocked statement (binding)

- `paper-loop -c configs/paper.yaml` → **must refuse** at every phase
  boundary.
- `demo-loop -c configs/practice.yaml` → **must refuse**.
- `forex_bot.cli --help` → **must not list `live-loop`**.
- `check_research_freeze.py` → **must PASS `loops_refuse`**.

## 10. Cross-links

- [`NEXT_PREFERRED_DIRECTION_004.md`](NEXT_PREFERRED_DIRECTION_004.md) (Phase 5 selection)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md) (Phase 6 binding design)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md) (Phase 7b — future evidence sprint spec)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- Sibling scaffold sprints: `research-random-entry-diagnostic-anchor-001`, `research-regime-switcher-atr-percentile-001`
