# Crypto Family E Diagnostic 2 — Funding Trend Continuation Result

**Sprint:** `crypto-family-e-exploratory-diagnostics-001`
**Type:** Exploratory diagnostic only — no strategy, campaign, front gate, or approval.

**Hypothesis:** Persistent same-sign funding over k settlements aligns with directional continuation.

**Classification:** `rejected`

best cell = continuation k3 h24: gross=3.77e-04, all_in=-1.66e-03, Holm-adj shuffled p=1.000. No effect distinguishable from the matched null; rejected.

Continuation trades in the sign of persistent funding; contrarian is the after-cost alternative. Monotonicity across k∈{3,6,9} is the design's pass signal.

## k = 3 settlements

| Horizon | Split | n | cont gross | cont all-in | cont 2× | contra gross | shuffled p |
|--------:|-------|--:|-----------:|------------:|--------:|-------------:|-----------:|
| 24 | BTC_PERP_USD | 5117 | 0.000598 | -0.001337 | -0.002937 | -0.000598 | 0.3980 |
| 24 | ETH_PERP_USD | 4938 | 0.000149 | -0.002004 | -0.003804 | -0.000149 | 0.8420 |
| 24 | pooled | 10055 | 0.000377 | -0.001664 | -0.003363 | -0.000377 | 0.5880 |
| 72 | BTC_PERP_USD | 4748 | 0.001192 | -0.001373 | -0.002973 | -0.001192 | 0.7040 |
| 72 | ETH_PERP_USD | 4608 | -0.001833 | -0.004598 | -0.006398 | 0.001833 | 0.3110 |
| 72 | pooled | 9356 | -0.000298 | -0.002961 | -0.004660 | 0.000298 | 0.9680 |
Skipped: {'BTC_PERP_USD': 240, 'ETH_PERP_USD': 240}.

## k = 6 settlements

| Horizon | Split | n | cont gross | cont all-in | cont 2× | contra gross | shuffled p |
|--------:|-------|--:|-----------:|------------:|--------:|-------------:|-----------:|
| 24 | BTC_PERP_USD | 4138 | 0.000257 | -0.001723 | -0.003323 | -0.000257 | 0.7800 |
| 24 | ETH_PERP_USD | 3846 | -0.000678 | -0.002873 | -0.004673 | 0.000678 | 0.3620 |
| 24 | pooled | 7984 | -0.000194 | -0.002277 | -0.003973 | 0.000194 | 0.8540 |
| 72 | BTC_PERP_USD | 3845 | 0.001589 | -0.001091 | -0.002691 | -0.001589 | 0.6090 |
| 72 | ETH_PERP_USD | 3595 | -0.002196 | -0.005095 | -0.006895 | 0.002196 | 0.2310 |
| 72 | pooled | 7440 | -0.000240 | -0.003026 | -0.004722 | 0.000240 | 0.9940 |
Skipped: {'BTC_PERP_USD': 240, 'ETH_PERP_USD': 240}.

## k = 9 settlements

| Horizon | Split | n | cont gross | cont all-in | cont 2× | contra gross | shuffled p |
|--------:|-------|--:|-----------:|------------:|--------:|-------------:|-----------:|
| 24 | BTC_PERP_USD | 3542 | 0.000402 | -0.001606 | -0.003206 | -0.000402 | 0.6800 |
| 24 | ETH_PERP_USD | 3173 | -0.000495 | -0.002725 | -0.004525 | 0.000495 | 0.6050 |
| 24 | pooled | 6715 | -0.000022 | -0.002135 | -0.003830 | 0.000022 | 0.9860 |
| 72 | BTC_PERP_USD | 3288 | 0.002160 | -0.000607 | -0.002207 | -0.002160 | 0.3890 |
| 72 | ETH_PERP_USD | 2971 | -0.001247 | -0.004240 | -0.006040 | 0.001247 | 0.6440 |
| 72 | pooled | 6259 | 0.000543 | -0.002332 | -0.004026 | -0.000543 | 0.9650 |
Skipped: {'BTC_PERP_USD': 240, 'ETH_PERP_USD': 240}.

## Why this is not a strategy

Exploratory sign test; no portfolio construction. Competes with Diagnostic 1 — at most one of reversion/continuation can hold.

