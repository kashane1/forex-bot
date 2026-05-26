# Backtrader CAMPAIGN_015 RiskEngine & Fill Parity — Result

**Date:** 2026-05-26
**Branch:** `infra-backtrader-campaign-015-riskengine-and-fill-parity-001`
**Label:** `BT_PARITY_STILL_DIVERGED`

## Answers

### 1 · Did trade-count gap shrink from 532 vs 164?

**Yes.** 532 → **416** BT trades; gap vs bespoke 164 went from **+368** to **+252**
(−116 trades, −31.5% of prior excess).

### 2 · Did first divergence disappear?

**Expected yes** for the documented first divergence (`same_bar_adverse_stop` at
fold 0 / EUR_USD 2021-11-04T13:00). Parity mode removes entry-bar adverse stop.
Not re-traced bar-by-bar in this sprint.

### 3 · Did RiskEngine parity explain most extra BT trades?

**Partially.** RiskEngine parity rejected **145** signals on the CSV lane vs
**119** bespoke sqlite rejections — wiring works, but BT still executes **416**
vs **164** bespoke trades. Residual excess is not fully explained by rejection
gaps alone; spread-source and state-sequencing drift remain.

### 4 · New divergence classification?

**`SIGNAL_RULE_MISMATCH`** (unchanged label; magnitude reduced).

### 5 · Is Backtrader now good enough as a secondary verifier?

**Improved but not sufficient alone.** BT now mirrors bespoke entry-bar policy
and runs read-only RiskEngine gates, yet +153% trade-count drift persists.
Useful for directional checks; not a substitute for bespoke evidence.

### 6 · Does this change CAMPAIGN_015 approval status?

**No.** CAMPAIGN_015 remains unapproved; precommit gates unchanged.

### 7 · Recommended next step

**Debug remaining BT parity** (CSV vs sqlite spread alignment, session gate
timestamps, re-entry / position-state sequencing) **before** any bespoke fill-model
correction or H4 data collection rerun.

Secondary track: optional `infra-bespoke-fill-model-correction-001` if team
decides entry-bar adverse stop should match precommit literal reading.

## Rejection parity summary

| code | BT parity | bespoke |
|---|---:|---:|
| SPREAD_TOO_WIDE | 55 | 22 |
| SPREAD_TO_ATR | 63 | 78 |
| SESSION_BLOCKED | 27 | 10 |
| MARGIN_BUFFER | 0 | 9 |

## Remaining divergence

- All 56 fold×pair cells still BT ≥ bespoke; many cells +100% to +700%
- Side mix: BT 224L/192S vs bespoke 85L/79S (~2.5× scale)
- NZD_USD and AUD_USD largest pair-level drift

## Safety reaffirmed

- `configs/approved_strategies.yaml`: `approved: []`
- Paper / demo / live: **blocked**
