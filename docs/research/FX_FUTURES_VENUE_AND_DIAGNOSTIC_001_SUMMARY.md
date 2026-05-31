# FX Futures Venue & Diagnostic — SUMMARY (Phase 7)

**Sprint:** `research-fx-futures-venue-and-diagnostic-001`
**Type:** Infrastructure / data / diagnostic **research design** only. Docs-only — zero code, zero data ingested.
**Status:** COMPLETE.
**Date:** 2026-05-31
**Freeze:** intact. Paper/demo/live remain blocked.

---

## What this sprint did

Evaluated whether **FX futures (CME)** is a credible *final venue test* for the programme's frozen real-but-weak structures (C1, S4, carry) — designing the universe, assessing data feasibility, building a research cost model, specifying the diagnostic, and reaching a viability verdict. No factor definition was altered; nothing was tuned, traded, or approved.

---

## Commit hashes by phase

| Phase | Hash | Artifact |
|-------|------|----------|
| 0 — baseline audit plan | `19c9df0` | `FX_FUTURES_VENUE_AND_DIAGNOSTIC_001_PLAN.md` |
| 1 — futures universe design | `5513cd4` | `FX_FUTURES_UNIVERSE_DESIGN.md` |
| 2 — data-source feasibility | `91bfef9` | `FX_FUTURES_DATA_SOURCE_FEASIBILITY.md` |
| 3 — venue-cost model | `da0c99f` | `FX_FUTURES_COST_MODEL.md` |
| 4 — diagnostic framework | `1e3e776` | `FX_FUTURES_DIAGNOSTIC_FRAMEWORK.md` |
| 5 — viability decision | `193941a` | `FX_FUTURES_VIABILITY_DECISION.md` |
| 6 — next prompt | `286a7f8` | `NEXT_PROMPT_AFTER_FX_FUTURES_VENUE_AND_DIAGNOSTIC.md` |
| 7 — summary | *(this commit)* | `FX_FUTURES_VENUE_AND_DIAGNOSTIC_001_SUMMARY.md` |

---

## 1. Futures universe selected

Seven full-size CME FX futures, mapped to the spot major set: **6E** (EUR), **6B** (GBP), **6J** (JPY), **6S** (CHF), **6A** (AUD), **6C** (CAD), **6N** (NZD). Quarterly cycle (H/M/U/Z), IMM expiry. **Quote inversion** required for 6J/6S/6C (futures quote XXX/USD vs spot USD/XXX) — a sign-only re-expression that preserves the frozen factor logic. E-micros excluded (proportionally worse cost/history). Roll = lookahead-safe volume/OI crossover; continuous series = ratio-adjusted for returns, unadjusted retained for explicit roll-cost accounting. Highest data-hygiene risk flagged: **6J ×100 vendor scaling**.

## 2. Data-source findings

Feasibility splits sharply by the resolution each frozen factor needs:
- **Carry (monthly):** **FEASIBLE on free/local EOD** (Stooq/Yahoo), decades of history — *more* than the spot corpus's ~6.4 y, fixing the carry power limit. The basis/roll (futures carry) is observable in the same free feed.
- **C1 (M15/H1/H4):** **PARTIAL** — free intraday is too shallow (Yahoo hourly ≈730 d); needs a paid/account intraday feed (IBKR or 1-min vendor). Collapsing to EOD would alter the definition (forbidden), so it's a stretch goal only.
- **S4 (M5, ≤1-bar half-life):** **NOT FEASIBLE** on free/local — needs synchronized tick + a latency model; its binding constraint (staleness) is venue-independent. Excluded with reasons, not silently dropped.

## 3. Cost-model findings

Futures **structurally removes the nightly financing wall** (the ≈4× spread squeeze that defeated C031/carry); cost of carry moves into the basis, realized via quarterly roll. Conservative round-trip estimates: **~2.3 bp (6E/6J), ~2.9 bp (others), financing = 0**, + ~3.7 bp/yr roll — versus spot ~3–5 bp **plus** the nightly financing squeeze. So futures is ~1.5–2× cheaper per round-trip and removes the holding wall. **Crucial honest caveat:** futures removes the financing *penalty* and the accrual *benefit* simultaneously (same rate differential, two sides), so carry-in-futures gross return ≈ its spot-predictive content — which was statistically zero. Futures gives carry a *fair* test; it cannot manufacture predictability.

## 4. Viability verdict

**`VIABLE_WITH_LIMITATIONS`.** A meaningful, decision-forcing diagnostic is executable — **for carry, on free/local EOD data** — but with an honest prior that it most likely **confirms the null**. C1 is data-gated (paid/account intraday); S4 is excluded (infeasible + venue-independent constraint). Not `READY_FOR_DIAGNOSTIC` (ingestion/roll adapter not built; coverage unconfirmed). Not `NOT_VIABLE` (carry is genuinely, freely testable and decision-forcing).

## 5. Validation results (Phase 7)

| Check | Result |
|-------|--------|
| `pytest tests/ -q` | **2454 passed** in 39.68s |
| `ruff check src scripts tests` | exit 1 — **5 pre-existing UP017 errors** in `scripts/run_edge_discovery_vol_managed_tsmom.py` + `scripts/build_carry_rate_dataset.py`, both **untouched** (this sprint changed zero code). No new lint debt. |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED (exit 0) |
| `python scripts/validate_research_archive.py` | ALL CHECKS PASSED (exit 0) |
| `python scripts/scan_artifacts_for_secrets.py` | PASSED (exit 0) |
| `git status --short` | clean |

## Compliance ledger

- **Campaign created?** No (no CAMPAIGN_032; none of any kind).
- **Strategy approved?** No.
- **Trading logic / entry-exit rules created?** No.
- **Factor definitions altered or retuned?** No (C1/S4/carry frozen).
- **Paper/demo/live?** Still blocked.
- **Freeze?** Intact.

## Recommended next sprint

`research-fx-futures-carry-diagnostic-001` — the first code-bearing futures sprint: build an additive futures instrument registry + lookahead-safe continuous-roll adapter, ingest free/local EOD CME FX-futures history, implement the futures cost model, and run the **frozen** carry factor (quote-inversion only) through the existing lab gates, gross and net. Decision-forcing: `CARRY_SURVIVES_IN_FUTURES` → one future pre-registered screen; `CARRY_DOES_NOT_SURVIVE_IN_FUTURES` → pre-committed archive (Option E). Full prompt in `NEXT_PROMPT_AFTER_FX_FUTURES_VENUE_AND_DIAGNOSTIC.md`.

## Files to review first

1. [FX_FUTURES_VIABILITY_DECISION.md](docs/research/FX_FUTURES_VIABILITY_DECISION.md) — the verdict + why.
2. [FX_FUTURES_DATA_SOURCE_FEASIBILITY.md](docs/research/FX_FUTURES_DATA_SOURCE_FEASIBILITY.md) — the per-factor feasibility split.
3. [FX_FUTURES_COST_MODEL.md](docs/research/FX_FUTURES_COST_MODEL.md) — financing-removed cost + the accrual-vs-basis subtlety.
4. [FX_FUTURES_DIAGNOSTIC_FRAMEWORK.md](docs/research/FX_FUTURES_DIAGNOSTIC_FRAMEWORK.md) — how frozen factors are tested unchanged.
5. [FX_FUTURES_UNIVERSE_DESIGN.md](docs/research/FX_FUTURES_UNIVERSE_DESIGN.md) — contracts, mappings, roll.
6. [NEXT_PROMPT_AFTER_FX_FUTURES_VENUE_AND_DIAGNOSTIC.md](docs/research/NEXT_PROMPT_AFTER_FX_FUTURES_VENUE_AND_DIAGNOSTIC.md) — the exact next prompt.
