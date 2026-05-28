# USD_JPY Volatility-Compression → Expansion — Diagnostic Result

**Sprint:** `usdjpy-volatility-compression-expansion-diagnostic-001` · **Phase 3**
**Tooling:** `scripts/analyze_usdjpy_volatility_compression_expansion.py`
**Inputs:** `research/usdjpy_vol_compression_expansion/dataset_manifest.json` +
gitignored per-bar parquet (95,756 M15 bars, train 59,852 / val 35,904; **TEST sealed**).
**Output:** `research/usdjpy_vol_compression_expansion/analysis_summary.json`

> **Descriptive diagnostic, NOT a tradable-edge claim.** "Expansion exists" is kept
> strictly separate from "tradable edge exists." Buckets are predeclared (compression =
> ≥3 of 4 percentile features {range, ATR, bandwidth, realized-vol} ≤ cut; primary cut
> 0.20; grid 0.10/0.20/0.30). No tuning, no best-cell selection. No campaign, no C024,
> no C023, no approval, no verdict change.

---

## Headline

**The literal "compression → expansion" thesis is contradicted in the form that would
matter for a strategy.** Compression predicts *smaller absolute* future range, not
larger — i.e. **volatility clustering** (low vol persists). The proportional expansion
that does exist (future range relative to the bar's own low ATR) is real but **not
directionally capturable**, and the one mildly-positive, both-split-consistent signal —
elevated breakout follow-through after compression at long horizons — is small and
direction-blind ex ante. Net: a **robust descriptive structure, no evident
cost-surviving live edge.**

---

## Answers to the ten questions

### Q1. Does compression predict larger future range? — **NO (opposite).**
Absolute future range is **smaller** after compression at every horizon, on **both**
splits, across the whole predeclared cut grid and every single feature:

| horizon | abs range ratio (comp/base) train | validation |
|---|---|---|
| h4 (1h) | 0.786 | 0.780 |
| h8 (2h) | 0.856 | 0.858 |
| h16 (4h) | 0.901 | 0.914 |
| h32 (8h) | 0.925 | 0.922 |

Cut-grid robustness @h8: train 0.83/0.86/0.85, val 0.83/0.86/0.86. Per-feature @h8 all
< 1 (range_pct strongest at 0.75/0.78). This is textbook **vol clustering**, the
opposite of what a compression-breakout needs.

### Q2. Does compression predict directional expansion? — **NO.**
`p_up` sits at 0.44–0.53 across horizons/splits; mean signed move is sub-pip and
**sign-inconsistent across splits** (e.g. h32 train +0.63 vs val +0.25; h8 train −0.54
vs val −0.35). No directional predictability — consistent with the atlas-level null.

### Q3. Does compression predict breakout follow-through? — **Mildly, and consistently.**
Conditional on a prior-range breakout, follow-through is a few points higher after
compression, on both splits, growing with horizon:

| horizon | follow-through comp/base train | validation |
|---|---|---|
| h8 | 0.446 / 0.403 | 0.458 / 0.412 |
| h16 | 0.531 / 0.466 | 0.569 / 0.468 |
| h32 | 0.645 / 0.551 | 0.682 / 0.546 |

This is the **only positive, both-split-consistent** conditioning. Caveat: compressed
breakout *rate* is very high at long horizons (0.94–0.99) because a low-ATR bar's tiny
prior range is mechanically exceeded, and follow-through uses a 0.5·(low ATR) buffer —
so much of this is small-move mechanics, not a large directional thrust.

### Q4. Does compression predict false breakout? — **NO meaningful conditioning.**
Compressed false-breakout rate ≈ baseline (0.44–0.58, within ~0.05 either way). No
compression-conditioned fade edge.

### Q5. Does any effect hold in BOTH train and validation? — **Yes, three of them.**
(a) absolute range ratio < 1 (clustering); (b) relative range/ATR ratio > 1
(proportional expansion, 1.08–1.29); (c) mildly elevated long-horizon follow-through.
The directional nulls are also consistent.

### Q6. Does the effect survive spread/cost context? — **No live-usable survival shown.**
The only positive cost numbers are the **hindsight oracle** (pick the better of MFE/MAE
after the fact): oracle-best minus a deliberately-optimistic 4.4-pip round-trip is
+17.6 (train) / +23.1 (val) — but that is **not live-tradable** (you cannot choose the
winning side in advance). With direction null, there is no demonstrated way to convert
the proportional expansion into PnL net of cost. Absolute future moves after compression
are *below* average (Q1), shrinking the room a real exit could capture.

### Q7. Is it session-dependent? — **No directional rescue.**
`p_up` stays 0.44–0.53 in every session; absolute range ratio < 1 in every session on
both splits. No session makes direction predictable.

### Q8. Stronger in Tokyo→London / London→NY / NY? — **No stable structure.**
The only large signed-move cells are tiny-n and **sign-flip across splits** (overlap:
train −1.65 vs val +2.67 on n≈200–230; rollover: train −1.96 vs val +2.54) — i.e.
noise. The high-n compression sessions (Tokyo, off-hours) show nothing directional.

### Q9. Is sample size preserved? — **Yes (overall); thin per-session.**
Primary-cut compressed events: ~8,541 train / 5,235 val — ample. Session subsets get
thin (overlap ~200–230), which is why their cells are unreliable.

### Q10. Directionally tradable or only volatility-tradable? — **At most volatility-,
not directionally-tradable.** Proportional (normalized) expansion exists; absolute
expansion does not (it shrinks); direction is unpredictable. There is no evident
directional, cost-surviving, live-usable edge.

---

## Interpretation

- **Real, robust, descriptive:** USD_JPY M15 volatility *clusters* (compression →
  continued below-average absolute range), and compressed bars expand *proportionally*
  to their suppressed ATR. Breakout follow-through after compression is mildly elevated
  at multi-hour horizons on both splits.
- **Not shown:** any directional predictability, any larger *absolute* move, or any
  cost-surviving live monetization. The single positive conditional (follow-through) is
  small, partly mechanical, and direction-blind ex ante (you only learn the side once
  the break happens).

## Decision on Phase 4

Per the precommit, Phase 4 monetization runs only if a **stable** compression→expansion
relationship exists. A stable relationship exists, but its tradable-relevant sign is
**unfavorable** (clustering) except for one weak conditional (post-compression breakout
follow-through). To avoid prematurely dismissing the steelman, **Phase 4 will run a
bounded, predeclared monetization diagnostic** on exactly the structures the data
suggests — breakout-continuation (the follow-through signal), false-breakout fade, and
a direction-agnostic straddle proxy — all net of cost. If none clears cost on both
splits, the readiness verdict becomes NOT_READY / PAUSE.
