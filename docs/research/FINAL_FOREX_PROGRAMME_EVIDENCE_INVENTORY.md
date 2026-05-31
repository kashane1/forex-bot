# Final Forex Programme — Evidence Inventory (Phase 1)

**Sprint:** `research-programme-direction-after-carry-001`
**Type:** Documentation only.
**Date:** 2026-05-31
**Purpose:** Classify every major research effort by its terminal verdict, so the direction decision rests on a complete, honest ledger.

## Classification scheme

- **rejected** — tested to a verdict; the effect does not exist or does not predict.
- **failed replication** — an apparent effect did not reproduce out-of-sample / out-of-universe.
- **real but weak** — a genuine effect exists but is too small to clear cost, or is single-name / untimed.
- **cost-defeated** — a real gross effect exists but is smaller than round-trip cost (+financing).
- **infrastructure-only** — built capability; produced no edge claim.

> Note: several efforts carry two tags (e.g. *real but weak* **and** *cost-defeated*). The primary tag is the one that ended the lane; secondary tags are noted.

---

## A. Major-pair strategy campaigns (C001–C031)

| Effort | Description | Classification | Note |
|--------|-------------|----------------|------|
| C001–C021 (pullback / MTF families) | Major-pair entry-signal strategies | rejected | No entry-signal edge; families retired |
| C022 / C023 USD_JPY microstructure | Entry + post-entry management | rejected | Direction null (~0.49); rollover cost-toxic |
| CAMPAIGN_025 (M5 Donchian + HTF breakout) | Breakout scaffold | rejected | Family closed via C026 ladder |
| CAMPAIGN_026 (timeframe ladder M3–M30) | Cost/expectancy vs timeframe | cost-defeated | Best M30 still net-negative; pure cost gradient |
| CAMPAIGN_027 (H4 z-score reversion) | The one front-gate survivor | rejected | REJECT_TRAIN_GATE; expectancy wafer-thin; AUD-dominated |
| CAMPAIGN_028 (relative-value / cointegration spread) | Spread reversion screen | rejected | LIKELY_SELECTION_NOISE; no scaffold earned |
| CAMPAIGN_029 (USD_JPY 10-pip range bars) | First non-time-bar lane | cost-defeated | Gross +0.084R → net −0.019R |
| CAMPAIGN_031 (vol-managed TSMOM portfolio) | Portfolio momentum | cost-defeated | Pre-cost Sharpe +0.32 → net −0.07; financing ≈4× spread; WITHIN_NULL |

**Family verdict:** the entire numbered-campaign programme produced **zero** approved strategies. Failure mode is split between *no edge at all* (rejected) and *real-gross-but-cost-defeated*.

---

## B. Factor discovery & validation (C1, S1–S5)

| Effort | Description | Classification | Note |
|--------|-------------|----------------|------|
| C1 factor validation (MTF confluence fade) | Fade H4+H1+M15 bullish alignment | real but weak / cost-defeated | Genuine factor; net-of-cost negative on all pairs |
| C1 cross replication (S1) | Re-test C1 on 8 non-USD crosses | failed replication | 60min only 2/4 negative; lone hit = single-pair noise → C1_ARTIFACT |
| S2 currency-strength validation | Per-currency strength index → forward returns | rejected | 0/80 null cells clear; strength persists but doesn't predict |
| S3 currency-strength ranking | Trade the S2 ranking | rejected | Pre-falsified by S2 (trades a non-predictive ranking) |
| S4 cross relative-value (triangular no-arb) | Residual reversion across 8 triangles | real but weak | Genuine no-arb reversion but ~10× inside cost band; first non-rejected factor |
| S5 (carry-adjacent shortlist slot) | — | rejected/moot | Financing-data-blocked at the time; superseded by dedicated carry path |

**Family verdict:** the S1–S5 shortlist is exhausted. S4 is the programme's only genuinely-real factor, but it lives inside the no-arbitrage band (sub-cost). C1 was genuine on USD majors but did not replicate on crosses.

---

## C. Non-time-bar research

| Effort | Description | Classification | Note |
|--------|-------------|----------------|------|
| Non-time-bars infra (range / volatility bars) | Lookahead-free bar builders | infrastructure-only | Recommended 10-pip range / 20-pip true-range |
| Non-time-bar feasibility | Cost-feasibility across thresholds | infrastructure-only | Cost ~1/threshold; feasibility ≠ edge |
| Non-time-bar thesis discovery | 24 hypotheses → 5 shortlist | infrastructure-only | Alt bars are a sampling fix, not an edge (web-cited) |
| H16 overshoot-exhaustion front gate | Conditional fade screen | rejected | No bucket gradient; reversion ≈0.50; null-indistinguishable |
| H03 thin-move front gate | Participation-tertile fade screen | rejected | Weak tilt, GBP-absent, cost-defeated; directional non-time-bar search RETIRED |

**Family verdict:** non-time bars are a legitimate sampling tool but yielded no edge on this corpus. The directional/microstructure non-time-bar lane is formally retired (reopen only with new data/thesis).

---

## D. Carry

| Effort | Description | Classification | Note |
|--------|-------------|----------------|------|
| Financing/rate-data ingestion | FRED OECD 3M interbank rates → carry differential | infrastructure-only | READY_WITH_LIMITATIONS; interbank ≠ broker financing |
| Carry factor validation (gross existence) | Monthly horizons, matched nulls, gross-only | real but weak | Mechanical accrual; spot-predictive leg null; single-name (JPY); untimed; financing-defeated by construction |

**Family verdict:** carry premium exists but is not tradable on this corpus. Financing-aware carry research judged not worthwhile (the C031 financing wall would erase the gross premium).

---

## E. Cross-universe expansion (infrastructure & data)

| Effort | Description | Classification | Note |
|--------|-------------|----------------|------|
| Non-USD cross ingestion + cost models | Additive cross registry, two-legged cost | infrastructure-only | Capability only |
| Non-USD cross data population | 14.7M M1 rows, 8 crosses, parity PASS | infrastructure-only | Crosses wider/fatter-tailed than majors |
| Cross factor-discovery planning | 24 families → 5 shortlist | infrastructure-only | Crosses added breadth only, not cost relief |

**Family verdict:** expansion succeeded as infrastructure; it added breadth (history/microstructure walls unchanged) but **did not move the cost wall**.

---

## F. Project-level reviews & synthesis (docs-only)

| Effort | Classification | Note |
|--------|----------------|------|
| Forex corpus viability review | infrastructure-only (analysis) | CONTINUE_ONLY_WITH_NEW_EXTERNAL_THESIS |
| Multi-market front-gate design | infrastructure-only (analysis) | Decided to add crosses first |
| Cross-factor programme synthesis | infrastructure-only (analysis) | Chose Option A (carry data ingest) |
| Strategy-search-pause memos (USD_JPY thread) | infrastructure-only (analysis) | PAUSE; restart needs new thesis/data |

---

## Tally

| Classification | Count (major efforts) |
|----------------|------------------------|
| rejected | 9 |
| failed replication | 1 (C1 cross) |
| real but weak | 3 (C1, S4, carry) |
| cost-defeated | 4 (C026, C029, C031; C1 secondary) |
| infrastructure-only | 12+ |

(Counts treat each lettered/numbered effort as one unit; some carry secondary tags. The exact integer is less important than the shape.)

---

## What the inventory proves

1. **No effort reached "approved strategy."** Not one.
2. **The few genuinely-real effects (C1, S4, carry) are all either cost-defeated, sub-cost-band, or single-name/untimed.** None is binding.
3. **The recurring terminal cause is cost**, not absence of ideas. When an effect was real, cost killed it; when cost was survivable, the effect wasn't real.
4. **Infrastructure is mature and not the bottleneck** — the lab, null benchmarks, cost models, cross data, non-time bars, and rate data all work.

The honest conclusion: **the in-repo forex strategy search is exhausted under the current corpus's cost structure.**
