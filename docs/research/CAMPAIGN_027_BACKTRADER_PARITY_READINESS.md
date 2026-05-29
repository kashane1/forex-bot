# CAMPAIGN_027_BACKTRADER_PARITY_READINESS

**Status:** TRAIN/VALIDATION EXECUTION — Phase 8 / REJECT_TRAIN_GATE /
**DEFER_PARITY_REJECTED** / TEST_LOCKBOX_CLOSED / NOT_APPROVED. Branch
`research-campaign-027-h4-filtered-zscore-reversion-train-validation-001`.

Determines whether CAMPAIGN_027 deserves a Backtrader parity sprint.

> Parity spec (design): [parity design](CAMPAIGN_027_BACKTRADER_PARITY_DESIGN.md).
> Gate G8 (`FUTURE_CAMPAIGN_REENTRY_GATES.md`): parity is required *before* any
> test-lockbox open or promotion — and only for a rule that passed train+validation.

---

## Did train/validation pass?

**No.** Train failed 4 of 8 binding gates (PF 1.043 < 1.05; years non-negative 1/3;
2× cost stress −0.00007745 < 0; `f_strong_extension` filter-ablation). Validation
was not run (confirmation, not a rescue). Classification: `REJECT_TRAIN_GATE`.

## Is parity justified?

**No.** Backtrader parity exists to independently reproduce a *passing* research
result before promotion review, catching engine-specific bugs that could inflate a
wafer-thin edge. There is **no passing result to reproduce**: the research engine
itself already rejects the rule on its own ledgers under the binding conservative
cost. Building a second engine to confirm a rejection would be wasted effort and
could be misread as keeping the campaign alive.

## Known parity risks (recorded for completeness; not exercised this sprint)

From the parity design, the discrepancy hot-spots that *would* have to be matched if
this rule had passed:

- **z-score warmup / shift** — one-bar `.shift(1)` and `ddof=1` (most likely
  reconciliation failure).
- **ATR-percentile warmup** — simple-mean ATR(14) (not Wilder) + trailing-250
  percentile shifted one bar; `minperiod` must equal the ≈270-bar research warmup.
- **session labeling** — UTC-hour buckets asia[0,7)/london[7,12); DST/local-time
  mistakes shift bars between quiet/loud buckets.
- **next_bar_open fills** — entry at open[t+1] and time-stop exit at open[t+13];
  `cheat_on_open` must be off on **both** legs.
- **hard-stop / time-exit ordering** — the protective 3×ATR stop may pre-empt the
  time stop intrabar; the **adverse stop wins a same-bar tie** — both engines must
  encode the identical tie-break.
- **cost overlay** — optimistic (realized spread) vs conservative (1.5-pip flat +
  2×0.2-pip slip), applied once per round trip.
- **financing** — conservative bp/day stress applied over the hold (per-bar vs
  once-per-trade is an easy divergence).

These remain *documented design risks only*; no Backtrader code is written.

## Recommendation

**`DEFER_PARITY_REJECTED`.** Do not build parity. The campaign is rejected at the
train gate; parity is moot. If a future sprint ever revives the family (only on a
**new external thesis**, not a re-tune), parity would be built per the existing
design before any test-lockbox open.

## No-approval statement

No strategy is approved. `configs/approved_strategies.yaml` stays `approved: []`.
The test lockbox was not opened; paper/demo/live remain blocked.
</content>
