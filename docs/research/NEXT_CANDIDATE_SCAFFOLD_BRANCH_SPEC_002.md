# Next Candidate — Scaffold Branch Spec (Sprint 002)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-002`
`strategy_evidence: false`

Phase 5a future-branch prompt specification for the **scaffold
sprint** that will implement CAMPAIGN_011 / `random_entry_anchor
0.1.0-c011` (the C5 diagnostic anchor selected in
[`NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md)).
**This document does not implement the candidate.** It is the
prompt a future Claude Code instance can use to run the scaffold
sprint cleanly.

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. **CAMPAIGN_011 is a diagnostic anchor / null
> model; the scaffold sprint cannot approve it.**

## 1. Branch identity

| field | value |
|---|---|
| branch name | `research-random-entry-diagnostic-anchor-001` |
| sprint type | **scaffold** (strategy module + config + tests + smoke; no walk-forward evidence run) |
| base commit | the tip of `research-new-candidate-strategy-discovery-002` (this discovery sprint) |
| campaign label | `CAMPAIGN_011` |
| strategy id | `random_entry_anchor` |
| strategy version | `0.1.0-c011` |
| target deliverables | strategy module + config sub-model + ≥ 20 unit tests + research config + pre-commit checklist + status doc + smoke result + readiness docs (walk-forward + financing + risk) + sprint summary |
| expected commits | 8 (Phase 0 → Phase 7) |

## 2. Standing safety rules (verbatim, binding for the scaffold sprint)

The scaffold sprint must reproduce every standing safety rule
this discovery sprint's prompt enumerated, plus:

- **Do not approve any strategy.** No edit to
  `configs/approved_strategies.yaml` except to verify it remains
  `approved: []`.
- **Do not run paper-loop or demo-loop except refusal checks.**
- **Do not create or run live-loop.**
- **Do not submit, create, modify, cancel, close, or query
  broker orders.**
- **Do not use live broker credentials.**
- **Do not use demo/practice order execution.**
- **Do not print credentials.**
- **Do not read `.env`.**
- **Do not fetch new data.**
- **Do not commit `.env` files, SQLite stores, candle CSVs,
  bulky raw outputs, tokens, credentials, cache files, or
  local-only generated data.**
- **Do not use QuantConnect / LEAN.**
- **Do not revive or tune CAMPAIGN_002, CAMPAIGN_010, or any
  other rejected family.**
- **Do not change historical campaign verdicts.**
- **Do not present a trading recommendation.**
- **Do not claim readiness for paper/demo/live.**
- **Be explicit when something is research-only,
  diagnostic-only, estimated-only, or blocked.**
- **Commit after each meaningful phase.**

Plus C5-specific binding rules:

- **The seed sequence is fixed in the pre-commit before any
  unit test runs.** Use `master_seed = 20260523` (or another
  single integer chosen *before* writing the strategy module).
- **The seed input contains only
  `(master_seed, instrument_name, bar_timestamp_iso)`.** Must
  not include any bar-`t` price data — that would be a
  lookahead bug.
- **`random_entry_anchor` cannot be approved.** The strategy is
  a null model by design; do not add it to
  `configs/approved_strategies.yaml` under any circumstance.
- **`random_entry_anchor` cannot enter any active loop.** Even
  if a future review approves the strategy via a deliberate
  human action (which they should not), the diagnostic-anchor
  framing makes paper / demo / live trading inappropriate.

## 3. Pre-existing context the scaffold sprint must read

Before any code, read:

- [`docs/research/NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md)
  (Phase 7 of this discovery sprint — the entry point)
- [`docs/research/NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md)
  (Phase 3 selection)
- [`docs/research/NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
  (Phase 4 detailed design — the binding spec)
- [`docs/research/CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md)
- [`docs/research/REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`docs/research/CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
  (the gate vector CAMPAIGN_011 inherits)
- [`docs/research/ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md)
  (the model scaffold sprint to mirror in structure)
- [`docs/research/STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`docs/research/STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`docs/research/WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`docs/research/FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`src/forex_bot/strategies/session_breakout.py`](../../src/forex_bot/strategies/session_breakout.py)
  (the closest existing strategy in shape — copy structure, not content)
- [`tests/unit/test_session_breakout.py`](../../tests/unit/test_session_breakout.py)
  (the test structure to mirror)
- [`configs/campaign_010_session_breakout.yaml`](../../configs/campaign_010_session_breakout.yaml)
  (the config structure to mirror)
- [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
  (verify `approved: []`)

## 4. Phase plan (8 commits)

### Phase 0 — repo truth audit + sprint plan

Verify:
- git branch / status / recent commits
- baseline tests pass (≥ 735)
- ruff finds only the 11 pre-existing UP042 in untouched files
- archive validator / freeze checker / secret scanner all PASS
- paper-loop / demo-loop refuse; no live-loop
- `configs/approved_strategies.yaml` reads `approved: []`
- CAMPAIGN_002 / CAMPAIGN_010 unchanged

Read the binding context per §3 above.

Commit `docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md`
with the audit results, file inventory, 8-phase plan.

### Phase 1 — implementation spec

Commit `docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`
elaborating
[`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
§§3–8 into a machine-facing rule table (R1–R8), candidate
identity, frozen parameters, no-lookahead invariants, expected
test cases. Mirrors the structure of
[`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md).

### Phase 2 — strategy scaffold

Add code:
- `src/forex_bot/strategies/random_entry_anchor.py` (~150 LOC)
  implementing the `Strategy` protocol with R1–R8.
- Update `src/forex_bot/strategies/__init__.py` to re-export.
- Update `src/forex_bot/config.py` to add
  `RandomEntryAnchorStrategyConfig` and
  `StrategyConfig.random_entry_anchor`.

Run `python -m pytest -q` after the edits to ensure no
regression (still ≥ 735 passes — new tests come in Phase 3).

Commit the code edits.

### Phase 3 — unit tests (≥ 20 cases)

Add `tests/unit/test_random_entry_anchor.py`:
- determinism (≥ 3 cases)
- no-lookahead structural audit (≥ 4 cases)
- distribution + frequency (≥ 3 cases)
- config validation (≥ 4 cases)
- strategy core R1/R2/R5/R7 (≥ 4 cases)
- approval/safety regression (≥ 2 cases)

All cases pass; full repo suite goes from 735 → ≥ 755.

Commit.

### Phase 4 — research config + CAMPAIGN_011 docs

Add `configs/campaign_011_random_entry_anchor.yaml`:
- `strategy.enabled = ["random_entry_anchor"]`
- `app.trading_enabled = false`, `app.allow_order_submission =
  false`, `app.allow_live_trading = false`
- 7-pair H4 universe
- `risk.max_open_positions = 1`
- `app.database_path = ./data/campaign_002.sqlite3`

Commit docs:
- `docs/research/CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` with the
  hypothesis verbatim, implementation files, config files,
  frozen parameters, required local-only evaluation commands,
  required walk-forward / financing / risk artifacts, verbatim
  gate vector inherited from CAMPAIGN_010, explicit no-approval
  statement.
- `docs/research/CAMPAIGN_011_STATUS.md` — candidate-scaffold-only.

### Phase 5 — smoke result

Run non-evidence smokes (no backtest):
- `python -m pytest tests/unit/test_random_entry_anchor.py -q` PASS
- `python -c "from forex_bot.config import load_settings; s =
  load_settings('configs/campaign_011_random_entry_anchor.yaml');
  print(s.strategy.enabled, s.strategy.random_entry_anchor is not None)"` PASS
- `python scripts/run_walk_forward_dry_run.py
  --campaign-name CAMPAIGN_011 --universe-start 2020-01-01
  --universe-end 2026-05-20 --style rolling --parameter-mode
  frozen --train-days 540 --validation-days 180 --test-days 180
  --step-days 180 --output /tmp/campaign_011_smoke/` PASS

Commit `docs/research/CAMPAIGN_011_SMOKE_RESULT.md`.

### Phase 6 — walk-forward + financing + risk readiness docs

Commit (no backtest run — just readiness assessment):
- `docs/research/CAMPAIGN_011_WALK_FORWARD_READINESS.md`
- `docs/research/CAMPAIGN_011_FINANCING_RISK_READINESS.md`

### Phase 7 — sprint summary + EVIDENCE_INDEX update + final validation

Commit:
- `docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md`
- Update `docs/research/EVIDENCE_INDEX.md` with a CAMPAIGN_011
  scaffold sub-section
- (No edit to `EVIDENCE_MANIFEST.json` until the evidence sprint
  produces a verdict; the scaffold sprint is precedent-setting
  here — CAMPAIGN_010's scaffold sprint did not add a manifest
  entry either, matching the convention)
- (No edit to `STRATEGY_STATUS.md` until the evidence sprint
  records a verdict)

Run final validation:
- `python -m pytest -q` (≥ 755)
- `ruff check src tests scripts research` (still 11 pre-existing
  UP042; no new findings)
- `python scripts/validate_research_archive.py` PASS
- `python scripts/check_research_freeze.py` PASS
- `python scripts/scan_artifacts_for_secrets.py` PASS
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml`
  refuses
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml`
  refuses
- `python -m forex_bot.cli --help` no `live-loop`
- `git status --short` clean

Verify:
- `configs/approved_strategies.yaml` reads `approved: []`
- CAMPAIGN_002 / CAMPAIGN_010 unchanged
- `random_entry_anchor` not in any active loop
- no `.env` read, no credential printed, no broker call

## 5. Non-goals (binding)

- **No walk-forward backtest run.** That is the evidence
  sprint's job — see
  [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md).
- **No financing overlay computation.** Same — evidence sprint.
- **No risk-diagnostics generation.** Same — evidence sprint.
- **No verifier extension.** Recommended as a separate
  follow-up sprint, never as a side-effect of this scaffold.
- **No approval action.**
- **No paper/demo/live enablement.**
- **No engine / financing / risk-policy code edits.**
- **No edits to any CAMPAIGN_010 or earlier artifact.**

## 6. Expected files (committed by the scaffold sprint)

| file | purpose |
|---|---|
| `src/forex_bot/strategies/random_entry_anchor.py` | new strategy module |
| `src/forex_bot/strategies/__init__.py` | re-export |
| `src/forex_bot/config.py` | new sub-model + slot |
| `tests/unit/test_random_entry_anchor.py` | ≥ 20 unit cases |
| `configs/campaign_011_random_entry_anchor.yaml` | research candidate config |
| `docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md` | Phase 0 plan |
| `docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md` | Phase 1 spec |
| `docs/research/CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` | Phase 4 pre-commit |
| `docs/research/CAMPAIGN_011_STATUS.md` | Phase 4 status (scaffold-only) |
| `docs/research/CAMPAIGN_011_SMOKE_RESULT.md` | Phase 5 smokes |
| `docs/research/CAMPAIGN_011_WALK_FORWARD_READINESS.md` | Phase 6 readiness |
| `docs/research/CAMPAIGN_011_FINANCING_RISK_READINESS.md` | Phase 6 readiness |
| `docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md` | Phase 7 sprint summary |
| `docs/research/EVIDENCE_INDEX.md` | Phase 7 update — add CAMPAIGN_011 scaffold sub-section |

## 7. Validation commands (run at every phase boundary)

```bash
python -m pytest -q
ruff check src tests scripts research
python scripts/validate_research_archive.py
python scripts/check_research_freeze.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

Plus at Phase 0 and Phase 7:

```bash
python -m forex_bot.cli paper-loop -c configs/paper.yaml
python -m forex_bot.cli demo-loop -c configs/practice.yaml
python -m forex_bot.cli --help
```

## 8. Final report requirements (Phase 7's 30-item structured response)

The scaffold sprint's final response should provide:

1. Branch name.
2. Commit hashes by phase.
3. Files changed by phase.
4. Tests and validation commands run.
5. Latest full test count.
6. Ruff status (pre-existing UP042 in untouched files).
7. Strategy module path + role.
8. StrategyConfig sub-model path + key fields.
9. Number of unit tests added.
10. Config YAML path + safety-flag verification.
11. CAMPAIGN_011 pre-commit checklist path.
12. Frozen parameter summary.
13. R1–R8 rule summary.
14. No-lookahead safeguards.
15. Smoke status (non-evidence).
16. Walk-forward readiness status.
17. Financing readiness status (ESTIMATED only; MODELED refused).
18. Risk-diagnostic readiness status.
19. Confirmation no strategy is approved.
20. Confirmation configs/approved_strategies.yaml remains approved: [].
21. Confirmation CAMPAIGN_002 / CAMPAIGN_010 remain REJECT.
22. Confirmation paper/demo/live remain blocked.
23. Confirmation no broker call.
24. Confirmation no credential read or printed.
25. Confirmation no QuantConnect/LEAN.
26. Research freeze/archive status.
27. Local files created but not committed.
28. Remaining blockers.
29. Recommended next branch
    (`research-random-entry-diagnostic-anchor-walk-forward-001`).
30. Exact files to review first.

## 9. Safety state (unchanged at sprint start and end)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (unchanged) |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | scaffold-only at the close of the scaffold sprint; verdict comes from the future evidence sprint |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| broker / OANDA call | none (no fetch needed; existing symlinked data store is reused) |
| `.env` read | none |
| credentials printed | none |
| engine-PnL change | none |
| `src/forex_bot/financing.py` change | none |
| `MODELED` financing reachable | no |
| pytest baseline at start | 735 |
| pytest baseline at end | ≥ 755 (≥ 20 new tests) |

## 10. Cross-links

- [`NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
- [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md)
  (the next sprint after this scaffold sprint)
- [`ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md)
  (the model scaffold sprint to mirror)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
