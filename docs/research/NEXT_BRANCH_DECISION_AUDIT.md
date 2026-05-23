# Next-Branch Decision Audit

**Date:** 2026-05-23 · **Worktree branch:** `claude/affectionate-fermi-d950fc`
**Base commit:** `d741ee7` (`Merge financing model + reconciliation tooling +
observed-capture pilot + bp/day fixture expansion sprints`)
**Sprint label:** `research-new-candidate-strategy-discovery-001`
`strategy_evidence: false`

Phase 0 truth audit. Records the committed state of the repo, the
five financing sprints' completion status, the walk-forward harness
status, the safety gates, and the chosen next branch. Nothing in
this audit fetched broker data, ran a strategy, or changed any
verdict. **No strategy approved. CAMPAIGN_002 remains REJECT.
Paper / demo / live remain blocked.**

## 1. Worktree state

| field | value |
|---|---|
| working directory | `/Users/kashane/dev/forex-bot/.claude/worktrees/affectionate-fermi-d950fc` |
| git branch | `claude/affectionate-fermi-d950fc` |
| base commit | `d741ee7ad55b1b7f50299c72a7c3c726bf3f89d9` |
| base commit message | "Merge financing model + reconciliation tooling + observed-capture pilot + bp/day fixture expansion sprints" |
| `git status` before this commit | clean |
| project venv | `/Users/kashane/dev/forex-bot/.venv/bin/python` |

## 2. Files inspected

### Status / summary docs

- [`docs/research/EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) — 9 campaigns, all
  REJECT / diagnostic; lists walk-forward harness + all 5 financing
  sprints; links resolve.
- [`docs/research/EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json) — 9
  campaign entries, all `strategy_approved: false`; 14 diagnostic
  artifacts; validator PASS.
- [`docs/research/WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
  — harness implemented, 42 tests pass, repo total reported 523.
- [`docs/research/RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md`](RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md)
  — sprint complete; recommended next branch `research-financing-model-001`.
- [`docs/research/WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
  — protocol for future strategy campaigns.
- [`docs/research/NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  — six-evidence menu for any future candidate.
- [`docs/research/FINANCING_MODEL_001_SUMMARY.md`](FINANCING_MODEL_001_SUMMARY.md)
  — calculator sprint complete (71 tests).
- [`docs/research/FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
  — headline status: ESTIMATED-only, MODELED refused, repo total 594
  at time of doc.
- [`docs/research/FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md`](FINANCING_RATE_SOURCE_FIXTURES_001_SUMMARY.md)
  — fixtures + loader sprint complete (43 tests).
- [`docs/research/FINANCING_RATE_SOURCE_FIXTURES_STATUS.md`](FINANCING_RATE_SOURCE_FIXTURES_STATUS.md)
  — 9 fixtures, loader, pilot spec; repo total 637.
- [`docs/research/FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md`](FINANCING_RECONCILIATION_TOOLING_001_SUMMARY.md)
  — CLI sprint complete (22 tests).
- [`docs/research/FINANCING_RECONCILIATION_TOOLING_STATUS.md`](FINANCING_RECONCILIATION_TOOLING_STATUS.md)
  — `scripts/reconcile_financing_fixtures.py` shipped; repo total 659.
- [`docs/research/FINANCING_OBSERVED_CAPTURE_PILOT_001_SUMMARY.md`](FINANCING_OBSERVED_CAPTURE_PILOT_001_SUMMARY.md)
  — capture-pilot sprint complete (27 tests).
- [`docs/research/FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`](FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md)
  — script shipped; dry-run exit 2 (no creds), no broker call,
  no MODELED; repo total 686.
- [`docs/research/FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md)
  — 7 rate fixtures (one per H4 universe pair) + 1 observed
  companion; 16 tests; **repo total 702.**
- [`docs/research/FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
  — NO APPROVED TRADING STRATEGY.
- [`docs/research/STRATEGY_STATUS.md`](STRATEGY_STATUS.md) — all
  paper/demo/live = NO.
- [`docs/research/FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md)
  — unauthorized menu.

### Code directories

- `research/walk_forward/` — harness package (models, splits, validate,
  reporting) — present.
- `research/financing/` — calculator package (models, rates, calculator,
  reporting, fixtures, README) — present.
- `research/financing/fixtures/` — synthetic JSON fixtures (events +
  per-pair rates) — present.
- `scripts/reconcile_financing_fixtures.py` — present.
- `scripts/capture_oanda_observed_financing_pilot.py` — present.
- `scripts/run_walk_forward_dry_run.py` — present.
- `src/forex_bot/strategies/` — existing strategy families: `base.py`,
  `indicators.py`, `mean_reversion.py`, `pullback_continuation.py`,
  `trend_following.py`, `volatility_breakout.py` — present. No new
  strategy added this sprint; none authorized to add.

### Configs

- [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
  — `approved: []` (verified verbatim; freeze-checker confirms).

## 3. Sprint completion matrix

| sprint | status | tests added | repo total at sprint close |
|---|---|---:|---:|
| research-walk-forward-harness-001 | **complete** | 42 | 523 |
| research-financing-model-001 | **complete** | 71 | 594 |
| research-financing-rate-source-fixtures-001 | **complete** | 43 | 637 |
| research-financing-reconciliation-tooling-001 | **complete** | 22 | 659 |
| research-financing-observed-capture-pilot-001 | **complete** (no real run; creds absent) | 27 | 686 |
| research-financing-bp-day-fixture-expansion-001 | **complete** | 16 | 702 |

**Walk-forward harness:** complete. The harness emits and validates
fold plans; future strategy campaigns must use it. The harness itself
does not run a strategy.

**Financing (model / fixtures / reconciliation / capture / bp-day
expansion):** complete. Financing remains `ESTIMATED` everywhere in
`research/financing/`. `MODELED` is refused at four pipeline layers
(`TableRateSource` ctor, `calculate_run`, `_build_report` in the
reconciliation CLI, capture-script never declares a treatment). The
existing approval gate `financing_treatment_blocks_approval` in
[`src/forex_bot/financing.py`](../../src/forex_bot/financing.py) is
unchanged and remains the authoritative live blocker.

**Observed-financing capture:** pipeline implemented; no real broker
data captured (practice credentials absent in this worktree). Any
future credentialed-run sprint is a separate human-authorized step.

## 4. Latest reported test count

**702 tests pass** (full repo suite, this worktree).
Recomputed in Phase 0: `702 passed in 3.08s`.

## 5. Safety state

| check | result |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| CAMPAIGN_002 verdict | **REJECT** (unchanged) |
| any strategy approved | **no** |
| paper-loop refuses | ✓ (`trend_following` not approved) |
| demo-loop refuses | ✓ (`trend_following` not approved) |
| `live-loop` command exists | **no** (CLI commands: `doctor`, `sync-instruments`, `fetch-candles`, `backtest`, `audit-data`, `paper-loop`, `demo-loop`, `reconcile`, `report`) |
| QuantConnect / LEAN | **retired** (decision 2026-05-22) |
| broker / OANDA call this sprint | **no** |
| `.env` read this sprint | **no** |
| credentials printed this sprint | **no** |
| engine PnL changed this sprint | **no** |
| `src/forex_bot/financing.py` changed this sprint | **no** |
| new external dependency this sprint | **no** |
| MODELED financing reachable | **no** (four refusal layers) |
| live promotion financing blocker | **stands** |

## 6. Validation commands run in Phase 0

```bash
.venv/bin/python scripts/validate_research_archive.py
.venv/bin/python scripts/check_research_freeze.py
.venv/bin/python scripts/scan_artifacts_for_secrets.py
.venv/bin/python -m forex_bot.cli paper-loop -c configs/paper.yaml
.venv/bin/python -m forex_bot.cli demo-loop -c configs/practice.yaml
.venv/bin/python -m forex_bot.cli --help
.venv/bin/python -m pytest -q
```

| command | result |
|---|---|
| `validate_research_archive.py` | **PASS** (9 campaigns, 14 diagnostic artifacts, 127 evidence-index links, 1988 artifact files) |
| `check_research_freeze.py` | **PASS** (loops refuse `['trend_following']`; registry empty) |
| `scan_artifacts_for_secrets.py` | **PASS** (value scan skipped — no `.env` to source; pattern scan over 2046 files clean) |
| `paper-loop -c configs/paper.yaml` | **refused** (expected) |
| `demo-loop -c configs/practice.yaml` | **refused** (expected) |
| `forex_bot.cli --help` | **OK** (no `live-loop`; 9 commands above) |
| `pytest -q` | **702 passed** in 3.08s |

## 7. Branch decision

**Decision rule (from the prompt):**

> If financing model, fixtures, reconciliation, and observed-capture
> pilot are all already completed or blocked, choose
> `research-new-candidate-strategy-discovery-001`.

All four financing sub-sprints **and** the bp/day fixture expansion
follow-up are complete. The walk-forward harness is complete. The
research freeze stands, the live blocker stands, and no strategy is
approved.

**Chosen sprint:** `research-new-candidate-strategy-discovery-001`
(PATH B).

### 7.1 Why not deployment / shadow / demo work

- Paper / demo / live remain blocked by the empty
  `approved_strategies.yaml` registry. No strategy has earned even
  PAPER-TRADE-ONLY status.
- Promotion requires a future candidate to pass the six-evidence
  menu in
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §8 (walk-forward PASS, financing overlay, real-data parity, etc.),
  **none of which currently has a candidate**.
- Until a meaningfully-distinct new candidate is *designed* (this
  sprint) and then *evidenced* (future sprints), deployment-track
  work has nothing to deploy.
- Reviving CAMPAIGN_002 is explicitly forbidden by the standing
  safety rules.

### 7.2 Why not more financing / observed-capture work

- All five financing sprints are committed and tested.
- The remaining financing gaps (real captured `DAILY_FINANCING`
  events; a `MODELED` source; engine-PnL integration) need either
  (a) a separately-authorized credentialed practice run or
  (b) human approval to wire MODELED. Both are outside this
  worktree's authorization envelope and outside the prompt's PATH A
  scope.
- The protocol explicitly recommends the discovery direction once
  financing is implemented "ESTIMATED/STRESS-only with MODELED
  refused".

## 8. Sprint scope — exact next phases

Per the prompt's PATH B, the new branch will execute these phases.
Each commits its own artifact before the next begins. Phases that
turn out to be blocked will be documented honestly.

| phase | deliverable | code? |
|---|---|---|
| B1 | `NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md` + `NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md` | docs only |
| B2 | `STRATEGY_FRAMEWORK_INVENTORY.md` | docs only |
| B3 | `CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md` (3–5 candidate families, distinct from CAMPAIGN_002; preferred candidate selected) | docs only |
| B4 | `PREFERRED_CANDIDATE_EVALUATION_DESIGN.md` (frozen-parameter walk-forward plan, financing overlay gate, risk diagnostics; **not yet run**) | docs only |
| B5 | optional safe helper scaffolding (docs-only candidate-proposal schema if useful) — strictly **no** strategy code | docs (+ small validator code only if safe) |
| B6 | `NEW_CANDIDATE_STRATEGY_DISCOVERY_001_SUMMARY.md` + `EVIDENCE_INDEX.md`/`EVIDENCE_MANIFEST.json` updates if appropriate + final validation | docs + validation |

### 8.1 Non-goals (locked in by the prompt and protocol)

- No strategy approved.
- No CAMPAIGN_002 tuning or revival.
- No paper / demo / live changes.
- No broker / OANDA calls.
- No `.env` read; no credential printing.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No strategy code wired into execution.
- No parameter search.
- No new external dependency unless trivially safe and clearly
  justified.

## 9. Local files created but not committed

None (Phase 0 has only produced this audit doc, which is committed
in this same phase).

## 10. Recommended next branch

**`research-new-candidate-strategy-discovery-001`** (PATH B).

## 11. Cross-links

- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
- [`EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md)
- [`FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`](FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md)
- [`FINANCING_RECONCILIATION_TOOLING_STATUS.md`](FINANCING_RECONCILIATION_TOOLING_STATUS.md)
- [`FINANCING_RATE_SOURCE_FIXTURES_STATUS.md`](FINANCING_RATE_SOURCE_FIXTURES_STATUS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md)
- [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
