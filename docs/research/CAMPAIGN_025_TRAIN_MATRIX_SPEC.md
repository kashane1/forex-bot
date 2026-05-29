# CAMPAIGN_025 — train-matrix specification (FROZEN before evidence)

Machine-readable: `research/campaign_025/train_matrix/candidate_registry.json`.
**16 candidates** (≤ preferred 16, ≤ max 24, ≤ hard-max 36). Frozen 2026-05-28,
before any train/validation evidence.

---

## Why a matrix, and why it is small

We test whether the C025 thesis (M5 Donchian breakout under M15 setup + H1/H4M1
trend + D1AGG regime) shows **robust** behaviour across a few **coherent** breakout/
exit designs. A small purposeful matrix (16) — not the full Cartesian product
(3·3·5·3·2·3 = 810) — keeps the multiple-comparisons surface tiny and avoids
overfitting. **Exit models are first-class strategy hypotheses**, not knobs: time-
stop-only, fixed 2R, fixed 3R, breakeven-then-trail, and Donchian channel exit are
genuinely different trading ideas about how a breakout should be harvested.

This is **not** unrestricted optimization, genetic search, or validation mining.

## Candidate table (frozen)

| ID | archetype | Donchian | stop (×ATR, farther of channel) | exit | time stop | H1 | M15 |
|---|---|---|---|---|---|---|---|
| C025_MTX_001 | baseline_continuation | 20 | 2.0 | time_stop_only | 48 | standard | pullback_or_compression |
| C025_MTX_002 | tight_breakout_scalp | 12 | 1.5 | fixed_2r_target | 36 | standard | pullback_or_compression |
| C025_MTX_003 | tight_strict_scalp | 12 | 1.5 | fixed_2r_target | 36 | strict | pullback_only |
| C025_MTX_004 | balanced_2r_breakout | 20 | 2.0 | fixed_2r_target | 48 | standard | pullback_or_compression |
| C025_MTX_005 | balanced_strict_2r | 20 | 2.0 | fixed_2r_target | 48 | strict | pullback_only |
| C025_MTX_006 | balanced_3r_continuation | 20 | 2.0 | fixed_3r_target | 72 | standard | pullback_or_compression |
| C025_MTX_007 | compression_3r_continuation | 20 | 2.0 | fixed_3r_target | 72 | standard | compression_only |
| C025_MTX_008 | wider_trend_runner | 30 | 2.5 | breakeven_then_atr_trail | 72 | standard | pullback_or_compression |
| C025_MTX_009 | strict_trend_runner | 30 | 2.5 | breakeven_then_atr_trail | 72 | strict | pullback_only |
| C025_MTX_010 | donchian_channel_follower | 20 | 2.0 | donchian_channel_exit | 72 | standard | pullback_or_compression |
| C025_MTX_011 | wide_donchian_channel_follower | 30 | 2.5 | donchian_channel_exit | 72 | standard | compression_only |
| C025_MTX_012 | fast_compression_breakout | 12 | 1.5 | fixed_2r_target | 36 | standard | compression_only |
| C025_MTX_013 | fast_compression_runner | 12 | 1.5 | breakeven_then_atr_trail | 48 | standard | compression_only |
| C025_MTX_014 | conservative_strict_no_target | 20 | 2.5 | time_stop_only | 72 | strict | pullback_only |
| C025_MTX_015 | shorter_base_no_target | 12 | 2.0 | time_stop_only | 48 | standard | pullback_or_compression |
| C025_MTX_016 | wider_base_no_target | 30 | 2.0 | time_stop_only | 72 | standard | pullback_or_compression |

Coverage: exit models {time_only 4, 2R 5, 3R 2, be+trail 3, channel 2}; Donchian
{12:5, 20:7, 30:4}; stop {1.5:4, 2.0:8, 2.5:4}; time-stop {36:3, 48:5, 72:8};
H1 {standard 12, strict 4}; M15 {p_or_c 8, pullback 4, compression 4}. All 16 have
unique parameter signatures (deduplicated).

## Base setup (preserved from scaffold, all candidates)

Long: H4 bullish, H1 bullish, D1AGG not-bearish, M15 setup present, M5 close >
prior N-bar Donchian high → enter next M5 open. Short mirrors. HTF from last
completed bar only; `next_bar_open`; no `signal_bar_close`; no same-bar entry.

- **H1 standard:** EMA20>EMA50 (long) / EMA20<EMA50 (short) + agreeing 3-bar EMA20 slope.
- **H1 strict:** standard **and** close>EMA50 (long) / close<EMA50 (short).
- **M15 pullback:** low touched ≤EMA20 within last 8 completed M15 bars (mirror for short).
- **M15 compression:** Donchian(12) width / ATR(14) ≤ 3.0.
- **M15 pullback_or_compression / pullback_only / compression_only** select which apply.

## Exact exit-model definitions (frozen)

R is measured from the **initial stop distance** `risk = |entry − initial_stop|`,
where the initial stop is the farther of `mult×ATR(14)` and the opposite prior
Donchian channel side, computed from data available at the signal bar.

- **time_stop_only:** hard stop, time stop, or end-of-data only. No target/BE/trail.
- **fixed_2r_target / fixed_3r_target:** take-profit at entry ± R·risk (R=2 or 3);
  hard stop and time stop remain active; no trail.
- **breakeven_then_atr_trail:** when price reaches **+1.0R intrabar** (M5 high for
  long / low for short), move stop to **entry** (breakeven). After **+1.5R intrabar**,
  trail on **completed bars**: long stop = max(existing, close − 1.5·ATR(14)); short
  = min(existing, close + 1.5·ATR(14)). No fixed target; time stop active.
- **donchian_channel_exit:** exit when a **completed** M5 close crosses the *prior*
  opposite Donchian(N) channel (long: close < prior Donchian low; short: close >
  prior Donchian high); hard stop and time stop remain active; no fixed target.

### Same-bar ambiguity & fill policy (frozen)

- Entry fill: **next M5 bar open** (conservative; no same-bar entry).
- Intrabar stop/target/BE/trail triggers use the M5 **high/low** of completed bars
  during the hold. When a single bar's range touches **both** the stop and the
  target, resolve **adverse-first** (assume the stop filled). This is the
  conservative convention and is applied uniformly.
- Donchian channel exit and time stop fill at the **next M5 bar open** after the
  triggering completed bar (conservative).
- **Exit priority:** (1) hard stop, (2) fixed target, (3) breakeven/trailing stop,
  (4) Donchian channel exit, (5) time stop, (6) end-of-data.

## Exit-reason labels (emitted)

`hard_stop`, `fixed_target_2r`, `fixed_target_3r`, `breakeven_stop`,
`atr_trailing_stop`, `donchian_channel_exit`, `time_stop`, `end_of_data`.

## Train-only selection filters

A candidate is **eligible** iff (on TRAIN, all pairs aggregated):
1. trades ≥ 100 (if **no** candidate reaches 100 → `BLOCKED_MATRIX_TOO_SPARSE`, no champion).
2. expectancy_R ≥ 0.
3. profit factor ≥ 1.03.
4. ≥ 3/7 pairs non-negative.
5. 2× cost-stress expectancy_R ≥ −0.005.
6. spread/ATR not structurally hostile (documented).
7. no single pair contributes > 50% of total positive R (else `SINGLE_PAIR_REVIEW_ONLY`).
8. profits not dependent on ambiguous same-bar target/stop assumptions.

## Train-only ranking (eligible candidates)

1. cost-stress-adjusted expectancy_R (base expectancy blended toward 2× stress),
2. number of non-negative train pairs,
3. lower single-pair concentration,
4. validation-readiness stability proxy (adequate trades, balanced long/short, no
   single-exit-reason artifact),
5. profit factor,
6. lower turnover when otherwise close,
7. simpler / more base-like candidate on ties.

Do **not** pick a candidate solely for highest raw expectancy if it has low trade
count, high pair concentration, or ambiguity-sensitive exits.

## No-validation-selection rule

The matrix runs on **train only**. Validation runs **once** on the **single**
train-selected champion. Validation metrics never influence selection. Non-selected
candidates are never validated. `selection_uses_validation: false` in the registry.

## Single-pair review rule

If one pair is materially strong but the aggregate train (or later validation)
gates fail, classify **`SINGLE_PAIR_REVIEW_ONLY_CANDIDATE`** — never PASS, never
approval — and require a separate future precommit for any single-pair campaign.

## Blocked conditions

`BLOCKED_DATA_COVERAGE`, `BLOCKED_MATRIX_TOO_SPARSE`,
`REJECT_MATRIX_NO_TRAIN_CANDIDATE`, `TRAIN_MATRIX_VALIDATION_REJECT`,
`SINGLE_PAIR_REVIEW_ONLY_CANDIDATE`. None permit approval or lockbox opening.
