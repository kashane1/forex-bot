# Forex Programme — Archive Structure Design (Phase B)

**Sprint:** `research-forex-archive-cleanup-and-crypto-roadmap-001`
**Date:** 2026-05-31
**Type:** Design proposal only. No file moves in this sprint.

---

## Design goals

1. A new researcher understands the completed forex programme within minutes.
2. Active crypto programme docs have a clear home separate from archived forex material.
3. Final evidence records remain discoverable and validation scripts keep working.
4. Provenance is preserved without overwhelming the repo root.
5. Historical sprint plans/prompts are accessible but not mistaken for active work.

---

## Proposed structure

```
docs/research/
├── FOREX_PROGRAMME_FINAL_STATE.md          # canonical forex entry point (NEW)
├── FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md   # authoritative cleanup proposal (NEW)
├── CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md    # next programme design (NEW)
├── NEXT_PROMPT_CRYPTO_DATA_DESIGN_001.md   # next sprint prompt (NEW)
│
├── EVIDENCE_MANIFEST.json                  # KEEP at current path (script dependency)
├── EVIDENCE_INDEX.md                       # KEEP at current path (script dependency)
├── STRATEGY_STATUS.md                      # KEEP — human strategy registry
├── STRATEGY_APPROVAL_PROCESS.md            # KEEP — shared infrastructure
├── FINAL_RESEARCH_DECISION_MEMO.md         # KEEP — early programme freeze memo
├── FINAL_FOREX_PROGRAMME_EVIDENCE_INVENTORY.md  # KEEP — terminal evidence ledger
├── PROGRAMME_LESSONS_LEARNED.md            # KEEP — cross-programme lessons
│
├── active/                                 # NEW — current programme docs only
│   └── crypto_programme/
│       ├── README.md                       # pointer to roadmap + stage status
│       └── (future stage docs land here)
│
├── archive/
│   └── forex_programme/
│       ├── README.md                       # archive index + navigation
│       ├── 00_final_synthesis/
│       │   ├── FINAL_PROGRAMME_DIRECTION_DECISION.md  (symlink or copy stub)
│       │   ├── CROSS_FACTOR_PROGRAMME_SYNTHESIS_SUMMARY.md
│       │   ├── FX_FUTURES_CARRY_VERDICT.md
│       │   ├── FX_FUTURES_CARRY_PROGRAMME_IMPLICATION.md
│       │   └── PROGRAMME_DIRECTION_AFTER_CARRY_SUMMARY.md
│       ├── 01_evidence_indexes/
│       │   ├── COMPLETE_PROGRAMME_EVIDENCE_INVENTORY.md
│       │   ├── FOREX_RESEARCH_EVIDENCE_INVENTORY.md
│       │   └── FOREX_DOCUMENTATION_INVENTORY.md
│       ├── 02_campaigns/
│       │   ├── README.md                   # campaign verdict table
│       │   ├── final_interpretations/      # CAMPAIGN_*_FINAL_INTERPRETATION.md
│       │   ├── reports/                    # (optional) if reports move from backtests/
│       │   └── planning/                   # *_PLAN, *_PRECOMMIT, *_SCAFFOLD, *_STATUS
│       ├── 03_factor_validation/
│       │   ├── c1/                         # C1 verdict + validation docs
│       │   ├── currency_strength_s2/       # S2 verdict + docs + csv artifacts
│       │   ├── cross_relative_value_s4/    # S4 verdict + docs + csv artifacts
│       │   ├── carry/                      # carry + futures carry docs
│       │   └── artifacts/                  # docs/research/c1_validation/, carry_rates/, etc.
│       ├── 04_front_gates/
│       │   ├── H16_overshoot_exhaustion/
│       │   ├── H03_thin_move/
│       │   ├── CAMPAIGN_031_vol_managed_tsmom/
│       │   └── edge_discovery/
│       ├── 05_replication/
│       │   ├── C1_CROSS_REPLICATION_VERDICT.md
│       │   └── non_usd_cross/
│       ├── 06_infrastructure/
│       │   ├── INFRA_* summaries (keep copies or stubs)
│       │   ├── BACKTRADER_*, LEAN_PARITY_*, FINANCING_*, OANDA_*
│       │   └── M1_*, non_time_bar specs
│       ├── 07_prompts_and_plans/
│       │   ├── NEXT_PROMPT_*.md            # all 18 executed next-prompt docs
│       │   ├── *_001_PLAN.md               # superseded sprint plans
│       │   └── *_001_SUMMARY.md            # historical sprint summaries
│       └── 08_superseded_working_notes/
│           ├── intermediate status updates
│           ├── scaffold-phase docs
│           └── ambiguous NEEDS_REVIEW items after human triage
│
└── infrastructure_reference/               # NEW — shared docs for any programme
    ├── RESEARCH_FREEZE_AND_APPROVAL.md     # (consolidated pointer doc, optional)
    ├── EDGE_DISCOVERY_PROTOCOL.md
    ├── FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md
    └── execution_realism_policy.md         # if exists as standalone
```

```
research/                                   # KEEP code at current paths initially
├── (all existing packages unchanged)       # campaign_*, carry/, fx_futures/, edge_discovery/
└── archive/                                # FUTURE: optional symlink/stub only
    └── forex_programme/
        └── README.md                       # pointer to docs/research/archive/
```

---

## Design decisions

### 1. What stays top-level and why

| Item | Reason |
|------|--------|
| `EVIDENCE_MANIFEST.json` | Hardcoded in `forex_bot.research_archive.MANIFEST_PATH` |
| `EVIDENCE_INDEX.md` | Hardcoded in `EVIDENCE_INDEX_PATH`; 747 links validated by freeze gate |
| `STRATEGY_STATUS.md` | Referenced by approval gate and new researchers |
| `FINAL_*` synthesis docs | Programme terminal state must be immediately visible |
| `FOREX_PROGRAMME_FINAL_STATE.md` | Single canonical entry point (new) |
| Freeze/approval process docs | Shared across forex archive and crypto programme |

**Rule:** nothing moves from top-level until manifest/index paths are updated and validation passes.

### 2. What moves under archived forex programme

- 380 ARCHIVE-classified docs (plans, executed prompts, scaffold/status docs)
- Historical sprint summaries superseded by programme synthesis
- Intermediate campaign planning docs (preccommits, scaffolds, walk-forward plans)
- Executed `NEXT_PROMPT_*` documents (18 files)

**Rule:** move in batches by subdirectory; never move manifest-referenced campaign reports without updating manifest paths first.

### 3. What infrastructure references remain shared

These stay accessible (top-level or `infrastructure_reference/`):

- `STRATEGY_APPROVAL_PROCESS.md`
- `EDGE_DISCOVERY_PROTOCOL.md`
- `FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md`
- Factor-validation protocol patterns (as templates, not forex-specific results)
- Cost-model and execution-realism documentation
- Data provenance and freeze/safety documentation

The `research/` Python packages (`edge_discovery/`, `carry/`, `fx_futures/`, campaign modules) remain in place — they are reusable infrastructure, not forex-only dead code.

### 4. What documents become final evidence records

| Record | Location (current → proposed) |
|--------|-------------------------------|
| Programme terminal verdict | `FINAL_FOREX_PROGRAMME_EVIDENCE_INVENTORY.md` → top-level KEEP |
| Futures carry terminal test | `FX_FUTURES_CARRY_VERDICT.md` → `archive/forex_programme/00_final_synthesis/` |
| Factor verdicts (C1, S2, S4, carry) | KEEP paths initially; copy stubs in archive index |
| Campaign final interpretations | `CAMPAIGN_*_FINAL_INTERPRETATION.md` → archive `02_campaigns/final_interpretations/` |
| Factor CSV/JSON artifacts | `docs/research/c1_validation/`, `carry_rates/`, etc. → archive `03_factor_validation/artifacts/` |

### 5. Campaign / factor / front-gate output grouping

- **Campaigns:** group by campaign number under `02_campaigns/`; final interpretations and gate decisions together; planning docs in `planning/` subfolder.
- **Factor validation:** group by factor family (C1, S2, S4, carry) with verdict doc + protocol + null comparison + committed CSV artifacts co-located.
- **Front gates:** group by hypothesis ID (H16, H03, C031) under `04_front_gates/`.

### 6. Old next-prompt docs

All 18 `NEXT_PROMPT_*` files → `archive/forex_programme/07_prompts_and_plans/`.

Add a single top-level stub:

```markdown
# Next Research Prompt

The forex programme is archived. See:
- docs/research/NEXT_PROMPT_CRYPTO_DATA_DESIGN_001.md (active next step)
- docs/research/archive/forex_programme/07_prompts_and_plans/ (historical)
```

### 7. Preserving provenance without overwhelming the repo

- Keep committed CSV/JSON artifacts with their construction_meta.json files.
- Do not deduplicate artifacts that differ by provenance hash.
- Archive index README lists artifact locations; do not inline large tables in README.
- `forex_documentation_inventory.json` remains the machine-readable full index.

### 8. Avoiding breakage of validation/archive scripts

**Must not move without script updates:**

| Path | Script dependency |
|------|-------------------|
| `docs/research/EVIDENCE_MANIFEST.json` | `research_archive.py`, freeze gate |
| `docs/research/EVIDENCE_INDEX.md` | freeze gate (747 link resolution) |
| `configs/approved_strategies.yaml` | approval gate |
| Campaign `report_path` entries in manifest | archive validation |
| Campaign `artifact_folder` paths | archive validation |

**Safe to move in later sprint (with manifest/index updates):**

- Superseded plans and prompts (not in manifest)
- Factor validation markdown (keep artifact paths stable or update index)
- Infrastructure sprint plans

### 9. Redirect / index files needed

| File | Purpose |
|------|---------|
| `docs/research/archive/forex_programme/README.md` | Archive navigation |
| `docs/research/active/crypto_programme/README.md` | Active programme pointer |
| `docs/research/FOREX_PROGRAMME_FINAL_STATE.md` | Canonical forex entry (links to archive) |
| Optional stub files at old paths after moves | One-line redirect to new location (temporary, 1 sprint) |

### 10. Script updates required in future cleanup sprint

| Script / module | Change needed if files move |
|-----------------|----------------------------|
| `src/forex_bot/research_archive.py` | Only if manifest/index paths change |
| `scripts/validate_research_archive.py` | None if manifest paths updated consistently |
| `scripts/check_research_freeze.py` | None |
| `EVIDENCE_MANIFEST.json` | Update `report_path` and `artifact_folder` if campaign docs move |
| `EVIDENCE_INDEX.md` | Regenerate or batch-update 747 links |
| Source code docstring paths (`config.py`, strategies) | Optional — low priority; stubs at old paths suffice |
| New: `scripts/generate_archive_redirects.py` | Optional helper for stub files |

**Recommendation:** Phase 1 of execution sprint moves only non-manifest-referenced docs. Phase 2 updates manifest after campaign report paths are decided.

---

## Alternative considered: flat `docs/research/archive/` dump

Rejected. A flat dump of 380+ files would be harder to navigate than the numbered subdirectory scheme above, which mirrors the programme's logical structure (campaigns → factors → front gates → infrastructure).

---

## Migration sequence (for execution sprint, not this sprint)

1. Create directory scaffold + README indexes (no moves).
2. Move `NEXT_PROMPT_*` and `*_001_PLAN.md` files (low risk).
3. Move factor validation markdown (keep artifact subdirs stable).
4. Move campaign planning/scaffold docs.
5. Triage 195 NEEDS_REVIEW items.
6. Update manifest/index if campaign reports relocate.
7. Run full validation suite.
8. Remove redirect stubs after one release cycle.
