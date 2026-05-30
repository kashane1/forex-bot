# Forex Structural Cost Constraints

**Question:** is the current seven-major OANDA FX corpus *structurally*
hard to trade — i.e., are the failures a property of the market/cost
environment rather than of the strategy ideas?

**Method:** synthesis of existing committed evidence only
(`COST_SPREAD_SLIPPAGE_FINANCING_AUDIT_RESULT.md`,
`CARRY_AND_FINANCING_READINESS_MEMO.md`, `FINANCING_MODEL_STATUS.md`,
the non-time-bar feasibility study, and the C026/C029/C031/C1
closeouts). No broker data is fetched; no new numbers are produced.

**Bottom line:** yes. The dominant, repeated failure mode is
**cost-defeated**, and the cost structure squeezes from *both ends* —
the per-trade spread wall on fast strategies and the financing wall on
slow strategies. This is a structural property of the corpus, not a
tuning failure.

---

## The two-sided cost squeeze (the core structural finding)

From `CARRY_AND_FINANCING_READINESS_MEMO.md` and the cost audit:

- **Fast (intraday, financing-free) strategies** avoid carry — but the
  gross edge is only a few pips and **round-trip spread + slippage is of
  the same order or larger.** They die on the spread wall.
- **Slow (multi-day/weekly) strategies** amortize per-trade spread over
  a bigger move — but **financing/carry on the hold is the same order as
  or larger than the gross edge** (C031: financing ≈4× spread cost).
  They die on the financing wall.
- **There is no free lunch on this corpus:** the cost structure squeezes
  both ends. This is the single most important structural fact.

## Constraint-by-constraint

### 1. Spread

- Per-pair typical OANDA retail spreads, applied entry + exit. EUR_USD
  ~0.8–1.2 pip; JPY pairs and crosses materially wider.
- Gross H4/M-timeframe edges are typically 1–3 pips → round-trip cost is
  the same order. **Spread alone defeats most intraday edges.**
- **Structural? Yes.** It is a property of the retail venue and the
  instruments, not of any one strategy.

### 2. Slippage

- A conservative per-trade slippage assumption on top of spread, larger
  for stop exits and volatile bars.
- Interacts adversely with exactly the conditions some effects need:
  large overshoots / high-vol bars (H16, C1 high-vol) have **wider**
  spreads and worse slippage, so the cost wall is *highest where the
  signal is strongest*.
- **Structural? Yes**, and adversarially correlated with signal strength.

### 3. Financing

- Per-instrument financing modeled as bp/day, applied as a ledger
  overlay. Sufficient as a *rejection* gate (if a strategy only works
  without financing, financing kills it and we can show it).
- For slow strategies financing is the binding cost (C031). The model is
  conservative; observed-rate calibration is parked behind the freeze.
- **Structural? Yes** for any multi-day hold on this corpus.

### 4. Rollover

- Overnight financing applies at the OANDA rollover; the USD_JPY
  microstructure atlas found rollover to be **cost-toxic** for holds
  spanning it.
- **Structural? Yes** for strategies that cannot avoid the rollover.

### 5. Session effects

- The USD_JPY session/volatility/spread atlas: vol timing is
  *predictable* (range clusters by session) but **direction is
  atlas-level ≈0.49** (coin-flip) and spreads are flat across macro
  cells. Off-hours have wider spreads (hurts thin-move/overshoot ideas).
- **Structural? Partly** — predictable vol does not translate into a
  monetizable directional edge at this cost.

### 6. OANDA retail execution model

- Every OANDA-available instrument uses the **same retail execution
  model** — retail spreads, retail financing, no order-book, no ECN
  depth. This is the environment all C001–C031 results live in.
- The cost model is "conservative but not pessimistic" — typical retail,
  not best-case institutional. So results are not artificially harsh;
  they reflect a real retail trader's environment.
- **Structural? Yes** — this is the defining constraint of the corpus.

### 7. Major-pair crowding

- The corpus is **seven USD-legged majors only.** Every pair shares the
  USD leg, so the book is a structural USD bet (explicit in C031) and
  signals are correlated. The most liquid, most-arbitraged instruments
  on earth offer the least inefficiency.
- **Structural? Yes** — crowding/efficiency is intrinsic to majors.

### 8. Limited instruments

- No non-USD crosses, no other asset classes in the research store.
  Breadth premia (cross-sectional, carry, relative-value) are
  underpowered or untestable (C016 cross-sectional REJECT; C028
  relative-value NO_SCAFFOLD; C031 breadth premise "dead" on 7 majors).
- **Structural? Yes** — and directly data-blocked.

### 9. Sample length

- ~6.4 years of H4 (M1-derived lower timeframes). Slow signals are
  underpowered; only ~1–3 usable years per validation split. C027 had
  1/3 positive years; C031's slow signal was "underpowered" by design.
- **Structural? Yes** for any slow/regime/macro signal needing multiple
  cycles. Reopen condition repeatedly cited: **10–15y**.

### 10. Lack of true tick / order-book data

- FX "volume" in this corpus is a **tick-count proxy**, not real
  volume; there is no L2/order-book. Genuine microstructure edges
  (queue position, flow, imbalance) are **not testable here** (H03/H16
  participation buckets are proxies).
- **Structural? Yes** — a hard data ceiling on the microstructure lane.

---

## What is *not* a structural cost problem

- **Infrastructure / parity** is sound (backtrader parity hardened,
  walk-forward harness works, contamination found and fixed, M1
  plumbing verified). Failures are not artifacts of broken tooling.
- **The null/front-gate machinery** works — it correctly demotes
  selection noise. So "we just got unlucky with ideas" is *not* the
  explanation; the gate has seen many ideas and the wall is consistent.

## Verdict

The seven-major OANDA retail FX corpus is **structurally hard to trade**
for the strategy families explored: a conservative-but-realistic
two-sided cost squeeze (spread wall + financing wall), on the most
efficient/crowded instruments, with limited breadth, a short sample, and
no true microstructure data. The observed failures are **predominantly
structural (market + cost) rather than idea-quality** — with the
important qualifier that the *one genuine effect found (C1)* confirms
edges can exist here; they are simply smaller than the cost of trading
them.

This feeds directly into the Phase 3 viability decision.
