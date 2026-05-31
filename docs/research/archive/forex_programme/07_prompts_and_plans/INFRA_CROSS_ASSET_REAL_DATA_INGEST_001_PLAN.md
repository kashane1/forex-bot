# Infra Cross-Asset Real Data Ingest — Sprint 001 Plan

**Date:** 2026-05-26  
**Branch:** `infra-cross-asset-real-data-ingest-001`  
**Base branch:** `infra-multi-timeframe-confluence-and-cost-atlas-001`  
**Sprint type:** Infrastructure / data only — **not** strategy, campaign, or trading enablement.

> **No strategy approved.** `configs/approved_strategies.yaml` remains `approved: []`. CAMPAIGN_018 will **not** be created. Paper / demo / live remain blocked.

---

## 0. Purpose

Replace the **FIXTURE_ONLY** cross-asset state with real, local, versioned external-feature datasets where possible, using public/read-only data sources (primarily FRED) and strict no-lookahead alignment to H4 research timestamps.

Outputs are **diagnostic data-readiness artifacts** only — not tradable edge, not strategy evidence, not campaign validation.

---

## 1. Non-goals

- New trading strategy or CAMPAIGN_018.
- Strategy campaign execution or confluence lift validation.
- Win-rate, expectancy, or profitability claims.
- Paper / demo / live enablement or strategy approval.
- Order placement, executor, or broker behavior changes.
- OANDA order APIs or live broker credentials.
- Retuning rejected campaigns (C008–C017).
- Wiring confluence into RiskEngine or order-capable loops.
- Paid vendor APIs or fragile web scraping.

---

## 2. Truth audit (Phase 0)

| check | result |
|---|---|
| Base branch | `infra-multi-timeframe-confluence-and-cost-atlas-001` |
| Prior sprint summary | `docs/research/INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_SUMMARY.md` ✓ |
| Cost atlas summary | `research/cost_atlas/cost_atlas_summary.json` ✓ |
| Confluence diagnostics | `research/confluence_diagnostics/confluence_diagnostic_summary.json` ✓ |
| Feature schema | `research/cross_asset_features/feature_schema.md` ✓ |
| Validation protocol | `docs/research/HIGH_PROBABILITY_TRADE_VALIDATION_PROTOCOL.md` ✓ |
| `approved_strategies.yaml` | `approved: []` ✓ |
| CAMPAIGN_018 | absent ✓ |
| `data/external_features/` | empty (gitignored) |
| FRED_API_KEY | checked without printing — absent in CI/agent env |
| Cross-asset status (prior) | `FIXTURE_ONLY`; `cross_asset_missing` = 2,142 / top reason codes |

---

## 3. Safety rules

- Do not edit `configs/approved_strategies.yaml` except to verify `approved: []`.
- Do not change executor/broker behavior.
- Do not commit `.env`, credentials, SQLite DBs, raw candle exports, or bulky downloads.
- Never print or commit `FRED_API_KEY`.
- All manifest artifacts: `strategy_evidence: false`.
- Preserve broad strategy search **PAUSED**.
- Missing data documented honestly — no fake real-data results.

---

## 4. Expected data sources (priority order)

1. **FRED API** — daily macro/market series (free, read-only).
2. **Local CSV** — operator drop path `data/external_features/`.
3. **CFTC COT** — optional/secondary; design + fixture parser only if live access awkward.
4. **OANDA candles** — only if already supported read-only; no order endpoints.

---

## 5. Target series

| feature_id | FRED series | required |
|---|---|---|
| `broad_usd_index` | DTWEXBGS | yes |
| `us_2y_yield` | DGS2 | yes |
| `us_10y_yield` | DGS10 | yes |
| `us_10y_minus_2y` | derived | yes |
| `vix` | VIXCLS | yes |
| `sp500` | SP500 | yes |
| `oil_wti` | DCOILWTICO | yes |
| `nasdaq_composite` | NASDAQCOM | optional |
| `gold` | local CSV only | optional |
| COT positioning | CFTC TFF | optional |

Legacy aliases (`dxy`, `us2y`, `us10y`, `oil`, `nasdaq`) remain mapped for backward compatibility with fixtures and prior diagnostics.

---

## 6. Auth / key handling

- Read `FRED_API_KEY` from environment or local `.env` (never committed).
- If missing: fetcher exits gracefully with `BLOCKED_AUTH_OR_LOCAL_CSV_REQUIRED` report.
- Raw FRED responses cached under `data/external_features/.fred_cache/` (gitignored).
- Compact normalized outputs under `research/cross_asset_features/` when small and policy-compliant.

---

## 7. Local CSV fallback

- Operator places CSVs in `data/external_features/` matching schema in `feature_schema.md`.
- Loader validates columns, monotonic dates, no future-dated rows, duplicate-date policy (`keep_last`).
- Registry documents expected filenames and transforms.

---

## 8. No-lookahead alignment rules

1. Daily close values become available only **after** the source observation date closes.
2. Availability timestamp convention: `observation_date + 1 calendar day @ 00:00 UTC` (conservative).
3. For H4 bar at time `T`, use latest feature where `availability_ts <= T`.
4. Forward-fill only from prior known observations — never backfill from future dates.
5. Weekly COT (if used): availability at report **release** date + documented lag, not Tuesday report date alone.
6. Flag stale values when last observation exceeds registry `max_staleness_days`.

---

## 9. Phase plan

| phase | deliverable | commit |
|---:|---|---|
| 0 | This plan + truth audit | yes |
| 1 | `source_registry.json`, schema hardening, registry docs/tests | yes |
| 2 | FRED fetcher, local CSV loader, runbook, tests | yes |
| 3 | Normalized features, derived series, quality report | yes |
| 4 | H4 alignment script, audit doc, tests | yes |
| 5 | COT design doc (+ fixture parser if practical) | yes |
| 6 | Re-run confluence diagnostics, impact doc | yes |
| 7 | Evidence index / backlog / manifest updates | yes |
| 8 | Final validation + summary | yes |

---

## 10. Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
```

---

## 11. Expected artifacts

| path | purpose |
|---|---|
| `research/cross_asset_features/source_registry.json` | Auditable source definitions |
| `research/cross_asset_features/normalized_features.csv` | Compact normalized wide table |
| `research/cross_asset_features/normalized_features_manifest.json` | Provenance manifest |
| `research/cross_asset_features/feature_quality_report.json` | Coverage / staleness |
| `research/cross_asset_features/h4_aligned_feature_availability.json` | H4 alignment coverage |
| `research/cross_asset_features/fred_fetch_blocked_report.json` | If API key absent |
| `research/confluence_diagnostics/confluence_diagnostic_summary_after_real_cross_asset.json` | Post-ingest diagnostics |
| `docs/research/CROSS_ASSET_*` | Registry, runbook, alignment audit, COT design, impact |

All artifacts: `strategy_evidence: false`.

---

## 12. Blockers / assumptions

| blocker | mitigation |
|---|---|
| `FRED_API_KEY` absent | Implement fetcher + blocked report; local CSV fallback; tests use mocks |
| `data/external_features/` empty | Normalization from FRED when key present; fixtures for unit tests |
| H4 SQLite store gitignored | Alignment/diagnostics use local store when present; tests use synthetic H4 index |
| COT mapping complexity | Design doc + fixture parser only; status `DESIGN_ONLY` |
| Fixture date range (2022-01) vs H4 window (2020+) | Real FRED ingest must cover full research window to eliminate early `cross_asset_missing` |

---

## 13. Recommended next sprint (decision at close)

- Real FRED succeeded + COT design-only → `infra-cot-positioning-feature-ingest-001`
- Real cross-asset + clean diagnostics → `research-c008-mean-reversion-post-mortem-001`
- Financing blocker obvious → `research-financing-modeled-pnl-and-carry-readiness-001`
- FRED/local still blocked → `infra-external-data-ingest-blocker-resolution-001`
