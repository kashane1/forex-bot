# CAMPAIGN_004 — Pre-Commit Specification

**Written and committed BEFORE any CAMPAIGN_004 backtest is run.** It
fixes the strategy rules, every parameter, and the pass/fail gates so
that results cannot retro-justify the design. Nothing here may be
changed after seeing results; a changed rule is a new campaign.

Strategy version: **`volatility_breakout 0.1.0-c004`**.

## Why a new entry family

CAMPAIGN_002 and CAMPAIGN_003 established that the Donchian
trend-following *entry* (close beyond a channel, EMA-regime filtered)
has no positive edge on the real 2020-2026 majors, and that
conditioning *when* it fires (ADX gate) does not rescue it. CAMPAIGN_004
therefore tests a **different entry**: a breakout that fires
specifically *out of a volatility-compressed regime*, with **no EMA
trend filter**. Direction comes from the breakout itself.

## Rule definition

All rules use **completed bars only** and **prior-bar** channels — no
lookahead. Evaluated at the latest completed bar `t`.

### Compression (precondition)

- Compute **ATR-14** (Wilder) over the H4 series.
- The 60-bar window of ATR-14 values **ending at bar `t-1`** (the bar
  immediately before the breakout bar) defines the local volatility
  distribution.
- **Compression holds** iff `ATR14[t-1] <= P40` of that window, where
  `P40` is the 40th percentile.
- Measuring at `t-1` (not `t`) is deliberate: bar `t` is the expansion
  bar; its ATR will already have jumped. The regime *going into* the
  break must have been quiet.

### Breakout (trigger)

- Donchian channel over the **20 bars strictly before `t`**:
  `DH = max(high[t-20:t])`, `DL = min(low[t-20:t])`.
- **Long** iff `close[t] > DH`. **Short** iff `close[t] < DL`.
- Direction is the breakout direction. **No EMA 50/200 filter.**
- An entry fires only when compression (above) AND breakout both hold.

### Stop

- Initial stop = `2.0 × ATR14[t]` from the entry, on the loss side.
- The strategy emits `stop_price`; the production RiskEngine sizes the
  position. Stops are server-side-protective in spirit (require_stop_loss).

### Exit

**Chosen before viewing results: 2.0× ATR-14 trailing stop** (not a
fixed-R target). Plus a `max_bars_in_trade` time stop.

- Rationale: the trailing stop is already implemented and tested in the
  backtest engine; using it keeps CAMPAIGN_004 comparable to
  CAMPAIGN_002/003 (same exit machinery) and introduces no new,
  unvalidated exit code. A fixed-R target would be a second free
  parameter; we decline it.

### Session / spread filters

- Unchanged from prior campaigns — the production RiskEngine applies
  them: `session_filter` blocks rollover (16:45–17:15 NY), Friday close,
  Sunday open; `spread_filter` caps absolute spread per pair and the
  spread/ATR ratio at 8%.
- The RiskEngine is wired into the backtest (`mode="backtest"`); every
  rejected signal is exported to `*_risk_rejections.csv`.

## Parameters (frozen)

| parameter | value | why this value |
|---|---|---|
| `atr_lookback` | 14 | Standard Wilder ATR; same as every prior campaign — keeps the volatility measure comparable. |
| `breakout_lookback` | 20 | As suggested in the task brief. 20 H4 bars ≈ 3.3 trading days — a short-horizon channel appropriate for a *breakout* (vs the 200-bar trend horizon). |
| `compression_lookback` | **60** | **Deviation from the suggested 20, justified:** a 40th-percentile estimate needs a meaningful sample. 20 H4 bars (~3 days) is too thin to define "compressed vs normal" — the percentile would be dominated by 1–2 bars. 60 H4 bars ≈ 10 trading days is the minimum window for a stable percentile while remaining fully causal. The task brief explicitly permits different values "if you explain why before running." This is that explanation. |
| `compression_percentile` | 40.0 | As suggested. The breakout must come from the quieter 40% of recent volatility. |
| `atr_stop_multiple` | 2.0 | As suggested; identical to CAMPAIGN_002/003 so the stop is not a hidden variable in the cross-campaign comparison. |
| `trailing_stop_atr_multiple` | 2.0 | As suggested; trailing exit chosen over fixed-R (see Exit). |
| `max_bars_in_trade` | 120 | As suggested. 120 H4 bars = 20 trading days — a generous time stop so breakouts that work have room, but open-ended drift is capped. |
| `risk_per_trade_pct` | 0.25 | Unchanged from every prior campaign — risk policy. |
| universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF | 6 pairs. NZD_USD excluded on the same cost-structure basis as CAMPAIGN_003 (widest median spread). |
| timeframe | H4 only | H1's hourly ATR cannot clear real spreads (CAMPAIGN_002/003 finding). |

**No parameter is swept. No robustness grid runs unless the baseline
clears the minimum evidence gates.** A single fixed configuration.

## Data

Real OANDA practice H4 candles, **reused** from
`data/campaign_002.sqlite3`, only if the provenance raw/normalized
SHA256 hashes match the CAMPAIGN_002 report. No re-fetch unless hashes
fail to verify; **no synthetic fallback** — stop if real data is
unavailable.

## Splits (fixed)

- Train: 2020-01-01 → 2022-12-31
- Validation: 2023-01-01 → 2024-12-31
- Untouched test: 2025-01-01 → 2026-05-20
- Full descriptive: 2020-01-01 → 2026-05-20

Cost regimes: base, stress_15x (1.5× spread + 0.3 pip), stress_2x (2.0×
spread + 0.5 pip).

## Financing

Financing is **not** modeled in-engine — accurate historical financing
cannot be obtained (see `docs/financing_decision.md`, CAMPAIGN_004
investigation). The conservative stress model
[`src/forex_bot/financing.py`](../../src/forex_bot/financing.py) is
applied as an after-the-fact debit. **A passing financing stress test
does not lift the live blocker** — financing must be properly modeled
(H-09) before any live consideration. The best attainable CAMPAIGN_004
recommendation is PAPER-TRADE-ONLY.

## Pass / fail gates (pre-committed)

**REJECT** if any of:

- untouched-test expectancy ≤ 0 after base costs
- untouched-test profit factor < 1.05
- stress_2x expectancy ≤ 0
- financing-stressed untouched-test expectancy ≤ 0
- only one pair contributes positively on the untouched test
- untouched-test trade count too low to be meaningful (< 30)
- max drawdown breaches the 8% policy
- data provenance is ambiguous or RiskEngine parity incomplete

**PAPER-TRADE-ONLY** (the best possible outcome) only if ALL of:

- untouched-test expectancy > 0 after base costs
- profit factor ≥ 1.05
- stress_2x expectancy ≥ 0
- ≥ 2 pairs positive or near-breakeven on the untouched test
- financing-stressed expectancy not negative
- drawdown within the 8% policy
- RiskEngine parity complete, data provenance clean
- limitations explicitly documented

**Live trading is out of scope for CAMPAIGN_004 and will not be
recommended regardless of results.**

## Known overfitting risks

1. **`compression_lookback = 60` is a judgement call.** It was chosen
   on statistical grounds (stable percentile) before any run, not by
   tuning — but it is still a degree of freedom. It is not swept; if a
   future campaign wants to test sensitivity, that is a separate,
   explicitly-labelled optimization campaign.
2. **NZD_USD exclusion** is partly returns-correlated (it was the worst
   CAMPAIGN_002 pair). The structural spread/ATR rationale is sound;
   the residual leakage is acknowledged. The report shows the result is
   not carried by a single pair.
3. **Single timeframe / single config** keeps the degrees of freedom
   low — the main overfitting defence. There is no grid, no optimizer,
   no post-hoc parameter change.
4. The compression+breakout idea is a well-known pattern; the risk is
   *not* that it is exotic, but that 2020-2026 may not contain enough
   clean compression→expansion sequences for it to matter. The trade
   count and per-split consistency in the report address this.
