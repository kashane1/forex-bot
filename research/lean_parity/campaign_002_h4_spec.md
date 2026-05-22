# CAMPAIGN_002 H4 — Lean parity replication spec

**Status: SPEC ONLY.** This describes how to replicate the CAMPAIGN_002
H4 `trend_following` baseline in QuantConnect Lean. It was not executed
(Lean is not installed in this repo). See
`docs/research/LEAN_PARITY_DESIGN.md`.

## Authoritative sources

These are the source of truth — copy parameters from them, not from
memory:

- **Strategy implementation:** `src/forex_bot/strategies/trend_following.py`
- **Frozen baseline parameters:** the `strategy.trend_following` block of
  `configs/paper.yaml` (`trend_following 0.1.0`).
- **Campaign report (target numbers):**
  `backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md`.
- **Stored candles:** `data/campaign_002.sqlite3` (real OANDA practice
  H4 bid/ask, 7 majors, 2020–2026).

## Strategy parameters (`trend_following 0.1.0`)

From the frozen baseline (`configs/paper.yaml`) — confirm against the
exact CAMPAIGN_002 config before running:

| parameter | value |
|---|---|
| `ema_fast` / `ema_slow` | 50 / 200 |
| `donchian_lookback` | 20 |
| `atr_lookback` | 14 |
| `atr_stop_multiple` | 2.5 |
| `trailing_stop_atr_multiple` | 2.0 (per CAMPAIGN_002 config — verify) |
| `max_bars_in_trade` | 80 |
| `min_atr_pips` | per-pair (EUR_USD 5.0, USD_JPY 8.0, GBP_USD 6.0, AUD_USD 5.0, USD_CAD 5.0) |
| `risk_per_trade_pct` | 0.25 |
| timeframe | H4 (17:00 NY aligned) |

## Signal logic to replicate

At each completed H4 bar (completed bars only, no lookahead):

1. **Trend regime:** EMA(50) vs EMA(200) — long-only regime when
   EMA50 > EMA200, short-only when EMA50 < EMA200.
2. **Entry:** a Donchian(20) breakout in the regime direction — close
   breaks the prior 20-bar high (long) / low (short).
3. **Volatility floor:** skip if ATR(14) in pips is below the pair's
   `min_atr_pips`.
4. **Stop:** hard stop at `2.5 × ATR(14)` from entry.
5. **Trailing stop:** ratchet at `2.0 × ATR` on each completed bar.
6. **Time stop:** exit after 80 bars.

Match the bespoke engine's same-bar exit precedence: adverse stop first,
then favourable exit, then time stop.

## Data

- **Use the stored candles**, not a fresh OANDA fetch. Export the H4
  bid/ask candles for the target instrument(s) from
  `data/campaign_002.sqlite3` via
  `forex_bot.data.repositories.CandleRepo`, into Lean custom-data CSVs.
- Preserve each candle's **17:00-NY-aligned open timestamp**.
- Verify the export reproduces the CAMPAIGN_002 data-request hash.
- Start with **EUR_USD only**; expand to the full universe only if the
  single-pair parity passes.

## Cost model

- CAMPAIGN_002 base regime: fixed slippage ~0.2–0.3 pips, spread
  multiplier 0.5×, bid/ask-aware fills (long enters at ask, short at
  bid). Configure the closest comparable Lean fill model; treat fill
  price as a tolerance comparison.
- Financing: **excluded** from parity (unmodeled in both — see
  `docs/research/FINANCING_MODEL_DESIGN.md`).
- RiskEngine spread/session/correlation filters: **excluded** from
  parity (see design doc §9). Size with a simple 0.25%-risk rule and
  compare only the bespoke engine's *accepted* trades.

## What to compare, and tolerances

Compare the Lean output against the committed CAMPAIGN_002 artifacts:

- trade entry bars (≥ 95% on the same bar),
- entry / exit prices (within ~1 pip),
- trade count (±5%), total return (±0.5 pp), expectancy R (±0.03),
- the verdict — both must read REJECT.

Full tolerances and pass/fail rules: `docs/research/LEAN_PARITY_DESIGN.md`
§10–11. Record every divergence in `src/forex_bot/lean/parity_notes.md`.

## Lean algorithm skeleton

Illustrative starting point — create this as a Python algorithm inside a
Lean workspace (`lean init`). It is **not** committed as a `.py` file in
this repo because it depends on Lean's `AlgorithmImports` runtime, which
is not installed here.

```python
# trend_following_c002_parity.py  — create inside a Lean workspace
from AlgorithmImports import *


class TrendFollowingC002Parity(QCAlgorithm):
    """Independent re-implementation of CAMPAIGN_002 H4 trend_following
    0.1.0, for parity verification against src/forex_bot/backtesting/.
    Verification only — this is an already-REJECT strategy."""

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2026, 5, 20)
        self.SetCash(500)
        # Consume the EXPORTED CAMPAIGN_002 H4 candles as custom data,
        # preserving 17:00-NY-aligned open timestamps. Do NOT use Lean's
        # native FX feed — its bar boundaries will not match.
        # self.symbol = self.AddData(Campaign002H4, "EUR_USD", Resolution.Daily).Symbol

        self.ema_fast = self.EMA("EUR_USD", 50)
        self.ema_slow = self.EMA("EUR_USD", 200)
        self.atr = self.ATR("EUR_USD", 14)
        # Donchian(20), bars-held counter, and the three exits are
        # implemented in OnData. Warm up 200 bars before the first entry.
        self.SetWarmUp(200)

    def OnData(self, data):
        if self.IsWarmingUp:
            return
        # TODO: EMA(50/200) regime gate
        # TODO: Donchian(20) breakout entry in the regime direction
        # TODO: min_atr_pips volatility floor
        # TODO: 2.5xATR hard stop, 2.0xATR trailing stop, 80-bar time stop
        # TODO: same-bar exit precedence — adverse stop first
        # TODO: 0.25%-risk position sizing
        ...
```

## Target numbers (from the CAMPAIGN_002 report)

The bespoke engine's CAMPAIGN_002 H4 trend baseline verdict was
**REJECT** at roughly **−0.085 R expectancy, profit factor 0.75,
−1.02% return**. A passing parity run reproduces figures within the §10
tolerances and the same REJECT verdict. Read the exact per-split and
per-pair numbers from `backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md`.
