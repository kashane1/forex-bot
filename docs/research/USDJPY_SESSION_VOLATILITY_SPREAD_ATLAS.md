# USD_JPY Session / Volatility / Spread Atlas

**Sprint:** `external-thesis-sourcing-and-session-atlas-001` · **Phase 2**
**Source:** read-only research Postgres `market_data.candles` (`USD_JPY`).
**Builder:** `scripts/build_usdjpy_session_volatility_spread_atlas.py`
**Summary artifact:** `research/usdjpy_session_atlas/usdjpy_session_atlas_summary.json`

> **This atlas is descriptive market structure, NOT a tradable edge.** It exists to
> tell us which externally-sourced theses are even *plausible* on USD_JPY before any
> campaign is designed. No strategy is implemented; no verdict changes; the 2025-07+
> test window is a sealed lockbox and is excluded. Every "supports / does not support"
> note below is about *plausibility of a mechanism*, not evidence of profitability.

---

## 1. Coverage & method

- **Window:** 2021-06-01 .. 2025-06-29 (train+validation only; **TEST lockbox 2025-07+
  excluded**).
- **Bars:** 95,756 completed M15 bars (train 59,852 / validation 35,904).
- **M1 cross-check:** ~1.50M M1 bars aggregated server-side for spread percentiles.
- **Spread:** computed from `ask_c − bid_c` (price), converted to pips (USD_JPY pip = 0.01).
- **Sessions** (DST-correct, per-center local time; priority rollover > overlap > ny >
  london > tokyo > off_hours):
  - Tokyo 09:00–15:00 JST · London 08:00–16:00 London · NY 08:00–17:00 ET
  - `london_ny_overlap` = London ∧ NY active · `rollover` = 17:00–18:00 ET
- **Volatility:** ATR(14) on M15 mid; realized range = (high−low); trailing rolling
  vol percentile over ~20 trading days (1920 bars).
- **Directional:** forward mid return over 1/4/8/16 M15 bars (15m–4h); trend-continuation
  vs mean-reversion measured against the sign of the last 4 bars' move.
- **Tradability:** MFE/MAE over a forward 16-bar (4h) horizon from an *arbitrary* entry
  bar (long perspective); breakout = break of prior 16-bar range; false-breakout = close
  returns inside the range within 8 bars; whipsaw = consecutive 1-bar sign reversals.

All forward/excursion metrics use only future bars relative to each timestamp; the vol
percentile uses only past bars. Parameters are fixed in the builder and logged in the
summary `_meta`.

---

## 2. Headline findings

### 2.1 Spread / cost structure — the most robust, M1-confirmed result

| session | M15 spread med | p90 | p95 | spread/ATR med | M1 spread med (xcheck) |
|---|---|---|---|---|---|
| london_ny_overlap | 1.6 | 2.0 | 2.5 | **0.138** | 1.6 |
| ny | 1.6 | 2.0 | 2.1 | 0.147 | 1.6 (ny+overlap) |
| london | 1.7 | 1.9 | 2.0 | 0.160 | 1.7 |
| tokyo | 1.7 | 2.0 | 2.1 | 0.179 | 1.7 |
| off_hours | 1.8 | 2.2 | 2.4 | 0.205 | 2.0 |
| **rollover** | **4.7** | **8.6** | **10.0** | **0.506** | **5.0 (p90/p95 = 10)** |

- USD_JPY trades at a tight, stable **~1.6–1.7 pip** median spread across the Tokyo,
  London, NY and overlap sessions. The M1 cross-check confirms the M15 numbers exactly.
- **Rollover (17:00 ET) is cost-toxic:** median ~5 pips, p90/p95 = 10 pips, spread/ATR
  ≈ 0.5 (i.e. half a unit of volatility is paid just to cross the spread). Any strategy
  trading the rollover bar is paying a tax it almost never earns back.
- **Off-hours** spreads are mildly elevated (p95 up to ~3 pips on M1).
- **Implication:** a session/cost **filter** (never trade rollover; deprioritize
  off-hours) is the single highest-confidence, most defensible piece of structure in the
  whole atlas. It is a *filter*, not an edge.

### 2.2 Volatility / activity — a clear, predictable diurnal curve

Realized M15 range and ATR by NY hour:

- **Peak: NY 08:00–11:00** (London cash open through the London/NY overlap) — range
  median **12.8 → 14.5 pips**, range-expansion probability **0.72–0.79**, ATR 11–13.8.
- **Secondary bump: NY 02:00–04:00** (Tokyo/early-London) — range 10–12, expansion prob
  0.62–0.69.
- **Trough: NY 14:00–18:00** (NY afternoon into rollover) — range 4.4–6.4, expansion
  prob 0.15–0.30.
- The **london_ny_overlap** bucket is the single most active (range med 13.8, expansion
  prob 0.76).
- **Implication:** *when* volatility expands is highly predictable (timing edge in the
  schedule, not in price). This supports the *timing* leg of volatility-expansion and
  opening-range theses — it says nothing about *direction*.

### 2.3 Directional predictability — the central null result

Across **every** session, hour, and volatility regime:

- **Trend-continuation probability ≈ mean-reversion probability ≈ 0.48–0.50.**
- Forward-return means are small (sub-pip to ~1 pip over 4h) relative to ~1.6 pip spread.
- `p_up` sits at 0.50–0.55 with a mild long tilt that is almost certainly the
  **2021–2024 USD_JPY uptrend as a period artifact**, not a repeatable edge (it appears
  as a low-grade drift everywhere rather than concentrating in any mechanism).
- Splitting by volatility regime does **not** rescue direction: continuation ≈ 0.49 in
  low, mid, and high vol alike.

This is the most important finding for thesis selection: **USD_JPY M15 forward direction
is essentially unpredictable from recent direction at every time of day.** It is fully
consistent with the documented failure of the C022/C023 trend/pullback/MTF-confluence
families. Any thesis whose core requires predicting continuation direction starts from
an atlas that gives it **no support**.

Two adjacent suspicious cells — NY 15:00 (h4 mean +1.5 pips, p_up 0.58) and NY 16:00
(h4 mean −1.5 pips, p_up 0.42) — point in *opposite* directions across the NY-close
boundary and are best read as close-auction noise / small-sample reversion, **not** a
signal. They are flagged here precisely so a future sprint does not mine them.

### 2.4 Breakout / fade structure — failure-prone but not free

- **False-breakout rate given a breakout: 0.72–0.80 across all sessions and regimes.**
  ~3 out of 4 breaks of a 4h range close back inside within 2h. Highest in low-vol
  (0.80), lowest in high-vol (0.75).
- However, **MFE:MAE after an arbitrary entry is < 1.0 everywhere (0.92–0.98)** — i.e.
  a position opened at a random time faces slightly *more* adverse than favorable
  excursion. There is no built-in favorable asymmetry to harvest by naively fading.
- Breakout frequency is highest in the overlap (0.34) and off-hours (0.31).
- **Implication:** the high unconditional false-breakout rate is *suggestive* of a
  fade/mean-reversion angle, but the sub-1.0 MFE:MAE and ~1.6 pip cost mean any such
  edge must come from **conditioning** (which breakouts, when) and is exactly the kind
  of result that is easy to overfit. High interest, high overfit-trap.

### 2.5 Weekday — essentially flat

Range median 8.4–9.5 pips and false-breakout rate ~0.77 on every weekday; no strong
day-of-week structure (Sunday has low n). Day-of-week is not a promising conditioning
variable on its own.

---

## 3. What the atlas supports vs. does not support (plausibility only)

| Mechanism family | Atlas read | Plausibility |
|---|---|---|
| No-trade cost/spread filter | Rollover toxic (5–10 pip), off-hours elevated; active sessions tight | **Strong / robust** (it's a filter, not an edge) |
| Volatility expansion timing (London open / overlap) | Range + expansion-prob peak 08:00–11:00 ET, very stable | **Timing plausible**; direction unaddressed |
| Opening-range behavior | Open-driven vol expansion is real | Timing plausible; **direction unproven** |
| Session-boundary range break (Tokyo→London) | Secondary vol bump at NY 02–04 | Weakly plausible; direction unproven |
| Mean reversion / false-breakout fade | 72–80% breakouts fail, but MFE:MAE < 1 | **Interesting but overfit-prone**; not free |
| Trend / continuation / pullback (C022/C023 family) | Continuation ≈ 0.49 everywhere | **Not supported** — atlas-level null |
| Carry / rates / risk-off regime | Not testable from candle atlas alone | Needs external overlay (FRED partial); deferred |
| Macro / calendar windows | Not testable without calendar overlay | Needs event calendar; deferred |
| Day-of-week effects | Flat | Not supported |

---

## 4. Caveats (so this is not misread as edge)

1. **Descriptive only.** Forward-return means are reported with no cost subtracted and
   no precommitment; they are not strategy returns.
2. **Period artifact risk.** 2021–2025 contained a large USD_JPY uptrend; the mild
   long tilt in `p_up` is likely that, not a repeatable bias.
3. **In-sample atlas.** Selecting a thesis *because* a particular atlas cell looks good
   would make the atlas the training set. The atlas narrows *mechanisms to consider*;
   the actual edge test must be a separate, precommitted, out-of-sample campaign.
4. **No multiple-testing correction.** Dozens of cells are reported; some will look
   attractive by chance. Treat any single attractive cell with suspicion.
5. **Test lockbox untouched.** Nothing here uses 2025-07+ data.

See `docs/research/USDJPY_EXTERNAL_THESIS_CANDIDATE_SCORECARD.md` (Phase 3) for how
these readings score the candidate theses against the Phase 1 framework.
