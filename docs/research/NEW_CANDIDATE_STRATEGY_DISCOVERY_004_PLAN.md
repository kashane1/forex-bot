# `research-new-candidate-strategy-discovery-004` — Sprint Plan (Phase 0)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-004`
(worktree branch `claude/affectionate-fermi-d950fc`) · `strategy_evidence: false`

Phase 0 repo truth audit + 10-phase sprint plan for the
**research-new-candidate-strategy-discovery-004** sprint. Re-opens
candidate discovery after CAMPAIGN_012's REJECT. **Discovery/design
sprint only — no strategy implementation, no backtest, no evidence
campaign.**

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
> CAMPAIGN_012 all remain REJECT. `configs/approved_strategies.yaml`
> remains `approved: []`. Paper / demo / live remain blocked.
> CAMPAIGN_011 is the **null baseline only**, not a trading candidate.

## 1. Branch / base commit / repo state

| dimension | value |
|---|---|
| git branch (worktree) | `claude/affectionate-fermi-d950fc` |
| logical sprint branch | `research-new-candidate-strategy-discovery-004` |
| base commit (HEAD before Phase 0) | `6b27c30` — Phase 9 of `research-regime-switcher-atr-percentile-walk-forward-001` (CAMPAIGN_012 evidence-sprint close) |
| working tree at Phase 0 start | clean (`git status --short` empty except `.claude/` tooling cache) |

## 2. Repo truth summary (verified)

| dimension | value |
|---|---|
| pytest count (baseline) | **818 passed** in 3.56 s |
| ruff status (baseline) | **3 pre-existing** in `research/lean_parity/algorithms/` (`2× RUF100` unused-noqa + `1× I001` unsorted-imports); untouched LEAN-parity archive; out of scope |
| `validate_research_archive.py` | ALL CHECKS PASSED (12 campaigns; 14 diagnostic artifacts; 216 evidence-index links resolve; 2,443 committed artifact files clean) |
| `check_research_freeze.py` | ALL CHECKS PASSED (loops refuse; no credentials) |
| `scan_artifacts_for_secrets.py` | PASSED |
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

**Verdict:** REJECT (5 of 8 inherited gates fail; outside indistinguishability band in the WORSE direction on three of four binding axes). The C3 daily-ATR-percentile regime-switcher hypothesis is **falsified** for the 7-pair H4 OANDA-practice universe and current cost model. The regime gate amplified cost drag by allowing more bars to qualify without improving signal quality.

## 6. Approved strategy status (verified)

- `configs/approved_strategies.yaml`: `approved: []` (registry empty).
- No paper / demo / live enablement of any candidate.
- Paper-loop / demo-loop refuse at the `approved_strategies.yaml` gate.
- No `live-loop` CLI command exists.

## 7. Safety state (verified)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 | all REJECT (untouched) |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | **no** (4 refusal layers; intact) |
| live-promotion financing blocker | stands |

## 8. Files inspected (Phase 0 audit; full set planned)

**Recent campaign outputs:**

- `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md`
- `docs/research/CAMPAIGN_012_EVIDENCE_SUMMARY.md`
- `docs/research/CAMPAIGN_012_WALK_FORWARD_RESULT.md`
- `docs/research/CAMPAIGN_012_STATUS.md`
- `docs/research/CAMPAIGN_012_FINANCING_OVERLAY.md`
- `docs/research/CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md`
- `docs/research/CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md`
- `docs/research/CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`

**Discovery-003 outputs (predecessor; binding):**

- `docs/research/CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`
- `docs/research/NEXT_PREFERRED_REAL_CANDIDATE_003.md`
- `docs/research/NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`
- `docs/research/NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md`

**Project-wide research guards:**

- `docs/research/CAMPAIGN_010_REJECTION_CLOSEOUT.md`
- `docs/research/REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`
- `docs/research/STRATEGY_STATUS.md`
- `docs/research/WALK_FORWARD_RESEARCH_PROTOCOL.md`
- `docs/research/WALK_FORWARD_HARNESS_STATUS.md`
- `docs/research/FINANCING_MODEL_STATUS.md`
- `docs/research/STRATEGY_APPROVAL_PROCESS.md`
- `docs/research/FINAL_RESEARCH_DECISION_MEMO.md`

**Existing code surface to reference (not modify):**

- `src/forex_bot/strategies/{trend_following,volatility_breakout,pullback_continuation,mean_reversion,session_breakout,random_entry_anchor,regime_switcher_atr_percentile}.py`
- `src/forex_bot/config.py` (strategy config schemas)
- `src/forex_bot/backtesting/d1_aggregation.py` (D1AGG aggregator — exists)
- `configs/campaign_010_session_breakout.yaml`
- `configs/campaign_011_random_entry_anchor.yaml`
- `configs/campaign_012_regime_switcher_atr_percentile.yaml`
- `scripts/run_campaign_010.py`, `run_campaign_011.py`, `run_campaign_012.py`
- `research/walk_forward/`, `research/financing/`, `research/parity_verifier/`

## 9. Discovery goals

1. **Codify CAMPAIGN_012's REJECT** as a rejected-family closeout
   (Phase 1) so retuning is structurally prevented.
2. **Update anti-overfit guardrails** with the CAMPAIGN_012 lessons —
   specifically: "regime-gate threshold + trend-filter lookback +
   ATR-percentile cutoff are off-limits to retune"; "no adding
   session/pair filters to rescue a rejected regime switcher"
   (Phase 2).
3. **Reassess** the deferred candidates (C2 / C4) + infrastructure
   alternatives (MODELED financing capture, paired-entry engine
   support, verifier extension, ruff cleanup) against the **now-7
   rejected baseline** (5 prior + CAMPAIGN_011 null + CAMPAIGN_012
   real) — explicit scoring on research value, distinctness from
   rejected families, blockers, infrastructure compatibility
   (Phase 3).
4. **Propose 3–5 genuinely new candidate families** that are NOT
   retunes of any rejected strategy (Phase 4).
5. **Select exactly one next path** — either a new candidate family
   for a future scaffold sprint, or an infrastructure prerequisite —
   with explicit rationale (Phase 5).
6. **Design the selected path** in enough detail that the future
   sprint can begin without re-inventing it (Phase 6).
7. **Write binding future-branch specs** (Phase 7).
8. **Helper decision** — no code unless it's a tiny docs/checklist
   helper clearly justified (Phase 8).
9. **End-of-sprint summary** + EVIDENCE_INDEX + STRATEGY_STATUS
   updates + final validation (Phase 9).

## 10. Non-goals (binding)

This discovery sprint **must not** do any of the following:

- **Implement a new strategy.** No `src/forex_bot/strategies/*.py`
  module added or modified for any future candidate.
- **Run a historical backtest.** No `run_campaign_NNN.py` invocation.
- **Run a walk-forward evidence sprint.** No new campaign artifact
  directory.
- **Run a financing overlay** or **portfolio-risk diagnostics**
  evidence run.
- **Fetch new data.** No OANDA HTTP request; no `fetch-candles`.
- **Read `.env`** or print any credential.
- **Submit / query any broker / account / order / trade / position
  / transaction endpoint.**
- **Run `paper-loop` / `demo-loop`** except for the standing refusal
  check.
- **Create or invoke any `live-loop` command.**
- **Use QuantConnect / LEAN** (retired).
- **Modify `configs/approved_strategies.yaml`** (must remain `approved: []`).
- **Revive or tune** CAMPAIGN_002 / 010 / 011 / 012 (binding per
  this sprint's safety rules + the prior rejection closeouts).
- **Use CAMPAIGN_011 as a trading candidate** (null model by design).
- **Perform broad parameter search** or **optimize parameters based
  on prior campaign results**.
- **Choose a family by looking for knobs that would have helped a
  rejected campaign** (the Phase 2 guardrails enforce this).
- **Present a trading recommendation** or **claim readiness for paper
  / demo / live**.
- **Commit bulky data** (`*.sqlite3` gitignored; this sprint produces
  only markdown).

## 11. Validation commands (per-phase + final)

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

Test-count target: **818 baseline → maintained** (this is a
docs-only sprint; no code, no tests added).

## 12. Expected outputs (10 phases, 1 commit per phase)

| phase | output | type |
|---|---|---|
| 0 | this plan doc | NEW |
| 1 | `CAMPAIGN_012_REJECTION_CLOSEOUT.md` | NEW |
| 2 | `REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md` | NEW |
| 3 | `NEXT_DIRECTION_REASSESSMENT_004.md` | NEW |
| 4 | `CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md` | NEW |
| 5 | `NEXT_PREFERRED_DIRECTION_004.md` | NEW |
| 6 | `NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md` **OR** `NEXT_PREFERRED_INFRASTRUCTURE_DESIGN_004.md` (chosen per Phase 5) | NEW |
| 7 | `NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md` + `NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md` **OR** `NEXT_INFRASTRUCTURE_BRANCH_SPEC_004.md` (+ optional `POST_INFRA_CANDIDATE_BRANCH_SPEC_004.md`) | NEW |
| 8 | `NEW_CANDIDATE_DISCOVERY_004_HELPER_DECISION.md` | NEW |
| 9 | `NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md` + `EVIDENCE_INDEX.md` EDIT + `STRATEGY_STATUS.md` EDIT (optional) | NEW + EDIT |

## 13. Explicit safety statements

1. **This sprint cannot approve any strategy.** Approval requires
   the full six-evidence ladder + a deliberate human approval action
   per [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md);
   no discovery sprint can substitute for it.
2. **This sprint cannot implement a strategy.** Any strategy module,
   config schema slot, or test file is reserved for a future scaffold
   sprint.
3. **CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, and CAMPAIGN_012 must
   not be tuned or revived.** Each carries a binding rejection
   closeout (CAMPAIGN_010 closeout in `CAMPAIGN_010_REJECTION_CLOSEOUT.md`;
   CAMPAIGN_011's null-model design is permanently un-approvable;
   CAMPAIGN_012's closeout is this sprint's Phase 1). CAMPAIGN_011
   is **only** the null baseline.

## 14. Cross-links

- [`REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md`](REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md) (predecessor sprint's summary)
- [`CAMPAIGN_012_EVIDENCE_SUMMARY.md`](CAMPAIGN_012_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md) (verdict)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (null baseline)
- [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md) (predecessor candidate menu)
- [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md) (template for Phase 1)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md) (template for Phase 2)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
