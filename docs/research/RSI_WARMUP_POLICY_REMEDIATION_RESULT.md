# RSI Warmup Policy Remediation — Result

**Module:** `src/forex_bot/strategies/indicators.py`  
**Classification:** **PASS** (backward compatible)

## Current behavior

| Policy | Warmup bars | Use |
|--------|-------------|-----|
| `neutral_fill` (default) | Filled to **50.0** | Legacy / historical campaigns |
| `nan` | **NaN** until `min_periods` | New strategies |

## Strategies inspected

- `mean_reversion` (C008/C009/C019 entries) — uses `rsi()` with default; gated by `warmup_bars_required()` ≥ max(ema, z, atr, rsi, adx)+3 (~203 bars), so RSI at signal bars is fully warmed. Legacy fillna does not affect fired signals.

## Backward compatibility

**Default unchanged** (`neutral_fill`) — historical campaign metrics unaffected.

## Tests added

- `test_rsi_strict_nan_warmup` in `tests/unit/test_indicators.py`

## Campaign rerun required?

**No** for C008/C009/C019 given warmup gates. Rerun only if a strategy used RSI with `warmup_bars_required < rsi_lookback`.

## Future rule

New strategies must use `warmup_policy="nan"` or document explicit legacy rationale.
