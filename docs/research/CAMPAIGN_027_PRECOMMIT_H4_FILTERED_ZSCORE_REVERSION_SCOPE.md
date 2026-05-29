# CAMPAIGN_027_PRECOMMIT_H4_FILTERED_ZSCORE_REVERSION_SCOPE

**Status:** SCAFFOLD_ONLY / PRECOMMITTED / NOT_RUN / NOT_APPROVED. Phase 2 of
`research-campaign-027-h4-filtered-zscore-reversion-scaffold-001`.

**This is the binding precommit.** It freezes the *exact* future strategy rules
**before any train/validation evidence is run**, so the rule cannot be re-tuned
after seeing results. Parameters are taken from the edge-discovery front-gate
artifacts; where the docs were silent, the value is taken verbatim from the lab
engine that produced the evidence
(`research/edge_discovery/front_gate_idea_selection/run_filter_ablation.py`,
`run_signal_probes.py`) and cited inline. Nothing here is approved; the test
lockbox stays closed; `configs/approved_strategies.yaml` stays `approved: []`.

> Evidence trace:
> [reconciliation](CAMPAIGN_027_EDGE_DISCOVERY_TO_PRECOMMIT_RECONCILIATION.md),
> [filter ablation](EDGE_DISCOVERY_FILTER_ABLATION_RESULTS.md),
> [signal probes](EDGE_DISCOVERY_SIGNAL_PROBE_RESULTS.md),
> [matched null](EDGE_DISCOVERY_MATCHED_NULL_SCREENING_RESULTS.md).
> Binding gates: [reentry gates](FUTURE_CAMPAIGN_REENTRY_GATES.md).

---

## Identity

| field | value |
|---|---|
| campaign_id | CAMPAIGN_027 |
| strategy name | `h4_filtered_zscore_reversion` |
| version | `0.1.0-c027` |
| timeframe | **H4** (execution and signal; no other timeframe is read) |

## Universe

The **seven majors**, all traded (not narrowed):

```
EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD
```

Rationale: the edge-adding subset is **pair-robust (6/7 positive; USD_CHF ≈
flat)**; the `f_cost_adv_pair` filter only reduces sample (no edge gain), so the
universe is **not** narrowed to cheap pairs. USD_JPY is a cost-advantaged member,
**not** a standalone thesis (its single-pair overlay is weaker than all-pair and
was flagged `LIKELY_SELECTION_NOISE`). USD_CHF is retained (precommitted) despite
≈flat front-gate expectancy; per-pair degradation is a future diagnostic, not a
mid-campaign universe edit.

## Split plan (placeholder — windows frozen, NOT run this sprint)

```
train:      2020-01-01 → 2022-12-31
validation: 2023-01-01 → 2024-12-31
test:       2025-01-01 → 2026-05-20   (LOCKBOX — sealed; not opened this sprint)
```

These windows are the repo-standard splits (same as C025). The exact
train/validation fold boundaries used for selection are the future sprint's to
declare *before* its run; selection happens on **train only** (gate G7).
Validation is confirmation, never parameter selection. **No split is run in this
sprint.**

## Data provenance

- **Source:** local H4 OHLC (bid/ask) for the 7 majors, 2020-01 → 2026-05, from
  `data/campaign_002.sqlite3` (worktree-aware resolution to the primary
  checkout). Native H4 candles, `complete = 1` only.
- **Mid:** `(bid + ask) / 2` per OHLC component (lab convention).
- **No new fetch; no broker round-trip; no derived/materialized timeframes**
  (the idea is native H4).

## Execution realism

| field | value |
|---|---|
| `fill_timing` | **`next_bar_open`** (the only approval-eligible model) |
| `execution_realism` | `conservative` |
| `evidence_use` | `approval_bound` |
| `promotion_eligible` | `false` |

**Fill-timing note (important).** The front-gate diagnostics entered at the
**signal-bar mid close** (`entry = mid[i]`) — a *diagnostic upper bound*, not
approval-eligible. The campaign trades the **approval-bound** convention:
**enter at the open of the next H4 bar after the signal bar** (`next_bar_open`).
`signal_bar_close` may be emitted as a diagnostic comparison only and is
`promotion_eligible: false` (gate G9). Any gap between the two is itself a
diagnostic the future sprint must report.

## Cost model

- **Optimistic (diagnostic):** realized per-bar bid-ask spread + 2 × 0.2-pip
  slippage, as a fraction of entry.
- **Conservative (BINDING for all gates):** flat **1.5-pip** spread + 2 × 0.2-pip
  slippage + **worst-case financing** over the 12-bar (≈48h) hold
  (`research.edge_discovery.costs.financing_stress_fraction`). This is the metric
  every kill condition is measured against.
- **2× cost stress:** the conservative model with spread and slip doubled; a
  material failure here is kill condition #7.

## Signal definition (exact, no lookahead)

Computed per pair on the **completed** H4 mid-close series; the decision is made
on the **last completed bar `t`** only.

```
LENGTH            = 20          # z-score lookback (bars)
mean_{t-1}        = mean( close[t-20 .. t-1] )      # rolling(20).mean().shift(1)
std_{t-1}         = std(  close[t-20 .. t-1] )      # rolling(20).std().shift(1), pandas ddof=1
z_t               = (close_t - mean_{t-1}) / std_{t-1}
```

- **z-score lookback:** 20 bars. (`LENGTH = 20`.)
- **Mean/σ are shifted one bar** so bar `t`'s z compares the *current* completed
  close to the mean/σ of the *prior* 20 bars — no lookahead. **σ uses pandas
  default `ddof=1`** (matches the lab engine that produced the evidence; this is
  a deliberate fidelity choice and differs from `indicators.zscore`, which uses
  `ddof=0` — the campaign strategy module computes z inline to match the lab).
- **Base trigger:** `|z_t| ≥ 2.0`.
- **Strong-extension filter (retained):** `|z_t| ≥ 2.5`. → the effective entry
  threshold is **`|z_t| ≥ 2.5`**.

## Z-score lookback / threshold (frozen)

| parameter | value | source |
|---|---|---|
| z lookback `LENGTH` | **20** | `run_filter_ablation.py:LENGTH=20` |
| base trigger | `|z| ≥ 2.0` | `run_filter_ablation.py:Z_THRESH=2.0` |
| strong-extension threshold (effective entry) | **`|z| ≥ 2.5`** | `f_strong_extension` |

## Volatility-regime filter (low-vol, frozen)

```
TR_t       = max( high_t - low_t,
                  |high_t - close_{t-1}|,
                  |low_t  - close_{t-1}| )      # mid OHLC; close_{t-1} = prior mid close
ATR_t      = mean( TR[t-13 .. t] )              # rolling(14).mean() — simple mean of TR
atr_pct_t  = percentile_rank( ATR_t within ATR[t-249 .. t] ), then .shift(1)   # trailing 250, no lookahead
f_low_vol  = (atr_pct_{t} ≤ 0.33)
```

| parameter | value | source |
|---|---|---|
| ATR lookback | **14** (simple mean of TR, **not** Wilder) | `run_filter_ablation.py: pd.Series(tr).rolling(14).mean()` |
| ATR-percentile trailing window | **250** bars, shifted 1 | `atr.rolling(250).apply(...).shift(1)` |
| low-vol threshold | **≤ 0.33** | `f_low_vol` |

## Quiet-session filter (frozen)

UTC-hour session bucket of the **entry timestamp**
(`research.edge_discovery.matched_nulls.session_bucket_utc`):

```
asia  [0,7)   london [7,12)   london_ny_overlap [12,16)   new_york [16,21)   late [21,24)
f_quiet_session = session ∈ { asia, london }
```

## Side rule (frozen) — SHORT-ONLY

```
raw side    = -sign(z_t)          # toward the mean
short when   z_t ≥ +2.5           # sell the rich extension → revert down  → ENTER
long  when   z_t ≤ −2.5           # buy the cheap extension → revert up    → NOT ENTERED (diagnostic-only)
```

- **Entered:** short only. **Long signals are disabled** (logged as
  diagnostic-only, never sized, never carry evidence). Rationale: `f_long_side`
  is the only `FILTER_HURTS_EDGE` filter (−0.000199) and leave-one-out shows
  removing the long side *raises* expectancy. Reversion edge lives on the short
  side.
- If a later sprint wants to revisit the long side, that is a **new precommit**,
  not a mid-campaign edit.

## Entry timing (frozen)

- **Decision** on the last completed H4 bar `t` when **all** of: `z_t ≥ +2.5`
  (short), `f_low_vol`, `f_quiet_session` hold and no open position exists for
  the instrument.
- **Fill** at the **open of bar `t+1`** (`next_bar_open`). `entry_intent =
  market`.

## Initial stop rule (frozen)

```
atr_stop_multiple = 3.0          # WIDE — tail-risk control, not the measured edge
stop_price (short) = entry + atr_stop_multiple × ATR_14_at_signal
```

Rationale: the front gate measured a **fixed-horizon proxy with no intrabar
stop**. A mandatory hard stop is required risk control (reversion's tail is a
range that breaks into a trend), but it is set **wide (3×ATR)** deliberately so
it bounds catastrophe without redefining the measured edge. The future train
sprint must report **stop sensitivity**: if the protective stop materially
degrades the h12 fixed-horizon expectancy, that is a finding to surface (the
C022/London-continuation lesson: tight intrabar stops destroyed a fixed-horizon
edge). The stop is **server-side-protective-eligible** but no broker is touched
this sprint.

## Exit rule (frozen)

- **Primary exit:** **time stop at 12 H4 bars** (the horizon `h12` at which the
  edge was measured; ≈48h). Exit at the `next_bar_open` of bar `t_entry + 12`
  (consistent with the entry fill convention).
- **Protective exit:** the hard ATR stop above (intrabar).
- **No fixed take-profit** in v1.
- **No trailing stop** in v1.

### Time stop (frozen)

```
max_bars_in_trade = 12           # H4 bars; matches the measured h12 proxy
```

### Fixed target?

**No.** The front gate measured a fixed-horizon exit, not a mean-touch target.
A **mean-touch target** (exit when price reverts to the rolling mean the z-score
is measured against, as in `mean_reversion` c009) is documented as a **future
variant only** — it changes the measured proxy and must be evaluated separately,
not folded into v1.

### Trailing stop?

**No.** The front gate provides no trailing-stop evidence.

### Exit priority

1. **Protective ATR stop** — if the bar's adverse excursion reaches the stop, the
   stop fills; the **adverse stop wins a same-bar tie** (conservative).
2. else **time stop** at `max_bars_in_trade = 12`.

(No target / no trailing means these are the only two exits; the time stop is the
expected dominant exit given the wide protective stop.)

## Risk / sizing (frozen, scaffold defaults)

Mirrors the repo scaffold convention (C025): starting equity \$500, 0.25%
risk/trade, one position per instrument, mandatory stop, server-side protection
required, no martingale/grid/averaging-down. These bound the future sim; they do
**not** enable any loop (the loop refuses while `approved_strategies.yaml` is
empty).

## Frozen parameter block (single source of truth)

```yaml
campaign_id: CAMPAIGN_027
strategy_family: h4_filtered_zscore_reversion
version: 0.1.0-c027
timeframe: H4
universe: [EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD]
signal:
  source: mid_close
  zscore_lookback: 20
  zscore_shift_bars: 1
  zscore_std_ddof: 1
  base_trigger_abs_z: 2.0
  strong_extension_abs_z: 2.5      # effective entry threshold
side:
  entered: short_only
  short_when_z_ge: 2.5
  long_when_z_le: -2.5             # DIAGNOSTIC_ONLY — never entered
filters:
  low_vol:
    atr_lookback: 14               # simple mean of TR
    atr_percentile_window: 250
    atr_percentile_shift_bars: 1
    threshold_le: 0.33
  quiet_session:
    sessions: [asia, london]       # UTC buckets asia[0,7) london[7,12)
  dropped:
    cost_adv_pair: FILTER_ONLY_REDUCES_SAMPLE
    long_side: FILTER_HURTS_EDGE
entry:
  fill_timing: next_bar_open
exit:
  max_bars_in_trade: 12            # time stop; measured h12 proxy
  atr_stop_multiple: 3.0           # protective, wide
  take_profit: none
  trailing_stop: none
  priority: [protective_atr_stop, time_stop]
cost:
  optimistic: realized_spread + 2*0.2pip_slip
  conservative: 1.5pip_spread + 2*0.2pip_slip + financing_over_12_bars   # BINDING
  stress: 2x_conservative
status: SCAFFOLD_ONLY / PRECOMMITTED / NOT_RUN / NOT_APPROVED
not_approved: true
promotion_eligible: false
paper_demo_live_enabled: false
```

## Recommended-approach compliance (kept deliberately simple)

- **No parameter matrix.** One frozen candidate only.
- **No broad exit-model search.** Simplest conservative H4 exit faithful to the
  measured h12 proxy (time stop + wide protective ATR stop).
- **No post-hoc long/short optimization.** Short-only is frozen from ablation,
  not re-chosen.
- Where the front gate under-specified the exit (it measured a stopless
  fixed-horizon proxy), v1 chooses the **simplest conservative** model and
  documents the deviation as a precommitted future-verification item.

## No-test-lockbox rule

The test window (2025-01-01 → 2026-05-20) is **sealed**. No runner, diagnostic,
or preflight in this campaign may sample it until a future sprint passes
train+validation **and** Backtrader parity **and** a human authorizes a
single-use open (gate G8). This sprint does not open it.

## No-approval rule

Approval is a separate, reviewed human edit to
`configs/approved_strategies.yaml`. This campaign is `not_approved: true`,
`promotion_eligible: false`, `paper_demo_live_enabled: false`. Nothing in this
scaffold approves it or makes it eligible.
