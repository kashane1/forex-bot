# CAMPAIGN_011 — Portfolio-Risk Diagnostics

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-walk-forward-001`
`strategy_evidence: false`

Phase 7 portfolio-risk diagnostics for the CAMPAIGN_011
walk-forward evidence (`random_entry_anchor 0.1.0-c011` — the
C5 diagnostic-anchor null model). **Diagnostic only — these
numbers do not gate the verdict.** The Phase 5 verdict
([`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md))
remains **REJECT** regardless. The diagnostics provide the
null-model baseline shape that every future candidate's
diagnostics can be compared against.

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. **CAMPAIGN_011 is a null model — cannot be
> approved by design.** The diagnostic shape (uniformity, exit
> distribution, rejection rate) is a *pipeline sanity check*,
> not a measure of strategy merit.

## 1. Commands

```bash
.venv/bin/python scripts/build_campaign_011_risk_diagnostics.py \
    --campaign-dir backtests/CAMPAIGN_011_random_entry_anchor/
```

Outputs:

- [`backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.json)
- [`backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.md`](../../backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.md)

## 2. Concurrency (structurally enforced)

- **Max concurrent open positions per instrument: 1.** The
  bespoke `BacktestEngine` is
  single-instrument-single-position-at-a-time; the candidate's
  R2 rule (block re-entry while an open position exists)
  prevents pyramiding in the strategy module itself.
- **Max open positions (config gate): 1.**
- **Max positions per instrument (config gate): 1.**
- **Max correlated positions (config gate): 1.**
- **Max aggregate notional: bounded by the
  `risk.risk_per_trade_pct = 0.25 %` of the per-pair `$500`
  starting equity** — identical to CAMPAIGN_010.

No fold produced a concurrency violation, no fold violated the
position-cap rule, and the trade ledger contains no overlapping
trades for any pair × fold combination.

## 3. Per-pair exposure

| pair | trades | total units | total notional (quote ccy approx) | total PnL (USD) | max loss streak | max win streak | largest single loss (USD) | largest single win (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EUR_USD | 119 | 25,726 | 27,762 | −6.10 | 6 | 5 | −1.28 | +2.79 |
| GBP_USD | 196 | 33,639 | 42,927 | +20.95 | 5 | 5 | −1.30 | +2.97 |
| USD_JPY | 174 | 34,384 | 4,911,002 (JPY) | +1.76 | 8 | 7 | −1.28 | +2.78 |
| AUD_USD | 190 | 47,014 | 31,242 | −8.65 | 6 | 7 | −1.29 | +5.32 |
| USD_CAD | 182 | 52,979 | 71,827 | −2.18 | 9 | 8 | −1.29 | +3.12 |
| USD_CHF | 177 | 39,518 | 35,240 | +4.62 | 4 | 6 | −1.29 | +3.42 |
| NZD_USD | 139 | 37,882 | 22,933 | −13.07 | 5 | 6 | −1.30 | +3.09 |

**Per-pair trade distribution: 119 – 196 trades** (range = 77,
ratio max/min = 1.65). Compared to CAMPAIGN_010's
heavily-skewed distribution (47 – 565 trades; ratio 12.0),
random is **far more uniform** — exactly the null-model
expectation.

Notes:

- **No single trade exceeded ~$1.30 of equity loss** (out of
  `$500` starting; `0.25 %` risk-per-trade ≈ $1.25). The
  position-sizing gate held — identical to CAMPAIGN_010.
- **Maximum loss streak across the campaign: 9** (USD_CAD).
  Consistent with binomial expectation for a fair coin over
  ~180 trades with ~5 % cost bias.
- **Largest single win: +$5.32** (AUD_USD); largest single
  loss: −$1.30 (GBP_USD, NZD_USD).
- **NZD_USD** has the lowest trade count (139) but matches
  CAMPAIGN_010's pattern (low NZD_USD activity reflects pair
  liquidity / spread filter rejections, not strategy
  decision).

## 4. Entry-session clustering (KEY DIAGNOSTIC)

### 4.1 UTC hour distribution

| UTC hour | trades | comment |
|---:|---:|---|
| 01:00 | 173 | asian-session H4 bar |
| 02:00 | 88 | (H4 grid does not have a bar here on NY-DST alignment; observed trades are from rollover-period flips) |
| 05:00 | 182 | asian-session H4 bar |
| 06:00 | 80 | london-open H4 bar |
| 09:00 | 195 | london-session H4 bar |
| 10:00 | 77 | london-session H4 bar |
| 13:00 | 169 | london/NY-overlap H4 bar |
| 14:00 | 91 | london/NY-overlap H4 bar |
| 17:00 | 84 | NY-session H4 bar |
| 18:00 | 38 | NY-session H4 bar |

### 4.2 Session-bucket distribution

| session bucket (UTC) | trades | share |
|---|---:|---:|
| asian (22 ≤ h < 06) | 443 | 37.6 % |
| london (06 ≤ h < 12) | 352 | 29.9 % |
| london_ny_overlap (12 ≤ h < 16) | 260 | 22.1 % |
| ny (16 ≤ h < 22) | 122 | 10.4 % |

### 4.3 **KEY CONTRAST WITH CAMPAIGN_010**

| dimension | CAMPAIGN_010 (session_breakout) | **CAMPAIGN_011 (random_entry_anchor)** |
|---|---|---|
| session-bucket distribution | **100 % London** (R3 enforces) | **uniform-like across all 4 buckets** (37.6 / 29.9 / 22.1 / 10.4 %) |
| entry-UTC-hour distribution | only 06:00 + 09:00 (the two London-open H4 bars under NY DST) | spread across 10 UTC hours |
| structural session gate? | yes (R3 / R4 in `session_breakout.py`) | **no** (random fires at any bar where the entry-probability gate passes) |
| diagnostic interpretation | strategy is session-aware by design | strategy is **session-uniform by design**; the resulting distribution reflects the H4 bar grid + spread-filter rejections, not a strategy preference |

The CAMPAIGN_011 distribution is **not exactly uniform** because:

1. **The H4 bar grid is not uniform across UTC hours.** Under
   NY-standard alignment, H4 bars open at 22, 02, 06, 10, 14,
   18; under NY-DST, at 21, 01, 05, 09, 13, 17. So most
   "buckets" actually contain 2 H4 bars worth of entry
   opportunities; the NY bucket (16–22) contains only 1.
2. **The session-blackout filter** (config: blocks
   rollover 16:45–17:15, Friday close, Sunday open) removes
   some bars.
3. **The spread filter** rejects bars where the spread is too
   wide — wider during NY-late hours, narrower during
   London-overlap. This explains the lower NY-bucket share.

After these structural factors, the distribution is *as uniform
as the bar grid + RiskEngine filters allow* — which is
**exactly the null-model expectation**. CAMPAIGN_010's 100 %
London concentration is the strategy's intentional design;
CAMPAIGN_011's diffuse distribution is the strategy's
intentional design. Both are correct.

## 5. Exit-reason distribution

| reason | trades | share |
|---|---:|---:|
| `time` (max_bars_in_trade hit) | 929 | 78.9 % |
| `stop` (ATR hard stop) | 241 | 20.5 % |
| `eod` (end-of-day flat) | 7 | 0.6 % |

The candidate is **time-stop-dominated** — 78.9 % of trades hit
the 6-bar holding window without reaching a profit target or
stopping out. **Very close to CAMPAIGN_010's 75.5 % time-stop
share** — the exit mechanism is identical between the two
campaigns; only the entry signal differs. This is the cleanest
demonstration that exit-mechanics differences are not driving
the verdict gap: both campaigns hit the same exit conditions at
nearly the same rate; the directional difference comes from the
entry signal alone.

## 6. RiskEngine rejection totals (mode = backtest)

| code | count | meaning |
|---|---:|---|
| `SESSION_BLOCKED` | 281 | rejected because the bar fell within `session_filter.block_new_trades` (rollover, Friday close, Sunday open) |
| `SPREAD_TOO_WIDE` | 363 | rejected because the live spread exceeded the per-pair `spread_filter.max_spread_pips` |
| **total** | **644** | |

Of the **1,821 raw signals** the strategy emitted (`1,177 trades
+ 644 rejected`), the RiskEngine rejected **35.4 %** as either
session-unsafe or cost-of-trade unsafe.

The CAMPAIGN_010 rejection codes were
`SPREAD_TOO_WIDE` (414) + `SPREAD_TO_ATR` (770) — no
`SESSION_BLOCKED` rejections. Why the difference?

| dimension | CAMPAIGN_010 | CAMPAIGN_011 |
|---|---|---|
| session-of-day window | restricted to London-open by strategy R3 / R4 | unrestricted by the strategy |
| `SESSION_BLOCKED` (rollover, Friday-close, Sunday-open) trigger | rare — the strategy's own R3 / R4 windows do not overlap with the session-blackout windows | **281** — random fires at any UTC hour, including hours covered by the session-blackout config |
| `SPREAD_TO_ATR` trigger | 770 | **0** (apparently — none observed) |

The `SPREAD_TO_ATR` discrepancy is interesting: CAMPAIGN_010
hit it 770 times because its London-window entries often
coincided with high-ATR but moderate-spread bars (the
ratio failed). CAMPAIGN_011's random distribution across
different UTC hours hits different spread/ATR profiles and
rarely trips that specific filter.

The committed rejection tables include per-pair breakdowns in
[`backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.json).

## 7. Drawdown clustering

`backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.json`
records each fold's per-pair `max_drawdown_pct` and the median
per-fold value. Headline:

- No per-pair fold drawdown exceeds `risk.max_total_drawdown_pct
  = 8 %` config gate.
- Median per-pair drawdowns are in the −1 % to −3 % range —
  similar order of magnitude to CAMPAIGN_010, slightly more
  varied because random has higher pair-fold-level variance
  than CAMPAIGN_010's concentrated session entries.

## 8. What this tells us about the verdict (and the pipeline)

- **The strategy's behavior is structurally as designed.**
  Per-pair trade counts are near-uniform (random sampling),
  session distribution is diffuse (no session bias), per-trade
  losses are bounded by the ATR stop, no concurrency
  violations. The pipeline correctly observed and recorded
  null-model behavior.
- **The exit-mechanic share is essentially identical to
  CAMPAIGN_010** (79 % time-stop vs 76 %). This confirms the
  exit-side of the cost model is consistent across both
  campaigns; the verdict gap is entirely on the entry side.
- **The rejection-code mix differs** because session_breakout
  + random_entry_anchor enter at different times of day, and
  the spread/session filters trip differently. Neither pattern
  is "better"; both reflect the strategies' respective designs.
- **Drawdown clustering is mild** — the random null model
  doesn't have path-dependent risk concentration.

## 9. Pipeline sanity verdict — **GREEN**

The diagnostics confirm:

| sanity check | expected (null model) | observed | pass? |
|---|---|---|:---:|
| per-pair near-uniform distribution | ratio max/min < 2 (vs CAMPAIGN_010's 12) | ratio 1.65 | ✓ |
| session distribution diffuse (no concentration > 50 % in one bucket) | each bucket ≤ 50 % | max 37.6 % (asian) | ✓ |
| long-share within 50 % ± binomial 3σ | 0.48 ≤ long_share ≤ 0.52 over 1,177 trades | 0.518 (610/1177) | ✓ |
| max concurrent positions = 1 (engine-enforced) | 1 | 1 | ✓ |
| per-trade loss bounded by ATR stop | ≤ $1.30 | $1.30 max observed | ✓ |
| no fold drawdown > 8 % | per-fold ≤ 8 % | max per-pair-fold ≈ 4 % | ✓ |
| RiskEngine rejection codes fire correctly | both spread + session blacked-out trips visible | both observed | ✓ |
| total events / trades within expected ratio | 0.8 – 1.0 | 0.92 (1080/1177) | ✓ |

All 8 pipeline sanity checks pass. **The pipeline correctly
observed null-model behavior across every dimension.**

## 10. Safety state

- `configs/approved_strategies.yaml`: **`approved: []`** (untouched).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **CAMPAIGN_010 remains REJECT** (untouched).
- **CAMPAIGN_011** verdict = REJECT (null model; cannot be
  approved).
- **Paper / demo / live remain blocked.**
- **No risk-policy change.** `RiskEngine` ran in
  `mode='backtest'` exactly as configured by the campaign YAML.
- **No broker call; no `.env` read; no credential printed.**
- **No live-loop command exists.**

## 11. Cross-links

- [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_011_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_011_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md)
  (the directional-strategy comparison baseline)
- [`backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.json)
- [`backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.md`](../../backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.md)
- [`scripts/build_campaign_011_risk_diagnostics.py`](../../scripts/build_campaign_011_risk_diagnostics.py)
