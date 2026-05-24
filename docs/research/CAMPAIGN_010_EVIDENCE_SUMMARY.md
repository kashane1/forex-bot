# CAMPAIGN_010 — Evidence Summary

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-walk-forward-001`
`strategy_evidence: false`

One-page evidence summary for the **CAMPAIGN_010 research candidate**
(`session_breakout 0.1.0-c010`) at the close of its walk-forward
evidence sprint.

> **Verdict: REJECT.** No strategy approved. CAMPAIGN_002 remains
> REJECT. `configs/approved_strategies.yaml` remains `approved: []`.
> Paper / demo / live remain blocked.

## 1. Candidate identity

| field | value |
|---|---|
| campaign label | `CAMPAIGN_010` |
| strategy name | `session_breakout` |
| version | `0.1.0-c010` |
| family | Asian-range / London-open H4 session breakout |
| universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD |
| timeframe | H4 |
| data span | 2020-01-01 → 2026-05-19 (real OANDA practice) |
| parameter mode | frozen (single pre-commit) |
| evaluation protocol | rolling walk-forward, 540/180/180/180 days |

## 2. Headline numbers

| dimension | value |
|---|---|
| folds executed | 8 |
| total trades | 2,791 |
| fold pass rate | **0 / 8** (gate 100 %) |
| aggregate expectancy R | **−0.0408** (gate ≥ 0.05) |
| aggregate profit factor | **0.04** (gate ≥ 1.10) |
| aggregate return % | **−36.56 %** |
| pairs positive | **1 / 7** (USD_CHF; gate ≥ 4) |
| single-pair dominance | 24.1 % (gate ≤ 40 %) — PASS |
| single-fold dominance | 30.3 % (gate ≤ 60 %) — PASS |
| financing treatment | `ESTIMATED` (MODELED refused) |
| financing missing-rate events | 0 |
| conservative stress flips verdict? | no (vacuously PASS — verdict was already REJECT) |
| independent verifier ran? | no — verifier capability-locked to CAMPAIGN_002 |
| overall verdict | **REJECT** |

## 3. Six-evidence-ladder status (per [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md) §8)

| item | status | reference |
|---|---|---|
| 1. Pre-commit doc | ✓ | [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md) |
| 2. Backtest report | ✓ | [`CAMPAIGN_010_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_010_WALK_FORWARD_EXECUTION.md) |
| 3. Walk-forward result | ✓ (verdict REJECT) | [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md) |
| 4. Financing reconciliation | ✓ (ESTIMATED + conservative stress; worsens REJECT) | [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md) |
| 5. Independent corroboration | ✗ (verifier did not run — capability-locked to CAMPAIGN_002; would only matter for a hypothetical PASS) | [`CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md) |
| 6. Human approval record | n/a — REJECT cannot be approved | — |

Items 1, 2, 3 (the REJECT-sufficient subset) are satisfied; items
4, 5, 6 are pre-conditions for *approval*, not for *rejection*.

## 4. Committed artifact tree

```
backtests/CAMPAIGN_010_session_breakout/
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

- `ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_PLAN.md` (Phase 0)
- `CAMPAIGN_010_DATA_PROVENANCE.md` (Phase 1)
- `CAMPAIGN_010_WALK_FORWARD_PLAN.md` (Phase 2)
- `CAMPAIGN_010_WALK_FORWARD_EXECUTION.md` (Phase 3)
- `CAMPAIGN_010_WALK_FORWARD_RESULT.md` (Phase 4)
- `CAMPAIGN_010_FINANCING_OVERLAY.md` (Phase 5)
- `CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md` (Phase 6)
- `CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md` (Phase 7)
- `CAMPAIGN_010_EVIDENCE_SUMMARY.md` (Phase 8 — this doc)
- `CAMPAIGN_010_STATUS.md` (updated Phase 8 to `rejected`)
- `ASIAN_LONDON_SESSION_BREAKOUT_WALK_FORWARD_001_SUMMARY.md` (Phase 8)

Scripts added by this sprint:

- `scripts/run_campaign_010.py` (per-fold backtest runner)
- `scripts/build_campaign_010_financing_overlay.py`
- `scripts/build_campaign_010_risk_diagnostics.py`

## 5. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **Paper / demo / live remain blocked.** `paper-loop` and
  `demo-loop` refuse; no `live-loop` command exists.
- **No broker call** at any phase. **No `.env` read; no credential
  printed; no account / order / trade / position / transaction
  endpoint queried.**
- **No QuantConnect / LEAN.**
- **No engine-PnL change.** **No `src/forex_bot/financing.py`
  edit.**
- **`MODELED` financing remains refused** at four layers.

## 6. Cross-links

- [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
