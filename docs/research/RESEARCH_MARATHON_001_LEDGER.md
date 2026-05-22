# Research Marathon 001 — Ledger

Append-only. One entry per completed campaign or infrastructure phase.
Newest entries at the bottom.

---

### Phase 0 — supervisor setup

- Branch `research-marathon-001` created.
- Plan, ledger, resume docs written.
- Generic marathon runner + report builder added (reused by
  CAMPAIGN_006–008).
- Status: **complete**.

---

### Phase 1 — CAMPAIGN_005 benchmarks & diagnostics (diagnostic only)

- Real OANDA H4 data reused from `data/campaign_002.sqlite3`.
- **Random-entry expectancy −0.095 R** (20 seeds, matched frequency,
  one position at a time, base costs). The three rejected strategies
  scored −0.071 to −0.163 R on the untouched test — i.e. **not
  meaningfully better than random**. Prior failures are cost/structure
  driven, not unique entry defects.
- **Efficiency ratio 0.24** (0=chop, 1=trend) — H4 majors retrace most
  of their movement; hostile to breakout/trend follow-through.
- **Return AC(1) ≈ 0.00** — no directional persistence at H4.
- Not a hard no-go on its own; informs the ladder — argues for lower
  turnover (D1) and non-breakout entries, exactly the CAMPAIGN_006-008
  hypotheses.
- Verdict: **diagnostic — no promotion.** Report:
  `backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md`.
- Status: **complete**. Ladder continues to CAMPAIGN_006.

---

### Phase 2 — CAMPAIGN_006 daily (D1) trend

- Fetched real OANDA practice D1 candles (6 pairs, ~1656 each) into
  `data/campaign_002.sqlite3`; provenance recorded.
- Ran `trend_following 0.1.0-baseline-frozen` on D1 — screening phase,
  36 runs. **Result: 0 trades in every run.**
- Root cause = **infrastructure incompatibility, not a strategy
  result.** D1 candles close at the 17:00 NY rollover, so (a) every
  signal hits the session-filter rollover blackout — `SESSION_BLOCKED`
  100/100 — and (b) the D1 close bid/ask is the rollover spread
  (EUR_USD D1 median 2.0 vs H4 1.5 pips). The intraday-designed
  backtester cannot validly test D1 without next-bar-open fills + a
  non-rollover spread reference.
- Did **not** hack the config to force trades — that would yield
  unreliable rollover-spread evidence.
- Verdict: **REJECT — no valid result (D1 infrastructure blocker).**
  Scoped to D1; H4 path validated and unaffected → marathon continues.
- Report: `backtests/CAMPAIGN_006_DAILY_TREND_REPORT.md`.
- Status: **complete**. Ladder continues to CAMPAIGN_007 (H4 pullback).

---

### Phase 3 — CAMPAIGN_007 H4 pullback-continuation

- New strategy `pullback_continuation 0.1.0-c007` — non-breakout
  entry: established trend + pullback to the EMA + continuation bar
  (6 strategy unit tests). Real OANDA H4 data reused.
- Screening run (36 runs, H4): **train expectancy −0.164 R, validation
  −0.166 R**, both clearly negative. Validation PF 0.66. Only 1/6 pairs
  positive on validation (USD_JPY, marginal +0.70%).
- **Screening gate FAIL** → the 2025-2026 reported test window was
  **not opened** (lockbox intact, per discipline).
- Avoiding breakout exhaustion did not help: the pullback-continuation
  entry is no better than the breakout entries — H4 trends in 2020-2024
  lack the persistence for a resumption to follow through.
- Verdict: **REJECT**. Report:
  `backtests/CAMPAIGN_007_H4_PULLBACK_REPORT.md`.
- Status: **complete**. Ladder continues to CAMPAIGN_008 (mean
  reversion, research-only).

---
