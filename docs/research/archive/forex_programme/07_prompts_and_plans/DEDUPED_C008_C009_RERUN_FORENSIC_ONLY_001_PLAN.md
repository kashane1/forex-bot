# Deduped C008/C009 Rerun — Forensic Only Sprint 001 Plan

**Date:** 2026-05-26  
**Branch:** `infra-deduped-c008-c009-rerun-forensic-only-001`  
**Base branch:** `research-stop-and-exit-diagnostics-001`

> **Forensic replay only** — `strategy_evidence: false`. No strategy approved. No CAMPAIGN_018. C008/C009 verdicts remain **REJECT** unless a separate future process says otherwise.

---

## Purpose

Re-run CAMPAIGN_008 and CAMPAIGN_009 with **deduped candle inputs** and **frozen original rules** to determine whether existing C008/C009 findings are reproducible on clean inputs after the canonical candle-dedupe fix (`30b4654`).

## Non-goals

- Approve C008, C009, or any exit variant.
- Create CAMPAIGN_018 or a new strategy family.
- Retune entries, exits, stops, targets, pairs, sessions, or filters.
- Open the 2025–2026 test lockbox.
- Enable paper/demo/live.
- Claim profitability or promotion eligibility.

## Frozen-rule requirements

| campaign | version | exit change vs C008 |
|---|---|---|
| C008 | `mean_reversion 0.1.0-c008` | none — hard stop or 40-bar time stop |
| C009 | `mean_reversion 0.2.0-c009` | **`midline_exit: true` only** |

Configs must match committed YAML verbatim. Any parameter mismatch aborts before replay.

## Source artifacts

### Prior stop/exit diagnostics (verified)

- `docs/research/STOP_AND_EXIT_DIAGNOSTICS_001_SUMMARY.md`
- `docs/research/CROSS_CAMPAIGN_EXIT_PATHOLOGY_MATRIX.md`
- `docs/research/C008_C009_EXIT_FORENSICS.md`
- `docs/research/STOP_DISTANCE_AND_ADVERSE_EXCURSION_DIAGNOSTICS.md`
- `docs/research/FUTURE_EXIT_RESEARCH_GATE.md`
- `research/exit_diagnostics/c008_c009_exit_forensics.json`
- `research/exit_diagnostics/stop_distance_adverse_excursion.json`

### Original C008/C009

| item | path |
|---|---|
| C008 precommit | `docs/research/CAMPAIGN_008_RANGE_MEAN_REVERSION_PRECOMMIT.md` |
| C009 precommit | `docs/research/CAMPAIGN_009_PRECOMMIT.md` |
| C008 config | `configs/campaign_008_range_mean_reversion.yaml` |
| C009 config | `configs/campaign_009_mean_reversion.yaml` |
| C008 report | `backtests/CAMPAIGN_008_RANGE_MEAN_REVERSION_REPORT.md` |
| C009 report | `backtests/CAMPAIGN_009_MEAN_REVERSION_REPORT.md` |
| C008 index | `backtests/campaign_008_range_mean_reversion/runs/_index.json` |
| C009 index | `backtests/campaign_009_mean_reversion/runs/_index.json` |
| Strategy | `src/forex_bot/strategies/mean_reversion.py` |
| Contamination | `research/contamination_audit/campaign_integrity_classification.json` |

## Dedupe requirements

- Load candles via `CandleRepo.list()` / `list_with_dedupe_stats()` — same boundary as C011–C017 dedup-safe campaigns.
- Policy: `keep_last` on `(instrument, granularity, UTC time)` — `src/forex_bot/data/candle_dedupe.py`.
- Preflight must record duplicate rows detected/dropped per pair/split.
- Output classification: `DEDUPED_INPUT`.

## Evidence-integrity caveats

- Original C008/C009 runs predated dedupe fix → **LIKELY_CONTAMINATED**.
- Deduped replay may change **trade counts and entry timing** (duplicate bars affected indicators).
- Data-request hashes will differ if candle counts change — expected, not a failure.
- Trade CSVs from original runs remain contaminated-era ledger; deduped replay produces a **new forensic ledger**.
- Test lockbox remains **closed** regardless of deduped validation metrics.

## No-retune / no-approval rules

Frozen configs only. No parameter selection from validation winners. All outputs marked `strategy_evidence: false`, `forensic_only: true`.

## Phase plan

| phase | deliverable |
|---:|---|
| 0 | This plan |
| 1 | `frozen_config_reconstruction.json`, `C008_C009_FROZEN_CONFIG_RECONSTRUCTION.md` |
| 2 | `scripts/rerun_c008_c009_deduped_forensic.py` + tests |
| 3 | Execute replay, `C008_C009_DEDUPED_FORENSIC_REPLAY_RESULTS.md` |
| 4 | `old_vs_deduped_metric_comparison.json`, comparison doc |
| 5 | deduped exit anatomy + MAE/MFE refresh |
| 6 | `C008_C009_EVIDENCE_INTEGRITY_DECISION.md` |
| 7 | archive/backlog updates |
| 8 | summary + validation |

## Expected outputs

```
research/deduped_c008_c009_rerun/
  frozen_config_reconstruction.json
  metrics_summary.json
  gate_result.json
  run_manifest.json
  evidence_status.json
  old_vs_deduped_metric_comparison.json
  deduped_exit_anatomy.json
  deduped_mae_mfe.json

backtests/CAMPAIGN_008_mean_reversion_deduped_forensic/   (gitignored trade CSVs)
backtests/CAMPAIGN_009_mean_reversion_midline_deduped_forensic/
```

## Blocked conditions

| condition | action |
|---|---|
| Config cannot be reconstructed exactly | `BLOCKED_EXACT_CONFIG_NOT_RECONSTRUCTED` — stop replay |
| SQLite store missing | `BLOCKED_DATA_STORE_MISSING` |
| Non-oanda-practice source | abort per original runners |
| Test window opened | **forbidden** — abort if attempted |

## Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
python scripts/rerun_c008_c009_deduped_forensic.py --help
```
