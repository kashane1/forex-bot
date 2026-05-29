# CAMPAIGN_031 — Vol-Managed TSMOM Front-Gate Screen (results)

_Generated: 2026-05-29T16:59:02.746422+00:00 · Freeze: intact; train-only; validation/test untouched; nothing approved_

**Train window:** 2020-01-01T00:00:00Z → 2022-12-31T23:59:59Z (train only).
**Universe:** AUD_USD, EUR_USD, GBP_USD, NZD_USD, USD_CAD, USD_CHF, USD_JPY.

> Data caveat: 7 USD-legged majors only, no crosses; ~3y train -> ~3 annual cycles after 252d warmup. Underpowered for a slow-signal deflated-Sharpe claim.

## House config (full-Σ C, MM on)

- Sharpe pre-cost: **0.323**, net: **-0.067** (boot 5–95%: -0.854 … 0.878)
- Ann return net: -0.60% · ann vol: 9.05% · days: 778
- Total turnover cost: 0.0204 · total financing: 0.0885
- Mean |net-USD| exposure: 0.899 · mean gross (active): 2.193

## Baselines & ablations

- 2× cost/financing stress Sharpe net: **-0.456**
- MM-off Sharpe net: 0.014 (MM adds -0.081)
- Naive-C Sharpe net: -0.033
- Naive-self baseline Sharpe net: 0.423
- Random-entry matched-turnover null: mean -0.533, p95 0.434, observed -0.067, P(obs≤null max) 0.235

## Frozen decision inputs (precommit §7)

- house_net_sharpe_gt_0: **False**
- house_2x_net_sharpe_gt_0: **False**
- boot_lo5_gt_0: **False**
- beats_null_p95: **False**
- beats_naive_self: **False**

All advance-conditions met: **False**.

This artifact records statistics against the pre-stated decision rule. The verdict (`EARNS_A_SCAFFOLD` / `DOES_NOT_EARN_A_SCAFFOLD` / `INSUFFICIENT_POWER` / `COST_FINANCING_DEFEATED`) is assigned in the Phase-3 interpretation memo, not here. Freeze intact; nothing approved; lockbox untouched.