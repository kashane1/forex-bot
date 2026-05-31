# Infra MTF Confluence and Cost Atlas — Sprint 001 Summary

**Date:** 2026-05-26  
**Branch:** `infra-multi-timeframe-confluence-and-cost-atlas-001`  
**Base:** `research-pro-alpha-confluence-and-asset-expansion-roadmap-001`

> **No strategy approved.** `configs/approved_strategies.yaml` remains `approved: []`. CAMPAIGN_018 was **not** created. Paper / demo / live remain blocked. Executor / broker behavior **unchanged**.

---

## 1. Branch name

`infra-multi-timeframe-confluence-and-cost-atlas-001`

---

## 2. Commit hashes by phase

| phase | hash | message |
|---:|---|---|
| 0 | `8560bcd` | docs: add infra mtf confluence and cost atlas sprint plan |
| 1 | `418af0f` | feat: add H4 cost atlas spread diagnostics infrastructure |
| 2 | `fa87b58` | feat: add multi-timeframe confluence research prototype |
| 3 | `9d71e2b` | feat: add cross-asset feature ingest scaffolding |
| 4 | `fbdbf10` | feat: add mtf confluence diagnostic runner and outputs |
| 5 | `1242776` | docs: add high probability trade validation protocol |
| 6 | (this commit) | docs: register infra mtf confluence sprint in research archive |
| 7 | (this commit) | docs: close out infra mtf confluence and cost atlas sprint |

---

## 3. Files changed by phase

| phase | key paths |
|---:|---|
| 0 | `docs/research/INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_PLAN.md` |
| 1 | `research/cost_atlas/`, `scripts/build_cost_atlas.py`, `tests/research/test_cost_atlas.py` |
| 2 | `research/confluence/`, `tests/research/test_confluence.py`, `docs/research/MTF_CONFLUENCE_PROTOTYPE_DESIGN_NOTES.md` |
| 3 | `research/cross_asset_features/`, `tests/fixtures/cross_asset/`, `tests/research/test_cross_asset_features.py` |
| 4 | `scripts/run_mtf_confluence_diagnostics.py`, `research/confluence_diagnostics/` |
| 5 | `docs/research/HIGH_PROBABILITY_TRADE_VALIDATION_PROTOCOL.md` |
| 6 | `docs/research/EVIDENCE_INDEX.md`, `FUTURE_RESEARCH_BACKLOG.md`, `EVIDENCE_MANIFEST.json` |
| 7 | this summary |

---

## 4. What was implemented

- **Cost atlas:** deduped H4 bid/ask loader via `CandleRepo`, per-bar spread/ATR/session/vol metrics, aggregations, hostile-window flags, compact JSON/CSV outputs.
- **MTF confluence prototype:** `research/confluence/` with `ConfluenceScore`, deterministic HTF states, divergence helper, A/B/C/REJECT grader with reason codes.
- **Cross-asset scaffolding:** CSV schema, loader, H4 forward-fill alignment, fixtures, availability report.
- **Diagnostic runner:** samples confluence grades across seven pairs; writes summary JSON + reason-code CSV.
- **Validation protocol:** pre-registration template for future lift tests.

---

## 5. What was deliberately not implemented

- New trading strategy or CAMPAIGN_018.
- Paper/demo/live enablement or `approved_strategies.yaml` edits.
- Executor/broker changes or OANDA order API calls.
- Retuning C015–C017 or C008/C009.
- RiskEngine wiring or Kelly sizing.
- Confluence threshold optimization or expectancy claims.

---

## 6. Cost atlas status

**Complete** on local real data.

| metric | value |
|---|---|
| bars analyzed | 69,648 |
| pairs | 7 |
| dedupe policy | `keep_last` |
| global median spread (pips) | ~1.7 |
| global median spread/ATR (%) | ~6.1 |
| outputs | `research/cost_atlas/cost_atlas_summary.json`, `cost_hostile_windows.json`, `pair_session_spread_atr.csv` |

---

## 7. MTF confluence prototype status

**Complete** — research module only, not wired to executor.

Diagnostic grade distribution (6,916 contexts, sample every 20 bars):

| grade | count |
|---|---:|
| A | 1,533 |
| B | 4,836 |
| REJECT | 394 |
| C | 153 |

Top reason codes: `d1_aligned`, `grade_b`, `usd_headwind`, `cross_asset_missing`.

---

## 8. Cross-asset feature ingest status

**Scaffolding complete; real data absent.**

- `data/external_features/` not present → status **FIXTURE_ONLY**
- Fixtures committed under `tests/fixtures/cross_asset/`
- Availability report: `research/cross_asset_features/feature_availability_report.json`

---

## 9. Local real data availability

| data | available |
|---|---|
| H4 SQLite (`data/campaign_002.sqlite3`) | **yes** (operator-local, gitignored) |
| Walk-forward fold plan | **yes** (committed) |
| Cross-asset real CSVs | **no** |

---

## 10. Fixture-only portions

- Cross-asset features in diagnostics (falls back to `tests/fixtures/cross_asset/`)
- Unit tests for cost atlas, confluence, cross-asset (synthetic/fixture DB)

---

## 11. Diagnostic outputs created

- `research/confluence_diagnostics/confluence_diagnostic_summary.json`
- `research/confluence_diagnostics/confluence_reason_code_counts.csv`
- `docs/research/MTF_CONFLUENCE_AND_COST_ATLAS_DIAGNOSTICS_001.md`

---

## 12. Test / validation results

| command | result |
|---|---|
| `pytest tests/ -q` | pass (see phase 7 run) |
| `ruff check src tests scripts research` | pass |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED |

---

## 13. No strategy approved

`configs/approved_strategies.yaml` → `approved: []`

---

## 14. CAMPAIGN_018 not created

No CAMPAIGN_018 artifacts or configs.

---

## 15. Paper/demo/live remain blocked

Research freeze `loops_refuse` PASS.

---

## 16. Executor/broker unchanged

No changes under `src/forex_bot/execution/` or `src/forex_bot/broker/`.

---

## 17. No broker order API calls

Read-only SQLite candle loads and local CSV fixtures only.

---

## 18. Research archive / freeze status

Archive and freeze gates pass after registry update. All new artifacts flagged `strategy_evidence: false`.

---

## 19. Remaining blockers

| blocker | next action |
|---|---|
| Cross-asset real CSVs missing | `infra-cross-asset-real-data-ingest-001` |
| D1/W1 from broker candles (CAMPAIGN_006) | synthetic D1/W1 from H4 used in prototype |
| Financing in engine PnL | future financing sprint |
| Confluence lift not validated | requires pre-registered campaign per validation protocol |

---

## 20. Recommended next sprint

**`infra-cross-asset-real-data-ingest-001`**

**Why:** Cost atlas is complete; confluence diagnostics show `cross_asset_missing` for a large share of contexts because only fixtures exist. Real DXY/yields/VIX CSVs unlock meaningful cross-asset gating research without starting a strategy campaign.

Alternatives deferred: C008 post-mortem (`research-c008-mean-reversion-post-mortem-001`), financing readiness (`research-financing-modeled-pnl-and-carry-readiness-001`).

---

## 21. Files to review first

1. [`docs/research/INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_SUMMARY.md`](INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_SUMMARY.md) — this document
2. [`research/cost_atlas/cost_atlas_summary.json`](../../research/cost_atlas/cost_atlas_summary.json) — cost distributions
3. [`research/confluence_diagnostics/confluence_diagnostic_summary.json`](../../research/confluence_diagnostics/confluence_diagnostic_summary.json) — grade/reason distribution
4. [`research/confluence/grader.py`](../../research/confluence/grader.py) — grading logic
5. [`docs/research/HIGH_PROBABILITY_TRADE_VALIDATION_PROTOCOL.md`](HIGH_PROBABILITY_TRADE_VALIDATION_PROTOCOL.md) — future validation rules
