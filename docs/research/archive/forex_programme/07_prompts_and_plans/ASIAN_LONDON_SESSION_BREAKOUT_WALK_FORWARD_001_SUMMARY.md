# Asian-London Session Breakout — Walk-Forward Evidence Sprint Summary

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-walk-forward-001`
`strategy_evidence: false`

End-of-sprint summary for the **first evidence-grade local
research evaluation** of CAMPAIGN_010 / `session_breakout
0.1.0-c010`.

> **Verdict: REJECT. No strategy approved.** CAMPAIGN_002 remains
> REJECT. `configs/approved_strategies.yaml` remains `approved: []`.
> Paper / demo / live remain blocked. Even with the rejection
> behind us, no item in the registry changes and no loop unblocks.

## 1. What this sprint did

| phase | output | committed |
|---|---|:---:|
| 0 | Repo truth audit + 8-phase sprint plan | ✓ ([`ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_PLAN.md)) |
| 1 | Data availability + provenance (existing 7-pair × 6-year H4 OANDA practice store reused via gitignored symlink; per-pair counts + provenance hashes verified) | ✓ ([`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md)) |
| 2 | Walk-forward plan via `scripts/run_walk_forward_dry_run.py` — 8 folds rolling, frozen, 540/180/180/180 days, universe 2020-01-01 → 2026-05-20 | ✓ ([`CAMPAIGN_010_WALK_FORWARD_PLAN.md`](CAMPAIGN_010_WALK_FORWARD_PLAN.md) + `backtests/.../walk_forward/plan.{json,md}`) |
| 3 | Per-fold backtest execution via the new `scripts/run_campaign_010.py` — 8 folds × 7 pairs = 56 runs; 2,791 trades; 7.9 s end-to-end on a local machine; frozen-parameter assertion in the runner blocks any drift before any backtest fires | ✓ ([`CAMPAIGN_010_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_010_WALK_FORWARD_EXECUTION.md) + per-pair-per-fold CSV/JSON under `folds/` + `walk_forward/results.{json,md}` + `walk_forward/fold_detail.json`) |
| 4 | Verdict classification against verbatim gates from [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md) §10 — 5 fail, 4 pass, `overall_verdict = REJECT` | ✓ ([`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)) |
| 5 | Financing overlay via `scripts/build_campaign_010_financing_overlay.py` — ESTIMATED + conservative-stress (MODELED refused at four layers); 2,483 rollover events; cashflow_home_stress_total = −$55.69; strictly worsens REJECT | ✓ ([`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md) + `financing/financing_run.{json,md}` + `financing/financing_summary.json`) |
| 6 | Portfolio-risk diagnostics via `scripts/build_campaign_010_risk_diagnostics.py` — concurrency structurally bounded, per-pair exposure under risk cap, entry-session clustering as designed (100 % London-window), 75.5 % time-stop exit dominance, RiskEngine rejected 29.8 % of raw signals as cost-unsafe | ✓ ([`CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md) + `risk/diagnostics.{json,md}`) |
| 7 | Independent verifier capability assessment — `research/parity_verifier/` is capability-locked to CAMPAIGN_002 trend_following; verifier did NOT run for CAMPAIGN_010 (extension out of scope for a rejected candidate) | ✓ ([`CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md)) |
| 8 | Status registries (CAMPAIGN_010_STATUS → rejected; STRATEGY_STATUS row reclassified; EVIDENCE_INDEX entry added) + sprint + evidence summary + final validation | ✓ (this doc, [`CAMPAIGN_010_EVIDENCE_SUMMARY.md`](CAMPAIGN_010_EVIDENCE_SUMMARY.md), [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md), [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md), [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)) |

## 2. Headline result

`session_breakout 0.1.0-c010` is **rejected**:

- Fold pass rate **0 / 8** under strict-pass (gate 100 %).
- Aggregate expectancy R **−0.0408** (gate ≥ 0.05).
- Aggregate profit factor **0.04** (gate ≥ 1.10).
- Pairs positive **1 / 7** (USD_CHF; gate ≥ 4 / 7).
- Under ESTIMATED + conservative-stress financing, USD_CHF flips
  to net negative (pairs positive → 0 / 7); the strict-pass
  rejection deepens.
- No parameter was tuned; no gate was relaxed. Frozen-parameter
  assertion in the runner aborts before any backtest if a single
  YAML value drifts from
  [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
  §5.

The candidate's failure is **directional**, not the result of
unsafe risk posture, lookahead bug, sample-size thinness, or
data quality issue — the diagnostic phases (5, 6) confirm this.

## 3. Why this REJECT is decisive

| dimension | observation |
|---|---|
| sample size | 2,791 trades over 8 folds × 4 years out-of-sample — well above the 200 / fold and 30 / fold gates |
| risk posture | every trade loss bounded by the ATR stop (~$1.30 worst); max concurrent positions = 1; spread filter rejected 29.8 % of raw signals; no risk-cap activation forced an exit |
| no-lookahead | structurally enforced (`generate_signal` reads only `close[t]` and `[-2]` indices; AST-level unit test rails) |
| financing | strictly worsens REJECT under conservative stress; USD_CHF (the only marginally positive pair) flips to net negative |
| candidate distinctness | session_breakout is a genuinely different family from CAMPAIGN_002/003/004/007/008/009 — its REJECT is a new piece of evidence in a different region of strategy space |
| classification | **REJECT** — not BLOCKED (pipeline ran cleanly), not INCONCLUSIVE (sample is rich), not RESEARCH_PASS_UNAPPROVED (gates fail by wide margins) |

## 4. Code added by this sprint (kept minimal)

| file | purpose | size |
|---|---|---|
| `scripts/run_campaign_010.py` | per-fold backtest runner mirroring `run_campaign_009.py`'s pattern, with walk-forward plan consumption + frozen-parameter enforcement + WalkForwardResults emission via `research.walk_forward.render_results_md` | ~500 LOC |
| `scripts/build_campaign_010_financing_overlay.py` | reads per-fold trade CSVs → `PositionInterval` → `research.financing.calculate_run(default_stress_rate_source())` → JSON + MD + extended per-pair / per-side / per-fold breakdown | ~200 LOC |
| `scripts/build_campaign_010_risk_diagnostics.py` | reads per-fold trade CSVs + fold_detail.json → risk-posture, exposure, streaks, session clustering, exit-reason distribution, RiskEngine rejection totals | ~250 LOC |
| `backtests/CAMPAIGN_010_session_breakout/` | committed campaign artifacts: walk_forward (plan + results + fold_detail), folds (per-pair-per-fold summary + trades), financing (run + summary), risk (diagnostics) | ~4 MB total |

No `src/forex_bot/` change. No engine edit. No financing-module
edit. No risk-policy edit. No CAMPAIGN_002 touch.

## 5. Baseline validation

All commands pass at the end of every phase and at the sprint's
tip commit:

| check | result |
|---|---|
| `python -m pytest -q` | **735 passed** (unchanged from prior sprint baseline; this sprint adds no new test files) |
| `ruff check src tests scripts research` | **11 pre-existing UP042 findings** in untouched files (`research/parity_verifier/models.py`, `research/walk_forward/models.py`, `research/financing/models.py`, `research/lean_parity/algorithms/...`). Identical to the prior sprint's documented baseline. Not refactored — would change `str(EnumValue)` runtime semantics outside this sprint's scope; recommended cleanup sprint: `infra-ruff-up042-stress-enum-001`. |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED (evidence-index links resolve, no credential strings, all manifests consistent) |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED (registry empty, loops refuse, archive valid) |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED (no credential value or shape; pattern scan over 2,000+ files) |
| `python -m forex_bot.cli paper-loop -c configs/paper.yaml` | refused (registry empty) |
| `python -m forex_bot.cli demo-loop -c configs/practice.yaml` | refused (registry empty) |
| `python -m forex_bot.cli --help` | no `live-loop` command present |
| `git status --short` | clean at every commit boundary |

## 6. Safety state (unchanged across all 8 phases)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT** and is untouched.
- **CAMPAIGN_010** reclassified `candidate-scaffold → rejected`.
- **Paper / demo / live remain blocked.**
- **No broker call** at any phase.
- **No `.env` read; no credential printed; no account / order /
  trade / position / transaction endpoint queried.**
- **No QuantConnect / LEAN.**
- **No engine-PnL change.** **No `src/forex_bot/financing.py`
  edit.**
- **No new external dependency.**
- **`MODELED` financing remains refused** at four layers.
- **Bulky data uncommitted.** The H4 SQLite store lives only as a
  gitignored symlink to the main checkout (verified by
  `git check-ignore -v`); no `.sqlite3`, no `.env`, no raw
  candle CSV was committed.

## 7. Remaining blockers (none for this candidate)

- This candidate is REJECTED — no further work is recommended for
  `session_breakout 0.1.0-c010`. Re-attempting the family by
  tweaking parameters would be a curve-fitting anti-pattern per
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
  §12.
- Independent verifier extension for `session_breakout` is **not
  recommended** — investment in a dead candidate is wasted.

## 8. Recommended next sprints

- **`research-new-candidate-strategy-discovery-002`** —
  the next *candidate-discovery* sprint, picking C2–C5 from
  [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
  on merit (not on CAMPAIGN_010's negative result). The chosen
  candidate would then need its own scaffold sprint + walk-forward
  evidence sprint mirroring this one.
- **`infra-ruff-up042-stress-enum-001`** — small cleanup sprint
  for the 11 pre-existing UP042 findings in untouched files,
  carried forward from the prior sprint.
- **`infra-free-local-parity-verifier-<NEXT-CANDIDATE>-005`** —
  conditional on a future PASS candidate, extend the
  free / local verifier to the new family's rule set so item 5 of
  the six-evidence ladder can be satisfied before approval review.

## 9. Cross-links

- [`CAMPAIGN_010_EVIDENCE_SUMMARY.md`](CAMPAIGN_010_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md)
- [`CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md)
- [`CAMPAIGN_010_DATA_PROVENANCE.md`](CAMPAIGN_010_DATA_PROVENANCE.md)
- [`CAMPAIGN_010_WALK_FORWARD_PLAN.md`](CAMPAIGN_010_WALK_FORWARD_PLAN.md)
- [`CAMPAIGN_010_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_010_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_SUMMARY.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
