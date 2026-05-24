# Next Candidate Evidence Branch Spec (Phase 7b)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-004`
`strategy_evidence: false`

Phase 7b binding spec for the **future evidence sprint** that runs
the walk-forward + financing overlay + risk diagnostics + verifier
assessment for `cross_pair_currency_strength_rotation 0.1.0-c013`
(CAMPAIGN_013). This doc is a binding *prompt template* for the
Claude Code instance that follows the scaffold sprint.

> No strategy approved. `configs/approved_strategies.yaml` remains
> `approved: []`. **Even a clean PASS produces
> `RESEARCH_PASS_UNAPPROVED`.**

## 1. Future branch identity

| field | value |
|---|---|
| **branch name** | **`research-cross-pair-currency-strength-rotation-walk-forward-001`** |
| base commit | (latest of `research-cross-pair-currency-strength-rotation-001`) |
| type | evidence sprint (runs walk-forward + financing + risk + verifier-assessment) |
| binding design | [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md) |
| sibling reference | `research-random-entry-diagnostic-anchor-walk-forward-001` (CAMPAIGN_011 evidence) + `research-regime-switcher-atr-percentile-walk-forward-001` (CAMPAIGN_012 evidence) |
| **approval allowed?** | **NO** — even a clean PASS produces `RESEARCH_PASS_UNAPPROVED` |

## 2. Phase outline (10 phases; mirrors CAMPAIGN_012 evidence sprint)

| phase | output | scope |
|---|---|---|
| 0 | `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md` | repo truth audit + 10-phase plan |
| 1 | `docs/research/CAMPAIGN_013_DATA_PROVENANCE.md` | data hashes (must match CAMPAIGN_010 / 011 / 012 verbatim) |
| 2 | `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/plan.{json,md}` + `docs/research/CAMPAIGN_013_WALK_FORWARD_PLAN.md` | 8-fold rolling/frozen plan |
| 3 | `scripts/run_campaign_013.py` | per-fold runner (mirrors `run_campaign_012.py`); **MUST include the multi-pair orchestration**: read all 7 pairs' completed H4 closes, align to common timestamps, inject as `cross_pair_closes` into `ctx.config` for each pair's strategy invocation |
| 4 | 56× per-fold per-pair `summary.json` + `trades.csv` + `walk_forward/results.{json,md}` + `walk_forward/fold_detail.json` + `docs/research/CAMPAIGN_013_WALK_FORWARD_EXECUTION.md` | execute 8 folds × 7 pairs = 56 backtests |
| 5 | `docs/research/CAMPAIGN_013_WALK_FORWARD_RESULT.md` | formal verdict (REJECT / REJECT_INDISTINGUISHABLE_FROM_NULL / RESEARCH_PASS_UNAPPROVED / BLOCKED); inherited gates + null-baseline comparison |
| 6 | `scripts/build_campaign_013_financing_overlay.py` + `backtests/.../financing/*` + `docs/research/CAMPAIGN_013_FINANCING_OVERLAY.md` | ESTIMATED + conservative stress; MODELED refused |
| 7 | `scripts/build_campaign_013_risk_diagnostics.py` + `backtests/.../risk/*` + `docs/research/CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md` | rank-gap clustering + cross-pair concurrent-rejection rate (a CAMPAIGN_013-specific diagnostic) |
| 8 | `docs/research/CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md` | verifier capability lock (CAMPAIGN_002 only); deferred unless `RESEARCH_PASS_UNAPPROVED` |
| 9 | `docs/research/CAMPAIGN_013_EVIDENCE_SUMMARY.md` + `docs/research/CAMPAIGN_013_STATUS.md` (UPDATE) + `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md` + EDIT `docs/research/EVIDENCE_INDEX.md` + EDIT `docs/research/EVIDENCE_MANIFEST.json` + EDIT `docs/research/STRATEGY_STATUS.md` + EDIT `tests/unit/test_validate_research_archive.py` (12 → 13 campaigns) | finalize |

## 3. Critical CAMPAIGN_013-specific runner requirement (binding)

**The Phase 3 runner is structurally different from CAMPAIGN_010 /
011 / 012 runners** because the strategy requires sibling-pair close
series at each invocation. Specifically:

```python
# Per-fold loop in run_campaign_013.py — high-level shape:
for fold in plan.folds:
    # Load ALL 7 pairs' completed H4 candles for the test window
    # PLUS warm-up margin (250 calendar days back, like CAMPAIGN_012):
    pair_frames: dict[str, CandleFrame] = {
        pair: load_pair_frame(pair, fold, candle_repo) for pair in pairs
    }
    # Align all 7 pairs to a common H4 timestamp index (intersection):
    common_index = _common_h4_index(pair_frames)
    # For each pair, build a closes-only series indexed by common_index:
    cross_pair_closes_all: dict[str, pd.Series] = {
        pair: pair_frames[pair].df.loc[common_index, "close"]
        for pair in pairs
    }
    # For each pair, run the engine with cross_pair_closes injected
    # into strategy_config:
    for pair in pairs:
        strategy_cfg = dict(frozen_strategy_cfg)
        strategy_cfg["cross_pair_closes"] = cross_pair_closes_all
        engine = BacktestEngine(
            instrument=meta[pair],
            strategy=CrossPairCurrencyStrengthRotationStrategy(...),
            strategy_config=strategy_cfg,
            # ...same as CAMPAIGN_012 runner...
        )
        engine.run(pair_frames[pair], data_request_hash=...)
```

**Binding invariants:**

1. The `cross_pair_closes` dict in `ctx.config` must contain
   **completed-only** close series (per the `completed_only().df`
   filter applied during loading).
2. The common index across pairs is the **intersection** of completed
   H4 timestamps — pairs with missing bars at a given timestamp are
   absent from the index for that timestamp.
3. The runner aligns all pairs **before** invoking any pair's
   strategy; this prevents a per-pair signal from racing on a
   not-yet-loaded sibling pair.
4. The runner does **NOT** mutate the strategy module to access
   sibling pairs directly; the integration contract is one-way
   (runner → strategy via `ctx.config`).

If the Phase 3 runner cannot satisfy these invariants (e.g. because
the bespoke engine's per-pair loop pattern doesn't naturally allow
the orchestration), the evidence sprint must document the blocker
and classify the verdict as `BLOCKED`.

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

Test-count target: **848 baseline → maintained or grown** (the Phase 9
EVIDENCE_MANIFEST.json update will bump
`test_validate_research_archive` from 12 to 13 campaigns).

## 5. Safety rules (binding)

- **NO broker / OANDA / account / order / trade / position /
  transaction endpoint queries.** The runner reads only the local
  SQLite store via `forex_bot.data.db.Database`.
- **NO `.env` read; no credential print.**
- **NO new data fetch.** Local store has full coverage.
- **NO `live-loop` command creation.**
- **NO `configs/approved_strategies.yaml` mutation.**
- **NO enabling** `cross_pair_currency_strength_rotation` in
  `configs/paper.yaml` / `configs/practice.yaml`.
- **NO QuantConnect / LEAN.**
- **NO parameter tuning.** The runner's `_assert_frozen()` must
  re-verify all 9 frozen parameters before any backtest fires.
- **NO modifying any rejected-family strategy module** or any
  CAMPAIGN_002 / 010 / 011 / 012 verdict / status / manifest /
  STRATEGY_STATUS row.
- **NO `max_open_positions` increase** to "rescue" trade count if
  the cross-pair concurrent-rejection rate depresses it (this is
  documented as a known behavior of C6, not a bug).

## 6. Non-goals (binding)

- No verifier extension (item 5 of six-evidence ladder) — defer to a
  separate sprint if Phase 5 verdict is `RESEARCH_PASS_UNAPPROVED`.
- No MODELED-financing source — refused at 4 layers; not lifted.
- No paired-entry engine support — C6 is single-leg per pair.
- No `live-loop` creation.
- No approval action.

## 7. Final report requirements (Phase 9 of evidence sprint; mirrors CAMPAIGN_012 evidence sprint's final response shape)

The evidence sprint's Phase 9 summary doc must report 40+ items
covering: branch name, commit hashes by phase, files changed by
phase, tests + validation commands, latest test count, ruff status,
data provenance status, whether data was existing or regenerated,
credentials status, broker-endpoint status, walk-forward plan status,
fold count + date ranges, per-fold execution status, aggregate metrics,
inherited gate verdict table, null-baseline comparison table, final
verdict classification, candidate-specific interpretation, whether
result meaningfully beats null, financing status + MODELED
classification, risk diagnostics status (including **cross-pair
concurrent-rejection rate as a CAMPAIGN_013-specific diagnostic**),
verifier status, implementation bugs fixed, data issues, no-tuning
confirmation, CAMPAIGN_013 not approved confirmation, no-approval
confirmation, paper/demo/live blocked confirmation, no QuantConnect/LEAN,
freeze status, remaining blockers, recommended next branch, files
to review first. Use the CAMPAIGN_012 evidence-sprint Phase 9 report
shape as the template.

## 8. Verdict classification options (binding)

| verdict | criterion |
|---|---|
| **REJECT** | any per-fold or aggregate gate fails (other than the indistinguishable-from-null case) |
| **REJECT_INDISTINGUISHABLE_FROM_NULL** | metrics cluster within ± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair of CAMPAIGN_011 |
| **RESEARCH_PASS_UNAPPROVED** | all per-fold + aggregate + financing + null-baseline-margin gates pass; **NOT approved** |
| **BLOCKED** | runner cannot complete (data issue, engine bug, runner orchestration failure) |

**Even RESEARCH_PASS_UNAPPROVED is not approval.** The verifier
extension + human approval action remain required.

## 9. Cross-pair-specific diagnostics (Phase 7 must include)

In addition to the standard CAMPAIGN_010 / 011 / 012 diagnostics:

- **Rank-gap distribution histogram** — how often does the gap
  exceed threshold? per pair, per fold.
- **Simultaneous-signal frequency** — at how many bars does the
  strategy signal on 2+, 3+, 4+, 5+ pairs concurrently? Diagnostic
  of the cross-pair concurrent-rejection problem.
- **`MAX_OPEN_POSITIONS_EXCEEDED` (or equivalent) rejection rate**
  — per fold, per pair. Expected to be non-trivial.
- **Currency-rank flip rate** — how often does a currency move from
  top-rank to bottom-rank within the lookback window? Stability
  diagnostic.
- **Pair-direction conflict rate** — fraction of bars where, e.g.,
  EUR_USD and EUR_GBP would signal different directions (only
  EUR_USD is in the universe, but this can be inferred from
  EUR/USD/GBP ranks). Sanity check on the currency-strength
  derivation.

These are reported in `CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md`
alongside the standard 8 sanity checks.

## 10. Approval boundary (binding)

**The future evidence sprint cannot approve any strategy.** Even
RESEARCH_PASS_UNAPPROVED is not approval. Item 5 (verifier extension)
and item 6 (human approval) of the six-evidence ladder remain
required.

## 11. Paper / demo / live blocked statement (binding)

- `paper-loop` / `demo-loop` → **must refuse** at every phase boundary.
- `forex_bot.cli --help` → **must not list `live-loop`**.
- `check_research_freeze.py` → **must PASS**.

## 12. Cross-links

- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md) (Phase 7a)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md)
- [`NEXT_PREFERRED_DIRECTION_004.md`](NEXT_PREFERRED_DIRECTION_004.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- Sibling evidence sprints: `research-random-entry-diagnostic-anchor-walk-forward-001`, `research-regime-switcher-atr-percentile-walk-forward-001`
