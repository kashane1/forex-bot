# Forex Archive Cleanup and Crypto Roadmap — Sprint Plan (Phase 0)

**Sprint:** `research-forex-archive-cleanup-and-crypto-roadmap-001`
**Branch:** `main`
**Base commit:** `e33ccc15cee44aaa6cc5f4932dc61f60e76a58c1`
**Date:** 2026-05-31
**Type:** Documentation, inventory, archive design, and roadmap planning only.

---

## Purpose

Hand off the completed forex strategy-search programme to archive status, produce an authoritative cleanup proposal, and design a conservative cryptocurrency research roadmap — **without** beginning crypto research, deleting files, or reopening forex strategy discovery.

This sprint is the mandatory gate before any cryptocurrency programme work begins.

---

## Non-goals

- Do **not** delete any files.
- Do **not** move files except small new proposal/index documents.
- Do **not** create crypto strategies, campaigns, or factor-validation sprints.
- Do **not** run crypto data ingestion or forex factor screens.
- Do **not** approve any strategy or enable paper/demo/live.
- Do **not** call broker/trading APIs.
- Do **not** commit secrets, raw databases, bulky data, or large generated artifacts.
- Do **not** reopen forex strategy discovery unless overwhelming evidence is found during audit.

---

## Safety rules

1. **Research freeze intact:** `configs/approved_strategies.yaml` must remain empty (`approved: []`).
2. **Execution blocked:** paper-loop and demo-loop must refuse all configured strategies.
3. **No cleanup execution:** actual file moves/deletions wait for review of `FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md`.
4. **Crypto blocked until archive proposal complete:** no crypto programme work until the cleanup proposal is written and reviewed.
5. **Documentation-only changes:** this sprint adds/updates markdown and JSON index files only.

---

## Current repo state (Phase 0 audit)

| Check | Result |
|-------|--------|
| Branch | `main` |
| HEAD | `e33ccc15cee44aaa6cc5f4932dc61f60e76a58c1` |
| Working tree | Clean at sprint start |
| `configs/approved_strategies.yaml` | Empty — `approved: []` |
| Paper/demo/live | Blocked — freeze gate passes |
| `docs/research/` files | ~1,061 files |
| `research/` files | ~1,065 files |
| Campaign manifest | 23 campaigns, all non-approval |
| Evidence index links | 747 links, all resolve |

### High-level documentation structure

| Area | Role |
|------|------|
| `docs/research/` | Primary research documentation — campaigns, factors, infrastructure, verdicts, plans, summaries, evidence indexes |
| `research/` | Research code and committed output artifacts (campaigns, factors, fx_futures, carry, etc.) |
| `configs/` | Strategy configs, campaign configs, approved-strategy registry, paper/practice/live configs |
| `scripts/` | Campaign runners, factor validation, data ingestion, validation/freeze/archive checks |
| `docs/research/EVIDENCE_MANIFEST.json` | Canonical campaign evidence manifest |
| `docs/research/EVIDENCE_INDEX.md` | Human-readable evidence index |
| `docs/research/FINAL_FOREX_PROGRAMME_EVIDENCE_INVENTORY.md` | Terminal programme evidence ledger |

### Forex programme status

**The forex strategy-search programme is complete and archived.**

- No approved strategies
- No approved campaigns
- No front-gate successes
- C1 factor failed cross-universe replication
- S2 currency-strength factor rejected
- S4 relative-value factor real but economically insignificant
- Carry phenomenon survived but failed as predictive factor (spot and futures)
- Primary failure mode: lack of economically meaningful predictive power, not infrastructure

---

## Validation commands

Run at Phase 0 and Phase G:

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

### Phase 0 validation results

| Command | Result |
|---------|--------|
| `pytest tests/ -q` | **PASS** — 2460 passed |
| `ruff check src tests scripts research` | **FAIL (pre-existing)** — 14 lint errors in scripts (RUF046, UP017 style issues); not introduced by this sprint |
| `python scripts/check_research_freeze.py` | **PASS** — all checks including loops_refuse |
| `python scripts/validate_research_archive.py` | **PASS** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASS** — value scan skipped (no OANDA creds in env); pattern scan clean |

---

## Expected phases

| Phase | Deliverable | Commit |
|-------|-------------|--------|
| **0** | This plan | Yes |
| **A** | `FOREX_DOCUMENTATION_INVENTORY.md` + `forex_documentation_inventory.json` | Yes |
| **B** | `FOREX_ARCHIVE_STRUCTURE_DESIGN.md` | Yes |
| **C** | `FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md` (authoritative) | Yes |
| **D** | `FOREX_PROGRAMME_FINAL_STATE.md` | Yes |
| **E** | `CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md` (after Phase C) | Yes |
| **F** | `NEXT_PROMPT_CRYPTO_DATA_DESIGN_001.md` | Yes |
| **G** | `FOREX_ARCHIVE_CLEANUP_AND_CRYPTO_ROADMAP_001_SUMMARY.md` + final validation | Yes |

---

## Expected deliverables

1. Complete forex documentation inventory with KEEP / ARCHIVE / DELETE_CANDIDATE / NEEDS_REVIEW classifications
2. Proposed archive folder structure design
3. Authoritative cleanup proposal (`FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md`)
4. Canonical forex programme final-state index
5. Conservative crypto research programme roadmap (design only)
6. Next-sprint prompt for crypto data design (not strategy)
7. Sprint summary with commit hashes and validation results

---

## Gate statements

> **Forex strategy search is complete.** Do not reopen forex strategy discovery unless overwhelming evidence is found during the audit.

> **Crypto programme work cannot begin until `FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md` exists, is complete, and has been reviewed.** Actual file cleanup/deletion must not occur until that proposal is explicitly approved.

---

## Proposed future cleanup branch (not executed in this sprint)

`research-forex-archive-cleanup-execution-001`
