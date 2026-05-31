# Cross Relative-Value — Null Comparison (Phase 5)

**Sprint:** `research-cross-relative-value-factor-validation-001` · Phase 5
**Status:** RESULT (descriptive; verdict deferred to Phase 7). Four frozen nulls
(protocol §9), 200 seeds. Figures from committed
`docs/research/cross_relative_value/nulls.csv`. `z = (observed_stretched_reversion
− null_mean) / null_std` on the pooled stretched bucket.
**Date:** 2026-05-30.

The four nulls each break a different part of the deviation→reversion link:
- **Unconditional** — reversion over all bars (any |z|): does the residual revert
  regardless of being stretched?
- **Randomized relationships** — the *most conservative* null: rebuild each
  residual from a **wrong triangle** (a derangement of the leg templates); does the
  *true* no-arb triangle revert more than a false one?
- **Shuffled timestamps** — forward window drawn from a random bar: breaks the
  deviation→reversion time link.
- **Matched** — session-matched random bars: removes session structure.

---

## 1. Pooled stretched reversion — matched-Z by horizon × null

```
horizon  matched  randomized_relationships  shuffled_timestamps  unconditional
   5      103.3            9.48                   138.9              432.9
  15      108.1            6.34                   149.0              445.1
  30      112.5            3.87                   154.2              421.5
  60      124.8            2.57                   134.2              410.8
 240      134.0            3.90                   119.7              370.5
```
**obs reversion:** 0.39 / 0.42 / 0.44 / 0.45 / 0.51 bp at 5/15/30/60/240 min.

## 2. Does the reversion exceed null expectations?

**Yes — overwhelmingly. 20 of 20 cells clear |z| ≥ 2.** Three of the four nulls
produce enormous Z (matched 103–134, shuffled 120–155, unconditional 370–445)
because the stretched residual reverts far more than a random/unconditioned bar.
This is unambiguously **not** a within-null result — it is the strongest
null-separation in the programme.

## 3. The decisive null — randomized relationships

The conservative **randomized-relationships** null (true triangle vs *wrong*
triangle) is the one that isolates whether reversion is a property of the **genuine
no-arbitrage relationship** rather than a generic mean-reverting series:
- It clears |z| ≥ 2 at **all 5 horizons** (9.48, 6.34, 3.87, 2.57, 3.90) → the
  **true** triangle reverts genuinely more than false leg-combinations. The
  reversion is a property of the real no-arb relationship, not an artifact of any
  ratio of co-moving instruments.
- **But its z is largest at the shortest horizon (9.48 at 5 min) and decays to
  ~2.6 by 60 min** — i.e. the *excess* reversion of the true triangle over false
  ones is concentrated at **short horizons**. This is consistent with the Phase-3
  front-loaded profile: a large part of the true-triangle advantage is fast
  stale-quote catch-up. (At 240 min it ticks back to 3.90, driven by NZD_JPY's
  genuine slow reversion.)

## 4. Reading

The reversion is **real and strongly null-separated** under all four nulls,
including the conservative randomized-relationships null — so it is a genuine
property of the no-arbitrage triangle, not a generic or spurious effect. The
*horizon decay* of the randomized-relationships z, together with the Phase-3
front-loading and the Phase-2 scale facts, locates much of the effect in the
short-horizon microstructure band — while the long-horizon residual (NZD_JPY and
the JPY complex) carries a genuine slow component.

---

## 5. Phase-5 reading (no verdict here)

The triangular reversion **decisively exceeds all four nulls** (20/20 cells clear;
the conservative randomized-relationships null clears at every horizon). This
**rules out FACTOR_REJECTED's "within null" criterion** — the effect is genuinely
real. The open question for Phase 7 is purely the §11 distinction: genuine RV
factor vs a real-but-within-cost-band no-arb/microstructure property. Phase 6 tests
robustness; the shared-leg cointegration contrast (Phase 6) further localizes where
the genuine reversion lives.
