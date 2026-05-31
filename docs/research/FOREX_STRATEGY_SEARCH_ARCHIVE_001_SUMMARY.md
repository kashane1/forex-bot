# Forex Strategy-Search Archive 001 — SUMMARY (Phase 6)

**Sprint:** `research-forex-strategy-search-archive-001`
**Type:** Documentation-only archive closeout. Zero code changes.
**Status:** COMPLETE.
**Date:** 2026-05-31
**Programme status:** **`ARCHIVED_STRATEGY_SEARCH`**
**Freeze:** intact. Paper/demo/live remain blocked.

---

## What this sprint did

Formally archived the forex strategy-search programme after the FX Futures Carry
Diagnostic returned **`CARRY_DOES_NOT_SURVIVE_IN_FUTURES`**. Produced a complete
evidence-based closeout package: audit plan, final evidence inventory, lessons
learned, archive decision, future opportunities catalog, and executive summary.
No strategy, campaign, factor screen, front gate, or trading logic was created.

---

## Commit hashes by phase

| Phase | Hash | Artifact |
|-------|------|----------|
| 0 — archive audit plan | `c4e0978` | `FOREX_STRATEGY_SEARCH_ARCHIVE_PLAN.md` |
| 1 — final evidence inventory | `bd67da1` | `FOREX_STRATEGY_SEARCH_FINAL_EVIDENCE_INVENTORY.md` |
| 2 — final lessons learned | `b036c80` | `FOREX_STRATEGY_SEARCH_FINAL_LESSONS.md` |
| 3 — archive decision | `deb35dd` | `FOREX_STRATEGY_SEARCH_ARCHIVE_DECISION.md` |
| 4 — future opportunities | `8d5e7bf` | `FOREX_RESEARCH_FUTURE_OPPORTUNITIES.md` |
| 5 — executive summary | `4f0ef29` | `FOREX_STRATEGY_SEARCH_FINAL_SUMMARY.md` |
| 6 — validation + summary | *(this commit)* | `FOREX_STRATEGY_SEARCH_ARCHIVE_001_SUMMARY.md` |

---

## Final evidence inventory (summary)

Every major effort classified. **Zero approved strategies across 31 campaigns.**

| Classification | Representative efforts |
|----------------|------------------------|
| **rejected** | C001–C023 families, C025, C027, C028, S2, S3, H16, H03, macro context, futures carry |
| **failed replication** | C1 cross replication (S1) — USD-regime artifact |
| **real but weak** | C1 (MTF confluence), S4 (triangular RV), spot carry (accrual only) |
| **cost-defeated** | C026, C029, C031, C1 validation/front gate, C008/C009, C015 |
| **infrastructure-only** | Lab + gates, cross/futures ingest, rate data, non-time bars, parity, null baseline |

**Central finding:** early failure mode = cost; final finding = idea quality /
market efficiency (proven when carry stayed null on CME futures with financing
wall removed).

Full ledger: `FOREX_STRATEGY_SEARCH_FINAL_EVIDENCE_INVENTORY.md`.

---

## Final lessons learned (summary)

**What worked:** machine-enforced freeze, pre-commit discipline, matched-null
benchmarks, cost-feasibility gates, honest bid/ask modeling, additive platform
engineering, decision-forcing venue tests.

**What failed:** no tradable edge in 31 campaigns; direction null everywhere;
genuine effects (C1, S4, carry) too small or non-predictive; exit tweaks cannot
rescue entry null; breadth and venue changes did not help.

**Recurring failure modes:** within-null, cost-defeated, financing-defeated,
failed replication, selection noise, turnover amplification, USD/regime artifact,
rescue-by-exit fallacy.

**Key false assumption falsified:** "carry is financing-defeated; a fair venue
will rescue it" → futures carry is non-predictive (h3 t = 0.09).

Full document: `FOREX_STRATEGY_SEARCH_FINAL_LESSONS.md`.

---

## Archive decision (summary)

**Decision:** `ARCHIVED_STRATEGY_SEARCH`.

**Why:** every shortlisted mechanism has a terminal verdict; the futures carry
diagnostic answered the root-cause question (idea quality, not merely cost); no
remaining reachable experiment attacks the binding constraint.

**Reopen requires:** at least one new input — new market, new data class (tick/L2,
fundamentals, positioning), or new external thesis — plus all gating conditions
(precommit, falsification panel, front-gate before campaign, human approval).

**Explicitly insufficient:** parameter re-tunes, timeframe swaps, single-pair focus,
"almost flat" results, relaxed gates, mining same data with new slicing.

Full document: `FOREX_STRATEGY_SEARCH_ARCHIVE_DECISION.md`.

---

## Future opportunities (summary)

Non-active catalog of directions outside the archived programme:

1. **FX futures research (extended)** — basis/roll studies; needs new hypothesis
2. **Different asset classes** — new project using platform patterns
3. **Alternative datasets** — tick/L2, options-implied, COT, fundamentals
4. **Institutional datasets & venues** — ECN spreads; may rescue S4 at institutional cost
5. **Market-microstructure research** — academic lane; needs tick data
6. **Platform reuse** — non-trading repurposing of mature infrastructure

Full catalog: `FOREX_RESEARCH_FUTURE_OPPORTUNITIES.md`.

---

## Validation results (Phase 6)

| Check | Result |
|-------|--------|
| `pytest tests/ -q` | **2460 passed** in 43.99s |
| `ruff check src scripts tests` | 5 errors — **all pre-existing** (UP017 `datetime.UTC` in `scripts/run_edge_discovery_vol_managed_tsmom.py` + `scripts/build_carry_rate_dataset.py`; FURB1096 in carry script). **Zero code changed this sprint.** |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED |
| `git status --short` | clean |

---

## Compliance ledger

| Question | Answer |
|----------|--------|
| Campaign created? | **No** (no CAMPAIGN_032; none of any kind) |
| Strategy approved? | **No** (`approved: []`) |
| Factor discovery/validation performed? | **No** |
| Trading logic built? | **No** |
| Rejected ideas revived? | **No** |
| Archived lanes reopened? | **No** |
| Paper/demo/live enabled? | **No** — still blocked |
| Freeze intact? | **Yes** |

---

## Files to review first

1. `FOREX_STRATEGY_SEARCH_FINAL_SUMMARY.md` — programme executive summary
2. `FOREX_STRATEGY_SEARCH_ARCHIVE_DECISION.md` — formal archive + reopen gates
3. `FOREX_STRATEGY_SEARCH_FINAL_EVIDENCE_INVENTORY.md` — complete classified ledger
4. `FX_FUTURES_CARRY_VERDICT.md` — terminal trigger verdict
5. `FOREX_STRATEGY_SEARCH_FINAL_LESSONS.md` — durable lessons
6. `FOREX_RESEARCH_FUTURE_OPPORTUNITIES.md` — non-active future directions

---

## Programme closeout statement

The forex strategy-search programme is **formally archived** with a complete,
evidence-based research record. Thirty-one campaigns, eight factor slots, six+
front-gate screens, three venue studies, and one decisive futures diagnostic
produced zero approved strategies — not from lack of discipline, but because
liquid FX at testable cost structures and available data classes did not yield a
tradable edge. The platform remains frozen and reusable. Any future work requires
a genuinely new input, not another pass over this corpus.

**Programme status: ARCHIVED.**
