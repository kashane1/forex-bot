# CAMPAIGN_011 — Financing + Portfolio-Risk Readiness

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-001`
`strategy_evidence: false`

Phase 6 financing-overlay + portfolio-risk integration-readiness
assessment for the **CAMPAIGN_011 research candidate**
(`random_entry_anchor 0.1.0-c011`). **Reading this document does
not approve the strategy and does not constitute a campaign
verdict.** It records whether the scaffold is *structurally
ready* for the future evidence sprint to compute the financing
overlay and risk diagnostics.

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. **CAMPAIGN_011 is a null model — cannot be
> approved by design. Item 5 (independent corroboration) and item
> 6 (human approval) of the six-evidence ladder are structurally
> not binding for this candidate.**

## 1. Headline status

| dimension | status |
|---|---|
| `research.financing.calculate_run` callable | **READY** — same interface CAMPAIGN_010 used; no changes required |
| `default_stress_rate_source()` available | **READY** — conservative-stress source, debit-on-both-sides; `MODELED` refused at four layers |
| `PositionInterval` adapter (trade CSV → financing input) | **READY** — same shape as CAMPAIGN_010's; the future evidence sprint will clone `scripts/build_campaign_010_financing_overlay.py` |
| `RiskEngine(mode="backtest")` integration | **READY** — same wiring as CAMPAIGN_010 |
| Risk diagnostics script | **NOT YET WRITTEN** — `scripts/build_campaign_011_risk_diagnostics.py` is a future-evidence-sprint task; clone `scripts/build_campaign_010_risk_diagnostics.py` and swap the `CAMPAIGN_011` constant |
| Financing-overlay invocation | **NOT EXECUTED** in this sprint | requires the future evidence sprint to have committed per-fold trade artifacts first |
| Risk diagnostics generation | **NOT EXECUTED** in this sprint | future evidence sprint |

**Net: financing + risk plumbing readiness is GREEN; overlay
computation remains the future evidence sprint's job.**

## 2. Financing overlay — ESTIMATED + conservative-stress only

| dimension | value |
|---|---|
| financing source | `research.financing.default_stress_rate_source()` (conservative-stress, debit-on-both-sides) |
| treatment | **`ESTIMATED`** |
| `MODELED` reachable? | **no** — refused at four layers (matches CAMPAIGN_010 + every prior research path) |
| `OBSERVED` available? | **no** — no captured `DAILY_FINANCING` events exist for 2020–2026 |
| engine-PnL mutation? | **no** — financing is an off-engine overlay; engine PnL is unchanged |
| live-promotion blocker | **`financing_is_live_blocker = true`** (unchanged, structurally moot for a null model) |

### 2.1 The four MODELED-refusal layers (unchanged by this sprint)

1. `research.financing.TableRateSource(treatment=MODELED)` raises at construction.
2. `research.financing.calculate_run(rate_source)` raises if `source.treatment == MODELED`.
3. `research.financing.FinancingRunReport.financing_treatment` is Pydantic-pinned to `ESTIMATED` / `OBSERVED` via the calculator output.
4. `src/forex_bot/financing.py` `financing_treatment_blocks_approval` continues to refuse paper / demo / live promotion without `MODELED`.

## 3. Expected holding period + financing sensitivity (random)

| dimension | value |
|---|---|
| expected holding period per trade | ≤ 6 H4 bars (= 1 trading day; matches CAMPAIGN_010) |
| trades expected to span the 17:00-NY rollover | ~50–70 % of trades (depends on bar-of-entry distribution) |
| expected Wednesday triple-swap incidence | ~⅛ of multi-day trades |
| expected total rollover events | ~0.6–0.8 events per trade × ~2,000–3,000 random trades ≈ 1,500–2,400 events (similar order of magnitude to CAMPAIGN_010's 2,483) |
| expected `cashflow_home_stress_total` magnitude | ~−$30 to −$60 USD (similar order of magnitude to CAMPAIGN_010's −$55.69) |
| expected `missing_rate_event_count` | **0** (conservative source has rates for every pair) |
| expected per-pair sensitivity | distributed across all 7 pairs in proportion to per-pair trade counts (random uniformly samples) |
| expected long/short sensitivity | ~equal debit on both sides (conservative source is symmetric) |
| expected impact on aggregate verdict | **vacuously PASSES** the `conservative_stress_run_does_not_flip_verdict` gate because the pre-financing verdict is already expected REJECT under random entry |

## 4. Future financing-overlay invocation (recorded; not run here)

The future
`research-random-entry-diagnostic-anchor-walk-forward-001`
sprint's Phase 5 must run:

```bash
# Clone scripts/build_campaign_010_financing_overlay.py:
#   - swap CAMPAIGN_010 → CAMPAIGN_011 in paths
#   - swap the campaign-dir argument
# Then run:
.venv/bin/python scripts/build_campaign_011_financing_overlay.py \
    --campaign-dir backtests/CAMPAIGN_011_random_entry_anchor/
```

Outputs (committed by the evidence sprint):
- `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.json`
- `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_run.md`
- `backtests/CAMPAIGN_011_random_entry_anchor/financing/financing_summary.json`

Plus `docs/research/CAMPAIGN_011_FINANCING_OVERLAY.md` mirroring
`CAMPAIGN_010_FINANCING_OVERLAY.md`.

## 5. Portfolio-risk diagnostics

### 5.1 Expected risk profile under random entry

| dimension | expected value | rationale |
|---|---|---|
| max concurrent open positions per instrument | **1** (engine-enforced + R2 rule) | identical to CAMPAIGN_010 |
| max open positions across portfolio | **1** (`risk.max_open_positions=1` config gate) | identical to CAMPAIGN_010 |
| per-pair trade count distribution | **~uniform across the 7 pairs** (~290–420 per pair × 8 folds, subject to R5 NaN-ATR rejections + R6 spread filter rejections) | random samples uniformly; **CONTRAST** with CAMPAIGN_010's pair-skewed distribution (USD_JPY = 492, NZD_USD = 47) |
| per-pair max loss per trade | ~$1.30 (bounded by ATR stop × `risk_per_trade_pct = 0.25 %` × `$500` starting equity per pair) | identical to CAMPAIGN_010 |
| per-pair max win per trade | bounded above by time-stop catching profitable moves at 6 bars | identical to CAMPAIGN_010's `+$5.35` order of magnitude |
| pair concentration (single-pair dominance %) | ≤ 25 % (uniform target ≈ 14 %) | random — no concentration |
| **session-of-day entry distribution** | **~uniform across all 24 UTC hours** | **KEY DIAGNOSTIC CONTRAST** — CAMPAIGN_010 was 100 % London-window (06 UTC + 09 UTC clusters); random has no session bias |
| loss streaks per pair | binomial(N, p ≈ 0.5 − cost-bias); expected max ~10 over ~300–400 trades per pair | random has no streak structure beyond binomial expectations |
| drawdown clustering | mild; no per-fold drawdown should exceed `risk.max_total_drawdown_pct = 8 %` | random has no path dependence |
| RiskEngine rejection profile | spread filter + spread-to-ATR rejection rate similar to CAMPAIGN_010's ~30 % | same spread thresholds; same rejection codes |

### 5.2 Future risk-diagnostics invocation (recorded; not run here)

The future evidence sprint's Phase 6 must run:

```bash
# Clone scripts/build_campaign_010_risk_diagnostics.py:
#   - swap CAMPAIGN_010 → CAMPAIGN_011 in paths
#   - add the "expected uniform session distribution" comparison
#     diagnostic (the key contrast vs CAMPAIGN_010)
# Then run:
.venv/bin/python scripts/build_campaign_011_risk_diagnostics.py \
    --campaign-dir backtests/CAMPAIGN_011_random_entry_anchor/
```

Outputs:
- `backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.json`
- `backtests/CAMPAIGN_011_random_entry_anchor/risk/diagnostics.md`

Plus `docs/research/CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`
mirroring `CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`.

## 6. Random-entry baseline value (the point of this candidate)

CAMPAIGN_005 reported the existing random-entry baseline:

| dimension | value (from CAMPAIGN_005) |
|---|---|
| universe | 6 majors (NZD_USD excluded) |
| hold | fixed 30 H4 bars (not the 6-bar time stop CAMPAIGN_011 uses) |
| financing overlay | not applied |
| risk diagnostics | not applied |
| walk-forward | single window |
| aggregate expectancy R | **−0.095 R** per trade |
| seeds | 20 (per-pair std reported) |

CAMPAIGN_011's evidence sprint will produce a strictly stronger
baseline:

| dimension | value (expected from CAMPAIGN_011) |
|---|---|
| universe | **7 pairs (matches CAMPAIGN_010)** |
| hold | **6 H4 bars time-stop (matches CAMPAIGN_010)** |
| financing overlay | **ESTIMATED + conservative-stress applied** |
| risk diagnostics | **full RiskEngine rejection table + concurrency + exposure trace** |
| walk-forward | **8-fold rolling/frozen (matches CAMPAIGN_010)** |
| aggregate expectancy R | expected to be roughly comparable to CAMPAIGN_005 (~−0.05 to −0.15 R), deepened by the longer effective cost-bias |
| seeds | **1 deterministic master_seed = 20260523** (exact reproducibility) |

The CAMPAIGN_011 evidence sprint's headline number is the
**per-fold + aggregate falsifiability floor** every subsequent
candidate must clear.

## 7. Independent verifier (covered separately)

See [`CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md).
Verifier extension is recommended as a follow-up but not blocking;
item 5 of the six-evidence ladder is structurally not binding
for a null model.

## 8. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT.**
- **CAMPAIGN_010 remains REJECT.**
- **Paper / demo / live remain blocked.**
- No broker call this sprint.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.
- `MODELED` financing remains refused at four layers.
- live-promotion financing blocker stands (structurally moot for
  a null model).

## 9. Cross-links

- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
- [`CAMPAIGN_011_SMOKE_RESULT.md`](CAMPAIGN_011_SMOKE_RESULT.md)
- [`CAMPAIGN_011_WALK_FORWARD_READINESS.md`](CAMPAIGN_011_WALK_FORWARD_READINESS.md)
- [`CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md)
- [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md)
  (template the future evidence sprint will mirror)
- [`CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md)
  (template the future evidence sprint will mirror)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md`](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md)
- [`scripts/build_campaign_010_financing_overlay.py`](../../scripts/build_campaign_010_financing_overlay.py)
- [`scripts/build_campaign_010_risk_diagnostics.py`](../../scripts/build_campaign_010_risk_diagnostics.py)
