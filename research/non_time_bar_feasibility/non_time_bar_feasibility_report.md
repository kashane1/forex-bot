# Non-time-bar feasibility report (diagnostic-only)

**Sprint:** research-range-volatility-bar-feasibility-001  
**Window:** 2021-05-27T00:00:00+00:00 → 2023-12-31T23:59:00+00:00  
**Pairs:** EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD  
**Slippage:** 0.2 pip/side · **price basis:** mid  

> Diagnostic geometry + cost only. No signals, no PnL, no returns, no approval. Test lockbox untouched (window is the C029 train window). Labels are hypotheses about where it is worth looking, not gate passes.

## C029 anchor

- 10-pip USD_JPY range: cost 2.29 pips vs 24.05-pip risk → cost-to-risk 0.095; gross +0.0839R, net -0.0188R (cost-defeated).
- Lab achievable gross-edge benchmark: ~0.08R.

## Label counts

| label | n |
|---|---:|
| FEASIBLE_FOR_STRATEGY_RESEARCH | 25 |
| FEASIBLE_ONLY_WITH_LARGER_STOPS | 41 |
| COST_DOMINATED | 10 |
| TOO_SPARSE | 0 |
| TOO_NOISY | 15 |
| INCONCLUSIVE | 0 |

## Range vs volatility

| bar_type | n | feasible | feasible_share | median cost/risk | min cost/risk |
|---|---:|---:|---:|---:|---:|
| range | 35 | 29 | 0.8286 | 0.0572 | 0.0314 |
| volatility | 56 | 37 | 0.6607 | 0.0643 | 0.0377 |

## USD_JPY vs other pairs (pooled)

| group | n | median cost/risk | min cost/risk | feasible_share | mean spread |
|---|---:|---:|---:|---:|---:|
| USD_JPY | 13 | 0.0549 | 0.0366 | 0.6154 | 1.7952 |
| others_pooled | 78 | 0.0629 | 0.0314 | 0.7436 | 1.8683 |

## Full matrix

| pair | type | thr | bars/yr | med min | overshoot | cost p | cost/thr | stop p | cost/risk | label |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| AUD_USD | range | 10 | 5668.11 | 32.0 | 1.4743 | 1.8864 | 0.1886 | 20 | 0.0943 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| AUD_USD | range | 15 | 2635.78 | 74.0 | 1.6321 | 1.8864 | 0.1258 | 30 | 0.0629 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| AUD_USD | range | 20 | 1487.04 | 139.0 | 1.819 | 1.8864 | 0.0943 | 40 | 0.0472 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| AUD_USD | range | 25 | 948.16 | 231.0 | 1.8883 | 1.8864 | 0.0755 | 50 | 0.0377 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| AUD_USD | range | 30 | 676.59 | 366.5 | 2.0961 | 1.8864 | 0.0629 | 60 | 0.0314 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| AUD_USD | volatility | 20 abs_close | 15729.9 | 20.0 | 0.9447 | 1.8864 | 0.0943 | 20 | 0.0943 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| AUD_USD | volatility | 30 abs_close | 10641.5 | 31.0 | 0.959 | 1.8864 | 0.0629 | 30 | 0.0629 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| AUD_USD | volatility | 40 abs_close | 8042.75 | 41.0 | 0.9629 | 1.8864 | 0.0472 | 40 | 0.0472 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| AUD_USD | volatility | 50 abs_close | 6461.59 | 52.0 | 0.9856 | 1.8864 | 0.0377 | 50 | 0.0377 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| AUD_USD | volatility | 20 true_range | 26443.5 | 11.0 | 1.2111 | 1.8864 | 0.0943 | 20 | 0.0943 | TOO_NOISY |
| AUD_USD | volatility | 30 true_range | 17959.4 | 17.0 | 1.2306 | 1.8864 | 0.0629 | 30 | 0.0629 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| AUD_USD | volatility | 40 true_range | 13598.6 | 23.0 | 1.246 | 1.8864 | 0.0472 | 40 | 0.0472 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| AUD_USD | volatility | 50 true_range | 10945.5 | 29.0 | 1.2434 | 1.8864 | 0.0377 | 50 | 0.0377 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| EUR_USD | range | 10 | 7037.12 | 20.0 | 1.7967 | 2.015 | 0.2015 | 20 | 0.1008 | COST_DOMINATED |
| EUR_USD | range | 15 | 3231.37 | 46.0 | 2.0559 | 2.015 | 0.1343 | 30 | 0.0672 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| EUR_USD | range | 20 | 1873.94 | 81.5 | 2.3179 | 2.015 | 0.1008 | 40 | 0.0504 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| EUR_USD | range | 25 | 1177.29 | 139.5 | 2.4963 | 2.015 | 0.0806 | 50 | 0.0403 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| EUR_USD | range | 30 | 822.4 | 221.5 | 2.7158 | 2.015 | 0.0672 | 60 | 0.0336 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| EUR_USD | volatility | 20 abs_close | 16675.7 | 18.0 | 1.1161 | 2.015 | 0.1008 | 20 | 0.1008 | COST_DOMINATED |
| EUR_USD | volatility | 30 abs_close | 11307.3 | 27.0 | 1.1413 | 2.015 | 0.0672 | 30 | 0.0672 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| EUR_USD | volatility | 40 abs_close | 8558.88 | 36.0 | 1.1399 | 2.015 | 0.0504 | 40 | 0.0504 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| EUR_USD | volatility | 50 abs_close | 6885.13 | 45.0 | 1.1418 | 2.015 | 0.0403 | 50 | 0.0403 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| EUR_USD | volatility | 20 true_range | 29444.6 | 9.0 | 1.4479 | 2.015 | 0.1008 | 20 | 0.1008 | TOO_NOISY |
| EUR_USD | volatility | 30 true_range | 20069.5 | 14.0 | 1.4669 | 2.015 | 0.0672 | 30 | 0.0672 | TOO_NOISY |
| EUR_USD | volatility | 40 true_range | 15228.4 | 19.0 | 1.4703 | 2.015 | 0.0504 | 40 | 0.0504 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| EUR_USD | volatility | 50 true_range | 12265.1 | 24.0 | 1.4887 | 2.015 | 0.0403 | 50 | 0.0403 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| GBP_USD | range | 10 | 12285.1 | 12.0 | 2.1844 | 2.5723 | 0.2572 | 20 | 0.1286 | COST_DOMINATED |
| GBP_USD | range | 15 | 5692.41 | 25.0 | 2.5184 | 2.5723 | 0.1715 | 30 | 0.0857 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| GBP_USD | range | 20 | 3286.92 | 45.0 | 2.8049 | 2.5723 | 0.1286 | 40 | 0.0643 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| GBP_USD | range | 25 | 2099.6 | 74.0 | 3.0429 | 2.5723 | 0.1029 | 50 | 0.0514 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| GBP_USD | range | 30 | 1486.27 | 106.0 | 3.2514 | 2.5723 | 0.0857 | 60 | 0.0429 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| GBP_USD | volatility | 20 abs_close | 22010.5 | 13.0 | 1.5114 | 2.5723 | 0.1286 | 20 | 0.1286 | TOO_NOISY |
| GBP_USD | volatility | 30 abs_close | 15015 | 20.0 | 1.5329 | 2.5723 | 0.0857 | 30 | 0.0857 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| GBP_USD | volatility | 40 abs_close | 11389.1 | 26.0 | 1.572 | 2.5723 | 0.0643 | 40 | 0.0643 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| GBP_USD | volatility | 50 abs_close | 9184.93 | 33.0 | 1.5482 | 2.5723 | 0.0514 | 50 | 0.0514 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| GBP_USD | volatility | 20 true_range | 38438.2 | 7.0 | 1.9411 | 2.5723 | 0.1286 | 20 | 0.1286 | TOO_NOISY |
| GBP_USD | volatility | 30 true_range | 26378.7 | 11.0 | 1.9716 | 2.5723 | 0.0857 | 30 | 0.0857 | TOO_NOISY |
| GBP_USD | volatility | 40 true_range | 20074.5 | 14.0 | 2.0119 | 2.5723 | 0.0643 | 40 | 0.0643 | TOO_NOISY |
| GBP_USD | volatility | 50 true_range | 16207 | 18.0 | 2.0372 | 2.5723 | 0.0514 | 50 | 0.0514 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| NZD_USD | range | 10 | 5082.94 | 38.0 | 1.4159 | 2.288 | 0.2288 | 20 | 0.1144 | COST_DOMINATED |
| NZD_USD | range | 15 | 2312.53 | 87.0 | 1.6149 | 2.288 | 0.1525 | 30 | 0.0763 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| NZD_USD | range | 20 | 1306.51 | 166.0 | 1.7607 | 2.288 | 0.1144 | 40 | 0.0572 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| NZD_USD | range | 25 | 854.04 | 269.0 | 1.9269 | 2.288 | 0.0915 | 50 | 0.0458 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| NZD_USD | range | 30 | 566.66 | 418.0 | 1.9594 | 2.288 | 0.0763 | 60 | 0.0381 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| NZD_USD | volatility | 20 abs_close | 14784 | 22.0 | 0.8998 | 2.288 | 0.1144 | 20 | 0.1144 | COST_DOMINATED |
| NZD_USD | volatility | 30 abs_close | 9999.23 | 33.0 | 0.9007 | 2.288 | 0.0763 | 30 | 0.0763 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| NZD_USD | volatility | 40 abs_close | 7552.08 | 45.0 | 0.9132 | 2.288 | 0.0572 | 40 | 0.0572 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| NZD_USD | volatility | 50 abs_close | 6069.28 | 56.0 | 0.9082 | 2.288 | 0.0458 | 50 | 0.0458 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| NZD_USD | volatility | 20 true_range | 25227.6 | 12.0 | 1.1432 | 2.288 | 0.1144 | 20 | 0.1144 | TOO_NOISY |
| NZD_USD | volatility | 30 true_range | 17117.3 | 19.0 | 1.1611 | 2.288 | 0.0763 | 30 | 0.0763 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| NZD_USD | volatility | 40 true_range | 12955.6 | 25.0 | 1.1701 | 2.288 | 0.0572 | 40 | 0.0572 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| NZD_USD | volatility | 50 true_range | 10422.4 | 31.0 | 1.1776 | 2.288 | 0.0458 | 50 | 0.0458 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| USD_CAD | range | 10 | 8516.82 | 18.0 | 1.5811 | 2.509 | 0.2509 | 20 | 0.1255 | COST_DOMINATED |
| USD_CAD | range | 15 | 3868.62 | 42.0 | 1.7347 | 2.509 | 0.1673 | 30 | 0.0836 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_CAD | range | 20 | 2156.69 | 75.0 | 1.8718 | 2.509 | 0.1255 | 40 | 0.0627 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_CAD | range | 25 | 1419.53 | 123.0 | 1.9608 | 2.509 | 0.1004 | 50 | 0.0502 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_CAD | range | 30 | 959.34 | 211.0 | 2.0335 | 2.509 | 0.0836 | 60 | 0.0418 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| USD_CAD | volatility | 20 abs_close | 18919.9 | 16.0 | 1.1804 | 2.509 | 0.1255 | 20 | 0.1255 | COST_DOMINATED |
| USD_CAD | volatility | 30 abs_close | 12850.3 | 25.0 | 1.1847 | 2.509 | 0.0836 | 30 | 0.0836 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_CAD | volatility | 40 abs_close | 9723.43 | 33.0 | 1.2126 | 2.509 | 0.0627 | 40 | 0.0627 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_CAD | volatility | 50 abs_close | 7826.73 | 42.0 | 1.1994 | 2.509 | 0.0502 | 50 | 0.0502 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_CAD | volatility | 20 true_range | 32288.2 | 9.0 | 1.5057 | 2.509 | 0.1255 | 20 | 0.1255 | TOO_NOISY |
| USD_CAD | volatility | 30 true_range | 22026.7 | 14.0 | 1.5243 | 2.509 | 0.0836 | 30 | 0.0836 | TOO_NOISY |
| USD_CAD | volatility | 40 true_range | 16713.9 | 18.0 | 1.5452 | 2.509 | 0.0627 | 40 | 0.0627 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_CAD | volatility | 50 true_range | 13469.8 | 23.0 | 1.5502 | 2.509 | 0.0502 | 50 | 0.0502 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_CHF | range | 10 | 5652.3 | 26.0 | 1.5459 | 2.3389 | 0.2339 | 20 | 0.1169 | COST_DOMINATED |
| USD_CHF | range | 15 | 2550.54 | 59.0 | 1.7803 | 2.3389 | 0.1559 | 30 | 0.078 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_CHF | range | 20 | 1432.27 | 109.0 | 1.9353 | 2.3389 | 0.1169 | 40 | 0.0585 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_CHF | range | 25 | 933.5 | 187.0 | 1.9618 | 2.3389 | 0.0936 | 50 | 0.0468 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| USD_CHF | range | 30 | 631.46 | 296.0 | 2.1929 | 2.3389 | 0.078 | 60 | 0.039 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| USD_CHF | volatility | 20 abs_close | 14828.8 | 20.0 | 1.0302 | 2.3389 | 0.1169 | 20 | 0.1169 | COST_DOMINATED |
| USD_CHF | volatility | 30 abs_close | 10045.5 | 30.0 | 1.0433 | 2.3389 | 0.078 | 30 | 0.078 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_CHF | volatility | 40 abs_close | 7599.15 | 40.0 | 1.0363 | 2.3389 | 0.0585 | 40 | 0.0585 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_CHF | volatility | 50 abs_close | 6107.86 | 50.0 | 1.057 | 2.3389 | 0.0468 | 50 | 0.0468 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| USD_CHF | volatility | 20 true_range | 24544.8 | 11.0 | 1.2991 | 2.3389 | 0.1169 | 20 | 0.1169 | TOO_NOISY |
| USD_CHF | volatility | 30 true_range | 16693 | 17.0 | 1.3175 | 2.3389 | 0.078 | 30 | 0.078 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_CHF | volatility | 40 true_range | 12647 | 23.0 | 1.3362 | 2.3389 | 0.0585 | 40 | 0.0585 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_CHF | volatility | 50 true_range | 10183.2 | 28.0 | 1.3375 | 2.3389 | 0.0468 | 50 | 0.0468 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| USD_JPY | range | 10 | 12905.8 | 10.0 | 2.7097 | 2.1952 | 0.2195 | 20 | 0.1098 | COST_DOMINATED |
| USD_JPY | range | 15 | 6120.59 | 21.0 | 3.3578 | 2.1952 | 0.1463 | 30 | 0.0732 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_JPY | range | 20 | 3585.1 | 38.0 | 3.8025 | 2.1952 | 0.1098 | 40 | 0.0549 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_JPY | range | 25 | 2381.58 | 59.0 | 4.3154 | 2.1952 | 0.0878 | 50 | 0.0439 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| USD_JPY | range | 30 | 1698.43 | 83.0 | 4.6359 | 2.1952 | 0.0732 | 60 | 0.0366 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| USD_JPY | volatility | 20 abs_close | 21597.8 | 13.0 | 1.6353 | 2.1952 | 0.1098 | 20 | 0.1098 | TOO_NOISY |
| USD_JPY | volatility | 30 abs_close | 14746.2 | 20.0 | 1.6877 | 2.1952 | 0.0732 | 30 | 0.0732 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_JPY | volatility | 40 abs_close | 11198.5 | 26.0 | 1.7258 | 2.1952 | 0.0549 | 40 | 0.0549 | FEASIBLE_ONLY_WITH_LARGER_STOPS |
| USD_JPY | volatility | 50 abs_close | 9027.17 | 33.0 | 1.7635 | 2.1952 | 0.0439 | 50 | 0.0439 | FEASIBLE_FOR_STRATEGY_RESEARCH |
| USD_JPY | volatility | 20 true_range | 38227.6 | 7.0 | 2.1324 | 2.1952 | 0.1098 | 20 | 0.1098 | TOO_NOISY |
| USD_JPY | volatility | 30 true_range | 26273.4 | 10.0 | 2.2025 | 2.1952 | 0.0732 | 30 | 0.0732 | TOO_NOISY |
| USD_JPY | volatility | 40 true_range | 20031.7 | 14.0 | 2.2363 | 2.1952 | 0.0549 | 40 | 0.0549 | TOO_NOISY |
| USD_JPY | volatility | 50 true_range | 16186.2 | 17.0 | 2.2715 | 2.1952 | 0.0439 | 50 | 0.0439 | FEASIBLE_FOR_STRATEGY_RESEARCH |
