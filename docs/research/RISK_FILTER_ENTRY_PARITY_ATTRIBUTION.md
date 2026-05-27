# Risk / Filter Entry Parity Attribution

**Branch:** `infra-entry-orchestration-parity-diagnostics-001`  
**Artifact:** [`research/entry_parity/risk_filter_attribution.json`](../../research/entry_parity/risk_filter_attribution.json)

---

## Primary root cause

**BACKTRADER_IMPLEMENTATION_GAP — missing quote→USD PnL conversion**

The Backtrader lane `_pnl()` treated USD_JPY and USD_CAD gross PnL as USD instead of converting JPY/CAD quote PnL to account currency. Example: a −1000 JPY loss was recorded as −$1000 equity → spurious **DRAWDOWN_LIMIT** rejections (71 on USD_JPY train alone).

Bespoke `BacktestEngine._pnl()` converts correctly via `quote_currency` / `base_currency`.

---

## Ruled out

| Hypothesis | Verdict |
|---|---|
| Indicator warmup | Ruled out — early entries match bit-for-bit |
| Fill timing | Ruled out — both `signal_bar_close` |
| Dedupe alignment | Ruled out — same SQLite feed |
| Session/spread filters | Same RiskEngine — not primary gap (rejections symmetric on matched pairs) |
| Same-bar re-entry | Only 3 bespoke-only entries across all campaigns |
| Signal generation | Ruled out — 100% BT ⊆ bespoke with identical timestamps |

---

## Secondary factor (minor)

Legacy BT risk-window code used rolling 7-day `realized_pl_week` instead of calendar Monday-week. **Not load-bearing** once PnL conversion fixed (counts unchanged 279→279 pre-fix).

---

## Bespoke rejection logs

Spread/session rejections exist in bespoke CSVs (`SPREAD_TOO_WIDE`, `SESSION_BLOCKED`, `SPREAD_TO_ATR`) — these apply equally when both lanes evaluate the same signal. They do not explain bespoke-only **taken** trades.

---

## Classification

**BACKTRADER_IMPLEMENTATION_GAP** — not a bespoke engine bug.
