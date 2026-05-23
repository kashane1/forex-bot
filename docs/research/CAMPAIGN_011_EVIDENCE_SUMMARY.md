# CAMPAIGN_011 — Evidence Summary

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-walk-forward-001`
`strategy_evidence: false`

One-page evidence summary for **CAMPAIGN_011** /
`random_entry_anchor 0.1.0-c011` — the C5 diagnostic-anchor
null model — at the close of its walk-forward evidence sprint.

> **Verdict: REJECT (null model anchor). No strategy approved.**
> CAMPAIGN_002 / CAMPAIGN_010 remain REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`.
> Paper / demo / live remain blocked. **CAMPAIGN_011 cannot be
> approved by design.** The REJECT verdict is the *expected
> and desired* outcome — it validates the evidence pipeline.

## 1. Candidate identity

| field | value |
|---|---|
| campaign label | `CAMPAIGN_011` |
| strategy name | `random_entry_anchor` |
| version | `0.1.0-c011` |
| role | **diagnostic anchor / null model** (NOT a paper candidate) |
| family | Deterministic-seed coin-flip H4 entry (no edge by construction) |
| universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD |
| timeframe | H4 |
| data span | 2020-01-01 → 2026-05-19 (real OANDA practice) |
| parameter mode | frozen (master_seed = 20260523; no seed optimization) |
| evaluation protocol | rolling walk-forward, 540/180/180/180 days |
| approval path | **none (null model by design)** |

## 2. Headline numbers

| dimension | value |
|---|---|
| folds executed | 8 |
| total trades | 1,177 |
| fold pass rate | **0 / 8** (gate 100 %) |
| aggregate expectancy R | **−0.0024 R** (gate ≥ 0.05) |
| aggregate profit factor | **0.91** (gate ≥ 1.10) |
| aggregate return % | **−0.53 %** over 4 years |
| pairs positive | **3 / 7** (GBP_USD, USD_JPY ≈ 0, USD_CHF; gate ≥ 4) |
| single-pair dominance | 36.5 % (gate ≤ 40 %) — PASS |
| single-fold dominance | 40.1 % (gate ≤ 60 %) — PASS |
| financing treatment | `ESTIMATED` (MODELED refused at four layers) |
| financing missing-rate events | 0 |
| financing impact | strictly worsens; USD_JPY flips +→− (pairs_positive → 2/7) |
| independent verifier ran? | no — capability-locked to CAMPAIGN_002; not required for null-model REJECT |
| overall verdict | **REJECT (null model anchor)** |

## 3. Null-model interpretation (the point of this candidate)

The verdict and metrics are exactly what a no-edge random
strategy should produce on H4 OANDA majors after costs:

| measurement | null-model expectation | observed | match? |
|---|---|---|:---:|
| aggregate expectancy R | ≈ 0 ± 0.05 | **−0.0024 R** | ✓ |
| aggregate profit factor | ≈ 1 ± 0.2 | **0.91** | ✓ |
| aggregate return over 4 years | ≈ 0 ± 5 % | **−0.53 %** | ✓ |
| pairs positive | ≈ 3.5 / 7 ± 1 | **3 / 7** | ✓ |
| long-short distribution | 50 / 50 ± binomial 3σ | 610 / 567 (51.8 % long) | ✓ |
| per-pair trade distribution | near-uniform | ratio max/min = 1.65 | ✓ |
| session-of-day distribution | diffuse (no concentration) | max bucket 37.6 % | ✓ |
| USD_JPY expectancy (longest-running random sample) | ≈ 0 | **+0.0000** (literal) | ✓ (textbook) |

**The pipeline is validated: gates correctly REJECT a
known-zero-edge strategy; metrics match random expectations
on every measurable dimension.**

## 4. The falsifiability floor (what future candidates must beat)

CAMPAIGN_011 establishes the per-fold + aggregate baseline that
every future C2 / C3 / C4 / new-family candidate must clear by
a meaningful margin to count as evidence of an edge:

| metric | random anchor (CAMPAIGN_011) | future real candidate must beat |
|---|---|---|
| aggregate expectancy R | −0.0024 R | by ≥ +0.05 R → reach ≥ 0.05 R |
| aggregate profit factor | 0.91 | by ≥ 0.19 → reach ≥ 1.10 |
| aggregate return % over 4 years | −0.53 % | meaningfully positive |
| pairs_positive | 3 / 7 | ≥ 4 / 7 |
| fold pass rate | 0 / 8 | 100 % (strict-pass) |

## 5. Six-evidence-ladder status (per [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md) §8)

| item | status | reference |
|---|---|---|
| 1. Pre-commit doc | ✓ | [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md) |
| 2. Backtest report | ✓ | [`CAMPAIGN_011_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_011_WALK_FORWARD_EXECUTION.md) |
| 3. Walk-forward result | ✓ (verdict REJECT) | [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md) |
| 4. Financing reconciliation | ✓ (ESTIMATED + conservative stress; strictly worsens REJECT) | [`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md) |
| 5. Independent corroboration | ✗ (verifier did not run; not required for null-model REJECT) | [`CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md) |
| 6. Human approval record | n/a — null model cannot be approved | — |

Items 1, 2, 3 (the REJECT-sufficient subset) are satisfied;
items 4–6 are pre-conditions for *approval*, not for
*rejection*. Item 6 is structurally impossible for a null
model.

## 6. Committed artifact tree

```
backtests/CAMPAIGN_011_random_entry_anchor/
├── walk_forward/
│   ├── plan.json
│   ├── plan.md
│   ├── results.json
│   ├── results.md
│   └── fold_detail.json
├── folds/
│   └── fold_NN/                    (8 folds × 7 pairs × 2 files)
│       ├── fold_NN_<PAIR>_summary.json
│       └── fold_NN_<PAIR>_trades.csv
├── financing/
│   ├── financing_run.json
│   ├── financing_run.md
│   └── financing_summary.json
└── risk/
    ├── diagnostics.json
    └── diagnostics.md
```

Compact summary docs in `docs/research/`:

- `RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_PLAN.md` (Phase 0)
- `CAMPAIGN_011_DATA_PROVENANCE.md` (Phase 1)
- `CAMPAIGN_011_WALK_FORWARD_PLAN.md` (Phase 2)
- `CAMPAIGN_011_WALK_FORWARD_EXECUTION.md` (Phase 4)
- `CAMPAIGN_011_WALK_FORWARD_RESULT.md` (Phase 5)
- `CAMPAIGN_011_FINANCING_OVERLAY.md` (Phase 6)
- `CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md` (Phase 7)
- `CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md` (Phase 8)
- `CAMPAIGN_011_EVIDENCE_SUMMARY.md` (Phase 9 — this doc)
- `CAMPAIGN_011_STATUS.md` (updated Phase 9 to `rejected (null model anchor)`)
- `RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_WALK_FORWARD_001_SUMMARY.md` (Phase 9)

Scripts added by this sprint:

- `scripts/run_campaign_011.py` (per-fold backtest runner)
- `scripts/build_campaign_011_financing_overlay.py`
- `scripts/build_campaign_011_risk_diagnostics.py`

## 7. Comparison to CAMPAIGN_010 (informational; not used for tuning)

| dimension | CAMPAIGN_010 (session_breakout) | **CAMPAIGN_011 (random_entry_anchor)** |
|---|---:|---:|
| total trades | 2,791 | **1,177** |
| aggregate expectancy R | −0.0408 | **−0.0024** (≈ 17× closer to 0) |
| aggregate return % | −36.56 % | **−0.53 %** (≈ 69× closer to 0) |
| aggregate profit factor | 0.04 | **0.91** (≈ 23× closer to 1) |
| pairs positive | 1 / 7 | **3 / 7** (closer to uniform) |
| fold pass rate | 0 / 8 | **0 / 8** (both REJECT) |
| session concentration | 100 % London | **diffuse across 4 buckets** (37/30/22/10) |
| verdict | REJECT (directional negative — strategy lost decisively) | **REJECT (null model — statistically indistinguishable from no edge)** |

CAMPAIGN_010 lost *more* than random would have on the same
data + cost model — evidence that the session-breakout entry
signal was *actively bad*, not merely random.

## 8. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **CAMPAIGN_010 remains REJECT** (untouched).
- **Paper / demo / live remain blocked.** `paper-loop` and
  `demo-loop` refuse; no `live-loop` command exists.
- **No broker call** at any phase. **No `.env` read; no credential
  printed; no account / order / trade / position / transaction
  endpoint queried.**
- **No QuantConnect / LEAN.**
- **No engine-PnL change.** **No `src/forex_bot/financing.py`
  edit.**
- **`MODELED` financing remains refused** at four layers.
- **No parameter tuning. No seed optimization.** Only
  `master_seed = 20260523` was used.
- **CAMPAIGN_011 cannot be approved by design** — null model.

## 9. Cross-links

- [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
