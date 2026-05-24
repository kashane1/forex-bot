# `research-calendar-event-window-anomaly-walk-forward-001` — Plan

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-walk-forward-001`
(worktree branch `claude/affectionate-fermi-d950fc`)
`strategy_evidence: false`

Phase 0 sprint plan for the CAMPAIGN_014 evidence-grade walk-forward
sprint. Implements the 10-phase pipeline from
[`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md)
adapted for the C7 Calendar-Event Window Anomaly candidate.
**Evidence sprint — this sprint may run walk-forward + financing +
risk diagnostics + verifier-status assessment. It must NOT approve
the strategy, must NOT enable paper / demo / live, must NOT change
frozen parameters after seeing results.**

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 / 013 remain
> REJECT. CAMPAIGN_014 is candidate-scaffold-only before this sprint;
> after this sprint it has an evidence verdict (REJECT or
> RESEARCH_PASS_UNAPPROVED or BLOCKED). `configs/approved_strategies.yaml`
> remains `approved: []`. CAMPAIGN_011 is the null baseline only —
> not a trading candidate.

## 1. Base commit + worktree

| dimension | value |
|---|---|
| base commit | `72b988e` (Phase 8 of `research-calendar-event-window-anomaly-001` scaffold sprint) |
| current branch | `claude/affectionate-fermi-d950fc` (worktree) |
| target evidence branch name | `research-calendar-event-window-anomaly-walk-forward-001` |
| working tree | clean (no untracked except `.claude/`) |
| pytest baseline | **968 / 968 PASS** (4.15 s) |
| ruff baseline | **3 pre-existing in `research/lean_parity/algorithms/`** (unchanged from CAMPAIGN_014 scaffold sprint) |
| `validate_research_archive.py` | **ALL PASS** (13 campaigns, 271 evidence-index links, 14 diagnostic artifacts) |
| `check_research_freeze.py` | **ALL PASS** (registry empty, paper + demo loops refuse) |
| `scan_artifacts_for_secrets.py` | **PASSED** (2693 / 2847 files scanned) |
| `paper-loop` / `demo-loop` | **REFUSED** (trend_following not approved) |
| `live-loop` command | does not exist |

## 2. Repo state verification

### 2.1 CAMPAIGN_014 scaffold deliverables (verified present)

| file | role | confirmed |
|---|---|:---:|
| `src/forex_bot/calendar_events.py` | event-fixture loader + helpers (~270 LOC) | ✓ |
| `src/forex_bot/strategies/calendar_event_window_anomaly.py` | strategy module (~412 LOC) | ✓ |
| `src/forex_bot/strategies/__init__.py` | re-export `CalendarEventWindowAnomalyStrategy` | ✓ |
| `src/forex_bot/config.py` | `CalendarEventWindowAnomalyStrategyConfig` + `StrategyConfig.calendar_event_window_anomaly` | ✓ |
| `tests/unit/test_calendar_event_window_anomaly.py` | 93 unit tests | ✓ |
| `configs/campaign_014_calendar_event_window_anomaly.yaml` | research-only config | ✓ |
| `scripts/build_campaign_014_event_fixture.py` | deterministic fixture compilation | ✓ |
| `research/calendar/fixtures/campaign_014_events.json` | 281-event committed fixture (sha256 `584a19a8…46ee1963`) | ✓ |

### 2.2 Existing campaign runner templates (will inform Phase 3)

| file | role |
|---|---|
| `scripts/run_campaign_010.py` | session_breakout single-pair-per-fold runner template |
| `scripts/run_campaign_011.py` | random_entry_anchor null-baseline runner (uses `BacktestEngine.from_config`-style strategy config injection) |
| `scripts/run_campaign_012.py` | regime_switcher single-pair-per-fold runner |
| `scripts/run_campaign_013.py` | cross_pair runner (most recent; per-pair-per-fold with shared per-fold context) |

C7's runner will be most similar to CAMPAIGN_013's structure
(per-pair-per-fold loop), except instead of building a cross-pair
context per fold, it will load + validate the event fixture **once
before all folds** and inject it into the strategy config as
`event_fixture` (preloaded `CalendarEventFixture`). No per-fold
network calls.

### 2.3 Existing artifact templates (will inform Phase 2 + Phase 4 layout)

| backtest layout | role |
|---|---|
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/{plan.json,plan.md,results.json,results.md,fold_detail.json}` | most recent template — used verbatim for CAMPAIGN_014 directory structure |
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/financing/...` | financing-overlay artifact location |
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/risk/...` | risk-diagnostics artifact location |
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/folds/fold_NN/...` | per-fold per-pair summary + trades CSV (gitignored bulk) |

CAMPAIGN_014's artifact directory: `backtests/CAMPAIGN_014_calendar_event_window_anomaly/`.

## 3. Local data availability (verified)

### 3.1 Candle store

| dimension | value |
|---|---|
| store path | `data/campaign_002.sqlite3` (symlinked to `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3`) |
| source | `oanda-practice` (per `data_sources` table) |
| home host | `https://api-fxpractice.oanda.com` |
| timeframe | H4 |
| universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD (all 7) |
| per-pair candle counts | EUR_USD 9931 · GBP_USD 9931 · USD_JPY 9932 · AUD_USD 9931 · USD_CAD 9931 · USD_CHF 9931 · NZD_USD 9935 |
| coverage | `2020-01-01T22:00:00+00:00` → `2026-05-19T21:00:00+00:00` |
| identity to CAMPAIGN_010 / 011 / 012 / 013 | YES (same physical SQLite, same `data_sources` rows, same raw_sha256 hashes per pair — verified) |
| committed in repo | **NO** (the symlink target is gitignored; only the symlink itself is committed via `data/.gitkeep`) |

No re-fetch required. The candle store is identical to what
CAMPAIGN_010 / 011 / 012 / 013 used.

### 3.2 Event fixture

| dimension | value |
|---|---|
| path | `research/calendar/fixtures/campaign_014_events.json` |
| sha256 | `584a19a8182bb3385cb152b9f1444f443fb5d0e1322330029885f11246ee1963` |
| coverage | 2020-01-01 → 2026-05-20 |
| total events | 281 (NFP 77 · FOMC 51 · ECB 51 · BoJ 51 · BoE 51) |
| audit status (this sprint Phase 0) | **PARTIAL — PROCEED WITH EXPLICIT CAVEAT** (per [`CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md`](CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md)) |
| committed in repo | **YES** (compact ~37 KB text) |

## 4. Event-fixture date-verification audit (Phase 0)

See [`CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md`](CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md)
for the full audit detail.

**Headline result:**

| class | verification | impact |
|---|---|---|
| NFP | **100 % verified** (procedural first-Friday rule) | full confidence |
| FOMC | **100 % verified** (official Fed calendar WebFetch) | full confidence |
| BoJ | 91 % verified for 2025-2026 (WebFetch); older years not WebFetch-checked; **1 post-coverage drift** (2026-03-18 vs 2026-03-19) | **NONE on this sprint** |
| ECB | not WebFetch-verified (calendar page shows future-only); structural consistency confirmed | scaffold-grade |
| BoE | not WebFetch-verified (URL returns 403); structural consistency confirmed | scaffold-grade |

**Audit verdict: PARTIAL — PROCEED WITH EXPLICIT CAVEAT.** NFP +
FOMC account for ~46 % of events but ~94 % of trade opportunities
(both impact all 7 USD pairs). All fold test windows are inside
fixture coverage. The 1 discovered BoJ drift is post-fold-coverage
and affects zero trades.

**Caveat:** If the evidence sprint produces RESEARCH_PASS_UNAPPROVED,
a deeper ECB + BoE + older BoJ date-verification audit is
mandatory before any paper-promotion consideration.

## 5. Phase plan (10 phases)

| phase | scope | output |
|---|---|---|
| **Phase 0** (this commit) | repo truth audit + fixture date-verification audit + sprint plan | `CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md` (this doc) + `CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md` |
| **Phase 1** | candle data + event fixture provenance summary | `CAMPAIGN_014_DATA_PROVENANCE.md` |
| **Phase 2** | authoritative walk-forward plan (8 folds rolling/frozen) | `backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/{plan.json,plan.md}` + `CAMPAIGN_014_WALK_FORWARD_PLAN.md` |
| **Phase 3** | per-fold local backtest runner (`scripts/run_campaign_014.py`) | runner + (optional) helper tests; no execution |
| **Phase 4** | execute 8-fold × 7-pair walk-forward | `backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/{results.json,results.md,fold_detail.json}` + per-fold summary JSONs + `CAMPAIGN_014_WALK_FORWARD_EXECUTION.md` |
| **Phase 5** | walk-forward verdict + null-baseline + turnover gates + event-class diagnostics | `CAMPAIGN_014_WALK_FORWARD_RESULT.md` |
| **Phase 6** | financing overlay (ESTIMATED + conservative-stress) | `scripts/build_campaign_014_financing_overlay.py` + `backtests/.../financing/...` + `CAMPAIGN_014_FINANCING_OVERLAY.md` |
| **Phase 7** | portfolio-risk diagnostics (standard + C7-specific) | `scripts/build_campaign_014_risk_diagnostics.py` + `backtests/.../risk/...` + `CAMPAIGN_014_PORTFOLIO_RISK_DIAGNOSTICS.md` |
| **Phase 8** | independent verifier status | `CAMPAIGN_014_INDEPENDENT_VERIFIER_STATUS.md` |
| **Phase 9** | campaign status + evidence manifest + final summary + final validation | `CAMPAIGN_014_STATUS.md` (update) + `CAMPAIGN_014_EVIDENCE_SUMMARY.md` + `CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_SUMMARY.md` + `EVIDENCE_INDEX.md` (update) + `EVIDENCE_MANIFEST.json` (update) + `STRATEGY_STATUS.md` (update) + test count assertion |

## 6. Walk-forward plan (binding inheritance)

Inherits CAMPAIGN_010 / 011 / 012 / 013 plan verbatim:

| dimension | value |
|---|---|
| split style | `rolling` |
| parameter mode | `frozen` |
| `strategy_evidence` flag | `false` |
| `universe_start` | `2020-01-01` |
| `universe_end` | `2026-05-20` |
| train_days per fold | 540 |
| validation_days per fold | 180 |
| test_days per fold | 180 |
| step_days | 180 |
| expected fold count | **8** |
| fold-coverage check | all 8 test windows must be ≤ fixture `coverage_end_utc` (= 2026-05-20) — verified PASS in Phase 0 audit |
| parameter sweep | **FORBIDDEN** (frozen mode) |
| adaptive parameters | **FORBIDDEN** (frozen mode) |

Expected fold test windows (per CAMPAIGN_013's verbatim plan):

| fold | train | validation | test |
|---|---|---|---|
| 0 | 2020-01-01 → 2021-06-23 | 2021-06-24 → 2021-12-20 | 2021-12-21 → 2022-06-18 |
| 1 | 2020-06-29 → 2021-12-20 | 2021-12-21 → 2022-06-18 | 2022-06-19 → 2022-12-15 |
| 2 | 2020-12-26 → 2022-06-18 | 2022-06-19 → 2022-12-15 | 2022-12-16 → 2023-06-13 |
| 3 | 2021-06-24 → 2022-12-15 | 2022-12-16 → 2023-06-13 | 2023-06-14 → 2023-12-10 |
| 4 | 2021-12-21 → 2023-06-13 | 2023-06-14 → 2023-12-10 | 2023-12-11 → 2024-06-07 |
| 5 | 2022-06-19 → 2023-12-10 | 2023-12-11 → 2024-06-07 | 2024-06-08 → 2024-12-04 |
| 6 | 2022-12-16 → 2024-06-07 | 2024-06-08 → 2024-12-04 | 2024-12-05 → 2025-06-02 |
| 7 | 2023-06-14 → 2024-12-04 | 2024-12-05 → 2025-06-02 | 2025-06-03 → 2025-11-29 |

## 7. Expected commands per phase

```bash
# Phase 0 (this commit)
git status --short
python -m pytest -q
ruff check src tests scripts research
python scripts/validate_research_archive.py
python scripts/check_research_freeze.py
python scripts/scan_artifacts_for_secrets.py
python -m forex_bot.cli paper-loop -c configs/paper.yaml      # expect refusal
python -m forex_bot.cli demo-loop -c configs/practice.yaml    # expect refusal
python -m forex_bot.cli --help                                 # confirm no live-loop

# Phase 1 — data provenance doc (no execution)

# Phase 2 — walk-forward plan generator (existing harness)
python -c "from research.walk_forward import generate_plan_for_campaign; ..."   # produces plan.json + plan.md

# Phase 3 — runner (lint only; no execution)
ruff check scripts/run_campaign_014.py

# Phase 4 — runner execution
python scripts/run_campaign_014.py \
    --config configs/campaign_014_calendar_event_window_anomaly.yaml \
    --plan   backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/plan.json \
    --out    backtests/CAMPAIGN_014_calendar_event_window_anomaly

# Phase 5 — verdict (no execution; doc only)

# Phase 6 — financing overlay
python scripts/build_campaign_014_financing_overlay.py \
    --campaign-dir backtests/CAMPAIGN_014_calendar_event_window_anomaly

# Phase 7 — risk diagnostics
python scripts/build_campaign_014_risk_diagnostics.py \
    --campaign-dir backtests/CAMPAIGN_014_calendar_event_window_anomaly

# Phase 8 — verifier status (doc only; verifier capability-locked to CAMPAIGN_002)

# Phase 9 — final validation (same as Phase 0 + git status)
```

## 8. Validation plan

Each phase ends with at least:

1. `python -m pytest -q` (if any code changed)
2. `ruff check src tests scripts research` (if any code changed)
3. `python scripts/validate_research_archive.py`
4. `python scripts/check_research_freeze.py`
5. `python scripts/scan_artifacts_for_secrets.py`
6. `git status --short`

Final Phase 9 validation also runs the paper / demo refusal checks +
CLI help.

## 9. Non-goals (binding)

- **No strategy approval.** Even a clean PASS produces only
  `RESEARCH_PASS_UNAPPROVED`.
- **No parameter tuning.** 14 frozen parameters are immutable
  per [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md) §5.
- **No CAMPAIGN_002 / 010 / 011 / 012 / 013 tuning or
  rule modification.** All remain REJECT and untouched.
- **No `max_open_positions` relaxation.**
- **No event-set / event-window / impact-ordering / ATR-settings /
  pair-universe / risk-settings / turnover-gate / walk-forward-gate /
  null-baseline-gate change based on results.**
- **No `actual` / `forecast` / `surprise` / `revision` /
  `commentary` / `market_reaction` event values.**
- **No paid / private / broker / credentialed event-feed
  scraping.**
- **No paper / demo / live execution** (refusal checks only).
- **No broker order submission / query.** No account / order /
  trade / position / transaction endpoint queried.
- **No `.env` read.** No credentials printed.
- **No QuantConnect / LEAN command run.**
- **Fixture is NOT modified mid-evidence.** The 1 BoJ drift
  (2026-03-18 vs 2026-03-19) is logged for a future
  fixture-revision sprint but **not** patched here.

## 10. Safety invariants (binding throughout this sprint)

| invariant | enforcement |
|---|---|
| `configs/approved_strategies.yaml` remains `approved: []` | validator + Phase 9 verification |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 verdicts unchanged | git-diff inspection on Phase 9 |
| CAMPAIGN_014's frozen-parameters table unchanged | runner's `_assert_frozen()` check (Phase 3) |
| no broker / OANDA call | scripted greps + runner imports inspected |
| no `.env` read | greps + secret scanner |
| no live-loop creation | CLI help check |
| no paper / demo enablement | refusal check |
| no MODELED financing reachable | financing overlay's source-treatment assertion |
| no PRNG / random seeding | strategy module + runner source-grep |
| fixture loader's deny-list intact | unit tests + secret scanner |
| no fixture modification mid-sprint | git-diff on `research/calendar/fixtures/` |
| no `max_open_positions` relaxation | `_assert_frozen()` + config-load assertion |

## 11. Verdict options (per Phase 5; binding)

| verdict | meaning |
|---|---|
| **REJECT** | inherited / aggregate / per-fold gates fail materially |
| **REJECT_INDISTINGUISHABLE_FROM_NULL** | within CAMPAIGN_011 ± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair indistinguishability band |
| **REJECT_TURNOVER_BUDGET** | total trades > 800 OR total signals > 1,500 |
| **RESEARCH_PASS_UNAPPROVED** | all inherited gates pass + null-baseline meaningfully beaten + turnover within budget + fixture coverage OK — **still NOT approval** |
| **BLOCKED** | execution cannot complete (data / fixture / harness failure) |

## 12. Cross-links

- [`CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md`](CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md) (this-sprint Phase 0 audit)
- [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md) (binding pre-commit — frozen parameters + gates + turnover budget + cost section)
- [`CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`](CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md) (binding R1-R8 spec)
- [`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md) (fixture provenance)
- [`CAMPAIGN_014_WALK_FORWARD_READINESS.md`](CAMPAIGN_014_WALK_FORWARD_READINESS.md) (future-evidence walk-forward readiness from scaffold sprint)
- [`CAMPAIGN_014_FINANCING_RISK_READINESS.md`](CAMPAIGN_014_FINANCING_RISK_READINESS.md) (future-evidence financing/risk readiness from scaffold sprint)
- [`CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md) (future-evidence verifier readiness from scaffold sprint)
- [`CALENDAR_EVENT_WINDOW_ANOMALY_001_SUMMARY.md`](CALENDAR_EVENT_WINDOW_ANOMALY_001_SUMMARY.md) (scaffold-sprint summary)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) (binding turnover guardrail)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md) (walk-forward protocol)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md) (financing model status)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md) (approval process — binding)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md) (current strategy registry / verdicts)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) (current evidence index)
