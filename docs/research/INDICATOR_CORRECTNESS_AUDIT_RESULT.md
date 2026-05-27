# Indicator Correctness Audit — Result

**Sprint:** Audit 001 · Phase 3  
**Classification:** **WARN** (RSI warmup uses `fillna(50)`; otherwise PASS)

## Indicators audited

| Indicator | Module | Definition |
|-----------|--------|------------|
| EMA | `indicators.ema` | `ewm(span=length, min_periods=length)` |
| ATR | `indicators.atr` | Wilder TR smooth, `min_periods=length` |
| Donchian | `donchian_high/low` | `shift(1).rolling(length)` — **excludes current bar** |
| RSI | `indicators.rsi` | Wilder-style; **`fillna(50.0)`** on warmup |
| z-score | `indicators.zscore` | Rolling mean/std; NaN until `min_periods` |
| ADX | `indicators.adx` | Wilder ADX; documented in docstring |

## Warmup behavior

- ATR, EMA, z-score, ADX: NaN until window full — **PASS**
- Donchian: NaN until `length` prior bars exist — **PASS**
- RSI: early values default to **50.0** — **WARN** (not blocked/NaN; strategies must use `warmup_bars_required()`)

## Prior-bar / no-lookahead

- Donchian: proven in `test_donchian_excludes_current_bar`, `test_donchian_breakout_uses_prior_only`
- ADX: `test_adx_no_lookahead`
- z-score: `test_zscore_no_lookahead` (new)

## Tests added

- `test_zscore_warmup_is_nan_not_zero`, `test_zscore_no_lookahead`, `test_rsi_early_bars_filled_to_50_not_nan` in `tests/unit/test_indicators.py`

## Divergence / ambiguity

- RSI `fillna(50)` can produce false “neutral” readings on short histories — mitigated by strategy warmup gates, not indicator-level block.
- Currency-strength / spread-ATR percentile helpers live in strategy modules — not re-audited formula-by-formula here.

## Campaign validity risk

Low for campaigns with adequate `warmup_bars_required`. **Medium** only if a strategy used RSI on bars `< length` without warmup gate.

## Classification

**WARN** overall due to RSI fill policy; core breakout/trend indicators **PASS**.
