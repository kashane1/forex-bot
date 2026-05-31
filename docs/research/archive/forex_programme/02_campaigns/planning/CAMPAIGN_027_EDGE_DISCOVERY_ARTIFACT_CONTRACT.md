# CAMPAIGN_027_EDGE_DISCOVERY_ARTIFACT_CONTRACT

**Status:** SCAFFOLD_ONLY / PRECOMMITTED / NOT_RUN / NOT_APPROVED. Phase 3 of
`research-campaign-027-h4-filtered-zscore-reversion-scaffold-001`.

Makes CAMPAIGN_027 **edge-discovery-lab compatible from day one**: it enumerates
exactly what a *future* execution sprint must emit so the lab
(`research/edge_discovery/`) can re-screen the campaign's own artifacts
(cost-feasibility → forward-returns → matched-null → filter-ablation →
matrix-sanity) **without** the C025/C026 "rolled-up metrics only, no per-signal
ledger" gap. The machine-readable form is
[`research/campaign_027/artifact_contract.json`](../../research/campaign_027/artifact_contract.json);
a contract test (`tests/unit/test_campaign_027_artifact_contract.py`) keeps it
honest. **No ledger is produced in this sprint** — this is the contract the
future sprint fills.

> Binding companions:
> [`FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md`](FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md)
> (emission items 1–12),
> [`EDGE_DISCOVERY_COMPATIBILITY_CHECKLIST.md`](EDGE_DISCOVERY_COMPATIBILITY_CHECKLIST.md).

---

## Required future-execution artifacts (maps to requirements items 1–12)

### A. Ledgers

1. **Signal ledger** — one row per *triggered* signal, **pre-filter**:
   `instrument, signal_time_utc, side, timeframe, zscore, atr14, atr_percentile,
   session_bucket, f_low_vol, f_strong_extension, f_quiet_session`. Includes
   **diagnostic-only long rows** (clearly flagged `entered=false`), so the lab
   can ablate the long side it was told to drop.
2. **Trade ledger** — one row per *executed* (short-only) trade, the canonical
   schema `real_data.load_campaign_trades` reads:
   `instrument, side, units, entry_time, exit_time, entry_price, exit_price,
   stop_price, pnl, r_multiple, bars_held, spread_paid_pips, exit_reason,
   fill_timing`. Layout:
   `backtests/CAMPAIGN_027_*/folds/fold_NN/fold_NN_<PAIR>_trades.csv`.
3. **Filter-stage / signal-funnel ledger** — per signal: `trigger,
   f_low_vol_pass, f_strong_extension_pass, f_quiet_session_pass` + a per-signal
   value proxy (`log_return` / `log_return_post_cost_conservative` / `r_multiple`)
   — the direct `filter_ablation` input.
8. **Candidate registry + matrix result table** — one row per variant (here a
   single frozen candidate) with the selection metric + label, plus per-pair
   breakdown per candidate (pair-holdout input). Even with one candidate the
   registry must exist (`candidate_registry.json`).

### B. Metadata

4. **Pair / side / session metadata** on the ledgers (instrument, side, session
   bucket derivable from `signal_time_utc`).
5. **Hold-duration metadata** — `bars_held` per trade (drives
   `holding_period_matched_random` / `full_matched_null`).
6. **Spread / cost fields** — `spread_paid_pips` per trade + per-pair/timeframe/
   session spread/ATR diagnostics; both optimistic and conservative post-cost
   metrics.
7. **Split-window metadata** — train/validation/test tag per row; **the lab must
   never sample the test rows** in any screen.
9. **Timeframe column** — explicit `timeframe = H4` on signal + trade ledgers.
10. **Null-benchmark compatibility fields** — `instrument, side, entry_time_utc,
    bars_held`, derivable session/weekday, **plus** the C011 deduped null
    baseline reference
    (`research/null_baselines/campaign_011_deduped_null_baseline.json`).
11. **Reproducibility manifest** (`run_manifest.json` per phase) — code/commit
    hash, input data path + dedupe policy, date span, the **precommitted rule**
    (the frozen block from the Phase-2 scope), lab module versions,
    `strategy_evidence:false` / `diagnostic_only:true` where applicable.
12. **Random-seed metadata** — explicit seed (or seed range) for every
    stochastic step (matched-null draws, bootstrap, sampling), logged in the run
    manifest and each null/matrix artifact.

## Conservative- and optimistic-cost metrics (both required)

Every per-trade and aggregate row must carry **both** `*_optimistic` and
`*_conservative` post-cost figures. The **conservative** figure (1.5-pip flat
spread + 0.2-pip slip + financing over the 12-bar hold) is the **binding** metric
for every kill condition; the optimistic figure is diagnostic context.

## Matched-null- and filter-ablation-compatible outputs

- **Matched-null:** the trade ledger's `instrument/side/entry_time_utc/bars_held`
  + derivable session/weekday are sufficient for the lab to reconstruct all six
  null modes from the campaign's own ledger (the exact gap C025/C026 had).
- **Filter-ablation:** the signal-funnel ledger's per-filter boolean pass columns
  + per-signal value proxy are the direct `filter_ablation` input; the future
  sprint must re-derive `FILTER_ADDS_EDGE` for each of the three retained filters
  on its own data.

## Layout convention (reuses the lab-understood layout)

```
research/campaign_027/
  artifact_contract.json                    # this contract (committed this sprint)
  preflight/                                # Phase 5 preflight artifacts (this sprint)
  train/                                    # FUTURE: matrix-sanity + ablation inputs
    candidate_registry.json
    train_metrics.csv
    train_pair_metrics.csv
    train_spread_atr_diagnostics.json
    train_signal_funnel.csv
    train_run_manifest.json
backtests/CAMPAIGN_027_*/folds/fold_NN/     # FUTURE: matched-null / forward-return input
  fold_NN_<PAIR>_trades.csv
  fold_NN_<PAIR>_summary.json
```

## Size / safety constraints (binding)

- Ledgers are **compact** (per-trade / per-signal rows, never per-bar). Bulky
  equity/per-bar CSVs stay gitignored.
- No raw candle dumps, DB files, `.env`, credentials, or bulky artifacts
  committed.
- Timestamps are UTC; readable with no broker round-trip.
- **No test-lockbox sampling** anywhere in any screen.

## Scaffold-state assertions (true now, enforced by the contract test)

- `not_approved: true`, `promotion_eligible: false`,
  `paper_demo_live_enabled: false`, `strategy_evidence: false`.
- `test_lockbox.sealed: true`, `test_lockbox.runnable_in_scaffold: false`.
- Every future-ledger entry is marked `produced_in_scaffold: false` (the contract
  declares them; this sprint does not emit them).
- No field anywhere asserts approval / promotion eligibility.
