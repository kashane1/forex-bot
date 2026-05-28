# Post-C022 — USD_JPY Scope Amendment Summary

**Date:** 2026-05-28 · **Type:** research-scoping amendment. Approves nothing, executes
nothing, creates no campaign, changes no verdict, claims no edge.

> Amendment to the completed
> [`POST_C022_FAMILY_RETIREMENT_AND_NEW_THESIS_SELECTION_001_SUMMARY.md`](POST_C022_FAMILY_RETIREMENT_AND_NEW_THESIS_SELECTION_001_SUMMARY.md).
> The selected next lane is **unchanged** (market-microstructure-style confirmation
> diagnostic); the next diagnostic sprint's **scope is narrowed to USD_JPY only**.

## 1. Branch

`research-post-c022-family-retirement-and-new-thesis-selection-001` (same branch as the
closeout sprint; no new branch created, per instruction).

## 2. Commit hashes for this amendment

| Phase | Hash | Title |
|---|---|---|
| A | `26a528f` | amend selection to USD_JPY-only scope |
| B | `b0df102` | reframe single-pair lane as USD_JPY scope |
| C | `b67e49a` | amend next-sprint prompt to USD_JPY-only |
| D | _this commit_ | final validation + scope-amendment summary |

## 3. Files changed

Amendment edits (Phases A–C): 3 files, +223 / −73 lines.

- **A:** `docs/research/NEXT_THESIS_SELECTION_DECISION.md` — new §1a (USD_JPY-only scope
  + justification + risks), §4 deliverables scoped to the USD_JPY subset, §5 single-pair
  note (no gate-lowering).
- **B:** `docs/research/NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md` — Lane E reframed:
  single-pair is *not* a standalone thesis; USD_JPY adopted as the *scope* for Lane D,
  with the seven-pair-vs-USD_JPY comparison and the "not approval / not C024 / not demo"
  limits; scoring-table row + Reading section updated.
- **C:** `docs/research/NEXT_SPRINT_PROMPT_AFTER_C022_FAMILY_CLOSEOUT.md` — rewritten for
  USD_JPY-only scope: new branch name
  `research-usdjpy-m15-microstructure-confirmation-diagnostic-001`, USD_JPY-only
  data/scope rules, eight detector categories (incl. Tokyo/London/NY session-aware and
  spread/ATR+vol context), and the explicit output questions.
- **D:** this file (new).

No source/strategy/broker/executor/config-gate code changed; docs only.

## 4. Selected lane (confirmed unchanged)

**Market-microstructure-style confirmation diagnostic.** The amendment does not change
*what* is being investigated — it still replaces the inert M15 EMA-reclaim trigger with
stronger, structurally different confirmation primitives.

## 5. Next scope (confirmed)

**USD_JPY only.** The next diagnostic sprint runs on USD_JPY alone (M15 execution
context; H1/H4 only if needed for feature reconstruction; local materialized store
read-only; no seven-pair aggregation).

## 6. Why USD_JPY-only is justified as a research diagnostic

- Seven-pair universal rules have repeatedly failed (C010, C015–C017, C020–C022); a
  universal static rule may be too blunt for *discovery*.
- Single-pair research reduces confounding (one spread/volatility/session profile) and
  speeds iteration (~1/7 the data per run).
- USD_JPY has repeatedly been "less bad" / near-flat in prior failed evidence — the most
  defensible single pair to interrogate first (not because it has edge — it does not).
- Clearer session (Tokyo/London/NY), spread/ATR, and macro personality → results are
  interpretable rather than a superposition of seven pairs.
- Operationally cleaner for eventual paper/demo monitoring *if* a strategy ever earned
  it (far-future consideration only).
- Still **diagnostic only** — read-only winner/loser separation on a narrowed scope.

## 7. Overfit risks and evidence-standard warnings

- **Higher overfit risk** on a single pair; mitigated by per-split reporting, the 0.05
  negligibility floor, and keeping post-hoc labels out of features.
- **Smaller sample** (USD_JPY ≈ 299 C022 base trades); sample-size preservation is an
  explicit output, and small-sample separation is treated cautiously.
- **Stricter walk-forward discipline later** — any future USD_JPY campaign needs a clean
  train/validation/test lockbox; single-pair results carry a *heightened* generalization
  burden.
- **No gate-lowering** — the five-part C024 readiness bar applies unchanged; "it's only
  one pair" is never grounds to relax it.
- **Not approval-adjacent** — USD_JPY focus is not proof of edge and brings paper/demo/live
  no closer.

## 8. C023 not executed

**Confirmed.** C023 remains scaffold-only / not executed; no execution occurred.

## 9. C024 not created

**Confirmed.** No CAMPAIGN_024 exists; readiness remains `NOT_READY`; the amended prompt
still ends at a readiness decision and creates no C024.

## 10. No strategy approved

**Confirmed.** `configs/approved_strategies.yaml` remains `approved: []`.

## 11. Paper/demo/live remain blocked

**Confirmed.** No broker/executor/order/live code touched; no OANDA mutation/order
calls; freeze gate `loops_refuse` still passes.

## 12. Tests and validations run (Phase D)

| command | result |
|---|---|
| `pytest tests/ -q` | **1967 passed, 3 skipped** (data-dependent skips). |
| `ruff check src tests scripts research` | **All checks passed.** |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED.** |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED.** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** — pattern scan over 5318 files clean; value scan SKIPPED (no real OANDA credentials sourced in this environment — expected safe state for a docs-only amendment). |
| `git status --short` | clean (all work committed). |

## 13. Exact files to review first

1. [`NEXT_THESIS_SELECTION_DECISION.md`](NEXT_THESIS_SELECTION_DECISION.md) — §1a (USD_JPY scope) + §5 single-pair note.
2. [`NEXT_SPRINT_PROMPT_AFTER_C022_FAMILY_CLOSEOUT.md`](NEXT_SPRINT_PROMPT_AFTER_C022_FAMILY_CLOSEOUT.md) — the amended USD_JPY-only prompt.
3. [`NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md`](NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md) — Lane E amendment.

## 14. Final next-sprint prompt location

[`docs/research/NEXT_SPRINT_PROMPT_AFTER_C022_FAMILY_CLOSEOUT.md`](NEXT_SPRINT_PROMPT_AFTER_C022_FAMILY_CLOSEOUT.md)
— branch `research-usdjpy-m15-microstructure-confirmation-diagnostic-001`.
