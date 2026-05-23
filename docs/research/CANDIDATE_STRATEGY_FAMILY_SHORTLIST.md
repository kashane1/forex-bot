# Candidate Strategy Family Shortlist

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-001`
`strategy_evidence: false`

The Phase B3 shortlist of five candidate strategy families that
satisfy the
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
constraints, each scored on distinctness against every prior
rejected family, with a single **preferred candidate** picked
for the Phase B4 evaluation design. **No strategy is
implemented, no campaign is run, no approval is granted.**

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked. Every candidate below requires a
> *future, separate, human-authorized* scaffold + backtest sprint
> before any of its claims can be tested. This document carries
> `strategy_evidence: false` and is design-only.

## 1. Scoring rules (recap)

Per
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
§3, a candidate is **meaningfully distinct** from a prior
rejected family only if **at least 3 of the 6** distinctness
dimensions differ:

| # | dimension |
|---:|---|
| 1 | theoretical bucket |
| 2 | primary entry signal |
| 3 | primary exit signal |
| 4 | timeframe / universe |
| 5 | data inputs |
| 6 | failure-mode hypothesis |

The four prior rejected families against which every candidate
is scored:

- **TF** — `trend_following 0.1.0` (CAMPAIGN_002).
- **VB** — `volatility_breakout 0.1.0-c004` (CAMPAIGN_004).
- **PB** — `pullback_continuation` (CAMPAIGN_007).
- **MR** — `mean_reversion` 0.1.0-c008 / 0.2.0-c009.

A candidate is on the shortlist only if it scores ≥ 3
distinctness points against **every** prior family. The shortlist
also applies the protocol's §12 overfitting-pattern audit per
candidate.

## 2. Candidate roster (5 families)

| # | candidate name | category (§4) | preferred? |
|---:|---|---|:--:|
| C1 | **Asian-range / London-open session breakout** | Session-of-day breakout (non-CAMPAIGN_004 flavour) | **★ PREFERRED** |
| C2 | Carry-aware long-only overlay | Carry-aware position overlay | runner-up (blocked on MODELED) |
| C3 | Daily-ATR-percentile regime switcher | Volatility-regime compression / expansion | candidate |
| C4 | Volatility-expansion non-directional straddle | Volatility-regime compression / expansion | candidate |
| C5 | H4 random-entry diagnostic anchor | Baseline / null model | anchor (NOT a paper candidate) |

Each candidate is detailed in §3–§7 below. The preferred
candidate is C1, with rationale in §8.

---

## 3. Candidate C1 — Asian-range / London-open session breakout

### 3.1 Hypothesis

The H4 bar that covers the **first London hours** (roughly
07:00–11:00 UTC) is preceded by a low-liquidity Asian-session
H4 bar. **If the Asian H4 bar establishes a narrow range AND
the London H4 bar's close penetrates that range in one
direction, the directional move tends to *continue* through
the London/NY-overlap H4 bar.** The edge — if any — would come
from the **liquidity-flow event** of the London open, not from
trend, not from compression, not from pullback, and not from
mean-reversion of an extreme.

This is **not** the CAMPAIGN_004 family (which used ATR
compression over a 60-bar window, ignored session, and used a
20-bar Donchian as the breakout channel). The "compression"
here is *one* Asian H4 bar's range; the "breakout" is *one*
London H4 bar's close relative to that prior bar's high/low.

### 3.2 Distinctness scoring

| dim | vs TF | vs VB | vs PB | vs MR |
|---:|:--:|:--:|:--:|:--:|
| 1 theoretical bucket | ✓ (liquidity event vs trend) | ✓ (single-bar session range vs 60-bar ATR compression) | ✓ (single-bar vs multi-bar pullback) | ✓ (continuation vs reversion) |
| 2 entry signal | ✓ (no Donchian-20, no EMA crossover) | ✓ (no ATR percentile, no 20-bar Donchian) | ✓ (no pullback to EMA) | ✓ (continuation, not reversion) |
| 3 exit signal | ≈ (ATR-multiple stop; differs in time stop = one bar) | ≈ (ATR-multiple stop; differs in time stop) | ≈ | ≈ |
| 4 timeframe / universe | ✓ (H4 + explicit session-of-day filter — a new dimension) | ✓ | ✓ | ✓ |
| 5 data inputs | ✓ (bar hour-of-day, derived from timestamp) | ✓ | ✓ | ✓ |
| 6 failure-mode hypothesis | ✓ ("CAMPAIGN_002 lost because Donchian-20 buys exhaustion; the London-open continuation buys the *first* extension, not an aged one") | ✓ ("CAMPAIGN_004 lost because ATR-compressed breakouts on H4 majors fade; session-defined breakouts may not, because the liquidity-flow timing is different") | ✓ ("CAMPAIGN_007 lost because the pullback-then-continuation gate is rarely tripped on H4 majors; the session-defined gate fires daily") | ✓ ("MR-c008/c009 lost because the train fold failed; this is a different family entirely") |

Score: **5–6 of 6 against every prior family**. Comfortably
clears the ≥ 3 threshold.

### 3.3 Required features

- Per-H4-bar timestamp — already present
  (`CandleFrame.df.index` is UTC).
- A trivial helper that derives session-of-day from the H4 bar
  timestamp. Session bins (UTC):
  - `asia`: 22:00 ≤ hour < 06:00
  - `london`: 06:00 ≤ hour < 12:00
  - `ny_overlap`: 12:00 ≤ hour < 16:00
  - `ny_late`: 16:00 ≤ hour < 22:00
  This helper would live in
  [`indicators.py`](../../src/forex_bot/strategies/indicators.py)
  (a single function) or as a strategy-local utility (the
  future scaffold sprint decides).
- A "prior-bar Asian range" computation: `high[t-1] - low[t-1]`
  when bar `t-1` is in the `asia` session. **No** rolling
  window beyond bar `t-1`.

### 3.4 Data requirements

- H4 OANDA practice data for the seven CAMPAIGN_002 pairs —
  **already present**. No new fetch needed.
- Synthetic financing rate fixtures (one per pair) — already
  present under
  [`research/financing/fixtures/`](../../research/financing/fixtures/).

### 3.5 Known failure modes

- **Session-of-day overfit.** The "London open" is a
  well-studied event; many published strategies have decayed.
  Mitigation: pre-commit gates that are deliberately strict
  (no robustness grid; no per-pair tuning).
- **Pair-specific behaviour.** USD_JPY's session structure
  differs from EUR_USD's. Mitigation: report per-pair pass /
  fail; the aggregate gate requires multiple pairs positive,
  not a single-pair save.
- **Holiday / DST artefacts.** UTC-based session bins ignore
  London/NY DST shifts. Mitigation: document the convention;
  treat any positive results on the DST-transition weeks with
  skepticism.
- **Holding through rollover.** A long position opened at the
  London H4 bar that survives until the next day will incur
  one financing rollover. The financing overlay will surface
  this; the pre-commit gates require positive PnL *net* of
  conservative stress.

### 3.6 Overfitting risks (per protocol §12 audit)

| pattern | mitigation |
|---|---|
| test-window leakage in design | candidate is specified by H4 bar timestamp and prior-bar high/low; **zero** references to specific 2020–2026 statistics in the design. |
| filter-set tuning to CAMPAIGN_002 losers | no "skip-X" filter; one entry rule, one exit rule. |
| parameter ranges spanning prior best-fit values | no parameter shared with any prior family (no Donchian-20, no EMA-50/200 crossover, no ATR-percentile). |
| implicit per-pair tuning | a single parameter set for all seven pairs; **no** per-pair overrides. |
| pick-the-best-fold | walk-forward harness enforces forward-only; preferred candidate is fixed *here* before any fold runs. |
| rejection-criterion drift | pre-commit gates fixed in the future scaffold sprint's `<CAMPAIGN>_PRECOMMIT.md` before any run. |
| result-driven family selection | C1 is selected *here* on theoretical / distinctness grounds, not on backtest results. |

### 3.7 Frozen parameter sketch (illustrative — finalized in Phase B4)

| parameter | proposed value | rationale |
|---|---|---|
| `asian_session_hours_utc` | `(22, 6)` | covers the late-NY-late + Asian sessions on UTC. |
| `london_session_hours_utc` | `(6, 12)` | first London hours on UTC. |
| `atr_lookback` | `14` | standard Wilder ATR, as in all prior families — for stop distance only. |
| `atr_stop_multiple` | `2.0` | same as CAMPAIGN_004 / CAMPAIGN_007 — stop is not a hidden variable. |
| `time_stop_bars` | `6` (≈ 1 trading day on H4) | the edge, if any, is intraday-window; a multi-day hold has no thesis. |
| `trailing_stop_atr_multiple` | `None` | no trail in v1 — keep the candidate's exit logic minimal and falsifiable. |
| `min_asian_range_atr_fraction` | `0.30` | the Asian-bar range must be ≥ 30 % of ATR-14 (avoid degenerate ranges). |
| `risk_per_trade_pct` | `0.25` | matches every prior campaign — risk is fixed, not the variable under test. |

### 3.8 Walk-forward plan sketch (finalized in Phase B4)

- `SplitStyle`: `rolling`.
- `train_days`: 540 (~18 months).
- `validation_days`: 180 (~6 months).
- `test_days`: 180 (~6 months).
- `step_days`: 180.
- Minimum fold count: 6 (per the harness; the existing universe
  comfortably supports this).
- `parameter_mode`: `frozen` (only authorized mode).

### 3.9 Financing sensitivity

Short holding period (≤ 6 H4 bars, i.e. ≤ 1 day) means most
trades incur **zero** rollover. Trades that span the daily
17:00-NY rollover will incur exactly one financing event;
Wednesday triple-swap applies if the trade is held into the
Wednesday→Thursday rollover. The candidate's report runs
`calculate_run(...)` with the conservative stress source and
the per-pair `TableRateSource` and shows:

- `cashflow_home_total` (estimated, per-pair)
- `cashflow_home_stress_total` (conservative)
- `missing_rate_event_count`
- `financing_treatment: estimated`
- `financing_in_engine_pnl: false`
- `financing_is_live_blocker: true`

The headline PnL gate must pass *net* of the stress overlay.

### 3.10 Risk-engine implications

No new risk-engine gate required. The existing gates
(stop-loss required; spread cap; session blackout — the
candidate is **session-aware** but does not bypass the
session-blackout config; sizing 0.25 %; daily loss limit;
exposure cap; max-positions-per-instrument 1) all apply
unchanged. The candidate's report must include the standard
risk-engine diagnostic checklist per
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
§9.

### 3.11 Rejection criteria (illustrative — finalized in Phase B4)

| criterion | threshold |
|---|---|
| per-fold expectancy_R | ≥ 0.05 R *net of stress financing* on every test fold |
| aggregate expectancy_R | ≥ 0.05 R *net of stress financing* across all test folds |
| fold pass rate | 100 % (strict pass) |
| profit factor (aggregate) | ≥ 1.10 |
| pairs positive (aggregate) | ≥ 4 of 7 |
| dominance | no single fold contributes > 60 % of aggregate PnL |
| min trade count (aggregate) | ≥ 200 |
| financing overlay | conservative-stress run does not flip the verdict |
| no-lookahead | every entry computed from bars strictly < t; pre-commit-time grep audit. |

Failing **any** of these → REJECT. No parameter tweaking,
no gate relaxation.

---

## 4. Candidate C2 — Carry-aware long-only overlay (runner-up; blocked on MODELED)

### 4.1 Hypothesis

A position-overlay family that **only trades long in pairs whose
financing rate makes the long side a credit, and is otherwise
flat.** The entry filter is a slow trend confirmation (price >
50-day EMA on daily). The edge — if any — is the *carry* itself
plus a small directional drift, not a fast price signal.

### 4.2 Distinctness scoring

| dim | vs TF | vs VB | vs PB | vs MR |
|---:|:--:|:--:|:--:|:--:|
| 1 | ✓ | ✓ | ✓ | ✓ |
| 2 | ✓ (financing-rate gate; no Donchian) | ✓ | ✓ | ✓ |
| 3 | ✓ (held-until-carry-flips exit; no ATR trail) | ✓ | ✓ | ✓ |
| 4 | ✓ (long-only; subset universe) | ✓ | ✓ | ✓ |
| 5 | ✓ (financing rates; daily EMA) | ✓ | ✓ | ✓ |
| 6 | ✓ ("CAMPAIGN_002 ignored carry entirely; carry-positive long is a different exposure"). | ✓ | ✓ | ✓ |

Score: **6 of 6 against every prior family**. Strongest
distinctness in the shortlist.

### 4.3 Why this is the runner-up, not the preferred

- **Headline PnL is structurally a financing-PnL question.**
  Without **MODELED** financing for the candidate's pairs / window,
  the headline number is synthetic. The protocol allows a
  diagnostic run with synthetic fixtures, but the *evidence-grade*
  result requires real captured `DAILY_FINANCING` events from
  OANDA — a separately-authorized credentialed-pilot sprint per
  [`FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`](FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md)
  §10. None exist today.
- **MODELED is refused at four layers** in
  `research/financing/`. Any candidate whose evidence rests on
  MODELED financing is structurally on hold until human
  approval flips the MODELED slot.
- **Higher overfitting risk on a short sample.** Carry is a
  slow signal; six years of H4 history yields only a handful of
  effectively-independent regime windows.
- C2's PnL gates can still be *designed* (Phase B4-equivalent
  for the future sprint), but until MODELED is available the
  candidate cannot be promoted past the diagnostic-only stage.

C2 is therefore parked as the **next** discovery target *after*
either (a) a credentialed practice / live capture sprint
produces ≥ 60 reconciled `DAILY_FINANCING` events and a
MODELED `FinancingModel` becomes available, or (b) human
approval re-scopes MODELED to allow a stress-only carry
experiment.

### 4.4 Frozen parameter sketch

| parameter | proposed value |
|---|---|
| `daily_ema_lookback` | 50 |
| `min_long_carry_bp_per_year` | 25 |
| `rebalance_frequency` | weekly (Monday open) |
| `max_concurrent_positions` | 3 |
| `atr_stop_multiple` (daily ATR) | 4.0 |
| `risk_per_trade_pct` | 0.25 |
| universe | 7-pair, subset by carry filter |
| timeframe | H4 (entry) / D1 (regime) |

### 4.5 Required infrastructure (future-sprint deps)

- A real or MODELED financing-rate source for the candidate's
  window (today: refused; see §4.3).
- A daily EMA from H4 candles (D1 aggregation already exists
  per [`d1_aggregation.py`](../../src/forex_bot/backtesting/d1_aggregation.py)).
- `StrategyConfig.<carry_overlay_name>` slot in
  [`config.py`](../../src/forex_bot/config.py).

---

## 5. Candidate C3 — Daily-ATR-percentile regime switcher

### 5.1 Hypothesis

H4 trend persistence is **conditional on the prior-day's
volatility regime**. If yesterday's daily ATR is in the **top
quartile** of the trailing 60-day distribution, today's H4
bars exhibit higher trend persistence; entries on H4 closes
through prior-H4 high/low have positive expectancy. If
yesterday's daily ATR is in the **bottom quartile**, today's
H4 bars exhibit reversion; no entries today.

### 5.2 Distinctness scoring

| dim | vs TF | vs VB | vs PB | vs MR |
|---:|:--:|:--:|:--:|:--:|
| 1 | ✓ (regime-switching) | ✓ (daily ATR percentile vs H4 ATR percentile) | ✓ | ✓ |
| 2 | ✓ (prior-H4 high/low close, no Donchian-20) | ✓ (daily percentile is the gate, not breakout direction) | ✓ | ✓ |
| 3 | ≈ (ATR-stop) | ≈ | ≈ | ≈ |
| 4 | ✓ (daily input, H4 execution) | ✓ | ✓ | ✓ |
| 5 | ✓ (daily ATR percentile, derived from H4 → D1 aggregation) | ✓ | ✓ | ✓ |
| 6 | ✓ ("CAMPAIGN_002 lost because Donchian-20 was unconditional; only trade when yesterday's vol was already elevated") | ✓ (different percentile window / direction) | ✓ | ✓ |

Score: **5 of 6 against every prior family**. Clears the
threshold.

### 5.3 Why not preferred (notes)

- **Adjacent to CAMPAIGN_002 in spirit** — the "trend" hypothesis
  is similar, only gated differently. Higher implicit overfitting
  risk than C1, which is a different *family*, not a different
  *gate*.
- **Daily ATR percentile requires D1 aggregation**, which is
  partially in place
  ([`d1_aggregation.py`](../../src/forex_bot/backtesting/d1_aggregation.py))
  but not yet a closed CAMPAIGN_006 path. The candidate would
  inherit that risk.

### 5.4 Frozen parameter sketch

| parameter | proposed value |
|---|---|
| `daily_atr_percentile_lookback` | 60 |
| `top_quartile_cutoff` | 0.75 |
| `bottom_quartile_cutoff` | 0.25 |
| `entry_gate` | prior-H4 high/low close on regime-on day |
| `atr_stop_multiple` | 2.0 |

### 5.5 Required infrastructure (future-sprint deps)

- D1 aggregation closure for the percentile computation.
- `StrategyConfig.<regime_switcher_name>` slot.

---

## 6. Candidate C4 — Volatility-expansion non-directional straddle

### 6.1 Hypothesis

When the H4 ATR jumps from a low-vol regime to a high-vol
regime (bar `t-1` ATR-14 in the bottom decile of the prior
60-bar distribution; bar `t` ATR-14 above the median), **a
move *of some direction* tends to follow**. Enter *both* long
and short on the next H4 bar with conservatively-sized
positions; close the losing side on the second bar; let the
winning side run to its ATR-stop / time-stop.

### 6.2 Distinctness scoring

| dim | vs TF | vs VB | vs PB | vs MR |
|---:|:--:|:--:|:--:|:--:|
| 1 | ✓ (non-directional regime-change) | ✓ (non-directional; c004 is directional) | ✓ | ✓ |
| 2 | ✓ (volatility-jump entry, no Donchian, no EMA) | ✓ (jump, not compression) | ✓ | ✓ |
| 3 | ✓ (paired straddle close + ATR stop) | ≈ | ≈ | ≈ |
| 4 | ✓ | ✓ | ✓ | ✓ |
| 5 | ≈ (H4 ATR, no new inputs) | ≈ | ≈ | ≈ |
| 6 | ✓ ("CAMPAIGN_002 lost because direction is hard; what if we don't predict direction at all?") | ✓ | ✓ | ✓ |

Score: **5 of 6 against every prior family**. Clears the
threshold.

### 6.3 Why not preferred (notes)

- **Requires the bespoke engine to support paired-entry
  semantics** — the engine's "single-position-at-a-time per
  instrument" rule blocks a literal straddle as currently
  configured. The candidate would need either (a) per-pair
  per-direction position separation (a non-trivial engine
  change) or (b) modelling each side as a separate
  "instrument" with shared underlying (an unbroken hack).
- **Risk-engine `max_positions_per_instrument = 1`** also
  blocks a literal straddle — a candidate-specific risk-engine
  gate would be required.
- The infrastructure dependencies push C4 to a later sprint.

---

## 7. Candidate C5 — H4 random-entry diagnostic anchor (anchor, not paper candidate)

### 7.1 Hypothesis

If a candidate from C1–C4 cannot beat **random entry under the
same RiskEngine gates and the same exit rules**, the candidate
has no edge. C5 is *not* a paper-trade candidate; it is the
**falsifiability anchor** the preferred candidate is measured
against.

### 7.2 Distinctness scoring

C5 is the **null model**. It is included to allow the
preferred candidate's report to display a side-by-side
comparison. CAMPAIGN_005 already established that the random
baseline on H4 majors is ~−0.095 R per trade; the candidate's
expectancy must clear that anchor by a meaningful margin to
count as evidence of an edge.

C5 does not have an approval path; its only output is a
comparison row in the preferred candidate's campaign report.

---

## 8. Preferred candidate: C1 (Asian-range / London-open session breakout)

The Phase B4 evaluation design will be built for **C1**. The
rationale, summarised:

| reason | detail |
|---|---|
| **Maximum distinctness** | Score 5–6 of 6 against every prior rejected family. |
| **Falsifiable theoretically** | The London-open liquidity-flow hypothesis is concrete; the rejection criterion is a strict per-fold pass rate, not "did it almost work". |
| **No infrastructure deps beyond what exists** | H4 OANDA data; UTC timestamps; existing indicators; existing RiskEngine; existing walk-forward harness; existing financing calculator. |
| **No code edits assumed by Phase B4** | The future scaffold sprint will add `StrategyConfig.<new_name>` and a strategy module — these are *that* sprint's tasks, not Phase B4's. |
| **Compatible with the existing risk engine** | No new risk-engine gate required; the `max_positions_per_instrument = 1` rule is satisfied; existing session-blackout config is *additionally* respected. |
| **Compatible with the existing engine** | Single-instrument, single-position, bar-by-bar — exactly what `BacktestEngine` does today. |
| **Compatible with the existing financing overlay** | Short holding period means most trades incur zero rollover; the few that don't are well-defined per the calculator. |
| **No MODELED dependency** | Unlike C2, C1 does not need real captured `DAILY_FINANCING` data to make its headline claim. Conservative stress is a valid posture. |
| **No D1 dependency** | Unlike C3, C1 does not need the CAMPAIGN_006 blocker lifted. |
| **No engine paired-entry change** | Unlike C4, C1 does not need the bespoke engine to support multiple simultaneous positions on the same instrument. |

C2 is the **strongest theoretical candidate** but is blocked on
MODELED financing; it is the natural next discovery target once
the capture sprint produces real reconcilable data.

C3 / C4 stay on the shortlist as future alternatives if C1's
future scaffold sprint screens fail; they are not abandoned.

C5 is the **anchor**, not a candidate.

## 9. Future implementation branch name (for Phase B4 / future sprint)

The preferred candidate (C1) will be implemented and evaluated
under a separate future, human-authorized sprint named:

**`research-asian-london-session-breakout-001`**

That sprint's first phase will:

1. Edit
   [`src/forex_bot/config.py`](../../src/forex_bot/config.py)
   to add a `SessionBreakoutStrategyConfig` and a
   `StrategyConfig.session_breakout` slot.
2. Add
   `src/forex_bot/strategies/session_breakout.py` implementing
   the `Strategy` protocol with the C1 entry / stop / exit
   rules.
3. Commit a
   `docs/research/CAMPAIGN_010_SESSION_BREAKOUT_PRECOMMIT.md`
   with the **finalised** parameters and pass / fail gates
   from Phase B4 of *this* discovery sprint.

None of those steps happens in this discovery sprint.

## 10. Overfitting-pattern audit summary

| candidate | test-window leakage | filter-set tuning | parameter range overlap | implicit per-pair tuning | pick-best-fold | rejection-criterion drift | result-driven family selection |
|---|---|---|---|---|---|---|---|
| C1 | clean | clean | clean | clean | clean | clean | clean (selected here on distinctness) |
| C2 | clean | clean | clean | clean | clean | clean | clean |
| C3 | clean | clean | minor (D1 aggregation shared with CAMPAIGN_006 infra) | clean | clean | clean | clean |
| C4 | clean | clean | clean | clean | clean | clean | clean |
| C5 | n/a (null model) | n/a | n/a | n/a | n/a | n/a | n/a |

No shortlisted candidate trips any §12 disqualifier.

## 11. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.**
- No code edited this phase.
- No new strategy module added.
- No campaign run.
- No broker / OANDA call.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.

## 12. Cross-links

- Sprint plan:
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md)
- Protocol:
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- Inventory:
  [`STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md)
- Next-direction memo:
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
- Walk-forward protocol:
  [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- Walk-forward status:
  [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- Financing protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Financing status:
  [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- Observed-capture pilot status:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`](FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md)
- Strategy status registry:
  [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- Future research backlog:
  [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md)
- CAMPAIGN_005 (random benchmark):
  [`backtests/CAMPAIGN_005_REPORT.md`](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
