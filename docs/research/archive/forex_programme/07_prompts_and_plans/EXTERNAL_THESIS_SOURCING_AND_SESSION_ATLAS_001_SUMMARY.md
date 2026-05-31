# External Thesis Sourcing & Session Atlas 001 — Summary

**Sprint:** `external-thesis-sourcing-and-session-atlas-001`
**Branch:** `research-external-thesis-sourcing-and-session-atlas-001` (fresh from
`origin/main` @ `018c0aa`)
**Date:** 2026-05-28
**Outcome:** research/diagnostic only. **No campaign, no C024, no C023 execution, no
strategy, no verdict change, no approval, paper/demo/live still blocked.**

---

## 1. What this sprint did

Changed search direction away from internal indicator-confluence variants (the retired
C022/C023 family) toward **externally-sourced, structurally-distinct theses**, screened
on paper against a 10-criterion framework, and grounded in a **read-only USD_JPY
session/volatility/spread atlas** built from materialized research-DB candles. Then
scored ten candidate theses against the atlas and selected the single most plausible one
to carry forward — into a *diagnostic*, not a campaign.

## 2. Commit hashes by phase

| phase | hash | what |
|---|---|---|
| 0 | `a13741e` | branch, audit, baseline, plan doc |
| 1 | `b29bc64` | external FX thesis sourcing framework |
| 2 | `51a701f` | USD_JPY session/vol/spread atlas (script + summary + doc) |
| 3 | `04071c7` | candidate thesis scorecard |
| 4 | `87da1be` | decision: MORE_DIAGNOSTICS_REQUIRED |
| 5 | `05820f8` | next-sprint diagnostic prompt |
| 6 | (this commit) | final validation + summary |

## 3. Files changed by phase

- **0:** `docs/research/EXTERNAL_THESIS_SOURCING_AND_SESSION_ATLAS_001_PLAN.md`
- **1:** `docs/research/EXTERNAL_FX_THESIS_SOURCING_FRAMEWORK.md`
- **2:** `scripts/build_usdjpy_session_volatility_spread_atlas.py`,
  `research/usdjpy_session_atlas/usdjpy_session_atlas_summary.json`,
  `docs/research/USDJPY_SESSION_VOLATILITY_SPREAD_ATLAS.md`, `.gitignore`
- **3:** `docs/research/USDJPY_EXTERNAL_THESIS_CANDIDATE_SCORECARD.md`
- **4:** `docs/research/NEXT_THESIS_AFTER_EXTERNAL_SOURCING_AND_ATLAS.md`
- **5:** `docs/research/NEXT_SPRINT_PROMPT_AFTER_EXTERNAL_THESIS_AND_SESSION_ATLAS.md`
- **6:** `docs/research/EXTERNAL_THESIS_SOURCING_AND_SESSION_ATLAS_001_SUMMARY.md`

Total: 9 files, docs/research + scripts + research/ + .gitignore only. **No** changes to
`src/`, broker/executor/order/live code, or `configs/approved_strategies.yaml`.

## 4. Local data availability (read-only research Postgres `market_data.candles`)

USD_JPY, full spread coverage (`spread_*` non-null on every row):

| gran | rows | min | max |
|---|---|---|---|
| M1 | 1,844,454 | 2021-05-26 | 2026-05-26 |
| M5 | 362,519 | 2021-05-26 | 2026-05-26 |
| M15 | 118,035 | 2021-05-26 | 2026-05-26 |
| H1 | 28,013 | 2021-05-26 | 2026-05-26 |
| H4 | 9,959 | 2020-01-01 | 2026-05-26 |
| H4M1 | 5,448 | 2021-05-26 | 2026-05-26 |

Columns: bid/ask OHLC, mid OHLC, spread OHLC, volume, complete. (sqlite DBs hold H1/H4/D
only; M1/M5/M15 are Postgres-only.) `.env` symlink used **only** for research-DB access;
credentials never printed.

## 5. Atlas coverage

95,756 completed M15 bars over **2021-06-01 .. 2025-06-29** (train 59,852 / validation
35,904); M1 spread cross-check over ~1.5M M1 bars (server-side aggregation). **TEST window
2025-07-01+ excluded (sealed lockbox).** Dimensions: session, NY-hour, UTC-hour, weekday,
volatility regime × spread / volatility / directional / tradability metrics.

## 6. Most important USD_JPY findings (descriptive, NOT edge)

1. **Spread/cost (robust, M1-confirmed):** ~1.6–1.7 pip median in Tokyo/London/NY/overlap;
   **rollover (17:00 ET) is cost-toxic** (median 4.7–5.0 pip, p90/p95 = 10 pip, spread/ATR
   ≈ 0.5); off-hours mildly elevated.
2. **Volatility timing (predictable):** range/ATR peak **NY 08:00–11:00** (London open →
   overlap), range-expansion prob 0.72–0.79; secondary bump at Tokyo open NY 02:00–04:00;
   trough NY 14:00–18:00. Expansion prob rises monotonically low→mid→high vol
   (0.29→0.50→0.71).
3. **Direction (central null):** trend-continuation ≈ mean-reversion ≈ **0.49 everywhere**
   — across all sessions, hours, and vol regimes. Forward-return means are sub-spread. The
   mild long tilt is a likely 2021–2024 uptrend artifact.
4. **Breakouts:** 72–80% of 4h-range breakouts fail (close back inside within 2h), but
   MFE:MAE after arbitrary entries is < 1.0 — fading is *not* free.
5. **Weekday:** essentially flat.

## 7. Candidate theses scored (10)

REJECT #2 NY-continuation (atlas null on direction; inside retired family). BLOCKED #7
macro-calendar & #8 carry/rates (missing overlay data). ADOPT #9 cost/spread filter as a
standing overlay (not a strategy). **TOP CANDIDATE #5** volatility-compression→expansion
(distinct, atlas-supported on the volatility leg, low-parameter). HOLD #1 Tokyo→London
break/fakeout, #3 prev-session sweep, #4 ORB, #6 intraday-extension reversion
(overfit-prone). #10 pause = fallback.

## 8. Selected next thesis / decision

**Classification: `MORE_DIAGNOSTICS_REQUIRED`.** Single carried-forward thesis = **#5
intraday volatility-compression → range-expansion (USD_JPY, M15)**. Not yet
precommit-ready because the atlas supports its volatility leg but is silent on
monetization/direction. Next step is a precommitted, read-only diagnostic with three
cost-net monetizations and kill criteria that flip to `PAUSE_STRATEGY_RESEARCH` on a null
(see Phase 5 prompt). #9 cost filter adopted as a standing overlay.

## 9–13. Invariants (verified Phase 6)

| check | expected | actual |
|---|---|---|
| 9. C023 executed? | no | **no** (only plan/scaffold/precommit exist; no result/gate/train artifacts) |
| 10. C024 created? | no | **no** (no `CAMPAIGN_024*` artifact or config; only forward-looking mentions) |
| 11. Any verdict changed? | no | **no** (`validate_research_archive` PASS; all verdicts non-approval) |
| 12. Any strategy approved? | no | **no** (`configs/approved_strategies.yaml` = `approved: []`) |
| 13. Paper/demo/live blocked? | yes | **yes** (freeze gate: paper/demo loops refuse, frozen) |

## 14. Tests & validation commands run

- `pytest tests/ -q` → **1996 passed, 3 skipped** (Phase 0 baseline + Phase 6 final).
- `ruff check src tests scripts research` → **All checks passed.**
- `python scripts/check_research_freeze.py` → **ALL CHECKS PASSED.**
- `python scripts/validate_research_archive.py` → **ALL CHECKS PASSED.**
- `python scripts/scan_artifacts_for_secrets.py` → **PASSED** (pattern scan; and the
  value scan **PASSED** with `.env` loaded — no credential values found).
- `git status --short` → clean (all changes committed).

## 15. Pre-existing skips/failures

3 skips, all pre-existing data-absence (unchanged by this sprint):
`tests/research/test_cost_atlas.py` (local H4 store absent); 2×
`tests/unit/entry_parity/test_compare_entries.py` (C008 bespoke CSVs absent, gitignored).
No failures.

## 16. Remaining blockers

- Thesis #5 monetization is unproven → gated behind the Phase-5 diagnostic.
- Theses #7 (macro calendar) and #8 (carry/rates/risk-off) are blocked on missing
  maintained overlay data (economic-calendar table; timeline-aligned rates/risk feature).
  Recorded as infrastructure backlog; not started.
- No strategy is approved; nothing is paper/demo/live-eligible.

## 17. Exact files to review first

1. `docs/research/NEXT_THESIS_AFTER_EXTERNAL_SOURCING_AND_ATLAS.md` (the decision)
2. `docs/research/USDJPY_SESSION_VOLATILITY_SPREAD_ATLAS.md` (the evidence)
3. `docs/research/USDJPY_EXTERNAL_THESIS_CANDIDATE_SCORECARD.md` (the scoring)
4. `scripts/build_usdjpy_session_volatility_spread_atlas.py` (the read-only tooling)
5. `docs/research/NEXT_SPRINT_PROMPT_AFTER_EXTERNAL_THESIS_AND_SESSION_ATLAS.md` (next step)

## 18. Recommended next sprint

`research-usdjpy-volatility-compression-expansion-diagnostic-001` — a read-only,
precommitted diagnostic (NOT a campaign, NOT C024, NOT a precommit-design) that tests
whether the compression→expansion state yields a cost-surviving trade structure on
train+validation, with kill criteria that retire the thesis (→ `PAUSE_STRATEGY_RESEARCH`)
on a null. Full prompt drafted in the Phase-5 document.
