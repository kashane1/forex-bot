# Crypto Family E Diagnostics 4 & 5 — OI Impulse / Funding-OI Interaction (LOW-POWER)

**Sprint:** `crypto-family-e-exploratory-diagnostics-001`
**Type:** Exploratory, explicitly LOW-POWER. No strategy/campaign/front gate/approval.

**Classification:** `blocked_low_power_oi`

Only ~180d aggregate daily OI (OKX rubik venue-aggregate USD notional) is freely available; per-instrument multi-year OI is the binding gap. Diagnostics 4 (OI impulse) and 5 (funding/OI interaction) are LOW-POWER and cannot reach candidate_for_front_gate from this sample.

## OI availability

| Instrument | OI rows | low-power |
|------------|--------:|:---------:|
| BTC_PERP_USD | 180 | yes |
| ETH_PERP_USD | 180 | yes |

With only ~180d aggregate daily OI, diagnostics 4 (OI impulse) and 5 (funding/OI interaction) cannot reach `candidate_for_front_gate`. Forward OI collection is the prerequisite for a powered test.

## Recommendation

Forward-collect per-instrument OI (8h or daily) before any OI-dependent diagnostic.

