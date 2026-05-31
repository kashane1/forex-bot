# Next Prompt After FX Futures Venue & Diagnostic (Phase 6)

**Sprint:** `research-fx-futures-venue-and-diagnostic-001`
**Type:** Documentation only.
**Date:** 2026-05-31
**Viability verdict (Phase 5):** `VIABLE_WITH_LIMITATIONS` → draft the **scoped diagnostic sprint** (carry-first, free/local EOD), with the archive closeout held as the documented fallback if the build/coverage step fails.

---

## Operator notes

- This is the **first code-bearing sprint** of the futures pivot: it builds an additive ingestion + continuous-contract roll adapter and *runs* the frozen carry factor under the futures cost model. It is **still not** a strategy/campaign/front-gate.
- Scope is deliberately narrow: **carry on free/local EOD futures data.** C1 is a *conditional stretch* only if an intraday feed is secured; **S4 is excluded** (Phase 2/4 reasoning).
- It is decision-forcing: result → either a narrow continue (one future pre-registered screen) or the **pre-committed archive (Option E).**
- Grep that any identifier/number is unused before assigning. Never commit a vendor credential; the secret-scan gate must stay green.
- Confirm tick/commission specs and the **6J ×100 scaling** at ingestion (Phase 1 `[CONFIRM]` items).

---

## The prompt

> We are starting the FX-futures carry diagnostic sprint from clean, updated origin/main.
>
> **Branch:**
>
> `research-fx-futures-carry-diagnostic-001`
>
> **Context:**
>
> The FX-futures venue-validation sprint returned `VIABLE_WITH_LIMITATIONS`: a meaningful futures diagnostic is executable for **carry** on free/local EOD CME FX-futures data, which removes the nightly financing wall that defeated spot carry/C031 and supplies decades of history. C1 needs a paid/account intraday feed (stretch only); S4 is excluded (needs synced tick + latency model; its ≤1-bar staleness constraint is venue-independent). This sprint builds the futures data layer and runs the FROZEN carry factor under the futures cost model.
>
> **Goal:**
>
> Determine whether the frozen cross-sectional carry factor shows any net survival in FX futures — i.e. whether carry was merely financing-defeated (→ might survive a fair venue) or genuinely non-predictive (→ will be null even with no financing). Decision-forcing for the whole programme.
>
> **This sprint is infrastructure + data + a read-only diagnostic only.**
>
> Do not create a strategy. Do not create a campaign. Do not create entry/exit rules or trading logic. Do not approve any strategy. Do not enable paper/demo/live. Do not alter the carry definition. Do not retune carry, C1, S4, or any rejected factor. Do not optimize any parameter.
>
> **Hard rules:**
>
> - Do not create CAMPAIGN_032 or any campaign.
> - The carry factor definition is FROZEN (month-end rank by short rate; HML-3 dollar-neutral; 1/3/6/12-month horizons; primary cell currency HML-3 total 3-month). The diagnostic substitutes the futures continuous series for the spot series with quote inversion only — no other change.
> - Keep the research freeze intact. Futures support is ADDITIVE only (new instrument registry entries, new ingestion path, new continuous-roll adapter, new futures cost model), mirroring the non-USD-cross expansion. Spot majors/crosses code untouched.
> - Roll rule and cost figures are pre-registered BEFORE any data is read; no optimization.
> - Never commit a vendor credential; secret-scan stays green.
> - Present no result as an edge — only as a gross/net survival diagnostic with honest data caveats.
>
> **PHASE 0 — plan + pre-registration.** `docs/research/FX_FUTURES_CARRY_DIAGNOSTIC_001_PLAN.md`: pre-register contracts (6E/6B/6J/6S/6A/6C/6N), roll rule (volume/OI crossover + cap), continuous-adjustment method (ratio for returns; unadjusted for roll cost), cost figures (from the venue cost model), matched-null design, and the pass/fail "survives cost" thresholds — all committed before data is read. Commit.
>
> **PHASE 1 — additive futures instrument registry + continuous-roll adapter.** Build the registry entries and a lookahead-safe continuous-contract builder (per the universe design); add validation/tests; spot code untouched. Commit.
>
> **PHASE 2 — ingest + validate free/local EOD data.** Ingest decades of EOD continuous CME FX-futures data (free source confirmed at ingest). Validate completeness, roll continuity, quote-inversion correctness, and the 6J scaling. Document source + coverage + limitations. Commit.
>
> **PHASE 3 — futures cost model (code).** Implement the Phase-3 venue cost model as a research cost module under `research/cost_models/` (financing = 0; explicit roll cost). Tests. Commit.
>
> **PHASE 4 — run the FROZEN carry factor.** Re-express carry on the futures series (inversion only) and run it through the existing matched-null / multiple-comparison / cost-feasibility gates, gross AND net. No new thresholds. Commit.
>
> **PHASE 5 — verdict.** `docs/research/FX_FUTURES_CARRY_DIAGNOSTIC_FINDINGS.md`: `CARRY_SURVIVES_IN_FUTURES` (→ recommend one future pre-registered front-gate screen, still no campaign) or `CARRY_DOES_NOT_SURVIVE_IN_FUTURES` (→ trigger the pre-committed archive, Option E). Commit.
>
> **PHASE 6 — next prompt.** Draft the implied next prompt (narrow screen OR archive sprint). Commit.
>
> **PHASE 7 — validation.** Run: pytest tests/ -q; ruff check src scripts tests; python scripts/check_research_freeze.py; python scripts/validate_research_archive.py; python scripts/scan_artifacts_for_secrets.py; git status --short. Create `FX_FUTURES_CARRY_DIAGNOSTIC_001_SUMMARY.md`.
>
> **Final response must include:** branch; commit hashes by phase; contracts + source + coverage caveats; carry gross vs net result vs the gates; verdict; whether any campaign was created (expected: no); whether any strategy was approved (expected: no); whether paper/demo/live remain blocked (expected: yes); recommended next sprint; files to review first.
>
> **Success criteria:** decisively determine whether frozen carry survives net of cost in FX futures. Do not create a strategy. Do not create a campaign. Do not attempt to trade.

---

## Fallback prompt (if the build/coverage step proves infeasible, or after a `DOES_NOT_SURVIVE` verdict)

> Archive/closeout sprint (`research-forex-strategy-search-archive-001`, docs-only): write the programme post-mortem; record that the failure ceiling is **transaction economics confirmed even in a fair-cost venue** (futures carry null with financing removed) → idea-quality/efficiency, not just retail cost, is the binding limit; define strict restart criteria (new market / new data / new external thesis — never a re-tune); freeze the platform as a reusable research asset. No strategy, no campaign, no approval; paper/demo/live stay blocked.

---

## Why this is the right next step

The carry diagnostic is the **cheapest experiment that can still change the programme's conclusion**: it is free/local, it removes the one wall (financing) that the programme could plausibly blame, and it disambiguates the two surviving hypotheses (financing-defeated vs non-predictive). Whichever way it lands, the programme can then either open one narrow screen or archive with a complete, honest, fair-venue-tested conclusion.
