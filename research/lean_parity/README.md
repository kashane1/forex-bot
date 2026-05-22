# Lean parity harness — preparation layer

**Status: PREPARATION HARNESS.** QuantConnect Lean is still **not**
installed in this repo and was **not run** — no backtest, no cloud job,
no live order. What changed in `infra-execution-fidelity-001` Phase 3:
the parity prep is now partly *runnable*. Two scripts
(`scripts/build_lean_parity_config.py`, `scripts/export_lean_parity_data.py`)
extract the authoritative parameters and export the candle data; the
remaining steps (install Lean, write the algorithm, run the backtest)
stay manual and human-initiated.

See `docs/research/LEAN_PARITY_EXECUTION_GUIDE.md` for what runs now and
what is manual, `docs/research/LEAN_PARITY_DESIGN.md` for the full
design, and `src/forex_bot/lean/README.md` for the Lean boundary rules.

## What this is

An independent re-implementation of **one** historical campaign
(CAMPAIGN_002, the H4 `trend_following` baseline) in QuantConnect Lean,
used to **verify the bespoke backtest engine** in
`src/forex_bot/backtesting/`. It is verification infrastructure — it
cannot approve any strategy, and the target campaign is already REJECT.

## Files

- `campaign_002_h4_spec.md` — the replication spec and Lean algorithm
  skeleton. **Note:** its hand-written parameter table predates Phase 3
  and was copied from the frozen baseline; for authoritative parameters
  use `lean_parity_config.json` (below), not that table.
- `lean_parity_config.json` — **authoritative** parameters, generated
  from the committed CAMPAIGN_002 config by
  `scripts/build_lean_parity_config.py`. Regenerate if the campaign
  config changes.
- `lean_h4_export_format.md` — the Lean custom-data CSV format that
  `scripts/export_lean_parity_data.py` produces.
- `CAMPAIGN_002_PARITY_CHECKLIST.md` — a tickable mapping + tolerance
  checklist for the parity run.
- (future) a Lean project directory created by `lean init`, the
  exported candle data (`exported/`), and a backtest results folder.
  None of that is committed — it does not exist until a human runs the
  setup below.

## Constraints (do not violate)

- **Local only.** Use Lean's free, open-source local backtester
  (the `lean` CLI + Docker). Do **not** run cloud backtests.
- **No paid QuantConnect tier.** The OANDA brokerage plugin and cloud
  compute require a paid org tier — not needed and not used for a local
  parity backtest on imported data.
- **No live, no orders, no credentials.** Parity is a historical
  backtest comparison only.
- **No re-fetch of data.** Parity replays the *same* stored candles the
  bespoke engine used (`data/campaign_002.sqlite3`), so a data
  difference cannot confound the comparison.

## Setup steps (for whoever runs this later)

Lean was not available during this sprint, so these steps are
documented rather than executed:

1. **Install the Lean CLI** (open-source, free):
   ```bash
   pip install lean
   ```
   Lean's local backtester runs strategies in Docker; install Docker
   Desktop and ensure it is running.
2. **Initialize a Lean workspace** in a scratch location (not inside
   this repo's package tree):
   ```bash
   lean init
   ```
3. **Create the algorithm** from the skeleton in
   `campaign_002_h4_spec.md` as a Python algorithm inside the Lean
   workspace.
4. **Export the candle data.** Write a small exporter that reads the
   CAMPAIGN_002 H4 bid/ask candles from `data/campaign_002.sqlite3`
   (via `forex_bot.data.repositories.CandleRepo`) and emits Lean
   custom-data CSVs, preserving the 17:00-NY-aligned open timestamps.
   Verify the export against the CAMPAIGN_002 data-request hash.
5. **Run the local backtest:**
   ```bash
   lean backtest "<algorithm name>"
   ```
6. **Compare** the Lean trade list and equity curve against the
   committed CAMPAIGN_002 artifacts, using the tolerances in
   `docs/research/LEAN_PARITY_DESIGN.md` §10–11.
7. **Record every divergence** in `src/forex_bot/lean/parity_notes.md`
   (fill model, quote source, spread, financing, order timing, warmup,
   fees) — that file already exists for exactly this purpose.

## Expected outcome

- A PASS corroborates the bespoke engine and the CAMPAIGN_002 REJECT
  verdict.
- A FAIL localizes a bespoke-engine bug to fix.
- Either way: no strategy is approved, and the research freeze holds.
