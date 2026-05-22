# Lean Parity — CAMPAIGN_002 H4 dry run BLOCKED

**Date:** 2026-05-22 · **Branch:** `infra-lean-parity-001` · Phase 4

The local Lean parity **dry run for CAMPAIGN_002 H4 was not executed.**
No Lean result was produced and **none was fabricated** — there is no
`docs/research/LEAN_PARITY_CAMPAIGN_002_RESULT.md` and no
`research/lean_parity/results/campaign_002_h4/`; those exist only after
a real, faithful local run.

This is an honest blocker, not a skipped phase. CAMPAIGN_002 remains
**REJECT** regardless; nothing here approves a strategy.

## What is in place

The Lean side is now substantially **ready**:

- **Lean CLI installed** — `lean 1.0.225` in an isolated venv
  (`infra-lean-parity-001` Phase 3; see `LEAN_PARITY_LOCAL_STATUS.md`).
- **Docker present** — Docker 29.1.3.
- **Seven-pair CAMPAIGN_002 H4 data** — the local store and the complete
  Lean export bundle (`research/lean_parity/exports/campaign_002_h4/`,
  Phases 1–2).
- **Authoritative parity config** — `research/lean_parity/lean_parity_config.json`.
- **Custom-engine reference** — the bespoke engine's CAMPAIGN_002 H4
  baseline, reproduced side-by-side in Phase 5
  (`backtests/diagnostics/custom_campaign_002_h4_parity.md`).

## The blocker

A Lean parity *result* is only meaningful if the Lean algorithm is a
**verified-faithful** reimplementation of the CAMPAIGN_002 H4
`trend_following` baseline. Two things stand between "Lean CLI
installed" and "trustworthy parity result":

1. **No faithful Lean algorithm exists.** `research/lean_parity/campaign_002_h4_spec.md`
   is a **spec with a skeleton** — its `OnData` body is entirely
   `# TODO`: the Donchian(20) breakout, the EMA(50/200) regime gate, the
   `min_atr_pips` floor, the three exits (2.0×ATR hard stop, 2.0×ATR
   trailing stop, 240-bar time stop) with the bespoke same-bar exit
   precedence, the 0.25%-risk sizing, and the custom-data class for the
   exported CSV are all unwritten. Authoring this **faithfully** — and
   verifying its faithfulness — is a deliberate, review-gated
   engineering task. A non-faithful algorithm produces a divergence
   that reflects an authoring error, not a custom-engine bug; reporting
   such numbers as a parity result would be a misleading "result",
   which this sprint forbids ("do not fake results").

2. **The `quantconnect/lean` Docker engine image is not pulled** — a
   multi-GB download performed on the first `lean backtest`. Mechanical,
   but not yet done.

This phase deliberately does **not** rush a Lean algorithm to produce
numbers. A parity comparison is verification of the *measurement
instrument*; an unverified instrument is worse than none.

## Exact next steps (deliberate human task)

```bash
# 1. Lean CLI — already installable; for a persistent setup:
python3 -m venv ~/lean-cli-venv && ~/lean-cli-venv/bin/pip install lean

# 2. Lean workspace, outside this repo's package tree:
cd ~/some/scratch/dir && ~/lean-cli-venv/bin/lean init

# 3. Author a FAITHFUL trend_following_c002_parity.py from the skeleton
#    in research/lean_parity/campaign_002_h4_spec.md. Port the logic
#    directly from src/forex_bot/strategies/trend_following.py and the
#    bespoke engine (src/forex_bot/backtesting/), using the authoritative
#    parameters in research/lean_parity/lean_parity_config.json
#    (atr_stop_multiple 2.0, max_bars_in_trade 240, min_atr_pips {}).
#    Consume the exported <INST>_H4_lean.csv as Lean custom data,
#    preserving the 17:00-NY-aligned open timestamps. Have the
#    reimplementation reviewed for faithfulness before trusting it.

# 4. Run the local backtest (pulls the quantconnect/lean image once):
~/lean-cli-venv/bin/lean backtest "TrendFollowingC002Parity"

# 5. Capture results into research/lean_parity/results/campaign_002_h4/
#    and write docs/research/LEAN_PARITY_CAMPAIGN_002_RESULT.md, comparing
#    against the Phase 5 custom-engine reproduction
#    (backtests/diagnostics/custom_campaign_002_h4_parity.md) and the
#    committed CAMPAIGN_002 report, using the tolerances in
#    docs/research/LEAN_PARITY_EXECUTION_GUIDE.md §4-5.
```

## What still does NOT require any of this

- The seven-pair data and Lean export bundle are complete and
  hash-pinned (Phases 1–2).
- The custom-engine side of the parity is reproducible now (Phase 5).
- The parity *readiness* status is captured in
  `docs/research/CAMPAIGN_002_H4_PARITY_STATUS.md` (Phase 6).

## Safety

No QuantConnect cloud, no paid tier, no brokerage connection, no live
trading. The Lean CLI was installed in an isolated venv that cannot
affect the forex-bot environment. CAMPAIGN_002 stays REJECT;
`strategy_evidence: false`; nothing here approves a strategy.
