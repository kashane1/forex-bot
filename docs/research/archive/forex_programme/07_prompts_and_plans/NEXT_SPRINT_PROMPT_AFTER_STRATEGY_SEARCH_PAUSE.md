# Next Sprint Prompt — After the Strategy-Search Pause

**Type:** **NON-strategy.** The standing decision is `PAUSE_STRATEGY_RESEARCH`. This prompt
must **not** start strategy research, a diagnostic mining lane, a campaign, C024, or
approval. It offers three mutually-exclusive non-strategy tracks; the operator picks one.

> Do not restart strategy research here. A restart requires meeting
> `STRATEGY_RESEARCH_RESTART_CRITERIA.md` first, in a separate proposal.

---

## Track A (default) — Merge-readiness / archive closeout

Use this if the goal is to land the pause cleanly and step away.

```
We are continuing the forex-bot research freeze. The strategy-search pause is complete.
Do a MERGE-READINESS / ARCHIVE closeout sprint. This is NOT strategy research, NOT a
campaign, NOT C024, NOT C023, NOT approval, NOT paper/demo/live.

Branch from the pause tip:
    research-strategy-search-pause-merge-readiness-001

Tasks (commit per phase):
  1. Audit the strategy-search-pause branch chain for merge-readiness: confirm only
     docs/research, scripts, research/, src/forex_bot/research modules + tests, and
     .gitignore changed; no broker/executor/order/live/config edits; approved_strategies
     .yaml == approved: []; C023 not executed; C024 absent; TEST sealed.
  2. Run the full gate suite: pytest -q, ruff, check_research_freeze, validate_research_
     archive, scan_artifacts_for_secrets (value-scan with .env if available).
  3. Confirm no .env/credentials/DBs/parquet/huge CSVs are staged; bulky outputs gitignored.
  4. Produce a one-page MERGE_READINESS_SUMMARY listing every branch/sprint in the chain,
     the standing PAUSE decision, and the exact human merge command.
  5. Do NOT merge or push (human action). Report the recommended command only.
```

## Track B — External data-acquisition infrastructure (unblocks future theses)

Use this if active progress is wanted without strategy mining.

```
We are continuing the forex-bot research freeze under PAUSE_STRATEGY_RESEARCH. Build
external DATA-ACQUISITION infrastructure only. This is NOT strategy research, NOT a
campaign, NOT C024, NOT approval, NOT paper/demo/live. No edge claims.

Branch:
    research-external-data-acquisition-infra-001

Goal: acquire/ingest the data that the macro-context lane proved was the binding
constraint, so future theses become *identifiable* — strictly as lookahead-safe research
features:
  * a verified JP rate leg (e.g. JGB 2y/10y) to build a real US-JP rate differential;
  * a longer multi-cycle history (beyond 2021-2025) so a rate/macro regime is not
    collinear with one period;
  * a verified BOJ / US-CPI economic-event calendar (public schedule dates only);
  * (optional) options/implied-vol or an order-flow proxy.

Rules: read-only research DB / .env for access only; never print credentials; as-of/lagged
joins; daily/weekly cadence; TEST sealed; commit compact manifests only (gitignore bulky/
raw); no strategy, no campaign, no verdict change; approved_strategies.yaml stays empty.
Deliverables: ingestion + provenance + lookahead-safety tests + a coverage manifest; a
readiness note on which previously-blocked theses each dataset would unblock. End at an
infrastructure-readiness decision, NOT a strategy decision.
```

## Track C — External-thesis research brief (only if the user supplies a new thesis)

Use this only when the operator brings a genuinely new, mechanism-backed thesis from
outside the repo.

```
We are continuing the forex-bot research freeze under PAUSE_STRATEGY_RESEARCH. The operator
has supplied a NEW external thesis: <PASTE THESIS + MECHANISM + PROPOSED OBJECTIVE RULES>.
Produce an EXTERNAL-THESIS RESEARCH BRIEF only — NOT an implementation, NOT a campaign,
NOT C024, NOT approval.

Branch:
    research-external-thesis-brief-001

Tasks (commit per phase):
  1. Score the thesis against STRATEGY_RESEARCH_RESTART_CRITERIA.md: which trigger(s) it
     meets; structural distinctness from the retired/closed families; data availability;
     mechanism plausibility; objective codability; cost-survival plausibility; lookahead
     and multiple-testing risk.
  2. State explicitly whether it MEETS the restart bar. If not, stop at NOT_READY.
  3. If it meets the bar, draft (do NOT run) a precommit-design outline with the standard
     falsification panel (realistic stop + conservative cost + multiple-testing haircut +
     year/half split + latency-independence) and a sealed-TEST protocol.
  4. Do not create C024 or any campaign; that is a later, separate, precommitted sprint.
```

---

## Operator note

- **Recommended default:** Track A (merge-readiness/archive), then pause and do external
  thesis sourcing outside the repo (per `NEXT_ACTION_OPTIONS_AFTER_STRATEGY_SEARCH_PAUSE.md`).
- Track B is the recommended *active* track if you want to remove the data constraints that
  ended the macro lane.
- Track C is gated on you supplying a qualifying thesis; absent that, do not restart.
- In all tracks: no C024, no C023, no approval, no paper/demo/live, `approved: []`, TEST
  sealed.
