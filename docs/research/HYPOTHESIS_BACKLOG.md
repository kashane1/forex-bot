# Research Hypothesis Backlog

Derived from the CAMPAIGN_002 post-mortem and diagnostics. **This is a
backlog, not a plan.** Listing a hypothesis here does not authorize a
campaign, a parameter change, or any paper/demo/live activity. Each
hypothesis is something a *future* campaign could test, one or two at a
time, under fixed splits and pre-committed gates.

Cross-cutting rules for every hypothesis below:

- No hypothesis may be promoted to paper/demo/live without passing a
  pre-committed out-of-sample gate.
- "Testable without changing live/paper behavior" means: it can be
  evaluated entirely in the backtester with the RiskEngine wired in,
  changing no order-submission code path.
- Every strategy-rule change creates a new explicit strategy version
  string; the frozen `0.1.0-baseline-frozen` is never edited.

Overfitting-risk scale: **low** = a-priori structural change, no data
peeking; **medium** = one new parameter or a universe choice with a
defensible non-returns rationale; **high** = choice motivated by
CAMPAIGN_002 returns, or adds many degrees of freedom.

---

## H-01 — H4 only, exclude H1 entirely

- **Hypothesis:** H1 hourly ATR is too small relative to real spreads
  for a breakout edge to clear costs; restricting to H4 removes the
  worst cost-to-signal regime.
- **Why CAMPAIGN_002 suggests it:** On H1, spread-family rejections are
  ~85% of all rejections and the spread/ATR filter alone vetoes most
  signals; the H1 untouched test is the worst split (PF 0.44, exp_r
  −0.206). H4 is "less bad" everywhere.
- **Code/data changes:** none — drop H1 from the campaign matrix.
- **Validation:** H4-only campaign, fixed splits, compare untouched-test
  expectancy vs CAMPAIGN_002 H4.
- **Pass/fail gate:** untouched-test expectancy ≥ 0 AND PF ≥ 1.05.
- **Overfitting risk:** low — a-priori cost-structure argument.
- **Live/paper-safe:** yes, backtest-only.

## H-02 — Remove / restrict high-spread pairs (NZD_USD, possibly USD_CHF)

- **Hypothesis:** Pairs whose median spread is large relative to ATR
  cannot support a breakout edge; excluding them on a cost-structure
  basis raises portfolio expectancy.
- **Why CAMPAIGN_002 suggests it:** NZD_USD has the widest median
  spread (2.5 pips) and only 38 H4 trades survive the filters in 6
  years — it is barely tradeable. USD_CHF has the campaign's largest
  abnormal-spread count (1,139 on H1), concentrated at rollover.
- **Code/data changes:** none — universe is a config list.
- **Validation:** re-run with NZD_USD removed; report with/without.
- **Pass/fail gate:** removing the pair must improve portfolio
  expectancy without that improvement being explained by a single
  remaining pair.
- **Overfitting risk:** medium — NZD_USD removal is defensible on
  spread/ATR structure (not returns); removing USD_CHF *by returns*
  would be high risk and is not recommended.
- **Live/paper-safe:** yes.

## H-03 — Trade only positive / near-breakeven pairs

- **Hypothesis:** A subset of pairs carries the trend-following edge;
  concentrating on them is better than averaging across all majors.
- **Why CAMPAIGN_002 suggests it:** Per-pair expectancy ranges from
  USD_JPY (−0.000R) and GBP_USD (−0.077R) down to NZD_USD (−0.212R).
- **Code/data changes:** none.
- **Validation:** rolling-window test — does the "good pair" set in the
  train window stay good in validation and test?
- **Pass/fail gate:** the selected set must be chosen on the TRAIN
  split only and remain non-negative on the untouched TEST split.
- **Overfitting risk:** **high** — selecting pairs by their realized
  return is in-sample selection. Only acceptable if the selection is
  frozen on train and the gate is enforced strictly on untouched test.
  Prefer H-02's structural argument over this returns-based one.
- **Live/paper-safe:** yes.

## H-04 — Replace Donchian breakout with pullback-continuation entry

- **Hypothesis:** Entering *on the breakout close* buys exhaustion;
  entering on a shallow pullback *after* a breakout, in the direction
  of the EMA regime, avoids the immediate-reversal population.
- **Why CAMPAIGN_002 suggests it:** 452 trades exit on the initial stop
  with the trailing stop never engaging — average −0.744R, 0% win.
  Those are entries that reverse immediately. A pullback entry waits
  for the reversal-or-continuation question to resolve.
- **Code/data changes:** new entry rule in a new strategy module /
  version (`trend_following_pullback`); needs a pullback-depth
  definition and a continuation trigger.
- **Validation:** backtest vs baseline on identical data/splits.
- **Pass/fail gate:** untouched-test expectancy ≥ 0, PF ≥ 1.05, AND
  fewer immediate-stop exits than the baseline.
- **Overfitting risk:** medium — introduces 1–2 new parameters; keep
  them pre-committed, no grid.
- **Live/paper-safe:** yes — new strategy module, no order-path change.

## H-05 — Add an ADX / trend-strength regime filter

- **Hypothesis:** Breakouts only follow through when a trend already
  exists; gating entries on ADX-14 above a conventional threshold
  removes breakouts taken in chop.
- **Why CAMPAIGN_002 suggests it:** The false-breakout population
  (immediate-stop exits) is the dominant loss source; trailing-stop
  exits are mildly positive. The difference between the two is whether
  a trend was actually present after entry — ADX is the standard
  proxy for "is a trend present now".
- **Code/data changes:** ADX indicator in `strategies/indicators.py`
  (new, with unit tests); one new strategy-config field.
- **Validation:** backtest with ADX filter on/off, identical splits.
- **Pass/fail gate:** untouched-test expectancy ≥ 0 AND PF ≥ 1.05 AND
  the immediate-stop exit share drops materially.
- **Overfitting risk:** medium — one new parameter. Pre-commit the
  threshold to a textbook value (ADX-14 > 25); do **not** sweep it.
- **Live/paper-safe:** yes.

## H-06 — Add a volatility expansion / compression filter

- **Hypothesis:** Breakouts from a *compressed* range expand more
  reliably than breakouts from already-extended volatility; gating on
  ATR percentile (enter only when current ATR is low vs its recent
  distribution) improves follow-through.
- **Why CAMPAIGN_002 suggests it:** Many losers are small whipsaws
  (−0.3R to 0R, 573 trades) — entries into noisy, non-compressed
  conditions. This is also the core idea of the volatility-breakout
  family (H-11).
- **Code/data changes:** ATR-percentile / Donchian-width-percentile
  helper; one new config field.
- **Validation:** backtest filter on/off.
- **Pass/fail gate:** untouched-test expectancy ≥ 0, PF ≥ 1.05.
- **Overfitting risk:** medium — one new parameter; pre-commit it.
- **Live/paper-safe:** yes.

## H-07 — Add a session filter informed by the diagnostics

- **Hypothesis:** Entry quality varies by trading session; restricting
  entries to the sessions with the least-negative diagnostic expectancy
  improves the average.
- **Why CAMPAIGN_002 suggests it:** `TRADE_DIAGNOSTICS.md` reports
  expectancy by UTC entry hour; rejection density also varies by
  session.
- **Code/data changes:** extend `session_filter` with an allow-list of
  entry hours (the block-list mechanism already exists).
- **Validation:** backtest with the session allow-list on/off; the
  allow-list MUST be derived from the TRAIN split only.
- **Pass/fail gate:** non-negative on untouched test; improvement not
  explained by one session in one year.
- **Overfitting risk:** **high** — hour-of-day buckets are a classic
  overfit surface (24 knobs). Only acceptable with train-only
  derivation and a strict untouched-test gate; prefer a coarse
  3-session split over per-hour tuning.
- **Live/paper-safe:** yes.

## H-08 — Add a time-of-week filter (rollover / Friday close)

- **Hypothesis:** Entries near daily rollover and the Friday close
  carry worse fills and weekend gap risk; excluding them improves
  realized expectancy.
- **Why CAMPAIGN_002 suggests it:** Abnormal spreads cluster 20:00–22:00
  UTC (rollover); `SESSION_BLOCKED` already fires there. Extending the
  idea to Friday afternoon is a small, structural change.
- **Code/data changes:** none — `session_filter.block_new_trades`
  already supports day+time windows; this is a config change only.
- **Validation:** backtest with the extended window on/off.
- **Pass/fail gate:** non-negative on untouched test; no degradation
  in trade count so severe the result becomes statistically thin.
- **Overfitting risk:** low — structural (rollover/weekend) rationale.
- **Live/paper-safe:** yes.

## H-09 — Add a financing / swap model before any longer-hold strategy

- **Hypothesis:** Overnight financing materially changes the economics
  of multi-day holds; no longer-hold strategy can be trusted until it
  is modeled.
- **Why CAMPAIGN_002 suggests it:** Median holding period is multi-day;
  financing is currently unmodeled (documented blocker).
- **Code/data changes:** capture 30+ days of practice `DAILY_FINANCING`
  transactions OR build an interest-rate-differential model; wire a
  per-day financing accrual into the backtester PnL.
- **Validation:** regression-test the financing accrual against a
  sample of real practice financing transactions.
- **Pass/fail gate:** modeled financing within tolerance of observed
  practice financing on a holdout sample.
- **Overfitting risk:** low — this is an accounting-correctness change,
  not a strategy change.
- **Live/paper-safe:** yes — backtester + data-capture only.

## H-10 — Test daily-timeframe trend following separately

- **Hypothesis:** A daily (D) timeframe gives ATR large enough to
  dwarf spread and may host a cleaner trend signal than H1/H4.
- **Why CAMPAIGN_002 suggests it:** The cost-to-signal problem worsens
  as the timeframe shortens (H1 worst, H4 less bad); extrapolating, D
  should have the best cost-to-signal ratio.
- **Code/data changes:** fetch D candles; the engine already supports
  granularity `D`.
- **Validation:** standalone D-timeframe campaign, fixed splits.
- **Pass/fail gate:** untouched-test expectancy ≥ 0, PF ≥ 1.05; note
  that D over 2020-2026 yields few trades — statistical power is a
  concern and must be stated.
- **Overfitting risk:** low-medium — same strategy, new timeframe; the
  main risk is too few trades to conclude anything.
- **Live/paper-safe:** yes.

## H-11 — Volatility breakout as a separate strategy family

- **Hypothesis:** A breakout that fires specifically from volatility
  *compression* (range contraction) has better follow-through than a
  pure Donchian extreme-break.
- **Why CAMPAIGN_002 suggests it:** The baseline's losers are
  dominated by breakouts that immediately reverse; compression-gated
  breakouts are the standard remedy. `strategies/volatility_breakout.py`
  already exists as a stub.
- **Code/data changes:** finish/freeze `volatility_breakout` as a
  versioned strategy; it must emit `Signal` objects and run through the
  RiskEngine like any other.
- **Validation:** standalone campaign, fixed splits, no grid.
- **Pass/fail gate:** untouched-test expectancy ≥ 0, PF ≥ 1.05, not
  carried by one pair.
- **Overfitting risk:** medium — a new family with its own parameters;
  pre-commit them, no optimizer.
- **Live/paper-safe:** yes.

## H-12 — Mean reversion as paper/research only, never live (yet)

- **Hypothesis:** In the range-bound regimes that broke the breakout
  strategy, a mean-reversion entry may have positive expectancy.
- **Why CAMPAIGN_002 suggests it:** The breakout fails *because* the
  majors mean-reverted; the symmetric strategy is the obvious research
  counterpart. `strategies/mean_reversion.py` exists and is already
  flagged paper-only.
- **Code/data changes:** none to enable research backtests; mean
  reversion stays `paper_only=True` and is excluded from live configs.
- **Validation:** research backtest only; even a positive result does
  **not** authorize live — mean reversion has fat-tailed loss risk and
  needs far more validation than a backtest.
- **Pass/fail gate:** research interest only; no promotion gate is
  defined because promotion is out of scope.
- **Overfitting risk:** high — mean reversion overfits easily; treat
  any positive backtest with strong suspicion.
- **Live/paper-safe:** research backtest only; must never reach live.

---

## Priority ordering (research judgement)

1. **H-09 (financing model)** — correctness prerequisite; everything
   downstream is untrustworthy without it for multi-day holds.
2. **H-05 (ADX regime filter)** + **H-01 (H4 only)** + **H-02 (drop
   NZD_USD)** — together these form the most controlled "can the
   baseline entry be salvaged by conditions?" test. This is the
   CAMPAIGN_003 candidate (Option A).
3. **H-11 (volatility breakout family)** — the leading *different-entry*
   alternative if conditioning the baseline fails (Option B / a likely
   CAMPAIGN_004).
4. **H-04 (pullback entry)** — second different-entry alternative.
5. **H-06, H-08, H-10** — smaller structural refinements.
6. **H-03, H-07** — high overfitting risk; only with strict train-only
   derivation.
7. **H-12** — research curiosity; never a promotion path.
