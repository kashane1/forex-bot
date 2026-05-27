# Cost, Spread, Slippage, and Financing Audit — Result

**Sprint:** Audit 001 · Phase 7  
**Classification:** **WARN** (spread/slippage explicit; financing partial)

## Current cost model

| Component | Source |
|-----------|--------|
| Spread at decision | `(ask - bid) / pip_size` from candle bid/ask at signal/fill bar |
| Fill slippage | `FillModel` fixed + spread multiplier on top of bid/ask |
| 2× stress | Campaign configs multiply slippage/spread stress — mechanical in runner (e.g. C019 `stress_2x`, `stress_15x` folders) |
| Financing | `financing.py` + observed/manual CSV paths; many campaigns **financing-unmodeled** in base runs |

## Spread filters

- RiskEngine `SPREAD_TOO_WIDE` / spread-to-ATR use snapshot at decision bar — same timestamp only.

## Financing / rollover

- Triple rollover and full carry modeling: **partial** — observed capture pilot exists; not all backtests apply financing overlay.
- Status explicit in campaign reports where `financing_mode: none` or overlay scripts documented.

## Tests / evidence

- `tests/unit/test_risk_engine_backtest_parity.py`
- `tests/research/test_financing_*`, `tests/unit/test_observed_financing.py`
- Cost atlas research (`research/cost_atlas/`) — diagnostic, not approval

## Tests added

None (snapshot audit).

## Recommendation

Dedicated **observed-cost / spread-regime** sprint before comparing overnight-holding strategies. Do not infer edge from base runs without financing overlay when hold > 1 day.

## Classification

**WARN:** Bid/ask spread at fill is sound; financing remains a known gap for multi-day holds.
