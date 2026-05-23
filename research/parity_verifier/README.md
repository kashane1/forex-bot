# research/parity_verifier — free / local independent parity verifier

A minimal independent re-implementation of the CAMPAIGN_002 H4
`trend_following 0.1.0` strategy + engine mechanics. Built from the
mapping spec (`docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md`) and
the authoritative parameter file
(`research/lean_parity/lean_parity_config.json`), with **no** imports
from `src/forex_bot/` and no external services.

> `strategy_evidence: false`. The verifier is a diagnostic instrument.
> It cannot approve a strategy. CAMPAIGN_002 remains REJECT. Paper /
> demo / live remain blocked. `configs/approved_strategies.yaml` stays
> empty.

## Module layout

| module | role |
|---|---|
| `models.py` | Pydantic models (Bar, CandleSeries, VerifierConfig, Signal, Trade, …) |
| `instruments.py` | Static instrument metadata for the seven-pair CAMPAIGN_002 universe |
| `data_loader.py` | Read-only loaders for the parameter JSON, bespoke reference JSON, and H4 candle CSVs |
| `indicators.py` | Independent EMA / ATR / Donchian — re-derived from the canonical definitions, not copied from the bespoke engine |
| `rules.py` | Independent rule evaluation: entry, exit precedence, initial stop, trailing-stop ratchet, bid/ask-aware fill, 0.25%-risk sizing, PnL |
| `event_loop.py` | Bar-by-bar deterministic loop over one pair |
| `compare.py` | Tolerance-ladder comparison against the bespoke reference |
| `reporting.py` | Markdown rendering for verifier and comparison output |

There is no `forex_bot` import anywhere in this package; a CI grep
guards it (Phase 1 test).

## Running

The end-to-end script entry point lives at
`scripts/run_free_local_parity_verifier.py`. It auto-detects which of
the seven H4 export CSVs are present locally (the CSVs are
gitignored bulk data) and reports a clear BLOCKED status for any pair
whose CSV is missing.

```bash
python scripts/run_free_local_parity_verifier.py \
    --output research/parity_verifier/results/campaign_002_h4/
```

## Safety

- No network calls, no broker calls, no QuantConnect / LEAN calls.
- No edits to `configs/approved_strategies.yaml`, the bespoke engine,
  the CAMPAIGN_002 rules, or any campaign report.
- No new external dependency — uses only `pandas`, `numpy`,
  `pydantic`, `pyyaml` (all already in the repo).
- Verifier outputs live under `research/parity_verifier/results/`;
  bulky outputs are gitignored.

See `docs/research/INFRA_FREE_LOCAL_PARITY_VERIFIER_001_PLAN.md` for
the implementation-sprint plan and
`docs/research/FREE_LOCAL_PARITY_VERIFIER_PLAN.md` for the original
design.
