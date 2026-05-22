# Lean Parity Algorithm — Implementation Notes

**Date:** 2026-05-22 · **Branch:** `infra-lean-parity-run-001` · Phase 2
**Algorithm:** `research/lean_parity/algorithms/campaign_002_h4_baseline/main.py`

What the Lean parity algorithm implements faithfully, what it
approximates, where Lean's mechanics differ from the bespoke engine,
and whether it is ready to run. Read alongside
`docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md`.

> Verification only. `strategy_evidence: false`. CAMPAIGN_002 is REJECT.

## Implemented faithfully

Ported directly from `trend_following.py` / `engine.py` / `fills.py` /
`sizing.py`:

- **Entry:** EMA(50) vs EMA(200) regime + Donchian(20) **prior-bar**
  breakout (`close > max(high[t-20..t-1])` long / mirror short).
- **Donchian excludes the current bar** — a manual `RollingWindow` of
  prior completed-bar mid highs/lows, pushed *after* the signal is
  evaluated. Lean's built-in `DonchianChannel` includes the forming bar
  and is deliberately **not** used.
- **min_atr_pips** is `{}` for CAMPAIGN_002 → the ATR volatility floor
  is disabled. **ADX gate** is unset → skipped. Both match the
  `0.1.0-baseline-frozen` config.
- **Initial stop:** `mid_close ∓ ATR×2.0`.
- **Trailing stop:** `bid_close − ATR×2.0` (long) / `ask_close + ATR×2.0`
  (short), ratcheting only in the favourable direction.
- **Exit precedence:** adverse stop first (fill **at the stop price**),
  then the 240-bar time stop. No take-profit, no opposite-signal exit —
  matches `trend_following`.
- **Fill model:** long `ask + slip`, short `bid − slip`,
  `slip = max(0.2 pips, spread×0.5)`.
- **Fill timing:** `signal_bar_close` — entry at the signal bar's own
  close.
- **Sizing:** fixed-fractional 0.25%-risk; `units = floor(raw_units)`.
- **PnL conversion:** quote==USD → direct; base==USD → `÷ exit_price`.
- **Indicators on mid prices; fills on bid/ask.**
- **One position per instrument**; per-symbol 220-bar warmup.
- Indicator math uses Lean's own `ExponentialMovingAverage` and
  `AverageTrueRange(Wilders)` — a genuine independent implementation.

## Approximated (commented `# APPROX:` in the code)

- **base==USD pip value:** `sizing.size_position` derives the pip value
  from the instrument's own mid quote; the algorithm uses `pip / entry`
  (entry ≈ mid). Sub-pip effect on units for USD_JPY / USD_CAD / USD_CHF.
- **Custom-data resolution:** the H4 series is declared
  `Resolution.Daily` — Lean has no native H4 custom-data resolution; the
  4-hour bars are consumed as discrete custom-data points. Needs
  verification that Lean does not resample them.
- **Exit fills exactly at the stop price** — this is faithful *to the
  bespoke engine*, which does the same; a real Lean stop order would
  fill at stop-or-worse.

## Where Lean's mechanics differ from the bespoke engine

- **Order system not used.** Lean's native market orders fill at the
  next data point, which would behave like `next_bar_open`, not
  `signal_bar_close`. To keep the timing faithful, the algorithm does
  **not** route through Lean's `Portfolio` / order system — it steps the
  trade bookkeeping (entry, trailing, exits, PnL, compounding equity)
  explicitly, mirroring `backtesting/engine.py`. Lean's independent
  contribution is therefore the **custom-data ingestion** and the
  **EMA / ATR indicator math**; the trade mechanics are a re-step.
  A future variant could use Lean's order system to widen the
  independent surface, accepting the documented fill-timing offset.
- **Indicator seeding:** Lean's EMA / Wilder smoothers seed the first
  bars differently from pandas `ewm(adjust=False)`. The effect decays
  well before the 220-bar warmup ends but can shift the very first
  eligible signals.
- **Decimal vs double:** the bespoke engine uses `Decimal`; Lean uses
  `double`. Expect sub-pip differences in fills and PnL.

## Expected mismatch causes for a first run

1. The custom-data `GetSource` path — almost certainly needs adjusting
   to the actual Lean workspace / data-folder layout.
2. `OnData` slice semantics for seven custom-data symbols — whether all
   symbols deliver each slice and how bars align in time.
3. Indicator readiness vs the explicit `bar_count > 220` warmup.
4. The `Resolution.Daily` declaration for 4-hour bars.

## Ready to run?

**Not yet validated.** `main.py` is a complete, best-effort faithful
implementation, but it was **authored offline and has not been executed
against Lean**. A first local `lean backtest` is expected to need a
debugging iteration (custom-data path, resolution, slice semantics).
Until it has run and its output has been sanity-checked, its numbers
must **not** be treated as a trustworthy parity result.

**Status: ready for a first local Lean run + debugging iteration
(Phase 4); not yet a validated parity algorithm.**
