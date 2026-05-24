# Edge-discovery study — turnover_cost_sensitivity

> Exploratory lab output. Not a strategy verdict; does not approve,
> promote, or change any campaign status. See
> `docs/research/EDGE_DISCOVERY_LAB_001_PLAN.md`.

## Setup

- Instrument basis: `EUR_USD` at midprice `1.1`
- Cost model: spread `1.5` pip + 2 × slip `0.2` pip
- Implied cost per trade (round-trip): `+0.000173` log-return units
- Pre-cost edge sweep (per trade): `[-0.0002, -0.0001, 0.0, 0.0001, 0.00025, 0.0005]`
- Trade-count sweep: `[50, 100, 250, 500, 1000, 2500]`

### Cumulative post-cost return (log units)

| pre-cost edge / trade | n=50 | n=100 | n=250 | n=500 | n=1000 | n=2500 |
|---|---|---|---|---|---|---|
| -0.00020 | -0.01864 | -0.03727 | -0.09318 | -0.18636 | -0.37273 | -0.93182 |
| -0.00010 | -0.01364 | -0.02727 | -0.06818 | -0.13636 | -0.27273 | -0.68182 |
| +0.00000 | -0.00864 | -0.01727 | -0.04318 | -0.08636 | -0.17273 | -0.43182 |
| +0.00010 | -0.00364 | -0.00727 | -0.01818 | -0.03636 | -0.07273 | -0.18182 |
| +0.00025 | +0.00386 | +0.00773 | +0.01932 | +0.03864 | +0.07727 | +0.19318 |
| +0.00050 | +0.01636 | +0.03273 | +0.08182 | +0.16364 | +0.32727 | +0.81818 |

### Cumulative cost burden (log units)

| pre-cost edge / trade | n=50 | n=100 | n=250 | n=500 | n=1000 | n=2500 |
|---|---|---|---|---|---|---|
| -0.00020 | +0.00864 | +0.01727 | +0.04318 | +0.08636 | +0.17273 | +0.43182 |
| -0.00010 | +0.00864 | +0.01727 | +0.04318 | +0.08636 | +0.17273 | +0.43182 |
| +0.00000 | +0.00864 | +0.01727 | +0.04318 | +0.08636 | +0.17273 | +0.43182 |
| +0.00010 | +0.00864 | +0.01727 | +0.04318 | +0.08636 | +0.17273 | +0.43182 |
| +0.00025 | +0.00864 | +0.01727 | +0.04318 | +0.08636 | +0.17273 | +0.43182 |
| +0.00050 | +0.00864 | +0.01727 | +0.04318 | +0.08636 | +0.17273 | +0.43182 |

### Cost share of pre-cost cumulative

| pre-cost edge / trade | n=50 | n=100 | n=250 | n=500 | n=1000 | n=2500 |
|---|---|---|---|---|---|---|
| -0.00020 | +0.86364 | +0.86364 | +0.86364 | +0.86364 | +0.86364 | +0.86364 |
| -0.00010 | +1.72727 | +1.72727 | +1.72727 | +1.72727 | +1.72727 | +1.72727 |
| +0.00000 | — | — | — | — | — | — |
| +0.00010 | +1.72727 | +1.72727 | +1.72727 | +1.72727 | +1.72727 | +1.72727 |
| +0.00025 | +0.69091 | +0.69091 | +0.69091 | +0.69091 | +0.69091 | +0.69091 |
| +0.00050 | +0.34545 | +0.34545 | +0.34545 | +0.34545 | +0.34545 | +0.34545 |

## Reading

- Reading down a column shows how a fixed trade count amplifies an edge in both directions: when the per-trade pre-cost edge is negative, more trades make the post-cost result strictly worse.
- Reading along a row shows how cumulative cost burden grows linearly in `n`. The cost-per-trade is `0.00015 ≈ 1.5 pips` on an EUR_USD-shaped midprice; a candidate needs a per-trade pre-cost edge well above that *plus* a margin over the random-entry null (CAMPAIGN_005: −0.095 R aggregate) before turnover helps it.
- The cells where `cost_share_of_pre_cost > 1` are cost-dominated: the strategy loses more in costs than the edge gains pre-cost. These cells should never graduate to a formal campaign.

