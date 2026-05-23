# Random-Entry Diagnostic Anchor — Walk-Forward Evidence Sprint Summary

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-walk-forward-001`
`strategy_evidence: false`

End-of-sprint summary for the **first evidence-grade local
research evaluation** of CAMPAIGN_011 / `random_entry_anchor
0.1.0-c011` — the C5 diagnostic-anchor null model.

> **Verdict: REJECT (null model anchor). No strategy approved.**
> CAMPAIGN_002 / CAMPAIGN_010 remain REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`.
> Paper / demo / live remain blocked. **CAMPAIGN_011 cannot be
> approved by design.** The REJECT verdict is the *expected and
> desired* outcome — it validates the evidence pipeline by
> demonstrating the gates correctly REJECT a known-zero-edge
> strategy with metrics consistent with random expectations.

## 1. What this sprint did

| phase | output | committed |
|---|---|:---:|
| 0 | Repo truth audit + 10-phase sprint plan | ✓ ([`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md)) |
| 1 | Data availability + provenance (gitignored symlink → same store as CAMPAIGN_010; all 7 hashes match verbatim) | ✓ ([`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md)) |
| 2 | Walk-forward plan via `scripts/run_walk_forward_dry_run.py` — 8 folds rolling, frozen, 540/180/180/180 days, universe 2020-01-01 → 2026-05-20 (IDENTICAL to CAMPAIGN_010) | ✓ ([`CAMPAIGN_011_WALK_FORWARD_PLAN.md`](CAMPAIGN_011_WALK_FORWARD_PLAN.md) + `backtests/.../walk_forward/plan.{json,md}`) |
| 3 | Per-fold backtest runner — new `scripts/run_campaign_011.py` (cloned from `scripts/run_campaign_010.py` with strategy class + `FROZEN_PARAMETERS` + `EXPECTED_MASTER_SEED` swapped; belt-and-suspenders master-seed check rejects any tuning); ruff clean, --help works, no regression | ✓ |
| 4 | Per-fold execution — 8 folds × 7 pairs = 56 backtests; 1,177 trades; 5.6 s end-to-end on local machine; frozen-parameter + master-seed (20260523) assertion held | ✓ ([`CAMPAIGN_011_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_011_WALK_FORWARD_EXECUTION.md) + per-pair-per-fold CSV/JSON + `walk_forward/results.{json,md}` + `walk_forward/fold_detail.json`) |
| 5 | Verdict classification against verbatim gates from [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md) §11 (inherited from CAMPAIGN_010 §10) — 4 PnL-direction gates fail, 6 structural / dominance / financing gates pass, `overall_verdict = REJECT` (expected null-model outcome) | ✓ ([`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md)) |
| 6 | Financing overlay via new `scripts/build_campaign_011_financing_overlay.py` — ESTIMATED + conservative-stress (MODELED refused at four layers); 1,080 rollover events; cashflow_home_stress_total = −$24.38; USD_JPY flips +→− (pairs_positive → 2/7) | ✓ ([`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md) + `financing/financing_run.{json,md}` + `financing_summary.json`) |
| 7 | Portfolio-risk diagnostics via new `scripts/build_campaign_011_risk_diagnostics.py` — per-pair ratio max/min = 1.65 (random-uniform, vs CAMPAIGN_010's 12.0); session distribution diffuse across all 4 UTC buckets (no concentration > 50 %); 79 % time-stop exit (matches CAMPAIGN_010 mechanics); 8/8 pipeline sanity checks pass | ✓ ([`CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md) + `risk/diagnostics.{json,md}`) |
| 8 | Independent verifier capability assessment — verifier capability-locked to CAMPAIGN_002; did NOT run for CAMPAIGN_011; not required for null-model REJECT (item 5 of six-evidence ladder is a paper-promotion gate); follow-up `infra-free-local-parity-verifier-random-entry-001` recommended for exact-equivalence corroboration | ✓ ([`CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md)) |
| 9 | Status registries updated; sprint + evidence summaries; final validation | ✓ (this doc + [`CAMPAIGN_011_EVIDENCE_SUMMARY.md`](CAMPAIGN_011_EVIDENCE_SUMMARY.md) + [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md) + [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md) + [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) + [`EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json)) |

## 2. Headline result

`random_entry_anchor 0.1.0-c011` is **rejected** as a null-model
diagnostic anchor (expected outcome):

- Fold pass rate **0 / 8** under strict-pass (gate 100 %).
- Aggregate expectancy R **−0.0024** (gate ≥ 0.05) — within
  0.0024 of zero, the textbook random-walk signature.
- Aggregate profit factor **0.91** (gate ≥ 1.10) — within 0.09
  of one.
- Aggregate return **−0.53 %** over 4 years (essentially zero).
- Pairs positive **3 / 7** (close to uniform-noise expectation
  of ~3.5; gate ≥ 4 / 7).
- USD_JPY expectancy = **+0.0000** to 4 decimal places (literal
  random-walk signature).
- Under ESTIMATED + conservative-stress financing, USD_JPY
  flips +→−, deepening the REJECT.
- No parameter tuned. No gate relaxed. No seed optimized.
  `master_seed = 20260523` was the only seed used.

The candidate's "failure" is **structural and expected** — a
random null model cannot produce ≥ 0.05 R expectancy or ≥ 1.10
profit factor by construction. The pipeline correctly observed
this.

## 3. Why this REJECT validates the pipeline

| pipeline-validation claim | evidence |
|---|---|
| The gates correctly REJECT a known-zero-edge strategy | 4 / 8 PnL-direction gates fail; no false positive |
| Metrics are statistically consistent with random expectations | expectancy ≈ 0, profit factor ≈ 1, return ≈ 0, pairs_positive ≈ uniform, USD_JPY expectancy literally 0.0000 |
| Per-pair sampling is uniform (random's signature) | trade-count ratio max/min = 1.65 (vs CAMPAIGN_010's 12.0) |
| Session-of-day distribution has no concentration | max session bucket 37.6 % (vs CAMPAIGN_010's 100 % London) |
| Long-short coin flip is statistically fair | 610 long / 567 short (binomial 95 % CI is ±35; observed diff is 43, within bounds) |
| Exit-mechanic share matches CAMPAIGN_010 | 79 % time-stop (vs 76 %); confirms exit cost model is consistent across both campaigns |
| Financing overlay has consistent per-trade cost | −$0.023/event (CAMPAIGN_010 was −$0.022/event); cost model is calibrated |
| RiskEngine rejection codes fire correctly | SPREAD_TOO_WIDE + SESSION_BLOCKED both observed |
| No anomalous over-performance | INVESTIGATE_PIPELINE branch not triggered |

All 9 pipeline-validation claims hold. **The CAMPAIGN_011
REJECT is the *expected and desired* outcome of a diagnostic
anchor.**

## 4. The falsifiability floor (what future candidates must beat)

Future C2 / C3 / C4 / new-family candidates must beat
CAMPAIGN_011's per-fold + aggregate metrics by a meaningful
margin to count as evidence of an edge:

| metric | random anchor (CAMPAIGN_011) | future real candidate must beat |
|---|---|---|
| aggregate expectancy R | −0.0024 R | by ≥ +0.05 R |
| aggregate profit factor | 0.91 | by ≥ 0.19 (to reach 1.10) |
| aggregate return % over 4 years | −0.53 % | meaningfully positive |
| pairs_positive | 3 / 7 | ≥ 4 / 7 |
| fold pass rate | 0 / 8 | 100 % (strict-pass) |
| per-pair worst expectancy R | −0.0737 (NZD_USD) | ≥ 0 across at least 4 pairs |

A candidate whose metrics resemble CAMPAIGN_011's has
demonstrated no edge.

## 5. Code added by this sprint (kept minimal)

| file | purpose | size |
|---|---|---|
| `scripts/run_campaign_011.py` | per-fold backtest runner mirroring `run_campaign_010.py`'s pattern, with `RandomEntryAnchorStrategy` import, `FROZEN_PARAMETERS` from CAMPAIGN_011 pre-commit, `EXPECTED_MASTER_SEED` belt-and-suspenders check, UNEXPECTED-PASS warning emission | ~470 LOC |
| `scripts/build_campaign_011_financing_overlay.py` | clone of CAMPAIGN_010's financing-overlay script with paths updated | ~200 LOC |
| `scripts/build_campaign_011_risk_diagnostics.py` | clone of CAMPAIGN_010's risk-diagnostics script with paths + campaign id updated | ~250 LOC |
| `backtests/CAMPAIGN_011_random_entry_anchor/` | committed campaign artifacts: walk_forward (plan + results + fold_detail), folds (per-pair-per-fold summary + trades), financing (run + summary), risk (diagnostics) | ~3 MB total |

No `src/forex_bot/` change. No engine edit. No financing-module
edit. No risk-policy edit. No CAMPAIGN_002 / CAMPAIGN_010 touch.

## 6. Baseline validation

All commands pass at the end of every phase and at the sprint's
tip commit:

| check | result |
|---|---|
| `python -m pytest -q` | **771 passed** (unchanged from prior sprint baseline; this sprint adds no new test files) |
| `ruff check src tests scripts research` | **11 pre-existing UP042 findings** in untouched files (matches the documented baseline). Not refactored — would change `str(EnumValue)` runtime semantics outside this sprint's scope. |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED |
| `python -m forex_bot.cli paper-loop -c configs/paper.yaml` | refused (registry empty) |
| `python -m forex_bot.cli demo-loop -c configs/practice.yaml` | refused (registry empty) |
| `python -m forex_bot.cli --help` | no `live-loop` command present |
| `git status --short` | clean at every commit boundary |

## 7. Safety state (unchanged across all 10 phases)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT** and is untouched.
- **CAMPAIGN_010 remains REJECT** and is untouched.
- **CAMPAIGN_011** verdict = REJECT (null model anchor; cannot
  be approved).
- **Paper / demo / live remain blocked.**
- **No broker call** at any phase.
- **No `.env` read; no credential printed; no account / order /
  trade / position / transaction endpoint queried.**
- **No QuantConnect / LEAN.**
- **No engine-PnL change.** **No `src/forex_bot/financing.py`
  edit.**
- **No new external dependency.**
- **`MODELED` financing remains refused** at four layers.
- **No parameter tuning. No seed optimization.** Only the
  pre-committed `master_seed = 20260523` was used.
- **Bulky data uncommitted.** The H4 SQLite store lives only as
  a gitignored symlink (created in a prior sprint); no
  `.sqlite3`, no `.env`, no raw candle CSV was committed.

## 8. Remaining blockers (none for this candidate)

- This candidate is REJECTED — no further work is recommended
  for `random_entry_anchor 0.1.0-c011`. The candidate is a null
  model anchor by design; re-running with a different seed
  would constitute a new candidate.
- Independent verifier extension for `random_entry_anchor` is
  **optional follow-up** — not blocking the REJECT verdict
  (which stands on items 1–3 of the six-evidence ladder).

## 9. Recommended next sprints

- **`research-new-candidate-strategy-discovery-003`** —
  the next *real* candidate-discovery sprint, picking C3
  (regime switcher), C2 (carry overlay — blocked on MODELED),
  or C4 (vol-expansion straddle — blocked on engine work).
  Recommended ordering per
  [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md):
  C3 → C2 → C4. With CAMPAIGN_011's falsifiability floor
  now established, any future candidate's metrics can be
  measured against an exact baseline.
- (Optional) **`infra-free-local-parity-verifier-random-entry-001`** —
  extend the verifier with a `random_entry_anchor` rule path;
  unique value here is **exact-equivalence** corroboration
  (same `(master_seed, pair, ts)` → same SHA-256 → bit-identical
  trades). Reusable template for future families.
- (Eventual) **`infra-ruff-up042-stress-enum-001`** — small
  cleanup sprint for the 11 pre-existing UP042 findings.

## 10. Cross-links

- [`CAMPAIGN_011_EVIDENCE_SUMMARY.md`](CAMPAIGN_011_EVIDENCE_SUMMARY.md)
- [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
- [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md)
- [`CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md)
- [`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md)
- [`CAMPAIGN_011_WALK_FORWARD_PLAN.md`](CAMPAIGN_011_WALK_FORWARD_PLAN.md)
- [`CAMPAIGN_011_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_011_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md)
  (the scaffold sprint that preceded this evidence sprint)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
