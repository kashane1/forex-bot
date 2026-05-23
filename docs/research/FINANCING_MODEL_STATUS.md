# Research-Grade Financing Calculator — Status

**Date:** 2026-05-23 · **Branch:** `research-financing-model-001`
`strategy_evidence: false`

Headline status of the research-grade financing / carry /
rollover calculator after Sprint 001. **The calculator is
implemented, tested, and ready for use by future strategy
campaigns as a richer per-event diagnostic on top of the
existing per-trade overlay.** It runs entirely off-engine and
does not modify any production code path.

> No strategy approved. CAMPAIGN_002 remains REJECT. Paper /
> demo / live remain blocked. The calculator is diagnostic
> infrastructure and writes `strategy_evidence: false` on every
> output it emits. It is **never** the source of `MODELED`
> financing; the existing
> [`src/forex_bot/financing.py`](../../src/forex_bot/financing.py)
> approval gate remains authoritative for the live-promotion
> blocker.

## 1. Implemented pieces

| component | file | role |
|---|---|---|
| Public API | `research/financing/__init__.py` | re-exports of models, rates, calculator, reporting |
| Pydantic models | `research/financing/models.py` | `PositionInterval` (instrument/side/units/price/tz-aware time invariants), `FinancingCalculatorConfig` (rollover hour, triple-swap weekday, weekend skip, missing-rate policy, conservative fallback), `DailyFinancingEvent` (stress<=0 + applied_side rails), `PositionFinancingSummary` (rollover-count cross-check), `FinancingRunReport` (Pydantic-pinned `strategy_evidence: false`, `financing_in_engine_pnl: false`, `financing_is_live_blocker: true`, treatment-match cross-check, MODELED refusal), `RatePair`, `FinancingTreatment` enum mirroring the canonical values, `MissingRatePolicy` enum |
| Rate sources | `research/financing/rates.py` | `FinancingRateSource` interface + `TableRateSource` (per-(date, instrument) lookup; refuses MODELED; defaults ESTIMATED; copies input table) + `ConservativeStressRateSource` (default; per-pair pessimistic bp/day, debit-only on both sides; mirrors `CONSERVATIVE_BP_PER_DAY` from the existing overlay locally to preserve import isolation) + `default_stress_rate_source()` helper |
| Calculator | `research/financing/calculator.py` | `calculate_position` (per-day rollover events, weekend skip, Wednesday triple, missing-rate fallback) + `calculate_run` (multi-position aggregate, injectable `now=`, MODELED-source refusal) + `MissingFinancingRateError` |
| Reporting | `research/financing/reporting.py` | `render_summary_md` (deterministic markdown) and `dump_events_json` (deterministic UTF-8, sorted keys, ISO-8601 dates, 2-space indent, no I/O) |
| Package README | `research/financing/README.md` | usage + scope rails + isolation notes |

Code layout mirrors the walk-forward harness conventions:
Pydantic models with `extra="forbid"`, frozen models, named
re-exports through the package root, and a grep-enforced
import-isolation test rail.

## 2. Tests

| file | cases | role |
|---|---|---|
| `tests/research/test_financing_models.py` | 23 | `PositionInterval` validation (instrument shape, side, positive units/price, time ordering, tz-aware, home_currency), `FinancingCalculatorConfig` defaults & bounds, `DailyFinancingEvent` stress<=0 + applied_side rails, `PositionFinancingSummary` rollover/event-count cross-check, `FinancingRunReport` strategy_evidence / engine_pnl / live_blocker / MODELED-refusal / treatment-match rails, grep-enforced import-isolation rail |
| `tests/research/test_financing_rates.py` | 12 | bp/day table mirrors the existing overlay; default stress source treatment & name; debit-on-both-sides; default for unknown pair; custom table + default; date-independence; `TableRateSource` None-on-miss, stored value, MODELED refusal, ESTIMATED default, input-copy isolation |
| `tests/research/test_financing_calculator.py` | 21 | long/short × positive/negative carry; zero rate; multi-day with Wednesday triple swap; same-day open + close = 0 rollovers; intraday rollover-crossing position records 1 event; triple-swap on Wed; triple-swap disable; weekend skip; weekend-skip disable; missing-rate conservative / skip / error / custom-fallback bp/day; USD-quote notional = units × price; USD-base notional = units; JPY-precision; cross-pair conservative-fallback note; `calculate_run` aggregation + empty list + MODELED-source refusal + missing-event counter |
| `tests/research/test_financing_reporting.py` | 15 | JSON determinism, parses, sorted keys, ISO-8601 dates; markdown determinism, required sections, triple-swap markers, MISSING markers, credit-path zero-stress marker, treatment enum value, triple-swap-disabled rendering, empty report |

**71 financing tests pass.** Full repo suite: **594 passes**
(523 prior + 71 new). Ruff is clean over `src tests scripts
research/parity_verifier research/walk_forward research/financing`.

## 3. Current limitations

- **Stress-only data today.** The two v1 rate sources
  (`TableRateSource`, `ConservativeStressRateSource`) cover any
  scenario the caller can build by hand. Neither retrieves
  observed historical rates, because:
  - OANDA's v20 REST API publishes no historical
    financing-rate series for 2020–2026.
  - The bot has captured no `DAILY_FINANCING` transactions
    (no orders have been submitted under the freeze).
  - The practice account's `longRate` / `shortRate` are `0`.
  This is unchanged from the existing overlay's posture.
- **Treatment ceiling.** Every source the module currently
  exposes is `ESTIMATED`. **`MODELED` is refused** by both the
  rate-source constructor (`TableRateSource(treatment=MODELED)`
  raises) and by `calculate_run` (a source self-reporting
  MODELED raises). The `MODELED` slot is reserved for the
  future `FutureOandaObservedFinancingModel` path in
  `src/forex_bot/financing.py`.
- **Engine PnL is unchanged.** The bespoke `BacktestEngine`'s
  PnL formula still contains no financing accrual. This
  calculator runs alongside the engine, not inside it. Engine
  reproducibility is preserved.
- **Cross-pair conversion deferred.** Pairs where neither base
  nor quote is the home currency fall back to a conservative
  fallback for the notional path and surface a note on every
  event (`"cross-pair conversion deferred — using units as
  notional ..."`). A v1.1+ extension could accept a per-date
  home-quote map; out of scope for v1.
- **Holiday calendar absent.** Missing holidays are treated as
  ordinary rollover days; if the rate source has no rate for a
  holiday, the missing-rate policy fires. This is deliberately
  conservative and avoids embedding a stale or
  jurisdiction-specific calendar in research-only code.
- **Calculator only.** No dry-run CLI script is provided in v1
  (unlike `scripts/run_walk_forward_dry_run.py`). The
  calculator is imported and driven from notebook or campaign
  code; future sprints can add a CLI if recurring usage demands.
- **Position log adapter pending.** Converting a campaign's
  trade artifacts (CSV / JSON dumps under
  `backtests/<campaign>/`) into `PositionInterval` lists is the
  campaign code's responsibility. The protocol does not
  prescribe a file format; a small per-campaign adapter
  function suffices.

## 4. Actual historical financing supported?

**No.** Real historical financing rates are not available to
this repo (per §3 above). The calculator can *consume* an
arbitrary table of rates via `TableRateSource`, but no such
table for OANDA's 2020–2026 history is committed, and the
sprint does not authorize fetching one.

## 5. Stress-only mode supported?

**Yes.** Stress mode is the default research path:

```python
from research.financing import calculate_run, default_stress_rate_source

report = calculate_run(
    positions,
    rate_source=default_stress_rate_source(),
    # config defaults to v1 protocol defaults
)
```

The default stress source is debit-only on both long and short
(the `cashflow_home_stress` view never assumes a credit).
Wednesday rollovers are triple-multiplied, weekends are skipped.
A pessimistic-flat run (no triple swap, no weekend skip) is one
config flip away — see [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
§11.

## 6. How future campaigns should use the calculator

1. **Pre-commit phase.** The campaign's
   `<CAMPAIGN>_PRECOMMIT.md` declares which rate source it
   plans to use (`default_stress_rate_source()` for v1
   research; a `TableRateSource` with provenance otherwise),
   the `FinancingCalculatorConfig` knobs, and the financing
   pass/fail gate (e.g. "campaign passes only if
   `cashflow_home_stress_total / total_pnl >= -X`").
2. **Build the position list.** Convert the campaign's
   committed trade artifacts into a
   `list[PositionInterval]` via a small adapter function
   inside the campaign code. Position-id strings should be
   opaque.
3. **Run the calculator.** Call `calculate_run(positions,
   rate_source, config)` and dump the report:
   ```python
   report = calculate_run(positions, source, cfg)
   Path("<campaign>/financing_run.json").write_text(dump_events_json(report))
   Path("<campaign>/financing_run.md").write_text(render_summary_md(report))
   ```
4. **Embed report metadata in the campaign report.** The
   campaign's `<CAMPAIGN>_REPORT.md` must surface the
   `financing_treatment`, `financing_in_engine_pnl`,
   `financing_is_live_blocker`, `cashflow_home_total`,
   `cashflow_home_stress_total`, and `missing_rate_event_count`
   fields verbatim.
5. **Approval gate.** The existing
   `financing_treatment_blocks_approval` in
   `src/forex_bot/financing.py` remains the authoritative
   approval check. The calculator reports `ESTIMATED` — enough
   to gate paper / demo (per the existing rule), never enough
   for live.
6. **Verdict.** Financing-stress alone is not a green light. A
   passing financing-stress diagnostic merely shows the result
   is not *additionally* killed by a pessimistic assumption; it
   does not establish an edge.

## 7. Relationship to the existing per-trade overlay

The new calculator and the existing
`src/forex_bot/financing.py` per-trade overlay are
**complementary**, not competing:

| concern | existing overlay | new research calculator |
|---|---|---|
| Where it runs | inside campaign reporting code | research-only, off-engine |
| Granularity | one bp/day debit per closed trade | per-day rollover event log |
| Long vs short | flattened to the worse side | distinct via `RatePair.long_annual_bp` and `short_annual_bp` |
| Calendar | `bars × hours / 24` | explicit per-date with weekend skip + Wednesday triple |
| Currency | USD-base / USD-quote heuristic | USD-base / USD-quote + cross-pair flagged fallback |
| Approval gate | `financing_treatment_blocks_approval` (authoritative) | embeds the same `FinancingTreatment` value into the report; does not gate by itself |
| Treatment ceiling | `ESTIMATED` (current default) or `UNMODELED` | `ESTIMATED` (refuses MODELED) |
| Live blocker | yes (authoritative) | yes (acknowledged in every report; never lifted by this module) |
| Tests | `tests/unit/test_financing.py`, `tests/unit/test_financing_model.py` | `tests/research/test_financing_*.py` (71 cases) |

Future campaigns should use **both**: the existing overlay for
the campaign report's bp/day stress column (the authoritative
approval-gate path), and the new calculator for richer per-event
diagnostics next to it.

## 8. Safety state (unchanged by this sprint)

- `configs/approved_strategies.yaml`: **`approved: []`**
  (verified by the freeze checker).
- **CAMPAIGN_002 remains REJECT** — its verdict is independent
  of any financing model.
- **Paper / demo / live remain blocked.** `paper-loop` and
  `demo-loop` refuse; no `live-loop` command exists.
- **`financing_treatment_blocks_approval` rules unchanged**:
  `live` unconditionally requires `MODELED`; `paper` / `demo`
  unmodeled blocked except by explicit human override; nothing
  in this sprint produces `MODELED` financing.
- **No bespoke-engine edit.**
- **No `src/forex_bot/financing.py` edit.**
- **No `ObservedFinancingEventRepo` write.** The table remains
  empty.
- **No OANDA call, no `.env` read, no credential printed.**
- **No new external dependency.**
- **Import isolation:** no file under `research/financing/`
  imports from `forex_bot` (grep-enforced).
- **No `MODELED` financing reachable** through any rate source
  in this module.

## 9. EVIDENCE_MANIFEST.json

The manifest tracks **campaigns**; this sprint adds no campaign,
so `docs/research/EVIDENCE_MANIFEST.json` requires no entry. The
diagnostic-artifact section would only be touched if a sprint
emitted concrete diagnostic files under `backtests/diagnostics/`
or similar. This sprint emits docs, code, and tests only —
which the archive validator covers via the docs-only path. The
validator continues to PASS.

## 10. Cross-links

- Sprint plan:
  [`FINANCING_MODEL_001_PLAN.md`](FINANCING_MODEL_001_PLAN.md)
- Current assumptions audit:
  [`FINANCING_MODEL_CURRENT_ASSUMPTIONS.md`](FINANCING_MODEL_CURRENT_ASSUMPTIONS.md)
- Protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- CAMPAIGN_002 retrospective:
  [`CAMPAIGN_002_FINANCING_RETROSPECTIVE.md`](CAMPAIGN_002_FINANCING_RETROSPECTIVE.md)
- Existing per-trade overlay design:
  [`FINANCING_MODEL_DESIGN.md`](FINANCING_MODEL_DESIGN.md)
- Observed-event capture layer:
  [`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md)
- Recommended-next-branch source:
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §5.4
- Walk-forward harness (sister sprint):
  [`RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md`](RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
