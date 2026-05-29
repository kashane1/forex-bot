# Non-time-bar feasibility report (diagnostic-only)

**Sprint:** research-range-volatility-bar-feasibility-001  
**Window:** 2021-05-27T00:00:00+00:00 → 2023-12-31T23:59:00+00:00  
**Pairs:** USD_JPY  
**Slippage:** 0.2 pip/side · **price basis:** mid  

> Diagnostic geometry + cost only. No signals, no PnL, no returns, no approval. Test lockbox untouched (window is the C029 train window). Labels are hypotheses about where it is worth looking, not gate passes.

## C029 anchor

- 10-pip USD_JPY range: cost 2.29 pips vs 24.05-pip risk → cost-to-risk 0.095; gross +0.0839R, net -0.0188R (cost-defeated).
- Lab achievable gross-edge benchmark: ~0.08R.

## Label counts

| label | n |
|---|---:|
| FEASIBLE_FOR_STRATEGY_RESEARCH | 4 |
| FEASIBLE_ONLY_WITH_LARGER_STOPS | 4 |
| COST_DOMINATED | 1 |
| TOO_SPARSE | 0 |
| TOO_NOISY | 4 |
| INCONCLUSIVE | 0 |

## Range vs volatility

| bar_type | n | feasible | feasible_share | median cost/risk | min cost/risk |
|---|---:|---:|---:|---:|---:|
| range | 5 | 4 | 0.8 | 0.0549 | 0.0366 |
| volatility | 8 | 4 | 0.5 | 0.0732 | 0.0439 |

## USD_JPY vs other pairs (pooled)

| group | n | median cost/risk | min cost/risk | feasible_share | mean spread |
|---|---:|---:|---:|---:|---:|
| USD_JPY | 13 | 0.0549 | 0.0366 | 0.6154 | 1.7952 |

## Full matrix

| pair | type | thr | bars/yr | med min | overshoot | cost p | cost/thr | stop p | cost/risk | label |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
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
