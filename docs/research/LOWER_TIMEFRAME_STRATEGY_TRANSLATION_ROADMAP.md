# Lower-Timeframe Strategy Translation Roadmap

## Why Pivot Away From H4-Only Entries

CAMPAIGN_020 ended REJECT after train expectancy was negative while validation was modestly positive. That repeats a broader pattern: H4-only entries may be too coarse for timing, even when higher-timeframe context has useful structure. The next research lane should test whether lower-timeframe execution improves entry precision without weakening the existing no-lookahead, cost, and approval guardrails.

## What Lower-Timeframe Execution Should Test

- M15 execution by default, with M5 available as a secondary execution timeframe.
- H1/H4/D1AGG confluence as completed higher-timeframe context.
- `next_bar_open` on the execution timeframe.
- `htf_align.align_last_completed` for every context join.
- Strict warmups per feature timeframe.
- Financing treatment declared before evidence.
- Spread/session/cost filters interpreted on the execution timeframe.

## Recommended First Candidate

`CAMPAIGN_021 lower_timeframe_mtf_confluence_entry`

Default structure:

- execution: M15
- optional sensitivity: M5
- context: H1, H4, D1AGG
- fills: `next_bar_open`
- HTF alignment: `htf_align`
- data source: canonical M1 locally aggregated to all research frames
- approval: impossible without separate completed evidence and human review

## Old Campaigns Worth Translating Later

- C020 MTF confluence first, because it is the closest conceptual fit.
- Event-window entries only if lower-timeframe event data exists.
- Avoid C008/C018/C019 exit-only family until new lower-timeframe entry evidence justifies revisiting exits.

## What Not To Redo Yet

- Do not rerun C020.
- M1 full-corpus validation is **complete** (`READY_WITH_WARNINGS` — see
  `M1_FULL_CORPUS_LTF_LANE_READINESS_DECISION.md`). CAMPAIGN_021
  **scaffold** may proceed; evidence remains blocked until scaffold precommit locks.
- D1AGG context for scaffold: **native H4→D1AGG** from Postgres until M1→D1AGG day completeness is repaired.
- Do not tune parameters before the lower-timeframe scaffold has a locked precommit.
- Do not open test lockboxes.
- Do not approve strategy configs.

## Data Requirements

- Validated canonical M1 bid/ask candles.
- Local aggregation manifests for M5/M15/H1/H4/D1AGG.
- Data-quality report with missing-minute, duplicate, incomplete, and spread summaries.
- Provenance hashes and ingestion batch IDs.

## Gates

Future evidence must preserve existing research gates plus lower-timeframe-specific gates:

- train gate before validation interpretation;
- validation gate before any lockbox discussion;
- no native OANDA D candles when D1AGG is required;
- no incomplete HTF context;
- no same-bar fills for approval-bound evidence;
- no approval from backtest results alone.

## Approval Statement

This roadmap creates no evidence and approves nothing. C020 remains REJECT and paper/demo/live remain blocked.
