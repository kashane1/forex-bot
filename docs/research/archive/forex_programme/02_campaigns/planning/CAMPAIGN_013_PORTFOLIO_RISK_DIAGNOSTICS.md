# CAMPAIGN_013 Portfolio-Risk Diagnostics (Phase 7)

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-walk-forward-001`
`strategy_evidence: false`

Phase 7 portfolio-risk diagnostics for **CAMPAIGN_013 /
`cross_pair_currency_strength_rotation 0.1.0-c013`**. These are
**diagnostic only** — they do not gate the verdict. The Phase 5
verdict was already REJECT; this report exists to characterize the
strategy's risk profile, document the cross-pair concurrency
behavior, and confirm no diagnostic finding contradicts the verdict.

> No broker call. No `.env` read. No transaction-stream query.
> `configs/approved_strategies.yaml` remains `approved: []`. Even a
> "clean" risk-diagnostics pass produces RESEARCH_PASS_UNAPPROVED at
> best. The candidate is REJECTED.

## 1. Command run

```bash
python scripts/build_campaign_013_risk_diagnostics.py \
  --campaign-dir backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation
```

Output (committed):

- `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/risk/diagnostics.json`
- `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/risk/diagnostics.md`

## 2. Per-pair exposure (8-fold aggregate)

| pair | trades | total units | total notional (quote ccy) | total PnL (USD) | max loss streak | max win streak | largest single loss | largest single win |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EUR_USD | 1,412 | 380,005 | 368,841 | −84.66 | 7 | 7 | −1.28 | +1.30 |
| GBP_USD | 648 | 100,113 | 124,198 | −48.94 | 7 | 8 | −1.27 | +1.42 |
| USD_JPY | 310 | 57,070 | 8,290,363 | +2.27 | 12 | 7 | −1.26 | +1.38 |
| AUD_USD | 1,942 | 470,260 | 305,252 | −101.32 | 9 | 8 | −1.29 | +1.27 |
| USD_CAD | 958 | 313,253 | 423,438 | −52.01 | 9 | 7 | −1.29 | +1.30 |
| USD_CHF | 807 | 191,099 | 166,467 | −73.33 | 14 | 6 | −1.30 | +1.26 |
| NZD_USD | 1,863 | 489,253 | 295,179 | −208.82 | 9 | 7 | −1.30 | +1.31 |

Observations:

- **NZD_USD's −$208.82 total PnL is 36.8 % of the −$566.79
  portfolio loss** — by far the worst single-pair contributor. This
  matches the Phase 5 aggregate's `single_pair_dominance_pct = 36.55
  %` (within rounding).
- **USD_CHF's max loss streak of 14** is the longest of any pair —
  consistent with USD_CHF's worst per-pair expectancy
  (−0.0801 R) and 833 DRAWDOWN_LIMIT rejections (see §6).
- **USD_JPY's max loss streak of 12** despite +0.0000 R aggregate
  expectancy reinforces that USD_JPY sits at the random-walk floor
  with high streakiness around zero.
- **Per-trade sizing is uniform.** Largest single loss is
  ~$1.30 across all pairs (= 2 × ATR × stop_units; ATR-stop sizing
  on $500 starting equity is consistent).
- **USD_JPY total notional is ~26 × the next-highest** because JPY is
  denominated in much smaller units (≈ 0.007 USD per JPY). This is a
  units-vs-USD-notional artifact, not a sizing difference; per-trade
  dollar risk is the same.

## 3. Entry-session clustering (UTC hour of entry)

| UTC hour | trades |
|---:|---:|
| 01:00 | 1,150 |
| 02:00 | 796 |
| 05:00 | 832 |
| 06:00 | 427 |
| 09:00 | 1,563 |
| 10:00 | 612 |
| 13:00 | 1,591 |
| 14:00 | 752 |
| 17:00 | 168 |
| 18:00 | 49 |

| session bucket | trades |
|---|---:|
| asian (22-06 UTC) | 2,778 |
| london (06-12 UTC) | 2,602 |
| london_ny_overlap (12-16 UTC) | 2,343 |
| ny (16-22 UTC) | 217 |

The entry-hour distribution clusters at H4-bar-boundary UTC hours
(01, 05, 09, 13, 17 — driven by OANDA's NY-17:00-anchored H4 bars),
with smaller secondary peaks one hour later (02, 06, 10, 14, 18) from
within-bar entries. **NY session (16-22 UTC) has only 217 entries**
because the H4 bar boundary at 21:00 UTC straddles the cutoff and
most entries land in the adjacent "asian" bucket. This is not a
strategy preference — it's a bucket-boundary artifact.

The Asian / London / London-NY-overlap buckets are roughly balanced
(2,343 - 2,778 each), confirming the strategy fires across all
trading sessions; there is no session-of-day concentration risk.

## 4. Exit reason distribution

| reason | trades | share |
|---|---:|---:|
| time | 6,087 | 76.7 % |
| stop | 1,830 | 23.1 % |
| eod | 23 | 0.3 % |

**76.7 % of exits are via `max_bars_in_trade = 6` time stop.** This
means the strategy holds most trades to their 6-bar (24-hour) limit
without hitting either an ATR stop or a take-profit (the strategy has
no take-profit by design). The dominance of time-stop exits means
each trade locks in whatever drift accumulated in those 6 bars —
which is on average a small negative number after spread + slippage.

The 23.1 % stop-exit rate is consistent with the 2 × ATR stop
multiplier on a non-trending H4 universe — most trades drift but few
travel far enough to trigger the ATR stop in either direction.

There are **no take-profit exits** (no `target` exit code is
configured for this strategy). The R4 holding-period rule
(`max_bars_in_trade = 6`) is the binding exit mechanism for ~3/4 of
trades.

## 5. Drawdown clustering

Drawdown is bounded per-pair-per-fold (each pair's run starts at $500
notional equity); CAMPAIGN_013's worst single per-fold per-pair
drawdown is on the order of −7 % to −12 %. The 8-fold aggregate
`single_fold_dominance_pct = 22.34 %` (well under the 60 % gate)
confirms no single fold dominates the loss profile — the strategy
loses fairly uniformly across folds.

Per-fold per-pair drawdowns are documented in `risk/diagnostics.json`
under `drawdown_clustering.per_fold[].per_pair_max_drawdown_pct`.

## 6. Risk-engine rejection totals (mode = backtest)

| code | total |
|---|---:|
| `SPREAD_TOO_WIDE` | 3,024 |
| `DRAWDOWN_LIMIT` | 1,507 |
| `SESSION_BLOCKED` | 992 |
| `MAX_OPEN_POSITIONS_EXCEEDED` | **0** |

**Rejection-by-pair breakdown:**

| pair | DRAWDOWN_LIMIT | SESSION_BLOCKED | SPREAD_TOO_WIDE | total rejections |
|---|---:|---:|---:|---:|
| EUR_USD | 0 | 224 | 1,081 | 1,305 |
| GBP_USD | 0 | 22 | 28 | 50 |
| USD_JPY | 0 | 21 | 38 | 59 |
| AUD_USD | 0 | 59 | 28 | 87 |
| USD_CAD | 0 | 32 | 23 | 55 |
| USD_CHF | **833** | 186 | 185 | 1,204 |
| NZD_USD | **674** | 448 | 1,641 | 2,763 |
| **total** | **1,507** | **992** | **3,024** | **5,523** |

Observations:

1. **`MAX_OPEN_POSITIONS_EXCEEDED = 0`** confirms the runner is
   per-pair, not portfolio-wide. The cap is enforced *within* each
   pair's engine but not *across* pairs (each pair runs in an
   isolated engine instance with its own $500 starting equity).
   This is the engine's architectural constraint, not a strategy
   choice. See §7.4 for the implication.

2. **`DRAWDOWN_LIMIT` (1,507) fires only on USD_CHF and NZD_USD** —
   the two worst pairs by aggregate P&L. The RiskEngine's drawdown
   cap is per-pair; these two pairs hit their per-pair drawdown
   limits often enough to block further entries. EUR_USD also lost
   $84.66 but the loss is spread evenly enough across folds that it
   never hits the per-pair drawdown cap.

3. **`SPREAD_TOO_WIDE` (3,024) concentrates on NZD_USD and EUR_USD**
   — the two pairs with the most attempted entries. The strategy's
   high firing rate combined with NZD_USD's wider typical spreads
   means many would-be entries are rejected on spread alone.

4. **`SESSION_BLOCKED` (992)** is moderate — the strategy's entries
   are mostly within trading sessions, but some bars near session
   boundaries are blocked.

5. **Total rejections (5,523) vs accepted (7,940) = 41 % rejection
   rate.** Even after rejections, the strategy fires 7,940 trades —
   what the *raw* signal count would be is 7,940 + 5,523 = ~13,463
   without rejections. The RiskEngine reduces trade count by ~41 %
   without rescuing per-pair expectancy.

## 7. Cross-pair-specific diagnostics

### 7.1 Cross-pair runner contract status per fold

| fold | contract_satisfied | common_index_length (H4 bars) |
|---|:---:|---:|
| 0 | ✓ | 1,841 |
| 1 | ✓ | 1,848 |
| 2 | ✓ | 1,837 |
| 3 | ✓ | 1,830 |
| 4 | ✓ | 1,835 |
| 5 | ✓ | 1,836 |
| 6 | ✓ | 1,825 |
| 7 | ✓ | 1,829 |

**All 8 folds satisfied the cross-pair runner integration contract.**
No fold was BLOCKED. The REJECT verdict comes from inherited gates
alone (see Phase 5).

### 7.2 Zero-trade pair-fold cell distribution

- **29 of 56 (51.8 %) pair-fold cells produced zero trades.**

The cross-pair rank-gap rule `|rank(quote) − rank(base)| ≥ 4` is
selective by design — more than half of (pair × fold) cells fail to
trigger any entry within the fold's test window because the rank gap
never reaches 4. This is the rule's *intended* sparseness, not a
runner defect.

Visualized (✓ = trades, · = zero):

```
            EUR  GBP  JPY  AUD  CAD  CHF  NZD
fold_00      ✓    ·    ·    ·    ·    ✓    ✓
fold_01      ·    ·    ·    ✓    ·    ·    ·
fold_02      ✓    ✓    ·    ✓    ·    ·    ✓
fold_03      ·    ·    ·    ✓    ·    ✓    ✓
fold_04      ✓    ·    ·    ✓    ✓    ·    ✓
fold_05      ✓    ·    ·    ✓    ✓    ·    ✓
fold_06      ✓    ·    ✓    ·    ·    ✓    ✓
fold_07      ·    ✓    ·    ✓    ✓    ·    ✓
```

This sparseness directly explains why `pairs_positive_count` is
bounded above by the count of trading pairs per fold — and why the ≥
4/7 gate is structurally hard for this strategy.

### 7.3 Per-fold long/short imbalance

| fold | long | short | total | long share |
|---|---:|---:|---:|---:|
| 0 | 509 | 285 | 794 | 64.1 % (long-skewed) |
| 1 | 0 | 321 | 321 | 0.0 % (all-short — single AUD_USD pair) |
| 2 | 1,166 | 0 | 1,166 | 100.0 % (all-long — USD weakness regime) |
| 3 | 207 | 603 | 810 | 25.6 % (short-skewed) |
| 4 | 322 | 933 | 1,255 | 25.7 % (short-skewed) |
| 5 | 321 | 931 | 1,252 | 25.6 % (short-skewed) |
| 6 | 524 | 625 | 1,149 | 45.6 % (near-balanced) |
| 7 | 878 | 315 | 1,193 | 73.6 % (long-skewed) |

The cross-pair signal flips between strong-USD and weak-USD regimes,
producing dramatic per-fold long/short imbalances. Folds 1 and 2
(2022 latter half / 2022-23 winter) are completely one-sided.

The 100 % all-long fold 2 is particularly notable — every entry in
the 1,166-trade fold is a long position, all losing in aggregate
(−$66.44 fold PnL). This shows the rank-gap rule fires
*systematically* in one direction during regime extremes; if that
direction is wrong, the entire fold is wrong.

Aggregate long/short balance across folds (3,927 / 4,013) is close to
50/50, so there is no global directional bias.

### 7.4 Per-fold simultaneous-signal frequency

A "simultaneous signal" is an H4 bar where ≥ 2 pairs fire entries at
the same timestamp.

| fold | bars w/ any signal | bars w/ ≥ 2 pairs | sim. share | concurrency histogram |
|---|---:|---:|---:|---|
| 0 | 591 | 176 | 29.8 % | 1: 415, 2: 149, 3: 27 |
| 1 | 321 | 0 | 0.0 % | 1: 321 |
| 2 | 712 | 313 | 44.0 % | 1: 399, 2: 201, 3: 83, **4: 29** |
| 3 | 591 | 195 | 33.0 % | 1: 396, 2: 171, 3: 24 |
| 4 | 752 | 327 | 43.5 % | 1: 425, 2: 176, 3: 126, **4: 25** |
| 5 | 729 | 341 | 46.8 % | 1: 388, 2: 189, 3: 122, **4: 30** |
| 6 | 757 | 299 | 39.5 % | 1: 458, 2: 217, 3: 71, **4: 11** |
| 7 | 720 | 333 | 46.2 % | 1: 387, 2: 210, 3: 106, **4: 17** |

**Cross-fold (excluding fold_01 which has only 1 trading pair):
~40 % of bars-with-signals have ≥ 2 simultaneous entries.** Several
folds see 4 pairs firing at the same H4 bar.

**Critical implication for portfolio-aware runners.** If the runner
were portfolio-aware with `max_open_positions = 1` enforced
*across* pairs, the simultaneous-signal bars (~40 % of trading
bars) would each result in only one accepted entry instead of 2-4.
This would cut trade count substantially. But as shown in Phase 5
§6.4 and §6 of this doc, the per-pair runner architecture
(`MAX_OPEN_POSITIONS_EXCEEDED = 0`) does not enforce portfolio-wide
caps; each pair's engine runs independently.

This is a *runner architecture* finding, not a strategy choice. The
strategy *generates* the simultaneous signals (because the rank-gap
rule can be satisfied for multiple base/quote combinations in the
same currency-strength snapshot); the engine *accepts all of them*
because each pair has its own isolated execution context.

The Phase 0 plan's standing rule — "do not relax `max_open_positions`
or risk settings to rescue trade count" — applies in reverse here:
even a more restrictive (portfolio-aware) cap could not rescue the
strategy, because **per-pair expectancy is already negative on 6 of
7 pairs**. Filtering simultaneous signals would reduce trade count
but not change the sign of aggregate expectancy.

### 7.5 Effective per-pair firing rate

Defined as: `trades_in_pair_fold / common_index_length`. This is the
fraction of available H4 bars on which each pair received an
accepted entry within a fold.

Example (fold 5; common_index = 1,836 bars):

| pair | trades | firing rate |
|---|---:|---:|
| EUR_USD | 287 | 15.6 % |
| GBP_USD | 0 | 0.0 % |
| USD_JPY | 0 | 0.0 % |
| AUD_USD | 328 | 17.9 % |
| USD_CAD | 321 | 17.5 % |
| USD_CHF | 0 | 0.0 % |
| NZD_USD | 316 | 17.2 % |

Trading pairs in fold 5 fire on ~16-18 % of available H4 bars. This
is far above the cross-pair rotator's design intent (gate rare
high-conviction rank-gap signals); the rank-gap rule is being
satisfied on roughly 1 in 6 bars for trading pairs, not 1 in 50 or
1 in 100 as a true "high-conviction" rotator would be. Combined with
the 6-bar holding period, this produces high turnover.

Full per-fold firing-rate detail is in `risk/diagnostics.json` under
`cross_pair_specific.per_fold_firing_rate`.

## 8. Concurrency summary

- **BacktestEngine is single-instrument single-position-at-a-time**
  (one position per pair per engine instance).
- **The CAMPAIGN_013 runner invokes one engine PER PAIR PER FOLD.**
  Multi-instrument concurrency is constrained at the RiskEngine layer
  *within each pair's run*, but **not** across the 7-pair universe.
- **`MAX_OPEN_POSITIONS_EXCEEDED` rejections observed: 0** (the
  per-pair runner has nothing to multi-instrument-cap).
- A portfolio-aware runner would reduce trade count proportionally
  to the simultaneous-signal rate (~40 %) but cannot rescue per-pair
  negative expectancy (Phase 5 §6.4).

## 9. Diagnostic findings vs verdict

| diagnostic dimension | observation | consistent with REJECT? |
|---|---|:---:|
| per-pair PnL concentration | NZD_USD dominates 37 % of losses; USD_CHF + AUD_USD make up another 32 % | YES (consistent with Phase 5's single-pair-dominance reading) |
| max loss streaks | up to 14 (USD_CHF) | YES (long streaks consistent with negative per-trade expectancy) |
| time-stop dominance | 76.7 % of exits at 6-bar limit | YES (no take-profit + no edge → exits at time cap; drift dominates outcome) |
| session distribution | balanced across Asian / London / overlap; NY low due to bucket boundary | neutral (no time-of-day concentration risk) |
| risk-engine rejections | 5,523 / 13,463 = 41 % | neutral (RiskEngine reduces trade count but cannot rescue expectancy) |
| `MAX_OPEN_POSITIONS_EXCEEDED` | 0 (per-pair runner) | informational (architectural finding; not a verdict driver) |
| zero-trade pair-fold cells | 29 / 56 (52 %) | YES (cross-pair rule's sparseness reduces effective sample per fold, makes ≥ 4/7 gate structurally hard) |
| simultaneous signals | ~40 % of trading bars have ≥ 2 concurrent entries | informational (rank-gap rule is not high-conviction; high concurrency rate consistent with the 7,940-trade total) |
| per-pair firing rate | ~16-18 % of bars for trading pairs | informational (high turnover; not a true "rare rotation" signal) |
| cross-pair contract | satisfied on all 8 folds | informational (REJECT is on inherited gates, not BLOCKED) |

**No diagnostic finding contradicts the Phase 5 REJECT verdict.**

## 10. Explicit no-approval statement

`configs/approved_strategies.yaml` remains `approved: []`. The
diagnostics above are *informational supplements* to the Phase 5
REJECT verdict; they do not constitute a re-litigation of the
verdict. Even if every diagnostic in this report were "clean," the
inherited-gate REJECT would still hold.

- The candidate is **not** enabled in `configs/paper.yaml` or
  `configs/practice.yaml`.
- Paper / demo / live remain blocked.
- No human approval action is justified by this evidence.
- The standing rule "do not relax `max_open_positions` or risk
  settings to rescue trade count" remains intact; this diagnostic
  pass does not motivate any rule change.

## 11. Committed artifacts

| path | what |
|---|---|
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/risk/diagnostics.json` | machine-readable per-pair / per-fold / per-session / per-rejection-code breakdown + cross-pair-specific cross sections |
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/risk/diagnostics.md` | human-readable summary |
| `scripts/build_campaign_013_risk_diagnostics.py` | NEW; extends CAMPAIGN_012 diagnostics script with cross-pair-specific sections (zero-cells, long/short, simultaneous signals, firing rate, contract status) |
| `docs/research/CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md` (this doc) | sprint-level summary |

## 12. Cross-links

- [`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_013_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_013_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_013_FINANCING_OVERLAY.md`](CAMPAIGN_013_FINANCING_OVERLAY.md)
- [`CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md) (sibling)
- [`CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md) (sibling)
- [`CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md) (sibling)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
