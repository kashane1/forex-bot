# C008 Trade Anatomy Diagnostics

**Diagnostic only** — `strategy_evidence: false`

Source: `research/c008_post_mortem/c008_trade_anatomy.json` from existing baseline train/validation trade CSVs (354 trades). No retuning.

## Overall shape

| split | trades | exp R | median R | win % | PF | avg bars | avg spread pips |
|---|---:|---:|---:|---:|---:|---:|---:|
| train | 216 | −0.025 | −0.79 | 27.8% | 0.99 | 18.8 | 1.55 |
| validation | 138 | +0.161 | −0.73 | 31.9% | 1.27 | 20.9 | 1.55 |

Report aggregate train exp R is −0.017 (campaign-weighted); trade-level mean is −0.025 — same sign, flat-negative band.

## Exit reason — dominant structural pattern

| split | exit | trades | exp R | win % |
|---|---|---:|---:|---:|
| train | stop | 153 | −0.80 | 0% |
| train | time | 62 | +1.89 | 96.8% |
| validation | stop | 88 | −0.79 | 0% |
| validation | time | 50 | +1.83 | 88.0% |

**All 44 validation winners exited via time stop** (40-bar horizon). Train losers are overwhelmingly hard-stop exits (153/156). Positive validation performance is structurally tied to trades that survive to the time stop.

## Train losers vs validation winners

| cohort | trades | exp R | exit mix | avg spread |
|---|---:|---:|---|---:|
| train losers | 156 | −0.79 | 153 stop, 2 time, 1 eod | 1.58 pips |
| validation winners | 44 | +2.11 | **44 time (100%)** | 1.56 pips |

Validation winner outlier concentration: top 5 winners = **32.9%** of total winner R (not majority, but meaningful tail).

Spread/cost did **not** materially differ between train losers and validation winners (~1.58 vs 1.56 pips).

## Pair concentration

**Train weak pair:** USD_CAD (−0.382 R, PF 0.40, 17% win rate). Other train pairs flat-to-positive per-pair.

**Validation:** all 6 pairs positive; strongest USD_CHF (+0.409 R), EUR_USD (+0.310 R).

## Session concentration

| session | train exp R | validation exp R |
|---|---:|---:|
| london | +0.151 | **+0.612** |
| london_ny_overlap | −0.252 | −0.088 |
| asia | +0.031 | −0.057 |

Validation winners concentrated in **london** (18/44) and london_ny_overlap (15/44).

## Side / weekday

- Train: longs weaker (−0.113 R) than shorts (+0.057 R).
- Validation: both sides positive (long +0.129, short +0.180).
- Train Monday/Tuesday weak (−0.37/−0.38 R); validation Tuesday strong (+0.717 R).

## R distribution

Heavy mass at −1 R (stop-outs): train 95 trades in (−10,−1]; validation 58. Positive tail in (1,3] and (3,10] similar across splits — winners are few but large when time stop fires.

## What cannot be concluded

- Cannot claim session/pair filters would fix train without retuning (forbidden).
- Cannot approve based on validation time-stop winners alone.

## Disclaimer

Descriptive anatomy only. Not strategy evidence.
