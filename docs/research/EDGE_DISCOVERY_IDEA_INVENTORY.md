# EDGE_DISCOVERY_IDEA_INVENTORY

**Status:** diagnostic / idea-selection inventory (Phase 1 of
`research-edge-discovery-front-gate-idea-selection-001`). Feasibility and
inventory only — no strategy is implemented, no campaign is created, nothing is
approved. Maximum status of anything here is *candidate hypothesis to be
screened cheaply*.

> Plan: [`EDGE_DISCOVERY_FRONT_GATE_IDEA_SELECTION_001_PLAN.md`](EDGE_DISCOVERY_FRONT_GATE_IDEA_SELECTION_001_PLAN.md).
> Gate phrasing: [`EDGE_DISCOVERY_PROTOCOL.md`](EDGE_DISCOVERY_PROTOCOL.md),
> [`PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md`](PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md).

---

## Data reality that constrains every idea (from Phase 0)

Local canonical store `data/campaign_002.sqlite3`: **7 majors** (EUR_USD,
GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD) at **H4, H1, D** only,
2020-01 → 2026-05. **No M1/M3/M5/M15/M30.** Event fixture
`campaign_014_events.json`. Slow-macro FRED caches. Financing proxy via
`forex_bot.financing`.

Consequences applied uniformly below:
- **Session granularity is coarse on H4.** A 4-hour bar straddles session
  boundaries; the cleanest session timing/lab work is on **H1** (24 bars/day,
  clean Asia/London/NY buckets via `matched_nulls.session_bucket_utc`). H4 is
  better for swing/range/volatility-regime ideas than for open-timing ideas.
- Any "open expansion / opening-range" idea that genuinely needs sub-hour
  resolution is **COMPATIBILITY_BLOCKED** here; the H1 approximation is the best
  available and must be labelled as an approximation.
- Structural distinctness vs rejected work: C025/C026 were **M5/M3–M30
  Donchian-breakout + HTF-confluence** families. Any H1/H4 idea on the majors is
  on a *different timeframe band* and (for most) a *different signal class*;
  breakout-flavored ideas must be explicitly differentiated from the rejected
  Donchian family (different TF band + different trigger construction), not a
  revival.

## Lab diagnostics legend

`[COST]` cost_feasibility/costs · `[FWD]` windows.compute_forward_returns ·
`[NULL]` matched_nulls · `[ABL]` filter_ablation · `[MC]` multiple_comparison/
matrix_sanity · `[EXIT]` studies/exit_asymmetry.

---

## Inventory

### 1. Asia range breakout
- **Hypothesis:** price breaking the prior Asia-session range high/low continues
  in the breakout direction into London.
- **Expected behavior:** directional follow-through after the Asia range is
  resolved; edge concentrated near London open.
- **Timeframe(s):** H1 (range built from Asia H1 bars; trigger on H1 close
  beyond range). H4 too coarse to define an Asia range cleanly.
- **Pair(s):** 7 majors; JPY/AUD/NZD plausibly more Asia-active.
- **Required data:** H1 OHLC (have). Session buckets (have, `session_bucket_utc`).
- **Signal-ledger fields:** instrument, side, entry_time, range_high/low, bars_held.
- **Filters:** session-of-trigger, Asia-range width percentile, direction.
- **Cost sensitivity:** moderate — H1 spread/ATR (Phase 2 measures); breakout
  entries pay spread at a fast-moving moment.
- **Likely failure mode:** breakouts mean-revert (false breaks); cost eats the
  small continuation; signal is a vol-clustering artifact, not direction.
- **Existing data supports screening?** Yes (H1 approximation of session range).
- **Diagnostics:** [COST] [FWD] [NULL session/timestamp] [ABL] [MC].
- **Structurally distinct from C025/C026?** Yes — H1 (not M5), session-range
  trigger (not Donchian-N + HTF confluence). Must show distinct construction.

### 2. Asia range fade
- **Hypothesis:** a sweep of the Asia range high/low that *re-enters* the range
  (failed breakout) reverts back through the range.
- **Expected behavior:** mean reversion after a liquidity-sweep wick.
- **Timeframe(s):** H1. **Pair(s):** 7 majors.
- **Required data:** H1 OHLC (have); intrabar sweep detection approximated by
  H1 high/low piercing then close back inside.
- **Signal-ledger fields:** instrument, side (opposite the sweep), entry_time,
  swept_level, bars_held.
- **Filters:** session, range-width, depth-of-sweep, re-entry confirmation.
- **Cost sensitivity:** moderate; fade entries can get better fills than chases.
- **Failure mode:** trend days run through the range (fade gets steamrolled);
  H1 cannot see the true sweep wick — approximation error.
- **Existing data supports screening?** Partially — H1 approximates the sweep;
  flag the resolution limitation.
- **Diagnostics:** [COST] [FWD] [NULL session/side-shuffle] [ABL] [MC].
- **Distinct from C025/C026?** Yes — fade (mean-reversion), opposite class to
  the rejected continuation-breakout family.

### 3. London open expansion
- **Hypothesis:** after a compressed Asia range, the London open produces a
  volatility expansion (range/ATR jump), tradable as a breakout of the Asia range
  at/after London open.
- **Expected behavior:** vol expansion is *predictable in magnitude* (prior
  USD_JPY work: vol timing predictable, direction null) — the open question is
  whether **direction** is tradable, not whether vol expands.
- **Timeframe(s):** H1. **Pair(s):** EUR/GBP (London-centric) + 7 majors.
- **Required data:** H1 OHLC (have); Asia-compression measure + London bucket.
- **Signal-ledger fields:** instrument, side, entry_time, asia_range_width,
  expansion_ratio, bars_held.
- **Filters:** Asia-compression percentile, London bucket, direction.
- **Cost sensitivity:** moderate–high (entering into the expansion pays spread).
- **Failure mode:** *the known one* — vol expands predictably but direction is a
  ~0.50 coin-flip, so there is range but no edge (the recurring USD_JPY result).
- **Existing data supports screening?** Yes (H1).
- **Diagnostics:** [COST] [FWD direction] [NULL session] [ABL] [MC]. The decisive
  test is whether *directional* forward return beats the session-matched null.
- **Distinct from C025/C026?** Yes — H1 session-conditioned, and partially
  overlaps prior USD_JPY vol-compression→expansion work (which was **FALSIFIED
  for tradability**). Revival risk: must NOT re-run the falsified single-pair
  USD_JPY monetization; only a *multi-pair direction* probe is new.

### 4. New York open continuation / reversal
- **Hypothesis:** the NY open (and London/NY overlap) either continues the
  London move (continuation) or reverses it (reversal).
- **Expected behavior:** overlap is the highest-liquidity window; momentum or
  reversal around the NY handoff.
- **Timeframe(s):** H1. **Pair(s):** 7 majors (USD pairs especially).
- **Required data:** H1 OHLC (have); london/london_ny_overlap/new_york buckets.
- **Signal-ledger fields:** instrument, side, entry_time, prior_london_return,
  bars_held.
- **Filters:** session bucket, prior-London-move sign/magnitude, direction.
- **Cost sensitivity:** moderate (overlap usually has the tightest spreads).
- **Failure mode:** both continuation and reversal net to ~null after cost;
  multiple-comparison risk from testing both directions.
- **Existing data supports screening?** Yes (H1).
- **Diagnostics:** [COST] [FWD both signs] [NULL session] [MC] (two directions ⇒
  multiple-comparison sanity matters).
- **Distinct from C025/C026?** Yes.

### 5. USD_JPY single-pair opportunity probe
- **Hypothesis:** USD_JPY (repeatedly cheapest/least-bad) carries a single-pair
  session-momentum or range edge the all-pair average hides.
- **Expected behavior:** unknown — prior USD_JPY threads (microstructure,
  vol-compression, macro-context) were all **null/exhausted**; this is a fresh
  H1/H4 opportunity-map probe, not a revival of those theses.
- **Timeframe(s):** H1 + H4. **Pair(s):** USD_JPY only, vs all-pair benchmark.
- **Required data:** H1/H4 OHLC (have).
- **Signal-ledger fields:** as for whichever session/range signal it pairs with.
- **Cost sensitivity:** historically *advantaged* on USD_JPY — Phase 2 confirms.
- **Failure mode:** single-pair selection artifact (FRAGILE_SINGLE_PAIR_RESULT);
  the cheap-cost advantage is real but unaccompanied by directional edge.
- **Existing data supports screening?** Yes.
- **Diagnostics:** [COST] [FWD] [NULL pair_matched] [MC single-pair fragility].
  Treated as a *concentration check overlay* on families 1–4/6–9, not a
  standalone signal. Single-pair results need explicit precommit to be eligible.
- **Distinct from C025/C026?** Yes (those were multi-pair lower-TF). **Revival
  guard:** must not reopen the closed USD_JPY microstructure/macro threads.

### 6. z-score mean reversion with regime/context filters
- **Hypothesis:** large standardized deviations from a rolling mean revert,
  conditional on a regime filter (e.g. low-trend / range regime).
- **Expected behavior:** reversion when the market is ranging; failure when
  trending (the classic regime dependence).
- **Timeframe(s):** H1 + H4. **Pair(s):** 7 majors.
- **Required data:** H1/H4 OHLC (have); rolling mean/std (compute), ATR/trend
  regime proxy (compute).
- **Signal-ledger fields:** instrument, side (toward mean), entry_time, zscore,
  regime_flag, bars_held.
- **Filters:** |z| threshold, regime (trend vs range), session, direction.
- **Cost sensitivity:** moderate; reversion targets are small so cost-in-R matters.
- **Failure mode:** reversion edge is a cost mirage; regime filter only shrinks
  sample (FILTER_ONLY_REDUCES_SAMPLE) without adding edge.
- **Existing data supports screening?** Yes — one of the cleanest to probe on H4/H1.
- **Diagnostics:** [COST] [FWD reversion sign] [NULL timestamp/side] [ABL regime
  filter] [MC]. Filter ablation is the crux (does the regime filter earn its keep?).
- **Distinct from C025/C026?** Yes — mean-reversion class, not breakout.

### 7. Failed-breakout fade
- **Hypothesis:** a breakout beyond a recent N-bar high/low that fails (price
  closes back inside within k bars) reverts.
- **Expected behavior:** mean reversion after trapped-breakout liquidity.
- **Timeframe(s):** H1 + H4. **Pair(s):** 7 majors.
- **Required data:** H1/H4 OHLC (have); rolling high/low (compute).
- **Signal-ledger fields:** instrument, side (fade), entry_time, broken_level,
  bars_to_failure, bars_held.
- **Filters:** breakout lookback N, failure window k, session, direction.
- **Cost sensitivity:** moderate.
- **Failure mode:** in trends, "failed" breakouts resume; definitional
  sensitivity to N/k creates multiple-comparison risk.
- **Existing data supports screening?** Yes.
- **Diagnostics:** [COST] [FWD] [NULL timestamp/side] [ABL] [MC over N/k grid].
- **Distinct from C025/C026?** Partially — it *uses* a breakout definition like
  Donchian but **fades** it (opposite side) on H1/H4. Must be framed as a
  distinct mean-reversion idea, not a Donchian-continuation revival.

### 8. Volatility compression → expansion
- **Hypothesis:** a low-ATR / narrow-range (compressed) regime precedes a
  volatility expansion, tradable as a breakout when expansion begins.
- **Expected behavior:** compression predicts *expansion magnitude* but
  (prior result) **not direction** — vol clustering, not directional edge.
- **Timeframe(s):** H4 (natural swing TF) + H1. **Pair(s):** 7 majors.
- **Required data:** H4/H1 OHLC (have); ATR + range-width percentile (compute).
- **Signal-ledger fields:** instrument, side, entry_time, atr_percentile,
  width_percentile, bars_held.
- **Failure mode:** the **already-observed** one — compression→expansion is real
  but direction is null (vol-compression→expansion thread was FALSIFIED for
  tradability on USD_JPY). The only new angle is **multi-pair, multi-TF
  direction** under a strict matched null.
- **Existing data supports screening?** Yes.
- **Diagnostics:** [COST] [FWD direction] [NULL session/timestamp] [MC].
- **Distinct from C025/C026?** Different TF band (H4/H1 not M5). **Revival
  guard:** do not re-run the closed USD_JPY-specific monetization; only a fresh
  cross-pair direction screen is permissible.

### 9. High-volatility exhaustion → reversal
- **Hypothesis:** after an extreme high-ATR / large-range move, momentum exhausts
  and price reverts.
- **Expected behavior:** reversal after a volatility spike (capitulation/blowoff).
- **Timeframe(s):** H4 + H1. **Pair(s):** 7 majors.
- **Required data:** H4/H1 OHLC (have); ATR/range percentile (compute).
- **Signal-ledger fields:** instrument, side (reversal), entry_time,
  range_percentile, bars_held.
- **Filters:** range/ATR percentile threshold, session, direction.
- **Cost sensitivity:** moderate; spreads widen during high-vol → cost worse
  exactly when the signal fires (adverse).
- **Failure mode:** high-vol = wide spreads (cost-hostile precisely at signal);
  "exhaustion" continues in a true trend.
- **Existing data supports screening?** Yes — but Phase 2 must check whether the
  high-vol cells are cost-hostile.
- **Diagnostics:** [COST in high-vol cells] [FWD] [NULL timestamp] [ABL] [MC].
- **Distinct from C025/C026?** Yes — mean-reversion class on H4/H1.

### 10. Event-window anomaly (existing fixtures only)
- **Hypothesis:** forward returns around fixture-defined event windows differ
  from non-event baseline (directional or vol).
- **Expected behavior:** event-driven vol; direction usually unpredictable.
- **Timeframe(s):** H1 + H4. **Pair(s):** 7 majors (or those the fixture covers).
- **Required data:** `campaign_014_events.json` (have, committed). **No new fetch.**
- **Signal-ledger fields:** instrument, side, entry_time, event_class, bars_held.
- **Cost sensitivity:** high — event spreads blow out.
- **Failure mode:** sparse events (few signals → INCONCLUSIVE_SPARSE);
  event spread cost dominates; fixture coverage thin.
- **Existing data supports screening?** Partially — only as far as the single
  committed fixture's coverage reaches; likely sparse. Prior `study_real_event_
  window.py` already exercises this path.
- **Diagnostics:** [COST] [FWD] [NULL timestamp]. Likely sparse-flagged.
- **Distinct from C025/C026?** Yes — orthogonal (event-conditioned).

### 11. Carry / financing-aware swing diagnostic
- **Hypothesis:** holding positions aligned with positive carry over multi-day
  swings adds (or financing drag subtracts) enough to matter.
- **Expected behavior:** small per-bar financing accrual; only relevant over
  long holds; cost-toxic at rollover (prior USD_JPY rollover finding).
- **Timeframe(s):** H4/D swing holds. **Pair(s):** 7 majors (JPY/CHF/AUD carry legs).
- **Required data:** OHLC (have) + a **financing/carry rate table**. Local: only
  the conservative worst-case `forex_bot.financing` proxy + slow FRED rate
  caches (DGS2/DGS10 = US only; **no JP/AU/CH legs**, no per-pair swap table).
- **Signal-ledger fields:** instrument, side, entry_time, bars_held,
  financing_fraction.
- **Cost sensitivity:** the whole idea *is* a cost/financing question.
- **Failure mode:** **data-blocked** — no per-pair carry/swap table; FRED has US
  leg only; the financing proxy is worst-case-only (not a directional carry signal).
- **Existing data supports screening?** **No** for a real carry signal. Only a
  *financing-drag stress diagnostic* is possible (how much does worst-case
  financing erode a long-hold swing?). Mark **COMPATIBILITY_BLOCKED** for carry
  edge; runnable only as a drag-stress note.
- **Diagnostics:** [COST financing overlay] only. No matched-null carry test
  possible without a carry-rate table.
- **Distinct from C025/C026?** Yes — orthogonal; but data-blocked here.

### 12. Pair / timeframe / session opportunity-map mining
- **Hypothesis (meta):** let measured market facts (cost, vol, session
  expansion) suggest *where* an edge could even exist, instead of forcing a
  preselected strategy.
- **Expected behavior:** produces the opportunity map that ranks pair×TF×session
  cells by cost feasibility and vol — the input to Phases 3–6.
- **Timeframe(s):** H1 + H4 (+ D context). **Pair(s):** all 7 majors.
- **Required data:** H1/H4/D OHLC (have).
- **Signal-ledger fields:** n/a (market-fact map, not a signal ledger).
- **Cost sensitivity:** it *measures* cost sensitivity.
- **Failure mode:** mistaking a cheap cell for an edge-bearing cell (cost ≠ edge).
- **Existing data supports screening?** Yes — this is Phase 2.
- **Diagnostics:** [COST] + ATR/vol/session stats. Feeds prototype selection.
- **Distinct from C025/C026?** It is meta/diagnostic, not a strategy.

---

## Feasibility summary (which can be screened cheaply here)

| # | Family | Screenable now? | Best TF | Class | Distinct from C025/C026 | Notes |
|---|---|---|---|---|---|---|
| 1 | Asia range breakout | Yes (H1 approx) | H1 | breakout | Yes | session-range, not Donchian |
| 2 | Asia range fade | Yes (H1 approx) | H1 | reversion | Yes | sweep approx on H1 |
| 3 | London open expansion | Yes (H1 approx) | H1 | breakout/vol | Yes (revival guard) | direction is the open question |
| 4 | NY open cont./rev. | Yes | H1 | both | Yes | 2 directions ⇒ MC risk |
| 5 | USD_JPY probe | Yes (overlay) | H1/H4 | concentration check | Yes (revival guard) | not standalone |
| 6 | z-score reversion + regime | Yes | H1/H4 | reversion | Yes | ablation is the crux |
| 7 | Failed-breakout fade | Yes | H1/H4 | reversion | Partially (guard) | fade not continuation |
| 8 | Vol compression→expansion | Yes | H4/H1 | breakout/vol | Yes (revival guard) | direction null risk |
| 9 | High-vol exhaustion→rev. | Yes | H4/H1 | reversion | Yes | cost-hostile cells risk |
| 10 | Event-window anomaly | Partial (sparse) | H1/H4 | event | Yes | fixture-coverage bound |
| 11 | Carry/financing swing | **No (data-blocked)** | H4/D | carry | Yes | no carry-rate table; drag-stress note only |
| 12 | Opportunity-map mining | Yes (= Phase 2) | H1/H4/D | meta | n/a | feeds 1–9 |

**Phase-3 prototype shortlist (provisional, pending Phase 2 opportunity map):**
families 1 (Asia breakout), 2/7 (failed-breakout / Asia fade — reversion),
4 (NY open), 6 (z-score reversion+regime), 8 (vol compression→expansion
direction), with family 5 (USD_JPY) applied as a single-pair concentration
overlay. Families 11 (carry) and the sub-hour resolution of 3/10 are noted as
data-/coverage-blocked. Final selection is made in Phase 3 from the Phase 2 map.

**This phase implements no strategy and creates no campaign.**
