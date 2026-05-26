# Next Non-Strategy Workstream Decision

**Date:** 2026-05-26  
**Branch:** `research-broad-strategy-pause-and-roadmap-001`  
**Inputs:** [`NON_STRATEGY_WORKSTREAM_OPTIONS_AFTER_PAUSE.md`](NON_STRATEGY_WORKSTREAM_OPTIONS_AFTER_PAUSE.md) · post-dedup meta-analysis · broad-search pause memo

> **No strategy approved.** `configs/approved_strategies.yaml` remains `approved: []`. CAMPAIGN_018 will **not** be created.

---

## Selected workstream (exactly one)

### **`infra-observed-cost-and-spread-regime-diagnostics-001`**

Combines:

1. **Observed transaction-cost distributions** from deduped bid/ask H4 candles (spread, spread/ATR, implied round-trip drag).
2. **Spread-regime and session-cost diagnostics** by pair, walk-forward fold, UTC session, weekday, and volatility regime.

---

## Why selected

| factor | rationale |
|---|---|
| Evidence | C015–C017 aggregate exp_r at or below deduped null (−0.0029 R); all worsen under **2× cost** |
| Pause mandate | Broad pattern search paused — next work must be **non-strategy** infrastructure |
| Local-first | Existing OANDA practice H4 bid/ask in SQLite — **no order APIs**, no live trading |
| Unblocks | Future pre-registered **cost gating** and honest net expectancy — without tuning rejected campaigns |
| Risk | Low — descriptive diagnostics; explicit ban on strategy creation |
| vs financing (P1) | Financing needs read-only API reconciliation; spread diagnostics answer immediate “is this universe structurally untradeable at H4?” |
| vs data expansion (P2) | C015 adequate *n* still WITHIN_NULL — more bars do not explain rejection cluster |
| vs Backtrader (P2) | Parity hardens trust in REJECT verdicts but does not characterize cost drag |
| vs stop research (defer) | Leaves cost question open; diagnostics sprint is bounded and cheap |

---

## Rejected alternatives (this sprint)

| option | verdict |
|---|---|
| Observed financing / rollover only | **defer** — do after spread/cost atlas exists |
| Data expansion first | **reject** — does not address 2× cost failure without new hypothesis |
| Broker fill/slippage replay | **defer** — high complexity; needs tick infrastructure |
| Backtrader parity hardening | **defer** — valuable, not blocking pause objectives |
| Portfolio/risk simulator | **defer** |
| Stop all research | **reject** — cost diagnostics are the minimal productive next step |

---

## Sprint scope (draft)

**Branch suggestion:** `infra-observed-cost-and-spread-regime-diagnostics-001`  
**Start from:** `research-broad-strategy-pause-and-roadmap-001`

### In scope

- Load deduped H4 bid/ask for seven-pair universe (same stores as C011–C017).
- Compute spread and spread/ATR distributions; segment by pair, fold window, session, weekday, vol regime.
- Identify **cost-hostile windows** (e.g. top decile spread/ATR by pair/session).
- Emit compact `research/cost_diagnostics/` JSON + `docs/research/OBSERVED_COST_SPREAD_DIAGNOSTICS_001.md`.
- Unit tests on fixture candles.

### Out of scope

- New strategy or CAMPAIGN_018.
- Retuning C015/C016/C017.
- `approved_strategies.yaml` edits.
- Paper/demo/live enablement.
- OANDA order placement (read-only credential use optional only for later financing sprint).

### Success criteria

- Reproducible diagnostics script(s) committed with tests.
- Human-readable report with tables/charts references (no tradable edge claims).
- Recommendations section: **future strategy gating hypotheses** (pre-registration required before any campaign).

---

## Handoff

Copy-paste agent prompt: [`NEXT_SPRINT_PROMPT_AFTER_BROAD_STRATEGY_PAUSE.md`](NEXT_SPRINT_PROMPT_AFTER_BROAD_STRATEGY_PAUSE.md).
