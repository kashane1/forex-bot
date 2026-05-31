# Forex Research — Future Opportunities

**Sprint:** `research-forex-strategy-search-archive-001` · Phase 4
**Type:** Opportunity catalog. **Not active work.** Documentation only.
**Date:** 2026-05-31

---

## Purpose

This document lists directions that *could* justify future research effort **outside**
the archived strategy-search programme. None are authorized, scheduled, or funded.
Each requires the reopen gates in `FOREX_STRATEGY_SEARCH_ARCHIVE_DECISION.md` §4
before any work begins.

---

## 1. FX futures research (extended)

**What:** Build on the additive CME FX-futures layer (`research/fx_futures/`) already
in-repo — deeper history, roll/basis studies, cross-currency futures RV, term-structure
of basis.

**Why interesting:** Financing wall removed; decades of EOD history; exchange volume
and centralized order book.

**Why not pursued now:** Carry — the strongest futures candidate — is non-predictive.
C1 intraday requires paid data; S4 is venue-independent and sub-cost. No frozen factor
survives the futures diagnostic.

**Unlock needed:** A **new factor hypothesis** with economic mechanism, not a re-test
of archived factors. Possibly: basis momentum, roll-yield timing with explicit
transaction model, or cross-futures RV with institutional cost assumptions.

**Risk:** Same market-efficiency ceiling that killed spot carry may apply to all
price-based futures signals at retail cost.

---

## 2. Different asset classes

**What:** Apply the research platform (lab, null gates, walk-forward harness, cost
models) to non-FX markets — e.g. equity index futures, Treasury futures, commodity
spread markets.

**Why interesting:** Different microstructure, cost structure, and participant mix;
potentially larger gross effects; deep free data (e.g. equity indices).

**Why not pursued now:** Effectively a **new project**. The FX programme's negative
results do not transfer, but the infrastructure patterns do.

**Unlock needed:** New project charter, new instrument registry, new cost model,
new economic thesis — not a restart of FX campaign numbering.

**Risk:** Starting fresh without the FX programme's falsification discipline would
repeat the same overfitting path.

---

## 3. Alternative datasets (retail-accessible)

**What:** Acquire and ingest datasets not used in the archived programme:

| Dataset | Unlocks | Availability |
|---------|---------|--------------|
| True tick / L2 FX | Microstructure, queue position, spread dynamics | Paid (IBKR, Databento, Refinitiv) |
| Options-implied vol / risk reversals | Forward-looking positioning proxy | Paid or delayed free |
| COT / positioning reports | Slow flow positioning | Free (weekly, lagged) |
| Economic surprise indices | Event-driven conditioning | Mixed free/paid |
| Multi-decade macro fundamentals | FX value (PPP, BEER, real rates) | FRED/IMF/OECD (partial free) |

**Why interesting:** Each unlocks decision variables the price-only M1/H4 corpus
could not test. H16/H03 microstructure fades failed partly because M1 mid is a
crude proxy for true microstructure.

**Why not pursued now:** Data acquisition sprints were evaluated and deferred in
favor of the futures carry diagnostic (higher information gain per dollar). That
diagnostic is now complete and null.

**Unlock needed:** Data-acquisition sprint (not a campaign) with provenance,
latency model, and pre-registered hypothesis before any factor screen.

---

## 4. Institutional datasets & venues

**What:** ECN tick data, prime-brokerage spreads, interbank streaming quotes,
central-limit-order-book depth.

**Why interesting:** Retail OANDA spreads (~1.6–1.7 pip active, 5–10 pip rollover)
may have defeated edges that survive at institutional cost (~0.1–0.3 pip). S4's
genuine no-arb reversion at ~10× inside the retail band might be tradable at
institutional cost — though staleness/latency constraints remain.

**Why not pursued now:** Gated behind unavailable access, cost, and latency modeling.
The programme correctly tested at the cost structure it could actually trade.

**Unlock needed:** Institutional data access + realistic latency model + explicit
statement that results are not actionable at retail cost (research-only finding).

**Risk:** Even at institutional cost, S4's staleness half-life (≤1 bar) may be
latency-defeated regardless of spread.

---

## 5. Market-microstructure research (academic lane)

**What:** Read-only studies of order-flow proxies, quote intensity, spread
dynamics, and adverse-selection measures — without building tradable strategies.

**Why interesting:** The programme's microstructure front gates (H16, H03) and
USD_JPY diagnostics consistently found direction null but sometimes found
descriptive post-entry structure. A pure research lane could contribute to
understanding without the pressure to find a tradable edge.

**Why not pursued now:** Without tick/L2 data, M1 mid proxies are insufficient.
The archived programme's conclusion is that microstructure *prediction* failed
on available data.

**Unlock needed:** Tick data + academic framing (publish findings, not approve
strategies).

---

## 6. Platform & tooling reuse (non-research)

**What:** Repurpose the mature infrastructure for non-trading purposes:

- Backtesting framework for education or other asset classes.
- Cost-model library for FX transaction analysis.
- Research-freeze pattern as a template for other bot projects.
- Postgres candle store as a general time-series backend.

**Why interesting:** High engineering value already sunk; no edge required.

**Why not pursued now:** Out of scope for the trading research programme; available
to any future effort without reopening strategy search.

---

## 7. Cross-cutting evaluation criteria

Any future opportunity should be scored before work begins:

| Criterion | Question |
|-----------|----------|
| New input? | Does it provide data, market, or thesis not exhausted in archive? |
| Mechanism? | Is there a stated economic reason before coding? |
| Cost realism? | Can effects survive at the venue's actual cost structure? |
| Latency? | Can the edge be captured without institutional speed? |
| Falsifiability? | Can matched nulls kill it cheaply? |
| Distinctness? | Does it avoid mapping to a closed lane (DO_NOT_REPEAT)? |
| Information gain? | Is expected learning high relative to prior art in archive? |

---

## 8. Explicitly deprioritized (lessons from archive)

These were considered during the programme and are **deprioritized** based on
evidence, not ignorance:

- Single-instrument directional/mean-reversion on any FX pair or cross.
- MTF indicator confluence entries (C1 family and descendants).
- Non-time-bar directional strategies without new tick data.
- Cross-sectional momentum on weekly rebalance (C016 pattern).
- Collinear RV spread best-of-N (C028 pattern).
- Vol-managed TSMOM on ~5y spot history (C031 pattern).
- Carry as a spot-predictive signal (spot and futures both null).
- Macro regime conditioning on single-cycle history.
- Exit/stop tweaks as rescue for entry-null strategies.

---

## 9. Cross-references

- Reopen gates: `FOREX_STRATEGY_SEARCH_ARCHIVE_DECISION.md` §4
- Closed lanes: `DO_NOT_REPEAT_LIST.md`
- Prior backlog: `FUTURE_RESEARCH_BACKLOG.md` (historical; superseded by this doc)
- Prior options memo: `POST_CARRY_STRATEGIC_OPTIONS.md`
- Platform assets: `FOREX_STRATEGY_SEARCH_FINAL_SUMMARY.md` §5
