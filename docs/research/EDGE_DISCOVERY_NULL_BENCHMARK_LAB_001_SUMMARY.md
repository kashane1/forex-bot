# EDGE_DISCOVERY_NULL_BENCHMARK_LAB_001 — SUMMARY

**Final classification:** `INFRASTRUCTURE/DIAGNOSTIC — NO STRATEGY APPROVED /
NO TEST LOCKBOX OPENED / C025+C026 VERDICTS PRESERVED`. This sprint **extended**
the existing import-isolated edge-discovery lab; it did **not** rebuild it.

---

1. **Branch.** `research-edge-discovery-null-benchmark-lab-001` (from
   origin/main `578f31b`, with C026 already merged).

2. **Commit hashes by phase.**
   - P0 truth audit + plan — `e04b8ad`
   - P1 existing-lab audit + capability map — `06e2eea`
   - P2 matched-null module — `70221a6`
   - P3 filter-ablation module — `d83ee01`
   - P4 multiple-comparison module — `ef1dadb`
   - P5 cost-feasibility flags + CLI scripts — `c605318`
   - P6 protocol/gates/workflow/checklist/artifact-req docs — `837dc25`
   - P7 C025/C026 retrospective — `2ae2e6f`
   - P8–9 index/status/manifest/backlog + validation + this summary — final commit.

3. **Files changed by phase.**
   - P0: `EDGE_DISCOVERY_NULL_BENCHMARK_LAB_001_PLAN.md`.
   - P1: `EDGE_DISCOVERY_EXISTING_LAB_AUDIT_001.md`.
   - P2: `research/edge_discovery/matched_nulls.py` + `__init__.py` +
     `tests/research/edge_discovery/test_matched_nulls.py`.
   - P3: `research/edge_discovery/filter_ablation.py` + `__init__.py` +
     `test_filter_ablation.py`.
   - P4: `research/edge_discovery/multiple_comparison.py` + `__init__.py` +
     `test_multiple_comparison.py`.
   - P5: `research/edge_discovery/cost_feasibility.py` + `__init__.py` +
     `test_cost_feasibility.py` + four `scripts/run_edge_discovery_*.py` +
     `test_cli_scripts.py` + `.gitignore`.
   - P6: `EDGE_DISCOVERY_PROTOCOL.md`, `FUTURE_CAMPAIGN_REENTRY_GATES.md`,
     `FUTURE_STRATEGY_SEARCH_WORKFLOW.md`,
     `PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md`,
     `FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md`.
   - P7: `scripts/run_edge_discovery_c025_c026_retrospective.py`,
     `research/edge_discovery/retrospectives/*.json`,
     `EDGE_DISCOVERY_RETROSPECTIVE_C025_C026.md`.
   - P8–9: `STRATEGY_STATUS.md`, `EVIDENCE_INDEX.md`, `EVIDENCE_MANIFEST.json`,
     `FUTURE_RESEARCH_BACKLOG.md`, this summary.

4. **Modules added** (all under `research/edge_discovery/`, import-isolated):
   `matched_nulls.py`, `filter_ablation.py`, `multiple_comparison.py`,
   `cost_feasibility.py`. Existing `windows`/`costs`/`null`/`report`/
   `real_data` and the `studies/` suite were reused, not duplicated.

5. **Scripts added.** `scripts/run_edge_discovery_matched_null.py`,
   `run_edge_discovery_filter_ablation.py`, `run_edge_discovery_matrix_sanity.py`,
   `run_edge_discovery_cost_feasibility.py`, and the retrospective runner
   `run_edge_discovery_c025_c026_retrospective.py`.

6. **Tests added.** `test_matched_nulls.py` (16), `test_filter_ablation.py` (8),
   `test_multiple_comparison.py` (10), `test_cost_feasibility.py` (7),
   `test_cli_scripts.py` (14) — 55 new lab tests; full lab suite 222 passed.

7. **How matched-null benchmarks work.** `matched_null_baseline(ledger,
   frames_by_pair, *, mode, window_bars, seeds)` draws structure-matched random
   entries from the per-pair candle frames and compares the strategy's own mean
   forward log-return (computed identically at the real entries) against the
   null distribution. Six modes preserve increasing structure:
   `timestamp_random_same_pair`, `side_shuffled`, `pair_matched_random`,
   `session_matched_random`, `holding_period_matched_random`,
   `full_matched_null`. Output: null mean/median/p05/p95, P(null ≥ strategy),
   strategy percentile, effect size, sparse-bucket list, and descriptive flags
   (`BEATS/ABOVE/WITHIN/BELOW_MATCHED_NULL`, `MATCHED_NULL_SPARSE`).
   Deterministic per seed; reuses the cost overlay so both sides pay it.

8. **How entry/exit decomposition works.** Reused — the existing
   `studies/exit_asymmetry_robustness` and `_cross_campaign` compare real vs
   null entries against real vs null exits to locate edge in the entry, the
   exit, or neither. The audit documents this as the decomposition home; no
   duplicate module was added.

9. **How forward-return diagnostics work.** Reused `windows.compute_forward_returns`
   — signed forward log-returns over a window at signal-bar close, with
   trailing/missing handling; horizons and side configurable.

10. **How filter ablation works.** `filter_ablation(signals, *, filter_cols,
    value_col, ...)` computes trigger-only / +one-filter / cumulative /
    leave-one-out / all-filters stages and a per-filter contribution. The
    adds-edge/hurts/only-reduces-sample decision is **noise-aware**: the
    marginal expectancy change must exceed the subset mean's standard error,
    so a random sample-shrinking filter is correctly tagged
    `FILTER_ONLY_REDUCES_SAMPLE`, not `ADDS/HURTS_EDGE`. Other flags:
    `FILTER_TOO_SPARSE`, `FILTER_PAIR_SPECIFIC_ONLY`.

11. **How cost feasibility works.** `cost_feasibility.classify_cost_feasibility`
    / `cost_feasibility_table` flag a spread/ATR ratio (it does **not**
    recompute spread/ATR — that stays in `costs.py`/`cost_atlas`) as
    `COST_FEASIBLE`/`COST_HOSTILE` with structural flags
    `TIMEFRAME_TOO_FAST`/`SESSION_HOSTILE`/`PAIR_COST_(DIS)ADVANTAGED`, plus
    min-target-R and an opportunity score. Default hostile threshold 0.25.

12. **How multiple-comparison checks work.** `matrix_sanity(table, *,
    metric_col, label_col, null_reference, null_std, ...)` bootstraps the
    best-of-N-under-noise distribution (`prob_best_le_null_max`,
    `deflated_improvement`), gaps the best to a null reference, and runs
    leave-one-pair-out / leave-one-time-block-out fragility. Flags:
    `ROBUST_MATRIX_SIGNAL`, `LIKELY_SELECTION_NOISE`,
    `FRAGILE_SINGLE_PAIR_RESULT`, `FRAGILE_TIME_BLOCK_RESULT`,
    `TOO_MANY_VARIANTS_FOR_EVIDENCE`, `INCONCLUSIVE`. Deterministic given seed.

13. **C025 retrospective findings.** Matrix-sanity: best expectancy −0.0767 R,
    **below** the C011 null (best−null −0.0738), `prob_best_le_null_max = 1.000`
    → `INCONCLUSIVE` + `LIKELY_SELECTION_NOISE` (pair-holdout: no sign flip —
    uniformly negative). Cost-feasibility: **16/16** M5 candidates
    `COST_HOSTILE` (spread/ATR ≈ 0.45). The lab reproduces C025's REJECT from
    committed artifacts.

14. **C026 retrospective findings.** Matrix-sanity: best expectancy −0.0083 R,
    still below the C011 null (best−null −0.0054), `prob_best_le_null_max =
    1.000` → `INCONCLUSIVE` + `LIKELY_SELECTION_NOISE` + **`FRAGILE_SINGLE_PAIR_RESULT`**
    (USD_JPY-dominant). Cost-feasibility by timeframe: M3 0.637
    `COST_HOSTILE/TIMEFRAME_TOO_FAST`, **M15 0.218 and M30 0.144 `COST_FEASIBLE`**.
    So cost alone does NOT explain C026's reject — the slower rungs are
    cost-feasible but the matched-to-null check shows no edge (the prose verdict
    "a cost gradient, not a hidden edge", made mechanical).

15. **Which diagnostics would have warned us before the full campaigns.**
    Cost-feasibility would have killed C025 (M5 hostile) and C026's M3 rung at
    step 1, before any campaign. Matrix-sanity-vs-the-C011-null would have shown
    C026's cost-feasible M15/M30 rungs are still below null and
    selection-noise-consistent. Both full campaigns were avoidable.

16. **New future strategy workflow.** Market/opportunity map → forward-return →
    filter ablation → matched-null → entry/exit decomposition →
    multiple-comparison → **gate review** → (only then) scaffold a campaign →
    train/validation → parity → test lockbox → promotion review. See
    [`FUTURE_STRATEGY_SEARCH_WORKFLOW.md`](FUTURE_STRATEGY_SEARCH_WORKFLOW.md).

17. **New pre-campaign checklist.**
    [`PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md`](PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md)
    — copy-per-idea: data coverage, cost feasibility, signal info, matched null,
    filter contribution, exit decomposition, multiple-comparison risk,
    concentration, expected trade count, failure conditions, deserves-a-campaign.

18. **Any strategy approved?** **No.**

19. **`approved_strategies.yaml` remains `approved: []`?** **Yes** — unchanged.

20. **Paper/demo/live remain blocked?** **Yes** — no loop/approval/executor
    files were touched.

21. **Test lockbox opened?** **No.** The lab never samples the lockbox; the
    retrospective used only committed train-window artifacts.

22. **Archive/freeze/secrets status.** `check_research_freeze.py`,
    `validate_research_archive.py`, `scan_artifacts_for_secrets.py` — all PASS
    (see item 23).

23. **Ruff/pytest results.** `ruff check src tests scripts research` — clean.
    `pytest tests/ -q` — **2157 passed, 3 skipped** (the 3 skips are pre-existing
    — absent local H4 store / gitignored C008 CSVs — not introduced here;
    baseline was 2101 passed / 3 skipped, so +56 from the new lab tests).
    Freeze/archive/secrets gates all PASS.

24. **Known limitations.** Matched-null / forward-return diagnostics require
    per-pair candle frames; in this worktree the real frames live only in a
    Postgres research DB / gitignored sqlite in the primary checkout, so those
    code paths are exercised on synthetic frames in tests and BLOCK cleanly in
    the CLI when frames are absent. The matched-null measures forward
    log-return, not R-multiples; a real campaign ledger carrying only
    `r_multiple` is a known metric-mismatch handled by deriving returns from
    frames. The cost-feasibility flag layer consumes spread/ATR ratios; it does
    not recompute them.

25. **Compatibility gaps for older campaigns.** C025/C026 persisted only
    rolled-up candidate metrics — no per-trade/signal ledger — so matched-null,
    forward-return, entry/exit decomposition, and filter-ablation retrospectives
    were `SKIPPED_*_UNAVAILABLE` (recorded in
    `research/edge_discovery/retrospectives/retrospective_compatibility_gaps.json`).
    [`FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md`](FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md)
    specifies the ledgers future campaigns must emit to close this gap.

26. **Recommended next step.** Use the lab as the **front gate** for the next
    strategy idea: run the pre-campaign checklist + re-entry gates *before*
    proposing a campaign. Do not start a campaign that has not cleared them. No
    new campaign is recommended by this sprint; the standing strategy-search
    pause is unchanged.

27. **Exact files to review first.**
    1. [`EDGE_DISCOVERY_EXISTING_LAB_AUDIT_001.md`](EDGE_DISCOVERY_EXISTING_LAB_AUDIT_001.md) — why we extended, not rebuilt.
    2. [`research/edge_discovery/matched_nulls.py`](../../research/edge_discovery/matched_nulls.py) — the core gap module.
    3. [`research/edge_discovery/multiple_comparison.py`](../../research/edge_discovery/multiple_comparison.py) — selection-noise checks.
    4. [`EDGE_DISCOVERY_RETROSPECTIVE_C025_C026.md`](EDGE_DISCOVERY_RETROSPECTIVE_C025_C026.md) — proof the lab reproduces both REJECTs.
    5. [`FUTURE_CAMPAIGN_REENTRY_GATES.md`](FUTURE_CAMPAIGN_REENTRY_GATES.md) — the binding gates.
