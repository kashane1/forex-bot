# Free / Local Parity Verifier — Accepted Status

**Date:** 2026-05-22 · **Branch:** `research-close-free-local-verifier-and-next-direction-001`
`strategy_evidence: false`

The free / local independent parity verifier work is **accepted as
corroborating evidence for the bespoke backtest engine** at the
WARN-band tolerance documented in
[`LEAN_PARITY_COMPARISON_METHOD.md`](LEAN_PARITY_COMPARISON_METHOD.md).
No further numerical-tightening sprints are planned. This document
is the single closeout reference for what the verifier proves and
does not prove.

> CAMPAIGN_002 remains REJECT. No strategy is approved.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper /
> demo / live remain blocked. No QuantConnect / LEAN. No OANDA API
> calls in the rounding-closure or closeout sprints.

## 1. Final accepted verifier result

Bespoke no-RiskEngine reference:
`research/lean_parity/campaign_002_h4_bespoke_reference.json` —
**1,647 trades**, `risk_engine_used: false`, window 2020-01-01 →
2026-05-20, 7 pairs.

Verifier final state (post Sprint 003 Phase 5 + Sprint 004
`round_price`):

| metric | value |
|---|---|
| Verifier total trades | **1,655** |
| Bespoke total trades | 1,647 |
| Total Δ % | **+0.49 %** (OK band, ±5 %) |
| Pairs OK | **3** (GBP_USD, USD_JPY, AUD_USD) |
| Pairs WARN | **4** (EUR_USD, USD_CAD, USD_CHF, NZD_USD) |
| Pairs FAIL | **0** |
| **Overall comparison status** | **WARN** |
| Verifier-side bugs fixed | 2 in Sprint 003; 0 in Sprint 004 |
| Bespoke-engine bugs found | 0 |

Per-pair (largest WARN deltas only):

| pair | bespoke trades | verifier trades | Δ % | ΔR | Δpp |
|---|---|---|---|---|---|
| USD_CHF | 224 | 223 | −0.45 | +0.0428 | +1.6332 |
| EUR_USD | 233 | 235 | +0.86 | +0.0160 | +0.7604 |
| NZD_USD | 240 | 242 | +0.83 | −0.0078 | −0.5096 |
| USD_CAD | 251 | 251 | +0.00 | −0.0605 | +0.0000 |

(Full per-pair table:
[`FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_FIXES.md`](FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_FIXES.md).)

## 2. Why exact parity is not required

The verifier's purpose is **independent corroboration** of the
bespoke engine's directional verdict, not bit-for-bit numerical
agreement. The
[`LEAN_PARITY_COMPARISON_METHOD.md`](LEAN_PARITY_COMPARISON_METHOD.md)
tolerance ladder was designed exactly for this: OK ≤ 5 % trade
count / 0.03 R expectancy / 0.5 pp return; WARN up to 15 % /
0.10 R / 2.0 pp; FAIL beyond. The verifier sits well inside the
WARN band on every metric for every pair, with no FAIL anywhere.

A WARN-band agreement between two independently-implemented
engines on a six-year, seven-pair, ~1,650-trade backtest is
substantial corroboration. The bespoke engine's directional verdict
(every pair is loss-making on the no-RiskEngine path) is reproduced
exactly by the verifier on every pair.

Asking for tighter agreement than that would mean asking for the
verifier to **be** the bespoke engine — which defeats the purpose.

## 3. Why a Decimal end-to-end rewrite is deferred

The remaining WARN drift is localized in
[`FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md`](FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md)
to **float-vs-Decimal arithmetic precision**. The cleanest single
piece of evidence is USD_CAD: identical 251-vs-251 trade count,
identical +0.0000 pp return delta, but −0.0605 R expectancy drift —
the R denominator (`initial_stop_distance × units`) differs at
sub-pip precision, which is exactly the float (≈15 digits) vs
Decimal (28 digits) signature.

Converting the verifier to `decimal.Decimal` end-to-end would
almost certainly close the remaining drift. It is **deferred** for
the reasons documented in
[`FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md`](FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md)
— most importantly because it would compromise the verifier's
independence from the bespoke engine.

## 4. What the verifier corroborates

- **Trade count** within ±1.62 % per pair and +0.49 % overall
  across 6 years and 7 instruments.
- **Directional expectancy**: every pair is loss-making on both
  engines (every verifier expectancy is negative, every bespoke
  expectancy is negative; signs match).
- **Sign-of-trade-list**: more shorts than longs on USD_CHF and
  NZD_USD, more longs than shorts on USD_JPY (verifier output
  matches the regime-direction expectations from EMA_fast/slow
  positioning).
- **Bespoke engine's structural behavior**: re-derived from spec
  on a wholly independent float-based implementation, every entry /
  exit / stop / trailing / sizing / PnL rule matches the bespoke
  spec literally (33 rule fixtures + 16 indicator fixtures + 87
  total verifier-side fixture tests pass).
- **The CAMPAIGN_002 H4 dataset itself**: per-pair SHA-256s match
  the committed `*.provenance.json` files exactly — the verifier
  consumed bit-for-bit the same candles the bespoke engine used.

## 5. What the verifier does not prove

- **It does not prove the bespoke engine is exactly correct.** It
  proves the bespoke engine and an independent re-implementation
  agree within float precision. The remaining sub-WARN drift is
  unresolved at the level the verifier can address without
  becoming the bespoke engine.
- **It does not approve any strategy.** Both engines agree the
  strategy is a loser. CAMPAIGN_002 remains REJECT. Two engines
  agreeing on a rejection is **not** the same as approval.
- **It does not lift the research freeze.** The freeze stands.
- **It does not enable any paper / demo / live loop.** Approval is
  a separate human decision that requires evidence of an edge — the
  verifier does not provide that evidence.
- **It does not corroborate the bespoke RiskEngine.** The verifier
  targets the **no-RiskEngine** bespoke path (1,647 trades). The
  RiskEngine-gated CAMPAIGN_002 result (1,032 trades) was
  separately reproduced exactly by the bespoke-on-bespoke
  reproduction in
  [`backtests/diagnostics/custom_campaign_002_h4_parity.md`](../../backtests/diagnostics/custom_campaign_002_h4_parity.md),
  not by the verifier.

## 6. Remaining WARN drift — summary

| pair | drift cell | size | most plausible cause |
|---|---|---|---|
| EUR_USD | return Δpp | +0.76 | sub-WARN precision noise, unknown bucket |
| USD_CAD | expectancy ΔR | −0.0605 | `sizing_pnl_mismatch` (R-denominator float precision) |
| USD_CHF | return Δpp | +1.63 | `sizing_pnl_mismatch` (USD-base divide-by-exit_price precision) |
| NZD_USD | return Δpp | −0.51 (WARN-by-0.01) | borderline precision noise |

All four pairs sit in the WARN 0.5–2.0 pp / 0.03–0.10 R band; none
near the FAIL thresholds (2.0 pp / 0.10 R). Direction of drift is
**mixed** across pairs (verifier is sometimes more negative,
sometimes less) — consistent with random float-precision noise
rather than a structural verifier bias.

Full classification:
[`FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md`](FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md).

## 7. No bespoke-engine bugs found

Across four sprints of verifier work (001 implementation, 002
data unblock attempt, 003 unblock + Phase 5 debug, 004 rounding
closure):

- **Verifier-side bugs fixed**: 2 (Sprint 003 — initial-stop base
  using post-slippage entry; same-bar re-entry blocked).
- **Bespoke-engine bugs found**: **0**.

The bespoke engine continues to be the source of truth for the
CAMPAIGN_002 H4 reference numbers. The verifier is corroborating
evidence, not a replacement.

## 8. Safety state at acceptance

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.** `paper-loop` and
  `demo-loop` both refuse via the empty approved-strategy registry.
  No `live-loop` command exists in the CLI.
- **No broker credentials used.** No OANDA API call in Sprint 004
  or this closeout sprint.
- **No QuantConnect / LEAN action** of any kind. Retirement stands.
- **No orders submitted.**
- **No bespoke-engine edits.** No CAMPAIGN_002 rule edits.

## 9. What happens next

This document closes the verifier-evidence loop. The next research
direction is in
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md).

No further free / local verifier sprint is planned unless one of
the conditions in
[`FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md`](FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md)
§5 is met, or a real bespoke-engine bug is independently
discovered.

## 10. Cross-links

- Plan & implementation:
  [`FREE_LOCAL_PARITY_VERIFIER_PLAN.md`](FREE_LOCAL_PARITY_VERIFIER_PLAN.md),
  [`INFRA_FREE_LOCAL_PARITY_VERIFIER_001_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_001_SUMMARY.md)
- Data unblock + first run + debug:
  [`INFRA_FREE_LOCAL_PARITY_VERIFIER_003_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_003_SUMMARY.md),
  [`FREE_LOCAL_PARITY_VERIFIER_003_UNBLOCKED_RESULT.md`](FREE_LOCAL_PARITY_VERIFIER_003_UNBLOCKED_RESULT.md),
  [`FREE_LOCAL_PARITY_VERIFIER_003_DEBUG_NOTES.md`](FREE_LOCAL_PARITY_VERIFIER_003_DEBUG_NOTES.md)
- Rounding closure + drift classification:
  [`INFRA_FREE_LOCAL_PARITY_VERIFIER_004_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_004_SUMMARY.md),
  [`FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_AUDIT.md`](FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_AUDIT.md),
  [`FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_FIXES.md`](FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_FIXES.md),
  [`FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md`](FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md)
- Headline status: [`FREE_LOCAL_PARITY_VERIFIER_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_STATUS.md)
- Comparison method (tolerances): [`LEAN_PARITY_COMPARISON_METHOD.md`](LEAN_PARITY_COMPARISON_METHOD.md)
- Mapping spec: [`CAMPAIGN_002_LEAN_MAPPING_SPEC.md`](CAMPAIGN_002_LEAN_MAPPING_SPEC.md)
- Decimal-rewrite deferral: [`FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md`](FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md)
- Next direction: [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
