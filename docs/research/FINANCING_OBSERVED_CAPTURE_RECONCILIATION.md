# Observed-Capture Reconciliation

**Date:** 2026-05-23 · **Branch:** `research-financing-observed-capture-pilot-001`
Phase 5 · `strategy_evidence: false`

Per the sprint instructions ("Only run if Phase 4 produced
redacted fixture-shaped observed events"), reconciliation is
**blocked** in this sprint — Phase 4 produced no observed
event file (no practice credentials were visible). This
document records the blocker, what reconciliation *would* have
done, and the explicit reminder that nothing here changes the
`MODELED` status.

> No broker / OANDA data was fetched. No reconciliation
> performed. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` stays `approved: []`.
> Paper / demo / live remain blocked. **`MODELED` financing
> remains blocked.**

## 1. Observed event file

**None.** Phase 4 attempted a dry-run only and refused with
`EXIT_MISSING_CREDS` because practice credentials are not
present in this worktree's environment. No
`observed_financing.json` was written.

See [`FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md)
for the full Phase 4 record.

## 2. Rate fixture that *would* have been used

If a future credentialed pilot run produced a non-empty
`observed_financing.json` covering EUR_USD rollovers in May
2026, the natural reconciliation target would be the existing
synthetic rate fixture:

[`research/financing/fixtures/rates_two_week_eur_usd.json`](../../research/financing/fixtures/rates_two_week_eur_usd.json)

- two business weeks of EUR_USD long/short rates
  (`long_annual_bp = -18.25`, `short_annual_bp = +9.125`),
  derived to reconcile against the calculator's stress output
  for matching 10k-unit EUR_USD positions
- one explicit `missing_dates` entry (`2026-05-19`) to
  exercise the `missing_rate_policy` plumbing

For any other pair or time window, no committed rate fixture
exists, and reconciliation would be **partial / blocked**
until either:

1. A future sprint adds rate-fixture variants for the
   remaining H4 universe pairs
   (`research-financing-bp-day-fixture-expansion-001`), or
2. A future captured run produces enough events that an
   *empirical* rate source can be built from the events
   themselves and reconciled against the calculator's stress
   default as a sanity check.

**Rates are not fabricated.** The reconciliation CLI's
`--rates` flag requires a valid rate fixture file; if none
covers the captured window, the operator must either supply
one explicitly (with documented provenance) or skip
reconciliation for that window.

## 3. Reconciliation result

**Not run.** The exact would-be command is preserved here for
the future credentialed sprint:

```bash
python scripts/reconcile_financing_fixtures.py \
  --observed /tmp/financing_observed_capture/observed_financing.json \
  --rates    research/financing/fixtures/rates_two_week_eur_usd.json \
  --output   /tmp/financing_observed_capture_reconcile/ \
  --missing-rate-policy skip \
  --tolerance 0.01
```

`--tolerance 0.01` (instead of the synthetic default `1e-9`)
matches the protocol's guidance for real-data reconciliation
in
[`FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md`](FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md)
§6: "A future real-data reconciliation would relax it
(e.g. `0.01`)."

The CLI's output (when run) would carry — verbatim from the
literal-pinned schema — `strategy_evidence: false`,
`financing_in_engine_pnl: false`,
`financing_is_live_blocker: true`, and at most
`financing_treatment: estimated`. The defense-in-depth
MODELED guard would refuse any attempt to emit `modeled`.

## 4. Mismatch classifications

n/a — no reconciliation performed. For reference, the four
classifications the CLI would emit per row are documented in
[`FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md`](FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md)
§7:

| classification | meaning |
|---|---|
| `match` | both sides exist, `|diff| ≤ tolerance` |
| `mismatch` | both sides exist, `|diff| > tolerance` |
| `missing_in_observed` | calculator has the row, observed does not |
| `missing_in_calculated` | observed has the row, calculator does not (e.g. rate missing under `skip` policy) |

A successful real-data reconciliation would target
`mismatch == 0` and well-understood `missing_*` counts.

## 5. Limitations

- **No real data.** Until a credentialed pilot runs and
  produces a non-empty observed-events file, this
  reconciliation step is structurally blocked.
- **Rate-fixture coverage is single-pair.** Only EUR_USD has
  a committed rate fixture; other pairs need either a future
  fixture-expansion sprint or a future captured-rate-derived
  table source.
- **Synthetic-only reconciliation success means nothing for
  MODELED.** The reconciliation CLI's existing synthetic-fixture
  runs (sister sprint Phase 4) demonstrate the calculator is
  internally consistent; they do not establish that the
  calculator matches OANDA. Only real-data reconciliation
  closes that gap.
- **Tolerance must be set by the operator per real run.** The
  CLI's default `1e-9` would surface broker-rounding noise
  as `mismatch`; real-data reconciliation should pass
  `--tolerance 0.01` (or whatever the per-event noise floor
  justifies, documented in a future pre-commit).
- **No batch / cross-pair driver yet.** A future
  `research-financing-reconciliation-batch-001` sprint could
  add an aggregator that runs the reconciliation CLI over
  many fixture pairs and produces a single summary doc;
  outside the scope of this sprint.

## 6. MODELED status

**`MODELED` financing remains blocked.**

The reconciliation CLI's defense-in-depth `_build_report`
guard would refuse `MODELED` even if every upstream layer
had been defeated. The full five-criterion checklist from
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
§11 remains unchanged by this sprint:

| # | criterion | status |
|---:|---|---|
| 1 | ≥ 60 captured rollovers across the traded universe | **0 — capture did not run** |
| 2 | per-event reconciliation passes against captured data | **blocked** — no captured data |
| 3 | `MODELED` `FinancingModel` implementation | not implemented |
| 4 | engine-PnL integration | not implemented |
| 5 | documented human approval | not granted |

A future credentialed pilot run that produces real events
satisfies criterion 1 *partially* (one window's worth, far
short of "≥ 60 across the universe") and unblocks criterion
2 for that window's pair set. It does not on its own move
the system to `MODELED`.

## 7. Cross-links

- Phase 4 run record (the blocker):
  [`FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_RUN.md)
- Sprint plan:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md`](FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md)
- Future-capture pilot spec:
  [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- Reconciliation CLI protocol (the would-be reconciliation
  step):
  [`FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md`](FINANCING_RECONCILIATION_TOOLING_PROTOCOL.md)
- Reconciliation CLI:
  [`scripts/reconcile_financing_fixtures.py`](../../scripts/reconcile_financing_fixtures.py)
- Synthetic runs of the reconciliation CLI (the existing
  diagnostic baseline):
  [`FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md`](FINANCING_RECONCILIATION_SYNTHETIC_RUNS.md)
- EUR_USD rate fixture:
  [`research/financing/fixtures/rates_two_week_eur_usd.json`](../../research/financing/fixtures/rates_two_week_eur_usd.json)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
