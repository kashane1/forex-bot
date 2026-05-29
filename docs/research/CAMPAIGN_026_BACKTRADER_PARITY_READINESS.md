# CAMPAIGN_026 — Backtrader parity readiness

**Recommendation: `DEFER_PARITY_REJECTED`.**

## Does any candidate deserve parity?

**No.** Backtrader parity is a **pre-promotion** check — it exists to confirm that a
train+validation-clean champion survives an independent, event-driven engine before any
approval-track step. CAMPAIGN_026 produced **no champion** (0/11 train-eligible;
`REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE`), validation did not run, and the family is
being rejected across all execution timeframes. There is nothing to build parity for.

Per the decision rule:
- no champion / rejected → **`DEFER_PARITY_REJECTED`** ← *this case*
- champion passes train+validation → would be `BUILD_PARITY_NEXT` (not reached)

## Risks that a future parity build would have to model (recorded for reuse)

If the Donchian + HTF idea (or any timeframe-sensitive strategy) is ever revived with a
genuinely new thesis, an event-driven parity build must faithfully reproduce:

- **M3/M15/M30 resampling alignment** — bucket-start timestamps, complete-bucket-only
  policy; an engine that bars-on-close differently, or fills incomplete buckets, will
  diverge from this vectorized simulator.
- **HTF context alignment** — last *completed* H1/H4M1/D1AGG bar via backward
  `merge_asof`; off-by-one (using the forming bar) injects lookahead.
- **`next_bar_open` modeling** — entry on the execution bar *after* the signal bar's
  close; many engines default to close-fill.
- **Same-bar stop/target ambiguity** — this simulator resolves adverse-first (stop
  wins); an engine using intrabar order or optimistic fills will overstate edge.
- **Trailing / channel exit behaviour** — breakeven→ATR-trail and Donchian-channel
  exits act on completed-bar closes with next-open fills; tick-level engines differ.
- **Spread / slippage / cost modeling** — `COST_BASE` deducts fixed-slippage + spread×
  multiplier per fill from PnL while exit *triggers* are cost-agnostic; a parity engine
  must match this convention (and ideally tighten it) to compare like-for-like.

## Decision

**Do not build parity.** No train/validation evidence justifies it. The risk list above
is preserved so a future, externally-motivated revival starts from a known parity spec
rather than rediscovering it.
