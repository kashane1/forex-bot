# Expanded FX Search-Space Map

**Sprint:** `research-nonusd-cross-factor-discovery-planning-001` · Phase 1
**Type:** search-space inventory. Docs-only. No factor, no screen, no campaign.
**Date:** 2026-05-30.

This document maps the now-available 15-instrument FX universe and classifies
each *research category* as **already explored**, **partially explored**, or
**newly enabled by crosses** — so Phase 2 generates families in the genuinely
new territory and Phase 3 fences off the explored-and-failed territory.

---

## 1. The universe (15 instruments, all OANDA practice, 2021-05-26 → 2026-05-26)

### 1a. USD majors (7) — control / baseline, fully mined

| Pair | USD leg | other leg | median spread (p) | role |
|------|---------|-----------|-------------------|------|
| EUR_USD | quote | EUR | 1.5 | most liquid; C1 discovery pair |
| GBP_USD | quote | GBP | 1.9 | — |
| USD_JPY | base | JPY | 1.7 | C1 discovery pair; non-time-bar test pair |
| AUD_USD | quote | AUD | 1.3 | tightest major; risk proxy |
| NZD_USD | quote | NZD | 1.5 | C1 lone short-side exception |
| USD_CAD | base | CAD | 1.9 | commodity (oil) leg |
| USD_CHF | base | CHF | 1.6 | safe-haven leg |

**Currencies present via majors:** USD, EUR, GBP, JPY, AUD, NZD, CAD, CHF
(8 currencies, but *every* pair shares USD).

### 1b. Non-USD crosses (8) — first-wave, newly populated

| Cross | base | quote | median spread (p) | cost band | carry character |
|-------|------|-------|-------------------|-----------|-----------------|
| EUR_GBP | EUR | GBP | 1.4 | near-major (cheapest cross) | low-diff, tight |
| EUR_JPY | EUR | JPY | 2.1 | near-major/moderate | JPY-funding |
| AUD_JPY | AUD | JPY | 1.9 | moderate | classic carry (risk-on proxy) |
| EUR_CHF | EUR | CHF | 1.6 | moderate | safe-haven; 2015 SNB break (outside window) |
| NZD_JPY | NZD | JPY | 2.5 | wide | classic carry |
| EUR_AUD | EUR | AUD | 2.6 | wide | EUR vs commodity-risk |
| GBP_CHF | GBP | CHF | 2.2 | wide/volatile (fattest tail, p99 19.9) | safe-haven + GBP risk |
| GBP_JPY | GBP | JPY | 3.1 | widest | "the dragon"; high-vol carry |

### 1c. Currency-coverage matrix (what legs are now independently expressible)

Crosses add **no new currency** (still USD/EUR/GBP/JPY/AUD/NZD/CAD/CHF) but they
add **independent pairings** that don't route through USD:

- **JPY** as quote in 4 crosses (EUR/GBP/AUD/NZD_JPY) → a JPY-funding / risk-on
  axis expressible *without* USD_JPY.
- **CHF** as quote in 2 crosses (EUR/GBP_CHF) → a safe-haven axis without USD_CHF.
- **EUR** as base in 5 instruments, **GBP** in 3, **AUD** in 2 → enough
  overlapping legs to build a **currency-strength** estimate by triangulation.
- **Triangles now closable:** EUR/USD·USD/JPY·EUR/JPY; GBP/USD·USD/JPY·GBP_JPY;
  EUR/USD·GBP/USD·EUR_GBP; EUR/USD·AUD/USD·EUR_AUD; USD/CHF·EUR/USD·EUR_CHF; etc.
  **9+ closable triangles** vs **0** in the majors-only corpus.

**Not present (still data-blocked):** CAD crosses (no CAD_JPY/EUR_CAD), so CAD
appears only via USD_CAD; any non-OANDA venue; tick/L2; >5y history; real
financing rates.

---

## 2. Research categories × exploration status

Legend: **EXPLORED** = mined to a verdict (usually REJECT) on the majors ·
**PARTIAL** = touched but data-limited / underpowered · **NEW** = structurally
impossible before crosses existed.

### A. Single-instrument directional (trend / breakout / pullback / confluence)
**Status: EXPLORED → REJECT (cost-defeated).** C015/017/025 (breakout),
C020–023 (pullback), C1 & C026/C029 (confluence/TF ladder) all failed on the
same spread/financing wall. Crosses add 8 more instruments but **the same family
on a wider-spread instrument is strictly worse** — a known re-tune trap (Phase 3).
*Crosses do NOT meaningfully reopen this category.*

### B. Single-instrument mean-reversion / z-score / price-level
**Status: EXPLORED → REJECT.** C008/C027 (price-level reversion, z-score) failed;
C027 was the lone front-gate survivor and still REJECT on its train gate. Same
verdict applies on wider-spread crosses. *Not reopened.*

### C. Non-time-bar / microstructure (range/vol bars, overshoot, participation)
**Status: EXPLORED → RETIRED.** Lane formally retired (H16/H03 FAIL). Crosses are
a *named* reopen condition, but **only via a fresh pre-registered screen**, and
the cost wall is *higher* on crosses (wider, fatter-tailed). *Reopenable in
principle, low priority — Phase 3/4 treat with suspicion.*

### D. Cross-sectional momentum (rank N instruments, long winners / short losers)
**Status: PARTIAL → underpowered, now NEWLY STRENGTHENED.** C016 (weekly
cross-sectional momentum) ran on USD majors but every pair shares USD, so the
"cross-section" was really a **USD-strength bet** with ~7 collinear names.
Crosses provide **non-collinear legs** → a genuine cross-section over currencies
becomes possible for the first time. *Materially reopened by breadth.*

### E. Currency-strength / dispersion (estimate per-currency strength, trade spread)
**Status: NEW (breadth-enabled).** Estimating a per-currency strength index
requires multiple pairings per currency; with majors-only every estimate is
USD-anchored and degenerate. With 15 instruments spanning 8 currencies and
overlapping legs, a **least-squares / average-of-pairs currency-strength vector**
is computable. *Structurally new.*

### F. Triangular / no-arbitrage consistency (e.g. EURUSD·USDJPY vs EURJPY)
**Status: NEW.** Requires a closed triangle of three co-quoted instruments — by
definition impossible with only USD-legged majors (no cross to close the
triangle). Now **9+ triangles closable**. *Structurally new.* (NB: true arbitrage
is latency/cost-defeated for a retail backtest; the *research* angle is
consistency-of-drift / lead-lag, not arb capture — flagged for Phase 3.)

### G. Carry / financing-driven (long high-yield vs low-yield currency)
**Status: PARTIAL → was data-blocked, now data-PRESENT but financing-UNMEASURED.**
C031 (vol-managed TSMOM) found financing ≈4× spread and the book collapsed to a
USD bet; classic carry (AUD_JPY, NZD_JPY, EUR_JPY) was **impossible** on majors.
Crosses supply real carry legs, **but the actual swap/financing rates are not yet
ingested** — the registry carry figures are two-legged *estimates*. *Reopened in
principle; gated on a financing-data prerequisite (Phase 5/6).* 

### H. Relative-value / cointegration (stationary spread between related pairs)
**Status: PARTIAL → underpowered, now NEWLY STRENGTHENED.** C028 (RV spread
reversion) was LIKELY_SELECTION_NOISE — half-lives ≫ hold, two-leg cost hostile,
and the candidate spreads were USD-major combinations (collinear). Crosses add
**economically-motivated** spreads (EUR_JPY vs GBP_JPY share the JPY leg;
EUR_GBP vs EUR_USD/GBP_USD triangle) with cleaner cointegration rationale.
*Reopened by breadth, but inherits C028's two-leg-cost caution.*

### I. Cross-pair confirmation / lead-lag / leadership (one pair leads another)
**Status: NEW.** Asking whether, e.g., EUR_USD leads EUR_JPY, or GBP_JPY leads
GBP_USD, requires non-collinear pairs sharing a leg. Majors-only gives only
USD-anchored lead-lag (already part of the USD-bet critique). *Structurally new.*

### J. Factor replication (re-screen a validated factor on independent data)
**Status: NEW (the headline use).** C1 is the only GENUINE factor; it was
discovered/validated only on collinear USD majors, leaving a residual-USD
question. Crosses are non-collinear → a **fresh, pre-registered C1 replication**
can settle whether C1 is a real multi-TF-confluence effect or a USD-regime
artifact. *Structurally new and explicitly sanctioned.* (Replication ≠ re-tune.)

### K. Volatility / regime structure (vol clustering, regime conditioning)
**Status: EXPLORED → no monetizable edge, plus NEW basket angle.** Single-pair
vol is predictable but not monetizable (C1 high-vol path, vol-compression thread
all REJECT). **New** with crosses: cross-currency **vol dispersion** and
**safe-haven (JPY/CHF) vs risk (AUD/NZD) regime baskets**. *Partially reopened as
a basket/dispersion theme, not as single-pair vol.*

### L. Macro / event / calendar
**Status: EXPLORED → data-blocked (no real rate leg, ~5y, no breadth).** Crosses
add breadth but **not** history or a real rate leg, so the binding limiters
persist. *Not meaningfully reopened by crosses alone.*

---

## 3. Summary table

| # | Category | Status | Reopened by crosses? |
|---|----------|--------|----------------------|
| A | Single-instrument directional | EXPLORED → REJECT | No (re-tune trap) |
| B | Single-instrument mean-reversion | EXPLORED → REJECT | No |
| C | Non-time-bar / microstructure | EXPLORED → RETIRED | Marginal (fresh screen only) |
| D | Cross-sectional momentum | PARTIAL → underpowered | **Yes (breadth)** |
| E | Currency-strength / dispersion | NEW | **Yes (structural)** |
| F | Triangular consistency | NEW | **Yes (structural)** |
| G | Carry / financing | PARTIAL → data-blocked | **Yes, gated on financing data** |
| H | Relative-value / cointegration | PARTIAL → underpowered | **Yes (breadth)** |
| I | Cross-pair lead-lag / leadership | NEW | **Yes (structural)** |
| J | Factor replication (C1) | NEW | **Yes (sanctioned)** |
| K | Volatility / regime (basket) | EXPLORED single-pair / NEW basket | Partially (basket only) |
| L | Macro / event / calendar | EXPLORED → data-blocked | No |

**Reading:** the cross data **opens or strengthens 7 categories (D, E, F, G, H,
I, J)** and partially reopens one more (K-basket). It does **not** reopen the
four single-instrument / microstructure / macro categories where the majors
already failed on cost, history, or microstructure walls — those remain closed
because crosses add **breadth only**.

Phase 2 generates candidate factor families from the seven-plus reopened
categories; Phase 3 fences off any family that is really a category-A/B/C/L
re-tune wearing a cross costume.
