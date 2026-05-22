# Resume — Research Marathon 001

If the marathon is interrupted, this file says exactly where it stopped
and how to continue. It is rewritten after every phase.

## Current status

- Phase: **0 complete — Phase 1 (CAMPAIGN_005) next.**
- Branch: `research-marathon-001`.
- Last commit: _(see git log)_.

## Environment setup (always run first)

```bash
cd /Users/kashane/dev/forex-bot
source .venv/bin/activate
set -a && source ./.env.local && set +a   # OANDA practice creds (gitignored)
bot doctor --config configs/campaign_002_real_oanda.yaml   # expect creds present
```

## Next action

Run CAMPAIGN_005 benchmarks:

```bash
python scripts/run_campaign_005_benchmarks.py
python scripts/build_campaign_005_report.py
```

Then proceed down the ladder in
[`RESEARCH_MARATHON_001_PLAN.md`](RESEARCH_MARATHON_001_PLAN.md):
CAMPAIGN_006 → 007 → 008 → Phase 5.

## Per-campaign procedure

1. Write `docs/research/CAMPAIGN_XXX_PRECOMMIT.md` **before** running.
2. Run the screening phase (train + validation + full + cost stress).
3. Evaluate the test-window gate. Run the test window **only** if it
   passes.
4. Build the report; append a ledger entry.
5. `pytest -q` and `ruff check src tests scripts`.
6. Commit code + small artifacts.
7. Check hard stop conditions before continuing.

## Hard stops

See [`RESEARCH_MARATHON_001_PLAN.md`](RESEARCH_MARATHON_001_PLAN.md).
If any is hit, stop and write the Phase 5 doc (NO_GO or
CANDIDATE_REVIEW).
