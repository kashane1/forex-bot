# Backtrader Parity Comparison — `CAMPAIGN_011`

> `strategy_evidence: false`. Verification infrastructure. Does **not** approve any strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains scaffold-only.

- Generated at: `2026-05-25T16:38:21+00:00`
- Strategy: `random_entry_anchor` `0.1.0-c011`
- Backtrader summary: `research/backtrader_lane/results/campaign_011_full_window_004/backtrader_summary.json`
- Bespoke reference: `research/lean_parity/campaign_011_h4_bespoke_reference.json`
- Total trades: backtrader **2808** · bespoke **2800** · Δ +8
- **Overall classification: `TOLERABLE_DRIFT`**

| instrument | BT trades | bespoke trades | Δ% | BT R | bespoke R | Δ R | classification |
|---|---:|---:|---:|---:|---:|---:|---|
| AUD_USD | 385 | 385 | +0.00% | — | -0.064600 | — | `PASS` |
| EUR_USD | 395 | 394 | +0.25% | — | -0.049600 | — | `TOLERABLE_DRIFT` |
| GBP_USD | 401 | 400 | +0.25% | — | -0.007300 | — | `TOLERABLE_DRIFT` |
| NZD_USD | 401 | 400 | +0.25% | — | -0.026500 | — | `TOLERABLE_DRIFT` |
| USD_CAD | 396 | 394 | +0.51% | — | -0.016100 | — | `TOLERABLE_DRIFT` |
| USD_CHF | 411 | 409 | +0.49% | — | 0.050300 | — | `TOLERABLE_DRIFT` |
| USD_JPY | 419 | 418 | +0.24% | — | 0.000400 | — | `TOLERABLE_DRIFT` |

#### AUD_USD notes
- all tight tolerance bands hold

#### EUR_USD notes
- trade-count drift 0.25% inside wider band; metric agreement holds

#### GBP_USD notes
- trade-count drift 0.25% inside wider band; metric agreement holds

#### NZD_USD notes
- trade-count drift 0.25% inside wider band; metric agreement holds

#### USD_CAD notes
- trade-count drift 0.51% inside wider band; metric agreement holds

#### USD_CHF notes
- trade-count drift 0.49% inside wider band; metric agreement holds

#### USD_JPY notes
- trade-count drift 0.24% inside wider band; metric agreement holds

