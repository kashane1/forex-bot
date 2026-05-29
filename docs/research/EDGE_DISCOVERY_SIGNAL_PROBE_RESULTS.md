# EDGE_DISCOVERY_SIGNAL_PROBE_RESULTS

**Status:** diagnostic / signal-probe results (Phase 3 of
`research-edge-discovery-front-gate-idea-selection-001`). Protocol **level 2**
only — forward-return information and a cheap random-timestamp comparison. No
strategy is built, no edge is claimed, no campaign is created, no test lockbox
is opened. Maximum status of anything here is *candidate hypothesis with cheap
supporting evidence*.

> Engine: `research/edge_discovery/front_gate_idea_selection/run_signal_probes.py`.
> Artifacts: `signal_probe_summary.csv`, `signal_probe_by_pair.csv`,
> `signal_probe_by_session.csv`, `signal_probe_forward_returns.json`,
> `signal_probe_null_comparison.json`, `skipped_signal_probes.json`.
> (Per-prototype signal ledgers and per-pair frames are reproducible local
> artifacts, regenerated deterministically by the script and **gitignored** to
> avoid committing bulky/raw candle-derived data.)

---

## Method

For each prototype: generate signals on the local store with **no lookahead**
(every rolling statistic shifted so bar *i* uses only bars ≤ *i*−1); enter at
the signal-bar mid close; measure **signed** forward log-returns at horizons
**1/3/6/12/24 bars**, pre- and post-cost. Cost = realized per-bar bid-ask
spread + 2×0.2-pip slip, as a fraction of entry. Null = **timestamp-random
same-pair** (redraw entry timestamps at random, *preserving each pair's signal
count and side composition*; 20 seeds, post-cost). This isolates whether the
signal's **timing** carries information beyond random timing at the same cost.

`prob_null_ge_strategy` = fraction of null seeds whose pooled post-cost mean ≥
the strategy's; `effect_size` = (strategy − null_mean)/null_std.

## Prototypes run (6) and skipped (2)

Run (all H4/H1, 7 majors, non-sparse): **z-score reversion (H4)**, **failed-
breakout fade (H4)**, **Asia-range breakout (H1)**, **NY-open continuation
(H1)**, **vol compression→expansion (H4)**, plus a **USD_JPY z-score-reversion
overlay**. Skipped (`skipped_signal_probes.json`): **carry/financing swing**
(no local carry/swap-rate table; FRED has the US leg only) and **sub-hour open
expansion** (no local M1/M5/M15/M30 to resolve the open bar) — both
data/compatibility-blocked, consistent with Phases 0–1.

## Headline: every prototype is net-negative post-cost; two carry real *information*

| Prototype | n | post h6 | post h12 | post h24 | best prob_null≥strat | best effect | hit h12 |
|---|---|---|---|---|---|---|---|
| **z-score reversion (H4)** | 11,935 | −0.000157 | **+0.000048** | **+0.000071** | 0.00 (h6–h24) | **+5.58** (h12) | 0.505 |
| **failed-breakout fade (H4)** | 8,324 | −0.000072 | **+0.000069** | −0.000006 | 0.00 (h1–h24) | +4.03 (h12) | 0.508 |
| Asia-range breakout (H1) | 9,441 | −0.000213 | −0.000219 | −0.000191 | 0.00 (h1 only) | +2.54 (h1) | 0.480 |
| NY-open continuation (H1) | 11,565 | −0.000283 | — | — | 0.55 (h6) | −0.42 | 0.459 |
| vol compression→expansion (H4) | 3,199 | −0.000440 | — | — | 0.95 (h6) | −1.38 | 0.471 |
| USD_JPY z-score overlay (H4) | 1,731 | −0.000246 | +0.000117 | +0.000045 | 0.10 (h12) | +1.43 (h12) | 0.522 |

### Forward-return information

- **z-score reversion (H4)** — pre-cost mean rises monotonically with horizon
  (+0.000009 → +0.000341 from h1→h24): a genuine, persistent **mean-reversion
  drift**. It **beats the cost-matched random-timestamp null with `prob_null_ge
  = 0.00` from h6 onward** (effect +2.6 → +5.6). Crucially, the *gross* drift
  outgrows the cost drag by **h12**, where post-cost turns marginally positive
  (+0.000048, hit 0.505) and stays positive at h24 (+0.000071). This is the one
  prototype with both (a) clear information beyond null and (b) post-cost
  positivity at the horizon it would actually trade.
- **failed-breakout fade (H4)** — same qualitative shape; beats null strongly
  (effect ~4), post-cost barely positive only at **h12** (+0.000069), back to ~0
  by h24. A secondary candidate, weaker and narrower than z-score reversion.
- **Asia-range breakout (H1)** — pre-cost ≈ 0; post-cost negative at every
  horizon; the only above-null point is h1 (where both strategy and null ≈
  −cost). Hit rate low (0.40–0.49). **No usable forward-return edge.**
- **NY-open continuation (H1)** — at/below null (prob 0.55, effect −0.42).
  **Continuation is null** at the NY handoff.
- **vol compression→expansion (H4)** — **worse than null** (prob 0.95, effect
  −1.38). Confirms, at a fresh H4 band, the recurring pattern: vol expansion is
  real but its **direction is null/anti-informative**. (Matches the prior
  USD_JPY vol-compression→expansion falsification.)
- **USD_JPY z-score overlay** — **weaker than the all-pair version** and
  *below* null at short horizons (prob 1.00, effect −2.08 at h1); only turns
  positive at h12 and even then under-performs the pooled all-pair signal
  (prob 0.10 vs 0.00; effect 1.43 vs 5.58). **Refutes a USD_JPY-specific
  reversion edge** — USD_JPY's value is cost, not signal.

### Cost-adjusted reading and the honesty caveats

- The post-cost positive means for z-score reversion at h12/h24 are **wafer-thin
  (≈ 0.005–0.007% per trade)** with **hit rate ≈ 0.50** — the positive
  expectancy is a small asymmetry, not a win-rate edge.
- The cost overlay uses realized spread + 0.2-pip slip. A more conservative slip
  (e.g. 0.5–1.0 pip, as event/illiquid fills warrant) would erase the h12
  +0.000048 entirely. **The edge sits inside the cost-assumption uncertainty
  band.** This must be stress-tested before any campaign claim.
- The h6 by-pair breakdown shows the (still-negative) per-pair means are
  **not concentrated in one pair** but are also **not uniformly positive**
  (AUD_USD/EUR_USD least-negative; USD_CHF/NZD_USD worst) — a pair-holdout
  fragility check is required (Phase 4 matrix-sanity).
- By session, the reversion drift is least-negative in **asia/london** and worst
  in **new_york/late** (where spreads are widest) — consistent with cost, not a
  distinct session edge.

## Which signals deserve matched-null / ablation follow-up?

- **z-score reversion (H4)** → **YES**: clear forward-return information beyond a
  cost-matched random-timestamp null, post-cost-positive at h12/h24. Take to
  Phase 4 (side-shuffled, session-matched, pair-matched, full matched null +
  matrix sanity / pair-holdout) at horizon **h12**.
- **failed-breakout fade (H4)** → **secondary YES**: weaker/narrower; run the
  same Phase-4 battery to see whether it is an independent signal or the same
  reversion tendency in a different costume.
- **Asia-range breakout (H1), NY-open continuation (H1), vol
  compression→expansion (H4), USD_JPY overlay** → **NO**: REJECT_CHEAPLY at the
  probe stage — null-confirming (or null-refuting in the wrong direction) after
  cost. No matched-null follow-up warranted.

**No edge is claimed.** Phase 4 tests whether the two surviving prototypes'
information persists against *structure-matched* nulls (the protocol's binding
bar) and whether it is a robust multi-pair effect or selection noise.
