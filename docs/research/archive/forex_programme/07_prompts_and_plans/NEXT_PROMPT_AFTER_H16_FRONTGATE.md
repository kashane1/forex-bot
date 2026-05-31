# Next prompt after the H16 front-gate screen

**Sprint:** `research-non-time-bar-overshoot-frontgate-001` · Phase 7
**Status:** drafted only — **do NOT execute in this sprint.**

The H16 verdict is **`FAIL_FRONT_GATE`** (decisive: no gradient, reversion ≈ 0.50,
cost-defeated, null-indistinguishable). **Recommendation: abandon H16.** It is removed
from the live shortlist and should not be scaffolded, tuned, or re-screened on this
corpus.

What remains is the **one pre-registered fallback** from the thesis-discovery sprint —
**H03 (thin-move fade)** — which was declared *before* any screen ran, so screening it
once is not a post-hoc variant hunt. Two options are drafted below.

- **Recommended: Prompt A** — run the single pre-registered H03 fallback **front-gate
  screen** (cheap; reuses the H16 harness). The prior is strongly toward another null
  (every directional FX family on this corpus has failed), but H03 is a *distinct*
  microstructure idea (move-quality, not completion-geometry) and deserves its one
  pre-registered shot.
- **Prompt B** — if you'd rather stop spending screens, a docs-only **closeout** that
  records the non-time-bar directional search as exhausted on current data.

**If H03 (Prompt A) also FAILS, do not generate further ideas on this corpus** — move to
Prompt B (retire directional non-time-bar search; reopen only with new data: ≥ 10–15y
history, non-USD crosses, or true tick data).

---

## Prompt A (recommended) — H03 thin-move fade front-gate screen

```
We are starting a front-gate screening sprint from clean, updated origin/main.

Branch:
research-non-time-bar-thinmove-frontgate-001

Context:
- H16 (overshoot-exhaustion fade) FAILED the front gate
  (docs/research/H16_FRONTGATE_DECISION.md): no gradient, reversion ~0.50,
  cost-defeated, null-indistinguishable on USD_JPY/EUR_USD/GBP_USD.
- H03 (thin-move fade) is the pre-registered fallback from the thesis-discovery sprint
  (docs/research/NON_TIME_BAR_FINAL_SHORTLIST.md). Thesis: when a range bar completes
  its price travel on UNUSUALLY LOW tick-volume (a "thin", low-participation move),
  the next bar(s) tend to REVERSE; the signal is travel-per-unit-volume (or simply the
  completing bar's tick-volume), NOT the move itself.

Goal:
Screen H03 through the SAME conditional-distribution harness used for H16
(src/forex_bot/research/overshoot_exhaustion_screen.py +
scripts/screen_h16_overshoot_exhaustion.py), bucketing by the completing bar's
tick-VOLUME (low/…/high) instead of overshoot, and measuring conditional fade returns.
Return a FAIL / INCONCLUSIVE / PASS verdict.

This is a SCREEN, not a campaign. Hard rules (identical to the H16 screen):
- No campaign, no CAMPAIGN_030, no scaffold, no approval, no approved_strategies edit,
  no paper/demo/live, no OANDA, no credentials, no backtest runner, no train/val/test
  split, no lockbox, no edge claim, no signal emission, no threshold optimisation.
- Local M1 only; C029 train window (2021-05-27..2023-12-31); 30-pip range bars;
  USD_JPY/EUR_USD/GBP_USD; 1/2/3-bar horizons; C029 cost model; seeded shuffle null;
  H12 spread-state filter reported. Pre-register the thin-volume bucket edges
  (quartiles) and BOTH directions before running.
- Commit compact diagnostics + docs + tests only; no raw M1/full bars/ledgers.

Method:
0. Baseline audit; branch; confirm approved_strategies empty + loops refuse; run the
   five validators.
1. Extend the existing harness with a per-bar tick-volume metric (reuse the bars'
   `volume` field; do NOT duplicate bar builders) and bucket by volume quartiles
   (and a thin-tail). Add unit tests for the new pure helper.
2. Run distribution + conditional-behavior + cost + null studies (reuse the H16 doc
   structure).
3. Verdict per the same criteria. If H03 also FAILS, record directional non-time-bar
   search as EXHAUSTED on the current corpus (new data required to reopen).
4. Final validation + summary.

Deliver: branch, commit hashes per phase, files changed, the four study findings, the
verdict, confirmation no campaign/approval, and the recommended next step (retire/new
data if FAIL; scaffold-prompt-only draft if PASS).
```

## Prompt B — close out directional non-time-bar search (docs-only)

```
We are starting a research closeout sprint from clean, updated origin/main.

Branch:
research-non-time-bar-directional-closeout-001

Context:
- The non-time-bar feasibility study showed cost stops dominating at wide thresholds,
  but every directional idea screened since has failed: H16 overshoot-exhaustion
  FAILED the front gate; the broader repo has rejected breakout (C015/017/025/029),
  pullback (C020-023), reversion (C008/027), momentum (C016/C031), and relative-value
  (C028) on this 7-major M1 corpus.

Goal (docs/archive only):
Record the directional / microstructure non-time-bar search as EXHAUSTED on the current
data; keep the (tested) infrastructure; integrate the H16 screen + feasibility + thesis
docs into the research backlog / EVIDENCE_INDEX; state the strict reopen criteria (new
data: >=10-15y history, non-USD crosses, or true tick/L2 data; or a fundamentally new
external thesis). No campaign, no approval, no paper/demo/live, no OANDA. Confirm
merge-readiness + run the five validators.
```

---

## Why no campaign prompt

H16 FAILED, so there is nothing to scaffold. Even on a future PASS (of H03 or anything
else), a campaign requires a *separate* fresh pre-commit with a newly-assigned number —
never created from a screen. This sprint's chain ends at a verdict.
