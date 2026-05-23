# Free / Local Parity Verifier — Decimal Precision Rewrite: DEFERRED

**Date:** 2026-05-22 · **Branch:** `research-close-free-local-verifier-and-next-direction-001`
`strategy_evidence: false`

A future sprint to convert the verifier from `float` to
`decimal.Decimal` end-to-end is **explicitly deferred**. This
document records exactly what such a rewrite would do, why it might
move WARN pairs to OK, why it is not worth doing now, how it would
compromise the verifier's independence, and the conditions under
which the deferral should be reopened.

> CAMPAIGN_002 remains REJECT regardless of any future verifier
> work. The free / local verifier's purpose is corroboration of
> the bespoke engine, not strategy approval.

## 1. What a Decimal rewrite would do

Convert every numeric path in
`research/parity_verifier/` from Python `float` to
`decimal.Decimal`:

- **Indicators** (`indicators.py`): EMA recursion, ATR Wilder
  smoothing, Donchian min/max all in Decimal.
- **Rules** (`rules.py`): initial-stop subtraction, trailing-stop
  arithmetic, fill-price slippage, sizing (`risk_amount /
  (stop_distance_pips × pip_value)`), PnL conversion
  (`gross_quote / exit_price` for USD-base).
- **Event loop** (`event_loop.py`): NAV compounding, bars_held,
  stop-pierce comparisons all on Decimal.
- **Models** (`models.py`): `Bar` / `Trade` / `PairResult` fields
  carry `Decimal` instead of `float` (with a small custom JSON
  encoder for `parity_summary.json`).

Estimated change scope: ~300 lines across `research/parity_verifier/`,
plus updated fixture expected values in
`tests/research/test_parity_verifier_*.py`. Implementation is
straightforward — every place the verifier currently does `a + b`
with floats becomes `a + b` with Decimals; no algorithmic change.

## 2. Why it might improve numerical agreement

The remaining WARN drift (4 / 7 pairs) is localized to
float-vs-Decimal arithmetic precision (see
[`FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md`](FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md)).
The cleanest evidence is USD_CAD: identical 251 trade count,
identical +0.0000 pp return, but −0.0605 R expectancy — the R
denominator differs at sub-pip precision (float ≈ 15 digits,
Decimal default 28 digits).

A Decimal rewrite would:

- Likely close USD_CAD's −0.06 R drift (R denominator becomes
  exact-match to bespoke).
- Likely close USD_CHF's +1.6 pp drift (USD-base divide-by-exit
  precision becomes exact).
- Likely move EUR_USD (+0.76 pp) and NZD_USD (−0.51 pp) inside
  the OK band as well.
- Probably bring overall comparison status from **WARN → OK** on
  all 7 pairs.

The numerical agreement would tighten from "two engines built from
the spec agree within ±1.62 % per pair" to "two engines built from
the spec agree exactly".

## 3. Why it is not worth doing now

Three reasons, in order of importance:

### 3.1 Diminishing returns vs research goals

The verifier's job was to **corroborate the bespoke engine's
directional verdict on CAMPAIGN_002**. That job is done:

- Both engines agree every CAMPAIGN_002 H4 pair is loss-making.
- CAMPAIGN_002 stays REJECT under either measurement.
- The bespoke engine is confirmed not to be the source of the
  REJECT — the strategy itself is.

Tightening the comparison from WARN to OK changes **nothing**
about the strategic verdict. CAMPAIGN_002 would still be REJECT.
No paper / demo / live decision hinges on whether USD_CHF's return
delta is +1.6 pp or +0.0 pp.

The research-direction question (what to try next) has moved on.
Continuing to polish the verifier numerically is "yak-shaving" at
this point — work that feels productive but doesn't change the
outcome.

### 3.2 Loss of verifier independence

The verifier's value comes from being **structurally independent**
from the bespoke engine: a separate package with a separate import
path, separate primitives, separate arithmetic conventions.

The bespoke engine uses `Decimal` for everything. If the verifier
also uses `Decimal` for everything **with the same precision
contexts**, the two implementations share the dominant arithmetic
property that drives sub-WARN drift. Their agreement then is no
longer "two independent engines reach the same answer" but "two
engines that use the same arithmetic library and the same precision
context reach the same answer" — which is much weaker corroboration
of the bespoke engine.

A Decimal-converted verifier wouldn't be **the bespoke engine**
(the rule code is still re-derived independently), but it would
share the bespoke's specific numerical-precision path. The current
float-based verifier disagrees with the bespoke engine by sub-pip
amounts and **agrees on the directional verdict** — that's
stronger corroboration than a Decimal rewrite would provide.

### 3.3 Opportunity cost

The same engineering time spent on Decimal precision would buy more
research value if invested in any of the candidate next-research
directions in
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md).
Closing the WARN drift gives ~0% additional knowledge about whether
a profitable strategy exists; a new strategy family / regime filter
/ portfolio-level investigation gives potentially substantial new
knowledge.

## 4. How a Decimal rewrite would compromise independence

| dimension | float verifier (now) | Decimal verifier (hypothetical) |
|---|---|---|
| Module tree | separate `research/parity_verifier/` package | same separate package |
| Import boundary | grep-enforced no-`forex_bot` import rail | same |
| Indicator definitions | re-derived from canonical formulas | re-derived, but using **the same numerical-precision library as bespoke** |
| Bar loop | independent control flow | independent control flow |
| Stop arithmetic | float `entry - distance`, no rounding (except initial-stop `round_price`) | Decimal `entry - distance`, same precision context as bespoke |
| PnL conversion | float divide for USD-base; sub-pip drift accumulates | Decimal divide for USD-base; matches bespoke exactly |
| What disagreement implies | "two implementations using different precision conventions agree on the directional verdict" — strong corroboration | "two implementations using **the same** precision convention agree exactly" — weaker corroboration |

The third row's parenthetical is the crux. Decimal precision is not
just a representation choice; it's a **shared numerical-precision
context** with `getcontext().prec = 28` by default. Two engines
using the same Decimal context that disagree by 0.0 R have shown
only that their algebraic structure matches — they have *not*
shown that the algebra is correct, because both use the same
arithmetic library.

The float-based verifier's WARN-band agreement with the bespoke
Decimal engine is **better evidence** that the bespoke engine is
correct, because the verifier's float arithmetic could plausibly
expose a bespoke bug (large bug → large divergence; observed
divergence is sub-pp → no large bespoke bug). A Decimal verifier
that matches bespoke perfectly tells us less, not more.

## 5. Conditions that would justify reopening

The deferral should be reopened only if **at least one** of the
following is met:

1. **A real bespoke-engine bug is independently discovered**
   (outside the verifier) that requires verifier re-verification at
   tighter precision to confirm the fix.
2. **A downstream consumer specifically requires tighter
   verifier-vs-bespoke agreement** (e.g. a regulatory or audit
   process that mandates exact-match parity, not WARN-band). No
   such consumer exists today.
3. **The bespoke engine itself is rewritten** to use a different
   precision context (e.g. extended-precision Decimal or
   arbitrary-precision rationals), making the verifier-vs-bespoke
   comparison structurally different from the current state.
4. **A new campaign produces a result whose interpretation hinges
   on sub-pp numerical agreement** between verifier and bespoke.
   This would be unusual (campaign verdicts are normally driven by
   directional expectancy and pre-committed gates, not by sub-pp
   precision), but possible.

If none of those conditions is met, the deferral stands and the
verifier should be considered closed.

## 6. Explicit non-need for CAMPAIGN_002

CAMPAIGN_002 is REJECT under both engines and both stop conventions
(with-RiskEngine 1,032 trades, no-RiskEngine 1,647 trades). The
bespoke engine has been corroborated by:

- An exact custom-engine reproduction with the RiskEngine
  (`backtests/diagnostics/custom_campaign_002_h4_parity.md`, 1,032
  trades, zero per-pair deltas).
- A WARN-band independent verifier on the no-RiskEngine path (this
  sprint's accepted result).

No further verifier work is required to confirm CAMPAIGN_002's
REJECT verdict. A Decimal rewrite would not change the verdict and
is therefore not needed for CAMPAIGN_002 purposes.

## 7. Safety statement

- This document does not approve any strategy.
- `configs/approved_strategies.yaml` remains `approved: []`.
- CAMPAIGN_002 remains REJECT.
- Paper / demo / live remain blocked.
- No bespoke-engine edit is proposed.
- No CAMPAIGN_002 rule edit is proposed.
- No tuning is proposed.

## 8. Cross-links

- Closeout reference:
  [`FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md)
- Drift classification:
  [`FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md`](FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md)
- Tolerance ladder:
  [`LEAN_PARITY_COMPARISON_METHOD.md`](LEAN_PARITY_COMPARISON_METHOD.md)
- Next research direction:
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
