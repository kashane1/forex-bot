# FX Futures Carry Diagnostic — SUMMARY (Phase 8)

**Sprint:** `research-fx-futures-carry-diagnostic-001`
**Type:** Decision-forcing diagnostic / factor evaluation. The first code-bearing futures sprint.
**Status:** COMPLETE.
**Date:** 2026-05-31
**Freeze:** intact. Paper/demo/live remain blocked.

---

## What this sprint did

Built the minimal additive FX-futures data layer, ingested real CME FX-futures history, and ran the **frozen** carry factor on futures price returns to resolve the programme's final open question: *was spot carry merely financing-defeated, or genuinely non-predictive?* No strategy, campaign, front gate, or train/validation/test was created.

---

## Verdict: `CARRY_DOES_NOT_SURVIVE_IN_FUTURES`

The frozen carry factor on real CME FX-futures price returns is **statistically zero in the matched 5-year window** (primary 3-month cell **+0.000426, ≈+0.04 %/qtr, NW-HAC t = +0.09**), **indistinguishable from every matched null** (Z +0.21 / −0.09 / +0.15; Holm rejects nothing), and **negative & below every null over 24 years ex-JPY** (h3 −0.0041, t = −1.65; null Z ≈ −3). **Carry is genuinely non-predictive**, confirming the venue study's prior. Triggers the pre-committed **Option E — archive the strategy search.**

---

## Commit hashes by phase (verified against `git log`)

| Phase | Hash | Content |
|-------|------|---------|
| 0 | `8d403fe` | baseline audit plan |
| 1 | `67e4462` | futures infrastructure (registry, ingest, continuous, diagnostic) |
| 2 (reconciliation) | `1f32190` | canonical data artifacts (raw CSVs+provenance, coverage, primary) + reproducibility caveat |
| 1 (completion) | `7d59ea7` | ruff-clean infra + impl doc + plan corrections (certifi SSL, noqa, strict zip) |
| 2 (deep data) | `9a8f243` | deep ex-JPY run (FRED rates, 304 mo) + corrected data-validation |
| 3–7 | `9650b7a` | result, null comparison, verdict, programme implication, next prompt |
| 8 | *(this commit)* | validation + summary |

> Commit-ordering note: the phase commits did not land in tidy numeric order because of a tooling problem during the run (see §9). The history is non-linear but every artifact is committed and consistent; the table above is the true mapping.

---

## 1. Futures data source used

Yahoo Finance chart v8 (key-less public), continuous front-month `=F`, EOD daily, SSL via the `certifi` CA bundle (system trust store rejected the chain). Seven full-size CME FX futures: 6E/6B/6J/6S/6A/6C/6N. FRED OECD 3M interbank CSV (key-less) for the deep-history signal.

## 2. Coverage obtained

- Raw committed snapshot: 7 contracts, ~6.4k daily rows each, all ending 2026-05-29; provenance + sha256.
- PRIMARY monthly matrix: **305 months, 2001-01 → 2026-05, 0 missing** (~25 y vs spot's ~6.4 y).
- DEEP signal: FRED ex-JPY (JPY series retired/404), **304 months, 2001-01 → 2026-04, 6 currencies**.
- **6J verified unscaled** (true ~0.006–0.007 USD/JPY) — the ×100 hazard does not apply. Native USD-per-foreign-currency ⇒ **no inversion** needed.
- **Reproducibility caveat:** Yahoo `=F` absolute levels/start vary across fetches (vendor roll re-anchor); the **return-based diagnostic is reproducible from the committed CSVs** (offline re-run reproduces `primary.json` byte-for-byte).

## 3. Carry diagnostic findings (futures price return = spot-predictive component)

PRIMARY (incl-JPY, 2021-05 → 2026-05, rank stability 0.984):

| Horizon | Mean | NW-t | Sign | n |
|--------:|-----:|-----:|-----:|--:|
| 1 m | +0.000291 | +0.16 | 0.610 | 59 |
| **3 m** | **+0.000426** | **+0.09** | 0.596 | 57 |
| 6 m | +0.000071 | +0.01 | 0.574 | 54 |
| 12 m | −0.003444 | −0.29 | 0.458 | 48 |

DEEP (ex-JPY, 2001-01 → 2026-04): h3 **−0.0041, t = −1.65** (negative, |t| < 2); all horizons negative.

Statistically zero (primary) / negative (deep); sign ~0.5; drop-JPY flips primary to −0.0047 (JPY-concentrated). Spot total was **+0.74 %/qtr** (accrual-driven); futures total (no accrual) is **+0.04 %/qtr, t = 0.09** — matching the spot study's spot-predictive leg (≈0, t = 0.10). The accrual *was* the premium; no predictive residual underneath.

## 4. Null-comparison findings

PRIMARY h3 (observed +0.000426): randomized-ranks Z **+0.21** (p 0.42), shuffled-timestamp Z **−0.09** (p 0.54), matched-random Z **+0.15** (p 0.43); **Holm rejects nothing**; unconditional baseline −0.0046. DEEP h3: carry **below every null** (Z ≈ −2.98 / −2.83 / −3.00, p ≈ 0.998) and below the **positive** unconditional baseline (+0.0028). Beats **no** null in either window.

## 5. Final verdict

`CARRY_DOES_NOT_SURVIVE_IN_FUTURES` — binary, decision-forcing, no middle option.

## 6. Programme implication

Carry was the last high-information experiment; futures was the pre-committed venue that removes the financing wall. The null result converts the programme's root cause from "cost-defeated (maybe fixable)" to **"idea-quality / market-efficiency is the binding limit."** With C1 (failed replication), S2 (rejected), S4 (economically insignificant), and now carry (non-predictive in futures), **no remaining mechanism both reachable with available data and able to attack the binding constraint exists.** → **Archive the strategy search (Option E).**

## 7. Validation results (Phase 8)

| Check | Result |
|-------|--------|
| `pytest tests/ -q` | **2460 passed** (incl. 6 new) |
| `ruff check src scripts tests` | pre-existing repo errors only; **new fx_futures/scripts/tests code is ruff-clean** |
| `ruff check research/fx_futures` | All checks passed |
| `check_research_freeze.py` | ALL CHECKS PASSED |
| `validate_research_archive.py` | ALL CHECKS PASSED |
| `scan_artifacts_for_secrets.py` | PASSED |
| `git status --short` | clean |

## 8. Compliance ledger

- **Campaign created?** No (no CAMPAIGN_032; none).
- **Strategy approved?** No. `approved: []`.
- **Entry/exit or trading logic?** No.
- **Carry definition altered / thresholds retuned / rejected factor reopened?** No (reused `research/carry/carry_factor.py` unmodified).
- **Paper/demo/live?** Still blocked.
- **Freeze?** Intact. **Credentials committed?** No (key-less endpoints).

## 9. Integrity note (disclosed in full, not hidden)

This sprint hit a sustained **tool-channel reliability problem** (intermittent truncation/duplication of command output, and parallel-batch cancellations that silently dropped queued `git add`/`commit` calls). It caused, and I corrected, the following:

1. **Placeholder coverage numbers** in an early Phase-0 plan draft (unverified start dates written while SSL was failing). Corrected against real artifacts; visible note left in the plan.
2. **A first Phase-8 summary commit (since reset away) contained fabricated commit hashes and a false "deep run not obtained" claim.** Root cause: phase commits 3–7 had been silently dropped by batch-cancellation, and I wrote the summary from an incorrect mental model instead of from `git log`. **Remediation:** soft-reset that commit, re-ran the diagnostic offline from committed data, **generated the result/null docs directly from the source-of-truth JSON via a script** (so numbers are not eye-transcribed through the noisy channel), wrote the remaining docs, and re-committed every phase with hashes verified against `git log` (§ table above).
3. **Yahoo `=F` non-determinism** across fetches (absolute levels/start) — investigated and documented (`FX_FUTURES_DATA_VALIDATION.md` §0); the **return-based result is reproducible from the committed CSVs** (offline re-run reproduces `primary.json` byte-for-byte), so the verdict is unaffected.

All numbers in the result/null/verdict docs are emitted from the committed `primary.json` / `deep.json`. The scientific conclusion was stable across every run.

## 10. Recommended next sprint

`research-forex-strategy-search-archive-001` — docs-only closeout: programme post-mortem, restart criteria, platform freeze. Full prompt in `NEXT_PROMPT_AFTER_FX_FUTURES_CARRY_DIAGNOSTIC.md`.

## 11. Files to review first

1. [FX_FUTURES_CARRY_VERDICT.md](FX_FUTURES_CARRY_VERDICT.md) — the binary call and why.
2. [FX_FUTURES_CARRY_DIAGNOSTIC_RESULT.md](FX_FUTURES_CARRY_DIAGNOSTIC_RESULT.md) — spot-vs-futures comparison (primary + deep).
3. [FX_FUTURES_CARRY_NULL_COMPARISON.md](FX_FUTURES_CARRY_NULL_COMPARISON.md) — null battery.
4. [FX_FUTURES_CARRY_PROGRAMME_IMPLICATION.md](FX_FUTURES_CARRY_PROGRAMME_IMPLICATION.md) — archive decision.
5. [FX_FUTURES_DATA_VALIDATION.md](FX_FUTURES_DATA_VALIDATION.md) — data provenance + reproducibility caveat.
6. [NEXT_PROMPT_AFTER_FX_FUTURES_CARRY_DIAGNOSTIC.md](NEXT_PROMPT_AFTER_FX_FUTURES_CARRY_DIAGNOSTIC.md) — the next prompt.
