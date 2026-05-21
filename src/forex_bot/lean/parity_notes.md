# Lean parity notes

_None yet — v0 does not include a Lean implementation by intent._

When the first Lean parity backtest is added, list each divergence
from the native engine here. Template:

| Aspect | Native | Lean | Notes |
|--------|--------|------|-------|
| Fill model | bid/ask + configurable slippage | _tbd_ | |
| Quote source | OANDA bid/ask per candle | _tbd_ | |
| Spread model | OANDA quote at signal time | _tbd_ | |
| Rollover | not modeled in v0 | _tbd_ | |
| Order timing | next bar open | _tbd_ | |
| Warmup | `max(EMA_slow, Donchian, ATR) + 2` | _tbd_ | |
| Fees | `commission_per_unit` config | _tbd_ | |
