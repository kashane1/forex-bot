# FX Futures Data-Source Feasibility (Phase 2)

**Sprint:** `research-fx-futures-venue-and-diagnostic-001`
**Type:** Documentation only. No data fetched; no broker/vendor API called.
**Date:** 2026-05-31
**Purpose:** Determine whether the FX-futures diagnostic can be fed from free/local data with adequate coverage and acceptable licensing/integration cost — broken down by the resolution each frozen factor actually requires.

> No credentials are used and no data is downloaded in this sprint. The availability claims below describe the *generally known* state of public futures data and must be re-confirmed at ingestion time. Any vendor key, if ever used, must never be committed (per the standing freeze/secret-scan discipline).

---

## 1. The decisive framing: resolution required per frozen factor

A futures diagnostic is only as feasible as the *data resolution the frozen factor needs.* The three factors differ enormously:

| Factor | Frozen definition resolution | Horizon | Data resolution required |
|--------|------------------------------|---------|--------------------------|
| **Carry** | Month-end cross-sectional rank, 1/3/6/12-month horizons | Monthly | **EOD daily is more than sufficient** |
| **C1** | H4 + H1 + M15 confluence fade, 30–60 min reversion | Intraday HTF | **Intraday (≥ M15), multi-year** |
| **S4** | M5 triangular no-arb residual, ~0.5 bp, ≤5-min / ≤1-bar half-life | Sub-5-min | **Synchronized intraday/tick across legs + latency model** |

This single table determines the verdict: feasibility is **high for carry, partial for C1, effectively nil (on free/local) for S4.**

---

## 2. Candidate data sources

| Source | Cost | Resolution | History depth | Redistribution / licensing | Integration |
|--------|------|-----------|---------------|----------------------------|-------------|
| **Stooq** | Free | EOD daily (continuous + individual) | Decades for FX futures | Personal/research use; no redistribution | Low (CSV, same as cross ingest) |
| **Yahoo Finance** (`6E=F`, `6J=F`, …) | Free | Daily; hourly ≤ ~730 d; 1-min ≤ ~60 d | Daily: long; intraday: **shallow** | ToS restricts redistribution; local research OK | Low (daily) / Low-Med (shallow intraday) |
| **Nasdaq Data Link / Quandl (CHRIS/Wiki continuous)** | Was free, **largely retired/deprecated** | EOD | Historical | Mostly paid now | Low if available; **unreliable** |
| **Barchart (free tier / ondemand)** | Free tier (limited) / paid | EOD + delayed intraday | Limited on free | Restrictive on free tier | Medium |
| **Interactive Brokers API** | Account-gated (~free with account) | Intraday incl. minutes | Good intraday (years), rate-limited | Account ToS; non-redistribution | Medium-High (account, pacing) |
| **FirstRate Data / Kibot / TickData** | Paid | 1-min / tick | Deep (≈2008+ for 1-min) | Licensed; non-redistribution | Medium |
| **Databento (CME)** | Paid (trial credits) | MBO/MBP/tick | Modern (≈2017+ for full depth) | Licensed | Medium-High |
| **Norgate Data** | Paid (subscription) | EOD (excellent roll/adjust) | Deep, clean continuous | Licensed | Low-Med (built for this) |
| **CME DataMine** | Paid (official) | Tick/EOD | Authoritative, deep | Official CME license | High |

---

## 3. Coverage findings by factor

### Carry — **FEASIBLE on free/local EOD data, deep history**
- CME FX futures have decades of EOD history (CME launched FX futures in 1972; EUR from 1999, legacy DEM before; JPY/GBP/CHF/CAD/AUD into the 1970s–80s). Free EOD continuous series (Stooq / Yahoo) comfortably cover the modern floating-rate era.
- Carry's monthly cross-sectional design needs only month-end levels per currency → **EOD daily is ample**, and free sources provide *more* history than the spot corpus's ~6.4 y, directly addressing the carry power limit.
- **The basis/roll** (which *is* futures carry) is observable from the front-vs-next quarterly prices in the same free EOD feed → the structurally cleanest part of the whole diagnostic.
- **Verdict: carry is fully fundable from free/local data.**

### C1 — **PARTIALLY FEASIBLE; gated behind paid or account-gated intraday**
- C1 needs M15/H1/H4 bars over a multi-year window. **Free intraday is too shallow** (Yahoo hourly ≈ 730 days; 1-min ≈ 60 days) to test a multi-year HTF confluence factor.
- Options: (a) IBKR API (account-gated, years of minute data, pacing limits), or (b) paid 1-min vendor (FirstRate/Kibot, ≈2008+). Both are *obtainable* but neither is "free/local."
- A **reduced C1 test on EOD-derived HTF** is not faithful: C1 is intrinsically an intraday-confluence factor; collapsing it to daily would *alter the definition*, which is forbidden.
- **Verdict: C1 is feasible only with a paid/account intraday source; not on free/local data without changing its definition.**

### S4 — **NOT FEASIBLE on free/local data; arguably not a futures research question at all**
- S4 lives at M5 with ~0.5 bp residuals and ≤1-bar (≤5-min) half-lives. Testing it in futures requires **synchronized intraday/tick across all triangular legs** plus a **latency/queue model**. Free/local data cannot supply this; only paid tick/MBP (Databento/CME DataMine) plus a microstructure backtest could.
- More fundamentally: sub-bp triangular no-arbitrage in listed futures is an **HFT/colocation domain**, not an EOD/HTF research domain. The staleness/latency constraint that bounded S4 in spot is **venue-independent and would bind at least as hard in futures.** A tighter spread does not fix a ≤1-bar half-life.
- **Verdict: S4 cannot be meaningfully tested as a futures diagnostic on free/local data, and the venue change does not address its binding constraint.**

---

## 4. Licensing constraints (summary)

- **EOD daily** from Stooq/Yahoo: usable for *internal, non-redistributed* research. This sprint and a carry-focused diagnostic stay within that.
- **Intraday/tick** (IBKR, FirstRate, Databento, CME DataMine): licensed, non-redistribution, some account-gated. Acceptable for internal research under their ToS, but **not free** and not "local" in the sense the spot corpus is.
- **No CME real-time/non-display fees** are incurred by EOD historical research.
- **Hard rule preserved:** any vendor credential is never committed; the secret-scan gate continues to enforce this.

---

## 5. Integration complexity (vs the existing spot pipeline)

| Item | Complexity | Note |
|------|-----------|------|
| EOD CSV ingest | Low | Mirrors the non-USD-cross ingestion pattern (additive registry + loader) |
| Continuous-contract roll construction | Medium | New infra (Phase 1 design); lookahead-safe crossover roll |
| Quote inversion (6J/6S/6C) | Low | Pure sign transform; documented in Phase 4 |
| 6J ×100 scaling normalization | Low-Medium | Highest data-hygiene risk; must be auto-detected |
| Calendar alignment (CME holidays, Sunday open) vs spot | Medium | Futures session ≠ spot 24/5; affects any cross-venue comparison |
| Intraday futures (for C1) | High | Account/paid source + pacing + storage |
| Tick/MBP (for S4) | Very High | Paid + latency model + microstructure backtest |

---

## 6. Net data-source findings

1. **Carry: free, local, deep — feasible now.** Free EOD CME FX-futures history (decades) fully supports the frozen monthly carry diagnostic, including the basis/roll that *is* futures carry.
2. **C1: feasible only with a paid/account intraday feed** (IBKR or 1-min vendor); not on free/local data without altering the definition.
3. **S4: not feasible on free/local data**, and the venue does not relax its binding (staleness/latency) constraint — re-testing S4 in futures would require HFT-grade data and infra and would still likely fail for venue-independent reasons.

This split is the core input to the Phase 5 viability verdict: a **carry-centric futures diagnostic is realistically executable from free/local data**, while C1 and S4 are gated or inappropriate. That points toward **VIABLE_WITH_LIMITATIONS**, scoped to carry (with C1 as a stretch goal contingent on an intraday source, and S4 explicitly excluded).
