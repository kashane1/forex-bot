# Remaining Untested Mechanisms After Carry (Phase 2)

**Sprint:** `research-programme-direction-after-carry-001`
**Type:** Documentation only.
**Date:** 2026-05-31
**Purpose:** Determine what genuinely remains untested after the in-repo factor search is exhausted, so the direction decision is made against a real opportunity set rather than a vague sense of "more out there."

---

## Framing

A mechanism only "remains" if it is **both** (a) plausibly able to produce a tradable edge and (b) not already foreclosed by an existing verdict. "We could re-tune X" is **not** a remaining mechanism — re-tuning a closed family is explicitly out of scope and violates the freeze discipline. The bar is: *a genuinely new source of edge, or a genuinely new market/cost structure in which a known effect could survive.*

The programme's terminal cause is **cost**. So the most important axis for any remaining mechanism is: *does it change the cost structure, or does it just present the same cost wall with a new label?*

---

## The five mechanisms the brief asks us to evaluate

### 1. Broker-financing realism

**What it is:** ingesting *real OANDA (or comparable broker) per-night financing rates* rather than the FRED interbank proxy, to model carry/overnight-hold strategies at true net cost.

**Status:** UNTESTED as data, but the **answer is already known by inference.** C031 measured broker financing at ≈4× spread cost; the carry validation showed the gross premium is mechanical and single-name. Real financing would *deepen* the cost wall, not relieve it. Ingesting it would let us state the net carry number precisely — but we already know its sign (negative) and we already declined this in the carry remaining-mechanisms doc.

**Could it produce an edge?** No. It can only confirm a loss more precisely. **Foreclosed by inference.**

---

### 2. Futures FX (CME / centralized order book)

**What it is:** exchange-traded FX futures (6E, 6J, 6B, etc.) instead of OTC spot. Centralized order book, tighter effective spreads, **no per-night financing leg** (cost is in the basis/roll, paid quarterly not nightly), decades of history, and real exchange volume (not a tick-count proxy).

**Status:** GENUINELY UNTESTED. This is the single mechanism that **changes the cost structure** rather than relabeling it. The two things that defeated the spot programme — the two-sided spread on every round trip and the ≈4× financing squeeze on held positions — are both structurally smaller or absent on futures.

**Could it produce an edge?** Plausibly. Not guaranteed (futures are also liquid and crowded; the basis is its own cost; roll management is non-trivial), but it is the *only* venue where a known-real-but-cost-defeated effect (e.g. C1-style confluence, S4 relative-value, momentum) could plausibly survive net of cost. It also unlocks deep history (decades vs ~6.4y), addressing the slow-signal power limit.

**This is the strongest remaining mechanism.**

---

### 3. Institutional-cost venues (ECN / prime / true tick + L2)

**What it is:** trading the *same* spot FX market but at institutional cost — ECN/prime-broker spreads (fractions of a pip), commission-based pricing, and access to true tick + Level-2 depth (which the corpus has never had).

**Status:** UNTESTED in this repo. Two distinct sub-cases:
- **Lower spreads (ECN/prime):** could narrow the cost wall enough that a sub-cost effect (S4's ~0.5bp no-arb reversion, ~10× inside the retail band) becomes marginally tradable. But it requires a funded institutional account and a live data feed — outside the research-platform scope and not currently available.
- **True tick + L2 microstructure:** a genuinely new *information* source (order-book imbalance, queue dynamics) the corpus has never tested. This is real new edge surface, but it requires a tick/L2 data subscription and a latency-aware backtest the platform doesn't model.

**Could it produce an edge?** Possibly, but gated behind data/access the project does not have and a non-trivial infra build (latency modeling, L2 reconstruction). Higher cost, higher uncertainty than futures.

---

### 4. Alternative datasets (longer history, fundamentals, positioning, alt-data)

**What it is:** datasets the repo lacks that could power *different* mechanisms — multi-decade history (for value/PPP/REER mean reversion), CFTC positioning, central-bank calendars, options-implied vol/risk-reversals, order-flow/alt-data.

**Status:** UNTESTED. These enable mechanisms the corpus literally cannot express today (e.g. FX *value* needs multi-decade fundamentals; positioning-based contrarian needs CFTC). 

**Could it produce an edge?** Each is a separate research programme with its own data acquisition, its own cost model, and no guarantee of surviving cost. Value in particular is slow (multi-year holds) and therefore maximally exposed to financing — the exact wall that killed carry. **Promising in principle, expensive and slow in practice; not the cheapest next step.**

---

### 5. Alternative asset classes (crypto, equities/ETFs, metals, rates)

**What it is:** leaving FX entirely for a market with a different microstructure/regime — crypto (24/7, different participants, periodic dislocations), equity index/ETFs (commission+spread, deep history, well-studied factors), metals (XAU), or rates futures.

**Status:** UNTESTED. These are **different markets**, each requiring new ingestion, a new cost model, and a new edge thesis. Crypto is the most structurally-different (retail-heavy, less efficient historically) but also the most regime-unstable and the most crowded by now. Equities have the richest documented factor literature but are the most studied/arbitraged.

**Could it produce an edge?** Each is plausible but amounts to **starting a new project**. High implementation cost, and the FX-specific infrastructure (cost models, factor lab, non-time bars) transfers only partially.

---

## Cross-cutting view: which mechanisms actually change the binding constraint?

| Mechanism | New edge source? | Changes cost structure? | Available now? | Verdict |
|-----------|------------------|-------------------------|----------------|---------|
| Broker-financing realism | No | Worsens it | Yes (ingest) | Foreclosed — confirms a loss |
| **Futures FX (CME)** | Reuses known effects | **YES** (no nightly financing, tighter, deep history) | Data ingestable | **Strongest remaining** |
| Institutional ECN/L2 | Yes (L2 info) | Narrows it | No (needs feed/account) | Gated, expensive |
| Alternative datasets | Yes (value/positioning) | Neutral; value worsens (slow) | No (needs data) | Promising, slow, costly |
| Alternative asset classes | Yes | Different wall | No (new project) | New programme |

---

## Conclusion

**Genuinely remaining, cost-relevant, near-term-testable: one — FX futures (CME).** It is the only mechanism that attacks the programme's actual binding constraint (cost) rather than relabeling it, while reusing the project's mature infrastructure (factor lab, null benchmarks, cost-model framework, non-time bars) and the strategy intuitions already developed.

Everything else is either **foreclosed by inference** (broker financing), **gated behind unavailable data/access** (institutional venues, alt-datasets), or **a new project** (other asset classes). Those remain valid future directions but are not the cheapest, highest-information next step.

This sets up the strategic-options scoring in Phase 3.
