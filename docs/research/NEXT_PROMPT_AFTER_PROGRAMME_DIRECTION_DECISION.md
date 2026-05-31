# Next Prompt After Programme Direction Decision (Phase 5)

**Sprint:** `research-programme-direction-after-carry-001`
**Type:** Documentation only.
**Date:** 2026-05-31
**Purpose:** Draft the exact next coding-agent prompt implied by the Phase 4 decision (pivot to FX futures as a data + infra + read-only diagnostic sprint, NOT a campaign).

---

## Notes for the operator

- This prompt assumes a clean, updated `origin/main` and the standing read-only research-DB authorization.
- It is a **data-ingest + infrastructure + diagnostic** sprint — the analogue of the financing/rate-data ingestion sprint, not a campaign or factor study.
- It is **decision-forcing**: its output either opens a real lane or triggers the pre-committed archive fallback.
- Before assigning any identifier, grep that the number/name is unused (per the standing "check identifier numbers are unused" lesson).
- FX futures data is broadly available without a broker API; if a vendor/credential is needed, never commit a key.

---

## The prompt

> We are starting an FX-futures venue + diagnostic sprint from clean, updated origin/main.
>
> **Branch:**
>
> `research-fx-futures-venue-and-diagnostic-001`
>
> **Context:**
>
> The in-repo spot-FX factor search is exhausted. Every shortlisted family has a verdict; none produced a tradable edge. The dominant failure mode is cost, not idea quality. The programme-direction-after-carry sprint decided (Option C) to test the one remaining cost-relevant mechanism: FX futures (CME), which remove the nightly financing leg, tighten effective spreads, and offer decades of history. This sprint builds that venue and runs a read-only survival diagnostic on the programme's already-identified genuine effects.
>
> **Goal:**
>
> Determine whether the programme's known-real-but-cost-defeated effects survive net of cost in FX futures. Decision-forcing: survive → a real lane opens; fail → trigger the archive fallback.
>
> **This sprint is data ingestion + infrastructure + a read-only diagnostic only.**
>
> Do not create a strategy.
> Do not create a campaign.
> Do not build trading logic.
> Do not approve any strategy.
> Do not enable paper/demo/live.
> Do not re-tune or revive any closed spot-FX family.
>
> **Hard rules:**
>
> - Do not create CAMPAIGN_032 or any campaign.
> - Treat the existing C1 (MTF confluence fade), S4 (triangular relative-value reversion), and time-series-momentum effect definitions as FROZEN and as-found. The diagnostic measures whether they survive futures cost; it does not search for new factors or re-fit parameters.
> - Keep the research freeze intact. Spot majors/crosses code is untouched — futures support is ADDITIVE only (new instrument registry entries, new ingestion path, new cost model), mirroring the non-USD-cross expansion pattern.
> - Never commit any vendor/data credential.
> - Present no futures result as an edge — only as a gross/net survival diagnostic with honest data caveats.
>
> **PHASE 0 — plan + pre-registration**
> Create `docs/research/FX_FUTURES_VENUE_AND_DIAGNOSTIC_001_PLAN.md`. Pre-register: which contracts (e.g. 6E/6J/6B/6A/6C/6S), the continuous-contract roll method, the diagnostic metrics, the matched-null design, and the pass/fail thresholds for "survives cost" — committed BEFORE any data is read. Commit.
>
> **PHASE 1 — futures instrument registry + cost/roll model**
> Add an additive futures instrument registry (`domain/` or equivalent) and a futures cost/roll model under `research/cost_models/` (tick value, exchange+clearing fees, bid/ask in ticks, roll/basis cost — NO copied spot assumptions). Add validation. Spot code untouched. Commit.
>
> **PHASE 2 — data ingestion + validation**
> Ingest continuous FX-futures data (deep history). Validate completeness, roll continuity, no lookahead, and internal consistency. Document vendor + roll method + limitations. Commit.
>
> **PHASE 3 — read-only diagnostic**
> Re-run the FROZEN C1 / S4 / TSMOM effect definitions against the futures data through the existing factor-lab gates (matched null, multiple-comparison, cost-feasibility), now using the futures cost/roll model. Gross AND net. Commit per finding.
>
> **PHASE 4 — verdict**
> Create `docs/research/FX_FUTURES_DIAGNOSTIC_FINDINGS.md` with one of:
> - `EFFECTS_SURVIVE_IN_FUTURES` → a real lane opens; recommend a pre-registered front-gate screen (still no campaign) as the next sprint.
> - `COST_WALL_HOLDS_IN_FUTURES` → trigger the pre-committed archive fallback (Option E).
> Commit.
>
> **PHASE 5 — next prompt**
> Draft the implied next prompt (front-gate screen design OR archive sprint). Commit.
>
> **PHASE 6 — validation**
> Run: pytest tests/ -q; ruff check src scripts tests; python scripts/check_research_freeze.py; python scripts/validate_research_archive.py; python scripts/scan_artifacts_for_secrets.py; git status --short. Create `FX_FUTURES_VENUE_AND_DIAGNOSTIC_001_SUMMARY.md`. 
>
> **Final response must include:** branch name; commit hashes by phase; contracts ingested + data caveats; diagnostic results (gross vs net per effect); verdict; whether any campaign was created (expected: no); whether any strategy was approved (expected: no); whether paper/demo/live remain blocked (expected: yes); recommended next sprint; files to review first.
>
> **Success criteria:** decisively determine whether the programme's genuine effects survive cost in FX futures. Do not create a strategy. Do not create a campaign. Do not attempt to trade.

---

## If the decision is ever overridden to Archive (Option E) instead

A short alternate prompt is held in reserve: a docs-only sprint (`research-forex-strategy-search-archive-001`) that writes the programme post-mortem, the restart criteria (new market/data/thesis only — never a re-tune), and freezes the platform as a reusable research asset. This is the Phase-4 fallback and is only used if the operator decides not to fund the futures venue, or after the futures diagnostic returns `COST_WALL_HOLDS_IN_FUTURES`.
