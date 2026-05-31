# Next-Sprint Prompt — USD_JPY M15 Microstructure Confirmation Diagnostic (after C022 family closeout)

**Date:** 2026-05-28 · **Sprint:** `research-post-c022-family-retirement-and-new-thesis-selection-001`
**Type:** prompt draft. This file *contains* the next sprint's prompt; it executes nothing itself.

> Copy the fenced block below verbatim into Claude/Cursor to run the next sprint.
> The next sprint is a **read-only, USD_JPY-only diagnostic**: it inventories and tests
> M15 microstructure-confirmation primitives against the existing **USD_JPY** C022
> trades (and/or reconstructed USD_JPY entry contexts), then produces a readiness
> decision for a *possible future* **USD_JPY-only** C024. It **does not** create C024,
> execute C023, implement a strategy, tune thresholds, approve anything, or touch
> paper/demo/live or broker/executor/order/live code.
>
> **Scope amendment (2026-05-28):** the selected lane is unchanged
> (market-microstructure-style confirmation); the next diagnostic is **scoped to
> USD_JPY only**, not seven pairs. Rationale and limits:
> [`NEXT_THESIS_SELECTION_DECISION.md`](NEXT_THESIS_SELECTION_DECISION.md) §1a and
> [`NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md`](NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md)
> Lane E amendment. USD_JPY focus is a **research-scoping decision only** — it is **not**
> a claim that USD_JPY has edge and does **not** bring approval or demo any closer.

---

```text
We are starting a forex-bot READ-ONLY USD_JPY-only M15 microstructure confirmation diagnostic sprint.

Branch/worktree:
Create a fresh worktree from current `main`.

Branch name:
research-usdjpy-m15-microstructure-confirmation-diagnostic-001

This is NOT a new strategy implementation sprint.
This is NOT C024 (do not create CAMPAIGN_024).
This is NOT C023 execution.
This is NOT a tuning/threshold-mining sprint.
This is NOT paper/demo/live enablement.
This is USD_JPY ONLY — do not aggregate or test the seven-pair universe.

Context:
The C022/C023 H4/H1 pullback-resolution family is RETIRED
(RETIRED_UNLESS_NEW_EXTERNAL_THESIS). Diagnostics localized C022's failure to the
ENTRY TRIGGER: the M15 EMA-reclaim signal is inert (m15_reclaim_distance_atr AUC
0.494/0.485), all ATR/time stop variants and a cost-free baseline stay negative, and
every structural entry feature sits at AUC ~= 0.50. The selected next lane is
market-microstructure-style confirmation: replace the weak reclaim trigger with
stronger, structurally different proof of an order-flow shift. Per the 2026-05-28
scope amendment, the next diagnostic is scoped to USD_JPY ONLY — the seven-pair
universal rule has repeatedly failed, USD_JPY has repeatedly been "less bad"/near-flat
(never strong enough to promote), and a single pair reduces confounds and speeds
iteration. USD_JPY focus is a research-scoping decision, NOT a claim of edge. See:
  docs/research/C022_C023_PULLBACK_RESOLUTION_FAMILY_CLOSEOUT.md
  docs/research/NEXT_THESIS_SELECTION_DECISION.md   (esp. section 1a + section 5 single-pair note)
  docs/research/NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md   (Lane E amendment)
  docs/research/C022_WINNER_LOSER_FEATURE_SEPARATION_RESULT.md
The C022 per-trade feature reconstruction pattern (lookahead-safe, side-agreement
verified) lives in src/forex_bot/research/c022_entry_features.py and
src/forex_bot/research/feature_separation.py — reuse it; do not edit strategy logic.

Main goal:
Run a READ-ONLY USD_JPY-only diagnostic to determine whether stronger M15
microstructure-confirmation primitives separate USD_JPY winners from losers BETTER
than the old C022 M15 EMA-reclaim trigger. Produce a readiness decision
(READY_FOR_PRECOMMIT / NOT_READY) for a POSSIBLE FUTURE USD_JPY-only C024 — but do not
create C024 in this sprint.

Scope and data:
* USD_JPY ONLY. No seven-pair aggregation; no other pair in the analysis set.
* M15 execution context.
* H1/H4 context ONLY if needed for feature reconstruction (do not broaden the thesis).
* Use the local materialized M15/H1/H4 store READ-ONLY (as in the feature-separation
  sprint); USD_JPY C022 base trades are ~299 by the MFE/MAE diagnostic — report the
  exact USD_JPY train/validation sample sizes at every step and treat small-sample
  separation cautiously.

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
* Do not present any diagnostic separation as tradable edge. USD_JPY focus is NOT proof
  of edge. Any future C024 must be precommitted out-of-sample in a separate sprint.
* Single pair does NOT lower the evidence bar. The five-part C024 readiness bar applies
  unchanged; do not relax gates because it is one pair.

Work in phases. Commit after each meaningful phase.

PHASE 0 — branch, audit, plan
1. Start from current `main`; create the fresh worktree/branch above.
2. Verify: C020/C021/C022 REJECT; C023 scaffold-only/not executed; C024 does not
   exist; approved_strategies.yaml is approved: []; paper/demo/live guards intact.
3. Confirm the USD_JPY C022 base trades + materialized USD_JPY M15/H1/H4 are reachable
   READ-ONLY (as in the feature-separation sprint). Report USD_JPY counts.
4. Run baselines: pytest tests/ -q; ruff check src tests scripts research;
   python scripts/check_research_freeze.py; python scripts/validate_research_archive.py;
   python scripts/scan_artifacts_for_secrets.py. Document any pre-existing failures.
5. Create docs/research/USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_001_PLAN.md
   (purpose, USD_JPY-only scope + rationale + risks, primitive inventory, non-goals,
   safety rules, separation method, readiness bar, validation commands, explicit
   no-C024/no-approval/no-edge-claim statement). Commit.

PHASE 1 — confirmation-primitive inventory (USD_JPY)
Create docs/research/USDJPY_M15_CONFIRMATION_PRIMITIVES_INVENTORY.md. For each
primitive, give a precise, causal, decision-bar-anchored definition and the bars/fields
it needs:
  1. reclaim + impulse candle (body/ATR on the trigger bar),
  2. reclaim + break of prior micro-swing (structure-break confirmation),
  3. reclaim + retest hold (pullback to the reclaimed level holds),
  4. failed reclaim / trap avoidance (reclaim that immediately fails = skip),
  5. liquidity sweep + displacement (stop-run beyond a prior extreme then reversal),
  6. range expansion after compression (NR/contraction then expansion bar),
  7. session-aware behavior — especially Tokyo / London / NY windows for USD_JPY,
  8. spread/ATR and volatility context (USD_JPY-specific cost/vol profile).
Note which are computable from M1/M15 OHLC alone and any that are not. Commit.

PHASE 2 — read-only detectors (USD_JPY)
Implement detectors in src/forex_bot/research/ (NOT in strategy code). Each returns a
boolean/scalar presence per USD_JPY trade/context at its decision bar, reconstructed
read-only from materialized USD_JPY frames. Compare candidate primitives against
USD_JPY C022-style trades and/or reconstructed USD_JPY entry contexts, depending on
available data. Add unit tests proving (a) causality (no post-entry bars used) and
(b) a side-agreement / alignment sanity check. Gitignore any large dataset; commit
manifest + small preview + summary JSON only. Commit.

PHASE 3 — winner/loser separation comparison (USD_JPY)
Reuse the feature-separation method (|AUC-0.5| effect, quintile win-rates, reported
per train/validation split, post-hoc outcome labels kept out of features via a
denylist). Score each primitive's presence on USD_JPY winners vs losers, and explicitly
compare each primitive's separation against the old C022 M15 EMA-reclaim trigger.
Report USD_JPY sample sizes throughout. Create
docs/research/USDJPY_M15_CONFIRMATION_PRIMITIVE_SEPARATION_RESULT.md with the table and
an honest read (negligibility floor 0.05; flag any instability across splits; flag
small-sample fragility). Commit.

PHASE 4 — readiness decision (NO C024 created)
Create docs/research/C024_USDJPY_MICROSTRUCTURE_READINESS_DECISION.md. Answer, for
USD_JPY:
  * Do any USD_JPY-specific M15 confirmation primitives separate winners from losers
    (and do they beat the old EMA-reclaim trigger)?
  * Are they stable between train and validation?
  * Are they plausible (order-flow/liquidity/session logic), not just threshold-mined?
  * Do they reduce straight-to-stop behavior (vs the 45.9% C022 never-reached-+0.25R)?
  * Do they preserve enough USD_JPY sample size to be meaningful?
  * Is there enough evidence to precommit a future USD_JPY-only C024?
  * Or should USD_JPY microstructure confirmation also be rejected/deferred?
Apply the five-part bar from NEXT_THESIS_SELECTION_DECISION.md section 5 (unchanged;
criterion 3 = not session/cost/volatility overfit WITHIN USD_JPY; plus the heightened
single-pair generalization burden). Output READY_FOR_PRECOMMIT or NOT_READY. Create NO
CAMPAIGN_024 and propose NO thresholds regardless of outcome. Commit.

PHASE 5 — final validation + summary
Run pytest / ruff / check_research_freeze / validate_research_archive /
scan_artifacts_for_secrets / git status --short. Verify: no verdict changed; no
strategy approved; approved_strategies.yaml still approved: []; no C024 created; C023
not executed; no paper/demo/live; no broker/executor changes; no OANDA mutation/order
calls; no credentials/DBs/huge artifacts staged. Create
docs/research/USDJPY_M15_MICROSTRUCTURE_CONFIRMATION_DIAGNOSTIC_001_SUMMARY.md (branch,
commit hashes by phase, files by phase, USD_JPY sample sizes, primitives tested,
separation results vs the EMA-reclaim baseline, readiness decision, what would justify
a future USD_JPY-only C024 precommit, verification that nothing was approved/executed,
tests run, pre-existing failures, files to review first, recommended next sprint).
Commit.
```

---

## Notes for whoever runs the above

- **USD_JPY focus is a research-scoping decision, not an edge claim.** Narrowing scope
  does not approve anything, does not bring demo closer, and does not lower the evidence
  bar. A USD_JPY-only result carries a *heightened* generalization burden.
- The prompt deliberately ends at a **readiness decision**, not a campaign. Even a
  `READY_FOR_PRECOMMIT` outcome only unlocks a *separate* USD_JPY-only precommit sprint;
  C024 is never created inside the diagnostic.
- The five-part readiness bar is reproduced from
  [`NEXT_THESIS_SELECTION_DECISION.md`](NEXT_THESIS_SELECTION_DECISION.md) §5 (+ the
  single-pair note) — keep them in sync if either is revised.
- Lane C (cost/tradeability guardrail) is a recommended *companion overlay* for any
  future signal sprint, not part of this diagnostic. USD_JPY's spread/ATR context is
  folded in as detector category 8 above.
- If the USD_JPY sample proves too small for stable train/validation separation, that
  itself is a finding — report it and lean `NOT_READY` rather than over-reading a few
  trades.
