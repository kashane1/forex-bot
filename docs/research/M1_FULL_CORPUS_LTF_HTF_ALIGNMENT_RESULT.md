# M1 Full Corpus LTF/HTF Alignment Result

**Overall status:** WARN
**Default execution timeframe:** M15 (M5 checked on EUR_USD + GBP_USD subset)

## Results

- **Lookahead violations:** 0 across all sampled pairs (120-day window per pair).
- **HTF feature time ≤ M15 decision time:** satisfied where features exist.
- **M1-derived D1AGG context:** empty → `HTF_UNAVAILABLE` dominates unavailable counts (expected given D1AGG result).
- **H1/H4 from M1:** present in sample windows; alignment helper runs without lookahead.

## M15 / M5 Readiness

| Lane | Status | Notes |
| --- | --- | --- |
| M15 default | **Ready with warnings** | Use M1-derived H1/H4; D1AGG via native H4 until M1 day completeness improves |
| M5 optional | **Ready with warnings** | Subset PASS on alignment sample |

## Blockers

None for scaffold if D1AGG provenance is hybrid (native H4→D1AGG). Pure M1-only D1AGG context is **not** ready.

**Artifact:** `ltf_htf_alignment_summary.json`
