# Next Sprint Prompt — After External Thesis Sourcing & Session Atlas

**Drafted by:** `external-thesis-sourcing-and-session-atlas-001` · Phase 5.
**Type of next sprint:** read-only **DIAGNOSTIC** (classification from Phase 4 =
`MORE_DIAGNOSTICS_REQUIRED`). This is **NOT** a precommit-design sprint, **NOT** an
execution sprint, **NOT** a campaign run. No new campaign number (no C024) is created
or implied by running it.

> Rationale: Phase 4 carried forward exactly one thesis — **#5 intraday
> volatility-compression → range-expansion (USD_JPY)** — but the atlas supports only its
> *volatility* leg and is silent on *monetization/direction*. Before any campaign is
> designed, a narrow precommitted diagnostic must answer whether the state converts into
> a cost-surviving trade structure. If it does not, the recommendation flips to
> `PAUSE_STRATEGY_RESEARCH`.

---

## Copy-paste prompt for the next sprint

```
We are starting the next forex-bot research sprint from the latest origin/main.

Sync and branch:

    cd /Users/kashane/dev/forex-bot
    git checkout main
    git pull --ff-only

Create a fresh branch:

    research-usdjpy-volatility-compression-expansion-diagnostic-001

This is NOT a strategy implementation sprint. NOT a campaign. NOT CAMPAIGN_024.
NOT C023 execution. NOT a precommit-design sprint. NOT a tuning sprint. NOT
paper/demo/live enablement. NOT approval.

Context: The external-thesis-sourcing-and-session-atlas-001 sprint is merged.
Conclusions carried in:
  * configs/approved_strategies.yaml remains approved: [] (verify only).
  * C022/C023 pullback-resolution family: RETIRED.
  * USD_JPY entry + post-entry microstructure diagnostics: CLOSED / NOT_READY.
  * Phase-4 decision = MORE_DIAGNOSTICS_REQUIRED; single carried-forward thesis
    = #5 intraday volatility-compression -> range-expansion (USD_JPY, M15).
  * #9 no-trade cost/spread filter ADOPTED as a standing overlay (rollover toxic
    ~5-10 pip; deprioritize off-hours).
  * No strategy approved; paper/demo/live blocked.

Read first:
  * docs/research/EXTERNAL_THESIS_SOURCING_AND_SESSION_ATLAS_001_SUMMARY.md
  * docs/research/USDJPY_SESSION_VOLATILITY_SPREAD_ATLAS.md
  * docs/research/USDJPY_EXTERNAL_THESIS_CANDIDATE_SCORECARD.md
  * docs/research/NEXT_THESIS_AFTER_EXTERNAL_SOURCING_AND_ATLAS.md
  * research/usdjpy_session_atlas/usdjpy_session_atlas_summary.json
  * scripts/build_usdjpy_session_volatility_spread_atlas.py

Main goal: Run ONE read-only, precommitted diagnostic that answers a single
question and nothing else:

  "Does an intraday volatility-compression -> expansion state on USD_JPY produce
   a cost-surviving, objectively-defined trade structure, and does it need a
   direction input or can it be direction-agnostic?"

Hard rules:
  * Do not create CAMPAIGN_024 (or any campaign number).
  * Do not implement a tradable strategy or signal-emitting loop.
  * Do not run a campaign; do not optimize/threshold-mine.
  * Do not alter any campaign verdict or rewrite historical metrics.
  * Do not modify configs/approved_strategies.yaml except to verify approved: [].
  * Do not enable paper/demo/live; do not modify broker/executor/order/live code.
  * Do not call OANDA mutation/order APIs; do not use live credentials.
  * Use local materialized M1/M5/M15/H1/H4 research-DB data READ-ONLY only.
  * The TEST window 2025-07-01+ stays a SEALED LOCKBOX. Train+validation only.
  * Do not commit .env, credentials, DBs, raw candle dumps, parquet, or huge CSVs.
  * Commit compact summaries only; gitignore bulky outputs.
  * Present results as a diagnostic, never as tradable edge.

Precommit BEFORE looking at any result (write them down in a plan doc and commit
that doc first):
  1. State definition: compression = trailing rolling ATR/range percentile below a
     fixed low threshold; expansion = subsequent realized range above a fixed
     multiple of the compressed range. Fix thresholds in advance; report a small
     pre-declared robustness grid; do NOT optimize to a best cell.
  2. Three monetizations, measured side by side, all net of session spread (use the
     atlas median + p90 by session) + a slippage allowance, with the #9 rollover/
     off-hours filter applied:
       (a) direction-agnostic post-compression excursion (|MFE| vs |MAE| vs cost);
       (b) expansion conditioned on a simple INDEPENDENT direction proxy;
       (c) fade of the first expansion leg.
  3. Kill criteria: if none of (a)/(b)/(c) clears cost by the pre-stated margin on
     BOTH train and validation, RETIRE the thesis and recommend
     PAUSE_STRATEGY_RESEARCH.

Work in phases; commit after each phase:
  Phase 0 — branch from latest origin/main; verify approved:[], guards intact,
            C023 not executed, C024 absent; confirm read-only DB coverage; run
            baseline (pytest, ruff, check_research_freeze, validate_research_archive,
            scan_artifacts_for_secrets); write the PRECOMMIT plan doc; commit.
  Phase 1 — implement read-only diagnostic tooling for the compression/expansion
            state + the three monetization measurements (no strategy class, no loop).
  Phase 2 — run the diagnostic on train+validation (TEST sealed); emit a compact
            JSON summary + a findings doc.
  Phase 3 — apply the precommitted kill criteria; classify
            READY_FOR_PRECOMMIT_DESIGN / MORE_DIAGNOSTICS_REQUIRED /
            PAUSE_STRATEGY_RESEARCH; draft the following sprint's prompt accordingly.
  Phase 4 — final validation + summary; verify no verdict/approval/guard changes,
            no C024, no C023 execution, no large/secret artifacts staged.

Final response must report: branch, commit hashes by phase, files changed, data
coverage, the three monetization results vs cost on train AND validation, whether
the kill criteria fired, the resulting classification, and explicit confirmation
that no campaign/C024/C023/approval/paper-demo-live changes occurred.
```

---

## Notes for the operator

- If the diagnostic returns **null** (kill criteria fire), do not look for a fourth
  monetization in the same sprint — that is threshold-mining. Record the null, retire
  #5, and the recommendation becomes `PAUSE_STRATEGY_RESEARCH` (or pivot to building the
  economic-calendar / rates-risk overlays so theses #7/#8 become testable later).
- Only if the diagnostic returns a **robust, cost-surviving** structure on *both*
  splits does a *subsequent* sprint design a precommitted campaign — and only at that
  point is a new campaign number even discussed.
- The TEST lockbox (2025-07+) must remain sealed through the diagnostic and any later
  design phase; it is opened only for a single final out-of-sample confirmation of a
  fully-precommitted campaign, never for exploration.
