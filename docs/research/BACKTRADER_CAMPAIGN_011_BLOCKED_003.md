# Backtrader CAMPAIGN_011 — Phase 5 — BLOCKED-by-design (Sprint 003)

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-003-real-data-run`
**Phase:** 5 of `BACKTRADER_REAL_DATA_RUN_003_PLAN.md`
**`strategy_evidence: false`**

## 0. Verdict

**Phase 5 precondition met, but CAMPAIGN_011 is deliberately not
ported in this sprint.** Two structural prerequisites are missing
that would make a CAMPAIGN_011 comparison apples-to-oranges; both are
documented below with the scoped follow-up needed. This is **not** a
data-availability block (Phase 1 unblocked all seven H4 pairs); it is
a comparison-target-structure block.

`research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py`
was **not** authored on this branch.

## 1. Precondition check

Phase 5 of `BACKTRADER_REAL_DATA_RUN_003_PLAN.md` says:

> Only proceed to CAMPAIGN_011 if CAMPAIGN_002 reaches PASS /
> TOLERABLE_DRIFT, or if its divergence is well-understood and does
> not block a null-model comparison.

CAMPAIGN_002 reached **PASS** post-fix on every metric, every pair
(see `BACKTRADER_CAMPAIGN_002_REAL_COMPARISON_003.md` §3.3). The
precondition is satisfied.

## 2. Why CAMPAIGN_011 in this sprint would be apples-to-oranges

CAMPAIGN_002 worked cleanly because there is a single, published,
no-RiskEngine bespoke reference run for it
(`research/lean_parity/campaign_002_h4_bespoke_reference.json`,
1 647 trades, full-window 2020-01-01 → 2026-05-19). The BT-lane
runner is a single-window full-run engine; comparing single-window
to single-window is straightforward.

CAMPAIGN_011's bespoke artefacts are very different in shape:

| dimension | CAMPAIGN_002 reference | CAMPAIGN_011 reference |
|---|---|---|
| run style | full window, single run | 8 walk-forward folds × 7 pairs = 56 cells |
| RiskEngine | no (`risk_engine=None`) | **yes** — spread-gate / session / loss-limits all wired in |
| aggregate file | single JSON | per-fold per-pair JSONs + walk-forward `results.json` |
| trade-list flatness | one flat list of 1 647 closed trades | 56 trade lists, one per (fold, pair) |
| comparison target | single number per pair per metric | per-fold per-pair grid |

To do a CAMPAIGN_011 comparison the same way CAMPAIGN_002 was done,
**two pieces** would need to be built first:

### 2.1 Prerequisite A — a no-RiskEngine CAMPAIGN_011 bespoke reference

The current bespoke run used the RiskEngine spread/session/loss-limit
gates; the BT lane (per Phase 4's `NO_RISK_ENGINE` flag and the same
flag inherited from CAMPAIGN_002) does **not** model those gates. A
direct single-run BT vs RiskEngine-wired bespoke comparison would
classify as `SIGNAL_RULE_MISMATCH` from spread/session-gate
rejections that BT skips — exactly the noise this sprint's
CAMPAIGN_002 comparison was clean of because CAMPAIGN_002 has the
no-RiskEngine reference (1 647 vs 1 032 trades).

Producing a no-RiskEngine CAMPAIGN_011 bespoke reference requires
running the bespoke engine in `risk_engine=None` mode against the
same data — that is a bespoke-side operation, not a Backtrader-lane
operation, and is out of scope for this sprint.

### 2.2 Prerequisite B — a walk-forward runner extension for the BT lane

The BT-lane runner today processes one full-window per campaign per
pair. CAMPAIGN_011's bespoke artefacts are per-fold per-pair under
`backtests/CAMPAIGN_011_random_entry_anchor/folds/`. A meaningful
fold-level comparison would need either:

- aggregating all 8 folds × 7 pairs into a single rolled-up bespoke
  reference (apples-to-mixed-fruit, and the walk-forward train/
  validation split would be lost), **or**
- extending the BT-lane runner to accept a fold plan (start/end
  per fold) and run the strategy over each fold's test window
  independently.

Neither is appropriate scope for this sprint. The first dilutes the
comparison; the second is a meaningful new feature.

## 3. What would still be valid and useful

A future sprint can do, in scoped order:

1. **Run the bespoke engine in `risk_engine=None` mode for
   CAMPAIGN_011** to produce a single no-RiskEngine full-window
   reference JSON analogous to `campaign_002_h4_bespoke_reference.json`.
   Out of scope for the BT-lane sprint sequence.
2. **Implement `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py`**
   per the spec the previous sprint already captured in
   `BACKTRADER_CAMPAIGN_011_BLOCKED_002.md` §4. The R1–R8 rule binding,
   frozen parameters (`master_seed = 20260523`, `entry_probability = 0.05`,
   `ATR(14)`, `atr_stop_multiple = 2.0`, `max_bars_in_trade = 6`), and
   three new approximation flags (`CAMPAIGN_011_DETERMINISTIC_SEED`,
   `CAMPAIGN_011_TIME_STOP_ONLY`, `CAMPAIGN_011_NO_RISK_ENGINE_PARITY`)
   are pre-pinned there.
3. **Run + compare** the new adapter against the new reference. Use
   the same `scripts/run_backtrader_parity.py` /
   `scripts/compare_backtrader_parity.py` pipeline that succeeded for
   CAMPAIGN_002 in this sprint.
4. **Optionally** add fold-aware runner support — but only if a
   bespoke per-fold reference is the primary comparison target.

## 4. What was deliberately NOT done

- **No** `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py`
  authored on this branch.
- **No** new bespoke run kicked off (no edits under
  `src/forex_bot/`; the bespoke engine remains untouched).
- **No** synthetic-on-CAMPAIGN_011 placeholder comparison. The
  sprint-002 plan rule "do not fake missing data" forbids it.

## 5. Carry-forward implementation prompt

The sprint-002 carry-forward prompt at
[`BACKTRADER_CAMPAIGN_011_BLOCKED_002.md`](BACKTRADER_CAMPAIGN_011_BLOCKED_002.md) §4
remains the authoritative implementation pointer. Sprint 003 adds
the **fix-002 R-formula fix** to its work-list:

> The future CAMPAIGN_011 adapter must use the *post-fix* R formula
> from sprint 003 — `r = pnl_home / ((entry − stop) × units)` with
> NO `/ exit_price` adjustment, matching
> `src/forex_bot/backtesting/engine.py:411-415` exactly.

## 6. Required disclosure

This decision cannot approve any strategy and does not enable paper
/ demo / live trading. CAMPAIGN_011 remains **REJECT (null model
anchor by design)**. CAMPAIGN_002 remains REJECT.
`configs/approved_strategies.yaml` remains `approved: []`. Paper /
demo / live remain blocked. `strategy_evidence: false`.
