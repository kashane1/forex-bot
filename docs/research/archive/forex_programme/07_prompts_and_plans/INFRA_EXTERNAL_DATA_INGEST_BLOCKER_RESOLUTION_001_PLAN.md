# Infra External Data Ingest Blocker Resolution — Sprint 001 Plan

**Date:** 2026-05-26  
**Branch:** `infra-external-data-ingest-blocker-resolution-001`  
**Base branch:** `infra-cross-asset-real-data-ingest-001`  
**Sprint type:** Infrastructure / data only — **not** strategy, campaign, or trading enablement.

> **No strategy approved.** `configs/approved_strategies.yaml` remains `approved: []`. CAMPAIGN_018 will **not** be created. Paper / demo / live remain blocked.

---

## 0. Purpose

Resolve the real external-data blocker from `infra-cross-asset-real-data-ingest-001` by running the existing FRED/local-CSV pipeline against the **full H4 research window**, producing complete normalized and H4-aligned cross-asset features — or documenting the remaining blocker honestly.

---

## 1. Non-goals

- Strategy, CAMPAIGN_018, confluence lift validation, win-rate/expectancy/PF by bucket.
- Paper / demo / live enablement; executor/broker changes; OANDA order APIs.
- Retuning rejected campaigns; optimized feature windows.

---

## 2. Source state (Phase 0 truth audit)

| check | result |
|---|---|
| Prior sprint summary | `docs/research/INFRA_CROSS_ASSET_REAL_DATA_INGEST_001_SUMMARY.md` ✓ |
| Source registry | `research/cross_asset_features/source_registry.json` ✓ |
| FRED runbook | `docs/research/CROSS_ASSET_FRED_INGEST_RUNBOOK.md` ✓ |
| Prior blocked report | `research/cross_asset_features/fred_fetch_blocked_report.json` ✓ |
| Prior diagnostic impact | `docs/research/CROSS_ASSET_REAL_DATA_DIAGNOSTIC_IMPACT.md` ✓ |
| H4 alignment sample | `research/cross_asset_features/h4_aligned_feature_availability.json` ✓ |
| Prior diagnostics | `confluence_diagnostic_summary_after_real_cross_asset.json` ✓ |
| `approved_strategies.yaml` | `approved: []` ✓ |
| CAMPAIGN_018 | absent ✓ |
| `FRED_API_KEY` | **absent** (checked via env + dotenv; not printed) |
| `data/external_features/` | **absent** — no manual CSVs |
| H4 SQLite store | `data/campaign_002.sqlite3` present |
| H4 union range | **2020-01-01 22:00 UTC → 2026-05-24 21:00 UTC** (~9,954 bars/pair) |
| Prior `cross_asset_missing` | **2,142** (fixture window 2022-01 only) |

---

## 3. Target date range

| parameter | value | rationale |
|---|---|---|
| `observation_start` | **2018-01-01** | Warmup before H4 start (2020-01) for derived 1d changes |
| `observation_end` | **2026-05-24** | Matches latest H4 bar date in local store |
| H4 research window | 2020-01-01 → 2026-05-24 | Seven-pair union from SQLite |

---

## 4. Target FRED series (from registry)

| feature_id | FRED ID | required |
|---|---|---|
| `broad_usd_index` | DTWEXBGS | yes |
| `us_2y_yield` | DGS2 | yes |
| `us_10y_yield` | DGS10 | yes |
| `vix` | VIXCLS | yes |
| `sp500` | SP500 | yes |
| `oil_wti` | DCOILWTICO | yes |
| `nasdaq_composite` | NASDAQCOM | optional |
| `gold` | local CSV only | optional — MANUAL_CSV_REQUIRED |

Derived: `us_10y_minus_2y`, 1d change/return columns (deterministic, existing).

---

## 5. Expected outputs

| path | purpose |
|---|---|
| `fred_fetch_status_real_window.json` | Per-series fetch status for target window |
| `docs/research/FRED_REAL_WINDOW_FETCH_RESULT.md` | Human-readable fetch result |
| `docs/research/EXTERNAL_DATA_INGEST_STILL_BLOCKED.md` | If FRED key absent |
| `local_csv_fallback_status.json` | Local CSV scan/validation status |
| `docs/research/EXTERNAL_FEATURE_LOCAL_CSV_TEMPLATE.md` | Manual drop template |
| Updated `normalized_features.csv` / manifest / quality report | Full-window real data (when unblocked) |
| `h4_aligned_feature_availability.json` | Full-window alignment coverage |
| `docs/research/CROSS_ASSET_H4_ALIGNMENT_AUDIT_FULL_WINDOW.md` | Alignment audit |
| `confluence_diagnostic_summary_full_window_cross_asset.json` | Post-resolution diagnostics |
| `docs/research/EXTERNAL_DATA_BLOCKER_RESOLUTION_DIAGNOSTIC_IMPACT.md` | Impact comparison |

All artifacts: `strategy_evidence: false`.

---

## 6. Safety rules

- Never print or commit `FRED_API_KEY`, `.env`, credentials, SQLite DBs, raw API dumps.
- Gitignore FRED cache under `data/external_features/.fred_cache/`.
- Commit compact normalized CSV/manifests only when they contain real full-window data.
- No fake coverage — document missing data honestly.

---

## 7. No-lookahead requirements

- Daily observation `D` → available `D+1 00:00 UTC`.
- H4 bar uses observations with `availability_ts <= bar_time` only.
- Forward-fill from prior observations; stale flags beyond `max_staleness_days`.

---

## 8. Fallback plan (FRED unavailable)

1. Document blocker in `EXTERNAL_DATA_INGEST_STILL_BLOCKED.md`.
2. Harden local CSV validation + template.
3. Do **not** invent data; do **not** claim full-window coverage from fixtures.
4. Re-run diagnostics on available data; report unchanged `cross_asset_missing`.
5. Recommend `infra-external-data-credentials-or-manual-csv-setup-001`.

---

## 9. Phase plan

| phase | deliverable |
|---:|---|
| 0 | This plan + truth audit |
| 1 | FRED fetch (or blocked docs + status JSON) |
| 2 | Local CSV fallback hardening + template |
| 3 | Normalize / derive / quality (full-window when unblocked) |
| 4 | H4 alignment audit full window |
| 5 | Confluence diagnostics comparison |
| 6 | COT status update (if needed) |
| 7 | Archive / backlog updates |
| 8 | Final validation + summary |

---

## 10. Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
```
