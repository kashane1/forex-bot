# CAMPAIGN_002 H4 — Lean parity algorithm

`main.py` is an independent Lean re-implementation of the
already-**REJECTED** CAMPAIGN_002 H4 `trend_following 0.1.0-baseline-frozen`
baseline, for **parity verification** of the bespoke backtest engine.

> Verification only — `strategy_evidence: false`. CAMPAIGN_002 is REJECT
> and stays REJECT. No QuantConnect cloud, no brokerage, no live trading.

## What it is

A faithful port of the strategy + engine mechanics specified in
`docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md`:

- EMA(50/200) regime + Donchian(20) prior-bar breakout + ATR(14) stop;
- 2.0×ATR initial stop, 2.0×ATR trailing stop, 240-bar time stop;
- `signal_bar_close` fill timing, bid/ask-aware fills, 0.25%-risk sizing;
- the seven CAMPAIGN_002 instruments.

It deliberately does **not** replicate the bespoke `RiskEngine` gates
(spread / session / loss limits) — see the mapping spec §0. The
apples-to-apples reference is therefore the no-RiskEngine bespoke run
(`research/lean_parity/campaign_002_h4_bespoke_reference.json`,
1,647 trades), not the 1,032-trade with-RiskEngine CAMPAIGN_002 result.

## Running it (local Lean, no cloud)

1. Install the Lean CLI in a dedicated venv and `lean init` a workspace
   **outside this repo** — see `docs/research/LEAN_PARITY_LOCAL_STATUS.md`.
2. Create a Lean project; copy `main.py` and `config.json` into it.
3. Place the exported candle CSVs where the custom-data reader expects
   them — a `campaign_002_h4/` folder under the Lean **data** directory,
   containing `EUR_USD_H4_lean.csv` … `NZD_USD_H4_lean.csv` (regenerate
   via `research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.md`).
   The `Campaign002H4.GetSource` path may need adjusting to your
   workspace layout.
4. `lean backtest "<project>"` (pulls the `quantconnect/lean` Docker
   image on first run).
5. The algorithm writes `parity_summary.json` to the Lean ObjectStore
   and logs a `PARITY_SUMMARY {...}` line — feed either to
   `scripts/compare_lean_campaign_002_parity.py`.

## Files

| file | role |
|---|---|
| `main.py` | the Lean algorithm + custom-data reader |
| `config.json` | Lean project config (adjust for your workspace) |
| `README.md` | this file |

## Status

This algorithm is a **best-effort faithful implementation authored
offline**. It has **not** been executed — see
`docs/research/LEAN_ALGORITHM_IMPLEMENTATION_NOTES.md` for what is
faithful, what is approximated, and the Lean-mechanics differences a
first live run is expected to surface.
