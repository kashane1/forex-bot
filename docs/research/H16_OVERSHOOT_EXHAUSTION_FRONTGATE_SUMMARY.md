# H16 overshoot-exhaustion fade — front-gate screen SUMMARY

**Branch:** `research-non-time-bar-overshoot-frontgate-001`
**Type:** front-gate **screen** (not a campaign / evidence / train-val-test).
**Date:** 2026-05-29. **Verdict:** **`FAIL_FRONT_GATE`.**

---

## 1. Commit hashes by phase

| phase | hash | deliverable |
|---|---|---|
| 0 | `b05e991` | front-gate screen plan |
| 1 | `bdd7919` | precise hypothesis |
| 2 | `bd9cd4d` | harness + tests + distribution study |
| 3 | `4a7d794` | post-overshoot behaviour study |
| 4 | `92eecf8` | cost-feasibility study |
| 5 | `2beaed6` | null comparison |
| 6 | `3e052b8` | verdict (FAIL_FRONT_GATE) |
| 7 | `1dcab57` | next prompt (drafted) |
| 8 | this doc | validation + summary |

Stacked on the unmerged thesis-discovery tip `5cb9bd6`.

## 2. Files changed

19 files, +2,718 lines: 10 docs; 1 pure module
(`src/forex_bot/research/overshoot_exhaustion_screen.py`); 1 driver
(`scripts/screen_h16_overshoot_exhaustion.py`); 1 test file (11 tests); `.gitignore`
block; and 6 compact diagnostics under `research/h16_overshoot_frontgate/`. **No
strategy code, executor, or config touched.**

## 3. Overshoot distribution findings
Large overshoots are a **rare right tail** (median completion overshoots its 30-pip
threshold by only ~1.2–1.7 p; top-5% by ≥ 9–16 p), **mildly clustered** (autocorr
0.07–0.19), **concentrated in rollover/overlap** sessions, and — adverse for the thesis
— the **extreme bucket carries ~30–50% wider spreads** than the small bucket (cost is
worst exactly where overshoot is biggest).

## 4. Post-overshoot behaviour findings
**No exhaustion effect.** No bucket gradient (EUR small bucket fades *more* than
extreme; GBP/JPY extreme ≈ 0 or negative), **reversion rate ≈ 0.50** on every
pair/horizon (coin-flip), every extreme-bucket mean fade **within ~1 SEM of zero**,
signs inconsistent across pairs/horizons, and the **top-5% tail leans to continuation**
(opposite of the thesis) at h1 on EUR/GBP.

## 5. Cost-feasibility findings
The conditional fade move **never exceeds round-trip cost** (2.0–2.65 p) on any
pair/horizon (`exceeds_cost` flag all False), and the relevant cost is actually higher
because large overshoots arrive with wider spreads in expensive sessions. Same
structural cost-defeat as C029/C026/C031.

## 6. Null comparison findings
The extreme bucket **underperforms the unconditional baseline** on all 3 pairs at h1;
in **8/9** shuffle-null cells the observed mean sits **inside** the null. The single
borderline cell (GBP h3, pct_rank 0.91) is not < 0.05, is cost-defeated, single-pair,
and inconsistent across pairs → multiple-comparison noise (C028 lesson). **Overshoot
carries no usable conditional information.**

## 7. Front-gate verdict: **`FAIL_FRONT_GATE`**
All three FAIL criteria met independently (no effect; cost-defeated;
null-indistinguishable). Not INCONCLUSIVE (ample sample positively supports "no
effect"); not PASS (no surviving effect). **H16 is abandoned.**

## 8. Was a campaign created? **No.** (No CAMPAIGN_030; no scaffold.)
## 9. Was any strategy approved? **No.** `configs/approved_strategies.yaml` = `approved: []`.
## 10. Do paper/demo/live remain blocked? **Yes** — loops refuse; freeze intact.

## 11. Validation (Phase 8, all green)
- `pytest tests/ -q` → **2351 passed, 3 skipped** (2340 + 11 new screen tests).
- `ruff check src scripts tests` → passed.
- `check_research_freeze.py` / `validate_research_archive.py` /
  `scan_artifacts_for_secrets.py` → all PASSED.
- `git status --short` → clean.

## 12. Recommended next step
**Abandon H16.** Then (drafted in
[`NEXT_PROMPT_AFTER_H16_FRONTGATE.md`](NEXT_PROMPT_AFTER_H16_FRONTGATE.md)) either run
the **one pre-registered fallback screen — H03 thin-move fade** (reuses this harness,
buckets by tick-volume), or, if you prefer to stop, the **docs-only closeout** that
retires directional non-time-bar search on this corpus. **If H03 also fails, retire**
(reopen only with new data: ≥ 10–15y history, non-USD crosses, or true tick data).

## 13. Files to review first
1. [`H16_FRONTGATE_DECISION.md`](H16_FRONTGATE_DECISION.md) — the verdict + criteria map.
2. [`H16_POST_OVERSHOOT_BEHAVIOR_STUDY.md`](H16_POST_OVERSHOOT_BEHAVIOR_STUDY.md) — the core no-effect result.
3. [`H16_NULL_COMPARISON.md`](H16_NULL_COMPARISON.md) — null/selection-noise treatment.
4. [`H16_COST_FEASIBILITY_STUDY.md`](H16_COST_FEASIBILITY_STUDY.md) + [`H16_OVERSHOOT_DISTRIBUTION_STUDY.md`](H16_OVERSHOOT_DISTRIBUTION_STUDY.md).
5. [`research/h16_overshoot_frontgate/h16_screen_matrix.csv`](../../research/h16_overshoot_frontgate/h16_screen_matrix.csv) — the compact result matrix.

## 14. Did this sprint succeed?
**Yes.** A successful screen does not find a strategy — it decides whether H16 deserves
a campaign. It cleanly determined **it does not**, on ample data, with cost and null
discipline, creating no campaign and approving nothing. The freeze is intact.
