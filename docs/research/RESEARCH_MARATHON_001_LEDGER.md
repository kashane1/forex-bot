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
