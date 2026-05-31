# Next-Sprint Prompt — External Thesis Sourcing + Session Atlas (after USD_JPY microstructure closeout)

**Date:** 2026-05-28 · **Type:** prompt draft. This file *contains* the next sprint's
prompt; it executes nothing itself.

> Copy the fenced block below verbatim into Claude/Cursor to run the next sprint. It is a
> **research / diagnostic-only** sprint that (a) maps USD_JPY (and optionally all-pair)
> session/time/volatility/spread behavior from local M1/M15/H1 data, and (b)
> sources/scores candidate **external** FX theses, producing a shortlist for a *future*
> precommit. It does **not** create a campaign, implement a strategy, create C024,
> execute C023, approve anything, or touch paper/demo/live — and it does **not** re-mine
> the closed C022/C023/USD_JPY microstructure family.

---

```text
We are starting a forex-bot READ-ONLY external-thesis-sourcing + session-atlas research sprint.

Branch/worktree:
Create a fresh worktree from current `main` (or from the USD_JPY microstructure closeout
branch HEAD if not yet merged — do NOT go back to a main that lacks the closeout docs).

Branch name:
research-external-thesis-sourcing-and-session-atlas-001

This is NOT a strategy implementation sprint.
This is NOT a campaign.
This is NOT C024 (do not create CAMPAIGN_024).
This is NOT C023 execution.
This is NOT paper/demo/live enablement.
This is NOT approval.
This is NOT a re-mining of the C022/C023/USD_JPY microstructure family (that thread is CLOSED).

Context:
The full C022/C023 pullback-resolution → USD_JPY microstructure entry → USD_JPY
post-entry trade-management thread is CLOSED with no actionable edge: internally-invented
confluence/reclaim/stop/confirmation combinations repeatedly failed, and post-entry
descriptive signals were not actionable (early-exit counterfactuals all reduced
expectancy). The lesson: the next edge must come from a genuinely NEW source (external
thesis) and/or from MAPPING behavior, not another internal technical combination. See:
  docs/research/C022_C023_USDJPY_MICROSTRUCTURE_THREAD_CLOSEOUT.md
  docs/research/NEXT_RESEARCH_LANE_AFTER_USDJPY_MICROSTRUCTURE_CLOSEOUT.md
Reuse existing read-only infra where useful (cost atlas, materialized M1/M15/H1 loaders,
feature-separation helpers). Do not edit strategy logic.

Main goal:
Produce (1) a read-only USD_JPY session/time/volatility/spread behavior ATLAS from local
data, and (2) an EXTERNAL-THESIS shortlist scored against repo evidence — a menu for a
future precommit. No strategy, no campaign, no approval.

Hard rules:
* Do not create CAMPAIGN_024.
* Do not execute C023.
* Do not implement a trading strategy or edit any strategy's entry/exit logic.
* Do not run a campaign.
* Do not re-mine the C022/C023/USD_JPY microstructure family or propose another variant of it.
* Do not change any campaign verdict or rewrite historical metrics.
* Do not modify configs/approved_strategies.yaml except to verify it stays approved: [].
* Do not enable paper/demo/live; do not modify broker/executor/order/live behavior.
* Do not call OANDA mutation/order APIs; do not use live trading credentials.
* Do not commit .env, credentials, DBs, raw candle dumps, huge CSVs, or bulky artifacts
  (gitignore any bulky atlas table; commit only compact summary CSV/JSON + docs).
* The atlas is DESCRIPTIVE — do not retro-fit it into a strategy or threshold-mine it.
* External theses are a SHORTLIST for future precommit — do not present any as proven
  edge, and do not implement one in this sprint.
* Distinguish clearly: descriptive map vs candidate hypothesis vs (forbidden) tradable rule.

Work in phases. Commit after each meaningful phase.

PHASE 0 — branch, audit, plan
1. Create the branch above from the closeout HEAD (not an older main).
2. Verify: C020/C021/C022 REJECT; C023 scaffold-only/not executed; C024 absent;
   approved_strategies.yaml is approved: []; paper/demo/live guards intact.
3. Confirm local M1/M15/H1 USD_JPY data is reachable READ-ONLY; confirm the cost atlas /
   materialized loaders are usable.
4. Run baselines: pytest tests/ -q; ruff check src tests scripts research;
   python scripts/check_research_freeze.py; python scripts/validate_research_archive.py;
   python scripts/scan_artifacts_for_secrets.py. Document pre-existing skips.
5. Create docs/research/EXTERNAL_THESIS_AND_SESSION_ATLAS_001_PLAN.md (purpose, scope,
   atlas spec, thesis-sourcing method, non-goals, safety rules, validation commands,
   explicit no-C024/no-C023/no-strategy/no-approval statement). Commit.

PHASE 1 — USD_JPY session / time-of-day behavior atlas (descriptive)
Build a read-only atlas module + script. For USD_JPY (and optionally all 7 majors),
summarize by UTC session bucket (Tokyo / London / overlap / NY / rollover) and by hour:
  * realized volatility (ATR, range) distribution,
  * spread / spread-to-ATR distribution (from the cost atlas),
  * directional drift and its dispersion,
  * reversal vs trend-persistence statistics (e.g. autocorrelation of returns),
  * gap / rollover behavior.
Report distributions, not a strategy. Gitignore any bulky per-bar table; commit a compact
summary CSV/JSON + docs/research/USDJPY_SESSION_ATLAS_RESULT.md. Add unit tests for the
atlas aggregation. Commit.

PHASE 2 — external thesis sourcing + shortlist
Create docs/research/EXTERNAL_FX_THESIS_SHORTLIST.md. Survey candidate external FX edges
from public / institutional / academic sources and/or user-provided notes (if available
locally; if not, clearly mark sources as TODO/user-supplied — do not fabricate citations).
For each candidate thesis, record: the claimed mechanism, the source, the horizon, the
data it would need, how it could be tested READ-ONLY against repo data, and how it scores
against the session atlas and existing repo evidence (does the atlas already contradict or
support it?). Produce a scored shortlist.

PHASE 3 — readiness / selection note
Create docs/research/EXTERNAL_THESIS_AND_SESSION_ATLAS_READINESS.md. Classify the sprint
outcome: which (if any) external thesis is `SHORTLISTED_FOR_PRECOMMIT` (well-defined,
testable read-only, not contradicted by the atlas, plausibly distinct from prior failures),
which are `DEFER`, which are `REJECT`. Do NOT precommit or implement any thesis here; a
future, separate sprint would pre-commit exactly one. Create no C024; approve nothing.

PHASE 4 — final validation + summary
Run pytest / ruff / check_research_freeze / validate_research_archive /
scan_artifacts_for_secrets / git status --short. Verify: no verdict changed; no strategy
approved; approved_strategies.yaml still approved: []; no C024; C023 not executed; no
paper/demo/live; no broker/executor changes; no OANDA calls; no credentials/DBs/huge
artifacts staged. Create
docs/research/EXTERNAL_THESIS_AND_SESSION_ATLAS_001_SUMMARY.md (branch, commit hashes by
phase, files by phase, atlas coverage, shortlist + scores, selected/deferred theses,
verification that nothing was approved/executed, tests run, pre-existing skips, files to
review first, recommended next sprint).
```

---

## Notes for whoever runs the above

- **No code-an-entry-strategy.** This sprint deliberately produces a *map* and a *menu*,
  not a strategy. The closed thread's lesson is that another internally-invented entry is
  not warranted.
- **Atlas is descriptive.** It must not be retro-fit into a rule or threshold-mined; its
  value is as a prior and a pre-screen for sourced theses.
- **External theses are a shortlist.** Even a `SHORTLISTED_FOR_PRECOMMIT` thesis only
  unlocks a *separate* pre-committed, out-of-sample sprint — never a campaign or C024 here.
- **If no credible external thesis is found and the atlas is purely descriptive,** that is
  a valid outcome: recommend pausing strategy search (Lane 1) and continuing
  infrastructure/process work, holding the freeze.
