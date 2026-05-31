# Backtrader CAMPAIGN_015 — Preflight After Provenance Repair (Phase 3)

**Sprint:** [BT C015 Provenance Repair 001](BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_001_PLAN.md)
**Branch:** `infra-backtrader-campaign-015-provenance-repair-001`
**Date:** 2026-05-26
**Preflight status:** **PASS — 7/7 instruments runnable, 0 blocked.**

> Infra-only document. Does NOT approve any strategy. Does NOT call
> OANDA, Backtrader-OANDA, Lean, QuantConnect, or any broker.
> `configs/approved_strategies.yaml` remains `approved: []`.

---

## 1 · Preflight result

```bash
python scripts/run_backtrader_parity.py \
  --campaign CAMPAIGN_015 \
  --output   research/campaign_015/diagnostics/backtrader_lane \
  --dry-run
```

Reports (excerpt):

```json
{
  "instruments_requested": ["EUR_USD","GBP_USD","USD_JPY","AUD_USD","USD_CAD","USD_CHF","NZD_USD"],
  "instruments_runnable":   ["EUR_USD","GBP_USD","USD_JPY","AUD_USD","USD_CAD","USD_CHF","NZD_USD"],
  "instruments_blocked":    []
}
```

All seven CAMPAIGN_002 H4 instruments load cleanly under the BT
lane's `research.backtrader_lane.data_adapter.load_candles`, which
enforces:

- CSV row-sha256 == committed `*.provenance.json` `data_sha256`;
- CSV row count == provenance `candle_count`;
- CSV time column is monotonic.

All three checks pass for all seven instruments.

---

## 2 · What this confirms

1. The Phase 2 lock-step repair is fully effective: the BT
   `load_candles` strict preflight no longer raises a
   `CandleProvenanceError`.
2. The Phase 2 export-side de-duplication (one canonical row per H4
   timestamp, kept in monotonic UTC order) was the right call: the BT
   lane's monotonic-time check would otherwise have re-blocked the
   run even with matching shas.
3. The CAMPAIGN_015 BT adapter
   ([`research/backtrader_lane/strategies/campaign_015_failed_breakout_reversal.py`](../../research/backtrader_lane/strategies/campaign_015_failed_breakout_reversal.py))
   accepts all 7 requested instruments via the standard runner.

---

## 3 · No live or network code paths exercised

The preflight uses only:
- local CSVs at `research/lean_parity/exports/campaign_002_h4/*.csv`
  (gitignored, regenerable),
- committed `*.provenance.json` sidecars,
- the BT-lane data adapter at
  `research.backtrader_lane.data_adapter`,
- the BT-lane runner at `research.backtrader_lane.runner`.

No `OANDA_*` environment variable is consumed; no broker HTTP/REST
endpoint is called; no Lean / QuantConnect cloud is touched.
`scripts/run_backtrader_parity.py` is the entry point and it
imports no broker SDK.

---

## 4 · Safety invariants (re-verified)

- `configs/approved_strategies.yaml` is `approved: []`.
- Paper / demo / live loops refuse to start.
- CAMPAIGN_015 frozen config / parameters / gates — untouched.
- Bespoke walk-forward runner — untouched.
- Anti-overfit classifier — untouched.

---

## 5 · Next step

**Phase 4** runs the BT lane to completion against the now-loadable
CSVs and compares the resulting trade/expectancy/exit-reason
distribution to the bespoke CAMPAIGN_015 rehydrate output. Divergence,
if any, gets one of the binding labels from the pre-commit:
`PASS / TOLERABLE_DRIFT / DATA_MISMATCH / TIMESTAMP_MISMATCH /
SIGNAL_RULE_MISMATCH / FILL_TIMING_MISMATCH /
STOP_OR_TIME_EXIT_MISMATCH / SIZING_OR_PNL_MISMATCH / BLOCKED`.
