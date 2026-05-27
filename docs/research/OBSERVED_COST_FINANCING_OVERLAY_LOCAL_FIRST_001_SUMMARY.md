# Observed Cost / Financing Overlay Local-First — Summary

**Branch:** `infra-observed-cost-financing-overlay-local-first-001`  
**Base:** `infra-shared-audit-warn-remediation-and-next-bar-open-001` @ `8a96f41`  
**Date:** 2026-05-27

## 1. Branch name

`infra-observed-cost-financing-overlay-local-first-001`

## 2. Commit hashes by phase

| Phase | Commit | Description |
|-------|--------|-------------|
| 0 | _(see git log)_ | Plan + baseline |
| 1 | _(see git log)_ | Ledger inventory |
| 2–3 | _(see git log)_ | Contract, fixtures, module, tests |
| 4 | _(see git log)_ | Overlay runner script |
| 5 | _(see git log)_ | Overlay artifacts + result doc |
| 6–8 | _(see git log)_ | Linkage, validity, future capture prompt |
| 9 | _(see git log)_ | Evidence index / manifest / backlog |
| 10 | _(see git log)_ | Final summary |

## 3. Files changed by phase

| Phase | Key paths |
|-------|-----------|
| 0 | `docs/research/OBSERVED_COST_FINANCING_OVERLAY_LOCAL_FIRST_001_PLAN.md` |
| 1 | `docs/research/FINANCING_OVERLAY_LEDGER_INVENTORY.md` |
| 2 | `src/forex_bot/research/financing_overlay.py`, `docs/research/FINANCING_OVERLAY_CONTRACT.md`, `tests/unit/test_financing_overlay_local_first.py` |
| 3 | `docs/research/FINANCING_FIXTURE_SUPPORT_LOCAL_FIRST_RESULT.md` |
| 4 | `scripts/apply_financing_overlay_to_trade_ledgers.py`, `.gitignore` |
| 5 | `research/financing_overlay_local_first/*`, `docs/research/FINANCING_OVERLAY_LOCAL_FIRST_RESULT.md` |
| 6–8 | Linkage, validity memo, capture prompt docs |
| 9 | `EVIDENCE_INDEX.md`, `EVIDENCE_MANIFEST.json`, `FUTURE_RESEARCH_BACKLOG.md` |
| 10 | This summary |

## 4. Baseline validation result

| Check | Result |
|-------|--------|
| pytest | 1753 passed (after sprint tests) |
| ruff | PASS (fixed imports) |
| research freeze | PASS |
| research archive | PASS (after summary committed) |
| secret scan | PASS (pattern) |

## 5. Existing financing modules inspected

`src/forex_bot/financing.py`, `research/financing/{overlay,calculator,models,rates,fixtures}.py`, prior `c008_c009_c018_financing_exposure.json`.

## 6. Trade ledger inventory summary

Six campaign families scanned (C008, C015, C016, C017, C018, C019); all trade CSVs overlay-ready with timestamps, units, R, PnL. See `FINANCING_OVERLAY_LEDGER_INVENTORY.md`.

## 7. Selected reference ledgers

C019 train+validation base, C016 weekly folds base, C017 weekly folds base, C008 deduped forensic train.

## 8. Financing overlay contract summary

Modes: `none`, `synthetic_fixture`, `manual_observed_fixture`, `unavailable`. Outputs: financing_home/r, adjusted metrics, hold buckets, warnings. Module: `src/forex_bot/research/financing_overlay.py`.

## 9. Fixture support summary

Synthetic stress via `default_stress_rate_source()`; manual mode merges `research/financing/fixtures/rates_two_week_*.json` with explicit synthetic labeling.

## 10. Overlay modes supported

All four modes implemented; primary run uses `none` + `synthetic_fixture` + `manual_observed_fixture`.

## 11. Commands run

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
python scripts/apply_financing_overlay_to_trade_ledgers.py --inventory-only
python scripts/apply_financing_overlay_to_trade_ledgers.py
```

## 12. Synthetic fixture result summary

| Ledger | Gross E[R] | Adjusted E[R] | Financing drag |
|--------|------------|---------------|----------------|
| c019_train_validation_base | -0.007 | -0.089 | -0.082 |
| c016_weekly_momentum_folds_base | -0.063 | -0.115 | -0.052 |
| c017_weekly_vol_breakout_folds_base | -0.023 | -0.067 | -0.044 |
| c008_deduped_forensic_train | -0.025 | -0.105 | -0.080 |

## 13. Manual observed fixture result summary

Manual fixture mode runs with same committed JSON tables; warnings label data as **diagnostic synthetic**, not broker-observed. Use for schema validation only until read-only capture sprint.

## 14–16. Campaign / pair / hold-bucket deltas

See `research/financing_overlay_local_first/overlay_summary_by_campaign.json`, `overlay_summary_by_pair.csv`, `overlay_summary_by_hold_bucket.csv`. Hold buckets **3–7d** and **7d+** accumulate largest financing drag.

## 17. Spread/cost linkage summary

Pair-level join to `research/cost_atlas/` possible; session/weekday per-trade join deferred. See `SPREAD_COST_AND_FINANCING_SENSITIVITY_LINKAGE.md`.

## 18. Campaign validity impact

Multi-day/weekly gross R is optimistic without financing overlay. **No verdict changes.** C019 remains REJECT; financing reinforces carry understatement.

## 19. Observed financing rerun required?

**Yes** for future promotion review of multi-day/weekly strategies — via read-only capture sprint, not synthetic stress alone.

## 20. C019 interpretation changes?

**No formal verdict change.** Research interpretation: gross metrics understate carry cost (~0.08R drag under stress); `next_bar_open` fill timing remains the larger validity issue.

## 21. CAMPAIGN_020 created?

**No.**

## 22. Strategy approved?

**No.** `approved: []`.

## 23. Paper/demo/live blocked?

**Yes.**

## 24. Executor/broker behavior changed?

**No.**

## 25. OANDA order APIs called?

**No.**

## 26. Credentials/secrets committed?

**No.**

## 27. SQLite/raw/bulky artifacts staged?

**No.**

## 28. Tests added

`tests/unit/test_financing_overlay_local_first.py` (9 tests).

## 29. Validation commands run

Listed in §11 — all PASS at sprint close.

## 30. Remaining WARN/BLOCKED items

- Financing: observed broker rates still missing (BLOCKED on human-authorized capture)
- Fill timing: approval-bound campaigns should use `next_bar_open`
- HTF align: `htf_align.align_last_completed()` not broadly migrated
- Parity: Backtrader preferred; Lean retired

## 31. Recommended next sprint

`infra-observed-financing-capture-readonly-002` — read-only practice financing transaction capture per `OBSERVED_FINANCING_CAPTURE_READ_ONLY_NEXT_PROMPT.md`.

## 32. Files to review first

1. `docs/research/FINANCING_OVERLAY_LOCAL_FIRST_RESULT.md`
2. `research/financing_overlay_local_first/adjusted_metric_delta.json`
3. `src/forex_bot/research/financing_overlay.py`
4. `docs/research/CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_FINANCING_OVERLAY_LOCAL_FIRST.md`
5. `scripts/apply_financing_overlay_to_trade_ledgers.py`

## Compact table

| Ledger | Financing Mode | Trades | Avg Hold Days | Financing ΔR | Adjusted Exp R | Sensitive Pairs | Interpretation Change | Follow-up |
|--------|----------------|--------|---------------|--------------|----------------|-----------------|----------------------|-----------|
| c019_train_validation_base | synthetic_fixture | 357 | 3.19 | -0.082 | -0.089 | JPY/CAD legs (see pair CSV) | No verdict change; gross optimistic | Observed capture |
| c016_weekly_momentum_folds_base | synthetic_fixture | 137 | 4.00 | -0.052 | -0.115 | Long-hold USD/JPY rows | Weekly gross understated | Observed capture |
| c017_weekly_vol_breakout_folds_base | synthetic_fixture | 230 | 5.87 | -0.044 | -0.067 | Multi-day fold trades | Weekly gross understated | Observed capture |
| c008_deduped_forensic_train | synthetic_fixture | 216 | 3.13 | -0.080 | -0.105 | Aligns with prior exposure JSON | C008 REJECT unchanged | Observed capture |

## No-approval statement

This sprint does not approve any strategy, enable trading loops, or change campaign verdicts. Synthetic financing is diagnostic only.
