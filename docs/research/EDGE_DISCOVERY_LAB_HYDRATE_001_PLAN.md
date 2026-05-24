# Edge Discovery Lab — Hydrate Sprint 001 Plan

**Sprint id:** `research-edge-discovery-lab-hydrate-001`
**Branch:** `research-edge-discovery-lab-hydrate-001`
**Opened:** 2026-05-24
**Disposition:** **Reconciliation and real-data hydration only.**
No strategy approved; no campaign verdict changed; the research
freeze remains intact; paper / demo / live loops still refuse every
configured strategy; no broker endpoints will be contacted.

---

## 1. Why this sprint exists

The prior sprint `research-edge-discovery-lab-001` shipped a working
local-research workbench but its
[summary](EDGE_DISCOVERY_LAB_001_SUMMARY.md) flagged three honest
limitations that mean **the lab has never actually been pointed at
the real research artifacts it was designed to ingest**:

1. The artifact-backed null baseline used was **CAMPAIGN_005**
   because CAMPAIGN_010–014 were not committed on that branch.
2. The four exploratory studies ran on a **synthetic 480-bar GBM
   fixture** and a **6-event synthetic calendar** — no real H4 OHLC
   for the seven majors, no real NFP/FOMC/CPI fixture.
3. The brief's CAMPAIGN_014 "event-window continuation vs reversal"
   narrative was treated as **brief context**, not as a study run on
   the real CAMPAIGN_014 fold results.

Before the lab is allowed to rank the next strategy candidate it
must be reconciled with the actual latest research state. That is
the entire scope of this sprint.

## 2. What this sprint will change

- Extend `research/edge_discovery/loaders.py` (and minimally one
  small companion module if cleaner) so the lab can ingest **real
  local artifacts that are already committed in this branch**:
  the committed CAMPAIGN_010–014 walk-forward result JSONs, the
  committed CAMPAIGN_014 event fixture
  (`research/calendar/fixtures/campaign_014_events.json`), the
  committed per-fold per-pair trade CSVs, and the lean-parity H4
  provenance manifests where they help establish coverage.
- Rerun the four studies against real artifacts wherever they exist
  in this branch. Outputs land under
  `research/edge_discovery/studies/outputs/real/` so the synthetic
  outputs the prior sprint committed stay byte-identical.
- Update (or add a hydrate addendum to)
  [`EDGE_DISCOVERY_LAB_001_RESULTS.md`](EDGE_DISCOVERY_LAB_001_RESULTS.md) and
  [`EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md`](EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md)
  to reflect what changed once real artifacts were used.
- Add focused tests for the new loader behavior, missing-file
  fallback, and provenance reporting.

## 3. What this sprint will NOT change

- No edits to `paper.yaml`, `practice.yaml`, `live.example.yaml`,
  `approved_strategies.yaml`, the loops module, the broker module,
  the evidence manifest, the evidence index, or `STRATEGY_STATUS.md`.
- No campaign verdict is altered. CAMPAIGN_010–014 keep their
  existing REJECT / DIAGNOSTIC verdicts.
- No new formal campaign is started. Even if a real-data finding is
  striking, it is documented as a lab study and a candidate
  hypothesis, not as a pre-commit.
- No broker calls; no `forex_bot.broker` imports added to the lab.
  The existing import-isolation test
  ([`tests/research/edge_discovery/test_isolation.py`](../../tests/research/edge_discovery/test_isolation.py))
  must keep passing unchanged.
- No relaxation of the verdict-word ban — lab outputs may not write
  "APPROVE" / "PASS" / "PROMOTE" / "DEPLOY".
- No fabrication of missing artifacts. Anything that is local-only,
  gitignored, or genuinely absent gets documented honestly in
  [`EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.md`](EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.md)
  (Phase 1) — the loaders gracefully fall back and the studies say
  "synthetic only" in their provenance section.

## 4. Branch / base reconciliation

| item | value |
|---|---|
| current branch | `research-edge-discovery-lab-hydrate-001` |
| base | `main` (merge-base = `bb739c2` = current `main` HEAD) |
| relationship to prior lab branch | strict superset; everything `research-edge-discovery-lab-001` shipped is present and unchanged |
| commits ahead of `main` at sprint start | 0 |
| sibling branches still present locally | `claude/affectionate-fermi-d950fc`, `claude/hardcore-leakey-a2449c`, `claude/keen-leakey-a15799`, `claude/vibrant-heisenberg-1d2de2`, `research-edge-discovery-lab-001` |
| recent main history | merged PR #1 = `research-calendar-event-window-anomaly-walk-forward-001` on top of `research-edge-discovery-lab-001` |

### Why CAMPAIGN_010–014 looked "missing" before but are present now

The prior sprint branched from a commit that pre-dated the merge of
`research-calendar-event-window-anomaly-walk-forward-001` into
`main`. Its working tree therefore lacked CAMPAIGN_010–014 docs and
backtest folders. Since then PR #1 has been merged and the
CAMPAIGN_010–014 evidence is in `main` — and therefore in this
branch's base. **No artifact policy excluded them; the missing-ness
was purely a branch-base / merge-ordering effect.**

Confirmed-present artifacts on this branch (sample, full list in
Phase 1):

- `docs/research/CAMPAIGN_010_*.md` through `CAMPAIGN_014_*.md` —
  all `STATUS`, `EVIDENCE_SUMMARY`, `WALK_FORWARD_RESULT`,
  `PORTFOLIO_RISK_DIAGNOSTICS`, `FINANCING_OVERLAY`,
  `INDEPENDENT_VERIFIER_STATUS`, `DATA_PROVENANCE` docs.
- `backtests/CAMPAIGN_010_session_breakout/` through
  `CAMPAIGN_014_calendar_event_window_anomaly/` — full
  `walk_forward/{plan,results,fold_detail}.{json,md}`,
  `financing/`, `risk/`, and `folds/fold_NN/` directories with
  per-pair `*_summary.json` and `*_trades.csv` files.
- `research/calendar/fixtures/campaign_014_events.json` — the
  Phase 1 NFP/FOMC/ECB/BoJ/BoE event fixture with full source
  attribution, 2020-01-01 → 2026-05-20 coverage.

Confirmed-absent artifacts on this branch (Phase 1 will inventory in
detail):

- Real seven-pair H4 OHLC CSVs are **gitignored** by design
  (`.gitignore` line `research/lean_parity/exports/**/*.csv`). Only
  the provenance JSONs (e.g.
  `research/lean_parity/exports/campaign_002_h4/EUR_USD_H4_lean.provenance.json`)
  are committed. The bulk candle CSVs are regenerated locally via
  `scripts/export_lean_parity_data.py` against the operator's
  practice OANDA snapshot.
- No `*.sqlite` / `*.db` / `*.parquet` candle store is committed
  anywhere in the tree (also excluded by `.gitignore`).

## 5. Sprint baseline metrics

Captured at the top of Phase 0 so any later drift is detectable.

| check | command | result |
|---|---|---|
| repo test count | `pytest --collect-only -q` | **1,104 tests collected** |
| full pytest | `pytest tests/ -q` | **1,104 passed in 4.83s** |
| freeze gate | `python scripts/check_research_freeze.py` | **ALL PASSED** (loops refuse `trend_following`) |
| archive validator | `python scripts/validate_research_archive.py` | **ALL PASSED** (14 campaign reports, 14 diagnostic artifacts, all non-approval verdicts) |
| secret scan | `python scripts/scan_artifacts_for_secrets.py` | **PASSED** (pattern scan over 2,862 artifact files; value scan skipped — no creds in env) |

Note: the prior lab summary recorded 838 tests passing on its base
commit. The current count is 1,104 because the intervening
calendar-event-window-anomaly campaign sprint added ~266 tests
(broadly: CAMPAIGN_014 unit tests, walk-forward plan tests, event
fixture tests). The hydrate sprint must keep this number monotonic.

## 6. Phases

| phase | output | commit signal |
|---|---|---|
| 0 | this plan + baseline metrics | "Phase 0 — plan + baseline" |
| 1 | `EDGE_DISCOVERY_REAL_ARTIFACT_INVENTORY.md` | "Phase 1 — real artifact inventory" |
| 2 | hydrated loaders + new tests | "Phase 2 — real-data loaders" |
| 3 | real-data studies under `studies/outputs/real/` | "Phase 3 — exploratory studies on real data" |
| 4 | results + ranking-rules addendum | "Phase 4 — ranking rules updated" |
| 5 | hydrate summary + final validation | "Phase 5 — final validation + summary" |

## 7. Safety reminders for this sprint

- The lab MUST NOT import `forex_bot.broker` (existing
  `test_isolation.py` enforces this; it stays unchanged and must
  keep passing).
- The lab MUST NOT change verdicts. Reading the committed
  CAMPAIGN_010–014 result JSONs is allowed; rewriting any
  `STATUS.md` / `WALK_FORWARD_RESULT.md` / report token / manifest
  entry is not.
- The lab MUST NOT write "APPROVE" / "PASS" / "PROMOTE" / "DEPLOY"
  in any output (verdict-word ban in
  [`research/edge_discovery/report.py`](../../research/edge_discovery/report.py); regression-guarded by
  [`tests/research/edge_discovery/test_report.py`](../../tests/research/edge_discovery/test_report.py)).
- Every Markdown / JSON output produced by this sprint must include
  a **Provenance** block that states: real vs synthetic, source
  artifact paths with SHA-256 if possible, date coverage, pair
  universe, limitations, and an explicit "exploratory only" line.
- If a real artifact is gitignored / local-only, the loader must
  detect it, log it, and fall back to the synthetic fixture **with
  a provenance line that says `synthetic-fallback`** — never
  silently substitute synthetic data for real.

## 8. Recommended next branch (forward-looking only, no commitment)

After this sprint lands, the next natural sprint is either:

- `research-edge-discovery-lab-real-event-window-002` — a focused
  study run that takes whatever real-event-window signal (if any)
  the hydrated lab surfaces and pressure-tests it against the
  existing turnover / cost / null-baseline gates.

- `infra-edge-discovery-h4-store-export-001` — a small,
  reproducible local export script that materializes a committed
  small-fixture H4 store the lab can use without depending on the
  operator's local OANDA snapshot.

This sprint takes no position on which of those comes next; it
just makes both possible.
