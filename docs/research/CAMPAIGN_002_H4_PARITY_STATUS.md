# CAMPAIGN_002 H4 — Independent-Engine Parity Status

**Date:** 2026-05-22 · **Branch:** `infra-lean-parity-001`

A human-readable status of independent-engine parity for the
CAMPAIGN_002 H4 `trend_following` baseline. `strategy_evidence: false` —
parity verifies the *measurement instrument* (the bespoke backtest
engine); it cannot and does not approve a strategy. **CAMPAIGN_002 is
REJECT and stays REJECT** regardless of any parity outcome.

## Parity readiness — summary

| component | status |
|---|---|
| Seven-pair H4 data (CAMPAIGN_002 universe) | **complete** |
| Seven-pair Lean export bundle | **complete** |
| Custom-engine CAMPAIGN_002 H4 reproduction | **done — exact match** |
| Lean CLI installed locally | **done** (isolated venv) |
| Lean parity backtest executed | **not yet — blocked** |
| Independent-engine (Lean ↔ custom) comparison | **not yet verified** |

**Overall: parity is data- and custom-engine-ready. The remaining gap
is the Lean side — a faithful Lean algorithm and a local Lean run.**

## Seven-pair data status

The local real-OANDA practice H4 store now holds the **full seven-pair
CAMPAIGN_002 universe**: EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD,
USD_CHF, NZD_USD — 2020-01-01 → 2026-05-19, ~9,931 completed H4 candles
each (NZD_USD 9,935). The seven-pair data-quality audit
(`OANDA_H4_DATA_QUALITY_AUDIT_7PAIR.md`) found every pair acceptable:
0 incomplete candles, 0 duplicates, full bid/ask coverage, only the
expected weekend / holiday gaps.

**Strong signal:** the freshly-rehydrated store's normalized candle
hashes **match the hashes recorded in the committed CAMPAIGN_002 report**
(`backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md`) — e.g. EUR_USD
`f5d1d1b19302…`, USD_JPY `64836ea0f08e…`, NZD_USD `c8724ce78e4c…`. The
re-fetched data is provably the **same candles** CAMPAIGN_002 used.

## Custom-engine reproduction status

`scripts/run_custom_campaign_002_h4_parity.py` re-ran the CAMPAIGN_002
H4 baseline on the bespoke engine, the committed campaign config, and
the seven-pair store, with CAMPAIGN_002's fill timing
(`signal_bar_close`) and the RiskEngine wired in.

**Result: an exact match to the committed CAMPAIGN_002 report** — all
seven pairs identical on trade count and expectancy R, 1,032 total
trades vs 1,032 committed (Δ +0). Full table:
`backtests/diagnostics/custom_campaign_002_h4_parity.md`.

The custom-engine side of the parity is therefore **reproducible and
hash-pinned** — a future Lean run has a committed reference to compare
against.

## Lean export status

The seven-pair CAMPAIGN_002 H4 Lean export bundle is **complete**:
`research/lean_parity/exports/campaign_002_h4/` carries seven
`<INST>_H4_lean.csv` files (gitignored — bulky) and seven committed
`*_H4_lean.provenance.json` sidecars, plus the `EXPORT_MANIFEST.md` and
the authoritative `lean_parity_config.json`. 69,522 candles total.

## Lean local run status

**Not run — blocked.** The `lean` CLI (1.0.225) is installed in an
isolated venv and Docker is present, but no Lean parity backtest was
executed and no result was fabricated. The blocker is documented in
`LEAN_PARITY_CAMPAIGN_002_BLOCKED.md`:

1. **No faithful Lean algorithm.** `research/lean_parity/campaign_002_h4_spec.md`
   is a spec + skeleton; the signal / exit / sizing / custom-data logic
   is unwritten. A faithful reimplementation must be authored and its
   faithfulness reviewed before any Lean number is trustworthy.
2. The `quantconnect/lean` Docker engine image is not yet pulled.

## What matched

- **Custom engine ↔ committed CAMPAIGN_002 report:** exact — every pair,
  trade count and expectancy R, Δ +0 / Δ ±0.000.
- **Re-fetched H4 data ↔ CAMPAIGN_002's recorded data hashes:** match —
  the store holds the identical candles.

## What remains unverified

- **The independent-engine cross-check.** No Lean (or any non-bespoke
  engine) run has been compared against the custom engine. The bespoke
  engine is internally reproducible, but it has **not yet** been
  corroborated by an independent implementation. That is the open item.

## Exact next step

Author and run the Lean side (a deliberate, review-gated task):

```bash
# Lean CLI in a dedicated venv:
python3 -m venv ~/lean-cli-venv && ~/lean-cli-venv/bin/pip install lean

# Lean workspace, outside this repo:
cd ~/scratch && ~/lean-cli-venv/bin/lean init

# Author a FAITHFUL trend_following_c002_parity.py from the skeleton in
# research/lean_parity/campaign_002_h4_spec.md, using the authoritative
# params in research/lean_parity/lean_parity_config.json and consuming
# the exported <INST>_H4_lean.csv as custom data. Review it for
# faithfulness before trusting any number.

~/lean-cli-venv/bin/lean backtest "TrendFollowingC002Parity"
# → capture into research/lean_parity/results/campaign_002_h4/ and
#   write docs/research/LEAN_PARITY_CAMPAIGN_002_RESULT.md.
```

## What would count as successful parity

Comparing the Lean run against the custom-engine reproduction
(`custom_campaign_002_h4_parity.md`) and the committed CAMPAIGN_002
report, within the tolerances in `LEAN_PARITY_EXECUTION_GUIDE.md` §4–5:

- ≥ 95% of trade entries on the **same bar**;
- trade count within **±5%**, total return within **±0.5 pp**,
  expectancy within **±0.03 R**;
- both engines read the **same verdict — REJECT**.

A PASS corroborates the bespoke engine. A FAIL localizes a bespoke-engine
bug to fix — never tuned away, never reported as a strategy result.

## Why this still does not approve a strategy

CAMPAIGN_002 closed **REJECT** in Research Marathon 001. Parity is
verification of the engine that produced that verdict, not of the
strategy. A parity PASS would only mean "the bespoke engine measured
correctly"; the thing it measured is still a rejected strategy.
`configs/approved_strategies.yaml` remains empty; every order-capable
loop still refuses. Nothing in this status, and nothing in any parity
result derived from it, approves a strategy or lifts the research
freeze.
