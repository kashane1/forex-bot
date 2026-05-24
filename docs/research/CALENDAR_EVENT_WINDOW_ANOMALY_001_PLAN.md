# `research-calendar-event-window-anomaly-001` — Scaffold Plan (Phase 0)

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-001`
(worktree branch `claude/affectionate-fermi-d950fc`) · `strategy_evidence: false`

Phase 0 repo truth audit + 9-phase scaffold plan for the **C7 /
CAMPAIGN_014 / `calendar_event_window_anomaly 0.1.0-c014`** candidate
selected by the `research-new-candidate-strategy-discovery-005` sprint.
**Scaffold sprint only — no historical backtest, no walk-forward
evidence, no financing overlay evidence, no portfolio-risk evidence,
no independent-verifier evidence, no broker call, no `.env` read.**

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
> CAMPAIGN_012 / CAMPAIGN_013 all remain REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper /
> demo / live remain blocked. CAMPAIGN_011 is the **null baseline
> only**, not a trading candidate. **A passing unit test suite or
> smoke run is NOT strategy approval.**

## 1. Branch / base commit / repo state

| dimension | value |
|---|---|
| git branch (worktree) | `claude/affectionate-fermi-d950fc` |
| logical sprint branch | `research-calendar-event-window-anomaly-001` |
| base commit (HEAD before Phase 0) | `ed20604` — Phase 10 of `research-new-candidate-strategy-discovery-005` (discovery-005 sprint close; C7 selection) |
| working tree at Phase 0 start | clean (`git status --short` empty except `.claude/` tooling cache, which is `.gitignore`d) |

## 2. Repo truth summary (verified at Phase 0)

| dimension | value |
|---|---|
| pytest count (baseline) | **875 passed** in 4.22 s |
| ruff status (baseline) | **3 pre-existing** in `research/lean_parity/algorithms/` (`2× RUF100` unused-noqa + `1× I001` unsorted-imports); untouched LEAN-parity archive; out of scope |
| `validate_research_archive.py` | ALL CHECKS PASSED (13 campaigns; 14 diagnostic artifacts; 260 evidence-index links resolve; 2,609 committed artifact files clean) |
| `check_research_freeze.py` | ALL CHECKS PASSED (loops refuse `['trend_following']` — frozen; no credentials) |
| `scan_artifacts_for_secrets.py` | PASSED (2,830 files value-scan-skipped; 2,679 files pattern-scanned; no credential value or shape) |
| `paper-loop -c configs/paper.yaml` | **refused** — `trend_following` not approved |
| `demo-loop -c configs/practice.yaml` | **refused** — `trend_following` not approved |
| `forex_bot.cli --help` | **no `live-loop` command** present |
| `configs/approved_strategies.yaml` | `approved: []` (verified verbatim) |

## 3. Latest campaign statuses (verified)

| campaign | strategy | verdict | role |
|---|---|---|---|
| CAMPAIGN_002 | `trend_following 0.1.0` | REJECT | historical rejected; untouched |
| CAMPAIGN_010 | `session_breakout 0.1.0-c010` | REJECT | historical rejected; untouched |
| CAMPAIGN_011 | `random_entry_anchor 0.1.0-c011` | REJECT (null-model anchor) | null baseline; **not a trading candidate** |
| CAMPAIGN_012 | `regime_switcher_atr_percentile 0.1.0-c012` | REJECT | regime-switcher; falsified; **off-limits to retune** |
| CAMPAIGN_013 | `cross_pair_currency_strength_rotation 0.1.0-c013` | REJECT | cross-pair rotator; falsified; **off-limits to retune (binding cooldown ≥ 3 sprints)** |
| **CAMPAIGN_014** | **`calendar_event_window_anomaly 0.1.0-c014`** | **PENDING SCAFFOLD** (this sprint) | C7 candidate; scaffold-only; **no evidence verdict yet** |

## 4. Discovery-005 outputs verified (the binding design this sprint implements)

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_005_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_005_SUMMARY.md) — selected C7
- [`NEXT_PREFERRED_DIRECTION_005.md`](NEXT_PREFERRED_DIRECTION_005.md) — C7 over C10 / C12 / infra-A rationale
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md) — R1–R8, 10 frozen parameters, 5 no-lookahead invariants, ≥ 30 expected tests, turnover budget + cost section
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md) — this sprint's prompt template (9 phases + Phase 1b)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) — next sprint after this one
- [`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md) — cross-pair-rotation cooldown
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) — binding turnover budget
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) — Patterns R–W
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md) — shortlist (C7 lead)
- [`NEXT_DIRECTION_REASSESSMENT_005.md`](NEXT_DIRECTION_REASSESSMENT_005.md) — 18-axis reassessment
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) — binding null baseline

## 5. Files inspected for implementation patterns

| file | role |
|---|---|
| `src/forex_bot/strategies/random_entry_anchor.py` | template for fail-closed + Signal emission + R1–R8 docstring |
| `src/forex_bot/strategies/regime_switcher_atr_percentile.py` | template for time-stop-only + `extra="forbid"` config |
| `src/forex_bot/strategies/cross_pair_currency_strength_rotation.py` | template for external-data injection via `ctx.config` (sibling of event-fixture injection pattern) + module-level constants |
| `src/forex_bot/strategies/__init__.py` | re-export convention |
| `src/forex_bot/config.py` | `*StrategyConfig` placement; `StrategyConfig.enabled` validator |
| `src/forex_bot/strategies/base.py` | `Strategy` Protocol + `StrategyContext` dataclass contract |
| `src/forex_bot/strategies/indicators.py` | `atr()` helper |
| `src/forex_bot/domain/signals.py` | `Signal` Pydantic model |
| `tests/unit/test_cross_pair_currency_strength_rotation.py` | template for ≥ 50 unit tests (1066 LOC) including source-grep contamination checks |
| `tests/unit/test_random_entry_anchor.py` | template for null-model safety tests |
| `tests/unit/test_regime_switcher_atr_percentile.py` | template for regime-style configs + validator tests |
| `configs/campaign_013_cross_pair_currency_strength_rotation.yaml` | template for research-only YAML (trading_enabled: false, broker keys unused) |

## 6. Existing event-calendar infrastructure search

Searched `src/forex_bot`, `tests`, `configs`, `research`, `scripts`,
`docs/research` for `event`, `calendar`, `economic`, `fomc`, `nfp`,
`ecb`, `boj`, `boe`. **No existing event-calendar infrastructure.**
The only `event` matches are unrelated (event loops, transactions,
financing rate events, parity-verifier event loop tests, broker
event mapping). C7 introduces a brand-new event-calendar primitive
to the repo.

## 7. CAMPAIGN_014 purpose

C7 / CAMPAIGN_014 tests the hypothesis that around scheduled high-
impact macroeconomic events (NFP / FOMC / ECB / BoJ / BoE), USD-pair
returns exhibit a **mean-reverting overshoot** in the H4 bars
immediately after the event close. The strategy trades **counter to
the first post-event H4 bar's direction** with an ATR stop and a
max-hold time stop. The event set is finite per year (~40–55 events
in the binding universe), making the turnover budget structurally
low (~150–520 trades over 4 years; well below CAMPAIGN_011's 1,177
null floor) and the **turnover-amplification anti-pattern (Patterns
M and V) structurally disqualified by design**.

This is a research candidate. It is **not approved**. The scaffold
sprint produces the strategy module + event-calendar loader +
config schema + tests + research config + CAMPAIGN_014 docs only.
Walk-forward, financing, risk, and verifier evidence are deferred
to the future evidence sprint `research-calendar-event-window-
anomaly-walk-forward-001`.

## 8. Implementation files expected

**NEW source files:**

- `src/forex_bot/calendar_events.py` (~200 LOC) — `CalendarEvent` model + `CalendarEventFixture` loader + `eligible_events_at_or_before()` helper + class precedence + coverage checker
- `src/forex_bot/strategies/calendar_event_window_anomaly.py` (~300 LOC) — `CalendarEventWindowAnomalyStrategy` with R1–R8 rule table

**EDIT source files:**

- `src/forex_bot/strategies/__init__.py` — re-export `CalendarEventWindowAnomalyStrategy`
- `src/forex_bot/config.py` — add `CalendarEventWindowAnomalyStrategyConfig` + `StrategyConfig.calendar_event_window_anomaly` slot + enabled-list check

## 9. Event-fixture files expected

| file | role |
|---|---|
| `research/calendar/fixtures/campaign_014_events.json` | committed event-calendar fixture: NFP / FOMC / ECB / BoJ / BoE 2020-01-01 → 2026-05-20; UTC timestamps; **no actual / forecast / surprise / revision values**; source URLs only; ~20–40 KB |
| `docs/research/CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md` | provenance doc — fixture path, per-class counts, first/last event timestamp, coverage range, source URLs, fields included/excluded, schema version, limitations, evidence-readiness |

**Fixture compilation approach** (selected): **manually-curated
committed fixture with documented official-source URLs**. Each event
entry includes only `event_id`, `event_class`, `event_time_utc`,
`source_name`, `source_url`, `schema_version`. The dates and times
for fixed-schedule events (NFP = first Friday of month at 12:30 UTC
historical schedule; FOMC = 8 scheduled meetings/year per published
calendar; ECB = scheduled rate decisions; BoJ = scheduled MPM; BoE =
scheduled MPC) are publicly documented and well-known; no scraping is
required. The compilation is deterministic (same source-URL list →
same fixture).

**Rejected alternatives:**

- **Scraping script** — no scraping required; the underlying schedules
  are publicly published and stable historical data.
- **Broker API** — explicitly forbidden by safety rules.
- **Synthetic-only fixture** — would be insufficient for the future
  evidence sprint's coverage contract; the real schedules are public.

## 10. Test files expected

- `tests/unit/test_calendar_event_window_anomaly.py` (~1,100 LOC; ≥ 50 cases) covering:
  - Config defaults + bounds + `extra="forbid"`
  - Fixture loader validation (schema, UTC, allowed classes, disallowed surprise/forecast/actual/revision fields, deterministic sort, coverage checker)
  - Eligible-event helper (no future events; ordering)
  - R1–R8 rule firing + fail-closed cases
  - Overlap precedence (FOMC > NFP > ECB > BoJ > BoE)
  - Re-entry block + position-already-open
  - Signal direction (counter-trend; positive event-bar return → SHORT; negative → LONG)
  - Stop placement (ATR-2 × prior_atr)
  - Determinism + signal_id stability
  - Anti-contamination source-grep tests (no broker/execution/loops imports; no PRNG; no CAMPAIGN_002/010/011/012/013 parameter keys; no Donchian/EMA/Asian/London/master_seed/regime_switcher/daily_atr_percentile/cross_pair/currency_strength/rank_gap)
  - `configs/approved_strategies.yaml` regression
  - Paper / demo config does not enable the new strategy
  - Fixture path is local + repo-relative + no credential-shaped fields
  - Future-evidence coverage rejection for uncovered date ranges
  - Loader performs no network calls at runtime

Test target: **875 → ≥ 925** (≥ 50 new). Discovery-005 spec said "≥
30 new"; we aim higher per the prior sibling sprint's pattern
(CAMPAIGN_013 scaffold added 57).

## 11. Docs expected (this sprint only)

| phase | doc |
|---|---|
| 0 | `CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md` (this doc) |
| 1 | `CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md` |
| 1b | `CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md` + the committed fixture JSON |
| 5 | `CAMPAIGN_014_PRECOMMIT_CHECKLIST.md` + `CAMPAIGN_014_STATUS.md` + `CALENDAR_EVENT_WINDOW_ANOMALY_READINESS.md` |
| 6 | `CAMPAIGN_014_SMOKE_RESULT.md` |
| 7 | `CAMPAIGN_014_WALK_FORWARD_READINESS.md` + `CAMPAIGN_014_FINANCING_RISK_READINESS.md` + `CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md` |
| 8 | `CALENDAR_EVENT_WINDOW_ANOMALY_001_SUMMARY.md` + EDIT `EVIDENCE_INDEX.md` + EDIT `STRATEGY_STATUS.md` |

## 12. Validation commands (per-phase + final)

```bash
python -m pytest -q
ruff check src tests scripts research
python scripts/validate_research_archive.py
python scripts/check_research_freeze.py
python scripts/scan_artifacts_for_secrets.py
python -m forex_bot.cli paper-loop -c configs/paper.yaml      # expect refusal
python -m forex_bot.cli demo-loop -c configs/practice.yaml    # expect refusal
python -m forex_bot.cli --help                                 # expect no live-loop
git status --short
```

**Test-count target:** 875 baseline → ≥ 925 after Phase 4 (≥ 50 new
unit tests).

**Ruff target:** 3 pre-existing in `research/lean_parity/algorithms/`
maintained.

## 13. Non-goals (binding for this sprint)

This scaffold sprint **must not** do any of the following:

- **Run a historical backtest.** Phase 6 smoke is config-load + fixture-load + unit suite + tiny synthetic-fixture signal smoke only; no `run_campaign_014.py` runner is created (that is for the evidence sprint).
- **Run a walk-forward evidence sprint.** No `backtests/CAMPAIGN_014_*/` artifact directory.
- **Run a financing overlay** or **portfolio-risk diagnostics** evidence run. No `scripts/build_campaign_014_financing_overlay.py`; no `scripts/build_campaign_014_risk_diagnostics.py` (deferred to evidence sprint).
- **Run a verifier evidence run.**
- **Fetch broker / OANDA data.** No `fetch-candles`; no HTTP to broker.
- **Read `.env`** or print any credential.
- **Submit / query any broker / account / order / trade / position / transaction endpoint.**
- **Run `paper-loop` / `demo-loop`** except for the standing refusal check.
- **Create or invoke any `live-loop` command.**
- **Modify `configs/approved_strategies.yaml`** (must remain `approved: []`).
- **Enable `calendar_event_window_anomaly` in `configs/paper.yaml` or `configs/practice.yaml`.**
- **Use QuantConnect / LEAN** (retired).
- **Revive or tune** CAMPAIGN_002 / 010 / 011 / 012 / 013.
- **Use CAMPAIGN_011 as a trading candidate.**
- **Use CAMPAIGN_013 per-pair results to select a pair-only rescue candidate.**
- **Perform broad parameter search** or **optimize parameters based on smoke behavior**.
- **Alter the 10 frozen C7 parameters** based on smoke behavior.
- **Lower the turnover budget** after seeing smoke behavior.
- **Use event actual / forecast / surprise / revision values** in the fixture or the strategy.
- **Scrape private, paid, broker, or credentialed event feeds.**
- **Commit `*.sqlite3`, candle CSVs, bulky raw scraped pages, tokens, credentials, or local-only generated data.**
- **Add the strategy to `EVIDENCE_MANIFEST.json`** (the validator's `check_manifest_schema` requires `report_path` and `artifact_folder` to exist; CAMPAIGN_014 has neither yet — manifest entry is reserved for the evidence sprint).

## 14. Explicit safety statements

1. **This scaffold sprint cannot approve any strategy.** Approval requires the full six-evidence ladder + a deliberate human approval action per [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md). A passing unit-test suite is not approval. A smoke pass is not evidence.
2. **This scaffold sprint must not run evidence.** No historical backtest, no walk-forward, no financing overlay evidence, no risk-diagnostics evidence, no verifier evidence. These are explicit deliverables of the future evidence sprint `research-calendar-event-window-anomaly-walk-forward-001`.
3. **CAMPAIGN_011 is the null baseline only**, not a trading candidate. The strategy `random_entry_anchor` is structurally un-approvable by design.
4. **C7 / CAMPAIGN_014 is selected (by discovery-005) but not approved.** Selection by a discovery sprint authorizes a scaffold sprint; scaffold-completion authorizes an evidence sprint; only a deliberate human approval action after a `RESEARCH_PASS_UNAPPROVED` verdict + verifier-extension corroboration can move the strategy into `configs/approved_strategies.yaml`.
5. **The event-calendar fixture must be public, local, reviewable, and broker-free.** Source URLs are public government / central-bank pages (BLS / FOMC.gov / ECB.europa.eu / BoJ.or.jp / BoE.co.uk). The fixture is a committed text file (~20–40 KB) that any future Claude instance or human reviewer can audit. **No credentials, no `.env` read, no broker call, no paid API, no scraping with login.**

## 15. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_005_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_005_SUMMARY.md) (predecessor sprint's summary; selected C7)
- [`NEXT_PREFERRED_DIRECTION_005.md`](NEXT_PREFERRED_DIRECTION_005.md) (C7 selection rationale)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md) (binding design)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md) (this sprint's prompt template)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) (next sprint after this)
- [`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md) (binding cooldown — cross-pair-rotation off-limits)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) (binding turnover guardrail)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) (binding Patterns R–W)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md) (base guardrails)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
