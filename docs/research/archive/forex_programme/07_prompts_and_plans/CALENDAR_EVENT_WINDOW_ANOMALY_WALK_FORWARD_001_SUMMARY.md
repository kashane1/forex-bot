# `research-calendar-event-window-anomaly-walk-forward-001` — Evidence Sprint Summary

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-walk-forward-001`
(worktree branch `claude/affectionate-fermi-d950fc`)
`strategy_evidence: false`

End-of-sprint summary for the CAMPAIGN_014 / C7 calendar-event
window anomaly evidence-grade walk-forward sprint. **Verdict:
REJECT (direction-of-trade falsification).** No strategy approved;
no historical campaign verdict changed.

> CAMPAIGN_014 joins CAMPAIGN_002 / 010 / 011 / 012 / 013 as REJECT
> and untouched. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.

## 1. What changed

| dimension | value |
|---|---|
| commits this sprint | 10 (Phase 0 through Phase 9) |
| files added (NEW source) | `scripts/run_campaign_014.py` (~620 LOC) + `scripts/build_campaign_014_financing_overlay.py` (~210 LOC) + `scripts/build_campaign_014_risk_diagnostics.py` (~390 LOC) = ~1,220 source LOC |
| files added (NEW docs) | 10 docs (Phase 0 plan + audit; Phase 1 provenance; Phase 2 plan doc; Phase 4 execution; Phase 5 verdict; Phase 6 financing; Phase 7 risk; Phase 8 verifier; Phase 9 evidence summary; Phase 9 this summary) + edits to `CAMPAIGN_014_STATUS.md`, `STRATEGY_STATUS.md`, `EVIDENCE_INDEX.md`, `EVIDENCE_MANIFEST.json`, `tests/unit/test_validate_research_archive.py` |
| files added (NEW artifacts) | 56 per-pair per-fold summary JSONs + 56 trades CSVs + `walk_forward/{plan.json,plan.md,results.json,results.md,fold_detail.json}` + `financing/{financing_run.json,financing_run.md,financing_summary.json}` + `risk/{diagnostics.json,diagnostics.md}` |
| total backtest artifact dir | ~530 KB (compact text only; no equity CSV; no SQLite; no scraped pages) |
| files edited | 4 (`tests/unit/test_validate_research_archive.py`, `docs/research/EVIDENCE_MANIFEST.json`, `docs/research/STRATEGY_STATUS.md`, `docs/research/EVIDENCE_INDEX.md`, `docs/research/CAMPAIGN_014_STATUS.md`) |
| markdown LOC added | ~3,800 |
| pytest count | **968 / 968 PASS** (unchanged baseline; test_real_manifest_has_all_thirteen_campaigns → test_real_manifest_has_all_fourteen_campaigns) |
| ruff findings | **3 pre-existing** in `research/lean_parity/algorithms/` (unchanged) |

## 2. Commits by phase

| phase | commit | scope |
|---|---|---|
| Phase 0 | `fc9538a` | repo truth audit + fixture date-verification audit + sprint plan |
| Phase 1 | `6dd72b4` | candle + event-fixture provenance |
| Phase 2 | `94c889a` | authoritative 8-fold walk-forward plan |
| Phase 3 | `cb29956` | per-fold runner `scripts/run_campaign_014.py` |
| Phase 4 | `51b3b4b` | execute 8-fold × 7-pair walk-forward (REJECT) |
| Phase 5 | `a7f6a37` | walk-forward verdict + null-baseline + turnover gates (REJECT — direction-of-trade falsification) |
| Phase 6 | `205bea1` | financing overlay (ESTIMATED + conservative stress; −$10.64; verdict unchanged) |
| Phase 7 | `b8b0ceb` | portfolio-risk diagnostics + event-class clustering (FOMC = 0 trades; NFP dominates losses) |
| Phase 8 | `e364717` | independent verifier status (NOT REQUIRED for REJECT) |
| Phase 9 | (this commit) | campaign status + evidence manifest + sprint summary + final validation |

## 3. Final verdict

| dimension | value |
|---|---|
| **research verdict** | **REJECT (direction-of-trade falsification)** |
| sub-classification rationale | OUTSIDE CAMPAIGN_011 indistinguishability band on all 4 PnL-direction dimensions, on the WORSE side; failure is NOT turnover-amplification (turnover within budget) |
| approval status | **NO** |
| inherited gates passing | 2 / 8 |
| turnover gates passing | 2 / 2 (PASS) |
| fixture-coverage gate | PASS (all 8 folds) |
| null-baseline meaningful improvement (over CAMPAIGN_011) | 0 / 6 (5 regress, 1 tied) |

## 4. Final aggregate metrics

| metric | value | CAMPAIGN_011 null | gate |
|---|---:|---:|---|
| total trades | 720 | 1,177 | ≥ 200 (turnover ≤ 800) |
| total raw signals | 1,240 | n/a | ≤ 1,500 |
| aggregate expectancy R | **−0.14774** | −0.0024 | ≥ 0.05 |
| aggregate profit factor | **0.00** | 0.91 | ≥ 1.10 |
| aggregate return % | **−30.8516** | −0.53 | meaningfully + |
| pairs positive | **0 / 7** | 3 / 7 | ≥ 4 / 7 |
| fold pass rate | **0 / 8** | 0 / 8 | 100 % |
| single_fold_dominance % | 16.24 | 40.1 | ≤ 60 |
| single_pair_dominance % | 20.69 | 36.5 | ≤ 40 |
| financing cashflow (stress) USD | **−10.64** | −24.38 | (LOWEST of any real candidate) |
| MAX_OPEN_POSITIONS_EXCEEDED | 0 | 0 | n/a |

## 5. Validations run

```
python -m pytest -q                                          # 968 / 968 PASS
ruff check src tests scripts research                        # 3 pre-existing in lean_parity (unchanged)
python scripts/validate_research_archive.py                  # ALL PASS (14 campaigns; 14 diagnostic artifacts; manifest schema PASS)
python scripts/check_research_freeze.py                      # ALL PASS
python scripts/scan_artifacts_for_secrets.py                 # PASSED
python -m forex_bot.cli paper-loop -c configs/paper.yaml     # refused
python -m forex_bot.cli demo-loop -c configs/practice.yaml   # refused
python -m forex_bot.cli --help                                # no live-loop
git status --short                                            # clean (only .claude tooling cache)
```

## 6. Six-evidence-ladder status (CAMPAIGN_014)

| item | name | status |
|---|---|---|
| 1 | data provenance | **COMPLETE** (Phase 1; byte-identical to CAMPAIGN_010/011/012/013 stores) |
| 2 | walk-forward verdict | **COMPLETE — REJECT** (Phase 5) |
| 3 | financing overlay | **COMPLETE** (ESTIMATED + conservative stress; −$10.64 impact; verdict unchanged) |
| 4 | risk diagnostics | **COMPLETE** (standard battery + CAMPAIGN_014-specific event-class clustering + per-event-class per-pair heatmap + concurrent-firing diagnostic) |
| 5 | independent verifier | **NOT REQUIRED for REJECT verdict** |
| 6 | deliberate human approval | **MOOT for REJECT** |

## 7. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| **CAMPAIGN_014** | **REJECT (this sprint)** |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | **no** (4 refusal layers; intact) |
| broker / OANDA call this sprint | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| historical campaign verdict change | **none** |
| parameter "tweak" or "rescue" | **none** (frozen parameters unchanged) |
| `max_open_positions` relaxation | **none** |
| pair carve-out post-result | **none** (ECB / BoE positive cells flagged but NOT used; Pattern P binding) |
| fixture modification mid-sprint | **none** (BoJ 2026-03-18 vs 2026-03-19 drift logged for future fixture-revision sprint, NOT patched) |

## 8. Two findings of independent research value

### 8.1 FOMC = 0 trades (structural untestability)

The 51 FOMC events in the fixture generated ZERO trades. The
mechanism: FOMC at ~19:00 UTC → event H4 bar 18:00–22:00 UTC →
trigger H4 bar opens 22:00 UTC. The 22:00 UTC trigger bar falls
inside the session_filter's rollover window (16:45–17:15 ET
overlaps 22:00 UTC EDT). All 7 USD pairs' FOMC signals get
SESSION_BLOCKED.

**Implication for future C7-family work:** the C7 hypothesis's
claim about FOMC is structurally untestable on this universe +
session filter. Restructuring the session_filter to enable FOMC
trading would constitute a NEW candidate (universe / cost-model
identity change), not a parameter tweak.

### 8.2 NFP dominates and loses (direction-of-trade falsification)

NFP-triggered trades: 571 / 720 = 79 % of all trades; PnL
−$151.17 = 98 % of all losses. Near-50/50 long/short balance
(284 long / 287 short) on NFP → losses on BOTH sides. The
strategy correctly identifies NFP event-bar direction and trades
counter; the data show post-event H4 bar CONTINUES the NFP
event-bar's direction.

**Implication:** the "post-event H4 mean-reverts" hypothesis is
empirically wrong on this universe. An "NFP continuation"
strategy (opposite direction) would be a NEW candidate, not a
re-tune of CAMPAIGN_014.

## 9. Remaining blockers (unchanged from scaffold sprint)

| blocker | affects | next step |
|---|---|---|
| MODELED financing refused at 4 layers | C2 + future carry candidates | `research-financing-modeled-capture-credentialed-001` (human authorization required; out of scope) |
| engine lacks paired-entry support | C4 + future paired/spread candidates | `infra-engine-paired-entry-support-001` (multi-sprint; HOLD) |
| verifier capability-locked to CAMPAIGN_002 | item 5 for any non-trend_following paper-promotion candidate | `infra-free-local-parity-verifier-<FAMILY>-NNN` per family; not blocking |
| 3 pre-existing ruff findings in lean_parity archive | cosmetic | `infra-ruff-lean-parity-archive-cleanup-001` (low priority) |
| **CAMPAIGN_014 BoJ 2026-03 fixture drift (post-coverage)** | future fixture re-use | `research-calendar-event-window-anomaly-fixture-audit-001` (low priority; affects nothing in 2025-11-29-and-earlier windows) |

**None of these block any current research.**

## 10. Recommended next branch

### **Next discovery sprint** (NOT a C7 retry)

CAMPAIGN_014 is REJECT. Per binding rules:

- **No C7 re-attempt is permitted** (Patterns O / P / Q binding;
  any C7 variant requires a NEW discovery sprint).
- **No pair-only ECB / BoE carve-out** (Pattern P binding).
- **No NFP-only strategy** (Pattern P binding; per-event-class
  carve-out from a rejected portfolio is the same overfit class).
- **An NFP-continuation strategy** (opposite direction from C014)
  would be genuinely new but requires a fresh discovery sprint
  with pre-committed gates.

The recommended next branch is therefore the **next discovery
sprint** (e.g. `research-new-candidate-strategy-discovery-006`)
to consider:

- A genuinely new event-window candidate (continuation, finer
  timeframe, or different event-class subset) — with its own
  fresh pre-commit
- A different family entirely (C10 weekly-bias H4-execution; C11
  long-horizon realized-vol-parity sizing — modifier only; C12
  monthly fundamentals-spread rebalance — currently on the
  discovery-005 shortlist as deferred but not abandoned)
- An infrastructure unblock (`research-financing-modeled-capture-
  credentialed-001` for MODELED financing; `infra-engine-paired-
  entry-support-001` for paired entries; etc.)

The discovery-005 sprint left a 4-family shortlist (C7 = exhausted
this sprint; C10, C11, C12 still candidates). A discovery-006
sprint would re-evaluate those + propose new candidates with the
CAMPAIGN_014 REJECT data point as binding context.

## 11. Exact files to review first

In review order:

1. **[`CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_SUMMARY.md`](CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_SUMMARY.md)** — this one-page sprint summary.
2. **[`CAMPAIGN_014_EVIDENCE_SUMMARY.md`](CAMPAIGN_014_EVIDENCE_SUMMARY.md)** — one-page evidence summary.
3. **[`CAMPAIGN_014_STATUS.md`](CAMPAIGN_014_STATUS.md)** — campaign-level REJECT status.
4. **[`CAMPAIGN_014_WALK_FORWARD_RESULT.md`](CAMPAIGN_014_WALK_FORWARD_RESULT.md)** — Phase 5 walk-forward verdict + null-baseline comparison.
5. **[`CAMPAIGN_014_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_014_PORTFOLIO_RISK_DIAGNOSTICS.md)** — Phase 7 diagnostics with FOMC = 0 trades + NFP-dominated-losses findings.
6. **[`CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md`](CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md)** — Phase 0 fixture audit.
7. **[`CAMPAIGN_014_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_014_WALK_FORWARD_EXECUTION.md)** — Phase 4 execution log.
8. **[`CAMPAIGN_014_FINANCING_OVERLAY.md`](CAMPAIGN_014_FINANCING_OVERLAY.md)** — Phase 6 financing impact.
9. **[`CAMPAIGN_014_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_014_INDEPENDENT_VERIFIER_STATUS.md)** — Phase 8 verifier status (NOT REQUIRED for REJECT).
10. **[`CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md)** — Phase 0 plan (reference).
11. **[`CAMPAIGN_014_DATA_PROVENANCE.md`](CAMPAIGN_014_DATA_PROVENANCE.md)** — Phase 1 provenance.
12. **[`CAMPAIGN_014_WALK_FORWARD_PLAN.md`](CAMPAIGN_014_WALK_FORWARD_PLAN.md)** — Phase 2 walk-forward plan.
13. Source: `scripts/run_campaign_014.py` (the runner).
14. Source: `scripts/build_campaign_014_financing_overlay.py`.
15. Source: `scripts/build_campaign_014_risk_diagnostics.py`.
16. **[`backtests/CAMPAIGN_014_calendar_event_window_anomaly/`](../../backtests/CAMPAIGN_014_calendar_event_window_anomaly/)** — all per-fold artifacts.
17. **[`CALENDAR_EVENT_WINDOW_ANOMALY_001_SUMMARY.md`](CALENDAR_EVENT_WINDOW_ANOMALY_001_SUMMARY.md)** — predecessor scaffold-sprint summary (for context).
18. **[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)** — binding null baseline (used for verdict).
19. **[`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md)** — binding turnover-budget gate (PASSED here).
20. **[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)** — approval-process binding (no approval possible).

## 12. Cross-links

- [`CALENDAR_EVENT_WINDOW_ANOMALY_001_SUMMARY.md`](CALENDAR_EVENT_WINDOW_ANOMALY_001_SUMMARY.md) (predecessor scaffold sprint's summary)
- [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md) (binding pre-commit)
- [`CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`](CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md) (binding R1-R8 spec)
- [`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md) (scaffold-sprint fixture provenance)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) (binding turnover budget)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) (binding patterns; Patterns M–W constrain future C7-family work)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md) (binding approval process)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md) (updated this sprint)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) (updated this sprint)
- [`EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json) (updated this sprint: 13 → 14 campaigns)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md) (financing-model status; MODELED still refused)
