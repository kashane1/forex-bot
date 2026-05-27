# Risk Sizing and Portfolio Constraint Audit — Result

**Sprint:** Audit 001 · Phase 8  
**Classification:** **PASS**

## Files inspected

- `risk/sizing.py` — pip value, NAV risk %, unit rounding
- `risk/policy.py` — spread, session, exposure, loss limits
- `risk/exposure.py`, `risk/kill_switch.py`
- `domain/instruments.py` — pip_location, min/max units

## Sizing formula

Documented in `sizing.py` module docstring: risk amount home → stop distance pips → pip value per unit → round down to trade precision.

## Metadata usage

- EUR_USD, USD_JPY: covered in `tests/unit/test_risk_engine_backtest_parity.py`, backtest PnL conversion tests
- JPY quote pip handling regression in `tests/unit/backtrader_exit_parity/test_pnl_home_currency.py`

## Portfolio constraints

- Max positions, per-instrument caps, correlated exposure — `risk/policy.py` + config YAML
- Kill switch blocks planning — `test_executor_safety.py`, policy tests
- Rejection reasons exported per signal in backtest runs

## Tests added

None — existing parity tests sufficient.

## Gaps

- Non-USD account currency cross conversions depend on quote availability in `quotes_by_instrument` — fail-closed to `PIP_VALUE_UNAVAILABLE`.

## Classification

**PASS** for shared sizing math and rejection export; live loop still blocked by empty approval registry.
