# Campaign Validity Impact — After next_bar_open Policy & HTF Migration

**Date:** 2026-05-27 · **Sprint:** `infra-next-bar-open-policy-and-htf-align-migration-001`

## next_bar_open policy impact

- Future **approval-bound** / **promotion-review** evidence must declare `fill_timing`; default **`next_bar_open`**.
- `signal_bar_close` evidence is **optimistic upper bound** unless explicitly justified as diagnostic/legacy.
- Enforcement: `execution_realism.py`, manifest policy block, archive validator.

## Old signal_bar_close evidence

| Treatment | Action |
|-----------|--------|
| CAMPAIGN_001–018 (mostly signal_bar_close) | **Not invalidated**; treat validation splits as upper-bound where uplift narrative matters |
| CAMPAIGN_019 | Manifest tagged `optimistic_upper_bound`; comparison doc records next_bar_open validation +0.0175 R |
| CAMPAIGN_015+ (some next_bar_open) | Already conservative timing where pinned |

**No automatic verdict changes.** No mass rerun required.

## C019 verdict

**Unchanged: REJECT.** Train gate fail. Fill-timing comparison adjusts interpretation of validation +0.096 R only.

## HTF align migration impact

- **Regime switcher** code path now uses shared `d1agg_htf` + `htf_align`; fixture-equivalent on tested paths.
- **CAMPAIGN_012** walk-forward artifacts: **not rerun**; verdict **REJECT** unchanged.
- **Weekly HTF campaigns:** not migrated; no rerun.

## Financing

- Modeled/overlay infrastructure unchanged this sprint.
- **Observed financing capture** still **BLOCKED** pending local practice credentials + overnight sample ([`OBSERVED_FINANCING_CAPTURE_READONLY_002_SUMMARY.md`](OBSERVED_FINANCING_CAPTURE_READONLY_002_SUMMARY.md)).

## Rerun recommendations (future work only)

| Item | Required for verdict? | Recommendation |
|------|----------------------|----------------|
| C019 under next_bar_open | No (already REJECT) | Optional if re-memo validation uplift |
| C008/C009 signal_bar_close | No | Optional sensitivity; deduped forensic already done |
| C012 post-HTF refactor | No | Optional only if arguing regime gate drift |

## No-approval statement

- `configs/approved_strategies.yaml`: `approved: []`
- No CAMPAIGN_020
- Paper / demo / live blocked
- No OANDA mutation APIs used in this sprint
