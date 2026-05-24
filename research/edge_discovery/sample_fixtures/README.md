# Edge-discovery sample fixtures

Small, **committed** fixtures so the lab utilities and Phase 3 studies
are reproducible without a hydrated local SQLite store. None of these
files is research evidence; they are illustrative inputs that exercise
the lab's loaders, windows, costs, and null code-paths end-to-end.

| file | shape | purpose |
|---|---|---|
| `synthetic_EUR_USD_H4.csv` | 480 H4 bars, deterministic from seed `42` | candle CSV in the d1_aggregation sample shape — exercises `load_candles_csv`, `compute_forward_returns`, `random_null_baseline`, and the cost overlay |
| `synthetic_events.csv` | 6 events across 3 classes (`NFP`, `FOMC`, `CPI`) | event CSV in the `time,event_class` shape — exercises `load_event_fixture` and the event-window study |

To re-run against real candle data, point the study scripts at a CSV
in the same column shape extracted from the hydrated local store.

> **Synthetic data is not strategy evidence.** Any output computed from
> these fixtures is illustrative and may not be cited as edge evidence.
> See `docs/research/EDGE_DISCOVERY_LAB_001_PLAN.md`.
