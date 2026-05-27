# next_bar_open Reference Comparison — Result

**Reference:** CAMPAIGN_019 · **Date:** 2026-05-27  
**Command:** `python scripts/compare_fill_timing_reference_campaign.py`  
**Data:** `data/campaign_002.sqlite3`, dedupe `keep_last`, source `oanda-practice`

## Reproduction check (signal_bar_close)

| Split | Metric | This run | C019 committed |
|-------|--------|----------|----------------|
| Train | trades | 219 | 219 |
| Train | expectancy R | **−0.072** | −0.072 |
| Validation | trades | 138 | 138 |
| Validation | expectancy R | **+0.0962** | +0.0962 |

Close-timing rerun matches committed C019 aggregates.

## Comparison table

| Split | Metric | signal_bar_close | next_bar_open | Δ (open − close) |
|-------|--------|------------------|---------------|------------------|
| Train | trade_count | 219 | 217 | −2 |
| Train | expectancy R | −0.072 | −0.0378 | **+0.034** |
| Train | profit_factor | 0.927 | 0.988 | +0.061 |
| Train | pairs_positive | 3 | 4 | +1 |
| Validation | trade_count | 138 | 133 | −5 |
| Validation | expectancy R | **+0.0962** | **+0.0175** | **−0.079** |
| Validation | profit_factor | 1.142 | 1.056 | −0.086 |
| Validation | pairs_positive | 6 | 4 | −2 |

## Interpretation

1. **Validation split is materially weaker** under `next_bar_open` (−0.079 R). The C019 validation uplift (+0.096 R vs train −0.072 R) was **partially inflated** by optimistic same-bar-close fills.
2. **Train split is mixed** — next_bar_open is slightly less negative (−0.038 vs −0.072), not uniformly worse. Fill-timing bias is **not monotonic** across splits for this strategy, but validation is the binding realism check for the observed uplift narrative.
3. **Trade count** drops slightly (final-bar `NEXT_BAR_OPEN_UNAVAILABLE` and different fill bars).
4. **Exit mix** shifts modestly (thesis_invalidation share −1.7 pp; time +1.2 pp).

## C019 interpretation impact

- **Verdict unchanged:** C019 remains **REJECT** (train gate fail). Fill-timing does not rescue the campaign.
- **Narrative adjustment:** Treat C019 validation +0.096 R (and similar signal_bar_close uplifts) as **upper-bound / optimistic** evidence until rerun under `next_bar_open`.
- **C019 rerun for verdict?** Not required for REJECT/approve decision; **recommended** if re-arguing validation-only edge in a future memo.

## Policy recommendation

| Audience | Rule |
|----------|------|
| Future approval-bound precommits | **Require `next_bar_open`** unless explicit justification documented |
| Historical CAMPAIGN_001–019 | Treat `signal_bar_close` results as **optimistic upper bound**, especially validation splits |
| Infrastructure default | Keep `signal_bar_close` as engine default for byte-identical replay; campaigns must **pin** timing in runner |

## Explicit non-approval

This comparison is **infrastructure evidence only**. No strategy was approved. CAMPAIGN_020 was not created.
