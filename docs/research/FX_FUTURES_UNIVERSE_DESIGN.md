# FX Futures Universe Design (Phase 1)

**Sprint:** `research-fx-futures-venue-and-diagnostic-001`
**Type:** Documentation only. No code, no data ingestion.
**Date:** 2026-05-31
**Purpose:** Define the candidate CME FX-futures universe, contract mappings to the existing spot corpus, specifications, and roll / continuous-contract methodology — as a *design*, not an implementation.

> **Assumption discipline:** the contract specifications below are the standard, long-stable CME FX figures used for research design. Exact tick sizes and contract sizes are periodically revised by the exchange and **must be re-confirmed against the live CME contract specs at the moment of ingestion** (next sprint). Every numeric spec here is therefore a *design assumption* flagged `[CONFIRM]`, not an authoritative quote.

---

## 1. Why these contracts

The spot corpus is **7 USD-legged majors** (EUR_USD, GBP_USD, USD_JPY, USD_CHF, AUD_USD, USD_CAD, NZD_USD) plus 8 non-USD crosses (added in the cross-expansion sprint). CME lists deep, liquid, full-size futures for exactly the seven major currencies, which lets the diagnostic re-test **C1** (USD majors) and **carry** (cross-sectional, 8-currency) on a like-for-like currency set. S4's triangular relationships can be reconstructed from the same legs.

The **E-micro** variants (1/10 size: M6E, M6B, M6A, M6C, M6S, and micro JPY) exist but are **not** chosen for the diagnostic: they carry proportionally wider relative cost and thinner history, which would bias a cost-survival test pessimistically. Full-size contracts give the cleanest liquidity and cost picture. (Micros remain relevant only to capital sizing, which is out of scope — no trading.)

---

## 2. Candidate universe and spot mapping

| CME root | Underlying | Spot-corpus analogue | Quote convention | Mapping note |
|----------|-----------|----------------------|------------------|--------------|
| **6E** | EUR/USD | EUR_USD | USD per 1 EUR | Direct |
| **6B** | GBP/USD | GBP_USD | USD per 1 GBP | Direct |
| **6J** | JPY/USD | USD_JPY | USD per 1 JPY | **Inverted** vs spot (spot is JPY per USD) |
| **6S** | CHF/USD | USD_CHF | USD per 1 CHF | **Inverted** vs spot |
| **6A** | AUD/USD | AUD_USD | USD per 1 AUD | Direct |
| **6C** | CAD/USD | USD_CAD | USD per 1 CAD | **Inverted** vs spot |
| **6N** | NZD/USD | NZD_USD | USD per 1 NZD | Direct |

**Critical design point — quote inversion.** All CME FX futures quote the *foreign currency as base* (XXX/USD). Three of the seven (JPY, CHF, CAD) are quoted *inverted* relative to the spot corpus's USD-base convention (USD_JPY, USD_CHF, USD_CAD). The diagnostic must map returns consistently: a long-6J position is long-JPY/short-USD, i.e. the **opposite sign** of a long-USD_JPY spot position. This sign-mapping is a pure transformation and **does not alter any frozen factor definition** — it only re-expresses the same currency exposure in the futures quote convention. It will be documented explicitly in the diagnostic framework (Phase 4).

---

## 3. Contract specifications (design assumptions, `[CONFIRM]` at ingestion)

| Contract | Contract size | Min tick `[CONFIRM]` | Tick value `[CONFIRM]` | Point value (per 1.00 move) |
|----------|---------------|----------------------|------------------------|------------------------------|
| 6E (EUR) | 125,000 EUR | 0.00005 USD/EUR | $6.25 | $125,000 |
| 6B (GBP) | 62,500 GBP | 0.0001 USD/GBP | $6.25 | $62,500 |
| 6J (JPY) | 12,500,000 JPY | 0.0000005 USD/JPY | $6.25 | (quoted ×100 on some feeds) |
| 6S (CHF) | 125,000 CHF | 0.0001 USD/CHF | $12.50 | $125,000 |
| 6A (AUD) | 100,000 AUD | 0.00005 USD/AUD | $5.00 | $100,000 |
| 6C (CAD) | 100,000 CAD | 0.00005 USD/CAD | $5.00 | $100,000 |
| 6N (NZD) | 100,000 NZD | 0.0001 USD/NZD | $10.00 | $100,000 |

Notes:
- **6J quoting quirk `[CONFIRM]`:** the JPY future is economically priced at ~0.0000067 USD/JPY; many data vendors publish it scaled ×100 (e.g. "0.67xx"). The ingestion adapter must detect and normalize the scale, or all 6J cost/return math will be off by 100×. Flagged as the single highest-risk data-hygiene item.
- Tick *values* are what matter for the cost model (Phase 3), since cost is expressed per round-turn in ticks. Contract *size* matters only for notional/sizing, which is out of scope.

---

## 4. Contract cycle and expiry

- **Cycle:** quarterly — March (H), June (M), September (U), December (Z). (CME also lists some serial months, but the quarterlies carry the liquidity and are the design basis.)
- **Expiry / last trade:** the **second business day before the third Wednesday** of the contract month; settlement on the third Wednesday (the IMM date). `[CONFIRM]`
- **Liquidity migration:** open interest and volume migrate from the front (expiring) to the next quarterly typically in the ~1–2 weeks before expiry.

---

## 5. Roll methodology (design)

A continuous series requires a rule for *when* to roll from the front contract to the next.

**Chosen design: volume/open-interest-crossover roll.**
- Roll on the first day the next quarterly's volume (or open interest) exceeds the front contract's, capped to occur no later than N business days before last-trade-date.
- Rationale: matches where real liquidity sits; avoids rolling into an illiquid back month too early or holding an expiring contract too late.
- **Lookahead safety:** the crossover decision uses only *contemporaneous and past* volume/OI — no future information. This must be enforced in the adapter (next sprint), mirroring the lookahead discipline already proven in `src/forex_bot/data/non_time_bars.py`.

**Alternative considered (rejected for the diagnostic):** fixed-calendar roll (e.g. always N days before expiry). Simpler and fully deterministic, but can roll away from liquidity in atypical quarters. Acceptable as a *robustness cross-check*, not the primary.

---

## 6. Continuous-contract methodology (design)

Stitching rolled contracts into one series introduces a price gap at each roll (the front and next contracts differ by the basis). Three standard treatments:

| Method | What it does | Use for the diagnostic |
|--------|--------------|------------------------|
| **Unadjusted (with roll gaps)** | Concatenate raw prices; gaps remain at rolls | Keep as the **cost/roll ledger source** — the roll gap *is* the roll cost signal |
| **Back-adjusted (difference / "Panama")** | Shift historical prices so the roll gap is removed additively | **Primary for return/signal series** — produces a continuous return stream for factor evaluation; absolute level is distorted but returns are clean |
| **Ratio-adjusted** | Same idea multiplicatively (preserves % returns) | **Primary for percentage-return factors** (carry, momentum); preferred over difference-adjust for long histories where price level changes a lot |

**Design choice:**
- **Signal/return computation:** ratio-adjusted continuous series (preserves multiplicative returns across decades).
- **Roll-cost accounting:** computed separately from the *unadjusted* series, so the basis/roll cost is measured explicitly rather than hidden by the adjustment (see Phase 3 cost model).
- This separation keeps the **factor returns** and the **roll cost** as independent, auditable quantities — essential for a gross-vs-net survival diagnostic.

**Lookahead caveat (documented):** back/ratio adjustment as normally implemented re-bases the *entire* history at each roll, which means the displayed historical level depends on later rolls. For *return* series this is harmless (returns are roll-local). For any computation that reads an absolute price level, the adapter must use the unadjusted series or a forward-only adjustment. This is a known pitfall and is called out so the next sprint does not introduce subtle lookahead.

---

## 7. What is explicitly NOT designed here

- No position sizing, no contract counts, no margin — that is trading, out of scope.
- No entry/exit timing — out of scope.
- No change to C1 / S4 / carry definitions — only a venue + quote-convention re-expression.
- No selection of a specific data vendor yet — that is Phase 2.

---

## 8. Open items carried to later phases

1. `[CONFIRM]` all tick sizes/values and the 6J scaling at ingestion (Phase 2 feasibility flags the source; next sprint confirms).
2. Roll-rule parameter (crossover cap N) to be fixed in the diagnostic pre-registration, not optimized.
3. Whether deep history (pre-2010) is available per contract — feeds into Phase 2 and the viability verdict.
