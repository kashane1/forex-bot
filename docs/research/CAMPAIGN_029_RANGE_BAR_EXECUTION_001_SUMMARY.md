# CAMPAIGN_029 — range-bar execution sprint close-out

**Strategy:** `usdjpy_range_bar_mtf_breakout 0.1.0-c029`
**Branch:** `research-campaign-029-usdjpy-range-bar-scaffold-001` (continued, unmerged)
**Verdict:** `REJECT_TRAIN_GATE` · `NOT_APPROVED` · lockbox **closed**
**Date:** 2026-05-29

> Extended the C029 scaffold into an execution-ready research lane: an M1-resolved
> execution engine, a frozen HTF/D1AGG staleness policy, an independent parity
> harness (PASS), and **train-only** evidence (validation correctly not run after a
> catastrophic train gate). Frozen rule unchanged; nothing approved; paper/demo/live
> blocked.

---

## 1. Commits by phase (this sprint)

| phase | commit | content |
|-------|--------|---------|
| 0 | `dea74b5` | continuation audit + plan |
| 1 | `1aaf725` | M1-resolved execution engine + 12 tests |
| 2 | `2da4c80` | loader + HTF/D1AGG availability + frozen staleness policy |
| 3 | `ee6c37b` | train/validation runner + frozen gates (+9 tests) |
| 4 | `5dcdde5` | independent parity harness → PASS (+2 tests) |
| 5 | `25369e8` | train evidence → REJECT_TRAIN_GATE |
| 6 | _this commit_ | final interpretation + summary + archive updates |

## 2. Files added / changed

- engine: `src/forex_bot/research/range_bar_execution.py`
- loader: `src/forex_bot/research/campaign_029_loader.py`
- gates: `src/forex_bot/research/campaign_029_gates.py`
- parity: `src/forex_bot/research/campaign_029_parity.py`
- scripts: `run_campaign_029_usdjpy_range_bar_mtf_breakout.py`,
  `analyze_campaign_029_htf_staleness.py`, `parity_campaign_029_usdjpy_range_bars.py`
- tests: `test_range_bar_execution.py` (13), `test_campaign_029_gates.py` (9),
  `test_campaign_029_parity.py` (2)
- docs: `CAMPAIGN_029_EXECUTION_CONTINUATION_PLAN.md`,
  `…_HTF_D1AGG_AVAILABILITY_AND_STALENESS.md`, `…_PARITY_RESULT.md`,
  `…_TRAIN_RESULT.md`, `…_GATE_DECISION.md`, `…_FINAL_INTERPRETATION.md`, this file
- artifacts (compact, tracked): `research/campaign_029/execution/{htf_staleness_summary,train_summary,gate_decision}.json`,
  `research/campaign_029/parity/parity_summary.json`
- updated: `EVIDENCE_INDEX.md`, `STRATEGY_STATUS.md`, `.gitignore`

## 3. Execution engine

M1-resolved (`range_bar_execution.run_range_bar_execution`): next-range-bar-open
entry; structural stop (`max(5-bar swing, 20pip floor)`) walked on the M1 tape with
conservative ambiguity (an M1 touch registers the stop; stop has priority over the
time exit); 12-range-bar time stop; no take-profit; M1-resolved cost (real
half-spread at entry+exit fill rows + 0.2 pip slippage each side). Vectorised
HTF aligners (`precompute_h4_trends`/`precompute_d1agg_regimes`) match the strategy
rule (cross-checked in tests).

## 4. HTF / D1AGG staleness (frozen)

H4 fresh(≤8h): train 85.4% / val 94.3%; D1AGG fresh(≤3d): train 98.2% / val 99.7%.
Finding: **H4M1 coverage ≈70% of native H4** inflates H4 staleness (14.6% train /
5.7% val blocked) — a noted data-coverage caveat, not a rule change. **Frozen
policy:** H4 missing/stale>8h ⇒ no trade; D1AGG missing/stale>3d ⇒ optional gate
skipped.

## 5. Parity — PASS

Independent verifier (no shared execution code) reproduced **all 2,387** train
trades exactly: exit reasons 100% aligned, mean |ΔnetR| = 0.0. → not `BLOCKED_PARITY`.

## 6. Train result + gate decision

| metric | value |
|--------|------:|
| trades | 2,387 |
| net expectancy | **−0.0188R** |
| gross expectancy | +0.0839R |
| net profit factor | 0.974 |
| 2× cost expectancy | −0.121R |
| hit rate | 39.4% |
| avg cost / risk | 2.29 pip / 24.0 pip |

**Binding train expectancy gate (≥0) fails catastrophically ⇒ `REJECT_TRAIN_GATE`;
validation NOT run; lockbox sealed.** A small gross edge fully eaten by realistic
cost — see `CAMPAIGN_029_FINAL_INTERPRETATION.md`.

## 7. Archive bookkeeping note

Following the **C027 precedent** (the comparable recent executed reject),
CAMPAIGN_029 is recorded in `EVIDENCE_INDEX.md` and `STRATEGY_STATUS.md` and is
**not** added to `docs/research/EVIDENCE_MANIFEST.json` (that manifest tracks the
original campaign series; C027/C028 are likewise absent). The freeze/archive gates
remain green.

## 8. Standing confirmations

No strategy approved (`approved_strategies.yaml` = `[]`); paper/demo/live blocked;
no OANDA/network/live creds; no tuning; frozen rule unchanged after results; test
lockbox closed; full trade ledger kept local & gitignored.

## 9. Recommended next step

**Stop work on the 10-pip `usdjpy_range_bar_mtf_breakout` thesis (CLOSED).** It is
cost-defeated, mirroring C026. If range bars are revisited, it must be a **new
precommit** with an externally-motivated change (e.g. a wider range threshold to
clear the cost floor, or a cheaper execution), evaluated through the same front
gate — never a re-tune of C029 on the same data. A useful side-quest is backfilling
**H4M1 coverage** (currently ~70% of native H4), which would reduce the staleness
block rate for any future range-bar lane.
