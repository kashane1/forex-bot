# Future Exit Research Gate

**Date:** 2026-05-26  
**Branch:** `research-stop-and-exit-diagnostics-001`

> **Diagnostic only** — `strategy_evidence: false`. Does not authorize work. Broad strategy search remains **paused**. No strategy approved.

Complements [`FUTURE_MEAN_REVERSION_RESEARCH_GATE.md`](FUTURE_MEAN_REVERSION_RESEARCH_GATE.md) with **exit-specific** requirements derived from stop/exit diagnostics sprint 001.

---

## 1. No old campaign revival

- **C008, C009, and all prior REJECT campaigns** cannot be re-run as promotion candidates.
- Forensic replays may use **dedup-safe engine** with `strategy_evidence: false` only — see infra dedup rerun sprint.
- Exit changes on frozen C008 entries require a **new campaign ID** and new precommit.

## 2. New campaign identity and precommit

- Assign **new CAMPAIGN_0XX** before any backtest bar.
- Precommit must enumerate: frozen **entries**, frozen **exit rule(s)**, splits, gates, null benchmark, financing treatment.
- Commit precommit **before** first run.

## 3. Entries frozen before exit testing

- Entry signal, filters, and sizing logic **locked** in precommit.
- Exit campaigns may **not** change entry thresholds, pair universe, or session filters unless the bundle is pre-registered as entry+exit co-design (discouraged).

## 4. Exit rules selected before fold results

- Exactly **one exit change** per campaign vs a declared baseline — unless a **bundle** (e.g. partial + runner) is pre-registered in writing.
- Forbidden: iterating exit rules after seeing validation expectancy.

## 5. Test lockbox

- Test window (2025–2026) remains **closed** until train + validation gates pass on dedup-safe evidence.
- Stop/exit diagnostics do **not** open the lockbox.

## 6. Financing

- Required when median hold crosses **≥ 24h** or time-stop ≥ 6 H4 bars with overnight exposure.
- C008 40-bar holds **require** financing model before any exit variant is compared fairly.
- Unmodeled financing is a **blocker** for carry-sensitive exit interpretation.

## 7. Cost atlas and FRED features

- Cost atlas joins **required** for diagnostics on all exit campaigns.
- FRED cross-asset features **included** in explanatory diagnostics; causal gating only if pre-registered.
- 2× cost stress on screening window where precommit requires.

## 8. Confluence

- Confluence grade/reason may be **explanatory only** unless pre-registered as an entry/exit gate.
- No tuning grader weights from C008/C009 exit forensics.

## 9. Sizing

- Sizing overlays **cannot** rescue negative expectancy exits.
- Exit research uses fixed sizing unless sizing is the explicit pre-registered variable (separate sprint).

## 10. Beat-null

- Must beat **CAMPAIGN_011 deduped** random-entry anchor (or documented successor) on declared splits.
- WITHIN_NULL = automatic REJECT.

## 11. Engine integrity

- Prefer **dedup-safe** backtest path for any new exit campaign.
- C008/C009 **LIKELY_CONTAMINATED** artifacts are not sufficient for promotion decisions.
- Backtrader parity required where precommit states it.

## 12. Minimum trade count

- Validation ≥ **30 trades** (repo standard).
- Per exit-reason bucket: ≥ **15** or collapse buckets in analysis.

## 13. No paper/demo/live

- Exit research does **not** enable paper-loop, demo-loop, or live execution.
- Separate **promotion sprint** required after all gates pass.

## 14. Documentation and evidence flags

- All exit diagnostic artifacts: `strategy_evidence: false`, `diagnostic_only: true`.
- Human-review memo required before any future approval sprint.

## 15. Relationship to mean-reversion gate

- Any future **mean-reversion** campaign must satisfy **both** this exit gate and [`FUTURE_MEAN_REVERSION_RESEARCH_GATE.md`](FUTURE_MEAN_REVERSION_RESEARCH_GATE.md).
- Exit-only campaigns on non-MR entries must still satisfy sections 1–13 above.

---

## Allowed hypothesis catalog

See [`FUTURE_EXIT_RESEARCH_HYPOTHESES.md`](FUTURE_EXIT_RESEARCH_HYPOTHESES.md) section A.

## Forbidden without new thesis

See [`FUTURE_EXIT_RESEARCH_HYPOTHESES.md`](FUTURE_EXIT_RESEARCH_HYPOTHESES.md) section B.
