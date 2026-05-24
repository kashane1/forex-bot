# `research-new-candidate-strategy-discovery-005` — Sprint Plan (Phase 0)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-005`
(worktree branch `claude/affectionate-fermi-d950fc`) · `strategy_evidence: false`

Phase 0 repo truth audit + 11-phase sprint plan (Phases 0–10) for the
**research-new-candidate-strategy-discovery-005** sprint. Re-opens
candidate discovery after CAMPAIGN_013's REJECT. **Discovery/design
sprint only — no strategy implementation, no backtest, no evidence
campaign, no financing overlay, no portfolio-risk diagnostics, no
verifier run, no data fetch.**

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
> CAMPAIGN_012 / CAMPAIGN_013 all remain REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper /
> demo / live remain blocked. CAMPAIGN_011 is the **null baseline
> only**, not a trading candidate.

## 1. Branch / base commit / repo state

| dimension | value |
|---|---|
| git branch (worktree) | `claude/affectionate-fermi-d950fc` |
| logical sprint branch | `research-new-candidate-strategy-discovery-005` |
| base commit (HEAD before Phase 0) | `ec3f848` — Phase 9 of `research-cross-pair-currency-strength-rotation-walk-forward-001` (CAMPAIGN_013 evidence-sprint close) |
| working tree at Phase 0 start | clean (`git status --short` empty except `.claude/` tooling cache, which is `.gitignore`d) |

## 2. Repo truth summary (verified at Phase 0)

| dimension | value |
|---|---|
| pytest count (baseline) | **875 passed** in 4.14 s |
| ruff status (baseline) | **3 pre-existing** in `research/lean_parity/algorithms/` (`2× RUF100` unused-noqa + `1× I001` unsorted-imports); untouched LEAN-parity archive; out of scope |
| `validate_research_archive.py` | ALL CHECKS PASSED (13 campaigns; 14 diagnostic artifacts; 248 evidence-index links resolve; 2,597 committed artifact files clean) |
| `check_research_freeze.py` | ALL CHECKS PASSED (loops refuse `['trend_following']`; no credentials) |
| `scan_artifacts_for_secrets.py` | PASSED (2,818 files value-scan-skipped; 2,667 files pattern-scanned; no credential value or shape) |
| `paper-loop -c configs/paper.yaml` | **refused** — `trend_following` not approved |
| `demo-loop -c configs/practice.yaml` | **refused** — `trend_following` not approved |
| `forex_bot.cli --help` | **no `live-loop` command** present |
| `configs/approved_strategies.yaml` | `approved: []` (verified verbatim) |

## 3. Latest campaign statuses (verified)

| campaign | strategy | verdict | role |
|---|---|---|---|
| CAMPAIGN_002 | `trend_following 0.1.0` | REJECT | historical rejected; untouched |
| CAMPAIGN_010 | `session_breakout 0.1.0-c010` | REJECT | historical rejected; untouched |
| CAMPAIGN_011 | `random_entry_anchor 0.1.0-c011` | REJECT (null-model anchor) | null baseline; **not a trading candidate** |
| CAMPAIGN_012 | `regime_switcher_atr_percentile 0.1.0-c012` | REJECT | C3 regime-switcher; falsified; **off-limits to retune** |
| **CAMPAIGN_013** | **`cross_pair_currency_strength_rotation 0.1.0-c013`** | **REJECT** | **C6 cross-pair rotator; falsified; off-limits to retune (this sprint's Phase 1 codifies the closeout)** |

## 4. CAMPAIGN_011 null-baseline summary (verbatim from [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md))

| metric | CAMPAIGN_011 floor |
|---|---:|
| aggregate expectancy R | **−0.0024** |
| aggregate profit factor | **0.91** |
| aggregate return % (4 y) | **−0.53 %** |
| pairs_positive | **3 / 7** |
| fold_pass_rate | **0 / 8** |
| total trades | 1,177 |
| USD_JPY expectancy | literally **+0.0000** (random-walk floor) |

**Meaningful-improvement margins** any future real-edge candidate must beat:

- aggregate expectancy R: by **≥ +0.0524** (→ ≥ 0.05 R)
- aggregate profit factor: by **≥ +0.19** (→ ≥ 1.10)
- aggregate return %: meaningfully positive (≥ **+5 %**)
- pairs_positive: **≥ 4 / 7**
- fold_pass_rate: **100 %** (strict)

**Indistinguishable-from-null REJECT band:** within
± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair of CAMPAIGN_011 → REJECT.

## 5. CAMPAIGN_012 rejection summary (per [`CAMPAIGN_012_EVIDENCE_SUMMARY.md`](CAMPAIGN_012_EVIDENCE_SUMMARY.md))

| metric | CAMPAIGN_012 result | CAMPAIGN_011 floor | gap |
|---|---:|---:|---|
| aggregate expectancy R | **−0.0521** | −0.0024 | −0.0497 (WORSE) |
| aggregate profit factor | **0.034** | 0.91 | −0.876 (WORSE) |
| aggregate return % (4 y) | **−43.52 %** | −0.53 % | −42.99 pp (WORSE) |
| pairs_positive | **1 / 7** | 3 / 7 | −2 pairs (WORSE) |
| fold_pass_rate | **0 / 8** | 0 / 8 | 0 (same) |
| total trades | 3,726 | 1,177 | ~3.2 × |

**Verdict:** REJECT (5 of 8 inherited gates fail; outside indistinguishability band in the WORSE direction on three of four binding axes). The C3 daily-ATR-percentile regime-switcher hypothesis is falsified for the 7-pair H4 OANDA-practice universe and current cost model. The regime gate amplified cost drag by allowing more bars to qualify without improving signal quality.

## 6. CAMPAIGN_013 rejection summary (per [`CAMPAIGN_013_EVIDENCE_SUMMARY.md`](CAMPAIGN_013_EVIDENCE_SUMMARY.md))

| metric | CAMPAIGN_013 result | CAMPAIGN_011 floor | gap |
|---|---:|---:|---|
| aggregate expectancy R | **−0.0564** | −0.0024 | −0.0540 (WORSE) |
| aggregate profit factor | **0.000** | 0.91 | −0.910 (WORSE) |
| aggregate return % (4 y) | **−113.36 %** | −0.53 % | −112.83 pp (WORSE) |
| pairs_positive | **1 / 7** (USD_JPY +0.0000 R) | 3 / 7 | −2 pairs (WORSE) |
| fold_pass_rate | **0 / 8** | 0 / 8 | 0 (same) |
| total trades | **7,940** | 1,177 | ~6.7 × |
| financing (stress, USD) | −139.99 | −24.38 | USD_JPY flips + → − under stress |
| cross-pair runner contract | **SATISFIED on all 8 folds** | n/a | REJECT is on inherited gates alone, not BLOCKED |

**Verdict:** REJECT (5 of 8 inherited gates fail; **catastrophically** outside the indistinguishability band in the WORSE direction on all four binding axes). The C6 cross-pair currency-strength rotation hypothesis ("rank-gap ≥ 4/7 over 24-bar log-return strength, long-strong-base / short-strong-quote") is **falsified** on the 7-pair H4 OANDA-practice universe. The rank-gap rule amplified trade frequency ~6.7 × vs the null baseline without improving signal quality — CAMPAIGN_013 is the **worst-performing campaign to date** by aggregate return, profit factor, and trade count.

## 7. Approved strategy status (verified)

- `configs/approved_strategies.yaml`: `approved: []` (registry empty).
- No paper / demo / live enablement of any candidate.
- Paper-loop / demo-loop refuse at the `approved_strategies.yaml` gate.
- No `live-loop` CLI command exists.

## 8. Safety state (verified)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | **no** (4 refusal layers; intact) |
| live-promotion financing blocker | stands |

## 9. Files inspected (Phase 0 audit)

**CAMPAIGN_013 evidence (the trigger for this discovery sprint):**

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md)
- [`CAMPAIGN_013_EVIDENCE_SUMMARY.md`](CAMPAIGN_013_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_013_STATUS.md`](CAMPAIGN_013_STATUS.md)
- [`CAMPAIGN_013_FINANCING_OVERLAY.md`](CAMPAIGN_013_FINANCING_OVERLAY.md)
- [`CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md)
- [`CAMPAIGN_013_DATA_PROVENANCE.md`](CAMPAIGN_013_DATA_PROVENANCE.md)

**Discovery-004 outputs (predecessor; binding):**

- [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md)
- [`NEXT_PREFERRED_DIRECTION_004.md`](NEXT_PREFERRED_DIRECTION_004.md)
- [`NEXT_DIRECTION_REASSESSMENT_004.md`](NEXT_DIRECTION_REASSESSMENT_004.md)
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md)
- [`NEW_CANDIDATE_DISCOVERY_004_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_004_HELPER_DECISION.md)

**Project-wide research guards:**

- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)

**Existing code surface to reference (NOT modify):**

- `src/forex_bot/strategies/{trend_following,volatility_breakout,pullback_continuation,mean_reversion,session_breakout,random_entry_anchor,regime_switcher_atr_percentile,cross_pair_currency_strength_rotation}.py`
- `src/forex_bot/config.py` (strategy config schemas)
- `configs/{campaign_010_session_breakout,campaign_011_random_entry_anchor,campaign_012_regime_switcher_atr_percentile,campaign_013_cross_pair_currency_strength_rotation}.yaml`
- `configs/approved_strategies.yaml` (registry — empty; verified)
- `scripts/run_campaign_{010,011,012,013}.py`
- `research/walk_forward/`, `research/financing/`, `research/parity_verifier/` (if present)

## 10. Discovery goals

1. **Codify CAMPAIGN_013's REJECT** as a rejected-family closeout
   (Phase 1) so the cross-pair rotator family cannot be retuned.
2. **Establish the turnover-amplification anti-pattern** as a
   first-class binding guardrail (Phase 2). CAMPAIGN_011 → CAMPAIGN_012
   → CAMPAIGN_013 shows a monotonic slope (1,177 → 3,726 → 7,940
   trades; −0.53 % → −43.52 % → −113.36 % return). Any future
   candidate that adds turnover-amplifying logic on top of a negative-
   edge entry direction is structurally disqualified unless it
   explicitly explains why net edge survives costs.
3. **Update anti-overfit guardrails** with the CAMPAIGN_013-specific
   patterns — specifically: "no cross-pair rank gate with different
   threshold"; "no cross-pair rotator with different lookback"; "no
   pair-filtered post-rejection rescue"; "no session/regime rescue
   filter on top of a rejected cross-pair rotator" (Phase 3).
4. **Reassess** the deferred candidates (C2 / C4 / C7 / C8 / C9) +
   infrastructure alternatives (MODELED financing capture, paired-
   entry engine support, verifier extension, ruff cleanup) against
   the **now-8 rejected baseline** (5 prior + CAMPAIGN_011 null +
   CAMPAIGN_012 real + CAMPAIGN_013 real) (Phase 4).
5. **Propose 3–5 genuinely new candidate families** or infrastructure-
   first paths that are NOT retunes of any rejected strategy and that
   explicitly address the turnover-amplification anti-pattern
   (Phase 5).
6. **Select exactly one next path** — either a new candidate family
   for a future scaffold sprint, or an infrastructure prerequisite —
   with explicit rationale (Phase 6).
7. **Design the selected path** in enough detail that the future
   sprint can begin without re-inventing it (Phase 7).
8. **Write binding future-branch specs** (Phase 8).
9. **Helper decision** — no code unless it's a tiny docs/checklist
   helper clearly justified (Phase 9).
10. **End-of-sprint summary** + EVIDENCE_INDEX + STRATEGY_STATUS
    updates + final validation (Phase 10).

## 11. Non-goals (binding)

This discovery sprint **must not** do any of the following:

- **Implement a new strategy.** No `src/forex_bot/strategies/*.py`
  module added or modified for any future candidate.
- **Run a historical backtest.** No `run_campaign_NNN.py` invocation.
- **Run a walk-forward evidence sprint.** No new campaign artifact
  directory.
- **Run a financing overlay** or **portfolio-risk diagnostics**
  evidence run.
- **Run a verifier evidence run.**
- **Fetch new data.** No OANDA HTTP request; no `fetch-candles`.
- **Read `.env`** or print any credential.
- **Submit / query any broker / account / order / trade / position
  / transaction endpoint.**
- **Run `paper-loop` / `demo-loop`** except for the standing refusal
  check.
- **Create or invoke any `live-loop` command.**
- **Use QuantConnect / LEAN** (retired).
- **Modify `configs/approved_strategies.yaml`** (must remain `approved: []`).
- **Revive or tune** CAMPAIGN_002 / 010 / 011 / 012 / 013 (binding per
  this sprint's safety rules + the prior rejection closeouts +
  Phase 1 of this sprint).
- **Use CAMPAIGN_011 as a trading candidate** (null model by design).
- **Use CAMPAIGN_013 per-pair results to select a pair-only rescue
  candidate** (USD_JPY's +0.0000 R is the random-walk floor; not a
  positive signal).
- **Perform broad parameter search** or **optimize parameters based
  on prior campaign results**.
- **Choose a family by looking for knobs that would have helped a
  rejected campaign** (the Phase 3 guardrails enforce this).
- **Select a turnover-amplifying candidate** unless the thesis
  explicitly explains why net edge should survive costs (the Phase 2
  anti-pattern enforces this).
- **Present a trading recommendation** or **claim readiness for paper
  / demo / live**.
- **Commit bulky data** (`*.sqlite3` gitignored; this sprint produces
  only markdown).

## 12. Validation commands (per-phase + final)

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

Test-count target: **875 baseline → maintained** (this is a docs-only
sprint; no code, no tests added).

Ruff target: **3 pre-existing in `research/lean_parity/algorithms/`
maintained** (untouched LEAN-parity archive).

## 13. Expected outputs (11 phases, 1 commit per phase)

| phase | output | type |
|---|---|---|
| 0 | this plan doc (`NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md`) | NEW |
| 1 | `CAMPAIGN_013_REJECTION_CLOSEOUT.md` | NEW |
| 2 | `TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md` | NEW |
| 3 | `REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md` | NEW |
| 4 | `NEXT_DIRECTION_REASSESSMENT_005.md` | NEW |
| 5 | `CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md` | NEW |
| 6 | `NEXT_PREFERRED_DIRECTION_005.md` | NEW |
| 7 | `NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md` **OR** `NEXT_PREFERRED_INFRASTRUCTURE_DESIGN_005.md` (chosen per Phase 6) | NEW |
| 8 | `NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md` + `NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md` **OR** `NEXT_INFRASTRUCTURE_BRANCH_SPEC_005.md` (+ optional `POST_INFRA_CANDIDATE_BRANCH_SPEC_005.md`) | NEW |
| 9 | `NEW_CANDIDATE_DISCOVERY_005_HELPER_DECISION.md` | NEW |
| 10 | `NEW_CANDIDATE_STRATEGY_DISCOVERY_005_SUMMARY.md` + `EVIDENCE_INDEX.md` EDIT + `STRATEGY_STATUS.md` EDIT (optional) | NEW + EDIT |

## 14. Explicit safety statements

1. **This sprint cannot approve any strategy.** Approval requires
   the full six-evidence ladder + a deliberate human approval action
   per [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md);
   no discovery sprint can substitute for it.
2. **This sprint cannot implement a strategy.** Any strategy module,
   config schema slot, test file, or runner script is reserved for a
   future scaffold sprint.
3. **CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, and
   CAMPAIGN_013 must not be tuned or revived.** Each carries a
   binding rejection closeout (CAMPAIGN_010 closeout in
   `CAMPAIGN_010_REJECTION_CLOSEOUT.md`; CAMPAIGN_011's null-model
   design is permanently un-approvable; CAMPAIGN_012's closeout in
   `CAMPAIGN_012_REJECTION_CLOSEOUT.md`; CAMPAIGN_013's closeout is
   this sprint's Phase 1). CAMPAIGN_011 is **only** the null baseline.
4. **Turnover amplification is now a first-class anti-pattern.**
   Phase 2 codifies this. Any future candidate that increases trade
   frequency without explicitly justifying why net edge survives
   spread / slippage / financing costs is structurally disqualified.

## 15. Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md) (predecessor sprint's summary)
- [`CAMPAIGN_013_EVIDENCE_SUMMARY.md`](CAMPAIGN_013_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md) (verdict)
- [`CAMPAIGN_013_FINANCING_OVERLAY.md`](CAMPAIGN_013_FINANCING_OVERLAY.md)
- [`CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md) (template for Phase 1)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md) (base anti-overfit guardrails)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md) (CAMPAIGN_012 addendum; template for Phase 3)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md) (predecessor discovery sprint)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
