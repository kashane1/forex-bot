# Backtrader Exit Parity Diagnostics 001 — Plan

**Branch:** `infra-backtrader-exit-parity-diagnostics-001`  
**Date:** 2026-05-27  
**Evidence class:** `parity_diagnostic_only` — `strategy_evidence: false`

---

## Purpose

Build a **local Backtrader-based secondary verification lane** focused on **exit behavior** for CAMPAIGN_008, CAMPAIGN_009, and CAMPAIGN_018. Determine whether stop/time/target/protective-stop findings from the bespoke `BacktestEngine` are reproduced when bar iteration runs through Backtrader with an independently ported exit state machine.

This sprint does **not** approve strategies, enable trading, or mutate campaign verdicts.

---

## Non-goals

- Create CAMPAIGN_019 or any new strategy family
- Approve any strategy (`configs/approved_strategies.yaml` stays `approved: []`)
- Enable paper/demo/live loops or place orders
- Call OANDA order/trade/position mutation endpoints
- Use live credentials
- Tune C008/C009/C018 parameters or change precommitted C018 rules
- Open test lockbox
- Claim profitability
- Resume manual overnight financing sample collection

---

## Campaigns covered

| Campaign | Entry module | Exit mechanics under test |
|---|---|---|
| **C008** | `mean_reversion 0.1.0-c008` | Hard ATR stop vs 40-bar time stop |
| **C009** | `mean_reversion 0.2.0-c009` | Midline target vs stop vs time |
| **C018** | `mean_reversion_protective_stop 0.1.0-c018` | Protective stop at +1R MFE → break-even |

---

## Exact parity targets

Compare bespoke deduped forensic replay vs Backtrader lane on **train** and **validation** splits:

| Metric | Tolerance |
|---|---|
| Total trade count per split | ±2 trades |
| Exit-reason share (stop/time/target/protective) | ±5 pp → CLOSE_MATCH; ±1 pp → PASS |
| Dominant pathology sign (C008 stop/time split; C009 target capping; C018 protective arm rate) | Must match direction |
| Expectancy R by exit reason | Informational (not gating) |
| C018 protective arm rate | ±5 pp |

**Reference artifacts (bespoke canonical):**

- C008/C009: `backtests/CAMPAIGN_008_mean_reversion_deduped_forensic/`, `backtests/CAMPAIGN_009_mean_reversion_midline_deduped_forensic/`
- C018: `backtests/CAMPAIGN_018_mean_reversion_protective_stop/{train,validation}/base/`
- Exit anatomy: `docs/research/C008_C009_DEDUPED_EXIT_ANATOMY.md`
- C018 mechanism: `research/campaign_018/mechanism_diagnostics.json`

---

## Local-only rules

- Deduped H4 candles from `data/campaign_002.sqlite3` via `CandleRepo.list_with_dedupe_stats` (keep_last)
- Backtrader optional extra: `backtrader>=1.9.78,<2.0` (`backtrader-lane` group in `pyproject.toml`)
- Fill timing: `signal_bar_close` (matches deduped forensic replay)
- Gap-fill policy: `none` (CAMPAIGN_001–018 default)
- Spread/slippage: `fixed_slippage_pips=0.2`, `spread_slippage_multiplier=0.5`
- Same-bar precedence: adverse stop before target before time
- C018 protective stop: arm at +1R MFE, move stop to entry, **no ratchet**
- RiskEngine backtest mode for entry sizing (matches bespoke forensic replay)

---

## Expected divergences

| Source | Likelihood | Detection |
|---|---|---|
| Indicator warmup bar count | Low | Entry count drift |
| Bid/ask column naming / NaN fallback | Low | Exit price drift |
| RiskEngine state (equity/drawdown windows) | Low | Entry count drift |
| EOD forced close on final bar | Low | +1 eod trade |
| Floating-point rounding in R | Informational | Expectancy R noise |

If Backtrader unavailable, document BLOCKED and do not substitute without explanation.

---

## Implementation layout

```
research/backtrader_exit_parity/
  constants.py       — splits, config paths, bespoke globs
  data_feed.py       — deduped H4 → Backtrader PandasData feed
  exit_logic.py      — independent exit state machine (ported from engine)
  strategy.py        — Backtrader loop + MeanReversion* entries
  runner.py          — C008/C009/C018 replay orchestration
  compare.py         — bespoke vs Backtrader exit-reason comparison
scripts/run_backtrader_exit_parity.py
tests/unit/backtrader_exit_parity/test_exit_fixtures.py
```

---

## Phase truth audit (Phase 0)

| Check | Result |
|---|---|
| `docs/research/DEDUPED_C008_C009_RERUN_FORENSIC_ONLY_001_SUMMARY.md` | Present |
| `docs/research/C008_C009_DEDUPED_EXIT_ANATOMY.md` | Present |
| `docs/research/C008_C009_DEDUPED_MAE_MFE_DIAGNOSTICS.md` | Present |
| `docs/research/CAMPAIGN_018_PROTECTIVE_STOP_EXECUTION_001_SUMMARY.md` | Present |
| `docs/research/CAMPAIGN_018_FINAL_INTERPRETATION.md` | Present |
| `research/campaign_018/gate_result.json` | Present |
| `research/campaign_018/mechanism_diagnostics.json` | Present |
| `configs/approved_strategies.yaml` → `approved: []` | Confirmed |
| CAMPAIGN_019 | Does not exist |
| Paper/demo/live | Blocked (research freeze) |
| Backtrader install | Available via `backtrader-lane` extra (1.9.78.x tested) |

---

## Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
python scripts/run_backtrader_exit_parity.py
```

---

## Divergence classification (Phase 3)

- **PASS** — trade counts match (±0), exit shares within 1 pp
- **CLOSE_MATCH** — counts within ±2, shares within 5 pp, pathology direction preserved
- **MATERIAL_DIVERGENCE** — counts or shares exceed tolerance; suspect engine bug or modeling gap
- **BLOCKED** — data missing, Backtrader unavailable, or bespoke reference absent

---

## Recommended next sprint (Phase 4 — provisional)

Selection deferred until parity replay completes. Candidates:

1. `research-exit-hypothesis-precommit-002` — if parity confirms exits
2. `research-financing-manual-rate-source-expansion-001` — if financing remains blocker (no manual trades)
3. `infra-engine-exit-bug-investigation-001` — if material divergence
4. `research-new-candidate-strategy-discovery-with-confluence-001` — only if engine corroborated and pivot away from C008 family desired
