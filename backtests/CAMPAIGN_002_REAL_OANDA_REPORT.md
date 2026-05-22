# CAMPAIGN 002 — Trend Following Baseline on REAL OANDA Practice Data

> **DATA SOURCE: REAL OANDA practice candles** for 7 major FX pairs,
> 2020-01-01 → 2026-05-20, H4 and H1, fetched via the OANDA v20 REST API.
> Practice host: `https://api-fxpractice.oanda.com`. Token and account ID
> redacted throughout (see `src/forex_bot/logging_config.py`).

## Provenance

- **Generated at:** 2026-05-21T19:55:25.240486
- **Git commit:** `b733a4648e0c212a909de2e1f7975747a9eeb629` (`b733a4648e0c`)
- **Git working tree dirty:** **YES**
- **OANDA environment:** practice — token/account redacted
- **Config:** [`configs/campaign_002_real_oanda.yaml`](../configs/campaign_002_real_oanda.yaml)
- **Config hash:** `d536a9b06818197f9915de6224e0b8ae58e77abe2c6f3c19426338646fb077bf`
- **Data source:** real OANDA practice; per-instrument provenance below
- **Total backtest runs:** 665
- **RiskEngine wired in:** **YES** (all runs) (Task D)

### Per-fetch data provenance

| instrument | gran | source | candles | first | last | pages | raw_sha256 (12) | norm_sha256 (12) |
|---|---|---|---:|---|---|---:|---|---|
| EUR_USD | H4 | oanda-practice | 132 | 2020-01-01 | 2020-01-31 | 1 | `a8979803f958…` | `fa6ec46b7fbf…` |
| EUR_USD | H4 | oanda-practice | 9934 | 2020-01-01 | 2026-05-19 | 4 | `f56b30030f3a…` | `f5d1d1b19302…` |
| GBP_USD | H4 | oanda-practice | 9934 | 2020-01-01 | 2026-05-19 | 4 | `6ea9b168cf23…` | `2c751fec8b0e…` |
| USD_JPY | H4 | oanda-practice | 9935 | 2020-01-01 | 2026-05-19 | 4 | `568f4c6104e1…` | `64836ea0f08e…` |
| AUD_USD | H4 | oanda-practice | 9934 | 2020-01-01 | 2026-05-19 | 4 | `710f6aed5875…` | `7a19f3e957ea…` |
| USD_CAD | H4 | oanda-practice | 9934 | 2020-01-01 | 2026-05-19 | 4 | `9fe3b74d78c5…` | `dc04b583759e…` |
| USD_CHF | H4 | oanda-practice | 9934 | 2020-01-01 | 2026-05-19 | 4 | `46a0f6748c7d…` | `11b0a134792a…` |
| NZD_USD | H4 | oanda-practice | 9938 | 2020-01-01 | 2026-05-19 | 4 | `c7c38eb2225d…` | `c8724ce78e4c…` |
| EUR_USD | H1 | oanda-practice | 39728 | 2020-01-01 | 2026-05-20 | 16 | `e1de49269b0d…` | `238c9359c286…` |
| GBP_USD | H1 | oanda-practice | 39727 | 2020-01-01 | 2026-05-20 | 16 | `813c0e9198a7…` | `d684dcfaa1aa…` |
| USD_JPY | H1 | oanda-practice | 39729 | 2020-01-01 | 2026-05-20 | 16 | `6880c2ca591d…` | `a9f15e0ccd29…` |
| AUD_USD | H1 | oanda-practice | 39723 | 2020-01-01 | 2026-05-20 | 16 | `cb2bfceb62b9…` | `39c52820fd1d…` |
| USD_CAD | H1 | oanda-practice | 39729 | 2020-01-01 | 2026-05-20 | 16 | `dbea75eb1eab…` | `47f36d56f0bb…` |
| USD_CHF | H1 | oanda-practice | 39724 | 2020-01-01 | 2026-05-20 | 16 | `a4fffc567635…` | `bb07b935bbc2…` |
| NZD_USD | H1 | oanda-practice | 39732 | 2020-01-01 | 2026-05-20 | 16 | `275e0707f23f…` | `da92d788e6cf…` |

## Assumptions

- **Strategy:** `trend_following 0.1.0-baseline-frozen`. **Identical** to
  CAMPAIGN_001 (frozen before either campaign): EMA 50/200 direction
  filter, Donchian-20 breakout using prior bars only, ATR-14, 2.0×ATR
  initial stop, 2.0×ATR trailing stop in the favourable direction only,
  max one open position per instrument.
- **Risk:** 0.25% of equity per trade, sized via the production
  `RiskEngine.evaluate()` (Task D). Backtest mode skips only operational
  gates (trading_enabled, kill_switch, reconciled, pending_order_count);
  every strategy/risk gate (stop, spread, session, sizing, exposure,
  margin) runs identically to live.
- **Fills:** bid for long exits / short entries, ask for long entries /
  short exits; `fixed_slippage_pips` and `spread_slippage_multiplier`
  applied in the unfavourable direction.
- **PnL → account currency (Task E):** quote-currency PnL is converted
  to USD using the exit price when `base == USD` (USD_JPY, USD_CAD,
  USD_CHF). For pairs where `quote == USD` (EUR_USD, GBP_USD, AUD_USD,
  NZD_USD), PnL is already in USD. Cross pairs without a runtime
  conversion quote would raise loudly; the campaign universe contains
  none of these.
- **Financing / rollover (Task F):** **NOT modeled** in the PnL stream.
  Treated as a blocker for any paper-to-live promotion. See
  [`docs/financing_decision.md`](../docs/financing_decision.md) for the
  rationale and the conservative stress estimate that should be applied
  before any operational decision.
- **Universe:** EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD.
- **Timeframes:** H4 primary, H1 secondary.
- **Splits:** train 2020-01-01 → 2022-12-31, validation 2023-01-01 →
  2024-12-31, untouched test 2025-01-01 → 2026-05-20, full 2020-01-01 →
  2026-05-20.
- **Cost regimes:** base (×0.5 spread, 0.2 pip slip), stress_15x (×1.5,
  0.3), stress_2x (×2.0, 0.5).

## Known limitations

1. **Financing unmodeled** — blocker for live promotion (see Task F doc).
2. **No real practice fills** — backtest fill model approximates broker
   behavior; no live broker dry-run yet.
3. **Single-position-at-a-time** — matches the v0 risk policy but
   leaves diversification benefits on the table.
4. **Max-bars-in-trade 240** chosen before viewing results; not swept.
5. **Practice-account data may differ from live in spreads / slippage**
   patterns during stress events; OANDA's practice fills are
   simulated. Treat results as a research baseline.

## Data audit

# Data audit

## Audit: EUR_USD H4

- Requested window: `2020-01-01 00:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- First/last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-19 21:00:00+00:00`
- Candle count: **9931** (complete=9931, incomplete=0)
- Bid availability: **9931/9931**
- Ask availability: **9931/9931**
- Median spread (pips): 1.50
- p95 spread (pips): 2.50
- Duplicate timestamps: **0**
- Missing intervals (non-weekend): **4**
- Weekend gaps: **333**
- Abnormal spreads (> 5× median): **107**
- Clean: **False**

### Missing intervals (sample)
- `2024-12-24T18:00:00+00:00` → `2024-12-25T22:00:00+00:00` (6 bars)
- `2024-12-31T18:00:00+00:00` → `2025-01-01T22:00:00+00:00` (6 bars)
- `2025-12-24T18:00:00+00:00` → `2025-12-25T22:00:00+00:00` (6 bars)
- `2025-12-31T18:00:00+00:00` → `2026-01-01T22:00:00+00:00` (6 bars)


### Abnormal spreads (sample)
- `2020-01-03T18:00:00+00:00` — 10.00 pips
- `2020-01-07T18:00:00+00:00` — 10.00 pips
- `2020-01-08T18:00:00+00:00` — 7.70 pips
- `2020-01-10T18:00:00+00:00` — 10.00 pips
- `2020-01-23T18:00:00+00:00` — 10.00 pips
- `2020-01-31T18:00:00+00:00` — 8.20 pips
- `2020-02-03T18:00:00+00:00` — 10.00 pips
- `2020-02-17T18:00:00+00:00` — 7.80 pips

_(+99 more)_
## Audit: GBP_USD H4

- Requested window: `2020-01-01 00:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- First/last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-19 21:00:00+00:00`
- Candle count: **9931** (complete=9931, incomplete=0)
- Bid availability: **9931/9931**
- Ask availability: **9931/9931**
- Median spread (pips): 1.90
- p95 spread (pips): 6.00
- Duplicate timestamps: **0**
- Missing intervals (non-weekend): **4**
- Weekend gaps: **333**
- Abnormal spreads (> 5× median): **174**
- Clean: **False**

### Missing intervals (sample)
- `2024-12-24T18:00:00+00:00` → `2024-12-25T22:00:00+00:00` (6 bars)
- `2024-12-31T18:00:00+00:00` → `2025-01-01T22:00:00+00:00` (6 bars)
- `2025-12-24T18:00:00+00:00` → `2025-12-25T22:00:00+00:00` (6 bars)
- `2025-12-31T18:00:00+00:00` → `2026-01-01T22:00:00+00:00` (6 bars)


### Abnormal spreads (sample)
- `2020-01-03T18:00:00+00:00` — 10.90 pips
- `2020-01-10T18:00:00+00:00` — 10.90 pips
- `2020-01-17T18:00:00+00:00` — 11.60 pips
- `2020-01-24T18:00:00+00:00` — 14.00 pips
- `2020-02-07T18:00:00+00:00` — 15.00 pips
- `2020-02-21T18:00:00+00:00` — 15.00 pips
- `2020-02-28T18:00:00+00:00` — 13.40 pips
- `2020-03-13T17:00:00+00:00` — 15.00 pips

_(+166 more)_
## Audit: USD_JPY H4

- Requested window: `2020-01-01 00:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- First/last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-19 21:00:00+00:00`
- Candle count: **9932** (complete=9932, incomplete=0)
- Bid availability: **9932/9932**
- Ask availability: **9932/9932**
- Median spread (pips): 1.60
- p95 spread (pips): 4.10
- Duplicate timestamps: **0**
- Missing intervals (non-weekend): **4**
- Weekend gaps: **333**
- Abnormal spreads (> 5× median): **304**
- Clean: **False**

### Missing intervals (sample)
- `2024-12-24T18:00:00+00:00` → `2024-12-25T22:00:00+00:00` (6 bars)
- `2024-12-31T18:00:00+00:00` → `2025-01-01T22:00:00+00:00` (6 bars)
- `2025-12-24T18:00:00+00:00` → `2025-12-25T22:00:00+00:00` (6 bars)
- `2025-12-31T18:00:00+00:00` → `2026-01-01T22:00:00+00:00` (6 bars)


### Abnormal spreads (sample)
- `2020-01-02T18:00:00+00:00` — 10.00 pips
- `2020-01-03T18:00:00+00:00` — 10.00 pips
- `2020-01-16T18:00:00+00:00` — 8.30 pips
- `2020-01-17T18:00:00+00:00` — 10.00 pips
- `2020-01-31T18:00:00+00:00` — 10.00 pips
- `2020-02-07T18:00:00+00:00` — 10.00 pips
- `2020-02-21T18:00:00+00:00` — 10.00 pips
- `2020-02-28T18:00:00+00:00` — 10.00 pips

_(+296 more)_
## Audit: AUD_USD H4

- Requested window: `2020-01-01 00:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- First/last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-19 21:00:00+00:00`
- Candle count: **9931** (complete=9931, incomplete=0)
- Bid availability: **9931/9931**
- Ask availability: **9931/9931**
- Median spread (pips): 1.40
- p95 spread (pips): 2.90
- Duplicate timestamps: **0**
- Missing intervals (non-weekend): **4**
- Weekend gaps: **333**
- Abnormal spreads (> 5× median): **184**
- Clean: **False**

### Missing intervals (sample)
- `2024-12-24T18:00:00+00:00` → `2024-12-25T22:00:00+00:00` (6 bars)
- `2024-12-31T18:00:00+00:00` → `2025-01-01T22:00:00+00:00` (6 bars)
- `2025-12-24T18:00:00+00:00` → `2025-12-25T22:00:00+00:00` (6 bars)
- `2025-12-31T18:00:00+00:00` → `2026-01-01T22:00:00+00:00` (6 bars)


### Abnormal spreads (sample)
- `2020-01-03T18:00:00+00:00` — 10.90 pips
- `2020-01-15T18:00:00+00:00` — 13.20 pips
- `2020-01-31T18:00:00+00:00` — 15.00 pips
- `2020-02-27T18:00:00+00:00` — 7.40 pips
- `2020-02-28T18:00:00+00:00` — 15.00 pips
- `2020-03-06T18:00:00+00:00` — 15.00 pips
- `2020-03-09T17:00:00+00:00` — 15.00 pips
- `2020-03-13T17:00:00+00:00` — 15.00 pips

_(+176 more)_
## Audit: USD_CAD H4

- Requested window: `2020-01-01 00:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- First/last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-19 21:00:00+00:00`
- Candle count: **9931** (complete=9931, incomplete=0)
- Bid availability: **9931/9931**
- Ask availability: **9931/9931**
- Median spread (pips): 1.90
- p95 spread (pips): 4.50
- Duplicate timestamps: **0**
- Missing intervals (non-weekend): **4**
- Weekend gaps: **333**
- Abnormal spreads (> 5× median): **141**
- Clean: **False**

### Missing intervals (sample)
- `2024-12-24T18:00:00+00:00` → `2024-12-25T22:00:00+00:00` (6 bars)
- `2024-12-31T18:00:00+00:00` → `2025-01-01T22:00:00+00:00` (6 bars)
- `2025-12-24T18:00:00+00:00` → `2025-12-25T22:00:00+00:00` (6 bars)
- `2025-12-31T18:00:00+00:00` → `2026-01-01T22:00:00+00:00` (6 bars)


### Abnormal spreads (sample)
- `2020-01-03T18:00:00+00:00` — 10.00 pips
- `2020-01-24T18:00:00+00:00` — 10.00 pips
- `2020-02-14T18:00:00+00:00` — 10.00 pips
- `2020-02-21T18:00:00+00:00` — 10.00 pips
- `2020-02-28T18:00:00+00:00` — 10.00 pips
- `2020-03-06T18:00:00+00:00` — 10.00 pips
- `2020-03-13T17:00:00+00:00` — 10.00 pips
- `2020-03-20T17:00:00+00:00` — 10.00 pips

_(+133 more)_
## Audit: USD_CHF H4

- Requested window: `2020-01-01 00:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- First/last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-19 21:00:00+00:00`
- Candle count: **9931** (complete=9931, incomplete=0)
- Bid availability: **9931/9931**
- Ask availability: **9931/9931**
- Median spread (pips): 1.70
- p95 spread (pips): 4.10
- Duplicate timestamps: **0**
- Missing intervals (non-weekend): **4**
- Weekend gaps: **333**
- Abnormal spreads (> 5× median): **165**
- Clean: **False**

### Missing intervals (sample)
- `2024-12-24T18:00:00+00:00` → `2024-12-25T22:00:00+00:00` (6 bars)
- `2024-12-31T18:00:00+00:00` → `2025-01-01T22:00:00+00:00` (6 bars)
- `2025-12-24T18:00:00+00:00` → `2025-12-25T22:00:00+00:00` (6 bars)
- `2025-12-31T18:00:00+00:00` → `2026-01-01T22:00:00+00:00` (6 bars)


### Abnormal spreads (sample)
- `2020-01-02T18:00:00+00:00` — 11.00 pips
- `2020-01-03T18:00:00+00:00` — 8.60 pips
- `2020-01-06T18:00:00+00:00` — 8.70 pips
- `2020-01-09T18:00:00+00:00` — 8.70 pips
- `2020-01-13T18:00:00+00:00` — 12.50 pips
- `2020-01-16T18:00:00+00:00` — 15.10 pips
- `2020-01-17T18:00:00+00:00` — 11.10 pips
- `2020-01-20T18:00:00+00:00` — 13.10 pips

_(+157 more)_
## Audit: NZD_USD H4

- Requested window: `2020-01-01 00:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- First/last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-19 21:00:00+00:00`
- Candle count: **9935** (complete=9935, incomplete=0)
- Bid availability: **9935/9935**
- Ask availability: **9935/9935**
- Median spread (pips): 2.50
- p95 spread (pips): 5.30
- Duplicate timestamps: **0**
- Missing intervals (non-weekend): **4**
- Weekend gaps: **333**
- Abnormal spreads (> 5× median): **188**
- Clean: **False**

### Missing intervals (sample)
- `2024-12-24T18:00:00+00:00` → `2024-12-25T22:00:00+00:00` (6 bars)
- `2024-12-31T18:00:00+00:00` → `2025-01-01T22:00:00+00:00` (6 bars)
- `2025-12-24T18:00:00+00:00` → `2025-12-25T22:00:00+00:00` (6 bars)
- `2025-12-31T18:00:00+00:00` → `2026-01-01T22:00:00+00:00` (6 bars)


### Abnormal spreads (sample)
- `2020-01-10T18:00:00+00:00` — 20.90 pips
- `2020-01-17T18:00:00+00:00` — 20.90 pips
- `2020-01-23T18:00:00+00:00` — 13.90 pips
- `2020-01-24T18:00:00+00:00` — 14.50 pips
- `2020-01-27T18:00:00+00:00` — 20.90 pips
- `2020-01-30T18:00:00+00:00` — 20.90 pips
- `2020-01-31T18:00:00+00:00` — 20.90 pips
- `2020-02-28T18:00:00+00:00` — 20.90 pips

_(+180 more)_

---

# Data audit

## Audit: EUR_USD H1

- Requested window: `2020-01-01 00:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- First/last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- Candle count: **39713** (complete=39713, incomplete=0)
- Bid availability: **39713/39713**
- Ask availability: **39713/39713**
- Median spread (pips): 1.50
- p95 spread (pips): 2.60
- Duplicate timestamps: **0**
- Missing intervals (non-weekend): **6**
- Weekend gaps: **333**
- Abnormal spreads (> 5× median): **245**
- Clean: **False**

### Missing intervals (sample)
- `2022-05-12T05:00:00+00:00` → `2022-05-12T08:00:00+00:00` (2 bars)
- `2024-05-20T14:00:00+00:00` → `2024-05-20T17:00:00+00:00` (2 bars)
- `2024-12-24T21:00:00+00:00` → `2024-12-25T22:00:00+00:00` (24 bars)
- `2024-12-31T21:00:00+00:00` → `2025-01-01T22:00:00+00:00` (24 bars)
- `2025-12-24T21:00:00+00:00` → `2025-12-25T22:00:00+00:00` (24 bars)
- `2025-12-31T21:00:00+00:00` → `2026-01-01T22:00:00+00:00` (24 bars)


### Abnormal spreads (sample)
- `2020-01-03T21:00:00+00:00` — 10.00 pips
- `2020-01-07T21:00:00+00:00` — 10.00 pips
- `2020-01-08T21:00:00+00:00` — 7.70 pips
- `2020-01-10T21:00:00+00:00` — 10.00 pips
- `2020-01-23T21:00:00+00:00` — 10.00 pips
- `2020-01-31T21:00:00+00:00` — 8.20 pips
- `2020-02-03T21:00:00+00:00` — 10.00 pips
- `2020-02-17T21:00:00+00:00` — 7.80 pips

_(+237 more)_
## Audit: GBP_USD H1

- Requested window: `2020-01-01 00:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- First/last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- Candle count: **39712** (complete=39712, incomplete=0)
- Bid availability: **39712/39712**
- Ask availability: **39712/39712**
- Median spread (pips): 1.90
- p95 spread (pips): 6.00
- Duplicate timestamps: **0**
- Missing intervals (non-weekend): **6**
- Weekend gaps: **333**
- Abnormal spreads (> 5× median): **601**
- Clean: **False**

### Missing intervals (sample)
- `2022-05-12T05:00:00+00:00` → `2022-05-12T08:00:00+00:00` (2 bars)
- `2024-05-20T14:00:00+00:00` → `2024-05-20T17:00:00+00:00` (2 bars)
- `2024-12-24T21:00:00+00:00` → `2024-12-25T22:00:00+00:00` (24 bars)
- `2024-12-31T21:00:00+00:00` → `2025-01-01T22:00:00+00:00` (24 bars)
- `2025-12-24T21:00:00+00:00` → `2025-12-25T22:00:00+00:00` (24 bars)
- `2025-12-31T21:00:00+00:00` → `2026-01-01T22:00:00+00:00` (24 bars)


### Abnormal spreads (sample)
- `2020-01-03T18:00:00+00:00` — 10.10 pips
- `2020-01-03T21:00:00+00:00` — 10.90 pips
- `2020-01-05T22:00:00+00:00` — 11.00 pips
- `2020-01-10T21:00:00+00:00` — 10.90 pips
- `2020-01-17T21:00:00+00:00` — 11.60 pips
- `2020-01-24T21:00:00+00:00` — 14.00 pips
- `2020-01-29T18:00:00+00:00` — 9.70 pips
- `2020-01-30T11:00:00+00:00` — 10.50 pips

_(+593 more)_
## Audit: USD_JPY H1

- Requested window: `2020-01-01 00:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- First/last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- Candle count: **39714** (complete=39714, incomplete=0)
- Bid availability: **39714/39714**
- Ask availability: **39714/39714**
- Median spread (pips): 1.60
- p95 spread (pips): 3.70
- Duplicate timestamps: **0**
- Missing intervals (non-weekend): **6**
- Weekend gaps: **333**
- Abnormal spreads (> 5× median): **635**
- Clean: **False**

### Missing intervals (sample)
- `2022-05-12T05:00:00+00:00` → `2022-05-12T08:00:00+00:00` (2 bars)
- `2024-05-20T14:00:00+00:00` → `2024-05-20T17:00:00+00:00` (2 bars)
- `2024-12-24T21:00:00+00:00` → `2024-12-25T22:00:00+00:00` (24 bars)
- `2024-12-31T21:00:00+00:00` → `2025-01-01T22:00:00+00:00` (24 bars)
- `2025-12-24T21:00:00+00:00` → `2025-12-25T22:00:00+00:00` (24 bars)
- `2025-12-31T21:00:00+00:00` → `2026-01-01T22:00:00+00:00` (24 bars)


### Abnormal spreads (sample)
- `2020-01-02T21:00:00+00:00` — 10.00 pips
- `2020-01-03T21:00:00+00:00` — 10.00 pips
- `2020-01-16T21:00:00+00:00` — 8.30 pips
- `2020-01-17T21:00:00+00:00` — 10.00 pips
- `2020-01-31T21:00:00+00:00` — 10.00 pips
- `2020-02-07T21:00:00+00:00` — 10.00 pips
- `2020-02-21T21:00:00+00:00` — 10.00 pips
- `2020-02-28T21:00:00+00:00` — 10.00 pips

_(+627 more)_
## Audit: AUD_USD H1

- Requested window: `2020-01-01 00:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- First/last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- Candle count: **39708** (complete=39708, incomplete=0)
- Bid availability: **39708/39708**
- Ask availability: **39708/39708**
- Median spread (pips): 1.30
- p95 spread (pips): 2.50
- Duplicate timestamps: **0**
- Missing intervals (non-weekend): **7**
- Weekend gaps: **333**
- Abnormal spreads (> 5× median): **343**
- Clean: **False**

### Missing intervals (sample)
- `2022-05-04T21:00:00+00:00` → `2022-05-05T03:00:00+00:00` (5 bars)
- `2022-05-12T05:00:00+00:00` → `2022-05-12T08:00:00+00:00` (2 bars)
- `2024-05-20T14:00:00+00:00` → `2024-05-20T17:00:00+00:00` (2 bars)
- `2024-12-24T21:00:00+00:00` → `2024-12-25T22:00:00+00:00` (24 bars)
- `2024-12-31T21:00:00+00:00` → `2025-01-01T22:00:00+00:00` (24 bars)
- `2025-12-24T21:00:00+00:00` → `2025-12-25T22:00:00+00:00` (24 bars)
- `2025-12-31T21:00:00+00:00` → `2026-01-01T22:00:00+00:00` (24 bars)


### Abnormal spreads (sample)
- `2020-01-03T21:00:00+00:00` — 10.90 pips
- `2020-01-15T21:00:00+00:00` — 13.20 pips
- `2020-01-31T21:00:00+00:00` — 15.00 pips
- `2020-02-27T21:00:00+00:00` — 7.40 pips
- `2020-02-28T21:00:00+00:00` — 15.00 pips
- `2020-03-06T21:00:00+00:00` — 15.00 pips
- `2020-03-09T20:00:00+00:00` — 15.00 pips
- `2020-03-10T21:00:00+00:00` — 7.00 pips

_(+335 more)_
## Audit: USD_CAD H1

- Requested window: `2020-01-01 00:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- First/last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- Candle count: **39714** (complete=39714, incomplete=0)
- Bid availability: **39714/39714**
- Ask availability: **39714/39714**
- Median spread (pips): 1.90
- p95 spread (pips): 4.50
- Duplicate timestamps: **0**
- Missing intervals (non-weekend): **6**
- Weekend gaps: **333**
- Abnormal spreads (> 5× median): **361**
- Clean: **False**

### Missing intervals (sample)
- `2022-05-12T05:00:00+00:00` → `2022-05-12T08:00:00+00:00` (2 bars)
- `2024-05-20T14:00:00+00:00` → `2024-05-20T17:00:00+00:00` (2 bars)
- `2024-12-24T21:00:00+00:00` → `2024-12-25T22:00:00+00:00` (24 bars)
- `2024-12-31T21:00:00+00:00` → `2025-01-01T22:00:00+00:00` (24 bars)
- `2025-12-24T21:00:00+00:00` → `2025-12-25T22:00:00+00:00` (24 bars)
- `2025-12-31T21:00:00+00:00` → `2026-01-01T22:00:00+00:00` (24 bars)


### Abnormal spreads (sample)
- `2020-01-03T21:00:00+00:00` — 10.00 pips
- `2020-01-22T14:00:00+00:00` — 10.00 pips
- `2020-01-24T21:00:00+00:00` — 10.00 pips
- `2020-02-14T21:00:00+00:00` — 10.00 pips
- `2020-02-21T21:00:00+00:00` — 10.00 pips
- `2020-02-28T21:00:00+00:00` — 10.00 pips
- `2020-03-04T14:00:00+00:00` — 10.00 pips
- `2020-03-06T21:00:00+00:00` — 10.00 pips

_(+353 more)_
## Audit: USD_CHF H1

- Requested window: `2020-01-01 00:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- First/last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- Candle count: **39709** (complete=39709, incomplete=0)
- Bid availability: **39709/39709**
- Ask availability: **39709/39709**
- Median spread (pips): 1.70
- p95 spread (pips): 4.60
- Duplicate timestamps: **0**
- Missing intervals (non-weekend): **7**
- Weekend gaps: **333**
- Abnormal spreads (> 5× median): **1139**
- Clean: **False**

### Missing intervals (sample)
- `2022-05-04T21:00:00+00:00` → `2022-05-05T03:00:00+00:00` (5 bars)
- `2022-05-12T05:00:00+00:00` → `2022-05-12T08:00:00+00:00` (2 bars)
- `2024-05-20T14:00:00+00:00` → `2024-05-20T17:00:00+00:00` (2 bars)
- `2024-12-24T21:00:00+00:00` → `2024-12-25T22:00:00+00:00` (24 bars)
- `2024-12-31T21:00:00+00:00` → `2025-01-01T22:00:00+00:00` (24 bars)
- `2025-12-24T21:00:00+00:00` → `2025-12-25T22:00:00+00:00` (24 bars)
- `2025-12-31T21:00:00+00:00` → `2026-01-01T22:00:00+00:00` (24 bars)


### Abnormal spreads (sample)
- `2020-01-01T22:00:00+00:00` — 11.00 pips
- `2020-01-02T21:00:00+00:00` — 11.00 pips
- `2020-01-02T22:00:00+00:00` — 9.00 pips
- `2020-01-03T21:00:00+00:00` — 8.60 pips
- `2020-01-05T22:00:00+00:00` — 9.80 pips
- `2020-01-06T21:00:00+00:00` — 8.70 pips
- `2020-01-06T22:00:00+00:00` — 11.00 pips
- `2020-01-09T21:00:00+00:00` — 8.70 pips

_(+1131 more)_
## Audit: NZD_USD H1

- Requested window: `2020-01-01 00:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- First/last timestamp: `2020-01-01 22:00:00+00:00` → `2026-05-20 00:00:00+00:00`
- Candle count: **39717** (complete=39717, incomplete=0)
- Bid availability: **39717/39717**
- Ask availability: **39717/39717**
- Median spread (pips): 2.50
- p95 spread (pips): 4.30
- Duplicate timestamps: **0**
- Missing intervals (non-weekend): **13**
- Weekend gaps: **333**
- Abnormal spreads (> 5× median): **347**
- Clean: **False**

### Missing intervals (sample)
- `2021-12-05T18:00:00+00:00` → `2021-12-05T20:00:00+00:00` (1 bars)
- `2021-12-05T20:00:00+00:00` → `2021-12-05T22:00:00+00:00` (1 bars)
- `2022-05-04T21:00:00+00:00` → `2022-05-05T03:00:00+00:00` (5 bars)
- `2022-05-12T05:00:00+00:00` → `2022-05-12T08:00:00+00:00` (2 bars)
- `2022-12-26T20:00:00+00:00` → `2022-12-26T22:00:00+00:00` (1 bars)
- `2023-12-25T19:00:00+00:00` → `2023-12-25T21:00:00+00:00` (1 bars)
- `2024-01-01T18:00:00+00:00` → `2024-01-01T21:00:00+00:00` (2 bars)
- `2024-02-12T18:00:00+00:00` → `2024-02-12T20:00:00+00:00` (1 bars)

_(+5 more)_

### Abnormal spreads (sample)
- `2020-01-10T21:00:00+00:00` — 20.90 pips
- `2020-01-17T21:00:00+00:00` — 20.90 pips
- `2020-01-23T21:00:00+00:00` — 13.90 pips
- `2020-01-24T21:00:00+00:00` — 14.50 pips
- `2020-01-27T21:00:00+00:00` — 20.90 pips
- `2020-01-30T21:00:00+00:00` — 20.90 pips
- `2020-01-31T21:00:00+00:00` — 20.90 pips
- `2020-02-28T21:00:00+00:00` — 20.90 pips

_(+339 more)_

## RiskEngine wiring summary

- Backtest runs invoking RiskEngine: **665/665**
- Rejection counts across the entire campaign (every reason recorded):

| code | count |
|---|---:|
| `SPREAD_TO_ATR` | 145694 |
| `DRAWDOWN_LIMIT` | 96345 |
| `SPREAD_TOO_WIDE` | 62438 |
| `SESSION_BLOCKED` | 32322 |
| `MARGIN_BUFFER` | 185 |

## Metrics by split

| split | gran | trades | rejected | avg return % | avg max-DD % | avg PF | avg exp R | avg win % |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| full | H1 | 1222 | 14616 | -5.37% | -6.06% | 0.55 | -0.208 | +29.31% |
| full | H4 | 1032 | 1753 | -5.09% | -6.38% | 0.65 | -0.155 | +32.85% |
| test_untouched | H1 | 247 | 2998 | -1.74% | -1.87% | 0.44 | -0.206 | +23.67% |
| test_untouched | H4 | 207 | 262 | -0.88% | -1.44% | 0.74 | -0.088 | +34.86% |
| train | H1 | 725 | 6581 | -3.42% | -4.39% | 0.57 | -0.196 | +30.08% |
| train | H4 | 597 | 496 | -2.61% | -4.00% | 0.72 | -0.135 | +32.92% |
| validation | H1 | 322 | 4647 | -0.67% | -1.46% | 0.65 | -0.104 | +30.41% |
| validation | H4 | 373 | 370 | -2.20% | -2.76% | 0.67 | -0.140 | +36.14% |

## Metrics by pair (full 2020-2026 window, base costs)

| pair | gran | trades | rejected | return % | max-DD % | PF | exp R | win % | avg trade (bars) | avg spread (pips) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| AUD_USD | H1 | 206 | 1961 | -7.52% | -8.10% | 0.66 | -0.148 | +33.98% | n/a | 1.29 |
| AUD_USD | H4 | 144 | 271 | -7.64% | -8.14% | 0.56 | -0.218 | +28.47% | n/a | 1.36 |
| EUR_USD | H1 | 150 | 2100 | -7.22% | -8.18% | 0.56 | -0.196 | +35.33% | n/a | 1.34 |
| EUR_USD | H4 | 132 | 274 | -7.04% | -8.05% | 0.55 | -0.218 | +29.55% | n/a | 1.38 |
| GBP_USD | H1 | 311 | 1618 | -5.40% | -7.11% | 0.83 | -0.069 | +38.26% | n/a | 1.72 |
| GBP_USD | H4 | 198 | 55 | -4.40% | -6.79% | 0.79 | -0.089 | +36.36% | n/a | 1.80 |
| NZD_USD | H1 | 1 | 2680 | -0.14% | -0.14% | 0.00 | -0.562 | +0.00% | n/a | 2.20 |
| NZD_USD | H4 | 38 | 576 | -1.95% | -1.99% | 0.53 | -0.203 | +36.84% | n/a | 2.33 |
| USD_CAD | H1 | 121 | 2308 | -6.69% | -7.09% | 0.54 | -0.162 | +30.58% | n/a | 1.74 |
| USD_CAD | H4 | 122 | 373 | -7.19% | -8.03% | 0.51 | -0.185 | +29.51% | n/a | 1.83 |
| USD_CHF | H1 | 53 | 2380 | -3.70% | -3.70% | 0.45 | -0.314 | +30.19% | n/a | 1.61 |
| USD_CHF | H4 | 181 | 120 | -6.91% | -8.09% | 0.65 | -0.171 | +30.94% | n/a | 1.62 |
| USD_JPY | H1 | 380 | 1569 | -6.93% | -8.13% | 0.82 | -0.001 | +36.84% | n/a | 1.63 |
| USD_JPY | H4 | 217 | 84 | -0.54% | -3.57% | 0.98 | -0.000 | +38.25% | n/a | 1.54 |

## Cost stress (full window)

| regime | gran | trades | rejected | avg return % | avg max-DD % | avg PF | avg exp R |
|---|---|---:|---:|---:|---:|---:|---:|
| base | H1 | 1222 | 14616 | -5.37% | -6.06% | 0.55 | -0.208 |
| base | H4 | 1032 | 1753 | -5.09% | -6.38% | 0.65 | -0.155 |
| stress_15x | H1 | 1024 | 15218 | -5.85% | -6.41% | 0.50 | -0.232 |
| stress_15x | H4 | 988 | 1863 | -5.49% | -6.57% | 0.62 | -0.168 |
| stress_2x | H1 | 891 | 15624 | -5.90% | -6.44% | 0.48 | -0.240 |
| stress_2x | H4 | 938 | 2003 | -5.69% | -6.68% | 0.59 | -0.181 |

## Robustness grid

_81 parameter combinations tested. 0 combinations show positive return (0%)._

> ⚠️ Only 0 of 81 combinations are positive — fragile.


**Top 10 by mean return:**

| ema_fast | ema_slow | donchian | atr_stop | trades | return % | max-DD % | exp R |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 60 | 200 | 20 | 2.5 | 945 | -3.55% | -5.54% | -0.124 |
| 60 | 200 | 30 | 2.5 | 888 | -3.57% | -5.33% | -0.121 |
| 50 | 200 | 30 | 2.5 | 904 | -3.62% | -5.36% | -0.115 |
| 60 | 150 | 30 | 2.5 | 916 | -3.65% | -5.45% | -0.124 |
| 50 | 200 | 20 | 2.5 | 986 | -3.70% | -5.73% | -0.118 |
| 60 | 200 | 15 | 2.5 | 999 | -3.71% | -5.70% | -0.131 |
| 50 | 250 | 30 | 2.5 | 887 | -3.71% | -5.36% | -0.127 |
| 60 | 150 | 20 | 2.5 | 993 | -3.72% | -5.82% | -0.121 |
| 50 | 150 | 15 | 2.5 | 1038 | -3.77% | -5.83% | -0.122 |
| 40 | 200 | 20 | 2.5 | 1004 | -3.80% | -5.89% | -0.120 |

**Bottom 5 by mean return:**

| ema_fast | ema_slow | donchian | atr_stop | trades | return % | max-DD % | exp R |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 40 | 150 | 30 | 1.5 | 853 | -6.98% | -7.31% | -0.214 |
| 60 | 200 | 20 | 1.5 | 896 | -7.00% | -7.43% | -0.224 |
| 50 | 250 | 20 | 1.5 | 935 | -7.02% | -7.41% | -0.226 |
| 60 | 250 | 15 | 1.5 | 979 | -7.04% | -7.53% | -0.230 |
| 60 | 250 | 20 | 1.5 | 904 | -7.09% | -7.47% | -0.235 |

## Worst drawdowns (across all runs)

| run | pair | gran | max-DD % | DD duration (bars) | return % | trades |
|---|---|---|---:|---:|---:|---:|
| `grid_a2b6993d_USD_CAD_H4` | USD_CAD | H4 | -8.23% | 9548 | -7.65% | 134 |
| `grid_cc53ec3f_GBP_USD_H4` | GBP_USD | H4 | -8.23% | 8788 | -7.25% | 164 |
| `grid_a2b6993d_USD_CHF_H4` | USD_CHF | H4 | -8.23% | 7786 | -7.93% | 192 |
| `cost_stress_2x_USD_CAD_H1` | USD_CAD | H1 | -8.23% | 38318 | -7.89% | 113 |
| `grid_398839fb_USD_CHF_H4` | USD_CHF | H4 | -8.23% | 8011 | -6.96% | 119 |
| `grid_511f157b_GBP_USD_H4` | GBP_USD | H4 | -8.23% | 8788 | -6.96% | 158 |
| `grid_922ec954_EUR_USD_H4` | EUR_USD | H4 | -8.23% | 9236 | -7.04% | 125 |
| `grid_6d799a3c_AUD_USD_H4` | AUD_USD | H4 | -8.23% | 9192 | -7.59% | 123 |

## Equity curves

Per-run equity curves (`*_equity.csv`):

- NZD_USD H4: `backtests/campaign_002_real_oanda/runs/baseline/H4/full/baseline_NZD_USD_H4_full_equity.csv`
- USD_JPY H4: `backtests/campaign_002_real_oanda/runs/baseline/H4/full/baseline_USD_JPY_H4_full_equity.csv`
- GBP_USD H4: `backtests/campaign_002_real_oanda/runs/baseline/H4/full/baseline_GBP_USD_H4_full_equity.csv`
- AUD_USD H4: `backtests/campaign_002_real_oanda/runs/baseline/H4/full/baseline_AUD_USD_H4_full_equity.csv`
- USD_CHF H4: `backtests/campaign_002_real_oanda/runs/baseline/H4/full/baseline_USD_CHF_H4_full_equity.csv`
- USD_CAD H4: `backtests/campaign_002_real_oanda/runs/baseline/H4/full/baseline_USD_CAD_H4_full_equity.csv`
- EUR_USD H4: `backtests/campaign_002_real_oanda/runs/baseline/H4/full/baseline_EUR_USD_H4_full_equity.csv`
- NZD_USD H1: `backtests/campaign_002_real_oanda/runs/baseline/H1/full/baseline_NZD_USD_H1_full_equity.csv`
- USD_JPY H1: `backtests/campaign_002_real_oanda/runs/baseline/H1/full/baseline_USD_JPY_H1_full_equity.csv`
- GBP_USD H1: `backtests/campaign_002_real_oanda/runs/baseline/H1/full/baseline_GBP_USD_H1_full_equity.csv`
- USD_CHF H1: `backtests/campaign_002_real_oanda/runs/baseline/H1/full/baseline_USD_CHF_H1_full_equity.csv`
- AUD_USD H1: `backtests/campaign_002_real_oanda/runs/baseline/H1/full/baseline_AUD_USD_H1_full_equity.csv`
- USD_CAD H1: `backtests/campaign_002_real_oanda/runs/baseline/H1/full/baseline_USD_CAD_H1_full_equity.csv`
- EUR_USD H1: `backtests/campaign_002_real_oanda/runs/baseline/H1/full/baseline_EUR_USD_H1_full_equity.csv`

## Recommendation

**REJECT** — [H1] negative test expectancy (H1 test: exp_r=-0.206, PF=0.44, ret=-1.74%, worst_dd=-5.28%, positive_pairs=0/7); [H4] negative test expectancy (H4 test: exp_r=-0.088, PF=0.74, ret=-0.88%, worst_dd=-2.54%, positive_pairs=1/7); stress_2x destroys expectancy (-0.211); financing/rollover unmodeled — see docs/financing_decision.md

## Reproducibility

```bash
# 1. OANDA practice creds in env (gitignored .env.local).
set -a; source ./.env.local; set +a

# 2. Confirm guards pass.
bot doctor --config configs/campaign_002_real_oanda.yaml

# 3. (Re-)fetch real candles for the campaign window.
for pair in EUR_USD GBP_USD USD_JPY AUD_USD USD_CAD USD_CHF NZD_USD; do
  for g in H4 H1; do
    bot fetch-candles \
        --config configs/campaign_002_real_oanda.yaml \
        --instrument $pair --granularity $g \
        --from 2020-01-01 --to 2026-05-20 \
        --campaign CAMPAIGN_002
  done
done

# 4. Audit.
bot audit-data --config configs/campaign_002_real_oanda.yaml \
    --instruments EUR_USD,GBP_USD,USD_JPY,AUD_USD,USD_CAD,USD_CHF,NZD_USD \
    --granularity H4 --from 2020-01-01 --to 2026-05-20 \
    --out backtests/campaign_002_real_oanda/audit_H4.md
bot audit-data --config configs/campaign_002_real_oanda.yaml \
    --instruments EUR_USD,GBP_USD,USD_JPY,AUD_USD,USD_CAD,USD_CHF,NZD_USD \
    --granularity H1 --from 2020-01-01 --to 2026-05-20 \
    --out backtests/campaign_002_real_oanda/audit_H1.md

# 5. Run the campaign.
python scripts/run_campaign_002.py --clean

# 6. Build this report.
python scripts/build_campaign_002_report.py \
    --runs backtests/campaign_002_real_oanda/runs \
    --db data/campaign_002.sqlite3 \
    --out backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md
```
