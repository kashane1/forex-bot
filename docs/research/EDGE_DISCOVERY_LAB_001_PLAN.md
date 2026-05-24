# Edge Discovery Lab — Sprint 001 Plan

**Sprint id:** `research-edge-discovery-lab-001`
**Branch:** `research-edge-discovery-lab-001`
**Date:** 2026-05-24
**Scope:** Research process improvement — a lightweight local
exploratory workbench. Not a strategy campaign, not paper / demo / live
trading, not a promotion sprint. The research freeze remains intact.

---

## 1. Purpose

Recent formal campaigns have repeatedly rejected strategy candidates.
The campaign machinery itself is sound — that is *why* it rejected
them — but it is **expensive per hypothesis**: it requires a frozen
strategy module, a pre-commit gate document, split discipline, the
RiskEngine wired in, robustness sweeps, financing stress, report
generation, etc. That makes it the wrong tool for the question "is
there even *any* signal here?"

The edge-discovery lab is the cheap pre-stage. It answers the question:

> Is there a measurable, repeatable, post-cost effect in this idea that
> would make a full campaign worth the cost?

If the answer is "no" or "noisy," the lab kills the idea at low cost
and the campaign machinery is never spun up. If the answer is "yes —
and here is the post-cost effect size, the trade-count budget, and the
random-baseline comparison," the lab outputs a candidate that is
*ready* for a formal pre-commit and campaign.

## 2. What counts as exploratory evidence

A lab study may legitimately claim:

- **Direction.** "Over window *W*, pair *P*, after condition *C*, the
  mean forward return is *μ* with std *σ* and *n* observations."
- **Comparison to a null.** "*μ* differs from the random-entry /
  no-trade null by *Δ*, with bootstrap CI [*l*, *u*]."
- **Cost sensitivity.** "Pre-cost effect is *e*; subtracting a
  spread+slippage cost model knocks it down to *e′*; at *N* trades the
  cost burden is *C*."
- **Concentration.** "*k* of *n* pairs / event classes / sessions
  contribute the majority of the effect — concentration ratio *r*."
- **Robustness sketch.** "Effect persists / does not persist across
  *m* coarse parameter perturbations."

A lab study **MUST**:

- declare its source data and the exact row-count it uses,
- name the comparison baseline (the null) it ran against,
- report pre-cost **and** post-cost effect,
- report *n*, std, and a bootstrap or permutation CI for any claim,
- treat all p-values as descriptive — multiple-testing is not
  controlled at lab scope, so significance language is banned,
- emit a compact JSON + Markdown artifact so future studies can
  reproduce or compare.

## 3. What the lab is NOT allowed to prove

The lab **cannot**, ever:

- approve a strategy. The approval registry remains empty.
- emit a verdict word — `APPROVE`, `PASS`, `GO`, `PROMOTE`, etc. are
  reserved for the formal campaign machinery.
- produce a "result" that can be cited as live / paper / demo evidence.
- promote, demote, re-open, or alter any historical campaign verdict.
- use private OANDA credentials, hit any broker endpoint, or fetch new
  market data. It runs only against committed local research artifacts.
- write into `configs/approved_strategies.yaml`, `paper.yaml`,
  `practice.yaml`, or `live.example.yaml`.
- run inside a paper / demo / live loop. The lab is import-isolated to
  `research/edge_discovery/` and called only from scripts or tests.

A lab finding is **a candidate hypothesis with cheap supporting
evidence**, never a strategy.

## 4. Graduation: lab study → formal campaign

A lab finding may be proposed for graduation to a formal pre-commit +
campaign **only if** all five of the following hold. The lab itself
does not graduate anything; it produces the evidence packet a human
reviews.

1. **Replicable.** Re-running the same study on the same artifacts
   reproduces the headline metric to within numerical noise (hash of
   inputs identical, summary stats stable).
2. **Post-cost positive in a non-trivial slice.** After applying a
   conservative spread + slippage model, the effect is positive on at
   least one slice (pair, event class, or session) that contains
   *n ≥ 30* observations.
3. **Beats the random-entry null.** The post-cost effect is materially
   above the random-entry baseline established in
   `backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md` (mean −0.095 R across
   6 majors). The lab reports the gap explicitly.
4. **Not turnover-amplified.** The lab's turnover/cost study shows that
   scaling trade count does not amplify a small negative edge into a
   large one — i.e. the effect survives at lower turnover too. (Direct
   lesson from prior rejected campaigns, see Phase 1 meta-analysis.)
5. **Pair-concentrated diagnosis is honest.** If the effect lives on
   *one* pair the proposal must say so. Single-pair findings are not
   automatically disqualified, but the formal campaign pre-commit must
   be written for that pair only with appropriately small expectations.

Graduation produces a *pre-commit proposal document* in
`docs/research/` following the established pattern
(`CAMPAIGN_00X_PRECOMMIT.md`); the lab evidence packet (JSON + MD) is
linked from that pre-commit. The lab itself never produces a
pre-commit.

## 5. Required safety constraints

Hard rails for the sprint:

- **No new broker traffic.** No imports from `forex_bot.broker.oanda`
  or equivalents that would hit the network. The lab module reads only
  from committed artifacts.
- **No new credential surfaces.** `scripts/scan_artifacts_for_secrets.py`
  remains green throughout the sprint.
- **Research freeze stays green.** `scripts/check_research_freeze.py`
  passes at the end of the sprint with the same set of checks (registry
  empty, archive consistent, loops refuse, no credentials).
- **No paper/demo/live wiring change.** No edits to `paper.yaml`,
  `practice.yaml`, `live.example.yaml`, `approved_strategies.yaml`, or
  to the loop modules under `src/forex_bot/loops.py`.
- **No campaign verdict mutation.** The evidence index, manifest,
  approval registry, and STRATEGY_STATUS.md are not changed by this
  sprint.
- **Verdict-word ban inside lab outputs.** Lab study outputs may not
  contain `APPROVE`, `PASS` (as a gate result), `GO`, `PROMOTE` for any
  strategy claim. Descriptive words ("positive", "negative",
  "indistinguishable from null") are fine.
- **No same-bar-fill tricks.** Where a study computes forward returns
  from a "signal" timestamp, it must use the close of the signal bar
  as the entry reference (or document explicitly when it does
  otherwise). This mirrors the existing `signal_bar_close` fill model
  in the backtester and prevents subtle look-ahead.

## 6. Expected artifacts

By sprint close the branch contains:

- `docs/research/EDGE_DISCOVERY_LAB_001_PLAN.md` *(this file)*.
- `docs/research/FAILED_CAMPAIGN_META_ANALYSIS_001.md` — Phase 1.
- `research/edge_discovery/` — small reusable utility module.
- 2–4 exploratory study scripts and their JSON + Markdown outputs,
  committed under `research/edge_discovery/studies/`.
- `docs/research/EDGE_DISCOVERY_LAB_001_RESULTS.md` — Phase 4
  consolidated results.
- `docs/research/EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md` — the
  decision rules for what graduates and what dies in the lab.
- Tests for the lab utilities under `tests/research/edge_discovery/`.
- `docs/research/EDGE_DISCOVERY_LAB_001_SUMMARY.md` — final sprint
  summary.

No changes outside these paths except:

- a small `README.md` link block under the existing research-frozen
  status section, if useful for discoverability, and
- nothing else.

## 7. Validation plan

A research-only sprint runs the lighter of the standard validation
suites:

- `python scripts/check_research_freeze.py` — registry empty, archive
  consistent, loops refuse, no credentials. Must pass at sprint close.
- `python scripts/validate_research_archive.py` — already invoked by
  the freeze gate, but called separately for clean reporting.
- `python scripts/scan_artifacts_for_secrets.py` — pattern scan over
  committed artifacts (value scan only runs when credentials are in
  the environment; that is fine).
- `python -m pytest tests/research/edge_discovery -q` — focused tests
  for the new utility module.
- `python -m pytest tests/ -q` — full unit suite, to catch incidental
  breakage. Expected runtime is modest because the lab adds new tests,
  not new I/O-heavy fixtures.
- `ruff check research/edge_discovery scripts tests/research/edge_discovery`
  on touched areas.

If any of these fail, the sprint reports it honestly in the summary
rather than weakening the check.

## 8. Phase plan

| phase | output | commit |
|---|---|---|
| 0 | this plan + baseline freeze run | one commit |
| 1 | `FAILED_CAMPAIGN_META_ANALYSIS_001.md` | one commit |
| 2 | `research/edge_discovery/` utility module + tests | one commit |
| 3 | 2–4 exploratory studies + JSON/MD outputs | one commit |
| 4 | `EDGE_DISCOVERY_LAB_001_RESULTS.md` + ranking rules | one commit |
| 5 | full test/validation run, `EDGE_DISCOVERY_LAB_001_SUMMARY.md` | one commit |

Each commit message follows the existing `Phase N (sprint-id): …`
convention.

## 9. Known asymmetries up-front

Honest notes that shape the sprint:

- **CAMPAIGN_010–014 referenced in the brief are not committed as
  artifacts in this branch.** The committed campaign artifacts are
  CAMPAIGN_001–009. The random-entry / null baseline is therefore
  CAMPAIGN_005 ("Benchmarks & Diagnostics"), not CAMPAIGN_011. The
  Phase 1 meta-analysis treats the brief's stated 010–014 findings
  (turnover amplification, NFP / FOMC behavior, H4 post-event
  mean-reversion rejection) as **sprint-brief context** that informs
  the lab design — they are noted as such and the lessons are
  incorporated even though the raw artifacts could not be located. If
  those artifacts land later, the meta-analysis can be updated; the
  ranking rules already encode the lessons.
- **No NFP / FOMC event-fixture file exists in the repo today.** The
  Phase 3 event-window study is therefore implemented as a *capability*:
  the loader, window builder, and reporter all work end-to-end on a
  small synthetic event fixture committed under
  `research/edge_discovery/sample_fixtures/`. When a real event
  fixture is supplied (e.g. as a CSV of event timestamps + class), the
  same study runs against it unchanged. This is honest "build the rig,
  validate on synthetic, document the gap."
- **No committed H4 OHLC CSV / parquet for the seven majors exists in
  this branch.** Real H4 candles were last fetched into a local SQLite
  store (`data/campaign_002.sqlite3` is referenced by CAMPAIGN_002 /
  005 / 008 / 009) which is not committed (per `.gitignore`). The lab
  is therefore designed to:
    1. consume a small committed sample (the existing
       `research/d1_aggregation/sample_EUR_USD_H4_to_D1.csv`) for
       reproducible study output, and
    2. accept any equivalently-shaped CSV path so the same study can
       be re-run against the local SQLite-derived store when a
       researcher hydrates it.
  The lab does NOT trigger a hydration of the broker store as a side
  effect.

These constraints make the sprint a *lab construction + small
illustrative studies* sprint, not a "discover an edge today" sprint.
That matches the brief: "Build a lightweight local edge-discovery
workbench so we can test many signal ideas cheaply before turning any
one idea into a full formal campaign."
