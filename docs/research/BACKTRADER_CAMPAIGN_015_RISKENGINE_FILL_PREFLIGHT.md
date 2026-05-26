# Backtrader CAMPAIGN_015 RiskEngine & Fill Parity — Preflight

**Date:** 2026-05-26
**Branch:** `infra-backtrader-campaign-015-riskengine-and-fill-parity-001`
**Output:** `research/campaign_015/diagnostics/backtrader_fold_window_riskengine_fill_parity/`

> Diagnostic-only. Does **not** approve any strategy.
> `configs/approved_strategies.yaml` remains `approved: []`.

## Command

```bash
python scripts/run_backtrader_parity.py \
  --campaign CAMPAIGN_015 \
  --run-mode fold_windows \
  --fold-plan research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/plan.json \
  --output research/campaign_015/diagnostics/backtrader_fold_window_riskengine_fill_parity \
  --entry-bar-stop-policy bespoke_current_no_entry_bar_stop \
  --risk-engine-parity \
  --dry-run
```

## Preflight results

| check | status |
|---|---|
| Folds | 8/8 |
| Pairs | 7/7 |
| Warmup coverage | 90 calendar days per fold ✓ |
| Provenance strict mode | PASS (all 7 instruments) |
| Runnable | `true` |
| Live/broker/OANDA paths | none |
| `entry_bar_stop_policy` | `bespoke_current_no_entry_bar_stop` |
| `risk_engine_parity` | `true` |

## Parity flags in manifest

- `ENTRY_BAR_STOP_POLICY` — bespoke_current mode documented
- `FOLD_WINDOW_BESPOKE_MIRROR` — per fold × pair equity reset
- `STRICT_TEST_WINDOW=False` — warmup-margin trades counted

## Safety

- CAMPAIGN_015 remains **unapproved**
- Paper / demo / live remain **blocked**
- No frozen CAMPAIGN_015 settings changed
