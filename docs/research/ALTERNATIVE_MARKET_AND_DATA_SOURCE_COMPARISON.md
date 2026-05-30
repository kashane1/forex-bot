# Alternative Market & Data-Source Comparison

**Purpose:** compare the current corpus against alternative
instruments/data sources as *research search spaces*, to inform where
the next edge is more likely to live. This is a research-direction
comparison, **not** a trading recommendation, **not** an ingestion plan,
and **not** an approval. Nothing here is backtested; no broker data is
fetched.

**Why now:** Phase 2 concluded the seven-major OANDA retail corpus is
structurally hard to trade (two-sided cost squeeze, crowded majors,
short sample, no true microstructure data). The natural question is
whether a *different cost structure or instrument universe* offers a
better-conditioned search space.

**Evaluation axes:** data availability · expected costs · likely edge
types · infrastructure required · compatibility with current repo ·
free/local feasibility · risk/complexity. Each is a *qualitative*
assessment grounded in the project's existing cost/structure findings
and general public market structure — to be confirmed by a front-gate
screen before any commitment.

---

## Summary matrix

| Option | Data availability | Expected cost vs current | Likely edge types | Repo compatibility | Free/local | Risk/complexity |
|--------|-------------------|--------------------------|-------------------|--------------------|-----------|-----------------|
| FX majors on OANDA (current) | Already ingested (~6.4y H4, M1-derived, 7 USD majors) | Baseline (retail two-sided squeeze) | Exhausted on tested families | Native | Yes | Low (known) |
| Non-USD FX crosses | Same OANDA model; not yet ingested | Wider spreads (worse per-trade) but **new driver mix** | Breadth: cross-sectional, carry, relative-value | High (same pipeline) | Yes (same broker/free) | Low–Med |
| FX futures (CME/6E,6J…) | Public/historical via vendors; not ingested | **Different (often lower) cost profile**; central limit order book | Trend, carry, term-structure; cleaner cost | Med (new adapter + contract roll) | Partial (some free, deep history paid) | Med |
| Index futures / index CFDs (ES/NQ, US500/NAS100) | Futures via vendors; CFDs via OANDA | Futures: competitive; CFDs: retail overnight cost | **Equity-risk premium, trend persistence** | Med (futures) / High (OANDA CFD) | Partial | Med |
| Metals (XAU/XAG) | OANDA + futures (GC/SI) | High vol; spread/financing nontrivial | Trend, safe-haven/regime flows | High (OANDA) / Med (futures) | Yes (OANDA) | Med |
| Crypto (BTC/ETH…) | Abundant free history; many venues | High cost/vol but **persistent momentum & inefficiency** | Momentum, cross-sectional, funding/basis carry | Med (new venue adapters, 24/7) | **Yes (free, deep)** | Med–High (regime change, venue risk) |
| Equities / ETFs | Abundant (some free EOD; intraday paid) | Commission + spread; borrow for shorts | Cross-sectional factors, value/momentum, earnings | Med (corporate actions, universe mgmt) | Partial (EOD free) | Med–High (survivorship, actions) |
| Rates / macro data | FRED already wired (cross-asset features); rate futures via vendors | n/a as features; futures have own cost | Macro overlays, carry, regime conditioning | High for features (FRED ingest exists) | **Yes (FRED free)** | Low (features) / Med (rate futures) |
| Higher-quality tick / L2 data | Paid vendors; some sampled free | n/a (data, not venue) | **Unlocks microstructure lane** (queue, flow, imbalance) | Med (new storage/replay) | Mostly paid | High (volume, cost, complexity) |
| Multi-broker FX data | Multiple feeds; aggregation effort | Lets you *compare* cost structures | Cost/execution arbitrage; better realism | Med (normalization) | Partial | Med |

---

## Per-option detail

### 1. FX majors on OANDA (current corpus — baseline)
- **Availability:** already ingested and instrumented (parity, null
  lab, M1 plumbing). 7 USD-legged majors, ~6.4y H4.
- **Cost:** the baseline two-sided squeeze (spread wall + financing
  wall). Conservative, realistic retail.
- **Edge types:** the tested families are exhausted; only C1 (real,
  not tradable) remains catalogued.
- **Compatibility:** native. **Free/local:** yes. **Risk:** low and
  fully known. **Role going forward:** control/baseline, not the place
  the next edge most likely lives.

### 2. Non-USD FX crosses (EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY, …)
- **Availability:** same OANDA retail model; just not in the research
  store. Cheapest expansion to ingest (same pipeline).
- **Cost:** generally **wider** spreads than EUR_USD — per-trade cost is
  *worse*, not better. The win is *driver diversity*, not lower cost.
- **Edge types:** breaks USD-leg crowding → enables genuine breadth
  (cross-sectional rotation, carry, relative-value/cointegration) that
  C016/C028/C031 found underpowered on 7 USD majors.
- **Compatibility:** high (same loaders/cost model). **Free/local:**
  yes. **Risk:** low–medium. **Caveat:** does **not** fix the cost wall;
  it fixes the *breadth* and *crowding* limitation only.

### 3. FX futures (e.g., CME 6E, 6J, 6B)
- **Availability:** historical via data vendors; not ingested. Deep
  history (>15y) obtainable.
- **Cost:** central-limit-order-book with a **different, often more
  favorable** cost/financing profile than retail spread betting — this
  is the kind of change that could move the two-sided squeeze.
- **Edge types:** trend, carry/term-structure, calendar-roll effects;
  cleaner cost makes thin edges potentially survivable.
- **Compatibility:** medium — needs a futures adapter and **continuous-
  contract roll** handling (new infra). **Free/local:** partial (some
  free, deep/clean history paid). **Risk:** medium.

### 4. Index futures / index CFDs (ES, NQ / US500, NAS100, SPX)
- **Availability:** futures via vendors; CFDs via OANDA (same retail
  model).
- **Cost:** index *futures* are competitively priced; index *CFDs*
  carry retail overnight financing (same squeeze risk as FX CFDs).
- **Edge types:** **equity-risk premium and trend persistence** — a
  structurally different (and historically more persistent) return
  source than spot FX mean-reversion/noise.
- **Compatibility:** medium (futures) / high (OANDA CFD). **Free/local:**
  partial. **Risk:** medium. Strong candidate on *edge potential*.

### 5. Metals (XAU_USD, XAG_USD; GC/SI futures)
- **Availability:** OANDA (immediate) and futures (deeper history).
- **Cost:** high vol; spread + financing nontrivial; on retail CFD the
  squeeze applies.
- **Edge types:** strong trends, safe-haven/regime flows — a different
  driver from FX majors.
- **Compatibility:** high (OANDA) / medium (futures). **Free/local:**
  yes (OANDA). **Risk:** medium (vol sizing).

### 6. Crypto (BTC_USD, ETH_USD, larger alts)
- **Availability:** **abundant, free, deep** intraday history across
  many venues — the easiest *new* lane to populate.
- **Cost:** high spread/vol and venue/withdrawal frictions — but
  documented **persistent cross-sectional momentum and funding/basis
  carry**, i.e., larger gross edges that can clear higher costs.
- **Edge types:** time-series & cross-sectional momentum, funding-rate
  carry, basis.
- **Compatibility:** medium (24/7 sessions, new venue adapters, no
  rollover concept). **Free/local:** **yes (best free-data story).**
  **Risk:** medium–high (regime change, venue/counterparty risk,
  shorter clean history).

### 7. Equities / ETFs
- **Availability:** abundant (free EOD; intraday paid).
- **Cost:** commission + spread; short borrow; corporate actions.
- **Edge types:** the richest factor literature (value, momentum,
  quality, earnings drift) — but most needs cross-sectional breadth and
  careful universe handling.
- **Compatibility:** medium — needs corporate-action handling,
  survivorship-free universes, dividends. **Free/local:** partial (EOD).
  **Risk:** medium–high (survivorship bias, data hygiene).

### 8. Rates / macro data
- **Availability:** **FRED is already wired** (cross-asset feature
  ingest exists); rate *futures* via vendors.
- **Cost:** as *features* there is no trading cost; as tradable rate
  futures there is a separate (modest) cost profile.
- **Edge types:** macro/regime overlays, carry, rate-differential
  conditioning — note the project found the JP rate leg absent and
  rate-regime non-identifiable on the current corpus, so this most
  *complements* a breadth expansion rather than standing alone.
- **Compatibility:** high for features (ingest exists). **Free/local:**
  **yes (FRED).** **Risk:** low (features) / medium (rate futures).

### 9. Higher-quality tick / order-book (L2) data
- **Availability:** mostly paid vendors; limited free samples.
- **Cost:** a *data* cost, not a venue cost.
- **Edge types:** the **only** way to make the microstructure lane
  (queue position, order flow, imbalance) testable at all — the lane
  H03/H16 could only proxy with tick-count volume.
- **Compatibility:** medium (new storage/replay infra). **Free/local:**
  mostly paid → poor free story. **Risk:** high (data volume, cost,
  build complexity, easy to overfit).

### 10. Multi-broker FX data
- **Availability:** multiple retail/institutional feeds; needs
  normalization.
- **Cost:** the point is to *measure and compare* cost structures across
  venues (and find tighter ones).
- **Edge types:** execution/cost-aware refinements; better realism for
  any FX result; potential cost arbitrage.
- **Compatibility:** medium (feed normalization). **Free/local:**
  partial. **Risk:** medium. More a *realism/cost* upgrade than a new
  edge source.

---

## Reading of the comparison (no recommendation yet)

- **Cheapest, lowest-risk expansion:** non-USD FX crosses (same
  pipeline) — but it fixes *breadth/crowding*, **not** the cost wall.
- **Best free-data new lane:** crypto (deep free history, larger gross
  edges) — at the price of regime/venue risk and 24/7 infra.
- **Best structural fix to the cost squeeze:** FX/index **futures**
  (different cost profile, deeper history) — at the price of roll infra.
- **Best edge-source diversity:** index futures / metals / crypto
  (different return drivers than spot-FX noise).
- **Best complement (free, already wired):** rates/macro via FRED.
- **Highest-ceiling but hardest:** true tick/L2 (unlocks
  microstructure) — paid, complex, overfit-prone.

The Phase 5 options doc ranks these, and Phase 6 selects exactly one
conservative next direction.
