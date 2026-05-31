# CAMPAIGN_026 — timeframe-ladder strategy specification (frozen)

**Frozen before any train evidence.** This spec + the machine-readable
[`candidate_registry.json`](../../research/campaign_026/timeframe_ladder/candidate_registry.json)
define the pre-committed matrix. Selection is **train-only**; validation never
selects timeframe or parameters. No approval, no test lockbox.

- campaign_id: `CAMPAIGN_026`
- strategy_family: `donchian_htf_confluence_timeframe_ladder`
- version: `0.1.0-c026`
- candidate count: **11** (preferred; hard max 15)
- candidate IDs: `C026_TF_001` … `C026_TF_011`

## Strategy structure

The C025 Donchian + HTF-confluence family, adapted by **execution timeframe**. Core
signal (unchanged from C025):

- **Donchian breakout** on the execution timeframe — channel uses **prior completed
  bars only** (`.shift(1)`); `close > donchian_high(n)` (long) / `close <
  donchian_low(n)` (short).
- **Entry** = next execution-bar open (`next_bar_open`).
- **HTF/local context** = last completed higher-timeframe bar (`merge_asof`
  backward) — **no lookahead**.
- **Initial stop** = farther of `atr_stop_multiple × ATR(prior bar)` and the opposite
  prior Donchian channel; risk = |entry_open − stop|.
- **Same-bar** stop/target ambiguity → adverse-first (stop wins).

## Execution timeframes & context ladder (frozen)

| Exec TF | Local setup | Trend gates | Regime |
|---|---|---|---|
| **M3** | M15 pullback/compression | H1 **and** H4M1 | D1AGG |
| **M15** | internal M15 pullback/compression | H1 **and** H4M1 | D1AGG |
| **M30** | H1 pullback/compression | H4M1 | D1AGG |

**M15 local-setup decision (frozen before evidence):** the spec permitted either an
H1 local setup *or* an internal M15 pullback/compression. We use the **internal M15**
option — it avoids H1 doubling as both the local-setup frame and a trend gate, keeping
M15 structurally parallel to how M3 uses its one-rung-up frame (M15) for setup while
H1/H4M1 act as trend. M30 keeps H1 as its (one-rung-up) local setup and drops the H1
trend gate (trend = H4M1 only), as the spec dictates.

Data provenance: M3/M15/M30/H1/H4M1 from M1-derived materialized bars
(`source=m1_materialized`); D1AGG from native-H4-derived aggregation (M1-derived D1AGG
**not** used). Fill realism: `next_bar_open`.

### Frozen shared parameters

ATR lookback 14; local EMA-fast 20, pullback lookback 8; compression Donchian 12 / ATR
14 / width≤3.0×ATR; H1 EMA 20/50 + 3-bar slope (standard vs strict adds close-vs-EMA50);
H4 EMA 20/50 trend; D1AGG EMA 20/50 + 3-bar slope "not-against". Donchian lengths used:
{20, 30}. Cost model: `COST_BASE` {fixed 0.2 pip, spread ×0.5}; `COST_STRESS_2X`
{fixed 0.5 pip, spread ×2.0}.

## Candidate matrix (11)

| ID | Exec | Donchian | ATR× | Exit | time-stop (bars) | context |
|---|---|---|---|---|---|---|
| C026_TF_001 | M3 | 20 | 2.0 | fixed_2r_target | 60 | standard |
| C026_TF_002 | M3 | 30 | 2.5 | breakeven_then_atr_trail | 90 | strict |
| C026_TF_003 | M3 | 30 | 2.5 | donchian_channel_exit (len 20) | 90 | standard |
| C026_TF_004 | M15 | 20 | 2.0 | fixed_2r_target | 32 | standard |
| C026_TF_005 | M15 | 20 | 2.0 | fixed_3r_target | 48 | standard |
| C026_TF_006 | M15 | 30 | 2.5 | breakeven_then_atr_trail | 48 | standard |
| C026_TF_007 | M15 | 20 | 2.0 | fixed_2r_target | 32 | strict (pullback_only) |
| C026_TF_008 | M30 | 20 | 2.0 | fixed_2r_target | 24 | standard |
| C026_TF_009 | M30 | 20 | 2.0 | fixed_3r_target | 36 | standard |
| C026_TF_010 | M30 | 30 | 2.5 | breakeven_then_atr_trail | 36 | standard |
| C026_TF_011 | M30 | 30 | 2.5 | donchian_channel_exit (len 20) | 36 | strict |

3 M3 + 4 M15 + 4 M30 = 11. Optional candidates 12–15 (compression-only / time-stop-only
baselines) were **not** added — 11 keeps the matrix small and within the preferred cap.
breakeven_then_atr_trail uses be=1.0R, trail-activation=1.5R, trail=1.5×ATR;
donchian_channel_exit uses opposite-channel length 20 (C025 conventions).

## Train-only selection filters (frozen)

- **trades ≥** 150 (M3) / 80 (M15, M30) — aggregate across pairs
- **expectancy ≥ 0** (net, COST_BASE)
- **profit factor ≥ 1.03**
- **≥ 3/7 pairs non-negative**
- **2× cost-stress expectancy ≥ −0.005R**
- **single-pair positive-R concentration ≤ 0.50** (else SINGLE_PAIR_REVIEW_ONLY)
- C011 deduped null = −0.0029154071495408797; promotion-grade beat margin +0.010R
  (applied at validation).

## Selection rule (train only; validation never selects)

Rank eligible candidates by, in order:

1. cost-stress-adjusted expectancy = ½(base + 2× stress) — descending
2. number of non-negative pairs — descending
3. lower spread/ATR
4. lower single-pair concentration
5. adequate trade count (more first)
6. profit factor — descending
7. (lower turnover / simpler timeframe handled implicitly by the above + ID tiebreak)
8. candidate_id (stable tiebreak)

Select **at most one** champion. If none is eligible →
`REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE` (or `SINGLE_PAIR_REVIEW_ONLY_CANDIDATE`
if a single-pair-flagged candidate is the only positive). **No validation-based
selection. No test lockbox.**
