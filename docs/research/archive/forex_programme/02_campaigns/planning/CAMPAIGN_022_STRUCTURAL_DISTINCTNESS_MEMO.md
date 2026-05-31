# CAMPAIGN_022 — Structural Distinctness Memo

**Date:** 2026-05-27
**Campaign:** CAMPAIGN_022 · `h4_h1_pullback_resolution_entry 0.1.0-c022`
**Conclusion:** **STRUCTURALLY DISTINCT** — proceed with scaffold (not blocked)

## Core distinction — pullback resolution vs "all-green" alignment

C020 (REJECT) and C021 both require **same-direction alignment across every timeframe
simultaneously**. C022 inverts the role of the intermediate timeframe:

| dimension | CAMPAIGN_021 (`lower_timeframe_mtf_confluence_entry`) | CAMPAIGN_022 |
|---|---|---|
| top timeframe | D1AGG (synthetic daily) | **H4** (no daily layer) |
| timeframe count | 4 (D1AGG + H4 + H1 + M15) | **3** (H4 + H1 + M15) |
| H1 role | must be **aligned bullish/bearish** (third green light) | must be in a **counter-trend pullback that holds** (NOT aligned) |
| H4 trend | single line: `close vs EMA50` | **3-vote score** (price/EMA50, EMA20/EMA50, EMA50 slope) + ADX≥20 gate |
| entry logic | all-green stack + M15 reclaim | H4 bias + H1 pullback **resolving back** into bias + M15 reclaim |
| data provenance | M15/H1/H4 m1_derived + **native H4→D1AGG** | **three m1_derived layers only**; daily-layer keys rejected |
| C-verdict | not executed | not executed; distinct hypothesis |

C022 is **not** a parameter retune of C021: it removes a whole timeframe, redefines the
H1 gate from *agreement* to *holding pullback*, and replaces the H4 single-line trend with
a multi-factor score. The entry only fires when the lower timeframe **resolves back** into
H4 structure — the opposite of "everything is green at once."

## Why not C020

C020 executed on **H4** with an H4 pullback trigger and a D1AGG trend gate. C022 executes
on **M15**, has no daily layer, and gates on an **H1 holding-pullback** state that C020
never modeled.

## Why not mean-reversion (C008 / C018 / C019)

Mean-reversion fades extension in low-ADX ranges with z-score / midline exits. C022 is
**pro-trend**: it requires an ADX-confirmed H4 trend and trades the *continuation* after a
pullback, with a hard ATR stop + M15 time stop only — no z-exit, no thesis-invalidation
stack.

## Why not C012 regime switcher

C012 uses a D1AGG ATR-percentile regime + short H4 momentum. C022 has no ATR-percentile
regime and no daily layer; its regime signal is the H4 multi-factor trend score.

## Why not C013 / C014 / C015 / C016 / C017 / C011

- **C013:** cross-pair currency ranking — C022 is single-pair structure.
- **C014:** calendar event windows — C022 has no event calendar.
- **C015:** failed-breakout fade — C022 requires an aligned H4 trend + pullback resolution,
  not a range false-break fade.
- **C016/C017:** weekly bar logic — C022 is intraday M15 with H4/H1 context.
- **C011:** random null — C022 is a directional structure hypothesis.

## Why the pullback-resolution hypothesis is worth testing

C020 was validation-positive but train-negative under H4 `next_bar_open`, consistent with
**late entries** on a slow bar. C021 retested on M15 but kept the strict all-green gate,
which the MTF literature flags as the *too-late* failure mode. C022 tests whether timing
the entry to the moment a counter-trend H1 pullback **resolves** back into the H4 trend
improves entry location — capturing the move earlier than waiting for full alignment.

## Falsification criteria (future execution only)

- Train expectancy < 0 under `next_bar_open` with frozen parameters.
- Validation fails precommitted gates (PF, trade count, pair breadth, 2× cost stress).
- Does not beat deduped C011 null by +0.010R margin.
- Does not beat C021's recorded outcome head-to-head on the same universe/windows.
- Backtrader parity fails before any test lockbox.

## No strategy approved

`configs/approved_strategies.yaml` remains `approved: []`. CAMPAIGN_020 remains **REJECT**.
This memo does not change any prior verdict.
