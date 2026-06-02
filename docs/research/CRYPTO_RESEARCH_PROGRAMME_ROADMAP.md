# Cryptocurrency Research Programme — Roadmap

**Sprint:** `research-forex-archive-cleanup-and-crypto-roadmap-001` (Phase E)
**Date:** 2026-05-31
**Status:** DESIGN ONLY — no data ingested, no factors run, no campaigns created
**Prerequisite:** `FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md` reviewed

---

## Scope guardrails

- **Universe:** BTC/USD and ETH/USD only. No altcoins. No basket expansion.
- **No strategy, campaign, or factor-validation sprint in this document's scope.**
- **Paper/demo/live remain blocked** until a future strategy passes full gates and human approval.
- **Conservative and evidence-driven** — same discipline as forex programme.

---

## 1. What data should be collected?

### Phase 1 (spot-first)

| Data class | Requirement |
|------------|-------------|
| OHLCV | 1-minute base (if reliable/affordable); materialized 5m, 15m, 1h, 4h, 1d |
| Bid/ask or spread proxy | Required for cost-realism; use exchange bid/ask if available, else conservative spread model |
| Volume | Native exchange volume (not tick-count proxy) |
| Timestamps | UTC; no session assumptions |
| Provenance | Source, fetch time, symbol mapping, gap policy documented per series |

### Phase 2+ (futures hooks, not blocking)

| Data class | Requirement |
|------------|-------------|
| Perpetual/futures OHLCV | Same timeframes as spot |
| Funding rate history | 8h typical; for Family E only |
| Open interest | Daily or 8h; for Family E only |
| Basis | Spot vs futures for carry-like diagnostics |

### Minimum historical depth

- **5 years** minimum for initial diagnostics (matches forex matched-window discipline)
- **10+ years** desirable for slow signals (BTC has sufficient history; ETH ~2017+)

---

## 2. What timeframe(s) should be prioritized?

**Recommended initial set:**

| Timeframe | Role |
|-----------|------|
| 1m | Base ingestion granularity (if source quality supports it) |
| 5m, 15m | Primary execution diagnostics |
| 1h, 4h | Context / regime filters |
| 1d | Slow regime and momentum diagnostics |

**Priority:** 5m/15m execution with 1h/4h context and daily regime — mirrors the forex MTF structure but without assuming FX session boundaries.

**Justification:** Crypto trades continuously; there are no London/NY session edges to exploit by default. The 5m/15m layer captures short-horizon persistence and pullback structure; 1h/4h provides trend context without the cost penalty of pure H4-only entries that failed in FX.

---

## 3. BTC only vs BTC+ETH?

**Recommendation: BTC+ETH from the start.**

| Rationale | Detail |
|-----------|--------|
| Generality test | Determines whether effects are crypto-wide or BTC-specific |
| Relative-value lane | Family B requires both assets |
| Minimal scope | Two assets only — no altcoin expansion |
| Cost control | Doubles data/validation work but not universe explosion |

Start all diagnostics with BTC-only and ETH-only splits **plus** pooled analysis. Report whether effects generalize across both.

---

## 4. Spot vs futures?

**Recommendation: spot OHLCV first; futures/funding designed but not blocking Phase 1.**

| Phase | Venue |
|-------|-------|
| Stage 1–3 | Spot BTC/USD, ETH/USD |
| Stage 4+ | Add perpetual/futures data for Family E (funding/OI) |

**Justification:** Spot data is simpler, free sources are more available, and Family C (Trend Persistence) does not require funding/OI. Futures market structure matters for Family E but should not delay the first diagnostic sprint.

Design hooks in the data schema for futures symbol mapping, funding rate fields, and OI — populate later.

---

## 5. Which forex lessons transfer?

1. **Null baselines are mandatory** — matched random, shuffled timestamp, randomized ranks
2. **Cost sensitivity is mandatory** — gross effects mean nothing without spread + fees
3. **No campaign without factor effect** — exploratory diagnostics first
4. **No tuning after seeing results** — pre-register gates and thresholds
5. **Provenance matters** — every dataset traceable to source and fetch time
6. **Infrastructure is not edge** — do not confuse platform maturity with alpha
7. **Cross-validation matters** — BTC/ETH split is the crypto equivalent of cross-universe replication
8. **Small real effects can still be untradeable** — S4 lesson applies directly
9. **Avoid expanding universe to find a win** — stay on BTC+ETH until a family clears gates

---

## 6. Which forex lessons should be discarded or relaxed?

| FX assumption | Crypto adjustment |
|---------------|-------------------|
| Low directional persistence | Crypto may exhibit stronger momentum/regime persistence — test, don't assume |
| H4-only entries sufficient | Continuous market; shorter execution timeframes may matter more |
| Session structure (London/NY/Asian) | No natural session boundaries; use volatility regimes instead |
| Carry/funding like FX rollover | Funding is exchange-specific, discrete, and structurally different — do not port FX carry construction |
| Seven-pair failure modes dominate | Two-asset crypto market structure is different; fewer collinearity traps but higher idiosyncratic risk |
| Mean reversion default | Do not assume FX-like choppy/range-bound behavior |

---

## 7. Which factor family should be tested first?

### Recommendation: **Family C — Trend Persistence**

**First diagnostic sprint after data ingestion.**

Examples: momentum, trend continuation, breakout persistence, regime persistence.

| Why first | Detail |
|-----------|--------|
| Structural difference | Crypto's most plausible edge vs FX is stronger directional persistence |
| Data simplicity | Requires spot OHLCV only — no funding/OI needed |
| Baseline value | Answers "is crypto worth deeper work?" before investing in complex families |
| FX contrast | FX trend/momentum failed cost-defeat; crypto may differ structurally |

### Why not first — other families

| Family | Deferral reason |
|--------|-----------------|
| **A — Multi-Timeframe Confluence** | Second candidate; often reducible to trend persistence + pullback logic; test after C establishes directional structure exists |
| **B — Relative Value (BTC/ETH)** | Important but closest to FX S4 "real but weak" failure mode; needs both assets; run after C |
| **D — Non-Time Bars** | Wait until standard time-bar persistence diagnostics confirm directional follow-through exists |
| **E — Funding/Open Interest** | Futures-only; not Phase 1; add after spot diagnostics and futures data design |

---

## 8. Staged roadmap

### Stage 0 — Archive review complete ✓ (this sprint)

- [x] Forex archive proposal written
- [x] Final FX state index exists
- [x] Human review of cleanup proposal
- [x] Archive cleanup executed (`FOREX_ARCHIVE_CLEANUP_EXECUTION_001_SUMMARY.md`)
- [x] NEEDS_REVIEW triage complete (`FOREX_NEEDS_REVIEW_TRIAGE_001_SUMMARY.md`)

### Stage 1 — Crypto data design ✓

- [x] Choose venue(s) and source options
- [x] Define spot vs futures scope
- [x] Define BTC/USD and ETH/USD symbol mapping
- [x] Define OHLCV, spread, provenance requirements
- [x] Define materialized timeframe requirements
- [x] Define cost model assumptions
- [x] Define minimum historical depth and gap policy
- **Deliverable:** [`active/crypto_programme/CRYPTO_DATA_INGESTION_PLAN.md`](active/crypto_programme/CRYPTO_DATA_INGESTION_PLAN.md)

### Stage 2 — Crypto data ingestion infrastructure ✓

- [x] Implement ingestion per plan
- [x] Validate data quality (7-day pilot)
- [x] Build minimal BTC/ETH canonical pilot dataset in Postgres
- [x] Full 5y backfill (BTC/ETH M1 + derived TFs)
- **Deliverables:** ingest/validate/materialize scripts; [`CRYPTO_DATA_INGESTION_001_SUMMARY.md`](active/crypto_programme/CRYPTO_DATA_INGESTION_001_SUMMARY.md)

### Stage 3 — Exploratory factor diagnostics (in progress)

- [x] Family C Trend Persistence — **STATISTICAL_ONLY_COST_DEFEATED**
- [x] Family B Relative Value — **STATISTICAL_ONLY_COST_DEFEATED** (gross H4 rel-momentum ~4.6 bps; paired all-in hurdle ~260 bps)
- [x] Null baselines, regime terciles, one-leg + paired cost variants
- [x] Family D vs E selection → **Family E chosen**; derivatives data prep complete (`CRYPTO_FAMILY_E_DERIVATIVES_DATA_PREP_001_SUMMARY.md`)
- [x] Derivatives backfill executed (`CRYPTO_DERIVATIVES_BACKFILL_001_RESULT.md`) — BTC+ETH 6.4y USD funding/OHLCV/basis; frozen cost model (`CRYPTO_DERIVATIVES_COST_MODEL_001.md`)
- [x] Family E exploratory diagnostics — **NO CANDIDATE** (`CRYPTO_FAMILY_E_EXPLORATORY_SYNTHESIS_001.md`): diagnostics 1/2/3/6/7 `rejected`, 4/5 `blocked_low_power_oi`. Strongest thread = downtrend-conditioned funding reversion (BTC+ETH 2×-positive) but fails the frozen bar (single regime slice on a rejected base). Third family to miss the bar (C/B cost-defeated).
- [ ] Family D non-time bars (deferred; low-info — re-samples spot OHLCV C/B already showed cost-defeated)
- [ ] Family A MTF confluence (deferred)
- **Decision: → crypto programme PAUSE synthesis** (`NEXT_PROMPT_CRYPTO_PROGRAMME_PAUSE_SYNTHESIS_001.md`). No campaigns, no front-gate, no approval.

### Stage 4 — First factor-family validation

- Select exactly one family (expected: Family C — Trend Persistence)
- Pre-register gates, nulls, and cost thresholds before running
- Full factor-validation protocol (matched nulls, robustness, cross-sectional if applicable)
- **No strategy campaign**

### Stage 5 — Possible campaign (strict gate)

- Only if a factor family clears strict front-gate evidence
- Effect must be economically meaningful after realistic costs
- No approval from exploratory results alone
- Paper/demo/live remain blocked until explicit human approval

---

## 9. What must be true before any crypto campaign exists?

1. Stage 0–3 complete with documented data quality validation
2. At least one factor family passes Stage 4 validation with:
   - Matched null Z ≥ 2 (or programme-equivalent gate)
   - Net-of-cost positive expectancy at conservative spread assumptions
   - Robust across BTC and ETH (not single-asset artifact)
   - Pre-registered gates not relaxed post-hoc
3. Cost model documented and stress-tested (2× spread minimum)
4. Provenance complete for all data used
5. Human review and explicit campaign pre-commit document
6. `configs/approved_strategies.yaml` remains empty until separate approval process

---

## 10. What must be true before any strategy can be considered for paper/demo/live?

1. A campaign must pass all pre-committed gates including walk-forward validation
2. Independent verifier parity (if applicable) must pass
3. Financing/fee model must be validated against observed costs (not just conservative estimates)
4. Strategy name added to `configs/approved_strategies.yaml` by explicit human review
5. Restart criteria from forex programme must be met (new market ✓, but edge must be demonstrated)
6. Paper trading minimum period with observed slippage before demo consideration

**Current state:** all of the above are false. Execution remains blocked.

---

## Factor family reference

### Family A — Multi-Timeframe Confluence
H4 trend + H1 trend + M15 pullback + M5 execution. Question: were these cost-defeated in FX because FX had weak directional persistence, and could crypto's structure change that?

### Family B — Relative Value
BTC vs ETH leadership, BTC/ETH spread, cross-asset divergence, relationship reversion. Closest to FX S4. Question: does BTC/ETH RV produce effect size large enough to survive costs?

### Family C — Trend Persistence (FIRST)
Momentum, trend continuation, breakout persistence, regime persistence. Question: does crypto exhibit stronger persistence than FX across BTC and ETH?

### Family D — Non-Time Bars
Range bars, volatility bars, event bars. Question: were non-time bars unproductive in FX because the market lacked directional follow-through, and could crypto volatility make them useful?

### Family E — Funding/Open Interest (FUTURE)
Perpetual funding rates, open interest, basis. Not Phase 1. Crypto derivatives market structure may matter but requires futures data design first.

---

## Related documents

- [`FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md`](FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md)
- [`FOREX_PROGRAMME_FINAL_STATE.md`](FOREX_PROGRAMME_FINAL_STATE.md)
- [`NEXT_PROMPT_CRYPTO_DATA_DESIGN_001.md`](NEXT_PROMPT_CRYPTO_DATA_DESIGN_001.md)
- [`PROGRAMME_LESSONS_LEARNED.md`](PROGRAMME_LESSONS_LEARNED.md)
