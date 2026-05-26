# C008 / C009 Evidence Reconstruction

**Diagnostic only** — `strategy_evidence: false`

Reconstructed from committed reports, pre-commit specs, and summary JSONs. No new backtests.

## Evidence table

| field | CAMPAIGN_008 | CAMPAIGN_009 |
|---|---|---|
| strategy version | `mean_reversion 0.1.0-c008` | `mean_reversion 0.2.0-c009` |
| rule change vs C008 | — | midline-target exit only |
| data window (screening) | train 2020–2022, val 2023–2024 | same |
| test window (2025–2026) | **NOT opened** | **NOT opened** |
| train trades | 216 | 252 |
| validation trades | 138 | 151 |
| train expectancy R | **−0.017** | **−0.062** |
| validation expectancy R | **+0.172** | **+0.170** |
| train PF | 1.02 | 0.97 |
| validation PF | 1.29 | 1.37 |
| train win % | 27.2% | 38.4% |
| validation win % | 31.5% | 47.8% |
| train return % | −0.05% | −0.08% |
| validation return % | +1.04% | +1.14% |
| train max-DD % | −2.92% | −2.45% |
| validation max-DD % | −1.84% | −1.40% |
| pairs positive (train) | 5/6 | 2/6 |
| pairs positive (validation) | **6/6** | 4/6 |
| stress_2x val exp R | n/a (full-window stress) | **+0.119** |
| stress_2x full exp R (C008) | **+0.027** | n/a |
| financing-stressed val exp R | +0.109 | +0.139 |
| screening gate | **FAIL** | **FAIL** |
| final verdict | **REJECT** (research-only) | **REJECT** (research-only) |

Sources: `backtests/CAMPAIGN_008_RANGE_MEAN_REVERSION_REPORT.md`, `backtests/CAMPAIGN_009_MEAN_REVERSION_REPORT.md`, pre-commit docs.

## Exact C008 failed gate

Pre-committed screening gate (`CAMPAIGN_008_RANGE_MEAN_REVERSION_PRECOMMIT.md`):

> Run test window only if ALL hold: **train expectancy ≥ 0**, validation expectancy ≥ 0, validation PF ≥ 1.05, ≥ 2 pairs positive on validation, validation trade count ≥ 30, stress_15x expectancy ≥ 0.

**Failed gate:** **train expectancy ≥ 0** — observed **−0.017 R** (PF 1.02, flat-negative within noise).

All other screening gates **passed**, including validation +0.172 R, PF 1.29, 6/6 pairs positive, validation n=138, full-window stress_2x +0.027 R.

Test lockbox (2025–2026) was **not opened** per marathon discipline.

## Exact C009 failed gate

Pre-committed screening gate (`CAMPAIGN_009_PRECOMMIT.md`):

> Gate 1: **train expectancy ≥ 0** — required ≥ 0.000 R, observed **−0.062 R** → **FAIL**.

Validation gates passed (+0.170 R, PF 1.37, 4/6 pairs, stress_2x +0.119 R, financing-stressed +0.139 R).

Midline-exit rescue **did not fix train** — train worsened vs C008 (−0.062 vs −0.017 R).

## Artifact gaps

| artifact | status |
|---|---|
| C008/C009 trade CSVs | present locally, gitignored (bulky) |
| C008/C009 summary JSONs | committed |
| Test-window runs | never executed (gate fail) |
| Evidence integrity | flagged LIKELY_CONTAMINATED in dedup audit — descriptive use only, no re-approval |
| Post-mortem JSON | `research/c008_post_mortem/*.json` (this sprint) |

## Disclaimer

Descriptive reconstruction only. C008/C009 remain **REJECT**. No strategy approved.
