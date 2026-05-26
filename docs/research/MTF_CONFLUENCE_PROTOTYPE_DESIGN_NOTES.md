# MTF Confluence Prototype — Design Notes

**Branch:** `infra-multi-timeframe-confluence-and-cost-atlas-001`  
**Status:** Research prototype — `strategy_evidence: false`

## Module location

`research/confluence/` — matches repo convention (`research/edge_discovery/`, `research/walk_forward/`).

Not wired into `src/forex_bot/execution/` or broker adapter.

## Output shape

`ConfluenceScore.to_features_dict()` → intended for `Signal.features["confluence"]` in future research campaigns.

## State rules (v0, frozen)

| state | rule |
|---|---|
| trend_up | close > EMA50 and EMA slope positive; ADX ≥ 20 |
| trend_down | close < EMA50 and EMA slope negative; ADX ≥ 20 |
| range | ADX < 20 |
| unknown | insufficient warmup bars |

D1/W1: synthetic from H4 resample (CAMPAIGN_006 D1 rollover issue acknowledged).

## Grading

- **REJECT:** cost hostile, W1/D1 hostile to side
- **A:** aligned HTF, acceptable cost, no penalty reason codes
- **B:** ≤1 penalty, acceptable/marginal cost
- **C:** unknown HTF/cost or multiple penalties

## Divergence

Filter/exit helper only — never standalone entry. See `research/confluence/divergence.py`.

## Non-goals this sprint

- RiskEngine wiring
- Threshold optimization
- Campaign validation
