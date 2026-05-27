# Fill Timing and Price Source Audit — Result

**Sprint:** Audit 001 · Phase 5  
**Classification:** **WARN** (price sides PASS; default `signal_bar_close` optimistic)

## Current fill convention

| Action | Price source (bid/ask available) |
|--------|----------------------------------|
| Long entry | **Ask** + adverse slippage |
| Long exit | **Bid** − adverse slippage |
| Short entry | **Bid** − adverse slippage |
| Short exit | **Ask** + adverse slippage |

Implemented in `backtesting/fills.py` `FillModel`. Midpoint fills are **not** used in `FillModel`; `CandleFrame` may derive mid for indicators only.

## Fill timing

| Mode | Behavior |
|------|----------|
| `signal_bar_close` (default) | Entry at signal bar close quote — **optimistic** (documented `FILL_TIMING_MODEL.md`) |
| `next_bar_open` | Entry at bar N+1 open — no future data; final-bar signal → `NEXT_BAR_OPEN_UNAVAILABLE` |

Stops/TP/time exits use bar range tests on bid/ask; thesis-invalidation uses bid/ask close.

## Spread / slippage

- Slippage = `max(fixed_slippage_pips, spread_pips * multiplier)` applied **once** per fill in adverse direction.
- Spread for risk filter from same-bar bid/ask — not double-counted with fill slippage (spread embedded in bid/ask, slippage is incremental).

## Same-bar behavior

- `next_bar_open`: entry and stop can occur same bar N+1 (documented).
- Exit priority documented in Phase 6 memo.

## Tests added / evidence

- `tests/unit/test_fill_price_side_audit_001.py` (new)
- `tests/unit/test_fill_timing.py`, `tests/unit/test_backtest_engine.py`

## Campaign validity impact

- CAMPAIGN_001–009 and most evidence used **`signal_bar_close`** — results are an **upper bound**, not execution-realistic.
- Campaigns that pinned `next_bar_open` are more conservative (e.g. D1AGG smoke tests).

## Classification

**WARN:** Price-side rules PASS; timing default is knowingly optimistic unless config overrides.
