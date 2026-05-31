# Forex Strategy-Search Programme — Final Evidence Inventory

**Sprint:** `research-forex-strategy-search-archive-001` · Phase 1
**Type:** Evidence classification. Docs-only. No new analysis.
**Date:** 2026-05-31
**Supersedes:** `FINAL_FOREX_PROGRAMME_EVIDENCE_INVENTORY.md`, `COMPLETE_PROGRAMME_EVIDENCE_INVENTORY.md` (as the programme terminal ledger)

---

## Classification scheme

| Tag | Meaning |
|-----|---------|
| **rejected** | Tested to a verdict; effect absent, within-null, or sign-incoherent |
| **failed replication** | Apparent effect did not generalize out-of-sample / out-of-universe |
| **real but weak** | Genuine effect exists but sub-cost, single-name, untimed, or financing-defeated |
| **cost-defeated** | Real gross effect smaller than round-trip cost (+ financing where applicable) |
| **infrastructure-only** | Built capability or data; no edge claim |

Some efforts carry a primary and secondary tag; the primary tag is what ended the lane.

---

## A. Strategy campaigns (C001–C031)

| ID | Description | Classification | Terminal note |
|----|-------------|----------------|---------------|
| C001–C002 | EMA + Donchian trend baseline | rejected | −0.085 R on real H4 data |
| C003 | ADX-14 trend gate variant | rejected | ADX gate did not rescue baseline |
| C004 | Volatility breakout (ATR compression) | rejected | Worst of trend/breakout families |
| C006 | D1 daily trend | infrastructure-only | Engine blocked — invalid D1 fill model |
| C007 | H4 pullback continuation | rejected | Train/val both negative |
| C008 / C009 | Regime-filtered z-score mean reversion | cost-defeated | Train fail; val uplift unconfirmed (lockbox sealed) |
| C010 | Asian/London session breakout | rejected | 0/8 fold pass; −36.6 % aggregate |
| C011 | Random entry null anchor | infrastructure-only | Canonical null baseline (−0.0029 R) |
| C012 | ATR-percentile regime switcher | rejected | Turnover amplification anti-pattern |
| C013 | Cross-pair currency strength rotation | rejected | 7,940 trades; worse than null |
| C014 | Calendar event window anomaly | rejected | NFP counter-trend falsified |
| C015 | Failed breakout reversal | cost-defeated | Deduped; WITHIN_NULL |
| C016 | Weekly cross-sectional momentum | rejected | USD bet; collinear |
| C017 | Weekly volatility contraction breakout | rejected | Deduped; NO_RELIABLE_ARCHETYPE cluster |
| C018 | Protective stop on C008 entries | rejected | Exit tweak cannot rescue absent entry edge |
| C019 | Thesis-invalidation exit on C008 | rejected | Same — exit layer falsified on train |
| C020 | MTF confluence pullback (H4) | rejected | Train −0.035 R |
| C021 | LTF MTF confluence (M15) | rejected | Train −0.017 R; higher turnover, no rescue |
| C022 / C023 | H4/H1 pullback resolution family | rejected | Entry signal null; family RETIRED |
| C025 | M5 Donchian + HTF breakout matrix | rejected | 0/16 train candidates; spread/ATR ≈ 0.45 |
| C026 | Timeframe ladder M3–M30 | cost-defeated | Best M30 still net-negative; pure cost gradient |
| C027 | H4 filtered z-score reversion | rejected | Last front-gate survivor; REJECT_TRAIN_GATE |
| C028 | Relative-value / cointegration spread screen | rejected | LIKELY_SELECTION_NOISE |
| C029 | USD_JPY 10-pip range-bar MTF breakout | cost-defeated | Gross +0.084R → net −0.019R |
| C031 | Vol-managed TSMOM portfolio | cost-defeated | Pre-cost Sharpe +0.32 → net −0.07; financing ≈4× spread |

**Campaign family verdict:** 31 numbered campaigns; **zero approved strategies**.

---

## B. Factor discovery & validation

| ID | Description | Classification | Terminal note |
|----|-------------|----------------|---------------|
| C1 validation | MTF confluence fade (H4+H1+M15) | real but weak / cost-defeated | Genuine on USD majors; net-of-cost negative all pairs |
| C1 high-vol front gate | Vol-conditioned directional screen | cost-defeated | FAIL_FRONT_GATE; net-negative 3/3 |
| S1 — C1 cross replication | Frozen C1 on 8 non-USD crosses | failed replication | USD-regime artifact; C1_ARTIFACT |
| S2 — currency strength | Per-currency strength → forward returns | rejected | 0/80 null cells clear; persists but doesn't predict |
| S3 — strength ranking | Trade S2 ranking | rejected | Pre-falsified by S2 |
| S4 — cross relative-value | Triangular no-arb residual reversion | real but weak | Genuine; ~10× inside cost band; staleness-bound |
| S5 — regime gate | Overlay on surviving generator | rejected | Moot — no surviving generator |
| Carry (spot) | Monthly horizons; gross existence study | real but weak | Mechanical accrual; spot-predictive leg null; JPY-concentrated |
| Carry (futures) | Frozen carry on CME price returns | rejected | **CARRY_DOES_NOT_SURVIVE_IN_FUTURES**; h3 t = 0.09 |

**Factor family verdict:** S1–S5 shortlist exhausted. S4 is the only non-rejected factor; it is economically insignificant. Carry — the canonical FX factor — is non-predictive even in a financing-free venue.

---

## C. Front gates & cheap screens

| Gate | Hypothesis family | Classification | Terminal note |
|------|-------------------|----------------|---------------|
| Edge-discovery front gate | 12 idea families on H1/H4 majors | infrastructure-only | 1 CAMPAIGN_ELIGIBLE → became C027 → REJECT |
| C1 high-vol front gate | Directional, vol-conditioned | cost-defeated | FAIL_FRONT_GATE |
| H16 overshoot-exhaustion | Microstructure conditional fade | rejected | Reversion ≈ 0.50; null-indistinguishable |
| H03 thin-move | Participation-tertile fade | rejected | Lane RETIRED |
| C028 RV spread screen | Cointegration spread reversion | rejected | LIKELY_SELECTION_NOISE |
| C031 TSMOM screen | Vol-managed portfolio momentum | cost-defeated | WITHIN_NULL + financing-defeated |

**Front-gate verdict:** the cheap-falsification pipeline worked — every screened idea that earned a scaffold was eventually rejected at train gate or earlier. No front gate produced an approved strategy.

---

## D. Venue studies

| Venue | Scope | Classification | Terminal note |
|-------|-------|----------------|---------------|
| OANDA spot majors (7 pairs) | Primary M1/H4 corpus ~2021–2026 | infrastructure-only | ~1.6–1.7 pip spread; structural cost wall |
| OANDA non-USD crosses (8 pairs) | Additive cross expansion | infrastructure-only | Breadth added; cost wall unchanged |
| Non-time-bar (range/vol bars) | Alt-clock sampling + feasibility | infrastructure-only | 10-pip range recommended; directional lane retired |
| FX futures (CME, 7 contracts) | EOD continuous; carry diagnostic | infrastructure-only (data) / rejected (carry) | Financing wall removed; carry still null |
| Macro / FRED context | Slow conditioning features | rejected | No actionable tradeability; JP leg absent |

**Venue verdict:** widening universe (crosses) and changing venue (futures) did not produce a tradable edge. Futures confirmed the binding limit is idea quality, not merely retail spot cost.

---

## E. Replication & integrity studies

| Study | Classification | Terminal note |
|-------|----------------|---------------|
| C1 cross replication (S1) | failed replication | Genuine majors effect = USD artifact |
| Deduped C008/C009 forensic replay | infrastructure-only | Descriptive claims confirmed; verdicts unchanged |
| C011 deduped null baseline | infrastructure-only | Promoted canonical null (−0.0029 R) |
| C015 deduped rerun | cost-defeated | Contamination removed; WITHIN_NULL stands |
| FX futures carry diagnostic | rejected | Spot predictive leg ≈ 0 confirmed under fair venue |
| Backtrader parity drills (C015, C029, etc.) | infrastructure-only | Bookkeeping verified; rejects are strategy's, not artifact's |

---

## F. Diagnostics & pause memos (non-campaign)

| Effort | Classification | Terminal note |
|--------|----------------|---------------|
| USD_JPY microstructure entry diagnostic | rejected | Best stable AUC |0.5−0.5| = 0.016 |
| USD_JPY post-entry trade management | rejected | Early-exit counterfactuals reduce expectancy |
| Volatility compression → expansion | rejected | Direction null; monetization loses on train |
| London compression-continuation | rejected | Intrabar stop + Bonferroni ×12 kills lead |
| Macro/rates/calendar tradeability | rejected | PAUSE_STRATEGY_RESEARCH trigger |
| M1 HTF confluence matrix | rejected | No binding cell survives cost |
| Exit asymmetry cross-campaign | infrastructure-only | Confirms exit tweaks don't rescue entry null |

---

## G. Infrastructure (preserved assets)

| Asset | Classification | Status |
|-------|----------------|--------|
| Edge-discovery lab + null/cost/MC gates | infrastructure-only | Working |
| Walk-forward harness (8-fold) | infrastructure-only | Working |
| Backtrader secondary parity lane | infrastructure-only | Working |
| Local Postgres OANDA data store | infrastructure-only | Working |
| Cross registry + two-legged cost model | infrastructure-only | Working |
| Carry/rate data (FRED OECD 3M) | infrastructure-only | READY_WITH_LIMITATIONS |
| Non-time-bar builders (range/vol) | infrastructure-only | Working |
| FX futures registry + ingest + diagnostic | infrastructure-only | Working |
| Research freeze gates | infrastructure-only | Enforced (`approved: []`) |
| Financing model + observed-capture pilot | infrastructure-only | Working |

---

## H. Tally

| Classification | Count (major efforts) |
|----------------|----------------------:|
| rejected | 28+ |
| failed replication | 1 (C1 cross) |
| real but weak | 3 (C1, S4, spot carry) |
| cost-defeated | 7 (C008/C009, C026, C029, C031, C1 secondary, C1 front gate, C015) |
| infrastructure-only | 15+ |

Exact integers matter less than the shape.

---

## I. What the inventory proves

1. **No effort reached "approved strategy."** Not one, across 31 campaigns and 5 factor slots.
2. **The few genuinely-real effects (C1, S4, spot carry) are all cost-defeated, sub-cost-band, single-name, untimed, or non-predictive in a fair venue.**
3. **The recurring terminal cause evolved from "cost-defeated (maybe fixable)" to "idea quality / market efficiency"** — proven when carry stayed null on CME futures with the financing wall removed.
4. **Infrastructure is mature and was never the bottleneck.** The lab, gates, data layers, and freeze enforcement all work.
5. **The in-repo forex strategy search is exhausted** under the current corpus, mechanisms, and available data classes.

---

## J. Pointer index

| Topic | Primary doc |
|-------|-------------|
| Strategy registry | `STRATEGY_STATUS.md` |
| Machine registry | `configs/approved_strategies.yaml` |
| Closed lanes | `DO_NOT_REPEAT_LIST.md` |
| Carry terminal verdict | `FX_FUTURES_CARRY_VERDICT.md` |
| Archive trigger | `FX_FUTURES_CARRY_PROGRAMME_IMPLICATION.md` |
| Evidence manifest | `EVIDENCE_MANIFEST.json` |
