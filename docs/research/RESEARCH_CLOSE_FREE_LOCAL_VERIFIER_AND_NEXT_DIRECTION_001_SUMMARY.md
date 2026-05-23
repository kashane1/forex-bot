# Research Close Free / Local Verifier and Next Direction 001 — Summary

**Date:** 2026-05-22 · **Branch:** `research-close-free-local-verifier-and-next-direction-001`
**Base commit:** `61501cb` (HEAD of `infra-free-local-parity-verifier-004-rounding-closure`)

Docs-only sprint closing the free / local independent parity
verifier evidence loop and proposing the next research direction
now that CAMPAIGN_002 is independently rejected.

**No code changes. No strategy approved. CAMPAIGN_002 remains
REJECT. Paper / demo / live remain blocked. No QC / LEAN. No OANDA
API calls.**

## 1. Branch name

`research-close-free-local-verifier-and-next-direction-001`.

## 2. Commit hashes by phase

| phase | commit |
|---|---|
| Phase 0 — baseline validation | (no docs changed → no commit, per sprint rule) |
| Phase 1 — accepted-status doc | `7f4837b` |
| Phase 2 — Decimal precision deferred doc | `c4500ab` |
| Phase 3 — next-research-direction plan | `0506471` |
| Phase 4 — final validation & summary | (this commit) |

## 3. Files changed by phase

| phase | files |
|---|---|
| Phase 0 | — (no doc changes) |
| Phase 1 | `docs/research/FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md` (new); `docs/research/FREE_LOCAL_PARITY_VERIFIER_STATUS.md` (ACCEPTED banner); `docs/research/EVIDENCE_INDEX.md`; `docs/research/EVIDENCE_MANIFEST.json` (+1 diagnostic_artifacts entry) |
| Phase 2 | `docs/research/FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md` (new); `docs/research/EVIDENCE_INDEX.md` |
| Phase 3 | `docs/research/NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md` (new); `docs/research/EVIDENCE_INDEX.md` |
| Phase 4 | `docs/research/RESEARCH_CLOSE_FREE_LOCAL_VERIFIER_AND_NEXT_DIRECTION_001_SUMMARY.md` (new) |

No code under `src/`, `tests/`, `scripts/`, or
`research/parity_verifier/` was modified. No campaign config,
campaign report, or `configs/approved_strategies.yaml` was touched.

## 4. Validation commands run

- `python -m pytest -q` → **481 passed** (unchanged from Sprint 004).
- `ruff check src tests scripts research/parity_verifier` → **clean**.
- `python scripts/validate_research_archive.py` → **ALL CHECKS PASSED**
  (13 diagnostic artifacts; 94 evidence-index links resolve; no
  credential-shaped strings in 1,936 committed artifact files).
- `python scripts/check_research_freeze.py` → **ALL CHECKS PASSED**
  (paper-loop + demo-loop both refuse `['trend_following']` —
  frozen).
- `python scripts/scan_artifacts_for_secrets.py` → **PASSED**.
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml` →
  **refused**.
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml` →
  **refused**.
- `python -m forex_bot.cli --help` → no `live-loop` command.

## 5. Accepted verifier status

The free / local independent parity verifier is **ACCEPTED as
WARN-band corroborating evidence** for the bespoke backtest engine
on CAMPAIGN_002 H4 `trend_following 0.1.0`:

| metric | value |
|---|---|
| Verifier total trades | 1,655 |
| Bespoke (no-RiskEngine) total trades | 1,647 |
| Total Δ % | +0.49 % (OK band) |
| Pairs OK / WARN / FAIL | 3 / 4 / 0 |
| Overall comparison status | **WARN** |
| Verifier-side bugs fixed (4 sprints) | 2 (both Sprint 003) |
| Bespoke-engine bugs found | **0** |

Both engines agree every CAMPAIGN_002 H4 pair is loss-making on the
no-RiskEngine path. CAMPAIGN_002 stays REJECT under either
measurement. Closeout reference:
[`FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md).

## 6. Why Decimal precision work is deferred

The remaining WARN drift on 4 / 7 pairs is localized to
float-vs-Decimal arithmetic precision (USD_CAD is the cleanest
evidence: identical trade count + identical return % but −0.06 R
expectancy drift = R-denominator float precision). A Decimal
end-to-end rewrite would close it but is **explicitly deferred**
for three reasons:

1. **Diminishing returns vs research goals** — tightening WARN to
   OK doesn't change CAMPAIGN_002's REJECT status.
2. **Loss of verifier independence** — two engines using the same
   numerical-precision context that agree exactly is *weaker*
   corroboration than two engines using different contexts agreeing
   on the directional verdict.
3. **Opportunity cost** — same time invested in the next-research
   candidates buys more knowledge.

Four conditions that would justify reopening are documented:
[`FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md`](FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md)
§5.

## 7. Strategy approval

**No strategy is approved.** `configs/approved_strategies.yaml`
remains `approved: []`. The verifier corroborated a REJECTION; it
did not approve a winner.

## 8. CAMPAIGN_002

**Remains REJECT.** Both engines agree.

## 9. Paper / demo / live

**All remain blocked.** Both `paper-loop` and `demo-loop` refused
at final validation; no `live-loop` command exists.

## 10. Recommended next research branch

**`research-walk-forward-harness-001`** (corresponds to §5.2 of
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)).

Rationale:
- **Infrastructure, not a signal** → low overfitting risk.
- **Strictly enabling** → every future strategy candidate becomes
  more credible if it survives walk-forward.
- **Re-validates existing REJECTs** → re-running CAMPAIGN_002 under
  walk-forward will confirm or refine the rejection; either is
  informative.
- **Compatible with the research freeze** → the harness ships
  empty by default and can only be invoked by deliberate human
  decision per campaign.
- **No new external dependency** → bespoke engine + free / local
  verifier already provide everything required.

A reasonable runner-up (which could be pursued in parallel since
neither blocks the other): **`research-financing-model-001`** (§5.4
of the next-direction doc) — required prerequisite before any
candidate strategy can be promoted to paper.

## 11. Exact files to review first

1. [`FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md)
   — single closeout reference for the verifier evidence loop.
2. [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
   — seven candidate next paths with overfitting risk + work
   scope; recommended next branch; success criteria + required
   evidence package for any future candidate.
3. [`FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md`](FREE_LOCAL_PARITY_VERIFIER_DECIMAL_PRECISION_DEFERRED.md)
   — explicit deferral of the Decimal rewrite with conditions for
   reopening.
4. [`FREE_LOCAL_PARITY_VERIFIER_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_STATUS.md)
   — historical status thread with the new ACCEPTED banner at the
   top pointing at the closeout doc.
5. [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) — refreshed index
   showing the closeout, deferral, and next-direction docs under
   the verifier section.
6. This summary
   ([`RESEARCH_CLOSE_FREE_LOCAL_VERIFIER_AND_NEXT_DIRECTION_001_SUMMARY.md`](RESEARCH_CLOSE_FREE_LOCAL_VERIFIER_AND_NEXT_DIRECTION_001_SUMMARY.md)).
