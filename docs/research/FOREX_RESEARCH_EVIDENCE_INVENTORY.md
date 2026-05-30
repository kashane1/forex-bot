# Forex Research Evidence Inventory

**Purpose:** a category-level map of what the project has tested, what
failed, what remains unresolved, and *how* each thing failed. This is a
synthesis of existing committed evidence (C001–C031, the C1 studies, the
non-time-bar lane, the edge-discovery lab, and the cost/financing
audits). No new evidence is produced here.

**Failure-mode taxonomy used below:**

- **no-effect** — no edge even gross of cost (indistinguishable from a
  matched null).
- **cost-defeated** — a real or apparent gross edge smaller than
  spread + slippage.
- **financing-defeated** — killed specifically by overnight
  financing/carry on multi-day holds.
- **data-blocked** — cannot be tested properly on the current corpus
  (history too short, instruments absent).
- **infrastructure-blocked** — blocked by tooling/parity, not market
  reality (rare here; mostly resolved).

---

## 1. Trend following

- **Tested:** H4 trend (C001), real-data H4 trend (C002), controlled-ADX
  trend (C003), daily trend (C006).
- **Failed:** all REJECT. Gross edges where present were a few pips;
  round-trip cost erased them. C002 additionally showed financing drag.
- **Unresolved:** whether trend persistence exists at *higher quality /
  lower cost* venues (futures) or on *trendier instruments* (indices,
  metals) — not testable on the current corpus.
- **Failure mode:** cost-defeated (primary); no-effect (secondary).

## 2. Breakout

- **Tested:** volatility breakout (C004), failed-breakout reversal
  (C015), weekly volatility-contraction breakout (C017).
- **Failed:** all REJECT. C015 also failed on concentration / gate
  failure. No robust post-cost edge.
- **Unresolved:** breakout on instruments with stronger directional
  follow-through (indices/crypto) under a *different* cost profile.
- **Failure mode:** no-effect / cost-defeated.

## 3. Mean reversion

- **Tested:** range mean-reversion (C008, C009), post-dedup variants
  (C012, C013), H4 filtered z-score reversion (C027).
- **Failed:** all REJECT. C027 was the *one* idea to clear the
  edge-discovery front gate into a scaffold, then failed its train gate
  (PF 1.043, 1/3 positive years, forking-path filter, expectancy
  +0.00012). C008/C009 showed exit pathology on top of cost.
- **Unresolved:** mean-reversion at lower cost (the gross signal is the
  thinnest of any family).
- **Failure mode:** cost-defeated; C027 also forking-path / wafer-thin.

## 4. Confluence (MTF / LTF)

- **Tested:** MTF confluence (C020), LTF/MTF confluence (C021), M5
  Donchian + HTF confluence (C025 scaffold), Donchian timeframe ladder
  M3–M30 (C026).
- **Failed:** REJECT. C026 showed cost + expectancy improve
  *monotonically* as the timeframe slows (M5 is **not** uniquely
  cost-defeated) but the best M30 is still net-negative — a cost
  gradient, not an edge.
- **Unresolved:** none on this corpus; family closed across M3–M30.
- **Failure mode:** cost-defeated (cost gradient with no edge floor).

## 5. Lower-timeframe execution (M1/M5/M15)

- **Tested:** M1-materialized loaders, M1 full-corpus response matrix,
  M5/M3/M30 ladder (C026), LTF confluence (C021), C1 factor at M1.
- **Failed:** no tradable LTF edge. The M1/HTF confluence factor (C1) is
  real but cost-defeated (see §8). LTF execution *infrastructure*
  (M1 materialization, next-bar-open policy, parity) is sound and kept.
- **Unresolved:** whether finer execution helps at a venue with
  meaningfully tighter spreads — not the current one.
- **Failure mode:** cost-defeated; infra is **not** blocked (it works).

## 6. Non-time bars (range / volatility bars)

- **Tested:** deterministic, lookahead-free range & volatility bar
  builders (`non_time_bars.py`); C029 (10-pip USD_JPY range-bar MTF
  breakout); non-time-bar feasibility study (7 majors × 13 thresholds);
  H16 and H03 front-gate screens.
- **Failed:** C029 REJECT_TRAIN_GATE (gross +0.084R, **net −0.019R**).
  H16 FAIL_FRONT_GATE (reversion ≈0.50, null-indistinguishable). H03
  FAIL_FRONT_GATE (weak tilt, cost-defeated, null-internal).
  Pre-registered stop-criterion met → **directional/microstructure
  non-time-bar search retired on this corpus** (infra kept).
- **Unresolved:** non-time bars on *new data* (longer history, non-USD
  crosses, true tick/L2).
- **Failure mode:** cost-defeated (C029) and no-effect (H16/H03);
  feasibility showed the wall is threshold-specific but cost-feasible ≠
  edge.

## 7. Microstructure-style ideas

- **Tested:** USD_JPY session/volatility/spread atlas; thin-move
  participation tertiles (H03); overshoot-exhaustion fade (H16);
  London-session post-compression continuation.
- **Failed:** direction is atlas-level ≈0.49 (coin-flip); rollover is
  cost-toxic; the London-continuation lead failed an overfit-hardened
  confirmation (Bonferroni ×12, trend-regime artifact). All NOT_READY /
  PAUSED.
- **Unresolved:** genuine microstructure needs **true tick / order-book
  data**, which the corpus lacks (FX volume here is a tick-count proxy).
- **Failure mode:** no-effect (direction) + data-blocked (no real L2).

## 8. Volatility / regime ideas

- **Tested:** vol-compression→expansion (USD_JPY); regime-conditioning
  of C1 (high-vol front gate); regime-switcher feasibility review (C3);
  vol-managed TSMOM regime overlay (C031, Moreira–Muir).
- **Failed:** compression→expansion falsified for tradability (smaller
  range = vol clustering; direction null). C1 high-vol: the effect is
  *genuine and C1-specific* (beats a vol-matched null on EUR/JPY) but
  **net-negative after cost on all three pairs** → FAIL_FRONT_GATE. The
  vol-managed overlay in C031 *hurt* rather than helped.
- **Unresolved:** vol timing is *predictable* (range clusters) but not
  *monetizable* on this cost structure; whether it monetizes at lower
  cost is open.
- **Failure mode:** cost-defeated (C1) / no-effect for direction.

## 9. Macro / event / carry ideas

- **Tested:** event/calendar campaign (C014); calendar-event-window
  anomaly; USD_JPY macro-regime-context tradeability; carry/financing
  readiness; vol-managed TSMOM as a structural USD/carry book (C031).
- **Failed:** C014 REJECT. Slow macro/rates/calendar context is
  lookahead-safe and latency-independent but gave **no actionable
  tradeability conditioning** (raw spread flat across macro cells;
  whipsaw ≈0.50; rate-regime non-identifiable/period-confounded, JP rate
  leg absent). C031's book is a structural USD bet that is within-null
  and financing-defeated.
- **Unresolved:** carry/macro needs **non-USD breadth, a real rate leg,
  10–15y history, and real financing rates** — all data-blocked on the
  current corpus.
- **Failure mode:** data-blocked (primary) + no-effect/financing-defeated.

## 10. Null models

- **Tested:** matched-null benchmark, filter-ablation, multiple-
  comparison correction, and cost-feasibility modules (the
  edge-discovery lab front gate); deduped null baselines (C011);
  per-campaign post-dedup null references (C012–C014).
- **Status:** **working and load-bearing.** The matched null is the
  reason several "positive" results were correctly killed as selection
  noise (C028) or "loses less than random" (C027 INFO pass). The lab is
  the mandated front gate for any new idea.
- **Unresolved:** none — this is infrastructure that does its job.
- **Failure mode:** n/a (this is a working gate, not a failed idea).

## 11. Cost / financing evidence

- **Tested:** spread/slippage/financing audit; per-instrument financing
  (bp/day) overlay on trade ledgers; observed-financing capture tooling
  (read-only, **parked** under the freeze); reconciliation tooling;
  campaign-002 financing retrospective; C031 financing decomposition.
- **Key findings:** spread alone defeats most intraday edges (gross
  edges 1–3 pips vs round-trip spread+slippage of the same order);
  financing dominates multi-day holds (C031: financing ≈4× spread); JPY
  pairs and crosses are *wider*, raising the wall exactly where some
  effects (C1) are strongest. The cost model is conservative but not
  pessimistic (typical retail, not best-case institutional).
- **Unresolved:** observed-rate calibration is parked until a strategy
  is near approval (not now). A materially lower cost structure
  (institutional/ECN/futures) is untested.
- **Failure mode:** n/a (this is the binding *constraint*, not a failed
  idea) — and it is the dominant cause of strategy rejections.

## 12. Parity / infrastructure evidence

- **Tested:** backtrader parity (hardened), entry-orchestration parity,
  walk-forward harness, free local parity verifier, M1 materialization
  + coverage verification, candle-aggregation timestamp audit, duplicate
  -candle contamination fix + post-dedup re-runs, next-bar-open policy.
- **Status:** **sound and not the blocker.** Parity is hardened;
  contamination was found and fixed; the walk-forward harness works;
  LTF/HTF data plumbing is verified. Some caveats remain (H4M1 coverage
  ≈70% of native H4; a 2020 M5-coverage gap).
- **Unresolved:** minor data-coverage caveats only; no infra blocks
  strategy search.
- **Failure mode:** infrastructure-blocked is **largely cleared** — the
  project is no longer code/infra blocked.

---

## Cross-cutting conclusion

- The **dominant failure mode across families is cost-defeated**, with
  **no-effect** second and **data-blocked** binding specifically on the
  macro/carry/microstructure lanes.
- **Infrastructure is not the blocker** — parity, null gating, LTF
  plumbing, and the front gate all work.
- The **single genuine effect found (C1)** is real but smaller than the
  cost of trading it on this corpus.
- The recurring "reopen" condition across every closeout is identical:
  **new data (10–15y history, non-USD crosses, true tick/L2, or a
  lower-cost venue) or a genuinely new external thesis — never a
  re-tune.**

This inventory feeds the structural cost analysis (Phase 2) and the
corpus viability decision (Phase 3).
