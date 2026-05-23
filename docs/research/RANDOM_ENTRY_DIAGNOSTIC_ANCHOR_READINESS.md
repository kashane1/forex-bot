# Random-Entry Diagnostic Anchor — Scaffold Readiness

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-001`
`strategy_evidence: false`

Phase 4 scaffold-readiness summary for **CAMPAIGN_011** /
`random_entry_anchor 0.1.0-c011`. **This document does not run
any evidence and does not approve the strategy.** It certifies
that the scaffold is structurally ready for the future evidence
sprint to drive `WalkForwardResults`.

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. **CAMPAIGN_011 is a null model — cannot be
> approved by design.**

## 1. Scaffold readiness status

| dimension | status |
|---|---|
| Strategy module conforms to the `Strategy` protocol | **READY** — `name`, `version`, `warmup_bars_required()`, `generate_signal(ctx) -> Signal | None` |
| Strategy module imports / structural audits | **READY** — no `forex_bot.broker` / `.execution` / `.loops`; no `random` / `numpy.random` / built-in `hash()`; no CAMPAIGN_002 / CAMPAIGN_010 parameter contamination (verified by 36 Phase 3 unit tests) |
| Deterministic seed input | **READY** — `_derive_random_pair(master_seed, instrument_name, bar_timestamp_iso)` signature is structurally rail-tested to contain no price arguments; SHA-256 over UTF-8 produces `(bar_random, gate_random)` from disjoint digest halves |
| Distribution / frequency invariants | **VERIFIED** — long-share is 0.5 ± 3σ over 10,000 bars (deterministic seed); entry rate is `entry_probability_per_bar` ± 2σ |
| Config sub-model + slot | **READY** — `RandomEntryAnchorStrategyConfig` (`extra="forbid"`) with defaults matching the frozen spec verbatim; `StrategyConfig.random_entry_anchor` slot wired; `_check_enabled` enforces required-when-enabled |
| Research config (`configs/campaign_011_random_entry_anchor.yaml`) | **READY** — loads via `load_settings(...)`; `app.trading_enabled=false`, `app.allow_order_submission=false`, `app.allow_live_trading=false`; 7-pair H4 universe matching CAMPAIGN_010 |
| Data plumbing | **READY** — `database_path: ./data/campaign_002.sqlite3` (gitignored symlink to the shared store created by the prior CAMPAIGN_010 evidence sprint); the future evidence sprint can read 7 pairs × ~9,931 H4 bars each immediately |
| Walk-forward harness compatibility | **READY** — `parameter_mode = frozen` and `split_style = rolling` are the only authorized modes and are the modes the candidate uses; the same `scripts/run_walk_forward_dry_run.py` invocation as CAMPAIGN_010 produces the same 8 folds |
| Financing-overlay compatibility | **READY** — `research.financing.calculate_run(positions, default_stress_rate_source())` exactly as CAMPAIGN_010 did; MODELED refused at four layers |
| Risk-diagnostic compatibility | **READY** — `RiskEngine(settings, mode="backtest")` exactly as CAMPAIGN_010 did; the existing `scripts/build_campaign_010_risk_diagnostics.py` pattern is directly reusable |
| Independent-verifier compatibility | **OPTIONAL FOLLOW-UP** — verifier is capability-locked to CAMPAIGN_002 `trend_following 0.1.0`; CAMPAIGN_011 extension recommended as `infra-free-local-parity-verifier-random-entry-001` but not blocking |
| Future evidence-sprint commands | **DOCUMENTED** in [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md) §7.2 + [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md) §4 |

**Net: scaffold readiness is GREEN; backtest evidence remains
the future evidence sprint's job.**

## 2. Future evidence branch identity

| field | value |
|---|---|
| branch name | `research-random-entry-diagnostic-anchor-walk-forward-001` |
| sprint type | evidence (full walk-forward + financing + risk + verifier-readiness) |
| base commit | the tip of `research-random-entry-diagnostic-anchor-001` (this scaffold sprint) |
| binding prompt spec | [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md) |
| expected commits | 9 (Phase 0 → Phase 8 — mirrors CAMPAIGN_010 evidence sprint exactly) |

## 3. Data expectations (no fetch needed)

| dimension | value |
|---|---|
| local store path | `data/campaign_002.sqlite3` (gitignored symlink to `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3`) |
| symlink status | present in this worktree (created by `research-asian-london-session-breakout-walk-forward-001` Phase 1; verified read-only by Phase 0 of this sprint) |
| pairs (7) | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD |
| timeframe | H4 |
| candle source label | `oanda-practice` (asserted at runtime by the future evidence sprint's runner) |
| coverage per pair | 2020-01-01 → 2026-05-19 (~9,931 H4 candles each) |
| credentials needed for evidence run | **none** — local data only |
| broker / OANDA call needed for evidence run | **none** |
| new external dependency | **none** |

## 4. Known limitations

- **Null-model verdict is preordained.** The expected outcome is
  REJECT. The sprint's *value* is in producing a per-fold +
  aggregate metric vector that future "real" candidates must
  beat by a meaningful margin; the verdict classification is
  the diagnostic.
- **Verifier coverage absent.** The free / local verifier is
  capability-locked to CAMPAIGN_002 `trend_following`; extension
  for `random_entry_anchor` is recommended as a follow-up but
  not required for the REJECT verdict (item 5 of the
  six-evidence ladder is a paper-promotion gate).
- **Entry-probability calibration is fixed.** `0.05` per bar was
  chosen *before* writing the strategy module to target the
  CAMPAIGN_010 trade-count regime. If the future evidence sprint
  finds the trade count falls outside the `≥ 30 per fold` /
  `≥ 200 aggregate` gates, the documented response is **not** to
  re-tune the gate — it is to record the result as INCONCLUSIVE
  and address the calibration in a *separate* sprint, never
  during the evidence run.
- **Single master_seed.** `master_seed = 20260523` is fixed.
  Any seed change constitutes a NEW candidate.

## 5. Why this is useful despite not being approvable

1. **Pipeline validation.** Running CAMPAIGN_011 through the
   full walk-forward + financing + risk pipeline exercises every
   stage that any future "real" candidate would, using the same
   engine, gates, universe, data, and financing source as
   CAMPAIGN_010. A clean REJECT confirms the pipeline correctly
   classifies a known-zero-edge strategy.
2. **Falsifiability bar.** The per-fold + aggregate expectancy R
   values become the reference floor that every subsequent C2 /
   C3 / C4 / new-family candidate must clear by a meaningful
   margin to count as evidence of an edge. CAMPAIGN_005 set a
   single-window baseline; CAMPAIGN_011 will set the
   walk-forward-aware, financing-net, risk-checked baseline.
3. **Deterministic reproducibility.** Because random has no
   parameters except the master seed (and the seed is frozen),
   the reference is exactly reproducible across runs and across
   any independent verifier implementation. This is uniquely
   valuable for the future verifier-extension sprint.
4. **Pipeline-bug detection.** If the future evidence sprint
   records an unexpected PASS, that **is** the value — it means
   the pipeline has an information-leakage bug (or the financing
   overlay's stress rates are too lenient, or the gates are
   miscalibrated). Detecting that *before* a future "real"
   candidate accidentally inherits the same bug saves substantial
   investigation effort downstream.
5. **Discovery-cycle hygiene.** After two consecutive directional
   REJECTs (CAMPAIGN_009, CAMPAIGN_010) on real-OANDA H4 majors
   in trend / breakout space, validating the pipeline before
   testing another "real" candidate is the highest-value next
   step. It also de-risks the next *real* candidate (C3 — regime
   switcher) by establishing a clean reference point.

## 6. Comparison to CAMPAIGN_005

| dimension | CAMPAIGN_005 (existing benchmark) | CAMPAIGN_011 (this scaffold) |
|---|---|---|
| protocol | single-window benchmark | rolling walk-forward (frozen, 540/180/180/180 days, 8 folds) |
| universe | 6 majors | **7 pairs** (matches CAMPAIGN_010) |
| fold structure | none | per-fold + aggregate breakdown |
| financing overlay | not applied | **ESTIMATED + conservative stress** (via `default_stress_rate_source()`) |
| risk diagnostics | not applied | full RiskEngine rejection table + concurrency + exposure trace |
| evidence-pipeline coverage | trades + per-pair expectancy only | full `WalkForwardResults` + gate vector + verdict classification |
| comparison value | aggregate-only random expectancy on 6 majors (−0.095 R) | **per-fold + aggregate + per-pair random expectancies on 7 pairs under the same gates used by CAMPAIGN_010 and any future candidate** |
| seed determinism | single seed per run | **frozen seed sequence committed in the pre-commit; deterministic across runs** |
| repeatability | one-off | re-runnable with deterministic outputs |
| useful as approval-gate input | no | **no** (null model still cannot be approved) — but **uniquely useful as the falsifiability anchor for future candidates** |

CAMPAIGN_011 is therefore a strictly stronger anchor than
CAMPAIGN_005 because the latter pre-dates the walk-forward
harness + financing calculator + risk-diagnostic conventions.
Once CAMPAIGN_011's evidence sprint completes, the falsifiability
bar is set on the *same* infrastructure every future candidate
will use.

## 7. Pre-flight checklist for the future evidence sprint

The future
`research-random-entry-diagnostic-anchor-walk-forward-001`
sprint's Phase 0 audit should verify:

- [ ] Repo state clean.
- [ ] `configs/approved_strategies.yaml` reads `approved: []`.
- [ ] CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011 verdicts /
      statuses unchanged.
- [ ] 771 pytests pass (this scaffold's contribution).
- [ ] 11 pre-existing UP042 ruff findings in untouched files
      (unchanged).
- [ ] Archive validator + freeze checker + secret scanner PASS.
- [ ] Loops refuse; no `live-loop`.
- [ ] `src/forex_bot/strategies/random_entry_anchor.py` exists
      and unit tests pass.
- [ ] `configs/campaign_011_random_entry_anchor.yaml` loads
      with frozen parameters matching this pre-commit verbatim.
- [ ] `data/campaign_002.sqlite3` symlink present; 7 pairs ×
      H4 store readable.
- [ ] `master_seed = 20260523` (or whatever is in the
      pre-commit) — must match exactly.

## 8. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **CAMPAIGN_010 remains REJECT** (untouched).
- **CAMPAIGN_011** scaffold-only at the close of this sprint.
- **Paper / demo / live remain blocked.**
- No broker / OANDA call this sprint.
- No `.env` read; no credential printed; no account / order /
  trade / position / transaction endpoint queried.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.
- `MODELED` financing remains refused at four layers.

## 9. Cross-links

- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
  (the gate vector CAMPAIGN_011 inherits)
- [`backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md`](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md)
  (the single-window precedent CAMPAIGN_011 strictly improves on)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
