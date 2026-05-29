# USD_JPY External Thesis Candidate Scorecard

**Sprint:** `external-thesis-sourcing-and-session-atlas-001` · **Phase 3**
**Inputs:** Phase 1 framework (`EXTERNAL_FX_THESIS_SOURCING_FRAMEWORK.md`),
Phase 2 atlas (`USDJPY_SESSION_VOLATILITY_SPREAD_ATLAS.md` +
`research/usdjpy_session_atlas/usdjpy_session_atlas_summary.json`), and the merged
campaign history.

> **Scoring is plausibility-screening, not edge.** A high score means a thesis is worth
> *designing a precommitted out-of-sample test for* in a future sprint — it does **not**
> mean the thesis is profitable. No thesis is implemented here; no campaign is created;
> no verdict changes. The atlas is in-sample and must not become the training set.

Scale per criterion: `strong` / `adequate` / `weak` / `fail`. Hard gates (criteria
1=distinctness, 2=mechanism, 4=data-compat, 6=codability, 7=cost-survival) can sink a
thesis regardless of the rest.

---

## Quick verdict table

| # | Candidate thesis | Distinct (G) | Mechanism (G) | Data (G) | Codable (G) | Cost-survival (G) | Sample | Overfit risk | Atlas support | **Screen** |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Tokyo range → London breakout/fakeout | adequate | adequate | strong | adequate | adequate | adequate | high | mixed | **HOLD** |
| 2 | NY continuation after London direction | weak | weak | strong | adequate | weak | adequate | high | **fail** | **REJECT** |
| 3 | Prev-session high/low sweep + displacement | strong | adequate | strong | adequate | weak | adequate | high | mixed | **HOLD** |
| 4 | Opening-range breakout + vol expansion | adequate | adequate | strong | adequate | weak | adequate | high | mixed | **HOLD** |
| 5 | Volatility compression → expansion | strong | strong | strong | strong | adequate | strong | medium | **supports timing** | **TOP CANDIDATE** |
| 6 | Extreme intraday extension → mean reversion | strong | adequate | strong | adequate | weak | adequate | high | mixed | **HOLD** |
| 7 | Macro/calendar event window behavior | strong | strong | **weak** | adequate | adequate | adequate | medium | untestable here | **BLOCKED (data)** |
| 8 | Carry/rates/risk-off regime | strong | strong | **weak** | adequate | strong | weak | untestable here | **BLOCKED (data)** |
| 9 | No-trade cost/spread filter only | adequate | strong | strong | strong | n/a | strong | low | **strong** | **ADOPT (as overlay, not a strategy)** |
| 10 | Pause strategy research | — | — | — | — | — | — | — | — | **fallback** |

"G" = hard gate. **Screen** legend: ADOPT (use now, as an overlay) · TOP CANDIDATE
(eligible for Phase 4 selection) · HOLD (plausible but overfit-prone / needs a tighter
precommit) · BLOCKED (fails a data gate until an overlay is built) · REJECT
(atlas-level null) · fallback.

---

## Per-thesis detail

### 1. Tokyo range → London breakout / fakeout
- **Mechanism:** Tokyo-session range gets swept or broken when London liquidity arrives.
- **Data needed:** M15/M1 within Tokyo + London windows (have it).
- **Sample size:** ~1 setup/day ⇒ ~1,000 events over train+val — adequate.
- **Expected hold:** minutes–2h.
- **Cost sensitivity:** entry near London open where spread is tight (~1.7 pip) — OK, but
  the fakeout variant trades into the 72–80% false-breakout regime.
- **Atlas compatibility:** vol *does* expand at the London open (NY 03:00–04:00 / 08:00),
  so the *timing* leg is real; but breakout *direction* is a coin flip and false breaks
  dominate. Mixed.
- **Distinctness:** different decision variable (prior-session range interaction) — OK.
- **Overfit risk:** high (range definition, break buffer, fakeout confirmation = several
  knobs).
- **Verdict: HOLD.** Plausible timing, but the breakout-direction null and many knobs
  make it overfit-prone. Would need a very tight precommit, likely framed as a *fade*
  (see #6) rather than a breakout.

### 2. NY continuation after London direction established
- **Mechanism:** London sets the day's direction; NY continues it.
- **Atlas compatibility:** **fails.** Continuation probability is ~0.48–0.49 in the NY
  session and forward-return means are sub-spread. The atlas directly contradicts the
  premise of directional continuation.
- **Distinctness:** this *is* the trend/continuation idea that C022/C023 already failed.
- **Verdict: REJECT.** Atlas-level null + structurally inside the retired family.

### 3. Previous-session high/low sweep + displacement
- **Mechanism:** stops cluster beyond the prior session's high/low; price sweeps them,
  then displaces. Structurally distinct from indicator confluence (level-interaction).
- **Data needed:** prior-session extremes from M15/M1 (have it).
- **Sample size:** ~2 levels/day ⇒ adequate.
- **Cost sensitivity:** sweeps often happen in thinner windows (session opens/off-hours)
  where spread is a touch wider; weak-to-adequate.
- **Atlas compatibility:** consistent with the high false-breakout rate (sweeps = failed
  breaks), but MFE:MAE < 1 says the displacement leg is not automatically favorable.
  Mixed.
- **Distinctness:** strong (no prior campaign tested explicit prior-session liquidity
  sweeps).
- **Overfit risk:** high (sweep definition, displacement threshold, invalidation).
- **Verdict: HOLD.** Genuinely distinct and mechanistically credible, but needs the
  atlas's fade structure to be *conditioned* carefully; high overfit surface.

### 4. Opening-range breakout (ORB) with volatility expansion
- **Mechanism:** first-N-minutes range defines bias; break with vol expansion runs.
- **Atlas compatibility:** vol expansion at the open is strongly confirmed (timing), but,
  as with #1, *direction* of the break is unpredictable and false breaks dominate. Mixed.
- **Cost sensitivity:** trades at the open (tight spread) — OK; but chasing breaks pays
  the spread into a 75%+ failure rate.
- **Overfit risk:** high (range length, break trigger, filter).
- **Verdict: HOLD.** Timing supported, direction not. Same caution as #1.

### 5. Volatility compression → range expansion  ★ TOP CANDIDATE
- **Mechanism:** volatility mean-reverts; periods of compression are followed by
  expansion. This is a **volatility** thesis, not a **direction** thesis — which is
  exactly where the atlas has signal (predictable vol cycle) and avoids where it has
  none (direction).
- **Data needed:** ATR / realized-range percentiles from M15 (have it; the atlas already
  computes the rolling vol percentile).
- **Sample size:** strong — every bar carries a vol-regime state; compression episodes
  are frequent.
- **Cost sensitivity:** expansion episodes coincide with the active sessions (tight
  spread); a vol thesis can also be expressed as a *filter/sizing* overlay that barely
  pays spread. Adequate–strong.
- **Atlas compatibility:** **supports the timing/state leg** — range-expansion
  probability moves monotonically with vol regime (low 0.29 → mid 0.50 → high 0.71) and
  with the hour-of-day curve. The honest gap: the atlas shows expansion is *predictable*
  but does **not** show a *directional* way to monetize it, so the eventual design must
  be direction-agnostic (e.g. straddle-like, or expansion-conditioned execution) or pair
  with an independent direction input.
- **Distinctness:** strong — no prior campaign was a pure volatility-state thesis (C017
  was a *weekly* volatility-contraction-breakout that still relied on a directional
  break; this would be intraday and can be framed direction-agnostic).
- **Overfit risk:** medium — vol regime is a low-parameter, robust, monotonic construct
  (fewer knobs than breakout/fade families).
- **Verdict: TOP CANDIDATE.** It is the one candidate whose *core requirement aligns
  with where the atlas actually has structure* (predictable volatility) and *avoids where
  it doesn't* (direction). It still must clear the "how do you monetize expansion without
  predicting direction?" question in a future precommit — that is the central design risk,
  not a data gap.

### 6. Extreme intraday extension → mean reversion
- **Mechanism:** after an outsized intraday move, price reverts.
- **Atlas compatibility:** the 72–80% false-breakout rate is *suggestive*, but
  MFE:MAE < 1.0 after arbitrary entries means reversion is **not** a free lunch; any edge
  must come from conditioning on *extremity* specifically (not measured in this atlas
  pass). Mixed.
- **Cost sensitivity:** weak — reversion targets are often small relative to the ~1.6 pip
  spread unless the extension is large.
- **Distinctness:** strong (no prior campaign tested intraday overextension reversion on
  USD_JPY).
- **Overfit risk:** high (extension threshold, reversion target, stop).
- **Verdict: HOLD.** Distinct and mechanistically plausible; the atlas neither confirms
  nor refutes the *conditional* (on-extremity) version, so it would need a dedicated
  diagnostic before a precommit (candidate for MORE_DIAGNOSTICS).

### 7. Macro / calendar event window behavior
- **Mechanism:** scheduled releases (US CPI/NFP/FOMC, BoJ, JP CPI) cause systematic
  vol/flow.
- **Data gate (criterion 4): WEAK/FAIL.** We have no committed economic-calendar table
  in the research DB; the atlas cannot test event windows without one. (A partial FRED
  cache exists for *rates/risk levels*, not an event-time calendar.)
- **Verdict: BLOCKED (data).** Mechanistically strong, but cannot be screened or
  precommitted until an event-calendar overlay is sourced and ingested. Defer.

### 8. Carry / rates / risk-off USD_JPY trend regime
- **Mechanism:** UST–JGB rate differential + risk sentiment drive multi-week JPY trends.
- **Data gate (criterion 4): WEAK.** Requires rates (DGS2/DGS10 exist in FRED cache) and
  risk (VIX/SP500 exist) *aligned to the candle timeline* as a maintained overlay; this
  is a regime/sizing input, and the natural horizon (weeks) gives **weak sample size**
  for an intraday repo and overlaps the period-artifact uptrend.
- **Verdict: BLOCKED (data) / weak sample.** Defer until a maintained rates/risk overlay
  exists; even then it is a *regime filter*, not a standalone intraday entry.

### 9. No-trade cost / spread filter only  ★ ADOPT (as overlay)
- **Mechanism:** never trade when the spread/ATR is hostile (rollover; thin off-hours).
- **Atlas compatibility:** **strong and robust** — rollover spread is 5–10 pips
  (spread/ATR ≈ 0.5) vs ~1.6–1.7 pips in active sessions; M1 confirms.
- **Distinctness/overfit:** it is a *filter*, not a strategy — near-zero overfit surface,
  one obvious threshold.
- **Verdict: ADOPT as a standing overlay/constraint** for *any* future design. It is not
  itself a source of edge (it cannot make money on its own), so it does **not** satisfy
  Phase 4's "select a thesis" requirement — but every future precommit should bake it in.

### 10. Pause strategy research
- **Verdict: fallback.** Selected only if no candidate clears the Phase 1 gates well
  enough to justify a precommit-design sprint. Given #5 clears the gates, pause is not the
  default this round (see Phase 4).

---

## Cross-cutting reading

- The atlas's **central null on direction** (continuation ≈ reversion ≈ 0.49 everywhere)
  REJECTS the directional-continuation thesis (#2) outright and weakens every thesis
  whose edge depends on predicting break direction (#1, #4, parts of #3).
- The atlas's **real structure is in volatility timing and spread/cost** — which is why
  the volatility-state thesis (#5) and the cost filter (#9) score best.
- The **fade/mean-reversion family** (#3, #6) is the most *interesting* given the 72–80%
  false-breakout rate, but MFE:MAE < 1 plus high knob-count make it the biggest
  overfit-trap; it needs a dedicated conditional diagnostic before any precommit.
- Two theses (#7, #8) are mechanistically strong but **blocked by missing overlay data**;
  they define a clear infrastructure backlog item, not a strategy this round.

Proceed to Phase 4 (`NEXT_THESIS_AFTER_EXTERNAL_SOURCING_AND_ATLAS.md`) for the single
selection / classification.
