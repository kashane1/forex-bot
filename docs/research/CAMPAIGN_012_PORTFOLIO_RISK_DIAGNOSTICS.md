# CAMPAIGN_012 Portfolio-Risk Diagnostics (Phase 7)

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-walk-forward-001`
`strategy_evidence: false`

Phase 7 portfolio-risk diagnostics for **CAMPAIGN_012 /
`regime_switcher_atr_percentile 0.1.0-c012`**. Diagnostic only —
**does not gate the verdict.** The Phase 5 verdict is `REJECT`
regardless. This doc records the risk-engine behaviour observed
during the walk-forward run, the trade-distribution shape, and a
comparison to CAMPAIGN_010 / CAMPAIGN_011 diagnostics.

> Diagnostic only. No strategy approved. `configs/approved_strategies.yaml`
> remains `approved: []`. CAMPAIGN_012 verdict remains REJECT.

## 1. Command run

```bash
python scripts/build_campaign_012_risk_diagnostics.py \
  --campaign-dir backtests/CAMPAIGN_012_regime_switcher_atr_percentile
```

Output (committed):

- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/risk/diagnostics.json`
- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/risk/diagnostics.md`

## 2. Concurrency (PASS)

| dimension | value |
|---|---|
| max concurrent open positions per instrument | **1** (structurally enforced) |
| `risk.max_open_positions` (config) | 1 |
| `risk.max_positions_per_instrument` (config) | 1 |
| `risk.max_correlated_positions` (config) | 1 |
| strategy R2 (block re-entry on existing position) | enforced |
| BacktestEngine concurrency model | single-instrument, single-position-at-a-time |

**Concurrency is structurally bounded; gate PASS.**

## 3. Per-pair exposure

| pair | trades | total units | total notional (quote ccy approx) | total PnL (USD) | max loss streak | max win streak | largest single loss | largest single win |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EUR_USD | 479 | 90,063 | 97,382 | −5.36 | 8 | 6 | −1.30 | +4.98 |
| GBP_USD | 555 | 82,832 | 105,856 | −40.61 | 8 | 6 | −1.28 | +2.53 |
| USD_JPY | 624 | 103,974 | 14,046,568 | **+41.71** | 9 | 8 | −1.30 | +4.86 |
| AUD_USD | 551 | 111,202 | 75,148 | −67.39 | 8 | 7 | −1.28 | +4.20 |
| USD_CAD | 584 | 137,031 | 186,190 | −63.55 | 10 | 9 | −1.29 | +2.62 |
| USD_CHF | 542 | 99,701 | 91,404 | −28.69 | 10 | 9 | −1.29 | +4.21 |
| NZD_USD | 391 | 87,860 | 53,902 | −53.68 | 9 | 6 | −1.29 | +2.96 |
| **total** | **3,726** | — | — | **−217.58** | — | — | — | — |

(USD_JPY's "total notional" is huge because it is denominated in JPY,
where 1 USD ≈ 150 JPY — multiplying units by entry-price-in-quote
gives a large number; this is not a risk concern.)

**Per-pair ratio max/min:** 624 / 391 = **1.60** — uniform-like
distribution. (CAMPAIGN_011's ratio was 1.65; CAMPAIGN_010's was
12.0.) The regime gate fires roughly evenly across pairs given how
the trend filter samples bars.

## 4. Session clustering (entry UTC hour)

| UTC hour | trades |
|---:|---:|
| 01:00 | 603 |
| 02:00 | 377 |
| 05:00 | 480 |
| 06:00 | 229 |
| 09:00 | 520 |
| 10:00 | 265 |
| 13:00 | 604 |
| 14:00 | 338 |
| 17:00 | 221 |
| 18:00 | 89 |

The H4 candle close grid (NY-aligned) lands at 01, 05, 09, 13, 17 UTC
in standard time and 02, 06, 10, 14, 18 in DST. Both alignments are
visible. Bin counts reflect how many bars per alignment can produce
signals; the strategy itself does not concentrate signals at any
specific hour.

### 4.1 4-bucket session distribution

| session bucket | trades | share % |
|---|---:|---:|
| asian (22–06 UTC) | 1,460 | **39.2 %** |
| london (06–12 UTC) | 1,014 | **27.2 %** |
| london_ny_overlap (12–16 UTC) | 942 | **25.3 %** |
| ny (16–22 UTC) | 310 | **8.3 %** |

**No single bucket > 50 % concentration.** The asian-heaviest profile
reflects that hours 22–05 contain more H4 close slots (4 slots: 22,
01/02, 05) than NY (1–2 slots). This is a bin-of-hours artifact, not
a strategy concentration. Distribution shape mirrors CAMPAIGN_011's
(diffuse across 4 buckets) and is the *opposite* of CAMPAIGN_010's
100 % london concentration.

## 5. Exit reason distribution

| reason | trades | share % |
|---|---:|---:|
| time (max_bars_in_trade = 6) | 2,953 | **79.3 %** |
| stop (ATR stop hit) | 760 | 20.4 % |
| eod (end-of-day flush) | 13 | 0.3 % |

**Time-stop exit rate 79.3 %** — matches CAMPAIGN_011's ~75 % time-
stop rate signature. The regime switcher's exit mechanics (ATR stop +
max_bars_in_trade = 6) behave identically to CAMPAIGN_010 / 011 — this
is a consistency check on the cost-model envelope, not on edge.

## 6. RiskEngine rejection-code distribution (mode=backtest)

| code | count | share of rejections % |
|---|---:|---:|
| SPREAD_TOO_WIDE | 2,013 | 72.6 % |
| SESSION_BLOCKED | 758 | 27.4 % |

**Total signals rejected: 2,771.** Total signals emitted by strategy:
2,771 (rejected) + 3,726 (filled) = **6,497**. RiskEngine rejection
rate: 2,771 / 6,497 = **42.7 %**.

- **SPREAD_TOO_WIDE rejection (72.6 % of rejections)** — the
  per-pair `max_spread_pips` filter is gating ~31 % of all signals.
  This is binding cost-safety behavior and matches CAMPAIGN_010 / 011
  exactly (identical spread filter config).
- **SESSION_BLOCKED rejection (27.4 %)** — the rollover (16:45–17:15
  NY) + Friday-close (15:00–23:59 Fri) + Sunday-open (00:00–19:00 Sun)
  blackouts cumulatively block ~12 % of signals.

The RiskEngine is doing its job. Without it, an additional 2,771
signals would have entered the engine at unfavourable spreads or
session-blackout timing.

## 7. Regime-period clustering (informational)

The regime switcher fires only when the prior-day D1AGG ATR-14 is in
the top 30 % of the trailing 60 D1AGG ATR distribution. The Phase 4
fold-by-fold trade counts implicitly reveal regime activity:

| fold | trades | test window | regime activity (relative) |
|---|---:|---|---|
| 0 | 678 | 2021-12 → 2022-06 (Russia-Ukraine; USD strength) | high |
| 1 | 811 | 2022-06 → 2022-12 (Fed-hike peak) | very high |
| 2 | 320 | 2022-12 → 2023-06 (banking-crisis volatility) | medium-low |
| 3 | 254 | 2023-06 → 2023-12 | low |
| 4 | 358 | 2023-12 → 2024-06 | medium |
| 5 | 407 | 2024-06 → 2024-12 (best PF=1.36) | medium |
| 6 | 638 | 2024-12 → 2025-06 (tariff news, USD volatility) | high |
| 7 | 260 | 2025-06 → 2025-11 (relative calm) | low |

Fold 0–1 (Russia-Ukraine + Fed hikes) produced the highest trade
counts and the worst returns — the regime gate fired *more* during
genuine vol periods, but the trend filter went the wrong way on those
trades. Fold 5 (relatively calmer 2024-H2) had the only positive
aggregate return (+1.52 %; PF 1.36) but still failed
pairs_positive_ge_4_of_7.

**Conclusion:** trade clusters do follow vol-regime periods, but the
clustering does not translate to positive expectancy. The "trends
follow vol" hypothesis is not borne out on this universe.

## 8. Loss streaks (per pair)

| pair | max loss streak | max win streak |
|---|---:|---:|
| EUR_USD | 8 | 6 |
| GBP_USD | 8 | 6 |
| USD_JPY | 9 | 8 |
| AUD_USD | 8 | 7 |
| USD_CAD | **10** | 9 |
| USD_CHF | **10** | 9 |
| NZD_USD | 9 | 6 |

Max loss streaks (8–10) are moderately worse than the random null
baseline (which would land around 6–8 at 45–47 % win rate). The
regime + trend filter produces slightly *more clustered* losses than
random — consistent with the gate triggering during the same vol
regime where the trend is going the wrong way.

## 9. Drawdown clustering (informational)

Per-fold median per-pair max drawdown (extracted from `fold_detail.json`):

| fold | median pair max DD % |
|---|---:|
| 0 | −2.20 % |
| 1 | −2.42 % |
| 2 | −1.89 % |
| 3 | −1.03 % |
| 4 | −1.06 % |
| 5 | −1.11 % |
| 6 | −1.79 % |
| 7 | −1.35 % |

Median per-pair max DD < 2.5 % per fold (test window ~6 months). The
drawdowns are not catastrophic on a per-fold-per-pair basis; the
issue is that they are *consistent* and accumulate across the 4-year
universe.

## 10. Per-pair ratio comparison to CAMPAIGN_010 / CAMPAIGN_011

| campaign | per-pair ratio max/min (trade count) | interpretation |
|---|---:|---|
| CAMPAIGN_010 (session breakout) | **12.0** | highly concentrated; London-session-dependent |
| CAMPAIGN_011 (null model) | **1.65** | uniform |
| **CAMPAIGN_012 (regime switcher)** | **1.60** | **uniform-like** (similar to null) |

The regime-switcher's pair distribution looks like the null model's:
roughly uniform across pairs. This is consistent with a regime feature
that gates by vol rather than by pair-specific edge.

## 11. RiskEngine gate behavior (PASS)

- **Spread filter functioning correctly:** 2,013 SPREAD_TOO_WIDE
  rejections out of 6,497 signals = 31 %. The per-pair
  `max_spread_pips` (1.5–2.5 pips) is binding on high-vol bars where
  spreads widen.
- **Session filter functioning correctly:** 758 SESSION_BLOCKED
  rejections = 12 %. Rollover / Friday-close / Sunday-open blackouts
  cumulatively gate ~12 % of signals.
- **Per-instrument cap functioning correctly:** No two concurrent
  positions on the same instrument observed (R2 + engine constraint).

## 12. Time-stop vs ATR-stop exits (PASS structural)

| exit type | count | share % | consistent with CAMPAIGN_010 / 011? |
|---|---:|---:|:---:|
| time (max_bars_in_trade = 6) | 2,953 | 79.3 % | ✓ (CAMPAIGN_011 was ~75 %) |
| stop (ATR stop) | 760 | 20.4 % | ✓ |
| eod (end-of-day flush) | 13 | 0.3 % | ✓ |

Cost-model envelope identical to CAMPAIGN_010 / 011. The time-stop
dominance is structural (the strategy uses `max_bars_in_trade = 6`
and time stops are common for short-horizon strategies); it is not a
signal-quality red flag.

## 13. Pipeline sanity checks (8 / 8 PASS)

| # | check | result |
|---|---|:---:|
| 1 | per-fold trade-count non-zero | ✓ (range 254–811) |
| 2 | per-fold per-pair trade-count sums to fold trade-count | ✓ |
| 3 | no trade exceeds `max_bars_in_trade = 6` | ✓ |
| 4 | no trade exits at a price violating the stop | ✓ |
| 5 | per-fold returns sum across pairs = fold aggregate | ✓ |
| 6 | RiskEngine rejection counts recorded | ✓ (SESSION_BLOCKED 758, SPREAD_TOO_WIDE 2013) |
| 7 | SESSION_BLOCKED rejections present | ✓ (rollover/Fri close/Sun open) |
| 8 | SPREAD_TOO_WIDE rejections present | ✓ (per-pair spread filter binding) |

**8 / 8 sanity checks pass.**

## 14. Comparison to CAMPAIGN_010 / CAMPAIGN_011 diagnostics

| diagnostic | CAMPAIGN_010 (session) | CAMPAIGN_011 (null) | **CAMPAIGN_012 (regime sw)** |
|---|---|---|---|
| max concurrent positions per instrument | 1 (enforced) | 1 (enforced) | **1 (enforced)** |
| per-pair ratio max/min | 12.0 (concentrated) | 1.65 (uniform) | **1.60 (uniform)** |
| session distribution | 100 % London | diffuse | **diffuse (asian 39 %; london 27 %; overlap 25 %; ny 8 %)** |
| time-stop exit % | ~75 % | ~75 % | **79.3 %** |
| SPREAD_TOO_WIDE rejections | (recorded) | (recorded) | **2,013** |
| SESSION_BLOCKED rejections | (recorded) | (recorded) | **758** |
| 8 sanity checks | 8 / 8 | 8 / 8 | **8 / 8** |

CAMPAIGN_012's diagnostic shape **most resembles CAMPAIGN_011 (the
null model)**, not CAMPAIGN_010 (the structured session strategy).
The trade distribution is uniform-across-pairs, session-diffuse, and
time-stop-dominated. The regime gate did not concentrate trading
toward profitable subsets — it produced a uniform-noise-shaped
distribution that lost to costs across all pairs except USD_JPY
(which sat at the random-walk floor).

## 15. Risk concerns / pass-warn-fail classification

| concern | classification | rationale |
|---|:---:|---|
| concurrency | **PASS** | structurally bounded |
| per-pair concentration | **PASS** | 22.4 % dominance (single-pair) < 40 % gate |
| per-fold concentration | **PASS** | 28.5 % dominance (single-fold) < 60 % gate |
| RiskEngine behaviour | **PASS** | spread + session filters binding as expected |
| sanity checks | **PASS** | 8 / 8 |
| loss-streak length | WARN | 10-bar streaks on USD_CAD / USD_CHF; not catastrophic but worse than random null |
| drawdown clustering | PASS | per-fold median DD < 2.5 %; no fold catastrophic |

**No risk-diagnostic concern would flip CAMPAIGN_012 from REJECT to
RESEARCH_PASS_UNAPPROVED.** The diagnostic shape is consistent with a
strategy that produces no edge — not with one that has edge but is
risk-misconfigured.

## 16. Missing tooling

None for the diagnostics this sprint required. All measurements above
were computed by `scripts/build_campaign_012_risk_diagnostics.py`
(mirrors `build_campaign_011_risk_diagnostics.py` verbatim with
campaign-id swap).

Future diagnostic improvements (not required for CAMPAIGN_012's
REJECT verdict; would only matter if a future candidate reached
`RESEARCH_PASS_UNAPPROVED`):

- Trade-level open-position-overlap audit across pairs (the engine
  enforces single-instrument single-position, but cross-pair
  concurrency is bounded only by `risk.max_open_positions = 1` —
  worth a future tooling sprint to verify exact concurrent counts
  across the universe).
- Margin-utilization simulation (currently only an upper bound is
  recorded; would need full intra-bar account state).

## 17. Explicit no-approval statement

These diagnostics are **diagnostic only**. They do not flip the Phase 5
verdict. CAMPAIGN_012 remains `REJECT`. `configs/approved_strategies.yaml`
remains `approved: []`. Paper / demo / live remain blocked.

## 18. Committed artifacts

| path | what |
|---|---|
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/risk/diagnostics.json` | machine-readable diagnostics |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/risk/diagnostics.md` | human-readable summary |
| `scripts/build_campaign_012_risk_diagnostics.py` | NEW; mirrors CAMPAIGN_011 verbatim |
| `docs/research/CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md` (this doc) | sprint-level summary |

## 19. Cross-links

- [`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_012_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_012_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_012_FINANCING_OVERLAY.md`](CAMPAIGN_012_FINANCING_OVERLAY.md)
- [`CAMPAIGN_012_FINANCING_RISK_READINESS.md`](CAMPAIGN_012_FINANCING_RISK_READINESS.md)
- [`CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md) (sibling)
- [`CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md) (sibling)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
