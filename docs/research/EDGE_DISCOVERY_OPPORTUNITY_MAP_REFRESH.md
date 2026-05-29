# EDGE_DISCOVERY_OPPORTUNITY_MAP_REFRESH

**Status:** diagnostic / market-fact map (Phase 2 of
`research-edge-discovery-front-gate-idea-selection-001`). Market facts only —
no edge claim, no strategy, no campaign, no approval. A cheap cost cell is *not*
an edge; it is only a precondition.

> Builder: `research/edge_discovery/front_gate_idea_selection/build_opportunity_map.py`
> Artifacts: `research/edge_discovery/front_gate_idea_selection/opportunity_map_*.{csv,json}`,
> `cost_feasibility_flags.json`. Reuses the lab's `cost_feasibility`, `costs`,
> `cost_atlas.metrics`. Local store `data/campaign_002.sqlite3`.

---

## Coverage

7 majors × {H4 (~9,937 bars/pair), H1 (~39,700 bars/pair)}, 2020-01 → 2026-05.
Spread/ATR ratio = bid-ask spread ÷ ATR(14) per bar; cells are medians.
Hostile threshold = 0.25 (lab default; M5 ≈ 0.45 was rejected as hostile).

## Cost-feasibility result (the headline)

**Every H1 and H4 cell on all seven majors is `COST_FEASIBLE`. Zero hostile
cells** (pair×TF and pair×TF×session). Ratios:

| Timeframe | spread/ATR range | interpretation |
|---|---|---|
| H4 | 0.043 (USD_JPY) → 0.105 (NZD_USD) | very feasible |
| H1 | 0.091 (USD_JPY) → 0.221 (NZD_USD) | feasible; NZD_USD H1 borderline |

This is the decisive contrast with the rejected lower-TF Donchian work: C025's
M5 was ≈ 0.45 (hostile) and C026's M3 ≈ 0.59. **H4/H1 are 3–10× cheaper in
spread/ATR terms.** Cost is *not* the binding constraint at this timeframe band —
so any null result here will be a genuine *no-edge* result, not a cost mirage.

### Cheapest pair / timeframe
1. USD_JPY H4 — 0.043 · 2. GBP_USD H4 — 0.052 · 3. AUD_USD H4 — 0.054 ·
4. EUR_USD H4 — 0.055 · 5. USD_CAD H4 — 0.065. (All H4 < all H1.)

### Cheapest pair / timeframe / session
USD_JPY H4 london_ny_overlap (0.037), USD_JPY H4 london (0.040), USD_JPY H4
asian (0.040), GBP_USD H4 overlap (0.046), GBP_USD H4 london (0.047),
EUR_USD H4 overlap (0.049). **USD_JPY occupies the three cheapest cells.**

### Most volatile (median ATR in pips)
USD_JPY H4 (41.4) > GBP_USD H4 (36.4) > USD_CAD H4 (29.9) > EUR_USD H4 (27.9)
> AUD_USD H4 (25.5). USD_JPY is simultaneously **cheapest and most volatile** —
the rare pair where cost is low relative to range.

### Cost-hostile combinations to avoid
None are hostile by the 0.25 gate. The *relatively* worst (lowest opportunity
score, watch on tight stops): **NZD_USD H1 (0.221)**, USD_CHF H1 (0.153),
USD_CAD H1 (0.134). On H4 the NY-session cells carry the widest tails (the
pre-existing H4 cost atlas already flags `*/ny` p90 spread/ATR elevation), so
H4-NY entries should use ATR-scaled, not fixed, stops.

### Cost in R (drag, not edge)
At a 1.0×ATR stop, round-trip cost consumes **3–5% of R on H4** and **7–16% on
H1** (NZD_USD H1 the outlier at ~25%). Tradeable, but a reversion idea targeting
< 0.3R is fighting a meaningful headwind — favors targets ≥ 1R or H4.

## Volatility / session behaviour

Median ATR(14) by session is **nearly flat** across Asia/London/overlap/NY:

| TF | asian | london | overlap | ny |
|---|---|---|---|---|
| H4 | 27.8 | 28.1 | 29.1 | 28.5 |
| H1 | 12.9 | 12.8 | 14.4 | 14.6 |

Vol *regime* clustering is strong (high-vol ATR ≈ 2× low-vol: H4 39.7 vs 20.9;
H1 19.6 vs 9.7), but **session-of-day expansion is weak** — and on H1 the
**London bucket ATR (12.8) essentially equals the Asian bucket (12.9)**; the
modest expansion is into the overlap/NY (14.4/14.6).

> **Measurement caveat:** ATR(14) is a 14-bar smoother, so it blurs intraday
> session boundaries and *understates* a genuine opening-range jump. A real
> "open expansion" test needs per-bar range at the open bar, not ATR(14). The
> flatness above is therefore evidence *against a large, smooth* session-vol
> gradient, not a refutation of a sharp single-bar open pop — but it already
> dampens the prior for "London open expansion" as a strong directional edge.

## Does USD_JPY deserve further single-pair screening?

**Yes, as a cost-advantaged screening venue — but with the revival guard.**
USD_JPY is unambiguously cost-advantaged (cheapest at both TFs, three cheapest
session cells) and the most volatile, so its cost/vol ratio is best-in-universe.
That makes it the *cheapest place to look for an edge*, which is exactly why it
keeps surfacing. But prior USD_JPY threads (microstructure, vol-compression→
expansion, macro-context) were all **null/exhausted** — the cost advantage has
never been accompanied by directional edge. So USD_JPY is retained as a
**single-pair concentration overlay** on the multi-pair probes (Phase 3), not as
a standalone thesis, and any single-pair-only survivor must clear the
multiple-comparison / single-pair-fragility gate before it could be eligible.

## M15/M30/H1/H4 vs M3/M5 as screening targets

- **M3/M5: rejected and unavailable.** Cost-hostile (C025/C026) *and* no local
  data (no M1 to materialize from). Out of scope.
- **M15/M30: cost-plausible but unavailable.** C026 found M15≈0.23 / M30≈0.15
  were not cost-bound, but there is no local M15/M30/M1 data → **COMPATIBILITY_
  BLOCKED** for screening here.
- **H1/H4: the correct screening targets.** Native, full-coverage, and uniformly
  cost-feasible. **H4 is the cheaper and structurally cleaner target** (lower
  cost-in-R, less micro-noise); **H1 adds session resolution** for session/range
  ideas. Recommendation: screen on **H4 primarily, H1 for session-timed ideas.**

## Which idea families are compatible with the market facts?

| Family | Verdict from the map | Rationale |
|---|---|---|
| 6 z-score reversion + regime | **Compatible (H4)** | feasible cost, strong vol-regime clustering to filter on |
| 7 failed-breakout fade | **Compatible (H4/H1)** | feasible; reversion class |
| 9 high-vol exhaustion→rev. | **Compatible but cost-watch** | high-vol cells have widest spreads (adverse at signal) |
| 1 Asia range breakout | Compatible (H1) | feasible; but session-vol gradient is weak |
| 2 Asia range fade | Compatible (H1) | feasible; reversion class |
| 4 NY open cont./rev. | Compatible (H1) | overlap/NY is where mild expansion actually is |
| 8 vol compression→expansion | Compatible (H4/H1) but **direction-risk** | vol clustering real; direction historically null |
| 3 London open expansion | **Weakly supported** | H1 London ATR ≈ Asian ATR — little open expansion |
| 5 USD_JPY probe | Overlay only | cost-advantaged venue, no standalone edge prior |
| 10 event-window | Compatible but likely sparse | single fixture; cost blows out on events |
| 11 carry/financing | **Data-blocked** | no carry-rate table locally |
| 12 opportunity mining | = this phase | — |

**Phase-3 implication:** the market facts favor **H4 reversion-class probes**
(z-score reversion + regime, failed-breakout fade) and an **H1 session probe**
(Asia-range breakout / NY-open), with a **vol compression→expansion direction
probe** included specifically to test the recurring "expansion yes, direction
no" pattern at a fresh TF band. The weak session-vol gradient demotes
"London open expansion" as a standalone candidate. No edge is claimed by any of
this — Phase 3 measures forward-return information; Phase 4 tests it against a
matched null.
