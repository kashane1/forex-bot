# Backtrader CAMPAIGN_015 RiskEngine & Fill Parity 001 — Plan

**Branch:** `infra-backtrader-campaign-015-riskengine-and-fill-parity-001`
**Base:** `infra-backtrader-campaign-015-signal-diff-001`
**Date:** 2026-05-26
**Sprint type:** Infrastructure (Backtrader secondary-lane fill + RiskEngine parity)

> Does **not** approve any strategy. `configs/approved_strategies.yaml`
> remains `approved: []`. Paper / demo / live remain blocked.

## 1 · Problem statement

Window-aligned fold-window comparison (532 BT vs 164 bespoke) is classified
**`SIGNAL_RULE_MISMATCH`**. Signal-diff sprint found:

1. **First divergence:** fold 0 / EUR_USD at `2021-11-04T13:00:00+00:00`
   — `FILL_TIMING_MISMATCH` / `same_bar_adverse_stop` on BT only.
2. **Dominant aggregate gap:** BT lane does not run bespoke `RiskEngine`
   spread/session/drawdown gates (`RISK_ENGINE_REJECTION_MISSING`).
3. **Raw signals align:** 0 raw-signal mismatches once indicators are
   timestamp-aligned.

This sprint closes the two largest known parity gaps **without** changing
bespoke `BacktestEngine`, CAMPAIGN_015 frozen settings, or approval status.

## 2 · Phase 0 truth audit (2026-05-26)

| check | status |
|---|---|
| Branch | `infra-backtrader-campaign-015-riskengine-and-fill-parity-001` |
| `configs/approved_strategies.yaml` | `approved: []` ✓ |
| Paper/demo/live refusal | research-freeze gate PASS ✓ |
| Signal-diff doc | `docs/research/BACKTRADER_CAMPAIGN_015_SIGNAL_DIFF.md` ✓ |
| First divergence | `research/campaign_015/diagnostics/signal_diff/first_divergence.json` ✓ |
| BT fold-window artifacts | `research/campaign_015/diagnostics/backtrader_fold_window/` ✓ |
| Bespoke rehydrate | `research/campaign_015/diagnostics/walk_forward_rehydrate/` ✓ |
| Prior classification | `SIGNAL_RULE_MISMATCH`, 532 vs 164 ✓ |
| `pytest tests/ -q` | 1467 passed |
| `check_research_freeze.py` | PASS |
| `validate_research_archive.py` | PASS |
| `scan_artifacts_for_secrets.py` | PASS |
| `ruff check` | 7 fixable F401 in `test_fold_windows.py` (pre-existing) |

## 3 · Root causes to address

### 3.1 Entry-bar same-bar adverse stop

| lane | behaviour on fill bar T+1 |
|---|---|
| Backtrader (current) | Rejects entry if bar range touches stop (`same_bar_adverse_stop`) |
| Bespoke `BacktestEngine` | Enters; does **not** apply entry-bar adverse stop; stop checked from bar T+2 |

**Parity fix:** add `entry_bar_stop_policy`:

- `backtrader_default` — preserve current BT behaviour (default for full-window).
- `bespoke_current_no_entry_bar_stop` — skip entry-bar adverse stop; later-bar
  stop/time exits unchanged.

### 3.2 RiskEngine rejection parity

Bespoke CAMPAIGN_015 runner (`scripts/run_campaign_015.py`) constructs
`RiskEngine(settings, mode="backtest")` and passes it to `BacktestEngine`.
BT fold-window lane currently sizes manually with no spread/session/drawdown gates.

**Parity fix:** read-only `RiskEngine` evaluation at pending-entry fill time
using local candle bid/ask only — no broker, no order submission.

## 4 · Implementation approach

| component | change |
|---|---|
| `campaign_015_failed_breakout_reversal.py` | `entry_bar_stop_policy`, `risk_engine_parity` kwargs |
| `research/backtrader_lane/risk_parity.py` | new read-only RiskEngine wrapper |
| `runner.py` / `run_backtrader_parity.py` | CLI flags + manifest parity fields |
| tests | entry-bar policy + risk rejection unit tests |
| output dir | `backtrader_fold_window_riskengine_fill_parity/` (no overwrite) |

### Parity run flags

```
--entry-bar-stop-policy bespoke_current_no_entry_bar_stop
--risk-engine-parity
```

## 5 · Hard rules (reaffirmed)

- No strategy approval, no YAML registry change, no paper/demo/live.
- No OANDA / broker / LEAN paths.
- No CAMPAIGN_015 parameter tuning or gate changes.
- No mutation of prior evidence (new labeled diagnostic paths only).
- Bespoke engine unchanged; fill-semantics inconsistency documented separately.

## 6 · Phase deliverables

| phase | deliverable |
|---|---|
| 0 | This plan |
| 1 | `entry_bar_stop_policy` + tests |
| 2 | RiskEngine parity layer + tests |
| 3 | `BACKTRADER_CAMPAIGN_015_RISKENGINE_FILL_PREFLIGHT.md` |
| 4 | BT parity run artifacts under `backtrader_fold_window_riskengine_fill_parity/` |
| 5 | `BACKTRADER_CAMPAIGN_015_RISKENGINE_FILL_COMPARISON.md` |
| 6 | `CAMPAIGN_015_ENTRY_BAR_STOP_SEMANTICS_AUDIT.md` |
| 7 | `BACKTRADER_CAMPAIGN_015_RISKENGINE_AND_FILL_PARITY_RESULT.md` |
| 8 | `BACKTRADER_CAMPAIGN_015_RISKENGINE_AND_FILL_PARITY_001_SUMMARY.md` |

## 7 · Success criteria

1. Trade-count gap 532 vs 164 shrinks materially.
2. First divergence (fold 0 / EUR_USD entry-bar stop) disappears under parity flags.
3. RiskEngine rejection counts become comparable to bespoke.
4. Classification improves (target: `TOLERABLE_DRIFT` or `PASS`; not required).
5. CAMPAIGN_015 remains unapproved; paper/demo/live remain blocked.
