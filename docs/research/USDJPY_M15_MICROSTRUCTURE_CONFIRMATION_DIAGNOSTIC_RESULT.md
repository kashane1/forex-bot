# USD_JPY M15 Microstructure-Confirmation Diagnostic — Result

**Status:** read-only diagnostic. No verdict change, no approval, no tuning, no C024, no campaign, no edge claim. USD_JPY-only. Findings are hypothesis-generating; no threshold is a parameter.

## Setup

- Winner: `profitable_trade = result_r > 0`.
- USD_JPY trades: 306 (train 133, validation 173).
- Win rate: 0.3791 (train 0.3459, validation 0.4046).
- Effect = |AUC−0.5|; negligible below 0.05. Stable = train & validation AUC on the same side of 0.5 with ≥ 30 per class.

## Baseline — old C022 EMA20-reclaim trigger

`reclaim_distance_atr`: AUC train 0.539 / validation 0.4863 · stable=False · min|AUC−0.5|=0.0137. This is the bar each microstructure primitive must beat.

## Headline

The strongest *stable live* separator is **range_expansion_after_compression** at |AUC−0.5| = 0.016 — **below the 0.05 negligibility floor**. No live primitive shows a material winner/loser separation.

## Per-detector score separation (winner AUC)

| detector | live? | AUC train | AUC val | stable | min|AUC−0.5| | overfit risk |
|---|---|---|---|---|---|---|
| reclaim_plus_impulse | live | 0.4908 | 0.4325 | yes | 0.0092 | low-signal (stable but negligible) |
| reclaim_plus_micro_swing_break | live | 0.4695 | 0.486 | yes | 0.014 | low-signal (stable but negligible) |
| liquidity_sweep_plus_displacement | live | 0.4648 | 0.5828 | no | 0.0352 | high |
| range_expansion_after_compression | live | 0.484 | 0.3828 | yes | 0.016 | low-signal (stable but negligible) |
| reclaim_plus_retest_hold | post-entry | 0.6112 | 0.552 | yes | 0.052 | elevated (stable but single-pair; needs OOS) |
| failed_reclaim_or_trap | post-entry | 0.5588 | 0.4091 | no | — | high |

## Present-vs-absent impact (does the confirmation help?)

Per split: win-rate lift, hard-stop reduction, straight-to-stop reduction, MFE improvement (present − absent; positive = the confirmation helps).

### reclaim_plus_impulse (live)

| split | n present | n absent | win-rate lift | hard-stop ↓ | straight-to-stop ↓ | MFE ↑ |
|---|---|---|---|---|---|---|
| train | 40 | 93 | 0.0059 | 0.0487 | 0.1118 | 0.0783 |
| validation | 57 | 116 | -0.0801 | -0.1312 | -0.1874 | -0.1983 |
- win-rate lift same-signed across splits: **False**.
- risk notes: present-vs-absent win-rate lift not same-signed across splits.

### reclaim_plus_micro_swing_break (live)

| split | n present | n absent | win-rate lift | hard-stop ↓ | straight-to-stop ↓ | MFE ↑ |
|---|---|---|---|---|---|---|
| train | 66 | 67 | -0.0249 | -0.0242 | 0.0109 | -0.002 |
| validation | 70 | 103 | -0.0558 | -0.0522 | -0.0721 | 0.4191 |
- win-rate lift same-signed across splits: **True**.

### liquidity_sweep_plus_displacement (live)

| split | n present | n absent | win-rate lift | hard-stop ↓ | straight-to-stop ↓ | MFE ↑ |
|---|---|---|---|---|---|---|
| train | 110 | 23 | 0.1027 | 0.0522 | -0.0209 | 0.1453 |
| validation | 139 | 34 | 0.1376 | 0.0774 | -0.0093 | 0.3198 |
- win-rate lift same-signed across splits: **True**.
- risk notes: AUC direction not stable across train/validation.

### range_expansion_after_compression (live)

| split | n present | n absent | win-rate lift | hard-stop ↓ | straight-to-stop ↓ | MFE ↑ |
|---|---|---|---|---|---|---|
| train | 25 | 108 | 0.0667 | 0.1589 | 0.2441 | 0.4334 |
| validation | 26 | 147 | -0.0688 | -0.0599 | -0.0764 | 0.1977 |
- win-rate lift same-signed across splits: **False**.
- risk notes: present-vs-absent win-rate lift not same-signed across splits.

### reclaim_plus_retest_hold (post-entry diagnostic-only)

| split | n present | n absent | win-rate lift | hard-stop ↓ | straight-to-stop ↓ | MFE ↑ |
|---|---|---|---|---|---|---|
| train | 98 | 35 | 0.1205 | 0.1429 | 0.3592 | 0.4601 |
| validation | 140 | 33 | -0.0242 | -0.0134 | 0.1493 | 0.0484 |
- win-rate lift same-signed across splits: **False**.
- risk notes: post-entry detector — not a live entry feature regardless of separation; present-vs-absent win-rate lift not same-signed across splits.

### failed_reclaim_or_trap (post-entry diagnostic-only)

| split | n present | n absent | win-rate lift | hard-stop ↓ | straight-to-stop ↓ | MFE ↑ |
|---|---|---|---|---|---|---|
| train | 74 | 59 | -0.1704 | -0.2416 | -0.4087 | -0.532 |
| validation | 82 | 91 | -0.2592 | -0.3215 | -0.3963 | -1.0063 |
- win-rate lift same-signed across splits: **True**.
- risk notes: post-entry detector — not a live entry feature regardless of separation; a class fell below the min-N trust floor on a split; AUC direction not stable across train/validation.

## Context features (for reference, not entry signals)

| feature | AUC train | AUC val | stable | min|AUC−0.5| |
|---|---|---|---|---|
| atr_at_entry | 0.4563 | 0.5125 | no | 0.0125 |
| atr_percentile | 0.5951 | 0.5336 | yes | 0.0336 |
| spread_to_atr_pct | 0.5117 | 0.466 | no | 0.0117 |
| hour | 0.5856 | 0.583 | yes | 0.083 |

## Reading (honest)

- **Live vs post-entry.** Only the *live* detectors could ever gate an entry. Retest-hold and failed-reclaim/trap inspect post-entry bars and are diagnostic-only — a separation there describes what already happened, it is not a usable entry filter.
- **Beating the baseline.** A primitive matters only if it separates winners from losers *better* than the inert EMA-reclaim trigger and stays stable across splits.
- **Single-pair caution.** USD_JPY's per-split samples are small; a large effect is a reason for *more* scrutiny, not less. No threshold here is a parameter and nothing is an edge.
No threshold selected as a parameter. Effect = |AUC-0.5|; negligible below 0.05. Stable = train & validation AUC same side of 0.5 with >= 30 per class. Single-pair sample is small — large effects are suspicious, not reassuring, until out-of-sample.
