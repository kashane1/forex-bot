# Resume — Research Marathon 001

## Current status

**MARATHON COMPLETE — outcome NO-GO.** No campaign remains to run.

- Branch: `research-marathon-001`.
- All phases done: Phase 0 (setup), CAMPAIGN_005 (benchmarks),
  CAMPAIGN_006 (D1 trend), CAMPAIGN_007 (H4 pullback), CAMPAIGN_008
  (mean reversion), Phase 5 (NO-GO conclusion).
- Conclusion: [`RESEARCH_MARATHON_001_NO_GO.md`](RESEARCH_MARATHON_001_NO_GO.md).
- Full per-phase record: [`RESEARCH_MARATHON_001_LEDGER.md`](RESEARCH_MARATHON_001_LEDGER.md).

Nothing is to be resumed. The marathon reached its end state cleanly:
no candidate earned PAPER-TRADE-ONLY; a documented NO-GO was produced.

## If a human authorizes further work

This is **not** an automatic resume — it requires an explicit human
decision (see the NO_GO doc's "recommended next human decision point").

The single direction worth attention is regime-filtered mean reversion
(CAMPAIGN_008: validation +0.172 R, 6/6 pairs, cost-stress survivor;
failed screening only on a flat train split, −0.017 R). A follow-up
would be a **new, separately-authorized campaign** with its own
pre-commit — e.g. adding a midline-target exit to `mean_reversion` and
re-screening. It is not part of this marathon.

## Environment setup (if any further work is authorized)

```bash
cd /Users/kashane/dev/forex-bot
source .venv/bin/activate
set -a && source ./.env.local && set +a   # OANDA practice creds (gitignored)
pytest -q && ruff check src tests scripts
```

## Reproduce the marathon

```bash
python scripts/run_campaign_005_benchmarks.py
python scripts/run_marathon_campaign.py --config configs/campaign_006_daily_trend.yaml \
    --out backtests/campaign_006_daily_trend/runs --campaign-id CAMPAIGN_006 --phase screen --clean
python scripts/run_marathon_campaign.py --config configs/campaign_007_h4_pullback.yaml \
    --out backtests/campaign_007_h4_pullback/runs --campaign-id CAMPAIGN_007 --phase screen --clean
python scripts/run_marathon_campaign.py --config configs/campaign_008_range_mean_reversion.yaml \
    --out backtests/campaign_008_range_mean_reversion/runs --campaign-id CAMPAIGN_008 --phase screen --clean
# Reports: scripts/build_marathon_report.py builds 006-008;
#          scripts/run_campaign_005_benchmarks.py writes the 005 report.
```

No order submission, paper-loop, or demo-loop is involved at any point.
