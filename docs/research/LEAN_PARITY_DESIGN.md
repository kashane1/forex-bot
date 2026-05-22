# Lean Parity Design

**Date:** 2026-05-22 · **Branch:** `infra-research-foundation-001` · Phase 3

> **Status: DESIGN ONLY.** QuantConnect Lean is not installed in this
> repo and was **not run**. No cloud jobs, no paid QuantConnect
> services, no live execution. This document and the
> `research/lean_parity/` skeleton describe how a parity check *would*
> be built; running it is a future, human-initiated step.

This builds on the existing Lean boundary notes in
`src/forex_bot/lean/README.md` and `src/forex_bot/lean/parity_notes.md`.

## 1. Purpose

The backtest engine in `src/forex_bot/backtesting/` is **bespoke**.
Every campaign verdict (CAMPAIGN_002–009, all REJECT) depends on that
engine being correct. If the engine had a systematic bug, the verdicts
could be wrong in either direction.

Lean parity re-implements **one** historical campaign in an independent
engine (QuantConnect Lean) and compares the results. It is **verification
infrastructure**, not a search for a trading edge:

- A **PASS** raises confidence that the bespoke engine — and therefore
  the REJECT verdicts — are sound.
- A **FAIL** localizes a discrepancy and points at an engine bug worth
  fixing.

Either outcome is valuable. Neither outcome can approve a strategy.

## 2. What Lean parity CAN validate

- That the bespoke engine's **trade entries and exits** for a given
  strategy + data are not grossly wrong (right bars, right direction).
- That the **strategy indicator logic** (EMA cross, Donchian breakout,
  ATR stop) produces the same signals in an independent implementation.
- That the **aggregate metrics** (trade count, return, expectancy) are
  in the same ballpark.
- That **stop / trailing-stop / time-stop exits** fire at comparable
  prices and bars.

## 3. What Lean parity CANNOT validate

- **Whether a strategy has edge.** Both engines will agree CAMPAIGN_002
  is REJECT — that is the point. Parity does not make anything tradable.
- **Financing.** Financing is unmodeled here and modeled differently (or
  not at all) in a Lean local backtest. Parity deliberately excludes it.
- **The RiskEngine.** Our `RiskEngine` (custom sizing, spread filter,
  session filter, margin, correlation) is bespoke. Lean has its own risk
  framework. They will **not** match exactly — see §8.
- **Live execution realism.** Neither engine is a live broker.

## 4. First parity target — CAMPAIGN_002 H4 baseline

Recommended first (and only, for v1) target: **the CAMPAIGN_002 H4
`trend_following 0.1.0` baseline.** Rationale:

- **Simplest strategy** — EMA(50/200) regime + Donchian(20) breakout +
  ATR(14) stop. No regime sub-models, no z-scores.
- **Already REJECT** — the stakes are low. A small parity discrepancy
  cannot flip a "promote" decision, because there is no promotion.
- **Real OANDA data**, well documented in
  `backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md`.
- A single instrument (EUR_USD H4) is enough for a first parity run;
  expand to the full universe only if the single-pair run passes.

The precise replication spec is `research/lean_parity/campaign_002_h4_spec.md`.

## 5. Required data alignment

Both engines must replay the **identical candles**:

- Same instrument(s), H4 timeframe, same 2020–2026 window.
- Export the OANDA H4 bid/ask candles from `data/campaign_002.sqlite3`
  into Lean's custom-data format. The exported OHLC and timestamps must
  be byte-identical to what the bespoke engine consumed — verify with
  the `compute_data_request_hash` value recorded in the CAMPAIGN_002
  artifacts.
- **No re-fetch.** Parity uses the same stored candles, not a fresh
  OANDA pull, so any data difference cannot confound the comparison.

## 6. Candle timestamp alignment

The single most likely source of false divergence:

- OANDA H4 candles in this repo are aligned to **17:00 New York**
  (`daily_alignment: 17`). Each candle's `time` is its **open**.
- Lean's built-in FX data is UTC-aligned and hourly/daily. A naive Lean
  import will **not** land on the same 4-hour boundaries.
- The Lean side must consume the **exported H4 candles as custom data**,
  preserving the 17:00-NY-aligned open timestamps — not resample Lean's
  own hourly data.
- Confirm the first and last bar timestamps match between engines before
  comparing anything else.

## 7. Spread / fill assumptions

- The bespoke engine fills bid/ask-aware: a long enters at the ask, a
  short at the bid, plus a `FillModel` (fixed slippage pips + a spread
  multiplier). CAMPAIGN_002 base regime: ~0.2–0.3 pip fixed slippage,
  0.5× spread multiplier.
- Lean's default fill model is mid-price with its own slippage model.
- For parity, the Lean algorithm must either replicate the bespoke
  fill model or accept — and **document** — a known divergence. v1
  recommendation: configure Lean with the simplest comparable model and
  treat fill price as a *tolerance* comparison (§9), not exact.

## 8. Stop / trailing-stop behaviour

The bespoke engine applies three exits — replicate all three:

1. **Hard ATR stop** — `atr_stop_multiple × ATR(14)` from entry.
2. **Trailing stop** — `trailing_stop_atr_multiple × ATR` ratcheting on
   each completed bar's close (long: stop only moves up).
3. **Time stop** — close after `max_bars_in_trade` bars.

Same-bar precedence: the adverse stop is checked before any favourable
exit. The Lean algorithm must use the same precedence or divergences
will accumulate on volatile bars.

## 9. RiskEngine mismatch risks

The bespoke `RiskEngine` does position sizing (0.25% risk), a
spread-to-ATR filter, a session/rollover filter, margin checks, and
correlation limits. Lean will not reproduce these exactly.

**v1 decision:** parity compares **strategy signals + fill/exit
mechanics**, *not* full RiskEngine behaviour. The Lean algorithm should
size positions with a simple fixed-risk rule and **skip** the spread /
session / correlation filters. Consequently:

- Rejection counts will **not** match — expected, documented, excluded
  from pass/fail.
- Compare the trades that *both* engines would have taken (i.e. the
  bespoke engine's *accepted* signals), bar-for-bar.

Full RiskEngine parity is explicitly **out of scope** for v1 and noted
as possible future work.

## 10. Expected tolerance ranges

Floating-point, fill-model, and indicator-seeding differences make an
exact match unrealistic. Illustrative tolerances (set firm values when
the run is actually built):

| quantity | tolerance |
|---|---|
| trade entry bar | same bar (≥ 95% of trades) |
| entry / exit price | within ~1 pip |
| trade count | within ±5% |
| total return | within ±0.5 percentage points |
| expectancy (R) | within ±0.03 R |

## 11. Pass / fail criteria

- **PASS** — ≥ 95% of trade entries land on the same bar in both
  engines, all aggregate metrics fall inside the §10 tolerances, and
  both engines reach the same verdict (REJECT). The bespoke engine is
  corroborated.
- **FAIL** — systematic divergence outside tolerance. Do **not** dismiss
  it: localize the discrepancy (indicator seeding, fill model, stop
  precedence, timestamp alignment) and treat it as a bespoke-engine bug
  to fix. Re-run after the fix.
- A parity result **never** approves a strategy. It only validates the
  measurement instrument.

## 12. Why not run it now

Lean's local backtester is free (open-source `lean` CLI + Docker), but
this sprint scopes Phase 3 to **design and a skeleton**. Running Lean
requires installing the toolchain and exporting data — a deliberate,
human-initiated step. Setup instructions are in
`research/lean_parity/README.md`. No paid QuantConnect functionality is
required for the local parity backtest described here.
