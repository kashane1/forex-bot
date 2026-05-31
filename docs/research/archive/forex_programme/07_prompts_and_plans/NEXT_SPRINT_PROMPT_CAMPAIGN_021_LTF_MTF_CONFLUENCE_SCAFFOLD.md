# Next Sprint Prompt: CAMPAIGN 021 LTF MTF Confluence Scaffold

Use this prompt only after canonical M1 data ingestion, aggregation, and validation are locally ready. This prompt scaffolds a future candidate; it must not execute evidence by itself.

## Prompt

We are starting a strategy scaffold sprint for a future lower-timeframe MTF confluence candidate.

Candidate:

- `CAMPAIGN_021 lower_timeframe_mtf_confluence_entry`
- execution timeframe: M15 default
- optional execution support: M5
- context: H1/H4/D1AGG
- source data: canonical M1 locally aggregated into M5/M15/H1/H4/D1AGG
- fill timing: `next_bar_open`
- HTF alignment: `htf_align.align_last_completed`
- financing treatment: declare before evidence

Hard rules:

1. Scaffold only unless a separate evidence-execution prompt explicitly authorizes a campaign run.
2. Do not run evidence.
3. Do not tune parameters.
4. Do not open a test lockbox.
5. Do not approve a strategy.
6. Do not edit `configs/approved_strategies.yaml`.
7. Do not enable paper/demo/live.
8. Do not call broker mutation endpoints.
9. Do not use live OANDA.
10. Preserve C020 as REJECT.

Tasks:

1. Verify canonical M1 store readiness and data-quality reports.
2. Verify M1-to-M5/M15/H1/H4/D1AGG aggregation manifests.
3. Create a precommit design for `lower_timeframe_mtf_confluence_entry`.
4. Define warmups, features, signal provenance, and no-lookahead checks.
5. Define train/validation/test lockbox boundaries without running them.
6. Add structural tests and no broker/executor import checks.
7. Create docs describing the candidate scaffold and all blocked evidence steps.

Expected result:

- Scaffold and tests only.
- No evidence artifacts.
- No verdict.
- No approval.
