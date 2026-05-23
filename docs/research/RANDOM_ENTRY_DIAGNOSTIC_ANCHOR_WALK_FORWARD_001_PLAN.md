# Random-Entry Diagnostic Anchor — Walk-Forward Evidence Sprint Plan

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-walk-forward-001`
`strategy_evidence: false`

Phase 0 truth audit + sprint plan for the **CAMPAIGN_011
walk-forward evidence sprint** (`random_entry_anchor 0.1.0-c011`
— the C5 diagnostic-anchor null model). **This document does not
approve the candidate. CAMPAIGN_011 cannot be approved by
design.**

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.
> **CAMPAIGN_011 is a null model — even an unexpected PASS
> triggers the investigation playbook, never promotion.**

## 1. Repo state (Phase 0 audit)

| dimension | value |
|---|---|
| current branch | `claude/affectionate-fermi-d950fc` (worktree for `research-random-entry-diagnostic-anchor-walk-forward-001`) |
| base commit | `53bcbd4` — Phase 7 of `research-random-entry-diagnostic-anchor-001` (CAMPAIGN_011 scaffold complete) |
| worktree path | `/Users/kashane/dev/forex-bot/.claude/worktrees/affectionate-fermi-d950fc/` |
| `git status` at Phase 0 start | clean |
| `configs/approved_strategies.yaml` | **`approved: []`** (verified) |
| CAMPAIGN_002 status | **REJECT** (unchanged; untouched) |
| CAMPAIGN_010 status | **REJECT** (unchanged; untouched) |
| CAMPAIGN_011 status | scaffold-only (no verdict yet; cannot be approved by design) |
| paper-loop / demo-loop | refuse — verified |
| live-loop | does not exist — verified |
| QuantConnect / LEAN | retired; not used |

### 1.1 Baseline validation results

| check | result |
|---|---|
| `python -m pytest -q` | **771 passed** in 2.92s |
| `ruff check src tests scripts research` | **11 pre-existing UP042 findings** in untouched files (`research/parity_verifier/models.py`, `research/walk_forward/models.py`, `research/financing/models.py`, `research/lean_parity/algorithms/...`). Matches the documented baseline. |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED (10 campaigns, 14 diagnostic artifacts, 181 evidence-index links, 2,158 artifact files clean) |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED |
| `python -m forex_bot.cli paper-loop -c configs/paper.yaml` | refused |
| `python -m forex_bot.cli demo-loop -c configs/practice.yaml` | refused |
| `python -m forex_bot.cli --help` | no `live-loop` command present |

### 1.2 Files inspected (read-only)

Scaffold + design (the binding documents from the prior sprint):

- [`docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md)
- [`docs/research/CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md)
- [`docs/research/CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
- [`docs/research/CAMPAIGN_011_SMOKE_RESULT.md`](CAMPAIGN_011_SMOKE_RESULT.md)
- [`docs/research/CAMPAIGN_011_WALK_FORWARD_READINESS.md`](CAMPAIGN_011_WALK_FORWARD_READINESS.md)
- [`docs/research/CAMPAIGN_011_FINANCING_RISK_READINESS.md`](CAMPAIGN_011_FINANCING_RISK_READINESS.md)
- [`docs/research/CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md)
- [`docs/research/NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md) (the binding prompt spec for this sprint)
- [`docs/research/WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`docs/research/WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`docs/research/FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`docs/research/STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`docs/research/STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`docs/research/FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)

Implementation patterns (the structural template):

- [`src/forex_bot/strategies/random_entry_anchor.py`](../../src/forex_bot/strategies/random_entry_anchor.py) (~190 LOC; ready)
- [`src/forex_bot/strategies/__init__.py`](../../src/forex_bot/strategies/__init__.py)
- [`src/forex_bot/config.py`](../../src/forex_bot/config.py) (`RandomEntryAnchorStrategyConfig` slot)
- [`tests/unit/test_random_entry_anchor.py`](../../tests/unit/test_random_entry_anchor.py) (36 cases passing)
- [`configs/campaign_011_random_entry_anchor.yaml`](../../configs/campaign_011_random_entry_anchor.yaml)
- [`scripts/run_campaign_010.py`](../../scripts/run_campaign_010.py) (template for the new runner)
- [`scripts/build_campaign_010_financing_overlay.py`](../../scripts/build_campaign_010_financing_overlay.py) (template for Phase 6)
- [`scripts/build_campaign_010_risk_diagnostics.py`](../../scripts/build_campaign_010_risk_diagnostics.py) (template for Phase 7)
- [`research/walk_forward/`](../../research/walk_forward/) — package unchanged
- [`research/financing/`](../../research/financing/) — package unchanged

## 2. CAMPAIGN_011 scaffold status (verified inherited from prior sprint)

| component | status |
|---|---|
| Strategy module | committed: [`src/forex_bot/strategies/random_entry_anchor.py`](../../src/forex_bot/strategies/random_entry_anchor.py) |
| Strategy re-export | committed: [`src/forex_bot/strategies/__init__.py`](../../src/forex_bot/strategies/__init__.py) |
| StrategyConfig sub-model + slot | committed: [`src/forex_bot/config.py`](../../src/forex_bot/config.py) |
| Research config | committed: [`configs/campaign_011_random_entry_anchor.yaml`](../../configs/campaign_011_random_entry_anchor.yaml) (frozen parameters match spec verbatim; `master_seed=20260523`, `entry_probability_per_bar=0.05`, `atr_lookback=14`, `atr_stop_multiple=2.0`, `max_bars_in_trade=6`) |
| Unit tests | committed: [`tests/unit/test_random_entry_anchor.py`](../../tests/unit/test_random_entry_anchor.py) — 36 cases passing |
| Pre-commit checklist | committed: [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md) |
| Readiness docs | committed (4 docs: walk-forward, financing-risk, independent-verifier, scaffold-readiness) |

The candidate is structurally ready for this evidence sprint to
drive `WalkForwardResults`.

## 3. Local data status

| dimension | value |
|---|---|
| expected store path | `./data/campaign_002.sqlite3` (per `configs/campaign_011_random_entry_anchor.yaml`) |
| symlink status | **already present** — `data/campaign_002.sqlite3 → /Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` (created by `research-asian-london-session-breakout-walk-forward-001` Phase 1; gitignored via `/data/` rule + `*.sqlite3` rule) |
| **per-pair H4 candle counts (audited this Phase 0; `completed_only=True`)** | EUR_USD 9931, GBP_USD 9931, USD_JPY 9932, AUD_USD 9931, USD_CAD 9931, USD_CHF 9931, NZD_USD 9935 — **total 69,522** (identical to CAMPAIGN_010's audit) |
| coverage window per pair | **2020-01-01 22:00:00 UTC → 2026-05-19 21:00:00 UTC** (identical across pairs) |
| recorded source label | `oanda-practice` (all pairs) |
| instrument metadata (`InstrumentRepo.get`) | present for all 7 pairs (`pip_location`, `display_precision` populated) |
| credentials used for this audit | **none** (read-only via `forex_bot.data.repositories`) |
| credentials printed | **none** |
| broker / OANDA call this audit | **none** |
| read-only candle regeneration needed? | **no** — existing symlink + store provide everything |

## 4. Sprint phases (10 commits)

| phase | scope | deliverable(s) |
|---|---|---|
| 0 (this doc) | Repo truth + 10-phase plan | [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md) |
| 1 | Data provenance | [`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md) |
| 2 | Authoritative walk-forward plan via `scripts/run_walk_forward_dry_run.py` (8 folds; rolling; frozen; matches CAMPAIGN_010 verbatim) | `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/{plan.json,plan.md}` + [`CAMPAIGN_011_WALK_FORWARD_PLAN.md`](CAMPAIGN_011_WALK_FORWARD_PLAN.md) |
| 3 | Per-fold runner — new `scripts/run_campaign_011.py` cloning `scripts/run_campaign_010.py`'s pattern, with `RandomEntryAnchorStrategy` and `FROZEN_PARAMETERS` from CAMPAIGN_011 pre-commit | runner script + ruff/import check |
| 4 | Execute per-fold backtests (8 folds × 7 pairs); commit compact per-pair summaries + trades CSV; commit `walk_forward/results.{json,md}` + `fold_detail.json` | [`CAMPAIGN_011_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_011_WALK_FORWARD_EXECUTION.md) + per-pair-per-fold artifacts |
| 5 | Apply pre-declared gates; classify verdict (expected REJECT; UNEXPECTED PASS → INVESTIGATE_PIPELINE) | [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md) |
| 6 | Financing overlay via new `scripts/build_campaign_011_financing_overlay.py` (clone of CAMPAIGN_010 financing script); ESTIMATED + conservative stress; MODELED refused | [`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md) + `financing/financing_run.{json,md}` + `financing/financing_summary.json` |
| 7 | Portfolio-risk diagnostics via new `scripts/build_campaign_011_risk_diagnostics.py` (clone of CAMPAIGN_010 risk script); emphasize uniform per-pair + session distribution | [`CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md) + `risk/diagnostics.{json,md}` |
| 8 | Verifier capability assessment (NOT RUN — capability-locked to CAMPAIGN_002) | [`CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md) |
| 9 | Update `CAMPAIGN_011_STATUS.md`, `STRATEGY_STATUS.md`, `EVIDENCE_INDEX.md`, `EVIDENCE_MANIFEST.json`; write `CAMPAIGN_011_EVIDENCE_SUMMARY.md` + `RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md`; final validation suite | sprint summary + updated registries |

Commits at the end of each phase.

## 5. Expected commands (Phases 2–9)

```bash
# Phase 2 — plan generation.
.venv/bin/python scripts/run_walk_forward_dry_run.py \
    --campaign-name CAMPAIGN_011 \
    --universe-start 2020-01-01 --universe-end 2026-05-20 \
    --style rolling --parameter-mode frozen \
    --train-days 540 --validation-days 180 --test-days 180 \
    --step-days 180 \
    --output backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/

# Phase 3 — new runner (clone of CAMPAIGN_010's).
# (No invocation in Phase 3; Phase 4 invokes it.)

# Phase 4 — per-fold execution.
.venv/bin/python scripts/run_campaign_011.py \
    --config configs/campaign_011_random_entry_anchor.yaml \
    --plan backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json \
    --out backtests/CAMPAIGN_011_random_entry_anchor/

# Phase 6 — financing overlay.
.venv/bin/python scripts/build_campaign_011_financing_overlay.py \
    --campaign-dir backtests/CAMPAIGN_011_random_entry_anchor/

# Phase 7 — portfolio-risk diagnostics.
.venv/bin/python scripts/build_campaign_011_risk_diagnostics.py \
    --campaign-dir backtests/CAMPAIGN_011_random_entry_anchor/
```

## 6. Validation plan

After every commit:

- `python -m pytest -q` (≥ 771)
- `ruff check src tests scripts research` — must not introduce
  any new finding beyond the 11 pre-existing UP042
- `python scripts/validate_research_archive.py`
- `python scripts/check_research_freeze.py`
- `python scripts/scan_artifacts_for_secrets.py`

Loops + CLI surface checks repeated at Phase 9.

## 7. Gates this sprint will evaluate (verbatim references)

Every per-fold + aggregate gate from
[`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
§11 is binding (the gates are inherited verbatim from
CAMPAIGN_010's pre-commit so the entry-signal comparison is
apples-to-apples). The pre-commit-checklist values are the
authority; the runner will report the gate vector unmodified.
**No gate is relaxed after seeing results.**

## 8. Non-goals (explicit)

- **No parameter tuning.** Frozen-parameter mode only.
- **No seed optimization.** `master_seed = 20260523` is fixed.
- **No CAMPAIGN_002 / CAMPAIGN_010 revival.** Both REJECT; both
  untouched. CAMPAIGN_010's exit logic + walk-forward fold
  structure + gate vector are inherited deliberately so the
  entry-signal comparison is clean.
- **No paper / demo / live promotion.** Null model is structurally
  ineligible.
- **No approval action.** `configs/approved_strategies.yaml`
  remains `approved: []`.
- **No QuantConnect / LEAN.**
- **No order submission.** No broker call. No `.env` read. No
  credential printed.
- **No new external dependency.**
- **No engine-PnL change.** Financing is an overlay on top of
  engine output; the engine PnL formula is unchanged.

## 9. Safety invariants

- `configs/approved_strategies.yaml`: **`approved: []`** (verified;
  remains).
- **CAMPAIGN_002 REJECT** (untouched).
- **CAMPAIGN_010 REJECT** (untouched).
- **CAMPAIGN_011** null model — cannot be approved by design.
- **Paper / demo / live blocked.** `paper-loop` and `demo-loop`
  refuse. No `live-loop` command.
- **No broker / OANDA call** — the existing symlinked store
  covers the entire 7-pair × 6-year universe.
- **No `.env` read; no credential printed; no broker account
  endpoint queried.**
- **No QuantConnect / LEAN.**
- **No bespoke-engine edit.** No `src/forex_bot/financing.py`
  edit.
- **No `MODELED` financing** — overlay uses
  `default_stress_rate_source()` (ESTIMATED + conservative
  stress); the four-layer MODELED refusal stands.
- **Bulky artifacts uncommitted.** Per-fold CSV/JSON dumps
  follow the CAMPAIGN_010 convention; only compact summary docs
  + per-pair summaries + trades CSV are committed.

## 10. Explicit no-approval statements

1. **This sprint cannot approve CAMPAIGN_011.** Approval is a
   deliberate human action with a documented `ApprovalEntry` per
   [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).
   The candidate is a null model; the protocol's §4 whitelist
   explicitly classifies it as "Baseline / null model — cannot
   itself be the 'preferred candidate' for paper promotion."
2. **A passing walk-forward verdict is not paper/demo readiness.**
   For CAMPAIGN_011, the expected outcome is REJECT.
3. **A passing financing-overlay diagnostic is not MODELED
   financing.** It is ESTIMATED + conservative-stress under
   `FINANCING_MODEL_PROTOCOL.md`; MODELED remains refused.
4. **The verifier status doc is not independent corroboration**
   unless the verifier actually runs against the candidate's
   trade artifacts under its declared tolerances. Item 5 of the
   six-evidence ladder is **not binding** for a null model that
   cannot be paper-promoted.

## 11. UNEXPECTED PASS investigation rule (binding)

If `WalkForwardResults.overall_verdict == "PASS"` (extremely
unlikely under random entry on H4 majors with spread + ATR-stop
costs):

1. **DO NOT** add `random_entry_anchor` to
   `configs/approved_strategies.yaml`.
2. **DO NOT** treat the result as evidence of an edge.
3. **DO** trigger the investigation playbook per
   [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
   §12:
   - Confirm `seed_input` does not include any bar-`t` data
     (re-grep `_derive_random_pair`'s signature + source).
   - Confirm fold-boundary leakage rules pass.
   - Confirm structural audits pass (no `forex_bot.broker`
     import; no CAMPAIGN_002 / 010 keys).
   - Confirm the entry-probability rate matches expected
     ~5 % per bar within statistical bounds.
   - Confirm the long-short distribution matches 50 / 50 within
     statistical bounds.
4. **DO** classify the verdict as `INVESTIGATE_PIPELINE` (or
   the repo-consistent equivalent) and escalate to a separate
   investigation sprint.
5. **DO** commit the result honestly; an unexpected PASS that
   turns out to be a pipeline bug is **not** a research-pass —
   it is a bug report.

## 12. Cross-links

- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
- [`CAMPAIGN_011_SMOKE_RESULT.md`](CAMPAIGN_011_SMOKE_RESULT.md)
- [`CAMPAIGN_011_WALK_FORWARD_READINESS.md`](CAMPAIGN_011_WALK_FORWARD_READINESS.md)
- [`CAMPAIGN_011_FINANCING_RISK_READINESS.md`](CAMPAIGN_011_FINANCING_RISK_READINESS.md)
- [`CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md)
  (the binding prompt spec this sprint follows)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
  (the comparison baseline + structural template)
- [`CAMPAIGN_010_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_010_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md)
- [`CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
