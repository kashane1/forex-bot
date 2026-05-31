# Forex Archive Cleanup and Crypto Roadmap — Sprint Summary (Phase G)

**Sprint:** `research-forex-archive-cleanup-and-crypto-roadmap-001`
**Date:** 2026-05-31
**Branch:** `main`

---

## 1. Branch name

`main` (base: `e33ccc15cee44aaa6cc5f4932dc61f60e76a58c1`)

---

## 2. Commit hashes by phase

| Phase | Commit | Message |
|-------|--------|---------|
| 0 | `cb94b1f` | Phase 0 — forex archive cleanup sprint plan |
| A | `1134bb5` | Phase A — forex documentation inventory |
| B | `e7d77b3` | Phase B — forex archive structure design |
| C | `43d9169` | Phase C — authoritative forex archive cleanup proposal |
| D | `fc286bc` | Phase D — forex programme final state index |
| E | `17f81df` | Phase E — crypto research programme roadmap |
| F | `debdf92` | Phase F — next prompt for crypto data design sprint |
| G | *(this commit)* | Phase G — final validation and summary |

---

## 3. Files changed by phase

| Phase | Files added |
|-------|-------------|
| 0 | `FOREX_ARCHIVE_CLEANUP_AND_CRYPTO_ROADMAP_001_PLAN.md` |
| A | `FOREX_DOCUMENTATION_INVENTORY.md`, `forex_documentation_inventory.json` |
| B | `FOREX_ARCHIVE_STRUCTURE_DESIGN.md` |
| C | `FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md` |
| D | `FOREX_PROGRAMME_FINAL_STATE.md` |
| E | `CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md` |
| F | `NEXT_PROMPT_CRYPTO_DATA_DESIGN_001.md` |
| G | `FOREX_ARCHIVE_CLEANUP_AND_CRYPTO_ROADMAP_001_SUMMARY.md` |

**Total:** 10 new documentation files. No files deleted. No files moved.

---

## 4. Validation commands run and results

| Command | Phase 0 | Phase G |
|---------|---------|---------|
| `pytest tests/ -q` | PASS (2460) | PASS (2460) |
| `ruff check src tests scripts research` | FAIL (14 pre-existing) | FAIL (14 pre-existing) |
| `python scripts/check_research_freeze.py` | PASS | PASS |
| `python scripts/validate_research_archive.py` | PASS | PASS |
| `python scripts/scan_artifacts_for_secrets.py` | PASS | PASS |
| `git status --short` | Clean | Clean |

**Ruff note:** 14 pre-existing style errors (RUF046, UP017) in scripts — not introduced by this sprint.

---

## 5. Forex documentation inventory summary

- **Total items inventoried:** 2,119 (docs/research/ + research/)
- **Source files:** `FOREX_DOCUMENTATION_INVENTORY.md`, `forex_documentation_inventory.json`
- **Major groups:** final verdicts, evidence indexes, campaigns, factor validation, front gates, infrastructure, executed prompts, research code/artifacts

---

## 6. Classification counts

| Classification | Count |
|----------------|-------|
| KEEP | 1,542 |
| ARCHIVE | 380 |
| DELETE_CANDIDATE | 1 |
| NEEDS_REVIEW | 195 |

---

## 7. Proposed archive structure

```
docs/research/
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

See `FOREX_ARCHIVE_STRUCTURE_DESIGN.md` for full detail.

---

## 8. Cleanup proposal summary

- **Main deliverable:** `FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md`
- **Future execution branch:** `research-forex-archive-cleanup-execution-001`
- **Policy:** archive over delete; no moves until proposal reviewed
- **Must-keep:** manifest, index, verdicts, factor artifacts, research code, freeze scripts
- **Staged cleanup:** 10 stages from scaffold creation through human sign-off

---

## 9. Confirmation: no files deleted

✓ No files were deleted during this sprint.

---

## 10. Confirmation: no crypto strategy created

✓ No cryptocurrency strategy was created.

---

## 11. Confirmation: no crypto campaign created

✓ No cryptocurrency campaign was created.

---

## 12. Confirmation: no factor-validation sprint created

✓ No factor-validation sprint was created.

---

## 13. Final forex programme state

- **Status:** COMPLETE · ARCHIVED
- **Approved strategies:** None (`approved: []`)
- **Approved campaigns:** None (23 campaigns, all non-approval)
- **Front-gate successes:** None
- **Terminal test:** FX futures carry diagnostic → `CARRY_DOES_NOT_SURVIVE_IN_FUTURES`
- **Entry point:** `FOREX_PROGRAMME_FINAL_STATE.md`

---

## 14. Crypto roadmap summary

Conservative 5-stage roadmap (archive review → data design → ingestion → exploratory diagnostics → factor validation → possible campaign). BTC/USD + ETH/USD only. Spot-first. Family C (Trend Persistence) recommended as first factor diagnostic after data validation.

---

## 15. Data recommendation summary

- **Spot OHLCV first** for BTC/USD and ETH/USD
- **1m base** if source quality supports; materialize 5m, 15m, 1h, 4h, 1d
- **Bid/ask or spread proxy** required for cost realism
- **5y minimum history** (10y desirable for BTC)
- **Futures/funding/OI hooks** in schema design only — not Phase 1
- **Next sprint:** data design only (`NEXT_PROMPT_CRYPTO_DATA_DESIGN_001.md`)

---

## 16. Timeframe recommendation summary

Priority: **5m/15m execution** with **1h/4h context** and **daily regime**. No FX session assumptions (continuous market).

---

## 17. BTC only vs BTC+ETH recommendation

**BTC+ETH from the start.** Enables generality testing and Family B relative-value work while keeping universe minimal (two assets, no altcoins).

---

## 18. Spot vs futures recommendation

**Spot first.** Futures/funding/OI designed but not blocking Phase 1. Family E (funding/OI) deferred until spot diagnostics establish whether crypto research is worthwhile.

---

## 19. Forex lessons that transfer

Null baselines mandatory; cost sensitivity mandatory; no campaign without factor effect; no post-hoc tuning; provenance matters; infrastructure is not edge; cross-validation (BTC/ETH split); small real effects can be untradeable; avoid universe expansion to find wins.

---

## 20. Forex lessons to discard or relax

Do not assume FX-like mean reversion or low persistence; do not assume H4-only entries suffice; do not assume session structure transfers; do not assume carry/funding behaves like FX rollover; do not over-weight seven-pair FX failure modes.

---

## 21. First crypto factor family recommended and why

**Family C — Trend Persistence.** Crypto's most plausible structural difference from FX is stronger momentum/regime persistence. Testable with spot OHLCV only (no funding data needed). Provides baseline for whether crypto warrants deeper work before investing in MTF confluence, relative value, or non-time bars.

---

## 22. Next sprint recommendation

**Branch:** `research-crypto-data-design-001`
**Prompt:** `NEXT_PROMPT_CRYPTO_DATA_DESIGN_001.md`
**Scope:** Data source evaluation, schema design, validation requirements, ingestion plan — documentation only, no large data ingestion without authorization.

---

## 23. Files to review first

1. [`FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md`](FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md) — authoritative cleanup proposal (review before any moves)
2. [`FOREX_PROGRAMME_FINAL_STATE.md`](FOREX_PROGRAMME_FINAL_STATE.md) — canonical forex entry point
3. [`FOREX_DOCUMENTATION_INVENTORY.md`](FOREX_DOCUMENTATION_INVENTORY.md) — full inventory with classifications
4. [`FOREX_ARCHIVE_STRUCTURE_DESIGN.md`](FOREX_ARCHIVE_STRUCTURE_DESIGN.md) — proposed folder structure
5. [`CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md`](CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md) — next programme design
6. [`NEXT_PROMPT_CRYPTO_DATA_DESIGN_001.md`](NEXT_PROMPT_CRYPTO_DATA_DESIGN_001.md) — next coding-agent prompt
7. [`FINAL_FOREX_PROGRAMME_EVIDENCE_INVENTORY.md`](FINAL_FOREX_PROGRAMME_EVIDENCE_INVENTORY.md) — terminal evidence ledger
8. [`FX_FUTURES_CARRY_VERDICT.md`](FX_FUTURES_CARRY_VERDICT.md) — terminal futures test

---

## Safety confirmations

| Check | Status |
|-------|--------|
| `configs/approved_strategies.yaml` empty | ✓ |
| Paper/demo/live blocked | ✓ |
| No broker/trading APIs called | ✓ |
| No secrets committed | ✓ |
| No raw large datasets committed | ✓ |
| Forex strategy search reopened | ✗ (not reopened) |
| Cleanup deletion performed | ✗ (none) |
| Archive moves performed | ✗ (none — docs only) |
