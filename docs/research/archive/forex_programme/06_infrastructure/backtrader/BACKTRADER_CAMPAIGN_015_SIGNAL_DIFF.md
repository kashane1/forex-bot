# Backtrader vs Bespoke Signal Diff — CAMPAIGN_015

> Diagnostic-only. Does **not** approve any strategy.
> `configs/approved_strategies.yaml` remains `approved: []`.

**Cell:** fold 0 / EUR_USD
**Trace bars:** 1157

## Phase 0 — comparison headline

- Window-aligned classification: `SIGNAL_RULE_MISMATCH`
- Backtrader fold-window trades: **532**
- Bespoke rehydrate trades: **164**

## Cell trace summary (fold × pair)

- Matching raw-signal bars (same side): **8**
- Bespoke RiskEngine rejections where BT would still enter: **2**
- Simulated bespoke entries in trace: **6**
- Simulated BT entries in trace: **5**

**Aggregate 532 vs 164 interpretation:** raw strategy rules align on CSV data once BT indicators are timestamp-aligned. The residual fold-window trade-count gap is dominated by the BT lane **not running the bespoke RiskEngine** (spread / session / drawdown gates), plus entry-bar lifecycle differences (`same_bar_adverse_stop_wins` on BT only).

## First divergence

- **Timestamp:** `2021-11-04T13:00:00+00:00`
- **Kind:** `entry_timing_mismatch`
- **Root cause:** `FILL_TIMING_MISMATCH`
- Bespoke raw: `none` | BT raw: `none`
- Bespoke accepted: `yes` (—)
- BT accepted: `no` (same_bar_adverse_stop)

### Notes

- kind=entry_timing_mismatch
- atr: bespoke=0.00252257 bt=0.00252257 delta=-0.00000000
- adx: bespoke=18.2792 bt=18.2788 delta=0.0004
- classified=FILL_TIMING_MISMATCH

## Root-cause classification

See `research/campaign_015/diagnostics/signal_diff/first_divergence.json`.

## Safety

- CAMPAIGN_015 remains **unapproved**.
- No broker/OANDA calls were made.
- No frozen CAMPAIGN_015 settings were changed.

## Recommended next step

1. Wire read-only RiskEngine parity into the BT CAMPAIGN_015 adapter (spread / session / drawdown / sizing gates only; no broker).
2. Align bespoke `BacktestEngine` entry-bar `same_bar_adverse_stop_wins` with the BT lane (or document both as approximations).
3. Re-run fold-window comparison after (1); expect trade-count gap to shrink materially before any approval discussion.
