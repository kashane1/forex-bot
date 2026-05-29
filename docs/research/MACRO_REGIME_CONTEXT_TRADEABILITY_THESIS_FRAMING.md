# Macro / Rates / Calendar Overlay — Corrected Thesis Framing

**Status:** framing amendment for a *future* sprint. Not a strategy, not a campaign, not
C024, not an approval, not paper/demo/live. Read-only research framing only.
**Supersedes** the loose "external-data overlays for theses #7/#8" wording in the
compression-continuation readiness decision and summary, and the brief #7/#8 sketches in
`USDJPY_EXTERNAL_THESIS_CANDIDATE_SCORECARD.md` / `EXTERNAL_FX_THESIS_SOURCING_FRAMEWORK.md`.

---

## 1. Why this amendment exists

The prior docs referenced building macro/calendar/rates overlays so that "thesis #7
(macro/calendar windows)" and "thesis #8 (carry/rates/risk-off regime)" could be tested.
That wording is easy to misread as **fast macro trading**. It must not be.

**We are NOT trying to trade macro/rates/calendar correlations faster than institutions.**
This project has no latency edge, no order-book access, no tick rate feed, and no ability
to react to headlines before macro desks or HFTs. Any framing built on speed is dead on
arrival and is explicitly out of scope.

---

## 2. What this thesis IS — slow regime / context classification

The only viable use of macro/rates/calendar information here is **slow, lookahead-safe
context classification of USD/JPY *tradeability*** over M15 / H1 / H4 horizons. The
question is not "what will the market do on the news," but:

> *"Given slowly-known macro/rates/calendar context, is this a period in which a future
> technical setup is more or less likely to be tradeable — and when should we simply not
> trade?"*

Concretely, can slow context help classify:

- **when NOT to trade** (structurally dangerous spread/whipsaw windows);
- when spreads / whipsaw are structurally hostile;
- when trend-following / breakout setups are more likely to *survive* (vs get chopped);
- when mean-reversion / fade behavior is more likely;
- whether **post-event stabilization** windows behave differently from normal periods;
- whether broad **rate-differential regimes** affect USD/JPY drift/volatility enough to
  inform *future research direction* (not to be the entry itself).

Macro context is a **conditioner / filter on tradeability**, never the entry signal.

---

## 3. Hard thesis constraints (out of scope — do not build)

- ❌ No fast-news trading.
- ❌ No immediate event-reaction strategy.
- ❌ No tick-level rate-correlation trading.
- ❌ No assumption we can beat institutions on speed.
- ❌ No live reaction to macro headlines.
- ❌ No predicting USD/JPY from fast rate ticks.
- ❌ No strategy implementation, no campaign, no C024, no approval.

If any diagnostic would only "work" because it reacts within seconds/minutes of a
release, it is out of scope by construction.

---

## 4. Preferred diagnostic categories (all slow, all lookahead-safe)

1. **Macro event-avoidance windows.** FOMC, BOJ, US CPI, US NFP. Characterize
   *pre-event* and *post-event* volatility / spread / whipsaw — to decide when a
   technical system should stand aside. (Event *dates/times* are public schedule data,
   known well in advance — using them is lookahead-safe and latency-free.)
2. **Delayed post-event stabilization.** Behavior at +4h, +8h, +24h, +48h after an event
   — does volatility/spread/tradeability normalize on a slow, predictable schedule?
3. **Rate-differential regime.** Rising/falling or high/low US–Japan rate differential,
   on **daily/weekly** alignment only (e.g. FRED DGS2/DGS10 vs JP equivalents). Does the
   slow regime correlate with USD/JPY drift/volatility *regimes* (not minute-by-minute)?
4. **Risk-regime context.** A risk-off/risk-on proxy (e.g. VIX / SP500 level/trend) if
   available, on a slow cadence — does risk regime condition USD/JPY tradeability?
5. **No-trade filters.** Identify windows/regimes in which technical systems are
   structurally untradeable (cost-toxic, whipsaw-dominated) — the highest-value,
   lowest-overfit output (it withholds trades; it does not generate them).
6. **Setup-conditioning.** Frame everything as *"macro context conditions whether a
   future technical setup is worth testing,"* never *"macro is the entry."*

---

## 5. Lookahead & latency safety requirements

- Event **schedule** data (release date/time) is known in advance → safe to use as a
  calendar window; only the *outcome/number* is unknown, and we do not trade the outcome.
- Rates/risk regime features must be aligned to the candle timeline with an explicit
  **as-of/lagged** join (use only values published on or before the decision bar) — no
  same-day revisions, no future values.
- All features are daily/weekly cadence; **nothing** depends on sub-minute timing.
- TEST window (2025-07-01+) stays sealed.

---

## 6. Data status (honest)

- **Rates/risk:** a FRED cache exists locally (`data/external_features/.fred_cache/`:
  DGS2, DGS10, VIXCLS, SP500, DTWEXBGS, DCOILWTICO, NASDAQCOM) — daily series, but **not
  yet a maintained, timeline-aligned research feature**. JP rate series for the
  differential leg may need sourcing.
- **Event calendar:** there is **no** economic-event calendar table in the research DB.
  FOMC/BOJ/CPI/NFP scheduled dates are public and must be sourced/ingested as a small,
  static, lookahead-safe fixture (dates only — not a credentialed feed).

So a macro-regime-context sprint is partly an **infrastructure** task (build the
lookahead-safe calendar + as-of rates/risk features) before any tradeability-conditioning
diagnostic can run.

---

## 7. Readiness bar for any FUTURE precommit (unchanged in spirit, sharpened)

A future precommit-design sprint off this thesis is allowed **only if** the result is:

1. **slow-regime based** (daily/weekly context, no intrabar event reaction);
2. **lookahead-safe** (as-of joins; schedule-only calendar use);
3. **not latency-dependent** (would work with minutes/hours of delay);
4. **not based on immediate news reaction**;
5. **not pretending to beat institutional speed**;
6. supported on **both train and validation** without touching TEST;
7. expressed as **tradeability conditioning / no-trade filtering**, not as a macro entry
   signal;
8. structurally distinct from the retired C022/C023 / microstructure /
   compression-expansion families.

If a macro-context diagnostic cannot meet all eight, the outcome is
`NOT_READY` / `PAUSE_STRATEGY_RESEARCH`, not a campaign.

---

## 8. Relationship to current state

This does **not** change any verdict. The current standing decision remains
`PAUSE_STRATEGY_RESEARCH` (London compression-continuation falsified; no internal
USD_JPY price-structure lead survives a hardened test). This amendment only corrects the
*framing* of the macro/rates/calendar direction so that, **if** it is pursued later, it is
pursued as slow tradeability-context classification — never as fast macro trading. The
corrected next-sprint prompt is in
`NEXT_SPRINT_PROMPT_MACRO_REGIME_CONTEXT_TRADEABILITY.md`.
