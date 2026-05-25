# Custom-engine CAMPAIGN_011 H4 parity reproduction (no-RiskEngine)

**Generated:** 2026-05-25T13:35:33.294638+00:00 · **Branch:** `infra-bespoke-campaign-011-norisk-reference-001`

> **DIAGNOSTIC / PARITY REPRODUCTION — NOT A NEW VERDICT.** This runs `random_entry_anchor 0.1.0-c011` (CAMPAIGN_011) on the bespoke engine with `risk_engine=None` so the future Backtrader CAMPAIGN_011 comparison sprint has a canonical, no-gates reference to compare against. CAMPAIGN_011 is a null model by construction; it remains **REJECT / null diagnostic anchor by design**. `configs/approved_strategies.yaml` is not touched. `strategy_evidence: false`.

## Run parameters

| field | value |
|---|---|
| strategy | `random_entry_anchor 0.1.0-c011` |
| master_seed | `20260523` (frozen, no seed sweep) |
| config hash | `69ab4e6f08dca374…` |
| fill timing | `signal_bar_close` |
| risk engine | **not wired** (`risk_engine=None`) — strategy + engine mechanics only |
| cost model | 0.2 pip fixed slippage + 0.5× spread, 0.0 commission/unit |
| window | 2020-01-01 → 2026-05-20 (full split) |
| data store | `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` (gitignored) |

## Full-window results (bespoke engine, no RiskEngine)

| instrument | candles | trades | expectancy R | return % | profit factor | win % | max DD % |
|---|---|---|---|---|---|---|---|
| EUR_USD | 9931 | 394 | -0.0496 | -4.83 | 0.85 | 47.2 | -6.09 |
| GBP_USD | 9931 | 400 | -0.0073 | -0.80 | 0.98 | 47.5 | -3.98 |
| USD_JPY | 9932 | 418 | 0.0004 | 5.90 | 1.18 | 49.5 | -3.82 |
| AUD_USD | 9931 | 385 | -0.0646 | -6.08 | 0.80 | 47.5 | -6.52 |
| USD_CAD | 9931 | 394 | -0.0161 | -2.02 | 0.93 | 47.2 | -4.77 |
| USD_CHF | 9931 | 409 | 0.0503 | 4.77 | 1.15 | 50.6 | -1.90 |
| NZD_USD | 9935 | 400 | -0.0265 | -2.67 | 0.92 | 47.5 | -5.94 |

**Total trades across the seven pairs (no RiskEngine): 2800.**

## What this establishes

- A reproducible, hash-pinned no-RiskEngine bespoke reference for CAMPAIGN_011 / `random_entry_anchor`, suitable for the future Backtrader CAMPAIGN_011 comparison sprint.
- It does **not** establish, measure, or imply any strategy edge. CAMPAIGN_011 is a null model by construction; the no-RiskEngine path silences spread / session / loss-limit gates, which by itself produces more trades but no edge.
- `configs/approved_strategies.yaml` is not touched. CAMPAIGN_011 cannot be approved by design.
