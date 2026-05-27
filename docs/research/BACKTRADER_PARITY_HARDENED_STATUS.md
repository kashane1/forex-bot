# Backtrader Parity — Hardened Status

**Branch:** `infra-backtrader-entry-parity-hardening-001`  
**Date:** 2026-05-27  
**Evidence class:** `parity_diagnostic_only` — `strategy_evidence: false`

---

## Root cause confirmed

Backtrader lane `_pnl()` treated JPY/CAD/CHF quote-currency PnL as USD,
inflating drawdown and triggering `DRAWDOWN_LIMIT` rejections (~20% fewer BT
trades). **Confirmed** in entry orchestration diagnostics; **fixed** in this sprint.

---

## Fix landed

| Component | Change |
|---|---|
| `research/backtrader_exit_parity/pnl.py` | `pnl_home_currency()` mirrors `BacktestEngine._pnl` |
| `strategy.py` | Uses `pnl_home_currency`; default `risk_window_mode=engine_aligned` |
| `runner.py` | Engine-aligned runs; metadata + `parity_run_manifest.json` |

**PnL conversion mode:** `home_currency_v1`  
**Backtrader version:** 1.9.78.123  
**Data source:** deduped `data/campaign_002.sqlite3`

---

## Tolerance achieved

**Yes** — ±1 trade per campaign (target met).

---

## Campaign parity status

| Campaign | Bespoke | BT | Gap | Entry parity | Exit parity |
|---|---:|---:|---:|---|---|
| C008 | 354 | 353 | 1 | VIABLE | CLOSE_MATCH |
| C009 | 403 | 402 | 1 | VIABLE | CLOSE_MATCH |
| C018 | 378 | 377 | 1 | VIABLE | CLOSE_MATCH |

---

## Exit parity validated

**Yes** for C008/C009/C018 — exit-reason shares CLOSE_MATCH bespoke on refreshed
artifacts. Train splits PASS exact match; validation splits within tolerance.

---

## Full campaign parity viable

**Yes, for C008/C009/C018 only** — independent Backtrader lane is viable within
±1 trade for entry orchestration and CLOSE_MATCH for exit shares. **Not**
generalized to all future strategies or campaigns.

---

## Remaining limitations

1. One shared bespoke-only GBP_USD entry (2024-01-16) across all three campaigns.
2. Non-USD cross pairs (e.g. GBP_JPY) unsupported — same as bespoke engine.
3. Parity lane uses shared strategy module for entries, not bespoke engine loop.
4. Manual financing sample remains **paused**.

---

## Custom engine bug suspected

**No.** Bespoke engine entry orchestration is trustworthy. Divergence was
Backtrader implementation gap only.

---

## Campaign verdict changed

**No.** C008/C009/C018 verdicts preserved (REJECT).

---

## Strategy approval

**No.** `configs/approved_strategies.yaml` → `approved: []`. Paper/demo/live
remain blocked.

---

## Recommended next sprint

**`research-exit-hypothesis-precommit-002`** — parity lane hardened; exit
pathology corroborated; entry gap resolved to ±1 trade.
