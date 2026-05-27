# Shared Signal and MTF Confluence Audit 001 — Plan

**Branch:** `infra-shared-signal-and-mtf-confluence-audit-001`  
**Date:** 2026-05-26  
**Sprint type:** Infrastructure audit (not strategy, not CAMPAIGN_020)

## Purpose

Audit and harden shared layers that affect **every** strategy campaign before trusting more research results:

- Candle representation, deduplication, and H4→D1AGG aggregation
- Higher-timeframe alignment semantics (no incomplete/future HTF bars)
- Indicator primitives (warmup, prior-bar, no lookahead)
- Signal domain contract vs risk/execution separation
- Backtest fill timing and bid/ask/slippage conventions
- Exit event ordering (stop/target/time/thesis-invalidation/EOD)
- Spread/cost/slippage/financing model explicitness
- Risk sizing and portfolio constraints
- Backtrader/parity reproduction readiness

**This sprint does not approve any strategy.** It does not modify CAMPAIGN_019 rules, gates, artifacts, or verdicts.

## Non-goals

- No CAMPAIGN_020 or new strategy campaigns
- No strategy parameter tuning
- No changes to `configs/approved_strategies.yaml` (must remain `approved: []`)
- No paper/demo/live enablement
- No OANDA order/trade/position API calls
- No live broker credentials
- No rewriting historical campaign verdicts

## Safety rules (hard)

1. Registry empty; loops refuse unapproved strategies before broker construction
2. Infrastructure-only code changes; minimal, well-tested
3. Honest PASS/WARN/FAIL/BLOCKED documentation
4. No commit of `.env`, tokens, SQLite DBs, raw candle exports, bulky artifacts
5. CAMPAIGN_019 artifacts are read-only context if present

## Start condition (this run)

| Check | Result |
|-------|--------|
| Branch | `infra-shared-signal-and-mtf-confluence-audit-001` (created from clean `main`) |
| Worktree | Clean at audit start (no uncommitted CAMPAIGN_019 mix) |
| `approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_019 artifacts | Present in repo (committed); treated read-only |

## Modules discovered

| Layer | Primary modules | Tests / docs |
|-------|-----------------|--------------|
| Candles / load | `domain/candles.py`, `data/repositories.py`, `data/candle_dedupe.py`, `broker/oanda.py`, `loops.fetch_latest_candles` | `test_d1_aggregation.py`, `test_candle_dedupe` (if any) |
| H4→D1AGG | `backtesting/d1_aggregation.py` | `test_d1_aggregation.py`, `D1_AGGREGATION_DESIGN.md` |
| Weekly HTF | `features/weekly_momentum.py`, `features/weekly_volatility.py` | strategy unit tests |
| Cross-asset align | `research/cross_asset_features/alignment.py` | `test_cross_asset_h4_alignment.py` |
| Indicators | `strategies/indicators.py` | `test_indicators.py`, parity verifier tests |
| Signals | `domain/signals.py`, `strategies/base.py` | `test_strategies.py`, campaign strategy tests |
| Fills | `backtesting/fills.py`, `backtesting/engine.py` | `test_fill_timing.py`, `test_backtest_engine.py` |
| Exits | `backtesting/engine.py` | `test_gap_fill.py`, `test_ambiguous_exit.py`, C019 tests |
| Risk | `risk/sizing.py`, `risk/policy.py`, `risk/exposure.py`, `risk/kill_switch.py` | `test_risk_engine_backtest_parity.py` |
| Financing | `financing.py` | `test_observed_financing.py`, research financing tests |
| Parity | `research/backtrader_lane/`, `backtesting/exporters.py` | backtrader_lane tests, `test_parity_verifier_*` |
| Research freeze | `scripts/check_research_freeze.py`, `research_archive.py` | CI / manual gate |
| Loops / approval | `approval.py`, `loops.py`, `guards.py` | `test_approved_strategies.py` |

## Audit checklist (Phases 1–10)

- [ ] Phase 1: Candle timestamp convention, complete flag, dedupe, D1AGG; no local M1→H1→H4 unless documented
- [ ] Phase 2: HTF join semantics per strategy + cross-asset availability alignment
- [ ] Phase 3: ATR, ADX, RSI, z-score, Donchian, EMA warmup and prior-bar behavior
- [ ] Phase 4: Signal schema, separation from orders/broker, timestamp vs cutoff
- [ ] Phase 5: Long ask / long bid exit; short mirror; fill_timing; no double spread
- [ ] Phase 6: Exit priority chain; C019 thesis_invalidation precedence if enabled
- [ ] Phase 7: Spread source, slippage, 2× stress, financing-unmodeled explicitness
- [ ] Phase 8: EUR_USD / USD_JPY sizing, reject reasons, kill switch
- [ ] Phase 9: Backtrader export schema; Lean optional
- [ ] Phase 10: Campaign validity impact memo (no verdict rewrite)

## Expected tests (this sprint)

- `tests/unit/test_candle_conventions_audit_001.py` — frame index, complete-only, dedupe policy
- `tests/unit/test_htf_backward_alignment_audit_001.py` — synthetic no-lookahead HTF join patterns
- Extensions to `tests/unit/test_indicators.py` — z-score/RSI warmup NaN behavior
- `tests/unit/test_signal_contract_audit_001.py` — signal-only, no broker, timestamp ordering
- `tests/unit/test_fill_price_side_audit_001.py` — explicit bid/ask side rules (if not fully covered)

Existing suites (`test_fill_timing`, `test_d1_aggregation`, `test_backtest_engine`, `test_cross_asset_h4_alignment`, C019 exit tests) are **evidence**, not replaced.

## Expected docs

| Phase | Document |
|-------|----------|
| 0 | This plan |
| 1 | `CANDLE_AGGREGATION_TIMESTAMP_AUDIT_RESULT.md` |
| 2 | `MTF_ALIGNMENT_AUDIT_RESULT.md` |
| 3 | `INDICATOR_CORRECTNESS_AUDIT_RESULT.md` |
| 4 | `SIGNAL_CONTRACT_AUDIT_RESULT.md` |
| 5 | `FILL_TIMING_AND_PRICE_SOURCE_AUDIT_RESULT.md` |
| 6 | `EXECUTION_EVENT_ORDER_AUDIT_RESULT.md` |
| 7 | `COST_SPREAD_SLIPPAGE_FINANCING_AUDIT_RESULT.md` |
| 8 | `RISK_SIZING_PORTFOLIO_CONSTRAINT_AUDIT_RESULT.md` |
| 9 | `PARITY_READINESS_AUDIT_RESULT.md` |
| 10 | `CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_SHARED_AUDIT.md` |
| 11 | `SHARED_SIGNAL_AND_MTF_CONFLUENCE_AUDIT_001_SUMMARY.md` |

## Classification rubric

| Status | Meaning |
|--------|---------|
| **PASS** | Convention documented; tests or prior sprint tests prove safe behavior |
| **WARN** | Probably safe but incomplete evidence, strategy-specific variance, or optimistic default documented |
| **FAIL** | Bug or unsafe behavior found; fix sprint recommended |
| **BLOCKED** | Could not audit (missing data, dirty worktree, external dependency) |

## What counts as BLOCKED for this sprint

- Uncommitted CAMPAIGN_019 execution mixing with audit changes
- Required local SQLite/raw exports missing for a claimed test
- Cannot run baseline pytest / research freeze gates

## Baseline validation (Phase 0)

| Command | Result |
|---------|--------|
| `pytest tests/ -q` | 1713 passed |
| `ruff check src tests scripts research` | All checks passed |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED (value scan skipped — no creds in env) |
| `git status --short` | Clean |

## Explicit non-approval statement

This audit sprint **does not** approve any strategy for paper, demo, or live trading. It **does not** add entries to `configs/approved_strategies.yaml`. Infrastructure PASS results only mean shared layers are understood and tested—not that any campaign edge is real.
