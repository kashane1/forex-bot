# Edge Discovery Lab — Hydrate Sprint 001 Summary

**Sprint id:** `research-edge-discovery-lab-hydrate-001`
**Branch:** `research-edge-discovery-lab-hydrate-001`
**Date opened / closed:** 2026-05-24 (single-day sprint)
**Disposition:** **Reconciliation + real-data hydration delivered.**
No strategy approved; no campaign verdict changed; the research
freeze remains fully intact; paper / demo / live loops still refuse
every configured strategy.

---

## 1. Goal recap

Take the edge-discovery lab from scaffold/demo mode (synthetic
fixtures + CAMPAIGN_005 null) to real local research mode by
(a) reconciling the prior `research-edge-discovery-lab-001` branch
state with the now-merged CAMPAIGN_010-014 artifacts, (b) hydrating
the lab's loaders against real local artifacts where available, and
(c) rerunning the four exploratory studies on real data. **No
strategy approval. No new formal campaign.**

## 2. Branch / base reconciliation result

| item | value |
|---|---|
| current branch | `research-edge-discovery-lab-hydrate-001` |
| base | `main` (`bb739c2` = current `main` HEAD) |
| sprint commits ahead of `main` | 5 (one per phase) |
| relation to prior `research-edge-discovery-lab-001` | strict superset; every prior-sprint file is present and unchanged |
| relation to CAMPAIGN_010-014 artifacts | **present on this branch** because main now includes the merged PR #1 (`research-calendar-event-window-anomaly-walk-forward-001`). The prior sprint's branch pre-dated that merge — the "missing artifacts" were a branch-base / merge-ordering effect, not an artifact-policy exclusion. |

## 3. Commits by phase

| phase | commit | what |
|---|---|---|
| 0 | `ee2ee14` | plan + baseline reconciliation (1,104-test baseline; freeze, archive, secrets all pass) |
| 1 | `f1f31c4` | real artifact inventory (which committed artifacts the lab can ingest; which are local-only; which are genuinely absent) |
| 2 | `9510441` | real-data loaders + provenance dataclass; 26 new tests |
| 3 | `5b9fef4` | four exploratory studies on real data; 22 new smoke tests; 8 new committed outputs under `studies/outputs/real/` |
| 4 | `98bda08` | results + ranking rules addenda; CAMPAIGN_011 replaces CAMPAIGN_005 as the binding null baseline |
| 5 | *(this commit)* | final validation + this summary |

## 4. Files changed

20 files, +4,501 insertions, ~1 deletion (the public-API
`__init__.py` exports list).

### Plan / decision docs (5 files under `docs/research/`)

- [`EDGE_DISCOVERY_LAB_HYDRATE_001_PLAN.md`](EDGE_DISCOVERY_LAB_HYDRATE_001_PLAN.md) — Phase 0 contract.
- [`EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.md`](EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.md) — Phase 1 inventory.
- [`EDGE_DISCOVERY_LAB_HYDRATE_001_RESULTS_ADDENDUM.md`](EDGE_DISCOVERY_LAB_HYDRATE_001_RESULTS_ADDENDUM.md) — Phase 4 results.
- [`EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md`](EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md) — Phase 4 ranking-rules
  bind to CAMPAIGN_011.
- `EDGE_DISCOVERY_LAB_HYDRATE_001_SUMMARY.md` — this file.

### Code under `research/edge_discovery/`

- [`__init__.py`](../../research/edge_discovery/__init__.py) — extended public API; existing exports
  preserved.
- [`real_data.py`](../../research/edge_discovery/real_data.py) — new module (555 lines): H4 SQLite store
  loader with env-var + worktree-aware path resolution, campaign
  walk-forward result loader, per-fold per-pair summary loader,
  per-fold per-pair trade-CSV loader, CAMPAIGN_014 event-fixture
  JSON loader, `StudyProvenance` / `StudyInput` dataclasses with
  `data_kind = "real" | "synthetic-fallback"` enforcement.

### Studies under `research/edge_discovery/studies/`

- [`study_real_event_window.py`](../../research/edge_discovery/studies/study_real_event_window.py) — CAMPAIGN_014 trades × fixture × CAMPAIGN_011 null.
- [`study_real_turnover_cost.py`](../../research/edge_discovery/studies/study_real_turnover_cost.py) — five-campaign per-trade integrity check.
- [`study_real_pair_baseline.py`](../../research/edge_discovery/studies/study_real_pair_baseline.py) — per-pair per-fold expectancy R vs CAMPAIGN_011 null.
- [`study_real_session_by_hour.py`](../../research/edge_discovery/studies/study_real_session_by_hour.py) — real EUR_USD H4 SQLite (with synthetic fallback).

### Study outputs (8 files under `research/edge_discovery/studies/outputs/real/`)

- `real_study_event_window.{json,md}`
- `real_study_pair_baseline.{json,md}`
- `real_study_session_by_hour.{json,md}`
- `real_study_turnover_cost.{json,md}`

The prior sprint's synthetic outputs under
`research/edge_discovery/studies/outputs/` are **byte-identical** to
their pre-sprint state.

### Tests (2 new files under `tests/research/edge_discovery/`)

- [`test_real_data.py`](../../tests/research/edge_discovery/test_real_data.py) — 26 tests covering all the new loaders,
  the H4 SQLite resolver (env, default, worktree-fallback, missing),
  the provenance dataclass invariants, and one real-store smoke test
  guarded by `pytest.skipif` so fresh-clone CI passes.
- [`test_real_studies_smoke.py`](../../tests/research/edge_discovery/test_real_studies_smoke.py) — 22 tests checking the four
  real-data study outputs exist, carry a complete provenance block,
  acknowledge the verdict-word ban, surface the NFP dominance and
  FOMC-zero-trades patterns, and pass the observed-vs-published
  cross-check.

### No files outside these paths were changed

`paper.yaml`, `practice.yaml`, `live.example.yaml`,
`approved_strategies.yaml`, the loops module, the broker module, the
evidence manifest, the evidence index, every `STRATEGY_STATUS.md`,
every `CAMPAIGN_*_STATUS.md`, every
`CAMPAIGN_*_WALK_FORWARD_RESULT.md`: all unchanged.

## 5. Tests / validation run

| check | command | result |
|---|---|---|
| focused edge-discovery suite | `pytest tests/research/edge_discovery -q` | **94 passed** (was 46 on the prior lab sprint's baseline; +48 from this sprint's `test_real_data.py` + `test_real_studies_smoke.py`) |
| full pytest | `pytest tests/ -q` | **1,152 passed** (was 1,104 at Phase 0 baseline; +48 net) |
| ruff (touched areas) | `ruff check research/edge_discovery tests/research/edge_discovery` | **All checks passed!** |
| ruff (repo-wide pre-existing) | n/a | the 3 pre-existing ruff errors in `research/lean_parity/algorithms/campaign_002_h4_baseline/main.py` that the prior lab sprint flagged are still present — **not introduced by this sprint**, see §9 below |
| research-freeze gate | `python scripts/check_research_freeze.py` | **ALL PASSED** (loops refuse `trend_following`; 14 campaigns; 14 diagnostic artifacts; no creds) |
| research-archive validator | `python scripts/validate_research_archive.py` | **ALL PASSED** (282 evidence-index links resolve; no credential strings in 2,787 artifact files) |
| secret scan | `python scripts/scan_artifacts_for_secrets.py` | **PASSED** (pattern scan over 2,879 files; value scan skipped — no creds in env, as expected for a research-only sprint) |
| paper/demo/live refusal | direct `assert_loop_strategies_approved('paper', ['trend_following'])` etc. | **all 3 refuse** (`StrategyNotApprovedError`) |
| import-isolation guard | `tests/research/edge_discovery/test_isolation.py` | **PASSED** — no `forex_bot.broker` / `loops` / `approval` / `execution` imports in the new lab code |

## 6. Real artifacts found vs missing

### Found and consumed (committed to the branch)

- CAMPAIGN_010-014 `walk_forward/results.json` aggregates.
- 280 per-fold per-pair `*_summary.json` files across the 5 campaigns
  (8 folds × 7 pairs each).
- 280 per-fold per-pair `*_trades.csv` files (16,354 total trade
  rows across the 5 campaigns).
- CAMPAIGN_014 calendar event fixture at
  [`research/calendar/fixtures/campaign_014_events.json`](../../research/calendar/fixtures/campaign_014_events.json)
  — 281 events × 5 classes (NFP, FOMC, ECB, BoJ, BoE), 2020-2026
  coverage, with official source URLs.
- Lean-parity H4 provenance JSONs (per-pair sidecars; the actual
  CSVs are gitignored).

### Found but local-only (gitignored)

- H4 OHLC SQLite store at `data/campaign_002.sqlite3` (operator-local,
  ~110 MB, 9,931-9,935 H4 bars per pair × 7 majors, 2020-01-01 →
  2026-05-19). The session study consumed it directly via
  `resolve_h4_store_path` and recorded its real-data provenance.
- Lean-parity H4 CSV exports (gitignored;
  `scripts/export_lean_parity_data.py` can regenerate them).

### Genuinely missing (documented honestly)

- **CPI events.** The committed fixture is NFP / FOMC / ECB / BoJ /
  BoE. The lab reports CPI absence as a limitation in the
  event-window study's provenance block; it does not fabricate CPI
  dates.
- **A committed small-fixture H4 sample** (≤ 1 MB) the lab could use
  on a fresh git clone without depending on the operator's local
  SQLite. This is the "recommended next branch"
  `infra-edge-discovery-h4-store-export-001` in §11 below.

## 7. Studies rerun on real data

| study | input | data_kind | headline result |
|---|---|---|---|
| `study_real_event_window.py` | CAMPAIGN_014 trades (720) + committed fixture + CAMPAIGN_011 null | real | gap to null = −0.1453 R → materially_below_null; NFP 79.3 % dominance; **FOMC has zero matched trades** |
| `study_real_turnover_cost.py` | per-trade ledgers for all 5 CAMPAIGN_010-014 | real | observed = published mean R to 1e-3 R for every campaign; zero campaigns have a positive pre-cost edge |
| `study_real_pair_baseline.py` | 280 per-fold per-pair summary JSONs across 5 campaigns; CAMPAIGN_011 is the null | real | one cell — EUR_USD under CAMPAIGN_012 — cleared the +0.05 R floor (+0.0950 R) |
| `study_real_session_by_hour.py` | real EUR_USD H4 store (9,927 bars, 2020-2026) | real | overall within-null; three hours flagged `materially_above_null` by the band classifier but absolute means are nowhere near the +0.05 R material-gap floor — worked example of the two-screen rule |

## 8. Studies still synthetic-only

The prior sprint's four committed synthetic studies under
`research/edge_discovery/studies/outputs/` remain in place,
**unchanged**:

- `study_event_window.{json,md}` (480-bar GBM fixture)
- `study_turnover_cost.{json,md}` (analytical sweep)
- `study_pair_baseline.{json,md}` (CAMPAIGN_001-009 report citations)
- `study_session.{json,md}` (480-bar GBM fixture)

Their disposition: the synthetic event-window and synthetic session
studies are now **capability checks** — they prove the rig is wired
correctly. The synthetic turnover-cost matrix's shape is still the
canonical analytical reference (the real-data turnover study just
populated its diagonal with 5 rejected real campaigns). The
synthetic pair-baseline citation table is a historical
cross-reference; the real-data version is the binding artifact.

## 9. Key findings (descriptive only — never strategy evidence)

The full table is in
[`EDGE_DISCOVERY_LAB_HYDRATE_001_RESULTS_ADDENDUM.md`](EDGE_DISCOVERY_LAB_HYDRATE_001_RESULTS_ADDENDUM.md). Top-of-stack:

1. **CAMPAIGN_011 replaces CAMPAIGN_005 as the binding null
   baseline.** Same data, same fold layout, same exit logic as a
   future candidate has to face — the apples-to-apples null floor.
2. **The brief's CAMPAIGN_014 NFP-dominance / FOMC-zero-trades
   narrative reproduces exactly on the real data.** 79.3 % NFP
   dominance, 0 FOMC matched trades, gap to null = −0.145 R per
   trade. CAMPAIGN_014 stays REJECT.
3. **No CAMPAIGN_010-014 campaign has a positive pre-cost per-trade
   edge** on the real ledgers (16,354 trades). Lesson 2 (cost /
   turnover is the most common cause of failure) corroborated.
4. **Exactly one (pair, candidate) cell beat the +0.05 R material
   gap vs the per-pair CAMPAIGN_011 null** on real data: EUR_USD
   under CAMPAIGN_012 (regime_switcher_atr_percentile), gap
   +0.0950 R. **Not a graduation** — CAMPAIGN_012 stays REJECT — but
   the single-pair-declared candidate angle is the strongest lab
   follow-up hypothesis.
5. **Two-screen rule clarified:** a proposal must pass BOTH the
   null-band classifier (≥ +1.0 stds) AND the per-pair material-gap
   floor (≥ +0.05 R). The real session study is a worked example
   of those screens diverging.
6. **Observed-vs-published reconciliation** of CAMPAIGN_010-014
   passes cleanly to 1e-3 R precision. The committed trade CSVs
   faithfully reproduce the published walk-forward aggregates —
   freeze-integrity result for the artifacts themselves.

## 10. Approval / safety status (unchanged)

- **Was any strategy approved by this sprint?** No. The approved-
  strategy registry remains `approved: []`.
- **Was any campaign verdict altered?** No. CAMPAIGN_001-014 carry
  their existing verdicts.
- **Is paper trading enabled?** No. `paper-loop` refuses every
  configured strategy (`StrategyNotApprovedError`).
- **Is demo trading enabled?** No. `demo-loop` refuses too.
- **Is live trading enabled?** No. `live` loop refuses; live
  promotion blockers (real financing model + valid D1) still stand.
- **Was the OANDA broker contacted?** No. The lab is import-isolated;
  `tests/research/edge_discovery/test_isolation.py` enforces it and
  still passes after the new module landed.
- **Was any campaign trade ledger modified?** No. The per-fold
  `*_summary.json` and `*_trades.csv` files are read-only inputs;
  every campaign artifact byte is unchanged.

## 11. Known issues (not introduced by this sprint)

- `ruff check` against the full repo still reports 3 errors in
  `research/lean_parity/algorithms/campaign_002_h4_baseline/main.py`
  (unsorted imports, two unused `# noqa` directives), from commit
  `e382af4` (`infra-lean-parity-run-001` Phase 2). The prior lab
  sprint's summary also flagged these. Flagging again so a future
  cleanup sprint can pick them up; nothing in `research/edge_discovery`
  triggers them.
- The H4 SQLite store remains operator-local-only. A future
  `infra-edge-discovery-h4-store-export-001` sprint could materialize
  a small ≤ 1 MB committed fixture so fresh-clone CI runs the real
  session study without the `synthetic-fallback` path. Not in scope
  for this sprint.
- The CAMPAIGN_014 event fixture has NFP / FOMC / ECB / BoJ / BoE
  but no CPI events. Adding CPI would require a Phase-1-style
  data-provenance sprint with official source citations; not done
  here.

## 12. Exact files to review first

For a ~12-minute review pass, in this order:

1. [`docs/research/EDGE_DISCOVERY_LAB_HYDRATE_001_PLAN.md`](EDGE_DISCOVERY_LAB_HYDRATE_001_PLAN.md) §4 — branch /
   base reconciliation explanation.
2. [`docs/research/EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.md`](EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.md) §3 — what is
   committed vs operator-local vs genuinely absent.
3. [`research/edge_discovery/studies/outputs/real/real_study_event_window.md`](../../research/edge_discovery/studies/outputs/real/real_study_event_window.md) —
   the NFP-dominance / FOMC-zero-trades / gap-below-null result.
4. [`research/edge_discovery/studies/outputs/real/real_study_pair_baseline.md`](../../research/edge_discovery/studies/outputs/real/real_study_pair_baseline.md) —
   the EUR_USD / CAMPAIGN_012 +0.0950 R cell.
5. [`docs/research/EDGE_DISCOVERY_LAB_HYDRATE_001_RESULTS_ADDENDUM.md`](EDGE_DISCOVERY_LAB_HYDRATE_001_RESULTS_ADDENDUM.md) §3 —
   what changed and what still holds after real artifacts.
6. [`docs/research/EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md`](EDGE_DISCOVERY_HYDRATE_RANKING_RULES_ADDENDUM.md) §A — the
   CAMPAIGN_011 null replaces CAMPAIGN_005 reasoning.
7. [`tests/research/edge_discovery/test_real_studies_smoke.py`](../../tests/research/edge_discovery/test_real_studies_smoke.py) — the
   regression-guard for the verdict-word ban and the NFP-dominance /
   FOMC-zero-trades patterns.

## 13. Recommended next branch

- `research-edge-discovery-lab-single-pair-probe-001` — a focused
  lab study that probes the EUR_USD / CAMPAIGN_012 +0.0950 R cell
  for (a) per-fold consistency (is one fold carrying it?), (b)
  cost-stress robustness at 2×, (c) the ECB / BoE shorts-only
  sub-slice. Lab follow-up; not a campaign. Single-script extensions
  of the existing real-data studies.

- `infra-edge-discovery-h4-store-export-001` — make a small,
  reproducible local export script that materializes a committed
  ≤ 1 MB fixture H4 store the lab can use without depending on the
  operator's local OANDA snapshot.

- (Optional, only if the §1 probe surfaces something) — once the
  single-pair probe lands, a *real candidate proposal* (still not a
  campaign) drafted against the updated ranking rules' §1 + the new
  §A binding null. The ranking rules' §1.5 single-pair declared-
  candidate path is the contract.

This sprint takes no position on which of these comes next; it just
makes all three possible.
