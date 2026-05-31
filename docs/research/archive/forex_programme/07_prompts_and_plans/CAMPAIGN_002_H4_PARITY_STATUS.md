# CAMPAIGN_002 H4 — Independent-Engine Parity Status

**Date:** 2026-05-22 · **Updated by:** `infra-lean-parity-run-001` Phase 6
**Re-confirmed:** `infra-lean-parity-execute-001` Phase 6 — the
execute sprint checked whether local Lean CLI credentials
(`~/.lean/credentials`) were present and **found them absent**; per the
sprint's "do not prompt for, request, or create QC credentials" rule,
no execution proceeded. The blocker chain is identical to the prior
sprint and now also documented in
[`LEAN_PARITY_EXECUTE_BLOCKED.md`](LEAN_PARITY_EXECUTE_BLOCKED.md) with
the auth-specific detail and verbatim next-step commands.

> **SUPERSEDED for the LEAN path — QuantConnect/LEAN CLI execution is
> RETIRED for this project** (decision date 2026-05-22, branch
> `infra-retire-quantconnect-lean-001`). The free-tier QuantConnect
> account does not provide the API access required for the intended
> local LEAN CLI workflow, and a paid QuantConnect upgrade has been
> declined. **Do not create a QC account, do not run `lean login`, do
> not run `lean init`, do not run any LEAN backtest.** The
> independent-engine parity gap described below is **not** going to be
> closed by LEAN; the replacement direction is a free / local
> independent verifier — see
> [`FREE_LOCAL_PARITY_VERIFIER_PLAN.md`](FREE_LOCAL_PARITY_VERIFIER_PLAN.md)
> and the decision record in
> [`QUANTCONNECT_LEAN_RETIREMENT_DECISION.md`](QUANTCONNECT_LEAN_RETIREMENT_DECISION.md).
> The LEAN algorithm / mapping spec / harness artifacts referenced in
> this doc are preserved as **historical infrastructure evidence only.**
> CAMPAIGN_002 remains **REJECT** regardless of any parity work, LEAN
> or otherwise.

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
| Custom-engine reproduction (with RiskEngine) | **done — exact match** |
| No-RiskEngine bespoke reference | **done — 1,647 trades** |
| CAMPAIGN_002 → Lean mapping spec | **done** |
| Faithful Lean parity algorithm | **authored — not yet validated** |
| Parity comparison harness | **done — tested** |
| Lean parity backtest executed | **not run — blocked** |
| Independent-engine (Lean ↔ custom) comparison | **not yet verified** |

**Overall: parity is fully prepared on the bespoke side and the Lean
algorithm + harness are written. The single remaining gap is executing
the Lean backtest, which is blocked by a cloud-credential requirement
(below).**

## Seven-pair data status

The local real-OANDA practice H4 store holds the full seven-pair
CAMPAIGN_002 universe; the seven-pair data-quality audit found every
pair acceptable. The store's normalized candle hashes match the hashes
recorded in the committed CAMPAIGN_002 report — the data is provably the
same candles CAMPAIGN_002 used.

## Custom-engine reproduction status

Two bespoke references now exist:

- **With RiskEngine** — `backtests/diagnostics/custom_campaign_002_h4_parity.md`:
  an **exact** reproduction of the committed CAMPAIGN_002 report —
  1,032 trades, per-pair deltas of zero.
- **No RiskEngine** — `research/lean_parity/campaign_002_h4_bespoke_reference.json`:
  the strategy + engine mechanics in isolation (the engine's
  `risk_engine=None` parity path) — **1,647 trades**. This is the
  apples-to-apples reference for the Lean algorithm, which replicates
  the strategy + mechanics but not the bespoke RiskEngine (see
  `CAMPAIGN_002_LEAN_MAPPING_SPEC.md` §0).

## Lean algorithm implementation status

A faithful Lean algorithm is **authored** —
`research/lean_parity/algorithms/campaign_002_h4_baseline/main.py` — a
direct port of the strategy + engine mechanics from the mapping spec:
EMA(50/200) regime, Donchian(20) prior-bar breakout, ATR stop/trailing
stop, the exit precedence and time stop, `signal_bar_close` fills, and
0.25%-risk sizing, using Lean's own EMA / ATR indicators.

It is **not yet validated** — authored offline, never executed against
Lean. `docs/research/LEAN_ALGORITHM_IMPLEMENTATION_NOTES.md` documents
every approximation and the Lean-mechanics differences a first run is
expected to surface.

## Lean run status — RETIRED

The local Lean backtest **was not executed and will not be executed
under this project**. QuantConnect/LEAN CLI execution is retired
(decision date 2026-05-22) because the free-tier QuantConnect account
does not provide the API access required for the intended local LEAN
CLI workflow, and a paid QuantConnect upgrade has been declined. No
LEAN result exists, no LEAN comparison exists, and no further LEAN
authentication attempts are to be made. See
`QUANTCONNECT_LEAN_RETIREMENT_DECISION.md`. The historical "auth
absent" record is in `LEAN_PARITY_EXECUTE_BLOCKED.md` (also marked
superseded).

## Comparison result

**Not available** — no Lean result exists to compare. The comparison
harness `scripts/compare_lean_campaign_002_parity.py` is written and
tested and will run the moment a Lean `parity_summary.json` exists.

## What matched

- **Custom engine ↔ committed CAMPAIGN_002 report:** exact (1,032
  trades, zero per-pair deltas).
- **Re-fetched H4 data ↔ CAMPAIGN_002's recorded data hashes:** match.

## What remains unverified

- **The independent-engine cross-check.** No Lean (or other non-bespoke)
  engine has been run against the bespoke engine. The bespoke engine is
  internally reproducible and now has a faithful Lean algorithm + harness
  ready, but it has **not yet** been corroborated by an independent
  engine. That is the open item.

## Exact next step

The LEAN-based independent-engine parity path is **retired**. The
replacement direction is a free / local independent verifier — see
`FREE_LOCAL_PARITY_VERIFIER_PLAN.md` for candidate approaches and the
recommended plan. The free / local verifier will use the same
no-RiskEngine bespoke reference (1,647 trades) and the same seven-pair
H4 export bundle, and will reuse the divergence-classification framing
from `LEAN_PARITY_COMPARISON_METHOD.md`. Until the free / local
verifier is implemented and run, the bespoke engine remains internally
reproducible but not yet corroborated by an independent engine.

## What would count as successful parity

The Lean run, compared against the **no-RiskEngine** bespoke reference
(1,647 trades) within the tolerances in `LEAN_PARITY_COMPARISON_METHOD.md`:
trade count within ±5%, expectancy within ±0.03 R, return within
±0.5 pp per pair. A PASS corroborates the bespoke engine; a FAIL
localizes a parity-implementation bug or a real engine discrepancy —
never tuned away.

## Why this still does not approve a strategy

CAMPAIGN_002 closed **REJECT**. Parity verifies the engine that produced
that verdict, not the strategy. Even a full parity PASS would only mean
"two engines agree on the numbers" — and the numbers are a rejected
strategy's. `configs/approved_strategies.yaml` remains empty; every
order-capable loop still refuses. Nothing here approves a strategy or
lifts the research freeze.
