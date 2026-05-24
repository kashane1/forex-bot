---
title: "feat: Backtest exit-fidelity — ambiguous SL+TP counter + opt-in gap-through fill"
type: feat
date: 2026-05-24
sprint_id: infra-exit-fidelity-001
working_branch: claude/keen-leakey-a15799
worktree: .claude/worktrees/keen-leakey-a15799
status: deepened
research_freeze: enforced
---

# feat: Backtest exit-fidelity — ambiguous SL+TP counter + opt-in gap-through fill

## Enhancement Summary

**Deepened on:** 2026-05-24
**Sections enhanced:** Overview, Phases 0-6, Acceptance Criteria, Risks
**Research agents used:** git-history-analyzer, best-practices-researcher, architecture-strategist, code-simplicity-reviewer, pattern-recognition-specialist, performance-oracle, kieran-python-reviewer, data-integrity-guardian

### Key improvements vs draft
1. **Sprint id corrected** from `audit-sl-tp-fidelity-001` → `infra-exit-fidelity-001` (pattern-recognition: every numbered sprint in this repo uses an `infra-`/`research-` prefix; mirrors `infra-execution-fidelity-001` precedent).
2. **Opt-in value renamed** from `"next_open"` → `"gap_through"` (architecture + simplicity: removes collision risk with `fill_timing="next_bar_open"`; "gap_through" describes what it does and cannot be confused).
3. **Phase 1 + Phase 2 merged.** Schema-only commits are not independently meaningful when defaults equal prior behavior — git-history confirms the `fill_timing` precedent shipped schema + behavior in one commit.
4. **`_STATUS.md` deliverable dropped.** Pattern-recognition + simplicity both flagged: no prior numbered sprint (`INFRA_*_001`, `RESEARCH_*_001`) ships a `_STATUS.md`. Precedent is PLAN + SUMMARY only.
5. **Hash snapshot guardrails added.** Data-integrity: snapshot file gets a `_doc` warning header + guardrail test to prevent accidental re-snapshotting.
6. **`_index.json` test split into two directions.** Old committed file loads via report builders; new summary with extra keys also loads via the same builders.
7. **AC count trimmed from 22 to 16** by removing process gates (lint/typecheck/commit-format are standing rules, not feature criteria) and dropping implied ACs.
8. **Local variable renames** in Phase 4 (`did_gap_fill`, `tp_also_in_range`) per kieran-python-reviewer — prevents kwarg-shadowing at call sites.
9. **Long/short mirror folded via `is_long` flag** per kieran — collapses 5 branches into 2 while preserving stop-then-TP precedence.
10. **Architecture additions:** hash-key-insertion-order regression test, property-based invariant test, optional `gap_fill_distance_pips: Decimal | None` field added now (cheap, prevents a v2 sprint).
11. **Phase 1 type-stability check** for `strategy_config` (data-integrity: hash inputs must contain only primitive types).
12. **Verdicts:** APPROVE (architecture), SIMPLIFY (simplicity — applied), MOSTLY CONSISTENT (pattern — applied), NEGLIGIBLE IMPACT (performance), APPROVE WITH NITS (kieran — applied), MOSTLY SAFE (data-integrity — applied).

### Findings explicitly considered and rejected

- **Drop the 16-case matrix to 6 tests** (simplicity). Rejected per architecture: the matrix is audit-trail bait (later researchers will search "did anyone test short-side TP gap-fill under next_bar_open with the risk engine?"). Cost is ~0.3s of test runtime; value is searchability. KEEP 16 + ADD 1 property-based test for invariants. Best of both.
- **Extract `ExitResolver` strategy class** (no agent suggested; preempted in original). Confirmed unnecessary by architecture-strategist (the rule-of-two: only one prior opt-in flag exists; refactor on the third).
- **Defer trailing-stop update instead of snapshotting** (considered in original). Re-confirmed by architecture + simplicity: deferring changes the hash for non-gap-fill runs under `gap_through`. Snapshot stays.

---

## Overview

This sprint addresses **two findings** from a walk-forward / backtest engine audit of the `BacktestEngine` exit logic in [src/forex_bot/backtesting/engine.py](src/forex_bot/backtesting/engine.py):

1. **Finding #1 — Same-bar SL+TP collisions are not measured.** The engine's exit precedence at engine.py:259-291 resolves "both stop and TP touched on the same bar" by an `if/elif` chain (stop wins). The tie-break is intentional and pre-declared in [CAMPAIGN_009_PRECOMMIT.md:59](docs/research/CAMPAIGN_009_PRECOMMIT.md:59), but the engine never records HOW OFTEN this collision happens. For a mean-reversion strategy with a midline TP (CAMPAIGN_009), this silently understates TP wins. Sprint adds pure-instrumentation per-trade flag + aggregate counter. **No behavior change, no `config_hash` change.**

2. **Finding #2 — Stop / TP fills are pinned to the exact level, ignoring bar-open gaps.** When a bar's `bid_open` (long) is already below `stop_price`, the engine still fills at exactly `stop_price` (engine.py:271); real stop-market orders fill at the open (worse than stop). Same for the favorable side: a long TP fires when `bid_high >= tp` and fills at exactly `tp`, even if `bid_open` already gapped past TP (where a real limit fills at the open, better than TP). Sprint adds an **opt-in** `backtest.gap_fill_policy: Literal["none", "gap_through"] = "none"` that activates four gap-fill cases. Default `"none"` preserves byte-identical `config_hash` for every CAMPAIGN_001–009 artifact.

This is **infrastructure** — fidelity + auditability work that makes the measurement instrument more honest. It does not look for a trading edge, does not approve any strategy, and does not relax any research-freeze guard. It is the **closest precedent** to [`infra-execution-fidelity-001`](docs/research/INFRA_EXECUTION_FIDELITY_001_PLAN.md) (the `fill_timing` sprint, 2026-05-22) and reuses its exact opt-in / hash-compatibility pattern.

## Problem Statement

### Finding #1: silent same-bar collision

In a mean-reversion strategy (CAMPAIGN_009), the TP sits at the rolling-mean midline and the hard stop is `entry ± atr_stop_multiple × ATR`. On a wide H4 bar — common in news or session opens — both can be in-range simultaneously. The engine's tie-break ([CAMPAIGN_009_PRECOMMIT.md:59](docs/research/CAMPAIGN_009_PRECOMMIT.md:59)):

> "if a bar touches both the stop and the target, the adverse stop wins (conservative)"

This is the right *behavior* (you cannot prove which fired first from OHLC), but the engine writes nothing to the trade log or metrics telling you it happened. A researcher reading CAMPAIGN_008/009 results cannot answer "how many of these stop-outs could have been TP wins?" — yet that question is the core ambiguity that distinguishes a fair stop-precedence from a tape-painted one.

**The collision rate has never been measured.** This sprint produces the first audit data on it.

### Finding #2: zero-slippage stop/TP fills ignore the gap

[CAMPAIGN_002_LEAN_MAPPING_SPEC.md:131-133](docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md:131-133):

> "**Known Lean-mechanics mismatch:** the bespoke engine fills a stop exit **exactly at the stop price**; Lean stop-market orders fill at the stop or worse on a gap. Treat exit price as a tolerance comparison."

The Lean side has been honoring this divergence by widening tolerances on parity comparisons. The bespoke side has been intentionally ignoring gaps — meaning every weekend gap, news jump, or session-open jump fills at the stop level even when bar-open is many pips through it. On D1AGG (synthetic daily) bars the bias is largest; on H4 it is smaller but non-zero.

This is currently an *intentional* bespoke constraint, not a bug — but it is also the obvious next fidelity feature to add, and the only honest way to support Lean parity without permanent tolerance widening. We add it as opt-in (`"gap_through"`), preserving every CAMPAIGN_001–009 default-mode hash.

## Proposed Solution

### Solution to Finding #1 — always-on instrumentation

- New `TradeRecord.ambiguous_exit: bool = False` (trailing default-with-safety).
- New `BacktestMetrics.ambiguous_exit_count: int = 0` (trailing default-with-safety).
- New `BacktestResult.ambiguous_exit_count: int = 0` (mirror).
- Engine detection: on every exit-bar where `exit_reason in {"stop", "trailing_stop"}` AND `take_profit_price is not None`, compute `tp_also_in_range = (bid_high >= tp)` (long) or `(ask_low <= tp)` (short). If true, set `ambiguous_exit=True`.
- **No `config_hash` impact** — pure observation.
- Exporters surface the new fields (trades CSV column, metrics JSON / MD / summary JSON).

### Solution to Finding #2 — opt-in gap-fill, exact `fill_timing` precedent

- New module-level constants in [src/forex_bot/backtesting/fills.py](src/forex_bot/backtesting/fills.py):
  ```python
  GapFillPolicy = Literal["none", "gap_through"]
  GAP_FILL_POLICIES: frozenset[str] = frozenset({"none", "gap_through"})
  ```
- New `BacktestConfig.gap_fill_policy: Literal["none", "gap_through"] = "none"` in [src/forex_bot/config.py](src/forex_bot/config.py).
- New `BacktestEngine` kwarg `gap_fill_policy: str = "none"`.
- **Hash inclusion mirrors `fill_timing` exactly** (engine.py:163-169) — verbatim per [git-history-analyzer findings](#research-insights-from-deepen-phase):
  ```python
  **(
      {"gap_fill_policy": self.gap_fill_policy}
      if self.gap_fill_policy != "none"
      else {}
  ),
  ```
- New CLI flag `--gap-fill-policy` mirroring `--fill-timing` ([src/forex_bot/cli.py:397-439](src/forex_bot/cli.py:397-439)).
- New `TradeRecord.gap_fill: bool = False` and `TradeRecord.gap_fill_distance_pips: Decimal | None = None`.
- New `BacktestMetrics.gap_fill_exit_count: int = 0` and `BacktestResult.gap_fill_exit_count: int = 0` and `BacktestResult.gap_fill_policy: str = "none"` (mirror `fill_timing` on BacktestResult).

**Four gap-fill cases** (only when `gap_fill_policy == "gap_through"`):

| trade side | exit kind | gap test | fill price | direction |
|---|---|---|---|---|
| long  | stop | `bid_open < pre_trailing_stop_price` | `bid_open` | adverse (worse than stop) |
| short | stop | `ask_open > pre_trailing_stop_price` | `ask_open` | adverse (worse than stop) |
| long  | tp   | `bid_open > tp_price` | `bid_open` | favorable (better than tp) |
| short | tp   | `ask_open < tp_price` | `ask_open` | favorable (better than tp) |

**Bid/ask_open `None` fallback** — the engine already falls back to mid OHLC for `bid_low`/`ask_high`/etc. (engine.py:203-235). The four cases above use the same fallback: `bid_open` → `Decimal(str(row["open"]))` if missing. **Pin this fallback rule explicitly in tests.**

**Trailing-stop ordering caveat** — the trailing stop is currently updated at the top of the bar using that bar's close ([engine.py:237-254](src/forex_bot/backtesting/engine.py:237-254)), then exit checks run. For the gap-fill comparison (which tests against the *open* of the bar), we **snapshot the stop value BEFORE the trailing update** (`pre_trailing_stop_price`) and use it for the `bid_open < stop_price` test. The existing range tests (`bid_low <= stop_price`) continue against the post-update stop. Architecture-strategist confirmed this is the right choice; alternatives (defer trailing update; accept time-inversion) both have worse trade-offs.

## Technical Approach

### Architecture

Delta on the existing single-file backtest engine. No new modules, no new abstractions — trailing-default field additions and one new `if` block inside the existing exit-check section. Per architecture-strategist: do NOT extract an `ExitResolver` (rule of two — only one prior opt-in flag exists; refactor on the third).

```
src/forex_bot/backtesting/engine.py     — exit-check block, snapshot pre-trailing stop, gap-fill
src/forex_bot/backtesting/metrics.py    — TradeRecord + BacktestMetrics new fields
src/forex_bot/backtesting/exporters.py  — CSV columns + JSON/MD propagation
src/forex_bot/backtesting/fills.py      — GAP_FILL_POLICIES constant + GapFillPolicy type alias
src/forex_bot/config.py                 — BacktestConfig.gap_fill_policy
src/forex_bot/cli.py                    — --gap-fill-policy flag
tests/unit/test_gap_fill.py             — new test module (parametrized matrix + property test)
tests/unit/test_ambiguous_exit.py       — new test module (collision detection + EOD negative)
tests/unit/test_backtest_exporters.py   — extend or add (round-trip + asymmetry)
tests/fixtures/pre_sprint_config_hashes.json — pinned hash snapshot with _doc guardrail
docs/research/INFRA_EXIT_FIDELITY_001_PLAN.md     — sprint plan deliverable (repo-convention)
docs/research/INFRA_EXIT_FIDELITY_001_SUMMARY.md  — final summary
docs/research/GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md — semantics + ordering caveat + parity-impact + asymmetry note
```

No changes to: strategies, risk policy, parity verifier (default mode preserves baselines), data loaders, financing, approval registry.

### Implementation Phases

| phase | deliverable | independent? | hash-safe? |
|---|---|---|---|
| 0 | Bootstrap: this plan as repo-convention `INFRA_EXIT_FIDELITY_001_PLAN.md`, freeze re-verification, pre-sprint hash snapshot with `_doc` guardrail | — | n/a |
| 1 | Schema additions + same-bar ambiguous-exit instrumentation (always-on, finding #1). Includes `strategy_config` primitive-type assertion. Tests. | depends on 0 | yes (no hash change) |
| 2 | `gap_fill_policy` plumbing: constant, config field, CLI flag, engine kwarg, conditional hash inclusion. Default = `"none"`. No exit-logic change yet. Hash-regression test against Phase 0 snapshot. | depends on 1 | yes (default unchanged) |
| 3 | Gap-fill exit logic (finding #2): all four cases, pre-trailing snapshot, bid/ask_open fallback. Parametrized 16-case matrix + 1 property test. | depends on 2 | yes (opt-in only) |
| 4 | Exporter propagation: trades CSV columns, metrics JSON/MD, summary JSON. Round-trip + asymmetry tests. `_index.json` two-direction load test. | depends on 1, 2, 3 | yes |
| 5 | Documentation: new `GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md`. Hard links to CAMPAIGN_002 / CAMPAIGN_009 / FILL_TIMING_MODEL. Parity-impact + asymmetry statements. | depends on 1-4 | n/a |
| 6 | Final validation: full `pytest` + `ruff`, hash regression for all 3 pinned configs, `_index.json` load via report builders, write `INFRA_EXIT_FIDELITY_001_SUMMARY.md`. | depends on 0-5 | n/a |

Each phase commits separately with message format `Phase N (infra-exit-fidelity-001): <one-line summary>`. If a phase is blocked, the blocker is documented in the in-flight `_PLAN.md` "Status" section (no separate `_STATUS.md` file — per repo convention).

#### Phase 0 — Bootstrap
- Verify `configs/approved_strategies.yaml` is still empty.
- Run `pytest` + `ruff check src tests scripts` — baseline green.
- Write `docs/research/INFRA_EXIT_FIDELITY_001_PLAN.md` (mirror this plan in repo-convention naming).
- Pick **3 pinned configs** (CAMPAIGN_001 baseline, CAMPAIGN_004 vol-breakout, CAMPAIGN_009 mean-reversion-with-TP — covers vanilla / breakout / TP-bearing axes).
- Build engines from each config (default mode, no run), record their `config_hash` to `tests/fixtures/pre_sprint_config_hashes.json` with a header `_doc` warning:
  ```json
  {
    "_doc": "DO NOT REGENERATE — this is the hash-compatibility baseline for infra-exit-fidelity-001 AC-9. Re-snapshotting would silently hide a hash regression. See docs/research/INFRA_EXIT_FIDELITY_001_PLAN.md.",
    "campaign_001_baseline": "<hex>",
    "campaign_004_volatility_breakout": "<hex>",
    "campaign_009_mean_reversion": "<hex>"
  }
  ```
- Commit: `Phase 0 (infra-exit-fidelity-001): plan, baseline, pre-sprint hash snapshot with _doc guardrail`.

#### Phase 1 — Schema additions + ambiguous-exit instrumentation (always-on)
- Add **trailing default-with-safety** fields to dataclasses:
  ```python
  # metrics.py TradeRecord (trailing — must remain last)
  ambiguous_exit: bool = False
  gap_fill: bool = False
  gap_fill_distance_pips: Decimal | None = None

  # metrics.py BacktestMetrics (trailing)
  ambiguous_exit_count: int = 0
  gap_fill_exit_count: int = 0

  # engine.py BacktestResult (trailing — gap_fill_policy mirrors fill_timing)
  ambiguous_exit_count: int = 0
  gap_fill_exit_count: int = 0
  gap_fill_policy: str = "none"
  ```
- Update `compute_metrics()` to compute `ambiguous_exit_count = sum(t.ambiguous_exit for t in trades)` and `gap_fill_exit_count = sum(t.gap_fill for t in trades)`. Trades-empty branch returns zeros.
- Add ambiguous-exit detection to the exit-check block (engine.py:259-291). After setting `exit_reason`:
  ```python
  tp_also_in_range = False
  if exit_reason in {"stop", "trailing_stop"} and tp is not None:
      tp_also_in_range = (
          bid_high >= tp if open_trade.side == "long" else ask_low <= tp
      )
  ```
  Thread `ambiguous_exit=tp_also_in_range` into the `TradeRecord(...)` constructor.
- EOD-close block (engine.py:528-567): `ambiguous_exit=False` (eod never matches `{"stop", "trailing_stop"}`).
- Tests in `tests/unit/test_ambiguous_exit.py`:
  - `test_long_stop_with_tp_in_range_flags_ambiguous`
  - `test_long_stop_with_tp_out_of_range_does_not_flag`
  - `test_short_stop_with_tp_in_range_flags_ambiguous`
  - `test_short_stop_with_tp_out_of_range_does_not_flag`
  - `test_tp_only_strategy_never_ambiguous` (`take_profit_price=None`)
  - `test_eod_exit_never_ambiguous`
  - `test_time_stop_never_ambiguous`
  - `test_trailing_stop_with_tp_in_range_flags_ambiguous`
  - `test_ambiguous_exit_count_aggregates`
  - `test_ambiguous_exit_with_risk_engine` (both `risk_engine=None` and `risk_engine=real`)
- **Hash invariance test:** `test_phase1_no_hash_change` — for each of the 3 pinned configs, build an engine and assert `config_hash` matches Phase 0 snapshot byte-for-byte.
- **Type-stability test:** `test_strategy_config_hash_input_types_are_repr_stable` — assert recursively that every value reachable in any campaign's `strategy_config` is one of `int | float | str | bool | None | list | dict`. No `numpy` scalar, no `pathlib.Path`, no `Decimal` (no campaign uses Decimal in `strategy_config` today; if one does later this test refuses to silently break hashes).
- **Hash key-order test:** `test_hash_dict_key_order_is_stable` — build two engines with the same config and assert their `config_hash` byte-matches (proves the conditional `**({...} if ... else {})` spread doesn't perturb key order).
- Commit: `Phase 1 (infra-exit-fidelity-001): schema + same-bar SL+TP ambiguous-exit instrumentation`.

#### Phase 2 — gap_fill_policy plumbing (default 'none', no logic yet)
- Add to `fills.py`:
  ```python
  GapFillPolicy = Literal["none", "gap_through"]
  GAP_FILL_POLICIES: frozenset[str] = frozenset({"none", "gap_through"})
  ```
- Add `BacktestConfig.gap_fill_policy: Literal["none", "gap_through"] = "none"` to `config.py`.
- Add `gap_fill_policy: str = "none"` to `BacktestEngine.__init__` and `self.gap_fill_policy = gap_fill_policy`.
- Add conditional inclusion to `config_hash` (verbatim mirror of `fill_timing`):
  ```python
  **(
      {"gap_fill_policy": self.gap_fill_policy}
      if self.gap_fill_policy != "none"
      else {}
  ),
  ```
- Set `gap_fill_policy=self.gap_fill_policy` in the `meta` dict at engine.py:142-171 (same shape as `fill_timing=self.fill_timing`).
- Add CLI flag `--gap-fill-policy` to `cli.py` mirroring `--fill-timing`. Validate against `GAP_FILL_POLICIES`; print `[dim]gap fill: ...[/dim]`; pass to engine kwarg.
- Tests in `tests/unit/test_gap_fill.py` (Phase 2 portion):
  - `test_default_policy_is_none`
  - `test_policy_accepts_gap_through`
  - `test_policy_rejects_unknown` (`pytest.raises((ConfigError, ValueError))`)
  - `test_engine_default_policy_none`
  - `test_default_policy_no_hash_change` — verifies engine-to-engine equality
  - `test_default_policy_matches_phase0_snapshot` — loads `tests/fixtures/pre_sprint_config_hashes.json`, rebuilds each pinned config's engine in default mode, asserts hash matches snapshot byte-for-byte
  - `test_gap_through_changes_hash`
  - `test_cli_rejects_invalid_gap_fill_policy` (exit code 2)
  - `test_cli_2x2_matrix` — `--fill-timing next_bar_open --gap-fill-policy gap_through` combines cleanly
  - `test_snapshot_doc_guardrail` — assert `tests/fixtures/pre_sprint_config_hashes.json["_doc"]` contains the warning string "DO NOT REGENERATE"
- Commit: `Phase 2 (infra-exit-fidelity-001): gap_fill_policy plumbing, default 'none' preserves hash`.

#### Phase 3 — Gap-fill exit logic
- In the exit-check block, snapshot the pre-update stop BEFORE the trailing-update block at engine.py:237:
  ```python
  pre_trailing_stop_price: Decimal = open_trade.stop_price  # see GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md
  ```
- After the trailing update and before the existing if/else exit chain, add a gap-fill resolver with the folded long/short logic (per kieran):
  ```python
  did_gap_fill = False
  if self.gap_fill_policy == "gap_through":
      is_long = open_trade.side == "long"
      open_px = bid_open if is_long else ask_open
      stop_breached = (
          open_px < pre_trailing_stop_price
          if is_long
          else open_px > pre_trailing_stop_price
      )
      tp_breached = (
          tp is not None and (
              open_px > tp if is_long else open_px < tp
          )
      )
      if stop_breached:
          exit_reason = (
              "trailing_stop"
              if open_trade.stop_price != open_trade.initial_stop_price
              else "stop"
          )
          exit_price = open_px
          did_gap_fill = True
      elif tp_breached:
          exit_reason = "target"
          exit_price = open_px
          did_gap_fill = True
  if not did_gap_fill:
      # ---- existing if/elif chain (range tests against post-update stop) ----
  ```
- Resolve `bid_open` / `ask_open` with the established `None` → mid-open fallback (alongside the existing 6 conversions at engine.py:203-235):
  ```python
  bid_open = (
      Decimal(str(row["bid_open"]))
      if row["bid_open"] is not None
      else Decimal(str(row["open"]))
  )
  ask_open = (
      Decimal(str(row["ask_open"]))
      if row["ask_open"] is not None
      else Decimal(str(row["open"]))
  )
  ```
- Compute `gap_fill_distance_pips` when `did_gap_fill`:
  ```python
  gap_fill_distance_pips = (
      ((pre_trailing_stop_price - open_px).copy_abs() / self.instrument.pip_size)
      if stop_breached
      else ((open_px - tp).copy_abs() / self.instrument.pip_size)
  ) if did_gap_fill else None
  ```
- Thread `gap_fill=did_gap_fill, gap_fill_distance_pips=gap_fill_distance_pips` into the `TradeRecord(...)` constructor.
- EOD-close block: `gap_fill=False, gap_fill_distance_pips=None`. Add explicit test.
- Tests in `tests/unit/test_gap_fill.py` (Phase 3 portion):
  - **Parametrized 16-case matrix** (flat `pytest.param(..., id=...)` per best-practices-researcher):
    ```python
    @pytest.mark.parametrize(
        ("side", "exit_kind", "fill_timing", "risk_engine"),
        [
            pytest.param(s, k, t, r,
                id=f"{s}-{k}-{'sbc' if t == 'signal_bar_close' else 'nbo'}-{'norisk' if r is None else 'risk'}")
            for s in ("long", "short")
            for k in ("stop", "tp")
            for t in ("signal_bar_close", "next_bar_open")
            for r in (None, "real")
        ],
    )
    def test_gap_fill_matrix(side, exit_kind, fill_timing, risk_engine, eur_usd, make_gap_scenario): ...
    ```
  - `test_policy_none_disables_gap_fill` (parametrized matching the 16 cases, asserts no gap-fill)
  - `test_gap_fill_uses_pre_trailing_stop` — trailing ratcheted on exit bar to tighter level; gap test must use pre-ratchet stop
  - `test_bid_ask_open_fallback_to_mid_open` — `bid_open=None ask_open=None` → falls back to `open`; all four gap cases still work
  - `test_eod_no_gap_fill` — explicit `gap_fill=False, gap_fill_distance_pips=None`
  - `test_d1agg_synthetic_weekend_gap` — D1AGG-shaped fixture with Friday→Monday gap
  - `test_simultaneous_ambiguous_and_gap` — bar gaps past stop AND TP in-range; assert `gap_fill=True` AND `ambiguous_exit=True` AND `exit_reason` reflects adverse-stop precedence
  - `test_gap_fill_distance_pips_computed_correctly` — for a long stop gap of 5 pips, assert `gap_fill_distance_pips == 5`
  - **Property-based invariant test** (per architecture-strategist):
    ```python
    @given(...)  # hypothesis
    def test_gap_fill_invariants(bar_geometry):
        # 1. If gap_fill: exit_price in {bid_open, ask_open}
        # 2. If policy == "none": gap_fill False for every trade
        # 3. gap_fill and ambiguous_exit are independent flags
    ```
- Commit: `Phase 3 (infra-exit-fidelity-001): opt-in gap-through-stop and gap-through-TP fill`.

#### Phase 4 — Exporter propagation + `_index.json` asymmetry tests
- `exporters.py` `write_trades_csv`: append `ambiguous_exit`, `gap_fill`, `gap_fill_distance_pips` to `fieldnames` (CSV convention: append-at-end per git-history-analyzer).
- `write_metrics_json`: add `ambiguous_exit_count`, `gap_fill_exit_count`, `gap_fill_policy` (next to `fill_timing`).
- `write_metrics_markdown`: append three new bullets (next to `Fill model:`).
- `write_summary_json`: add same three (gap_fill_policy present even when `"none"`).
- Tests:
  - `test_csv_round_trip_carries_ambiguous_and_gap_fill` — bool + optional Decimal round-trip
  - `test_metrics_json_carries_new_fields`
  - `test_metrics_md_renders_zero_when_no_collisions`
  - `test_summary_json_carries_policy_even_when_default`
  - **`test_old_index_json_loads_via_report_builders`** (per data-integrity): load committed `backtests/campaign_001/runs/_index.json` via `scripts/build_campaign_report.load_index` (and equivalents for 003/004/009 if they exist). Assert no KeyError on missing `ambiguous_exit_count`/`gap_fill_exit_count`.
  - **`test_new_summary_json_loads_via_report_builders`**: write a fresh summary with the new keys; load via the same report-builder functions. Assert no schema rejection.
- Commit: `Phase 4 (infra-exit-fidelity-001): exporter propagation + _index.json forward/backward read tolerance`.

#### Phase 5 — Documentation
- Write `docs/research/GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md`:
  - Section: same-bar SL+TP ambiguous-exit semantics (link CAMPAIGN_009_PRECOMMIT.md).
  - Section: gap-fill four cases + table.
  - Section: pre-trailing-stop snapshot ordering caveat with worked example.
  - Section: bid/ask_open `None` fallback rule.
  - Section: **parity-impact policy** — "under default `none`, parity verdicts are byte-identical to pre-sprint runs; under `gap_through` parity comparisons are NOT back-compared and will likely fail existing tolerance tests until baselines are rebuilt — out of scope here".
  - Section: **artifact asymmetry** (per data-integrity) — old committed `_index.json` and `summary.json` files lack the two new count keys; newly-generated default-mode files have them as `0`. Documented as expected.
  - Section: **known limitations** — entry-bar gap-through-stop (the `next_bar_open` entry pathology where a gap entry can fill *below* its own long stop) is **out of scope** for this sprint.
  - Section: compatibility with prior campaigns — quote the FILL_TIMING_MODEL.md "Compatibility with old campaigns" stanza.
- **Do NOT modify** `CAMPAIGN_002_LEAN_MAPPING_SPEC.md`, `CAMPAIGN_009_PRECOMMIT.md`, or any CAMPAIGN_* artifact. Cross-link only.
- Commit: `Phase 5 (infra-exit-fidelity-001): gap-fill model doc + asymmetry + parity-impact statements`.

#### Phase 6 — Final validation
- `pytest -q tests/` — full green.
- `ruff check src tests scripts` — full green.
- `python -c "import yaml; assert yaml.safe_load(open('configs/approved_strategies.yaml'))['approved'] == []"` — freeze still in place.
- `python scripts/check_research_freeze.py` (if present) — passes.
- **Hash regression**: re-load `tests/fixtures/pre_sprint_config_hashes.json` and assert no drift across all 3 pinned configs in default mode.
- **`_index.json` builder check**: load every committed `backtests/campaign_*/runs/_index.json` via its corresponding `scripts/build_campaign_*_report.py` load function. No KeyError, no schema rejection.
- Write `docs/research/INFRA_EXIT_FIDELITY_001_SUMMARY.md` (sprint completion summary).
- Final commit: `Phase 6 (infra-exit-fidelity-001): final validation + sprint summary, all hash regressions green`.

## Research Findings / Prior Art

### Constraints inherited from prior campaigns

- **Stop wins same-bar ties** ([CAMPAIGN_009_PRECOMMIT.md:59](docs/research/CAMPAIGN_009_PRECOMMIT.md:59)) — load-bearing. The new ambiguous-exit flag *describes* this tie-break; it does not change it.
- **Bespoke fills stop exactly at stop, never worse** ([CAMPAIGN_002_LEAN_MAPPING_SPEC.md:131-133](docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md:131-133)) — current default behavior. Opt-in `gap_through` introduces a *new* behavior; it does not "fix" anything that was previously declared a bug.
- **No silent fallback fills** ([FILL_TIMING_MODEL.md:58-60](docs/research/FILL_TIMING_MODEL.md:58-60)) — gap-fill must explicitly mark the trade with `gap_fill=True`; no quiet substitutions.

### Pattern precedent: `fill_timing` (the only prior opt-in fidelity flag)

Implemented in `infra-execution-fidelity-001` (2026-05-22) in a **single commit** `990112c` (+559/-10 across 8 files — confirmed by git-history-analyzer). Quoted from [FILL_TIMING_MODEL.md:100-105](docs/research/FILL_TIMING_MODEL.md:100-105):

> "The engine only folds `fill_timing` into its `config_hash` when it departs from `signal_bar_close`. A `signal_bar_close` run therefore produces the **same `config_hash`** as it did before this feature existed, so prior campaign artifacts (CAMPAIGN_001–009) stay hash-comparable. A `next_bar_open` run gets a distinct `config_hash`, so the two can never be silently confused."

This sprint follows the exact same pattern for `gap_fill_policy`.

### Same-bar collision frequency: never measured

No prior doc quantifies how often same-bar SL+TP collisions occur in CAMPAIGN_008/009 H4 data. This sprint produces the first audit data — treat the new metric as audit infrastructure, not as a validation of any prior claim.

## SpecFlow Gaps Resolved

Distilled from the SpecFlow analysis. Each gap below has been folded into the phase plan above; this section records the resolution.

1. **`next_bar_open` entry-bar gap-through-stop** — Out of sprint scope. Pre-existing pathology unrelated to exit fidelity. Documented in `GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md` § "Known limitations".
2. **Trailing-stop ordering** — Resolved via `pre_trailing_stop_price` snapshot. Documented with rationale.
3. **Same-bar SL + gap-through-TP** — Resolved: `gap_fill` and `ambiguous_exit` are orthogonal flags. Test `test_simultaneous_ambiguous_and_gap` covers the combined case.
4. **EOD invariant** — Resolved: explicit tests assert `gap_fill=False`, `ambiguous_exit=False`, `gap_fill_distance_pips=None` for `exit_reason="eod"`.
5. **Trailing-stop reason classification** — Unchanged: `exit_reason` keys off `stop_price != initial_stop_price` (existing behavior). `gap_fill=True` set independently.
6. **Risk-engine vs legacy path** — Resolved: parametrized matrix includes both `risk_engine=None` and `risk_engine=<real>`.
7. **D1AGG specifically** — Resolved: dedicated `test_d1agg_synthetic_weekend_gap`.
8. **Lean parity impact** — Default mode preserves baselines. `gap_through` mode parity out of scope; noted in model doc.
9. **Acceptance criteria** — See below.
10. **`_index.json` backward read + bid/ask_open `None` fallback + CLI 2×2 matrix** — All covered by Phase 4 + Phase 2 tests.

## Acceptance Criteria

### Functional Requirements

- [ ] **AC-1** `BacktestConfig.gap_fill_policy` defaults to `"none"`; accepts `"none"` and `"gap_through"`; rejects all other values via `ConfigError`/`ValueError`.
- [ ] **AC-2** CLI `--gap-fill-policy invalid_value` exits with code 2.
- [ ] **AC-3** With `gap_fill_policy="gap_through"`, all four gap-fill cases activate as specified.
- [ ] **AC-4** Gap-fill comparison uses the **pre-trailing-update stop** (snapshot semantics) — proved by `test_gap_fill_uses_pre_trailing_stop`.
- [ ] **AC-5** EOD exits never set `gap_fill=True`, `ambiguous_exit=True`, or non-None `gap_fill_distance_pips`.
- [ ] **AC-6** `gap_fill` and `ambiguous_exit` are orthogonal — proved by `test_simultaneous_ambiguous_and_gap` AND the property-based invariant test.
- [ ] **AC-7** `gap_fill_distance_pips` is `None` when `gap_fill=False`; positive `Decimal` when `gap_fill=True`.
- [ ] **AC-8** Per-trade flags round-trip cleanly through CSV and JSON exporters (`test_csv_round_trip_carries_ambiguous_and_gap_fill`).

### Non-Functional Requirements

- [ ] **AC-9** With `gap_fill_policy="none"`, `BacktestResult.config_hash` matches `tests/fixtures/pre_sprint_config_hashes.json` byte-for-byte for all 3 pinned configs (CAMPAIGN_001, CAMPAIGN_004, CAMPAIGN_009).
- [ ] **AC-10** With `gap_fill_policy="gap_through"`, `config_hash` differs from `"none"` for the same config.
- [ ] **AC-11** Hash dict key-order is stable across runs (`test_hash_dict_key_order_is_stable`).
- [ ] **AC-12** `strategy_config` contains only primitive types (`int|float|str|bool|None|list|dict`) — prevents Python-version-dependent `repr()` drift (`test_strategy_config_hash_input_types_are_repr_stable`).
- [ ] **AC-13** Pre-sprint snapshot file carries `_doc` guardrail; test `test_snapshot_doc_guardrail` asserts the warning string is preserved.
- [ ] **AC-14** Every committed `backtests/campaign_*/runs/_index.json` is loaded successfully by its corresponding `scripts/build_campaign_*_report.py` load function in the test suite.
- [ ] **AC-15** Freshly-generated summary.json with new keys also loads via the same report builders (forward-compat).
- [ ] **AC-16** `configs/approved_strategies.yaml` remains `approved: []` at every commit.

## Alternative Approaches Considered

1. **Always-on gap-fill (no opt-in flag).** Rejected — would change `config_hash` for every existing CAMPAIGN_001-009 artifact, violating the hash-comparable guarantee.

2. **Defer trailing update until after exit checks (instead of snapshot).** Rejected — would silently change post-update stop semantics for non-gap-fill bars under any `fill_timing` mode, breaking hash compatibility.

3. **Extract `ExitResolver` helper class.** Rejected (architecture-strategist: rule of two — only one prior opt-in flag exists; refactor on the third).

## Dependencies & Risks

### Risks
| risk | likelihood | impact | mitigation |
|---|---|---|---|
| Hash regression in default mode | low (mirrors `fill_timing`) | high | Phase 0 snapshot + AC-9 + AC-11 + AC-12 |
| `strategy_config` contains non-primitive type | low | high (Python-version-dependent hash) | AC-12 test |
| Snapshot accidentally re-generated to mask regression | medium (human error) | high | `_doc` guardrail + AC-13 |
| `_index.json` schema mismatch on read | low (data-integrity confirmed all readers tolerant) | medium | AC-14 + AC-15 |
| Parity verifier baselines break | low (default mode unchanged) | medium | Verified in repo research; re-verified Phase 6 |
| Trailing-stop ordering misunderstood | medium | medium | Phase 5 doc with worked example; `test_gap_fill_uses_pre_trailing_stop` enforces semantics |
| Scope creep into entry-bar gap handling | medium | medium | Explicitly out of scope; documented in model doc |

## Future Considerations

- **Lean parity baselines under `gap_through` mode.** Separate sprint required.
- **Entry-bar gap-through-stop** in `next_bar_open` mode (pre-existing engine pathology). Deserves a dedicated audit sprint.
- **Hoist `Decimal(str(row[...]))` conversions to CandleFrame load time** (per performance-oracle). Optional — cuts per-bar engine overhead for all uses, not just this sprint's additions. Sprint id suggestion: `infra-decimal-hoisting-001`.
- **`gap_fill_distance_pips` histogram analytics** — once the field exists, a future sprint can produce a distribution-of-gap-sizes report across CAMPAIGN_001-009 to inform whether `gap_through` mode would have changed any verdict.

## References & Research

### Internal References (read-only)

- Engine exit precedence: [src/forex_bot/backtesting/engine.py:200-291](src/forex_bot/backtesting/engine.py:200-291)
- Trailing-stop update block: [src/forex_bot/backtesting/engine.py:237-254](src/forex_bot/backtesting/engine.py:237-254)
- `config_hash` exclusion pattern (precedent): [src/forex_bot/backtesting/engine.py:153-170](src/forex_bot/backtesting/engine.py:153-170)
- `BacktestConfig.fill_timing` (precedent): [src/forex_bot/config.py:341](src/forex_bot/config.py:341)
- CLI `--fill-timing` (precedent): [src/forex_bot/cli.py:397-439](src/forex_bot/cli.py:397-439)
- `TradeRecord` + `BacktestMetrics`: [src/forex_bot/backtesting/metrics.py](src/forex_bot/backtesting/metrics.py)
- Exporters: [src/forex_bot/backtesting/exporters.py](src/forex_bot/backtesting/exporters.py)
- `eur_usd` test fixture: [tests/conftest.py:47-57](tests/conftest.py:47-57)
- Synthetic candle test helper (precedent): [tests/unit/test_fill_timing.py:75-89](tests/unit/test_fill_timing.py:75-89)
- TP-exit test (precedent): [tests/unit/test_take_profit_exit.py](tests/unit/test_take_profit_exit.py)
- `_index.json` readers: [scripts/build_campaign_report.py:78-99](scripts/build_campaign_report.py:78-99), [scripts/build_campaign_009_report.py:73-82](scripts/build_campaign_009_report.py:73-82), [scripts/build_marathon_report.py:58-65](scripts/build_marathon_report.py:58-65)

### Prior Sprint Plans (templates)

- [docs/research/INFRA_EXECUTION_FIDELITY_001_PLAN.md](docs/research/INFRA_EXECUTION_FIDELITY_001_PLAN.md) — closest precedent (opt-in fidelity flag + hash compatibility).
- [docs/research/INFRA_EXECUTION_FIDELITY_001_SUMMARY.md](docs/research/INFRA_EXECUTION_FIDELITY_001_SUMMARY.md) — summary doc pattern.
- [docs/research/FILL_TIMING_MODEL.md](docs/research/FILL_TIMING_MODEL.md) — model doc to mirror.
- [docs/research/CAMPAIGN_009_PRECOMMIT.md](docs/research/CAMPAIGN_009_PRECOMMIT.md) — same-bar tie-break rule.
- [docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md](docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md) — gap-fill mismatch documentation.

### Memory (auto-recalled)

- `forex-bot-research-freeze` — repo is frozen research platform; numbered infra sprints only.
- `infra-sprint-working-style` — commit per phase; document blockers honestly; pytest+ruff green at every commit; never weaken the freeze.

---

## Research Insights from Deepen Phase

This appendix consolidates findings from 8 parallel research/review agents (git-history-analyzer, best-practices-researcher, architecture-strategist, code-simplicity-reviewer, pattern-recognition-specialist, performance-oracle, kieran-python-reviewer, data-integrity-guardian) run on 2026-05-24. The plan body above incorporates the actionable findings; this appendix captures the supporting evidence and lessons learned.

### Git history of the `fill_timing` precedent

The `fill_timing` feature (the *only* prior opt-in fidelity flag in this repo) shipped in:

- **One atomic commit** `990112c` (Phase 1 of `infra-execution-fidelity-001`, 2026-05-22).
- **+559 lines / -10 lines across 8 files**: `config.py`, `engine.py`, `fills.py`, `metrics.py`, `exporters.py`, `cli.py`, `tests/unit/test_fill_timing.py` (279 lines, 13 tests), `docs/research/FILL_TIMING_MODEL.md` (133 lines).
- **Zero subsequent fix-up commits.** `git log -S"fill_timing"` after 2026-05-22 finds no follow-ups.

**Implication:** the gap-fill core change *could* fit in one commit, but this plan splits it into 4 atomic commits (Phase 1 instrumentation + Phase 2 plumbing + Phase 3 logic + Phase 4 exporters) because the gap-fill semantics are genuinely more complex than `fill_timing`'s "where does the entry fill" decision, and Phase 2's hash invariance check is load-bearing safety before any logic lands.

**Hash test pattern from `fill_timing`:** the precedent does NOT freeze a hex hash. Instead, `test_signal_bar_close_default_matches_explicit` asserts `implicit.config_hash == explicit.config_hash`. This plan adds *both* patterns: the engine-to-engine equality assertion AND a checked-in snapshot of pre-sprint hashes (with `_doc` guardrail to prevent accidental regeneration).

### Python dataclass evolution

- **Trailing defaults are the only safe additions.** Adding a no-default field after a default raises `TypeError: non-default argument 'X' follows default argument` at class-decoration time. Lock the trailing position with a `# trailing default-with-safety — must remain last` comment.
- **`field(default_factory=...)` only for mutable defaults.** `bool`/`int`/`str`/`Decimal`-literal/`None` use bare `= False`/`= 0`/`= None`.
- **Mypy strict is satisfied by bare defaults.** No need for `field(default=False)` wrappers.
- **Do NOT add `slots=True`.** It returns a new class object, breaks pickle round-trip in subtle ways (CPython #104035 for frozen+slots), and the records are not allocation hot.
- **Tolerant deserialization pattern:**
  ```python
  from dataclasses import fields
  def from_dict_tolerant(cls, data: dict):
      known = {f.name for f in fields(cls)}
      return cls(**{k: v for k, v in data.items() if k in known})
  ```

### pytest matrix patterns

- **Flat-tuple `pytest.param(..., id=...)` beats stacked decorators** for 4-axis matrices. IDs are diagnostic at failure time; `pytest -k "long-stop"` can bisect.
- **Factory-fixture (`make_gap_scenario`) beats module-level helper.** Composable with `eur_usd` fixture; gets pytest collection-time error reporting.
- **One parametrized test function, not 16 separate functions.** Scaffold deduplication; uniform failure surface.
- **`is not None` (not truthy) for `Decimal` checks.** `Decimal("0")` is falsy.

### Architecture verdicts

- **APPROVE WITH CHANGES.** Pattern compliance with `fill_timing` is complete; single-engine architecture is right (do NOT extract `ExitResolver`); trailing-stop snapshot is the right choice vs alternatives.
- **Phase 5 over-serializes.** Could split 5a/5b after Phase 1/2 and Phase 3 respectively. Cosmetic concern; not worth splitting.
- **Add hash key-insertion-order regression test** (AC-11) — proves the conditional `**({...} if ... else {})` spread doesn't perturb key order.
- **Add `gap_fill_distance_pips: Decimal | None`** now (cheap, prevents v2 sprint).
- **16-case matrix is audit-trail bait, not exhaustiveness.** Keep it AND add property-based test for invariants.

### Simplification verdicts (applied)

- **AC count reduced from 22 to 16** by dropping CI gates (lint, mypy, commit format) and implied criteria. CI gates are standing rules; ACs should be feature criteria.
- **Doc deliverables reduced from 4 to 3** by dropping `_STATUS.md` (no prior numbered sprint ships one).
- **Renamed `next_open` → `gap_through`** — removes confusion with `fill_timing="next_bar_open"`.
- **Merged Phase 1 (schema-only) + Phase 2 (ambiguous detection)** — schema-only has no independent commit value.

### Pattern consistency verdicts (applied)

- **Sprint id prefix corrected** to `infra-exit-fidelity-001` — every numbered sprint uses `infra-`/`research-` prefix.
- **`_STATUS.md` removed** — no precedent for numbered sprints.

### Performance verdict

- **NEGLIGIBLE IMPACT.** New per-bar work (~5-15μs) is <1% of existing per-bar cost (~10-1000μs dominated by `generate_signal` + 6 existing `Decimal(str(...))` conversions). No change to the plan. Future optional sprint `infra-decimal-hoisting-001` could hoist all conversions.

### Kieran's nits (applied)

- Local var `gap_fill` → `did_gap_fill` (prevents kwarg-shadowing at call site).
- Local var `ambiguous` → `tp_also_in_range` (more meaningful at call site).
- Long/short mirror folded via `is_long` flag (5 branches → 2).
- Snapshot type-annotated explicitly: `pre_trailing_stop_price: Decimal = open_trade.stop_price`.
- Keep `Literal` over `Enum` (mirrors `FillTiming`).
- Keep `frozenset` constant + `Literal` type alias together.

### Data-integrity verdict

- **MOSTLY SAFE (3 caveats — all addressed).**
- All `_index.json`/`summary.json` readers are tolerant (`json.loads` + `.get(...)`). No dataclass deserialization. Adding fields is provably safe.
- `hashlib.sha1(repr(payload))` is version-stable for primitive-only `strategy_config`. AC-12 enforces this.
- **`FoldMetrics` future-proofing:** add a comment in `research/walk_forward/models.py` that any future `FoldMetrics(**summary_metrics)` consumer must filter to known keys (since `summary.json["metrics"]` will gain `ambiguous_exit_count` / `gap_fill_exit_count`, and `FoldMetrics` is `extra="forbid"`). This is documentation-only — Phase 5 doc work.
- Phase 0 snapshot file gets `_doc` guardrail header. AC-13 enforces.

---

**Sprint ready for `/workflows:work`.**
