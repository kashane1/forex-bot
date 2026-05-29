# CAMPAIGN_028 — New-Thesis Brief (Phase 0: thesis selection, pre-front-gate)

**Status:** `THESIS_SELECTION` / `NOT_RUN` / `NOT_APPROVED` / `NO_PRECOMMIT_YET`
**Date:** 2026-05-28
**Author:** research audit (founder's-pack review → new-thesis hunt)
**Freeze:** intact. No strategy evidence produced. No TEST data touched. `configs/approved_strategies.yaml` unchanged (empty).

> This is a **decision document**, not a campaign. It exists to (1) record why the
> submitted "MTF confluence pullback" founder's pack does **not** earn a campaign, and
> (2) select a genuinely-new thesis that satisfies
> [`STRATEGY_RESEARCH_RESTART_CRITERIA.md`](STRATEGY_RESEARCH_RESTART_CRITERIA.md) so a
> future C028 can be screened by the edge-discovery front gate **before** any precommit.

---

## 0. Why the submitted pack does not earn a campaign

The founder's pack ("Lower-Timeframe Multi-Timeframe Confluence Pullback Strategy":
D1 trend filter → H4 EMA20/50 → H1 ADX≥18 → M15 pullback/reclaim, next-bar-open, ATR +
time stop) is, mechanically, work the repo has **already built, run, and rejected**:

| Submitted element | Already tested as | Verdict |
| --- | --- | --- |
| LTF MTF confluence pullback, M15 exec + H1/H4/D1 context | **C021** [`lower_timeframe_mtf_confluence_entry.py`](../../src/forex_bot/strategies/lower_timeframe_mtf_confluence_entry.py) | **REJECT** — train −0.0174R on 1,438 trades |
| HTF trend + EMA20 re-acceptance pullback | **C020** [`multi_timeframe_confluence_pullback.py`](../../src/forex_bot/strategies/multi_timeframe_confluence_pullback.py) | **REJECT** — train −0.035R |
| H4/H1 pullback-resolution → M15 reclaim + ADX gate | **C022** [`h4_h1_pullback_resolution_entry.py`](../../src/forex_bot/strategies/h4_h1_pullback_resolution_entry.py) | **REJECT** — train −0.1042R; entry AUC ≈ 0.50 |
| Lower-TF Donchian/breakout + HTF confluence | **C025 / C026** | **REJECT** — no edge, only a cost gradient M3→M30 |

The [`FINAL_RESEARCH_DECISION_MEMO`](FINAL_RESEARCH_DECISION_MEMO.md) retired the whole
trend/breakout/pullback/MTF-confluence family: *"no further trend / breakout / pullback
campaign is run … Resurrecting any of them requires a genuinely new thesis and a fresh
human decision, **not another parameter pass.**"* Swapping the D1 filter and an RSI band is
a parameter pass over an entry edge that has already been falsified (`RESTART_CRITERIA §3`
explicitly rejects "try ADX 25", "use M5 instead of M15", "add one more filter", "change
the stop").

**The rest of the pack (§5–§10) describes infrastructure the repo already has**:
next-bar-open fills, 2×/3× cost+slippage+financing stress, walk-forward, train/val/TEST
lockbox, matched-null + random-entry baselines, best-of-N bootstrap, risk engine + sizing +
kill switch, MTF alignment features, EMA/ADX/RSI/ATR indicators, the experiment-manifest
YAML pattern, and the candles/trades schema.

**Genuinely missing infra the pack does usefully name** (parked, not adopted here — see §6):
stationary bootstrap, Monte-Carlo risk-of-ruin, deflated Sharpe, White Reality Check; plus
a portfolio-risk layer (correlated-exposure / per-currency-direction caps / daily-weekly
loss stops).

---

## 1. The bar a new thesis must clear

From [`STRATEGY_RESEARCH_RESTART_CRITERIA.md`](STRATEGY_RESEARCH_RESTART_CRITERIA.md):

**Need ≥1 trigger:** (1) external thesis w/ documented mechanism + codable rules; (2) new
external data source; (3) public/academic spec **structurally different** from every failed
lane — *different decision variable, not different thresholds*; (4) a slow, non-latency
micro/macro mechanism we can actually capture; (5) a multiple-testing-reducing process
change *paired with* 1–4.

**Plus all gating conditions:** precommitted hypothesis + cost/stop/multiple-testing model;
the standard falsification panel (realistic intrabar stop + conservative cost +
multiple-testing haircut + year/half-split robustness); train/validation **without touching
TEST**; structural distinctness from retired families; explicit separation of *"effect
exists"* vs *"tradable edge exists."*

And the data reality: the **edge-discovery front gate screens H1/H4 on the 7 majors only**
(SQLite, 2020-01 → 2026-05). Sub-H1 (M1/M5/M15) exists in research Postgres but the lab
does not consume it. Rates (JP leg), economic calendar, options/IV, and order-flow are
**absent**.

---

## 2. Exhausted vs unexplored thesis space

| Family | Tested as | Status for C028 |
| --- | --- | --- |
| Trend / breakout / ADX | C001–004, C006(blocked), C007 | **RETIRED** |
| Pullback / MTF confluence | C020, C021, C022, C023 | **RETIRED** |
| Lower-TF Donchian + HTF | C025, C026 | **REJECT (cost-defeated)** |
| Session breakout | C010 | **REJECT** |
| Regime/vol-percentile gate | C012 | **REJECT** |
| Cross-pair currency-strength **rotation** (directional, rank-gap, 6-bar hold) | C013 | **REJECT (−113%)** |
| Calendar event-window | C014 | **REJECT** (NFP), FOMC blocked |
| Failed-breakout reversal | C015 | **REJECT** |
| Weekly cross-sectional momentum | C016 | **REJECT** |
| Weekly vol-contraction breakout | C017 | **REJECT** |
| Single-instrument mean-reversion (z-score) | C008, C009, C018, C019, C027(scaffold) | REJECT / scaffold-only |
| Vol-compression → expansion | external-thesis diagnostic | **FALSIFIED on train** |
| Seasonality / day-of-week direction | session atlas | **atlas-null (≈0.49 everywhere)** |
| **Carry / rate-differential** | — | **UNTESTED — data-blocked** (no foreign rate leg, no financing-PnL) |
| **Value / PPP / REER reversion** | — | **UNTESTED — data-blocked** (no rates, no multi-cycle macro) |
| **Cointegration / relative-value spread reversion** | — | **UNTESTED — testable NOW on H1/H4 majors** |

Only **four** classic edge families are genuinely unexplored: carry, value/PPP, cointegration/
relative-value, and (mechanism-gated) seasonality. Of these, **only cointegration/
relative-value is testable now without new data**; the others are blocked on data the repo
does not have.

---

## 3. Candidate ranking for C028

| # | Candidate | Trigger | Testable now? | Mechanism strength | Verdict |
| --- | --- | --- | --- | --- | --- |
| **A** | **Relative-value / cointegration spread reversion** (lead) | #3 (new decision variable) + #1 (documented RV mechanism) | **Yes** — H1/H4, 7 majors, lab-screenable | Medium (FX cointegration is fragile — see risks) | **RECOMMENDED to take to the front gate** |
| B | Carry / rate-differential | #2 (new data) — strongest trigger | **No** — needs foreign rate legs + financing-PnL model | High (best long-run FX literature) | **Recommended as a data-infra sprint first**, then a carry scaffold |
| C | Value / PPP / REER reversion | #2 | No — needs rates + multi-cycle macro | Medium-high | Deferred (data-blocked) |
| D | Seasonality / flow w/ new mechanism | #1 + #4 | Partially | Low (atlas says direction is null) | Deferred (needs a mechanism that explains the atlas null) |

Everything below the line (trend, pullback, MTF, session, vol-compression, single-instrument
z-score) is retired/rejected and **disqualified** by `RESTART_CRITERIA §3`.

---

## 4. Recommended thesis (A): relative-value / cointegration spread reversion

### 4.1 Statement
On a **pair of correlated FX instruments** (e.g. EUR/USD and GBP/USD), the hedge-ratio-
adjusted **log-price spread** `s_t = log(P¹_t) − β·log(P²_t)` is, during cointegrated
regimes, mean-reverting around a slow-moving equilibrium. When `s_t` deviates to a
statistical extreme, **fade the spread** (short the rich leg, long the cheap leg) and exit on
reversion to equilibrium or on a cointegration-breakdown stop.

### 4.2 Why this clears the restart bar
- **Decision variable is new.** Every retired lane keyed off a *single instrument's* price
  structure (trend slope, pullback reclaim, breakout, single z-score). This keys off a
  **two-instrument residual** — a different state variable, satisfying trigger #3's
  "different decision variable, not different thresholds."
- **Distinct from C013.** C013 was *directional currency-strength rotation* (long the strong
  base / short the strong quote on a 6-bar rank-gap **momentum** hold) and lost −113%. This
  is the **opposite sign of bet** (reversion, not rotation) on a **relationship spread**, not
  a single-currency rank. Different direction, different variable, different horizon.
- **Documented mechanism (trigger #1).** Relative-value / pairs trading and FX cointegration
  are an established public/academic literature; the economic anchor is shared macro
  exposure (common USD leg, correlated risk sensitivities) pulling two prices back toward a
  stable ratio.
- **Testable now, cheaply.** Needs only H1/H4 closes for the 7 majors — already in SQLite —
  so the **edge-discovery front gate can kill or pass it for near-zero cost** before any
  scaffold.

### 4.3 Honest risks (must be front-and-center in screening — *"effect exists" ≠ "edge exists"*)
1. **USD common-factor confound (the big one).** All 7 majors share USD. EUR/USD and
   GBP/USD co-move because both are "USD strength," i.e. a **common factor**, not necessarily
   an economically-anchored stationary spread. A naïve spread may be dominated by the USD leg
   and **drift with EUR-vs-GBP fundamentals** rather than revert. Mitigation: test
   **USD-neutralized / triangulated** constructions (e.g. EUR/GBP cross implied from the two
   USD legs) and require the spread to pass a stationarity check **in-sample on train only**.
2. **Cointegration instability out-of-sample.** FX cointegration relationships are widely
   found to be **unstable / break across regimes**. The hedge ratio β estimated on train can
   decay. Mitigation: year/half-split robustness in the falsification panel; treat β as
   precommitted (estimated on train, frozen), not refit live.
3. **Multiple testing across pair combinations.** With 7 majors there are 21 raw pairings (more
   with crosses). Screening many spreads and keeping the best **is** selection mining.
   Mitigation: the lab's `matrix_sanity` / best-of-N bootstrap (`LIKELY_SELECTION_NOISE`
   gate) must pass; precommit the pair set + construction rule before any TEST.
4. **Cost.** A spread trade is **two legs** → roughly double the round-trip spread cost. The
   reversion edge must clear `2×` leg cost under the conservative model. The lab's
   `cost_feasibility` gate screens this first.

### 4.4 Universe & construction (to be precommitted only if the gate passes)
- **Legs:** pairs/triples drawn from {EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF,
  NZD_USD}. Candidate spreads grouped by economic kinship (e.g. EUR/GBP via USD legs;
  AUD/NZD; USD_CAD/USD_CHF as USD-leg controls).
- **State variable:** rolling z-score of `s_t` (lookback precommitted; β frozen from train).
- **Entry:** |z| ≥ threshold (precommitted), fade the spread, next-bar-open fill.
- **Exit:** revert to z≈0 (time-boxed) **or** cointegration-breakdown stop (z runs further /
  rolling stationarity fails) — exits precommitted, no TP curve-fitting.
- **Timeframe:** **H4** (lab-native, lowest cost headwind among screenable TFs).

### 4.5 How the front gate screens it (Phase 1 of C028 — no precommit needed to screen)
Run, on **train data only**, in this order; any RED kills it:
1. `cost_feasibility` on the **two-leg** spread (spread/ATR of the combined position) →
   require `COST_FEASIBLE`.
2. forward-return information of the spread z-score at the intended hold horizon → present?
3. `matched_null` — beat a structure-matched null (same legs/horizon/session, shuffled
   timing) → require above null p95, not `WITHIN_MATCHED_NULL`.
4. `filter_ablation` — does the stationarity/regime filter **add edge** or only reduce
   sample? → require `FILTER_ADDS_EDGE`.
5. `matrix_sanity` across the candidate spread set → require `ROBUST_MATRIX_SIGNAL`, **not**
   `LIKELY_SELECTION_NOISE` / `FRAGILE_*`.

**If any gate is RED → C028 is written up as a documented rejection (like C026), freeze
intact.** **If all GREEN → proceed to Phase 2.**

---

## 5. Proposed C028 sequence (gate-first, mirrors C027 discipline)

| Phase | Deliverable | Gate |
| --- | --- | --- |
| **0** | This brief (thesis selection + restart-trigger justification) | — |
| **1** | Edge-discovery **front-gate screen** of the spread thesis on H1/H4 train data (cost → fwd-return → matched-null → ablation → matrix-sanity) | **decision point** |
| **2** *(only if Phase 1 all-green)* | Precommit scope doc (frozen β, lookback, thresholds, exits, cost model) + artifact contract — the binding rule | locked before any run |
| **3** | Pure signal module + config YAML + unit tests (no broker import); preflight-only runner | scaffold-safe |
| **4** | Backtrader-parity design (design only) | — |
| **5** | Future train/validation prompt (NOT executed) + status/index/manifest/backlog | TEST sealed |

This guarantees we never resurrect a retired family **and** never scaffold an idea the cheap
screen would have killed.

---

## 6. Secondary path (B): unlock carry via a data-infra sprint

Carry is the **highest-conviction** FX edge in the literature and the **only** classic family
the repo has flagged repeatedly as "blocked, not falsified." It needs, before any strategy
work: foreign (esp. JP) short-rate legs, a verified **financing-PnL / observed-swap** model,
and multi-cycle history so a rate regime is identifiable. `RESTART_CRITERIA §5` explicitly
sanctions **data acquisition / engineering** as the only work allowed while strategy search is
paused — so a carry **data-infra sprint** is a legitimate, non-mining use of C028 that would
later unlock the strongest trigger (#2, new external data). It is a bigger commitment than
Path A and produces no signal evidence by itself.

---

## 7. What this brief does NOT do
- No precommit, no frozen parameters, no strategy evidence, no TEST access.
- No change to `configs/approved_strategies.yaml` (remains empty).
- No code. The lead thesis must survive the **front gate first**; only then is a scaffold
  earned.

**Recommendation:** take **Path A (relative-value / cointegration spread reversion)** into the
edge-discovery front gate as Phase 1 of C028. Keep **Path B (carry data-infra)** as the
high-ceiling alternative if a data-acquisition sprint is preferred over a price-only screen.
