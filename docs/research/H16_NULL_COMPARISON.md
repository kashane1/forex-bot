# H16 — null comparison (Phase 5)

**Sprint:** `research-non-time-bar-overshoot-frontgate-001` · Phase 5
**Artifacts:** [`null_study.json`](../../research/h16_overshoot_frontgate/null_study.json),
[`behavior_study.json`](../../research/h16_overshoot_frontgate/behavior_study.json).

> Two null comparisons: (a) the **unconditional** next-bar fade (does overshoot
> conditioning beat doing nothing?), and (b) a **seeded permutation/shuffle null**
> (2,000 draws) that breaks the overshoot↔forward-return link and asks where the
> observed extreme-bucket mean sits in the resulting distribution.

---

## 1. Conditional vs unconditional (does the overshoot bucket add information?)

At h1, the extreme-bucket mean fade is **not** systematically above the unconditional
mean:

| pair | extreme-bucket mean (h1) | unconditional mean (h1) | extreme beats unconditional? |
|---|---:|---:|:--:|
| EUR_USD | +0.60 | +1.22 | No (below) |
| GBP_USD | −0.20 | +0.49 | No (below) |
| USD_JPY | −0.39 | −0.21 | No (below) |

On all three pairs the **extreme bucket underperforms the unconditional baseline** at
h1 — conditioning on large overshoot makes the (already ≈ zero) fade *worse*, not
better.

## 2. Permutation (shuffle) null — extreme-bucket mean fade

`one_sided_p_ge` = fraction of shuffled draws with mean ≥ observed (small ⇒ observed
unusually high); `pct_rank` = fraction of draws ≤ observed.

| pair | horizon | observed | null mean | null p95 | p(null ≥ obs) | pct_rank |
|---|---:|---:|---:|---:|---:|---:|
| EUR_USD | 1 | +0.60 | +1.20 | +3.07 | 0.69 | 0.31 |
| EUR_USD | 2 | +0.38 | +1.18 | +3.99 | 0.68 | 0.32 |
| EUR_USD | 3 | +1.09 | +1.28 | +4.48 | 0.55 | 0.45 |
| GBP_USD | 1 | −0.20 | +0.48 | +1.92 | 0.78 | 0.22 |
| GBP_USD | 2 | +2.02 | +0.84 | +2.86 | 0.17 | 0.83 |
| GBP_USD | 3 | +2.34 | +0.24 | +2.74 | 0.086 | 0.91 |
| USD_JPY | 1 | −0.39 | −0.21 | +1.20 | 0.59 | 0.41 |
| USD_JPY | 2 | +1.03 | +0.40 | +2.35 | 0.31 | 0.69 |
| USD_JPY | 3 | −0.66 | +0.15 | +2.66 | 0.71 | 0.29 |

## 3. Interpretation

- **Overshoots contain no information beyond random variation.** In **8 of 9** cells the
  observed extreme-bucket mean sits **comfortably inside** the shuffle null (pct_rank
  0.22–0.83; p(null ≥ obs) 0.17–0.78) — i.e. indistinguishable from randomly relabelling
  which bars are "extreme".
- The **single** cell that approaches significance — GBP_USD h3, pct_rank 0.91, p(null ≥
  obs) 0.086 — is **not** below 0.05, is **cost-defeated** (+2.34 < 2.65-pip cost), is a
  **single pair at the longest horizon**, and is **inconsistent** with USD_JPY h3
  (−0.66) and EUR_USD h3 (+1.09, inside null). Across **9 cells examined**, one at
  pct_rank ~0.91 is exactly what chance produces — the multiple-comparison / selection-
  noise discipline (the C028 lesson) says this is **noise, not signal**.
- Combined with §1 (extreme bucket *below* unconditional on every pair), the conclusion
  is unambiguous: **overshoot magnitude carries no usable conditional information** about
  subsequent direction.

## 4. Verdict contribution

H16 hits the **null-indistinguishable** falsifier (#4): the conditional effect is inside
both the unconditional baseline and the shuffle null. Together with the absent gradient
(Phase 3) and cost-defeat (Phase 4), the screen has met **four** independent FAIL
criteria.
