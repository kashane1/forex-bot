# Cross-Asset Real Data Source Registry

**Diagnostic only** — `strategy_evidence: false`. No trading claims. No strategy evidence.

This document mirrors `research/cross_asset_features/source_registry.json` for human review.

## Purpose

Define auditable, reproducible external feature sources before fetch or alignment. These features support **future** multi-timeframe confluence research — not current strategy approval or live trading.

## Required features

| feature_id | FRED ID | why it matters (research context) |
|---|---|---|
| `broad_usd_index` | DTWEXBGS | USD regime headwind/tailwind for FX direction |
| `us_2y_yield` | DGS2 | Short-rate / policy context |
| `us_10y_yield` | DGS10 | Rates bias in confluence grader |
| `us_10y_minus_2y` | derived | Curve shape macro proxy |
| `vix` | VIXCLS | Risk-on / risk-off regime |
| `sp500` | SP500 | Equity risk appetite |
| `oil_wti` | DCOILWTICO | Commodity-linked FX context |

## Optional features

| feature_id | source | notes |
|---|---|---|
| `nasdaq_composite` | FRED NASDAQCOM | Growth sentiment complement |
| `gold` | local CSV only | Operator must verify licensing |
| `cot_eur_net` | CFTC TFF | Weekly positioning; design-only this sprint |
| derived 1d change/return columns | derived | Deterministic; not optimized |

## Source priority

1. FRED API (`fred_api`) — free, read-only.
2. Local CSV drop (`data/external_features/`).
3. Derived from ingested parents.
4. COT (`optional_cot`) — secondary.

## No-lookahead rule

Daily observations dated `D` become available at **`D + 1 day 00:00 UTC`**. H4 alignment uses `availability_ts <= bar_time` with forward-fill from prior observations only.

## Auth

Set `FRED_API_KEY` locally (never commit). If absent, fetcher writes `BLOCKED_AUTH_OR_LOCAL_CSV_REQUIRED` and local CSV fallback remains available.

## Legacy aliases

Fixtures and prior CSVs may use `dxy.csv`, `us2y.csv`, `us10y.csv`, `oil.csv`, `nasdaq.csv`. Loaders map these to canonical IDs.

## Machine-readable registry

See [`research/cross_asset_features/source_registry.json`](../../research/cross_asset_features/source_registry.json).
