# FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS

**Status:** process doc (binding). What a future campaign must **emit** so the
edge-discovery lab can re-screen it (matched-null, decomposition, forward-return,
ablation, matrix-sanity) retrospectively. Diagnostic/governance only.

> Motivation: the C025/C026 retrospective (see
> [`EDGE_DISCOVERY_RETROSPECTIVE_C025_C026.md`](EDGE_DISCOVERY_RETROSPECTIVE_C025_C026.md))
> could run matrix-sanity and cost-feasibility on committed artifacts, but
> **could not** run matched-null / forward-return / entry-exit decomposition
> because C025/C026 persisted only rolled-up candidate metrics — **no per-trade
> or per-signal ledger**. This doc removes that gap for future campaigns.

---

## The problem the requirements fix

C025/C026 committed `train_matrix_metrics.csv`, per-pair/side metrics, spread/
ATR diagnostics, and a candidate registry — enough for matrix-sanity and
cost-feasibility, but the individual `Trade` objects existed only in memory.
Without a ledger, the lab cannot reconstruct entries/sides/holds and therefore
cannot run the matched-null, forward-return, or entry/exit diagnostics on the
real campaign. Future campaigns must persist the inputs below.

## Required emissions

A campaign that wants to be lab-re-screenable must commit (compact; no bulky
candle dumps):

1. **Signal ledger** — one row per triggered signal, pre-filter:
   `instrument, signal_time_utc, side, timeframe, <feature columns>`.
2. **Trade ledger** — one row per executed trade (the canonical schema the lab
   already reads via `real_data.load_campaign_trades`):
   `instrument, side, units, entry_time, exit_time, entry_price, exit_price,
   stop_price, pnl, r_multiple, bars_held, spread_paid_pips, exit_reason,
   fill_timing`. Laid out as `<campaign_dir>/folds/fold_NN/fold_NN_<PAIR>_trades.csv`.
3. **Filter-stage / funnel ledger** — per signal, a boolean pass column per
   filter (`trigger, filter_a_pass, filter_b_pass, ...`) plus a per-signal value
   proxy (`log_return` / `r_multiple`). This is the direct input to
   `filter_ablation`.
4. **Pair / side / session metadata** — present on the ledgers (instrument,
   side, and a session bucket derivable from `signal_time_utc`).
5. **Hold-duration metadata** — `bars_held` per trade (drives the
   `holding_period_matched_random` and `full_matched_null` modes).
6. **Spread / cost fields** — `spread_paid_pips` per trade and the spread/ATR
   diagnostics per pair/timeframe/session (drives cost-feasibility and the
   post-cost overlay).
7. **Split-window metadata** — the train / validation / test windows and which
   split each row belongs to (so the lab never samples the test lockbox).
8. **Candidate registry + matrix result table** — one row per variant with the
   selection metric and label (the `matrix_sanity` input), plus per-pair
   breakdowns per candidate for pair-holdout fragility.

## Layout convention

Reuse the existing campaign layout the lab already understands:

```
research/campaign_0XX/<phase>/
  candidate_registry.json
  <phase>_metrics.csv                 # matrix-sanity input (one row/candidate)
  <phase>_pair_metrics.csv            # pair-holdout input
  <phase>_spread_atr_diagnostics.json # cost-feasibility input
  <phase>_signal_funnel.csv           # filter-ablation input (pass columns + value)
backtests/CAMPAIGN_0XX_*/folds/fold_NN/
  fold_NN_<PAIR>_trades.csv           # matched-null / forward-return / decomposition input
  fold_NN_<PAIR>_summary.json
```

## Size / safety constraints

- Ledgers are **compact** (per-trade / per-signal rows, not per-bar). Bulky
  equity/per-bar CSVs stay gitignored, as today.
- No raw candle dumps, DB files, credentials, or `.env` committed.
- Ledger timestamps are UTC; no broker round-trips needed to read them.

## Compatibility back-reference

The specific gaps for older campaigns are recorded in
`research/edge_discovery/retrospectives/retrospective_compatibility_gaps.json`.
Future campaigns satisfying this doc will not appear there.
