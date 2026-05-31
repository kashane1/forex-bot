# Forex Programme — Archive and Cleanup Proposal

**Sprint:** `research-forex-archive-cleanup-and-crypto-roadmap-001`
**Date:** 2026-05-31
**Status:** PROPOSAL — awaiting human review
**Type:** Authoritative cleanup proposal. No deletions or moves until reviewed and approved.

---

## 1. Executive summary

The forex strategy-search programme is **complete**. After exhaustive testing across traditional trend-following, multi-timeframe confluence, H4/M15/M1 factor discovery, non-time-bar research, cross-universe replication, carry factors, and FX-futures venue validation, the programme produced **no approved strategies, no approved campaigns, and no front-gate successes**.

The dominant failure mode is **lack of economically meaningful predictive power**, not infrastructure deficiency. The mature research platform (factor-validation framework, front-gate process, campaign process, replication process, cost analysis, data ingestion, provenance tracking, freeze controls) should be preserved and reused for the cryptocurrency programme.

This proposal inventories 2,119 documentation and artifact items, classifies them for KEEP / ARCHIVE / DELETE_CANDIDATE / NEEDS_REVIEW, defines a proposed archive folder structure, and specifies a staged cleanup sequence for a future execution sprint.

> **No deletion or file move should occur until this proposal is reviewed and explicitly approved.**

> **Cryptocurrency programme work begins only after this proposal is complete and reviewed.**

---

## 2. Forex strategy-search programme is complete

The programme tested:

- Traditional trend-following, multi-timeframe confluence, H4 and M15 strategies
- M1 factor discovery, non-time-bar research
- Overshoot/exhaustion (H16) and thin-participation (H03) factors
- Currency-strength (S2), relative-value (S4), and carry factors
- Cross-universe replication and non-USD crosses
- FX futures venue validation and futures carry diagnostic

**Verdict:** archived. Do not reopen forex strategy discovery unless overwhelming new evidence appears.

---

## 3. Summary of final forex outcomes

| Outcome | Detail |
|---------|--------|
| Approved strategies | **None** — `configs/approved_strategies.yaml` is empty |
| Approved campaigns | **None** — all 23 manifest campaigns have `strategy_approved: false` |
| Front-gate successes | **None** — H16, H03, C031 all rejected |
| C1 factor | Genuine on USD majors; **failed cross-universe replication** (S1 → C1_ARTIFACT) |
| S2 currency-strength | **Rejected** — strength persists but does not predict |
| S4 relative-value | **Real but economically insignificant** — sub-cost-band no-arb reversion |
| Carry factor | Phenomenon survives as mechanical accrual; **failed as predictive factor** (spot t≈0.1; futures t=0.09) |
| Futures carry diagnostic | **Failed** — `CARRY_DOES_NOT_SURVIVE_IN_FUTURES` |
| Primary failure mode | **Idea quality / market efficiency** — effects too small for costs, not infrastructure |

---

## 4. Inventory summary

Source: `FOREX_DOCUMENTATION_INVENTORY.md` and `forex_documentation_inventory.json`

| Classification | Count | Description |
|----------------|-------|-------------|
| **KEEP** | 1,542 | Final verdicts, evidence records, infrastructure, research code |
| **ARCHIVE** | 380 | Executed prompts, superseded plans, intermediate status docs |
| **DELETE_CANDIDATE** | 1 | `eur_usd_m1_response_matrix_summary.csv` (pending review) |
| **NEEDS_REVIEW** | 195 | Ambiguous campaign/intermediate docs |
| **Total** | 2,119 | docs/research/ + research/ combined |

---

## 5. Must Keep

These must never be deleted:

### Evidence and verdicts
- `docs/research/EVIDENCE_MANIFEST.json`
- `docs/research/EVIDENCE_INDEX.md`
- `docs/research/FINAL_RESEARCH_DECISION_MEMO.md`
- `docs/research/FINAL_FOREX_PROGRAMME_EVIDENCE_INVENTORY.md`
- `docs/research/FINAL_PROGRAMME_DIRECTION_DECISION.md`
- `docs/research/STRATEGY_STATUS.md`
- `docs/research/PROGRAMME_LESSONS_LEARNED.md`
- `docs/research/CROSS_FACTOR_PROGRAMME_SYNTHESIS_SUMMARY.md`
- All `*_VERDICT.md` files (C1, S2, S4, carry, FX futures carry)
- All `CAMPAIGN_*_FINAL_INTERPRETATION.md` files
- Campaign reports referenced by manifest (23 campaigns)

### Factor validation artifacts
- `docs/research/c1_validation/`
- `docs/research/currency_strength/`
- `docs/research/cross_relative_value/`
- `docs/research/carry_rates/`

### Infrastructure
- `configs/approved_strategies.yaml` (empty registry)
- `src/forex_bot/research_archive.py`, `approval.py`
- `scripts/check_research_freeze.py`, `validate_research_archive.py`
- `research/edge_discovery/`, `research/carry/`, `research/fx_futures/`
- All campaign Python modules under `research/` and `src/forex_bot/`

### Safety documentation
- `docs/research/STRATEGY_APPROVAL_PROCESS.md`
- `docs/research/EDGE_DISCOVERY_PROTOCOL.md`
- `docs/research/FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md`

---

## 6. Safe Archive

Move to `docs/research/archive/forex_programme/` (see structure design):

- 18 `NEXT_PROMPT_*.md` files (all executed)
- ~140 `*_001_PLAN.md` sprint plans superseded by summaries
- ~146 `*_001_SUMMARY.md` historical sprint summaries (keep copies accessible via archive index)
- Campaign scaffold, precommit, status, and walk-forward planning docs
- Infrastructure sprint plans (keep summaries at top-level or in `06_infrastructure/`)
- Intermediate status updates and scaffold-phase documents

**Archive principle:** move, do not delete. Preserve git history and provenance.

---

## 7. Likely Delete

Only after explicit review and confirmation no manifest/index reference:

| Path | Reason | Risk |
|------|--------|------|
| `docs/research/eur_usd_m1_response_matrix_summary.csv` | Intermediate diagnostic; full data in `research/` | Low |

**Default policy:** prefer ARCHIVE over DELETE. Deletion is exceptional.

Additional DELETE_CANDIDATE items may emerge from triage of 195 NEEDS_REVIEW docs during execution sprint.

---

## 8. Needs Review

195 items flagged NEEDS_REVIEW, primarily:

- Campaign docs without clear FINAL/VERDICT/REPORT suffix
- Intermediate diagnostic markdown with unclear supersession
- Duplicate or near-duplicate planning documents
- Files that may be referenced by manifests but not auto-detected

**Triage process (execution sprint):**
1. Check manifest/index references
2. Check if superseded by a summary or final interpretation
3. If unique evidence → KEEP or ARCHIVE (not DELETE)
4. If duplicate → ARCHIVE or DELETE_CANDIDATE with cross-reference

---

## 9. Proposed archive folder structure

See `FOREX_ARCHIVE_STRUCTURE_DESIGN.md` for full detail. Summary:

```
docs/research/
├── (top-level final docs + manifest/index — unchanged initially)
├── active/crypto_programme/
└── archive/forex_programme/
    ├── 00_final_synthesis/
    ├── 01_evidence_indexes/
    ├── 02_campaigns/
    ├── 03_factor_validation/
    ├── 04_front_gates/
    ├── 05_replication/
    ├── 06_infrastructure/
    ├── 07_prompts_and_plans/
    └── 08_superseded_working_notes/
```

---

## 10. Proposed staged cleanup sequence

**Future branch:** `research-forex-archive-cleanup-execution-001`

| Stage | Action | Risk |
|-------|--------|------|
| 0 | Create archive directory scaffold + README indexes | None |
| 1 | Move executed `NEXT_PROMPT_*` docs | Low |
| 2 | Move superseded `*_PLAN.md` files | Low |
| 3 | Move historical `*_SUMMARY.md` to archive (keep stubs if needed) | Low |
| 4 | Move campaign planning/scaffold docs | Medium — check cross-refs |
| 5 | Triage 195 NEEDS_REVIEW items | Medium |
| 6 | Move factor validation markdown (keep artifact dirs stable) | Medium |
| 7 | Update manifest/index if campaign report paths change | High — full validation required |
| 8 | Add redirect stubs at old paths (temporary) | Low |
| 9 | Run full validation suite | Gate |
| 10 | Human sign-off; optional DELETE of confirmed duplicates | High — explicit approval |

---

## 11. Files that must not be deleted

- `EVIDENCE_MANIFEST.json`, `EVIDENCE_INDEX.md`
- `configs/approved_strategies.yaml`
- All manifest-referenced campaign reports and artifact folders
- All `*_VERDICT.md` and `FINAL_*` synthesis documents
- Factor validation CSV/JSON artifacts with provenance metadata
- Research Python code under `src/` and `research/`
- Validation scripts: `check_research_freeze.py`, `validate_research_archive.py`, `scan_artifacts_for_secrets.py`

---

## 12. Files that should remain top-level

- `FOREX_PROGRAMME_FINAL_STATE.md` (canonical entry)
- `FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md` (this document)
- `EVIDENCE_MANIFEST.json`, `EVIDENCE_INDEX.md`
- `STRATEGY_STATUS.md`, `STRATEGY_APPROVAL_PROCESS.md`
- `FINAL_FOREX_PROGRAMME_EVIDENCE_INVENTORY.md`
- `PROGRAMME_LESSONS_LEARNED.md`
- `CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md` (active next programme)
- `NEXT_PROMPT_CRYPTO_DATA_DESIGN_001.md` (active next sprint)

---

## 13. Files that should become final indexes

| Index | Role |
|-------|------|
| `FOREX_PROGRAMME_FINAL_STATE.md` | Human entry point |
| `forex_documentation_inventory.json` | Machine-readable full inventory |
| `archive/forex_programme/README.md` | Archive navigation |
| `FINAL_FOREX_PROGRAMME_EVIDENCE_INVENTORY.md` | Terminal evidence ledger (already exists) |
| `EVIDENCE_INDEX.md` | Campaign evidence links (already exists) |

---

## 14. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Breaking freeze/archive validation | Move non-manifest files first; run validation after each stage |
| Broken docstring paths in source code | Temporary redirect stubs at old paths; update docstrings in separate PR |
| Loss of provenance | Never delete artifacts; git history preserved; archive over delete |
| Confusing new researchers | `FOREX_PROGRAMME_FINAL_STATE.md` + archive README |
| Premature crypto work | Gate: this proposal must be reviewed before crypto data ingestion |
| Accidental strategy approval | Keep `approved: []`; run freeze gate in CI |

---

## 15. Validation required before any actual cleanup

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

All must pass (ruff pre-existing failures documented separately). Additionally after any moves:

- All 747 evidence-index links must resolve
- All 23 campaign reports must exist at manifest paths
- All 22 artifact folders must exist
- `approved: []` must remain empty
- Paper/demo loops must refuse strategies

---

## 16. No deletion until reviewed

> **No file deletion should occur until this proposal is reviewed and explicitly approved by a human operator.**

Archive moves may proceed only after review of this proposal and the structure design document. Deletion is a separate, explicit decision per file.

---

## 17. Crypto programme gate

> **Cryptocurrency programme work — including data ingestion, factor diagnostics, campaigns, and strategy construction — begins only after this cleanup proposal is complete and reviewed.**

The next authorised sprint is data design only: see `NEXT_PROMPT_CRYPTO_DATA_DESIGN_001.md`.

---

## Related documents

- `FOREX_ARCHIVE_STRUCTURE_DESIGN.md` — folder structure detail
- `FOREX_DOCUMENTATION_INVENTORY.md` — full inventory
- `forex_documentation_inventory.json` — machine-readable index
- `FOREX_PROGRAMME_FINAL_STATE.md` — canonical forex entry point
- `CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md` — next programme design
