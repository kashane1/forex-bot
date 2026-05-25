# Backtrader Lane — Phase 7 Second Campaign — BLOCKED

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-001`
**Phase:** 7 of `INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md`
**`strategy_evidence: false`**

## 0. Overall verdict

**BLOCKED — same root cause as Phase 6.** The seven H4 CSVs at
`research/lean_parity/exports/campaign_002_h4/*.csv` are gitignored and
the rehydrated source SQLite store `data/oanda_h4_research.sqlite3` is
also gitignored. With no real candle data locally regenerable in this
worktree, running a *second* campaign would just produce another
BLOCKED row in `comparison_summary.json` — the runner and harness
already proved that path works in Phase 6.

Implementing a second campaign port in this sprint, while the
verification target is unreachable, would be infrastructure for its
own sake and is **not** in the plan
(`INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md` §7 "Phase 7 — expand …
if feasible"). The plan explicitly allows: "If a second campaign is
too large, document the blocker and create a scoped next-step prompt
instead." That is what this document is.

## 1. Why a second campaign is deferred

| factor | observation |
|---|---|
| real data available locally | **no** (`research/lean_parity/exports/campaign_002_h4/*.csv` absent; `data/oanda_h4_research.sqlite3` absent) |
| bespoke reference available | yes (committed per-fold JSONs under `backtests/CAMPAIGN_011_random_entry_anchor/folds/`) |
| Backtrader adapter exists for CAMPAIGN_011 | **no** — not implemented in this sprint |
| would a Backtrader CAMPAIGN_011 adapter produce comparable output without local CSVs | **no** — same BLOCKED state as Phase 6, with no new comparison signal |
| does the existing pipeline need any new code to support CAMPAIGN_011 once data exists | **only** a new strategy adapter file under `research/backtrader_lane/strategies/` |

In short: the lane's runner, data adapter, comparison harness, and
divergence classifier are already campaign-agnostic. What's missing
to run CAMPAIGN_011 is (a) the data and (b) one new strategy adapter
file. Without (a), (b) cannot be exercised on real data. The Phase 7
selection rule asks us to pick a campaign "that exercises a different
failure mode" — but we can't *exercise* anything when both the first
*and* second campaign's data is absent.

## 2. Recommended second campaign (for the future unblock sprint)

**`CAMPAIGN_011` — `random_entry_anchor 0.1.0-c011` (null-model
anchor).** Reasons:

1. **Different failure mode than CAMPAIGN_002.** CAMPAIGN_002 stresses
   indicator + signal-rule parity (EMA, Donchian, trailing stop).
   CAMPAIGN_011 stresses **deterministic-seed reproducibility** — the
   per-bar entry is a SHA-256-based coin flip with a fixed
   `master_seed = 20260523`, frozen in the spec.
2. **Minimal indicator surface.** ATR(14) only, no EMA, no Donchian,
   no trailing. If CAMPAIGN_002 reveals indicator-mismatch noise,
   CAMPAIGN_011 isolates it from the rest of the engine.
3. **Short trades.** `max_bars_in_trade = 6` (vs CAMPAIGN_002's 240) —
   so time-stop exits dominate, exercising the time-stop logic in
   isolation.
4. **Bespoke reference exists.** Per-fold per-pair trades CSVs and
   summary JSONs under `backtests/CAMPAIGN_011_random_entry_anchor/`
   give a target to compare against (8 folds × 7 pairs = 56 cells).
5. **CAMPAIGN_011 cannot be approved by design.** The whole campaign
   is structurally ineligible for `configs/approved_strategies.yaml`,
   so even a perfect PASS verifies the engine — not a strategy.

### Different failure modes the lane could surface

| label | how CAMPAIGN_011 would isolate it |
|---|---|
| `DATA_MISMATCH` | tested by the data adapter's sha256 round-trip; if CAMPAIGN_011 trips this, the CSV regeneration is wrong |
| `SIGNAL_RULE_MISMATCH` | tested by per-bar SHA-256 reproducibility — both engines must produce *identical* coin flips on identical seed input strings |
| `FILL_MODEL_MISMATCH` | tested by entry-price differences on agreeing signals; CAMPAIGN_011 uses the same FillModel as CAMPAIGN_002 |
| `STOP_OR_EXIT_ORDERING_MISMATCH` | tested by time-stop vs stop ordering when both could fire on the same bar; CAMPAIGN_011's short holding window stresses this |
| `INDICATOR_MISMATCH` | tested by ATR-only — if CAMPAIGN_011 disagrees but CAMPAIGN_002 agrees on ATR-dependent metrics, the bug is elsewhere |

This is the "different failure mode" property the plan asks Phase 7
to exercise — but exercising it requires the *first* lane's data, too.

## 3. Why **not** CAMPAIGN_012 / 013 / 010 / 014

| candidate | why deferred |
|---|---|
| CAMPAIGN_012 (regime_switcher_atr_percentile) | requires D1AGG aggregation (NY-17 alignment) that Backtrader cannot natively express; `UNSUPPORTED_BY_BACKTRADER` is the likely outcome; would need bespoke H4→D1 pre-aggregation, which is itself a sprint |
| CAMPAIGN_013 (cross_pair_currency_strength_rotation) | multi-pair synchronised signals; Backtrader can express it but the adapter is substantially larger than CAMPAIGN_011; not "the minimum frozen adapter required" |
| CAMPAIGN_010 (session_breakout) | mid-complexity (session-window entries + Asian/London regime gates); similar effort to CAMPAIGN_002 but does not exercise a *different* failure mode as cleanly as CAMPAIGN_011 does |
| CAMPAIGN_014 (calendar_event_window_anomaly) | scaffold-only — plan §0 forbids producing evidence for CAMPAIGN_014 unless evidence already exists in the repo |
| CAMPAIGN_002 (same as Phase 4) | already chosen for Phase 4 |
| CAMPAIGN_006 (daily_trend) | REJECT-NO-VALID-RESULT in bespoke for D1-infrastructure reasons; not meaningful to compare |

## 4. Scoped next-step prompt for the future sprint

For a future infra branch (suggested name:
`infra-backtrader-secondary-lane-002-real-data-run`), do this work:

1. Restore (do not fetch new) `data/oanda_h4_research.sqlite3` via
   `scripts/rehydrate_oanda_h4_store.py` against a credentialed OANDA
   practice account, **or** copy the file in from a previous restore.
2. Regenerate the seven CAMPAIGN_002 H4 CSVs via
   `scripts/export_lean_parity_data.py`.
3. Run `scripts/run_backtrader_parity.py --campaign CAMPAIGN_002 ...`
   and `scripts/compare_backtrader_parity.py ...`. Document the result
   in `docs/research/BACKTRADER_PARITY_CAMPAIGN_002_COMPARISON.md`.
4. Implement the CAMPAIGN_011 Backtrader adapter under
   `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py`,
   honoring R1–R8 from
   `docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`.
5. Run the lane on CAMPAIGN_011 (single full-window, or per-fold for
   walk-forward parity).
6. Compare against `backtests/CAMPAIGN_011_random_entry_anchor/`.
   Document the result in
   `docs/research/BACKTRADER_PARITY_CAMPAIGN_011_COMPARISON.md`.

Hard non-goals (binding, repeated from this sprint's plan):

- No approval. No `configs/approved_strategies.yaml` edit.
- No tuning. Frozen rules only.
- No broker call. No OANDA API call beyond
  `scripts/rehydrate_oanda_h4_store.py` (which already exists, is
  read-only, and is the operational sprint's responsibility — not the
  Backtrader-lane sprint's).
- No LEAN. No cloud backtest.
- No verdict mutation. CAMPAIGN_002 stays REJECT; CAMPAIGN_011 stays
  REJECT-as-null-model.

## 5. Required disclosure

**This blocked result cannot approve any strategy and does not enable
paper / demo / live trading.** It is a deliberate scoping decision:
the Backtrader-lane secondary-verification infrastructure is complete
and tested; what is missing is the real candle data needed to run
*any* campaign on it. CAMPAIGN_002 remains REJECT. CAMPAIGN_010,
CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/
research-only. CAMPAIGN_014 remains scaffold-only.
`configs/approved_strategies.yaml` remains `approved: []`.

`strategy_evidence: false`.
