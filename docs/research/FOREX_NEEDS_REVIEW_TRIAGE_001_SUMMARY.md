# Forex NEEDS_REVIEW Triage — Executive Decisions

**Date:** 2026-05-31
**Authority:** Operator delegation — no human per-file review required
**Inventory:** `forex_documentation_inventory.json` updated

---

## Summary

| Decision | Count |
|----------|-------|
| **KEEP** (reclassified) | 57 |
| **ARCHIVE** (moved + stub) | 138 |
| **DELETE** | 0 |

All 195 inventory `NEEDS_REVIEW` items resolved (179 under `docs/research/` + 16 under `research/` counted in inventory).

---

## KEEP — rationale

| Category | Count | Rule |
|----------|-------|------|
| C1 validation CSV/JSON | 34 | Already in `docs/research/c1_validation/` — canonical factor evidence |
| C1 high-vol frontgate artifacts | 5 | Already in `c1_highvol_frontgate/` |
| Carry artifacts | 1 | `carry_rates/carry_differentials.csv` |
| Research code artifacts | 2 | `research/campaign_028/...`, `research/carry/...` |
| M1 response matrix diagnostics | 3 | Referenced by `EURUSD_M1_RESPONSE_MATRIX_RESULT.md`; keep paths stable |
| Other | 12 | Includes `CAMPAIGN_011_DEDUPED_NULL_BASELINE.md` (manifest `report_path`) |

**DELETE_CANDIDATE decision:** `eur_usd_m1_response_matrix_*.csv/json` → **KEEP**, not delete. Small committed artifacts with doc cross-references; full matrix also in `research/`.

---

## ARCHIVE — rationale

139 markdown files at `docs/research/` root — intermediate campaign, backtrader parity, factor study, and direction docs superseded by final verdicts, final interpretations, or programme synthesis. **`CAMPAIGN_011_DEDUPED_NULL_BASELINE.md` excluded** — it is the manifest `report_path` for CAMPAIGN_011 and must remain at its canonical location.

| Destination | Pattern | Examples |
|-------------|---------|----------|
| `03_factor_validation/c1/` | `C1_*` studies (not verdicts) | `C1_COST_REALISM_STUDY.md` |
| `03_factor_validation/carry/` | `CARRY_*` readiness docs | `CARRY_DATASET_VALIDATION.md` |
| `00_final_synthesis/` | FX futures carry supporting docs | `FX_FUTURES_CARRY_PROGRAMME_IMPLICATION.md` |
| `06_infrastructure/backtrader/` | Backtrader parity lane | `BACKTRADER_CAMPAIGN_015_COMPARISON.md` |
| `02_campaigns/planning/` | Campaign gate/postmortem/diagnostic | `CAMPAIGN_018_GATE_DECISION.md` |
| `08_superseded_working_notes/direction/` | Programme direction memos | `NEXT_FACTOR_DISCOVERY_DIRECTION.md` |

Redirect stubs at original paths preserve 44 manifest/index-referenced links.

---

## Validation

Post-triage: freeze gate PASS, archive validation PASS, pytest 2460 PASS.

---

## Related

- [`FOREX_ARCHIVE_CLEANUP_EXECUTION_001_SUMMARY.md`](FOREX_ARCHIVE_CLEANUP_EXECUTION_001_SUMMARY.md)
- [`archive/forex_programme/README.md`](archive/forex_programme/README.md)
