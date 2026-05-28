# Next-Sprint Prompt — Microstructure Confirmation Diagnostic (after C022 family closeout)

**Date:** 2026-05-28 · **Sprint:** `research-post-c022-family-retirement-and-new-thesis-selection-001`
**Type:** prompt draft. This file *contains* the next sprint's prompt; it executes nothing itself.

> Copy the fenced block below verbatim into Claude/Cursor to run the next sprint.
> The next sprint is a **read-only diagnostic**: it inventories and tests M15
> confirmation primitives against the existing C022 trade set, then produces a
> readiness decision for a *possible future* C024. It **does not** create C024,
> execute C023, implement a strategy, tune thresholds, approve anything, or touch
> paper/demo/live or broker/executor/order/live code.

---

```text
We are starting a forex-bot READ-ONLY market-microstructure confirmation diagnostic sprint.

Branch/worktree:
Create a fresh worktree from current `main`.

Branch name:
research-m15-microstructure-confirmation-diagnostic-001

This is NOT a new strategy implementation sprint.
This is NOT C024 (do not create CAMPAIGN_024).
This is NOT C023 execution.
This is NOT a tuning/threshold-mining sprint.
This is NOT paper/demo/live enablement.

Context:
The C022/C023 H4/H1 pullback-resolution family is RETIRED
(RETIRED_UNLESS_NEW_EXTERNAL_THESIS). Diagnostics localized C022's failure to the
ENTRY TRIGGER: the M15 EMA-reclaim signal is inert (m15_reclaim_distance_atr AUC
0.494/0.485), all ATR/time stop variants and a cost-free baseline stay negative, and
every structural entry feature sits at AUC ~= 0.50. The selected next lane is
market-microstructure-style confirmation: replace the weak reclaim trigger with
stronger, structurally different proof of an order-flow shift. See:
  docs/research/C022_C023_PULLBACK_RESOLUTION_FAMILY_CLOSEOUT.md
  docs/research/NEXT_THESIS_SELECTION_DECISION.md
  docs/research/C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md
The C022 per-trade feature reconstruction pattern (lookahead-safe, side-agreement
verified) lives in src/forex_bot/research/c022_entry_features.py and
src/forex_bot/research/feature_separation.py — reuse it; do not edit strategy logic.

Main goal:
Determine, READ-ONLY, whether any M15 confirmation primitive separates C022 winners
from losers. Produce a readiness decision (READY_FOR_PRECOMMIT / NOT_READY) for a
POSSIBLE FUTURE C024 — but do not create C024 in this sprint.

Hard rules:
* Do not create CAMPAIGN_024.
* Do not execute C023.
* Do not implement a new strategy or edit any strategy's entry/exit logic.
* Do not retune C022 or mine thresholds into an edge.
* Do not alter existing campaign verdicts or rewrite historical metrics.
* Do not modify configs/approved_strategies.yaml except to verify it stays approved: [].
* Do not enable paper/demo/live; do not modify broker/executor/order/live behavior.
* Do not call OANDA mutation/order APIs; do not use live credentials.
* Do not commit .env, credentials, SQLite DBs, raw candle dumps, huge CSVs, or bulky
  generated artifacts (gitignore large parquet/CSV; commit only manifests + small
  previews + summary JSON, as the C022 feature-separation sprint did).
* Detectors must be strictly causal / decision-bar-anchored — no lookahead. Verify
  with a side-agreement / alignment sanity check (as in the C022 reconstruction).
* Do not present any diagnostic separation as tradable edge. Any future C024 must be
  precommitted out-of-sample in a separate sprint before execution.

Work in phases. Commit after each meaningful phase.

PHASE 0 — branch, audit, plan
1. Start from current `main`; create the fresh worktree/branch above.
2. Verify: C020/C021/C022 REJECT; C023 scaffold-only/not executed; C024 does not
   exist; approved_strategies.yaml is approved: []; paper/demo/live guards intact.
3. Confirm the C022 base trade set + materialized M15/H1/H4 are reachable READ-ONLY
   (as in the feature-separation sprint).
4. Run baselines: pytest tests/ -q; ruff check src tests scripts research;
   python scripts/check_research_freeze.py; python scripts/validate_research_archive.py;
   python scripts/scan_artifacts_for_secrets.py. Document any pre-existing failures.
5. Create docs/research/M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_001_PLAN.md
   (purpose, primitive inventory, non-goals, safety rules, separation method,
   readiness bar, validation commands, explicit no-C024/no-approval statement).
   Commit.

PHASE 1 — confirmation-primitive inventory
Create docs/research/M15_CONFIRMATION_PRIMITIVES_INVENTORY.md. For each primitive,
give a precise, causal, decision-bar-anchored definition and the bars/fields it needs:
  * reclaim + impulse candle (body/ATR threshold on the trigger bar),
  * reclaim + break of prior micro-swing (structure break confirmation),
  * reclaim + retest hold (pullback to reclaimed level holds),
  * liquidity sweep + displacement (stop-run beyond a prior extreme then reversal),
  * range expansion after compression (NR/contraction then expansion bar),
  * failed reclaim / trap avoidance (reclaim that immediately fails = skip).
Note which are computable from M1/M15 OHLC alone and any that are not. Commit.

PHASE 2 — read-only detectors
Implement detectors in src/forex_bot/research/ (NOT in strategy code). Each returns a
boolean/scalar presence per C022 trade at its decision bar, reconstructed read-only
from materialized frames. Add unit tests proving (a) causality (no post-entry bars
used) and (b) a side-agreement / alignment sanity check. Gitignore any large dataset;
commit manifest + small preview + summary JSON only. Commit.

PHASE 3 — winner/loser separation comparison
Reuse the feature-separation method (|AUC-0.5| effect, quintile win-rates, reported
per train/validation split, post-hoc outcome labels kept out of features via a
denylist). Score each primitive's presence on C022 winners vs losers. Create
docs/research/M15_CONFIRMATION_PRIMITIVE_SEPARATION_RESULT.md with the table and an
honest read (negligibility floor 0.05; flag any instability across splits). Commit.

PHASE 4 — readiness decision (NO C024 created)
Create docs/research/C024_MICROSTRUCTURE_READINESS_DECISION.md. Apply the five-part
bar from NEXT_THESIS_SELECTION_DECISION.md section 5:
  (1) >=1 primitive separates in BOTH splits, effect materially above the 0.05 floor
      and above the best structural C022 feature;
  (2) plausible order-flow/liquidity logic;
  (3) survives controlling for cost/hour/volatility (not context overfit);
  (4) no outcome leakage (causal detectors);
  (5) plausibly material enough to move REJECT toward non-negative while keeping a
      usable sample, judged before any threshold is chosen.
Output READY_FOR_PRECOMMIT or NOT_READY. Create NO CAMPAIGN_024 and propose NO
thresholds regardless of outcome. Commit.

PHASE 5 — final validation + summary
Run pytest / ruff / check_research_freeze / validate_research_archive /
scan_artifacts_for_secrets / git status --short. Verify: no verdict changed; no
strategy approved; approved_strategies.yaml still approved: []; no C024 created; C023
not executed; no paper/demo/live; no broker/executor changes; no OANDA mutation/order
calls; no credentials/DBs/huge artifacts staged. Create
docs/research/M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_001_SUMMARY.md (branch, commit
hashes by phase, files by phase, primitives tested, separation results, readiness
decision, what would justify a future C024 precommit, verification that nothing was
approved/executed, tests run, pre-existing failures, files to review first, recommended
next sprint). Commit.
```

---

## Notes for whoever runs the above

- The prompt deliberately ends at a **readiness decision**, not a campaign. Even a
  `READY_FOR_PRECOMMIT` outcome only unlocks a *separate* precommit sprint; C024 is
  never created inside the diagnostic.
- The five-part readiness bar is reproduced from
  [`NEXT_THESIS_SELECTION_DECISION.md`](NEXT_THESIS_SELECTION_DECISION.md) §5 — keep
  the two in sync if either is revised.
- Lane C (cost/tradeability guardrail) is a recommended *companion overlay* for any
  future signal sprint, not part of this diagnostic.
