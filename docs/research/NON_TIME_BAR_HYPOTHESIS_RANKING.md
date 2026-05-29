# Non-time-bar hypothesis ranking & screening

**Sprint:** `research-external-non-time-bar-thesis-discovery-001` · Phase 5
**Type:** screening using the lab's edge-discovery principles. No backtests, no PnL.

> Each of the 24 catalog hypotheses is scored on 8 dimensions and classified
> `REJECT_IMMEDIATELY` / `LOW_PRIORITY` / `PROMISING` / `FRONT_GATE_CANDIDATE`.
> Scores are qualitative (H/M/L) and reflect *prior* reasoning, not any run.
> Screening principles are those of
> [`FUTURE_CAMPAIGN_REENTRY_GATES.md`](FUTURE_CAMPAIGN_REENTRY_GATES.md) and
> [`PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md`](PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md):
> beat a *matched* null post-cost, be cost-feasible on the *traded* cell, every filter
> must add edge, and not be a single-pair / selection-noise / rejected-family artifact.

For "overlap w/ rejected": **L** = low overlap (good, distinct); **H** = high overlap
(bad, resembles a rejected family). For cost-sensitivity & turnover: **L** is good.

---

## 1. Scoring table

| id | idea | orig. | testability | impl cost | data avail | robustness | overlap↓ | turnover↓ | cost-sens↓ | class |
|---|---|---|---|---|---|---|---|---|---|---|
| H01 | Dollar-bar trend persistence (TSMOM event-time) | H | H | M | yes | M | L | M | M | **FRONT_GATE_CANDIDATE** |
| H02 | Activity-surprise (dollar/clock) conditioning | M | M | M | yes | M | L | M | M | PROMISING |
| H03 | Thin-move fade (travel ÷ volume) | H | H | M | yes | M | L | M | M | **FRONT_GATE_CANDIDATE** |
| H04 | Dollar-bar RV-ratio regime gate | M | M | M | yes | M | L | L | L | PROMISING |
| H05 | Symmetric vol-scaled CUSUM event drift | H | H | M | yes | M | L | M | M | **FRONT_GATE_CANDIDATE** |
| H06 | CUSUM event-storm conditioning | M | M | M | yes | M | L | L | L | PROMISING |
| H07 | CUSUM up/down asymmetry skew | M | M | M | yes | L | M | M | M | LOW_PRIORITY |
| H08 | Bar-duration (ACD) regime gate | H | M | M | yes | M | L | L | L | PROMISING |
| H09 | Duration-shock continuation | M | M | M | yes | M | L | M | M | PROMISING |
| H10 | BVC-proxy imbalance bars | M | M | H | proxy | L | M | H | H | LOW_PRIORITY |
| H11 | Close-location micro-pressure | M | M | M | proxy | L | M | M | M | LOW_PRIORITY |
| H12 | Spread-state (liquidity-regime) filter | M | H | L | yes | H | L | L | **L** | **FRONT_GATE_CANDIDATE** (as filter) |
| H13 | Cross-pair activity lead-lag (event-time) | H | M | H | yes | M | L | M | M | PROMISING |
| H14 | Common-vol-factor regime gate | M | M | H | yes | M | L | L | L | PROMISING |
| H15 | USD-bloc activity breadth | M | L | H | yes | L | M | M | M | LOW_PRIORITY |
| H16 | Overshoot-exhaustion fade | H | H | L | yes | M | L | M | M | **FRONT_GATE_CANDIDATE** |
| H17 | Multi-threshold (gap) regime | M | M | L | yes | M | L | L | L | PROMISING |
| H18 | Bar-shape (body/range) continuation | L | M | L | yes | L | M | M | M | LOW_PRIORITY |
| H19 | Vol-scaled sizing overlay | M | M | M | yes | M | L | L | L | PROMISING |
| H20 | Triple-barrier exit horizon | L | M | M | yes | L | H | M | M | LOW_PRIORITY |
| H21 | Cross-pair session-open impulse | M | M | M | yes | L | M | M | M | LOW_PRIORITY |
| H22 | Asian-range structural bar | L | M | M | yes | L | M | M | M | LOW_PRIORITY |
| H23 | Wider range-bar MTF breakout (25–30p) | L | H | L | yes | L | **H** | M | M | **REJECT_IMMEDIATELY** |
| H24 | Renko / P&F trend-follow | L | M | L | proxy | L | H | M | M | **REJECT_IMMEDIATELY** |

## 2. Classification rationale

### REJECT_IMMEDIATELY (2)
- **H23** — a 25–30-pip version of C029's MTF-breakout rule is a **threshold retune of a
  rejected family** (anti-pattern §3.1). The feasibility study made it *cost-feasible*,
  not *edged*; running it would relearn C029's lesson. Reject.
- **H24** — renko/P&F have **no edge evidence** and carry the **virtual-price backtest
  hazard** (Phase 3). Reject.

### LOW_PRIORITY (8) — H07, H10, H11, H15, H18, H20, H21, H22
Reasons: depend on an **unproven flow proxy** (H10, H11, H07 — could manufacture
spurious signal), are **single-pair/structure ideas the repo already found null or
fragile** (H21, H22 echo the failed USD_JPY London lead; H20 echoes the null exit
edge of C018/C019), or are **low-novelty candlestick re-skins** (H18) / **low
testability** (H15). Revisit only with better data or a new angle.

### PROMISING (9) — H02, H04, H06, H08, H09, H13, H14, H17, H19
Genuinely distinct, data-available *conditioning/sizing or structural* ideas that are
**not yet sharp enough to be a standalone front-gate thesis** but are strong building
blocks. H08 (conditional duration) and H13 (cross-pair activity lead-lag) are the
strongest of this tier and are the first reserves if a front-gate candidate falls.

### FRONT_GATE_CANDIDATE (5) — H01, H03, H05, H12, H16
These are the only ideas that (a) are clearly **distinct from every rejected family**,
(b) are **testable now** on existing data, (c) **do not re-bet raw FX direction** in
the way the repo has repeatedly found null (or, for H01, bet on the one externally-
replicated directional effect — TSMOM — in a new clock), and (d) carry an **external
anchor** strong enough to justify a front-gate screen:
- **H01** — TSMOM is the most replicated systematic effect; event-time framing is novel.
- **H03** — thin-move fade is a clean microstructure reversion intuition using both
  clocks; cheap to specify; no prior repo test.
- **H05** — symmetric vol-scaled CUSUM drift is the textbook event bar the repo never
  built; post-event drift is a falsifiable, matched-null-testable claim.
- **H16** — overshoot-exhaustion fade reuses geometry we *already compute*; lowest
  implementation cost; directly falsifiable.
- **H12** — spread-state filter is grounded in **our own** feasibility evidence, has the
  **lowest cost-sensitivity and overfit risk**, and is exactly a **G4 filter-ablation**
  test (does the filter add edge?). It is a *filter/overlay*, not a standalone signal —
  so it graduates as a **conditioning layer to combine with H01/H03/H05/H16**, not as a
  lone entry rule.

## 3. Counts

| class | n |
|---|---|
| REJECT_IMMEDIATELY | 2 |
| LOW_PRIORITY | 8 |
| PROMISING | 9 |
| FRONT_GATE_CANDIDATE | 5 |
| **total** | **24** |

## 4. Screening cautions carried forward

- **Selection-noise discipline (C028):** the 5 front-gate candidates were chosen by
  *reasoning*, not by screening many variants and keeping the best. If, at front-gate
  time, several thresholds/pairs are swept, the `multiple_comparison` best-of-N test
  applies and a "winner" that doesn't beat best-of-N noise is **not** evidence.
- **Cost-feasibility first (C025/C026/C029):** every candidate must trade a cell with
  cost/risk ≤ 0.05 (range ≥ 25–30 pip / volatility ≥ 50 pip per the feasibility study),
  and H12 should be applied so trading concentrates in low-spread sessions.
- **Matched null, not generic null (C027):** each candidate must beat the
  *structure-matched* null on its claimed source of edge, on more than one pair.
