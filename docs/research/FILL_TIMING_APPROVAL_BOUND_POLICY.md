# Fill Timing — Approval-Bound Evidence Policy

**Date:** 2026-05-27 · **Sprint:** `infra-next-bar-open-policy-and-htf-align-migration-001`  
**Type:** infrastructure / policy only — **no strategy approval**

## Why `signal_bar_close` is optimistic

Filling at the signal bar’s close assumes the trader could enter at a price known only when that bar completes. For H4 (and faster) signals, that price is not knowable at decision time without lookahead. The bespoke engine’s conservative analogue is **`next_bar_open`**: queue on the signal bar, execute at the **next** bar’s open.

## C019 comparison evidence (reference run)

Committed C019 used `signal_bar_close`. Infrastructure comparison on the same C019 config and data (`scripts/compare_fill_timing_reference_campaign.py`):

| Split | Metric | signal_bar_close | next_bar_open | Δ (open − close) |
|-------|--------|------------------|---------------|------------------|
| Train | expectancy R | −0.072 | −0.0378 | +0.034 |
| Train | profit_factor | 0.927 | 0.988 | +0.061 |
| Train | pairs_positive | 3 | 4 | +1 |
| Validation | expectancy R | **+0.0962** | **+0.0175** | **−0.079** |
| Validation | profit_factor | 1.142 | 1.056 | −0.086 |
| Validation | pairs_positive | 6 | 4 | −2 |

**Binding takeaway:** C019 validation uplift (+0.096 R) is **partly inflated** by optimistic close fills. C019 remains **REJECT** (train gate); fill timing does not change the verdict.

Full table: [`NEXT_BAR_OPEN_REFERENCE_COMPARISON_RESULT.md`](NEXT_BAR_OPEN_REFERENCE_COMPARISON_RESULT.md).

## Required rule

| Audience | Rule |
|----------|------|
| **Approval-bound** / **promotion-review** campaigns | Must declare `fill_timing: next_bar_open` unless an explicit, reviewed `fill_timing_justification` documents a deliberate exception |
| Default for new approval-bound evidence | `next_bar_open` |
| Engine default | May remain `signal_bar_close` for byte-identical replay; campaigns must **pin** timing in runner/summary |

## Allowed uses of `signal_bar_close`

- **Legacy** — CAMPAIGN_001–019 executed before policy (treat as upper-bound where relevant)
- **Diagnostic** — fill-timing comparison, parity probes
- **Upper-bound research** — optimistic ceiling for sensitivity
- **Parity / debugging** — Backtrader lane approximation notes
- **Exploratory** — non-promotion experiments
- **Precommitted exception** — rare, documented in precommit with justification

`signal_bar_close` must **not** be labeled `promotion_eligible: true` or `evidence_use: approval_bound` without failing validation.

## Required metadata labels

| Field | Suggested values |
|-------|------------------|
| `fill_timing` | `next_bar_open` \| `signal_bar_close` \| `mixed` \| `unknown` |
| `execution_realism` | `conservative` \| `optimistic_upper_bound` \| `diagnostic` \| `unknown` |
| `evidence_use` | `approval_bound` \| `promotion_review` \| `research_only` \| `legacy` \| `diagnostic` |
| `promotion_eligible` | `true` \| `false` |
| `fill_timing_justification` | free text when timing ≠ `next_bar_open` or for legacy/diagnostic |

Implementation: `src/forex_bot/research/execution_realism.py`.

## Backward compatibility

- Historical campaigns are **not** auto-rewritten to PASS/FAIL from metadata gaps alone.
- Campaigns without `research_metadata` in YAML load in **legacy mode** (`evidence_use: legacy`, `promotion_eligible: false`).
- C019 is recorded in `EVIDENCE_MANIFEST.json` as `signal_bar_close` / `optimistic_upper_bound` / `legacy` / `promotion_eligible: false`.
- **No rerun required** to preserve REJECT verdict; rerun under `next_bar_open` is **future work** if re-arguing validation-only narratives.

## No-approval statement

This policy does not approve any strategy. `configs/approved_strategies.yaml` remains `approved: []`. Paper / demo / live remain blocked.
