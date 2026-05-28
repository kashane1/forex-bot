# Campaign & identifier numbering convention

**Rule:** Before assigning a number or identifying code to **new** work, verify it
has **never been used before** — including for ideas that were *proposed but never
built*. If the value is taken, choose the next genuinely-free one.

This applies to every identifying token, not just campaigns:

- campaign IDs — `CAMPAIGN_0NN`
- strategy version suffixes — `0.1.0-cNN`
- sprint / branch names — `research-campaign-0NN-…-001`
- config / file slugs — `campaign_0NN_*.yaml`, `run_campaign_0NN_*.py`
- evidence-manifest `artifact_id`s

## Why this exists

On 2026-05-28 a scaffold was built as **CAMPAIGN_024**, but `C024` had already been
recorded for an **abandoned** C022/C023 pullback-resolution continuation
(`C024_READINESS_FROM_C022_FEATURE_SEPARATION.md`, marked `C024 NOT_READY`). The
number was never tied to a built campaign, but it was in the record — and the
collision forced a full wholesale rename to **CAMPAIGN_025** (branch, files,
identifiers, registry, memory). A 30-second up-front check would have avoided it.

**A "NOT_READY / not created" note still counts as the number being taken.** Do not
reuse such a number for unrelated new work.

## How to check before starting numbered work

1. Pick the candidate number `NN` (normally `max(existing) + 1`).
2. Grep the whole repo for every spelling of the token:
   ```
   git grep -iE "CAMPAIGN_0NN|campaign_0NN|-c0NN|[^0-9]c0NN[^0-9]"
   ```
3. Scan the registries and closeout/readiness docs specifically:
   - `docs/research/STRATEGY_STATUS.md`
   - `docs/research/EVIDENCE_INDEX.md`
   - `docs/research/EVIDENCE_MANIFEST.json`
   - `docs/research/FUTURE_RESEARCH_BACKLOG.md`
   - any `*_READINESS_*`, `*_CLOSEOUT*`, or `NEXT_*` docs
4. If **any** hit exists (built or abandoned), increment `NN` and repeat.
5. Record the chosen number in the plan/precommit so the decision is auditable.

## If a collision is found after work has started

Rename **wholesale** in one pass: branch, file names, directory names, in-file
identifiers and version strings, registry entries, and memory — but **preserve the
historical references** to the previously-used number (they correctly describe the
older item). See the C024→C025 rename for a worked example.
