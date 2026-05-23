# Next Research Direction — After CAMPAIGN_002 Independent REJECT

**Date:** 2026-05-22 · **Branch:** `research-close-free-local-verifier-and-next-direction-001`
`strategy_evidence: false`

The free / local independent verifier has confirmed the bespoke
engine's directional verdict on CAMPAIGN_002 H4 `trend_following
0.1.0`: every pair is loss-making on the no-RiskEngine path; both
engines agree. The strategy is rejected, the engine is not at
fault, and the research-direction question moves on.

This document proposes the next research direction. **Nothing here
is authorized.** Each candidate path requires an explicit human
decision before any code is written, and every path inherits the
research-freeze safety rules in
[`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md).

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked. No QuantConnect / LEAN. No OANDA
> API calls.

## 1. Current evidence summary

| dimension | status |
|---|---|
| CAMPAIGN_002 H4 trend_following (with RiskEngine, 1,032 trades) | **REJECT** — `backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md` |
| CAMPAIGN_002 H4 trend_following (no-RiskEngine, 1,647 trades) | **REJECT** — bespoke reference: every pair loss-making |
| Bespoke engine | Verified by exact custom-engine reproduction (`backtests/diagnostics/custom_campaign_002_h4_parity.md`) AND independent WARN-band verifier ([`FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md)) — **0 bespoke-engine bugs found** across both reproduction paths |
| All other campaigns (001, 003–009) | REJECT / DIAGNOSTIC, all `strategy_approved: false` |
| Research Marathon 001 | NO-GO close-out |
| QuantConnect / LEAN | RETIRED |
| Free / local verifier | ACCEPTED (closeout) |
| `configs/approved_strategies.yaml` | empty |
| Paper / demo / live loops | refused (no strategy approved) |

**Net: every strategy family the project has tested has failed its
pre-committed gates. The bespoke engine is not the cause. The
infrastructure is in good shape. The strategies themselves were not
profitable on real OANDA H4 data over 2020–2026.**

## 2. Why CAMPAIGN_002 should not be revived immediately

- **Independent corroboration.** Two engines now agree the
  strategy is loss-making on every pair. This is the strongest
  evidence yet that the rejection is real, not an engine artifact.
- **Pre-committed gates failed.** CAMPAIGN_002 was rejected
  against gates that were committed before the run. Revisiting it
  without changing anything would either confirm REJECT again
  (waste of time) or pretend the original gates didn't exist
  (research-freeze violation).
- **Parameter tweaks would be overfitting.** CAMPAIGN_002 already
  represents the "obvious" trend_following configuration
  (EMA 50/200, Donchian 20, ATR 14, 2.0× / 2.0× stop / trail,
  240 bar time stop). Pulling those parameters around to try to
  flip individual pairs to positive is curve-fitting on the same
  in-sample window. The
  [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md) §6 and
  the
  [`RESEARCH_MARATHON_001_NO_GO.md`](RESEARCH_MARATHON_001_NO_GO.md)
  close-out explicitly warned against this.
- **The verifier didn't approve.** The verifier corroborated the
  REJECTION, not approved a winner. There is nothing in the
  comparison docs that suggests CAMPAIGN_002 should be promoted.

## 3. What failed (re-stated for the record)

### 3.1 Directional expectancy

| pair | bespoke no-RiskEngine expectancy R | verifier expectancy R |
|---|---|---|
| EUR_USD | −0.1961 | −0.1801 |
| GBP_USD | −0.0971 | −0.0966 |
| USD_JPY | −0.0001 | −0.0126 |
| AUD_USD | −0.2134 | −0.2167 |
| USD_CAD | −0.1804 | −0.2409 |
| USD_CHF | −0.1430 | −0.1002 |
| NZD_USD | −0.2645 | −0.2723 |

Every pair under both engines has negative expectancy R. The
"least bad" pair (USD_JPY at ~0 R) still loses to spreads / slip.

### 3.2 Pair-level loss-making behavior

Every pair's `return_pct` is negative on both engines (range −1.07
to −15.21 pp on the verifier, −1.37 to −14.70 pp on the bespoke).
There is no single pair the strategy was secretly making money on.

### 3.3 No-RiskEngine path

The 1,647-trade no-RiskEngine path is the **strategy + engine
mechanics in isolation** (no spread / session / loss-limit gates).
That path loses on every pair. The strategy itself, not the risk
filters, is what fails.

### 3.4 RiskEngine-gated path

The 1,032-trade with-RiskEngine path is the committed
CAMPAIGN_002 result. It also loses (verdict: REJECT). The exact
custom-engine reproduction in
`backtests/diagnostics/custom_campaign_002_h4_parity.md` matches
those numbers exactly (zero per-pair deltas, 1,032 trades). So the
RiskEngine isn't masking a winner either.

## 4. What NOT to do next

- **No parameter overfitting on CAMPAIGN_002.** No tweaking ATR
  multiples / EMA lengths / Donchian lookback to flip the verdict.
  The verdict is real.
- **No tiny tweaks to force CAMPAIGN_002 positive.** Adding a
  bespoke "skip-if-spread-tight" gate or a "skip-Friday" filter to
  carve out a few extra winners is curve-fitting unless the filter
  is *pre-committed* on theoretical grounds, *tested on
  out-of-sample data only*, and *accompanied by a clear
  falsification hypothesis*.
- **No paper / demo / live enablement.** Any new strategy
  candidate requires evidence of an edge before paper, never as a
  way to "see what happens".
- **No CAMPAIGN_002 rule changes.** The mapping spec, the
  authoritative parameter JSON, and the bespoke engine are frozen.
- **No verifier Decimal rewrite** without a documented reopening
  per
  [`FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md`](FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md)
  §5.
- **No QuantConnect / LEAN reopening.** Retirement stands.

## 5. Candidate next paths

Each candidate is described with the **research question it might
answer**, the **overfitting risk**, the **prerequisite
infrastructure**, and a **rough work scope**. They are listed in
recommended order of next-research value, not authorization order.

### 5.1 New strategy family (highest-leverage)

- **Question.** Is there *any* strategy family on this universe and
  timeframe that has a positive expectancy after real spreads,
  financing, and the existing RiskEngine gates?
- **Approach.** Pre-commit a new family from a different
  theoretical bucket than trend_following, volatility_breakout,
  pullback_continuation, mean_reversion (the four already tried).
  Plausible buckets: a **carry-aware position-overlay** (only
  trades long in positive-swap pairs and short in negative-swap
  pairs, conditional on a regime filter); a **session-of-day**
  family (e.g. London-open breakout — different from CAMPAIGN_004's
  ATR-compression breakout); a **macro-conditional** family
  (e.g. only trade after a clean macro release window).
- **Overfitting risk.** High — this is "yet another strategy
  family". Mitigated only by pre-committed gates, sealed test
  window, and Marathon-001-style discipline.
- **Prerequisite infrastructure.** Financing model (otherwise
  carry-overlay numbers are unreliable; see §5.4); session-tag
  metadata on candles (probably already present).
- **Work scope.** ~1 pre-commit doc + 1 backtest campaign + 1
  result memo. Estimate 2 sprints.

### 5.2 Walk-forward robustness framework (highest infrastructure value)

- **Question.** Of the strategies we've tested or might test, which
  ones survive a true walk-forward (train / validate / test
  rolling window) rather than a single-window backtest?
- **Approach.** Build a generic walk-forward harness in
  `forex_bot.research/` that takes any strategy + universe + window
  spec and produces a rolling-window train/validation/test
  evaluation. CAMPAIGN_002 would be the first test case (almost
  certainly still REJECT, but with stronger evidence about regime
  dependence). Future strategy candidates would be evaluated
  walk-forward by default.
- **Overfitting risk.** Low (this is infrastructure, not a signal).
- **Prerequisite infrastructure.** None — uses existing engine.
- **Work scope.** ~1 design doc + walk-forward harness + tests +
  one applied walk-forward on CAMPAIGN_002. Estimate 2 sprints.
- **Why this is high-value.** Every new strategy candidate from §5.1
  is more credible (less curve-fit) if it survives walk-forward;
  every old REJECT becomes more conclusive.

### 5.3 Market-regime segmentation

- **Question.** Are CAMPAIGN_002 (or future candidates) loss-making
  *equally* across all regimes, or only in specific regimes (e.g.
  high-volatility, low-spread, ranging, trending)?
- **Approach.** Build a regime-segmentation tool that tags every
  H4 bar with regime labels (ADX bucket, ATR percentile, weekly
  trend direction, session). Re-bucket CAMPAIGN_002's 1,647
  no-RiskEngine trades by regime and measure expectancy per
  regime. If any regime is positive in-sample AND remains positive
  on a sealed test window, that's a regime-filtered candidate for
  §5.1.
- **Overfitting risk.** **High** — regime segmentation is
  classical curve-fitting (slice the data many ways, find a slice
  that's positive). Only valid if the regime taxonomy is
  pre-committed and the test window is sealed.
- **Prerequisite infrastructure.** None.
- **Work scope.** ~1 segmentation library + applied analysis.
  Estimate 1–2 sprints.

### 5.4 Improve financing / swap model

- **Question.** What are CAMPAIGN_002 (and future candidates') net
  results after a *real* financing model rather than the current
  conservative stress overlay?
- **Approach.** This is item §1 of the existing
  [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md). Add a
  financing accrual to the backtest engine keyed on position carry
  and rollover timestamps; reconcile against real OANDA practice
  financing transactions. Until this is done, no backtest figure
  can be claimed as a net result.
- **Overfitting risk.** Low (cost model, not signal).
- **Prerequisite infrastructure.** Historical swap-rate source.
- **Work scope.** Significant — ~3 sprints. But required before
  any candidate can be approved.

### 5.5 Volatility / session filter research

- **Question.** Do any pre-committed volatility or
  session-of-day filters (applied *to existing rejected
  strategies*, not new ones) flip the verdict in a way that
  survives out-of-sample testing?
- **Approach.** Pre-commit a small set of filters (e.g. "skip
  Friday after 17:00 NY", "skip when ATR is in the top decile",
  "skip when daily ADX < 15"), apply them uniformly to CAMPAIGN_002
  AND CAMPAIGN_004 AND CAMPAIGN_007, measure pre-committed-gate
  outcomes on a sealed test window.
- **Overfitting risk.** Medium-high — small risk of cherry-picking
  the filter set. Mitigated by pre-commit.
- **Prerequisite infrastructure.** Session-tag metadata; session
  blackout machinery (already in RiskEngine).
- **Work scope.** ~1 pre-commit + 1 applied campaign + 1 result
  memo. Estimate 1–2 sprints.

### 5.6 Portfolio-level risk diagnostics

- **Question.** Independent of strategy choice, does the project
  have the right *portfolio-level* risk plumbing (correlation
  caps, exposure limits, drawdown brakes, account-level kill
  switches) to safely run a paper-trading candidate if one were
  ever approved?
- **Approach.** Diagnostic-only audit of the RiskEngine's
  portfolio-level rules; produce a coverage report listing every
  gate and its test coverage. Not a strategy investigation —
  infrastructure validation.
- **Overfitting risk.** None (diagnostic-only).
- **Prerequisite infrastructure.** None.
- **Work scope.** ~1 audit doc + targeted tests for any gaps.
  Estimate 1 sprint.

### 5.7 New timeframe regime (deprioritized)

- **Question.** Would moving from H4 to D1 (daily) or H1 expose
  edges the H4 universe doesn't?
- **Approach.** Requires the D1 backtest support item from
  [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md) §2 to
  be done first (D1 currently can't be backtested cleanly). H1 is
  testable today but multiplies the noise floor.
- **Overfitting risk.** Same as §5.1.
- **Prerequisite infrastructure.** D1 fill / spread machinery.
- **Work scope.** Significant.
- **Deprioritized because** prerequisite §2 is itself a
  multi-sprint effort, and the H4 universe already exhausted four
  strategy families — moving timeframes without first exhausting
  the H4 strategy space is shopping for confirmation.

## 6. Recommended next branch

**`research-walk-forward-harness-001`** (corresponds to §5.2).

Rationale:
- **Infrastructure, not a signal** — low overfitting risk.
- **Strictly enabling** — every future strategy candidate becomes
  more credible if it survives walk-forward.
- **Re-validates existing REJECTs** — re-running CAMPAIGN_002
  under walk-forward will confirm or refine the rejection;
  either is informative.
- **Compatible with the research freeze** — the harness ships
  empty by default and can only be invoked by a deliberate human
  decision per campaign.
- **No new external dependency** — the bespoke engine and the
  free / local verifier already do everything required.

A walk-forward harness is the single piece of infrastructure that
most cleanly raises the bar on what counts as "evidence of an
edge". With it in place, §5.1 / §5.3 / §5.5 all become more
trustworthy.

A reasonable runner-up is **`research-financing-model-001`** (§5.4)
— required before any candidate can be promoted to paper. The two
could be pursued in parallel since neither blocks the other.

## 7. Proposed success criteria for any future candidate

Any future strategy candidate, regardless of family or timeframe,
must satisfy **all** of the following before it can be considered
for paper trading:

1. **Pre-committed gates.** Pass/fail criteria fixed *before* the
   backtest runs.
2. **Real OANDA practice data only.** No synthetic candles.
3. **Real financing modelled** (per §5.4). No "ignore financing
   for now" disclaimers.
4. **Walk-forward stability** (per §5.2): the strategy passes its
   gates on each of multiple train / validate / test windows, not
   just one. Positive on a single sealed test window after a
   single-window backtest is **not enough**.
5. **Independent corroboration.** Either the bespoke engine
   reproduces the result exactly (custom-engine reproduction) or
   the free / local verifier corroborates within WARN tolerance.
6. **No tuning during the test.** If a gate fails, the candidate
   is REJECT; no tweaking parameters to flip the verdict.
7. **Diagnostic-artifact attestation** that the candidate is
   `strategy_evidence: true` (a deliberate, reviewed flip from
   the current default).
8. **Human approval** to add the strategy name to
   `configs/approved_strategies.yaml`, with a documented
   `ApprovalEntry` per the `forex_bot.approval` schema.

A candidate that meets 1–7 but not 8 stays in research; 8 is the
ultimate human-in-the-loop gate.

## 8. Required evidence before any future strategy can be considered for paper/demo

Concrete evidence package required:

| evidence | source |
|---|---|
| Pre-commit doc with hypothesis, gates, window, universe | `docs/research/<CAMPAIGN_NAME>_PRECOMMIT.md` |
| Backtest report with gate verdicts | `backtests/<CAMPAIGN_NAME>_REPORT.md` |
| Walk-forward result | `backtests/<CAMPAIGN_NAME>_WALK_FORWARD.md` (new template) |
| Financing reconciliation | `docs/research/<CAMPAIGN_NAME>_FINANCING_RECONCILIATION.md` (new template) |
| Independent corroboration | exact custom-engine reproduction or free/local verifier WARN-band agreement |
| Human approval record | a reviewed `ApprovalEntry` in `configs/approved_strategies.yaml` plus the evidence-index entry pointing at the campaign |

Until all six exist for a single candidate, no paper / demo
enablement is possible.

## 9. Safety state

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.** `paper-loop` and
  `demo-loop` refuse; no `live-loop` command exists.
- **No new external dependency proposed.**
- **No bespoke-engine edit proposed.**
- **No CAMPAIGN_002 rule edit proposed.**
- **No QuantConnect / LEAN reopening proposed.**
- **No OANDA API call proposed for this planning doc.**

Each candidate path in §5 inherits these rails and adds them to
its own pre-commit spec when authorized.

## 10. Cross-links

- Verifier closeout:
  [`FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md)
- Decimal-rewrite deferral:
  [`FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md`](FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md)
- Research freeze:
  [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- Future research backlog:
  [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md)
- Marathon close-out:
  [`RESEARCH_MARATHON_001_NO_GO.md`](RESEARCH_MARATHON_001_NO_GO.md)
- Strategy approval process:
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
