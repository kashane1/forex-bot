# M1 Full Corpus Validation And Aggregation 001 Summary

1. **Branch name.** `infra-m1-full-corpus-validation-and-aggregation-001`
2. **Base branch/commit.** `main` at `bc8a5b1`
3. **Commit hashes by phase.**
   - Phase 0: `9421b17`
   - Phase 1: `c80efc4`
   - Phase 2: `9a176a9`
   - Phase 3–4: `477e670`
   - Phase 5–7: `f6cfab5`
   - Phase 8: `56f9779`
   - Phase 9: this summary commit
4. **Files changed by phase.**
   - Phase 0: plan, `m1_corpus_validation.py`, `run_m1_full_corpus_validation.py`, `project_env.py`, script dotenv wiring
   - Phase 1: `m1_corpus_inventory.json`, inventory result doc
   - Phase 2: `m1_quality_*`, quality result doc
   - Phase 3–4: `aggregate_coverage_*`, `h4_drift_*`, aggregation + drift docs
   - Phase 5–7: `d1agg_*`, `ltf_htf_alignment_*`, `ltf_preflight_summary.json`, result docs
   - Phase 8: readiness decision, `EVIDENCE_INDEX`, backlog, roadmap, `STRATEGY_STATUS`
   - Phase 9: this summary
5. **Baseline validation result.** `pytest tests/ -q`: 1831 passed, 2 failed (`evidence_index_links` until summary committed; pre-existing ruff elsewhere unchanged). `check_research_freeze` / `validate_research_archive`: fail until summary link exists. `scan_artifacts_for_secrets`: pass.
6. **M1 inventory result.** PASS — all seven pairs, exact expected counts, 2021-05-27→2026-05-26 UTC.
7. **Expected vs actual row counts.** All deltas 0 (12,793,196 total).
8. **M1 data quality result.** WARN — calendar-model missing minutes ~2–5%; zero duplicates, bid/ask/OHLC violations, bad spreads.
9. **Pair-level PASS/WARN/FAIL.** Inventory PASS all; quality PASS EUR_USD, WARN six others; no FAIL.
10. **Aggregation coverage.** M5/M15/H1/H4 viable all pairs (~361k / ~116k / ~27k / ~5k bars EUR_USD). M1-only D1AGG bar count 0 (incomplete trading days).
11. **H4 drift comparison.** WARN — 0 OHLC mismatch on overlap; native-only H4 from gaps/omitted M1 blocks.
12. **D1AGG convention.** WARN M1 path; native H4→D1AGG ~1,294 bars/pair PASS.
13. **LTF/HTF alignment.** WARN — 0 lookahead; D1AGG unavailable on M1-only; M15/H1/H4 samples OK.
14. **LTF backtest preflight.** WARN — M15 `next_bar_open` OK; FAIL flag only on empty M1-D1AGG context frame.
15. **Readiness classification.** `READY_WITH_WARNINGS` → CAMPAIGN_021 **scaffold** next.
16. **Raw M1 committed.** No.
17. **CAMPAIGN_021 evidence.** No.
18. **Strategy approved.** No.
19. **Paper/demo/live blocked.** Yes.
20. **Executor/broker behavior changed.** No.
21. **OANDA mutation APIs called.** No.
22. **Live environment used.** No.
23. **Credentials/secrets printed or committed.** No.
24. **SQLite/Postgres/raw DB staged.** No.
25. **Tests added.** `tests/unit/test_m1_corpus_validation.py`
26. **Validation commands run.** `pytest tests/ -q`, `ruff check` on new modules, `run_m1_full_corpus_validation.py` phases, archive/freeze/secret scan.
27. **Remaining WARN/BLOCKED.** Hybrid D1AGG provenance required; optional M1 H4 trading-day repair sprint; full-repo ruff pre-existing findings unchanged.
28. **Recommended next sprint.** `research-campaign-021-ltf-mtf-confluence-scaffold-001`
29. **Review first.** `M1_FULL_CORPUS_LTF_LANE_READINESS_DECISION.md`, `research/m1_full_corpus_validation/h4_drift_summary.json`, `m1_quality_summary.json`, `run_m1_full_corpus_validation.py`

| Layer | Status | Key Evidence | Risk | Follow-up |
| --- | --- | --- | --- | --- |
| M1 store | PASS | `m1_corpus_inventory.json` | None | — |
| M1 quality | WARN | `m1_quality_summary.json` | Calendar close gaps | Monitor; no repair |
| Aggregation | PASS (M5–H4) | `aggregate_coverage_summary.json` | D1AGG M1 path empty | Hybrid D1AGG in C021 |
| H4 drift | WARN | `h4_drift_summary.json` | Series divergence | Document in scaffold |
| D1AGG | WARN | `d1agg_convention_summary.json` | M1 day incompleteness | Native H4→D1AGG |
| Alignment | WARN | `ltf_htf_alignment_summary.json` | D1AGG unavailable M1-only | Hybrid context |
| Preflight | WARN | `ltf_preflight_summary.json` | Empty M1 D1AGG frame | Same hybrid |
| Readiness | READY_WITH_WARNINGS | readiness decision doc | Scaffold scope creep | C021 scaffold only |
