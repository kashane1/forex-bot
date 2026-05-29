# CAMPAIGN_029 — parity result (primary engine vs independent verifier)

**Strategy:** `usdjpy_range_bar_mtf_breakout 0.1.0-c029`
**Status:** execution continuation; `NOT_RUN / NOT_APPROVED`
**Artifact:** [`research/campaign_029/parity/parity_summary.json`](../../research/campaign_029/parity/parity_summary.json)
**Harness:** [`scripts/parity_campaign_029_usdjpy_range_bars.py`](../../scripts/parity_campaign_029_usdjpy_range_bars.py),
[`src/forex_bot/research/campaign_029_parity.py`](../../src/forex_bot/research/campaign_029_parity.py)

> Backtrader cannot represent irregular-time range bars as the system of record
> (see `CAMPAIGN_029_BACKTRADER_PARITY_DESIGN.md` §1), so parity is checked with a
> **small independent local verifier** that re-implements the trigger / stop /
> next-bar-open fill / 12-bar time stop / M1-walked exit with **no shared execution
> code**, sharing only the data inputs (range bars, M1 index, and the precomputed
> H4/D1AGG context labels — the labels are separately cross-checked against the
> strategy module's `align_last_completed` path).

---

## 1. Result (train window, 2021-05-27 → 2023-12-31)

| metric | value | acceptance bar | pass |
|--------|------:|----------------|:----:|
| primary engine trades | **2,387** | — | — |
| verifier trades | **2,387** | count diff ≤ 1 | ✅ |
| exit-reason aligned share | **100.0%** | ≥ 99% | ✅ |
| side aligned | **100%** | all | ✅ |
| mean \|Δ net R\| | **0.000000** | ≤ 0.02R | ✅ |
| max \|Δ net R\| | **0.000000** | (reported) | ✅ |

**PARITY STATUS: `PASS`.** The two independent implementations agree **exactly**
on the train window — same trade set, same entries, same exit reasons, identical
per-trade R. No unexplained lookahead or timestamp mismatch.

## 2. What this does and does not establish

- **Does:** the entry/stop/exit *accounting* of the primary engine is reproducible
  by independent code → the train/validation numbers are not an artifact of one
  engine's bookkeeping. This satisfies the precommit's "parity required before any
  promotion-review" gate for the **execution mechanics**.
- **Does not:** prove the strategy has edge (that is the gate decision), and does
  not exercise the test lockbox (parity ran on train only, by design §6).

## 3. Scope / shared inputs (honest boundary)

The verifier shares the **precomputed HTF context labels** (`h4_trends`,
`d1_regimes`) with the engine rather than recomputing EMAs/alignment, to isolate
the parity test to the execution accounting (the most error-prone part). Those
labels are themselves cross-checked against the strategy's per-bar
`aligned_h4_trend` in `tests/unit/test_range_bar_execution.py`
(`test_vectorised_h4_aligner_matches_strategy_rule`). Trigger, stop, fill, and the
M1 exit walk are fully re-implemented in the verifier.

## 4. Feeds the gate decision

`parity_status = PASS` is passed to `campaign_029_gates.classify(...)`; a validation
pass can therefore reach at most `PROMOTION_REVIEW_REQUIRED` (never approval). A
parity `FAIL`/`NOT_RUN` would force `BLOCKED_PARITY`.
