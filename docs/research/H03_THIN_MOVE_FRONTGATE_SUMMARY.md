# H03 thin-move fade — front-gate screen SUMMARY (Phase 8)

**Sprint:** `research-non-time-bar-thin-move-frontgate-001`
**Date:** 2026-05-29 · **Type:** front-gate screen only · **Verdict:** `FAIL_FRONT_GATE`

> The **last** pre-registered non-time-bar candidate. H16 already failed; H03 now fails
> too → the directional/microstructure non-time-bar lane is **retired** on this corpus.
> No campaign, no approval, no lockbox, no train/val/test, freeze intact.

---

## 1. What was tested

The pre-registered H03 thesis: a 30-pip range bar that completes its travel on
**unusually low tick-count volume** ("thin", low-participation move) is more likely to
**mean-revert** over the next 1–3 bars than a high-participation completion. Measured as
conditional **fade returns** (positive ⇒ reversion), bucketed by per-pair volume tertiles
(low/medium/high) + a bottom-decile ultra-thin tail, on EUR_USD / GBP_USD / USD_JPY over
the C029 train window (2021-05-27 → 2023-12-31). Conditional distributions only — no
positions, PnL, signals, or lockbox.

## 2. Findings (one line each)

- **Participation distribution:** volume spans ~10× low→high per pair; ample sample
  (2,132 / 3,853 / 4,403 bars). But "thin" is **confounded** — low-volume bars complete
  in *minutes* (vs hours), **overshoot more** (USD_JPY 6.8 vs 3.4 pips → overlaps the
  failed H16), carry **wider spreads**, and skew to **Tokyo/rollover**.
- **Conditional behaviour:** reversion rate ≈ **0.50** everywhere (coin-flip). A weak
  correctly-signed average tilt (low−high > 0 on 7/9 cells) exists, but it is
  **non-monotone** (medium often ≥ low), **GBP-absent**, and driven by the *high* bucket
  drifting (continuation), not the low bucket reverting. Ultra-thin tail is erratic
  (continuation on EUR h1).
- **Cost feasibility:** the low-bucket fade beats its own (wider) round-trip cost on
  **EUR_USD only** (h2/h3), as fat-tailed drift; GBP_USD and USD_JPY **never** clear
  cost. Thin bars are the *most expensive* cell to trade.
- **Null comparison:** **0 of 18** cells beat the 95th-percentile shuffled-participation
  null; the lone borderline cell (EUR low-h3, p_ge 0.0525) is multiple-comparison-expected
  + cost-confounded selection noise (C028). No lift over the unconditional baseline.

## 3. Verdict

**`FAIL_FRONT_GATE`** — all five pre-registered falsifiers met. Not `INCONCLUSIVE`:
null-beating on zero pairs with an ample sample ⇒ flat + confounded, not under-powered.
Not `PASS`: no monotone gradient, cost-feasible on one pair only, null-internal
everywhere. H03 abandoned. Full reasoning in
[`H03_FRONTGATE_DECISION.md`](H03_FRONTGATE_DECISION.md).

## 4. Lane decision

The discovery sprint's stop-criterion (H16 **and** H03 both fail matched-null-post-cost)
is now triggered → **retire directional/microstructure non-time-bar search on the current
corpus.** Infrastructure and front-gate discipline are kept; reopen only with new data
(≥ 10–15y history, non-USD crosses, or true tick/L2 data) or a fundamentally new external
thesis, via a fresh pre-registered screen. See
[`NON_TIME_BAR_LANE_FINAL_DECISION.md`](NON_TIME_BAR_LANE_FINAL_DECISION.md).

## 5. Validation (Phase 8)

| check | result |
|---|---|
| `pytest tests/ -q` | **2358 passed, 3 skipped** (skips = absent local fixtures) |
| `ruff check src scripts tests` | **All checks passed** |
| `check_research_freeze.py` | **ALL CHECKS PASSED** (loops refuse; approved registry frozen) |
| `validate_research_archive.py` | **ALL CHECKS PASSED** (every campaign `strategy_approved=false`) |
| `scan_artifacts_for_secrets.py` | **PASSED** (no credential-shaped strings) |

## 6. Compliance

No CAMPAIGN_030 / no campaign of any number; no strategy approved; approved strategies
untouched; no paper/demo/live; no OANDA APIs / live credentials; no backtest runner; no
lockbox opened; no train/validation/test evidence. Front-gate screen only.

## 7. Artifacts

- Docs: `H03_THIN_MOVE_FRONTGATE_PLAN.md`, `H03_THIN_MOVE_HYPOTHESIS.md`,
  `H03_PARTICIPATION_DISTRIBUTION_STUDY.md`, `H03_CONDITIONAL_BEHAVIOR_STUDY.md`,
  `H03_COST_FEASIBILITY_STUDY.md`, `H03_NULL_COMPARISON.md`, `H03_FRONTGATE_DECISION.md`,
  `NON_TIME_BAR_LANE_FINAL_DECISION.md`, this summary.
- Code: `src/forex_bot/research/thin_move_screen.py` (pure helpers, reuses the H16
  primitives), `scripts/screen_h03_thin_move.py` (DB-streaming driver),
  `tests/unit/test_thin_move_screen.py` (7 tests).
- Compact diagnostics: `research/h03_thin_move_frontgate/{distribution,behavior,cost,null}_study.json`,
  `h03_screen_matrix.csv`, `h03_screen_manifest.json` (bulky per-bar tables gitignored).
