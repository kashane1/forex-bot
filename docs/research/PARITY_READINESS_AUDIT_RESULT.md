# Parity Readiness Audit — Result

**Sprint:** Audit 001 · Phase 9  
**Classification:** **WARN** (Backtrader lane strong; Lean optional/secondary)

## Backtrader status

| Input | Parity support |
|-------|----------------|
| Candles | `research/backtrader_lane/data_adapter.py` — bid/ask lines |
| Fills | Campaign-specific strategies mirror ask/bid entry/exit |
| Exits | `research/backtrader_exit_parity/exit_logic.py` shared with engine tests |
| Risk | `research/backtrader_lane/risk_parity.py` |
| Exports | Compare scripts + pinned fixtures under `tests/unit/backtrader_lane/` |

Trade CSV exports include `exit_reason`, `fill_timing`, thesis/ambiguous columns (`backtesting/exporters.py`).

## Lean status

- `docs/research/LEAN_PARITY_DESIGN.md` — design only
- **Not run** this sprint (no cloud auth; per safety rules)

## Divergence classification

`tests/research/test_parity_verifier_*.py` classify indicator / fill / exit / event-loop divergence.

## Schema gaps

- Standardized `available_data_cutoff` not in export schema
- Campaign ID only via run metadata / config hash, not per-trade column

## Tests added

None.

## Classification

**WARN:** Backtrader reproduction is mature for audited campaigns; full Lean parity and signal-level export remain incomplete.
