# M1 Full Corpus LTF Backtest Preflight Result

**Overall status:** WARN (M1-only D1AGG context empty); M15 execution checks pass

## Checks (60-day sample per pair)

| Check | Result |
| --- | --- |
| M15 execution frame non-empty | PASS all pairs |
| `next_bar_open` after mid-series signal | PASS all pairs |
| H1/H4 context frames | PASS (M1-derived sample) |
| M1-derived D1AGG context | FAIL — empty frame (documented) |
| Time-stop in execution bars | PASS (`time_stop_bars=48`) |

Preflight **FAIL** flag is solely `context frame empty: D1AGG` when forcing M1→D1AGG. With native H4→D1AGG context (existing store), preflight would pass — to be wired explicitly in CAMPAIGN_021 scaffold config.

## Strategy / Evidence

- No strategy evidence run.
- No train/validation/test campaign.
- No broker/executor imports in validation path.

**Artifact:** `ltf_preflight_summary.json`
