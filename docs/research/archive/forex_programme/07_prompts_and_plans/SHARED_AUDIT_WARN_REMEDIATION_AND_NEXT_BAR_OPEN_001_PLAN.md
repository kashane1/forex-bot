# Shared Audit WARN Remediation and next_bar_open — Plan

**Branch:** `infra-shared-audit-warn-remediation-and-next-bar-open-001`  
**Base:** `infra-shared-signal-and-mtf-confluence-audit-001` @ `1349488`  
**Date:** 2026-05-27

## Purpose

Remediate infrastructure **WARN** findings from Shared Signal and MTF Confluence Audit 001 without running new strategy campaigns or approving strategies. Primary deliverable: a conservative **signal_bar_close vs next_bar_open** comparison on a frozen reference campaign.

## Non-goals

- No CAMPAIGN_020; no strategy tuning; no test lockbox; no paper/demo/live
- No OANDA order APIs; no live credentials; no verdict rewrites
- No CAMPAIGN_019 rule/gate/verdict changes

## WARN items addressed

| WARN | Phase | Action |
|------|-------|--------|
| Fill timing optimistic default | 1–3 | C019 reference comparison runner + result doc |
| No shared MTF adapter | 4 | `forex_bot.features.htf_align` + tests |
| RSI fillna(50) warmup | 5 | `warmup_policy` on `rsi()` — default legacy |
| Signal provenance gaps | 6 | Optional additive `Signal` fields |
| Financing partial | 7 | Next-scope doc only |
| Parity export schema | 8 | Doc + nullable export columns where safe |
| Lean design-only | 8 | Documented; no cloud run |

## Reference campaign (fill timing)

**Primary:** CAMPAIGN_019 (`mean_reversion_thesis_invalidation 0.1.0-c019`)

- Same frozen entry params as C008 (validated in runner)
- `BacktestEngine` supports `fill_timing`; C019 runner omits it → defaults `signal_bar_close` (matches committed artifacts)
- Splits for comparison: **train + validation**, **base cost only** (6 pairs)
- Data: `data/campaign_002.sqlite3`, dedupe `keep_last`, `oanda-practice` source

**Fallback:** CAMPAIGN_008 runner pattern — **not needed**; C019 is safe for dual-mode runs with only `fill_timing` varied.

## Safety rules

1. `configs/approved_strategies.yaml` stays `approved: []`
2. Comparison script: local SQLite only, no broker
3. Compact artifacts under `research/fill_timing_reference_comparison/`; large trades in gitignored `local_trades/`
4. `strategy_evidence: false`, `not_approved: true`, `test_lockbox_opened: false`

## Expected artifacts

| Path | Phase |
|------|-------|
| `docs/research/NEXT_BAR_OPEN_REFERENCE_COMPARISON_DESIGN.md` | 1 |
| `scripts/compare_fill_timing_reference_campaign.py` | 2 |
| `research/fill_timing_reference_comparison/*.json` | 3 |
| `docs/research/NEXT_BAR_OPEN_REFERENCE_COMPARISON_RESULT.md` | 3 |
| `src/forex_bot/features/htf_align.py` | 4 |
| `docs/research/RSI_WARMUP_POLICY_REMEDIATION_RESULT.md` | 5 |
| `docs/research/SIGNAL_PROVENANCE_FIELDS_REMEDIATION_RESULT.md` | 6 |
| `docs/research/OBSERVED_COST_FINANCING_OVERLAY_NEXT_SCOPE.md` | 7 |
| `docs/research/PARITY_EXPORT_SCHEMA_REMEDIATION_RESULT.md` | 8 |
| `docs/research/CAMPAIGN_VALIDITY_IMPACT_MEMO_AFTER_WARN_REMEDIATION.md` | 9 |

## Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

## Explicit non-approval statement

This sprint produces **infrastructure evidence only**. It does not approve any strategy or enable paper/demo/live trading.
