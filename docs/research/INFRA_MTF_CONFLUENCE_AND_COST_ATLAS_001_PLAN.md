# Infra MTF Confluence and Cost Atlas — Sprint 001 Plan

**Date:** 2026-05-26  
**Branch:** `infra-multi-timeframe-confluence-and-cost-atlas-001`  
**Base branch:** `research-pro-alpha-confluence-and-asset-expansion-roadmap-001`  
**Sprint type:** Implementation infrastructure — **not** strategy, campaign, or trading enablement.

> **No strategy approved.** `configs/approved_strategies.yaml` remains `approved: []`. CAMPAIGN_018 will **not** be created. Paper / demo / live remain blocked.

---

## 0. Purpose

Implement the first three layers of the pro-alpha trade-quality stack:

1. **Cost atlas / spread diagnostics** — observed spread/ATR by pair, session, weekday, vol regime, fold.
2. **Multi-timeframe confluence prototype** — research-only `ConfluenceScore` grader (A/B/C/REJECT).
3. **Cross-asset feature ingest scaffolding** — local CSV schema, loader, H4 alignment (fixtures only unless operator supplies data).

Outputs are **diagnostic infrastructure** and future research-gating recommendations only — not tradable edge.

---

## 1. Non-goals

- New trading strategy or CAMPAIGN_018.
- Paper / demo / live enablement or strategy approval.
- Order placement or broker execution changes.
- Retuning CAMPAIGN_015–017 or C008/C009.
- OANDA order APIs or live broker credentials.
- Kelly sizing, exit optimization, or confluence threshold tuning on rejected campaigns.
- Claiming confluence improves win rate or expectancy without pre-registered validation.

---

## 2. Architecture rule (binding)

```text
market data
  -> strategy/research feature layer
  -> Signal.features / ConfluenceScore
  -> RiskEngine evaluation
  -> executor/broker
```

The executor stays **dumb**. This sprint does not wire confluence into executor or broker.

---

## 3. Data sources

| source | use | dedupe |
|---|---|---|
| `data/campaign_002.sqlite3` | Seven-pair H4 bid/ask (gitignored locally) | `CandleRepo.list()` → `keep_last` |
| `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json` | Fold window metadata | n/a |
| `tests/fixtures/cross_asset/*.csv` | Cross-asset feature fixtures | n/a |
| `data/external_features/` (operator-local, gitignored) | Real cross-asset CSVs if present | n/a |

Fallback: synthetic candle fixtures when SQLite absent → `docs/research/COST_ATLAS_DATA_BLOCKED.md`.

---

## 4. Safety rules

- Do not edit `configs/approved_strategies.yaml` except to verify `approved: []`.
- Do not change executor/broker behavior.
- Do not commit `.env`, credentials, SQLite DBs, raw candle exports, or API tokens.
- All manifest artifacts: `strategy_evidence: false`.
- Preserve broad strategy search **PAUSED**.

---

## 5. Phase plan

| phase | deliverable | commit |
|---:|---|---|
| 0 | This plan + truth audit | yes |
| 1 | `research/cost_atlas/` + tests + compact outputs | yes |
| 2 | `research/confluence/` + tests + design notes | yes |
| 3 | `research/cross_asset_features/` + fixtures + tests | yes |
| 4 | `scripts/run_mtf_confluence_diagnostics.py` + diagnostic outputs | yes |
| 5 | `HIGH_PROBABILITY_TRADE_VALIDATION_PROTOCOL.md` | yes |
| 6 | EVIDENCE_INDEX, FUTURE_RESEARCH_BACKLOG, EVIDENCE_MANIFEST | yes |
| 7 | Summary + final validation | yes |

---

## 6. Expected artifacts

| path | phase |
|---|---|
| `research/cost_atlas/cost_atlas_summary.json` | 1 |
| `research/cost_atlas/cost_hostile_windows.json` | 1 |
| `research/cost_atlas/pair_session_spread_atr.csv` | 1 |
| `research/cost_atlas/README.md` | 1 |
| `research/confluence/` (module) | 2 |
| `docs/research/MTF_CONFLUENCE_PROTOTYPE_DESIGN_NOTES.md` | 2 |
| `research/cross_asset_features/` | 3 |
| `tests/fixtures/cross_asset/` | 3 |
| `research/confluence_diagnostics/` | 4 |
| `docs/research/MTF_CONFLUENCE_AND_COST_ATLAS_DIAGNOSTICS_001.md` | 4 |
| `docs/research/HIGH_PROBABILITY_TRADE_VALIDATION_PROTOCOL.md` | 5 |
| `docs/research/INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_SUMMARY.md` | 7 |

---

## 7. Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
```

---

## 8. Blockers / assumptions

| assumption | fallback |
|---|---|
| Local `data/campaign_002.sqlite3` exists | Fixture-backed tests; `COST_ATLAS_DATA_BLOCKED.md` |
| Walk-forward `plan.json` committed | Fold columns null in atlas |
| No `data/external_features/` CSVs | Fixture-only cross-asset tests; `BLOCKED_LOCAL_DATA_REQUIRED` in availability report |
| D1 from H4 aggregation for confluence | Synthetic D1 from H4 resample in prototype |

---

## 9. Phase 0 truth audit

| check | status |
|---|---|
| Base branch | `research-pro-alpha-confluence-and-asset-expansion-roadmap-001` @ `09909bd` |
| Roadmap docs (6) | present |
| `approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_018 | absent |
| Local H4 SQLite | present (~133 MB, operator-local, gitignored) |
| Fold plan | `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json` |
