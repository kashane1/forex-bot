# Multi-Market Research Universe

**Purpose:** define the research universe the multi-market front gate
should be able to evaluate — current majors, candidate non-USD FX
crosses, and future asset classes — each with a qualitative
cost/liquidity/feasibility profile. This is a **design** document: no
instrument is ingested, traded, or approved here. Profiles are
qualitative estimates to be confirmed by a cost/data sprint, not broker
quotes (no APIs, no credentials).

**Notation:** spreads in pips (FX) or as a relative band; "≈" = typical
calm-market retail estimate; cost orientation is *relative to EUR_USD*,
the cheapest instrument in the current corpus.

---

## Tier 0 — Current corpus (already ingested, baseline/control)

7 USD-legged majors, ~6.4y H4 + M1-derived. Role going forward:
**control/baseline and null reference**, not the primary edge search.

| Instrument | Spread | Financing | Liquidity | Notes |
|---|---|---|---|---|
| EUR_USD | ≈0.8–1.2 | low | highest | cheapest; baseline |
| GBP_USD | ≈1.2–1.8 | low–med | very high | |
| USD_JPY | ≈0.9–1.5 | med (rate diff) | very high | JPY-funding leg |
| AUD_USD | ≈1.0–1.6 | med | high | risk-proxy |
| NZD_USD | ≈1.4–2.2 | med | high | thinner than AUD |
| USD_CAD | ≈1.3–2.0 | med | high | oil-linked |
| USD_CHF | ≈1.2–1.8 | low–med | high | CHF safe-haven |

**Structural limitation:** every pair shares the USD leg → correlated
signals, a structural USD bet, and breadth premia (cross-sectional,
carry, relative-value) are underpowered (C016/C028/C031).

---

## Tier 1 — Candidate non-USD FX crosses (first expansion target)

Same OANDA retail execution model and same ingestion pipeline as the
majors — the **cheapest genuinely-new data** to add. The value is
**driver diversity and breaking USD-leg crowding**, *not* lower cost
(crosses are generally **wider** than EUR_USD). Two sub-groups: JPY
crosses (funding/risk theme) and European/AUD crosses (cross themes).

| Cross | Spread (est.) | Financing | Liquidity | Impl. difficulty | Free data | Repo compat. |
|---|---|---|---|---|---|---|
| EUR_GBP | ≈1.0–2.0 | low (small rate diff) | high | low | yes (same broker model) | native |
| EUR_JPY | ≈1.2–2.2 | med | high | low | yes | native |
| GBP_JPY | ≈2.0–3.5 | med | high (very volatile) | low | yes | native |
| AUD_JPY | ≈1.5–2.8 | med–high (carry classic) | high | low | yes | native |
| NZD_JPY | ≈2.2–3.8 | med–high (carry) | med | low | yes | native |
| EUR_AUD | ≈1.8–3.2 | med | med | low | yes | native |
| EUR_CHF | ≈1.5–2.5 | low | med | low | yes | native (SNB-peg history caveat) |
| GBP_CHF | ≈2.5–4.0 | low–med | med | low | yes | native |

**Reading of Tier 1:**
- **Lowest-cost crosses:** EUR_GBP, EUR_JPY — closest to major-like
  spreads; best first candidates on a pure cost basis.
- **Carry-theme crosses:** AUD_JPY, NZD_JPY — classic positive-carry
  longs; financing is *central* to their behaviour, so an
  instrument-specific financing model is mandatory before any inference.
- **Volatile/wide crosses:** GBP_JPY, GBP_CHF, EUR_AUD, NZD_JPY — wider
  spreads; higher cost wall; useful for *breadth/independence* even if
  individually cost-hostile.
- **History caveat:** EUR_CHF has a structural break (the 2015 SNB-peg
  removal) — any study must window around it; do not treat it as a clean
  continuous series.
- **Implementation difficulty: uniformly low** — all are OANDA
  instruments on the existing H4 bid/ask + M1 pipeline; the only new
  work is per-instrument cost calibration and lookahead-free parity.

---

## Tier 2 — Future markets (later expansions; design-level only)

Different asset classes that change the *cost structure* and/or *return
drivers*. Higher implementation cost; sequence them after the cross
expansion proves the multi-market gate.

### FX futures (e.g. CME 6E, 6J, 6B, 6A)
- **Spread/cost:** central-limit order book; commission + 1-tick spread
  — often a **more favourable, more transparent** cost profile than
  retail spread-betting (the kind of change that could move the
  two-sided squeeze).
- **Financing:** embedded in the futures basis/roll, not daily swap.
- **Liquidity:** very high (front month).
- **Impl. difficulty:** **medium** — needs a futures adapter and
  **continuous-contract roll** handling (new infra) + a contract
  calendar.
- **Free data:** partial (some free; deep clean history usually paid).
- **Repo compat.:** medium (new adapter; bar model is compatible).

### Index futures / index CFDs (ES, NQ / US500, NAS100, GER40, JP225)
- **Spread/cost:** index futures competitively priced; index CFDs carry
  retail overnight financing (same squeeze risk as FX CFDs).
- **Financing:** futures via basis; CFDs via daily financing.
- **Liquidity:** very high (major index futures).
- **Drivers:** **equity-risk premium and trend persistence** — a
  structurally different, historically more persistent return source.
- **Impl. difficulty:** medium (futures) / low–medium (OANDA CFD).
- **Free data:** partial. **Repo compat.:** medium / high (OANDA CFD).

### Metals (XAU_USD, XAG_USD; GC/SI futures)
- **Spread/cost:** XAU_USD available on OANDA now (wider, vol-scaled);
  futures deeper history.
- **Financing:** metals carry (storage/lease) — nontrivial.
- **Liquidity:** high (gold), medium (silver).
- **Drivers:** trend, safe-haven/regime flows.
- **Impl. difficulty:** **low** via OANDA / medium via futures.
- **Free data:** yes (OANDA). **Repo compat.:** high (OANDA).

### Crypto (BTC_USD, ETH_USD, larger liquid alts)
- **Spread/cost:** high spread/vol and venue/withdrawal frictions — but
  documented **persistent momentum and funding/basis carry** (larger
  gross edges that can clear higher cost).
- **Financing:** perpetual funding rate / spot has none — different model
  entirely (no daily rollover concept).
- **Liquidity:** high (BTC/ETH), variable (alts), 24/7.
- **Impl. difficulty:** medium–high — 24/7 sessions (no weekend gap), new
  venue adapters, different calendar.
- **Free data:** **yes — abundant, deep, free** (best free-data story).
- **Repo compat.:** medium (session/calendar assumptions differ).

### Equities / ETFs (e.g. SPY, QQQ, sector/factor ETFs, single names)
- **Spread/cost:** commission + spread; short borrow for shorts.
- **Financing:** margin interest; dividends/corporate actions.
- **Liquidity:** very high (large ETFs); variable (single names).
- **Drivers:** richest factor literature (value, momentum, quality,
  earnings drift) — but most needs cross-sectional breadth.
- **Impl. difficulty:** **medium–high** — corporate-action handling,
  survivorship-free universes, dividend adjustment.
- **Free data:** partial (free EOD; intraday paid).
- **Repo compat.:** medium (universe management + actions are new).

---

## Universe recommendation (this sprint)

- **Adopt the full universe as the lab's *target scope*** (the
  framework in Phase 2 is designed for all tiers), but **stage
  ingestion**.
- **First expansion = Tier 1 non-USD crosses**, led by the lowest-cost,
  breadth-adding subset: **EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY**
  (with NZD_JPY, EUR_AUD, EUR_CHF, GBP_CHF as the second wave). Rationale:
  same pipeline, free/local, lowest implementation risk, directly
  attacks USD-leg crowding, and powers the breadth families that were
  underpowered on 7 USD majors.
- **Defer Tier 2** (crypto → metals/index → futures → equities) until the
  cross expansion validates the multi-market gate end-to-end. Crypto is
  the strongest *later* candidate on free-data depth + edge potential;
  futures are the strongest on *cost-structure change*.

Detailed cross feasibility is in `NON_USD_CROSS_FEASIBILITY_STUDY.md`;
the prioritized acquisition plan is in
`MULTI_MARKET_DATA_ACQUISITION_ROADMAP.md`; the single chosen path is in
`NEXT_DATA_EXPANSION_DECISION.md`.
