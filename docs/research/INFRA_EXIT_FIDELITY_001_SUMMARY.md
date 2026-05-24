# Infrastructure Exit-Fidelity Sprint 001 — Summary

**Sprint id:** `infra-exit-fidelity-001`
**Branch:** `claude/keen-leakey-a15799`
**Date completed:** 2026-05-24
**Plan:** [INFRA_EXIT_FIDELITY_001_PLAN.md](INFRA_EXIT_FIDELITY_001_PLAN.md)
**Workflow plan (deepened):** [docs/plans/2026-05-24-feat-backtest-exit-fidelity-plan.md](../plans/2026-05-24-feat-backtest-exit-fidelity-plan.md)

## Outcome

✅ **SHIPPED.** Both exit-fidelity features are in place; all safety invariants hold; the research freeze is unchanged; every CAMPAIGN_001–009 artifact remains hash-comparable under default mode.

## What changed

### Feature 1 — Same-bar SL+TP ambiguous-exit instrumentation (always-on)

The engine now records when an adverse-stop exit happened on a bar where the take-profit was also in range. Per-trade flag `TradeRecord.ambiguous_exit`, aggregate `BacktestMetrics.ambiguous_exit_count` (mirrored on `BacktestResult.ambiguous_exit_count`).

- **Pure observation** — never changes `exit_reason`, `exit_price`, `pnl`, `r_multiple`, or `final_equity`.
- **No `config_hash` change** — Phase 0 hash snapshot for all 3 pinned configs (CAMPAIGN_001 / CAMPAIGN_004 / CAMPAIGN_009) is byte-identical after this feature lands.
- **First-ever measurement** of same-bar SL+TP collision frequency. CAMPAIGN_009-class mean-reversion strategies can now answer "how many stop-outs hid a TP win?" by reading the new counter.

### Feature 2 — Opt-in gap-through fill (`backtest.gap_fill_policy = "gap_through"`)

When a bar OPENS past a stop or take-profit level, the engine fills at the bar open instead of at the level. Four cases (long/short × stop/tp). Adverse for stops, favorable for TPs. Mirrors how real stop-market and limit orders fill when price has already moved through.

- **Strictly opt-in.** Default `"none"` preserves byte-identical `config_hash` for every existing campaign artifact.
- **Distinct hash under `gap_through`** — never silently confused with default-mode runs.
- **Trailing-stop snapshot** — gap-fill comparison uses the pre-trailing-update stop (the level active at the bar's open), not a tightened post-update level. Range tests continue to use the post-update stop (unchanged).
- **bid/ask_open `None` fallback** — falls back to mid `open` via `pd.notna()`. Same retrofit applied to all 8 pre-existing bid/ask resolutions (latent NaN-handling bug fixed).
- **Per-trade `gap_fill: bool` + `gap_fill_distance_pips: Decimal | None`** flags, aggregated as `gap_fill_exit_count` on metrics + result.
- **`BacktestResult.gap_fill_policy`** propagated to every artifact (CSV row, metrics JSON, metrics MD, summary JSON).

## Phase ledger

| Phase | Commit | Files | Tests added |
|---|---|---|---|
| 0 | `d12193b` | plan doc, repo-convention plan, hash snapshot + regenerator, workflow plan (deepened) | — |
| 1 | `0cff658` | schema additions on TradeRecord/BacktestMetrics/BacktestResult, ambiguous-exit detection in engine, to_dict bool-handling fix | 13 (long+short detection, EOD/time-stop/no-TP negatives, trailing-stop, risk-engine parity, multi-trade aggregation, type-stability, key-order, Phase 0 hash regression) |
| 2 | `96c520f` | `GapFillPolicy` Literal + `GAP_FILL_POLICIES` frozenset, `BacktestConfig.gap_fill_policy`, engine kwarg + conditional hash inclusion, `--gap-fill-policy` CLI flag | 13 (config defaults/accepts/rejects, frozenset-Literal parity, engine default, hash invariance + match-snapshot, hash differs under gap_through, CLI rejection + 2x2 matrix, snapshot doc guardrail) |
| 3 | `2f136e0` | pre-trailing snapshot, gap-fill resolver (folded long/short via is_long), bid/ask_open resolution + pd.notna retrofit across all bid/ask resolutions | 52 (16-case parametrized matrix under gap_through + 16-case mirror under none, trailing snapshot ordering, mid-open fallback, EOD negative, simultaneous ambiguous+gap, D1AGG weekend gap, 16-case property-based invariants) |
| 4 | `9f27677` | CSV columns, metrics JSON/MD lines, summary JSON, asymmetry tests | 10 (CSV round-trip + empty-string convention, metrics JSON/MD/summary new fields, MD renders 0, summary carries policy at default, write_all smoke, committed `_index.json` loads cleanly + lacks new fields by construction, legacy dict construction) |
| 5 | `b4df773` | `GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md` (200+ lines: semantics, table, ordering caveat, fallback rule, parity-impact, asymmetry, known limitations) | — |
| 6 | (this commit) | this summary | — |

**Total: 88 new tests added** across the sprint. Final pytest: **790 passed, 0 failed**. Ruff: **clean**.

## Safety invariants (verified at final commit)

| Invariant | Status |
|---|---|
| `configs/approved_strategies.yaml` is `approved: []` | ✅ verified |
| `paper-loop` / `demo-loop` / live refuse every strategy | ✅ unchanged (no approval edits) |
| Backtesting commands still available | ✅ (`bot backtest` works; new flag accepted) |
| No credentials staged / logged / committed | ✅ (no `.env` touched, no OANDA call) |
| CAMPAIGN_001–009 artifacts immutable | ✅ (none modified; only read in tests + referenced in docs) |
| Default `gap_fill_policy = "none"` reproduces prior `config_hash` | ✅ (3 pinned configs byte-identical to Phase 0 snapshot) |
| Ambiguous-exit counter is pure observation | ✅ (never changes exit_reason/exit_price/PnL) |
| pytest + ruff green | ✅ (790 passed, 0 failed; ruff clean) |

## Hash regression evidence

Phase 0 pinned snapshot at [tests/fixtures/pre_sprint_config_hashes.json](../../tests/fixtures/pre_sprint_config_hashes.json) (with `_doc` guardrail):

```
campaign_001_baseline               d8af17169b6836e8
campaign_004_volatility_breakout    aea8cb29230317b6
campaign_009_mean_reversion         308d3dcb1abeb52f
```

Re-run at end of Phase 6 (default-mode `gap_fill_policy="none"`): byte-identical to all three.

Re-run with `gap_fill_policy="gap_through"`: produces a distinct hash (verified by `test_gap_through_changes_hash`). The two modes can never be silently confused.

## What changed in the engine, file-by-file

- `src/forex_bot/backtesting/engine.py`: +101 / -29 lines. Pre-trailing snapshot, gap-fill resolver, BacktestResult schema additions, conditional hash inclusion, ambiguous-exit detection, pd.notna retrofit across 8 bid/ask resolutions, threading of new fields into TradeRecord constructor.
- `src/forex_bot/backtesting/metrics.py`: +57 / -3 lines. TradeRecord 3 new trailing fields, BacktestMetrics 2 new trailing fields, to_dict bool-handling fix, compute_metrics aggregation for new counts (both empty-trades and populated branches).
- `src/forex_bot/backtesting/exporters.py`: +22 / -2 lines. CSV fieldnames + row dict, metrics JSON top-level, metrics MD lines, summary JSON top-level.
- `src/forex_bot/backtesting/fills.py`: +18 / -0 lines. `GapFillPolicy` type alias + `GAP_FILL_POLICIES` frozenset (mirrors `FillTiming` / `FILL_TIMINGS`).
- `src/forex_bot/config.py`: +6 / -0 lines. `BacktestConfig.gap_fill_policy: Literal["none", "gap_through"] = "none"`.
- `src/forex_bot/cli.py`: +18 / -1 lines. `--gap-fill-policy` typer Option, validation against `GAP_FILL_POLICIES`, `[dim]` echo, engine kwarg thread-through.
- `scripts/snapshot_pre_sprint_hashes.py`: NEW, 116 lines. Pre-sprint hash snapshot regenerator (one-off; carries header warning against accidental rerun).
- `tests/fixtures/pre_sprint_config_hashes.json`: NEW, 6 lines (with `_doc` guardrail).
- `tests/unit/test_ambiguous_exit.py`: NEW, 480 lines.
- `tests/unit/test_gap_fill.py`: NEW, 670 lines.
- `tests/unit/test_exit_fidelity_exporters.py`: NEW, 320 lines.
- `docs/research/INFRA_EXIT_FIDELITY_001_PLAN.md`: NEW, 76 lines.
- `docs/research/INFRA_EXIT_FIDELITY_001_SUMMARY.md`: NEW, this file.
- `docs/research/GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md`: NEW, 203 lines.
- `docs/plans/2026-05-24-feat-backtest-exit-fidelity-plan.md`: NEW, 386 lines (workflow plan; deepened by 8 review/research agents).

**Untouched (read-only references):** `CAMPAIGN_001..009/runs/_index.json` and all `*_summary.json` artifacts; CAMPAIGN_*_PRECOMMIT.md / POSTMORTEM.md / LEAN_MAPPING_SPEC.md / WALK_FORWARD_RETROSPECTIVE.md / etc; `FILL_TIMING_MODEL.md`; `INFRA_EXECUTION_FIDELITY_001_*` artifacts.

## Deferred / out of scope

- **Lean parity baselines under `gap_through` mode.** The bespoke engine in `gap_through` mode moves toward Lean's stop-or-worse fill behavior; existing parity tolerances were captured under the old bespoke behavior and would likely diverge. Regenerating baselines requires Lean cloud runs — a separate sprint.
- **Entry-bar gap-through-stop in `next_bar_open` mode** (the entry-fills-past-its-own-stop pathology). Pre-existing engine behavior in the entry code path; orthogonal to exit fidelity. Deserves a dedicated audit sprint.
- **`_index.json` backfill for prior CAMPAIGN_001–009 runs.** Would force writes to immutable campaign artifacts and violate the freeze. Not done. Forward + backward read tolerance verified instead.
- **`gap_fill_distance_pips` signed vs absolute.** Currently absolute; the sign is implicit in `exit_reason`. Future enhancement.
- **"TP-reachable-at-open" specific flag.** `ambiguous_exit` records bid_high/ask_low touches; doesn't distinguish "TP was reachable at the bar's open" specifically. Future enhancement.

## Recommendations

1. **Use default mode as the canonical reference** for every prior CAMPAIGN_001-009 verdict. `gap_through` is research infrastructure, not a re-evaluation of a prior verdict.
2. **Measure ambiguous-exit collision rates** on CAMPAIGN_008 / CAMPAIGN_009 (the mean-reversion-with-TP campaigns). If the rate is non-trivial, it becomes evidence that the stop-precedence rule materially understates TP wins for those strategies.
3. **For future low-frequency / D1AGG research**, default to `gap_through` from the start. Daily bars have the largest gap-to-next-open exposure; the default `none` is most misleading there.
4. **Never regenerate the Phase 0 hash snapshot** without confirming with the sprint author. The snapshot's `_doc` header carries a verbatim warning enforced by `test_snapshot_doc_guardrail`.
5. **The pd.notna() retrofit** to all bid/ask resolutions is a strict correctness improvement (latent NaN bug previously never triggered because every prior test set bid/ask explicitly). If a future test or campaign uses mid-only candles, the engine now handles them correctly.

## Cross-references

- [INFRA_EXIT_FIDELITY_001_PLAN.md](INFRA_EXIT_FIDELITY_001_PLAN.md) — sprint plan
- [GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md](GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md) — semantics + ordering + asymmetry + known limitations
- [docs/plans/2026-05-24-feat-backtest-exit-fidelity-plan.md](../plans/2026-05-24-feat-backtest-exit-fidelity-plan.md) — workflow plan (deepened by 8 review/research agents)
- [FILL_TIMING_MODEL.md](FILL_TIMING_MODEL.md) — precedent opt-in fidelity feature
- [INFRA_EXECUTION_FIDELITY_001_PLAN.md](INFRA_EXECUTION_FIDELITY_001_PLAN.md) + [INFRA_EXECUTION_FIDELITY_001_SUMMARY.md](INFRA_EXECUTION_FIDELITY_001_SUMMARY.md) — precedent sprint
- [CAMPAIGN_009_PRECOMMIT.md §59](CAMPAIGN_009_PRECOMMIT.md) — same-bar tie-break rule (load-bearing)
- [CAMPAIGN_002_LEAN_MAPPING_SPEC.md §131-133](CAMPAIGN_002_LEAN_MAPPING_SPEC.md) — original gap-fill mismatch documentation
