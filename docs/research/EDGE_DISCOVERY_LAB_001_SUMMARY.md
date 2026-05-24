# Edge Discovery Lab — Sprint 001 Summary

**Sprint id:** `research-edge-discovery-lab-001`
**Branch:** `research-edge-discovery-lab-001`
**Date opened / closed:** 2026-05-24 (single-day sprint)
**Disposition:** **Process improvement delivered.** No strategy
approved; no campaign verdict changed; the research freeze remains
fully intact; paper / demo / live loops still refuse every configured
strategy.

---

## 1. Goal recap

Build a lightweight local edge-discovery workbench so future signal
ideas can be tested cheaply *before* any one of them is scaffolded
into a full formal campaign. Apply the recent meta-analysis lessons.
Do not approve a strategy. Do not start a new formal campaign.

## 2. Commits by phase

| phase | commit | what |
|---|---|---|
| 0 | `c11f47a` | plan + baseline freeze run |
| 1 | `5dce263` | failed-campaign meta-analysis |
| 2 | `9c9f10a` | edge-discovery utility module + tests |
| 3 | `b8cbcc5` | four exploratory studies + outputs |
| 4 | `8103d79` | lab results + candidate ranking rules |
| 5 | *(this commit)* | tests, docs, final validation, summary |

## 3. Files changed

34 files, +4,861 lines, 0 deletions.

Plan / decision docs (5 files under `docs/research/`):

- [`docs/research/EDGE_DISCOVERY_LAB_001_PLAN.md`](EDGE_DISCOVERY_LAB_001_PLAN.md) — Phase 0 lab contract.
- [`docs/research/FAILED_CAMPAIGN_META_ANALYSIS_001.md`](FAILED_CAMPAIGN_META_ANALYSIS_001.md) — Phase 1 cross-cut and lessons.
- [`docs/research/EDGE_DISCOVERY_LAB_001_RESULTS.md`](EDGE_DISCOVERY_LAB_001_RESULTS.md) — Phase 4 results.
- [`docs/research/EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md`](EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md) — Phase 4 graduation contract.
- `docs/research/EDGE_DISCOVERY_LAB_001_SUMMARY.md` — this file.

Utility module (5 files under `research/edge_discovery/`):

- [`research/edge_discovery/__init__.py`](../../research/edge_discovery/__init__.py) — public API.
- [`research/edge_discovery/loaders.py`](../../research/edge_discovery/loaders.py) — candle + event loaders with SHA-256 provenance.
- [`research/edge_discovery/windows.py`](../../research/edge_discovery/windows.py) — fixed-window signed forward-return computation.
- [`research/edge_discovery/costs.py`](../../research/edge_discovery/costs.py) — cost overlay (spread + slip + financing stress).
- [`research/edge_discovery/null.py`](../../research/edge_discovery/null.py) — seeded random-entry null + descriptive band.
- [`research/edge_discovery/report.py`](../../research/edge_discovery/report.py) — JSON + Markdown reporter with verdict-word ban.

Sample fixtures (3 files):

- [`research/edge_discovery/sample_fixtures/synthetic_EUR_USD_H4.csv`](../../research/edge_discovery/sample_fixtures/synthetic_EUR_USD_H4.csv) — 480 H4 bars, seed-42 deterministic.
- [`research/edge_discovery/sample_fixtures/synthetic_events.csv`](../../research/edge_discovery/sample_fixtures/synthetic_events.csv) — 6 events × 3 classes.
- [`research/edge_discovery/sample_fixtures/_generate_fixtures.py`](../../research/edge_discovery/sample_fixtures/_generate_fixtures.py) — deterministic regenerator.

Exploratory studies (4 scripts + 8 committed outputs):

- [`research/edge_discovery/studies/study_event_window.py`](../../research/edge_discovery/studies/study_event_window.py) + [`.../outputs/study_event_window.{json,md}`](../../research/edge_discovery/studies/outputs/study_event_window.md)
- [`research/edge_discovery/studies/study_turnover_cost.py`](../../research/edge_discovery/studies/study_turnover_cost.py) + [`.../outputs/study_turnover_cost.{json,md}`](../../research/edge_discovery/studies/outputs/study_turnover_cost.md)
- [`research/edge_discovery/studies/study_pair_baseline.py`](../../research/edge_discovery/studies/study_pair_baseline.py) + [`.../outputs/study_pair_baseline.{json,md}`](../../research/edge_discovery/studies/outputs/study_pair_baseline.md)
- [`research/edge_discovery/studies/study_session.py`](../../research/edge_discovery/studies/study_session.py) + [`.../outputs/study_session.{json,md}`](../../research/edge_discovery/studies/outputs/study_session.md)

Tests (7 files under `tests/research/edge_discovery/`):

- `test_loaders.py`, `test_windows.py`, `test_costs.py`, `test_null.py`,
  `test_report.py`, `test_isolation.py`, plus `__init__.py`. 46 tests.

No files outside these paths were changed. No edits to
`paper.yaml`, `practice.yaml`, `live.example.yaml`,
`approved_strategies.yaml`, the loops module, the broker module,
the evidence manifest, the evidence index, or `STRATEGY_STATUS.md`.

## 4. Tests / validation run

| check | result | notes |
|---|---|---|
| `pytest tests/research/edge_discovery -q` | **46 passed** | new lab suite |
| `pytest tests/ -q` | **838 passed** | full repo suite |
| `ruff check research/edge_discovery tests/research/edge_discovery` | **clean** | touched-area lint |
| `ruff check` (repo-wide) | **3 pre-existing errors in `research/lean_parity/algorithms/campaign_002_h4_baseline/main.py`** | not introduced by this sprint — see [§9 known issues](#9-known-issues-not-introduced-by-this-sprint) |
| `python scripts/check_research_freeze.py` | **ALL PASSED** | registry empty, archive consistent, loops refuse, no credentials |
| `python scripts/validate_research_archive.py` | **ALL PASSED** | 9 campaigns + 14 diagnostic artifacts, all non-approval verdicts |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** | pattern scan over 2,078 artifact files; value scan skipped (no creds in env, as expected for research-only sprint) |
| paper/demo/live loop refusal | **all 3 refuse** | direct invocation of `assert_loop_strategies_approved` |

## 5. Key meta-analysis findings (Phase 1)

The full table and per-row notes live in
[`FAILED_CAMPAIGN_META_ANALYSIS_001.md`](FAILED_CAMPAIGN_META_ANALYSIS_001.md). The top-of-stack
distillations the ranking rules now enforce:

- **Random-entry null is the bar to clear**, not zero. CAMPAIGN_005
  established the universe mean at **−0.095 R**.
- **Cost / turnover is the most common cause of failure** in the
  archive (CAMPAIGN_002 H4/H1, CAMPAIGN_004, plus the brief's
  CAMPAIGN_012 / 013 narrative).
- **Pair concentration** repeats across CAMPAIGN_002 / 003 / 007
  (only EUR_USD or USD_JPY positive); celebrating without
  diagnosing is the trap.
- **Validation-only positivity** (CAMPAIGN_008 6/6 val positive +
  train negative) is the highest-overfit pattern in the archive;
  CAMPAIGN_009 confirmed it falsifies under a single-rule rescue.
- **Infrastructure blockers** (CAMPAIGN_006 D1 untestable) must be
  classified separately or they poison the meta-stats.
- **Event-window studies** must surface dominance-share and
  zero-trade-class slices — the brief's CAMPAIGN_014 NFP/FOMC
  pattern is exactly the failure mode to make visible.

## 6. Exploratory studies completed (Phase 3)

Four studies — all illustrative, all explicitly **not** strategy
evidence — committed with their JSON + Markdown outputs:

1. **`study_event_window.py`** on the synthetic event + H4 fixtures.
   Output is `within_null` on the aggregate (as expected — synthetic
   data has no real event behavior). The point is the structure: per-
   class breakdown, dominance share, zero-trade-class flag, null
   comparison, SHA-256 provenance — all present and reproducible.
2. **`study_turnover_cost.py`** — analytical (no candle input).
   Materialized the cost-per-trade for an EUR_USD-shape midprice as
   `+0.000173` log-units round-trip. The matrix shows that any
   per-trade pre-cost edge below the cost-per-trade makes turnover
   strictly harmful — operationalized as ranking-rule §1.4 and §4.
3. **`study_pair_baseline.py`** — pulled verbatim per-pair numbers
   from committed CAMPAIGN_002–009 reports and CAMPAIGN_005's random-
   entry baseline. Per-pair table includes a "test-window above-null
   count" and a "validation-only above-null count" so the
   high-overfit-risk pattern from Lesson 4 is visible at a glance.
4. **`study_session.py`** — capability check on the synthetic H4
   fixture; per-UTC-hour means cluster within ~0.02 null stds, which
   is the right behavior for synthetic GBM data and validates the rig.

## 7. Top candidate hypotheses ranked (Phase 4)

From [`EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md`](EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md) §6 — *lab studies*,
not campaigns. None of these is authorized to produce a strategy
verdict; they are the next things the lab should run when real
inputs land:

1. **Real-event-window study** (NFP / FOMC / CPI 2020–2026 × 6 majors)
   — direct test of the brief's CAMPAIGN_014 narrative; cheapest to run
   once an event fixture exists.
2. **Real-data turnover-cost validation** on each rejected campaign's
   per-trade edge — grounds the lab's cost arithmetic so the cost-
   stress gate is artifact-backed.
3. **Pair-level, regime-conditioned forward-return profile** on the
   hydrated H4 store — the broadest descriptive map the lab can
   offer before any single candidate is proposed.
4. (Optional) Day-of-week × time-of-day cross study.
5. (Optional) Bias-of-fixtures audit.

The first lab finding that satisfies all seven §1 graduation gates
and zero §2 red flags would be the first candidate the lab can
honestly hand to the formal campaign machinery as a pre-commit
proposal.

## 8. Approval / safety status (unchanged)

- **Was any strategy approved by this sprint?** No. The approved-
  strategy registry remains empty.
- **Was any campaign verdict altered?** No. CAMPAIGN_001–009 carry
  their existing verdicts; the evidence manifest, evidence index, and
  `STRATEGY_STATUS.md` are byte-identical.
- **Is paper trading enabled?** No. `paper-loop` refuses every
  configured strategy.
- **Is demo trading enabled?** No. `demo-loop` refuses every
  configured strategy.
- **Is live trading enabled?** No. `live` loop refuses too; the
  live-promotion blockers (real financing model + valid D1) still
  stand per `FUTURE_RESEARCH_BACKLOG.md`.
- **Was the OANDA broker contacted?** No. The lab is import-isolated
  away from `forex_bot.broker`; `tests/research/edge_discovery/
  test_isolation.py` enforces it.

## 9. Known issues (not introduced by this sprint)

- `ruff check` reports 3 errors in
  `research/lean_parity/algorithms/campaign_002_h4_baseline/main.py`
  (unsorted imports, two unused `# noqa` directives). These come from
  commit `e382af4` (`infra-lean-parity-run-001` Phase 2). They are
  outside the edge-discovery scope; flagging them here so a future
  cleanup sprint can pick them up.

## 10. Blockers / limitations honestly recorded

- **CAMPAIGN_010 – CAMPAIGN_014 referenced in the sprint brief are
  not committed as artifacts in this branch.** The artifact-backed
  null baseline used throughout the sprint is CAMPAIGN_005, not
  CAMPAIGN_011. The meta-analysis treats the brief's 010–014
  narrative as sprint-brief context; if those artifacts land later,
  Phase 1's table extends naturally and the ranking rules' §3 will
  re-anchor its null cite to those campaigns.
- **No real H4 OHLC CSV is committed for the seven majors.** The
  lab's loaders work against any CSV in the d1_aggregation sample
  shape, so the same study scripts run unchanged against a hydrated
  local store — but the committed run is on synthetic fixtures.
- **No real NFP / FOMC / CPI event fixture is committed.** The
  event-window study runs on a 6-event synthetic fixture for
  reproducibility; a real fixture is the next-3-studies item 1.

## 11. Exact files to review first

For a 10-minute review pass, in this order:

1. [`docs/research/EDGE_DISCOVERY_LAB_001_PLAN.md`](EDGE_DISCOVERY_LAB_001_PLAN.md) — what the lab is *for*
   and what it may not do.
2. [`docs/research/FAILED_CAMPAIGN_META_ANALYSIS_001.md`](FAILED_CAMPAIGN_META_ANALYSIS_001.md) — the ten
   reusable lessons the rest of the sprint encodes.
3. [`docs/research/EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md`](EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md) — the
   actual gates a candidate has to clear before a human writes a
   pre-commit.
4. [`research/edge_discovery/studies/outputs/study_pair_baseline.md`](../../research/edge_discovery/studies/outputs/study_pair_baseline.md) —
   the only study output that synthesizes existing artifact-backed
   numbers; useful sanity check.
5. [`research/edge_discovery/studies/outputs/study_turnover_cost.md`](../../research/edge_discovery/studies/outputs/study_turnover_cost.md) —
   the cost/turnover matrix the ranking rules cite.
6. [`tests/research/edge_discovery/test_isolation.py`](../../tests/research/edge_discovery/test_isolation.py) — the
   guard that keeps the lab from drifting into the broker / loops /
   approval modules.
7. [`tests/research/edge_discovery/test_report.py`](../../tests/research/edge_discovery/test_report.py) — the
   verdict-word ban; the one test that proves the lab refuses to
   write an "APPROVE" sentence.

If anything in the lab needs to change, the right knob is usually in
`EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md` (decision rules) — the
code is small and intentionally boring.
