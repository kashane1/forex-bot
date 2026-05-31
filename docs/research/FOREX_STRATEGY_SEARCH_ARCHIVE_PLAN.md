# Forex Strategy-Search Programme — Archive Plan (Phase 0)

**Sprint:** `research-forex-strategy-search-archive-001`
**Type:** Documentation and archival only. No code, no data, no factor work.
**Date:** 2026-05-31
**Branch:** `research-forex-strategy-search-archive-001`
**Freeze:** intact. Paper/demo/live remain blocked.

---

## 1. Purpose

This sprint formally archives the forex strategy-search programme after its
pre-registered terminal decision. The FX Futures Carry Diagnostic sprint
(`research-fx-futures-carry-diagnostic-001`) returned
**`CARRY_DOES_NOT_SURVIVE_IN_FUTURES`**, triggering Option E (archive) from the
programme-direction decision. This plan defines the audit scope, deliverables,
and compliance guardrails for the closeout sprint.

---

## 2. Terminal decision chain (evidence audit)

The archive rests on a complete, auditable chain:

| Step | Sprint | Verdict / outcome | Key artifact |
|------|--------|-------------------|--------------|
| 1 | Cross-factor programme synthesis | Cost is the dominant failure mode; S4 is the only genuine factor (sub-cost) | `COMPLETE_PROGRAMME_EVIDENCE_INVENTORY.md` |
| 2 | Carry factor validation | Carry premium exists gross but is financing-defeated and spot-predictive leg is null | `CARRY_FACTOR_VERDICT.md` |
| 3 | Programme direction after carry | Option C (futures pivot) chosen over immediate archive; futures is the last cheap, high-information experiment | `FINAL_PROGRAMME_DIRECTION_DECISION.md` |
| 4 | FX futures venue design | Carry feasible on free EOD; C1 data-gated; S4 excluded (venue-independent) | `FX_FUTURES_VIABILITY_DECISION.md` |
| 5 | FX futures carry diagnostic | **`CARRY_DOES_NOT_SURVIVE_IN_FUTURES`** — carry non-predictive even with financing wall removed | `FX_FUTURES_CARRY_VERDICT.md` |
| 6 | Programme implication | Archive triggered; idea-quality / market-efficiency is the binding limit | `FX_FUTURES_CARRY_PROGRAMME_IMPLICATION.md` |

**Conclusion from audit:** every shortlisted mechanism has a terminal verdict. The
one venue change that could have rescued a real-but-cost-defeated effect (futures,
removing the nightly financing wall) was executed on the strongest candidate
(carry) and found non-predictive. No remaining mechanism both (a) is reachable
with available data and (b) attacks the binding constraint.

---

## 3. Programme scope reviewed

### 3a. Strategy campaigns (C001–C031)

Numbered campaigns from trend-following baseline through vol-managed TSMOM.
**Zero approved strategies.** Terminal outcomes split between rejected (no edge),
cost-defeated (gross effect smaller than spread), and financing-defeated (C031).

Primary registries: `STRATEGY_STATUS.md`, `EVIDENCE_INDEX.md`,
`EVIDENCE_MANIFEST.json`, `configs/approved_strategies.yaml` (empty).

### 3b. Factor discovery & validation (C1, S1–S5, carry)

- **C1** — genuine on USD majors; **failed cross replication** (USD-regime artifact).
- **S2** — currency strength: real descriptor, **non-predictive**.
- **S3** — ranking on S2: **pre-falsified**.
- **S4** — triangular relative-value: **real but economically insignificant** (~10× inside cost band).
- **S5** — regime overlay: **moot** (no surviving generator).
- **Carry** — real-but-weak on spot; **non-predictive in futures**.

### 3c. Front gates & cheap screens

Edge-discovery front gate (12 families → 1 borderline survivor → C027 REJECT),
C1 high-vol front gate (FAIL), H16 overshoot-exhaustion (FAIL), H03 thin-move
(FAIL), C028 RV screen (LIKELY_SELECTION_NOISE), C031 TSMOM screen
(COST_FINANCING_DEFEATED + WITHIN_NULL).

### 3d. Venue studies

- **Spot OANDA majors + crosses** — primary corpus; ~6.4y M1/H4 history; structural cost wall.
- **Non-time-bar lane** (range/volatility bars) — infrastructure retained; directional search retired.
- **FX futures (CME)** — additive data layer built; carry diagnostic completed; verdict negative.

### 3e. Replication studies

- C1 cross replication (S1) — **failed replication**.
- Deduped reruns (C008/C009 forensic, C011 null baseline, C015 deduped) — integrity confirmed; verdicts unchanged.
- FX futures carry — **replication of spot carry predictive leg under financing-free venue** → null.

### 3f. Infrastructure (preserved, not archived away)

Edge-discovery lab + null/cost gates, walk-forward harness, Backtrader parity lane,
cross ingestion + cost models, carry/rate data (FRED), non-time-bar builders,
FX futures registry + ingest, research freeze gates (`check_research_freeze.py`,
`validate_research_archive.py`).

---

## 4. Sprint deliverables (phases 1–6)

| Phase | Artifact | Purpose |
|-------|----------|---------|
| 1 | `FOREX_STRATEGY_SEARCH_FINAL_EVIDENCE_INVENTORY.md` | Complete classified ledger |
| 2 | `FOREX_STRATEGY_SEARCH_FINAL_LESSONS.md` | Durable lessons + failure taxonomy |
| 3 | `FOREX_STRATEGY_SEARCH_ARCHIVE_DECISION.md` | Formal archive decision + reopen criteria |
| 4 | `FOREX_RESEARCH_FUTURE_OPPORTUNITIES.md` | Non-active future directions |
| 5 | `FOREX_STRATEGY_SEARCH_FINAL_SUMMARY.md` | Executive summary of entire programme |
| 6 | Validation + `FOREX_STRATEGY_SEARCH_ARCHIVE_001_SUMMARY.md` | Gate checks + sprint closeout |

---

## 5. Hard rules (binding)

- Do **not** create CAMPAIGN_032 or any campaign.
- Do **not** perform factor discovery, factor validation, or front-gate screening.
- Do **not** build trading logic or approve any strategy.
- Do **not** enable paper/demo/live.
- Do **not** revive rejected ideas or reopen archived lanes.
- Documentation only — no code changes unless validation scripts require fixes (expected: none).

---

## 6. Success criteria

1. Complete, evidence-based research record for the entire programme.
2. Every major effort classified with a terminal verdict.
3. Archive decision documented with explicit reopen conditions.
4. Research freeze intact; `configs/approved_strategies.yaml` remains empty.
5. All validation gates pass (pytest, ruff, freeze check, archive validation, secrets scan).

---

## 7. Source documents (read-first for phases 1–5)

1. `FX_FUTURES_CARRY_VERDICT.md` — terminal trigger.
2. `FINAL_FOREX_PROGRAMME_EVIDENCE_INVENTORY.md` — prior inventory (superseded by Phase 1).
3. `COMPLETE_PROGRAMME_EVIDENCE_INVENTORY.md` — cross-factor synthesis ledger.
4. `FX_FUTURES_CARRY_PROGRAMME_IMPLICATION.md` — archive rationale.
5. `FOREX_BOT_RESEARCH_LESSONS_LEARNED_001.md` — prior lessons (superseded by Phase 2).
6. `DO_NOT_REPEAT_LIST.md` — closed lanes and anti-patterns.
7. `STRATEGY_RESEARCH_RESTART_CRITERIA.md` — prior restart gates (incorporated into Phase 3).
