# Cost Atlas (diagnostic only)

Observed spread / ATR distributions from deduped H4 bid/ask candles for the
seven-pair research universe. **Not strategy evidence** (`strategy_evidence: false`).

## Regenerate

```bash
python scripts/build_cost_atlas.py
```

Requires local `data/campaign_002.sqlite3` (gitignored) or `EDGE_DISCOVERY_H4_DB`.

## Outputs

| file | description |
|---|---|
| `cost_atlas_summary.json` | Global and segmented aggregates |
| `cost_hostile_windows.json` | Top-decile / elevated spread/ATR cells |
| `pair_session_spread_atr.csv` | Pair × session medians and percentiles |

## Dedupe

Loads via `CandleRepo.list()` with `keep_last` policy — consistent with C011–C017.

## Use

Future research-gating recommendations only. Do not treat as tradable edge.
