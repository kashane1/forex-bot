# Infrastructure Free / Local Parity Verifier Sprint 004 — Plan

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-004-rounding-closure`
**Base commit:** `a332a00` (HEAD of `infra-free-local-parity-verifier-003-with-data`)

Focused precision / rounding closure sprint. Sprint 003 unblocked
the full-data verifier run and fixed two verifier-side bugs;
overall comparison moved from FAIL to WARN. This sprint targets the
remaining WARN-band drift on the verifier side only.

> `strategy_evidence: false`. This sprint cannot approve a strategy.
> CAMPAIGN_002 remains REJECT. Paper / demo / live remain blocked.
> `configs/approved_strategies.yaml` stays empty.

## 1. Purpose

Investigate the remaining WARN drift between the independent
verifier and the no-RiskEngine bespoke reference (1,647 trades) and,
where the cause is a verifier-side precision or rounding gap, fix it
without touching the bespoke engine, strategy rules, or CAMPAIGN_002
parameters.

The candidate causes called out by Sprint 003's debug notes are:
1. Bespoke uses `decimal.Decimal` end-to-end; verifier uses float.
2. Bespoke calls `instrument.round_price(stop)` (display-precision
   rounding); verifier doesn't.
3. PnL conversion for USD-base pairs (USD_JPY, USD_CAD, USD_CHF)
   may have subtly different intermediate precision.

## 2. Non-goals

- Not a strategy approval. CAMPAIGN_002 stays REJECT.
- Not a tuning loop.
- Not a paper / demo / live trigger.
- Not an OANDA / QC / LEAN call — zero API calls, the local
  `data/campaign_002.sqlite3` and the already-exported CSVs are
  the only data sources.
- Not a bespoke-engine change. The bespoke engine is the source of
  truth; only the verifier moves.
- Not a CAMPAIGN_002 rule change. The frozen parameter set in
  `research/lean_parity/lean_parity_config.json` is read-only input.

## 3. Safety invariants

1. `configs/approved_strategies.yaml` stays `approved: []`.
2. CAMPAIGN_002 remains REJECT. No campaign re-run.
3. Paper / demo loops keep refusing; no `live-loop` command exists.
4. No QC credential is requested, read, written, or echoed.
5. No OANDA API call. The only OANDA-touch permitted is reading the
   already-local `data/campaign_002.sqlite3` (cross-worktree read,
   user-authorized in Sprint 003) — no fetch, no rehydrate.
6. No credential value is printed. No `.env` is staged.
7. No `*.sqlite3`, candle CSV, or bulky verifier output gets staged.
8. The bespoke engine under `src/forex_bot/` is **not modified**
   unless a real bespoke bug is proven and explicitly documented
   first (and even then, by a separate sprint).
9. Validators must pass on every commit: pytest, ruff, archive
   validator, freeze checker, secret scanner.
10. No reopening of the QuantConnect / LEAN path.

## 4. Current drift summary (post Sprint 003 Phase 5)

Verifier total: **1,655 trades** vs bespoke **1,647 trades**
(Δ **+0.49 %**, within OK ±5 % tolerance). Overall comparison
status: **WARN**.

| pair | bespoke trades | verifier trades | Δ % | Δ R | Δ pp | status |
|---|---|---|---|---|---|---|
| EUR_USD | 233 | 235 | +0.86 | +0.0160 | +0.7644 | WARN |
| GBP_USD | 215 | 215 | +0.00 | +0.0005 | +0.0075 | **OK** |
| USD_JPY | 247 | 251 | +1.62 | −0.0125 | +0.3093 | **OK** |
| AUD_USD | 237 | 238 | +0.42 | −0.0033 | −0.2241 | **OK** |
| USD_CAD | 251 | 251 | +0.00 | −0.0605 | +0.0025 | WARN |
| USD_CHF | 224 | 223 | −0.45 | +0.0428 | +1.6304 | WARN |
| NZD_USD | 240 | 242 | +0.83 | −0.0077 | −0.5110 | WARN |
| **total** | **1647** | **1655** | **+0.49** | | | **WARN** |

3 pairs OK, 4 pairs WARN, 0 pairs FAIL. The four WARN pairs sit in
different cells of the tolerance ladder:
- **USD_CAD** WARN comes from expectancy ΔR (−0.0605, just past the
  ±0.03 R OK band; return is essentially identical at +0.0025 pp).
- **USD_CHF** WARN comes from return Δpp (+1.6304, in the 0.5–2.0
  pp WARN band).
- **EUR_USD** and **NZD_USD** WARN come from sub-pp return drift
  (in the 0.5–2.0 pp WARN band).
- All four are well below the ±15 % trade-count and ±0.10 R FAIL
  thresholds.

## 5. Candidate causes (to be confirmed at audit)

| candidate | hypothesis |
|---|---|
| Decimal-vs-float | Bespoke uses `decimal.Decimal` for all prices, stops, sizing, and PnL; verifier uses Python `float`. Sub-pip rounding differences accumulate over thousands of bars and many trade-by-trade compounding steps. |
| Missing `round_price` | Bespoke calls `instrument.round_price(stop_or_price)` to truncate at the instrument's display precision before storing. Verifier never rounds. |
| Pip-value / unit math | Verifier uses simple `pip_size / mid_price` for USD-base pairs; bespoke may use a different `mid_price` field (e.g. open or close) or apply Decimal rounding at intermediate steps. |
| PnL exit-price divisor | Bespoke `_pnl` may use `bid_close` (or rounded mid) for the USD-base divide; verifier uses the raw `exit_price`. |
| Trailing-stop ratchet base | Bespoke ratchets off bid_close (long) / ask_close (short). Verifier matches. But Decimal rounding could shift the candidate stop. |
| Trade-count clusters | The +/-1 to +/-4 trade-count drift per pair could be a small number of borderline trades where a sub-pip rounding shifts a stop pierce on a single bar. |

The audit (Phase 1) will inspect each candidate against the
bespoke source code and produce a precision-mismatch table.

## 6. Planned diagnostics

- **Phase 1** — read-only audit of bespoke instrument metadata,
  `round_price`, `size_position`, `_pnl`, fill model, and trailing
  update; produce a mismatch table without changing code.
- **Phase 2** — add fixture tests pinning verifier behavior at the
  audited precision (EUR_USD 5-decimal rounding, USD_JPY 3-decimal
  rounding, USD-base PnL divide).
- **Phase 3** — apply the smallest verifier-side changes needed;
  re-run verifier + comparison; record before/after.
- **Phase 4** — classify any remaining WARN drift precisely:
  first mismatched trade per pair, stop-level drift, entry/exit
  timestamp drift. Decide whether further verifier work is
  worthwhile.

## 7. Expected outputs

| output | path | committed? |
|---|---|---|
| Plan (this doc) | `docs/research/INFRA_FREE_LOCAL_PARITY_VERIFIER_004_PLAN.md` | yes |
| Rounding audit | `docs/research/FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_AUDIT.md` | yes |
| Rounding fixes notes | `docs/research/FREE_LOCAL_PARITY_VERIFIER_004_ROUNDING_FIXES.md` | yes |
| Remaining drift notes | `docs/research/FREE_LOCAL_PARITY_VERIFIER_004_REMAINING_DRIFT.md` | yes |
| Updated STATUS doc | `docs/research/FREE_LOCAL_PARITY_VERIFIER_STATUS.md` | yes |
| Updated COMPARISON doc | `docs/research/FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md` | yes |
| Updated EVIDENCE_INDEX / MANIFEST | `docs/research/EVIDENCE_INDEX.md`, `docs/research/EVIDENCE_MANIFEST.json` | yes |
| Sprint summary | `docs/research/INFRA_FREE_LOCAL_PARITY_VERIFIER_004_SUMMARY.md` | yes |
| Updated verifier code | `research/parity_verifier/*.py` (only if precision fixes are applied) | yes |
| Updated verifier tests | `tests/research/test_parity_verifier_*.py` | yes |
| Verifier run outputs | `research/parity_verifier/results/campaign_002_h4_full_data/` | no — gitignored |

## 8. Explicit statement on approval

Nothing this sprint produces can or does approve a strategy. It does
not edit `configs/approved_strategies.yaml`, the bespoke engine, the
CAMPAIGN_002 rules, the campaign reports, or `EVIDENCE_MANIFEST.json`
campaign verdicts. Its outputs are diagnostic only — every committed
verifier artifact carries `strategy_evidence: false` and the
comparison-report model rejects construction with the rail flipped.

A clean OK across all seven pairs would mean only: "two engines
built from the spec, without sharing code, agree on the numbers for
a rejected strategy". A persistent WARN that survives all reasonable
verifier-side fixes would mean only: "two engines built from the
spec agree on the directional verdict but disagree on small
magnitudes that are most plausibly Decimal-vs-float precision". In
neither case does CAMPAIGN_002 stop being REJECT.
