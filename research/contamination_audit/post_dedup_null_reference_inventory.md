# Post-Dedup Null Reference Inventory (machine)

**Sprint:** POST_DEDUP_NULL_REFERENCE_REFRESH_001  
**Files scanned:** 8046  
**Files with matches:** 490  

## Summary

- Canonical null JSON: `research/null_baselines/campaign_011_deduped_null_baseline.json`
- Superseded artifact: `backtests/CAMPAIGN_011_random_entry_anchor`
- Files with old null metrics: **176**
- Files referencing canonical null JSON: **24**

### Campaign file hits

| campaign | files with mention |
|---|---:|
| CAMPAIGN_012 | 181 |
| CAMPAIGN_013 | 138 |
| CAMPAIGN_014 | 129 |

### Pattern counts

| pattern | files |
|---|---:|
| `above_null_claim` | 24 |
| `campaign_011` | 267 |
| `campaign_012` | 181 |
| `campaign_013` | 138 |
| `campaign_014` | 129 |
| `canonical_null_json` | 24 |
| `old_null_expectancy` | 116 |
| `old_null_json_path` | 67 |
| `old_null_pf` | 98 |
| `old_null_return` | 52 |
| `old_null_trades` | 84 |
| `random_entry_anchor` | 261 |
| `superseded_null_reference` | 10 |

## Per-file matches (sample)

### `docs/research/BACKTRADER_CAMPAIGN_011_004_PLAN.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 51

- L1 `campaign_011`: # Backtrader CAMPAIGN_011 port — Sprint 004 Plan
- L9 `campaign_011`: > CAMPAIGN_011 rules, does not change CAMPAIGN_011's verdict, and
- L12 `campaign_011`: > CAMPAIGN_011 remains **REJECT / null diagnostic anchor by design**.
- L16 `campaign_011`: Port CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011` into the
- L16 `random_entry_anchor`: Port CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011` into the
- … 46 more matches

### `docs/research/BACKTRADER_CAMPAIGN_011_BLOCKED_002.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 39

- L1 `campaign_011`: # Backtrader CAMPAIGN_011 — Phase 5 — BLOCKED (cascade)
- L19 `campaign_011`: The Phase 5 precondition is therefore unmet, and a CAMPAIGN_011 port
- L22 `campaign_011`: ## 1. Why CAMPAIGN_011 is the correct future target (unchanged)
- L25 `campaign_011`: CAMPAIGN_011 `random_entry_anchor 0.1.0-c011` as the recommended
- L25 `random_entry_anchor`: CAMPAIGN_011 `random_entry_anchor 0.1.0-c011` as the recommended
- … 34 more matches

### `docs/research/BACKTRADER_CAMPAIGN_011_BLOCKED_003.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 28

- L1 `campaign_011`: # Backtrader CAMPAIGN_011 — Phase 5 — BLOCKED-by-design (Sprint 003)
- L10 `campaign_011`: **Phase 5 precondition met, but CAMPAIGN_011 is deliberately not
- L12 `campaign_011`: that would make a CAMPAIGN_011 comparison apples-to-oranges; both are
- L17 `campaign_011`: `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py`
- L17 `random_entry_anchor`: `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py`
- … 23 more matches

### `docs/research/BACKTRADER_CAMPAIGN_011_FIDELITY_FIX_004.md`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 18

- L1 `campaign_011`: # Backtrader CAMPAIGN_011 — Phase 5 fidelity fix
- L5 `campaign_011`: **Phase:** 5 of `BACKTRADER_CAMPAIGN_011_004_PLAN.md`
- L9 `campaign_011`: > comparison are fixed here. After both fixes, the BT-lane CAMPAIGN_011
- L12 `campaign_011`: > No bespoke-engine change, no CAMPAIGN_011 rule change, no strategy
- L13 `campaign_011`: > approval. CAMPAIGN_011 remains REJECT / null diagnostic anchor by
- … 13 more matches

### `docs/research/BACKTRADER_CAMPAIGN_011_FULL_WINDOW_COMPARISON_004.md`

Patterns: `campaign_011`, `old_null_expectancy`, `random_entry_anchor`
Match count: 26

- L1 `campaign_011`: # Backtrader CAMPAIGN_011 — Phase 4 full-window comparison
- L5 `campaign_011`: **Phase:** 4 of `BACKTRADER_CAMPAIGN_011_004_PLAN.md`
- L8 `campaign_011`: > The **initial** (pre-fix) Backtrader-lane CAMPAIGN_011 output, run by
- L11 `campaign_011`: > CAMPAIGN_011 tolerance bands defined in
- L12 `campaign_011`: > `CAMPAIGN_011_NORISK_REFERENCE_CONTRACT.md` §9. The divergence is
- … 21 more matches

### `docs/research/BACKTRADER_CAMPAIGN_011_FULL_WINDOW_RUN_004.md`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 18

- L1 `campaign_011`: # Backtrader CAMPAIGN_011 — Phase 3 full-window run (pre-fix)
- L5 `campaign_011`: **Phase:** 3 of `BACKTRADER_CAMPAIGN_011_004_PLAN.md`
- L9 `campaign_011`: > CAMPAIGN_011 run output, exactly as produced. Any divergence found
- L11 `campaign_011`: > fix lands in Phase 5. CAMPAIGN_011 remains REJECT / null diagnostic
- L18 `campaign_011`:     --campaign CAMPAIGN_011 \
- … 13 more matches

### `docs/research/BACKTRADER_CAMPAIGN_011_HANDOFF_FROM_NORISK_REFERENCE.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 40

- L1 `campaign_011`: # Backtrader CAMPAIGN_011 — handoff from the no-RiskEngine reference
- L10 `campaign_011`: > sprint will port CAMPAIGN_011 to the Backtrader secondary lane and
- L13 `campaign_011`: > CAMPAIGN_011 remains REJECT / null diagnostic anchor by design.
- L19 `campaign_011`: | **Canonical full-window no-RiskEngine reference JSON** | `research/lean_parity/campaign_011_h4_bespoke_reference.json` | yes | the BT-vs-bespoke comparison target |
- L20 `campaign_011`: | Informational per-fold rollup JSON | `research/lean_parity/campaign_011_h4_bespoke_reference_per_fold.json` | yes | sanity check vs the published walk-forward plan |
- … 35 more matches

### `docs/research/BACKTRADER_CAMPAIGN_011_PER_FOLD_DEFERRED_004.md`

Patterns: `campaign_011`
Match count: 16

- L1 `campaign_011`: # Backtrader CAMPAIGN_011 — Phase 6 per-fold comparison deferred
- L5 `campaign_011`: **Phase:** 6 of `BACKTRADER_CAMPAIGN_011_004_PLAN.md`
- L14 `campaign_011`: > below pinned. CAMPAIGN_011 remains REJECT / null diagnostic anchor
- L20 `campaign_011`: `research/lean_parity/campaign_011_h4_bespoke_reference_per_fold.json`
- L23 `campaign_011`: candles from the SQLite store (`scripts/export_campaign_011_norisk_reference.py`
- … 11 more matches

### `docs/research/BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_001_SUMMARY.md`

Patterns: `campaign_011`
Match count: 1

- L59 `campaign_011`: - All prior backtests/CAMPAIGN_011_* artifacts — read-only consumed

### `docs/research/BACKTRADER_DATA_ADAPTER_SPEC.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 4

- L203 `campaign_011`: `strategy_evidence: false`. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011,
- L204 `campaign_012`: CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
- L204 `campaign_013`: CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
- L205 `campaign_014`: CAMPAIGN_014 remains scaffold-only. Paper / demo / live remain blocked.

### `docs/research/BACKTRADER_FIRST_CAMPAIGN_ADAPTER.md`

Patterns: `campaign_011`
Match count: 4

- L13 `campaign_011`: ### Why CAMPAIGN_002, not CAMPAIGN_011
- L18 `campaign_011`: CAMPAIGN_011 (deterministic by seed, minimal indicator surface, but
- L46 `campaign_011`: CAMPAIGN_011's per-bar SHA-256 coin-flip is itself a downstream check
- L48 `campaign_011`: which is what CAMPAIGN_002 is for. (CAMPAIGN_011 is a candidate for

### `docs/research/BACKTRADER_INSTALL_AND_SMOKE_RESULT.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 4

- L151 `campaign_011`: approve a strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011,
- L152 `campaign_012`: CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
- L152 `campaign_013`: CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
- L153 `campaign_014`: CAMPAIGN_014 remains scaffold-only. Paper / demo / live remain blocked.

### `docs/research/BACKTRADER_PARITY_COMPARISON_SPEC.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 4

- L199 `campaign_011`: `strategy_evidence: false`. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011,
- L200 `campaign_012`: CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
- L200 `campaign_013`: CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
- L201 `campaign_014`: CAMPAIGN_014 remains scaffold-only. Paper / demo / live remain blocked.

### `docs/research/BACKTRADER_PARITY_FIRST_RESULT.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 4

- L156 `campaign_011`: - CAMPAIGN_011 REJECT (null model anchor) verdict.
- L157 `campaign_012`: - CAMPAIGN_012 REJECT verdict.
- L158 `campaign_013`: - CAMPAIGN_013 REJECT verdict.
- L159 `campaign_014`: - CAMPAIGN_014 scaffold-only status.

### `docs/research/BACKTRADER_REAL_DATA_PREFLIGHT_002.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 5

- L19 `campaign_011`: CSVs that are absent. Phase 5 (CAMPAIGN_011) also cannot proceed
- L217 `campaign_011`: CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain
- L217 `campaign_012`: CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain
- L217 `campaign_013`: CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain
- L218 `campaign_014`: rejected/null/research-only. CAMPAIGN_014 remains scaffold-only.

### `docs/research/BACKTRADER_REAL_DATA_RUN_002_PLAN.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 5

- L20 `campaign_011`:    comparison outcome. CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012,
- L20 `campaign_012`:    comparison outcome. CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012,
- L21 `campaign_013`:    CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014
- L21 `campaign_014`:    CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014
- L167 `campaign_011`: - **Phase 5:** CAMPAIGN_011 decision — only if CAMPAIGN_002 reached

### `docs/research/BACKTRADER_RUNNER_CONTRACT.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 4

- L229 `campaign_011`: `strategy_evidence: false`. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011,
- L230 `campaign_012`: CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
- L230 `campaign_013`: CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
- L231 `campaign_014`: CAMPAIGN_014 remains scaffold-only. Paper / demo / live remain blocked.

### `docs/research/BACKTRADER_SECOND_CAMPAIGN_BLOCKED.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 39

- L31 `campaign_011`: | bespoke reference available | yes (committed per-fold JSONs under `backtests/CAMPAIGN_011_random_entry_anchor/folds/`) |
- L31 `random_entry_anchor`: | bespoke reference available | yes (committed per-fold JSONs under `backtests/CAMPAIGN_011_random_entry_anchor/folds/`) |
- L31 `old_null_json_path`: | bespoke reference available | yes (committed per-fold JSONs under `backtests/CAMPAIGN_011_random_entry_anchor/folds/`) |
- L32 `campaign_011`: | Backtrader adapter exists for CAMPAIGN_011 | **no** — not implemented in this sprint |
- L33 `campaign_011`: | would a Backtrader CAMPAIGN_011 adapter produce comparable output without local CSVs | **no** — same BLOCKED state as Phase 6, with no new comparison signal |
- … 34 more matches

### `docs/research/BIAS_OF_FIXTURES_ARTIFACT_INVENTORY.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_trades`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 32

- L37 `campaign_011`: | CAMPAIGN_011 random_entry_anchor (null) | `ac6e72942d1a016c` | 5,942 B | `eff542e1a5e5d66e` | 8 | 1,177 | REJECT |
- L37 `random_entry_anchor`: | CAMPAIGN_011 random_entry_anchor (null) | `ac6e72942d1a016c` | 5,942 B | `eff542e1a5e5d66e` | 8 | 1,177 | REJECT |
- L37 `old_null_trades`: | CAMPAIGN_011 random_entry_anchor (null) | `ac6e72942d1a016c` | 5,942 B | `eff542e1a5e5d66e` | 8 | 1,177 | REJECT |
- L38 `campaign_012`: | CAMPAIGN_012 regime_switcher_atr_percentile | `3bea07f2399bda31` | 5,996 B | `f0977b42905125ef` | 8 | 3,726 | REJECT |
- L39 `campaign_013`: | CAMPAIGN_013 cross_pair_currency_strength_rotation | `ddef199dc95b0f38` | 5,852 B | `d7b56323e625866c` | 8 | 7,940 | REJECT |
- … 27 more matches

### `docs/research/BIAS_OF_FIXTURES_AUDIT_001_PLAN.md`

Patterns: `campaign_014`, `campaign_011`, `old_null_trades`, `campaign_012`, `random_entry_anchor`, `campaign_013`
Match count: 21

- L28 `campaign_014`: - the CAMPAIGN_014 event fixture
- L29 `campaign_014`:   (`research/calendar/fixtures/campaign_014_events.json`)
- L61 `campaign_011`: treat CAMPAIGN_011 as the binding random-entry null and compute
- L65 `campaign_011`: screen B.1-B.4) **depends on the CAMPAIGN_011 null shape itself**.
- L83 `campaign_011`: - **CAMPAIGN_011 null artifacts** — the binding random-entry
- … 16 more matches

### `docs/research/BIAS_OF_FIXTURES_AUDIT_001_RESULT.md`

Patterns: `campaign_011`, `old_null_expectancy`, `campaign_014`, `campaign_012`, `campaign_013`
Match count: 24

- L23 `campaign_011`: ## Q1 — Is CAMPAIGN_011 acceptable as the binding null?
- L44 `old_null_expectancy`: | mean_R_overall vs others | −0.0024 vs others [−0.148, −0.041] | **outside (less negative)** |
- L59 `campaign_014`: 63 % clustering at UTC 9 or CAMPAIGN_014's 62 % at UTC 13. No
- L62 `campaign_011`: **Bottom line for Q1: CAMPAIGN_011 is acceptable as the binding
- L90 `campaign_011`: - CAMPAIGN_010 and CAMPAIGN_011 trade only on each fold's test
- … 19 more matches

### `docs/research/BIAS_OF_FIXTURES_AUDIT_001_SUMMARY.md`

Patterns: `campaign_011`, `campaign_014`, `campaign_012`
Match count: 4

- L16 `campaign_011`: The lab's research substrate — the CAMPAIGN_011 null, the
- L76 `campaign_014`: | event fixtures | 1 | `research/calendar/fixtures/campaign_014_events.json` (281 events) |
- L88 `campaign_011`: CAMPAIGN_011 is **acceptable** as the binding null baseline.
- L211 `campaign_012`: 3. **An optional CAMPAIGN_012-014 test-only re-execution** to

### `docs/research/C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`

Patterns: `campaign_011`, `campaign_012`, `random_entry_anchor`
Match count: 21

- L14 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
- L30 `campaign_011`: | universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD (same as CAMPAIGN_010 / CAMPAIGN_011) |
- L36 `campaign_011`: CAMPAIGN_011 (deterministic feature-driven entry vs random),
- L51 `campaign_012`: | `version` | `0.1.0-c012` | candidate id; matches the CAMPAIGN_012 label proposed in Phase 4 |
- L52 `campaign_011`: | `timeframe` | `H4` | matches CAMPAIGN_010 / CAMPAIGN_011 (only authorized intraday timeframe) |
- … 16 more matches

### `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md`

Patterns: `campaign_014`, `campaign_011`, `campaign_012`, `campaign_013`, `random_entry_anchor`, `old_null_trades`
Match count: 38

- L7 `campaign_014`: CAMPAIGN_014 / `calendar_event_window_anomaly 0.1.0-c014`** candidate
- L13 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
- L14 `campaign_012`: > CAMPAIGN_012 / CAMPAIGN_013 all remain REJECT.
- L14 `campaign_013`: > CAMPAIGN_012 / CAMPAIGN_013 all remain REJECT.
- L16 `campaign_011`: > demo / live remain blocked. CAMPAIGN_011 is the **null baseline
- … 33 more matches

### `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_001_SUMMARY.md`

Patterns: `campaign_014`, `campaign_011`, `campaign_012`, `campaign_013`
Match count: 33

- L6 `campaign_014`: End-of-sprint summary for the CAMPAIGN_014 / C7 calendar-event window
- L14 `campaign_014`: > REJECT and untouched. CAMPAIGN_014 is **scaffold-only**; no evidence
- L63 `campaign_014`: | fixture file | `research/calendar/fixtures/campaign_014_events.json` |
- L65 `campaign_014`: | schema | `campaign_014.event_fixture.v1` |
- L69 `campaign_014`: | compilation method | offline deterministic Python script (`scripts/build_campaign_014_event_fixture.py`) |
- … 28 more matches

### `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`

Patterns: `campaign_014`, `campaign_011`, `old_null_trades`, `campaign_012`, `campaign_013`
Match count: 14

- L6 `campaign_014`: Phase 1 machine-facing implementation spec for **CAMPAIGN_014 /
- L100 `campaign_014`: | `event_calendar_path` | `"research/calendar/fixtures/campaign_014_events.json"` | committed text fixture; broker-free |
- L115 `campaign_014`: (`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`, Phase 5) freezes them
- L130 `campaign_011`: | **comparison to CAMPAIGN_011 null floor** | well below 1,177 (~3.5–7 × less) |
- L130 `old_null_trades`: | **comparison to CAMPAIGN_011 null floor** | well below 1,177 (~3.5–7 × less) |
- … 9 more matches

### `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_READINESS.md`

Patterns: `campaign_014`, `campaign_013`, `campaign_011`, `old_null_trades`, `old_null_expectancy`, `old_null_pf`, `old_null_return`
Match count: 29

- L6 `campaign_014`: Phase 5 scaffold-readiness summary for **CAMPAIGN_014 /
- L24 `campaign_014`: | 6 | committed event-calendar fixture | ✓ `research/calendar/fixtures/campaign_014_events.json` (281 events) |
- L25 `campaign_014`: | 7 | fixture provenance documented | ✓ `CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md` |
- L26 `campaign_014`: | 8 | research-only YAML config | ✓ `configs/campaign_014_calendar_event_window_anomaly.yaml` |
- L29 `campaign_014`: | 11 | binding pre-commit checklist | ✓ `CAMPAIGN_014_PRECOMMIT_CHECKLIST.md` |
- … 24 more matches

### `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md`

Patterns: `campaign_014`, `campaign_011`, `random_entry_anchor`, `campaign_012`, `campaign_013`
Match count: 52

- L7 `campaign_014`: Phase 0 sprint plan for the CAMPAIGN_014 evidence-grade walk-forward
- L17 `campaign_014`: > REJECT. CAMPAIGN_014 is candidate-scaffold-only before this sprint;
- L20 `campaign_011`: > remains `approved: []`. CAMPAIGN_011 is the null baseline only —
- L32 `campaign_014`: | ruff baseline | **3 pre-existing in `research/lean_parity/algorithms/`** (unchanged from CAMPAIGN_014 scaffold sprint) |
- L41 `campaign_014`: ### 2.1 CAMPAIGN_014 scaffold deliverables (verified present)
- … 47 more matches

### `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_SUMMARY.md`

Patterns: `campaign_014`, `campaign_011`, `old_null_trades`, `old_null_expectancy`, `old_null_pf`
Match count: 37

- L7 `campaign_014`: End-of-sprint summary for the CAMPAIGN_014 / C7 calendar-event
- L12 `campaign_014`: > CAMPAIGN_014 joins CAMPAIGN_002 / 010 / 011 / 012 / 013 as REJECT
- L21 `campaign_014`: | files added (NEW source) | `scripts/run_campaign_014.py` (~620 LOC) + `scripts/build_campaign_014_financing_overlay.py` (~210 LOC) + `scripts/build_campaign_014_risk_diagnostics.py` (~390 LOC) = ~1,220 source LOC |
- L22 `campaign_014`: | files added (NEW docs) | 10 docs (Phase 0 plan + audit; Phase 1 provenance; Phase 2 plan doc; Phase 4 execution; Phase 5 verdict; Phase 6 financing; Phase 7 risk; Phase 8 verifier; Phase 9 evidence summary; Phase 9 this summary) + edits t
- L25 `campaign_014`: | files edited | 4 (`tests/unit/test_validate_research_archive.py`, `docs/research/EVIDENCE_MANIFEST.json`, `docs/research/STRATEGY_STATUS.md`, `docs/research/EVIDENCE_INDEX.md`, `docs/research/CAMPAIGN_014_STATUS.md`) |
- … 32 more matches

### `docs/research/CAMPAIGN_011_DATA_PROVENANCE.md`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 8

- L1 `campaign_011`: # CAMPAIGN_011 — Data Provenance
- L6 `campaign_011`: Phase 1 data-provenance record for the **CAMPAIGN_011
- L16 `campaign_011`: > **CAMPAIGN_011 is a null model — cannot be approved by design.**
- L60 `campaign_011`: - The CAMPAIGN_011 entry-signal comparison is on **identical
- L110 `campaign_011`: - [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- … 3 more matches

### `docs/research/CAMPAIGN_011_DEDUPED_NULL_BASELINE.md`

Patterns: `campaign_011`, `canonical_null_json`, `campaign_012`, `random_entry_anchor`, `old_null_json_path`, `old_null_trades`, `old_null_expectancy`
Match count: 17

- L1 `campaign_011`: # CAMPAIGN_011 — Deduped Null Baseline
- L3 `campaign_011`: **Sprint:** CAMPAIGN_011_DEDUPED_NULL_BASELINE_001
- L4 `campaign_011`: **Canonical JSON:** [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json)
- L4 `canonical_null_json`: **Canonical JSON:** [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json)
- L5 `campaign_012`: **Status:** NULL MODEL — REJECT expected; metrics are the falsifiability floor for CAMPAIGN_012–014 re-evaluation.
- … 12 more matches

### `docs/research/CAMPAIGN_011_DEDUPED_NULL_BASELINE_001_PLAN.md`

Patterns: `campaign_011`, `campaign_012`, `random_entry_anchor`, `canonical_null_json`, `old_null_json_path`
Match count: 22

- L1 `campaign_011`: # CAMPAIGN_011 Deduped Null-Baseline Promotion — Plan
- L3 `campaign_011`: **Sprint:** CAMPAIGN_011_DEDUPED_NULL_BASELINE_001
- L10 `campaign_011`: Promote the deduped CAMPAIGN_011 random-entry anchor as the **canonical null reference** for post-dedupe evidence comparisons. This is an evidence-integrity sprint only — not strategy approval, not tuning, not paper/demo/live enablement.
- L18 `campaign_011`: | No CAMPAIGN_011 tuning or seed changes | frozen config unchanged |
- L21 `campaign_012`: | CAMPAIGN_012–014 comparisons pending re-eval | after promotion |
- … 17 more matches

### `docs/research/CAMPAIGN_011_DEDUPED_NULL_BASELINE_001_SUMMARY.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_trades`, `old_null_expectancy`, `old_null_pf`, `canonical_null_json`, `old_null_json_path`, `campaign_012`
Match count: 31

- L1 `campaign_011`: # CAMPAIGN_011 Deduped Null-Baseline Promotion — Summary
- L9 `campaign_011`: Deduped CAMPAIGN_011 random-entry anchor promoted to **canonical null baseline**. No strategy approved. Paper/demo/live remain blocked.
- L11 `campaign_011`: ## CAMPAIGN_011 run
- L15 `campaign_011`: | Method | **Inspected** local `backtests/CAMPAIGN_011_random_entry_anchor_deduped/` (no rerun) |
- L15 `random_entry_anchor`: | Method | **Inspected** local `backtests/CAMPAIGN_011_random_entry_anchor_deduped/` (no rerun) |
- … 26 more matches

### `docs/research/CAMPAIGN_011_DEDUPED_RUN_VERIFICATION.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_trades`, `old_null_expectancy`, `old_null_pf`
Match count: 15

- L1 `campaign_011`: # CAMPAIGN_011 — Deduped Run Verification
- L3 `campaign_011`: **Sprint:** CAMPAIGN_011_DEDUPED_NULL_BASELINE_001
- L10 `campaign_011`: `backtests/CAMPAIGN_011_random_entry_anchor_deduped/` is complete,
- L10 `random_entry_anchor`: `backtests/CAMPAIGN_011_random_entry_anchor_deduped/` is complete,
- L11 `campaign_011`: consistent with frozen CAMPAIGN_011 settings, and suitable as the
- … 10 more matches

### `docs/research/CAMPAIGN_011_EVIDENCE_SUMMARY.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_trades`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `old_null_json_path`
Match count: 47

- L1 `campaign_011`: # CAMPAIGN_011 — Evidence Summary
- L6 `campaign_011`: One-page evidence summary for **CAMPAIGN_011** /
- L7 `random_entry_anchor`: `random_entry_anchor 0.1.0-c011` — the C5 diagnostic-anchor
- L13 `campaign_011`: > Paper / demo / live remain blocked. **CAMPAIGN_011 cannot be
- L21 `campaign_011`: | campaign label | `CAMPAIGN_011` |
- … 42 more matches

### `docs/research/CAMPAIGN_011_FINANCING_OVERLAY.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`, `old_null_trades`, `old_null_return`, `old_null_expectancy`, `old_null_pf`
Match count: 46

- L1 `campaign_011`: # CAMPAIGN_011 — Financing Overlay (ESTIMATED + Conservative Stress)
- L6 `campaign_011`: Phase 6 financing overlay for the CAMPAIGN_011 walk-forward
- L10 `campaign_011`: both long and short) to every committed CAMPAIGN_011 trade.
- L19 `campaign_011`: > **CAMPAIGN_011 is a null model — cannot be approved by design.**
- L37 `campaign_011`: .venv/bin/python scripts/build_campaign_011_financing_overlay.py \
- … 41 more matches

### `docs/research/CAMPAIGN_011_FINANCING_RISK_READINESS.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 42

- L1 `campaign_011`: # CAMPAIGN_011 — Financing + Portfolio-Risk Readiness
- L7 `campaign_011`: assessment for the **CAMPAIGN_011 research candidate**
- L8 `random_entry_anchor`: (`random_entry_anchor 0.1.0-c011`). **Reading this document does
- L16 `campaign_011`: > `approved: []`. **CAMPAIGN_011 is a null model — cannot be
- L29 `campaign_011`: | Risk diagnostics script | **NOT YET WRITTEN** — `scripts/build_campaign_011_risk_diagnostics.py` is a future-evidence-sprint task; clone `scripts/build_campaign_010_risk_diagnostics.py` and swap the `CAMPAIGN_011` constant |
- … 37 more matches

### `docs/research/CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 31

- L1 `campaign_011`: # CAMPAIGN_011 — Independent Verifier Readiness
- L7 `campaign_011`: for **CAMPAIGN_011** / `random_entry_anchor 0.1.0-c011`.
- L7 `random_entry_anchor`: for **CAMPAIGN_011** / `random_entry_anchor 0.1.0-c011`.
- L13 `campaign_011`: > `approved: []`. **CAMPAIGN_011 is a null model — cannot be
- L24 `random_entry_anchor`: | can verifier run `random_entry_anchor` today? | **no** — the entry / exit rules in `research/parity_verifier/rules.py` implement only the CAMPAIGN_002 logic; there is no `random_entry_anchor` rule path |
- … 26 more matches

### `docs/research/CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 40

- L1 `campaign_011`: # CAMPAIGN_011 — Independent Verifier Status
- L7 `campaign_011`: verifier (`research/parity_verifier/`) against CAMPAIGN_011 /
- L8 `random_entry_anchor`: `random_entry_anchor 0.1.0-c011`. **This document does not
- L15 `campaign_011`: > remains REJECT. **CAMPAIGN_011 verdict = REJECT (null-model
- L27 `random_entry_anchor`: | can verifier run `random_entry_anchor` today? | **no** — the entry / exit rules in `research/parity_verifier/rules.py` implement only the CAMPAIGN_002 logic; there is no `random_entry_anchor` rule path |
- … 35 more matches

### `docs/research/CAMPAIGN_011_NORISK_REFERENCE_001_PLAN.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 62

- L1 `campaign_011`: # CAMPAIGN_011 no-RiskEngine bespoke reference — Sprint 001 Plan
- L9 `campaign_011`: > CAMPAIGN_011 rules, does not change CAMPAIGN_011's verdict, and
- L12 `campaign_011`: > CAMPAIGN_011 remains **REJECT / null diagnostic anchor by design**.
- L17 `campaign_011`: `random_entry_anchor 0.1.0-c011` (CAMPAIGN_011), suitable for the
- L17 `random_entry_anchor`: `random_entry_anchor 0.1.0-c011` (CAMPAIGN_011), suitable for the
- … 57 more matches

### `docs/research/CAMPAIGN_011_NORISK_REFERENCE_CONTRACT.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 53

- L1 `campaign_011`: # CAMPAIGN_011 no-RiskEngine reference — schema contract
- L5 `campaign_011`: **Phase:** 1 of `CAMPAIGN_011_NORISK_REFERENCE_001_PLAN.md`
- L10 `campaign_011`: > before Phase 2 generates it. Approves nothing. CAMPAIGN_011 remains
- L15 `campaign_011`: A future Backtrader CAMPAIGN_011 comparison sprint must be able to
- L29 `campaign_011`: | Plan source | `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json` (committed) | the rolling plan is frozen pre-commit; this sprint must **not** create a new plan |
- … 48 more matches

### `docs/research/CAMPAIGN_011_NORISK_REFERENCE_RESULT.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 35

- L1 `campaign_011`: # CAMPAIGN_011 no-RiskEngine bespoke reference — Phase 3 result
- L5 `campaign_011`: **Phase:** 3 of `CAMPAIGN_011_NORISK_REFERENCE_001_PLAN.md`
- L8 `campaign_011`: > The no-RiskEngine bespoke reference for CAMPAIGN_011 /
- L9 `random_entry_anchor`: > `random_entry_anchor 0.1.0-c011` has been generated, hash-pinned,
- L10 `campaign_011`: > and reproducibly verified. **CAMPAIGN_011 remains REJECT / null
- … 30 more matches

### `docs/research/CAMPAIGN_011_NORISK_REFERENCE_RUNNER.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 40

- L1 `campaign_011`: # CAMPAIGN_011 no-RiskEngine reference — runner
- L5 `campaign_011`: **Phase:** 2 of `CAMPAIGN_011_NORISK_REFERENCE_001_PLAN.md`
- L8 `campaign_011`: > Documents the new `scripts/export_campaign_011_norisk_reference.py`
- L10 `campaign_011`: > reference for CAMPAIGN_011. It does not approve any strategy,
- L11 `campaign_011`: > does not tune anything, and does not change CAMPAIGN_011's
- … 35 more matches

### `docs/research/CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`

Patterns: `campaign_011`, `canonical_null_json`, `random_entry_anchor`, `old_null_trades`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `above_null_claim`
Match count: 66

- L1 `campaign_011`: # CAMPAIGN_011 — Null-Baseline Interpretation
- L9 `campaign_011`: > [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json)
- L9 `canonical_null_json`: > [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json)
- L10 `campaign_011`: > and [`CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md`](CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md).
- L13 `campaign_011`: Phase 1 formalization of how CAMPAIGN_011 (`random_entry_anchor
- … 61 more matches

### `docs/research/CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md`

Patterns: `campaign_011`, `canonical_null_json`, `random_entry_anchor`, `old_null_json_path`, `old_null_trades`, `old_null_expectancy`, `old_null_pf`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 20

- L1 `campaign_011`: # CAMPAIGN_011 Null Baseline — Supersession Record
- L3 `campaign_011`: **Sprint:** CAMPAIGN_011_DEDUPED_NULL_BASELINE_001
- L10 `campaign_011`: | Machine rollup | [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json) |
- L10 `canonical_null_json`: | Machine rollup | [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json) |
- L11 `campaign_011`: | Rollup markdown | [`research/null_baselines/campaign_011_deduped_null_baseline.md`](../../research/null_baselines/campaign_011_deduped_null_baseline.md) |
- … 15 more matches

### `docs/research/CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`, `old_null_trades`
Match count: 43

- L1 `campaign_011`: # CAMPAIGN_011 — Portfolio-Risk Diagnostics
- L6 `campaign_011`: Phase 7 portfolio-risk diagnostics for the CAMPAIGN_011
- L7 `random_entry_anchor`: walk-forward evidence (`random_entry_anchor 0.1.0-c011` — the
- L10 `campaign_011`: ([`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md))
- L17 `campaign_011`: > `approved: []`. **CAMPAIGN_011 is a null model — cannot be
- … 38 more matches

### `docs/research/CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 78

- L1 `campaign_011`: # CAMPAIGN_011 — Pre-Commit Checklist
- L6 `campaign_011`: Pre-commit / evaluation checklist for **CAMPAIGN_011** /
- L7 `random_entry_anchor`: `random_entry_anchor 0.1.0-c011` — the **C5 diagnostic anchor /
- L16 `campaign_011`: > `approved: []`. Paper / demo / live remain blocked. **CAMPAIGN_011
- L24 `campaign_011`: | campaign label | `CAMPAIGN_011` |
- … 73 more matches

### `docs/research/CAMPAIGN_011_SMOKE_RESULT.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 35

- L1 `campaign_011`: # CAMPAIGN_011 — Non-Evidence Smoke Result
- L6 `campaign_011`: Phase 5 **non-evidence** smoke result for CAMPAIGN_011 /
- L7 `random_entry_anchor`: `random_entry_anchor 0.1.0-c011`. **These smokes are NOT
- L15 `campaign_011`: > **CAMPAIGN_011 is a null model — cannot be approved by design.**
- L25 `campaign_011`: s = load_settings('configs/campaign_011_random_entry_anchor.yaml')
- … 30 more matches

### `docs/research/CAMPAIGN_011_STATUS.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `old_null_json_path`, `old_null_trades`
Match count: 58

- L1 `campaign_011`: # CAMPAIGN_011 — Status
- L6 `campaign_011`: Status of the **CAMPAIGN_011 research candidate**
- L7 `random_entry_anchor`: (`random_entry_anchor 0.1.0-c011`) at the close of the
- L12 `campaign_011`: > - **CAMPAIGN_011 is a null model by design.** It cannot be
- L24 `campaign_011`: >   [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md).
- … 53 more matches

### `docs/research/CAMPAIGN_011_WALK_FORWARD_EXECUTION.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`, `old_null_expectancy`, `old_null_trades`, `old_null_pf`, `old_null_return`
Match count: 53

- L1 `campaign_011`: # CAMPAIGN_011 — Walk-Forward Execution
- L6 `campaign_011`: Phase 4 per-fold execution record for the CAMPAIGN_011 research
- L7 `random_entry_anchor`: candidate (`random_entry_anchor 0.1.0-c011` — the C5
- L9 `campaign_011`: the strategy. CAMPAIGN_011 is a null model — cannot be approved
- L16 `campaign_011`: > `approved: []`. **CAMPAIGN_011 cannot be approved by design.**
- … 48 more matches

### `docs/research/CAMPAIGN_011_WALK_FORWARD_PLAN.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 35

- L1 `campaign_011`: # CAMPAIGN_011 — Walk-Forward Plan
- L6 `campaign_011`: Phase 2 authoritative walk-forward plan for the CAMPAIGN_011
- L7 `random_entry_anchor`: research candidate (`random_entry_anchor 0.1.0-c011` — the C5
- L14 `campaign_011`: > `approved: []`. **CAMPAIGN_011 is a null model — cannot be
- L22 `campaign_011`: [`CAMPAIGN_011_WALK_FORWARD_READINESS.md`](CAMPAIGN_011_WALK_FORWARD_READINESS.md)
- … 30 more matches

### `docs/research/CAMPAIGN_011_WALK_FORWARD_READINESS.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 43

- L1 `campaign_011`: # CAMPAIGN_011 — Walk-Forward Readiness
- L7 `campaign_011`: **CAMPAIGN_011 research candidate** (`random_entry_anchor
- L7 `random_entry_anchor`: **CAMPAIGN_011 research candidate** (`random_entry_anchor
- L15 `campaign_011`: > `approved: []`. Paper / demo / live remain blocked. **CAMPAIGN_011
- L24 `campaign_011`: | `parameter_mode = "frozen"` compatibility | **READY** | design + spec mandate frozen mode (only authorised); confirmed in `configs/campaign_011_random_entry_anchor.yaml` |
- … 38 more matches

### `docs/research/CAMPAIGN_011_WALK_FORWARD_RESULT.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`, `old_null_expectancy`, `old_null_pf`, `old_null_trades`, `old_null_return`
Match count: 58

- L1 `campaign_011`: # CAMPAIGN_011 — Walk-Forward Result and Verdict
- L11 `campaign_011`: Phase 5 formal classification of the CAMPAIGN_011 walk-forward
- L12 `random_entry_anchor`: evidence (`random_entry_anchor 0.1.0-c011` — the C5
- L15 `campaign_011`: [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- L22 `campaign_011`: > **CAMPAIGN_011 is a null model — cannot be approved by design.
- … 53 more matches

### `docs/research/CAMPAIGN_012_DATA_PROVENANCE.md`

Patterns: `campaign_012`, `campaign_011`
Match count: 21

- L1 `campaign_012`: # CAMPAIGN_012 Data Provenance — H4 OANDA-practice 7-pair store
- L6 `campaign_012`: Phase 1 data-provenance record for CAMPAIGN_012 /
- L8 `campaign_012`: fetched.** The CAMPAIGN_012 evidence sprint reuses the validated
- L10 `campaign_011`: CAMPAIGN_011 (byte-for-byte identical candles).
- L15 `campaign_011`: > CAMPAIGN_011 is the **null baseline only**, not a trading candidate.
- … 16 more matches

### `docs/research/CAMPAIGN_012_EVIDENCE_SUMMARY.md`

Patterns: `campaign_012`, `campaign_011`, `old_null_trades`, `old_null_expectancy`, `old_null_pf`, `old_null_return`
Match count: 36

- L1 `campaign_012`: # CAMPAIGN_012 Evidence Summary
- L6 `campaign_012`: One-page evidence summary for **CAMPAIGN_012 /
- L13 `campaign_011`: > markedly **worse** than CAMPAIGN_011 null baseline (well outside
- L22 `campaign_011`: | metric | CAMPAIGN_012 | CAMPAIGN_011 (null floor) | gate |
- L22 `campaign_012`: | metric | CAMPAIGN_012 | CAMPAIGN_011 (null floor) | gate |
- … 31 more matches

### `docs/research/CAMPAIGN_012_FINANCING_OVERLAY.md`

Patterns: `campaign_012`, `campaign_011`
Match count: 24

- L1 `campaign_012`: # CAMPAIGN_012 Financing Overlay (Phase 6)
- L7 `campaign_012`: **CAMPAIGN_012 / `regime_switcher_atr_percentile 0.1.0-c012`**. The
- L16 `campaign_012`: > CAMPAIGN_002 / 010 / 011 remain REJECT. CAMPAIGN_012 verdict
- L35 `campaign_012`: `build_campaign_012_financing_overlay.py` script aborts before any
- L45 `campaign_012`: python scripts/build_campaign_012_financing_overlay.py \
- … 19 more matches

### `docs/research/CAMPAIGN_012_FINANCING_RISK_READINESS.md`

Patterns: `campaign_012`, `campaign_011`
Match count: 21

- L1 `campaign_012`: # CAMPAIGN_012 Financing / Risk Readiness
- L27 `campaign_012`:   to switch source in CAMPAIGN_012 must abort the runner.
- L43 `campaign_012`: CAMPAIGN_012's evidence sprint cannot lift this blocker. Even a
- L44 `campaign_012`: passing CAMPAIGN_012 retains the live-promotion blocker; paper
- L51 `campaign_011`:   rollover event (consistent with CAMPAIGN_010 / CAMPAIGN_011 on the
- … 16 more matches

### `docs/research/CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md`

Patterns: `campaign_012`, `campaign_011`
Match count: 10

- L1 `campaign_012`: # CAMPAIGN_012 Independent-Verifier Readiness
- L7 `campaign_012`: CAMPAIGN_012. This doc records the current capability gap, when the
- L32 `campaign_011`: - CAMPAIGN_011 verifier status: same; null-model REJECT did not require
- L42 `campaign_012`: If CAMPAIGN_012's evidence verdict is REJECT (any reason — per-fold
- L49 `campaign_012`: If CAMPAIGN_012's evidence verdict reaches **`RESEARCH_PASS_UNAPPROVED`**:
- … 5 more matches

### `docs/research/CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md`

Patterns: `campaign_012`, `campaign_011`, `random_entry_anchor`
Match count: 18

- L1 `campaign_012`: # CAMPAIGN_012 Independent Verifier Status (Phase 8)
- L6 `campaign_012`: Phase 8 verifier-status assessment for **CAMPAIGN_012 /
- L16 `campaign_012`: > CAMPAIGN_012. No strategy approved.
- L26 `campaign_011`: | supports `random_entry_anchor` (CAMPAIGN_011)? | **NO** (no PRNG re-implementation) |
- L26 `random_entry_anchor`: | supports `random_entry_anchor` (CAMPAIGN_011)? | **NO** (no PRNG re-implementation) |
- … 13 more matches

### `docs/research/CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md`

Patterns: `campaign_012`, `campaign_011`
Match count: 35

- L1 `campaign_012`: # CAMPAIGN_012 Portfolio-Risk Diagnostics (Phase 7)
- L6 `campaign_012`: Phase 7 portfolio-risk diagnostics for **CAMPAIGN_012 /
- L11 `campaign_011`: comparison to CAMPAIGN_010 / CAMPAIGN_011 diagnostics.
- L14 `campaign_012`: > remains `approved: []`. CAMPAIGN_012 verdict remains REJECT.
- L19 `campaign_012`: python scripts/build_campaign_012_risk_diagnostics.py \
- … 30 more matches

### `docs/research/CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md`

Patterns: `campaign_012`, `superseded_null_reference`, `campaign_011`, `canonical_null_json`, `old_null_expectancy`, `old_null_trades`, `old_null_return`, `old_null_pf`
Match count: 28

- L1 `campaign_012`: # CAMPAIGN_012 — Post-Dedup Null Reference Refresh
- L5 `campaign_012`: **Campaign:** CAMPAIGN_012 / `regime_switcher_atr_percentile 0.1.0-c012`
- L14 `superseded_null_reference`: | Old null comparison | **SUPERSEDED_NULL_REFERENCE** |
- L19 `campaign_011`: Source: [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json)
- L19 `canonical_null_json`: Source: [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json)
- … 23 more matches

### `docs/research/CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`

Patterns: `campaign_012`, `campaign_011`, `old_null_expectancy`, `old_null_pf`, `old_null_return`
Match count: 24

- L1 `campaign_012`: # CAMPAIGN_012 — Pre-Commit Checklist (`regime_switcher_atr_percentile 0.1.0-c012`)
- L7 `campaign_012`: Binding pre-commit for CAMPAIGN_012 / `regime_switcher_atr_percentile 0.1.0-c012`,
- L15 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 remain
- L17 `campaign_011`: > Paper / demo / live remain blocked. CAMPAIGN_011 is the **null baseline
- L25 `campaign_011`: > momentum also lost. CAMPAIGN_011 demonstrated that random entry on the
- … 19 more matches

### `docs/research/CAMPAIGN_012_REJECTION_CLOSEOUT.md`

Patterns: `campaign_012`, `campaign_011`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `old_null_trades`
Match count: 55

- L1 `campaign_012`: # CAMPAIGN_012 Rejection Closeout
- L6 `campaign_012`: Phase 1 binding closeout for **CAMPAIGN_012 /
- L8 `campaign_012`: verdict and the off-limits parameter surface. **No CAMPAIGN_012
- L13 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
- L14 `campaign_012`: > CAMPAIGN_012 all remain REJECT. `configs/approved_strategies.yaml`
- … 50 more matches

### `docs/research/CAMPAIGN_012_SMOKE_RESULT.md`

Patterns: `campaign_012`, `campaign_011`
Match count: 16

- L1 `campaign_012`: # CAMPAIGN_012 Smoke Result — `regime_switcher_atr_percentile 0.1.0-c012`
- L6 `campaign_012`: Phase 5 NON-EVIDENCE smoke for the CAMPAIGN_012 scaffold. **This is not
- L14 `campaign_011`: > CAMPAIGN_002 / 010 / 011 remain REJECT and untouched. CAMPAIGN_011
- L21 `campaign_012`: | `python -c "from forex_bot.config import load_settings; s = load_settings('configs/campaign_012_regime_switcher_atr_percentile.yaml')"` | config-load smoke | **PASS** — all 12 frozen parameters parse to the expected types + values; `app.m
- L25 `campaign_011`: | `python scripts/run_walk_forward_dry_run.py --campaign-name CAMPAIGN_012_regime_switcher_atr_percentile --style rolling --parameter-mode frozen --train-days 540 --validation-days 180 --test-days 180 --step-days 180 --universe-start 2020-0
- … 11 more matches

### `docs/research/CAMPAIGN_012_STATUS.md`

Patterns: `campaign_012`, `campaign_011`, `old_null_expectancy`, `old_null_return`, `old_null_pf`, `old_null_trades`
Match count: 38

- L1 `campaign_012`: # CAMPAIGN_012 Status — `regime_switcher_atr_percentile 0.1.0-c012`
- L10 `campaign_012`: | campaign id | CAMPAIGN_012 |
- L12 `campaign_011`: | backtest verdict | **REJECT** (5 of 8 inherited aggregate gates fail; markedly worse than CAMPAIGN_011 null baseline) |
- L13 `campaign_012`: | walk-forward verdict | REJECT (`CAMPAIGN_012_WALK_FORWARD_RESULT.md`) |
- L15 `campaign_011`: | portfolio-risk diagnostics verdict | diagnostic only (8 / 8 sanity checks pass; uniform-noise distribution shape, like CAMPAIGN_011 null) |
- … 33 more matches

### `docs/research/CAMPAIGN_012_WALK_FORWARD_EXECUTION.md`

Patterns: `campaign_012`, `campaign_011`, `random_entry_anchor`, `old_null_trades`, `old_null_expectancy`, `old_null_return`, `old_null_pf`
Match count: 39

- L1 `campaign_012`: # CAMPAIGN_012 Walk-Forward Execution (Phase 4)
- L6 `campaign_012`: Phase 4 per-fold execution record for **CAMPAIGN_012 /
- L13 `campaign_011`: > CAMPAIGN_011 is the **null baseline only**; this sprint compares
- L14 `campaign_011`: > CAMPAIGN_012's metrics to CAMPAIGN_011's verbatim floor and does
- L14 `campaign_012`: > CAMPAIGN_012's metrics to CAMPAIGN_011's verbatim floor and does
- … 34 more matches

### `docs/research/CAMPAIGN_012_WALK_FORWARD_PLAN.md`

Patterns: `campaign_012`, `campaign_011`, `old_null_expectancy`, `old_null_pf`, `old_null_return`
Match count: 28

- L1 `campaign_012`: # CAMPAIGN_012 Walk-Forward Plan (Phase 2)
- L6 `campaign_012`: Authoritative Phase 2 walk-forward plan for **CAMPAIGN_012 /
- L15 `campaign_011`: ## 1. Plan structure (inherited verbatim from CAMPAIGN_010 / CAMPAIGN_011)
- L27 `campaign_011`: | **fold count** | **8** | matches CAMPAIGN_010 / CAMPAIGN_011 verbatim |
- L34 `campaign_012`:   --campaign-name CAMPAIGN_012_regime_switcher_atr_percentile \
- … 23 more matches

### `docs/research/CAMPAIGN_012_WALK_FORWARD_READINESS.md`

Patterns: `campaign_012`, `campaign_011`, `above_null_claim`, `old_null_expectancy`, `old_null_pf`, `old_null_return`
Match count: 40

- L1 `campaign_012`: # CAMPAIGN_012 Walk-Forward Readiness
- L12 `campaign_011`: > `configs/approved_strategies.yaml` remains `approved: []`. CAMPAIGN_011
- L22 `campaign_011`: | sibling reference (CAMPAIGN_011) | `research-random-entry-diagnostic-anchor-walk-forward-001` |
- L25 `campaign_011`: ## 2. Expected plan parameters (inherited verbatim from CAMPAIGN_010 / CAMPAIGN_011)
- L39 `campaign_011`: identical to CAMPAIGN_010 / CAMPAIGN_011 plans):
- … 35 more matches

### `docs/research/CAMPAIGN_012_WALK_FORWARD_RESULT.md`

Patterns: `campaign_012`, `campaign_011`, `old_null_expectancy`, `old_null_return`, `old_null_pf`, `old_null_trades`, `random_entry_anchor`
Match count: 59

- L1 `campaign_012`: # CAMPAIGN_012 Walk-Forward Result (Phase 5)
- L7 `campaign_011`: > null-baseline comparison used pre-fix SQLite; CAMPAIGN_011 baseline is
- L10 `campaign_012`: Formal Phase 5 verdict for **CAMPAIGN_012 /
- L14 `campaign_011`: > fail; CAMPAIGN_012 is markedly worse than the CAMPAIGN_011 null
- L14 `campaign_012`: > fail; CAMPAIGN_012 is markedly worse than the CAMPAIGN_011 null
- … 54 more matches

### `docs/research/CAMPAIGN_013_DATA_PROVENANCE.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`
Match count: 23

- L1 `campaign_013`: # CAMPAIGN_013 Data Provenance — H4 OANDA-practice 7-pair store
- L6 `campaign_013`: Phase 1 data-provenance record for CAMPAIGN_013 /
- L8 `campaign_013`: was fetched.** The CAMPAIGN_013 evidence sprint reuses the validated
- L10 `campaign_011`: CAMPAIGN_011 / CAMPAIGN_012 (byte-for-byte identical candles).
- L10 `campaign_012`: CAMPAIGN_011 / CAMPAIGN_012 (byte-for-byte identical candles).
- … 18 more matches

### `docs/research/CAMPAIGN_013_EVIDENCE_SUMMARY.md`

Patterns: `campaign_013`, `campaign_011`, `old_null_trades`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `campaign_012`
Match count: 42

- L1 `campaign_013`: # CAMPAIGN_013 Evidence Summary
- L6 `campaign_013`: One-page evidence summary for **CAMPAIGN_013 /
- L14 `campaign_011`: > factor, and trade count. Catastrophically worse than CAMPAIGN_011
- L26 `campaign_011`: | metric | CAMPAIGN_013 | CAMPAIGN_011 (null floor) | gate |
- L26 `campaign_013`: | metric | CAMPAIGN_013 | CAMPAIGN_011 (null floor) | gate |
- … 37 more matches

### `docs/research/CAMPAIGN_013_FINANCING_OVERLAY.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`, `old_null_trades`
Match count: 34

- L1 `campaign_013`: # CAMPAIGN_013 Financing Overlay (Phase 6)
- L7 `campaign_013`: **CAMPAIGN_013 / `cross_pair_currency_strength_rotation 0.1.0-c013`**.
- L18 `campaign_013`: > CAMPAIGN_002 / 010 / 011 / 012 remain REJECT. CAMPAIGN_013 verdict
- L37 `campaign_013`: `build_campaign_013_financing_overlay.py` script aborts before any
- L47 `campaign_013`: python scripts/build_campaign_013_financing_overlay.py \
- … 29 more matches

### `docs/research/CAMPAIGN_013_FINANCING_RISK_READINESS.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`
Match count: 20

- L1 `campaign_013`: # CAMPAIGN_013 Financing / Risk Readiness
- L27 `campaign_013`:   attempt to switch source in CAMPAIGN_013 must abort the runner.
- L49 `campaign_013`: | `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/financing/financing_run.json` | per-rollover-event detail |
- L50 `campaign_013`: | `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/financing/financing_run.md` | human-readable per-position summary |
- L51 `campaign_013`: | `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/financing/financing_summary.json` | aggregate + by-pair / by-side / by-fold breakdown |
- … 15 more matches

### `docs/research/CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md`

Patterns: `campaign_013`, `random_entry_anchor`, `campaign_011`, `campaign_012`
Match count: 15

- L1 `campaign_013`: # CAMPAIGN_013 Independent-Verifier Readiness
- L7 `campaign_013`: CAMPAIGN_013. Records the current capability gap, when the gap must
- L40 `campaign_013`: If CAMPAIGN_013's evidence verdict is REJECT (any reason — per-fold
- L47 `campaign_013`: If CAMPAIGN_013's evidence verdict reaches **`RESEARCH_PASS_UNAPPROVED`**:
- L67 `campaign_013`: | trigger | only required if CAMPAIGN_013 evidence verdict is `RESEARCH_PASS_UNAPPROVED` |
- … 10 more matches

### `docs/research/CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md`

Patterns: `campaign_013`, `campaign_011`, `random_entry_anchor`, `campaign_012`, `old_null_return`
Match count: 29

- L1 `campaign_013`: # CAMPAIGN_013 Independent Verifier Status (Phase 8)
- L6 `campaign_013`: Phase 8 verifier-status assessment for **CAMPAIGN_013 /
- L16 `campaign_013`: > CAMPAIGN_013. No strategy approved.
- L26 `campaign_011`: | supports `random_entry_anchor` (CAMPAIGN_011)? | **NO** (no PRNG re-implementation) |
- L26 `random_entry_anchor`: | supports `random_entry_anchor` (CAMPAIGN_011)? | **NO** (no PRNG re-implementation) |
- … 24 more matches

### `docs/research/CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md`

Patterns: `campaign_013`, `campaign_012`, `campaign_011`
Match count: 18

- L1 `campaign_013`: # CAMPAIGN_013 Portfolio-Risk Diagnostics (Phase 7)
- L6 `campaign_013`: Phase 7 portfolio-risk diagnostics for **CAMPAIGN_013 /
- L21 `campaign_013`: python scripts/build_campaign_013_risk_diagnostics.py \
- L22 `campaign_013`:   --campaign-dir backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation
- L27 `campaign_013`: - `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/risk/diagnostics.json`
- … 13 more matches

### `docs/research/CAMPAIGN_013_POST_DEDUP_NULL_REFERENCE.md`

Patterns: `campaign_013`, `superseded_null_reference`, `campaign_011`, `canonical_null_json`, `old_null_expectancy`, `old_null_trades`, `old_null_return`, `old_null_pf`
Match count: 23

- L1 `campaign_013`: # CAMPAIGN_013 — Post-Dedup Null Reference Refresh
- L5 `campaign_013`: **Campaign:** CAMPAIGN_013 / `cross_pair_currency_strength_rotation 0.1.0-c013`
- L14 `superseded_null_reference`: | Old null comparison | **SUPERSEDED_NULL_REFERENCE** |
- L19 `campaign_011`: Source: [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json)
- L19 `canonical_null_json`: Source: [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json)
- … 18 more matches

### `docs/research/CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`

Patterns: `campaign_013`, `campaign_011`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `campaign_012`
Match count: 25

- L1 `campaign_013`: # CAMPAIGN_013 — Pre-Commit Checklist (`cross_pair_currency_strength_rotation 0.1.0-c013`)
- L7 `campaign_013`: Binding pre-commit for CAMPAIGN_013 / `cross_pair_currency_strength_rotation 0.1.0-c013`,
- L18 `campaign_011`: > demo / live remain blocked. CAMPAIGN_011 is the **null baseline
- L48 `campaign_013`: | `configs/campaign_013_cross_pair_currency_strength_rotation.yaml` | research-only loadable YAML; 7-pair H4 universe; frozen parameters; `trading_enabled: false`; `allow_order_submission: false`; `allow_live_trading: false`; `max_positions
- L135 `campaign_011`: ## 9. Null-baseline comparison requirement (binding; CAMPAIGN_011-derived)
- … 20 more matches

### `docs/research/CAMPAIGN_013_REJECTION_CLOSEOUT.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `old_null_trades`
Match count: 80

- L1 `campaign_013`: # CAMPAIGN_013 Rejection Closeout
- L6 `campaign_013`: Phase 1 binding closeout for **CAMPAIGN_013 /
- L9 `campaign_013`: the off-limits parameter surface. **No CAMPAIGN_013 verdict artifact is
- L14 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
- L15 `campaign_012`: > CAMPAIGN_012 / CAMPAIGN_013 all remain REJECT.
- … 75 more matches

### `docs/research/CAMPAIGN_013_SMOKE_RESULT.md`

Patterns: `campaign_013`, `campaign_011`
Match count: 13

- L1 `campaign_013`: # CAMPAIGN_013 Smoke Result — `cross_pair_currency_strength_rotation 0.1.0-c013`
- L6 `campaign_013`: Phase 5 NON-EVIDENCE smoke for the CAMPAIGN_013 scaffold. **This is
- L15 `campaign_011`: > CAMPAIGN_011 is the **null baseline only**, not a trading
- L22 `campaign_013`: | `python -c "from forex_bot.config import load_settings; s = load_settings('configs/campaign_013_cross_pair_currency_strength_rotation.yaml')"` | config-load smoke | **PASS** — all 9 frozen parameters parse to the expected types + values; 
- L26 `campaign_013`: | `python scripts/run_walk_forward_dry_run.py --campaign-name CAMPAIGN_013_cross_pair_currency_strength_rotation --style rolling --parameter-mode frozen --train-days 540 --validation-days 180 --test-days 180 --step-days 180 --universe-start
- … 8 more matches

### `docs/research/CAMPAIGN_013_STATUS.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`, `old_null_expectancy`, `old_null_trades`, `old_null_return`
Match count: 32

- L1 `campaign_013`: # CAMPAIGN_013 Status — `cross_pair_currency_strength_rotation 0.1.0-c013`
- L10 `campaign_013`: | campaign id | CAMPAIGN_013 |
- L12 `campaign_013`: | backtest verdict | **REJECT** ([`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md)) |
- L55 `campaign_011`:   of any campaign to date (~214 × CAMPAIGN_011's null floor; ~2.6 ×
- L56 `campaign_012`:   CAMPAIGN_012's regime-switcher).
- … 27 more matches

### `docs/research/CAMPAIGN_013_WALK_FORWARD_EXECUTION.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`, `old_null_trades`, `old_null_expectancy`, `old_null_return`, `old_null_pf`
Match count: 33

- L1 `campaign_013`: # CAMPAIGN_013 Walk-Forward Execution (Phase 4)
- L6 `campaign_013`: Phase 4 per-fold execution record for **CAMPAIGN_013 /
- L14 `campaign_011`: > CAMPAIGN_011 is the **null baseline only**.
- L19 `campaign_013`: python scripts/run_campaign_013.py \
- L20 `campaign_013`:   --config configs/campaign_013_cross_pair_currency_strength_rotation.yaml \
- … 28 more matches

### `docs/research/CAMPAIGN_013_WALK_FORWARD_PLAN.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`
Match count: 20

- L1 `campaign_013`: # CAMPAIGN_013 Walk-Forward Plan (Phase 2)
- L6 `campaign_013`: Authoritative Phase 2 walk-forward plan for **CAMPAIGN_013 /
- L33 `campaign_013`:   --campaign-name CAMPAIGN_013_cross_pair_currency_strength_rotation \
- L37 `campaign_013`:   --output backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward
- L42 `campaign_013`: - `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/plan.json`
- … 15 more matches

### `docs/research/CAMPAIGN_013_WALK_FORWARD_READINESS.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`, `old_null_expectancy`, `old_null_pf`, `old_null_return`
Match count: 31

- L1 `campaign_013`: # CAMPAIGN_013 Walk-Forward Readiness
- L13 `campaign_011`: > CAMPAIGN_011 is the **null baseline only**, not a trading
- L23 `campaign_011`: | sibling reference (CAMPAIGN_011) | `research-random-entry-diagnostic-anchor-walk-forward-001` |
- L24 `campaign_012`: | sibling reference (CAMPAIGN_012) | `research-regime-switcher-atr-percentile-walk-forward-001` |
- L43 `campaign_013`: The CAMPAIGN_013 runner is **structurally different** from
- … 26 more matches

### `docs/research/CAMPAIGN_013_WALK_FORWARD_RESULT.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`, `old_null_expectancy`, `old_null_return`, `old_null_pf`, `old_null_trades`, `random_entry_anchor`
Match count: 67

- L1 `campaign_013`: # CAMPAIGN_013 Walk-Forward Result (Phase 5)
- L9 `campaign_013`: Formal Phase 5 verdict for **CAMPAIGN_013 /
- L13 `campaign_013`: > fail; CAMPAIGN_013 is the **worst-performing campaign to date** on
- L21 `campaign_011`: > CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 / CAMPAIGN_012 remain
- L21 `campaign_012`: > CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 / CAMPAIGN_012 remain
- … 62 more matches

### `docs/research/CAMPAIGN_014_DATA_PROVENANCE.md`

Patterns: `campaign_014`, `campaign_011`, `campaign_012`, `campaign_013`
Match count: 38

- L1 `campaign_014`: # CAMPAIGN_014 Data Provenance — H4 OANDA-practice 7-pair store + event fixture
- L6 `campaign_014`: Phase 1 data-provenance record for CAMPAIGN_014 /
- L8 `campaign_014`: was fetched.** The CAMPAIGN_014 evidence sprint reuses the
- L10 `campaign_011`: CAMPAIGN_010 / CAMPAIGN_011 / CAMPAIGN_012 / CAMPAIGN_013
- L10 `campaign_012`: CAMPAIGN_010 / CAMPAIGN_011 / CAMPAIGN_012 / CAMPAIGN_013
- … 33 more matches

### `docs/research/CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md`

Patterns: `campaign_014`
Match count: 15

- L1 `campaign_014`: # CAMPAIGN_014 Event-Fixture Date-Verification Audit
- L6 `campaign_014`: Phase 0 binding date-verification audit for the committed CAMPAIGN_014
- L8 `campaign_014`: (`research/calendar/fixtures/campaign_014_events.json`,
- L9 `campaign_014`: `schema_version=campaign_014.event_fixture.v1`, 281 events). This is
- L11 `campaign_014`: [`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md)
- … 10 more matches

### `docs/research/CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`

Patterns: `campaign_014`
Match count: 17

- L1 `campaign_014`: # CAMPAIGN_014 Event-Fixture Provenance
- L6 `campaign_014`: Phase 1B provenance document for the committed CAMPAIGN_014 event-
- L18 `campaign_014`: research/calendar/fixtures/campaign_014_events.json
- L22 `campaign_014`: `campaign_014.event_fixture.v1` (see
- L28 `campaign_014`: python scripts/build_campaign_014_event_fixture.py
- … 12 more matches

### `docs/research/CAMPAIGN_014_EVIDENCE_SUMMARY.md`

Patterns: `campaign_014`, `campaign_011`, `old_null_trades`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `above_null_claim`
Match count: 37

- L1 `campaign_014`: # CAMPAIGN_014 Evidence Summary
- L6 `campaign_014`: One-page evidence summary for **CAMPAIGN_014 /
- L13 `campaign_011`: > aggregate gates fail; materially WORSE than CAMPAIGN_011 null
- L28 `campaign_011`: | metric | CAMPAIGN_014 | CAMPAIGN_011 (null floor) | gate |
- L28 `campaign_014`: | metric | CAMPAIGN_014 | CAMPAIGN_011 (null floor) | gate |
- … 32 more matches

### `docs/research/CAMPAIGN_014_FINANCING_OVERLAY.md`

Patterns: `campaign_014`, `campaign_011`, `old_null_trades`, `campaign_012`, `campaign_013`
Match count: 21

- L1 `campaign_014`: # CAMPAIGN_014 Financing Overlay (ESTIMATED + conservative stress)
- L6 `campaign_014`: Phase 6 financing-overlay record for CAMPAIGN_014 /
- L10 `campaign_014`: sprint's `CAMPAIGN_014_FINANCING_RISK_READINESS.md` §3).
- L12 `campaign_014`: > No strategy approved. CAMPAIGN_014 remains REJECT. MODELED
- L19 `campaign_014`: python scripts/build_campaign_014_financing_overlay.py \
- … 16 more matches

### `docs/research/CAMPAIGN_014_FINANCING_RISK_READINESS.md`

Patterns: `campaign_014`, `campaign_011`, `old_null_trades`, `campaign_013`
Match count: 20

- L1 `campaign_014`: # CAMPAIGN_014 Financing / Risk Readiness
- L7 `campaign_014`: summary for the **future** CAMPAIGN_014 evidence sprint. **Scaffold
- L20 `campaign_014`: | MODELED-availability gate | the future evidence sprint's `scripts/build_campaign_014_financing_overlay.py` MUST abort if treatment is MODELED |
- L40 `campaign_014`: Per [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md) §10:
- L43 `campaign_011`: - comparison to CAMPAIGN_011 null (1,177): ~3.5–7 × less
- … 15 more matches

### `docs/research/CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md`

Patterns: `campaign_014`, `campaign_013`
Match count: 16

- L1 `campaign_014`: # CAMPAIGN_014 Independent-Verifier Readiness
- L6 `campaign_014`: Phase 7 independent-verifier readiness summary for **CAMPAIGN_014 /
- L23 `campaign_014`: ## 2. Verifier extension status for CAMPAIGN_014
- L28 `campaign_014`: **Required ONLY if CAMPAIGN_014 reaches `RESEARCH_PASS_UNAPPROVED`**
- L37 `campaign_014`: | trigger condition | CAMPAIGN_014 reaches `RESEARCH_PASS_UNAPPROVED` in the evidence sprint |
- … 11 more matches

### `docs/research/CAMPAIGN_014_INDEPENDENT_VERIFIER_STATUS.md`

Patterns: `campaign_014`, `campaign_013`, `campaign_011`, `campaign_012`
Match count: 26

- L1 `campaign_014`: # CAMPAIGN_014 Independent-Verifier Status
- L6 `campaign_014`: Phase 8 independent-verifier status for CAMPAIGN_014 /
- L11 `campaign_014`: > No strategy approved. CAMPAIGN_014 REJECT (Phase 5).
- L26 `campaign_014`: ## 2. CAMPAIGN_014 verifier extension decision
- L62 `campaign_013`: | effort | medium (~5–7 days; smaller than CAMPAIGN_013's would have been because no cross-pair runner contract) |
- … 21 more matches

### `docs/research/CAMPAIGN_014_PORTFOLIO_RISK_DIAGNOSTICS.md`

Patterns: `campaign_014`, `campaign_013`, `campaign_012`, `campaign_011`
Match count: 23

- L1 `campaign_014`: # CAMPAIGN_014 Portfolio-Risk Diagnostics
- L6 `campaign_014`: Phase 7 portfolio-risk diagnostics for CAMPAIGN_014 /
- L11 `campaign_014`: > No strategy approved. CAMPAIGN_014 remains REJECT (Phase 5).
- L17 `campaign_014`: python scripts/build_campaign_014_risk_diagnostics.py \
- L18 `campaign_014`:     --campaign-dir backtests/CAMPAIGN_014_calendar_event_window_anomaly
- … 18 more matches

### `docs/research/CAMPAIGN_014_POST_DEDUP_NULL_REFERENCE.md`

Patterns: `campaign_014`, `superseded_null_reference`, `campaign_011`, `canonical_null_json`, `old_null_expectancy`, `old_null_trades`, `old_null_return`, `old_null_pf`
Match count: 23

- L1 `campaign_014`: # CAMPAIGN_014 — Post-Dedup Null Reference Refresh
- L5 `campaign_014`: **Campaign:** CAMPAIGN_014 / `calendar_event_window_anomaly 0.1.0-c014`
- L14 `superseded_null_reference`: | Old null comparison | **SUPERSEDED_NULL_REFERENCE** |
- L19 `campaign_011`: Source: [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json)
- L19 `canonical_null_json`: Source: [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json)
- … 18 more matches

### `docs/research/CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`

Patterns: `campaign_014`, `campaign_011`, `old_null_trades`, `campaign_012`, `campaign_013`, `old_null_return`
Match count: 30

- L1 `campaign_014`: # CAMPAIGN_014 Pre-Commit Checklist
- L6 `campaign_014`: Phase 5 binding pre-commit checklist for **CAMPAIGN_014 /
- L18 `campaign_011`: > `approved: []`. CAMPAIGN_011 is the null baseline only.
- L44 `campaign_014`: | `configs/campaign_014_calendar_event_window_anomaly.yaml` | research-only candidate config |
- L45 `campaign_014`: | `scripts/build_campaign_014_event_fixture.py` | deterministic fixture compilation script |
- … 25 more matches

### `docs/research/CAMPAIGN_014_SMOKE_RESULT.md`

Patterns: `campaign_014`
Match count: 25

- L1 `campaign_014`: # CAMPAIGN_014 Smoke Result
- L6 `campaign_014`: Phase 6 NON-EVIDENCE smoke checks for CAMPAIGN_014 /
- L23 `campaign_014`:     s = load_settings('configs/campaign_014_calendar_event_window_anomaly.yaml')"
- L27 `campaign_014`:     f = load_event_fixture('research/calendar/fixtures/campaign_014_events.json')"
- L54 `campaign_014`: | Config-load (`forex_bot.config.load_settings`) on `configs/campaign_014_calendar_event_window_anomaly.yaml` | **PASS** — config loads; `version=0.1.0-c014`; `enabled=['calendar_event_window_anomaly']`; `trading_enabled=False`; `allow_live
- … 20 more matches

### `docs/research/CAMPAIGN_014_STATUS.md`

Patterns: `campaign_014`, `campaign_011`, `random_entry_anchor`, `campaign_012`, `campaign_013`
Match count: 32

- L1 `campaign_014`: # CAMPAIGN_014 Status — `calendar_event_window_anomaly 0.1.0-c014` — REJECT
- L10 `campaign_014`: | campaign id | CAMPAIGN_014 |
- L13 `campaign_014`: | walk-forward verdict | **REJECT** ([`CAMPAIGN_014_WALK_FORWARD_RESULT.md`](CAMPAIGN_014_WALK_FORWARD_RESULT.md)) |
- L28 `campaign_014`: | Phase 0 fixture date-verification audit | NEW — `CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md` |
- L30 `campaign_014`: | Phase 1 data provenance | NEW — `CAMPAIGN_014_DATA_PROVENANCE.md` |
- … 27 more matches

### `docs/research/CAMPAIGN_014_WALK_FORWARD_EXECUTION.md`

Patterns: `campaign_014`, `campaign_011`, `old_null_trades`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `campaign_012`
Match count: 42

- L1 `campaign_014`: # CAMPAIGN_014 Walk-Forward Execution
- L6 `campaign_014`: Phase 4 walk-forward execution record for CAMPAIGN_014 /
- L9 `campaign_011`: expectancy R is materially negative). The CAMPAIGN_011 null-baseline
- L11 `campaign_014`: [`CAMPAIGN_014_WALK_FORWARD_RESULT.md`](CAMPAIGN_014_WALK_FORWARD_RESULT.md)
- L15 `campaign_014`: > REJECT and untouched. CAMPAIGN_014 reaches REJECT here.
- … 37 more matches

### `docs/research/CAMPAIGN_014_WALK_FORWARD_PLAN.md`

Patterns: `campaign_014`, `campaign_011`, `campaign_013`, `above_null_claim`, `old_null_trades`, `campaign_012`
Match count: 29

- L1 `campaign_014`: # CAMPAIGN_014 Walk-Forward Plan
- L6 `campaign_014`: Phase 2 authoritative walk-forward plan for **CAMPAIGN_014 /
- L14 `campaign_011`: > `approved: []`. CAMPAIGN_011 is the null baseline only.
- L20 `campaign_014`: | machine-readable plan | `backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/plan.json` |
- L21 `campaign_014`: | human-readable plan | `backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/plan.md` |
- … 24 more matches

### `docs/research/CAMPAIGN_014_WALK_FORWARD_READINESS.md`

Patterns: `campaign_014`, `campaign_013`, `campaign_011`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `above_null_claim`
Match count: 23

- L1 `campaign_014`: # CAMPAIGN_014 Walk-Forward Readiness
- L7 `campaign_014`: CAMPAIGN_014 evidence sprint
- L24 `campaign_014`: | binding pre-commit | [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md) (immutable) |
- L25 `campaign_013`: | sibling reference | `research-cross-pair-currency-strength-rotation-walk-forward-001` (CAMPAIGN_013) |
- L47 `campaign_014`: | `backtests/CAMPAIGN_014_calendar_event_window_anomaly/` | per-fold + aggregate output directory (gitignored bulky CSVs; only summary JSONs and aggregate report are committed) |
- … 18 more matches

### `docs/research/CAMPAIGN_014_WALK_FORWARD_RESULT.md`

Patterns: `campaign_014`, `campaign_011`, `campaign_012`, `old_null_expectancy`, `old_null_pf`, `old_null_trades`, `above_null_claim`, `campaign_013`
Match count: 46

- L1 `campaign_014`: # CAMPAIGN_014 Walk-Forward Result — REJECT
- L9 `campaign_014`: Phase 5 walk-forward verdict for CAMPAIGN_014 /
- L11 `campaign_011`: execution metrics with the CAMPAIGN_011 null-baseline comparison,
- L13 `campaign_014`: CAMPAIGN_014-specific event-class diagnostics.
- L16 `campaign_014`: > 011 / 012 / 013 remain REJECT and untouched. CAMPAIGN_014 joins
- … 41 more matches

### `docs/research/CAMPAIGN_015_DEDUPED_NULL_AND_ANTI_OVERFIT.md`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 5

- L9 `campaign_011`: > CAMPAIGN_011 rerun (`backtests/CAMPAIGN_011_random_entry_anchor_deduped/`).
- L9 `random_entry_anchor`: > CAMPAIGN_011 rerun (`backtests/CAMPAIGN_011_random_entry_anchor_deduped/`).
- L16 `campaign_011`: | CAMPAIGN_011 null deduped | `backtests/CAMPAIGN_011_random_entry_anchor_deduped/walk_forward/fold_detail.json` |
- L16 `random_entry_anchor`: | CAMPAIGN_011 null deduped | `backtests/CAMPAIGN_011_random_entry_anchor_deduped/walk_forward/fold_detail.json` |
- L20 `campaign_011`: | metric | CAMPAIGN_015 deduped | CAMPAIGN_011 null deduped |

### `docs/research/CAMPAIGN_015_DEDUPED_RERUN_001_SUMMARY.md`

Patterns: `campaign_011`
Match count: 1

- L43 `campaign_011`: **`WITHIN_NULL`** (deduped CAMPAIGN_011 null baseline used).

### `docs/research/CAMPAIGN_015_DEDUPED_RERUN_INTERPRETATION.md`

Patterns: `above_null_claim`
Match count: 1

- L38 `above_null_claim`: **No.** Anti-overfit label is **`WITHIN_NULL`**, not above null.

### `docs/research/CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_PRECOMMIT.md`

Patterns: `campaign_014`, `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 13

- L23 `campaign_014`: CAMPAIGN_001 — CAMPAIGN_014 are historical evidence and remain
- L196 `campaign_014`: | financing | **ESTIMATED only** — no MODELED financing in v1; `financing_treatment = "estimated"` in manifest | matches CAMPAIGN_014 financing posture |
- L274 `campaign_011`:   remaining 7 folds, compare against the CAMPAIGN_011 sample-matched
- L294 `campaign_011`: The null model is `random_entry_anchor 0.1.0-c011` (CAMPAIGN_011),
- L294 `random_entry_anchor`: The null model is `random_entry_anchor 0.1.0-c011` (CAMPAIGN_011),
- … 8 more matches

### `docs/research/CAMPAIGN_015_NULL_AND_ANTI_OVERFIT_DIAGNOSTICS.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 17

- L8 `campaign_011`: > CAMPAIGN_011 (the null baseline) is **not** modified by this
- L19 `campaign_011`: which to compare CAMPAIGN_011.
- L39 `campaign_011`: | `WITHIN_NULL` | campaign aggregate metrics sit inside the CAMPAIGN_011 null band |
- L113 `campaign_011`: ## 6. Null comparison: read-only ingest of CAMPAIGN_011
- L115 `campaign_011`: CAMPAIGN_011 (`random_entry_anchor 0.1.0-c011`) is the matched null
- … 12 more matches

### `docs/research/CAMPAIGN_015_NULL_AND_ANTI_OVERFIT_POST_RUN.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 6

- L10 `campaign_011`: **Null model:** `random_entry_anchor 0.1.0-c011` (CAMPAIGN_011), with the
- L10 `random_entry_anchor`: **Null model:** `random_entry_anchor 0.1.0-c011` (CAMPAIGN_011), with the
- L22 `campaign_011`: classifier to the rehydrate walk-forward output and the CAMPAIGN_011
- L157 `campaign_011`:   --null-fold-detail backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/fold_detail.json \
- L157 `random_entry_anchor`:   --null-fold-detail backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/fold_detail.json \
- … 1 more matches

### `docs/research/CAMPAIGN_015_POST_RUN_DIAGNOSTICS_001_PLAN.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 5

- L73 `campaign_011`: 5. How does CAMPAIGN_015 compare to the CAMPAIGN_011 random-entry
- L116 `campaign_011`: - CAMPAIGN_011 random-entry null: [`backtests/CAMPAIGN_011_random_entry_anchor/`](../../backtests/CAMPAIGN_011_random_entry_anchor/).
- L116 `random_entry_anchor`: - CAMPAIGN_011 random-entry null: [`backtests/CAMPAIGN_011_random_entry_anchor/`](../../backtests/CAMPAIGN_011_random_entry_anchor/).
- L116 `old_null_json_path`: - CAMPAIGN_011 random-entry null: [`backtests/CAMPAIGN_011_random_entry_anchor/`](../../backtests/CAMPAIGN_011_random_entry_anchor/).
- L204 `campaign_011`: - `NULL_DOMINATED` — no meaningful gap vs the CAMPAIGN_011 random-entry

### `docs/research/CAMPAIGN_015_POST_RUN_DIAGNOSTICS_001_SUMMARY.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 13

- L71 `campaign_011`: - `backtests/CAMPAIGN_011_random_entry_anchor/` — null artifacts
- L71 `random_entry_anchor`: - `backtests/CAMPAIGN_011_random_entry_anchor/` — null artifacts
- L71 `old_null_json_path`: - `backtests/CAMPAIGN_011_random_entry_anchor/` — null artifacts
- L118 `campaign_011`:   --null-fold-detail     backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/fold_detail.json \
- L118 `random_entry_anchor`:   --null-fold-detail     backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/fold_detail.json \
- … 8 more matches

### `docs/research/CAMPAIGN_015_POST_RUN_INTERPRETATION.md`

Patterns: `campaign_011`, `random_entry_anchor`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 5

- L66 `campaign_011`: | CAMPAIGN_011 | `random_entry_anchor` (null) | -0.002 |
- L66 `random_entry_anchor`: | CAMPAIGN_011 | `random_entry_anchor` (null) | -0.002 |
- L67 `campaign_012`: | CAMPAIGN_012 | `regime_switcher_atr_percentile` | -0.052 |
- L68 `campaign_013`: | CAMPAIGN_013 | `cross_pair_currency_strength_rotation` | -0.056 |
- L69 `campaign_014`: | CAMPAIGN_014 | `calendar_event_window_anomaly` | -0.148 |

### `docs/research/CAMPAIGN_015_VS_DEDUPED_NULL_CHECK.md`

Patterns: `campaign_011`, `random_entry_anchor`, `canonical_null_json`
Match count: 7

- L3 `campaign_011`: **Sprint:** CAMPAIGN_011_DEDUPED_NULL_BASELINE_001
- L12 `campaign_011`: | CAMPAIGN_011 deduped null | `backtests/CAMPAIGN_011_random_entry_anchor_deduped/walk_forward/fold_detail.json` |
- L12 `random_entry_anchor`: | CAMPAIGN_011 deduped null | `backtests/CAMPAIGN_011_random_entry_anchor_deduped/walk_forward/fold_detail.json` |
- L13 `campaign_011`: | Canonical null rollup | `research/null_baselines/campaign_011_deduped_null_baseline.json` |
- L13 `canonical_null_json`: | Canonical null rollup | `research/null_baselines/campaign_011_deduped_null_baseline.json` |
- … 2 more matches

### `docs/research/CAMPAIGN_CONTAMINATION_AUDIT_001_PLAN.md`

Patterns: `campaign_011`, `old_null_expectancy`, `old_null_trades`
Match count: 4

- L109 `campaign_011`: - CAMPAIGN_011 null-baseline docs where affected
- L155 `campaign_011`: 1. **CAMPAIGN_011 null baseline** — pre-fix bespoke metrics (−0.0024 R, 1177 trades) likely contaminated; deduped rerun folder exists locally but may need formal promotion.
- L155 `old_null_expectancy`: 1. **CAMPAIGN_011 null baseline** — pre-fix bespoke metrics (−0.0024 R, 1177 trades) likely contaminated; deduped rerun folder exists locally but may need formal promotion.
- L155 `old_null_trades`: 1. **CAMPAIGN_011 null baseline** — pre-fix bespoke metrics (−0.0024 R, 1177 trades) likely contaminated; deduped rerun folder exists locally but may need formal promotion.

### `docs/research/CAMPAIGN_CONTAMINATION_AUDIT_001_SUMMARY.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 8

- L46 `campaign_011`: | CAMPAIGN_011 null baseline must rerun? | **Yes — Priority 1.** Promote deduped rerun as canonical. |
- L48 `campaign_011`: | CAMPAIGN_010–014 rerun? | **Should rerun** after CAMPAIGN_011 deduped promotion (priorities 2–5 in backlog). |
- L58 `campaign_011`: - `docs/research/CAMPAIGN_011_WALK_FORWARD_RESULT.md`
- L59 `campaign_012`: - `docs/research/CAMPAIGN_012_WALK_FORWARD_RESULT.md`
- L60 `campaign_013`: - `docs/research/CAMPAIGN_013_WALK_FORWARD_RESULT.md`
- … 3 more matches

### `docs/research/CAMPAIGN_DATA_SOURCE_INVENTORY.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 126

- L174 `campaign_011`: ### CAMPAIGN_011 (51 artifacts)
- L176 `campaign_011`: - `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.md` — **UNKNOWN_REQUIRES_RERUN** — verdict=n/a
- L176 `random_entry_anchor`: - `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.md` — **UNKNOWN_REQUIRES_RERUN** — verdict=n/a
- L176 `old_null_json_path`: - `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.md` — **UNKNOWN_REQUIRES_RERUN** — verdict=n/a
- L177 `campaign_011`: - `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_summary.json` — **UNKNOWN_REQUIRES_RERUN** — verdict=n/a
- … 121 more matches

### `docs/research/CAMPAIGN_EVIDENCE_INTEGRITY_AFTER_DEDUP_FIX.md`

Patterns: `campaign_011`, `canonical_null_json`, `campaign_012`, `campaign_013`, `campaign_014`, `old_null_expectancy`, `old_null_trades`
Match count: 17

- L12 `campaign_011`: CAMPAIGN_011 deduped null baseline is **promoted** (`research/null_baselines/campaign_011_deduped_null_baseline.json`). CAMPAIGN_012–014 null comparisons in prior verdict docs remain **pending re-eval** against the deduped floor.
- L12 `canonical_null_json`: CAMPAIGN_011 deduped null baseline is **promoted** (`research/null_baselines/campaign_011_deduped_null_baseline.json`). CAMPAIGN_012–014 null comparisons in prior verdict docs remain **pending re-eval** against the deduped floor.
- L12 `campaign_012`: CAMPAIGN_011 deduped null baseline is **promoted** (`research/null_baselines/campaign_011_deduped_null_baseline.json`). CAMPAIGN_012–014 null comparisons in prior verdict docs remain **pending re-eval** against the deduped floor.
- L28 `campaign_011`: | CAMPAIGN_011 | DEDUP_SAFE | REJECT | no | yes | yes |
- L29 `campaign_012`: | CAMPAIGN_012 | LIKELY_CONTAMINATED | REJECT | no | no | yes |
- … 12 more matches

### `docs/research/CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`

Patterns: `campaign_011`
Match count: 5

- L330 `campaign_011`: CAMPAIGN_011 (the proposed C5 implementation) would:
- L332 `campaign_011`: | dimension | CAMPAIGN_005 | CAMPAIGN_011 (proposed) |
- L343 `campaign_011`: CAMPAIGN_011 is therefore a strictly stronger anchor than
- L355 `campaign_011`: After C5's CAMPAIGN_011 establishes the falsifiability bar, the
- L358 `campaign_011`: 1. C5 (this sprint's selection — CAMPAIGN_011)

### `docs/research/CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`

Patterns: `campaign_011`, `random_entry_anchor`, `campaign_012`
Match count: 21

- L8 `campaign_011`: rejected families plus the CAMPAIGN_011 null-model anchor) and
- L13 `campaign_011`: > remains REJECT. CAMPAIGN_011 remains REJECT (null-model
- L19 `campaign_011`: Per [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- L29 `campaign_011`: | **RAND (null)** — `random_entry_anchor 0.1.0-c011` (CAMPAIGN_011) | REJECT (null-model anchor; cannot be approved by design); functions as falsifiability floor |
- L29 `random_entry_anchor`: | **RAND (null)** — `random_entry_anchor 0.1.0-c011` (CAMPAIGN_011) | REJECT (null-model anchor; cannot be approved by design); functions as falsifiability floor |
- … 16 more matches

### `docs/research/CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md`

Patterns: `campaign_011`, `campaign_012`, `old_null_expectancy`
Match count: 19

- L10 `campaign_011`: prior + CAMPAIGN_011 null + CAMPAIGN_012 real). **No implementation;
- L10 `campaign_012`: prior + CAMPAIGN_011 null + CAMPAIGN_012 real). **No implementation;
- L32 `campaign_011`: | why distinct from CAMPAIGN_011 (null) | fully deterministic from price; no PRNG; no `master_seed` |
- L33 `campaign_012`: | why distinct from CAMPAIGN_012 | no single-pair vol gate; no close-vs-close trend filter; signal is the *rank delta* between currencies, not a within-pair momentum |
- L35 `campaign_011`: | required engine support | YES — fits single-instrument single-position invariant **per pair**, but the strategy must orchestrate across pairs in the per-bar tick (the existing per-pair runner pattern handles this naturally — same as CAMPA
- … 14 more matches

### `docs/research/CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `old_null_trades`, `random_entry_anchor`
Match count: 35

- L11 `campaign_011`: section) against the now-8 rejected baseline (5 prior + CAMPAIGN_011
- L12 `campaign_012`: null + CAMPAIGN_012 real + CAMPAIGN_013 real). **No implementation;
- L12 `campaign_013`: null + CAMPAIGN_012 real + CAMPAIGN_013 real). **No implementation;
- L21 `campaign_013`: Discovery-004's shortlist used C6–C9 (C6 → CAMPAIGN_013 REJECT; C7 / C8 /
- L26 `campaign_012`: are candidate-shortlist IDs, not CAMPAIGN_012 / CAMPAIGN_013
- … 30 more matches

### `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`, `random_entry_anchor`
Match count: 41

- L6 `campaign_013`: Phase 0 repo truth audit + 8-phase scaffold plan for **CAMPAIGN_013 /
- L13 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
- L14 `campaign_012`: > CAMPAIGN_012 all remain REJECT. `configs/approved_strategies.yaml`
- L15 `campaign_011`: > remains `approved: []`. CAMPAIGN_011 is **only the null baseline**,
- L16 `campaign_013`: > not a trading candidate. C6 / CAMPAIGN_013 is **selected but not
- … 36 more matches

### `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`
Match count: 36

- L6 `campaign_013`: End-of-sprint summary for the CAMPAIGN_013 scaffold sprint.
- L15 `campaign_011`: > Paper / demo / live remain blocked. CAMPAIGN_011 is the **null
- L39 `campaign_013`: | Phase 4 | `592f669` | research config + CAMPAIGN_013 docs |
- L50 `campaign_013`: | `configs/campaign_013_cross_pair_currency_strength_rotation.yaml` | research-only candidate config |
- L53 `campaign_013`: | `docs/research/CAMPAIGN_013_PRECOMMIT_CHECKLIST.md` | Phase 4 |
- … 31 more matches

### `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`

Patterns: `campaign_013`, `campaign_011`, `random_entry_anchor`, `campaign_012`, `old_null_expectancy`, `old_null_pf`, `old_null_return`
Match count: 21

- L6 `campaign_013`: Phase 1 binding implementation spec for **CAMPAIGN_013 /
- L15 `campaign_011`: > Paper / demo / live remain blocked. CAMPAIGN_011 is the **null
- L23 `campaign_011`: - [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (null-baseline gate)
- L149 `random_entry_anchor`: Same rule as `session_breakout` R2 / `random_entry_anchor` R2 /
- L263 `campaign_011`: Mirrors CAMPAIGN_010 R5 / CAMPAIGN_011 R5 / CAMPAIGN_012 R4 verbatim.
- … 16 more matches

### `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_READINESS.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`, `old_null_expectancy`, `old_null_pf`, `old_null_return`
Match count: 22

- L6 `campaign_013`: One-page scaffold-readiness summary for **CAMPAIGN_013 /
- L14 `campaign_011`: > Paper / demo / live remain blocked. CAMPAIGN_011 is the **null
- L25 `campaign_013`: | candidate YAML | ✓ | `configs/campaign_013_cross_pair_currency_strength_rotation.yaml` (7-pair H4 universe; `trading_enabled: false`) |
- L31 `campaign_013`: | pre-commit checklist | ✓ | [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md) committed |
- L45 `campaign_012`: | relation | mirrors `research-regime-switcher-atr-percentile-walk-forward-001` (CAMPAIGN_012 evidence) exactly |
- … 17 more matches

### `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`
Match count: 34

- L7 `campaign_013`: **CAMPAIGN_013 / `cross_pair_currency_strength_rotation 0.1.0-c013`**.
- L14 `campaign_011`: > Paper / demo / live remain blocked. **CAMPAIGN_011 is the null
- L44 `campaign_013`: ## 3. CAMPAIGN_013 scaffold status (verified)
- L52 `campaign_013`: | `configs/campaign_013_cross_pair_currency_strength_rotation.yaml` | **present**; loads cleanly via `load_settings()` |
- L53 `campaign_013`: | 10× `docs/research/CAMPAIGN_013_*` and `CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_*` docs | **all present** |
- … 29 more matches

### `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`, `old_null_expectancy`, `old_null_pf`, `old_null_return`
Match count: 47

- L6 `campaign_013`: End-of-sprint summary for the CAMPAIGN_013 evidence sprint. Ran the
- L14 `campaign_011`: > factor, and trade count. Catastrophically worse than CAMPAIGN_011
- L18 `campaign_011`: > `approved: []`. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
- L19 `campaign_012`: > CAMPAIGN_012 remain REJECT and untouched. Paper / demo / live
- L34 `campaign_012`: | walk-forward runtime | **~20.2 seconds** for 8 folds × 7 pairs = 56 backtests (much faster than CAMPAIGN_012's ~33 min; no D1AGG aggregation) |
- … 42 more matches

### `docs/research/EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md`

Patterns: `campaign_014`, `campaign_011`
Match count: 4

- L80 `campaign_014`:   CAMPAIGN_014 FOMC pattern from the brief). Lesson 6.
- L90 `campaign_011`: ## 3. Comparing against the CAMPAIGN_011 / CAMPAIGN_005 null
- L92 `campaign_011`: The sprint brief mentions CAMPAIGN_011 as the random-entry / null
- L169 `campaign_014`:    *Hypothesis:* the brief's CAMPAIGN_014 narrative (NFP dominates and

### `docs/research/EDGE_DISCOVERY_EXIT_ASYMMETRY_ADDENDUM.md`

Patterns: `campaign_014`, `campaign_011`
Match count: 7

- L25 `campaign_014`: Across CAMPAIGN_010 - CAMPAIGN_014 (5 campaigns × 7 pairs × 8 folds
- L28 `campaign_011`: - **Every** campaign including the random-entry null CAMPAIGN_011
- L59 `campaign_011`: against the CAMPAIGN_011 random-entry null **on the matched fold
- L64 `campaign_011`: - Candidate `mean_R_given_time` ≥ CAMPAIGN_011 `mean_R_given_time`
- L74 `campaign_011`: - Candidate `mean_R_given_stop` ≥ CAMPAIGN_011 `mean_R_given_stop`
- … 2 more matches

### `docs/research/EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_expectancy`, `old_null_trades`, `campaign_012`, `campaign_014`
Match count: 22

- L19 `campaign_011`: ## A. CAMPAIGN_011 replaces CAMPAIGN_005 as the binding null baseline
- L25 `campaign_011`: Effective this sprint, the binding null baseline is **CAMPAIGN_011
- L26 `random_entry_anchor`: random_entry_anchor**, per its
- L27 `campaign_011`: [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md). The original §3 table
- L35 `campaign_011`: § "Null per pair (CAMPAIGN_011 mean expectancy R across 8 folds)".
- … 17 more matches

### `docs/research/EDGE_DISCOVERY_LAB_001_PLAN.md`

Patterns: `campaign_011`
Match count: 1

- L207 `campaign_011`:   CAMPAIGN_005 ("Benchmarks & Diagnostics"), not CAMPAIGN_011. The

### `docs/research/EDGE_DISCOVERY_LAB_001_RESULTS.md`

Patterns: `campaign_014`, `campaign_012`
Match count: 4

- L33 `campaign_014`: | `study_event_window.py` | committed synthetic NFP/FOMC/CPI fixture + H4 candle fixture | `studies/outputs/study_event_window.{json,md}` | event-class breakdown, dominance share, zero-trade-class flag, null comparison — the CAMPAIGN_014 na
- L34 `campaign_012`: | `study_turnover_cost.py` | analytical sweep (no candle input) | `studies/outputs/study_turnover_cost.{json,md}` | post-cost matrix over (pre-cost edge × trade count); cost-share-of-mean — the CAMPAIGN_012/013 narrative pattern |
- L58 `campaign_014`:   session/data filter blocks a class, e.g. the CAMPAIGN_014 FOMC
- L185 `campaign_014`:    CAMPAIGN_014 narrative.** No new pre-commit until the lab output

### `docs/research/EDGE_DISCOVERY_LAB_001_SUMMARY.md`

Patterns: `campaign_012`, `campaign_014`, `campaign_011`
Match count: 5

- L98 `campaign_012`:   CAMPAIGN_012 / 013 narrative).
- L108 `campaign_014`:   zero-trade-class slices — the brief's CAMPAIGN_014 NFP/FOMC
- L143 `campaign_014`:    — direct test of the brief's CAMPAIGN_014 narrative; cheapest to run
- L188 `campaign_014`: - **CAMPAIGN_010 – CAMPAIGN_014 referenced in the sprint brief are
- L191 `campaign_011`:   CAMPAIGN_011. The meta-analysis treats the brief's 010–014

### `docs/research/EDGE_DISCOVERY_LAB_HYDRATE_001_PLAN.md`

Patterns: `campaign_014`
Match count: 8

- L26 `campaign_014`: 3. The brief's CAMPAIGN_014 "event-window continuation vs reversal"
- L28 `campaign_014`:    the real CAMPAIGN_014 fold results.
- L40 `campaign_014`:   committed CAMPAIGN_014 event fixture
- L41 `campaign_014`:   (`research/calendar/fixtures/campaign_014_events.json`), the
- L101 `campaign_014`: - `docs/research/CAMPAIGN_010_*.md` through `CAMPAIGN_014_*.md` —
- … 3 more matches

### `docs/research/EDGE_DISCOVERY_LAB_HYDRATE_001_RESULTS_ADDENDUM.md`

Patterns: `campaign_014`, `campaign_011`, `old_null_expectancy`, `random_entry_anchor`, `old_null_trades`, `campaign_012`, `campaign_013`
Match count: 45

- L20 `campaign_014`: / per-fold trade CSVs, the committed CAMPAIGN_014 event fixture, and
- L30 `campaign_014`: ### 2.1 Event-window study — real CAMPAIGN_014 trades + real fixture
- L36 `campaign_014`: | n trades | 720 | every trade from the committed CAMPAIGN_014 per-fold per-pair CSVs |
- L37 `campaign_014`: | overall mean R | **−0.1477** | identical to the published CAMPAIGN_014 aggregate (cross-check passes) |
- L38 `campaign_011`: | CAMPAIGN_011 null mean R | −0.0024 | binding null floor per [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) |
- … 40 more matches

### `docs/research/EDGE_DISCOVERY_LAB_HYDRATE_001_SUMMARY.md`

Patterns: `campaign_011`, `campaign_014`, `campaign_012`
Match count: 22

- L41 `campaign_011`: | 4 | `98bda08` | results + ranking rules addenda; CAMPAIGN_011 replaces CAMPAIGN_005 as the binding null baseline |
- L55 `campaign_011`:   bind to CAMPAIGN_011.
- L65 `campaign_014`:   per-fold per-pair trade-CSV loader, CAMPAIGN_014 event-fixture
- L71 `campaign_011`: - [`study_real_event_window.py`](../../research/edge_discovery/studies/study_real_event_window.py) — CAMPAIGN_014 trades × fixture × CAMPAIGN_011 null.
- L71 `campaign_014`: - [`study_real_event_window.py`](../../research/edge_discovery/studies/study_real_event_window.py) — CAMPAIGN_014 trades × fixture × CAMPAIGN_011 null.
- … 17 more matches

### `docs/research/EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_expectancy`, `old_null_trades`, `old_null_json_path`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 23

- L39 `campaign_011`: | CAMPAIGN_011 random_entry_anchor (**null model**) | [`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json) | REJECT | false | 8 | 1,177 | **−0.0
- L39 `random_entry_anchor`: | CAMPAIGN_011 random_entry_anchor (**null model**) | [`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json) | REJECT | false | 8 | 1,177 | **−0.0
- L39 `old_null_expectancy`: | CAMPAIGN_011 random_entry_anchor (**null model**) | [`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json) | REJECT | false | 8 | 1,177 | **−0.0
- L39 `old_null_trades`: | CAMPAIGN_011 random_entry_anchor (**null model**) | [`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json) | REJECT | false | 8 | 1,177 | **−0.0
- L39 `old_null_json_path`: | CAMPAIGN_011 random_entry_anchor (**null model**) | [`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json) | REJECT | false | 8 | 1,177 | **−0.0
- … 18 more matches

### `docs/research/EDGE_DISCOVERY_SINGLE_PAIR_PROBE_ADDENDUM.md`

Patterns: `campaign_012`, `campaign_011`, `old_null_expectancy`, `campaign_014`
Match count: 13

- L22 `campaign_012`: above-floor cell (EUR_USD / CAMPAIGN_012, +0.0950 R) across a 7-pair
- L87 `campaign_012`: The probe surfaced a striking pattern: the EUR_USD / CAMPAIGN_012
- L118 `campaign_012`: ## C. Does CAMPAIGN_012 remain rejected?
- L121 `campaign_012`: [`CAMPAIGN_012_STATUS.md`](CAMPAIGN_012_STATUS.md) and the probe's
- L125 `campaign_011`: - Aggregate expectancy R is −0.0521 (vs +0.05 gate, vs CAMPAIGN_011
- … 8 more matches

### `docs/research/EVIDENCE_INDEX.md`

Patterns: `campaign_012`, `campaign_011`, `random_entry_anchor`, `canonical_null_json`, `campaign_013`, `campaign_014`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `old_null_trades`, `above_null_claim`
Match count: 225

- L23 `campaign_012`: | [`POST_DEDUP_NULL_REFERENCE_REFRESH_001_SUMMARY.md`](POST_DEDUP_NULL_REFERENCE_REFRESH_001_SUMMARY.md) | CAMPAIGN_012–014 null-reference refresh close-out |
- L45 `campaign_011`: | 011 | [`docs/research/CAMPAIGN_011_DEDUPED_NULL_BASELINE.md`](CAMPAIGN_011_DEDUPED_NULL_BASELINE.md) | **REJECT** (null anchor) | random_entry_anchor deduped canonical: exp_r −0.0029, 1180 trades · [`campaign_011_deduped_null_baseline.jso
- L45 `random_entry_anchor`: | 011 | [`docs/research/CAMPAIGN_011_DEDUPED_NULL_BASELINE.md`](CAMPAIGN_011_DEDUPED_NULL_BASELINE.md) | **REJECT** (null anchor) | random_entry_anchor deduped canonical: exp_r −0.0029, 1180 trades · [`campaign_011_deduped_null_baseline.jso
- L45 `canonical_null_json`: | 011 | [`docs/research/CAMPAIGN_011_DEDUPED_NULL_BASELINE.md`](CAMPAIGN_011_DEDUPED_NULL_BASELINE.md) | **REJECT** (null anchor) | random_entry_anchor deduped canonical: exp_r −0.0029, 1180 trades · [`campaign_011_deduped_null_baseline.jso
- L46 `campaign_012`: | 012 | [`docs/research/CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md) | **REJECT** | regime_switcher: exp_r −0.0521 · **LIKELY_CONTAMINATED** metrics; null gap refreshed vs deduped null (−0.0029 R) —
- … 220 more matches

### `docs/research/EVIDENCE_MANIFEST.json`

Patterns: `campaign_011`, `random_entry_anchor`, `campaign_012`, `campaign_013`, `campaign_014`, `canonical_null_json`, `old_null_json_path`, `old_null_expectancy`, `old_null_trades`, `superseded_null_reference`
Match count: 105

- L3 `campaign_011`:   "description": "Machine-readable index of all research evidence: fifteen campaigns (CAMPAIGN_001-009 plus CAMPAIGN_010 session_breakout, CAMPAIGN_011 random_entry_anchor null-model, CAMPAIGN_012 regime_switcher_atr_percentile, CAMPAIGN_01
- L3 `random_entry_anchor`:   "description": "Machine-readable index of all research evidence: fifteen campaigns (CAMPAIGN_001-009 plus CAMPAIGN_010 session_breakout, CAMPAIGN_011 random_entry_anchor null-model, CAMPAIGN_012 regime_switcher_atr_percentile, CAMPAIGN_01
- L3 `campaign_012`:   "description": "Machine-readable index of all research evidence: fifteen campaigns (CAMPAIGN_001-009 plus CAMPAIGN_010 session_breakout, CAMPAIGN_011 random_entry_anchor null-model, CAMPAIGN_012 regime_switcher_atr_percentile, CAMPAIGN_01
- L3 `campaign_013`:   "description": "Machine-readable index of all research evidence: fifteen campaigns (CAMPAIGN_001-009 plus CAMPAIGN_010 session_breakout, CAMPAIGN_011 random_entry_anchor null-model, CAMPAIGN_012 regime_switcher_atr_percentile, CAMPAIGN_01
- L3 `campaign_014`:   "description": "Machine-readable index of all research evidence: fifteen campaigns (CAMPAIGN_001-009 plus CAMPAIGN_010 session_breakout, CAMPAIGN_011 random_entry_anchor null-model, CAMPAIGN_012 regime_switcher_atr_percentile, CAMPAIGN_01
- … 100 more matches

### `docs/research/EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_PLAN.md`

Patterns: `campaign_012`, `campaign_014`, `campaign_011`, `random_entry_anchor`, `campaign_013`
Match count: 20

- L23 `campaign_012`: the **exit / payoff shape** that surfaced in the EUR_USD / CAMPAIGN_012
- L25 `campaign_014`: CAMPAIGN_010 - CAMPAIGN_014, or whether it was incidental to one
- L36 `campaign_012`: classified the EUR_USD / CAMPAIGN_012 +0.0950 R cell as
- L64 `campaign_014`: > **Q1.** Across CAMPAIGN_010 - CAMPAIGN_014, do `stop` exits
- L71 `campaign_011`: > null** CAMPAIGN_011 as well? In other words, is the asymmetry a
- … 15 more matches

### `docs/research/EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_RESULT.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_trades`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 23

- L29 `campaign_011`: | CAMPAIGN_011_random_entry_anchor | 1,177 | 0.205 | −0.8312 | +0.2093 | 0.705 |
- L29 `random_entry_anchor`: | CAMPAIGN_011_random_entry_anchor | 1,177 | 0.205 | −0.8312 | +0.2093 | 0.705 |
- L29 `old_null_trades`: | CAMPAIGN_011_random_entry_anchor | 1,177 | 0.205 | −0.8312 | +0.2093 | 0.705 |
- L30 `campaign_012`: | CAMPAIGN_012_regime_switcher_atr_percentile | 3,726 | 0.204 | −0.8178 | +0.1450 | 0.679 |
- L31 `campaign_013`: | CAMPAIGN_013_cross_pair_currency_strength_rotation | 7,940 | 0.231 | −0.9483 | +0.2105 | 0.856 |
- … 18 more matches

### `docs/research/EXIT_ASYMMETRY_CROSS_CAMPAIGN_001_SUMMARY.md`

Patterns: `campaign_012`, `campaign_014`, `campaign_011`, `random_entry_anchor`, `old_null_trades`, `campaign_013`
Match count: 22

- L15 `campaign_012`: surfaced inside the EUR_USD / CAMPAIGN_012 falsification probe is
- L17 `campaign_014`: CAMPAIGN_014, or whether it was incidental to one cell.
- L20 `campaign_011`: including the random-entry null CAMPAIGN_011, exhibits the same
- L87 `campaign_011`: | CAMPAIGN_011_random_entry_anchor (null) | 56 | 1,177 |
- L87 `random_entry_anchor`: | CAMPAIGN_011_random_entry_anchor (null) | 56 | 1,177 |
- … 17 more matches

### `docs/research/FAILED_CAMPAIGN_META_ANALYSIS_001.md`

Patterns: `campaign_011`, `campaign_014`
Match count: 3

- L13 `campaign_011`: > canonical evidence is **DEDUP-SAFE** (deduped rerun). CAMPAIGN_011
- L39 `campaign_014`: for `CAMPAIGN_010`–`CAMPAIGN_014` were not located in
- L56 `campaign_011`:   trigger bar; CAMPAIGN_011 = null baseline). These are recorded as

### `docs/research/FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_FIXES.md`

Patterns: `old_null_expectancy`
Match count: 1

- L69 `old_null_expectancy`: | USD_JPY | 251 → 251 (0) | −0.0126 → −0.0126 (0) | −1.0642 → −1.0666 (−0.0024) |

### `docs/research/INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`, `random_entry_anchor`
Match count: 9

- L24 `campaign_011`:    CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain REJECT / null /
- L24 `campaign_012`:    CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain REJECT / null /
- L24 `campaign_013`:    CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain REJECT / null /
- L25 `campaign_014`:    research-only exactly as currently documented. CAMPAIGN_014 remains
- L213 `campaign_011`: | CAMPAIGN_011 (random_entry_anchor — null model) | deterministic by seed; minimal strategy logic (coin flip + ATR stop + max-bars); makes data-loop / fill-model / sizing isolatable from indicator / rule complexity; lowest implementation co
- … 4 more matches

### `docs/research/INFRA_BACKTRADER_SECONDARY_LANE_001_SUMMARY.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`, `random_entry_anchor`
Match count: 20

- L18 `campaign_011`: > **No strategy approved. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011,
- L19 `campaign_012`: > CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
- L19 `campaign_013`: > CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
- L20 `campaign_014`: > CAMPAIGN_014 remains scaffold-only. `configs/approved_strategies.yaml`
- L154 `campaign_011`: **BLOCKED, deferred (Phase 7).** Implementing a CAMPAIGN_011 port in
- … 15 more matches

### `docs/research/INFRA_BACKTRADER_SECONDARY_LANE_002_SUMMARY.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 14

- L20 `campaign_011`: > **No strategy approved. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011,
- L21 `campaign_012`: > CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
- L21 `campaign_013`: > CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
- L22 `campaign_014`: > CAMPAIGN_014 remains scaffold-only. `configs/approved_strategies.yaml`
- L37 `campaign_011`: | 5 | `271dcd9` | CAMPAIGN_011 BLOCKED (cascade); carry-forward implementation prompt |
- … 9 more matches

### `docs/research/INFRA_BACKTRADER_SECONDARY_LANE_003_SUMMARY.md`

Patterns: `campaign_011`, `random_entry_anchor`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 20

- L42 `campaign_011`: | 5 | `e71ac4d` | CAMPAIGN_011 BLOCKED-by-design (structural prereqs) |
- L128 `campaign_011`: ## 9. CAMPAIGN_011 status
- L132 `campaign_011`: that would make a CAMPAIGN_011 comparison apples-to-oranges:
- L134 `campaign_011`: 1. No published no-RiskEngine bespoke reference for CAMPAIGN_011
- L137 `campaign_011`: 2. CAMPAIGN_011's bespoke artefacts are per-fold walk-forward (8
- … 15 more matches

### `docs/research/INFRA_BACKTRADER_SECONDARY_LANE_004_CAMPAIGN_011_SUMMARY.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 82

- L8 `campaign_011`: > Ports CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011` into the
- L8 `random_entry_anchor`: > Ports CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011` into the
- L13 `campaign_011`: > CAMPAIGN_011 remains REJECT / null diagnostic anchor by design.
- L21 `campaign_011`: | BT-lane adapter | `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py` | implements R1-R8 byte-for-byte against the bespoke strategy; deterministic SHA-256 seed; reuses CAMPAIGN_002 helpers |
- L21 `random_entry_anchor`: | BT-lane adapter | `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py` | implements R1-R8 byte-for-byte against the bespoke strategy; deterministic SHA-256 seed; reuses CAMPAIGN_002 helpers |
- … 77 more matches

### `docs/research/INFRA_BESPOKE_CAMPAIGN_011_NORISK_REFERENCE_001_SUMMARY.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 68

- L9 `campaign_011`: > CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011` so the future
- L9 `random_entry_anchor`: > CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011` so the future
- L10 `campaign_011`: > Backtrader CAMPAIGN_011 sprint has a clean apples-to-apples
- L11 `campaign_011`: > comparison target. **No strategy was approved.** CAMPAIGN_011
- L20 `campaign_011`: | Canonical full-window reference JSON | `research/lean_parity/campaign_011_h4_bespoke_reference.json` | 2.4 KB | the Backtrader-vs-bespoke comparison target |
- … 63 more matches

### `docs/research/NEW_CANDIDATE_DISCOVERY_002_HELPER_DECISION.md`

Patterns: `campaign_011`
Match count: 4

- L84 `campaign_011`: > like CAMPAIGN_010 / CAMPAIGN_011).
- L96 `campaign_011`: ### Option E — A research-archive entry for CAMPAIGN_011 as a placeholder
- L102 `campaign_011`: `artifact_folder` to exist; CAMPAIGN_011 has neither (no
- L106 `campaign_011`: **Decision: reject.** CAMPAIGN_011 entries must wait for the

### `docs/research/NEW_CANDIDATE_DISCOVERY_003_HELPER_DECISION.md`

Patterns: `campaign_011`, `campaign_013`, `campaign_012`
Match count: 13

- L11 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
- L31 `campaign_011`: | Concrete, actionable for the future scaffold + evidence sprints | The comparison logic is already codified in [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) §3 + §8 + §9 — a separate checkli
- L32 `campaign_013`: | Reusable across future candidates (CAMPAIGN_013+, etc.) | The protocol's §13 documentation discipline is the same enforcement, but in markdown form |
- L58 `campaign_013`: **Decision: reject.** If a future candidate (CAMPAIGN_013+)
- L88 `campaign_012`: | Could be unit-tested | The CAMPAIGN_012 evidence sprint can be the first to demonstrate the section; codifying the requirement in the *evidence-branch spec* (Phase 6b §4 Phase 4) is enforcement enough |
- … 8 more matches

### `docs/research/NEW_CANDIDATE_DISCOVERY_004_HELPER_DECISION.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`
Match count: 12

- L37 `campaign_011`: | would be reusable across future evidence sprints | already codified in [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) §3 + §8 + §9; CAMPAIGN_012's `WALK_FORWARD_RESULT.md` §3 demonstrates th
- L37 `campaign_012`: | would be reusable across future evidence sprints | already codified in [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) §3 + §8 + §9; CAMPAIGN_012's `WALK_FORWARD_RESULT.md` §3 demonstrates th
- L37 `campaign_013`: | would be reusable across future evidence sprints | already codified in [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) §3 + §8 + §9; CAMPAIGN_012's `WALK_FORWARD_RESULT.md` §3 demonstrates th
- L61 `campaign_011`: | would catch drift if a future verdict doc forgot the section | the convention is binding via the CAMPAIGN_011 interpretation doc + each candidate's `*_PRECOMMIT_CHECKLIST.md` §8; CAMPAIGN_012's `WALK_FORWARD_RESULT.md` already includes th
- L61 `campaign_012`: | would catch drift if a future verdict doc forgot the section | the convention is binding via the CAMPAIGN_011 interpretation doc + each candidate's `*_PRECOMMIT_CHECKLIST.md` §8; CAMPAIGN_012's `WALK_FORWARD_RESULT.md` already includes th
- … 7 more matches

### `docs/research/NEW_CANDIDATE_DISCOVERY_005_HELPER_DECISION.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 12

- L39 `campaign_011`: | would be reusable across future evidence sprints | already codified in [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) §3 + §8 + §9; CAMPAIGN_012's and CAMPAIGN_013's `WALK_FORWARD_RESULT.md`
- L39 `campaign_012`: | would be reusable across future evidence sprints | already codified in [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) §3 + §8 + §9; CAMPAIGN_012's and CAMPAIGN_013's `WALK_FORWARD_RESULT.md`
- L39 `campaign_013`: | would be reusable across future evidence sprints | already codified in [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) §3 + §8 + §9; CAMPAIGN_012's and CAMPAIGN_013's `WALK_FORWARD_RESULT.md`
- L39 `campaign_014`: | would be reusable across future evidence sprints | already codified in [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) §3 + §8 + §9; CAMPAIGN_012's and CAMPAIGN_013's `WALK_FORWARD_RESULT.md`
- L72 `campaign_014`: | would catch drift if a future verdict doc forgot the turnover-budget section | the convention is binding via the Phase 2 anti-pattern doc + each candidate's `*_PRECOMMIT_CHECKLIST.md` (per the Phase 7 design §18). CAMPAIGN_014's evidence-
- … 7 more matches

### `docs/research/NEW_CANDIDATE_STRATEGY_DISCOVERY_002_PLAN.md`

Patterns: `campaign_011`
Match count: 1

- L144 `campaign_011`:    and proposed `CAMPAIGN_011` label.

### `docs/research/NEW_CANDIDATE_STRATEGY_DISCOVERY_002_SUMMARY.md`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 15

- L16 `campaign_011`: > entry diagnostic anchor, future CAMPAIGN_011) is a null model
- L51 `campaign_011`: | candidate selection | **C5 — random entry diagnostic anchor** chosen for future CAMPAIGN_011 |
- L93 `campaign_011`: | C3 (regime switcher) | 5/6 | D1 ATR aggregation; parameter-overlap soft warning | **medium-high** | **deferred (second priority after CAMPAIGN_011)** |
- L98 `campaign_011`: after CAMPAIGN_011: C5 → C3 → C2 → C4.
- L111 `random_entry_anchor`: | proposed strategy id | `random_entry_anchor` |
- … 10 more matches

### `docs/research/NEW_CANDIDATE_STRATEGY_DISCOVERY_003_PLAN.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_trades`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `above_null_claim`, `campaign_012`
Match count: 46

- L7 `campaign_011`: sprint, opened after CAMPAIGN_011 / `random_entry_anchor
- L7 `random_entry_anchor`: sprint, opened after CAMPAIGN_011 / `random_entry_anchor
- L14 `campaign_011`: > remains REJECT. CAMPAIGN_011 remains REJECT (null-model anchor;
- L25 `campaign_011`: | base commit | `66254f4` — Phase 9 of `research-random-entry-diagnostic-anchor-walk-forward-001` (CAMPAIGN_011 REJECT, status registries updated) |
- L31 `campaign_011`: | CAMPAIGN_011 status | **REJECT (null-model anchor)** (unchanged; cannot be approved by design) |
- … 41 more matches

### `docs/research/NEW_CANDIDATE_STRATEGY_DISCOVERY_003_SUMMARY.md`

Patterns: `campaign_011`, `campaign_012`, `old_null_expectancy`, `old_null_pf`, `old_null_return`
Match count: 41

- L7 `campaign_011`: discovery sprint, opened after CAMPAIGN_011 (the C5 null-model
- L14 `campaign_011`: > remains REJECT. CAMPAIGN_011 remains REJECT (null-model
- L17 `campaign_012`: > ATR-percentile regime switcher, future CAMPAIGN_012) is NOT
- L31 `campaign_011`: | 1 | `7f44faf` | [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) | 242 |
- L54 `campaign_011`: | CAMPAIGN_011 | REJECT (null-model anchor; untouched) |
- … 36 more matches

### `docs/research/NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md`

Patterns: `campaign_012`, `campaign_011`, `random_entry_anchor`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `old_null_trades`
Match count: 49

- L8 `campaign_012`: candidate discovery after CAMPAIGN_012's REJECT. **Discovery/design
- L12 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
- L13 `campaign_012`: > CAMPAIGN_012 all remain REJECT. `configs/approved_strategies.yaml`
- L15 `campaign_011`: > CAMPAIGN_011 is the **null baseline only**, not a trading candidate.
- L23 `campaign_012`: | base commit (HEAD before Phase 0) | `6b27c30` — Phase 9 of `research-regime-switcher-atr-percentile-walk-forward-001` (CAMPAIGN_012 evidence-sprint close) |
- … 44 more matches

### `docs/research/NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md`

Patterns: `campaign_012`, `campaign_013`, `campaign_011`, `random_entry_anchor`
Match count: 24

- L7 `campaign_012`: candidate selection after CAMPAIGN_012's REJECT; selected **C6 —
- L9 `campaign_013`: (`cross_pair_currency_strength_rotation 0.1.0-c013`, CAMPAIGN_013).
- L15 `campaign_011`: > Paper / demo / live remain blocked. CAMPAIGN_011 is the null
- L36 `campaign_012`: | Phase 1 | `769a96e` | CAMPAIGN_012 rejection closeout |
- L60 `campaign_012`: ## 4. CAMPAIGN_012 rejection closeout (Phase 1)
- … 19 more matches

### `docs/research/NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`, `random_entry_anchor`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `old_null_trades`
Match count: 76

- L8 `campaign_013`: candidate discovery after CAMPAIGN_013's REJECT. **Discovery/design
- L13 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
- L14 `campaign_012`: > CAMPAIGN_012 / CAMPAIGN_013 all remain REJECT.
- L14 `campaign_013`: > CAMPAIGN_012 / CAMPAIGN_013 all remain REJECT.
- L16 `campaign_011`: > demo / live remain blocked. CAMPAIGN_011 is the **null baseline
- … 71 more matches

### `docs/research/NEW_CANDIDATE_STRATEGY_DISCOVERY_005_SUMMARY.md`

Patterns: `campaign_013`, `campaign_014`, `campaign_011`, `old_null_expectancy`, `old_null_trades`, `old_null_return`, `campaign_012`, `random_entry_anchor`
Match count: 37

- L7 `campaign_013`: candidate selection after CAMPAIGN_013's REJECT; codified the
- L11 `campaign_014`: CAMPAIGN_014). **Design / discovery sprint only — no strategy
- L16 `campaign_011`: > Paper / demo / live remain blocked. CAMPAIGN_011 is the null
- L37 `campaign_013`: | Phase 1 | `c3376ff` | CAMPAIGN_013 rejection closeout |
- L62 `campaign_013`: ## 4. CAMPAIGN_013 rejection closeout (Phase 1)
- … 32 more matches

### `docs/research/NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 86

- L7 `campaign_011`: sprint** that will run CAMPAIGN_011 / `random_entry_anchor
- L7 `random_entry_anchor`: sprint** that will run CAMPAIGN_011 / `random_entry_anchor
- L17 `campaign_011`: > `approved: []`. **CAMPAIGN_011 is a diagnostic anchor / null
- L29 `campaign_011`: | campaign label | `CAMPAIGN_011` |
- L30 `random_entry_anchor`: | strategy id | `random_entry_anchor` |
- … 81 more matches

### `docs/research/NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`, `above_null_claim`
Match count: 26

- L9 `campaign_013`: (CAMPAIGN_013). This doc is a binding *prompt template* for the
- L24 `campaign_011`: | sibling reference | `research-random-entry-diagnostic-anchor-walk-forward-001` (CAMPAIGN_011 evidence) + `research-regime-switcher-atr-percentile-walk-forward-001` (CAMPAIGN_012 evidence) |
- L24 `campaign_012`: | sibling reference | `research-random-entry-diagnostic-anchor-walk-forward-001` (CAMPAIGN_011 evidence) + `research-regime-switcher-atr-percentile-walk-forward-001` (CAMPAIGN_012 evidence) |
- L27 `campaign_012`: ## 2. Phase outline (10 phases; mirrors CAMPAIGN_012 evidence sprint)
- L32 `campaign_013`: | 1 | `docs/research/CAMPAIGN_013_DATA_PROVENANCE.md` | data hashes (must match CAMPAIGN_010 / 011 / 012 verbatim) |
- … 21 more matches

### `docs/research/NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`

Patterns: `campaign_014`, `campaign_012`, `campaign_013`, `campaign_011`, `above_null_claim`
Match count: 45

- L8 `campaign_014`: `calendar_event_window_anomaly 0.1.0-c014` (CAMPAIGN_014). This doc
- L26 `campaign_012`: | sibling reference | `research-cross-pair-currency-strength-rotation-walk-forward-001` (CAMPAIGN_013 evidence) + `research-regime-switcher-atr-percentile-walk-forward-001` (CAMPAIGN_012 evidence) |
- L26 `campaign_013`: | sibling reference | `research-cross-pair-currency-strength-rotation-walk-forward-001` (CAMPAIGN_013 evidence) + `research-regime-switcher-atr-percentile-walk-forward-001` (CAMPAIGN_012 evidence) |
- L27 `campaign_014`: | binding pre-commit | `docs/research/CAMPAIGN_014_PRECOMMIT_CHECKLIST.md` (from scaffold sprint Phase 4) — **immutable** for this sprint |
- L29 `campaign_013`: ## 2. Phase outline (10 phases; mirrors CAMPAIGN_013 evidence sprint)
- … 40 more matches

### `docs/research/NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 40

- L7 `campaign_011`: sprint** that will implement CAMPAIGN_011 / `random_entry_anchor
- L7 `random_entry_anchor`: sprint** that will implement CAMPAIGN_011 / `random_entry_anchor
- L16 `campaign_011`: > `approved: []`. **CAMPAIGN_011 is a diagnostic anchor / null
- L26 `campaign_011`: | campaign label | `CAMPAIGN_011` |
- L27 `random_entry_anchor`: | strategy id | `random_entry_anchor` |
- … 35 more matches

### `docs/research/NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`
Match count: 18

- L8 `campaign_013`: (CAMPAIGN_013). This doc is a binding *prompt template* for the next
- L24 `campaign_011`: | sibling reference | `research-random-entry-diagnostic-anchor-001` (CAMPAIGN_011 scaffold) + `research-regime-switcher-atr-percentile-001` (CAMPAIGN_012 scaffold) |
- L24 `campaign_012`: | sibling reference | `research-random-entry-diagnostic-anchor-001` (CAMPAIGN_011 scaffold) + `research-regime-switcher-atr-percentile-001` (CAMPAIGN_012 scaffold) |
- L26 `campaign_012`: ## 2. Phase outline (8 phases; mirrors CAMPAIGN_012 scaffold sprint)
- L34 `campaign_013`: | 4 | `configs/campaign_013_cross_pair_currency_strength_rotation.yaml` + `docs/research/CAMPAIGN_013_PRECOMMIT_CHECKLIST.md` + `docs/research/CAMPAIGN_013_STATUS.md` + `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_READINESS.md` | ca
- … 13 more matches

### `docs/research/NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md`

Patterns: `campaign_014`, `campaign_012`, `campaign_013`, `campaign_011`
Match count: 22

- L8 `campaign_014`: (CAMPAIGN_014). This doc is a binding *prompt template* for the next
- L24 `campaign_012`: | sibling reference | `research-cross-pair-currency-strength-rotation-001` (CAMPAIGN_013 scaffold) + `research-regime-switcher-atr-percentile-001` (CAMPAIGN_012 scaffold) |
- L24 `campaign_013`: | sibling reference | `research-cross-pair-currency-strength-rotation-001` (CAMPAIGN_013 scaffold) + `research-regime-switcher-atr-percentile-001` (CAMPAIGN_012 scaffold) |
- L26 `campaign_013`: ## 2. Phase outline (9 phases; mirrors CAMPAIGN_013 scaffold sprint + adds Phase 1b for event-fixture compilation)
- L35 `campaign_014`: | 4 | `configs/campaign_014_calendar_event_window_anomaly.yaml` + `docs/research/CAMPAIGN_014_PRECOMMIT_CHECKLIST.md` + `docs/research/CAMPAIGN_014_STATUS.md` + `docs/research/CALENDAR_EVENT_WINDOW_ANOMALY_READINESS.md` | candidate config Y
- … 17 more matches

### `docs/research/NEXT_DIRECTION_REASSESSMENT_004.md`

Patterns: `campaign_011`, `campaign_012`
Match count: 9

- L8 `campaign_011`: **now-7 rejected baseline** (5 prior + CAMPAIGN_011 null +
- L9 `campaign_012`: CAMPAIGN_012 real) and recommends a single next path. **No
- L14 `campaign_011`: > CAMPAIGN_011 is the null baseline only, not a trading candidate.
- L38 `campaign_011`: | distinctness from CAMPAIGN_011 (null) | not a re-parameterized random-entry? |
- L39 `campaign_012`: | distinctness from CAMPAIGN_012 | structurally different signal family? |
- … 4 more matches

### `docs/research/NEXT_DIRECTION_REASSESSMENT_005.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `old_null_trades`
Match count: 36

- L9 `campaign_011`: + CAMPAIGN_011 null + CAMPAIGN_012 real + CAMPAIGN_013 real) and the
- L9 `campaign_012`: + CAMPAIGN_011 null + CAMPAIGN_012 real + CAMPAIGN_013 real) and the
- L9 `campaign_013`: + CAMPAIGN_011 null + CAMPAIGN_012 real + CAMPAIGN_013 real) and the
- L16 `campaign_011`: > `approved: []`. CAMPAIGN_011 is the null baseline only, not a
- L25 `campaign_013`: | **C6** | Cross-pair currency strength rotation | candidate | **REJECTED in CAMPAIGN_013** — out of scope; cooldown binding (Phase 1) |
- … 31 more matches

### `docs/research/NEXT_PREFERRED_CANDIDATE_002.md`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 21

- L23 `campaign_011`: under campaign label **`CAMPAIGN_011`** with strategy
- L24 `random_entry_anchor`: **`random_entry_anchor 0.1.0-c011`**.
- L30 `random_entry_anchor`: | proposed strategy id | `random_entry_anchor` |
- L32 `campaign_011`: | proposed campaign label | `CAMPAIGN_011` |
- L66 `random_entry_anchor`: | dimension | CAMPAIGN_002 (`trend_following 0.1.0`) | **C5 (`random_entry_anchor 0.1.0-c011`)** | distinct? |
- … 16 more matches

### `docs/research/NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`

Patterns: `random_entry_anchor`, `campaign_011`, `old_null_json_path`
Match count: 62

- L7 `random_entry_anchor`: selected next preferred candidate, **C5 — `random_entry_anchor
- L8 `campaign_011`: 0.1.0-c011` (CAMPAIGN_011)** — per the Phase 3 selection in
- L15 `campaign_011`: > `approved: []`. **CAMPAIGN_011 is a diagnostic anchor / null
- L122 `random_entry_anchor`: - `signal_id` = `sha256("|".join(["random_entry_anchor", "0.1.0-c011", ctx.instrument.name, timeframe, bar_timestamp_iso, direction]))[:24]`
- L123 `random_entry_anchor`: - `strategy_name = "random_entry_anchor"`
- … 57 more matches

### `docs/research/NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`

Patterns: `campaign_013`, `campaign_011`, `campaign_012`, `random_entry_anchor`, `old_null_expectancy`, `old_null_pf`, `old_null_return`
Match count: 43

- L7 `campaign_013`: `cross_pair_currency_strength_rotation 0.1.0-c013` (CAMPAIGN_013)**
- L13 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
- L14 `campaign_012`: > CAMPAIGN_012 remain REJECT. `configs/approved_strategies.yaml`
- L15 `campaign_013`: > remains `approved: []`. **CAMPAIGN_013 cannot be approved by this
- L35 `campaign_011`: > threshold large enough to overcome H4 cost drag*. CAMPAIGN_011
- … 38 more matches

### `docs/research/NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md`

Patterns: `campaign_011`, `old_null_trades`, `campaign_012`, `campaign_013`, `campaign_014`, `random_entry_anchor`, `above_null_claim`
Match count: 18

- L186 `campaign_011`: | **comparison to CAMPAIGN_011 null** | well below 1,177 (the null floor); ~3.5–7 × less than CAMPAIGN_011 |
- L186 `old_null_trades`: | **comparison to CAMPAIGN_011 null** | well below 1,177 (the null floor); ~3.5–7 × less than CAMPAIGN_011 |
- L187 `campaign_012`: | **comparison to CAMPAIGN_012** | ~7–12 × less than CAMPAIGN_012 (3,726) |
- L188 `campaign_013`: | **comparison to CAMPAIGN_013** | ~15–25 × less than CAMPAIGN_013 (7,940) |
- L257 `campaign_014`:     """Frozen config for the C7 candidate (CAMPAIGN_014)."""
- … 13 more matches

### `docs/research/NEXT_PREFERRED_DIRECTION_004.md`

Patterns: `campaign_013`, `campaign_011`, `random_entry_anchor`, `campaign_012`
Match count: 19

- L25 `campaign_013`: | **proposed campaign label** | **CAMPAIGN_013** |
- L48 `campaign_011`: | CAMPAIGN_011 (`random_entry_anchor`, null) | NO | C6 is fully deterministic from price — no PRNG, no `master_seed`, no Bernoulli draw. |
- L48 `random_entry_anchor`: | CAMPAIGN_011 (`random_entry_anchor`, null) | NO | C6 is fully deterministic from price — no PRNG, no `master_seed`, no Bernoulli draw. |
- L49 `campaign_012`: | CAMPAIGN_012 (`regime_switcher_atr_percentile`) | NO | C6 has **no single-pair vol-percentile gate**. The signal is structural cross-pair relative strength, *not* "trade within HIGH-VOL regime". |
- L64 `campaign_012`: | **L** — "pick new family because it fixes a CAMPAIGN_012 per-fold artifact" | NO — C6's hypothesis exists independent of CAMPAIGN_012. | The cross-pair currency-strength concept is documented in FX literature (e.g. "currency strength inde
- … 14 more matches

### `docs/research/NEXT_PREFERRED_DIRECTION_005.md`

Patterns: `campaign_014`, `campaign_011`, `random_entry_anchor`, `campaign_012`, `campaign_013`, `old_null_trades`
Match count: 19

- L26 `campaign_014`: | **proposed campaign label** | **CAMPAIGN_014** |
- L54 `campaign_011`: | CAMPAIGN_011 (`random_entry_anchor`, null) | NO | fully deterministic from calendar fixture + price; no PRNG, no `master_seed`, no Bernoulli draw |
- L54 `random_entry_anchor`: | CAMPAIGN_011 (`random_entry_anchor`, null) | NO | fully deterministic from calendar fixture + price; no PRNG, no `master_seed`, no Bernoulli draw |
- L55 `campaign_012`: | CAMPAIGN_012 (`regime_switcher_atr_percentile`) | NO | no single-pair vol-percentile gate; no close-vs-close trend filter; signal is event-window-conditional |
- L56 `campaign_013`: | CAMPAIGN_013 (`cross_pair_currency_strength_rotation`) | NO | no cross-pair ranking; no cross-sectional FX-rank metric; signal is per-pair event-window-conditional |
- … 14 more matches

### `docs/research/NEXT_PREFERRED_REAL_CANDIDATE_003.md`

Patterns: `campaign_011`, `campaign_012`, `random_entry_anchor`, `above_null_claim`
Match count: 41

- L15 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
- L22 `campaign_012`: under campaign label **`CAMPAIGN_012`** with strategy
- L31 `campaign_012`: | proposed campaign label | `CAMPAIGN_012` |
- L34 `campaign_011`: | timeframe | H4 (matches CAMPAIGN_010 / CAMPAIGN_011) |
- L35 `campaign_011`: | universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD (matches CAMPAIGN_010 / CAMPAIGN_011) |
- … 36 more matches

### `docs/research/NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`

Patterns: `campaign_012`, `campaign_011`, `random_entry_anchor`, `above_null_claim`, `old_null_expectancy`, `old_null_pf`, `old_null_return`
Match count: 62

- L8 `campaign_012`: `regime_switcher_atr_percentile 0.1.0-c012` (CAMPAIGN_012)** —
- L16 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
- L18 `campaign_012`: > `approved: []`. **CAMPAIGN_012 cannot be approved by this
- L30 `campaign_011`: > momentum also lost. CAMPAIGN_011 demonstrated that random
- L39 `campaign_011`: > CAMPAIGN_011's pre-commit so the comparison is on the
- … 57 more matches

### `docs/research/NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`

Patterns: `campaign_012`, `campaign_011`, `above_null_claim`
Match count: 68

- L7 `campaign_012`: sprint** that will run CAMPAIGN_012 /
- L15 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
- L29 `campaign_012`: | campaign label | `CAMPAIGN_012` |
- L33 `campaign_011`: | expected commits | 9 (Phase 0 → Phase 8 — mirrors CAMPAIGN_010 / CAMPAIGN_011 evidence sprints structurally) |
- L43 `campaign_011`: - **The walk-forward plan uses CAMPAIGN_010 / CAMPAIGN_011's
- … 63 more matches

### `docs/research/NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md`

Patterns: `campaign_012`, `campaign_011`, `random_entry_anchor`
Match count: 37

- L7 `campaign_012`: sprint** that will implement CAMPAIGN_012 /
- L15 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
- L17 `campaign_012`: > `approved: []`. **CAMPAIGN_012 cannot be approved by the
- L29 `campaign_012`: | campaign label | `CAMPAIGN_012` |
- L54 `campaign_011`:   CAMPAIGN_011.**
- … 32 more matches

### `docs/research/POST_DEDUP_NULL_REFERENCE_INVENTORY.md`

Patterns: `campaign_011`, `canonical_null_json`, `random_entry_anchor`, `old_null_json_path`, `campaign_012`, `campaign_013`, `campaign_014`, `superseded_null_reference`, `old_null_trades`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `above_null_claim`
Match count: 5543

- L9 `campaign_011`: - Canonical null JSON: `research/null_baselines/campaign_011_deduped_null_baseline.json`
- L9 `canonical_null_json`: - Canonical null JSON: `research/null_baselines/campaign_011_deduped_null_baseline.json`
- L10 `campaign_011`: - Superseded artifact: `backtests/CAMPAIGN_011_random_entry_anchor`
- L10 `random_entry_anchor`: - Superseded artifact: `backtests/CAMPAIGN_011_random_entry_anchor`
- L10 `old_null_json_path`: - Superseded artifact: `backtests/CAMPAIGN_011_random_entry_anchor`
- … 5538 more matches

### `docs/research/POST_DEDUP_NULL_REFERENCE_REFRESH_001_PLAN.md`

Patterns: `campaign_012`, `campaign_011`, `canonical_null_json`, `old_null_trades`, `old_null_expectancy`, `old_null_pf`, `campaign_013`, `campaign_014`, `superseded_null_reference`
Match count: 22

- L10 `campaign_012`: Refresh CAMPAIGN_012–014 null-comparison references so they point to the
- L11 `campaign_011`: canonical deduped CAMPAIGN_011 null baseline, and determine whether their
- L19 `campaign_011`: | Machine rollup | [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json) |
- L19 `canonical_null_json`: | Machine rollup | [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json) |
- L20 `campaign_011`: | Rollup markdown | [`research/null_baselines/campaign_011_deduped_null_baseline.md`](../../research/null_baselines/campaign_011_deduped_null_baseline.md) |
- … 17 more matches

### `docs/research/POST_DEDUP_NULL_REFERENCE_REFRESH_001_SUMMARY.md`

Patterns: `campaign_012`, `campaign_011`, `canonical_null_json`, `old_null_expectancy`, `old_null_trades`, `campaign_013`, `campaign_014`, `superseded_null_reference`
Match count: 29

- L9 `campaign_012`: Refresh CAMPAIGN_012–014 null-comparison references to the canonical deduped
- L10 `campaign_011`: CAMPAIGN_011 null baseline and determine whether conclusions materially change.
- L16 `campaign_011`: | path | `research/null_baselines/campaign_011_deduped_null_baseline.json` |
- L16 `canonical_null_json`: | path | `research/null_baselines/campaign_011_deduped_null_baseline.json` |
- L30 `old_null_expectancy`: | files with old null metrics (−0.0024 / 1,177 / etc.) | 173 |
- … 24 more matches

### `docs/research/POST_DEDUP_RERUN_BACKLOG.md`

Patterns: `campaign_011`, `campaign_012`, `canonical_null_json`, `campaign_013`, `campaign_014`
Match count: 13

- L7 `campaign_011`: > CAMPAIGN_011 deduped null baseline **promoted**. CAMPAIGN_012–014 null-reference
- L7 `campaign_012`: > CAMPAIGN_011 deduped null baseline **promoted**. CAMPAIGN_012–014 null-reference
- L15 `campaign_011`: | 1 | **CAMPAIGN_011** null baseline | Canonical null-model anchor | **DONE** — see `research/null_baselines/campaign_011_deduped_null_baseline.json` |
- L15 `canonical_null_json`: | 1 | **CAMPAIGN_011** null baseline | Canonical null-model anchor | **DONE** — see `research/null_baselines/campaign_011_deduped_null_baseline.json` |
- L21 `campaign_012`: | 2 | **CAMPAIGN_012** | Walk-forward on pre-fix SQLite; null ref refreshed | REJECT holds vs deduped null; deduped rerun for certified metrics |
- … 8 more matches

### `docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 33

- L7 `campaign_011`: will implement **CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011`**
- L7 `random_entry_anchor`: will implement **CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011`**
- L16 `campaign_011`: > **CAMPAIGN_011 is a null model by design and cannot be approved.**
- L23 `campaign_011`: | base commit | `d926341` — Phase 7 of `research-new-candidate-strategy-discovery-002` (CAMPAIGN_011 selected as next candidate, design committed) |
- L98 `random_entry_anchor`: | strategy id | `random_entry_anchor` |
- … 28 more matches

### `docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_SUMMARY.md`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 45

- L6 `campaign_011`: End-of-sprint summary and handoff for the **CAMPAIGN_011
- L7 `random_entry_anchor`: scaffold sprint** (`random_entry_anchor 0.1.0-c011` — the C5
- L14 `campaign_011`: > **CAMPAIGN_011 is a null model by design — cannot be approved
- L29 `random_entry_anchor`: | 3 | `04d7f2d` | [`tests/unit/test_random_entry_anchor.py`](../../tests/unit/test_random_entry_anchor.py) — 36 unit + structural-audit cases | 692 |
- L31 `campaign_011`: | 5 | `ec18636` | [`CAMPAIGN_011_SMOKE_RESULT.md`](CAMPAIGN_011_SMOKE_RESULT.md) | 237 |
- … 40 more matches

### `docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 20

- L7 `campaign_011`: **CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011`**. This is the
- L7 `random_entry_anchor`: **CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011`**. This is the
- L14 `campaign_011`: > `approved: []`. **CAMPAIGN_011 is a null model — cannot be
- L21 `campaign_011`: | campaign label | `CAMPAIGN_011` |
- L22 `random_entry_anchor`: | strategy name | `random_entry_anchor` |
- … 15 more matches

### `docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_READINESS.md`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 23

- L6 `campaign_011`: Phase 4 scaffold-readiness summary for **CAMPAIGN_011** /
- L7 `random_entry_anchor`: `random_entry_anchor 0.1.0-c011`. **This document does not run
- L14 `campaign_011`: > `approved: []`. **CAMPAIGN_011 is a null model — cannot be
- L25 `random_entry_anchor`: | Config sub-model + slot | **READY** — `RandomEntryAnchorStrategyConfig` (`extra="forbid"`) with defaults matching the frozen spec verbatim; `StrategyConfig.random_entry_anchor` slot wired; `_check_enabled` enforces required-when-enabled |
- L26 `campaign_011`: | Research config (`configs/campaign_011_random_entry_anchor.yaml`) | **READY** — loads via `load_settings(...)`; `app.trading_enabled=false`, `app.allow_order_submission=false`, `app.allow_live_trading=false`; 7-pair H4 universe matching C
- … 18 more matches

### `docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 68

- L6 `campaign_011`: Phase 0 truth audit + sprint plan for the **CAMPAIGN_011
- L7 `random_entry_anchor`: walk-forward evidence sprint** (`random_entry_anchor 0.1.0-c011`
- L9 `campaign_011`: approve the candidate. CAMPAIGN_011 cannot be approved by
- L15 `campaign_011`: > **CAMPAIGN_011 is a null model — even an unexpected PASS
- L23 `campaign_011`: | base commit | `53bcbd4` — Phase 7 of `research-random-entry-diagnostic-anchor-001` (CAMPAIGN_011 scaffold complete) |
- … 63 more matches

### `docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_trades`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `old_null_json_path`
Match count: 45

- L7 `campaign_011`: research evaluation** of CAMPAIGN_011 / `random_entry_anchor
- L7 `random_entry_anchor`: research evaluation** of CAMPAIGN_011 / `random_entry_anchor
- L13 `campaign_011`: > Paper / demo / live remain blocked. **CAMPAIGN_011 cannot be
- L24 `campaign_011`: | 1 | Data availability + provenance (gitignored symlink → same store as CAMPAIGN_010; all 7 hashes match verbatim) | ✓ ([`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md)) |
- L25 `campaign_011`: | 2 | Walk-forward plan via `scripts/run_walk_forward_dry_run.py` — 8 folds rolling, frozen, 540/180/180/180 days, universe 2020-01-01 → 2026-05-20 (IDENTICAL to CAMPAIGN_010) | ✓ ([`CAMPAIGN_011_WALK_FORWARD_PLAN.md`](CAMPAIGN_011_WALK_FOR
- … 40 more matches

### `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md`

Patterns: `campaign_012`, `campaign_011`, `random_entry_anchor`
Match count: 39

- L6 `campaign_012`: Phase 0 repo truth audit + 8-phase scaffold plan for **CAMPAIGN_012 /
- L13 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 remain
- L15 `campaign_011`: > CAMPAIGN_011 is **only the null baseline**, not a trading candidate.
- L38 `campaign_011`: - [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- L59 `campaign_011`: - `src/forex_bot/strategies/random_entry_anchor.py` (CAMPAIGN_011 scaffold reference)
- … 34 more matches

### `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md`

Patterns: `campaign_012`, `campaign_011`, `random_entry_anchor`
Match count: 32

- L6 `campaign_012`: End-of-sprint summary for the CAMPAIGN_012 scaffold sprint. Scaffolds
- L13 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
- L15 `campaign_011`: > `approved: []`. Paper / demo / live remain blocked. CAMPAIGN_011 is
- L39 `campaign_012`: | Phase 4 | `32aa0d5` | research config + CAMPAIGN_012 docs |
- L50 `campaign_012`: | `configs/campaign_012_regime_switcher_atr_percentile.yaml` | research-only candidate config |
- … 27 more matches

### `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`

Patterns: `campaign_012`, `campaign_011`, `random_entry_anchor`, `old_null_expectancy`, `old_null_pf`, `old_null_return`
Match count: 28

- L6 `campaign_012`: Phase 1 binding implementation spec for **CAMPAIGN_012 /
- L13 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
- L15 `campaign_011`: > `approved: []`. Paper / demo / live remain blocked. CAMPAIGN_011
- L23 `campaign_011`: - [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (null-baseline gate)
- L32 `campaign_011`: > session momentum also lost. CAMPAIGN_011 demonstrated that random
- … 23 more matches

### `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_READINESS.md`

Patterns: `campaign_012`, `campaign_011`, `old_null_expectancy`, `old_null_pf`, `old_null_return`
Match count: 26

- L6 `campaign_012`: One-page scaffold-readiness summary for **CAMPAIGN_012 /
- L12 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
- L14 `campaign_011`: > `approved: []`. Paper / demo / live remain blocked. CAMPAIGN_011 is
- L25 `campaign_012`: | candidate YAML | ✓ | `configs/campaign_012_regime_switcher_atr_percentile.yaml` (7-pair H4 universe; `trading_enabled: false`) |
- L32 `campaign_012`: | pre-commit checklist | ✓ | [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md) committed |
- … 21 more matches

### `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md`

Patterns: `campaign_012`, `campaign_011`, `old_null_expectancy`, `old_null_return`, `old_null_pf`
Match count: 54

- L7 `campaign_012`: **CAMPAIGN_012 / `regime_switcher_atr_percentile 0.1.0-c012`**, the C3
- L12 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
- L14 `campaign_011`: > `approved: []`. Paper / demo / live remain blocked. **CAMPAIGN_011
- L44 `campaign_012`: ## 3. CAMPAIGN_012 scaffold status (verified)
- L52 `campaign_012`: | `configs/campaign_012_regime_switcher_atr_percentile.yaml` | **present**; loads cleanly via `load_settings()` |
- … 49 more matches

### `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md`

Patterns: `campaign_012`, `campaign_011`, `old_null_expectancy`, `old_null_pf`, `old_null_return`
Match count: 43

- L6 `campaign_012`: End-of-sprint summary for the CAMPAIGN_012 evidence sprint. Ran the
- L11 `campaign_011`: > markedly worse than CAMPAIGN_011 null baseline. `configs/approved_strategies.yaml`
- L12 `campaign_011`: > remains `approved: []`. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
- L47 `campaign_011`:   - `scripts/run_campaign_012.py` (frozen-parameter assertion before any backtest; mirrors `run_campaign_011.py`)
- L47 `campaign_012`:   - `scripts/run_campaign_012.py` (frozen-parameter assertion before any backtest; mirrors `run_campaign_011.py`)
- … 38 more matches

### `docs/research/REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`

Patterns: `campaign_012`, `campaign_011`
Match count: 28

- L8 `campaign_012`: Adds CAMPAIGN_012-specific guardrails so the discovery-004 sprint
- L13 `campaign_011`: > No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
- L14 `campaign_012`: > CAMPAIGN_012 all remain REJECT. `configs/approved_strategies.yaml`
- L27 `campaign_012`: | **daily-ATR-percentile regime switcher + H4 close-vs-close trend** | **CAMPAIGN_012** | **REJECT** | **[`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md)** (new) |
- L28 `campaign_011`: | H4 deterministic-seed random-entry diagnostic anchor (null model) | CAMPAIGN_011 | REJECT (null) | structurally un-approvable by design; null-baseline only |
- … 23 more matches

### `docs/research/REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`

Patterns: `campaign_013`, `campaign_012`, `campaign_011`
Match count: 49

- L9 `campaign_013`: Adds CAMPAIGN_013-specific guardrails so the discovery-005 sprint (and
- L29 `campaign_012`: | daily-ATR-percentile regime switcher + H4 close-vs-close trend | CAMPAIGN_012 | REJECT | [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md) |
- L30 `campaign_013`: | **8-currency strength rank-gap cross-pair rotation** | **CAMPAIGN_013** | **REJECT** | **[`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md)** (new; Phase 1 of this sprint) |
- L31 `campaign_011`: | H4 deterministic-seed random-entry diagnostic anchor (null model) | CAMPAIGN_011 | REJECT (null) | structurally un-approvable by design; null-baseline only |
- L33 `campaign_013`: ## 2. New disqualifying overfitting patterns from CAMPAIGN_013
- … 44 more matches

### `docs/research/SINGLE_PAIR_PROBE_001_PLAN.md`

Patterns: `campaign_012`, `campaign_011`, `campaign_013`, `campaign_014`
Match count: 26

- L7 `campaign_012`: the EUR_USD / CAMPAIGN_012 +0.0950 R material-gap cell is either a
- L20 `campaign_011`: | pair | CAMPAIGN_011 null R (8-fold mean) | CAMPAIGN_012 R (8-fold mean) | gap | floor |
- L20 `campaign_012`: | pair | CAMPAIGN_011 null R (8-fold mean) | CAMPAIGN_012 R (8-fold mean) | gap | floor |
- L25 `campaign_011`: CAMPAIGN_010-014 vs CAMPAIGN_011-null comparison table cleared the
- L36 `campaign_012`: - The walk-forward result for CAMPAIGN_012 is **REJECT** and stays
- … 21 more matches

### `docs/research/SINGLE_PAIR_PROBE_001_RESULT.md`

Patterns: `campaign_012`, `campaign_011`, `campaign_013`, `campaign_014`
Match count: 16

- L6 `campaign_012`: **Status:** **Falsification result.** The EUR_USD / CAMPAIGN_012
- L17 `campaign_011`: **EUR_USD under CAMPAIGN_012 at +0.0950 R vs the CAMPAIGN_011
- L17 `campaign_012`: **EUR_USD under CAMPAIGN_012 at +0.0950 R vs the CAMPAIGN_011
- L31 `campaign_012`: CAMPAIGN_012 EUR_USD per-fold expectancy R across the 8 walk-
- L49 `campaign_011`:   primarily by CAMPAIGN_011 being unusually bad on those folds
- … 11 more matches

### `docs/research/SINGLE_PAIR_PROBE_001_SUMMARY.md`

Patterns: `campaign_012`, `campaign_014`
Match count: 4

- L7 `campaign_012`: single above-floor cell (EUR_USD / CAMPAIGN_012, +0.0950 R)
- L15 `campaign_012`: **No.** The EUR_USD / CAMPAIGN_012 cell fails three of the Phase 0
- L153 `campaign_012`: - **Was any campaign verdict altered?** No. CAMPAIGN_012 remains
- L196 `campaign_014`:    over from the hydrate sprint) — focused study of the CAMPAIGN_014

### `docs/research/STRATEGY_STATUS.md`

Patterns: `campaign_011`, `random_entry_anchor`, `campaign_012`, `campaign_013`, `campaign_014`, `canonical_null_json`, `old_null_expectancy`, `old_null_trades`, `old_null_pf`, `old_null_return`
Match count: 54

- L48 `campaign_011`: | `random_entry_anchor 0.1.0-c011` | rejected (null model anchor) | NO | NO | NO | CAMPAIGN_011 |
- L48 `random_entry_anchor`: | `random_entry_anchor 0.1.0-c011` | rejected (null model anchor) | NO | NO | NO | CAMPAIGN_011 |
- L49 `campaign_012`: | `regime_switcher_atr_percentile 0.1.0-c012` | rejected | NO | NO | NO | CAMPAIGN_012 |
- L50 `campaign_013`: | `cross_pair_currency_strength_rotation 0.1.0-c013` | rejected | NO | NO | NO | CAMPAIGN_013 |
- L51 `campaign_014`: | `calendar_event_window_anomaly 0.1.0-c014` | rejected | NO | NO | NO | CAMPAIGN_014 |
- … 49 more matches

### `docs/research/TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `old_null_expectancy`, `old_null_trades`, `old_null_return`, `old_null_pf`
Match count: 43

- L9 `campaign_011`: CAMPAIGN_011 → CAMPAIGN_012 → CAMPAIGN_013 sequence: each campaign
- L9 `campaign_012`: CAMPAIGN_011 → CAMPAIGN_012 → CAMPAIGN_013 sequence: each campaign
- L9 `campaign_013`: CAMPAIGN_011 → CAMPAIGN_012 → CAMPAIGN_013 sequence: each campaign
- L26 `campaign_011`: | **CAMPAIGN_011** (null model) | none — PRNG entry at `entry_probability = 0.05` per H4 bar per pair | **1,177** | **−0.0024** | **0.91** | **−0.53 %** | 3 / 7 |
- L26 `old_null_expectancy`: | **CAMPAIGN_011** (null model) | none — PRNG entry at `entry_probability = 0.05` per H4 bar per pair | **1,177** | **−0.0024** | **0.91** | **−0.53 %** | 3 / 7 |
- … 38 more matches

### `research/anti_overfit/campaign_015.py`

Patterns: `campaign_011`, `above_null_claim`
Match count: 5

- L4 `campaign_011`: CAMPAIGN_015 aggregate metrics and the matched CAMPAIGN_011 null
- L43 `above_null_claim`: # Aggregate gates (Phase 0 §8.1; for the "above null" determination).
- L55 `campaign_011`:     """All inputs needed to classify CAMPAIGN_015 vs the CAMPAIGN_011
- L79 `campaign_011`:     # Null aggregate (CAMPAIGN_011, matched sample)
- L243 `campaign_011`:         reasons.append("campaign aggregate metrics sit inside CAMPAIGN_011 null band")

### `research/backtrader_lane/__init__.py`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 4

- L5 `campaign_011`: and must not approve any strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011,
- L6 `campaign_012`: CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only exactly as
- L6 `campaign_013`: CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only exactly as
- L7 `campaign_014`: documented; CAMPAIGN_014 remains scaffold-only.

### `research/backtrader_lane/compare.py`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 4

- L423 `campaign_011`:         "CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/"
- L423 `campaign_012`:         "CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/"
- L423 `campaign_013`:         "CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/"
- L424 `campaign_014`:         "research-only. CAMPAIGN_014 remains scaffold-only."

### `research/backtrader_lane/runner.py`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 5

- L102 `campaign_011`:     campaign_id: str           # "CAMPAIGN_002", "CAMPAIGN_011", …
- L344 `campaign_011`:                 "CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/"
- L344 `campaign_012`:                 "CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/"
- L344 `campaign_013`:                 "CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/"
- L345 `campaign_014`:                 "research-only. CAMPAIGN_014 remains scaffold-only. Paper/"

### `research/backtrader_lane/strategies/__init__.py`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 2

- L17 `campaign_011`:     campaign_011_random_entry_anchor,  # noqa: F401
- L17 `random_entry_anchor`:     campaign_011_random_entry_anchor,  # noqa: F401

### `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 64

- L1 `campaign_011`: """Backtrader port of CAMPAIGN_011 H4 ``random_entry_anchor 0.1.0-c011``.
- L1 `random_entry_anchor`: """Backtrader port of CAMPAIGN_011 H4 ``random_entry_anchor 0.1.0-c011``.
- L4 `random_entry_anchor`: `src/forex_bot/strategies/random_entry_anchor.py` (R1-R8) and the
- L6 `campaign_011`: `research/lean_parity/campaign_011_h4_bespoke_reference.json` produced
- L25 `campaign_011`: ``configs/campaign_011_random_entry_anchor.yaml`` and verified against
- … 59 more matches

### `research/calendar/fixtures/campaign_014_events.json`

Patterns: `campaign_014`
Match count: 1

- L2 `campaign_014`:   "schema_version": "campaign_014.event_fixture.v1",

### `research/campaign_015/diagnostics/backtrader_fold_window/run_manifest.json`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 4

- L3 `campaign_011`:     "description": "Backtrader secondary-lane run manifest. Verification only \u2014 strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains sca
- L3 `campaign_012`:     "description": "Backtrader secondary-lane run manifest. Verification only \u2014 strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains sca
- L3 `campaign_013`:     "description": "Backtrader secondary-lane run manifest. Verification only \u2014 strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains sca
- L3 `campaign_014`:     "description": "Backtrader secondary-lane run manifest. Verification only \u2014 strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains sca

### `research/campaign_015/diagnostics/backtrader_fold_window_deduped/run_manifest.json`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 4

- L3 `campaign_011`:     "description": "Backtrader secondary-lane run manifest. Verification only \u2014 strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains sca
- L3 `campaign_012`:     "description": "Backtrader secondary-lane run manifest. Verification only \u2014 strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains sca
- L3 `campaign_013`:     "description": "Backtrader secondary-lane run manifest. Verification only \u2014 strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains sca
- L3 `campaign_014`:     "description": "Backtrader secondary-lane run manifest. Verification only \u2014 strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains sca

### `research/campaign_015/diagnostics/backtrader_fold_window_riskengine_fill_parity/run_manifest.json`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 4

- L3 `campaign_011`:     "description": "Backtrader secondary-lane run manifest. Verification only \u2014 strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains sca
- L3 `campaign_012`:     "description": "Backtrader secondary-lane run manifest. Verification only \u2014 strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains sca
- L3 `campaign_013`:     "description": "Backtrader secondary-lane run manifest. Verification only \u2014 strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains sca
- L3 `campaign_014`:     "description": "Backtrader secondary-lane run manifest. Verification only \u2014 strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains sca

### `research/campaign_015/diagnostics/backtrader_lane/comparison_summary.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 4

- L3 `campaign_011`: > `strategy_evidence: false`. Verification infrastructure. Does **not** approve any strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains scaffold-only.
- L3 `campaign_012`: > `strategy_evidence: false`. Verification infrastructure. Does **not** approve any strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains scaffold-only.
- L3 `campaign_013`: > `strategy_evidence: false`. Verification infrastructure. Does **not** approve any strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains scaffold-only.
- L3 `campaign_014`: > `strategy_evidence: false`. Verification infrastructure. Does **not** approve any strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains scaffold-only.

### `research/campaign_015/diagnostics/backtrader_lane/run_manifest.json`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 4

- L3 `campaign_011`:     "description": "Backtrader secondary-lane run manifest. Verification only \u2014 strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains sca
- L3 `campaign_012`:     "description": "Backtrader secondary-lane run manifest. Verification only \u2014 strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains sca
- L3 `campaign_013`:     "description": "Backtrader secondary-lane run manifest. Verification only \u2014 strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains sca
- L3 `campaign_014`:     "description": "Backtrader secondary-lane run manifest. Verification only \u2014 strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains sca

### `research/campaign_015/diagnostics/null_and_anti_overfit.json`

Patterns: `random_entry_anchor`, `campaign_011`
Match count: 2

- L6 `random_entry_anchor`:   "null_model": "random_entry_anchor",
- L132 `campaign_011`:   "diagnostic_disclaimer": "Even a ROBUST_ABOVE_NULL label here does NOT approve failed_breakout_reversal; approval requires a fresh pre-committed campaign on a clean candidate and a human registry edit. CAMPAIGN_011 evidence is read-only."

### `research/campaign_015/diagnostics/null_and_anti_overfit.md`

Patterns: `random_entry_anchor`, `campaign_011`
Match count: 3

- L4 `random_entry_anchor`: **Null model:** `random_entry_anchor`
- L8 `campaign_011`: > Even a ROBUST_ABOVE_NULL label here does NOT approve failed_breakout_reversal; approval requires a fresh pre-committed campaign on a clean candidate and a human registry edit. CAMPAIGN_011 evidence is read-only.
- L10 `campaign_011`: ## Per-fold gap vs matched CAMPAIGN_011 null

### `research/campaign_015/diagnostics/null_and_anti_overfit_deduped.json`

Patterns: `random_entry_anchor`, `campaign_011`
Match count: 2

- L6 `random_entry_anchor`:   "null_model": "random_entry_anchor",
- L132 `campaign_011`:   "diagnostic_disclaimer": "Even a ROBUST_ABOVE_NULL label here does NOT approve failed_breakout_reversal; approval requires a fresh pre-committed campaign on a clean candidate and a human registry edit. CAMPAIGN_011 evidence is read-only."

### `research/campaign_015/diagnostics/null_and_anti_overfit_deduped.md`

Patterns: `random_entry_anchor`, `campaign_011`
Match count: 3

- L4 `random_entry_anchor`: **Null model:** `random_entry_anchor`
- L8 `campaign_011`: > Even a ROBUST_ABOVE_NULL label here does NOT approve failed_breakout_reversal; approval requires a fresh pre-committed campaign on a clean candidate and a human registry edit. CAMPAIGN_011 evidence is read-only.
- L10 `campaign_011`: ## Per-fold gap vs matched CAMPAIGN_011 null

### `research/contamination_audit/campaign_data_source_inventory.json`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 672

- L1716 `campaign_011`:       "campaign_id": "CAMPAIGN_011",
- L1717 `random_entry_anchor`:       "strategy_name": "random_entry_anchor 0.1.0-c011",
- L1718 `campaign_011`:       "artifact_path": "backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.md",
- L1718 `random_entry_anchor`:       "artifact_path": "backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.md",
- L1718 `old_null_json_path`:       "artifact_path": "backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.md",
- … 667 more matches

### `research/contamination_audit/campaign_data_source_inventory.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 126

- L172 `campaign_011`: ### CAMPAIGN_011 (51 artifacts)
- L174 `campaign_011`: - `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.md` — **UNKNOWN_REQUIRES_RERUN** — verdict=n/a
- L174 `random_entry_anchor`: - `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.md` — **UNKNOWN_REQUIRES_RERUN** — verdict=n/a
- L174 `old_null_json_path`: - `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.md` — **UNKNOWN_REQUIRES_RERUN** — verdict=n/a
- L175 `campaign_011`: - `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_summary.json` — **UNKNOWN_REQUIRES_RERUN** — verdict=n/a
- … 121 more matches

### `research/contamination_audit/campaign_integrity_classification.json`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_trades`, `campaign_012`, `old_null_json_path`, `campaign_013`, `campaign_014`
Match count: 71

- L17 `campaign_011`:   "campaign_011_deduped_artifact": "backtests/CAMPAIGN_011_random_entry_anchor_deduped",
- L17 `random_entry_anchor`:   "campaign_011_deduped_artifact": "backtests/CAMPAIGN_011_random_entry_anchor_deduped",
- L217 `campaign_011`:       "campaign_id": "CAMPAIGN_011",
- L218 `random_entry_anchor`:       "strategy_name": "random_entry_anchor 0.1.0-c011",
- L224 `old_null_trades`:       "why": "Null-model anchor on pre-fix SQLite (\u22120.0024 R, 1177 trades). Deduped rerun artifact exists locally (\u22120.0029 R, 1180 trades) but must be promoted as canonical before null comparisons for CAMPAIGN_012\u2013015 remain 
- … 66 more matches

### `research/contamination_audit/campaign_integrity_classification.md`

Patterns: `campaign_011`, `old_null_expectancy`, `old_null_trades`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 10

- L97 `campaign_011`: ### CAMPAIGN_011 — NULL_BASELINE_REQUIRES_RERUN
- L103 `old_null_expectancy`: - **Why:** Null-model anchor on pre-fix SQLite (−0.0024 R, 1177 trades). Deduped rerun artifact exists locally (−0.0029 R, 1180 trades) but must be promoted as canonical before null comparisons for CAMPAIGN_012–015 remain valid.
- L103 `old_null_trades`: - **Why:** Null-model anchor on pre-fix SQLite (−0.0024 R, 1177 trades). Deduped rerun artifact exists locally (−0.0029 R, 1180 trades) but must be promoted as canonical before null comparisons for CAMPAIGN_012–015 remain valid.
- L103 `campaign_012`: - **Why:** Null-model anchor on pre-fix SQLite (−0.0024 R, 1177 trades). Deduped rerun artifact exists locally (−0.0029 R, 1180 trades) but must be promoted as canonical before null comparisons for CAMPAIGN_012–015 remain valid.
- L105 `campaign_012`: ### CAMPAIGN_012 — LIKELY_CONTAMINATED
- … 5 more matches

### `research/contamination_audit/post_dedup_null_reference_inventory.json`

Patterns: `campaign_011`, `canonical_null_json`, `random_entry_anchor`, `old_null_json_path`, `campaign_012`, `campaign_013`, `campaign_014`, `superseded_null_reference`, `old_null_expectancy`, `old_null_trades`, `old_null_pf`, `above_null_claim`, `old_null_return`
Match count: 121046

- L4 `campaign_011`:   "canonical_null_json": "research/null_baselines/campaign_011_deduped_null_baseline.json",
- L4 `canonical_null_json`:   "canonical_null_json": "research/null_baselines/campaign_011_deduped_null_baseline.json",
- L5 `campaign_011`:   "superseded_null_artifact": "backtests/CAMPAIGN_011_random_entry_anchor",
- L5 `random_entry_anchor`:   "superseded_null_artifact": "backtests/CAMPAIGN_011_random_entry_anchor",
- L5 `old_null_json_path`:   "superseded_null_artifact": "backtests/CAMPAIGN_011_random_entry_anchor",
- … 121041 more matches

### `research/contamination_audit/post_dedup_null_reference_inventory.md`

Patterns: `campaign_011`, `canonical_null_json`, `random_entry_anchor`, `old_null_json_path`, `campaign_012`, `campaign_013`, `campaign_014`, `superseded_null_reference`, `old_null_trades`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `above_null_claim`
Match count: 5543

- L9 `campaign_011`: - Canonical null JSON: `research/null_baselines/campaign_011_deduped_null_baseline.json`
- L9 `canonical_null_json`: - Canonical null JSON: `research/null_baselines/campaign_011_deduped_null_baseline.json`
- L10 `campaign_011`: - Superseded artifact: `backtests/CAMPAIGN_011_random_entry_anchor`
- L10 `random_entry_anchor`: - Superseded artifact: `backtests/CAMPAIGN_011_random_entry_anchor`
- L10 `old_null_json_path`: - Superseded artifact: `backtests/CAMPAIGN_011_random_entry_anchor`
- … 5538 more matches

### `research/edge_discovery/real_data.py`

Patterns: `campaign_014`, `campaign_011`, `canonical_null_json`, `random_entry_anchor`, `old_null_json_path`
Match count: 13

- L9 `campaign_014`: and the committed CAMPAIGN_014 event fixture JSON).
- L243 `campaign_014`:     ``backtests/CAMPAIGN_014_calendar_event_window_anomaly``. The
- L271 `campaign_011`:     """Load the deduped CAMPAIGN_011 canonical null rollup.
- L274 `campaign_011`:     ``research/null_baselines/campaign_011_deduped_null_baseline.json``,
- L274 `canonical_null_json`:     ``research/null_baselines/campaign_011_deduped_null_baseline.json``,
- … 8 more matches

### `research/edge_discovery/studies/bias_cross_campaign_comparability.py`

Patterns: `campaign_014`, `campaign_011`, `random_entry_anchor`, `campaign_012`, `campaign_013`
Match count: 9

- L5 `campaign_014`: Checks whether CAMPAIGN_010 - CAMPAIGN_014 are comparable enough for
- L56 `campaign_011`:     "CAMPAIGN_011_random_entry_anchor",
- L56 `random_entry_anchor`:     "CAMPAIGN_011_random_entry_anchor",
- L57 `campaign_012`:     "CAMPAIGN_012_regime_switcher_atr_percentile",
- L58 `campaign_013`:     "CAMPAIGN_013_cross_pair_currency_strength_rotation",
- … 4 more matches

### `research/edge_discovery/studies/bias_null_baseline.py`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 18

- L5 `campaign_011`: Audits CAMPAIGN_011 (the binding random-entry null baseline) against
- L19 `campaign_011`: The script is read-only: it consumes only the committed CAMPAIGN_011
- L27 `campaign_011`:   * ``backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_NN/
- L27 `random_entry_anchor`:   * ``backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_NN/
- L27 `old_null_json_path`:   * ``backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_NN/
- … 13 more matches

### `research/edge_discovery/studies/exit_asymmetry_cross_campaign.py`

Patterns: `campaign_012`, `campaign_014`, `campaign_011`, `random_entry_anchor`, `old_null_json_path`, `campaign_013`
Match count: 22

- L7 `campaign_012`: that surfaced inside the EUR_USD / CAMPAIGN_012 falsification probe
- L9 `campaign_014`: committed CAMPAIGN_010 - CAMPAIGN_014 trade ledger.
- L19 `campaign_011`:   * ``backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_NN/fold_NN_<PAIR>_trades.csv``
- L19 `random_entry_anchor`:   * ``backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_NN/fold_NN_<PAIR>_trades.csv``
- L19 `old_null_json_path`:   * ``backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_NN/fold_NN_<PAIR>_trades.csv``
- … 17 more matches

### `research/edge_discovery/studies/exit_asymmetry_robustness.py`

Patterns: `campaign_011`, `random_entry_anchor`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 11

- L11 `campaign_011`: ``mean_R_given_time`` or ``mean_R_overall`` vs CAMPAIGN_011 — plus
- L66 `campaign_011`:     "CAMPAIGN_011_random_entry_anchor",
- L66 `random_entry_anchor`:     "CAMPAIGN_011_random_entry_anchor",
- L67 `campaign_012`:     "CAMPAIGN_012_regime_switcher_atr_percentile",
- L68 `campaign_013`:     "CAMPAIGN_013_cross_pair_currency_strength_rotation",
- … 6 more matches

### `research/edge_discovery/studies/outputs/real/bias_cross_campaign_comparability.json`

Patterns: `campaign_011`, `random_entry_anchor`, `campaign_012`, `campaign_013`, `campaign_014`, `old_null_trades`, `old_null_expectancy`, `old_null_json_path`
Match count: 44

- L139 `campaign_011`:         "CAMPAIGN_011_random_entry_anchor": 1,
- L139 `random_entry_anchor`:         "CAMPAIGN_011_random_entry_anchor": 1,
- L140 `campaign_012`:         "CAMPAIGN_012_regime_switcher_atr_percentile": 1,
- L141 `campaign_013`:         "CAMPAIGN_013_cross_pair_currency_strength_rotation": 1,
- L142 `campaign_014`:         "CAMPAIGN_014_calendar_event_window_anomaly": 1
- … 39 more matches

### `research/edge_discovery/studies/outputs/real/bias_cross_campaign_comparability.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_trades`, `campaign_012`, `campaign_013`, `campaign_014`, `old_null_expectancy`
Match count: 24

- L27 `campaign_011`: | CAMPAIGN_011_random_entry_anchor | 1177 | 1177 | 0 | 0 | 1.000 | complete |
- L27 `random_entry_anchor`: | CAMPAIGN_011_random_entry_anchor | 1177 | 1177 | 0 | 0 | 1.000 | complete |
- L27 `old_null_trades`: | CAMPAIGN_011_random_entry_anchor | 1177 | 1177 | 0 | 0 | 1.000 | complete |
- L28 `campaign_012`: | CAMPAIGN_012_regime_switcher_atr_percentile | 3726 | 2009 | 1717 | 0 | 0.539 | partial |
- L29 `campaign_013`: | CAMPAIGN_013_cross_pair_currency_strength_rotation | 7940 | 3237 | 3530 | 1173 | 0.408 | partial |
- … 19 more matches

### `research/edge_discovery/studies/outputs/real/bias_null_baseline.json`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_trades`, `campaign_012`, `campaign_013`, `campaign_014`, `old_null_expectancy`, `old_null_json_path`
Match count: 47

- L8 `campaign_011`:     "null_campaign": "CAMPAIGN_011_random_entry_anchor",
- L8 `random_entry_anchor`:     "null_campaign": "CAMPAIGN_011_random_entry_anchor",
- L9 `old_null_trades`:     "null_trade_count": 1177,
- L51 `campaign_011`:       "campaign": "CAMPAIGN_011_random_entry_anchor",
- L51 `random_entry_anchor`:       "campaign": "CAMPAIGN_011_random_entry_anchor",
- … 42 more matches

### `research/edge_discovery/studies/outputs/real/bias_null_baseline.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_trades`, `campaign_012`, `campaign_013`, `campaign_014`, `old_null_expectancy`
Match count: 32

- L9 `campaign_011`: - null_campaign: `CAMPAIGN_011_random_entry_anchor`
- L9 `random_entry_anchor`: - null_campaign: `CAMPAIGN_011_random_entry_anchor`
- L10 `old_null_trades`: - null_trade_count: 1177
- L19 `campaign_011`: | CAMPAIGN_011_random_entry_anchor | 8 | 7 | 0 |
- L19 `random_entry_anchor`: | CAMPAIGN_011_random_entry_anchor | 8 | 7 | 0 |
- … 27 more matches

### `research/edge_discovery/studies/outputs/real/exit_asymmetry_cross_campaign.json`

Patterns: `campaign_011`, `random_entry_anchor`, `campaign_012`, `campaign_013`, `campaign_014`, `old_null_trades`, `old_null_expectancy`, `old_null_json_path`
Match count: 122

- L17 `campaign_011`:       "CAMPAIGN_011_random_entry_anchor",
- L17 `random_entry_anchor`:       "CAMPAIGN_011_random_entry_anchor",
- L18 `campaign_012`:       "CAMPAIGN_012_regime_switcher_atr_percentile",
- L19 `campaign_013`:       "CAMPAIGN_013_cross_pair_currency_strength_rotation",
- L20 `campaign_014`:       "CAMPAIGN_014_calendar_event_window_anomaly"
- … 117 more matches

### `research/edge_discovery/studies/outputs/real/exit_asymmetry_cross_campaign.md`

Patterns: `campaign_014`, `campaign_011`, `random_entry_anchor`, `old_null_expectancy`, `old_null_trades`, `campaign_012`, `campaign_013`, `old_null_json_path`
Match count: 41

- L9 `campaign_014`: > CAMPAIGN_010 - CAMPAIGN_014 remain REJECT-anchored.
- L21 `campaign_011`: | CAMPAIGN_011_random_entry_anchor | 1,177 | 0.205 | 0.789 | -0.8312 | 0.2093 | -0.0024 | -2.872 | 0.705 | 0.665 |
- L21 `random_entry_anchor`: | CAMPAIGN_011_random_entry_anchor | 1,177 | 0.205 | 0.789 | -0.8312 | 0.2093 | -0.0024 | -2.872 | 0.705 | 0.665 |
- L21 `old_null_expectancy`: | CAMPAIGN_011_random_entry_anchor | 1,177 | 0.205 | 0.789 | -0.8312 | 0.2093 | -0.0024 | -2.872 | 0.705 | 0.665 |
- L21 `old_null_trades`: | CAMPAIGN_011_random_entry_anchor | 1,177 | 0.205 | 0.789 | -0.8312 | 0.2093 | -0.0024 | -2.872 | 0.705 | 0.665 |
- … 36 more matches

### `research/edge_discovery/studies/outputs/real/exit_asymmetry_robustness.json`

Patterns: `campaign_013`, `campaign_011`, `random_entry_anchor`, `campaign_012`, `campaign_014`, `old_null_json_path`
Match count: 77

- L7 `campaign_013`:       "campaign": "CAMPAIGN_013_cross_pair_currency_strength_rotation",
- L138 `campaign_011`:       "campaign": "CAMPAIGN_011_random_entry_anchor",
- L138 `random_entry_anchor`:       "campaign": "CAMPAIGN_011_random_entry_anchor",
- L150 `campaign_011`:       "campaign": "CAMPAIGN_011_random_entry_anchor",
- L150 `random_entry_anchor`:       "campaign": "CAMPAIGN_011_random_entry_anchor",
- … 72 more matches

### `research/edge_discovery/studies/outputs/real/exit_asymmetry_robustness.md`

Patterns: `campaign_014`, `campaign_012`, `campaign_011`, `random_entry_anchor`, `campaign_013`, `old_null_json_path`
Match count: 21

- L9 `campaign_014`: > CAMPAIGN_010 - CAMPAIGN_014 remain REJECT-anchored.
- L28 `campaign_012`: | CAMPAIGN_012_regime_switcher_atr_percentile | EUR_USD | +0.0300 | -4.391 | -0.0189 | 0.0542 |
- L37 `campaign_011`: | CAMPAIGN_011_random_entry_anchor | NZD_USD | 0.1411 | 0.1999 |
- L37 `random_entry_anchor`: | CAMPAIGN_011_random_entry_anchor | NZD_USD | 0.1411 | 0.1999 |
- L38 `campaign_014`: | CAMPAIGN_014_calendar_event_window_anomaly | USD_CHF | 0.1354 | 0.1129 |
- … 16 more matches

### `research/edge_discovery/studies/outputs/real/probe_robustness_eur_usd_c012.json`

Patterns: `campaign_012`, `campaign_011`, `random_entry_anchor`, `campaign_013`, `campaign_014`, `old_null_json_path`
Match count: 18

- L4 `campaign_012`:   "candidate_campaign": "CAMPAIGN_012_regime_switcher_atr_percentile",
- L5 `campaign_011`:   "null_campaign": "CAMPAIGN_011_random_entry_anchor",
- L5 `random_entry_anchor`:   "null_campaign": "CAMPAIGN_011_random_entry_anchor",
- L130 `campaign_012`:       "candidate": "CAMPAIGN_012_regime_switcher_atr_percentile",
- L150 `campaign_013`:       "candidate": "CAMPAIGN_013_cross_pair_currency_strength_rotation",
- … 13 more matches

### `research/edge_discovery/studies/outputs/real/probe_robustness_eur_usd_c012.md`

Patterns: `campaign_012`, `campaign_011`, `campaign_013`, `campaign_014`
Match count: 5

- L4 `campaign_012`: > promote, or change any campaign status. CAMPAIGN_012 remains REJECT;
- L5 `campaign_011`: > CAMPAIGN_011 remains the null model.
- L69 `campaign_012`: | CAMPAIGN_012_regime_switcher_atr_percentile | +0.0300 | -0.0189 | -0.0650 | **+0.0950** | ✓ | 3 | 479 |
- L71 `campaign_013`: | CAMPAIGN_013_cross_pair_currency_strength_rotation | -0.0290 | -0.0057 | -0.0650 | **+0.0360** |   | 0 | 1412 |
- L72 `campaign_014`: | CAMPAIGN_014_calendar_event_window_anomaly | -0.2148 | -0.3081 | -0.0650 | **-0.1498** |   | 3 | 100 |

### `research/edge_discovery/studies/outputs/real/probe_single_pair_eur_usd_c012.json`

Patterns: `campaign_012`, `campaign_011`, `random_entry_anchor`, `old_null_json_path`, `old_null_trades`
Match count: 55

- L4 `campaign_012`:   "candidate_campaign": "CAMPAIGN_012_regime_switcher_atr_percentile",
- L5 `campaign_011`:   "null_campaign": "CAMPAIGN_011_random_entry_anchor",
- L5 `random_entry_anchor`:   "null_campaign": "CAMPAIGN_011_random_entry_anchor",
- L10 `campaign_012`:         "campaign_name": "CAMPAIGN_012_regime_switcher_atr_percentile",
- L40 `campaign_012`:         "campaign_name": "CAMPAIGN_012_regime_switcher_atr_percentile",
- … 50 more matches

### `research/edge_discovery/studies/outputs/real/probe_single_pair_eur_usd_c012.md`

Patterns: `campaign_012`, `campaign_011`, `random_entry_anchor`
Match count: 8

- L4 `campaign_012`: > promote, or change any campaign status. CAMPAIGN_012 remains REJECT;
- L5 `campaign_011`: > CAMPAIGN_011 remains the null model.
- L10 `campaign_012`: - candidate: `CAMPAIGN_012_regime_switcher_atr_percentile`
- L11 `campaign_011`: - null: `CAMPAIGN_011_random_entry_anchor`
- L11 `random_entry_anchor`: - null: `CAMPAIGN_011_random_entry_anchor`
- … 3 more matches

### `research/edge_discovery/studies/outputs/real/real_study_event_window.json`

Patterns: `campaign_014`, `campaign_011`, `random_entry_anchor`, `old_null_expectancy`, `old_null_json_path`, `old_null_trades`
Match count: 17

- L3 `campaign_014`:   "campaign_source": "CAMPAIGN_014_calendar_event_window_anomaly",
- L4 `campaign_011`:   "null_source": "CAMPAIGN_011_random_entry_anchor",
- L4 `random_entry_anchor`:   "null_source": "CAMPAIGN_011_random_entry_anchor",
- L9 `old_null_expectancy`:   "null_mean_r": -0.002439857834553023,
- L95 `campaign_014`:         "path": "backtests/CAMPAIGN_014_calendar_event_window_anomaly",
- … 12 more matches

### `research/edge_discovery/studies/outputs/real/real_study_event_window.md`

Patterns: `campaign_014`, `campaign_011`, `random_entry_anchor`, `old_null_trades`, `old_null_json_path`, `old_null_expectancy`
Match count: 16

- L4 `campaign_014`: > promote, or change any campaign status. CAMPAIGN_014 remains
- L5 `campaign_011`: > REJECT and CAMPAIGN_011 remains the null model.
- L13 `campaign_014`:   - `campaign_trades` — `backtests/CAMPAIGN_014_calendar_event_window_anomaly` — rows=`720` — sha256=`(per-fold per-pa…`
- L14 `campaign_014`:   - `event_fixture_json` — `research/calendar/fixtures/campaign_014_events.json` — rows=`281` — sha256=`584a19a8182bb338…`
- L15 `campaign_011`:   - `campaign_walk_forward_results` — `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json` — rows=`1177` — sha256=`ac6e72942d1a016c…`
- … 11 more matches

### `research/edge_discovery/studies/outputs/real/real_study_pair_baseline.json`

Patterns: `campaign_011`, `random_entry_anchor`, `campaign_012`, `campaign_013`, `campaign_014`, `old_null_json_path`
Match count: 69

- L3 `campaign_011`:   "null_campaign": "CAMPAIGN_011_random_entry_anchor",
- L3 `random_entry_anchor`:   "null_campaign": "CAMPAIGN_011_random_entry_anchor",
- L6 `campaign_012`:     "CAMPAIGN_012_regime_switcher_atr_percentile",
- L7 `campaign_013`:     "CAMPAIGN_013_cross_pair_currency_strength_rotation",
- L8 `campaign_014`:     "CAMPAIGN_014_calendar_event_window_anomaly"
- … 64 more matches

### `research/edge_discovery/studies/outputs/real/real_study_pair_baseline.md`

Patterns: `campaign_011`, `above_null_claim`
Match count: 5

- L5 `campaign_011`: > 014 remain REJECT; CAMPAIGN_011 remains the null model.
- L14 `campaign_011`:   - CAMPAIGN_011 supplies the null floor per pair, not a global scalar — same universe, same fold layout, random entries.
- L15 `campaign_011`:   - No campaign verdict is changed by this study. CAMPAIGN_010, 012, 013, 014 remain REJECT and CAMPAIGN_011 remains the null model.
- L17 `campaign_011`: ## Null per pair (CAMPAIGN_011 mean expectancy R across 8 folds)
- L31 `above_null_claim`: | pair | null R | C010_session_breakout R | gap C010_session_breakout | C012_regime_switcher_atr_percentile R | gap C012_regime_switcher_atr_percentile | C013_cross_pair_currency_strength_rotation R | gap C013_cross_pair_currency_strength_r

### `research/edge_discovery/studies/outputs/real/real_study_turnover_cost.json`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_trades`, `old_null_expectancy`, `campaign_012`, `campaign_013`, `campaign_014`, `old_null_json_path`
Match count: 35

- L24 `campaign_011`:       "campaign_name": "CAMPAIGN_011_random_entry_anchor",
- L24 `random_entry_anchor`:       "campaign_name": "CAMPAIGN_011_random_entry_anchor",
- L25 `old_null_trades`:       "n_trades_observed": 1177,
- L26 `old_null_trades`:       "n_trades_published": 1177,
- L27 `old_null_expectancy`:       "mean_r_observed": -0.0024398578345530258,
- … 30 more matches

### `research/edge_discovery/studies/outputs/real/real_study_turnover_cost.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_expectancy`, `old_null_trades`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 9

- L21 `campaign_011`: | CAMPAIGN_011_random_entry_anchor | 1177 | 1177 | -0.0024 | -0.0024 | -0.0006 | 0.493 | 1.73 | REJECT |
- L21 `random_entry_anchor`: | CAMPAIGN_011_random_entry_anchor | 1177 | 1177 | -0.0024 | -0.0024 | -0.0006 | 0.493 | 1.73 | REJECT |
- L21 `old_null_expectancy`: | CAMPAIGN_011_random_entry_anchor | 1177 | 1177 | -0.0024 | -0.0024 | -0.0006 | 0.493 | 1.73 | REJECT |
- L21 `old_null_trades`: | CAMPAIGN_011_random_entry_anchor | 1177 | 1177 | -0.0024 | -0.0024 | -0.0006 | 0.493 | 1.73 | REJECT |
- L22 `campaign_012`: | CAMPAIGN_012_regime_switcher_atr_percentile | 3726 | 3726 | -0.0521 | -0.0521 | -0.0031 | 0.462 | 1.75 | REJECT |
- … 4 more matches

### `research/edge_discovery/studies/outputs/study_pair_baseline.md`

Patterns: `above_null_claim`
Match count: 2

- L13 `above_null_claim`: | pair | random R | CAMPAIGN_002_H4_test | CAMPAIGN_003_test | CAMPAIGN_004_test | CAMPAIGN_007_val | CAMPAIGN_008_val | CAMPAIGN_009_val | best gap | best campaign | n above null (test) | n above null (val-only) |
- L26 `above_null_claim`: - A pair with `n above null (test) >= 1` shows at least one *test-window* result above the null — that is the strongest form of evidence in the archive. A pair with only `n above null (val-only) >= 1` was above null only on a validation win

### `research/edge_discovery/studies/probe_robustness_eur_usd_c012.py`

Patterns: `campaign_012`, `campaign_011`, `random_entry_anchor`, `campaign_013`, `campaign_014`
Match count: 10

- L2 `campaign_012`: CAMPAIGN_012 +0.0950 R cell.
- L13 `campaign_012`: Exploratory lab output. Not strategy evidence. CAMPAIGN_012 remains
- L39 `campaign_012`: CANDIDATE = "CAMPAIGN_012_regime_switcher_atr_percentile"
- L40 `campaign_011`: NULL = "CAMPAIGN_011_random_entry_anchor"
- L40 `random_entry_anchor`: NULL = "CAMPAIGN_011_random_entry_anchor"
- … 5 more matches

### `research/edge_discovery/studies/probe_single_pair_eur_usd_c012.py`

Patterns: `campaign_012`, `campaign_011`, `random_entry_anchor`
Match count: 13

- L1 `campaign_012`: """Single-pair probe — extract the EUR_USD / CAMPAIGN_012 evidence
- L2 `campaign_011`: slice and its CAMPAIGN_011 EUR_USD null counterpart.
- L7 `campaign_012`: metrics and the per-trade ledger for EUR_USD under CAMPAIGN_012,
- L8 `campaign_011`: side-by-side with CAMPAIGN_011's EUR_USD numbers.
- L14 `campaign_012`: Exploratory lab output. Not strategy evidence. CAMPAIGN_012 remains
- … 8 more matches

### `research/edge_discovery/studies/study_event_window.py`

Patterns: `campaign_014`
Match count: 1

- L8 `campaign_014`: the patterns the sprint brief's CAMPAIGN_014 narrative warned about:

### `research/edge_discovery/studies/study_pair_baseline.py`

Patterns: `above_null_claim`
Match count: 4

- L194 `above_null_claim`:     lines.append("| pair | random R | " + " | ".join(camps) + " | best gap | best campaign | n above null (test) | n above null (val-only) |")
- L219 `above_null_claim`:         "- A pair with `n above null (test) >= 1` shows at least one "
- L221 `above_null_claim`:         "form of evidence in the archive. A pair with only `n above null "
- L222 `above_null_claim`:         "(val-only) >= 1` was above null only on a validation window "

### `research/edge_discovery/studies/study_real_event_window.py`

Patterns: `campaign_014`, `campaign_011`, `canonical_null_json`
Match count: 31

- L1 `campaign_014`: """Real-data study — CAMPAIGN_014 event-window continuation vs reversal.
- L6 `campaign_014`:   * trades:  committed CAMPAIGN_014 per-fold per-pair trade CSVs (real
- L8 `campaign_014`:   * events:  research/calendar/fixtures/campaign_014_events.json
- L10 `campaign_011`:   * null:    CAMPAIGN_011 deduped canonical null rollup (the
- L11 `campaign_011`:              binding null baseline per CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- … 26 more matches

### `research/edge_discovery/studies/study_real_pair_baseline.py`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`, `random_entry_anchor`, `above_null_claim`
Match count: 14

- L2 `campaign_011`: folds, compared against the CAMPAIGN_011 random-entry null.
- L12 `campaign_011`:     CAMPAIGN_011 null by ≥ +0.05 R (the lab's material-gap floor)
- L16 `campaign_011`: CAMPAIGN_011 supplies the per-pair null floor — per-pair
- L17 `campaign_011`: expectancy-R averaged across CAMPAIGN_011's eight folds, NOT a global
- L50 `campaign_012`:     "CAMPAIGN_012_regime_switcher_atr_percentile",
- … 9 more matches

### `research/edge_discovery/studies/study_real_turnover_cost.py`

Patterns: `campaign_011`, `random_entry_anchor`, `campaign_012`, `campaign_013`, `campaign_014`
Match count: 7

- L46 `campaign_011`:     "CAMPAIGN_011_random_entry_anchor",
- L46 `random_entry_anchor`:     "CAMPAIGN_011_random_entry_anchor",
- L47 `campaign_012`:     "CAMPAIGN_012_regime_switcher_atr_percentile",
- L48 `campaign_013`:     "CAMPAIGN_013_cross_pair_currency_strength_rotation",
- L49 `campaign_014`:     "CAMPAIGN_014_calendar_event_window_anomaly",
- … 2 more matches

### `research/edge_discovery/studies/study_turnover_cost.py`

Patterns: `campaign_012`
Match count: 1

- L3 `campaign_012`: Direct attack on the lesson the sprint brief's CAMPAIGN_012 / 013

### `research/lean_parity/campaign_011_h4_bespoke_reference.json`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 2

- L87 `campaign_011`:   "parity_target": "CAMPAIGN_011 H4 random_entry_anchor null-model baseline",
- L87 `random_entry_anchor`:   "parity_target": "CAMPAIGN_011 H4 random_entry_anchor null-model baseline",

### `research/lean_parity/campaign_011_h4_bespoke_reference_per_fold.json`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`
Match count: 5

- L545 `campaign_011`:   "parity_target": "CAMPAIGN_011 H4 random_entry_anchor null-model baseline (per-fold)",
- L545 `random_entry_anchor`:   "parity_target": "CAMPAIGN_011 H4 random_entry_anchor null-model baseline (per-fold)",
- L546 `campaign_011`:   "plan_source": "backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json",
- L546 `random_entry_anchor`:   "plan_source": "backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json",
- L546 `old_null_json_path`:   "plan_source": "backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json",

### `research/null_baselines/__init__.py`

Patterns: `campaign_011`
Match count: 7

- L3 `campaign_011`: from research.null_baselines.campaign_011_deduped import (
- L4 `campaign_011`:     CANONICAL_CAMPAIGN_011_DEDUPED_JSON,
- L5 `campaign_011`:     CANONICAL_CAMPAIGN_011_DEDUPED_MD,
- L6 `campaign_011`:     load_campaign_011_deduped_null_baseline,
- L10 `campaign_011`:     "CANONICAL_CAMPAIGN_011_DEDUPED_JSON",
- … 2 more matches

### `research/null_baselines/campaign_011_deduped.py`

Patterns: `campaign_011`, `canonical_null_json`, `random_entry_anchor`, `old_null_json_path`
Match count: 15

- L1 `campaign_011`: """CAMPAIGN_011 deduped null-baseline rollup loader.
- L4 `campaign_011`: ``research/null_baselines/campaign_011_deduped_null_baseline.json``.
- L4 `canonical_null_json`: ``research/null_baselines/campaign_011_deduped_null_baseline.json``.
- L6 `campaign_011`: ``backtests/CAMPAIGN_011_random_entry_anchor/`` (LIKELY_CONTAMINATED).
- L6 `random_entry_anchor`: ``backtests/CAMPAIGN_011_random_entry_anchor/`` (LIKELY_CONTAMINATED).
- … 10 more matches

### `research/null_baselines/campaign_011_deduped_null_baseline.json`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`, `old_null_expectancy`, `old_null_trades`, `old_null_pf`
Match count: 19

- L3 `campaign_011`:   "campaign_id": "CAMPAIGN_011",
- L4 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",
- L11 `campaign_011`:   "seed_derivation": "Frozen master_seed on strategy config; per-bar entry uses SHA-256(master_seed, instrument, bar_index) \u2014 see CAMPAIGN_011_PRECOMMIT_CHECKLIST.md \u00a75\u2013\u00a76.",
- L14 `campaign_011`:   "config_path": "configs/campaign_011_random_entry_anchor.yaml",
- L14 `random_entry_anchor`:   "config_path": "configs/campaign_011_random_entry_anchor.yaml",
- … 14 more matches

### `research/null_baselines/campaign_011_deduped_null_baseline.md`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_json_path`, `old_null_trades`, `old_null_expectancy`
Match count: 11

- L1 `campaign_011`: # CAMPAIGN_011 — Deduped Canonical Null Baseline (rollup)
- L4 `campaign_011`: > pre-fix `backtests/CAMPAIGN_011_random_entry_anchor/` metrics.
- L4 `random_entry_anchor`: > pre-fix `backtests/CAMPAIGN_011_random_entry_anchor/` metrics.
- L4 `old_null_json_path`: > pre-fix `backtests/CAMPAIGN_011_random_entry_anchor/` metrics.
- L9 `random_entry_anchor`: | strategy | `random_entry_anchor` `0.1.0-c011` |
- … 6 more matches

### `backtests/CAMPAIGN_001_REPORT.md`

Patterns: `old_null_pf`
Match count: 1

- L457 `old_null_pf`: | EUR_USD | H1 | 863 | -8.01% | -14.42% | 0.91 | -0.037 | +34.76% | 1.10 |

### `backtests/CAMPAIGN_001_REPORT.pre_pnl_fix.md`

Patterns: `old_null_pf`
Match count: 2

- L447 `old_null_pf`: | train | H4 | 630 | -14.04% | -17.35% | 0.91 | -0.072 | +33.82% |
- L457 `old_null_pf`: | EUR_USD | H1 | 863 | -8.01% | -14.42% | 0.91 | -0.037 | +34.76% | 1.10 |

### `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.md`

Patterns: `old_null_trades`
Match count: 1

- L18 `old_null_trades`: - positions: 1177

### `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_summary.json`

Patterns: `campaign_011`
Match count: 1

- L2 `campaign_011`:   "campaign_id": "CAMPAIGN_011",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_00/fold_00_AUD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_00/fold_00_EUR_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_00/fold_00_GBP_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_00/fold_00_NZD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_00/fold_00_USD_CAD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_00/fold_00_USD_CHF_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_00/fold_00_USD_JPY_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_01/fold_01_AUD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_01/fold_01_EUR_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_01/fold_01_GBP_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_01/fold_01_NZD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_01/fold_01_USD_CAD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_01/fold_01_USD_CHF_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_01/fold_01_USD_JPY_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_02/fold_02_AUD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_02/fold_02_EUR_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_02/fold_02_GBP_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_02/fold_02_NZD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_02/fold_02_USD_CAD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_02/fold_02_USD_CHF_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_02/fold_02_USD_JPY_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_03/fold_03_AUD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_03/fold_03_EUR_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_03/fold_03_GBP_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_03/fold_03_NZD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_03/fold_03_USD_CAD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_03/fold_03_USD_CHF_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_03/fold_03_USD_JPY_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_04/fold_04_AUD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_04/fold_04_EUR_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_04/fold_04_GBP_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_04/fold_04_NZD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_04/fold_04_USD_CAD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_04/fold_04_USD_CHF_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_04/fold_04_USD_JPY_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_05/fold_05_AUD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_05/fold_05_EUR_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_05/fold_05_GBP_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_05/fold_05_NZD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_05/fold_05_USD_CAD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_05/fold_05_USD_CHF_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_05/fold_05_USD_JPY_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_06/fold_06_AUD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_06/fold_06_EUR_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_06/fold_06_GBP_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_06/fold_06_NZD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_06/fold_06_USD_CAD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_06/fold_06_USD_CHF_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_06/fold_06_USD_JPY_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_07/fold_07_AUD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_07/fold_07_EUR_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_07/fold_07_GBP_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_07/fold_07_NZD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_07/fold_07_USD_CAD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_07/fold_07_USD_CHF_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_07/fold_07_USD_JPY_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.json`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 2

- L2 `campaign_011`:   "campaign_id": "CAMPAIGN_011",
- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.md`

Patterns: `campaign_011`
Match count: 1

- L1 `campaign_011`: # CAMPAIGN_011 — Portfolio-Risk Diagnostics (auto-generated)

### `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/fold_detail.json`

Patterns: `campaign_011`, `random_entry_anchor`, `old_null_trades`, `old_null_expectancy`
Match count: 6

- L2 `campaign_011`:   "campaign_id": "CAMPAIGN_011",
- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",
- L10 `campaign_011`:   "config_path": "configs/campaign_011_random_entry_anchor.yaml",
- L10 `random_entry_anchor`:   "config_path": "configs/campaign_011_random_entry_anchor.yaml",
- L1490 `old_null_trades`:     "total_trades": 1177,
- … 1 more matches

### `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json`

Patterns: `campaign_011`
Match count: 1

- L2 `campaign_011`:   "campaign_name": "CAMPAIGN_011",

### `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.md`

Patterns: `campaign_011`
Match count: 1

- L1 `campaign_011`: # Walk-Forward Plan — CAMPAIGN_011

### `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json`

Patterns: `campaign_011`, `old_null_trades`, `old_null_expectancy`
Match count: 3

- L3 `campaign_011`:     "campaign_name": "CAMPAIGN_011",
- L195 `old_null_trades`:     "total_trades_across_folds": 1177,
- L196 `old_null_expectancy`:     "aggregate_expectancy_r": -0.002439857834553023,

### `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.md`

Patterns: `campaign_011`, `old_null_trades`, `old_null_expectancy`
Match count: 3

- L1 `campaign_011`: # Walk-Forward Results — CAMPAIGN_011
- L9 `old_null_trades`: - Total trades across folds: **1177**
- L10 `old_null_expectancy`: - Aggregate expectancy R: **-0.0024**

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_00/fold_00_AUD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_00/fold_00_EUR_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_00/fold_00_GBP_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_00/fold_00_NZD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_00/fold_00_USD_CAD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_00/fold_00_USD_CHF_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_00/fold_00_USD_JPY_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_01/fold_01_AUD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_01/fold_01_EUR_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_01/fold_01_GBP_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_01/fold_01_NZD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_01/fold_01_USD_CAD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_01/fold_01_USD_CHF_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_01/fold_01_USD_JPY_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_02/fold_02_AUD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_02/fold_02_EUR_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_02/fold_02_GBP_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_02/fold_02_NZD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_02/fold_02_USD_CAD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_02/fold_02_USD_CHF_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_02/fold_02_USD_JPY_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_03/fold_03_AUD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_03/fold_03_EUR_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_03/fold_03_GBP_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_03/fold_03_NZD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_03/fold_03_USD_CAD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_03/fold_03_USD_CHF_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_03/fold_03_USD_JPY_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_04/fold_04_AUD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_04/fold_04_EUR_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_04/fold_04_GBP_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_04/fold_04_NZD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_04/fold_04_USD_CAD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_04/fold_04_USD_CHF_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_04/fold_04_USD_JPY_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_05/fold_05_AUD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_05/fold_05_EUR_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_05/fold_05_GBP_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_05/fold_05_NZD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_05/fold_05_USD_CAD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_05/fold_05_USD_CHF_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_05/fold_05_USD_JPY_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_06/fold_06_AUD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_06/fold_06_EUR_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_06/fold_06_GBP_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_06/fold_06_NZD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_06/fold_06_USD_CAD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_06/fold_06_USD_CHF_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_06/fold_06_USD_JPY_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_07/fold_07_AUD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_07/fold_07_EUR_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_07/fold_07_GBP_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_07/fold_07_NZD_USD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_07/fold_07_USD_CAD_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_07/fold_07_USD_CHF_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_07/fold_07_USD_JPY_summary.json`

Patterns: `random_entry_anchor`
Match count: 1

- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/walk_forward/fold_detail.json`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 4

- L2 `campaign_011`:   "campaign_id": "CAMPAIGN_011",
- L3 `random_entry_anchor`:   "strategy_name": "random_entry_anchor",
- L10 `campaign_011`:   "config_path": "configs/campaign_011_random_entry_anchor.yaml",
- L10 `random_entry_anchor`:   "config_path": "configs/campaign_011_random_entry_anchor.yaml",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/walk_forward/results.json`

Patterns: `campaign_011`
Match count: 1

- L3 `campaign_011`:     "campaign_name": "CAMPAIGN_011",

### `backtests/CAMPAIGN_011_random_entry_anchor_deduped/walk_forward/results.md`

Patterns: `campaign_011`
Match count: 1

- L1 `campaign_011`: # Walk-Forward Results — CAMPAIGN_011

### `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/financing/financing_summary.json`

Patterns: `campaign_012`
Match count: 1

- L2 `campaign_012`:   "campaign_id": "CAMPAIGN_012",

### `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/risk/diagnostics.json`

Patterns: `campaign_012`
Match count: 1

- L2 `campaign_012`:   "campaign_id": "CAMPAIGN_012",

### `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/risk/diagnostics.md`

Patterns: `campaign_012`
Match count: 2

- L1 `campaign_012`: # CAMPAIGN_012 — Portfolio-Risk Diagnostics (auto-generated)
- L3 `campaign_012`: > Diagnostic only — does not gate the verdict. CAMPAIGN_012 is

### `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/fold_detail.json`

Patterns: `campaign_012`
Match count: 2

- L2 `campaign_012`:   "campaign_id": "CAMPAIGN_012",
- L9 `campaign_012`:   "config_path": "configs/campaign_012_regime_switcher_atr_percentile.yaml",

### `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/plan.json`

Patterns: `campaign_012`
Match count: 1

- L2 `campaign_012`:   "campaign_name": "CAMPAIGN_012_regime_switcher_atr_percentile",

### `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/plan.md`

Patterns: `campaign_012`
Match count: 1

- L1 `campaign_012`: # Walk-Forward Plan — CAMPAIGN_012_regime_switcher_atr_percentile

### `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/results.json`

Patterns: `campaign_012`
Match count: 1

- L3 `campaign_012`:     "campaign_name": "CAMPAIGN_012_regime_switcher_atr_percentile",

### `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/results.md`

Patterns: `campaign_012`
Match count: 1

- L1 `campaign_012`: # Walk-Forward Results — CAMPAIGN_012_regime_switcher_atr_percentile

### `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/financing/financing_summary.json`

Patterns: `campaign_013`
Match count: 1

- L2 `campaign_013`:   "campaign_id": "CAMPAIGN_013",

### `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/risk/diagnostics.json`

Patterns: `campaign_013`
Match count: 2

- L2 `campaign_013`:   "campaign_id": "CAMPAIGN_013",
- L13 `campaign_013`:     "note": "BacktestEngine is single-instrument single-position-at-a-time. The CAMPAIGN_013 runner invokes one engine PER PAIR PER FOLD; MAX_OPEN_POSITIONS_EXCEEDED therefore fires 0 times because the cap is not portfolio-wide across the 7

### `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/risk/diagnostics.md`

Patterns: `campaign_013`
Match count: 3

- L1 `campaign_013`: # CAMPAIGN_013 — Portfolio-Risk Diagnostics (auto-generated)
- L3 `campaign_013`: > Diagnostic only — does not gate the verdict. CAMPAIGN_013 is
- L61 `campaign_013`: - The CAMPAIGN_013 runner invokes one engine PER PAIR PER FOLD; `MAX_OPEN_POSITIONS_EXCEEDED` rejections observed: 0.

### `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/fold_detail.json`

Patterns: `campaign_013`
Match count: 2

- L2 `campaign_013`:   "campaign_id": "CAMPAIGN_013",
- L9 `campaign_013`:   "config_path": "configs/campaign_013_cross_pair_currency_strength_rotation.yaml",

### `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/plan.json`

Patterns: `campaign_013`
Match count: 1

- L2 `campaign_013`:   "campaign_name": "CAMPAIGN_013_cross_pair_currency_strength_rotation",

### `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/plan.md`

Patterns: `campaign_013`
Match count: 1

- L1 `campaign_013`: # Walk-Forward Plan — CAMPAIGN_013_cross_pair_currency_strength_rotation

### `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/results.json`

Patterns: `campaign_013`
Match count: 1

- L3 `campaign_013`:     "campaign_name": "CAMPAIGN_013_cross_pair_currency_strength_rotation",

### `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/results.md`

Patterns: `campaign_013`
Match count: 1

- L1 `campaign_013`: # Walk-Forward Results — CAMPAIGN_013_cross_pair_currency_strength_rotation

### `backtests/CAMPAIGN_014_calendar_event_window_anomaly/financing/financing_summary.json`

Patterns: `campaign_014`
Match count: 1

- L2 `campaign_014`:   "campaign_id": "CAMPAIGN_014",

### `backtests/CAMPAIGN_014_calendar_event_window_anomaly/risk/diagnostics.json`

Patterns: `campaign_014`
Match count: 2

- L2 `campaign_014`:   "campaign_id": "CAMPAIGN_014",
- L13 `campaign_014`:     "note": "BacktestEngine is single-instrument single-position-at-a-time. The CAMPAIGN_014 runner invokes one engine PER PAIR PER FOLD; MAX_OPEN_POSITIONS_EXCEEDED therefore fires 0 times because the cap is not portfolio-wide. NFP/FOMC ev

### `backtests/CAMPAIGN_014_calendar_event_window_anomaly/risk/diagnostics.md`

Patterns: `campaign_014`
Match count: 4

- L1 `campaign_014`: # CAMPAIGN_014 — Portfolio-Risk Diagnostics (auto-generated)
- L3 `campaign_014`: > Diagnostic only — does not gate the verdict. CAMPAIGN_014 is
- L52 `campaign_014`: - The CAMPAIGN_014 runner invokes one engine PER PAIR PER FOLD; `MAX_OPEN_POSITIONS_EXCEEDED` rejections observed: 0.
- L56 `campaign_014`: ## CAMPAIGN_014 calendar-event-window-specific

### `backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/fold_detail.json`

Patterns: `campaign_014`
Match count: 4

- L2 `campaign_014`:   "campaign_id": "CAMPAIGN_014",
- L9 `campaign_014`:   "config_path": "configs/campaign_014_calendar_event_window_anomaly.yaml",
- L35 `campaign_014`:     "path": "research/calendar/fixtures/campaign_014_events.json",
- L36 `campaign_014`:     "schema_version": "campaign_014.event_fixture.v1",

### `backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/plan.json`

Patterns: `campaign_014`
Match count: 3

- L2 `campaign_014`:   "campaign_name": "CAMPAIGN_014_calendar_event_window_anomaly",
- L84 `campaign_014`:     "Event fixture: research/calendar/fixtures/campaign_014_events.json (281 events; 2020-01-01 \u2192 2026-05-20 coverage).",
- L85 `campaign_014`:     "Fixture date-verification audit: PARTIAL \u2014 PROCEED WITH EXPLICIT CAVEAT (see CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md).",

### `backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/plan.md`

Patterns: `campaign_014`
Match count: 3

- L1 `campaign_014`: # Walk-Forward Plan — CAMPAIGN_014_calendar_event_window_anomaly
- L14 `campaign_014`: - Event fixture: research/calendar/fixtures/campaign_014_events.json (281 events; 2020-01-01 → 2026-05-20 coverage).
- L15 `campaign_014`: - Fixture date-verification audit: PARTIAL — PROCEED WITH EXPLICIT CAVEAT (see CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md).

### `backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/results.json`

Patterns: `campaign_014`
Match count: 3

- L3 `campaign_014`:     "campaign_name": "CAMPAIGN_014_calendar_event_window_anomaly",
- L85 `campaign_014`:       "Event fixture: research/calendar/fixtures/campaign_014_events.json (281 events; 2020-01-01 \u2192 2026-05-20 coverage).",
- L86 `campaign_014`:       "Fixture date-verification audit: PARTIAL \u2014 PROCEED WITH EXPLICIT CAVEAT (see CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md).",

### `backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/results.md`

Patterns: `campaign_014`
Match count: 1

- L1 `campaign_014`: # Walk-Forward Results — CAMPAIGN_014_calendar_event_window_anomaly

### `backtests/campaign_001/runs/_index.json`

Patterns: `old_null_expectancy`
Match count: 1

- L4386 `old_null_expectancy`:         "sortino": -0.0024959526354320772,

### `backtests/campaign_001/runs/baseline/H1/full/baseline_EUR_USD_H1_full_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs/baseline/H1/train/baseline_AUD_USD_H1_train_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs/cost_stress/base/H1/cost_base_EUR_USD_H1_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs/robustness/03517110/grid_03517110_EUR_USD_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs/robustness/037204b4/grid_037204b4_NZD_USD_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs/robustness/12efd448/grid_12efd448_EUR_USD_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs/robustness/165331ed/grid_165331ed_USD_JPY_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs/robustness/1d3313b1/grid_1d3313b1_USD_CHF_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L14 `old_null_pf`: - Sharpe: **-0.91**, Sortino: **-1.32**

### `backtests/campaign_001/runs/robustness/70f034aa/grid_70f034aa_AUD_USD_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs/robustness/959b274a/grid_959b274a_USD_CHF_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L14 `old_null_pf`: - Sharpe: **-0.91**, Sortino: **-1.11**

### `backtests/campaign_001/runs/robustness/9baa12b9/grid_9baa12b9_GBP_USD_H4_metrics.json`

Patterns: `old_null_expectancy`
Match count: 1

- L18 `old_null_expectancy`:     "sortino": -0.0024959526354320772,

### `backtests/campaign_001/runs/robustness/9baa12b9/grid_9baa12b9_GBP_USD_H4_summary.json`

Patterns: `old_null_expectancy`
Match count: 1

- L18 `old_null_expectancy`:     "sortino": -0.0024959526354320772,

### `backtests/campaign_001/runs/robustness/a2b6993d/grid_a2b6993d_NZD_USD_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs/robustness/ea6b219e/grid_ea6b219e_USD_CAD_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L11 `old_null_pf`: - Total return: **0.91%**

### `backtests/campaign_001/runs.pre_pnl_fix/_index.json`

Patterns: `old_null_expectancy`
Match count: 1

- L368 `old_null_expectancy`:         "sortino": -0.0024959526354320772,

### `backtests/campaign_001/runs.pre_pnl_fix/baseline/H1/full/baseline_EUR_USD_H1_full_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs.pre_pnl_fix/baseline/H1/train/baseline_AUD_USD_H1_train_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs.pre_pnl_fix/baseline/H4/full/baseline_USD_JPY_H4_full_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L12 `old_null_pf`: - Final equity: **0.91** (start 500.00)

### `backtests/campaign_001/runs.pre_pnl_fix/baseline/H4/train/baseline_USD_JPY_H4_train_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L12 `old_null_pf`: - Final equity: **0.91** (start 500.00)

### `backtests/campaign_001/runs.pre_pnl_fix/cost_stress/base/H1/cost_base_EUR_USD_H1_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs.pre_pnl_fix/cost_stress/base/H4/cost_base_USD_JPY_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L12 `old_null_pf`: - Final equity: **0.91** (start 500.00)

### `backtests/campaign_001/runs.pre_pnl_fix/robustness/03517110/grid_03517110_EUR_USD_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs.pre_pnl_fix/robustness/037204b4/grid_037204b4_NZD_USD_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs.pre_pnl_fix/robustness/12efd448/grid_12efd448_EUR_USD_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs.pre_pnl_fix/robustness/362a93bb/grid_362a93bb_USD_CHF_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L14 `old_null_pf`: - Sharpe: **-0.91**, Sortino: **-1.06**

### `backtests/campaign_001/runs.pre_pnl_fix/robustness/70f034aa/grid_70f034aa_AUD_USD_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs.pre_pnl_fix/robustness/70f034aa/grid_70f034aa_USD_CHF_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L14 `old_null_pf`: - Sharpe: **-0.85**, Sortino: **-0.91**

### `backtests/campaign_001/runs.pre_pnl_fix/robustness/922ec954/grid_922ec954_USD_CHF_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L14 `old_null_pf`: - Sharpe: **-0.91**, Sortino: **-1.06**

### `backtests/campaign_001/runs.pre_pnl_fix/robustness/9baa12b9/grid_9baa12b9_GBP_USD_H4_metrics.json`

Patterns: `old_null_expectancy`
Match count: 1

- L18 `old_null_expectancy`:     "sortino": -0.0024959526354320772,

### `backtests/campaign_001/runs.pre_pnl_fix/robustness/9baa12b9/grid_9baa12b9_GBP_USD_H4_summary.json`

Patterns: `old_null_expectancy`
Match count: 1

- L18 `old_null_expectancy`:     "sortino": -0.0024959526354320772,

### `backtests/campaign_001/runs.pre_pnl_fix/robustness/9c584299/grid_9c584299_USD_CHF_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L14 `old_null_pf`: - Sharpe: **-0.91**, Sortino: **-1.13**

### `backtests/campaign_001/runs.pre_pnl_fix/robustness/a2b6993d/grid_a2b6993d_NZD_USD_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_001/runs.pre_pnl_fix/robustness/e227b239/grid_e227b239_USD_CAD_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L14 `old_null_pf`: - Sharpe: **-0.70**, Sortino: **-0.91**

### `backtests/campaign_001/runs.pre_pnl_fix/robustness/f5eebd09/grid_f5eebd09_USD_JPY_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L12 `old_null_pf`: - Final equity: **0.91** (start 500.00)

### `backtests/campaign_001/runs.pre_pnl_fix/robustness/ff0bdbb2/grid_ff0bdbb2_USD_JPY_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L12 `old_null_pf`: - Final equity: **0.91** (start 500.00)

### `backtests/campaign_002_real_oanda/runs/_index.json`

Patterns: `old_null_expectancy`
Match count: 11

- L2348 `old_null_expectancy`:         "median_r": -0.002478905285416339,
- L2987 `old_null_expectancy`:         "median_r": -0.002478905285416339,
- L3627 `old_null_expectancy`:         "median_r": -0.002406451050734812,
- L5227 `old_null_expectancy`:         "median_r": -0.0024577437445564955,
- L8737 `old_null_expectancy`:         "median_r": -0.002489068564724664,
- … 6 more matches

### `backtests/campaign_002_real_oanda/runs/baseline/H1/full/baseline_USD_JPY_H1_full_metrics.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.002478905285416339,

### `backtests/campaign_002_real_oanda/runs/baseline/H1/full/baseline_USD_JPY_H1_full_summary.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.002478905285416339,

### `backtests/campaign_002_real_oanda/runs/baseline/H1/test_untouched/baseline_GBP_USD_H1_test_untouched_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L14 `old_null_pf`: - Sharpe: **-0.91**, Sortino: **-0.90**

### `backtests/campaign_002_real_oanda/runs/cost_stress/base/H1/cost_base_USD_JPY_H1_metrics.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.002478905285416339,

### `backtests/campaign_002_real_oanda/runs/cost_stress/base/H1/cost_base_USD_JPY_H1_summary.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.002478905285416339,

### `backtests/campaign_002_real_oanda/runs/cost_stress/stress_15x/H1/cost_stress_15x_USD_JPY_H1_metrics.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.002406451050734812,

### `backtests/campaign_002_real_oanda/runs/cost_stress/stress_15x/H1/cost_stress_15x_USD_JPY_H1_summary.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.002406451050734812,

### `backtests/campaign_002_real_oanda/runs/robustness/03517110/grid_03517110_EUR_USD_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L14 `old_null_pf`: - Sharpe: **-1.23**, Sortino: **-0.91**

### `backtests/campaign_002_real_oanda/runs/robustness/03517110/grid_03517110_GBP_USD_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_002_real_oanda/runs/robustness/03517110/grid_03517110_USD_JPY_H4_metrics.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.0024282682926604886,

### `backtests/campaign_002_real_oanda/runs/robustness/03517110/grid_03517110_USD_JPY_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L11 `old_null_pf`: - Total return: **0.91%**

### `backtests/campaign_002_real_oanda/runs/robustness/03517110/grid_03517110_USD_JPY_H4_summary.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.0024282682926604886,

### `backtests/campaign_002_real_oanda/runs/robustness/0421ccd9/grid_0421ccd9_USD_CAD_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L14 `old_null_pf`: - Sharpe: **-0.91**, Sortino: **-0.70**

### `backtests/campaign_002_real_oanda/runs/robustness/0421ccd9/grid_0421ccd9_USD_JPY_H4_metrics.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.0024282682926604886,

### `backtests/campaign_002_real_oanda/runs/robustness/0421ccd9/grid_0421ccd9_USD_JPY_H4_summary.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.0024282682926604886,

### `backtests/campaign_002_real_oanda/runs/robustness/17b5d3b1/grid_17b5d3b1_USD_JPY_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L14 `old_null_pf`: - Sharpe: **-0.91**, Sortino: **-0.78**

### `backtests/campaign_002_real_oanda/runs/robustness/199a15f7/grid_199a15f7_USD_JPY_H4_metrics.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.0024908371412332305,

### `backtests/campaign_002_real_oanda/runs/robustness/199a15f7/grid_199a15f7_USD_JPY_H4_summary.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.0024908371412332305,

### `backtests/campaign_002_real_oanda/runs/robustness/3628a3f9/grid_3628a3f9_USD_JPY_H4_metrics.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.002489068564724664,

### `backtests/campaign_002_real_oanda/runs/robustness/3628a3f9/grid_3628a3f9_USD_JPY_H4_summary.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.002489068564724664,

### `backtests/campaign_002_real_oanda/runs/robustness/362a93bb/grid_362a93bb_USD_JPY_H4_metrics.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.0024577437445564955,

### `backtests/campaign_002_real_oanda/runs/robustness/362a93bb/grid_362a93bb_USD_JPY_H4_summary.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.0024577437445564955,

### `backtests/campaign_002_real_oanda/runs/robustness/805609ad/grid_805609ad_USD_JPY_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L15 `old_null_pf`: - Profit factor: **0.91**

### `backtests/campaign_002_real_oanda/runs/robustness/9c29a336/grid_9c29a336_USD_JPY_H4_metrics.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.0024432126253640524,

### `backtests/campaign_002_real_oanda/runs/robustness/9c29a336/grid_9c29a336_USD_JPY_H4_summary.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.0024432126253640524,

### `backtests/campaign_002_real_oanda/runs/robustness/a2b6993d/grid_a2b6993d_USD_CHF_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L14 `old_null_pf`: - Sharpe: **-0.91**, Sortino: **-0.81**

### `backtests/campaign_002_real_oanda/runs/robustness/ac11d37c/grid_ac11d37c_USD_JPY_H4_metrics.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.002487219196452503,

### `backtests/campaign_002_real_oanda/runs/robustness/ac11d37c/grid_ac11d37c_USD_JPY_H4_summary.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.002487219196452503,

### `backtests/campaign_002_real_oanda/runs/robustness/ff64082d/grid_ff64082d_USD_JPY_H4_metrics.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.002413200306092042,

### `backtests/campaign_002_real_oanda/runs/robustness/ff64082d/grid_ff64082d_USD_JPY_H4_summary.json`

Patterns: `old_null_expectancy`
Match count: 1

- L22 `old_null_expectancy`:     "median_r": -0.002413200306092042,

### `backtests/campaign_003_controlled_adx/runs/baseline/validation/baseline_GBP_USD_H4_validation_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L11 `old_null_pf`: - Total return: **-0.91%**

### `backtests/campaign_003_controlled_adx/runs/cost_stress/stress_15x/cost_stress_15x_AUD_USD_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L14 `old_null_pf`: - Sharpe: **-0.91**, Sortino: **-0.63**

### `backtests/campaign_009_mean_reversion/runs/train/stress_2x/train_stress_2x_USD_CHF_H4_metrics.md`

Patterns: `old_null_pf`
Match count: 1

- L14 `old_null_pf`: - Sharpe: **-0.91**, Sortino: **-12.48**

### `backtests/diagnostics/backtrader_campaign_011_full_window_004_postfix/comparison_summary.json`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 4

- L2 `campaign_011`:   "backtrader_summary_path": "research/backtrader_lane/results/campaign_011_full_window_004_postfix/backtrader_summary.json",
- L3 `campaign_011`:   "bespoke_reference_path": "research/lean_parity/campaign_011_h4_bespoke_reference.json",
- L7 `campaign_011`:   "campaign_id": "CAMPAIGN_011",
- L147 `random_entry_anchor`:   "strategy_id": "random_entry_anchor",

### `backtests/diagnostics/backtrader_campaign_011_full_window_004_postfix/comparison_summary.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`, `random_entry_anchor`
Match count: 8

- L1 `campaign_011`: # Backtrader Parity Comparison — `CAMPAIGN_011`
- L3 `campaign_011`: > `strategy_evidence: false`. Verification infrastructure. Does **not** approve any strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains scaffold-only.
- L3 `campaign_012`: > `strategy_evidence: false`. Verification infrastructure. Does **not** approve any strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains scaffold-only.
- L3 `campaign_013`: > `strategy_evidence: false`. Verification infrastructure. Does **not** approve any strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains scaffold-only.
- L3 `campaign_014`: > `strategy_evidence: false`. Verification infrastructure. Does **not** approve any strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains scaffold-only.
- … 3 more matches

### `backtests/diagnostics/backtrader_campaign_011_full_window_004_prefix/comparison_summary.json`

Patterns: `campaign_011`, `old_null_expectancy`, `random_entry_anchor`
Match count: 5

- L2 `campaign_011`:   "backtrader_summary_path": "research/backtrader_lane/results/campaign_011_full_window_004/backtrader_summary.json",
- L3 `campaign_011`:   "bespoke_reference_path": "research/lean_parity/campaign_011_h4_bespoke_reference.json",
- L7 `campaign_011`:   "campaign_id": "CAMPAIGN_011",
- L105 `old_null_expectancy`:       "win_rate_delta": -0.0024030303030302957
- L147 `random_entry_anchor`:   "strategy_id": "random_entry_anchor",

### `backtests/diagnostics/backtrader_campaign_011_full_window_004_prefix/comparison_summary.md`

Patterns: `campaign_011`, `campaign_012`, `campaign_013`, `campaign_014`, `random_entry_anchor`
Match count: 8

- L1 `campaign_011`: # Backtrader Parity Comparison — `CAMPAIGN_011`
- L3 `campaign_011`: > `strategy_evidence: false`. Verification infrastructure. Does **not** approve any strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains scaffold-only.
- L3 `campaign_012`: > `strategy_evidence: false`. Verification infrastructure. Does **not** approve any strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains scaffold-only.
- L3 `campaign_013`: > `strategy_evidence: false`. Verification infrastructure. Does **not** approve any strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains scaffold-only.
- L3 `campaign_014`: > `strategy_evidence: false`. Verification infrastructure. Does **not** approve any strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014 remains scaffold-only.
- … 3 more matches

### `backtests/diagnostics/custom_campaign_011_h4_parity_norisk.md`

Patterns: `campaign_011`, `random_entry_anchor`
Match count: 8

- L1 `campaign_011`: # Custom-engine CAMPAIGN_011 H4 parity reproduction (no-RiskEngine)
- L5 `campaign_011`: > **DIAGNOSTIC / PARITY REPRODUCTION — NOT A NEW VERDICT.** This runs `random_entry_anchor 0.1.0-c011` (CAMPAIGN_011) on the bespoke engine with `risk_engine=None` so the future Backtrader CAMPAIGN_011 comparison sprint has a canonical, no-
- L5 `random_entry_anchor`: > **DIAGNOSTIC / PARITY REPRODUCTION — NOT A NEW VERDICT.** This runs `random_entry_anchor 0.1.0-c011` (CAMPAIGN_011) on the bespoke engine with `risk_engine=None` so the future Backtrader CAMPAIGN_011 comparison sprint has a canonical, no-
- L11 `random_entry_anchor`: | strategy | `random_entry_anchor 0.1.0-c011` |
- L36 `campaign_011`: - A reproducible, hash-pinned no-RiskEngine bespoke reference for CAMPAIGN_011 / `random_entry_anchor`, suitable for the future Backtrader CAMPAIGN_011 comparison sprint.
- … 3 more matches

### `docs/research/EVIDENCE_INDEX.md`

Patterns: `campaign_012`, `campaign_011`, `random_entry_anchor`, `canonical_null_json`, `campaign_013`, `campaign_014`, `old_null_expectancy`, `old_null_pf`, `old_null_return`, `old_null_trades`, `above_null_claim`
Match count: 225

- L23 `campaign_012`: | [`POST_DEDUP_NULL_REFERENCE_REFRESH_001_SUMMARY.md`](POST_DEDUP_NULL_REFERENCE_REFRESH_001_SUMMARY.md) | CAMPAIGN_012–014 null-reference refresh close-out |
- L45 `campaign_011`: | 011 | [`docs/research/CAMPAIGN_011_DEDUPED_NULL_BASELINE.md`](CAMPAIGN_011_DEDUPED_NULL_BASELINE.md) | **REJECT** (null anchor) | random_entry_anchor deduped canonical: exp_r −0.0029, 1180 trades · [`campaign_011_deduped_null_baseline.jso
- L45 `random_entry_anchor`: | 011 | [`docs/research/CAMPAIGN_011_DEDUPED_NULL_BASELINE.md`](CAMPAIGN_011_DEDUPED_NULL_BASELINE.md) | **REJECT** (null anchor) | random_entry_anchor deduped canonical: exp_r −0.0029, 1180 trades · [`campaign_011_deduped_null_baseline.jso
- L45 `canonical_null_json`: | 011 | [`docs/research/CAMPAIGN_011_DEDUPED_NULL_BASELINE.md`](CAMPAIGN_011_DEDUPED_NULL_BASELINE.md) | **REJECT** (null anchor) | random_entry_anchor deduped canonical: exp_r −0.0029, 1180 trades · [`campaign_011_deduped_null_baseline.jso
- L46 `campaign_012`: | 012 | [`docs/research/CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md) | **REJECT** | regime_switcher: exp_r −0.0521 · **LIKELY_CONTAMINATED** metrics; null gap refreshed vs deduped null (−0.0029 R) —
- … 220 more matches

### `docs/research/EVIDENCE_MANIFEST.json`

Patterns: `campaign_011`, `random_entry_anchor`, `campaign_012`, `campaign_013`, `campaign_014`, `canonical_null_json`, `old_null_json_path`, `old_null_expectancy`, `old_null_trades`, `superseded_null_reference`
Match count: 105

- L3 `campaign_011`:   "description": "Machine-readable index of all research evidence: fifteen campaigns (CAMPAIGN_001-009 plus CAMPAIGN_010 session_breakout, CAMPAIGN_011 random_entry_anchor null-model, CAMPAIGN_012 regime_switcher_atr_percentile, CAMPAIGN_01
- L3 `random_entry_anchor`:   "description": "Machine-readable index of all research evidence: fifteen campaigns (CAMPAIGN_001-009 plus CAMPAIGN_010 session_breakout, CAMPAIGN_011 random_entry_anchor null-model, CAMPAIGN_012 regime_switcher_atr_percentile, CAMPAIGN_01
- L3 `campaign_012`:   "description": "Machine-readable index of all research evidence: fifteen campaigns (CAMPAIGN_001-009 plus CAMPAIGN_010 session_breakout, CAMPAIGN_011 random_entry_anchor null-model, CAMPAIGN_012 regime_switcher_atr_percentile, CAMPAIGN_01
- L3 `campaign_013`:   "description": "Machine-readable index of all research evidence: fifteen campaigns (CAMPAIGN_001-009 plus CAMPAIGN_010 session_breakout, CAMPAIGN_011 random_entry_anchor null-model, CAMPAIGN_012 regime_switcher_atr_percentile, CAMPAIGN_01
- L3 `campaign_014`:   "description": "Machine-readable index of all research evidence: fifteen campaigns (CAMPAIGN_001-009 plus CAMPAIGN_010 session_breakout, CAMPAIGN_011 random_entry_anchor null-model, CAMPAIGN_012 regime_switcher_atr_percentile, CAMPAIGN_01
- … 100 more matches
