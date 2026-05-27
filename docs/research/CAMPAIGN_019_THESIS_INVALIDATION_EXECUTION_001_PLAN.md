# CAMPAIGN_019 Thesis Invalidation Execution 001 — Plan

**Branch:** `research-campaign-019-thesis-invalidation-execution-001`  
**Date:** 2026-05-27  
**Evidence class:** `strategy_evidence: true`, `not_approved: true`

---

## Purpose

Implement and run precommitted CAMPAIGN_019 (`mean_reversion_thesis_invalidation 0.1.0-c019`) with
z-score continuation thesis-invalidation exit on frozen C008 entries.

---

## Source precommit docs

- `EXIT_HYPOTHESIS_PRECOMMIT_002_SUMMARY.md`
- `CAMPAIGN_019_PRECOMMIT_EXIT_HYPOTHESIS_SCOPE.md`
- `CAMPAIGN_019_EXIT_HYPOTHESIS_GATE_DESIGN.md`
- `CAMPAIGN_019_EXIT_HYPOTHESIS_IMPLEMENTATION_DESIGN.md`

---

## Frozen scope

- Entry: identical C008 (ADX<20, z±2.0+RSI, 6-pair H4, 0.25% risk)
- Exit: 1.5× ATR stop, 40-bar time, no target/protective/trail
- New: long z≤−3.0 / short z≥+3.0 → `thesis_invalidation` at bar close
- Priority: thesis_invalidation → stop → time → EOD

---

## Non-goals

No tuning, approval, paper/demo/live, executor/broker changes, OANDA APIs.

---

## Gate plan

Precommitted screening + optional test lockbox; Backtrader parity ±1 trade required before lockbox.

---

## Expected artifacts

`research/campaign_019/*.json`, backtests gitignored CSVs, parity `c019_parity_summary.json`.

---

## Phase 0 truth audit

| check | status |
|---|---|
| Precommit docs | Present |
| `approved: []` | Confirmed |
| Deduped DB | `data/campaign_002.sqlite3` |
| C008/C009/C018 baselines | Present |

---

## Blocked conditions

`BLOCKED_PRECOMMIT_AMBIGUITY` if exit rule cannot be implemented without scope change.
