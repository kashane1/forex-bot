# Forex Archive Cleanup — Execution Summary

**Sprint:** `research-forex-archive-cleanup-execution-001`
**Date:** 2026-05-31
**Branch:** `research-forex-archive-cleanup-execution-001`
**Approval:** `FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md` reviewed and approved by operator

---

## 1. What was executed

| Stage | Action | Result |
|-------|--------|--------|
| 0 | Archive directory scaffold + README indexes | Created `docs/research/archive/forex_programme/` (9 subdirs) and `docs/research/active/crypto_programme/` |
| 1–3 | Move ARCHIVE-classified docs (prompts, plans, summaries) | **380 files moved** |
| 8 | Redirect stubs at original paths | **380 stubs created** |
| 5 | NEEDS_REVIEW executive triage | **138 archived**, 57 kept, 0 remaining |
| 9 | Full validation suite | **All checks passed** |
| 10 | Deletions | **None** (policy: archive over delete) |

Stages 6–7 (manifest/index path updates) not required — manifest report paths unchanged; evidence-index links resolve via stubs.

---

## 2. Move breakdown

| Destination | Files moved |
|-------------|-------------|
| `archive/forex_programme/07_prompts_and_plans/` | 325 |
| `archive/forex_programme/02_campaigns/planning/` | 46 |
| `archive/forex_programme/03_factor_validation/` | 9 |
| **Total** | **380** |

---

## 3. What stayed top-level

Unchanged per proposal §12:

- `EVIDENCE_MANIFEST.json`, `EVIDENCE_INDEX.md`
- All `*_VERDICT.md`, `CAMPAIGN_*_FINAL_INTERPRETATION.md`, `FINAL_*` synthesis docs
- Factor validation artifact directories (`c1_validation/`, `carry_rates/`, etc.)
- `FOREX_PROGRAMME_FINAL_STATE.md`, `STRATEGY_STATUS.md`, crypto roadmap docs
- `NEXT_PROMPT_CRYPTO_DATA_DESIGN_001.md` (active next sprint)

---

## 4. Redirect stubs

Each moved file has a stub at its original path linking to the archive location. This preserves:

- 747 evidence-index link resolutions
- Test docstring references to plan documents
- Fixture `_doc` cross-references

---

## 5. Validation results

| Command | Result |
|---------|--------|
| `pytest tests/ -q` | PASS — 2460 passed |
| `python scripts/check_research_freeze.py` | PASS — all 13 checks |
| `python scripts/validate_research_archive.py` | PASS — all 12 checks |
| `python scripts/scan_artifacts_for_secrets.py` | PASS |
| Evidence index links | 747/747 resolve |
| Campaign reports | 23/23 present |
| `approved: []` | Empty |

---

## 6. Remaining work (future sprints)

| Item | Count | Notes |
|------|-------|-------|
| NEEDS_REVIEW triage | 0 remaining | See `FOREX_NEEDS_REVIEW_TRIAGE_001_SUMMARY.md` |
| DELETE_CANDIDATE | 1 | `eur_usd_m1_response_matrix_summary.csv` — not deleted |
| Remove redirect stubs | 380 | After one release cycle (proposal §14) |
| Update EVIDENCE_INDEX links | Optional | Point directly to archive paths |

---

## 7. Tooling added

- `scripts/execute_forex_archive_cleanup.py` — idempotent move + stub generator (inventory-driven)
- `docs/research/archive/forex_programme/README.md` — archive navigation
- `docs/research/active/crypto_programme/README.md` — active programme pointer

---

## 8. Safety confirmations

| Check | Status |
|-------|--------|
| Files deleted | ✗ None |
| Manifest report paths changed | ✗ None |
| `approved: []` empty | ✓ |
| Forex strategy search reopened | ✗ |
| Crypto programme gate cleared | ✓ — data design sprint authorised |

---

## 9. Next step

Proceed with crypto data design sprint per [`NEXT_PROMPT_CRYPTO_DATA_DESIGN_001.md`](NEXT_PROMPT_CRYPTO_DATA_DESIGN_001.md).
