# `research-new-candidate-strategy-discovery-005` — Sprint Summary

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-005`
(worktree branch `claude/affectionate-fermi-d950fc`) · `strategy_evidence: false`

End-of-sprint summary for the discovery-005 sprint. Re-opened
candidate selection after CAMPAIGN_013's REJECT; codified the
turnover-amplification anti-pattern as a first-class binding
guardrail; selected **C7 — Calendar-Event Window Anomaly (CEWA)** as
the next real candidate (`calendar_event_window_anomaly 0.1.0-c014`,
CAMPAIGN_014). **Design / discovery sprint only — no strategy
implementation, no backtest, no broker call.**

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 / 013 remain
> REJECT. `configs/approved_strategies.yaml` remains `approved: []`.
> Paper / demo / live remain blocked. CAMPAIGN_011 is the null
> baseline only, not a trading candidate.

## 1. What changed

| dimension | value |
|---|---|
| commits this sprint | 11 (Phase 0 through Phase 10) |
| files added | 11 NEW docs |
| files edited | 2 (EVIDENCE_INDEX + STRATEGY_STATUS) |
| Python LOC added | **0** |
| test LOC added | **0** |
| markdown LOC added | ~3,200 |
| pytest count | **875 → 875** (preserved) |
| ruff findings | **3 pre-existing** in `research/lean_parity/algorithms/` (unchanged baseline) |

## 2. Commits by phase

| phase | commit | scope |
|---|---|---|
| Phase 0 | `4034e77` | repo truth audit & discovery plan |
| Phase 1 | `c3376ff` | CAMPAIGN_013 rejection closeout |
| Phase 2 | `a8d9e53` | turnover-amplification anti-pattern (Patterns M–Q) |
| Phase 3 | `b567dc6` | guardrails addendum (Patterns R–W) |
| Phase 4 | `f0deb51` | reassess candidates + infrastructure (18-axis scoring) |
| Phase 5 | `2ee6c79` | candidate family shortlist (C7 reaffirmed + C10–C13 fresh) |
| Phase 6 | `253ae34` | select next path — C7 (CEWA) |
| Phase 7 | `327a8c0` | C7 implementation + evaluation design |
| Phase 8 | `3ee1766` | future scaffold + evidence branch specs |
| Phase 9 | `4d378cc` | helper decision — NO helper |
| Phase 10 | (this commit) | summary + EVIDENCE_INDEX + STRATEGY_STATUS update + final validation |

## 3. Latest repo state

| dimension | value |
|---|---|
| pytest count | 875 passed (4.x s) |
| ruff status | 3 pre-existing in `research/lean_parity/algorithms/` (unchanged) |
| `validate_research_archive.py` | ALL PASS (13 campaigns) |
| `check_research_freeze.py` | ALL PASS (loops refuse) |
| `scan_artifacts_for_secrets.py` | PASSED |
| `paper-loop` / `demo-loop` | refuse |
| `live-loop` | does not exist |
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |

## 4. CAMPAIGN_013 rejection closeout (Phase 1)

Codified CAMPAIGN_013's REJECT verdict + off-limits parameter
surface (14+ off-limits parameters / variant shapes + 9 disqualified
variant examples) and a binding cooldown rule. The cross-pair-
rotation family is on indefinite cooldown until a future human
explicitly authorizes a "materially different" cross-sectional FX
thesis.

## 5. Turnover-amplification anti-pattern (Phase 2)

Codified the empirically-visible turnover-amplification slope as a
first-class binding anti-pattern. The slope (binding evidence over
3 independent pre-committed campaigns, same universe + cost model):

| campaign | filter shape | trades | aggregate return % | expectancy R |
|---|---|---:|---:|---:|
| CAMPAIGN_011 (null) | PRNG `entry_probability = 0.05` | 1,177 | −0.53 % | −0.0024 |
| CAMPAIGN_012 (regime) | D1AGG ATR-percentile ≥ 0.70 HIGH-VOL gate | 3,726 | −43.52 % | −0.0521 |
| CAMPAIGN_013 (rotator) | 8-currency rank-gap ≥ 4/7 | 7,940 | −113.36 % | −0.0564 |

Monotonic in trade count on every binding axis. The pattern is
specific: on H4 majors under the inherited cost model, adding a
turnover-amplifying filter to a negative-edge entry direction
produces materially worse results, not better.

Binding turnover-budget requirement for future candidates: pre-
declare expected trade-count range, derivation, comparison to
CAMPAIGN_011 / 012 / 013, why signal frequency survives costs, REJECT
trigger if raw signal rate explodes, no `max_open_positions` /
risk-limit relaxation to rescue trade count.

5 new disqualifying patterns:

- **M** — high-frequency H4 firehose entries (≥ 2 × CAMPAIGN_013 count)
- **N** — broad simultaneous multi-pair entries without portfolio-level edge proof
- **O** — turnover-amplifying filter on rejected entry direction (the headline)
- **P** — pair-only survivor selection from rejected campaigns
- **Q** — cost-insensitive signal design (no per-trade cost section)

## 6. Updated anti-overfit guardrails (Phase 3)

Discovery-005 addendum adds 6 new disqualifying overfitting patterns
(R–W) specifically motivated by CAMPAIGN_013 (additive to A–G base
guardrails + H–L discovery-004 addendum + M–Q Phase 2 anti-pattern):

- **R** — same cross-pair rank gate, different threshold (forbidden)
- **S** — same cross-pair ranking metric, different lookback (forbidden)
- **T** — same cross-pair rotator, pair-filtered after rejection (forbidden)
- **U** — same cross-pair rotator with session/regime rescue filter (forbidden)
- **V** — high-turnover variant of any rejected family (forbidden)
- **W** — select new family because it fixes a CAMPAIGN_013 per-pair / per-fold artifact (forbidden)

Plus "genuinely new" criteria (11 axes; expanded from discovery-004's
7) any candidate must satisfy after the now-8 rejected baseline (5
prior + CAMPAIGN_011 null + CAMPAIGN_012 real + CAMPAIGN_013 real),
including: explicit turnover budget (Patterns M–Q binding), explicit
cost section (Pattern Q binding), not a high-frequency firehose
(Pattern M binding), not broad simultaneous-pair without portfolio
edge proof (Pattern N binding).

## 7. Candidate and infrastructure paths reassessed (Phase 4)

10 paths scored on 18 axes:

| path | type | status |
|---|---|---|
| C2 carry overlay | candidate | DEFERRED (gated by infra-A) |
| C4 vol-expansion paired straddle | candidate | DEFERRED (gated by infra-B; multi-sprint engine rewrite) |
| C6 cross-pair rotation | candidate | **REJECTED in CAMPAIGN_013; cooldown ≥ 3 sprints** |
| C7 CEWA | candidate | **VIABLE — LEAD** |
| C8 MWVCB | candidate | VIABLE; elevated CAMPAIGN_004/012 proximity risk |
| C9 TODCAMRS | candidate | VIABLE; weakest distinctness (5/6); highest Pattern Q burden |
| C10+ new families | candidate | VIABLE (Phase 5 shortlist) |
| infra-A `research-financing-modeled-capture-credentialed-001` | infrastructure | HOLD (requires human authorization) |
| infra-B `infra-engine-paired-entry-support-001` | infrastructure | HOLD (multi-sprint; only C4 justifies today) |
| infra-C verifier extension per-family | infrastructure | DEFER (post-PASS; no candidate has passed) |
| infra-D ruff cleanup | infrastructure | LOW PRIORITY (cosmetic) |

Recommended path: new candidate sprint with C7 (CEWA) as lead + C10+
shortlist exploration in Phase 5.

## 8. New candidate families proposed (Phase 5)

Shortlist of 4 active candidates + 1 disqualified + 1 infra fallback:

| candidate | name | distinctness | turnover | blockers |
|---|---|:---:|---|---|
| **C7** | Calendar-Event Window Anomaly (CEWA) | 8/8 | LOW (~150–400/4y) | small one-time calendar fixture (broker-free) |
| **C10** | Weekly-Bias H4-Execution (WBH4E) | 8/8 | LOWEST (~50–350/4y) | NONE |
| **C11** | Long-Horizon Realized-Vol-Parity Sizing (LHRVPS) | n/a (sizing) | inherits | engine sizing-injection point + paired entry candidate |
| **C12** | Monthly Fundamentals-Spread Rebalance (MFSR) | 8/8 | LOW (~150–340/4y) | NONE; financing burden meaningful at 21-day hold |
| **C13** | Quarterly Earnings-Season Calendar Filter (QESCF) | n/a | n/a | **DISQUALIFIED** (Pattern U + K + G; rejected-family stack) |
| infra-A | MODELED financing capture | n/a | n/a | HOLD — requires human authorization |

15 disqualified family variants documented (C6 retunes, regime-
switcher retunes, trend/breakout/MR/session/pullback retunes, weighted-
pair-vote ensemble, high-frequency M30 momentum, all-pair simultaneous
entry, C13 QESCF).

## 9. Selected next path (Phase 6)

# **SELECTED: C7 — Calendar-Event Window Anomaly (CEWA)**

| field | value |
|---|---|
| candidate id | C7 |
| strategy id | `calendar_event_window_anomaly` |
| version | `0.1.0-c014` |
| campaign label | **CAMPAIGN_014** |
| scaffold branch | `research-calendar-event-window-anomaly-001` |
| evidence branch | `research-calendar-event-window-anomaly-walk-forward-001` |

**Why C7 over C10 / C12 / C11 / C13 / infra-A / infra-B / infra-C / infra-D:**

- Economically grounded hypothesis (post-event mis-priced-surprise
  mean reversion is well-documented FX phenomenon)
- Reusable calendar-fixture data primitive for future event-window
  candidates
- Per-event-class diagnostic surface (NFP/FOMC/ECB/BoJ/BoE × 7 pairs)
  produces high-information evidence even if REJECT
- Structural defense against turnover-amplification (event set is
  finite per year, not threshold-tuned)
- No infrastructure prerequisites (zero broker dependency, no engine
  change, no MODELED financing requirement)

## 10. Why selected path is distinct from rejected families

| rejected family | shared mechanism with C7? | distinctness argument |
|---|---|---|
| CAMPAIGN_002 (`trend_following`) | NO | no EMA / Donchian / single-pair direction trigger; signal is *post-event counter-trend* |
| CAMPAIGN_010 (`session_breakout`) | NO | no Asian-range / London-window logic |
| CAMPAIGN_011 (`random_entry_anchor`, null) | NO | fully deterministic from calendar fixture + price; no PRNG |
| CAMPAIGN_012 (`regime_switcher_atr_percentile`) | NO | no single-pair vol-percentile gate; no close-vs-close trend filter |
| CAMPAIGN_013 (`cross_pair_currency_strength_rotation`) | NO | no cross-pair ranking; no cross-sectional FX-rank metric |
| CAMPAIGN_004 (`volatility_breakout`) | NO | no ATR-compression / breakout logic |
| CAMPAIGN_007 (`pullback_continuation`) | NO | no pullback definition |
| CAMPAIGN_008 / 009 (`mean_reversion`) | LIMITED — both counter-trend, but C7's *trigger* is event-time-conditional (not statistic-conditional) and ~25–60 × lower turnover |

**Distinctness vs each rejected family: 8 / 8.**

## 11. Why this is not parameter tuning

- No existing strategy in the bespoke engine implements calendar-
  event-window-conditional entries; all 8 implemented strategies gate
  on price features only (trend, breakout, pullback, range Z-score,
  session window, PRNG, vol percentile, cross-pair rank).
- C7 requires a new event-calendar fixture (~10–50 KB committed JSON
  / CSV) and a new event-calendar loader — **new data primitive**,
  not a knob on existing one.
- C7's frozen parameters pre-committed pre-implementation; no sweep
  around prior campaigns' values; no CAMPAIGN_013 or CAMPAIGN_012
  parameter reused.

## 12. Implementation design summary (Phase 7 highlights)

- **R1–R8 binding rule table** — warm-up, event-window proximity
  trigger, counter-direction signal, overlap precedence (FOMC > NFP >
  ECB > BoJ > BoE), ATR stop, time stop, re-entry block, fail-closed.
- **5 new no-lookahead invariants** binding for calendar access
  (event-time ≤ bar-complete-time; loader exposes no future events;
  no surprise/consensus/revision; per-fold fixture-coverage check;
  first-published-only values).
- **10 frozen parameters** pre-committed (`event_set`,
  `impact_ordering`, `post_event_window_bars=6`, `atr_lookback=14`,
  `atr_stop_multiple=2.0`, `max_post_event_bars=6`,
  `re_entry_block_bars=3`, `risk_per_trade_pct=0.005`,
  `initial_equity_per_pair=500`, `event_warmup_bars=1`).
- **`CalendarEventWindowAnomalyStrategyConfig` schema** with
  `extra="forbid"` + `@model_validator` rejecting invalid bounds.
- **≥ 30 unit tests** planned (config validation, happy path, counter-
  direction signal, fail-closed cases, overlap precedence, re-entry
  block, max-hold, ATR stop, 5 no-lookahead invariants, fixture
  loader, per-event-class impacted-pairs mapping, forbidden imports,
  approval regression, determinism, multi-pair per-event-class,
  pre-event-bar handling).
- **Walk-forward** inherits CAMPAIGN_010 / 011 / 012 / 013 plan
  verbatim (8 folds rolling/frozen) + null-baseline comparison gate
  + turnover-budget gate (REJECT > 800 trades) + signal-density gate
  (REJECT > 1,500 signals) + event-fixture coverage contract
  (BLOCKED if any fold uncovered).
- **Cost section** (Pattern Q binding): per-trade ~1.5–4 bp total;
  gross expectancy ≥ 7 bp hypothesized; net ≥ 5 bp expected;
  aggregate-R ≥ 0.05 R at upper trade-count budget.
- **Financing** ESTIMATED + conservative stress; MODELED refused
  (live-promotion blocker stands; not C7's concern at short hold).
- **Risk diagnostics** include CAMPAIGN_014-specific event-class
  clustering + per-event-class per-pair sensitivity + pre-event vs
  post-event direction breakdown + entry-window concentration.
- **Verifier extension** required only if `RESEARCH_PASS_UNAPPROVED`.

## 13. Future branch specs (Phase 8)

Two binding prompt templates for the next Claude Code instances:

- **`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md`** — scaffold sprint
  `research-calendar-event-window-anomaly-001` (9 phases including
  Phase 1b event-fixture compilation; no evidence run; test target
  875 → ≥ 905).
- **`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`** — evidence sprint
  `research-calendar-event-window-anomaly-walk-forward-001` (10
  phases; runs walk-forward + financing + risk + verifier-assessment;
  binding turnover-budget + signal-density + event-fixture coverage
  contracts).

## 14. Safety state at sprint close

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | REJECT (null-model anchor; untouched) |
| CAMPAIGN_012 | REJECT (untouched) |
| CAMPAIGN_013 | REJECT (untouched) |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| live-promotion financing blocker | stands |
| broker / OANDA call this sprint | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| historical campaign verdict change | **none** |
| parameter "tweak" or "rescue" | **none** (no rejected family revived) |
| pytest baseline | 875 (preserved) |
| ruff baseline | 3 pre-existing (unchanged) |
| code added this sprint | **none** |
| tests added this sprint | **none** |

## 15. Validations run

```
python -m pytest -q                                        # 875 passed
ruff check src tests scripts research                      # 3 pre-existing
python scripts/validate_research_archive.py                # ALL PASS
python scripts/check_research_freeze.py                    # ALL PASS
python scripts/scan_artifacts_for_secrets.py               # PASSED
python -m forex_bot.cli paper-loop -c configs/paper.yaml   # refused
python -m forex_bot.cli demo-loop -c configs/practice.yaml # refused
python -m forex_bot.cli --help                             # no live-loop
git status --short                                         # clean
```

## 16. Remaining blockers

| blocker | affects | next step |
|---|---|---|
| MODELED financing refused at 4 layers | C2 + future carry candidates | `research-financing-modeled-capture-credentialed-001` (requires human authorization; out of scope for Claude Code) |
| engine lacks paired-entry support | C4 + future paired/spread candidates | `infra-engine-paired-entry-support-001` (multi-sprint; HOLD until additional multi-family justification) |
| verifier capability-locked to CAMPAIGN_002 | item 5 of six-evidence ladder for any non-`trend_following` paper-promotion candidate | `infra-free-local-parity-verifier-<FAMILY>-NNN` per family; not needed until a candidate reaches `RESEARCH_PASS_UNAPPROVED` |
| 3 pre-existing ruff findings | cosmetic | `infra-ruff-lean-parity-archive-cleanup-001` (low priority) |
| engine sizing-injection point absent | C11 (LHRVPS) sizing modifier; non-blocking for entry-signal candidates | small infra sprint if a future entry candidate justifies pairing with C11 |

**None of these block CAMPAIGN_014's scaffold sprint or evidence sprint.**

## 17. Recommended next branch

### **`research-calendar-event-window-anomaly-001`** (scaffold sprint)

The 9-phase scaffold-branch prompt is the full text of
[`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md).
Adds strategy module + event-calendar loader + ≥ 30 unit tests +
event-fixture (one-time compile from public sources) + research
config + CAMPAIGN_014 docs + non-evidence smoke. Test-count target
875 → ≥ 905. No backtest run; no broker call; no approval.

After the scaffold completes, the recommended sprint after is
**`research-calendar-event-window-anomaly-walk-forward-001`**
(the 10-phase evidence sprint, full prompt in
[`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md)).

## 18. Exact files to review first

In review order:

1. **[`NEW_CANDIDATE_STRATEGY_DISCOVERY_005_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_005_SUMMARY.md)** — this one-page sprint summary.
2. **[`NEXT_PREFERRED_DIRECTION_005.md`](NEXT_PREFERRED_DIRECTION_005.md)** — Phase 6 selection (C7 / CAMPAIGN_014); selection rationale vs every other path.
3. **[`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md)** — binding R1–R8 + 10 frozen parameters + 5 no-lookahead invariants + ≥ 30 expected tests + turnover-budget + cost section.
4. **[`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md)** — the prompt for the next sprint.
5. **[`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md)** — the prompt for the sprint after that.
6. **[`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md)** — the off-limits parameter surface for the rejected cross-pair-rotation family.
7. **[`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md)** — binding turnover-budget guardrail (Patterns M–Q) + slope evidence.
8. **[`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md)** — binding Patterns R–W + "genuinely new" criteria.
9. **[`NEXT_DIRECTION_REASSESSMENT_005.md`](NEXT_DIRECTION_REASSESSMENT_005.md)** — Phase 4 candidate/infra scoring (18 axes).
10. **[`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md)** — Phase 5 C7 / C10 / C11 / C12 / C13 proposals.
11. **[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)** (reference) — binding null baseline.
12. **[`NEW_CANDIDATE_DISCOVERY_005_HELPER_DECISION.md`](NEW_CANDIDATE_DISCOVERY_005_HELPER_DECISION.md)** — no-helper rationale.
13. (Reference) **[`NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md)** — Phase 0 plan.

## 19. Cross-links

- [`CAMPAIGN_013_EVIDENCE_SUMMARY.md`](CAMPAIGN_013_EVIDENCE_SUMMARY.md) (the predecessor evidence sprint's outcome)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md) (predecessor sprint summary)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_SUMMARY.md) (predecessor discovery sprint)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
