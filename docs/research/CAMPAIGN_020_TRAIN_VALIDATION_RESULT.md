# CAMPAIGN_020 — Train / Validation Result

**Date:** 2026-05-27  
**Branch:** `research-campaign-020-mtf-confluence-execution-001`  
**Fill timing:** `next_bar_open` (mandatory)  
**Dedupe:** `keep_last` · **Data:** `oanda-practice` / `data/campaign_002.sqlite3`

## Aggregate metrics

| split | cost | trades | expectancy_r | profit_factor | pairs positive |
|---|---|---:|---:|---:|---:|
| Train | base | 353 | **−0.035** | 1.0046 | 2 / 6 |
| Validation | base | 204 | **+0.053** | 1.1313 | 5 / 6 |
| Validation | 2× stress | 204 | **+0.049** | — | — |

## Train gate

**FAIL** — train expectancy **−0.035 R** &lt; 0 under `next_bar_open`.

Per gate discipline: execution **stopped** after train evaluation. Validation metrics above are **recorded for transparency only** — they do **not** constitute screening pass and did **not** authorize test lockbox.

## Validation gates (informational — screening failed on train)

| gate | threshold | result |
|---|---|---|
| validation expectancy &gt; 0 | &gt; 0 | **PASS** (+0.053 R) |
| validation PF | ≥ 1.05 | **PASS** (1.1313) |
| validation trades | ≥ 80 | **PASS** (204) |
| validation pairs positive | ≥ 2 | **PASS** (5) |
| 2× cost stress validation | ≥ 0 | **PASS** (+0.049 R) |
| beat deduped C011 null | &gt; +0.0071 R | **PASS** |
| train expectancy | ≥ 0 | **FAIL** |

## Hold / financing

- Average hold **3.72 calendar days**; **77.7%** of trades held &gt; 1 day.
- Financing overlay sensitivity: **not applied** — loader rejected rows where `entry_time == exit_time` on same-bar exits (infrastructure quirk); documented in `research/campaign_020/financing_overlay_sensitivity.json`.

## Artifacts

- Backtests: `backtests/CAMPAIGN_020_mtf_confluence_pullback/`
- Research JSON: `research/campaign_020/`
