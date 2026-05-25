# Backtrader CAMPAIGN_011 — Phase 5 — BLOCKED (cascade)

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-002-real-data-run`
**Phase:** 5 of `BACKTRADER_REAL_DATA_RUN_002_PLAN.md`
**`strategy_evidence: false`**

## 0. Verdict

**BLOCKED (cascade from Phase 1).** The Phase 0 plan's precondition
for Phase 5 reads:

> Only proceed if CAMPAIGN_002 reached PASS or TOLERABLE_DRIFT, or
> if divergence is clearly documented and not blocking for a null-model
> comparison.

CAMPAIGN_002 reached **none of those states** because Phase 1 was
BLOCKED on data unavailability (`BACKTRADER_REAL_DATA_PREFLIGHT_002.md`).
The Phase 5 precondition is therefore unmet, and a CAMPAIGN_011 port
is **deferred** rather than implemented in this sprint.

## 1. Why CAMPAIGN_011 is the correct future target (unchanged)

Sprint 001's `BACKTRADER_SECOND_CAMPAIGN_BLOCKED.md` §2 selected
CAMPAIGN_011 `random_entry_anchor 0.1.0-c011` as the recommended
second port because it exercises a different failure mode than
CAMPAIGN_002:

| dimension | CAMPAIGN_002 | CAMPAIGN_011 |
|---|---|---|
| indicators | EMA(50/200), Donchian(20), ATR(14), trailing | ATR(14) only |
| entry rule | regime + breakout | SHA-256 per-bar coin flip with `master_seed = 20260523` |
| exits | adverse stop, trailing, time-stop @ 240 bars | adverse stop, time-stop @ 6 bars |
| reproducibility | float-precision sensitive | bit-exact (SHA-256) |
| bespoke reference | single-window JSON (1,647 trades) | per-fold per-pair CSV/JSON under `backtests/CAMPAIGN_011_random_entry_anchor/` |

A CAMPAIGN_011 Backtrader port would isolate `SIGNAL_RULE_MISMATCH`
and `SIZING_OR_PNL_MISMATCH` failure modes from CAMPAIGN_002's
indicator-warmup noise.

## 2. Why CAMPAIGN_011 also cannot run in this worktree

CAMPAIGN_011 used the **same** local rehydrated H4 candle store
(`data/oanda_h4_research.sqlite3`) and the **same** seven-pair H4
universe as CAMPAIGN_002 — see
`docs/research/CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` §4
("data reused from `data/campaign_002.sqlite3` (gitignored symlink,
same as CAMPAIGN_010)").

The single artefact that unblocks Phase 1 of this sprint (the
rehydrated H4 store) is also the single artefact CAMPAIGN_011 would
need. There is no separate "CAMPAIGN_011 data" to source; restoring
the H4 store unblocks both campaigns at once.

## 3. What this sprint deliberately did NOT do

- **Did not** author
  `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py`
  on this branch. Implementing an adapter we cannot run on real data
  is infrastructure for its own sake; the spec already says it would
  produce only another BLOCKED row at Phase 6. Sprint 001 already
  recorded the scoped CAMPAIGN_011 implementation prompt in
  `BACKTRADER_SECOND_CAMPAIGN_BLOCKED.md` §4.
- **Did not** create a synthetic fixture-driven "fake" CAMPAIGN_011
  comparison. The previous sprint's smoke tests already exercise the
  runner on a synthetic fixture, which is sufficient to prove the
  pipeline plumbing; a synthetic CAMPAIGN_011 comparison would
  duplicate that without adding evidence value, and the prompt rule
  "do not fake missing data" forbids it for any real campaign claim.
- **Did not** mutate `configs/approved_strategies.yaml`, the bespoke
  engine, or any campaign verdict. CAMPAIGN_011 stays REJECT (null
  model anchor by design); the freeze gate remains green.

## 4. Carry-forward scoped implementation prompt

When `data/oanda_h4_research.sqlite3` is restored and the seven CSVs
are exported per `BACKTRADER_REAL_DATA_PREFLIGHT_002.md` §10, the
next sprint can implement CAMPAIGN_011 with **minimum** new
infrastructure:

### 4.1 New file

`research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py`

### 4.2 Frozen parameters (from
[`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md) §3)

```python
master_seed                = 20_260_523
entry_probability_per_bar  = 0.05
atr_lookback               = 14
atr_stop_multiple          = 2.0
trailing_stop_atr_multiple = None         # no trail
max_bars_in_trade          = 6
min_atr_pips               = {}
risk_per_trade_pct         = 0.25
```

### 4.3 R1–R8 binding (verbatim from the spec)

R1. Warmup: `len(df) >= atr_lookback + 2`.
R2. Block re-entry while in position.
R3. Seed input: `f"{master_seed}|{instrument}|{bar_iso}"` (UTF-8) →
    `SHA-256`; `bar_random` = high 64 bits; `gate_random` = next 64 bits.
    No bar-`t` price / ATR data in the seed input.
R4. Entry gate: `gate_random / 2**64 < 0.05`.
R5. Fail-closed on NaN / non-finite / zero prior ATR (`ATR[t-1]`).
R6. Spread filter delegated to RiskEngine — **NOT enforced** in the BT
    port (matches the no-RiskEngine reference convention).
R7. Direction: `"long"` if `bar_random & 1 == 0` else `"short"`.
    Stop: `close[t] -/+ 2.0 × prior_atr`.
R8. Emit signal; `exit_model = "time_stop_only"` (max 6 bars).

### 4.4 Approximation flags to surface

- `CAMPAIGN_011_DETERMINISTIC_SEED` — SHA-256 over the deterministic
  seed input string; bit-exact between bespoke and BT.
- `CAMPAIGN_011_TIME_STOP_ONLY` — no trailing-stop branch; only ATR
  stop and 6-bar time-stop.
- `CAMPAIGN_011_NO_RISK_ENGINE_PARITY` — like the CAMPAIGN_002 adapter,
  spread / session / loss-limit gates are not modelled (uses the
  no-RiskEngine reference if one is created; otherwise compares to the
  with-RiskEngine bespoke trades and expects `SIZING_OR_PNL_MISMATCH` /
  `SIGNAL_RULE_MISMATCH` from gated bars).

### 4.5 Bespoke reference target

- Per-fold per-pair summary JSONs:
  `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_{00..07}/fold_NN_<PAIR>_summary.json`
- Aggregate walk-forward result:
  `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json`
- Note: no published no-RiskEngine reference exists for CAMPAIGN_011
  (the campaign ran with the RiskEngine wired in). A first-pass
  comparison will likely classify as `SIZING_OR_PNL_MISMATCH` from
  the spread-gate trade rejections that the BT port omits — that is
  the expected baseline, not a bug. A no-RiskEngine bespoke reference
  for CAMPAIGN_011 would be a separate operational step in a future
  branch.

### 4.6 Test plan (mirrors the CAMPAIGN_002 port)

- 9 pure-helper tests (already covered by the CAMPAIGN_002 port's
  helpers; reuse `_round_price`, `_size_position`, `_trade_pnl`).
- 4–6 integration tests on a synthetic 250-bar fixture proving:
  - warmup honoured (no signal before `atr_lookback + 2 = 16` bars),
  - per-bar SHA-256 coin-flip is bit-stable across two runs (a SHA
    seed test, not a Cerebro test),
  - one long + one short trade appear when the seed deterministically
    selects them on the fixture's price path,
  - time-stop fires at 6 bars when no adverse stop hit,
  - no `forex_bot` / broker / LEAN / QuantConnect import.
- 1 frozen-parameter contract test (loads the frozen YAML / spec
  values and asserts they match the spec).

## 5. Required disclosure

This BLOCKED-cascade decision cannot approve any strategy and does
not enable paper / demo / live trading. CAMPAIGN_011 remains
**rejected as null model anchor**. CAMPAIGN_002 remains REJECT.
CAMPAIGN_010, CAMPAIGN_012, CAMPAIGN_013 remain rejected/research-only.
CAMPAIGN_014 remains scaffold-only.
`configs/approved_strategies.yaml` remains `approved: []`. Paper /
demo / live remain blocked. `strategy_evidence: false`.
