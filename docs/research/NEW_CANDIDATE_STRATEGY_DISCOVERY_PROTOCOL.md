# New Candidate Strategy Discovery — Protocol

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-001`
`strategy_evidence: false`

Protocol the discovery sprint (and its outputs) must follow.
Defines what "meaningfully distinct from CAMPAIGN_002" means, the
allowed and disallowed family categories, the overfitting patterns
that automatically disqualify a proposal, the frozen-parameter
requirement, the walk-forward requirement, the financing overlay
requirement, the portfolio-risk diagnostic requirement, and the
no-approval rule.

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked. This document binds the *design*
> of any future candidate; it does not approve one. Every artifact
> emitted under this protocol carries `strategy_evidence: false`.

## 1. Goal of the discovery sprint

Produce a documented, theoretically-justified design for **one**
future candidate strategy family that:

- is **meaningfully distinct** from CAMPAIGN_002 (`trend_following
  0.1.0`) and from the other three rejected families
  (`volatility_breakout 0.1.0-c004`, `pullback_continuation`,
  `mean_reversion`);
- is compatible with the bespoke `BacktestEngine` as it exists
  today (no engine changes assumed);
- can be **frozen-parameter** walk-forward evaluated using the
  existing harness (`research/walk_forward/`);
- carries a **financing overlay** computed by the existing
  research calculator (`research/financing/`);
- has a pre-stated rejection criterion that would be hard to
  unconsciously curve-fit around.

The sprint stops at design. Implementation, backtest, and
approval are explicitly out of scope and are *separate, future,
human-authorized* sprints.

## 2. Non-goals (binding)

- **No approval.** No strategy may be added to
  `configs/approved_strategies.yaml`.
- **No paper / demo / live changes.** `paper-loop`, `demo-loop`,
  `live-loop` are not touched.
- **No CAMPAIGN_002 tuning, revival, or parameter search.**
- **No tweak-driven rescue** of any of the four rejected families.
  (A reuse of an existing family's *name* is allowed only as a
  shared parameter type, e.g. ADX threshold, never as a recycled
  signal definition.)
- **No strategy code** in this sprint, including "toy / no-signal
  scaffolds".
- **No broker / OANDA call.** No `.env` read. No credentials
  printed.
- **No engine-PnL edit.** No `src/forex_bot/financing.py` edit.
- **No QuantConnect / LEAN.**
- **No new external dependency.**

## 3. "Meaningfully distinct from CAMPAIGN_002"

A proposed family is **meaningfully distinct from CAMPAIGN_002**
only if **all** of the following hold; otherwise it is a tweak,
not a new family:

| dimension | distinctness requirement |
|---|---|
| theoretical bucket | not "EMA-crossover trend on H4 majors" and not a relabelled version of one. |
| primary entry signal | not "Donchian-20 breakout in the direction of EMA-50 vs EMA-200". |
| primary exit signal | not "ATR-multiple trail with N-bar time stop" *as the sole exit*. |
| timeframe / universe | identical universe (six majors + NZD_USD on H4) is **allowed only** when the strategy is also testable on a strict subset (e.g. one pair, one session). |
| data inputs | must use at least one data input not used by CAMPAIGN_002 (session-of-day metadata, daily ATR percentile, regime label, weekday seasonal, financing rate, etc.). |
| failure-mode hypothesis | must articulate a *new* reason CAMPAIGN_002 lost (e.g. "we lost because we held through choppy sessions") and a *new* mechanic that addresses it. |

The same six rows apply pair-wise against the other three rejected
families. If a proposal cannot show distinctness on ≥ 3 of the 6
rows vs. *every* rejected family, it is rejected at the shortlist
stage.

## 4. Allowed strategy-family categories

The shortlist must propose categories from this whitelist (or
make an explicit, justified case for an addition):

- **Carry-aware position overlay** — only takes long positions in
  positive-swap pairs and short positions in negative-swap pairs,
  conditioned on a regime filter. Depends on the financing
  calculator's `RatePair` / sign convention; gates against an
  obvious "carry overfit" by requiring a *price-direction*
  edge in addition to the carry direction.
- **Session-of-day breakout (non-CAMPAIGN_004 flavour)** — e.g. a
  London-open breakout from the Asian-session range. Distinct
  from CAMPAIGN_004 (which used ATR compression, not a session
  range) and from CAMPAIGN_002 (which used Donchian-20). Depends
  on session-tag metadata on the candle store.
- **Time-of-week seasonal filter** — e.g. avoid Friday late /
  Monday open / pre-NFP windows. **Stand-alone** only as a
  diagnostic; **as a filter** on a new entry signal it is allowed
  as a secondary input but cannot be the entire edge.
- **Volatility-regime compression / expansion** — entries
  gated on volatility-regime changes detected from a slower
  timeframe (e.g. daily ATR percentile). Distinct from CAMPAIGN_004
  because the entry mechanic is regime-switching, not breakout.
- **Mean-reversion with explicit *fresh* regime filter** — only
  authorized if the regime filter is genuinely new (not c008's
  ADX-14, not c009's midline-target). The prior mean-reversion
  campaigns failed their pre-committed train gates; a third look
  is high-risk and must be defensible per
  [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md) §7.
- **Baseline / null model** — e.g. a buy-and-hold, a coin-flip
  entry on H4 close, an always-flat baseline. Allowed only as a
  diagnostic comparison anchor for the preferred candidate;
  cannot itself be the "preferred candidate" for paper promotion.

A proposal in any of these categories must still satisfy §3
(distinctness from every prior rejected family).

## 5. Disallowed strategy-family categories

The shortlist may not propose:

- **A retitle of an already-rejected family** with the same
  signal definition but new parameters (overfitting on
  CAMPAIGN_002 / 003 / 004 / 007 / 008 / 009).
- **A pure parameter sweep** of any rejected family.
- **A "skip-X" filter** designed in response to the *specific
  losing trades* of a prior campaign.
- **A news / event filter** as a standalone family unless and
  until reliable historical event data is committed
  ([`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md) §8).
- **A multi-asset family** (index / commodity / crypto) unless
  the new asset universe is first committed under a separate
  human-authorized data-foundation sprint
  ([`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md) §5).
- **A D1-only family** until the D1 backtest blocker is lifted
  ([`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md) §2,
  CAMPAIGN_006).
- **An H1 family** unless the shortlist explicitly justifies the
  noise floor and shows the strategy is theoretically scalable
  to H4.
- **Any strategy whose backtest cannot be reproduced
  deterministically** by the bespoke engine.
- **Any strategy that requires unmodeled financing in its
  result** (post-financing PnL must be the headline number).
- **Any strategy whose signal includes the test window's data**
  ("trained on 2020–2026, evaluated on 2020–2026" is forbidden;
  the walk-forward harness enforces fold-boundary leakage
  rules, but the proposal must also be no-lookahead within each
  fold).

## 6. Frozen-parameter requirement

A new candidate must declare every parameter as **frozen** in
its pre-commit before any backtest:

- Entry-signal parameters (lookback, threshold, ratio).
- Stop / target parameters (ATR multiple, fixed-pip, ratio).
- Exit-rule parameters (time stop, trail, target).
- Risk-engine inputs (position sizing fraction, daily loss limit).
- Universe and timeframe.

`parameter_mode = "frozen"` is the only mode the walk-forward
harness authorizes today
([`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
§1, §3). The `per_fold_from_train` / `per_fold_from_validation`
modes are schema-supported for future adaptive campaigns; using
them today violates the research freeze.

The preferred candidate's eval design (Phase B4) must record the
frozen-parameter set verbatim. Any later edit to that set
constitutes a *new* candidate that needs its own design pass.

## 7. Walk-forward requirement

A new candidate must commit to the walk-forward harness from the
start:

- **Plan generation** — `rolling_window_plan(...)` or
  `expanding_window_plan(...)` from `research/walk_forward/`.
- **Validation** — `validate_plan(plan)` must pass; min fold
  count ≥ 3, forward-only, no consecutive test-window overlap,
  all boundaries inside the universe.
- **Per-fold report** — `FoldMetrics` per fold; cross-checked
  by `AggregateMetrics.fold_pass_rate ==
  folds_passing_gates / fold_count`.
- **Verdict** — `WalkForwardResults.overall_verdict` is `PASS`
  or `REJECT`, never auto-`PASS`.

`WalkForwardResults.overall_verdict == "PASS"` is **one of six**
evidence items the candidate must accumulate before paper
([`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§8). It is not by itself sufficient.

## 8. Financing overlay requirement

A new candidate must compute and report a financing overlay using
the research calculator from
[`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md):

- Build a `list[PositionInterval]` from the candidate's committed
  trade artifacts (the candidate's per-campaign adapter writes
  this).
- Run `calculate_run(positions, rate_source, config)`.
- Use `default_stress_rate_source()` by default; or a
  `TableRateSource` built from one of the committed synthetic
  fixtures under `research/financing/fixtures/` when reporting
  pair-specific overlays.
- Dump both `financing_run.json` and `financing_run.md` as
  diagnostic artifacts.
- Embed `financing_treatment`, `financing_in_engine_pnl`,
  `financing_is_live_blocker`, `cashflow_home_total`,
  `cashflow_home_stress_total`, `missing_rate_event_count`
  verbatim in the campaign report.

The financing overlay is **diagnostic**; it does not approve
anything. `financing_treatment_blocks_approval` in
`src/forex_bot/financing.py` remains the authoritative gate.
Until MODELED financing exists for the candidate's pairs and
window — none does today — the candidate is structurally
ineligible for live promotion. Paper / demo promotion still
requires a human approval entry separately.

## 9. Portfolio-risk diagnostic requirement

A new candidate must produce at least the following
risk-engine diagnostics as part of its evidence package:

- per-pair exposure trace at fold boundaries;
- maximum concurrent open-position count;
- maximum aggregate notional;
- correlation-cap activation count;
- daily / weekly loss-limit activation count;
- session-blackout activation count.

These mirror the existing `RiskEngine` gates and must surface in
the candidate's report alongside the strategy metrics. They are
diagnostic-only — they do not gate the strategy's verdict, but
they *must exist* before a candidate can be considered for
paper promotion.

## 10. No-paper / no-demo / no-live rule

Nothing in this discovery sprint, the preferred candidate's
future scaffold sprint, the candidate's future backtest sprint,
or any subsequent walk-forward / financing reconciliation sprint
may:

- add a name to `configs/approved_strategies.yaml`;
- launch `paper-loop`, `demo-loop`, or any future `live-loop`
  (which does not exist and must not be added by this protocol's
  authority);
- enable any broker call other than read-only practice
  endpoints from the already-shipped capture script
  (`scripts/capture_oanda_observed_financing_pilot.py`), which
  *itself* requires a separate, human-authorized credentialed
  run.

Approval is the human-in-the-loop gate per
[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
and is **never** a default outcome of any sprint that follows
this protocol.

## 11. "What counts as evidence" — six-item ladder

Every future candidate must accumulate the six evidence items in
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§8 before any paper / demo enablement:

1. **Pre-commit doc** with hypothesis, gates, window, universe.
2. **Backtest report** with gate verdicts.
3. **Walk-forward result** (per §7).
4. **Financing reconciliation** (per §8 — diagnostic-only against
   the existing synthetic fixtures today; MODELED reconciliation
   is a separate, future credentialed-pilot precondition).
5. **Independent corroboration** — exact custom-engine
   reproduction or free / local verifier WARN-band agreement.
6. **Human approval record** — a reviewed `ApprovalEntry` in
   `configs/approved_strategies.yaml`.

All six are required. Item 6 is the bright-line human gate; the
other five are necessary but not sufficient.

## 12. Disqualifying overfitting patterns

A proposal is rejected outright if it exhibits any of these:

- **Test-window leakage in design.** The proposal already cites
  test-window statistics ("we know USD_CAD ranged in 2024") as a
  reason to expect the strategy to work.
- **Filter-set tuning to a prior campaign's losing trades.** The
  proposal motivates a "skip-X" filter by listing specific
  losing CAMPAIGN_002 (or other) trades.
- **Parameter ranges that span the prior campaigns'
  best-performing values.** The proposal proposes a parameter
  range that *includes* the values that made a rejected family
  least-bad on the same data.
- **Implicit per-pair tuning.** The proposal allows different
  parameters per pair (e.g. "ATR multiple 2.5 on EUR_USD, 1.8 on
  AUD_USD") without an explicit theoretical reason and without
  pre-committing the pair-parameter map.
- **A "pick the best fold" rule.** The proposal selects the
  preferred candidate after seeing more than one fold's results.
- **Rejection-criterion drift.** The proposal carries language
  like "if the train fold fails, we'll adjust the threshold"
  (the harness's gates are pre-committed and immutable per
  campaign).
- **Result-driven family selection.** Phase B3 selects the
  preferred candidate based on hand-wavy plausibility, not on
  the distinctness / falsifiability scoring above.

The shortlist (Phase B3) must include a brief audit per
candidate listing how it avoids each of these patterns.

## 13. Documentation discipline

Every output of this sprint, and every output of any future
sprint built on top of it, must:

- declare `strategy_evidence: false` at the top of the doc
  unless and until the doc is the final approval record that
  flips the flag (a separate, reviewed action under
  `STRATEGY_APPROVAL_PROCESS.md`);
- cite the safety state verbatim in a "Safety state" section
  (`approved_strategies.yaml: approved: []`; CAMPAIGN_002
  REJECT; paper / demo / live blocked; no broker call; no
  MODELED; no engine PnL change);
- cross-link the relevant prior status docs;
- avoid mentioning any credential, OANDA account id, transaction
  id, or other broker-sensitive content (the secret scanner is
  the rail of last resort).

## 14. Validation rails for sprint outputs

Phase B6 of the sprint must show all of the following PASS:

- `python scripts/validate_research_archive.py`
- `python scripts/check_research_freeze.py`
- `python scripts/scan_artifacts_for_secrets.py`
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml` →
  refused
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml` →
  refused
- `python -m forex_bot.cli --help` → no `live-loop`
- `python -m pytest -q` → ≥ 702 passes (only higher if a Phase
  B5 helper adds tests)
- `git status --short` → clean

If any of these would fail, the responsible phase must be
re-opened and fixed before the sprint can be declared complete.

## 15. Cross-links

- Sprint plan:
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md)
- Phase 0 audit:
  [`NEXT_BRANCH_DECISION_AUDIT.md`](NEXT_BRANCH_DECISION_AUDIT.md)
- Next-direction memo:
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
- Walk-forward protocol:
  [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- Walk-forward harness status:
  [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- Financing calculator protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Financing calculator status:
  [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- Financing observed-capture pilot spec:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Strategy approval process:
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- Strategy status registry:
  [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- Research freeze decision:
  [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- Future research backlog:
  [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
